# Alerts: New Users

15 alerts organized by pillar. Designed to catch meaningful shifts in new user health before they compound into retention/revenue problems.

---

## Pillar 1: Technical Health (Pipeline & Data Integrity)

### Alert 1: New User Volume Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] Daily Install Volume Drop |
| description | Daily new user count dropped significantly vs trailing average — may indicate acquisition issue, store listing problem, or attribution failure |
| table_name | v_f_main_user_kpis |
| aggregation_expression | COUNT(DISTINCT user_id) |
| where_condition | v_f_user_rpt.f_days_since_first_activity = 0 AND v_f_user_rpt.is_active = TRUE AND product_id = 105 |
| dimension_1 | v_f_user_rpt.lt_first_platform_name |
| dimension_2 | v_d_country.geo_tier |
| date_filter | snapshot_date |
| frequency | 24 h |
| relative_percentage_threshold | 25- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** A sudden volume drop signals broken UA campaigns, store issues, or attribution pipeline failures. Platform × geo split catches localized problems (e.g., Android-only drop in T1 Asia).

---

### Alert 2: Paid vs Organic Mix Shift
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] Paid Share Drop |
| description | Share of paid-acquired new users dropped — either UA spend cut or attribution broke; impacts blended retention/ARPI forecasts |
| custom_query | See below |
| dimension_1 | lt_first_channel_type |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  k.v_f_user_rpt.lt_first_channel_type AS dimension_1_result,
  'all' AS dimension_2_result,
  COUNT(DISTINCT k.user_id) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date, k.v_f_user_rpt.lt_first_channel_type
```

**Why it matters:** Paid and organic users have different retention/monetization profiles. If paid share drops without a corresponding organic lift, total volume is falling and mix-adjusted KPIs shift unpredictably.

---

### Alert 3: FTUE Start % Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] FTUE Start Rate Drop |
| description | % of D0 users who start the tutorial dropped — app opens not converting to game engagement, likely a client/loading issue |
| custom_query | See below |
| dimension_1 | platform_name |
| frequency | 24 h |
| relative_percentage_threshold | 15- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  DATE(f.collector_time) AS validation_date,
  f.platform_name AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN f.step_order = 1 THEN f.user_id END),
    COUNT(DISTINCT ao.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.STD_tophat.sys_app_open` ao
LEFT JOIN `dwh-prod-tophat.STD_tophat.sys_fte_flow` f
  ON ao.user_id = f.user_id AND DATE(f.collector_time) = DATE(ao.collector_time)
INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  ON ao.user_id = k.user_id AND k.snapshot_date = DATE(ao.collector_time)
WHERE DATE(ao.collector_time) = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY DATE(f.collector_time), f.platform_name
```

**Why it matters:** If users open the app but never start FTUE, there's a pre-tutorial gate failure — loading screen hang, authentication crash, or splash screen drop-off. The 11% auth-step drop is already known; this catches further degradation.

---

### Alert 4: Suspicious New User Spike
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] Suspicious User % Spike |
| description | % of new users flagged as suspicious/untrusted is above normal levels — potential bot wave or fraud |
| custom_query | See below |
| frequency | 24 h |
| absolute_upper_threshold | 0.15 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN s.is_ever_suspicious_at_creation OR pub.publisher_name = 'untrusted devices' THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` s ON s.user_id = k.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` pub ON k.v_f_user_rpt.lt_first_publisher_name = pub.publisher_name
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date
```

**Why it matters:** Bot waves inflate new user counts while diluting retention metrics. Early detection prevents wasted resources and corrupted analysis.

---

## Pillar 2: Behavioral / Engagement

### Alert 5: D1 Retention Decline
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] D1 Retention Rate Drop |
| description | D1 retention rate for new user cohort dropped — fundamental signal of onboarding health |
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
WHERE d0.snapshot_date = CURRENT_DATE() - 2
  AND d0.v_f_user_rpt.f_days_since_first_activity = 0
  AND d0.v_f_user_rpt.is_active = TRUE
  AND d0.product_id = 105
GROUP BY d0.snapshot_date, d0.v_f_user_rpt.lt_first_platform_name, d0.v_d_country.geo_tier
```

**Why it matters:** D1 retention is the leading indicator of new user experience quality. A 15%+ relative drop signals a systemic onboarding problem (economy, bugs, pop-up fatigue). Platform × geo split localizes the issue.

---

### Alert 6: D7 Retention Decline
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] D7 Retention Rate Drop |
| description | D7 retention dropped — indicates mid-term onboarding failure, typically economy or feature unlock pacing issues |
| custom_query | Same pattern as Alert 5, with d7 join at INTERVAL 7 DAY, snapshot = CURRENT_DATE() - 8 |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** D7 captures whether users survived the initial economy walls (OOR/OOC at Board 1-2). It's where feature unlocks should be hooking players.

---

### Alert 7: D0 Rolls Spent Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] D0 Rolls Spent Drop |
| description | Average rolls spent on D0 dropped — new users not engaging with core loop sufficiently |
| table_name | v_f_main_user_kpis |
| aggregation_expression | AVG(dim_user_snapshot.f_rolls_spent) |
| where_condition | v_f_user_rpt.f_days_since_first_activity = 0 AND v_f_user_rpt.is_active = TRUE AND product_id = 105 |
| dimension_1 | v_f_user_rpt.lt_first_platform_name |
| date_filter | snapshot_date |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** Rolls spent is a proxy for "did the user actually play the core loop?" A drop means users are bouncing before engaging — possibly stuck in FTUE, overwhelmed by pop-ups, or hitting OOR too early.

---

### Alert 8: Out-of-Rolls Rate Spike (D0)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] OOR Popup Rate Spike on D0 |
| description | % of D0 sessions hitting the Out-of-Rolls popup is above normal — economy too tight for new users |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 25+ |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  DATE(ui.collector_time) AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN ui.screen_name = 'offers_out_of_rolls_popup' THEN ui.user_id END),
    COUNT(DISTINCT ui.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.STD_tophat.sys_ui_nodedup` ui
INNER JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
  ON ui.user_id = k.user_id AND k.snapshot_date = DATE(ui.collector_time)
WHERE DATE(ui.collector_time) = CURRENT_DATE() - 1
  AND ui.interaction_type = 'load'
  AND ui.product_id = 105
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.product_id = 105
GROUP BY DATE(ui.collector_time)
```

**Why it matters:** OOR is the #1 session end reason for new users (20-29% of sessions). A spike means economy generosity was reduced (intentionally or by bug) and will directly suppress D1 retention.

---

### Alert 9: Board 2 Reach Rate Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] Board 2 Reach % Drop (by D3) |
| description | % of new users reaching Board 2 by D3 dropped — users stuck in early game, not reaching hook features |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 15- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  k.v_f_user_rpt.lt_first_platform_name AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN k.dim_user_snapshot.last_board_level >= 2 THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 3
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date, k.v_f_user_rpt.lt_first_platform_name
```

**Why it matters:** Board 2 unlocks Community Chest, Albums, Offers, and Flash Events — the features that create habit loops. 86% of D0 users are still on Boards 1-2; if Board 2 reach declines, fewer users ever experience the game's retention drivers.

---

## Pillar 3: Economy & Monetization

### Alert 10: D0 Conversion Rate by Platform
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] D0 Payer Conversion Drop |
| description | D0 conversion rate (paying users / DAU) dropped by platform — earliest monetization signal |
| custom_query | See below |
| dimension_1 | lt_first_platform_name |
| frequency | 24 h |
| relative_percentage_threshold | 25- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  k.v_f_user_rpt.lt_first_platform_name AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN k.v_f_user_rpt.f_payments > 0 THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date, k.v_f_user_rpt.lt_first_platform_name
```

**Why it matters:** D0 conversion captures impulse-buy behavior on starter packs and first-session offers. Platform split matters because iOS has different payment friction (Apple Pay) vs Android (Google Play billing).

---

### Alert 11: D1 Conversion Rate by Platform
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] D1 Payer Conversion Drop |
| description | D1 cumulative conversion rate (paying users / D0 installs) dropped by platform — first full-day monetization gate |
| custom_query | See below |
| dimension_1 | lt_first_platform_name |
| frequency | 24 h |
| relative_percentage_threshold | 25- |
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
    COUNT(DISTINCT CASE WHEN d1.v_f_user_rpt.is_customer = TRUE THEN d1.user_id END),
    COUNT(DISTINCT d0.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d0
LEFT JOIN `dwh-prod-tophat.BIZ.v_f_main_user_kpis` d1
  ON d0.user_id = d1.user_id
  AND d1.snapshot_date = d0.snapshot_date + 1
WHERE d0.snapshot_date = CURRENT_DATE() - 2
  AND d0.v_f_user_rpt.f_days_since_first_activity = 0
  AND d0.v_f_user_rpt.is_active = TRUE
  AND d0.product_id = 105
GROUP BY d0.snapshot_date, d0.v_f_user_rpt.lt_first_platform_name
```

**Why it matters:** D1 conversion includes users who hit their first OOR, saw the starter pack, and decided to pay (or not). A drop by platform can indicate offer presentation bugs, pricing issues, or payment gateway failures that are platform-specific.

---

### Alert 12: D7 ARPI Decline
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] D7 ARPI Drop |
| description | D7 ARPI (revenue per install) for new users dropped — combined signal of conversion rate × ARPPU |
| custom_query | Revenue sum through D7 / D0 installs, by platform |
| dimension_1 | lt_first_platform_name |
| frequency | 24 h |
| relative_percentage_threshold | 30- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

**Why it matters:** ARPI captures the combined effect of conversion × ARPPU. A 30%+ drop means either the monetization funnel is broken or user quality shifted dramatically.

---

## Pillar 4: Acquisition Quality / Mix Shift

### Alert 13: Platform Mix Shift (iOS Share)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] iOS Share Drop |
| description | iOS share of new users dropped below expected range — iOS users retain 1.7x better; mix shift = blended retention hit |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 15- |
| seasonality | 7 |
| data_points | 14 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  k.v_d_country.geo_tier AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN k.v_f_user_rpt.lt_first_platform_name = 'ios' THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date, k.v_d_country.geo_tier
```

**Why it matters:** iOS users get 25 extra dice (Apple login) and have ~1.7x D7 retention vs Android. A shift toward Android depresses blended retention without any product change. Geo split catches regional UA rebalancing.

---

### Alert 14: Guest Login Rate Spike (Android)
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] Android Guest Login Rate Spike |
| description | % of Android new users staying as Guest is above normal — Guest D7 retention is 4.9% vs 12.1% for Facebook-authenticated |
| custom_query | See below |
| frequency | 24 h |
| absolute_upper_threshold | 0.85 |
| recovery_alert | TRUE |
| slack_channel | tophat_lifecycle_alerts |

```sql
SELECT
  k.snapshot_date AS validation_date,
  'all' AS dimension_1_result,
  'all' AS dimension_2_result,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN k.v_f_user_rpt.day_last_social_type = 'guest' THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity = 0
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.v_f_user_rpt.lt_first_platform_name = 'android'
  AND k.product_id = 105
GROUP BY k.snapshot_date
```

**Why it matters:** 78.7% of Android users are Guests with 4.9% D7 retention vs 12.1% (Facebook) or 43.3% (Google). A spike means the auth prompt/popup flow may be broken or the second-chance popup was disabled.

---

## Pillar 5: Feature & Content

### Alert 15: FTUE Minigame Participation Drop
| Field | Value |
|-------|-------|
| validation_name | [Lifecycle - New Users] FTUE Minigame Participation Drop |
| description | % of new users participating in the FTUE minigame dropped — the minigame is a proven retention lever |
| custom_query | See below |
| frequency | 24 h |
| relative_percentage_threshold | 20- |
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
    COUNT(DISTINCT CASE WHEN k.dim_user_snapshot.is_ftue_minigame_active IS NOT NULL THEN k.user_id END),
    COUNT(DISTINCT k.user_id)
  ) AS aggregation_result
FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` k
WHERE k.snapshot_date = CURRENT_DATE() - 1
  AND k.v_f_user_rpt.f_days_since_first_activity BETWEEN 0 AND 3
  AND k.v_f_user_rpt.is_active = TRUE
  AND k.product_id = 105
GROUP BY k.snapshot_date
```

**Why it matters:** The FTUE minigame is a tested retention lever (AB-tested by the team). If participation drops, users aren't reaching or engaging with the tailored early experience that drives stickiness.
