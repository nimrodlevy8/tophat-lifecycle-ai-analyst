# Skill: Balance Class Analysis

## When to Apply

Trigger this skill whenever the user asks about:
- Roll balance, end-of-day balance, balance health
- Class mobility / class transitions
- Wealth distribution, "how many players are in each class?"
- Balance percentiles (median, p80, p90, p95, p99) by segment
- "Are players accumulating?" or "Are players running low?"
- Balance trends by tenure or album progression

## Core Concept

**Balance Classes** based on `dim_user_snapshot.rolls_end_balance`:

| Class | Range |
|-------|-------|
| 1.Lower | 0-500 rolls |
| 2.Middle | 501-2,000 |
| 3.Upper | 2,001-10,000 |
| 4.Rich | 10,001-40,000 |
| 5.Tycoon | 40,000+ |

## Daily Balance Class Query Pattern

```sql
WITH daily_base AS (
    SELECT
        snapshot_date,
        user_id,
        CASE
            WHEN v_f_user_rpt.is_loyal_payer THEN '3.LP'
            WHEN v_f_user_rpt.is_regular_customer THEN '2.RC'
            WHEN v_f_user_rpt.is_regular THEN '1.Regular'
            ELSE '0.ROP'
        END AS segment,
        dim_user_snapshot.rolls_end_balance AS ending_balance,
        -- Starting balance = end - net change
        dim_user_snapshot.rolls_end_balance - v_f_user_rpt.f_hc_source + v_f_user_rpt.f_hc_sink AS starting_balance
    FROM `dwh-prod-tophat.BIZ.v_f_user_standard_kpis`
    LEFT JOIN `dwh-prod-tophat.BIZ.dim_user_cheater` cheat
        ON cheat.user_id = user_id AND DATE(cheat.snapshot_date) = snapshot_date
    WHERE v_f_user_rpt.is_active
      AND snapshot_date >= CURRENT_DATE() - 30
      AND (NOT cheat.is_cheater OR cheat.is_cheater IS NULL)
)
```

## Class Mobility Pattern

Compute starting and ending class for each user-day, then aggregate transitions:

```sql
CASE 
    WHEN starting_balance <= 500 THEN '1.Lower'
    WHEN starting_balance <= 2000 THEN '2.Middle'
    WHEN starting_balance <= 10000 THEN '3.Upper'
    WHEN starting_balance <= 40000 THEN '4.Rich'
    ELSE '5.Tycoon'
END AS class_start,

CASE 
    WHEN ending_balance <= 500 THEN '1.Lower'
    WHEN ending_balance <= 2000 THEN '2.Middle'
    WHEN ending_balance <= 10000 THEN '3.Upper'
    WHEN ending_balance <= 40000 THEN '4.Rich'
    ELSE '5.Tycoon'
END AS class_end
```

Then: `GROUP BY segment, class_start, class_end` to get transition matrix.

## Balance Percentile Tracking

```sql
SELECT 
    snapshot_date,
    segment,
    APPROX_QUANTILES(ending_balance, 100)[OFFSET(50)] AS median,
    APPROX_QUANTILES(ending_balance, 100)[OFFSET(80)] AS p80,
    APPROX_QUANTILES(ending_balance, 100)[OFFSET(90)] AS p90,
    APPROX_QUANTILES(ending_balance, 100)[OFFSET(95)] AS p95,
    APPROX_QUANTILES(ending_balance, 100)[OFFSET(99)] AS p99
FROM daily_base
GROUP BY snapshot_date, segment
```

## Album-Progression-Normalized Balance

Compare balance across albums at the same % progression point:

```sql
-- Progression percent:
SAFE_DIVIDE(
    DATE_DIFF(snapshot_date, DATE(album.start_date), DAY),
    DATE_DIFF(DATE(album.end_date), DATE(album.start_date), DAY)
) AS album_progression_pct
```

This enables fair season-over-season balance comparison regardless of album length.

## Balance by Tenure Bucket

Cut additionally by tenure for new-vs-mature player balance health:
- a.D0-D6, b.D7-D14, c.D15-D30, d.D31-D90, e.D91-D180, f.D181-D365, g.D365+

## Presentation Standards

- Balance class distribution shown as 100% stacked bars (% of segment per class)
- Percentile trends shown as line charts (one line per percentile, faceted by segment)
- Class mobility shown as grouped bar charts (one facet per starting class, colored by ending class)
- Use DoD and WoW percentage changes for the summary table
- Format balance values with K suffix (e.g., "12.5K")
