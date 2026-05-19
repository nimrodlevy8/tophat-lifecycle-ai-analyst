# Reactivation Weekly Performance Dashboard — Design Spec

## Purpose

A weekly dashboard that answers two questions for the Lifecycle and EE teams:
1. **Performance**: How are reactivated users performing this week vs. prior weeks? (retention, monetization, engagement)
2. **Mix**: What is the composition of reactivations, and is quality shifting? (dormancy, LTV, board level, repeat-reactivator share)

**Cadence**: Refreshed weekly (Monday), covering the trailing completed week (Mon–Sun).  
**Audience**: Richa (Lifecycle PM), Steven (EE PM), and their teams.

---

## Dashboard Layout

| Section | Panels | Purpose |
|---------|--------|---------|
| **A. Executive Summary** | KPI scorecards + WoW trends | At-a-glance health check |
| **B. Volume & Trend** | Time series of daily reactivation count | Spot volume anomalies, seasonal lifts |
| **C. Retention Performance** | D1, D7, D14 retention trended weekly | Core re-engagement success metric |
| **D. Monetization** | D7 conversion rate, D7 ARPI | Are reactivations converting? |
| **E. Mix — Dormancy** | Stacked area: dormancy bucket share over time | Shift toward longer-dormant users = harder to retain |
| **F. Mix — LTV Tier** | Stacked area: LTV tier share over time | Quality of wallet returning |
| **G. Mix — Board Level** | Stacked bar: board level distribution | Pre-hook vs. post-hook feature exposure |
| **H. Mix — Repeat Reactivators** | Line: share of users with 5+ prior reactivations | Chronic re-churner inflation |
| **I. Retention by Dormancy** | Grouped bar: D7 retention per dormancy bucket | Performance × mix interaction |
| **J. Retention by LTV** | Grouped bar: D7 retention per LTV tier | Do payers retain better? |
| **K. Platform & Geo** | Table: volume, D7 ret, D7 conv by platform × geo tier | Localize issues |

---

## Section A: Executive Summary (Scorecards)

**Metrics displayed as large numbers with WoW delta:**

| Metric | Definition | Good direction |
|--------|-----------|----------------|
| Reactivated Users (weekly) | COUNT(DISTINCT user_id) reactivated in the week | Stable or aligned with campaigns |
| D7 Retention | % of weekly cohort active 7 days later | ↑ |
| D7 Conversion Rate | % making IAP within 7 days | ↑ |
| D7 ARPI | Revenue / reactivated users (7-day window) | ↑ |
| Repeat Reactivator Share | % with 5+ prior reactivations | ↓ |
| Suspicious Share | % flagged suspicious | ↓ |

### Query: Weekly Scorecards

```sql
WITH week_range AS (
  SELECT DATE_TRUNC(CURRENT_DATE() - 8, WEEK(MONDAY)) AS week_start,
         DATE_TRUNC(CURRENT_DATE() - 8, WEEK(MONDAY)) + 6 AS week_end
),

reactivations AS (
  SELECT
    k.user_id,
    k.snapshot_date,
    k.v_f_user_rpt.f_days_since_prev_activity,
    k.v_f_user_rpt.f_lt_iap_revenue,
    k.dim_user_snapshot.last_board_level,
    CASE WHEN (s.is_ever_suspicious_at_creation OR p.publisher_name = 'untrusted devices')
         THEN TRUE ELSE FALSE END AS is_suspicious
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
    ON s.user_id = k.user_id
  LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
    ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
  CROSS JOIN week_range w
  WHERE k.snapshot_date BETWEEN w.week_start AND w.week_end
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
),

reactivation_counts AS (
  SELECT user_id,
         COUNT(*) OVER (PARTITION BY user_id ORDER BY snapshot_date
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prior_reactivations
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis`
  WHERE v_f_user_rpt.is_daily_reactivated = TRUE
    AND snapshot_date >= '2023-04-01'
),

retained AS (
  SELECT r.user_id, r.snapshot_date
  FROM reactivations r
  INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` a
    ON a.user_id = r.user_id
    AND a.snapshot_date = DATE_ADD(r.snapshot_date, INTERVAL 7 DAY)
    AND a.v_f_user_rpt.is_active = TRUE
  WHERE r.is_suspicious = FALSE
),

revenue_7d AS (
  SELECT r.user_id, r.snapshot_date,
         SUM(k.v_f_user_rpt.f_iap_revenue) AS rev_7d
  FROM reactivations r
  INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
    ON k.user_id = r.user_id
    AND k.snapshot_date BETWEEN r.snapshot_date AND DATE_ADD(r.snapshot_date, INTERVAL 7 DAY)
    AND k.product_id = 105
  WHERE r.is_suspicious = FALSE
  GROUP BY r.user_id, r.snapshot_date
)

SELECT
  COUNT(DISTINCT r.user_id) AS reactivated_users,
  COUNT(DISTINCT retained.user_id) / COUNT(DISTINCT r.user_id) AS d7_retention,
  COUNT(DISTINCT CASE WHEN rev.rev_7d > 0 THEN r.user_id END) / COUNT(DISTINCT r.user_id) AS d7_conversion,
  SUM(rev.rev_7d) / COUNT(DISTINCT r.user_id) AS d7_arpi,
  COUNT(DISTINCT CASE WHEN rc.prior_reactivations >= 5 THEN r.user_id END) / COUNT(DISTINCT r.user_id) AS repeat_reactivator_share,
  COUNT(DISTINCT CASE WHEN r.is_suspicious THEN r.user_id END) / COUNT(DISTINCT r.user_id) AS suspicious_share
FROM reactivations r
LEFT JOIN retained ON retained.user_id = r.user_id AND retained.snapshot_date = r.snapshot_date
LEFT JOIN revenue_7d rev ON rev.user_id = r.user_id AND rev.snapshot_date = r.snapshot_date
LEFT JOIN reactivation_counts rc ON rc.user_id = r.user_id
WHERE r.is_suspicious = FALSE
```

---

## Section B: Volume & Trend

**Chart type**: Line chart (daily granularity, 8 weeks trailing)  
**Y-axis**: Reactivated user count  
**Color split**: Clean vs. Suspicious  
**Annotations**: Mark season starts and major LiveOps events

### Query: Daily Volume Trend

```sql
SELECT
  k.snapshot_date,
  CASE WHEN (s.is_ever_suspicious_at_creation OR p.publisher_name = 'untrusted devices')
       THEN 'Suspicious' ELSE 'Clean' END AS user_type,
  COUNT(DISTINCT k.user_id) AS reactivated_users
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
  ON s.user_id = k.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
  ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
WHERE k.snapshot_date >= CURRENT_DATE() - 57  -- 8 weeks + 1 day
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
GROUP BY ALL
ORDER BY snapshot_date
```

---

## Section C: Retention Performance (Weekly Trended)

**Chart type**: Line chart, weekly cohort  
**Y-axis**: Retention rate (%)  
**Series**: D1, D7, D14 (separate lines)  
**Benchmark line**: 8-week rolling average

### Query: Weekly Retention Trend

```sql
WITH weekly_cohorts AS (
  SELECT
    DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
    k.user_id,
    k.snapshot_date
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
    ON s.user_id = k.user_id
  LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
    ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
  WHERE k.snapshot_date >= CURRENT_DATE() - 71  -- 8 weeks + 14 days for D14 maturity
    AND k.snapshot_date <= CURRENT_DATE() - 15  -- ensure D14 has matured
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
    AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
)

SELECT
  c.cohort_week,
  COUNT(DISTINCT c.user_id) AS cohort_size,
  COUNT(DISTINCT d1.user_id) / COUNT(DISTINCT c.user_id) AS d1_retention,
  COUNT(DISTINCT d7.user_id) / COUNT(DISTINCT c.user_id) AS d7_retention,
  COUNT(DISTINCT d14.user_id) / COUNT(DISTINCT c.user_id) AS d14_retention
FROM weekly_cohorts c
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d1
  ON d1.user_id = c.user_id
  AND d1.snapshot_date = DATE_ADD(c.snapshot_date, INTERVAL 1 DAY)
  AND d1.v_f_user_rpt.is_active = TRUE
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d7
  ON d7.user_id = c.user_id
  AND d7.snapshot_date = DATE_ADD(c.snapshot_date, INTERVAL 7 DAY)
  AND d7.v_f_user_rpt.is_active = TRUE
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d14
  ON d14.user_id = c.user_id
  AND d14.snapshot_date = DATE_ADD(c.snapshot_date, INTERVAL 14 DAY)
  AND d14.v_f_user_rpt.is_active = TRUE
GROUP BY cohort_week
ORDER BY cohort_week
```

---

## Section D: Monetization

**Chart type**: Dual-axis line chart (weekly)  
**Left Y-axis**: D7 Conversion Rate (%)  
**Right Y-axis**: D7 ARPI ($)

### Query: Weekly Monetization Trend

```sql
WITH weekly_cohorts AS (
  SELECT
    DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
    k.user_id,
    k.snapshot_date
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
    ON s.user_id = k.user_id
  LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
    ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
  WHERE k.snapshot_date >= CURRENT_DATE() - 64
    AND k.snapshot_date <= CURRENT_DATE() - 8
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
    AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
),

revenue AS (
  SELECT c.user_id, c.cohort_week, c.snapshot_date,
         SUM(a.v_f_user_rpt.f_iap_revenue) AS rev_7d
  FROM weekly_cohorts c
  INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` a
    ON a.user_id = c.user_id
    AND a.snapshot_date BETWEEN c.snapshot_date AND DATE_ADD(c.snapshot_date, INTERVAL 7 DAY)
    AND a.product_id = 105
  GROUP BY c.user_id, c.cohort_week, c.snapshot_date
)

SELECT
  c.cohort_week,
  COUNT(DISTINCT c.user_id) AS cohort_size,
  COUNT(DISTINCT CASE WHEN r.rev_7d > 0 THEN c.user_id END) / COUNT(DISTINCT c.user_id) AS d7_conversion_rate,
  COALESCE(SUM(r.rev_7d), 0) / COUNT(DISTINCT c.user_id) AS d7_arpi
FROM weekly_cohorts c
LEFT JOIN revenue r ON r.user_id = c.user_id AND r.cohort_week = c.cohort_week AND r.snapshot_date = c.snapshot_date
GROUP BY c.cohort_week
ORDER BY c.cohort_week
```

---

## Section E: Mix — Dormancy Duration

**Chart type**: 100% stacked area (weekly)  
**X-axis**: Week  
**Y-axis**: Share of reactivations (%)  
**Color**: Dormancy bucket (0-7d, 8-14d, 15-30d, 31-60d, 61-90d, 91-180d, 180d+)

### Query: Dormancy Mix Over Time

```sql
SELECT
  DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
  CASE WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 7 THEN 'a.0-7d'
       WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 14 THEN 'b.8-14d'
       WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 30 THEN 'c.15-30d'
       WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 60 THEN 'd.31-60d'
       WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 90 THEN 'e.61-90d'
       WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 180 THEN 'f.91-180d'
       WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) > 180 THEN 'g.180d+'
  END AS dormancy_bucket,
  COUNT(DISTINCT k.user_id) AS reactivated_users
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
  ON s.user_id = k.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
  ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
WHERE k.snapshot_date >= CURRENT_DATE() - 57
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
  AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
  AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
GROUP BY ALL
ORDER BY cohort_week, dormancy_bucket
```

---

## Section F: Mix — LTV Tier

**Chart type**: 100% stacked area (weekly)  
**Color**: LTV bucket ($0 NP, $0-5, $5-20, $20-50, $50-100, $100-500, $500-1k, $1k+)

### Query: LTV Mix Over Time

```sql
SELECT
  DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
  CASE WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) = 0 THEN 'a.$0 (NP)'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 5 THEN 'b.$0-5'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 20 THEN 'c.$5-20'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 50 THEN 'd.$20-50'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 100 THEN 'e.$50-100'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 500 THEN 'f.$100-500'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 1000 THEN 'g.$500-1k'
       WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) > 1000 THEN 'h.$1k+'
  END AS ltv_bucket,
  COUNT(DISTINCT k.user_id) AS reactivated_users
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
  ON s.user_id = k.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
  ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
WHERE k.snapshot_date >= CURRENT_DATE() - 57
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
  AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
  AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
GROUP BY ALL
ORDER BY cohort_week, ltv_bucket
```

---

## Section G: Mix — Board Level

**Chart type**: 100% stacked bar (weekly)  
**Color**: Board level bucket (1-5, 6-10, 11-20, 21-50, 51-100, 100+)

**Why it matters**: Users BL1-5 never unlocked Tournaments or Social Minigames (Board 4 hooks). Their retention ceiling is fundamentally different — high BL1-5 share means the re-entry experience must compensate for missing feature exposure.

### Query: Board Level Mix

```sql
SELECT
  DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
  CASE WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 5 THEN 'a.BL 1-5'
       WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 10 THEN 'b.BL 6-10'
       WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 20 THEN 'c.BL 11-20'
       WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 50 THEN 'd.BL 21-50'
       WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 100 THEN 'e.BL 51-100'
       WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) > 100 THEN 'f.BL 100+'
  END AS board_level_bucket,
  COUNT(DISTINCT k.user_id) AS reactivated_users
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
  ON s.user_id = k.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
  ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
WHERE k.snapshot_date >= CURRENT_DATE() - 57
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
  AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
  AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
GROUP BY ALL
ORDER BY cohort_week, board_level_bucket
```

---

## Section H: Mix — Repeat Reactivator Share

**Chart type**: Line chart (weekly)  
**Y-axis**: % of reactivations from users with 5+ prior reactivations  
**Threshold line**: Red at 20% (quality degradation signal)

**Why it matters**: Chronic re-churners have progressively worse retention per cycle. A rising share means the "reactivation funnel" is recycling the same low-retention users rather than pulling back genuinely recoverable ones.

### Query: Repeat Reactivator Share

```sql
WITH reactivation_history AS (
  SELECT
    user_id,
    snapshot_date,
    COUNT(*) OVER (PARTITION BY user_id ORDER BY snapshot_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prior_reactivations
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis`
  WHERE v_f_user_rpt.is_daily_reactivated = TRUE
    AND v_f_user_rpt.is_active = TRUE
    AND v_f_user_rpt.f_days_since_first_activity >= 30
    AND product_id = 105
    AND snapshot_date >= '2023-04-01'
)

SELECT
  DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
  COUNT(DISTINCT k.user_id) AS total_reactivations,
  COUNT(DISTINCT CASE WHEN rh.prior_reactivations >= 5 THEN k.user_id END) AS repeat_5plus,
  COUNT(DISTINCT CASE WHEN rh.prior_reactivations >= 5 THEN k.user_id END)
    / COUNT(DISTINCT k.user_id) AS repeat_5plus_share
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
  ON s.user_id = k.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
  ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
LEFT JOIN reactivation_history rh
  ON rh.user_id = k.user_id AND rh.snapshot_date = k.snapshot_date
WHERE k.snapshot_date >= CURRENT_DATE() - 57
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
  AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
  AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
GROUP BY ALL
ORDER BY cohort_week
```

---

## Section I: Retention by Dormancy Bucket

**Chart type**: Grouped bar chart  
**X-axis**: Dormancy bucket  
**Y-axis**: D7 Retention (%)  
**Color**: Current week vs. 4-week average (benchmark)

**Interpretation guide**: Shorter dormancy (0-14d) should have highest retention. If long-dormancy users (180d+) are suddenly retaining better, it may signal a successful campaign targeting deep churners. If short-dormancy retention drops, the re-entry experience may be degraded.

### Query: D7 Retention by Dormancy

```sql
WITH reactivations AS (
  SELECT
    k.user_id,
    k.snapshot_date,
    DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
    CASE WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 7 THEN 'a.0-7d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 14 THEN 'b.8-14d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 30 THEN 'c.15-30d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 60 THEN 'd.31-60d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 90 THEN 'e.61-90d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 180 THEN 'f.91-180d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) > 180 THEN 'g.180d+'
    END AS dormancy_bucket
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
    ON s.user_id = k.user_id
  LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
    ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
  WHERE k.snapshot_date >= CURRENT_DATE() - 43  -- 5 weeks + 8 days for D7 maturity
    AND k.snapshot_date <= CURRENT_DATE() - 8
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
    AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
)

SELECT
  r.cohort_week,
  r.dormancy_bucket,
  COUNT(DISTINCT r.user_id) AS cohort_size,
  COUNT(DISTINCT d7.user_id) / COUNT(DISTINCT r.user_id) AS d7_retention
FROM reactivations r
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d7
  ON d7.user_id = r.user_id
  AND d7.snapshot_date = DATE_ADD(r.snapshot_date, INTERVAL 7 DAY)
  AND d7.v_f_user_rpt.is_active = TRUE
GROUP BY ALL
ORDER BY cohort_week, dormancy_bucket
```

---

## Section J: Retention by LTV Tier

**Chart type**: Grouped bar chart  
**X-axis**: LTV bucket  
**Y-axis**: D7 Retention (%)  
**Color**: Current week vs. 4-week average

### Query: D7 Retention by LTV

```sql
WITH reactivations AS (
  SELECT
    k.user_id,
    k.snapshot_date,
    DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
    CASE WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) = 0 THEN 'a.$0 (NP)'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 20 THEN 'b.$0-20'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 100 THEN 'c.$20-100'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 500 THEN 'd.$100-500'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) > 500 THEN 'e.$500+'
    END AS ltv_bucket
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
    ON s.user_id = k.user_id
  LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
    ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
  WHERE k.snapshot_date >= CURRENT_DATE() - 43
    AND k.snapshot_date <= CURRENT_DATE() - 8
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
    AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
)

SELECT
  r.cohort_week,
  r.ltv_bucket,
  COUNT(DISTINCT r.user_id) AS cohort_size,
  COUNT(DISTINCT d7.user_id) / COUNT(DISTINCT r.user_id) AS d7_retention
FROM reactivations r
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d7
  ON d7.user_id = r.user_id
  AND d7.snapshot_date = DATE_ADD(r.snapshot_date, INTERVAL 7 DAY)
  AND d7.v_f_user_rpt.is_active = TRUE
GROUP BY ALL
ORDER BY cohort_week, ltv_bucket
```

---

## Section K: Platform & Geo Breakdown

**Chart type**: Table (heatmap coloring on D7 retention)  
**Rows**: Platform × Geo Tier  
**Columns**: Volume, D7 Retention, D7 Conversion, WoW Change

### Query: Platform × Geo Performance

```sql
WITH reactivations AS (
  SELECT
    k.user_id,
    k.snapshot_date,
    DATE_TRUNC(k.snapshot_date, WEEK(MONDAY)) AS cohort_week,
    k.v_f_user_rpt.lt_first_platform_name AS platform,
    c.geo_tier
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s
    ON s.user_id = k.user_id
  LEFT JOIN `dwh-prod-core.pub.v_d_publisher` p
    ON k.v_f_user_rpt.lt_first_publisher_name = p.publisher_name
  LEFT JOIN `dwh-prod-core.pub.v_d_country` c
    ON k.v_f_user_rpt.lt_first_country = c.iso2
  WHERE k.snapshot_date >= CURRENT_DATE() - 22  -- 2 weeks + 8 for D7
    AND k.snapshot_date <= CURRENT_DATE() - 8
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
    AND (p.publisher_name IS NULL OR p.publisher_name != 'untrusted devices')
)

SELECT
  r.cohort_week,
  r.platform,
  r.geo_tier,
  COUNT(DISTINCT r.user_id) AS reactivated_users,
  COUNT(DISTINCT d7.user_id) / COUNT(DISTINCT r.user_id) AS d7_retention
FROM reactivations r
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d7
  ON d7.user_id = r.user_id
  AND d7.snapshot_date = DATE_ADD(r.snapshot_date, INTERVAL 7 DAY)
  AND d7.v_f_user_rpt.is_active = TRUE
GROUP BY ALL
ORDER BY cohort_week, platform, geo_tier
```

---

## Interpretation Framework

When reviewing this dashboard weekly, look for these patterns:

| Signal | What it means | Action |
|--------|---------------|--------|
| Volume up + D7 retention flat | Good — growing without diluting quality | Monitor mix for confirmation |
| Volume up + D7 retention down | Mix shift or re-entry experience degrading | Check dormancy/LTV mix panels |
| Repeat-reactivator share rising | CRM recycling same users; diminishing returns | Shift spend to fresh churners |
| Long-dormancy share rising | Campaign targeting deeper churners | Expected if running win-back; check their D7 is acceptable |
| Low-BL share rising | More "never really played" users returning | RTUE may not be enough; consider re-onboarding |
| NP share rising + conversion stable | Healthy — volume growth from non-payers without hurting economics | No action needed |
| iOS D7 diverging from Android | Platform-specific re-entry issue | Check push delivery, RTUE eligibility by platform |

---

## Technical Notes

- **D7 maturity**: Any cohort must be ≥8 days old before D7 can be computed. Dashboard auto-excludes immature cohorts.
- **Suspicious filtering**: Always applied. Section B shows suspicious volume separately for contamination monitoring.
- **Scan estimate**: Each weekly query scans ~200-400 GB given 8-week window on v_f_main_user_kpis. Acceptable for weekly refresh.
- **Album/season context**: Consider adding album annotations to the time series (Section B/C) once dim_album is joined.
