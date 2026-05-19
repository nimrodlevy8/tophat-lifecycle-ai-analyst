# AI Analyst Plus — Skills & Agents Reference

> **Project:** scopely-mgo-ai-analyst | **Last updated:** 2026-05-06

This document lists every skill (automated behavior) and agent (multi-step workflow) available in the AI Analyst Plus system.

---

## Skills (51)

Skills activate automatically when their trigger condition is met, or manually via `/command`.

### Core Analytical Workflow

| Skill | Trigger | Description |
|---|---|---|
| [Question Router](.claude/skills/question-router/skill.md) | Every analytical request | Classifies questions into complexity levels (L1-L5) and routes to the appropriate analytical path. Also handles question framing via the Question Ladder. |
| [Analysis Design Spec](.claude/skills/analysis-design-spec/skill.md) | Before any analysis starts | Defines question, decision, data needs, dimensions, time range, output format, and success criteria upfront. |
| [Analysis Design](.claude/skills/analysis-design/skill.md) | `/analysis-design` | Full lifecycle from vague hunch to rigorous investigation plan -- hypothesis sharpening, confound scan, V1 execution, feedback synthesis, V2 redesign. |
| [Run Pipeline](.claude/skills/run-pipeline/skill.md) | `/run-pipeline` | End-to-end analysis pipeline from raw data and business question to validated findings and slide deck. |
| [Resume Pipeline](.claude/skills/resume-pipeline/skill.md) | `/resume-pipeline` | Detects existing artifacts, determines last completed step, and resumes an interrupted pipeline. |
| [Explore](.claude/skills/explore/skill.md) | `/explore` | Quick interactive data exploration -- browse tables, check distributions, spot patterns without the full pipeline. |
| [Forecast](.claude/skills/forecast/skill.md) | User asks about predictions or projections | Generates time-series forecasts with seasonality detection, model selection, and confidence intervals. |
| [Runs](.claude/skills/runs/skill.md) | `/runs` | Lists, inspects, compares, and cleans up past pipeline runs. |

### Data Management & Connection

| Skill | Trigger | Description |
|---|---|---|
| [Connect Data](.claude/skills/connect-data/skill.md) | `/connect-data` | Guided wizard to add a new dataset (CSV, DuckDB, MotherDuck, Postgres, BigQuery, Snowflake). |
| [Switch Dataset](.claude/skills/switch-dataset/skill.md) | `/switch-dataset {name}` | Changes the active dataset for analysis. |
| [Data Inspect](.claude/skills/data-inspect/skill.md) | `/data`, `/data {table}`, or `/datasets` | Shows active dataset schema -- tables, columns, row counts, relationships. Also lists all connected datasets. |
| [Data Profiling](.claude/skills/data-profiling/skill.md) | After connecting a new dataset | Deep-profiles schema, distributions, temporal patterns, completeness, and anomalies. |
| [Distribution Profiler](.claude/skills/distribution-profiler/skill.md) | Profile a column's distribution | Profiles statistical distribution -- identification, valid stats, recommended tests, A/B testing guidance. |
| [Archaeology](.claude/skills/archaeology/skill.md) | Before writing SQL | Retrieves proven SQL patterns and join templates from query archaeology so agents reuse validated work. |
| [Metrics](.claude/skills/metrics/skill.md) | `/metrics` | Browses and displays metric definitions from the active dataset's metric dictionary. |
| [Metric Spec](.claude/skills/metric-spec/skill.md) | Defining or documenting a metric | Standardized template to eliminate ambiguity about calculation, interpretation, and measurement. |

### Validation & Quality

| Skill | Trigger | Description |
|---|---|---|
| [Data Quality Check](.claude/skills/data-quality-check/skill.md) | Starting any analysis or new data source | Validates completeness, consistency, and coverage; flags issues as BLOCKER / WARNING / INFO. |
| [Triangulation](.claude/skills/triangulation/skill.md) | After producing findings, before presenting | Cross-references findings using multiple calculation methods before presentation. |
| [Semantic Validation](.claude/skills/semantic-validation/skill.md) | After validation agent runs | Orchestrates 4-layer validation stack plus confidence scoring for a comprehensive quality assessment. |
| [Guardrails](.claude/skills/guardrails/skill.md) | Defining metrics or reporting positive findings | Pairs every success metric with guardrail metrics; checks for trade-offs before declaring wins. |
| [Stress Test](.claude/skills/stress-test/skill.md) | `/stress-test` | 7-point review of any analysis plan for methodological flaws (wrong baselines, survivorship bias, missing segments, confounds). |
| [Tracking Gaps](.claude/skills/tracking-gaps/skill.md) | Analysis may require data that doesn't exist | Assesses whether needed data exists, identifies gaps, and produces prioritized instrumentation requests. |
| [SRM Check](.claude/skills/srm-check/skill.md) | Loading experiment / A/B test data | Detects Sample Ratio Mismatch to validate randomization integrity before analysis proceeds. |

### Visualization & Presentation

| Skill | Trigger | Description |
|---|---|---|
| [Visualization Patterns](.claude/skills/visualization-patterns/skill.md) | Generating any chart or visualization | Applies standardized rules for chart type selection, color, typography, and annotation. |
| [Presentation Themes](.claude/skills/presentation-themes/skill.md) | Creating a deck or presentation | Ensures consistent theme, professional styling, and coherent analytical story across slides. |
| [Deck Critique](.claude/skills/deck-critique/skill.md) | `/deck-critique` | Scores slides against the Data Story Checklist (SO-WHAT, STAKES, EVIDENCE, ASK); returns grade A-F with fix prescription. For slide-level or full-deck fixes, use agents directly. |
| [Stakeholder Communication](.claude/skills/stakeholder-communication/skill.md) | Producing a narrative or deck | Adapts findings to the audience -- same insight, different framing and detail level per stakeholder type. |
| [Close-the-Loop](.claude/skills/close-the-loop/skill.md) | End of analysis with recommendations | Ensures every recommendation has a decision owner, success metric, follow-up date, and fallback plan. |

### Export & Sharing

| Skill | Trigger | Description |
|---|---|---|
| [Export](.claude/skills/export/skill.md) | `/export {format}` | Exports results as slides, email, Slack, brief, data CSV, Google Doc, or Word file. |
| [Google Doc Export](.claude/skills/google-doc-export/skill.md) | Building a Google Doc via MCP | Document structure, image placement, heading hierarchy, and formatting standards for Docs. |
| [Google Slides Export](.claude/skills/google-slides-export/skill.md) | Building Google Slides via MCP | Design system, layout library, and pre-flight checklist for Slides. |
| [Chart-to-Drive](.claude/skills/chart-to-drive/skill.md) | Uploading charts to Google Drive | Uploads local PNGs to Drive for insertion into Docs and Slides. |
| [Session Handoff](.claude/skills/session-handoff/skill.md) | Approaching context limits | Preserves resource IDs, pipeline progress, and auth state so the next session picks up seamlessly. |

### Knowledge & Feedback

| Skill | Trigger | Description |
|---|---|---|
| [Knowledge Bootstrap](.claude/skills/knowledge-bootstrap/skill.md) | Session start | Loads all knowledge subsystems: active dataset, user profile, corrections, learnings, query archaeology, analysis archive. |
| [Setup](.claude/skills/setup/skill.md) | `/setup` | 4-phase conversational interview to populate the knowledge system from user's real company context. |
| [Auth Preflight](.claude/skills/auth-preflight/skill.md) | Session start when Google APIs needed | Verifies Google Workspace credentials and handles re-auth before workflows begin. |
| [Business](.claude/skills/business/skill.md) | `/business` | Browses organization knowledge -- glossary terms, products, metrics, OKRs, team structure. |
| [Feedback Capture](.claude/skills/feedback-capture/skill.md) | User corrects your work or `/log-correction` | Silently captures corrections, methodology learnings, and positive feedback. Also handles manual correction logging. |
| [History](.claude/skills/history/skill.md) | `/history` | Browses and searches past analyses from the archive. |
| [Patterns](.claude/skills/patterns/skill.md) | Detecting recurring analytical patterns | Surfaces recurring patterns discovered across past analyses. |
| [Archive Analysis](.claude/skills/archive-analysis/skill.md) | End of pipeline | Saves completed analyses to the knowledge archive for future reference. |
| [File Organization](.claude/skills/file-organization/skill.md) | Start of any analysis or `/organize` | Enforces consistent folder structure across working/ and outputs/. |

### External Access

| Skill | Trigger | Description |
|---|---|---|
| [BigQuery Access](.claude/skills/bigquery-access/skill.md) | Before any BigQuery query | Connection method, schema rules, date limits, SQL formatting standards, read-only enforcement. |
| [Hex Access](.claude/skills/hex-access/skill.md) | Before any Hex interaction | CLI via WSL (`wsl bash -lc "hex ..."`), create/run projects, manage cells, list connections. |
| [Slack Access](.claude/skills/slack-access/skill.md) | Before any Slack interaction | Scopely workspace only, whitelisted channels, no posting without explicit instruction. |
| [JIRA Access](.claude/skills/jira-access/skill.md) | Before any JIRA interaction | Strictly read-only, no modifications, no sharing without per-instance approval. |

### Domain-Specific (Vertical-Scoped)

These skills only activate when the matching vertical is set in `.knowledge/active.yaml`.

| Skill | Trigger | Scope | Description |
|---|---|---|---|
| [Coop Analysis](.claude/skills/coop-analysis/skill.md) | Analyzing coop (Partners) events | `minigame` | Pusher classification, partner structure, social metrics, friend types, query patterns. |
| [JIRA Incidents](.claude/skills/jira-incidents/skill.md) | `/jira-incidents` | `minigame` | Per-minigame-event incident report: severity, TTR, minigame classification, narrative. |

### Experimentation

| Skill | Trigger | Description |
|---|---|---|
| [Experiment Brief](.claude/skills/experiment-brief/skill.md) | User expresses intent to test something | Auto-generates a structured experiment brief (hypothesis, metrics, guardrails, duration estimate). |

### Meta

| Skill | Trigger | Description |
|---|---|---|
| [Skill Creator](.claude/skills/skill-creator/skill.md) | Creating or editing skills | Creates new skills, modifies existing ones, runs evals, and benchmarks performance. |
| [Architect](.claude/skills/architect/skill.md) | `/architect` | Multi-persona planning methodology (3-5 experts) through 5 phases to produce a master plan for new projects. |

### Archived

| Skill | Location | Reason |
|---|---|---|
| Compare Datasets | `.claude/skills/_archived/compare-datasets/` | Not used in April; single-dataset workflow. Available if needed. |

---

## Agents (28)

Agents are multi-step workflow templates. Claude reads the agent file, substitutes variables, and executes step by step.

### Question & Hypothesis

| Agent | Description |
|---|---|
| [Question Framing](agents/question-framing.md) | Generates prioritized analytical questions from a business problem with hypotheses and data requirements. |
| [Hypothesis](agents/hypothesis.md) | Turns analytical questions into testable hypotheses with expected outcomes, confirming/rejecting criteria, and test plans. |
| [Hypothesis Sharpener](agents/hypothesis-sharpener.md) | Transforms a vague hunch into a precise, testable hypothesis with metrics, comparison groups, and accept/reject criteria. |
| [Confound Scanner](agents/confound-scanner.md) | Adversarial agent that finds threats to validity -- concurrent changes, selection biases, measurement artifacts. |

### Data & Analysis

| Agent | Description |
|---|---|
| [Data Explorer](agents/data-explorer.md) | Discovers what data exists, profiles quality and completeness, identifies gaps, and recommends supportable analyses. |
| [Descriptive Analytics](agents/descriptive-analytics.md) | Performs drivers analysis, segmentation, and funnel analysis to identify what's happening and why. |
| [Overtime / Trend](agents/overtime-trend.md) | Time-series analysis to identify trends, detect anomalies, decompose seasonality, and produce annotated timelines. |
| [Cohort Analysis](agents/cohort-analysis.md) | Retention curves, cohort comparison, vintage analysis, and cohort LTV to reveal how behavior evolves over time. |
| [Root Cause Investigator](agents/root-cause-investigator.md) | Iteratively drills down through dimensions to find the specific, actionable root cause of a metric change. |
| [Opportunity Sizer](agents/opportunity-sizer.md) | Quantifies business value of an opportunity or fix with sensitivity analysis on key assumptions. |
| [Minigame Health Assessor](agents/minigame-health-assessor.md) | **Scope: `minigame`** — Domain-specialized PM front door for minigame analytics. Four modes: health-check, comparison, deep-dive, pm-question. Only activates when `vertical: minigame`. |

### Validation & Verification

| Agent | Description |
|---|---|
| [Validation](agents/validation.md) | Re-derives key numbers, checks arithmetic, cross-references sources, and flags statistical errors. |
| [Cross-Verification](agents/cross-verification.md) | Verifies findings via same-source, different-calculation-path checks; produces confidence scores and provenance records. |

### Storytelling & Visualization

| Agent | Description |
|---|---|
| [Story Architect](agents/story-architect.md) | Designs a narrative-first storyboard (Context -> Tension -> Resolution) before any charting happens. |
| [Narrative Coherence Reviewer](agents/narrative-coherence-reviewer.md) | Reviews the storyboard for coherent flow, progressive depth, and no story gaps before charts are generated. |
| [Chart Maker](agents/chart-maker.md) | Generates a single styled chart from data and a chart spec, applying theme and annotation standards. |
| [Visual Design Critic](agents/visual-design-critic.md) | Reviews charts against the SWD checklist and produces specific, code-level fix reports. |
| [Storytelling](agents/storytelling.md) | Turns raw analysis outputs into a stakeholder-ready narrative tied to the original business question. |

### Presentation & Export

| Agent | Description |
|---|---|
| [Deck Creator](agents/deck-creator.md) | Creates a complete Marp slide deck from narrative + charts with theme, speaker notes, and formatting. |
| [Google Slides Creator](agents/google-slides-creator.md) | Creates a live, editable Google Slides presentation using the Layout Library with theme support. |
| [Google Slides Reviewer](agents/google-slides-reviewer.md) | Quality gate that reviews and fixes formatting issues in Google Slides after creation. |
| [Google Doc Creator](agents/google-doc-creator.md) | Creates a formatted Google Doc from narrative and charts with proper heading hierarchy and image placement. |
| [Google Doc Reviewer](agents/google-doc-reviewer.md) | Quality gate that reviews and fixes formatting issues in Google Docs after creation. |

### Experimentation

| Agent | Description |
|---|---|
| [Experiment Designer](agents/experiment-designer.md) | Designs experiments with power estimation, guardrail selection, and pre-registered decision rules. |
| [Experiment Analyzer](agents/experiment-analyzer.md) | Conducts complete experiment analysis -- SRM validation, treatment effects, segments, novelty checks, guardrails. |
| [Experiment Readout](agents/experiment-readout.md) | Transforms experiment results into a stakeholder-ready readout with ramp plan and follow-up proposals. |

### Advanced Planning & Feedback

| Agent | Description |
|---|---|
| [Feedback Synthesizer](agents/feedback-synthesizer.md) | Takes V1 findings and stakeholder feedback, categorizes it, and produces a structured V2 investigation plan. |
| [Weekly Digest](agents/weekly-digest.md) | Generates an executive-ready weekly email summary from Google Slides/Docs links, classified by team vertical. |

---

## Verticals (Multi-Team Support)

The AI Analyst supports multiple analytical teams within Monopoly GO through a **vertical** system. Each vertical is an analytical domain (minigame events, economy, retention, UA, social) with its own tables, metrics, and optionally specialized agents/skills.

### How It Works

1. `.knowledge/active.yaml` contains a `vertical` field (default: `general`)
2. At session start, Knowledge Bootstrap loads domain context from `.knowledge/verticals/{vertical}/domain.md`
3. Skills/agents tagged with a vertical scope only activate when that vertical is active
4. Universal (unscoped) skills/agents work for all verticals

### Available Verticals

| Vertical | Description | Specialized Agents | Specialized Skills |
|----------|-------------|--------------------|--------------------|
| `minigame` | Event performance, health, coop, liveops | Minigame Health Assessor | Coop Analysis, JIRA Incidents |
| `economy` | Currency flows, sinks/sources, shop | _(add your own)_ | _(add your own)_ |
| `retention` | Player lifecycle, churn, reactivation | _(add your own)_ | _(add your own)_ |
| `ua` | Acquisition, campaigns, LTV payback | _(add your own)_ | _(add your own)_ |
| `social` | Friend graphs, gifting, teams | _(add your own)_ | _(add your own)_ |
| `general` | Cross-cutting, no domain routing | — | — |

### Setting Up Your Vertical

```yaml
# .knowledge/active.yaml
vertical: economy  # or: minigame, retention, ua, social, general
```

### Adding Domain Context

Create `.knowledge/verticals/{your-vertical}/domain.md` with:
- Key concepts and terminology
- Primary tables and columns
- Specialized agents/skills (if any)
- Routing rules for domain questions
- Visualization standards and known patterns

See `.knowledge/verticals/_template/domain.md` for the full template.

### What New Analysts Should Do

1. Clone the repo
2. Run `/setup` — it asks for your vertical and configures `active.yaml`
3. If your vertical folder doesn't exist yet, create it from the template
4. Add your domain-specific tables, metrics, and quirks to `domain.md`
5. Optionally add specialized skills/agents — tag them with `scope: {your-vertical}`

### Scope Rules

- **`scope: all`** (or no scope) — activates for every vertical
- **`scope: minigame`** — only activates when `vertical: minigame` is set
- When a scoped skill's trigger fires but the vertical doesn't match, it's skipped silently
- New verticals can add their own scoped skills without touching existing ones

---

## Changelog

| Date | Change |
|---|---|
| 2026-05-06 | Added multi-vertical support system. New: `.knowledge/verticals/` folder structure, `vertical` field in `active.yaml`, scope tags on skills/agents tables, domain-specific routing in CLAUDE.md workflow, vertical context loading in knowledge-bootstrap. Minigame-specific skills (Coop Analysis, JIRA Incidents) and agents (Minigame Health Assessor) now scoped to `vertical: minigame`. New analysts on other verticals (economy, retention, UA, social) can add their domain context without modifying core files. |
| 2026-05-01 | Added `monopoly-go` brand theme at `themes/brands/monopoly-go/`. Deleted `BUILD_STATUS.yaml`. Updated `pyproject.toml` (author, version 2.0, added 8 dependencies). |
| 2026-05-01 | Cleanup: 60 -> 51 skills, 38 -> 28 agents. Merged: log-correction into feedback-capture, datasets into data-inspect. Deleted: demo, first-run-welcome, setup-dev-context, demo-breakout, story-extractor, presentation-doctor, receipt-generator, comms-drafter, CONTRACT_TEMPLATE. Archived: compare-datasets. Added: hex-access. Merged gdoc master plan into google-doc-export skill (heading hierarchy, content source mapping, error matrix, edge cases). Deleted Snowflake/Postgres setup guides and scripts. |
| 2026-04-29 | Added hex-access skill (CLI via WSL). Added SQL formatting rules to bigquery-access. |
| 2026-04-09 | Initial reference document created. |
