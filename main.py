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
    meta = report.vendor_metadata
    print(f"  Company:        {meta.company or 'Unknown'}")
    print(f"  Product:        {meta.product or report.tool_name}")
    print(f"  Vendor URL:     {meta.url or 'Not found'}")
    print(f"  Security page:  {meta.security_url or 'Not found'}")
    print(f"  Trust center:   {meta.trust_center_url or 'Not found'}")
    print(f"  Privacy policy: {meta.privacy_policy_url or 'Not found'}")
    print(f"\n  Review level:   {report.review_level or 'Unknown'}")
    print(f"  Confidence:     {report.confidence or 'Unknown'}")
    if report.recommendation_summary:
        print(f"\n  Recommendation: {report.recommendation_summary}")

    print("\nCategory scores:")
    cats = report.categorized_signals
    for label, cat in [
        ("Compliance & Governance", cats.compliance_and_governance),
        ("Identity & Access     ", cats.identity_and_access),
        ("AI Data Privacy       ", cats.ai_data_privacy),
    ]:
        bar = "#" * (cat.score_percentage // 10) + "." * (10 - cat.score_percentage // 10)
        print(f"  {label}  [{bar}] {cat.score_percentage}%")
        if cat.positive:
            print(f"    + {', '.join(cat.positive)}")
        if cat.missing:
            print(f"    - {', '.join(cat.missing)}")

    ai = report.ai_agent_signals
    print("\nAI agent signals:")
    print(f"  Zero data retention:   {_signal_icon(ai.zero_data_retention)}")
    print(f"  User in the loop:      {_signal_icon(ai.user_in_the_loop)}")
    print(f"  Execution environment: {ai.execution_environment or '?'}")
    if ai.prompt_logging_period_days is not None:
        print(f"  Prompt log retention:  {ai.prompt_logging_period_days} days")

    print(f"\nThreat timeline: {len(report.threat_timeline)} event(s)")
    for evt in report.threat_timeline:
        date_str = f" ({evt.date})" if evt.date else ""
        sev_str = f" [{evt.severity}]" if evt.severity else ""
        cve_str = f" {evt.cve_id}" if evt.cve_id else ""
        print(f"  * {evt.title}{date_str}{sev_str}{cve_str}")
        print(f"    {evt.source_url}")

    if report.actionable_hardening_steps:
        print("\nHardening steps:")
        for step in report.actionable_hardening_steps:
            print(f"  > {step.title}")

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
