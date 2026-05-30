from __future__ import annotations

# ── Palette ──────────────────────────────────────────────────────────────────
GREEN        = "#10d98a"
GREEN_DIM    = "rgba(16,217,138,0.10)"
GREEN_BORDER = "rgba(16,217,138,0.30)"

YELLOW        = "#f5a623"
YELLOW_DIM    = "rgba(245,166,35,0.10)"
YELLOW_BORDER = "rgba(245,166,35,0.30)"

RED        = "#ef4444"
RED_DIM    = "rgba(239,68,68,0.10)"
RED_BORDER = "rgba(239,68,68,0.30)"

BLUE        = "#3b82f6"
BLUE_DIM    = "rgba(59,130,246,0.10)"
BLUE_BORDER = "rgba(59,130,246,0.30)"

BG      = "#0a0e17"
BG_CARD = "#0e1726"
BORDER  = "#1a2a42"
TEXT    = "#e2e8f0"
MUTED   = "#64748b"


# ── Semantic helpers ──────────────────────────────────────────────────────────
def review_color(level: str | None) -> str:
    if not level:
        return YELLOW
    l = level.lower()
    if "low" in l:
        return GREEN
    if "high" in l:
        return RED
    return YELLOW


def severity_color(sev: str | None) -> str:
    if not sev:
        return YELLOW
    s = sev.lower()
    if s in ("critical", "high"):
        return RED
    if s == "medium":
        return YELLOW
    return "#7dbc47"


def signal_color(val) -> str:
    if val is True:
        return GREEN
    if val is False:
        return RED
    return YELLOW


def score_color(score: int) -> str:
    if score >= 70:
        return GREEN
    if score >= 40:
        return YELLOW
    return RED


def usecase_color(val: str | None) -> str:
    if val == "safe":
        return GREEN
    if val == "avoid":
        return RED
    return YELLOW


def confidence_color(val: str | None) -> str:
    if val == "high":
        return GREEN
    if val == "low":
        return RED
    return YELLOW


PLOTLY_BASE = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(color=TEXT, family="system-ui, -apple-system, sans-serif"),
    margin=dict(l=20, r=20, t=36, b=20),
)

# ── CSS injection ─────────────────────────────────────────────────────────────
CSS = """<style>
/* ── Global ──────────────────────────────────────────────── */
.stApp { background: #0a0e17 !important; color: #e2e8f0; }
.main .block-container { padding: 1.2rem 2.5rem 3rem; max-width: 1440px; }
#MainMenu, footer { visibility: hidden; }
section[data-testid="stSidebar"] > div { background: #07090f !important; }
div[data-testid="stToolbar"] { visibility: hidden; }

/* ── Typography ───────────────────────────────────────────── */
h1,h2,h3,h4 { color: #e2e8f0 !important; }

/* ── Section headers ──────────────────────────────────────── */
.as-section {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.22em;
    text-transform: uppercase; color: #64748b;
    border-bottom: 1px solid #1a2a42;
    padding-bottom: 0.55rem; margin-bottom: 1.2rem; margin-top: 2.5rem;
}

/* ── App header ───────────────────────────────────────────── */
.as-header {
    display: flex; align-items: center; gap: 0.75rem;
    padding-bottom: 1rem; border-bottom: 1px solid #1a2a42;
    margin-bottom: 0.25rem;
}
.as-header-right { margin-left: auto; text-align: right; }
.as-header-tool { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.as-header-meta { font-size: 0.68rem; color: #64748b; margin-top: 2px; }
.as-wordmark { font-size: 1.1rem; font-weight: 800; letter-spacing: 0.06em; color: #e2e8f0; }
.as-wordmark span { color: #3b82f6; }
.as-tagline { font-size: 0.63rem; color: #64748b; letter-spacing: 0.1em; }

/* ── KPI cards ────────────────────────────────────────────── */
.as-kpi {
    background: #0e1726; border: 1px solid #1a2a42;
    border-top: 2px solid var(--kc, #3b82f6);
    border-radius: 8px; padding: 1.1rem 1.25rem; height: 100%;
}
.as-kpi-label {
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: #64748b; margin-bottom: 0.5rem;
}
.as-kpi-value {
    font-size: 1.3rem; font-weight: 800;
    color: var(--kc, #e2e8f0); line-height: 1.15; margin-bottom: 0.15rem;
}
.as-kpi-sub { font-size: 0.7rem; color: #64748b; }

/* ── Recommendation panel ─────────────────────────────────── */
.as-rec {
    background: #0b1525; border: 1px solid #1a2a42;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0; padding: 1.1rem 1.4rem; margin-top: 1rem;
}
.as-rec-label {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.2em;
    text-transform: uppercase; color: #3b82f6; margin-bottom: 0.5rem;
}
.as-rec-text { font-size: 0.9rem; color: #cbd5e1; line-height: 1.7; }

/* ── Domain cards ─────────────────────────────────────────── */
.as-domain {
    background: #0e1726; border: 1px solid #1a2a42;
    border-radius: 8px; padding: 1rem 1.1rem;
    min-height: 180px; display: flex; flex-direction: column;
}
.as-domain-name {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #94a3b8; margin-bottom: 0.5rem;
}
.as-domain-score {
    font-size: 1.6rem; font-weight: 800; line-height: 1; margin-bottom: 0.5rem;
}
.as-bar-bg {
    background: rgba(255,255,255,0.06); border-radius: 3px;
    height: 4px; width: 100%; overflow: hidden; margin-bottom: 0.55rem;
}
.as-bar-fill { height: 100%; border-radius: 3px; }
.as-domain-items { font-size: 0.67rem; color: #475569; line-height: 1.6; }

/* ── Risk alert cards ─────────────────────────────────────── */
.as-risk {
    background: #0e1726; border: 1px solid #1a2a42;
    border-left: 3px solid var(--rc, #ef4444);
    border-radius: 0 8px 8px 0; padding: 1.1rem 1.3rem; margin-bottom: 0.65rem;
}
.as-risk-num {
    font-size: 2.2rem; font-weight: 900; color: var(--rc, #ef4444);
    opacity: 0.25; float: right; line-height: 1; margin-top: -4px;
}
.as-risk-title { font-size: 0.9rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.3rem; }
.as-risk-desc { font-size: 0.8rem; color: #94a3b8; line-height: 1.55; }
.as-badge {
    display: inline-block; padding: 2px 8px; border-radius: 3px;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; margin-bottom: 0.5rem;
}

/* ── Signal matrix ────────────────────────────────────────── */
.as-signal-row {
    background: #0e1726; border: 1px solid #1a2a42; border-radius: 6px;
    padding: 0.6rem 0.9rem; display: flex; align-items: center;
    justify-content: space-between; margin-bottom: 0.35rem;
}
.as-signal-name { font-size: 0.8rem; color: #cbd5e1; }
.as-signal-pill {
    font-size: 0.65rem; font-weight: 700; padding: 2px 9px;
    border-radius: 3px; letter-spacing: 0.06em; text-transform: uppercase;
}

/* ── Risk bars ────────────────────────────────────────────── */
.as-rbar-wrap { margin-bottom: 0.7rem; }
.as-rbar-row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 0.75rem; margin-bottom: 0.22rem;
}
.as-rbar-name { color: #cbd5e1; }
.as-rbar-score { font-weight: 700; font-variant-numeric: tabular-nums; }

/* ── Timeline events ──────────────────────────────────────── */
.as-evt {
    background: #0e1726; border: 1px solid #1a2a42;
    border-left: 3px solid var(--ec, #f5a623);
    border-radius: 0 8px 8px 0; padding: 0.9rem 1.1rem; margin-bottom: 0.5rem;
}
.as-evt-date { font-size: 0.67rem; color: #64748b; font-family: monospace; }
.as-evt-title { font-size: 0.88rem; font-weight: 600; color: #e2e8f0; margin: 0.2rem 0 0.35rem; }
.as-evt-meta { display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center; }
.as-tag {
    display: inline-block; padding: 1px 7px; border-radius: 3px;
    font-size: 0.64rem; font-weight: 600; font-family: monospace; border: 1px solid;
}
.as-tag-cve  { color:#60a5fa; border-color:rgba(96,165,250,0.3); background:rgba(96,165,250,0.08); }
.as-tag-ok   { color:#10d98a; border-color:rgba(16,217,138,0.3); background:rgba(16,217,138,0.08); }
.as-tag-warn { color:#ef4444; border-color:rgba(239,68,68,0.3);  background:rgba(239,68,68,0.08);  }
.as-evt-desc { font-size: 0.77rem; color: #94a3b8; line-height: 1.5; margin-top: 0.4rem; }

/* ── Use case cards ───────────────────────────────────────── */
.as-uc {
    background: #0e1726; border: 1px solid #1a2a42;
    border-radius: 8px; padding: 1rem; text-align: center;
    min-height: 200px; display: flex; flex-direction: column;
}
.as-uc-reason { flex: 1; }
.as-uc-label {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #64748b; margin-bottom: 0.5rem;
}
.as-uc-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
.as-uc-verdict { font-size: 0.9rem; font-weight: 700; margin-bottom: 0.5rem; }
.as-uc-reason { font-size: 0.72rem; color: #64748b; line-height: 1.45; text-align: left; }

/* ── Hardening cards ──────────────────────────────────────── */
.as-hard {
    background: #0e1726; border: 1px solid #1a2a42; border-radius: 8px;
    padding: 0.85rem 1.1rem; margin-bottom: 0.45rem;
    display: flex; gap: 0.85rem; align-items: flex-start;
}
.as-hard-icon { font-size: 1rem; flex-shrink: 0; padding-top: 2px; }
.as-hard-title { font-size: 0.83rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.2rem; }
.as-hard-desc { font-size: 0.76rem; color: #94a3b8; line-height: 1.5; }
.as-pri {
    display: inline-block; padding: 1px 7px; border-radius: 2px;
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; margin-left: 0.4rem; vertical-align: middle;
}

/* ── Vendor profile ───────────────────────────────────────── */
.as-vrow {
    display: flex; gap: 1rem; padding: 0.5rem 0;
    border-bottom: 1px solid rgba(26,42,66,0.6); font-size: 0.82rem;
}
.as-vkey {
    color: #64748b; min-width: 140px; font-size: 0.65rem;
    font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding-top: 1px;
}
.as-vval { color: #e2e8f0; word-break: break-all; }
.as-vval a { color: #60a5fa; text-decoration: none; }
.as-vval a:hover { text-decoration: underline; }

/* ── Sources ──────────────────────────────────────────────── */
.as-src {
    display: block; background: #0b1320; border: 1px solid #1a2a42;
    border-radius: 4px; padding: 0.38rem 0.8rem;
    font-size: 0.71rem; font-family: monospace; color: #60a5fa;
    margin-bottom: 0.28rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    text-decoration: none;
}
.as-src:hover { background: #0f1a2e; border-color: rgba(96,165,250,0.35); }

/* ── Empty state ──────────────────────────────────────────── */
.as-empty {
    background: #0e1726; border: 1px dashed #1a2a42; border-radius: 8px;
    padding: 1.5rem; text-align: center; color: #64748b; font-size: 0.82rem;
}

/* ── Routing card ─────────────────────────────────────────── */
.as-route {
    background: #0e1726; border: 1px solid #1a2a42; border-radius: 8px;
    padding: 0.9rem 1.1rem; height: 100%;
}
.as-route-owner {
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #64748b; margin-bottom: 0.4rem;
}
.as-route-text { font-size: 0.78rem; color: #94a3b8; line-height: 1.55; }

/* ── Equal-height columns ─────────────────────────────────── */
div[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
    height: 100%;
    display: flex;
    flex-direction: column;
}
.as-kpi, .as-domain, .as-uc, .as-route, .as-risk, .as-vrow-wrap {
    height: 100%;
    box-sizing: border-box;
}
/* KPI cards equal height within their row */
.as-kpi { display: flex; flex-direction: column; justify-content: space-between; }

/* ── Conf pill ────────────────────────────────────────────── */
.as-conf {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.67rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
}
</style>"""
