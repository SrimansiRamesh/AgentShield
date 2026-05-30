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
from models import (
    AIAgentSignals,
    CategorizedSignals,
    CategoryScore,
    HardeningStep,
    RiskOwnerRouting,
    ThreatEvent,
    ToolSecurityReport,
    VendorMetadata,
)

logger = logging.getLogger(__name__)

# Bright Data MCP server package
_BD_MCP_PACKAGE = "@brightdata/mcp"

SYSTEM_PROMPT = """You are AgentShield, a professional security research assistant and cybersecurity architect 
specializing in AI developer tools.

Your job is to research the security posture of a given AI tool by gathering publicly available 
information and producing a structured, actionable report optimized for enterprise due diligence.

---

RESEARCH STRATEGY (follow this order):
1. Search: "{tool_name} official website"
2. Search: "{tool_name} security"
3. Scrape the vendor homepage to find links to: security page, trust center, privacy policy
4. Scrape each of those pages for evidence of security certifications and features
5. Search: "{tool_name} SOC2 compliance"
6. Search: "{tool_name} security incident breach CVE vulnerability"
7. Scrape any news or advisory pages that look relevant
8. Search: "{tool_name} data training privacy policy"
9. Search: "{tool_name} data retention prompt logging policy"

---

SIGNALS TO DETECT

Standard security signals (explicit mentions only):
- SOC 2 (Type I or II)
- ISO 27001
- SSO (SAML, OAuth, OIDC)
- MFA / 2FA / TOTP
- RBAC / role-based access control
- Audit logs / audit trails
- Encryption (at rest, in transit, AES-256, TLS)
- Vulnerability disclosure program / responsible disclosure
- Bug bounty program (HackerOne, Bugcrowd, etc.)

AI/Agent-specific signals (explicit mentions only):
- zero_data_retention: Does the vendor commit to not training on user data, or offer an opt-out?
- prompt_logging_period: How many days are inputs/outputs retained? (integer or null)
- execution_environment: Is code/actions executed locally, in a cloud-isolated environment, or unknown?
- user_in_the_loop: Does the tool require manual approval before terminal or destructive actions?

Signal rules:
- Only set a signal to true if you found explicit evidence in scraped content
- Set to false only if a source explicitly states the feature is absent
- Use null for anything you could not confirm either way
- NEVER infer a signal from generic phrases like "enterprise-grade security" — those are null, not true

---

INCIDENT RULES:
- Prioritize incidents from the last 24 months
- For each incident extract: CVE ID if present, whether a patch exists, affected versions if mentioned
- Only include incidents with a verifiable source URL
- Assign ui_badge_color as: critical → "red", high → "red", medium → "orange", low → "yellow"

---

REVIEW LEVEL RULES (heuristic-driven, no numerical scoring):
Assign "High Review Required" if ANY of the following:
- zero_data_retention is false or null
- 2 or more high/critical CVEs found
- execution_environment is "cloud_isolated" or "unknown" with no user_in_the_loop

Assign "Medium Review Required" if ANY of the following:
- SOC2 is null or false
- bug_bounty is false or null
- 1 high/critical CVE found
- prompt_logging_period is unknown or greater than 30 days

Assign "Low Review Required" only if:
- SOC2 is true, zero_data_retention is true, no high/critical CVEs, and MFA is true

---

CATEGORIZATION RULES:

compliance_and_governance covers: soc2, iso27001, encryption, vulnerability_disclosure, bug_bounty
identity_and_access covers: sso, mfa, rbac, audit_logs
ai_data_privacy covers: zero_data_retention, prompt_logging_period, execution_environment, user_in_the_loop

For each category:
- positive: list of signals confirmed true
- missing: list of signals that are false or null
- score_percentage: (confirmed true signals / total signals in category) × 100, rounded to nearest 5

---

HARDENING STEPS RULES:
Generate 3-5 actionable hardening steps based on missing signals and known incidents.
Each step must be specific to this vendor — not generic advice.
Format as a title (what to do) and description (how to do it in this vendor's platform).

---

OUTPUT FORMAT:
When you have gathered sufficient information, output ONLY a raw JSON object.
No explanation, no markdown fences, no preamble.

{
  "vendor_metadata": {
    "company": "string or null",
    "product": "string or null",
    "url": "string or null",
    "security_url": "string or null",
    "trust_center_url": "string or null",
    "privacy_policy_url": "string or null"
  },
  "review_level": "Low Review Required" | "Medium Review Required" | "High Review Required",
  "recommendation_summary": "string",
  "confidence": "high" | "medium" | "low",
  "confidence_reason": "string",
  "categorized_signals": {
    "compliance_and_governance": {
      "score_percentage": 0-100,
      "positive": ["string", ...],
      "missing": ["string", ...]
    },
    "identity_and_access": {
      "score_percentage": 0-100,
      "positive": ["string", ...],
      "missing": ["string", ...]
    },
    "ai_data_privacy": {
      "score_percentage": 0-100,
      "positive": ["string", ...],
      "missing": ["string", ...]
    }
  },
  "ai_agent_signals": {
    "zero_data_retention": true | false | null,
    "prompt_logging_period_days": integer | null,
    "execution_environment": "local" | "cloud_isolated" | "unknown",
    "user_in_the_loop": true | false | null
  },
  "threat_timeline": [
    {
      "id": "string or null",
      "title": "string",
      "date": "YYYY-MM-DD or null",
      "severity": "low" | "medium" | "high" | "critical",
      "description": "string",
      "cve_id": "string or null",
      "patched": true | false | null,
      "source_url": "string",
      "ui_badge_color": "red" | "orange" | "yellow"
    }
  ],
  "use_case_fit": {
    "storing_pii": "safe" | "caution" | "avoid",
    "internal_dev_tooling": "safe" | "caution" | "avoid",
    "regulated_industries": "safe" | "caution" | "avoid",
    "agentic_autonomous_execution": "safe" | "caution" | "avoid"
  },
  "use_case_reasoning": {
    "storing_pii": "string",
    "internal_dev_tooling": "string",
    "regulated_industries": "string",
    "agentic_autonomous_execution": "string"
  },
  "actionable_hardening_steps": [
    {
      "title": "string",
      "description": "string"
    }
  ],
  "incident_velocity": "string or null",
  "risk_owner_routing": {
    "security_team": "string or null",
    "legal": "string or null",
    "procurement": "string or null"
  },
  "sources": ["url1", "url2", ...]
}


"""


def _salvage_truncated_json(text: str) -> dict | None:
    """Try progressively shorter prefixes until one parses as valid JSON."""
    # Walk back from the end looking for a closing brace that completes the object
    for i in range(len(text) - 1, 0, -1):
        if text[i] == "}":
            candidate = text[: i + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
    return None


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
                    max_tokens=16384,
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
            else:
                # No tool calls and stop_reason != end_turn.
                # Try to parse any text block as the final report first.
                for block in response.content:
                    if hasattr(block, "text") and block.text.strip():
                        report = self._parse_report(block.text, tool_name, scraped_urls)
                        if report:
                            logger.info("Parsed report from non-end_turn response")
                            return report
                # Conversation must end with a user message or the API rejects it.
                messages.append({
                    "role": "user",
                    "content": "Please output the final JSON security report based on your research so far.",
                })

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
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end <= start:
            logger.debug("No JSON object found in agent response")
            return None

        try:
            data = json.loads(text[start:end])
        except json.JSONDecodeError as exc:
            logger.error("JSON parse error: %s", exc)
            # Response was likely truncated - walk back to the last valid closing brace
            data = _salvage_truncated_json(text[start:end])
            if data is None:
                return None
            logger.warning("Parsed salvaged (truncated) JSON - report may be partial")

        try:
            all_sources = deduplicate_sources(data.get("sources", []) + scraped_urls)

            meta_raw = data.get("vendor_metadata", {})
            vendor_metadata = VendorMetadata(**{
                k: v for k, v in meta_raw.items()
                if k in VendorMetadata.model_fields
            })

            ai_raw = data.get("ai_agent_signals", {})
            ai_signals = AIAgentSignals(**{
                k: v for k, v in ai_raw.items()
                if k in AIAgentSignals.model_fields
            })

            cat_raw = data.get("categorized_signals", {})
            categorized = CategorizedSignals(
                compliance_and_governance=CategoryScore(
                    **cat_raw.get("compliance_and_governance", {})
                ),
                identity_and_access=CategoryScore(
                    **cat_raw.get("identity_and_access", {})
                ),
                ai_data_privacy=CategoryScore(
                    **cat_raw.get("ai_data_privacy", {})
                ),
            )

            threat_timeline = [
                ThreatEvent(**e)
                for e in data.get("threat_timeline", [])
                if isinstance(e, dict) and "title" in e
            ]

            hardening = [
                HardeningStep(**s)
                for s in data.get("actionable_hardening_steps", [])
                if isinstance(s, dict) and "title" in s
            ]

            routing_raw = data.get("risk_owner_routing", {})
            routing = RiskOwnerRouting(**{
                k: v for k, v in routing_raw.items()
                if k in RiskOwnerRouting.model_fields
            })

            return ToolSecurityReport(
                tool_name=tool_name,
                vendor_metadata=vendor_metadata,
                review_level=data.get("review_level"),
                recommendation_summary=data.get("recommendation_summary"),
                confidence=data.get("confidence"),
                confidence_reason=data.get("confidence_reason"),
                categorized_signals=categorized,
                ai_agent_signals=ai_signals,
                threat_timeline=threat_timeline,
                use_case_fit=data.get("use_case_fit", {}),
                use_case_reasoning=data.get("use_case_reasoning", {}),
                actionable_hardening_steps=hardening,
                incident_velocity=data.get("incident_velocity"),
                risk_owner_routing=routing,
                sources=all_sources,
            )

        except Exception as exc:
            logger.error("Failed to construct ToolSecurityReport: %s", exc)
            return None
