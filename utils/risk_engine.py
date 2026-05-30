from __future__ import annotations


def compute_risk_scores(data: dict) -> dict[str, int]:
    ai     = data.get("ai_agent_signals", {})
    cats   = data.get("categorized_signals", {})
    events = data.get("threat_timeline", [])

    crit  = sum(1 for e in events if e.get("severity") == "critical")
    high  = sum(1 for e in events if e.get("severity") == "high")
    med   = sum(1 for e in events if e.get("severity") == "medium")

    gov_missing = cats.get("compliance_and_governance", {}).get("missing", [])
    iam_missing = cats.get("identity_and_access", {}).get("missing", [])
    ai_missing  = cats.get("ai_data_privacy", {}).get("missing", [])

    exec_env = (ai.get("execution_environment") or "unknown").lower()
    uitl     = ai.get("user_in_the_loop")
    zdr      = ai.get("zero_data_retention")
    log_days = ai.get("prompt_logging_period_days")

    # ── Code Execution Risk ────────────────────────────────────────────────
    exec_risk = 35
    if exec_env == "cloud_isolated":
        exec_risk += 25
    elif exec_env == "unknown":
        exec_risk += 15
    elif exec_env == "local":
        exec_risk -= 10
    if uitl is False:
        exec_risk += 25
    elif uitl is None:
        exec_risk += 12
    exec_risk += crit * 12 + high * 6
    exec_risk = _clamp(exec_risk)

    # ── Prompt Injection Risk ──────────────────────────────────────────────
    inj_risk = 30
    if uitl is False:
        inj_risk += 25
    elif uitl is None:
        inj_risk += 12
    if zdr is False:
        inj_risk += 15
    elif zdr is None:
        inj_risk += 8
    inj_risk += crit * 10 + high * 5
    inj_risk = _clamp(inj_risk)

    # ── Data Exposure Risk ─────────────────────────────────────────────────
    data_risk = 25
    if zdr is False:
        data_risk += 30
    elif zdr is None:
        data_risk += 18
    if log_days and log_days > 30:
        data_risk += 20
    elif log_days is None:
        data_risk += 10
    if "soc2" in gov_missing:
        data_risk += 12
    if "encryption" in gov_missing:
        data_risk += 18
    data_risk = _clamp(data_risk)

    # ── Identity Risk ──────────────────────────────────────────────────────
    identity_risk = 10 + len(iam_missing) * 20
    identity_risk = _clamp(identity_risk)

    # ── Supply Chain Risk ──────────────────────────────────────────────────
    supply_risk = 20
    if "vulnerability_disclosure" in gov_missing:
        supply_risk += 22
    if "bug_bounty" in gov_missing:
        supply_risk += 18
    supply_risk += crit * 15 + high * 8 + med * 3
    supply_risk = _clamp(supply_risk)

    return {
        "Code Execution": exec_risk,
        "Prompt Injection": inj_risk,
        "Data Exposure": data_risk,
        "Identity": identity_risk,
        "Supply Chain": supply_risk,
    }


def derive_top_risks(data: dict) -> list[dict]:
    events = data.get("threat_timeline", [])
    cats   = data.get("categorized_signals", {})
    ai     = data.get("ai_agent_signals", {})
    risks: list[dict] = []

    # 1. Critical/High incidents first
    for evt in sorted(events, key=lambda e: _sev_rank(e.get("severity")), reverse=True):
        sev = evt.get("severity", "low")
        if sev not in ("critical", "high"):
            break
        risks.append({
            "title": evt["title"],
            "severity": sev,
            "explanation": evt.get("description", ""),
            "source": evt.get("source_url", ""),
        })
        if len(risks) >= 2:
            break

    # 2. Missing critical controls
    gov_miss = cats.get("compliance_and_governance", {}).get("missing", [])
    iam_miss = cats.get("identity_and_access", {}).get("missing", [])

    if "soc2" in gov_miss and len(risks) < 3:
        risks.append({
            "title": "No SOC 2 Attestation Found",
            "severity": "high",
            "explanation": "No SOC 2 Type I or Type II report was found. This leaves audit trail, access control, and operational security unverified by an independent auditor.",
            "source": "",
        })

    if not risks or "mfa" in iam_miss and len(risks) < 3:
        if "mfa" in iam_miss:
            risks.append({
                "title": "Multi-Factor Authentication Not Confirmed",
                "severity": "medium",
                "explanation": "MFA was not explicitly confirmed as available or enforced. This increases risk of account compromise via credential stuffing or phishing.",
                "source": "",
            })

    if ai.get("zero_data_retention") is None and len(risks) < 3:
        risks.append({
            "title": "Data Retention Policy Unclear",
            "severity": "medium",
            "explanation": "The vendor has not published a clear data retention policy for AI-processed inputs. Code, prompts, and sensitive content may be stored for an unknown duration.",
            "source": "",
        })

    if "bug_bounty" in gov_miss and len(risks) < 3:
        risks.append({
            "title": "No Bug Bounty Program Detected",
            "severity": "medium",
            "explanation": "No public bug bounty or coordinated disclosure program was found. Vulnerabilities may go unreported or be disclosed without vendor coordination.",
            "source": "",
        })

    return risks[:3]


def _sev_rank(sev: str | None) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get((sev or "").lower(), 0)


def _clamp(v: int) -> int:
    return max(0, min(100, v))
