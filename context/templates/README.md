# SQL Templates

Reusable query patterns extracted from past analyses. The analyst should check here before writing a query from scratch.

## How to Add a Template

Name the file descriptively (e.g., `retention_by_segment.sql`) and include:

```sql
-- Template: Retention by Activity Segment
-- Use case: Standard Dx retention broken out by activity segment
-- Parameters: {date_from}, {date_to}, {retention_day}
-- Source tables: dataset.player_activity, dataset.segments
-- Last used: 2025-XX-XX

SELECT
  s.activity_segment,
  COUNT(DISTINCT CASE WHEN a.event_date = cohort.install_date THEN a.user_id END) AS cohort_size,
  COUNT(DISTINCT CASE WHEN a.event_date = DATE_ADD(cohort.install_date, INTERVAL {retention_day} DAY) THEN a.user_id END) AS retained,
  -- etc.
FROM ...
```

## Priority Templates to Build

From past queries, extract patterns for:
1. Dx retention by segment (D1, D7, D14, D30)
2. ARPDAU / revenue by tenure bucket
3. Reactivation funnel by inactivity length
4. Segment migration rates (week over week)
5. Feature participation rates by segment
6. AB test metric comparison (treatment vs control)
7. Anomaly baseline calculation (rolling averages with day-of-week adjustment)
8. FTUE funnel conversion rates
9. Economy balance (rolls/cash earn vs spend)
10. Social score distribution and churn correlation
