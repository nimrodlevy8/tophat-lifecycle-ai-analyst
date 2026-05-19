---
name: question-router
description: |
  Classify incoming analytical questions into complexity levels (L1-L5) and route them to the appropriate response path. This skill ensures that simple questions get quick answers without unnecessary overhead, while complex investigations get the full analytical treatment they deserve. Use this skill at the start of EVERY user interaction that involves data analysis, metrics, business questions, or investigative requests. Trigger on phrases like "analyze", "why did", "what's happening with", "how many", "compare", "show me", "breakdown", "investigate", "root cause", "size the opportunity", "design an experiment", "create a deck", "run the pipeline", or ANY question that asks about data, metrics, trends, segments, funnels, user behavior, revenue, conversion, retention, or any other analytical topic. Also apply when users ask follow-up questions mid-analysis, when they request charts or visualizations, when they mention datasets or tables, when they ask about business performance, when they want to understand why something changed, or when they need to make a data-driven decision. This skill should be your FIRST step before launching any analytical workflow — it prevents wasting time on over-engineered responses to simple questions and ensures complex questions get the depth they deserve. Even if the question seems straightforward, use this skill to confirm the appropriate level of depth. Apply liberally.
---

# Skill: Question Router

## Purpose
Classify incoming user questions into complexity levels (L1-L5) and route
them to the appropriate response path. This replaces the old "skip-step"
logic with a structured classification that adapts the workflow depth to
the question's actual needs.

## When to Use
- At the start of every user interaction that looks like an analytical request
- Before launching the full 18-step pipeline
- When the user asks a follow-up question mid-analysis

## Classification Levels

### L1: Factual Lookup
**Pattern:** User wants a specific number or fact from the data.
**Examples:**
- "How many users signed up in March?"
- "What's the average order value?"
- "How many products are in the electronics category?"

**Response path:** Query the data directly. Return the answer with source
citation (table, column, filter). No agents needed.

**Time:** ~30 seconds

### L2: Simple Comparison
**Pattern:** User wants to compare two things or see a breakdown.
**Examples:**
- "Compare conversion rates by device"
- "Show me revenue by category"
- "What's the split of users by acquisition channel?"

**Response path:** Query + quick chart. Use `chart_helpers` directly.
Apply Visualization Patterns skill. No full pipeline.

**Time:** ~2 minutes

### L3: Guided Analysis
**Pattern:** User has a specific analytical question requiring multiple steps.
**Examples:**
- "Why did conversion drop last month?"
- "Which user segment has the highest LTV?"
- "Is our new checkout flow performing better?"

**Response path:** Subset of the pipeline — Frame → Explore → Analyze →
Validate → Present findings. Skip storyboard/deck unless requested.
Use 3-5 agents.

**Time:** ~10 minutes

### L4: Deep Investigation
**Pattern:** User needs root cause analysis, opportunity sizing, or
experiment design.
**Examples:**
- "Investigate why mobile revenue dropped 15% in Q3"
- "Size the opportunity if we fix the cart abandonment issue"
- "Design an A/B test for the new pricing page"

**Response path:** Full pipeline minus deck. Frame → Hypothesize → Explore →
Analyze → Root Cause → Validate → Size → Present findings.
Use 6-10 agents.

**Time:** ~20 minutes

### L5: Full Presentation
**Pattern:** User wants a complete analysis with a polished slide deck.
**Examples:**
- "Run the full pipeline on Q4 performance"
- `/run-pipeline`
- "Build me a board-ready deck on our retention problem"

**Response path:** Complete 18-step pipeline. All agents, full storyboard,
charts, narrative, and Marp deck.

**Time:** ~30-45 minutes

## Classification Algorithm

### Fast-Path Detection (optional shortcut for obvious L1 questions)

Before running the full classification workflow, check if the question matches
an obvious L1 pattern. If YES, skip to L1 execution immediately. If NO or
UNCERTAIN, proceed to Step 0.

**Trigger phrases for fast-path L1:**
- Starts with "how many" or "how much"
- Starts with "what's the total" or "what's the average"
- Starts with "count of" or "number of"
- Contains "count" + single metric/entity + optional time filter
- Examples:
  - "how many orders last month?"
  - "what's the total revenue in Q4?"
  - "count of users who converted"

**Do NOT fast-path if:**
- Question contains "compare", "by", "breakdown", or "split"
- Question contains "why", "investigate", or "analyze"
- Question mentions multiple metrics or dimensions
- Question references a product change or hypothesis
- You're uncertain whether it's genuinely simple

**Why fast-path matters:** L1 questions don't benefit from the full classification
overhead. The user wants a quick answer, not a classification report. Fast-path
saves ~40 seconds and ~7-9k tokens for simple lookups.

**Output format for fast-path L1:**
- Answer the question directly
- Include source citation (table, column, filter)
- Offer 2-3 contextual next actions
- Skip the classification documentation

If you use the fast-path, you're done — don't proceed to Step 0 or beyond.

---

### Step 0: Pre-flight (runs on every query before classification)

Enrichment steps — never block routing. If any sub-step fails, skip it silently.
**IMPORTANT:** Only report pre-flight findings if they actually find something.
Silent skip if nothing found.

1. **Feedback check** — The Feedback Capture skill runs BEFORE this router.
   By the time a message reaches here, corrections/learnings are already
   captured. If the message was purely feedback (no analytical question),
   it was handled upstream — skip routing.

2. **Entity disambiguation** — If the entity index is loaded (from bootstrap):
   - Call `resolve_entity(query_text, entity_index)` from
     `helpers/entity_resolver.py`.
   - If matches found, call `format_disambiguation(matches)` and set
     `{{RESOLVED_ENTITIES}}` for downstream agents.
   - Example: "why is cvr dropping?" → Resolved: 'cvr' -> conversion_rate (metric)
   - **ONLY REPORT IF MATCHES FOUND.** If no matches, silent skip.

3. **Corrections check** — Read `.knowledge/corrections/index.yaml`.
   - If `total_corrections > 0` for the active dataset, set
     `{{CORRECTION_COUNT}}` so analysis agents check the correction log
     before writing SQL (e.g., known join pitfalls, filter requirements).
   - **ONLY REPORT IF CORRECTIONS EXIST.** If index missing or count is 0, silent skip.

4. **Dataset detection** — Before classifying, check whether the question
   references a dataset other than the currently active one.
   - Read `.knowledge/datasets/` to get all known dataset IDs and display names.
   - Scan the user's question for exact or fuzzy matches to any dataset name.
   - **ONLY REPORT IF MISMATCH FOUND.** If no dataset reference or matches active, silent skip.
   - If a non-active dataset is referenced:
     - Inform the user: "It looks like you're asking about **{display_name}**, but
       the active dataset is **{active_display_name}**."
     - Offer: "Want me to switch? (`/switch-dataset {id}`)"
     - Do NOT proceed with analysis until the user confirms which dataset to use.

5. **Archaeology note** — The Query Archaeology skill provides SQL pattern
   context (prior queries, reusable CTEs) to analysis agents when available.
   No action needed here — just acknowledge it flows downstream automatically.

After pre-flight completes, proceed to Step 1.

---

### Step 1: Parse the question

Extract:
- **Subject:** What entity/metric is being asked about?
- **Action:** Lookup, compare, analyze, investigate, or present?
- **Scope:** Single metric, breakdown, multi-dimensional, or end-to-end?
- **Output expectation:** Number, chart, findings, or deck?

### Step 2: Score complexity signals

| Signal | L1 | L2 | L3 | L4 | L5 |
|--------|----|----|----|----|-----|
| Asks for a single number | +3 | | | | |
| Uses "compare" or "by {dimension}" | | +3 | | | |
| Uses "why", "investigate", "root cause" | | | | +3 | |
| Uses "analyze", "what's happening with" | | | +3 | | |
| Mentions "deck", "presentation", "slides" | | | | | +3 |
| Uses `/run-pipeline` | | | | | +5 |
| Mentions sizing, opportunity, impact | | | | +2 | |
| Mentions experiment, A/B test | | | | +2 | |
| Question has multiple sub-questions | | | +2 | +1 | |
| "Quick" or "just" qualifier | +2 | +1 | | | |

Assign the level with the highest score. Ties break toward the lower level
(prefer faster response).

### Step 3: Adapt from user profile

If `.knowledge/user/profile.md` exists, read the user's preferences:
- **Detail level = "executive-summary":** Bias one level down (L3 → L2)
- **Detail level = "deep-dive":** Bias one level up (L2 → L3)
- **Technical level = "advanced":** Show more SQL, skip explanations
- **Technical level = "beginner":** Add more context, explain terms

### Step 4: Respond based on classification level

**For L1-L2:** Execute immediately. No confirmation needed. Streamlined output:
- Answer the question (or produce chart)
- Include source citation (table, column, filter)
- Offer 2-3 contextual next actions
- **Do NOT include:** Full classification rationale, pre-flight details (unless
  something was found), complexity scoring table, skill adherence checklist.
  Save that documentation for your own internal tracking — the user just wants
  the answer.

**For L3-L5:** Brief the user on the plan BEFORE executing:
```
I'd classify this as a **[Level] — [Label]**. Here's my plan:
1. [Step summary]
2. [Step summary]
...
Estimated time: ~[X] minutes. Want me to proceed, or adjust the scope?
```

Include any relevant pre-flight findings (dataset mismatch, corrections available,
resolved entities) in this confirmation message.

The user can:
- **Confirm:** Proceed with the plan
- **Adjust up:** "Go deeper" → bump to next level
- **Adjust down:** "Just give me the quick answer" → drop to lower level

---

## Integration with Pipeline

When routed to L3+, the Question Router hands off to the appropriate agents
by setting the entry point in the Default Workflow:

| Level | Entry Point | Exit Point | Validation Tier |
|-------|-------------|------------|-----------------|
| L1 | Direct query | Answer inline | Tier 1 only (always-on) |
| L2 | Direct query + chart | Answer inline | Tier 1 only (always-on) |
| L3 | Step 1 (Frame) | Step 7 (Validate) — present findings inline | Tier 1 always + Tier 2 offered (CP 2.1) |
| L4 | Step 1 (Frame) | Step 8 (Size) — present findings inline | Tier 2 default (CP 2.1 menu) |
| L5 | Step 1 (Frame) | Step 18 (Close the Loop) — full deck | Tier 2 default, Tier 3 available (CP 2.1 menu) |

---

## Contextual Suggestions & Proactive Recommendations

After delivering results at any level, offer 2-3 relevant next actions based
on what was just completed. Match suggestions to the level and findings.

**MANDATORY: At least one suggestion must be a proactive analytical
recommendation** — a better way to look at the data, a deeper cut, or an
additional step that would add insight. This is not optional. Examples:
- If you showed a time series: suggest cohort analysis to control for mix shift
- If you analyzed in aggregate: suggest segmenting by the most likely confound
- If the time window was short: suggest extending to capture full cycles
- If you found a trend: suggest decomposing to isolate the driver
- If you showed a snapshot: suggest a before/after comparison

**After L1/L2 results:**
- "Want to break this down by [dimension from schema]?"
- "Want to see how this trended over time?"
- "Want to compare this across [available segment]?"
- **[Proactive]** "This number alone doesn't tell us much — segmenting by
  [likely confound] would reveal whether the change is uniform or concentrated.
  Want me to add that cut?"

**After L3 findings:**
- "Want me to investigate the root cause of [top finding]?"
- "Want to size the opportunity if we fix [issue]?"
- "Want a deck of these findings for [audience]?"
- **[Proactive]** "[Specific methodology recommendation based on findings —
  e.g., 'A cohort view would separate the redesign effect from seasonal
  patterns. Want me to re-run with cohorts?']"

**After L4 investigation:**
- "Want me to design an experiment to test [hypothesis]?"
- "Want a presentation-ready deck?"
- "Want to check this against [related metric from dictionary]?"
- **[Proactive]** "[Specific next-level recommendation — e.g., 'The root cause
  points to a specific user segment. A sensitivity analysis would quantify the
  revenue impact of fixing it. Want me to size that?']"

**After L5 deck delivery:**
- "Want to archive this analysis? (`/archive`)"
- "Want to explore a related question?"
- "Want to export in a different format? (`/export`)"
- **[Proactive]** "[Strategic recommendation — e.g., 'This analysis looked at
  the past 30 days. A 6-month retrospective would reveal whether this is a new
  trend or a recurring pattern. Want me to extend?']"

Always tailor suggestions to the actual findings — reference specific metrics,
segments, or anomalies discovered. Generic suggestions ("want to know more?")
are not helpful.

---

## Edge Cases

- **Ambiguous questions:** Default to L2, ask a clarifying question. "Do you
  want a quick breakdown, or should I investigate the drivers?"
- **Follow-up after analysis:** Re-classify. "Now make a deck" bumps a
  completed L3 to L5 (but reuses existing analysis, skips to Step 9).
- **Multiple questions in one message:** Classify each separately. Execute
  the highest-level one, note the others as follow-ups.
- **Non-analytical requests:** "Help me write a SQL query" or "Explain this
  chart" — handle directly without classification.

---

## Anti-Patterns

1. **Never run the full 18-step pipeline for an L1 question.** "How many
   users do we have?" should not trigger hypothesis generation.
2. **Never skip validation for L3+ questions.** Even guided analyses need
   a sanity check before presenting results.
3. **Never assume the user wants a deck.** Only create slides if explicitly
   requested or classified as L5.
4. **Never re-classify mid-execution without user input.** If you realize
   the question is more complex than initially classified, pause and ask.
5. **Never include classification overhead in L1/L2 output.** The user asked
   "how many orders?" — give them the number, not a 3-page classification report.

---

## Why These Changes Matter

**Fast-path for L1:** Testing showed the full classification workflow adds
~40 seconds and ~9k tokens for simple lookups. The user who asks "how many
orders last month?" doesn't need to see pre-flight checks, scoring tables,
and skill adherence checklists — they need the answer. Fast-path detection
identifies obvious L1 questions and shortcuts to execution.

**Silent pre-flight:** Pre-flight enrichment (entity disambiguation, corrections
check) adds value ONLY when it finds something. Reporting "no entity matches,
no corrections, no dataset conflict" adds noise without insight. The improved
version only surfaces findings when they exist.

**Streamlined L1/L2 output:** The classification rationale matters for L3+
where you're asking the user to commit 10-20 minutes. For L1/L2, the decision
is already made — just execute and deliver. Save the process documentation for
internal tracking.
