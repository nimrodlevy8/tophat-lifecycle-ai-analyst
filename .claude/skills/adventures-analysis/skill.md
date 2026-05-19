# Skill: Adventures Event Analysis

## Trigger

Apply when analyzing **Adventures** events in Monopoly GO!. This includes
questions about adventure progression, chapter/level completion, adventure
economy (currency sources/sinks), cross-iteration comparison, or per-level
economy breakdowns.

---

## Adventures Event Structure

### What is an Adventures Event?

An **Adventures event** is a team-based, story-driven minigame where players
progress through levels by spending adventure_event_currency (earned via
tournaments, milestones, givercards, etc.). Teams of players are matched by
MMR segmentation. Each level contains objects (milestones) that team members
collectively complete. Players advance through the narrative with
milestone-based rewards at each stage.

### Key Concepts

- **Teams:** Players are grouped into teams via MMR-based matchmaking. Each
  team has an `mmr_segmentation_segment_id` (e.g., segment 1-5) and
  `mmr_segmentation_config_id`.
- **Levels:** Adventure progression is measured in levels (0-N). Level
  attribution uses `fac_intraday_adventure_snapshot_date_level_user_progression`.
  Level 0 = assigned to team but no engagement yet.
- **Objects/Milestones:** Within each level, teams complete objects (identified
  by `milestone_id` containing `_object_` or `_obj_`). Treasure milestones
  are excluded from progression counting.
- **Completion:** A team "completes" the adventure by finishing all non-treasure
  objects. `is_completer` flag on the user snapshot marks individual completion.
- **Adventure Currency:** `adventure_event_currency` is the in-event currency.
  Players sink it via `AdventureEventAttemptSpend` and earn it from multiple
  sources.
- **Event Duration:** Adventures typically run 3-5 days. Event time is
  normalized to percentage (0-100% in 5% buckets) for cross-event comparison.

### Versioning & Event Labels

Events follow a naming convention in `liveops_id`:
- `AdventureEvent_V4_WWL` — Version 4, Whole Wide Land theme
- `AdventureEvent_V4_TSL2` — Version 4, TSL2 slot
- `AdventureEvent_V5_SL` — Version 5, Standard Lane
- `Adventures_FairyTales_1_WWL` — FairyTales theme v1, WWL slot
- `Adventures_HotDog_E3_TSL` / `_WWL` — HotDog Edition 3
- `Adventures_Vikings_E2_WWL` / `_TSL2` — Vikings Edition 2

Use CASE-based labeling to create human-readable `event_label` from raw
`liveops_id` (see SQL patterns below).

---

## Key Tables

| Table | Schema | Purpose |
|-------|--------|---------|
| `fac_intraday_adventure_user_snapshot_daily` | `dwh-prod-tophat.DM` | Daily user-level snapshot per adventure event (completion status, team assignment) |
| `dim_intraday_adventure_teams` | `dwh-prod-tophat.DM` | Team metadata: MMR segment, config, cheater count, team_user_id_array |
| `fac_intraday_minigame_snapshot_daily` | `dwh-prod-tophat.DM` | Cross-minigame daily snapshot (currency_sink, rolls_sink, completion_time) |
| `fac_intraday_adventure_snapshot_date_level_user_progression` | `dwh-prod-tophat.DM` | Per-user per-level progression — correct source for level attribution |
| `d_intraday_minigame_completers` | `dwh-prod-tophat.DM` | Completer flag per user×event |
| `d_minigame_user_attributes` | `dwh-prod-tophat.DM` | User attributes per event (liveops segment: loyal payer, regular customer, F2P regular) |
| `dim_intraday_live_minigames` | `dwh-prod-tophat.BIZ` | Event metadata (start/end times, minigame_type) |
| `STD_tophat.game_milestone` | `dwh-prod-tophat.STD_tophat` | Raw milestone events (action_type='finished' for completion tracking) |
| `STD_tophat.sys_gti` | `dwh-prod-tophat.STD_tophat` | Global transaction inventory — source for all currency flows |
| `STD_tophat.sys_payment` | `dwh-prod-tophat.STD_tophat` | IAP payment events |

### Key Joins

```
fac_intraday_adventure_user_snapshot_daily
  JOIN dim_intraday_live_minigames USING (sk_liveops_event)
  JOIN dim_intraday_adventure_teams ON (team_id, sk_liveops_event)
  LEFT JOIN d_minigame_user_attributes ON (user_id, liveops_id)
```

---

## Analysis Lenses

### 1. Progression Analysis (Completion Curves)

**Purpose:** Track how teams progress through objects over event time,
segmented by MMR.

**Method:** Use `game_milestone` (action_type='finished') to count distinct
objects completed per team over normalized time buckets (0-100% in 5%
increments). Divide by total non-treasure objects to get completion rate.

**Key SQL patterns:**
- Generate time buckets: `GENERATE_ARRAY(0, 100, 5)`
- Compute bucket cutoffs: `TIMESTAMP_ADD(event_start, INTERVAL pct/100 * duration SECOND)`
- Count objects completed before each cutoff per team
- Average across teams within each MMR segment
- Normalize: `avg_objects_completed / total_non_treasure_objects`

**Checkpoint pivot:** Create a wide table with `pct_at_0`, `pct_at_5`, ...,
`pct_at_100` per event for quick cross-event comparison. Weight by team count
when aggregating across MMR segments.

### 2. Adventure Economy Analysis

**Purpose:** Understand currency sources/sinks, cost to complete, and economy
balance.

**Currency Source Taxonomy:**
| Source | transaction_subtype | reference_subtype | Description |
|--------|-------------------|-------------------|-------------|
| Attempt Spend (SINK) | `AdventureEventAttemptSpend` | — | Currency spent on level attempts |
| Tournament | earn | `%tournament%` | From associated tournaments |
| Milestone | earn | `%milestone%` | From milestone completions |
| Quick Wins | earn | `quick wins` / `quick_wins` | Quick win rewards |
| Free Gift | `FreeGift` | — | Free gifts |
| CRM | `AdHocIAMReward` | `crm` | CRM-triggered rewards |
| Board Pickup | `BoardPickupReward` | `team_adventure` | Board landing rewards |
| Level Rewards | `AdventureEventLevelReward` | `team_adventure` | Level completion rewards |
| Object Rewards | `AdventureEventActionReward` | `team_adventure` | Object completion rewards |
| Givercard | `AdventureEventTeamGiftCardReward` | — | Team gift card contributions |
| Event Start | gift + `AdventureEventStart` | — | Initial currency grant |
| Web Portal Loyalty | `WebPortalLoyaltyProgramFreeGift` | — | Web portal loyalty program |
| CS Gift | gift + `CustomerServiceAdmin` | `customer_service` | Customer service grants |

**Roll Economy:** Track `rolls` separately — sink (consume, qty<0) and
source (earn, qty>0).

**IAP:** From `sys_payment` (success=true), summing `amount_us` and counting
distinct `event_id` as payments.

**Filters for sys_gti:**
- `item_id IN ('adventure_event_currency', 'rolls')`
- `transaction_type IN ('earn', 'gift', 'consume', 'convert')`
- `LOWER(transaction_subtype) NOT LIKE '%cleanup%'`
- `build_type = 1`

### 3. Per-Level Economy

**Purpose:** Attribute currency flows to specific adventure levels for
difficulty calibration.

**Level Attribution Method:**
Use `fac_intraday_adventure_snapshot_date_level_user_progression` to get
each user's level start time. Build non-overlapping time windows per level:
- First level window starts at event_start_date
- Each subsequent level starts at its `f_start_time`
- Last level extends to event_end_date
- Users with no progression rows get a synthetic level-0 window

Then join sys_gti transactions to level windows by timestamp range.

**Important:** Roll events do NOT carry adventure-level context — per-level
analysis is currency-only.

**Recon pattern:** Always reconcile per-level sums back to the base
(event-day windowed) table. Check sink, givercard, objects_rewards, and
source columns — tolerance should be <1% difference.

### 4. Segment Analysis (LiveOps Segments)

**Segment definition (from d_minigame_user_attributes):**
```sql
CASE
    WHEN is_loyal_payer_first_day THEN '1. Loyal Payer'
    WHEN is_regular_customer_first_day THEN '2. Regular Customer'
    WHEN is_regular_first_day THEN '3. F2P Regular'
    ELSE '4. Other'
END AS liveops_segment
```

Break all economy metrics by liveops_segment × MMR segment × is_completer.

### 5. Cost to Complete

**Purpose:** Distribution of currency/rolls needed to finish the adventure.

**Method:**
- Use `fac_intraday_minigame_snapshot_daily.f_currency_sink_to_complete`
  (non-zero values only)
- Join with `d_intraday_minigame_completers` to filter to actual completers
- Use latest `snapshot_date < CURRENT_DATE()` per liveops
- Report: mean, median (APPROX_QUANTILES[OFFSET(50)]), and distribution
  (bin by 10-unit buckets)
- Segment by MMR segment and liveops_segment

### 6. Revenue (IAP by Completer Status)

Break IAP by `is_complete` × `liveops_segment`:
- `avg_iap_per_user`
- `avg_iap_per_transaction`
- `avg_payments_per_user`
- User counts

### 7. Cross-Event Comparison

Compare events using:
- Completion checkpoint table (% milestones at each time bucket)
- Currency sink to complete (mean/median by segment)
- Economy balance (source vs. sink ratios)
- Daily progression curves per MMR segment

---

## Eligible Users Query Pattern

Standard base CTE for any adventure analysis:

```sql
SELECT
    mg.start_date AS event_start_date,
    mg.end_date AS event_end_date,
    mg.start_time AS liveops_start_date,
    mg.end_time AS liveops_end_date,
    snap.liveops_id,
    snap.user_id,
    snap.team_id,
    t.mmr_segmentation_config_id AS config_id,
    t.mmr_segmentation_segment_id AS segment_id,
    snap.is_autofilled_user AS is_autofilled,
    FALSE AS is_late_joiner,
    (t.n_cheater_players > 0) AS is_cheater_team,
    MAX(CAST(snap.is_completer AS INT64)) > 0 AS is_complete
FROM `dwh-prod-tophat.DM.fac_intraday_adventure_user_snapshot_daily` AS snap
INNER JOIN `dwh-prod-tophat.BIZ.dim_intraday_live_minigames` AS mg
    ON snap.sk_liveops_event = mg.sk_liveops_event
INNER JOIN `dwh-prod-tophat.DM.dim_intraday_adventure_teams` AS t
    ON snap.team_id = t.team_id AND snap.sk_liveops_event = t.sk_liveops_event
WHERE
    snap.liveops_id IN ({{LIVEOPS_IDS}})
    AND snap.team_id IS NOT NULL
    AND snap.team_id != 'None'
GROUP BY ALL
```

---

## Event Listing Query

```sql
SELECT DISTINCT
    minigame_type,
    liveops_id,
    DATE(start_time) AS event_start_date,
    DATE(end_time) AS event_end_date,
    CASE WHEN liveops_id LIKE '%@%'
        THEN CONCAT(
            DATE(start_time),
            REPLACE(
                RIGHT(SPLIT(liveops_id,'@')[1],
                    LENGTH(SPLIT(liveops_id,'@')[1])
                    - LENGTH(SPLIT(SPLIT(liveops_id,'@')[1],'_')[0])
                ), 'SE_', ''
            )
        )
        ELSE liveops_id
    END AS liveops_id_cleaned
FROM `dwh-prod-tophat.BIZ.dim_intraday_live_minigames`
WHERE minigame_type = 'adventure'
    AND liveops_id NOT LIKE '%Internal%'
ORDER BY liveops_id_cleaned
```

---

## Treasure Objects (Lootboxes)

### What are Treasure Objects?

Each adventure level contains **treasure objects** — lootboxes that reward
players with rolls, currency, stickers, album stickers, and cash when opened.
They are distinct from progression objects: treasure objects are excluded from
completion counting but provide valuable rewards.

### Identifying Treasure Objects

- In `reference_global_event_id` (JSON field in sys_gti): object_id contains `TreasureObj`
- Filter: `LOWER(reference_global_event_id) LIKE '%treasure%'`
- Parse the object_id: `JSON_EXTRACT_SCALAR(reference_global_event_id, '$.object_id')`
- The JSON structure contains: `liveops_id`, `milestone_id` (level), `object_id`, `object_milestone_id`
- Optional fields: `user_id_source` (who triggered it), `team_id`

### Treasure Object Naming Convention

Pattern: `{Theme}_Level{N}_object_{Type}_TreasureObj_{Letter}`

Example from FairyTales:
- `Fairytale_Level1_object_Traversal01b_TreasureObj_F` — Level 1 team treasure
- `Fairytale_Level1_object_Traversal01b_TreasureObj_G` — Level 1 solo treasure
- `Fairytale_Level2_object_Activate01a_TreasureObj_G` — Level 2 team treasure
- `Fairytale_Level2_object_Activate01a_TreasureObj_H` — Level 2 mid treasure (stickers)
- `Fairytale_Level3_object_BossFight01a_TreasureObj_J` — Level 3 team treasure
- `Fairytale_Level3_object_BossFight01a_TreasureObj_K` — Level 3 final treasure (album)

### Treasure Reward Types

| Reward Category | item_id Pattern | Typical Contents |
|----------------|----------------|-----------------|
| Team Treasure (currency+rolls) | `AdvLoot_TeamTrsur_CurrencyRolls_*` | adventure_event_currency + rolls |
| Solo Treasure (mega rolls) | `AdvLoot_SoloTrsur_RollsMega_*` | Large roll grants |
| Mid-level (stickers+cash) | `AdvLoot_Mid_Team_RollEvSticker*` | currency_soft (cash) + sticker packs |
| Final (album stickers) | `AdvLoot_Final_Team_Stickers1234Star_new` | 1/2/3/4 Star Sticker Packs + album stickers |
| Adventure Event Card | `adventure_event_card` | Card box (qty often 0 = container) |
| Album Stickers | `{Album}_{Page}_{Slot}` (e.g., `FairytalesAlbum_3_5`) | Individual named stickers |

### Lootbox Mechanic (earn vs. convert)

Treasure rewards appear as a pair of transactions:
1. **earn** (+1 `AdvLoot_*` container) — player receives the lootbox
2. **convert** (-1 `AdvLoot_*` container) — lootbox is consumed/opened
3. **earn** (rolls, currency, stickers) — actual rewards from the lootbox

When querying treasure rewards, include both `earn` and `convert` transaction_types
to see the full lifecycle. The `convert` rows with -1 quantity confirm the box was
opened. The `earn` rows with actual rewards (rolls, currency, stickers) are the
loot contents.

### Segment-Specific Lootboxes

Lootbox container item_ids are segment-specific:
- `AdvLoot_TeamTrsur_CurrencyRolls_4D3L_Lvl1_v2_seg1` — Segment 1, Level 1
- `AdvLoot_TeamTrsur_CurrencyRolls_4D3L_Lvl2_v2_seg2` — Segment 2, Level 2

The `_seg{N}` suffix determines which reward table is used. This means different
segments get different reward quantities from the same treasure object.

### Querying Treasure Rewards

```sql
-- Treasure object rewards per user per team
-- Always use: build_type = 1, reference_subtype = 'team_adventure'
SELECT
    s.segment,
    s.team_id,
    g.user_id,
    JSON_EXTRACT_SCALAR(g.reference_global_event_id, '$.object_id') AS object_id,
    g.transaction_type,
    g.item_id,
    g.item_name,
    SUM(g.item_quantity) AS item_quantity,
    COUNT(*) AS txn_count
FROM `dwh-prod-tophat.STD_tophat.sys_gti` AS g
INNER JOIN segments AS s
    ON g.user_id = s.user_id
WHERE DATE(g.collector_date) BETWEEN {{DATE_START}} AND {{DATE_END}}
    AND g.reference_subtype = 'team_adventure'
    AND LOWER(g.reference_global_event_id) LIKE '%treasure%'
    AND g.build_type = 1
GROUP BY s.segment, s.team_id, g.user_id, object_id, g.transaction_type, g.item_id, g.item_name
ORDER BY s.segment, s.team_id, g.user_id, object_id, g.transaction_type, g.item_id
```

### MMR Segment ID Patterns

Segment IDs vary by event theme (not always `mmr_segmentation_segment_1`):
- V4/V5 events: `mmr_segmentation_segment_1` through `_5`
- FairyTales: `fairytale-bucket_Seg1` through `_Seg5`

Always check actual values first. Use CASE-based normalization:
```sql
CASE
    WHEN LOWER(mmr_segmentation_segment_id) LIKE '%seg1%' THEN 'seg1'
    WHEN LOWER(mmr_segmentation_segment_id) LIKE '%seg2%' THEN 'seg2'
    WHEN LOWER(mmr_segmentation_segment_id) LIKE '%seg3%' THEN 'seg3'
    WHEN LOWER(mmr_segmentation_segment_id) LIKE '%seg4%' THEN 'seg4'
    WHEN LOWER(mmr_segmentation_segment_id) LIKE '%seg5%' THEN 'seg5'
    ELSE 'other'
END AS segment
```

---

## Hex Reference Projects

| Project | ID | Purpose |
|---------|-----|---------|
| Adventures Progress Charts | `0335HWXJ5jHebEzZDjFrh5` | Completion curves by MMR segment, time-normalized progression |
| Adventure V4 TSL2 Economy (LRK Segments) | `0335MzbWYtT1dOxo6zrHvs` | Economy with liveops_segment breakdown (Loyal Payer / Regular / F2P) |
| Adventure V4 TSL2 Economy | `032VMTBXPwvjpkbkeFMNWe` | Core economy template with per-level attribution, recon patterns |

---

## Common Pitfalls

1. **Level attribution:** Do NOT use `reference_subtype_2` from sys_gti for
   level — it's unreliable. Use `fac_intraday_adventure_snapshot_date_level_user_progression`
   with time-windowed joins.

2. **Treasure milestones:** Always exclude milestones containing 'treasure'
   (`LOWER(milestone_id) NOT LIKE '%treasure%'`) when counting progression objects.

3. **Object identification:** Filter milestone_ids with
   `REGEXP_CONTAINS(milestone_id, r'_(object|obj)_')` to get progression objects.

4. **Non-team users:** Always filter `team_id IS NOT NULL AND team_id != 'None'`
   — unassigned users break team-level analysis.

5. **Autofilled users:** The `is_autofilled_user` flag marks bot-filled team
   slots. Include in team counts but flag separately in analysis.

6. **Event date vs. liveops date:** `event_start_date`/`event_end_date` are
   calendar dates; `liveops_start_date`/`liveops_end_date` are timestamps with
   hour precision. Use calendar dates for day-level joins, timestamps for
   hour-level progression.

7. **Per-level time windows:** First level reaches back to event start, last
   level extends to event end. This ensures no transaction gaps. Always run
   the recon query to verify per-level sums match base table.

8. **Cleanup transactions:** Always exclude `LOWER(transaction_subtype) NOT LIKE '%cleanup%'`
   from sys_gti.

9. **build_type filter:** Always add `build_type = 1` to sys_gti queries
   (production builds only).

10. **Segment NULL check:** When breaking by segment_id, always add
    `AND segment_id IS NOT NULL` — some users have NULL segments.

11. **Cross-system currency sources:** Milestones, tournaments, quickwins, and
    freegifts come from outside the adventure itself — they're "cross-system"
    sources. Separate them from in-adventure sources (level rewards, object
    rewards, givercards, board pickups) for economy interpretation.

12. **Rolls vs. Currency:** Rolls sink/source is completely separate from
    adventure currency. Rolls flow through `item_id = 'rolls'`, currency through
    `item_id = 'adventure_event_currency'`. RTP = rolls_source / -rolls_sink.

---

## Metrics Glossary

| Metric | Definition |
|--------|-----------|
| `avg_pct_milestones_completed` | objects_completed / total_non_treasure_objects (0-1 scale) |
| `currency_sink_to_complete` | Total currency spent by completers (from f_currency_sink_to_complete) |
| `rolls_sink_to_complete` | Total rolls consumed by completers |
| `currency_source` | All currency earned from any source |
| `rolls_rtp` | rolls_source / -rolls_sink (return-to-player on rolls) |
| `ratio_hour_progressed` | hours_since_start / total_event_hours (0-1 scale) |
| `n_teams` | Count of distinct teams in segment |
| `pct_event_time` | Normalized event progress (0-100 in 5% steps) |

---

## Known Events (as of 2026-05-15)

| Event Label | liveops_id | Dates |
|-------------|-----------|-------|
| V4 WWL | `AdventureEvent_V4_WWL@04012026_SE_Adventures_V4_WWL` | 2026-04-01 to 2026-04-04 |
| V5 SL | `AdventureEvent_V5_SL@04282026_SE_Adventures_V5_SL` | 2026-04-28 to 2026-05-02 |
| FairyTales 1 WWL | `Adventures_FairyTales_1_WWL@05132026_SE_Adventures_FairyTales_1_WWL` | 2026-05-13 to 2026-05-18 |
