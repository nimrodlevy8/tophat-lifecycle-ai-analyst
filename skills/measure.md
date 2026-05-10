# Measurement Framework Development

Design KPIs, success metrics, and instrumentation plans for features, initiatives, or experiments. This is about defining *how we'll know if something worked* before it launches.

## Methodology

### 1. Understand the Initiative
- What is being built/launched/changed?
- What is the goal? (Increase retention? Drive revenue? Improve engagement?)
- Who is the target audience? (Which segments?)
- What's the timeline?

### 2. Define the Metric Hierarchy

#### North Star Metric
The single metric that best captures whether this initiative succeeded. Must be:
- Directly influenced by the initiative
- Measurable in BigQuery within the evaluation window
- Meaningful to the business

#### Primary Metrics (2-3)
Leading indicators that the North Star is moving. These should be observable sooner than the North Star.

#### Guardrail Metrics (2-3)
Metrics that should NOT degrade. If they do, the initiative may be causing harm even if the primary metrics improve.

#### Diagnostic Metrics
Deeper metrics for understanding *why* the primary metrics moved (or didn't). Not for success/fail decisions, but for learning.

### 3. Define Targets
- What does "success" look like? (Minimum detectable effect, target lift)
- What's the baseline for each metric?
- How long do we need to observe before we can evaluate?

### 4. Instrumentation Check
- Can we measure all defined metrics with existing BigQuery tables?
- If not, what new events/columns/tables are needed?
- Who needs to implement the instrumentation? (Client team, server team, data eng?)

### 5. Evaluation Plan
- How will we evaluate? (AB test, pre/post, synthetic control?)
- What segments should we cut by?
- When will we do the first read? Final read?

## Output Format
1. **Initiative summary** (what, why, who, when)
2. **Metric hierarchy** (table: metric name, definition, source table, baseline, target)
3. **Instrumentation gaps** (what's missing and who needs to build it)
4. **Evaluation plan** (method, timeline, segment cuts)
5. **Risks & assumptions** (what could invalidate the measurement)

<!-- TODO: Add team-specific metric taxonomy and standards -->
<!-- Feed me:
  - Your standard metric definitions (how exactly you calculate retention, ARPDAU, etc.)
  - Past measurement frameworks you've built
  - Instrumentation/event taxonomy if documented
  - Standard evaluation timelines for different metric types
-->
