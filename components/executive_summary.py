from __future__ import annotations
import streamlit as st
from styles.theme import review_color, confidence_color, GREEN, RED
from utils.text import to_bullets_html


def render(data: dict) -> None:
    st.markdown('<div class="as-section">01 &nbsp; Executive Summary</div>', unsafe_allow_html=True)

    review  = data.get("review_level") or "Unknown"
    conf    = data.get("confidence") or "unknown"
    events  = data.get("threat_timeline", [])
    crit_hi = sum(1 for e in events if e.get("severity") in ("critical", "high"))
    rc = review_color(review)
    cc = confidence_color(conf)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="as-kpi" style="--kc:{rc}">
          <div class="as-kpi-label">Review Level</div>
          <div class="as-kpi-value">{review}</div>
          <div class="as-kpi-sub">Enterprise adoption decision</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="as-kpi" style="--kc:{cc}">
          <div class="as-kpi-label">Confidence</div>
          <div class="as-kpi-value">{conf.title()}</div>
          <div class="as-kpi-sub">{to_bullets_html(data.get('confidence_reason') or 'Based on public sources')}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        evt_color = RED if len(events) > 0 else GREEN
        velocity = data.get("incident_velocity") or "From public sources"
        st.markdown(f"""
        <div class="as-kpi" style="--kc:{evt_color}">
          <div class="as-kpi-label">Total Incidents</div>
          <div class="as-kpi-value">{len(events)}</div>
          <div class="as-kpi-sub">{velocity}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        ch_color = RED if crit_hi > 0 else GREEN
        st.markdown(f"""
        <div class="as-kpi" style="--kc:{ch_color}">
          <div class="as-kpi-label">Critical / High Findings</div>
          <div class="as-kpi-value">{crit_hi}</div>
          <div class="as-kpi-sub">Requiring immediate review</div>
        </div>""", unsafe_allow_html=True)

    # Recommendation as bullets
    rec = data.get("recommendation_summary") or "No recommendation available."
    rec_html = to_bullets_html(rec, color="#cbd5e1")
    st.markdown(f"""
    <div class="as-rec">
      <div class="as-rec-label">&#9656; Security Briefing</div>
      <div class="as-rec-text" style="font-size:0.88rem">{rec_html}</div>
    </div>""", unsafe_allow_html=True)

    # Risk owner routing as bullets
    routing = data.get("risk_owner_routing") or {}
    if any(routing.values()):
        st.markdown('<div style="margin-top:1rem"></div>', unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        owners = [
            ("Security Team", routing.get("security_team")),
            ("Legal",         routing.get("legal")),
            ("Procurement",   routing.get("procurement")),
        ]
        for col, (owner, text) in zip([r1, r2, r3], owners):
            with col:
                if text:
                    st.markdown(f"""
                    <div class="as-route">
                      <div class="as-route-owner">{owner}</div>
                      <div class="as-route-text">{to_bullets_html(text)}</div>
                    </div>""", unsafe_allow_html=True)
