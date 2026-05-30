"""AgentShield — AI Tool Security Assessment Platform."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="AgentShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from styles.theme import CSS, review_color, confidence_color
from utils.data_loader import load_report, _normalize
from utils.risk_engine import derive_top_risks
import components.executive_summary  as sec_exec
import components.posture_overview   as sec_posture
import components.top_risks          as sec_risks
import components.signal_matrix      as sec_signals
import components.agent_risk_profile as sec_radar
import components.threat_timeline    as sec_timeline
import components.deployment         as sec_deploy
import components.hardening_plan     as sec_harden
import components.sources            as sec_sources

st.markdown(CSS, unsafe_allow_html=True)


# ── API key resolution (env → Streamlit secrets) ──────────────────────────────
def _get_secret(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        try:
            val = st.secrets.get(key, "")
        except Exception:
            pass
    return val or ""


ANTHROPIC_KEY = _get_secret("ANTHROPIC_API_KEY")
BD_TOKEN      = _get_secret("BRIGHTDATA_API_TOKEN")
KEYS_PRESENT  = bool(ANTHROPIC_KEY and BD_TOKEN)


# ── Research runner ───────────────────────────────────────────────────────────
def run_research(tool_name: str) -> dict:
    from research_agent import ResearchAgent
    agent = ResearchAgent(api_key=ANTHROPIC_KEY, brightdata_api_token=BD_TOKEN)
    report = asyncio.run(agent.research(tool_name))
    return _normalize(json.loads(report.to_json()))


# ── Session state defaults ────────────────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "landing"
if "report_data" not in st.session_state:
    st.session_state.report_data = None
if "tool_name" not in st.session_state:
    st.session_state.tool_name = ""
if "error" not in st.session_state:
    st.session_state.error = ""


# ── Sidebar (only on dashboard view) ─────────────────────────────────────────
if st.session_state.view == "dashboard" and st.session_state.report_data:
    data = st.session_state.report_data
    meta    = data.get("vendor_metadata", {}) or {}
    product = meta.get("product") or data.get("tool_name", "")
    company = meta.get("company") or ""
    review  = data.get("review_level") or ""
    rc      = review_color(review)
    conf    = data.get("confidence") or ""
    cc      = confidence_color(conf)
    ts      = (data.get("report_generated_at") or "")[:10]

    with st.sidebar:
        st.markdown("""
        <div style="padding:0.25rem 0 0.8rem">
          <div style="font-size:1.05rem;font-weight:800;letter-spacing:0.06em;color:#e2e8f0">
            Agent<span style="color:#3b82f6">Shield</span>
          </div>
          <div style="font-size:0.6rem;color:#64748b;letter-spacing:0.12em;margin-top:2px">
            AI TOOL SECURITY ASSESSMENT
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("← New Analysis", use_container_width=True):
            st.session_state.view = "landing"
            st.session_state.report_data = None
            st.session_state.tool_name = ""
            st.session_state.error = ""
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="background:#0e1726;border:1px solid #1a2a42;border-radius:8px;padding:0.9rem 1rem">
          <div style="font-size:0.9rem;font-weight:700;color:#e2e8f0;margin-bottom:0.15rem">{product}</div>
          <div style="font-size:0.72rem;color:#64748b;margin-bottom:0.7rem">{company}</div>
          <div style="font-size:0.65rem;font-weight:700;color:{rc};letter-spacing:0.06em">{review}</div>
          <div style="font-size:0.65rem;color:{cc};margin-top:0.2rem">Confidence: {conf}</div>
          {f'<div style="font-size:0.62rem;color:#475569;margin-top:0.4rem">Scanned {ts}</div>' if ts else ''}
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        compare_file = st.file_uploader("Compare with another report", type=["json"],
                                        key="compare", label_visibility="visible")

        st.markdown("---")
        tool_slug = (data.get("tool_name") or "tool").lower().replace(" ", "_")
        md_lines = [
            f"# AgentShield: {product}", f"**Company:** {company}",
            f"**Review Level:** {review}", f"**Confidence:** {conf}", "",
            "## Recommendation", data.get("recommendation_summary", ""), "",
            "## Top Risks",
        ]
        for r in derive_top_risks(data):
            md_lines.append(f"- **[{r['severity'].upper()}]** {r['title']}: {r.get('explanation','')}")
        md_lines += ["", "## Sources", *[f"- {s}" for s in data.get("sources", [])]]

        st.download_button(
            "Download summary (.md)",
            data="\n".join(md_lines),
            file_name=f"{tool_slug}_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )

        # Upload own JSON
        st.markdown("---")
        uploaded = st.file_uploader("Or load a saved report", type=["json"],
                                    key="upload_saved", label_visibility="visible")
        if uploaded:
            st.session_state.report_data = load_report(uploaded.read())
            st.rerun()


# ════════════════════════════════════════════════════════
# VIEW: LANDING
# ════════════════════════════════════════════════════════
if st.session_state.view == "landing":

    st.markdown("""
    <div style="text-align:center;padding:3.5rem 1rem 2rem">
      <div style="font-size:2.8rem;margin-bottom:0.5rem">🛡️</div>
      <div style="font-size:2.2rem;font-weight:800;color:#e2e8f0;letter-spacing:-0.01em;margin-bottom:0.5rem">
        Agent<span style="color:#3b82f6">Shield</span>
      </div>
      <div style="font-size:1rem;color:#64748b;max-width:520px;margin:0 auto;line-height:1.6">
        Enter any AI tool name and get an executive security assessment —
        SOC 2, CVEs, data retention, incident history, and deployment risk — in minutes.
      </div>
    </div>""", unsafe_allow_html=True)

    # Search box
    col_pad, col_input, col_btn, col_pad2 = st.columns([1, 4, 1.2, 1])
    with col_input:
        tool_input = st.text_input(
            "tool",
            placeholder="e.g. Cursor, CrewAI, LangGraph, Claude Code...",
            label_visibility="collapsed",
            key="tool_input_field",
        )
    with col_btn:
        analyze = st.button("Analyze →", type="primary", use_container_width=True)

    # Example chips
    st.markdown("""
    <div style="text-align:center;margin-top:0.5rem;margin-bottom:2rem">
      <span style="font-size:0.72rem;color:#475569;margin-right:0.5rem">Try:</span>
    </div>""", unsafe_allow_html=True)

    chip_cols = st.columns([2, 1, 1, 1, 1, 1, 2])
    examples = ["Cursor", "CrewAI", "LangGraph", "GitHub Copilot", "Replit"]
    for col, name in zip(chip_cols[1:6], examples):
        with col:
            if st.button(name, use_container_width=True, key=f"chip_{name}"):
                tool_input = name
                analyze = True

    # Error display
    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = ""

    # How it works
    st.markdown("""
    <div style="max-width:860px;margin:1rem auto 0;display:grid;grid-template-columns:repeat(3,1fr);gap:1rem">
      <div style="background:#0e1726;border:1px solid #1a2a42;border-radius:8px;padding:1.2rem;text-align:center">
        <div style="font-size:1.5rem;margin-bottom:0.5rem">🔍</div>
        <div style="font-size:0.8rem;font-weight:700;color:#e2e8f0;margin-bottom:0.3rem">Live Web Research</div>
        <div style="font-size:0.73rem;color:#64748b;line-height:1.5">
          Searches vendor sites, security pages, CVE databases, and news sources in real time
        </div>
      </div>
      <div style="background:#0e1726;border:1px solid #1a2a42;border-radius:8px;padding:1.2rem;text-align:center">
        <div style="font-size:1.5rem;margin-bottom:0.5rem">🛡️</div>
        <div style="font-size:0.8rem;font-weight:700;color:#e2e8f0;margin-bottom:0.3rem">Security Signal Extraction</div>
        <div style="font-size:0.73rem;color:#64748b;line-height:1.5">
          Detects SOC 2, MFA, RBAC, encryption, bug bounty, data retention and more
        </div>
      </div>
      <div style="background:#0e1726;border:1px solid #1a2a42;border-radius:8px;padding:1.2rem;text-align:center">
        <div style="font-size:1.5rem;margin-bottom:0.5rem">📊</div>
        <div style="font-size:0.8rem;font-weight:700;color:#e2e8f0;margin-bottom:0.3rem">Executive Risk Report</div>
        <div style="font-size:0.73rem;color:#64748b;line-height:1.5">
          Produces a structured security assessment with deployment guidance and hardening steps
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Upload existing JSON
    st.markdown("<div style='max-width:860px;margin:1.5rem auto 0'>", unsafe_allow_html=True)
    with st.expander("Or upload an existing report JSON"):
        uploaded = st.file_uploader("Upload report", type=["json"], label_visibility="collapsed")
        if uploaded:
            st.session_state.report_data = load_report(uploaded.read())
            st.session_state.view = "dashboard"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if not KEYS_PRESENT:
        st.warning(
            "API keys not configured. Set `ANTHROPIC_API_KEY` and `BRIGHTDATA_API_TOKEN` "
            "as environment variables or Streamlit secrets to enable live research.",
            icon="⚠️",
        )

    # Trigger analysis
    if analyze and tool_input and tool_input.strip():
        st.session_state.tool_name = tool_input.strip()
        st.session_state.view = "researching"
        st.rerun()
    elif analyze:
        st.warning("Please enter a tool name first.")


# ════════════════════════════════════════════════════════
# VIEW: RESEARCHING
# ════════════════════════════════════════════════════════
elif st.session_state.view == "researching":
    tool = st.session_state.tool_name

    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem 1.5rem">
      <div style="font-size:1.6rem;font-weight:800;color:#e2e8f0;margin-bottom:0.4rem">
        Researching <span style="color:#3b82f6">{tool}</span>
      </div>
      <div style="font-size:0.85rem;color:#64748b">
        Searching vendor sites, security pages, CVE databases, and public incident records.<br>
        This typically takes <strong style="color:#e2e8f0">3 – 6 minutes</strong>.
      </div>
    </div>""", unsafe_allow_html=True)

    steps = [
        f"Locating {tool}'s official website and documentation",
        "Scraping security pages and trust center",
        "Searching for SOC 2, ISO 27001, and compliance certifications",
        "Scanning CVE databases and public incident reports",
        "Analyzing AI-specific risks and data retention policies",
        "Generating executive risk assessment",
    ]
    steps_html = "".join(
        f'<div style="display:flex;align-items:center;gap:0.6rem;padding:0.35rem 0;'
        f'font-size:0.8rem;color:#64748b">'
        f'<span style="color:#3b82f6">›</span> {s}</div>'
        for s in steps
    )
    st.markdown(f"""
    <div style="max-width:500px;margin:0 auto;background:#0e1726;border:1px solid #1a2a42;
                border-radius:8px;padding:1.2rem 1.5rem">
      {steps_html}
    </div>""", unsafe_allow_html=True)

    if not KEYS_PRESENT:
        st.error("API keys missing. Set ANTHROPIC_API_KEY and BRIGHTDATA_API_TOKEN.")
        if st.button("Go back"):
            st.session_state.view = "landing"
            st.rerun()
    else:
        with st.spinner("Agent running..."):
            try:
                data = run_research(tool)
                st.session_state.report_data = data
                st.session_state.view = "dashboard"
                st.rerun()
            except Exception as exc:
                st.session_state.error = f"Research failed: {exc}"
                st.session_state.view = "landing"
                st.rerun()


# ════════════════════════════════════════════════════════
# VIEW: DASHBOARD
# ════════════════════════════════════════════════════════
elif st.session_state.view == "dashboard":
    data = st.session_state.report_data
    if not data:
        st.session_state.view = "landing"
        st.rerun()

    # Compare mode
    compare_data: dict = {}
    try:
        cf = st.session_state.get("compare")
        if cf:
            compare_data = load_report(cf.read())
    except Exception:
        pass

    meta    = data.get("vendor_metadata", {}) or {}
    product = meta.get("product") or data.get("tool_name", "")
    company = meta.get("company") or ""
    review  = data.get("review_level") or ""
    rc      = review_color(review)

    st.markdown(f"""
    <div class="as-header">
      <div>
        <div class="as-wordmark">Agent<span>Shield</span></div>
        <div class="as-tagline">AI TOOL SECURITY ASSESSMENT PLATFORM</div>
      </div>
      <div class="as-header-right">
        <div class="as-header-tool">{product}{" &nbsp;&middot;&nbsp; " + company if company else ""}</div>
        <div class="as-header-meta" style="color:{rc};font-weight:700">{review}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if compare_data:
        name_a = compare_data.get("vendor_metadata", {}).get("product") or compare_data.get("tool_name", "Report A")
        name_b = product or "Report B"
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f'<div style="text-align:center;font-weight:700;color:#3b82f6;padding:0.4rem 0 0">{name_a}</div>', unsafe_allow_html=True)
            sec_exec.render(compare_data)
            sec_posture.render(compare_data)
            sec_risks.render(compare_data)
            sec_signals.render(compare_data)
        with col_b:
            st.markdown(f'<div style="text-align:center;font-weight:700;color:#10d98a;padding:0.4rem 0 0">{name_b}</div>', unsafe_allow_html=True)
            sec_exec.render(data)
            sec_posture.render(data)
            sec_risks.render(data)
            sec_signals.render(data)
    else:
        sec_exec.render(data)

        st.markdown('<div class="as-section">Security Posture &amp; Top Risks</div>', unsafe_allow_html=True)
        col_left, col_right = st.columns([3, 2])
        with col_left:
            sec_posture.render_inline(data)
        with col_right:
            sec_risks.render_inline(data)

        st.markdown('<div class="as-section">Signal Matrix &amp; Agent Risk Profile</div>', unsafe_allow_html=True)
        col_sig, col_rad = st.columns([2, 3])
        with col_sig:
            sec_signals.render_inline(data)
        with col_rad:
            sec_radar.render_inline(data)

        sec_timeline.render(data)
        sec_deploy.render(data)

        st.markdown('<div class="as-section">Hardening Plan</div>', unsafe_allow_html=True)
        with st.expander(f"View {len(data.get('actionable_hardening_steps') or [])} remediation steps"):
            sec_harden.render_inline(data)

        sec_sources.render(data)
