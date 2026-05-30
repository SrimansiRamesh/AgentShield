from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from extractors import deduplicate_sources
from models import PublicIncident, SecuritySignals, ToolSecurityReport

logger = logging.getLogger(__name__)

# Bright Data MCP server package
_BD_MCP_PACKAGE = "@brightdata/mcp"

SYSTEM_PROMPT = """\
You are AgentShield, a professional security research assistant specializing in AI developer tools.

Your job is to research the security posture of a given tool by gathering publicly available information.

Research strategy (follow this order):
1. Search: "{tool_name} official website"
2. Search: "{tool_name} security"
3. Scrape the vendor homepage to find links to: security page, trust center, privacy policy
4. Scrape each of those pages for evidence of security certifications and features
5. Search: "{tool_name} SOC2 compliance"
6. Search: "{tool_name} security incident breach CVE vulnerability"
7. Scrape any news or advisory pages that look relevant

Security signals to detect (look for explicit mentions):
- SOC 2 (Type I or II)
- ISO 27001
- SSO (SAML, OAuth, OIDC)
- MFA / 2FA / TOTP
- RBAC / role-based access control
- Audit logs / audit trails
- Encryption (at rest, in transit, AES-256, TLS)
- Vulnerability disclosure program / responsible disclosure
- Bug bounty program (HackerOne, Bugcrowd, etc.)

Rules:
- Only set a signal to true if you found explicit evidence in the scraped content.
- Set to false only if the source explicitly says the feature is absent.
- Use null for anything you could not confirm either way.
- Collect all URLs you scrape or find as sources.

When you have gathered sufficient information, output ONLY a JSON object — no explanation, no markdown fences, just the raw JSON:

{
  "tool_name": "string",
  "company": "string or null",
  "product_name": "string or null",
  "vendor_url": "string or null",
  "security_page_url": "string or null",
  "trust_center_url": "string or null",
  "privacy_policy_url": "string or null",
  "security_signals": {
    "soc2": true | false | null,
    "iso27001": true | false | null,
    "sso": true | false | null,
    "mfa": true | false | null,
    "rbac": true | false | null,
    "audit_logs": true | false | null,
    "encryption": true | false | null,
    "vulnerability_disclosure": true | false | null,
    "bug_bounty": true | false | null
  },
  "public_incidents": [
    {
      "date": "string or null",
      "title": "string",
      "description": "string",
      "severity": "low | medium | high | critical | null",
      "source_url": "string"
    }
  ],
  "sources": ["url1", "url2", ...]
}
"""


def _to_anthropic_tool(tool: Any) -> dict[str, Any]:
    schema = getattr(tool, "inputSchema", None) or {"type": "object", "properties": {}}
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": schema,
    }


class ResearchAgent:
    def __init__(
        self,
        api_key: str | None = None,
        brightdata_api_token: str | None = None,
        model: str = "claude-opus-4-8",
        max_iterations: int = 25,
    ) -> None:
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )
        self.brightdata_token = brightdata_api_token or os.environ.get(
            "BRIGHTDATA_API_TOKEN", ""
        )
        self.model = model
        self.max_iterations = max_iterations

    async def research(self, tool_name: str) -> ToolSecurityReport:
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", _BD_MCP_PACKAGE],
            env={**os.environ, "API_TOKEN": self.brightdata_token},
        )

        logger.info("Starting Bright Data MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                raw_tools = await session.list_tools()
                tools = [_to_anthropic_tool(t) for t in raw_tools.tools]
                logger.info(
                    "MCP tools available: %s", [t["name"] for t in tools]
                )

                if not tools:
                    raise RuntimeError(
                        "Bright Data MCP server returned no tools. "
                        "Check your BRIGHTDATA_API_TOKEN."
                    )

                return await self._agentic_loop(session, tools, tool_name)

    async def _agentic_loop(
        self,
        session: ClientSession,
        tools: list[dict[str, Any]],
        tool_name: str,
    ) -> ToolSecurityReport:
        system = SYSTEM_PROMPT.replace("{tool_name}", tool_name)
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    f"Research the security posture of: {tool_name}\n\n"
                    "Be thorough. Scrape their website, security pages, trust center, "
                    "privacy policy, and search for any public incidents or CVEs. "
                    "When done, output the JSON report."
                ),
            }
        ]
        scraped_urls: list[str] = []

        for iteration in range(1, self.max_iterations + 1):
            logger.info("Iteration %d / %d", iteration, self.max_iterations)

            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system,
                    tools=tools,
                    messages=messages,
                )
            except anthropic.APIError as exc:
                logger.error("Anthropic API error: %s", exc)
                raise

            logger.debug("Stop reason: %s", response.stop_reason)
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        report = self._parse_report(
                            block.text, tool_name, scraped_urls
                        )
                        if report:
                            logger.info("Research complete. Sources: %d", len(report.sources))
                            return report
                logger.warning("Agent finished but produced no valid JSON; returning partial report")
                return ToolSecurityReport(
                    tool_name=tool_name,
                    sources=deduplicate_sources(scraped_urls),
                )

            # Handle tool calls
            tool_results: list[dict[str, Any]] = []
            for block in response.content:
                if not hasattr(block, "type") or block.type != "tool_use":
                    continue

                result_text = await self._call_tool(session, block, scraped_urls)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    }
                )

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

        logger.warning("Max iterations reached; returning partial report")
        return ToolSecurityReport(
            tool_name=tool_name,
            sources=deduplicate_sources(scraped_urls),
        )

    async def _call_tool(
        self,
        session: ClientSession,
        block: Any,
        scraped_urls: list[str],
    ) -> str:
        tool_name = block.name
        tool_input = block.input or {}
        logger.info(
            "Tool call: %s  input: %s",
            tool_name,
            json.dumps(tool_input)[:300],
        )

        # Track URLs that get scraped
        for key in ("url", "query"):
            if key in tool_input and key == "url":
                scraped_urls.append(tool_input[key])

        try:
            result = await session.call_tool(tool_name, tool_input)
            content = result.content

            if isinstance(content, list):
                parts = [
                    c.text if hasattr(c, "text") else str(c) for c in content
                ]
                result_text = "\n".join(parts)
            else:
                result_text = str(content)

            logger.debug(
                "Tool result (%d chars): %s...", len(result_text), result_text[:400]
            )
            return result_text

        except Exception as exc:
            logger.error("Tool call failed (%s): %s", tool_name, exc)
            return f"Tool call failed: {exc}"

    def _parse_report(
        self,
        text: str,
        tool_name: str,
        scraped_urls: list[str],
    ) -> ToolSecurityReport | None:
        # Find the outermost JSON object in the response
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end <= start:
            logger.debug("No JSON object found in agent response")
            return None

        try:
            data = json.loads(text[start:end])
        except json.JSONDecodeError as exc:
            logger.error("JSON parse error: %s", exc)
            return None

        try:
            all_sources = deduplicate_sources(
                data.get("sources", []) + scraped_urls
            )

            signals_raw = data.get("security_signals", {})
            signals = SecuritySignals(**{
                k: v for k, v in signals_raw.items()
                if k in SecuritySignals.model_fields
            })

            incidents = [
                PublicIncident(**inc)
                for inc in data.get("public_incidents", [])
                if isinstance(inc, dict) and "title" in inc
            ]

            return ToolSecurityReport(
                tool_name=data.get("tool_name", tool_name),
                company=data.get("company"),
                product_name=data.get("product_name"),
                vendor_url=data.get("vendor_url"),
                security_page_url=data.get("security_page_url"),
                trust_center_url=data.get("trust_center_url"),
                privacy_policy_url=data.get("privacy_policy_url"),
                security_signals=signals,
                public_incidents=incidents,
                sources=all_sources,
            )

        except Exception as exc:
            logger.error("Failed to construct ToolSecurityReport: %s", exc)
            return None
