# Alerting & Anomaly Detection

Detect when metrics deviate from expected behavior, diagnose root causes, and maintain monitoring standards.

## Methodology

### Reactive: "Is this metric normal?"
1. **Establish baseline**: Pull the metric for the trailing 30-90 days. Compute mean, std dev, and day-of-week patterns.
2. **Compare current value**: How many standard deviations from expected? Account for seasonality (weekday vs weekend, event days vs non-event).
3. **Contextualize**: Check if a season change, event start/end, app update, or experiment ramp happened around the anomaly.
4. **Segment the anomaly**: Is it broad (all segments) or concentrated (one geo, one platform, one tenure bucket)?
5. **Diagnose**: Drill into upstream/downstream metrics to find the root cause. E.g., if ARPDAU dropped, check: DAU change? Payer rate change? ARPPU change?
6. **Report**: Current value, expected value, deviation magnitude, likely cause, recommended action.

### Proactive: "Set up monitoring for X"
1. Define the metric and its canonical calculation (from `context/methodology/metric_definitions.md`)
2. Set baseline window (recommend 30 days rolling, excluding known anomalies)
3. Set threshold: default to ±2 standard deviations for alerts, ±3 for critical
4. Define segment-level monitoring where relevant (e.g., alert if Occasionals retention drops even if overall is fine)
5. Output: the monitoring query, threshold logic, and recommended check frequency

## Common Anomaly Patterns in MGO
- **Season transitions**: metrics shift at season boundaries — not anomalies
- **Event-driven spikes**: flash events and tentpoles cause expected surges
- **Weekend effects**: DAU/engagement patterns differ on weekends
- **App updates**: new versions can cause metric shifts

<!-- TODO: Fill in operational details -->
<!-- Feed me:
  - What monitoring tools do you currently use? (Looker alerts, custom SQL jobs, Datadog, etc.)
  - What are the critical metrics that are already monitored?
  - What thresholds are currently in place?
  - Examples of past anomalies and how they were diagnosed
  - Event calendar with dates (to distinguish expected shifts from real anomalies)
-->
