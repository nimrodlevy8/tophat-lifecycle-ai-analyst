# Monopoly Go — Minigames

## Classification

| Minigame | Type | `minigame_type` in data |
|----------|------|------------------------|
| Adventures | Social | `adventure` |
| Coop / Partners | Social | `coop_event` |
| Racers / Tycoon Race | Social | `tycoon_race` |
| Treasure Dig | Solo | `minigame_dig` |
| Boutique | Solo | `boutique` |
| Prize Drop / Plinko | Solo | `prize_drop` |
| Carnival Games | Solo (umbrella) | `carnival_games` |

Carnival sub-games: Juggle Jam, Battleship, Fortune Teller (rotate within `carnival_games`).

---

## Social Minigames

### Adventures

**Overview:** Team-based; group of ~4 players collaboratively advances through a mini-board. Multiple versions (V1, V2, V3).

**Mechanics:**
1. **Team Formation:** ~4 players matched by activity level, friends, or random. Team composition significantly affects outcomes.
2. **Separate Mini-Board:** Themed adventure board distinct from main board, with its own spaces, events, milestones.
3. **Token Mechanics:** Adventure tokens earned from main-game tournaments/milestones → spent to roll on adventure board.
4. **Progression:** Team advances through board, triggering mini-events and collecting checkpoint rewards.
5. **Rewards:** Escalate with depth — rolls, cash, sticker packs, exclusive items. Higher milestones = rarer stickers, larger roll rewards.

**Duration:** 2–4 days.

**Version Differences (from internal PAT-002):**
- **V1:** Basic team progression.
- **V2:** Improved team mechanics. Low-engaged players with 0–2 regular teammates showed **+14–18pp** higher 7-day return rate vs. Coop.
- **V3:** Card mechanics + mini-milestones. Outperforms earlier versions for engagement, especially low-engaged.

**Currency flow:** Tournaments/Milestones → Adventure tokens → Adventure board → Rolls, cash, sticker packs.

---

### Coop / Partners

**Overview:** Collaborative; 2 players work together to complete "attractions" (themed objectives).

**Mechanics:**
1. **Partner Matching:** Paired with 1 partner by activity level. "Carry partners" (one doing most work) is a known issue.
2. **Attractions:** Multiple per event, each tracked via `attraction_id`. Progress bar maxes at **80,000 points** (= 100%).
3. **Point Contribution:** Both partners spend event currency → points accumulate per attraction.
4. **Completion Thresholds:**
   - Under 20%: ≤ 16,000 pts
   - 20–50%: 16,001–40,000 pts
   - 50–80%: 40,001–64,000 pts
   - Over 80%: > 64,000 pts
5. **Event Completion:** All attractions complete → event complete. Tracked in `d_intraday_minigame_completers`.

**Duration:** 2–4 days.

**Rewards:** Milestone-based as attractions fill; final completion significantly larger. Both partners share rewards.

**Key analytical findings:**
- **PAT-003:** Overall Coop KPIs flat, but "pushers" (3–4 attractions at 50%+) who carry partners (80%+ participation) show declining retention and ARPDAU. ~3% of regulars but ~5% of regular revenue. **Masked by Simpson's Paradox — always sub-segment.**
- **PAT-006:** After June 2025 VfM increase, Coop CE stepped up dramatically.
- Named events: "CoopAquaPartners," "CookingPartners"

---

### Racers (Tycoon Race)

**Overview:** Competitive leaderboard minigame. Players compete in brackets for placement-based rewards. Two modes: **Team** (default) and **Solo**.

**Mechanics:**
1. **Brackets:** 20–30 players grouped into a race bracket via MMR-based matchmaking.
2. **Race Modes:** **Team** (groups of ~4 players compete as a unit) or **Solo** (individual competition). Players can choose or are assigned.
3. **Scoring:** Points from main-game actions (rolling, building, attacking, stealing, milestones). Different actions have different point values.
4. **Track Progression:** Points move token along race track with milestone checkpoints and laps. Multiple race stages per event (Race_1, Race_2, … Podium).
5. **Boosters:** Rockets (speed boost), Turbo (burst), Ball-and-Chain (sabotage opponents). Key P2W lever.
6. **Leaderboard:** Final placement (Podium stage) determines reward tier.
7. **Team Formation:** Invitation system (send/receive/accept/decline invitations, join team requests). Autofill option available.
8. **MMR System:** Both user-level (`f_user_mmr`) and team-level (`f_team_mmr`) matchmaking ratings determine bracket assignment.

**Duration:** 1–3 days (multi-stage within the event).

**Rewards:** Based on placement (1st, top 3, top 10, top 50%). Higher = significantly better. Large roll packages, sticker packs (including rare/gold), cash.

**World League (WWL) Events:** Major recurring Racers events named sequentially (WWL18, WWL19, … WWL27+). These are the primary iteration unit for trend analysis.

**Key Data Tables:**
- `DM.fac_intraday_tycoon_race_snapshot_daily` — user-day grain: MMR, score, invitations, race mode, team/competition assignment
- `DM.fac_intraday_tycoon_race_competition` — bracket-level results: point spreads, placements, with nested team_details
- `DM.fac_intraday_tycoon_race_team_stage_progression` — team-stage grain: booster usage, revenue, user_metrics (nested per-player), bad_partners count
- `DM.fac_intraday_tycoon_race_hourly_progression` — hourly grain: pacing, points, economy flow per hour
- `looker_sandbox.competition_users` — pre-joined view: segmentation (activity, liveops, last 7d active), race mode, revenue, rolls, MMR, momentum, d7 return rate
- `looker_sandbox.racer_inequality_users` — flow analysis view: player category tracking across WWL events

**Player Segmentation for Racers:**
- **Activity Segment:** 1-4 day active, 5-6 day active, Regular (7 day)
- **Liveops Segment:** Standard liveops segmentation
- **Last 7 Day Active Segment:** Recent activity level
- Combined with race_mode (Solo/Team) for full behavioral categorization

**Known Analytical Patterns:**
- **Solo vs. Team dynamics:** Solo percentage varies by segment; track solo_percentage as a health indicator
- **P2W perception:** Strongest of any minigame — booster usage (rockets, turbo, ball-and-chain) and revenue concentration drive this
- **Bracket fairness:** Point spreads (1st vs 2nd, 1st vs 4th) indicate bracket balance; high spreads = matchmaking concern
- **Player flow:** Track how players move between activity categories (1-4 day → Regular, Team → Solo, Active → Churned) across WWL iterations
- **Bad partners:** `f_n_team_bad_partners` indicates carry burden — similar to Coop's carry partner issue
- **Revenue window:** Track both event revenue (ARPU during event) and 28-day post-event revenue for full impact assessment

**Standard liveops_id cleaning pattern:**
```sql
-- Clean liveops_id for human-readable grouping
CASE WHEN liveops_id LIKE '%@%'
  THEN CONCAT(DATE(start_time), REPLACE(RIGHT(SPLIT(liveops_id,'@')[1],
    LENGTH(SPLIT(liveops_id,'@')[1]) - LENGTH(SPLIT(SPLIT(liveops_id,'@')[1],'_')[0])), 'SE_',''))
  ELSE liveops_id
END AS liveops_id_cleaned
```

**Standard exclusion filters (comprehensive — excludes SL, TSL, AB, MVT, Internal,
Dark Launch, Control/Variant, cheater splits, and integration tests):**
```sql
AND NOT REGEXP_CONTAINS(liveops_id, r'(?i)Internal|Dark.Launch|_INT@|_INT_|ABTest|MVT_|TSL|Cheater|_solo@|Control|Variant|RubberBanding')
AND NOT REGEXP_CONTAINS(liveops_id, r'(_SL_|_SL@|_SL$)')
```
The SL pattern uses anchors to avoid catching legitimate substrings (e.g.,
"Slytherin" contains "SL" but not as `_SL_`).

**Chat/Messaging in Racers:**
- Team chat tracked via `STD_tophat.chat_interactions_companion` with `group_type = 'group_event'`
- Content types: `text` (free-form), `emoji` (canned stickers/emojis)
- `liveops_id` field in chat_interactions_companion links messages to specific Racers events
- Aggregated daily chat activity in `DM.f_chat_activity` with `group_type = 'group_event'`

**Note:** Social events (Coop, Racers) boost return rates and momentum vs. solo events.

---

## Solo Minigames

### Treasure Dig

**Overview:** Grid-based excavation.

**Mechanics:**
1. **Grid:** Rectangular (commonly 5×5 or 6×6) of covered tiles hiding rewards or empty space.
2. **Dig Tokens:** Spent to reveal tiles; each dig costs set number of tokens.
3. **Reward Distribution:** Common tiles (small cash/rolls), uncommon (medium), rare/vault tiles (large rolls, sticker packs, rare stickers).
4. **Vault/Chest System:** High-value items in grid; may require digging surrounding tiles first or finding keys.
5. **Layer Depth:** Some versions have 2–3 layers — clearing top layer reveals deeper layer with better rewards but higher token costs.
6. **Completion:** Reveal all tiles across all layers.

**Duration:** 1–3 days.

---

### Boutique

**Overview:** Shop/crafting-style minigame.

**Mechanics:**
1. **Shop Interface:** Craft items, fill orders, complete collections.
2. **Orders:** Recipes requiring specific ingredients. Ingredients earned by spending Boutique tokens or gameplay.
3. **Level Progression:** Completing orders advances through levels → new items, higher-value rewards.
4. **Ingredient System:** Tiered (common to rare). Multi-ingredient combinations and "block" mechanics extensively A/B tested.
5. **Reward Cycle:** Each completed order = rewards; full level = bonus rewards.

**Duration:** 2–4 days.

**Confirmed A/B Tests:**
- Multivariate Test (Oct 2025): Control + 6 variants (A–F) — different configurations
- Multi-ingredient Block Test (Dec 2025): Control + Variant A
- Batch Block Tuning Test (Feb 2026): Control + Test Variant
- Case Block Tuning Test (Feb 2026): Control + Test Variant

**Key finding (PAT-004):** Completion rate volatility (ratio of low-engaged to high-engaged CR) positively correlates with 7-day return rate. Currency-sink volatility does NOT. **Difficulty levers > economy levers.**

---

### Plinko / Prize Drop

**Overview:** Plinko-style drop game.

**Mechanics:**
1. **Board:** Vertical board with pegs; reward slots of varying value at bottom.
2. **Tokens:** Spend event tokens per ball drop.
3. **Physics:** Ball bounces semi-randomly; player may choose initial drop position.
4. **Reward Slots:** Edge = low, center = moderate, jackpot slot(s) = highest (large rolls, rare sticker packs).
5. **Multipliers:** Some versions include multiplier zones or special pegs.
6. **Progressive Rewards:** Some versions have cumulative milestone track regardless of ball landing.

**Duration:** 1–3 days.

---

### Carnival Games

Umbrella category covering rotating sub-games. Benchmarked as "1-day FF" (Flash Fortune), "1-day JJ" (Juggle Jam).

**Duration:** 1–2 days (shorter than other minigames).

**Shared carnival token currency** across sub-games.

#### Juggle Jam
Timing/rhythm game. Tap to keep objects airborne. Points for catches; combo multiplier for consecutive catches. Round ends on miss or timer. Points → event progress.

#### Battleship
Grid-based hit/miss (5×5 or 6×6). Select tiles to fire; hits reveal ship segments. Sinking complete ships = bonus. Clear all ships = board clear reward. Has match-based mechanics with tracked metrics: match analysis, unfinished matches, match funnel, matchmaking times.

#### Fortune Teller
Card/reveal-based. Face-down cards or wheel; player reveals cards. Visible rarity tiers. Common to jackpot rewards. Progressive unlocks over multiple rounds.

---

## Minigame Impact on Player Behavior

- Social minigames (especially Adventures V2/V3) drive higher return rates than solo
- Coop requires careful sub-segmentation (Simpson's Paradox risk)
- Boutique A/B test history makes it a well-instrumented testing ground
- Carnival games are short-burst engagement (1–2 days); good for gap-filling between major events
- All minigames depend on Tournaments/Milestones for currency supply — tournament participation is upstream of minigame engagement
