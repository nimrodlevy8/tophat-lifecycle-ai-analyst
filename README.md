# AI Analyst Plus — Monopoly GO

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Claude Code Required](https://img.shields.io/badge/requires-Claude%20Code-blueviolet.svg)](https://claude.ai/code)

An AI-powered product analyst that lives inside Claude Code. Ask business questions in plain English, get validated analyses, branded charts, and stakeholder-ready slide decks — in minutes, not days.

**33** agents | **60** skills | **45** helper modules | DAG-based parallel execution | PowerPoint + PDF + Google Docs + Google Slides export

---

## What This Is

AI Analyst Plus turns Claude Code into a product analytics system for Monopoly GO. It combines:

- **Skills** (`.claude/skills/`) — standards Claude follows automatically (chart styling, data validation, question framing, stakeholder communication)
- **Agents** (`agents/`) — multi-step analytical workflows orchestrated by a DAG engine (question framing → data exploration → analysis → storytelling → deck creation)
- **Helpers** (`helpers/`) — Python modules for charting, SQL validation, data connectivity, statistical tests, and more
- **Knowledge** (`.knowledge/`) — persistent memory for dataset context, corrections, proven SQL patterns, and business glossary

You interact by talking to Claude. Ask a question, invoke a slash command, or let Claude figure out which skills and agents to apply.

---

## Quick Start

**1. Start Claude Code**

```bash
claude
```

**2. Ask a question**

```
What's our conversion rate by segment?
```

Or run the full pipeline:

```
/run-pipeline question="Why is activation dropping for Regulars?"
```

---

## Don't Know What to Do? Just Ask.

Claude knows the entire system — every agent, skill, command, and dataset. If you're stuck:

```
What can I do with this data?
How do I connect a new dataset?
Which agents handle root cause analysis?
Re-run just the chart maker and deck creator.
```

You don't need to memorize anything in this README. Think of it as a reference — Claude is the guide.

---

## Five Things You Can Do

### 1. Ask a quick question

```
What's our ARPDAU by activity segment this week?
```

Claude queries BigQuery and returns an answer with a chart. Simple questions get answered in under 2 minutes without running the full pipeline.

### 2. Run a full analysis

```
/run-pipeline question="What's driving the decline in Regular retention?"
```

The pipeline runs up to 19 steps across 4 phases: Frame the question, Analyze the data, Build the story, Create the deck. You get a validated analysis, branded charts, a narrative, and a slide deck. Exports to PowerPoint, PDF, Google Slides, and Google Docs.

### 3. Explore a dataset

```
/explore
```

Interactive data browsing without committing to a full analysis. Preview tables, check distributions, spot patterns, form hypotheses.

### 4. Run a minigame health assessment

```
Assess the health of Coop events over the last 3 months.
```

The Minigame Health Assessor agent auto-detects the right mode (health-check, comparison, deep-dive, or PM question), loads domain context (minigame mechanics, KPIs, query archaeology), and orchestrates the analysis end-to-end.

### 5. Generate the weekly digest

```
/weekly-digest
```

Provide Google Slides/Docs links and Claude fetches content, classifies by team (New Minigame Vertical vs LRK Vertical), summarizes each artifact, drafts the executive email, and publishes to Confluence.

---

## Integrations

| Integration | Method | Access |
|------------|--------|--------|
| **BigQuery** | `bq` CLI | Read-only. Schema: `dwh-prod-tophat`. Date-limited queries enforced. |
| **JIRA** | Atlassian MCP | Strictly read-only — no creates, updates, or modifications. |
| **Confluence** | Atlassian MCP | Read-only except Weekly Digest parent page and Ad Hoc Output Examples. |
| **Slack** | Slack MCP | Scopely workspace only, whitelisted channels, no posting without instruction. |
| **Hex** | Hex CLI (WSL) | Notebook creation and management for SQL/Python analysis code. |
| **Google Workspace** | `gws` CLI | Read-only access to Docs, Slides, and Drive. |
| **Google Slides** | `gws` CLI | Deck creation and formatting via API. |
| **Google Docs** | `gws` CLI | Analysis readout export with embedded charts. |

---

## How It Works: The Pipeline

When you run `/run-pipeline`, Claude orchestrates agents across 4 phases:

```
1. FRAME              2. ANALYZE                          3. STORY                 4. DECK
+-----------------+   +-----------------------------+   +--------------------+   +------------------+
| Question        |   | Data Explorer               |   | Story Architect    |   | Storytelling     |
|   Framing       |   |   > Cross-Verification      |   |   > Coherence      |   |   > Deck Creator |
|   > Hypothesis  |   |   > Descriptive Analytics    |   |     Reviewer       |   |   > Slide Review |
|     Generation  |   |   > Root Cause Investigator  |   |   > Chart Maker    |   |   > Close the    |
|                 |-->|   > Validation               |-->|   > Design Critic  |-->|     Loop         |
+-----------------+   |   > Opportunity Sizer        |   +--------------------+   +------------------+
                      +-----------------------------+
```

**Phase 1 — Frame:** Structures your business question into analytical questions with testable hypotheses.

**Phase 2 — Analyze:** Explores the data, runs segmentation/funnel/drivers analysis, drills to root cause, cross-verifies findings, validates, and sizes the opportunity.

**Phase 3 — Story:** Designs a storyboard (Context-Tension-Resolution arc), generates charts, and reviews visual quality.

**Phase 4 — Deck:** Writes a stakeholder narrative, builds a branded slide deck, reviews design, and ensures every recommendation has a follow-up plan. Exports to PowerPoint, PDF, Google Slides, or Google Docs.

If the pipeline gets interrupted, resume where you left off:

```
/resume-pipeline
```

---

## All Commands

| Command | What It Does |
|---------|-------------|
| `/run-pipeline` | Full analysis to slide deck |
| `/resume-pipeline` | Resume interrupted pipeline |
| `/explore` | Interactive data exploration |
| `/data` | Show active dataset schema |
| `/datasets` | List all connected datasets |
| `/switch-dataset` | Change the active dataset |
| `/connect-data` | Add a new data source |
| `/setup` | Interactive onboarding interview |
| `/metrics` | Browse the metric dictionary |
| `/history` | View past analyses |
| `/patterns` | View recurring analytical patterns |
| `/export` | Export as slides, email, Slack, brief, data, Google Doc, or Word |
| `/forecast` | Generate a time-series forecast |
| `/runs` | List, inspect, compare pipeline runs |
| `/business` | Browse organization knowledge |
| `/log-correction` | Log a data or methodology correction |
| `/architect` | Multi-persona planning methodology |
| `/compare-datasets` | Compare metrics across datasets |
| `/deck-critique` | Score a deck slide-by-slide against SWD checklist |
| `/deck-rescue` | Full deck rewrite pipeline |
| `/slide-transform` | Redesign a single bad slide |
| `/analysis-design` | Full lifecycle from hunch to validated investigation plan |
| `/stress-test` | 7-point review of any analysis plan |
| `/experiment-brief` | Generate a structured A/B test brief |
| `/jira-incidents` | Per-minigame incident report from JIRA |
| `/organize` | Enforce folder structure on loose files |
| `/demo` | Guided breakout room experience |

Or just ask in plain English. "Show me retention by segment" works as well as any command.

---

## Your Data

### Active dataset

The system reads `.knowledge/active.yaml` at analysis start to determine the active dataset, then loads context from `.knowledge/datasets/{active}/` (manifest, schema, quirks). Use `/data` to inspect and `/switch-dataset` to change.

### Supported sources

Run `/connect-data` for a guided wizard. Supported sources:

- **BigQuery** — primary warehouse (`dwh-prod-tophat`)
- **DuckDB** — local or MotherDuck
- **CSV files** — drop them in a directory, point Claude at it
- **Postgres** — any Postgres-compatible database
- **Snowflake** — Snowflake with user/password or key pair

The system auto-profiles your data, creates schema documentation, and remembers context across sessions in `.knowledge/datasets/`.

### Data source fallback

If the primary connection fails, the system automatically falls back: primary (e.g., BigQuery) → local DuckDB → CSV files. You're always informed which source is active.

---

## Architecture

```
scopely-mgo-ai-analyst/
├── CLAUDE.md                    # AI persona, skills table, rules, workflow
├── agents/                      # 33 agent prompt templates (markdown)
│   ├── INDEX.md                 # Complete agent registry with invoke conditions
│   ├── registry.yaml            # DAG dependencies and execution order
│   └── CONTRACT_TEMPLATE.md     # Template for writing new agents
├── .claude/skills/              # 60 skill definitions
├── helpers/                     # 45 Python modules
│   ├── chart_helpers.py         # SWD charting (swd_style, highlight_bar, etc.)
│   ├── data_helpers.py          # Data source abstraction and fallback
│   ├── sql_helpers.py           # SQL sanity checks
│   ├── gdoc_builder.py          # Google Doc export (python-docx)
│   ├── forecast_helpers.py      # Time-series forecasting
│   └── ...                      # See helpers/INDEX.md for full list
├── .knowledge/                  # Persistent memory
│   ├── active.yaml              # Currently active dataset
│   ├── datasets/                # Per-dataset manifest, schema, quirks
│   ├── corrections/             # Logged mistakes to prevent repeat errors
│   ├── query-archaeology/       # Proven SQL patterns by domain
│   └── organizations/           # Business glossary, metrics, products, teams
├── .mcp.json                    # MCP server config (Slack, Hex, Atlassian)
├── themes/                      # Marp CSS themes (light + dark)
├── templates/                   # Marp deck templates, HTML components
├── outputs/                     # Final deliverables (analyses, charts, decks)
└── working/                     # Intermediate files (gitignored)
```

### Skills vs Agents

**Skills** are standards Claude follows automatically. When you make a chart, the Visualization Patterns skill activates. When you start an analysis, Data Quality Check runs. You never invoke them — they apply when their trigger condition matches. Multiple skills can fire at once.

**Agents** are multi-step workflows for specific tasks. They're markdown prompt templates with `{{VARIABLES}}` that get substituted at runtime. The pipeline orchestrates them in dependency order using a DAG engine.

### Knowledge System

`.knowledge/` persists across sessions:
- **Dataset context** — schema, quirks, connection details per dataset
- **Corrections** — logged mistakes so the same SQL error never happens twice
- **Query archaeology** — proven SQL patterns retrieved before writing new queries
- **Business glossary** — organization-specific terms, metrics, products, teams
- **Analysis archive** — past analyses indexed for future reference

---

## Customization

| Want to... | Do this |
|-----------|---------|
| Change how Claude thinks | Edit `CLAUDE.md` (persona, rules, workflow) |
| Add a new skill | Create `.claude/skills/my-skill/skill.md` or use `/skill-creator` |
| Add a new agent | Create `agents/my-agent.md` using `agents/CONTRACT_TEMPLATE.md` |
| Change the slide theme | Create a YAML theme in `themes/brands/` |
| Modify the pipeline | Edit `.claude/skills/run-pipeline/skill.md` |
| Add to the agent DAG | Edit `agents/registry.yaml` |

---

## Requirements

- **Python 3.10+**
- **Claude Code** with a [Claude Pro or Max subscription](https://claude.ai/code)
- **Node.js 18+** (for Marp PDF/HTML export)
- **`gws` CLI** (for Google Workspace read/write)
- **`bq` CLI** (for BigQuery access)
- **WSL** (for Hex CLI on Windows)

---

## Getting Help

- **Setup guide:** [docs/setup-guide.md](docs/setup-guide.md)
- **Theming:** [docs/theming.md](docs/theming.md)
- **Agent reference:** [agents/INDEX.md](agents/INDEX.md)
- **Helper reference:** [helpers/INDEX.md](helpers/INDEX.md)
