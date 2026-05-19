# Template: Reactivators Economy (RTUE Minigame Analysis)

Source: Hex project "Reactivators economy" (019d4cc9)

## Purpose
Analyze RTUE minigame economy: event type mix, milestone progression, rolls spent/sourced per level, RTP curves, completion timing, and post-completion retention.

## Key Queries

### Reactivation Event Type Mix
```sql
WITH reactivations AS (
  SELECT user_id, snapshot_date, v_f_user_rpt.f_hc_sink, v_f_user_rpt.f_hc_source
  FROM `dwh-prod-tophat.BIZ.v_f_user_standard_kpis`
  WHERE snapshot_date >= '2026-01-01'
    AND v_f_user_rpt.is_daily_reactivated
    AND dim_user_snapshot.last_board_level >= 5
    AND v_f_user_rpt.is_active
),
rtue AS (
  SELECT user_id, DATE(collector_date) AS snapshot_date, liveops_id, COUNT(DISTINCT user_id)
  FROM `dwh-prod-tophat.STD_tophat.game_liveops`
  WHERE DATE(collector_date) >= '2026-01-01'
    AND liveops_id NOT LIKE '%MLS%' AND liveops_id NOT LIKE '%TN%'
    AND liveops_id NOT LIKE '%LeagueSeason%' AND liveops_id NOT LIKE '%SeasonalBoard%'
    AND liveops_id NOT LIKE '%GoFriends%' AND liveops_id NOT LIKE '%MegaHeist%'
    AND liveops_id NOT LIKE '%HighRoller%' AND liveops_id NOT LIKE '%LuckyChance%'
    AND (liveops_id LIKE '%Coop%' OR liveops_id LIKE '%Treasures%' OR liveops_id LIKE '%Race%' 
         OR liveops_id LIKE '%Boutique%' OR liveops_id LIKE '%Plinko%')
    AND action_type = 'liveops_starts'
  GROUP BY ALL
)
SELECT r.snapshot_date, liveops_id,
  CASE WHEN liveops_id LIKE '%RTUE%' THEN 'RTUE' ELSE 'Regular' END AS RTUE,
  CONCAT(
    CASE WHEN liveops_id LIKE '%Coop%' THEN 'Coop'
         WHEN liveops_id LIKE '%Treasures%' THEN 'Treasures'
         WHEN liveops_id LIKE '%Boutique%' THEN 'Boutique'
         WHEN liveops_id LIKE '%Plinko%' THEN 'Plinko'
         WHEN liveops_id LIKE '%Racers%' THEN 'Racers'
         ELSE 'Other' END, '-',
    CASE WHEN liveops_id LIKE '%_1D%' THEN '1D'
         WHEN liveops_id LIKE '%_2D%' THEN '2D'
         WHEN liveops_id LIKE '%_3D%' THEN '3D'
         WHEN liveops_id LIKE '%_4D%' THEN '4D'
         WHEN liveops_id LIKE '%_5D%' THEN '5D' ELSE '_' END
  ) AS duration,
  COUNT(DISTINCT r.user_id) AS users
FROM reactivations r
LEFT JOIN rtue s ON r.user_id = s.user_id AND s.snapshot_date = r.snapshot_date
GROUP BY ALL
```

### Milestone Progression Data
```sql
SELECT user_id, liveops_id,
  CASE WHEN liveops_id LIKE '%_1D%' THEN '1D' ... ELSE '_' END AS duration,
  milestone_order,
  DATE(SAFE.PARSE_TIMESTAMP('%m/%d/%Y %H:%M:%S', liveops_start_time)) AS start_date,
  MIN(collector_time) AS min_time,
  MIN(IF(action_type = 'finished', collector_time, 
      SAFE.PARSE_TIMESTAMP('%m/%d/%Y %H:%M:%S', liveops_end_time))) AS finish_time
FROM `dwh-prod-tophat.STD_tophat.game_milestone`
WHERE DATE(collector_time) BETWEEN DATE_SUB(CURRENT_DATE()-7, INTERVAL 45 DAY) AND CURRENT_DATE()
  AND liveops_id LIKE '%RTUE%' AND liveops_id NOT LIKE '%MLS%'
GROUP BY 1, 2, 3, 4, 5, 6
```

### Revenue Per Milestone (join sys_payment within milestone window)
```sql
SELECT m.user_id, m.liveops_id, m.start_date, m.milestone_order,
  COUNT(*) AS purchases, SUM(r.amount_us_excl_vat) AS revenue
FROM milestone_data m
INNER JOIN `dwh-prod-tophat.STD_tophat.sys_payment` r
  ON m.user_id = r.user_id
  AND r.collector_time BETWEEN m.min_time AND m.finish_time
  AND r.success AND r.build_type = 1
GROUP BY 1, 2, 3, 4
```

### GTI Rolls Per Milestone
```sql
SELECT m.user_id, m.liveops_id, m.start_date, m.milestone_order,
  SUM(CASE WHEN g.item_quantity < 0 THEN -g.item_quantity END) AS rolls_spent,
  SUM(CASE WHEN g.item_quantity > 0 THEN g.item_quantity END) AS rolls_source
FROM milestone_data m
INNER JOIN `dwh-prod-tophat.STD_tophat.sys_gti_nodedup` g
  ON m.user_id = g.user_id
  AND g.collector_time BETWEEN m.min_time AND m.finish_time
  AND g.build_type = 1 AND g.item_id = 'rolls'
GROUP BY 1, 2, 3, 4
```

## Key Metrics Computed
- `% Of users` = SUM(level_users) / SUM(total_users)
- `Rolls spent per user` = SUM(rolls_spent) / SUM(level_users)
- `Running RTP` = SUM(running_rolls_source) / SUM(running_rolls_spent)

## Key Findings (from markdown cells)
- ~50% of reactivated users don't get an event when coming back ("Other")
- RTUE Treasures-1D is consistently the top event by participation
- 1D events: users accumulate ~5.9K rolls to complete; 3D/4D: ~14K
- 4D events have highest level-1 finish (97%) and best completion throughout
- RTP climbs from ~70-74% at milestone 1 to >100% by milestone 14-15 for 2D+ events
- 72% of 1D completers finish within first hour
- Faster completers consistently get better RTP across all durations

## Additional Tables
- `dwh-prod-tophat.STD_tophat.game_milestone` — milestone progression events
- `dwh-prod-tophat.STD_tophat.sys_gti_nodedup` — deduplicated GTI (rolls transactions)
- `dwh-prod-tophat.STD_tophat.sys_payment` — payment events
- `dwh-prod-tophat.BIZ.v_f_user_rpt_extended_materialized` — extended user KPIs (for retention checks)
