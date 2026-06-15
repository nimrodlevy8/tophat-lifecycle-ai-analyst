# Skill: Vertical RTP Analysis

## When to Apply

Trigger this skill whenever the user asks about:
- Vertical RTP, RTP by vertical, vertical decomposition
- "Which verticals drive RTP?", "What's the RTP breakdown by feature?"
- Source composition by l1_vertical or l2_feature
- "How much do Board/Tournament/FlashEvents contribute to returns?"
- Vertical share of source, per-vertical contribution analysis
- Any RTP question that needs a breakdown by game feature/vertical

Also trigger when the user asks for vertical-level comparison across time periods, or wants to understand which game features are returning the most rolls to players.

## Core Concept

**Vertical RTP = rolls sourced from a specific vertical / TOTAL rolls sunk (all verticals)**

Critical distinction: The DENOMINATOR is the SAME across all verticals — it is the user's total daily sink, NOT a per-vertical sink. This means vertical RTPs sum to the total general RTP.

### Why Total Sink as Denominator?
- Players sink rolls into the board (primarily one activity)
- Sources come back from many verticals (Board rewards, Tournament prizes, etc.)
- Per-vertical sink would be meaningless — most verticals only source, they don't sink
- Using total sink lets you decompose: General RTP = Sum of all vertical RTPs

## Source Classifier Table

**Table**: `dwh-prod-tophat.DM.dim_economy_source_classifier_list`

**Key columns** (all lowercase):
- `reference_subtype`, `transaction_subtype` — join keys
- `l1_vertical` — primary vertical grouping
- `l2_feature` — sub-feature drill-down
- `l3_context` — deeper context
- `transaction_category` — gameplay / free / paid

Join directly without filtering on `snapshot_date`.

**DO NOT USE**: `l1_Verticall` (old casing from deprecated experimental table)

## Known Verticals (l1_vertical)

| Vertical | Description |
|----------|-------------|
| Board | Main board gameplay rewards (Chance, Community Chest, Go) |
| BoardProg | Board progression rewards (level-up, landmark) |
| Milestones | Milestone track completion rewards |
| Tournament | Tournament event prizes |
| FlashEvents | Limited-time flash events |
| SoloMinigames | Single-player minigame rewards (Dig, Plinko, Boutique) |
| SocialMinigames | Multiplayer minigame rewards (Racers, Coop, Adventures) |
| Album | Album/sticker set completion rewards |
| Daily | Daily login/activity/calendar rewards |
| Regen | Time-based roll regeneration |
| Monetization | Purchase-related grants (IAP, progressive offers) |
| Seasonal | Seasonal event rewards |
| Misc | Uncategorized (FTUE, social connects, etc.) |

## Two-CTE Architecture (MANDATORY)

Same mandatory pattern as gameplay RTP — separate Source CTE and Sink CTE, joined on (user_id, snapshot_date). The sink CTE is IDENTICAL to the gameplay RTP skill's sink. The source CTE differs:
- Groups by (snapshot_date, user_id, l1_vertical)
- Does NOT filter by `transaction_category` (includes all source categories)

## Vertical RTP Query Pattern

```sql
WITH daily_vertical_source AS (
    SELECT
        DATE(r.transaction_date) AS snapshot_date,
        r.user_id,
        b.l1_vertical,
        SUM(r.item_quantity) AS vertical_rolls_source
    FROM `dwh-prod-tophat.DM.fac_sinks_n_sources` AS r
    INNER JOIN `dwh-prod-tophat.DM.dim_economy_source_classifier_list` AS b
        ON r.reference_subtype = b.reference_subtype
        AND r.transaction_subtype = b.transaction_subtype
    WHERE
        r.product_id = 105
        AND r.item_id = 'rolls'
        AND DATE(r.transaction_date) >= DATE '{start_date}'
        AND r.item_quantity > 0
    GROUP BY 1, 2, 3
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
    g.l1_vertical,
    COUNT(DISTINCT s.user_id) AS users,
    SUM(s.roll_sink) AS total_roll_sink,
    SUM(COALESCE(g.vertical_rolls_source, 0)) AS vertical_rolls_source,
    SAFE_DIVIDE(
        SUM(COALESCE(g.vertical_rolls_source, 0)),
        SUM(s.roll_sink)
    ) AS vertical_rtp
FROM daily_roll_sink AS s
LEFT JOIN daily_vertical_source AS g
    ON s.user_id = g.user_id
    AND s.snapshot_date = g.snapshot_date
GROUP BY 1, 2
ORDER BY 1, 2;
```

## Key Differences from Gameplay RTP Skill

| Aspect | Gameplay RTP | Vertical RTP |
|--------|-------------|--------------|
| Source filter | `transaction_category = 'gameplay'` | No category filter (all sources) |
| Source grain | (date, user) | (date, user, l1_vertical) |
| Final dimensions | date only | date + l1_vertical |
| Denominator | Total user sink | Same total user sink (shared) |
| Summation property | Single value | Sum of verticals ≈ General RTP |

## l2_feature Drill-Down

For deeper decomposition within a vertical, replace `l1_vertical` with `l2_feature` in the source CTE:

```sql
-- In daily_vertical_source, change:
--   b.l1_vertical  -->  b.l2_feature
-- And group by l2_feature instead of l1_vertical
-- The sink CTE and join structure remain identical
```

Useful for questions like "What's the RTP contribution of TycoonRacers vs Partners within SocialMinigames?"

## Critical Rules

1. **Denominator is TOTAL sink** — never divide by per-vertical sink. The sink CTE has no vertical dimension.
2. **No transaction_category filter** on source — vertical decomposition includes all source types.
3. **Vertical RTPs should sum to ~General RTP** — use this as a sanity check. If they don't sum, some sources are unclassified (NULL l1_vertical).
4. **Use `l1_vertical`** (lowercase) — not `l1_Verticall`.
5. **Sink CTE is identical** to the one in economy-rtp-analysis skill — same HAVING bounds, same cheater join.

## Presentation Standards

- **Stacked area chart**: Daily RTP with each vertical as a stacked layer (shows total RTP composition over time)
- **Horizontal bar chart**: Average vertical RTP contribution ranked from largest to smallest
- **100% stacked bar**: Share of total source by vertical per day
- **Heatmap**: Vertical x Date with RTP intensity coloring
- Exclude Regen, Misc, Monetization from "gameplay vertical" views (or call them out separately)
- Format as percentages (e.g., "Board: 42.1%")
- Include a "Total" row/line that sums all verticals to validate against overall RTP
- When showing WoW changes, highlight verticals with largest absolute change in RTP contribution

## Common Pitfalls

1. **DO NOT** compute per-vertical sinks — sinks are total per user, not attributable to verticals
2. **DO NOT** use `transaction_category = 'gameplay'` filter — vertical decomposition includes all source categories
3. **DO NOT** use the old classifier table or old column casing (`l1_Verticall`, `Reference_subtype`)
4. **DO NOT** confuse l1_vertical with l2_feature — l1 is the grouping (Board, Tournament...), l2 is the specific feature (TycoonRacers, Partners...)
5. **Sanity check**: Sum of all vertical RTPs for a day should approximately equal general RTP for that day. If not, check for NULL verticals from unmatched classifier joins.