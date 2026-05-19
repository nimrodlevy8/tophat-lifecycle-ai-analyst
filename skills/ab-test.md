# AB Test Analysis

Evaluate experiments: statistical rigor, impact quantification, segment-level effects, and a clear ship/no-ship recommendation.

## Methodology

### 1. Experiment Setup Review
- Confirm: what is the hypothesis? What is the treatment? What are the primary and guardrail metrics?
- Check randomization unit (user-level, device-level, etc.)
- Verify allocation percentages and that groups are balanced on key dimensions (tenure, activity segment, geo)

### 2. Sample Size & Duration Check
- Confirm sufficient sample for the expected effect size
- Check if the test has been running long enough for the metrics to mature (e.g., D7 retention needs at least 7 days post-exposure)

### 3. Statistical Testing
- Primary metrics: run two-sided hypothesis tests
- Report: point estimate, confidence interval, p-value, and relative lift
- For retention/conversion metrics: proportion z-test or chi-square
- For revenue/continuous metrics: t-test or Mann-Whitney if non-normal
- For multiple comparisons: apply Bonferroni or BH correction and note it

### 4. Segment Cuts
Default cuts for every experiment (unless not applicable):
- Activity segment (Regular, Occasional, Casual, etc.)
- Tenure bucket
- Geo tier
- Platform (iOS vs Android)

Flag heterogeneous treatment effects — if the treatment helps Occasionals but hurts Regulars, that's critical.

### 5. Guardrail Check
- Verify no significant degradation on guardrail metrics
- Common guardrails: revenue, session count, crash rate, OOR/OOC rates

### 6. Recommendation
- Ship / Don't ship / Extend (with reasoning)
- If shipping: suggest rollout plan (which segments first, any holdout?)
- If not shipping: what would need to change?

## Output Format
Structure every AB test readout as:
1. **Executive summary** (2-3 sentences: what was tested, what happened, what to do)
2. **Setup** (hypothesis, treatment, allocation, duration, sample sizes)
3. **Primary metric results** (table with control, treatment, lift, CI, p-value)
4. **Guardrail results** (same format)
5. **Segment cuts** (table or heatmap)
6. **Recommendation** (ship/no-ship with reasoning)

<!-- TODO: Fill in team-specific standards -->
<!-- Feed me: 
  - What statistical significance threshold do you use? (p < 0.05? 0.1?)
  - Do you use sequential testing / always-valid p-values?
  - What's your standard MDE target?
  - What are the standard guardrail metrics?
  - Example AB test readouts from past experiments
  - Which experimentation platform do you use? (Statsig, internal, etc.)
  - How are experiment assignments stored in BigQuery?
-->
