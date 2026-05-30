from __future__ import annotations
import streamlit as st
from styles.theme import severity_color, RED, YELLOW, GREEN
from utils.risk_engine import derive_top_risks
from utils.text import to_bullets_html


_SEV_BG = {
    "critical": "rgba(239,68,68,0.15)",
    "high":     "rgba(239,68,68,0.10)",
    "medium":   "rgba(245,166,35,0.10)",
    "low":      "rgba(125,188,71,0.10)",
}


def render_inline(data: dict) -> None:
    """Render without section header — for embedding in columns."""
    risks = derive_top_risks(data)
    if not risks:
        st.markdown('<div class="as-empty">No significant risks identified.</div>', unsafe_allow_html=True)
        return
    for i, risk in enumerate(risks, 1):
        sev   = risk.get("severity", "medium")
        color = severity_color(sev)
        bg    = _SEV_BG.get(sev, _SEV_BG["medium"])
        src   = risk.get("source", "")
        src_html = (
            f'<a href="{src}" target="_blank" style="font-size:0.7rem;color:#60a5fa;text-decoration:none">&#8599; Source</a>'
            if src else ""
        )
        st.markdown(f"""
        <div class="as-risk" style="--rc:{color};background:{bg}">
          <div class="as-risk-num">{i:02d}</div>
          <div>
            <span class="as-badge" style="background:{color}22;color:{color};border:1px solid {color}44">{sev.upper()}</span>
            {src_html}
          </div>
          <div class="as-risk-title">{risk['title']}</div>
          <div class="as-risk-desc">{to_bullets_html(risk.get('explanation',''))}</div>
        </div>""", unsafe_allow_html=True)


def render(data: dict) -> None:
    st.markdown('<div class="as-section">03 &nbsp; Top Security Risks</div>', unsafe_allow_html=True)

    risks = derive_top_risks(data)
    if not risks:
        st.markdown('<div class="as-empty">No significant risks identified.</div>', unsafe_allow_html=True)
        return

    for i, risk in enumerate(risks, 1):
        sev   = risk.get("severity", "medium")
        color = severity_color(sev)
        bg    = _SEV_BG.get(sev, _SEV_BG["medium"])
        src   = risk.get("source", "")
        src_html = (
            f'<a href="{src}" target="_blank" style="font-size:0.7rem;color:#60a5fa;text-decoration:none">'
            f'&#8599; Source</a>'
            if src else ""
        )
        st.markdown(f"""
        <div class="as-risk" style="--rc:{color};background:{bg}">
          <div class="as-risk-num">{i:02d}</div>
          <div>
            <span class="as-badge" style="background:{color}22;color:{color};border:1px solid {color}44">
              {sev.upper()}
            </span>
            {src_html}
          </div>
          <div class="as-risk-title">{risk['title']}</div>
          <div class="as-risk-desc">{to_bullets_html(risk.get('explanation',''))}</div>
        </div>""", unsafe_allow_html=True)
