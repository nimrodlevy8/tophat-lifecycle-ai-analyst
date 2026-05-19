# Agent Index

## System Variables (auto-resolved)
| Variable | Value | Used in |
|----------|-------|---------|
| `{{DATE}}` | Current date, YYYY-MM-DD | All agent output filenames |
| `{{DATASET_NAME}}` | Short name derived from data path or user input | File naming, report headers |
| `{{BUSINESS_CONTEXT_TITLE}}` | Short title derived from `{{BUSINESS_CONTEXT}}` | Question brief header |
| `{{RUN_ID}}` | Unique run identifier (YYYY-MM-DD_question-slug) | Run Pipeline, Resume Pipeline |
| `{{RUN_DIR}}` | Per-run output directory path | All agents during pipeline |
| `{{SQL_PATTERNS}}` | Archaeology-retrieved SQL patterns | Analysis agents |
| `{{CORRECTIONS}}` | Logged corrections for current context | Analysis agents |
| `{{LEARNINGS}}` | Category-specific learnings | Question Framing, Storytelling |
| `{{ENTITY_INDEX}}` | Disambiguation index | Question Router |
| `{{ORG_CONTEXT}}` | Business context (glossary, products, teams) | Question Framing, Storytelling |
| `{{THEME}}` | Active theme name | Chart Maker, Deck Creator |
| `{{CONTEXT}}` | Presentation context (workshop/talk/analysis) | Story Architect, Deck Creator |
| `{{STORYBOARD}}` | Story Architect output | Chart Maker, Storytelling |
| `{{FIX_REPORT}}` | Visual Design Critic feedback | Chart Maker (fix pass) |
| `{{DECK_FILE}}` | Generated deck path | Visual Design Critic |
| `{{CONFIDENCE_GRADE}}` | Validation confidence score (A-F) | Storytelling, Deck Creator |

## Agents
| Agent | Path | Scope | Invoke When |
|-------|------|-------|-------------|
| Question Framing | `agents/question-framing.md` | all | User provides a business problem to analyze |
| Hypothesis | `agents/hypothesis.md` | all | Questions are framed, need testable hypotheses |
| Data Explorer | `agents/data-explorer.md` | all | Need to understand what data exists in a source |
| Descriptive Analytics | `agents/descriptive-analytics.md` | all | Need to analyze a dataset (segmentation, funnels, drivers) |
| Overtime / Trend | `agents/overtime-trend.md` | all | Need time-series analysis or trend identification |
| Cohort Analysis | `agents/cohort-analysis.md` | all | Need cohort retention curves, LTV analysis, or vintage comparison |
| Root Cause Investigator | `agents/root-cause-investigator.md` | all | Initial analysis found an anomaly — need to drill down iteratively to find the specific root cause |
| Opportunity Sizer | `agents/opportunity-sizer.md` | all | Root cause identified or opportunity found — quantify the business impact with sensitivity analysis |
| Experiment Designer | `agents/experiment-designer.md` | all | Need to test a causal hypothesis — designs A/B tests or quasi-experimental analyses with power estimation and decision rules |
| Story Architect | `agents/story-architect.md` | all | Analysis is complete — designs the storyboard (narrative beats + visual mapping) before any charting. Pass `{{CONTEXT}}` for workshop/talk closing sequences. |
| Chart Maker | `agents/chart-maker.md` | all | Need to generate a specific chart. |
| Visual Design Critic | `agents/visual-design-critic.md` | all | After Chart Maker generates charts — reviews against SWD checklist. After Deck Creator — reviews slide-level design with `{{DECK_FILE}}` and `{{THEME}}`. |
| Narrative Coherence Reviewer | `agents/narrative-coherence-reviewer.md` | all | After Story Architect produces the storyboard, before charting — reviews story flow, beat structure, and Closing beats if present |
| Storytelling | `agents/storytelling.md` | all | Analysis and charts are complete, need a narrative |
| Cross-Verification | `agents/cross-verification.md` | all | After analysis (step 6.5) — verify analytical claims via independent calculation paths (Types A-D: boundary, parts-to-whole, ratio recompute, algebraic identity). Includes reproducibility checks. |
| Validation | `agents/validation.md` | all | Need to verify findings before presenting |
| Deck Creator | `agents/deck-creator.md` | all | Need to create a presentation from analysis. Supports `{{THEME}}` (analytics-dark) and `{{CONTEXT}}` (workshop/talk closing sequence). |
| Google Slides Creator | `agents/google-slides-creator.md` | all | Need a live, editable Google Slides deck (alternative to Deck Creator). Uses `{{NARRATIVE}}`, `{{STORYBOARD}}`, optional `{{THEME}}` (light/dark) and `{{DECK_TITLE}}`. Requires Google Workspace MCP. |
| Google Slides Reviewer | `agents/google-slides-reviewer.md` | all | Auto-invoked after Google Slides Creator -- reviews formatting (overflow, overlap, fonts, colors) and self-applies fixes. Max 2 iterations. |
| Google Doc Creator | `agents/google-doc-creator.md` | all | Need a live, editable Google Doc from analysis narrative + charts. Handles image placement (bottom-to-top), heading hierarchy, and formatting. Requires Google Workspace MCP. |
| Google Doc Reviewer | `agents/google-doc-reviewer.md` | all | Auto-invoked after Google Doc Creator -- reviews heading hierarchy, image placement, spacing, formatting. Self-applies fixes. Max 2 iterations. |
| Experiment Analyzer | `agents/experiment-analyzer.md` | all | Full experiment analysis — 8-question framework: SRM → treatment effect → reliability → segments → duration → ROI → recommendation → follow-ups. Takes raw experiment data, produces nuanced conditional recommendation. |
| Experiment Readout | `agents/experiment-readout.md` | all | Transform experiment analysis into stakeholder-ready readout with executive summary, visualizations, per-segment decisions, ramp plan, and follow-up experiments. Adapts to audience (executive/technical/cross-functional). |
| Hypothesis Sharpener | `agents/hypothesis-sharpener.md` | all | Takes a vague hunch and transforms it into a testable hypothesis with precise metrics, comparison groups, natural experiments, and accept/reject criteria. Called by `/analysis-design` skill. |
| Confound Scanner | `agents/confound-scanner.md` | all | Adversarial agent that finds threats to validity — concurrent changes, data quality issues, selection biases. Argues AGAINST the hypothesis to make the investigation airtight. Called by `/analysis-design` skill. |
| Feedback Synthesizer | `agents/feedback-synthesizer.md` | all | Takes V1 findings + messy stakeholder feedback, categorizes it (methodological flaws, missing confounds, reframes, new analyses), and produces a structured V2 investigation plan with stakeholder answer map. Called by `/analysis-design` skill. |
| Minigame Health Assessor | `agents/minigame-health-assessor.md` | **minigame** | Domain-specialized PM front door for minigame analytics. Four modes: `health-check` (event KPI assessment), `comparison` (cross-minigame/iteration ranking), `deep-dive` (anomaly investigation), `pm-question` (ad-hoc product questions). Knows all 7 minigame types, KPIs, patterns (PAT-001–007), past readouts, and query archaeology. Auto-detects mode from question. Orchestrates existing agents (Descriptive Analytics, Root Cause Investigator, Chart Maker, etc.) with domain context. Only activates when `vertical: minigame` is set in `.knowledge/active.yaml`. |
| Weekly Digest | `agents/weekly-digest.md` | all | Generate an executive-ready weekly email summary from Google Slides/Docs links. Fetches documents via `gws` CLI, classifies by team (New Minigame Vertical vs LRK Vertical), extracts key findings, and produces a structured markdown email. |
