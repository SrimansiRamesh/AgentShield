# 🛡️ AgentShield

**AI Tool Security Assessment Platform**

Built at the **[Web Data UNLOCKED Hackathon](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon)** hosted by [lablab.ai](https://lablab.ai) at the Bright Data office in San Francisco.

The challenge: build something meaningful using Bright Data's web data infrastructure. We built a security research agent that uses Bright Data's MCP tools to scrape and search the public web, then renders the findings as an executive-grade security dashboard.

---

## The Problem

Security and procurement teams evaluating AI developer tools — Cursor, CrewAI, LangGraph, GitHub Copilot — have no fast, standardized way to assess their security posture before deployment. Manually reviewing vendor security pages, trust centers, CVE databases, and incident history takes hours and requires knowing where to look.

AgentShield automates that research in 3–6 minutes using a live web research agent.

---

## What It Does

Enter any AI tool name. AgentShield launches a Claude Opus agent equipped with Bright Data MCP tools to search and scrape public sources in real time. When research is complete, a structured security assessment dashboard renders automatically in the browser.

**The agent collects:**
- Vendor website, security page, trust center, and privacy policy
- Compliance certifications: SOC 2, ISO 27001
- Access controls: SSO, MFA, RBAC, audit logs
- Encryption posture (at rest, in transit)
- Vulnerability disclosure program and bug bounty program
- AI-specific signals: data retention policy, prompt logging period, execution environment, user-in-the-loop controls
- Public CVEs, security incidents, and breach history

**The dashboard shows:**
- Review level verdict: Low / Medium / High Review Required
- 5-domain security posture overview with scores
- Top 3 prioritized risks with explanations
- Full security signal matrix (11 controls)
- Agent risk radar across 5 threat dimensions
- Interactive threat timeline with CVE details
- Deployment suitability by use case (PII, regulated industries, agentic execution)
- Actionable hardening steps with priority tiers
- Risk owner routing (security team, legal, procurement)
- Full evidence and source list

---

## How Bright Data Powers It

Bright Data's MCP server provides the agent with two critical capabilities that make this possible:

**Web search** — The agent searches for the vendor's official website, security pages, CVE disclosures, and public incident reports without hitting rate limits or bot detection.

**Page scraping** — The agent scrapes full page content from security pages, trust centers, privacy policies, and news articles. Many of these pages have anti-scraping protections that Bright Data bypasses transparently.

Without Bright Data, the agent would be limited to whatever the LLM already knows from training data — which is both stale and incomplete. With it, every report reflects the current state of the vendor's public security posture.

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
├── research_agent.py             # Agentic research loop (Claude + Bright Data MCP)
├── models.py                     # Pydantic schemas for the JSON report
├── extractors.py                 # Regex-based security signal detection
│
├── components/
│   ├── executive_summary.py      # KPI cards + recommendation + risk routing
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
│   └── theme.py                  # Dark SOC aesthetic CSS + color constants
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
# Edit .env with your keys
export $(cat .env | xargs)
```

Or export directly:

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

Generate a JSON report without the web UI:

```bash
python main.py Cursor
python main.py CrewAI --output crewai_report.json
python main.py LangGraph --verbose
```

Load the resulting JSON file via the dashboard's upload button.

---

## Report Schema

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
  "confidence_reason": "...",
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
2. Connect your GitHub repo
3. Railway detects the Dockerfile automatically
4. Add environment variables: `ANTHROPIC_API_KEY` and `BRIGHTDATA_API_TOKEN`
5. Deploy — public URL in ~3 minutes

### Local Docker

```bash
docker build -t agentshield .
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e BRIGHTDATA_API_TOKEN=your-token \
  agentshield
```

### Streamlit Community Cloud (dashboard only)

Hosts the dashboard in upload-your-own-JSON mode. Live research requires Node.js which Streamlit Cloud does not support.

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect the repo, set main file to `app.py`
3. Set requirements file to `requirements_dashboard.txt` under Advanced Settings
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
- Absence of evidence is not evidence of absence — a missing signal means the vendor has not publicly disclosed it, not that the control does not exist
- Report quality is bounded by how much security information the vendor publishes
- Not a replacement for a formal vendor security assessment or SOC 2 audit review

---

## Team

Built at the [Web Data UNLOCKED Hackathon](https://lablab.ai/ai-hackathons/brightdata-ai-agents-web-data-hackathon) at the Bright Data office, San Francisco, May 2026.
