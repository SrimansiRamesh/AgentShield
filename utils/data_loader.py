from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_report(raw: bytes | str) -> dict:
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return _normalize(json.loads(raw))
    except Exception as exc:
        logger.error("Failed to parse report: %s", exc)
        return {}


def load_report_file(path: str | Path) -> dict:
    try:
        return _normalize(json.loads(Path(path).read_text()))
    except Exception as exc:
        logger.error("Failed to load report file: %s", exc)
        return {}


def _cat(raw: dict, key: str) -> dict:
    r = raw.get(key, {})
    return {
        "score_percentage": int(r.get("score_percentage", 0)),
        "positive": list(r.get("positive", [])),
        "missing":  list(r.get("missing", [])),
    }


def _normalize(d: dict) -> dict:
    meta = d.get("vendor_metadata", {}) or {}
    ai   = d.get("ai_agent_signals", {}) or {}
    cats = d.get("categorized_signals", {}) or {}

    return {
        "tool_name": d.get("tool_name") or "Unknown Tool",
        "vendor_metadata": {
            "company":          meta.get("company"),
            "product":          meta.get("product"),
            "url":              meta.get("url"),
            "security_url":     meta.get("security_url"),
            "trust_center_url": meta.get("trust_center_url"),
            "privacy_policy_url": meta.get("privacy_policy_url"),
        },
        "review_level":           d.get("review_level"),
        "recommendation_summary": d.get("recommendation_summary"),
        "confidence":             d.get("confidence"),
        "confidence_reason":      d.get("confidence_reason"),
        "categorized_signals": {
            "compliance_and_governance": _cat(cats, "compliance_and_governance"),
            "identity_and_access":       _cat(cats, "identity_and_access"),
            "ai_data_privacy":           _cat(cats, "ai_data_privacy"),
        },
        "ai_agent_signals": {
            "zero_data_retention":       ai.get("zero_data_retention"),
            "prompt_logging_period_days": ai.get("prompt_logging_period_days"),
            "execution_environment":     ai.get("execution_environment"),
            "user_in_the_loop":          ai.get("user_in_the_loop"),
        },
        "threat_timeline": [_norm_event(e) for e in (d.get("threat_timeline") or [])],
        "use_case_fit":     dict(d.get("use_case_fit") or {}),
        "use_case_reasoning": dict(d.get("use_case_reasoning") or {}),
        "actionable_hardening_steps": list(d.get("actionable_hardening_steps") or []),
        "incident_velocity":  d.get("incident_velocity"),
        "risk_owner_routing": dict(d.get("risk_owner_routing") or {}),
        "sources":            list(d.get("sources") or []),
        "report_generated_at": d.get("report_generated_at", ""),
    }


def _norm_event(e: dict) -> dict:
    return {
        "id":          e.get("id"),
        "title":       e.get("title") or "Unknown Incident",
        "date":        e.get("date"),
        "severity":    (e.get("severity") or "low").lower(),
        "description": e.get("description") or "",
        "cve_id":      e.get("cve_id"),
        "patched":     e.get("patched"),
        "source_url":  e.get("source_url") or "",
        "ui_badge_color": e.get("ui_badge_color"),
    }
