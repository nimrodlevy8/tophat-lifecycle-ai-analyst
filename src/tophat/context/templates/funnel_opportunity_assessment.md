# Template: Funnel Opportunity Assessment (Hex)

Source: Hex project "Funnel Opportunity Assessment" (019a8316)

## Purpose
Assess new user funnel health: startup times, home auth rates, D1-D30 retention trends (indexed), and active social network rates by platform.

## Key Tables Discovered

- `dwh-prod-core.hub.startup_complete` — App startup events (time_since_startup, session, device_token, platform_name)
- `dwh-prod-tophat.pub.v_f_ftue` — FTUE funnel events (tutorial_module, tutorial_name, step_name)
- `dwh-prod-tophat.DM.f_user_standard_kpis` — User standard KPIs (DM layer, used for FTUE join)
- `dwh-prod-mkt.pub.v_f_mkt_user_full_cohort` — Marketing cohort table (Dx retention, revenue, users by cohort_date)
- `dwh-prod-mkt.pub.v_d_ua_googleads_asset_type_factors` — Google Ads factors
- `dwh-prod-core.pub.v_d_platform` — Platform dimension
- `dwh-prod-core.pub.v_d_publisher` — Publisher dimension (channel_type_group for paid/organic)
- `dwh-adev-tophat.BIZ.f_social_framework_backup` — Social framework (friend counts, install_date)

## Startup Time Pattern (Median per day, D0 first session only)
```sql
-- Median startup time for new users' first session, by platform
SELECT session_date, platform, median
FROM (
  SELECT session_date, platform,
    PERCENTILE_CONT(total_time, 0.5) OVER(PARTITION BY session_date, platform) AS median
  FROM pre_data  -- filtered to DSI=0, first session only
)
GROUP BY ALL
```

## Home Auth Rate Pattern
```sql
-- % of users reaching home_authentication out of those who reached Download step
SAFE_DIVIDE(
  COUNT(DISTINCT CASE WHEN tutorial_module = 'home_authentication' THEN user_id END),
  COUNT(DISTINCT CASE WHEN tutorial_module = 'Download' THEN user_id END)
) * 100 AS ha_rate
FROM `dwh-prod-tophat.pub.v_f_ftue` ftue
WHERE tutorial_name IN ('Download','Loading','home_authentication','FTUE_tutorial',...)
  AND ftue.build_type = 1
  AND DATE(ftue.collector_date) = DATE(fuk.lt_first_activity_time)
```

## Retention from Marketing Cohort Table
```sql
-- Pre-built Dx retention from cohort table (no need to self-join)
SAFE_DIVIDE(SUM(f_d1_active_users), SUM(IF(dsi >= 1, f_users, 0))) AS retention_rate_d1
SAFE_DIVIDE(SUM(f_d7_active_users), SUM(IF(dsi >= 7, f_users, 0))) AS retention_rate_d7
SAFE_DIVIDE(SUM(f_d30_active_users), SUM(IF(dsi >= 30, f_users, 0))) AS retention_rate_d30
FROM `dwh-prod-mkt.pub.v_f_mkt_user_full_cohort`
WHERE cohort_type = 'New User'
```

## Indexed Retention (Python)
```python
# Index each metric to its first N months average (baseline = 100)
baseline = series.iloc[:BASELINE_MONTHS].mean()
indexed = (series / baseline) * 100
```

## Marginal Component Contribution (Waterfall)
```python
# D30 retention decomposed into: D1 × (D3/D1) × (D7/D3) × (D30/D7)
# Log-additive shares for order-invariant waterfall
logs = np.log(components / 100.0)
total_change = final_indexed - 100
contributions = total_change * (logs / logs.sum())
```

## Active Social Network Rate
```python
# % of D7/D30 active users with ≥4 friends
d7_active_network = friends_d7_users / d7_users
d30_active_network = friends_d30_users / d30_users
```
