# Template: FTUE Minigame AB Test (Hex)

Source: Hex project "FTUE Minigame AB Test" (019ce116)

## Purpose
Analyze the FTUE Solo Minigame AB test: user assignment, board progression, retention, engagement, and event-level performance.

## Key Tables Discovered

- `dwh-prod-tophat.BIZ.ab_test_mapping` — AB test variant assignments (test_name, variant_name, user_assignment_date, test_start_date)
- `dwh-prod-tophat.DM.dim_board` — Board progression (user_id, board_level, start_time, end_time)
- `dwh-prod-tophat.BIZ.fac_daily_actionable_cheaters` — Actionable cheater flag (is_actionable_cheater_lt)
- `dwh-prod-tophat.STD_tophat.ban` — Ban events (ban_type, ban_action, collector_date)

## Population Filtering (AB Test)
```sql
-- Full exclusion pattern for AB tests:
WHERE is_untrusted_device IS FALSE
  AND is_ever_suspicious_at_creation IS FALSE
  AND is_banned IS FALSE
  AND is_actionable_cheater_lt IS FALSE
```

## AB Test User Assignment Pattern
```sql
SELECT t.user_id, variant_name, user_assignment_date AS test_enter_date
FROM `dwh-prod-tophat.BIZ.ab_test_mapping` t
WHERE test_name = '<TEST_NAME>'
  AND test_start_date BETWEEN '<START>' AND '<END>'
```

## Board Progression Pattern
```sql
WITH base AS (
  SELECT u.user_id, variant_name, board_level, start_time
  FROM users u
  JOIN `dwh-prod-tophat.DM.dim_board` b ON u.user_id = b.user_id
  WHERE b.board_level BETWEEN 4 AND 6
),
progression AS (
  SELECT b.*, nb.board_level AS next_board_level, nb.start_time AS next_board_start
  FROM base b
  LEFT JOIN `dwh-prod-tophat.DM.dim_board` nb
    ON b.user_id = nb.user_id AND nb.board_level = b.board_level + 1
)
SELECT variant_name, board_level,
  COUNT(DISTINCT user_id) AS users_started,
  SUM(IF(next_board_start <= TIMESTAMP_ADD(start_time, INTERVAL 1 DAY), 1, 0)) AS progressed_d1,
  SUM(IF(next_board_start <= TIMESTAMP_ADD(start_time, INTERVAL 3 DAY), 1, 0)) AS progressed_d3,
  SUM(IF(next_board_start <= TIMESTAMP_ADD(start_time, INTERVAL 7 DAY), 1, 0)) AS progressed_d7
FROM progression GROUP BY ALL
```

## Retention & Engagement Pattern (from anchor date)
```sql
-- "Baked" pattern: only count users whose anchor date is old enough for the window
DATE_DIFF(CURRENT_DATE() - 1, anchor_date, DAY) >= X AS dX_baked

-- Retention:
MAX(CASE WHEN snapshot_date = anchor_date + X AND v_f_user_rpt.is_active THEN 1 ELSE 0 END) AS dX_retention

-- Playtime/Sessions/Revenue (cumulative from anchor):
SUM(IF(snapshot_date BETWEEN anchor_date AND anchor_date + X, v_f_user_rpt.f_session_duration, 0)) AS dX_playtime
SUM(IF(snapshot_date BETWEEN anchor_date AND anchor_date + X, v_f_user_rpt.f_sessions, 0)) AS dX_sessions
MAX(IF(snapshot_date BETWEEN anchor_date AND anchor_date + X AND v_f_user_rpt.f_iap_revenue > 0, 1, 0)) AS dX_converted
SUM(IF(snapshot_date BETWEEN anchor_date AND anchor_date + X, v_f_user_rpt.f_iap_revenue, 0)) AS dX_revenue
```

## Statistical Testing (Python — proportions z-test)
```python
from statsmodels.stats.proportion import proportions_ztest

count = [variant_retained, control_retained]
nobs = [variant_baked, control_baked]
stat, pval = proportions_ztest(count, nobs)

# Significance labels:
"Yes (p < 0.001)" if pval < 0.001
"Yes (p < 0.01)" if pval < 0.01
"Yes (p < 0.05)" if pval < 0.05
"No (p > 0.05)"
```

## LiveOps Config Classification
```sql
CASE 
  WHEN (variant LIKE 'Control%' AND liveops_config IN ('LiveOps_Minigame + LiveOps_MLS','NO_Minigame + LiveOps_MLS'))
    OR (variant LIKE 'Variant%' AND liveops_config = 'FTUE_Minigame + FTUE_MLS') 
  THEN 'Valid Config' ELSE 'Bad Config'
END AS config_type
```

## Computed Metrics
- `d1_progression` = SUM(progressed_d1) / SUM(users_started)
- `d1_retention` = SUM(d1_retained) / SUM(d1_baked)
- `d1_conversion` = SUM(d1_converted) / SUM(d1_baked)
- `d1_playtime` = SUM(d1_playtime_baked) / SUM(d1_baked) / 60 (minutes)
- `d1_arpu` = SUM(d1_revenue_baked) / SUM(d1_baked)
