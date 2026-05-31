# 🛡️ AgentShield

**AI Tool Security Assessment Platform**

AgentShield researches the public security posture of any AI developer tool — Cursor, CrewAI, LangGraph, GitHub Copilot, and more — and renders an executive-grade security assessment dashboard in your browser.

Enter a tool name. The agent searches vendor websites, security pages, CVE databases, and public incident records. You get a structured risk report in 3–6 minutes.

---

## What It Does

Most teams adopting AI tools have no standardized way to evaluate their security posture before deployment. AgentShield automates that due diligence using live web research and an LLM agent, then presents the findings as an executive dashboard built for security leaders.

**The agent collects:**
- Vendor metadata and security/trust center pages
- Compliance certifications: SOC 2, ISO 27001
- Access controls: SSO, MFA, RBAC, audit logs
- Encryption posture (at rest, in transit)
- Vulnerability disclosure and bug bounty programs
- AI-specific signals: data retention policy, prompt logging, execution environment, user-in-the-loop controls
- Public CVEs, security incidents, and breach history

**The dashboard shows:**
- Review level verdict: Low / Medium / High Review Required
- 5-domain security posture overview with scores
- Top 3 prioritized risks with explanations
- Full security signal matrix (11 controls)
- Agent risk radar across 5 threat dimensions
- Interactive threat timeline with CVE details
- Deployment suitability by use case (PII, regulated industries, agentic execution)
- Actionable hardening steps
- Full evidence and source list

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Streamlit Web App                  │
│                                                      │
│  Landing Page  →  Research View  →  Dashboard View  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│               Research Agent (Claude Opus)           │
│                                                      │
│  Agentic loop: up to 25 iterations                  │
│  Tools: Bright Data MCP (search + scrape)           │
└─────────────────────┬───────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   Bright Data MCP          Claude Opus 4
   Web Search               Reasoning +
   Page Scraping            JSON extraction
```

---

## Project Structure

```
agentshield/
├── app.py                        # Streamlit entry point — all three views
├── main.py                       # CLI alternative: python main.py <tool>
│
├── research_agent.py             # Agentic research loop (Claude + MCP)
├── models.py                     # Pydantic schemas for the JSON report
├── extractors.py                 # Regex-based security signal detection
│
├── components/
│   ├── executive_summary.py      # KPI cards + recommendation + routing
│   ├── posture_overview.py       # 5-domain security posture grid
│   ├── top_risks.py              # Auto-derived top 3 risk cards
│   ├── signal_matrix.py          # 11-signal status matrix
│   ├── agent_risk_profile.py     # Radar chart across 5 risk dimensions
│   ├── threat_timeline.py        # CVE and incident timeline
│   ├── deployment.py             # Use-case deployment suitability
│   ├── hardening_plan.py         # Actionable remediation checklist
│   ├── vendor_profile.py         # Vendor metadata and links
│   └── sources.py                # Collapsible evidence source list
│
├── utils/
│   ├── data_loader.py            # JSON normalization with null-safe defaults
│   ├── risk_engine.py            # Heuristic risk scoring + top risk derivation
│   └── text.py                   # Paragraph-to-bullets HTML helper
│
├── styles/
│   └── theme.py                  # Dark theme CSS + color constants
│
├── Dockerfile                    # Node.js 20 + Python 3 for deployment
├── requirements.txt              # Full dependencies (agent + dashboard)
└── requirements_dashboard.txt    # Dashboard-only dependencies
```

---

## Quickstart

### Prerequisites

- Python 3.11+
- Node.js 20+ (required for Bright Data MCP server)
- An [Anthropic API key](https://console.anthropic.com)
- A [Bright Data API token](https://brightdata.com)

### 1. Clone and install

```bash
git clone https://github.com/SrimansiRamesh/AgentShield.git
cd AgentShield
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and fill in your keys
export $(cat .env | xargs)
```

Or set directly:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export BRIGHTDATA_API_TOKEN=your-token-here
```

### 3. Run the web app

```bash
streamlit run app.py
```

Open `http://localhost:8501`, type any AI tool name, and click **Analyze**.

### 4. CLI alternative

If you want to generate a JSON report without the web UI:

```bash
python main.py Cursor
python main.py CrewAI --output crewai_report.json
python main.py LangGraph --verbose
```

Then load the resulting JSON file via the dashboard's upload button.

---

## Report Schema

The agent produces a structured JSON report:

```json
{
  "tool_name": "Cursor",
  "vendor_metadata": {
    "company": "Anysphere, Inc.",
    "product": "Cursor",
    "url": "https://cursor.com",
    "security_url": "https://cursor.com/security",
    "trust_center_url": "https://trust.cursor.com",
    "privacy_policy_url": "https://cursor.com/privacy"
  },
  "review_level": "High Review Required",
  "recommendation_summary": "...",
  "confidence": "high",
  "categorized_signals": {
    "compliance_and_governance": {
      "score_percentage": 60,
      "positive": ["soc2", "encryption", "vulnerability_disclosure"],
      "missing": ["iso27001", "bug_bounty"]
    },
    "identity_and_access": { "score_percentage": 75, "...": "..." },
    "ai_data_privacy": { "score_percentage": 25, "...": "..." }
  },
  "ai_agent_signals": {
    "zero_data_retention": null,
    "prompt_logging_period_days": null,
    "execution_environment": "cloud_isolated",
    "user_in_the_loop": true
  },
  "threat_timeline": [
    {
      "title": "Sandbox escape via .git config",
      "date": "2026-02-13",
      "severity": "critical",
      "cve_id": null,
      "patched": false,
      "source_url": "https://..."
    }
  ],
  "use_case_fit": {
    "internal_dev_tooling": "caution",
    "storing_pii": "caution",
    "regulated_industries": "caution",
    "agentic_autonomous_execution": "avoid"
  },
  "actionable_hardening_steps": ["..."],
  "risk_owner_routing": {
    "security_team": "...",
    "legal": "...",
    "procurement": "..."
  },
  "sources": ["https://...", "..."]
}
```

---

## Deployment

### Railway (recommended)

Railway supports the Dockerfile natively and provides a free tier.

1. Go to [railway.app](https://railway.app) and create a new project
2. Connect your GitHub repo (`SrimansiRamesh/AgentShield`)
3. Railway detects the Dockerfile automatically
4. Add environment variables in the Railway dashboard:
   - `ANTHROPIC_API_KEY`
   - `BRIGHTDATA_API_TOKEN`
5. Deploy — you get a public URL in ~3 minutes

### Render

1. New Web Service → connect GitHub repo
2. Runtime: **Docker**
3. Add the two environment variables
4. Deploy

### Local Docker

```bash
docker build -t agentshield .
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e BRIGHTDATA_API_TOKEN=your-token \
  agentshield
```

Open `http://localhost:8501`.

### Streamlit Community Cloud (dashboard only)

Streamlit Cloud can host the dashboard in upload-your-own-JSON mode (no live research, since Node.js is not available).

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect the GitHub repo, set main file to `app.py`
3. Under Advanced Settings, set requirements file to `requirements_dashboard.txt`
4. Add secrets: `ANTHROPIC_API_KEY` and `BRIGHTDATA_API_TOKEN`

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Claude Opus 4 (Anthropic) |
| Web research | Bright Data MCP — search + scrape |
| Agent orchestration | Anthropic Python SDK + MCP Python client |
| Data validation | Pydantic v2 |
| Web app | Streamlit |
| Charts | Plotly |
| Deployment | Docker (Node.js 20 + Python 3.11) |

---

## Security Signal Definitions

| Signal | What it means |
|---|---|
| SOC 2 | Independent audit of security, availability, and confidentiality controls |
| ISO 27001 | Internationally recognized information security management certification |
| SSO | Single sign-on support (SAML, OAuth, OIDC) |
| MFA | Multi-factor or two-factor authentication available |
| RBAC | Role-based access control for user permissions |
| Audit Logs | Access and activity logging available for review |
| Encryption | Data encrypted at rest and in transit |
| Vuln. Disclosure | Published responsible disclosure or security reporting process |
| Bug Bounty | Public bug bounty program (HackerOne, Bugcrowd, etc.) |
| Zero Data Retention | Vendor commits to not training on or retaining user inputs |
| User in the Loop | Tool requires manual approval before executing destructive actions |

---

## Risk Dimensions

The agent risk radar scores five dimensions from 0 (low risk) to 100 (high risk):

| Dimension | Derived from |
|---|---|
| Code Execution | Execution environment, user-in-the-loop controls |
| Prompt Injection | Data retention policy, loop controls, CVE history |
| Data Exposure | Retention policy, encryption, SOC 2 status |
| Identity | Missing IAM controls: MFA, SSO, RBAC, audit logs |
| Supply Chain | Vulnerability disclosure, bug bounty, CVE count |

Scores are heuristic-derived from public signals and are not a substitute for a formal security audit.

---

## Limitations

- All data comes from publicly available sources only
- Absence of evidence is not evidence of absence — a missing signal means the vendor has not publicly disclosed it, not necessarily that the control does not exist
- Report quality is bounded by how much security information the vendor publishes
- CVE and incident data is limited to what appears in public search results and news
- Not a replacement for a formal vendor security assessment, penetration test, or SOC 2 audit review

---

## Contributing

Pull requests are welcome. For significant changes, open an issue first to discuss the approach.

---

*Built at the Anthropic Safety Fellows hackathon, May 2026.*
