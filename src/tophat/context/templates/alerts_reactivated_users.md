# Alerts: Reactivated Users

15 alerts organized by pillar. Designed to catch meaningful shifts in reactivation health — from volume and quality to re-churn risk.

---

## Pillar 1: Technical Health (Pipeline & Data Integrity)

### Alert 1: Reactivation Volume Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] Daily Reactivation Volume Drop |
| description | Daily reactivated user count dropped significantly — may indicate CRM pipeline failure, push notification issues, or LiveOps calendar gap |
| table_name | v_f_main_user_kpis |
| aggregation_expression | COUNT(DISTINCT user_id) |
| where_condition | v_f_user_rpt.is_daily_reactivated = TRUE AND v_f_user_rpt.is_active = TRUE AND v_f_user_rpt.f_days_since_first_activity >= 30 AND product_id = 105 |
| dimension_1 | v_f_user_rpt.lt_first_platform_name |
| dimension_2 | v_d_country.geo_tier |
| date_filter | snapshot_date |
| frequency | 24 h |
| relative_percentage_threshold | 25- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** Reactivations are 14.2% of WAU. A 25%+ drop signals either a CRM/push delivery failure or that the pull-back triggers (IP seasons, LiveOps events) are missing. Platform × geo split localizes the issue.

---

### Alert 2: Reactivation Volume Spike (Suspicious)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] Suspicious Reactivation Spike |
| description | Reactivation volume spiked abnormally — could be bot wave or false reactivations from attribution issues |
| table_name | v_f_main_user_kpis |
| aggregation_expression | COUNT(DISTINCT user_id) |
| where_condition | v_f_user_rpt.is_daily_reactivated = TRUE AND v_f_user_rpt.is_active = TRUE AND v_f_user_rpt.f_days_since_first_activity >= 30 AND product_id = 105 |
| date_filter | snapshot_date |
| frequency | 24 h |
| relative_percentage_threshold | 50+ |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** Unexpected spikes can indicate fraudulent reactivation campaigns, attribution bugs, or dormant-account hijacking. Distinguish from legitimate IP-driven spikes (season launches) by checking events calendar.

---

### Alert 3: Duplicate Accounts Share (Multi-Device)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] Multi-Device User Share Spike |
| description | % of reactivated users with >1 device_id in sys_app_open is above normal — likely duplicate/alt accounts inflating reactivation counts |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 20+ |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
WITH reactivated_today AS (
  SELECT DISTINCT k.user_id
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  WHERE k.snapshot_date = CURRENT_DATE() - 1
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
),
device_counts AS (
  SELECT ao.user_id,
    COUNT(DISTINCT ao.device_id) AS n_devices
  FROM `dwh-prod-tophat.STD_tophat.sys_app_open` ao
  INNER JOIN reactivated_today r ON ao.user_id = r.user_id
  WHERE DATE(ao.collector_time) BETWEEN CURRENT_DATE() - 30 AND CURRENT_DATE() - 1
  GROUP BY ao.user_id
)
SELECT
  CURRENT_DATE() - 1 AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN dc.n_devices > 1 THEN dc.user_id END),
    COUNT(DISTINCT dc.user_id)
  ) AS aggregation_result
FROM device_counts dc
```

**Why it matters:** Users with multiple device_ids are likely duplicate/alt accounts gaming rewards or recovery flows. They inflate reactivation volume without representing genuine re-engagement and contaminate retention metrics.

---

## Pillar 2: Behavioral / Engagement

### Alert 4: D1 Retention Decline (Reactivated)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D1 Retention Drop |
| description | D1 retention for reactivated users dropped — first-day stickiness failing, likely re-entry experience issue |
| custom_query | See below |
| dimension_1 | lt_first_platform_name |
| dimension_2 | geo_tier |
| frequency | 24 h |
| relative_percentage_threshold | 15- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  d0.snapshot_date AS validation_date,
  d0.v_f_user_rpt.lt_first_platform_name AS dimension_1_result,
  d0.v_d_country.geo_tier AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT d1.user_id),
    COUNT(DISTINCT d0.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d0
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d1
  ON d0.user_id = d1.user_id
  AND d1.snapshot_date = d0.snapshot_date + 1
  AND d1.v_f_user_rpt.is_active = TRUE
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s ON s.user_id = d0.user_id
WHERE d0.snapshot_date = CURRENT_DATE() - 2
  AND d0.v_f_user_rpt.is_daily_reactivated = TRUE
  AND d0.v_f_user_rpt.is_active = TRUE
  AND d0.v_f_user_rpt.f_days_since_first_activity >= 30
  AND d0.product_id = 105
  AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
GROUP BY d0.snapshot_date, d0.v_f_user_rpt.lt_first_platform_name, d0.v_d_country.geo_tier
```

**Why it matters:** Reactivated D1 baseline is ~30-37% (with RTUE). A 15%+ relative drop = users came back but found nothing compelling enough to return the next day.

---

### Alert 5: D7 Retention Decline (Reactivated)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D7 Retention Drop |
| description | D7 retention for reactivated users dropped — users not sticking past first week, re-churn risk elevated |
| custom_query | Same structure as Alert 4, join at INTERVAL 7 DAY, snapshot = CURRENT_DATE() - 8 |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** D7 retention separates "curiosity reactivations" from real re-engagement. This is where Rich Returns and RTUE sustain users. A drop means re-entry hooks are failing.

---

### Alert 6: Session Duration Drop (Reactivation D0-D3)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D0-D3 Session Duration Drop |
| description | Average session duration for recently reactivated users dropped — weaker engagement per session |
| table_name | v_f_main_user_kpis |
| aggregation_expression | AVG(v_f_user_rpt.f_session_duration) |
| where_condition | v_f_user_rpt.f_days_since_last_reactivation BETWEEN 0 AND 3 AND v_f_user_rpt.is_active = TRUE AND v_f_user_rpt.f_days_since_first_activity >= 30 AND product_id = 105 |
| date_filter | snapshot_date |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** RTUE variant lifted D1 playtime to 27.7 min. If session durations shrink, users are opening the game but not finding reasons to stay — content or economy isn't holding them.

---

### Alert 7: D0 Rolls Spent Drop (Reactivated)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D0 Rolls Spent Drop |
| description | Average rolls spent on reactivation day dropped — users returning but not engaging with core loop |
| table_name | v_f_main_user_kpis |
| aggregation_expression | AVG(dim_user_snapshot.f_rolls_spent) |
| where_condition | v_f_user_rpt.is_daily_reactivated = TRUE AND v_f_user_rpt.is_active = TRUE AND v_f_user_rpt.f_days_since_first_activity >= 30 AND product_id = 105 |
| date_filter | snapshot_date |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** If reactivated users aren't spending rolls, they opened the game but didn't play. Symptom of low roll balance on return, overwhelming pop-ups, or content that doesn't immediately engage.

---

## Pillar 3: Economy & Monetization

### Alert 8: D7 Conversion Rate Drop (Reactivated)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D7 Conversion Rate Drop |
| description | D7 conversion rate for reactivated users dropped — monetization opportunity declining in early re-engagement window |
| custom_query | See below |
| dimension_1 | lt_first_platform_name |
| frequency | 24 h |
| relative_percentage_threshold | 30- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  d0.snapshot_date AS validation_date,
  d0.v_f_user_rpt.lt_first_platform_name AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN d7.v_f_user_rpt.is_customer = TRUE AND d0.v_f_user_rpt.is_customer = FALSE THEN d7.user_id END),
    COUNT(DISTINCT d0.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d0
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d7
  ON d0.user_id = d7.user_id
  AND d7.snapshot_date = d0.snapshot_date + 7
WHERE d0.snapshot_date = CURRENT_DATE() - 8
  AND d0.v_f_user_rpt.is_daily_reactivated = TRUE
  AND d0.v_f_user_rpt.is_active = TRUE
  AND d0.v_f_user_rpt.f_days_since_first_activity >= 30
  AND d0.product_id = 105
GROUP BY d0.snapshot_date, d0.v_f_user_rpt.lt_first_platform_name
```

**Why it matters:** Reactivated LTV 250+ users showed +141% app open rate with generous rewards. If D7 conversion drops, offers/economy for returning users aren't matching expectations or welcome-back rewards aren't creating purchase urgency.

---

### Alert 9: D0 ARPDAU Drop (Reactivated Payers)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D0 ARPDAU Drop (Existing Payers) |
| description | Revenue per active reactivated user on return day dropped — existing payers not spending on return |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 25- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    SUM(k.v_f_user_rpt.f_iap_revenue),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.v_f_user_rpt.is_customer = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date
```

**Why it matters:** Existing payers returning is the highest-value reactivation event. If their D0 spend drops, either the welcome-back offers are wrong, the game state they return to is discouraging, or payment flow has issues.

---

## Pillar 4: Reactivation Quality / Mix Shift (Consolidated)

### Alert 10: Reactivation Mix — Consolidated Dimension Tracker
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] Mix Shift — Multi-Dimension |
| description | Tracks share distribution across all key reactivation dimensions daily. Alerts if any single dimension's distribution shifts beyond threshold. |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
WITH reactivated AS (
  SELECT
    k.snapshot_date,
    k.user_id,
    -- Platform
    k.v_f_user_rpt.lt_first_platform_name AS platform,
    -- Geo Tier
    k.v_d_country.geo_tier,
    -- Customer status
    CASE WHEN k.v_f_user_rpt.is_customer = TRUE THEN 'customer' ELSE 'non_customer' END AS customer_status,
    -- Board Level Bucket
    CASE WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 5 THEN 'BL1-5'
         WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 10 THEN 'BL6-10'
         WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 20 THEN 'BL11-20'
         WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) <= 50 THEN 'BL21-50'
         WHEN COALESCE(k.dim_user_snapshot.last_board_level, 0) > 50 THEN 'BL50+'
    END AS board_level_bucket,
    -- Days Since Previous Activity Bucket
    CASE WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 14 THEN 'dorm_0-14d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 30 THEN 'dorm_15-30d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 60 THEN 'dorm_31-60d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 90 THEN 'dorm_61-90d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) <= 180 THEN 'dorm_91-180d'
         WHEN COALESCE(k.v_f_user_rpt.f_days_since_prev_activity, 0) > 180 THEN 'dorm_180d+'
    END AS dormancy_bucket,
    -- Lifetime Active Days Bucket
    CASE WHEN COALESCE(k.v_f_user_rpt.f_lt_active_days, 0) <= 5 THEN 'lt_act_0-5'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_active_days, 0) <= 20 THEN 'lt_act_6-20'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_active_days, 0) <= 50 THEN 'lt_act_21-50'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_active_days, 0) <= 100 THEN 'lt_act_51-100'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_active_days, 0) > 100 THEN 'lt_act_100+'
    END AS lt_active_days_bucket,
    -- Lifetime IAP Revenue Bucket
    CASE WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) = 0 THEN 'ltv_0_NP'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 20 THEN 'ltv_0-20'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 100 THEN 'ltv_20-100'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) <= 500 THEN 'ltv_100-500'
         WHEN COALESCE(k.v_f_user_rpt.f_lt_iap_revenue, 0) > 500 THEN 'ltv_500+'
    END AS lt_revenue_bucket,
    -- Friends Bucket
    CASE WHEN COALESCE(k.dim_user_snapshot.n_friends, 0) = 0 THEN 'friends_0'
         WHEN COALESCE(k.dim_user_snapshot.n_friends, 0) <= 5 THEN 'friends_1-5'
         WHEN COALESCE(k.dim_user_snapshot.n_friends, 0) <= 20 THEN 'friends_6-20'
         WHEN COALESCE(k.dim_user_snapshot.n_friends, 0) > 20 THEN 'friends_20+'
    END AS friends_bucket
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s ON s.user_id = k.user_id
  WHERE k.snapshot_date = CURRENT_DATE() - 1
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
)
-- Output one row per dimension × bucket for alerting system to evaluate share shifts
SELECT snapshot_date AS validation_date, 'board_level' AS dimension_1_result, board_level_bucket AS dimension_2_result,
  SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) AS aggregation_result FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'dormancy', dormancy_bucket, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'lt_active_days', lt_active_days_bucket, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'lt_revenue', lt_revenue_bucket, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'customer_status', customer_status, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'platform', platform, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'geo_tier', geo_tier, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
UNION ALL
SELECT snapshot_date, 'friends', friends_bucket, SAFE_DIVIDE(COUNT(*), SUM(COUNT(*)) OVER()) FROM reactivated GROUP BY ALL
```

**Why it matters:** Reactivation quality depends on mix. This single alert monitors board_level, dormancy duration, lifetime active days, LTV, customer status, platform, geo_tier, and social (friends) distribution simultaneously. A shift in any dimension changes expected D7 retention and ARPI — catching it early lets the team investigate whether CRM targeting changed, a campaign skewed the pool, or the dormant audience is depleting in high-value segments.

**Dimensions tracked:**
- Board level (BL1-5 users never experienced hook features; 24% are BL1)
- Days since previous activity (KPIs optimal within 28 days; 180d+ are essentially re-onboarding)
- Lifetime active days (≤5 days = never really played the game)
- Lifetime IAP revenue / LTV tier (LTV 250+ respond 141% better to offers)
- Customer status (non-payers have fundamentally different re-engagement ceiling)
- Platform (iOS vs Android retention profiles differ ~1.7x)
- Geo tier (acquisition cost and LTV vary dramatically by tier)
- Friends count (Social Score inversely correlates with churn)

---

### Alert 11: Repeat Reactivators Share Spike
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] Repeat Reactivators (5+) Share Spike |
| description | % of reactivations from users with 5+ prior reactivations is above normal — chronic re-churners diluting quality |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 20+ |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
WITH reactivation_counts AS (
  SELECT user_id, snapshot_date,
    COUNT(*) OVER (PARTITION BY user_id ORDER BY snapshot_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS n_reactivations_to_date
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis`
  WHERE v_f_user_rpt.is_daily_reactivated = TRUE
    AND snapshot_date >= DATE('2023-04-01')
    AND product_id = 105
)
SELECT
  k.snapshot_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN rc.n_reactivations_to_date >= 6 THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN reactivation_counts rc ON k.user_id = rc.user_id AND k.snapshot_date = rc.snapshot_date
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
GROUP BY k.snapshot_date
```

**Why it matters:** Chronic re-churners (5+ prior reactivations) have progressively worse retention per cycle. If they dominate the mix, blended retention drops even if product quality is constant. Tracked separately because reactivation_count is a behavioral signal distinct from the mix dimensions above.

---

## Pillar 5: Feature & Content (Re-entry Experience)

### Alert 12: First Minigame Enrollment Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] First Available Minigame Enrollment Drop |
| description | % of reactivated users enrolling in the first available solo minigame after return dropped — key re-engagement hook not landing |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
WITH reactivated AS (
  SELECT k.user_id, k.snapshot_date AS reactivation_date
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s ON s.user_id = k.user_id
  WHERE k.snapshot_date BETWEEN CURRENT_DATE() - 4 AND CURRENT_DATE() - 1
    AND k.v_f_user_rpt.is_daily_reactivated = TRUE
    AND k.v_f_user_rpt.is_active = TRUE
    AND k.v_f_user_rpt.f_days_since_first_activity >= 30
    AND k.product_id = 105
    AND (s.is_ever_suspicious_at_creation IS NULL OR s.is_ever_suspicious_at_creation = FALSE)
),
first_minigame AS (
  SELECT r.user_id, r.reactivation_date,
    MIN(lo.collector_time) AS first_mg_time
  FROM reactivated r
  INNER JOIN `dwh-prod-tophat.STD_tophat.game_liveops` lo
    ON r.user_id = lo.user_id
    AND DATE(lo.collector_time) BETWEEN r.reactivation_date AND r.reactivation_date + 3
    AND lo.action_type = 'enroll'
    AND lo.liveops_type IN ('minigame_dig', 'prize_drop', 'boutique', 'carnival_games', 'adventure')
  GROUP BY r.user_id, r.reactivation_date
)
SELECT
  r.reactivation_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT fm.user_id),
    COUNT(DISTINCT r.user_id)
  ) AS aggregation_result
FROM reactivated r
LEFT JOIN first_minigame fm ON r.user_id = fm.user_id AND r.reactivation_date = fm.reactivation_date
GROUP BY r.reactivation_date
```

**Why it matters:** Minigames are the primary content hook for reactivated users (RTUE Dig lifted D1 retention +19.3%). If users aren't enrolling in the first available minigame, either the LiveOps calendar has a gap, the minigame isn't surfaced properly, or users are churning before it becomes available.

---

### Alert 13: Season-Start Reactivation Lift Missing
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] Season Start Volume Lift Below Expected |
| description | Reactivation volume did not lift on season start day as expected — IP/season launch not pulling users back |
| custom_query | See below |
| frequency | 24 h |
| absolute_lower_threshold | 1.10 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
WITH season_starts AS (
  SELECT event_start_date
  FROM `dwh-prod-tophat.pub.v_d_monopoly_go_events_calendar`
  WHERE event_type = 'season_start' AND event_start_date = CURRENT_DATE() - 1
),
baseline AS (
  SELECT AVG(cnt) AS avg_volume
  FROM (
    SELECT COUNT(DISTINCT user_id) AS cnt
    FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis`
    WHERE v_f_user_rpt.is_daily_reactivated = TRUE
      AND v_f_user_rpt.is_active = TRUE
      AND v_f_user_rpt.f_days_since_first_activity >= 30
      AND product_id = 105
      AND snapshot_date BETWEEN CURRENT_DATE() - 15 AND CURRENT_DATE() - 2
    GROUP BY snapshot_date
  )
)
SELECT
  ss.event_start_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    (SELECT COUNT(DISTINCT user_id) FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis`
     WHERE snapshot_date = ss.event_start_date
       AND v_f_user_rpt.is_daily_reactivated = TRUE AND v_f_user_rpt.is_active = TRUE
       AND v_f_user_rpt.f_days_since_first_activity >= 30 AND product_id = 105),
    b.avg_volume
  ) AS aggregation_result
FROM season_starts ss, baseline b
```

**Why it matters:** Season starts (especially IP-driven like Harry Potter) are the strongest organic reactivation triggers. If volume doesn't lift 10%+, either the IP isn't resonating, push notifications aren't deploying, or the dormant audience is exhausted.

---

### Alert 14: RTUE Completion Rate Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] RTUE Minigame Completion Rate Drop |
| description | Completion rate of RTUE Dig minigame for reactivated users dropped — difficulty or reward tuning may be off |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  DATE(lo.collector_time) AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN lo.is_completed = TRUE THEN lo.user_id END),
    COUNT(DISTINCT CASE WHEN lo.action_type = 'enroll' THEN lo.user_id END)
  ) AS aggregation_result
FROM `dwh-prod-tophat.STD_tophat.game_liveops` lo
INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  ON lo.user_id = k.user_id AND k.snapshot_date = DATE(lo.collector_time)
WHERE DATE(lo.collector_time) BETWEEN CURRENT_DATE() - 4 AND CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.dim_user_snapshot.is_rtue_active = TRUE
  AND k.product_id = 105
  AND LOWER(lo.liveops_type) LIKE '%rtue%'
GROUP BY DATE(lo.collector_time)
```

**Why it matters:** RTUE completion rates are 5x higher than regular Dig events (~35.8% D1, driven by easier configs). If completion drops, difficulty configs may have changed or rewards aren't motivating — directly undermining the +19.3% D1 retention lift.

---

### Alert 15: Pop-up Fatigue — Offer Impressions Spike on D0
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - Reactivations] D0 Offer Impressions Spike |
| description | Number of offer impressions shown to reactivated users on D0 spiked — pop-up fatigue may be driving immediate re-churn |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 30+ |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  f.snapshot_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    SUM(f.offer_impressions),
    COUNT(DISTINCT f.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.fac_revenue_funnel` f
INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  ON f.user_id = k.user_id AND f.snapshot_date = k.snapshot_date
WHERE f.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.is_daily_reactivated = TRUE
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.f_days_since_first_activity >= 30
  AND k.product_id = 105
GROUP BY f.snapshot_date
```

**Why it matters:** Pop-up fatigue and sequencing is a known open question. Reactivated users returning to a barrage of offers may close the app immediately. A spike in offer impressions per user on D0 suggests the offer suppression logic for returning users isn't working properly.
