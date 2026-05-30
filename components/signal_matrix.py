from __future__ import annotations
import streamlit as st
from styles.theme import signal_color, GREEN, YELLOW, RED


_SIGNALS: list[tuple[str, str]] = [
    ("SOC 2",                    "soc2"),
    ("ISO 27001",                "iso27001"),
    ("SSO",                      "sso"),
    ("MFA / 2FA",                "mfa"),
    ("RBAC",                     "rbac"),
    ("Audit Logs",               "audit_logs"),
    ("Encryption",               "encryption"),
    ("Vulnerability Disclosure", "vulnerability_disclosure"),
    ("Bug Bounty",               "bug_bounty"),
    ("Zero Data Retention",      "zero_data_retention"),
    ("User in the Loop",         "user_in_the_loop"),
]


def _pill(val) -> str:
    if val is True:
        return f'<span class="as-signal-pill" style="background:rgba(16,217,138,0.12);color:#10d98a">&#10003; Confirmed</span>'
    if val is False:
        return f'<span class="as-signal-pill" style="background:rgba(239,68,68,0.12);color:#ef4444">&#10007; Absent</span>'
    return f'<span class="as-signal-pill" style="background:rgba(245,166,35,0.10);color:#f5a623">&#63; Unknown</span>'


def _get_val(label_key: str, data: dict):
    cats = data.get("categorized_signals", {})
    ai   = data.get("ai_agent_signals", {})

    # AI signals
    if label_key == "zero_data_retention":
        return ai.get("zero_data_retention")
    if label_key == "user_in_the_loop":
        return ai.get("user_in_the_loop")

    # Standard signals: check positive/missing lists
    for cat in cats.values():
        if label_key in (cat.get("positive") or []):
            return True
        if label_key in (cat.get("missing") or []):
            return False

    return None


def render(data: dict) -> None:
    st.markdown('<div class="as-section">04 &nbsp; Security Signal Matrix</div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    mid = len(_SIGNALS) // 2 + len(_SIGNALS) % 2

    for col, signals in [(left, _SIGNALS[:mid]), (right, _SIGNALS[mid:])]:
        with col:
            rows_html = ""
            for label, key in signals:
                val = _get_val(key, data)
                rows_html += f"""
                <div class="as-signal-row">
                  <span class="as-signal-name">{label}</span>
                  {_pill(val)}
                </div>"""
            st.markdown(rows_html, unsafe_allow_html=True)
    _legend()


def render_inline(data: dict) -> None:
    """Render without section header — for embedding in columns."""
    for signals in [_SIGNALS]:
        rows_html = ""
        for label, key in signals:
            val = _get_val(key, data)
            rows_html += f"""
            <div class="as-signal-row">
              <span class="as-signal-name">{label}</span>
              {_pill(val)}
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)
    _legend()


def _legend() -> None:
    st.markdown("""
    <div style="margin-top:0.6rem;font-size:0.68rem;color:#64748b">
      <span style="color:#10d98a">&#10003; Confirmed</span> &nbsp;&nbsp;
      <span style="color:#f5a623">? Unknown / not disclosed</span> &nbsp;&nbsp;
      <span style="color:#ef4444">&#10007; Explicitly absent</span>
    </div>""", unsafe_allow_html=True)
