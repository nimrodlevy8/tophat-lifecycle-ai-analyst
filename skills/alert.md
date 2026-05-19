# Alerting & Anomaly Detection

## When to use
Something looks off in a metric, or building/checking monitoring.

## Methodology
1. Identify the metric and its expected baseline (trailing 7d/28d average).
2. Quantify the deviation: absolute change, z-score, % deviation from baseline.
3. Check correlated metrics — is this isolated or part of a broader shift?
4. Check external factors: app updates, events calendar, seasonality.
5. Segment the anomaly: which player groups are most affected?
6. Classify: real issue vs. noise vs. expected (event-driven).
7. If real: recommend investigation path or immediate action.
