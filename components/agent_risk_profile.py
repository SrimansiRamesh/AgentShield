from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
from styles.theme import score_color, RED, YELLOW, GREEN, BG, PLOTLY_BASE
from utils.risk_engine import compute_risk_scores


def render_inline(data: dict) -> None:
    """Render without section header — for embedding in columns."""
    render(data)


def render(data: dict) -> None:
    st.markdown('<div class="as-section">05 &nbsp; Agent Risk Profile</div>', unsafe_allow_html=True)

    scores = compute_risk_scores(data)
    cats   = list(scores.keys())
    vals   = list(scores.values())

    left, right = st.columns([3, 2])

    with left:
        # Radar chart
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(239,68,68,0.10)",
            line=dict(color="#ef4444", width=2),
            marker=dict(size=7, color="#ef4444", line=dict(color="#ff7070", width=1)),
            name="Risk Score",
        ))
        layout = {**PLOTLY_BASE, "margin": dict(l=60, r=60, t=30, b=30)}
        fig.update_layout(
            **layout,
            polar=dict(
                bgcolor="rgba(14,23,38,0.5)",
                radialaxis=dict(
                    range=[0, 100],
                    tickvals=[25, 50, 75, 100],
                    ticktext=["25", "50", "75", "100"],
                    tickfont=dict(size=9, color="#64748b"),
                    gridcolor="#1a2a42",
                    linecolor="#1a2a42",
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color="#e2e8f0"),
                    gridcolor="#1a2a42",
                    linecolor="#1a2a42",
                    rotation=90,
                    direction="clockwise",
                ),
            ),
            showlegend=False,
            height=360,
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("<br>", unsafe_allow_html=True)
        for name, score in scores.items():
            color = score_color(100 - score)  # invert: high score = high risk = red
            risk_color = score_color(100 - score)
            label = "HIGH" if score >= 70 else "MED" if score >= 40 else "LOW"
            label_color = RED if score >= 70 else YELLOW if score >= 40 else GREEN
            st.markdown(f"""
            <div class="as-rbar-wrap">
              <div class="as-rbar-row">
                <span class="as-rbar-name">{name}</span>
                <span class="as-rbar-score" style="color:{label_color}">{score} &nbsp;
                  <span style="font-size:0.6rem">{label}</span>
                </span>
              </div>
              <div class="as-bar-bg">
                <div class="as-bar-fill" style="width:{score}%;background:{label_color}"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:1rem;font-size:0.68rem;color:#64748b;line-height:1.5">
          Scores are heuristic-derived from security signals,<br>
          AI agent posture, and threat history.<br>
          Higher = greater risk.
        </div>""", unsafe_allow_html=True)
