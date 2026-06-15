# Skill: Economy RTP Analysis

## When to Apply

Trigger this skill whenever the user asks about:
- RTP (Return to Player), gameplay RTP, general RTP, paid/free RTP
- Roll sources vs sinks, overall economy health
- "How much are players getting back?", "What's the gameplay RTP?"
- Economy health monitoring, roll balance health
- Per-segment or per-day RTP trends
- RTP distribution / percentiles across users

## Core Concept

**Gameplay RTP = gameplay rolls sourced / total rolls sunk**

The fundamental architecture uses TWO SEPARATE CTEs joined on (user_id, snapshot_date):
1. **Source CTE** — aggregates positive item_quantity (grants) classified as gameplay
2. **Sink CTE** — aggregates total sinks per user per day with noise filtering

The SINK is the spine (denominator). Sources are LEFT JOINed onto sinks.
This means the denominator is always "users who actively sunk rolls" — not all users.

### Decomposition Categories
- **Gameplay RTP**: `transaction_category = 'gameplay'` sources / total sinks
- **Free RTP**: `transaction_category IN ('gameplay', 'free')` sources / total sinks
- **Paid RTP**: `transaction_category = 'paid'` sources / total sinks
- **General RTP**: all sources / all sinks

## Source Classifier Table

**Table**: `dwh-prod-tophat.DM.dim_economy_source_classifier_list`

**Column names** (all lowercase):
- `reference_subtype` — join key
- `transaction_subtype` — join key
- `transaction_category`: gameplay / free / paid
- `l1_vertical`: Board, Milestones, Tournament, FlashEvents, SoloMinigames, SocialMinigames, Album, Daily, Regen, Monetization, BoardProg, Seasonal
- `l2_feature`: TycoonRacers, Partners, Dig, Adventures, Boutique, Carnival, etc.
- `l3_context`: deeper sub-feature context

This table has a `snapshot_date` column but no filter is needed — join directly without filtering on it.

**DO NOT USE**: `dwh-prod-tophat-exp.zz_yanir_ashkenazi.maps_source_classifier` (deprecated)

## Two-CTE Architecture (MANDATORY)

Never compute sources and sinks in the same CTE or using CASE WHEN in one pass.
Always build separate CTEs and join them.

### Why Two CTEs?
1. Source and sink have different filter logic (classifier join vs sink_source flag)
2. Sink CTE applies per-user-per-day HAVING noise bounds (500-200,000)
3. Cheater exclusion applies only to the sink side
4. Aggregation grain must be (snapshot_date, user_id) FIRST, then rolled up

## Daily Gameplay RTP Query Pattern

```sql
WITH daily_gameplay_source AS (
    SELECT
        DATE(r.transaction_date) AS snapshot_date,
        r.user_id,
        SUM(r.item_quantity) AS gameplay_rolls_source
    FROM `dwh-prod-tophat.DM.fac_sinks_n_sources` AS r
    INNER JOIN `dwh-prod-tophat.DM.dim_economy_source_classifier_list` AS b
        ON r.reference_subtype = b.reference_subtype
        AND r.transaction_subtype = b.transaction_subtype
    WHERE
        r.product_id = 105
        AND r.item_id = 'rolls'
        AND DATE(r.transaction_date) >= DATE '{start_date}'
        AND r.item_quantity > 0
        AND b.transaction_category = 'gameplay'
    GROUP BY 1, 2
),
daily_roll_sink AS (
    SELECT
        DATE(r.transaction_date) AS snapshot_date,
        r.user_id,
        SUM(ABS(r.item_quantity)) AS roll_sink
    FROM `dwh-prod-tophat.DM.fac_sinks_n_sources` AS r
    LEFT JOIN `dwh-prod-tophat.BIZ.dim_user_cheater` AS c
        ON r.user_id = c.user_id
        AND DATE(r.transaction_date) = c.snapshot_date
    WHERE
        r.product_id = 105
        AND r.item_id = 'rolls'
        AND DATE(r.transaction_date) >= DATE '{start_date}'
        AND r.sink_source = 'sink'
        AND COALESCE(c.is_cheater, FALSE) = FALSE
    GROUP BY 1, 2
    HAVING SUM(ABS(r.item_quantity)) BETWEEN 500 AND 200000
)
SELECT
    s.snapshot_date,
    COUNT(DISTINCT s.user_id) AS users,
    SUM(s.roll_sink) AS roll_sink,
    SUM(COALESCE(g.gameplay_rolls_source, 0)) AS gameplay_rolls_source,
    SAFE_DIVIDE(
        SUM(COALESCE(g.gameplay_rolls_source, 0)),
        SUM(s.roll_sink)
    ) AS gameplay_rtp
FROM daily_roll_sink AS s
LEFT JOIN daily_gameplay_source AS g
    ON s.user_id = g.user_id
    AND s.snapshot_date = g.snapshot_date
GROUP BY 1
ORDER BY 1;
```

## Critical Methodology Rules

1. **Source CTE**: Filter `item_quantity > 0` (positive grants) + classifier `transaction_category = 'gameplay'`. Do NOT use `sink_source` column for sources.

2. **Sink CTE**: Filter `sink_source = 'sink'`, take `ABS(item_quantity)`, apply HAVING bounds.

3. **HAVING filter (noise gate)**: `HAVING SUM(ABS(r.item_quantity)) BETWEEN 500 AND 200000` per user per day. This replaces any KPI active-user join.

4. **Cheater join**: Only on SINK side. Join on BOTH `user_id` AND `snapshot_date` (date-partitioned). Use `COALESCE(c.is_cheater, FALSE) = FALSE`.

5. **Join direction**: Sink is LEFT side (spine). Source is LEFT JOINed. Use `COALESCE(source, 0)` in numerator.

6. **User-level first**: Both CTEs aggregate to (snapshot_date, user_id) grain before the final join and rollup.

7. **No KPI table**: Do NOT join `v_f_user_standard_kpis` for active user filtering. The HAVING bounds serve as the activity gate.

## RTP Distribution Pattern (Percentiles per User)

For user-level RTP distribution, compute per-user RTP from the two-CTE pattern, then take percentiles:

```sql
-- After the two CTEs above, compute user-level RTP:
, user_rtp AS (
    SELECT
        s.snapshot_date,
        s.user_id,
        SAFE_DIVIDE(
            COALESCE(g.gameplay_rolls_source, 0),
            s.roll_sink
        ) AS user_gameplay_rtp
    FROM daily_roll_sink AS s
    LEFT JOIN daily_gameplay_source AS g
        ON s.user_id = g.user_id
        AND s.snapshot_date = g.snapshot_date
)
SELECT
    snapshot_date,
    COUNT(*) AS users,
    AVG(user_gameplay_rtp) AS avg_rtp,
    APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(25)] AS p25,
    APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(50)] AS p50,
    APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(75)] AS p75,
    APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(90)] AS p90
FROM user_rtp
GROUP BY 1
ORDER BY 1;
```

## RTP Curve Pattern (Cumulative)

User-level running RTP as function of cumulative sinks. Requires `STD_tophat.sys_gti_nodedup` (raw granular timestamps — ask user before querying):

```sql
-- Window function for running totals (per user, within time grain)
SUM(CASE WHEN item_quantity > 0 AND transaction_category = 'gameplay' THEN item_quantity ELSE 0 END)
    OVER (PARTITION BY user_id ORDER BY collector_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_source,
SUM(CASE WHEN sink_source = 'sink' THEN ABS(item_quantity) ELSE 0 END)
    OVER (PARTITION BY user_id ORDER BY collector_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sink

-- Then bucket by cumulative sinks:
1000 * (1 + CAST(FLOOR((cumulative_sink - 1) / 1000) AS INT64)) AS sinks_group_1000
```

## Player Segments (for optional segmentation)

| Code | Name | Logic |
|------|------|-------|
| 3.LP | Loyal Payer | `v_f_user_rpt.is_loyal_payer` |
| 2.RC | Regular Customer | `v_f_user_rpt.is_regular_customer` |
| 1.Regular | Regular | `v_f_user_rpt.is_regular` |
| 0.ROP | Rest of Players | Everyone else |

If segment breakdown is requested, add a KPI join only for segmentation labels — NOT for active user filtering.

## Common Pitfalls

1. **DO NOT** use the old experimental classifier table (`dwh-prod-tophat-exp.zz_yanir_ashkenazi.maps_source_classifier`)
2. **DO NOT** use `Reference_subtype` or `Transaction_subtype` (capital R/T) — the DM table uses lowercase
3. **DO NOT** compute source and sink in one CASE WHEN pass
4. **DO NOT** use `sink_source` column to identify sources — only `item_quantity > 0` matters for sources
5. **DO NOT** join KPI table for active user filtering — the HAVING bounds are the noise gate
6. **DO NOT** use `l1_Verticall` (old casing) — the DM table uses `l1_vertical`

## Presentation Standards

- Always show DoD and WoW (or vs 7 days ago) comparison
- Use green arrows for positive movement, red for negative
- RTP formatted as percentage (e.g., "82.5%")
- When presenting summary tables, include user count alongside RTP
- Line charts for daily RTP trends
- Note the HAVING bounds (500-200K) in methodology footnotes
- Expected range for gameplay RTP: typically 0.60-0.90 (not near 1.0)