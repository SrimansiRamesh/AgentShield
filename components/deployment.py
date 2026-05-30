from __future__ import annotations
import streamlit as st
from styles.theme import usecase_color
from utils.text import to_bullets_html


_ICONS = {"safe": "✅", "caution": "⚠️", "avoid": "🚫"}
_LABELS = {
    "internal_dev_tooling":         "Internal Dev Tooling",
    "storing_pii":                  "Storing PII",
    "regulated_industries":         "Regulated Industries",
    "agentic_autonomous_execution": "Agentic / Autonomous",
}


def render(data: dict) -> None:
    st.markdown('<div class="as-section">07 &nbsp; Deployment Suitability</div>', unsafe_allow_html=True)

    fit       = data.get("use_case_fit", {}) or {}
    reasoning = data.get("use_case_reasoning", {}) or {}

    cols = st.columns(4)
    for col, (key, label) in zip(cols, _LABELS.items()):
        verdict      = fit.get(key)
        reason       = reasoning.get(key, "")
        color        = usecase_color(verdict)
        icon         = _ICONS.get(verdict or "", "?")
        verdict_text = (verdict or "unknown").upper()

        with col:
            st.markdown(f"""
            <div class="as-uc">
              <div class="as-uc-label">{label}</div>
              <div class="as-uc-icon">{icon}</div>
              <div class="as-uc-verdict" style="color:{color}">{verdict_text}</div>
              <div class="as-uc-reason" style="font-size:0.72rem">
                {to_bullets_html(reason or 'No reasoning provided.', color='#64748b')}
              </div>
            </div>""", unsafe_allow_html=True)
