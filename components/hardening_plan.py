from __future__ import annotations
import streamlit as st
from styles.theme import RED, YELLOW, GREEN
from utils.text import to_bullets_html


def _priority(index: int, data: dict) -> tuple[str, str]:
    events = data.get("threat_timeline", [])
    has_crit = any(e.get("severity") in ("critical", "high") for e in events)
    if index == 0 and has_crit:
        return "High", RED
    if index < 2:
        return "Medium", YELLOW
    return "Low", GREEN


def render_inline(data: dict) -> None:
    """Render steps only — no section header, for use inside an expander."""
    steps = data.get("actionable_hardening_steps", []) or []
    if not steps:
        st.markdown('<div class="as-empty">No hardening steps generated.</div>', unsafe_allow_html=True)
        return
    for i, step in enumerate(steps):
        pri_label, pri_color = _priority(i, data)
        title = step.get("title", "Untitled step")
        desc  = step.get("description", "")
        st.markdown(f"""
        <div class="as-hard">
          <div class="as-hard-icon">&#9633;</div>
          <div>
            <div class="as-hard-title">{title}
              <span class="as-pri" style="background:{pri_color}22;color:{pri_color};border:1px solid {pri_color}44">{pri_label}</span>
            </div>
            <div class="as-hard-desc">{to_bullets_html(desc)}</div>
          </div>
        </div>""", unsafe_allow_html=True)


def render(data: dict) -> None:
    st.markdown('<div class="as-section">08 &nbsp; Hardening Plan</div>', unsafe_allow_html=True)

    steps = data.get("actionable_hardening_steps", []) or []
    if not steps:
        st.markdown('<div class="as-empty">No hardening steps generated.</div>', unsafe_allow_html=True)
        return

    for i, step in enumerate(steps):
        pri_label, pri_color = _priority(i, data)
        title = step.get("title", "Untitled step")
        desc  = step.get("description", "")
        st.markdown(f"""
        <div class="as-hard">
          <div class="as-hard-icon">&#9633;</div>
          <div>
            <div class="as-hard-title">
              {title}
              <span class="as-pri" style="background:{pri_color}22;color:{pri_color};border:1px solid {pri_color}44">
                {pri_label}
              </span>
            </div>
            <div class="as-hard-desc">{to_bullets_html(desc)}</div>
          </div>
        </div>""", unsafe_allow_html=True)
