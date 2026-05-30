from __future__ import annotations

import re
import logging
from typing import Optional


logger = logging.getLogger(__name__)

# Regex patterns for each security signal (case-insensitive)
_SIGNAL_PATTERNS: dict[str, str] = {
    "soc2": r"\bsoc[\s\-]?2\b",
    "iso27001": r"\biso[\s\-]?27001\b",
    "sso": (
        r"\bsso\b"
        r"|\bsingle[\s\-]sign[\s\-]on\b"
        r"|\bsaml\b"
        r"|\boauth\b"
        r"|\boidc\b"
    ),
    "mfa": (
        r"\bmfa\b"
        r"|\bmulti[\s\-]factor\b"
        r"|\b2fa\b"
        r"|\btwo[\s\-]factor\b"
        r"|\btotp\b"
    ),
    "rbac": (
        r"\brbac\b"
        r"|\brole[\s\-]based\s+access\s+control\b"
        r"|\brole[\s\-]based\s+permissions\b"
    ),
    "audit_logs": (
        r"\baudit\s+log[s]?\b"
        r"|\baudit\s+trail[s]?\b"
        r"|\baudit\s+record[s]?\b"
        r"|\baudit\s+event[s]?\b"
    ),
    "encryption": (
        r"\bencrypt(?:ed|ion|ing)?\b"
        r"|\baes[\s\-]256\b"
        r"|\bat[\s\-]rest\b"
        r"|\bin[\s\-]transit\b"
        r"|\btls\b"
        r"|\bssl\b"
        r"|\bend[\s\-]to[\s\-]end\s+encrypt\b"
    ),
    "vulnerability_disclosure": (
        r"\bvulnerability\s+disclosure\b"
        r"|\bresponsible\s+disclosure\b"
        r"|\bsecurity\s+disclosure\b"
        r"|\bcoordinated\s+disclosure\b"
        r"|\bsecurity\s+report(?:ing)?\b"
    ),
    "bug_bounty": (
        r"\bbug\s+bounty\b"
        r"|\bhackerone\b"
        r"|\bbugcrowd\b"
        r"|\bsynack\b"
        r"|\bintigriti\b"
    ),
}

_INCIDENT_KEYWORDS = [
    "breach", "incident", "vulnerability", "CVE-", "exploit", "data leak",
    "data exposure", "security advisory", "security bulletin", "zero-day",
    "unauthorized access", "attack", "compromise", "hacked", "ransomware",
]


def extract_security_signals(text: str) -> dict[str, Optional[bool]]:
    signals: dict[str, Optional[bool]] = {}
    for key, pattern in _SIGNAL_PATTERNS.items():
        found = bool(re.search(pattern, text, re.IGNORECASE))
        signals[key] = True if found else None
    logger.debug(
        "Signals found: %s",
        [k for k, v in signals.items() if v is True],
    )
    return signals


def looks_like_incident(text: str) -> bool:
    lower = text.lower()
    return any(kw.lower() in lower for kw in _INCIDENT_KEYWORDS)


def extract_company_name(text: str, tool_name: str) -> Optional[str]:
    patterns = [
        rf"{re.escape(tool_name)}\s+is\s+(?:a\s+product\s+of|made\s+by|by|from)\s+([A-Z][A-Za-z0-9\s,\.&]+?)(?:\.|,|\n|$)",
        r"(?:©|Copyright)\s*\d{4}(?:\s*-\s*\d{4})?\s+([A-Z][A-Za-z0-9\s,\.&]+?)(?:\.|,|\n|All\s+rights)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def deduplicate_sources(sources: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for url in sources:
        normalized = url.rstrip("/").lower()
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)
    return result
