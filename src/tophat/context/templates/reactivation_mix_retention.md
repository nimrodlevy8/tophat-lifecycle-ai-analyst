# Template: Reactivation Mix & Retention

Source: Hex project "Reactivations mix Retention" (032dwdsYhy9R9nS4TJlm18)

## Purpose
Analyze reactivation volume and D7 retention by multiple segmentation dimensions. Used as a base for weekly performance tracking and deep dives into reactivation quality.

## Key Patterns

### Suspicious User Filtering (MANDATORY)
All reactivation and new user funnel queries MUST filter out suspicious users:

```sql
LEFT JOIN `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` AS f_suspicious_at_creation 
  ON f_suspicious_at_creation.user_id = reactivations.user_id
LEFT JOIN `dwh-prod-core.pub.v_d_publisher` AS v_d_publisher 
  ON reactivations.lt_first_publisher_name = v_d_publisher.publisher_name

-- In WHERE or CASE:
CASE WHEN (f_suspicious_at_creation.is_ever_suspicious_at_creation 
       OR v_d_publisher.publisher_name = 'untrusted devices') 
     THEN 'suspicious' ELSE 'rest' END AS suspicious
```

Always show BOTH views (with and without suspicious) to report contamination %.

### Reactivation Definition
```sql
WHERE v_f_user_rpt.is_active
  AND v_f_user_rpt.is_daily_reactivated
  AND v_f_user_rpt.f_days_since_first_activity >= 30
```

### Reactivation Count (Historical)
```sql
reactivation_counts AS (
  SELECT user_id,
         snapshot_date,
         COUNT(*) OVER (PARTITION BY user_id ORDER BY snapshot_date 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS n_reactivations_to_date
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis`
  WHERE v_f_user_rpt.is_daily_reactivated
    AND snapshot_date >= DATE('2023-04-01')
)
```

### Retention Join Pattern (Dx)
```sql
LEFT JOIN (
  SELECT user_id, snapshot_date 
  FROM `dwh-prod-tophat.BIZ.v_f_main_user_kpis` 
  WHERE v_f_user_rpt.is_active AND snapshot_date >= {{date}}
) a
ON a.user_id = reactivations.user_id
AND a.snapshot_date = DATE_ADD(reactivations.snapshot_date, INTERVAL 7 DAY)

-- Then aggregate:
COUNT(DISTINCT CASE WHEN a.snapshot_date = DATE_ADD(reactivations.snapshot_date, INTERVAL 7 DAY) 
      THEN a.user_id END) AS retained_d7
```

### Country/Geo Enrichment
```sql
LEFT JOIN `dwh-prod-core.pub.v_d_country` AS v_d_country 
  ON main_user_kpis_v2.v_f_user_rpt.lt_first_country = v_d_country.iso2
```

### Album Context
```sql
LEFT JOIN `dwh-prod-tophat.DM.dim_album` AS dim_album 
  ON main_user_kpis_v2.snapshot_date BETWEEN DATE(dim_album.start_time) AND DATE(dim_album.end_time)
```

## Standard Bucketing Conventions

### Lifetime Active Days
```sql
CASE WHEN COALESCE(CAST(f_lt_active_days AS INTEGER), 0) <= 5 THEN CAST(f_lt_active_days AS STRING)
     WHEN COALESCE(CAST(f_lt_active_days AS INTEGER), 0) <= 10 THEN 'a.6-10'
     WHEN COALESCE(CAST(f_lt_active_days AS INTEGER), 0) <= 20 THEN 'b.11-20'
     WHEN COALESCE(CAST(f_lt_active_days AS INTEGER), 0) <= 50 THEN 'c.21-50'
     WHEN COALESCE(CAST(f_lt_active_days AS INTEGER), 0) <= 100 THEN 'd.51-100' 
     WHEN COALESCE(CAST(f_lt_active_days AS INTEGER), 0) > 100 THEN 'e.100+' END
```

### Board Level
```sql
CASE WHEN COALESCE(first_board_level, 0) <= 5 THEN CAST(first_board_level AS STRING)
     WHEN COALESCE(first_board_level, 0) <= 10 THEN 'a.6-10'
     WHEN COALESCE(first_board_level, 0) <= 20 THEN 'b.11-20'
     WHEN COALESCE(first_board_level, 0) <= 50 THEN 'c.21-50'
     WHEN COALESCE(first_board_level, 0) <= 100 THEN 'd.51-100' 
     WHEN COALESCE(first_board_level, 0) > 100 THEN 'e.100+' END
```

### Reactivation Count Bucket
```sql
CASE WHEN (rc.n_reactivations_to_date - 1) = 0 THEN '0'
     WHEN (rc.n_reactivations_to_date - 1) = 1 THEN '1'
     WHEN (rc.n_reactivations_to_date - 1) = 2 THEN '2'
     WHEN (rc.n_reactivations_to_date - 1) <= 4 THEN 'a.3-4'
     WHEN (rc.n_reactivations_to_date - 1) <= 9 THEN 'b.5-9'
     WHEN (rc.n_reactivations_to_date - 1) <= 19 THEN 'c.10-19'
     WHEN (rc.n_reactivations_to_date - 1) >= 20 THEN 'd.20+' END
```

### Days Since Previous Activity
```sql
CASE WHEN COALESCE(f_days_since_prev_activity, 0) <= 7 THEN 'a.0-7'
     WHEN COALESCE(f_days_since_prev_activity, 0) <= 14 THEN 'b.8-14'
     WHEN COALESCE(f_days_since_prev_activity, 0) <= 30 THEN 'c.15-30'
     WHEN COALESCE(f_days_since_prev_activity, 0) <= 60 THEN 'd.31-60'
     WHEN COALESCE(f_days_since_prev_activity, 0) <= 90 THEN 'e.61-90'
     WHEN COALESCE(f_days_since_prev_activity, 0) <= 180 THEN 'f.91-180'
     WHEN COALESCE(f_days_since_prev_activity, 0) > 180 THEN 'g.180+' END
```

### Lifetime IAP Revenue Bucket
```sql
CASE WHEN COALESCE(f_lt_iap_revenue, 0) = 0 THEN 'a.0 (NP)'
     WHEN COALESCE(f_lt_iap_revenue, 0) <= 5 THEN 'b.0-5'
     WHEN COALESCE(f_lt_iap_revenue, 0) <= 20 THEN 'c.5-20'
     WHEN COALESCE(f_lt_iap_revenue, 0) <= 50 THEN 'd.20-50'
     WHEN COALESCE(f_lt_iap_revenue, 0) <= 100 THEN 'e.50-100'
     WHEN COALESCE(f_lt_iap_revenue, 0) <= 500 THEN 'f.100-500'
     WHEN COALESCE(f_lt_iap_revenue, 0) <= 1000 THEN 'g.500-1k'
     WHEN COALESCE(f_lt_iap_revenue, 0) > 1000 THEN 'h.1k+' END
```

### Rolls Spent (HC Sink) Bucket
```sql
CASE WHEN COALESCE(f_hc_sink, 0) = 0 THEN 'a.0'
     WHEN COALESCE(f_hc_sink, 0) <= 100 THEN 'b.1-100'
     WHEN COALESCE(f_hc_sink, 0) <= 500 THEN 'c.101-500'
     WHEN COALESCE(f_hc_sink, 0) <= 1000 THEN 'd.501-1,000'
     WHEN COALESCE(f_hc_sink, 0) > 1000 THEN 'e.1,001+' END
```

### Friends Bucket
```sql
CASE WHEN n_friends IS NULL THEN NULL
     WHEN COALESCE(n_friends, 0) = 0 THEN 'a.0'
     WHEN COALESCE(n_friends, 0) <= 5 THEN 'b.1-5'
     WHEN COALESCE(n_friends, 0) <= 10 THEN 'c.5-10'
     WHEN COALESCE(n_friends, 0) <= 20 THEN 'd.10-20'
     WHEN COALESCE(n_friends, 0) > 20 THEN 'e.20+' END
```

### RTP (Return to Player)
```sql
CASE WHEN SAFE_DIVIDE(COALESCE(f_hc_source, 0), COALESCE(f_hc_sink, 0)) = 0 THEN 'a.0'
     WHEN SAFE_DIVIDE(COALESCE(f_hc_source, 0), COALESCE(f_hc_sink, 0)) <= 0.5 THEN 'b.0-50%'
     WHEN SAFE_DIVIDE(COALESCE(f_hc_source, 0), COALESCE(f_hc_sink, 0)) <= 0.8 THEN 'c.50-80%'
     WHEN SAFE_DIVIDE(COALESCE(f_hc_source, 0), COALESCE(f_hc_sink, 0)) <= 0.95 THEN 'd.80-95%'
     WHEN SAFE_DIVIDE(COALESCE(f_hc_source, 0), COALESCE(f_hc_sink, 0)) <= 1 THEN 'e.95-100%'
     WHEN SAFE_DIVIDE(COALESCE(f_hc_source, 0), COALESCE(f_hc_sink, 0)) > 1 THEN 'f.100%+' END
```

## Additional Tables Referenced

- `dwh-prod-tophat.BIZ.v_f_main_user_kpis` — Main user KPI view (source of truth)
- `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` — Suspicious user flag
- `dwh-prod-core.pub.v_d_publisher` — Publisher dimension (for untrusted devices filter)
- `dwh-prod-core.pub.v_d_country` — Country dimension (for geo_tier)
- `dwh-prod-tophat.DM.dim_album` — Album dimension (for album context)
- `dwh-prod-tophat.BIZ.d_monopoly_go_events_calendar_country` — LiveOps events calendar

## Notes
- Always use `snapshot_date <= CURRENT_DATE() - 8` for D7 retention (needs 7 days of forward data)
- Use `GROUP BY ALL` (BigQuery shorthand)
- Prefix bucket values with letters (a., b., c.) for proper sort order in visualizations
- `n_reactivations_to_date - 1` gives prior reactivation count (excluding current)
