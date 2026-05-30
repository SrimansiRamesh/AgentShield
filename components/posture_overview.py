from __future__ import annotations
import streamlit as st
from styles.theme import score_color, signal_color, GREEN, YELLOW, RED


def _pct(positives: list[str], total: int) -> int:
    if total == 0:
        return 0
    return round(len(positives) / total * 100 / 5) * 5


def _domain_card(name: str, score: int, positives: list, missing: list) -> str:
    color = score_color(score)
    fill = f'<div class="as-bar-fill" style="width:{score}%;background:{color}"></div>'
    pos_str = ", ".join(positives) if positives else "none confirmed"
    miss_str = ", ".join(missing) if missing else "none"
    return f"""
    <div class="as-domain">
      <div class="as-domain-name">{name}</div>
      <div class="as-domain-score" style="color:{color}">{score}%</div>
      <div class="as-bar-bg">{fill}</div>
      <div class="as-domain-items">
        <span style="color:#10d98a">&#10003;</span> {pos_str}<br>
        <span style="color:#ef4444">&#10007;</span> {miss_str}
      </div>
    </div>"""


def render(data: dict) -> None:
    st.markdown('<div class="as-section">02 &nbsp; Security Posture Overview</div>', unsafe_allow_html=True)

    cats = data.get("categorized_signals", {})
    ai   = data.get("ai_agent_signals", {})
    meta = data.get("vendor_metadata", {})
    gov  = cats.get("compliance_and_governance", {})
    iam  = cats.get("identity_and_access", {})
    priv = cats.get("ai_data_privacy", {})
    events = data.get("threat_timeline", [])

    # ── 1. Governance & Compliance ──────────────────────────────────────────
    gov_pos = gov.get("positive", [])
    gov_mis = gov.get("missing", [])
    gov_score = gov.get("score_percentage", _pct(gov_pos, 5))

    # ── 2. Identity & Access ────────────────────────────────────────────────
    iam_pos = iam.get("positive", [])
    iam_mis = iam.get("missing", [])
    iam_score = iam.get("score_percentage", _pct(iam_pos, 4))

    # ── 3. AI Data Privacy ──────────────────────────────────────────────────
    ai_pos = priv.get("positive", [])
    ai_mis = priv.get("missing", [])
    ai_score = priv.get("score_percentage", 0)
    # Supplement with ai_agent_signals
    if ai.get("zero_data_retention") is True and "zero_data_retention" not in ai_pos:
        ai_pos.append("zero_data_retention")
    elif ai.get("zero_data_retention") is None and "zero_data_retention" not in ai_mis:
        ai_mis.append("zero_data_retention (unknown)")

    # ── 4. Agent Runtime Safety ─────────────────────────────────────────────
    saf_pos, saf_mis = [], []
    env = ai.get("execution_environment") or "unknown"
    uitl = ai.get("user_in_the_loop")
    if env == "local":
        saf_pos.append("local_execution")
    else:
        saf_mis.append(f"execution_env: {env}")
    if uitl is True:
        saf_pos.append("user_in_the_loop")
    elif uitl is False:
        saf_mis.append("user_in_the_loop")
    else:
        saf_mis.append("user_in_the_loop (unknown)")
    crit_hi = sum(1 for e in events if e.get("severity") in ("critical", "high"))
    if crit_hi == 0:
        saf_pos.append("no_critical_cves")
    else:
        saf_mis.append(f"{crit_hi} critical/high CVE(s)")
    saf_score = _pct(saf_pos, len(saf_pos) + len(saf_mis))

    # ── 5. Security Transparency ────────────────────────────────────────────
    tr_pos, tr_mis = [], []
    if meta.get("trust_center_url"):
        tr_pos.append("trust_center")
    else:
        tr_mis.append("trust_center")
    if meta.get("security_url"):
        tr_pos.append("security_page")
    else:
        tr_mis.append("security_page")
    if "vulnerability_disclosure" in gov_pos:
        tr_pos.append("vuln_disclosure")
    else:
        tr_mis.append("vuln_disclosure")
    if "bug_bounty" in gov_pos:
        tr_pos.append("bug_bounty")
    else:
        tr_mis.append("bug_bounty")
    tr_score = _pct(tr_pos, 4)

    domains = [
        ("Governance & Compliance",  gov_score, gov_pos, gov_mis),
        ("Identity & Access",        iam_score, iam_pos, iam_mis),
        ("AI Data Privacy",          ai_score,  ai_pos,  ai_mis),
        ("Agent Runtime Safety",     saf_score, saf_pos, saf_mis),
        ("Security Transparency",    tr_score,  tr_pos,  tr_mis),
    ]

    cols = st.columns(5)
    for col, (name, score, pos, mis) in zip(cols, domains):
        with col:
            st.markdown(_domain_card(name, score, pos, mis), unsafe_allow_html=True)


def render_inline(data: dict) -> None:
    """Render without section header — for embedding in columns."""
    render(data)
