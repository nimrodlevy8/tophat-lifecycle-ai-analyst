# Skill: Economy RTP Analysis

## When to Apply

Trigger this skill whenever the user asks about:
- RTP (Return to Player), gameplay RTP, general RTP, paid/free RTP
- Roll sources vs sinks, source decomposition by vertical
- "How much are players getting back?", "Which verticals drive RTP?"
- Economy health monitoring, roll balance health
- Per-segment RTP comparison (LP, RC, Regular, ROP)
- RTP distribution / percentiles across users

## Core Concept

**RTP = rolls sourced / rolls sunk** (on a given grain: daily, weekly, per-event, per-user)

Decomposition:
- **Gameplay RTP**: `transaction_category = 'gameplay'` sources only
- **Free RTP**: `transaction_category IN ('gameplay', 'free')` sources
- **Paid RTP**: `transaction_category = 'paid'` sources
- **General RTP**: all sources / all sinks

## Source Classifier Join Pattern

Always join sinks/sources to the source classifier to attribute:

```sql
FROM `dwh-prod-tophat.DM.fac_sinks_n_sources` r
LEFT JOIN `dwh-prod-tophat-exp.zz_yanir_ashkenazi.maps_source_classifier` b
    ON r.Reference_subtype = b.Reference_subtype
    AND r.Transaction_subtype = b.Transaction_subtype
WHERE r.item_id = 'rolls'
  AND r.product_id = 105
```

The classifier provides:
- `transaction_category`: gameplay / free / paid
- `l1_Verticall`: Board, Milestones, Tournament, FlashEvents, SoloMinigames, SocialMinigames, Album, Daily, Regen, Monetization, BoardProg, Seasonal
- `l2_Feature`: TycoonRacers, Partners, Dig, Adventures, Boutique, Carnival, etc.

## Standard RTP Query Pattern (Daily, by Vertical)

```sql
SELECT
    DATE(r.transaction_date) AS day,
    b.l1_Verticall,
    SUM(CASE WHEN r.item_quantity > 0 AND b.transaction_category = 'gameplay' 
        THEN r.item_quantity ELSE 0 END) AS gameplay_source,
    SUM(CASE WHEN r.item_quantity < 0 
        THEN ABS(r.item_quantity) ELSE 0 END) AS total_sink,
    SAFE_DIVIDE(
        SUM(CASE WHEN r.item_quantity > 0 AND b.transaction_category = 'gameplay' 
            THEN r.item_quantity ELSE 0 END),
        NULLIF(SUM(CASE WHEN r.item_quantity < 0 
            THEN ABS(r.item_quantity) ELSE 0 END), 0)
    ) AS gameplay_rtp
FROM `dwh-prod-tophat.DM.fac_sinks_n_sources` r
INNER JOIN `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` kpi
    ON r.user_id = kpi.user_id
    AND DATE(r.transaction_date) = kpi.snapshot_date
    AND kpi.product_id = 105
LEFT JOIN `dwh-prod-tophat-exp.zz_yanir_ashkenazi.maps_source_classifier` b
    ON r.Reference_subtype = b.Reference_subtype
    AND r.Transaction_subtype = b.Transaction_subtype
LEFT JOIN `dwh-prod-tophat.BIZ.dim_user_cheater` cheat
    ON cheat.user_id = r.user_id
    AND DATE(cheat.snapshot_date) = DATE(r.transaction_date)
WHERE r.item_id = 'rolls'
  AND r.product_id = 105
  AND DATE(r.transaction_date) >= CURRENT_DATE() - 30
  AND kpi.v_f_user_rpt.is_active
  AND (NOT cheat.is_cheater OR cheat.is_cheater IS NULL)
GROUP BY 1, 2
```

## RTP Distribution Pattern (Percentiles per Segment)

For user-level distribution, compute per-user RTP first then take percentiles:

```sql
-- User-day grain
SAFE_DIVIDE(
    SUM(CASE WHEN item_quantity > 0 AND transaction_category = 'gameplay' THEN item_quantity ELSE 0 END),
    NULLIF(SUM(CASE WHEN item_quantity < 0 THEN ABS(item_quantity) ELSE 0 END), 0)
) AS user_gameplay_rtp

-- Then aggregate:
AVG(user_gameplay_rtp) AS avg_rtp,
APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(25)] AS p25,
APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(50)] AS p50,
APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(75)] AS p75,
APPROX_QUANTILES(user_gameplay_rtp, 100)[OFFSET(90)] AS p90
```

## RTP Curve Pattern (Cumulative)

User-level running RTP as function of cumulative sinks (bucketed in 1000s):

```sql
-- Window function for running totals
SUM(CASE WHEN item_quantity > 0 AND transaction_category = 'gameplay' THEN item_quantity ELSE 0 END) 
    OVER (PARTITION BY user_id, [time_grain] ORDER BY collector_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS current_sources,
SUM(CASE WHEN item_quantity < 0 THEN ABS(item_quantity) ELSE 0 END) 
    OVER (PARTITION BY user_id, [time_grain] ORDER BY collector_time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS current_sinks

-- Then bucket:
1000 * (1 + CAST(FLOOR((current_sinks - 1) / 1000) AS INT64)) AS sinks_group_1000
```

## Excluded Verticals for "Gameplay RTP" Views

When showing gameplay-only RTP by vertical, typically exclude: Regen, Misc, Monetization, NotSure.

## Player Segments

| Code | Name | Logic |
|------|------|-------|
| 3.LP | Loyal Payer | `v_f_user_rpt.is_loyal_payer` |
| 2.RC | Regular Customer | `v_f_user_rpt.is_regular_customer` |
| 1.Regular | Regular | `v_f_user_rpt.is_regular` |
| 0.ROP | Rest of Players | Everyone else |

## Presentation Standards

- Always show DoD and WoW (or vs 7 days ago) comparison
- Use green arrows for positive movement, red for negative
- RTP formatted as percentage
- When presenting summary tables, include segment breakdown with color-coded deltas
- Heatmaps with column-normalized (per-metric) color scales work well for RTP distribution tracking
