# AB Test Analysis

## When to use
Evaluate an experiment: significance, impact, segment cuts, recommendation.

## Methodology
1. Confirm test parameters: variants, allocation, duration, primary metric.
2. Pull aggregate results per variant.
3. Run statistical significance tests (z-test for proportions, t-test for means).
4. Cut by key segments: lifecycle stage, geo tier, activity segment.
5. Check for:
   - Sample ratio mismatch (SRM)
   - Novelty/primacy effects (time trends)
   - Interaction with concurrent tests
6. Present: winner/loser/inconclusive, effect size (absolute + relative), confidence interval.
7. Recommend: ship, iterate, or kill — with specific reasoning.
