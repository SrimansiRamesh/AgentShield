#!/usr/bin/env python3
"""AgentShield: Security posture research for AI tools."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from research_agent import ResearchAgent

_LOG = logging.getLogger(__name__)


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    for noisy in ("httpx", "httpcore", "mcp", "anyio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agentshield",
        description="Research the security posture of an AI tool using public sources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py Cursor\n"
            "  python main.py CrewAI --output crew_report.json\n"
            "  python main.py LangGraph --max-iterations 30 --verbose\n"
        ),
    )
    parser.add_argument(
        "tool_name",
        help="Name of the AI tool to research (e.g. Cursor, CrewAI, LangGraph)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Path to save the JSON report (default: <tool_name>_security_report.json)",
    )
    parser.add_argument(
        "--model", "-m",
        default="claude-opus-4-8",
        help="Claude model to use (default: claude-opus-4-8)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=25,
        help="Maximum research iterations (default: 25)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def _check_env() -> list[str]:
    missing: list[str] = []
    if not os.environ.get("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.environ.get("BRIGHTDATA_API_TOKEN"):
        missing.append("BRIGHTDATA_API_TOKEN")
    return missing


def _signal_icon(value: bool | None) -> str:
    if value is True:
        return "[+]"
    if value is False:
        return "[-]"
    return "[?]"


async def run(args: argparse.Namespace) -> int:
    missing = _check_env()
    if missing:
        for var in missing:
            print(f"Error: {var} environment variable is not set", file=sys.stderr)
        print(
            "\nSet them in your shell or create a .env file and load it with:\n"
            "  export $(cat .env | xargs)",
            file=sys.stderr,
        )
        return 1

    safe_name = args.tool_name.lower().replace(" ", "_").replace("/", "_")
    output_path: Path = args.output or Path(f"{safe_name}_security_report.json")

    print(f"\nAgentShield: Researching '{args.tool_name}'")
    print(f"Model: {args.model}  |  Max iterations: {args.max_iterations}")
    print("-" * 60)

    agent = ResearchAgent(
        model=args.model,
        max_iterations=args.max_iterations,
    )

    try:
        report = await agent.research(args.tool_name)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as exc:
        _LOG.exception("Research failed")
        print(f"\nError: {exc}", file=sys.stderr)
        return 1

    report_json = report.to_json(indent=2)
    output_path.write_text(report_json, encoding="utf-8")

    # Print summary
    print(f"\nReport saved: {output_path}")
    print("\nSummary")
    print("-------")
    print(f"  Company:        {report.company or 'Unknown'}")
    print(f"  Product:        {report.product_name or report.tool_name}")
    print(f"  Vendor URL:     {report.vendor_url or 'Not found'}")
    print(f"  Security page:  {report.security_page_url or 'Not found'}")
    print(f"  Trust center:   {report.trust_center_url or 'Not found'}")
    print(f"  Privacy policy: {report.privacy_policy_url or 'Not found'}")

    print("\nSecurity signals:")
    signals = report.security_signals.model_dump()
    label_map = {
        "soc2": "SOC 2",
        "iso27001": "ISO 27001",
        "sso": "SSO",
        "mfa": "MFA / 2FA",
        "rbac": "RBAC",
        "audit_logs": "Audit Logs",
        "encryption": "Encryption",
        "vulnerability_disclosure": "Vuln. Disclosure",
        "bug_bounty": "Bug Bounty",
    }
    for key, label in label_map.items():
        icon = _signal_icon(signals.get(key))
        print(f"  {icon}  {label}")

    print(f"\nPublic incidents found: {len(report.public_incidents)}")
    for inc in report.public_incidents:
        date_str = f" ({inc.date})" if inc.date else ""
        sev_str = f" [{inc.severity}]" if inc.severity else ""
        print(f"  * {inc.title}{date_str}{sev_str}")
        print(f"    {inc.source_url}")

    print(f"\nSources consulted: {len(report.sources)}")
    for src in report.sources[:10]:
        print(f"  {src}")
    if len(report.sources) > 10:
        print(f"  ... and {len(report.sources) - 10} more (see full report)")

    return 0


def main() -> None:
    args = _parse_args()
    _setup_logging(args.verbose)
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
