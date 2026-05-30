from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from styles.theme import severity_color, BG, PLOTLY_BASE
from utils.text import to_bullets_html


_SEV_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def render(data: dict) -> None:
    st.markdown('<div class="as-section">06 &nbsp; Threat Timeline</div>', unsafe_allow_html=True)

    events = data.get("threat_timeline", [])
    if not events:
        st.markdown('<div class="as-empty">No threat events recorded for this tool.</div>', unsafe_allow_html=True)
        return

    sorted_events = sorted(
        events,
        key=lambda e: (e.get("date") or "0000-00-00"),
        reverse=True,
    )

    # ── Plotly scatter timeline ─────────────────────────────────────────────
    dated = [e for e in sorted_events if e.get("date")]
    if dated:
        try:
            import pandas as pd
            dates  = pd.to_datetime([e["date"] for e in dated], errors="coerce")
            labels = [e.get("title", "")[:45] for e in dated]
            colors = [severity_color(e.get("severity")) for e in dated]
            sizes  = [16 if e.get("severity") in ("critical", "high") else 11 for e in dated]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=[0] * len(dated),
                mode="markers",
                marker=dict(size=sizes, color=colors, line=dict(color="#0a0e17", width=2)),
                customdata=labels,
                hovertemplate="<b>%{customdata}</b><br>%{x|%Y-%m-%d}<extra></extra>",
            ))
            layout = {**PLOTLY_BASE, "margin": dict(l=10, r=10, t=20, b=10)}
            fig.update_layout(
                **layout,
                height=90,
                showlegend=False,
                xaxis=dict(showgrid=False, zeroline=False,
                           tickfont=dict(size=10, color="#64748b"), linecolor="#1a2a42"),
                yaxis=dict(visible=False, range=[-1, 2], showgrid=False, zeroline=False),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    # ── Expandable event cards ──────────────────────────────────────────────
    for evt in sorted_events:
        sev   = evt.get("severity", "low")
        color = severity_color(sev)
        date  = evt.get("date") or "Date unknown"
        cve   = evt.get("cve_id")
        pat   = evt.get("patched")
        src   = evt.get("source_url", "")

        cve_html     = f'<span class="as-tag as-tag-cve">{cve}</span>' if cve else ""
        patched_html = (
            '<span class="as-tag as-tag-ok">Patched</span>' if pat is True
            else '<span class="as-tag as-tag-warn">Unpatched</span>' if pat is False
            else ""
        )
        src_html = (
            f'<a href="{src}" target="_blank" class="as-tag" '
            f'style="color:#60a5fa;border-color:rgba(96,165,250,0.3);background:rgba(96,165,250,0.08)">'
            f'&#8599; Source</a>'
            if src else ""
        )

        with st.expander(f"{'🔴' if sev in ('critical','high') else '🟡' if sev == 'medium' else '🟢'} {evt['title']}  ·  {date}"):
            st.markdown(f"""
            <div class="as-evt" style="--ec:{color};border:none;padding:0">
              <div class="as-evt-meta">
                <span class="as-badge" style="background:{color}22;color:{color};border:1px solid {color}44">
                  {sev.upper()}
                </span>
                {cve_html} {patched_html} {src_html}
              </div>
              <div class="as-evt-desc">{to_bullets_html(evt.get('description',''))}</div>
            </div>""", unsafe_allow_html=True)
