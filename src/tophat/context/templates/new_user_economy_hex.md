# Template: New User Economy Analysis (Hex)

Source: Hex project "users economy on install analysis" (019cccb3)

## Purpose
Analyze how the in-game economy affects new user (D0-D6) retention: session end reasons, economy state at churn, OOR/OOC frequency, first economy wall timing, RTP impact, and platform differences.

## Population Definition
- New users (D0-D6 tenure), `v_d_rpt_tenure.tenure_segment = 'D0-D6'`
- Installed between 54 and 14 days ago
- **Excluded:** users with 0 or NULL `f_rolls_spent` on D0 (never engaged with core loop)
- Retention metric: active on exactly day 14 after first activity

## Key Query Patterns

### New User Base (reusable CTE)
```sql
WITH new_user_base AS (
  SELECT r.user_id,
    MIN(r.snapshot_date) AS first_activity_date,
    MAX(CASE WHEN r.v_f_user_rpt.f_lt_iap_revenue > 0 THEN 'Paying' ELSE 'Non-Paying' END) AS is_paying
  FROM `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` r
  WHERE r.snapshot_date >= CURRENT_DATE - 54
    AND r.product_id = 105
    AND r.v_f_user_rpt.is_active = TRUE
    AND r.v_d_rpt_tenure.tenure_segment = 'D0-D6'
    AND DATE(r.v_f_user_rpt.lt_first_install_time) BETWEEN CURRENT_DATE - 54 AND CURRENT_DATE - 14
    AND r.user_id NOT IN (
      SELECT DISTINCT u0.user_id
      FROM `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` u0
      WHERE u0.v_f_user_rpt.f_days_since_first_activity = 0
        AND u0.product_id = 105
        AND u0.snapshot_date >= CURRENT_DATE - 54
        AND (u0.dim_user_snapshot.f_rolls_spent IS NULL OR u0.dim_user_snapshot.f_rolls_spent = 0)
    )
  GROUP BY r.user_id
)
```

### Session End Reason Classification
```sql
-- OOR/OOC detected by sys_ui popup within 3 min of session end
MAX(CASE WHEN ui.screen_name = 'offers_out_of_rolls_popup' THEN 1 ELSE 0 END) = 1 AS has_oor,
MAX(CASE WHEN ui.screen_name = 'offers_out_of_money_popup' THEN 1 ELSE 0 END) = 1 AS has_ooc

-- Classification:
CASE
  WHEN has_oor AND has_ooc THEN 'Both OOR & OOC'
  WHEN has_oor THEN 'Out of Rolls (OOR)'
  WHEN has_ooc THEN 'Out of Cash (OOC)'
  ELSE 'Other'
END AS session_end_reason
```

### OOR/OOC Popup Detection
```sql
FROM `dwh-prod-tophat.STD_tophat.sys_ui_nodedup` ui
WHERE ui.interaction_type = 'load'
  AND ui.interaction_object_category = 'display'
  AND ui.screen_name IN ('offers_out_of_rolls_popup', 'offers_out_of_money_popup')
  AND ui.product_id = 105
  AND ui.collector_time BETWEEN TIMESTAMP_SUB(s.session_end_time, INTERVAL 3 MINUTE) AND s.session_end_time
```

### Board Level from GTI (BoardWelcomeReward)
```sql
-- Get user's board level at a point in time
SELECT user_id, CAST(reference_subtype_2 AS INT64) AS board_level, collector_time
FROM `dwh-prod-tophat.STD_tophat.sys_gti_nodedup`
WHERE item_id = 'rolls' AND transaction_subtype = 'BoardWelcomeReward' AND product_id = 105
```

### RTP Calculation
```sql
SAFE_DIVIDE(r.dim_user_snapshot.f_rolls, r.dim_user_snapshot.f_rolls_spent) AS rtp
-- Or from daily aggregates:
SAFE_DIVIDE(SUM(v_f_user_rpt.f_hc_source), SUM(v_f_user_rpt.f_hc_sink)) AS rtp
```

### D14 Retention Join Pattern
```sql
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` r14
  ON ud.user_id = r14.user_id
  AND r14.snapshot_date = ud.first_activity_date + 14
  AND r14.product_id = 105
-- Then: IF(r14.v_f_user_rpt.is_active = TRUE, 1, 0) AS retained_d14
```

### RTP Curve (Running totals from GTI)
```sql
-- Running cumulative source/sink from sys_gti_nodedup
SUM(CASE WHEN item_quantity > 0 AND transaction_category = 'gameplay' THEN item_quantity ELSE 0 END)
  OVER (PARTITION BY user_id, dsfa ORDER BY collector_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS current_sources,
SUM(CASE WHEN item_quantity < 0 THEN ABS(item_quantity) ELSE 0 END)
  OVER (PARTITION BY user_id, dsfa ORDER BY collector_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS current_sinks
```

## Sessions Table
```sql
FROM `dwh-prod-core.pub.v_f_session_daily` s
WHERE s.product_id = 105 AND s.f_session_duration_secs >= 60
```

## Cheater Exclusion Pattern
```sql
LEFT JOIN (
  SELECT DISTINCT user_id FROM `dwh-prod-security.cheating_analytics.analyzed_users`
  WHERE product_id = 105 AND is_cheater AND method_used NOT IN ('strict_rules_query')
) cheaters ON ...
WHERE cheaters.user_id IS NULL
```

## Additional Tables Discovered
- `dwh-prod-core.pub.v_f_session_daily` — Session-level data (start/end time, duration)
- `dwh-prod-tophat.STD_tophat.sys_ui_nodedup` — Deduplicated UI events (popup detection)
- `dwh-prod-tophat.BIZ.dim_user_cheater` — Cheater flag dimension
- `dwh-prod-security.cheating_analytics.analyzed_users` — Cheater detection results
- `dwh-prod-tophat-exp.zz_yanir_ashkenazi.maps_source_classifier` — Economy source classifier (maps reference_subtype + transaction_subtype to vertical/feature/context)

## Standard Roll Spent Buckets (New Users)
```sql
CASE
  WHEN f_rolls_spent IS NULL THEN 'NULL'
  WHEN f_rolls_spent = 0 THEN '0'
  WHEN f_rolls_spent < 10 THEN '1-10'
  WHEN f_rolls_spent < 25 THEN '10-25'
  WHEN f_rolls_spent < 50 THEN '25-50'
  WHEN f_rolls_spent < 100 THEN '50-100'
  WHEN f_rolls_spent < 250 THEN '100-250'
  WHEN f_rolls_spent < 500 THEN '250-500'
  WHEN f_rolls_spent < 1000 THEN '500-1K'
  ELSE '1K+'
END AS rolls_spent_bucket
```

## RTP Buckets
```sql
CASE
  WHEN rtp < 0.25 THEN '<25%'
  WHEN rtp < 0.5 THEN '25-50%'
  WHEN rtp < 0.75 THEN '50-75%'
  WHEN rtp < 1.0 THEN '75-100%'
  WHEN rtp < 1.25 THEN '100-125%'
  WHEN rtp < 1.5 THEN '125-150%'
  ELSE '150%+'
END AS rtp_bucket
```
