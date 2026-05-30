from __future__ import annotations
import streamlit as st
from styles.theme import confidence_color, GREEN, YELLOW, RED


def _row(key: str, val: str | None, link: bool = False) -> str:
    if not val:
        val_html = '<span style="color:#475569">Not found</span>'
    elif link:
        val_html = f'<a href="{val}" target="_blank">{val}</a>'
    else:
        val_html = val
    return f"""
    <div class="as-vrow">
      <span class="as-vkey">{key}</span>
      <span class="as-vval">{val_html}</span>
    </div>"""


def render(data: dict) -> None:
    st.markdown('<div class="as-section">09 &nbsp; Vendor Profile</div>', unsafe_allow_html=True)

    meta = data.get("vendor_metadata", {}) or {}
    conf = data.get("confidence") or "unknown"
    conf_reason = data.get("confidence_reason") or ""
    conf_color = confidence_color(conf)

    left, right = st.columns([3, 2])

    with left:
        html = (
            _row("Company",         meta.get("company"))
            + _row("Product",       meta.get("product"))
            + _row("Vendor URL",    meta.get("url"),              link=True)
            + _row("Security Page", meta.get("security_url"),    link=True)
            + _row("Trust Center",  meta.get("trust_center_url"), link=True)
            + _row("Privacy Policy",meta.get("privacy_policy_url"), link=True)
            + _row("Report Date",   data.get("report_generated_at", "")[:10] or None)
        )
        st.markdown(f'<div style="background:#0e1726;border:1px solid #1a2a42;border-radius:8px;padding:0.5rem 1.1rem">{html}</div>',
                    unsafe_allow_html=True)

    with right:
        st.markdown(f"""
        <div style="background:#0e1726;border:1px solid #1a2a42;border-radius:8px;padding:1.1rem">
          <div style="font-size:0.62rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;
                      color:#64748b;margin-bottom:0.6rem">Research Confidence</div>
          <div>
            <span class="as-conf" style="background:{conf_color}22;color:{conf_color};border:1px solid {conf_color}44">
              {conf.upper()}
            </span>
          </div>
          <div style="font-size:0.78rem;color:#94a3b8;margin-top:0.8rem;line-height:1.55">
            {conf_reason or 'No confidence reasoning provided.'}
          </div>
        </div>""", unsafe_allow_html=True)
