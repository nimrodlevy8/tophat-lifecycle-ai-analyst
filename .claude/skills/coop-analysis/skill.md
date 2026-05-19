# Skill: Coop Event Analysis

## Trigger

Apply when analyzing **coop events** (aka "Partners" events) in Monopoly GO!.
This includes questions about coop partner composition, pusher/carrier behavior,
social connectivity between partners, friend types, or any coop-specific metrics.

---

## Coop Event Structure

### What is a Coop Event?

A **coop event** (branded as "Partners" in-game) is a social minigame where
players are matched with partners and progress through **attractions** together.
Each attraction is a shared milestone bar that both players contribute to by
spending rolls.

### Player-Partner Structure (CRITICAL)

Each user has **up to 4 partners** per coop event. Each partner corresponds to
a separate attraction. The data is structured as:

```
user_id × liveops_id × partner_user_id × attraction_id
```

**One row per user × partner × attraction** in the raw data. Since each user
has ~4 partners and each partner maps to one attraction, a typical user has ~4
rows per event.

**NEVER use `MAX(partner_user_id)`** or any aggregation that collapses partners.
All 4 partners must be preserved as distinct pairs. Use:

```sql
SELECT DISTINCT user_id, liveops_id, partner_user_id
FROM raw_data
WHERE partner_user_id IS NOT NULL
```

### Attractions

Each user-partner pair works on one attraction. Attractions have:
- `attraction_id` — unique identifier
- `max_bar_attraction_points` — the milestone cap for that attraction
- `player_contribution_attraction_points` — what the user contributed

Attractions with `max_bar_attraction_points > 40000` are considered "real"
attractions (vs trivial/tutorial ones). Null or 'None' `attraction_id` values
should be excluded from attraction-based metrics.

---

## Pusher/Carrier Classification

### Definition

A **Pusher (Carry)** is a player who carries their coop partners by contributing
disproportionately. Classification is at the **USER level** (not per-pair):

```sql
user_classification AS (
  SELECT
    user_id, liveops_id,
    CASE
      WHEN COUNT(DISTINCT CASE
             WHEN attraction_id IS NOT NULL AND attraction_id != 'None'
               AND max_bar_attraction_points > 40000
             THEN attraction_id END) >= 3
        AND SAFE_DIVIDE(SUM(player_contribution_attraction_points),
                        SUM(max_bar_attraction_points)) > 0.8
      THEN 'Pusher (Carry)'
      ELSE 'Non-Pusher'
    END AS player_role
  FROM raw_data
  GROUP BY user_id, liveops_id
)
```

**Two conditions (both required):**
1. **3+ attractions** above the 40K threshold (i.e., they pushed on most of
   their attractions)
2. **>80% overall participation rate** across ALL attractions and ALL partners

**Critical:** This aggregation must be across ALL attractions and ALL partners
per `(user_id, liveops_id)`. It is a user-level property, NOT a pair-level one.

Everyone else is classified as `Non-Pusher`.

---

## Social/Relationship Metrics

### Relationship Score

Relationship score measures how connected two players are. It is stored
**per pair** (not per user) using a canonical pair ID.

**Source table:** `dwh-prod-tophat.DM.f_relationship_score_net`

| Column | Description |
|--------|-------------|
| `group_id` | Canonical pair ID: `LEAST(user_a, user_b) \| GREATEST(user_a, user_b)` |
| `snapshot_date` | Date the score was computed |
| `f_relationship_score` | Overall relationship score (0-1 range) |
| `f_minigames_score` | Minigame sub-score (component of overall score) |
| `has_social_interactions` | Boolean — have they interacted socially |

**Canonical pair ID construction** (must match `group_id` format):

```sql
CONCAT(
  LEAST(CAST(user_id AS STRING), CAST(partner_user_id AS STRING)),
  '|',
  GREATEST(CAST(user_id AS STRING), CAST(partner_user_id AS STRING))
) AS pair_group_id
```

**Key principle:** Pusher classification is at USER level. Social metrics are
at PAIR level. Never conflate the two. Build them in separate CTEs, then join.

### Friend Type / Source

Friend connection type is stored in the active friendships view:

**Source table:** `dwh-prod-tophat.DM.v_active_friendships`

| Column | Description |
|--------|-------------|
| `user_id` | One end of the friendship |
| `friend_id` | Other end of the friendship |
| `friend_source_type` | How they became friends |
| `friend_source_subtype` | More specific source |

**Friend source types** (by volume):
- **Facebook** (Automatic) — connected via Facebook
- **In-Game** — found each other in-game (subtypes: Suggested, Non-Suggested, Tycoon Card, Friend Code, Unknown)
- **Invite** — one invited the other (subtypes: native_share, fb-messenger, whatsapp)
- **Address Book** (Automatic) — connected via contacts

**Friendship is directional in storage** — check both directions:

```sql
LEFT JOIN v_active_friendships f1
  ON pair.user_a = f1.user_id AND pair.user_b = f1.friend_id
LEFT JOIN v_active_friendships f2
  ON pair.user_b = f2.user_id AND pair.user_a = f2.friend_id
  AND f1.user_id IS NULL  -- only use f2 if f1 didn't match
```

If neither direction has a row, they are **Not Friends**.

**Alternative table:** `dwh-prod-tophat.DM.d_user_friends` has full history
with `is_active_friendship` flag. Use for historical friend analysis.

---

## Activity Segments

Player activity is measured via `f_last_7d_active_days` from the minigame
user attributes table:

| Segment | Days Active | Sort Label |
|---------|------------|------------|
| 1-4 Day Active | 1-4 | `1. 1-4 Day Active` |
| 5-6 Day Active | 5-6 | `2. 5-6 Day Active` |
| Regular | 7 | `3. Regular` |
| Other | NULL or 0 | `4. Other` (typically excluded) |

Source: `dwh-prod-tophat.DM.d_minigame_user_attributes` joined on
`(user_id, liveops_id)`.

For 3x3 grid analyses (user-activity x partner-activity), join the attributes
table TWICE — once for the user, once for the partner:

```sql
LEFT JOIN d_minigame_user_attributes attr
  ON user_id = attr.user_id AND liveops_id = attr.liveops_id
LEFT JOIN d_minigame_user_attributes partner_attr
  ON partner_user_id = partner_attr.user_id AND liveops_id = partner_attr.liveops_id
```

---

## Key Tables

| Table | Schema | Purpose |
|-------|--------|---------|
| `coop_attraction_progression` | `dwh-prod-tophat-exp.looker_sandbox` | Raw coop data: user × partner × attraction |
| `d_minigame_user_attributes` | `dwh-prod-tophat.DM` | User attributes per event (activity days, cheater flag) |
| `dim_intraday_live_minigames` | `dwh-prod-tophat.BIZ` | Event metadata (start_date, end_date, liveops_id) |
| `f_relationship_score_net` | `dwh-prod-tophat.DM` | Pair-level relationship scores by snapshot date |
| `v_active_friendships` | `dwh-prod-tophat.DM` | Active friendships (source type, both directions) |
| `d_user_friends` | `dwh-prod-tophat.DM` | Full friend history with is_active flag |
| `f_minigame_continuous_engagement` | `dwh-prod-tophat.BIZ` | Per user×liveops, last % timespan currency was spent (CE metric) |
| `v_f_user_rpt_cornerstone_minigame` | `dwh-prod-data-science.pub` | Daily snapshot of player's cornerstone minigame segment |
| `v_f_user_standard_kpis` | `dwh-prod-tophat.BIZ` | Daily player KPIs. CRITICAL: filter v_f_user_rpt.is_active = true for active users |

---

## Coop Events Analyzed (Jun 2025 - Mar 2026)

These 8 events were used in the pusher/carrier analysis. Their `liveops_id`
values and event start dates:

| Event | liveops_id | Start Date |
|-------|-----------|------------|
| Hot Dog Partners 3 | `HotDogPartners32025@06172025_SE_Coop_HotDogPartners32025` | 2025-06-17 |
| Aqua Partners | `CoopAquaPartners2024@07082025_SE_Coop_AquaPartners2025` | 2025-07-08 |
| Ice Cream Partners | `CoopIceCreamPartners2024@09162025_SE_Coop_IceCreamPartners2025_reuse` | 2025-09-16 |
| Cooking Partners | `CookingPartners2025@10072025_SE_Coop_CookingPartners2025` | 2025-10-07 |
| Cozy Comforts 2 | `CozyComforts_Coop_02@11252025_SE_Coop_CozyComforts_Coop_02` | 2025-11-25 |
| Butter Partners 2 | `Butter_Partners_02@01132026_SE_Coop_Butter_Partners_02` | 2026-01-13 |
| Pets Partners 1 | `Pets_Partners_01@02172026_SE_Coop_Pets_Partners_01` | 2026-02-17 |
| Hotcake Partners 2 | `Hotcake_Partners_02@03102026_SE_Coop_Hotcake_Partners_02` | 2026-03-10 |

**liveops_id format:** `{EventName}@{MMDDYYYY}_SE_Coop_{EventName}`

To get a clean event name from liveops_id, split on `@`, take the second part,
remove the date prefix and `_SE` prefix, then humanize underscores.

---

## Standard Query Patterns

### Pattern 1: Basic Coop Pair Query

Always start with raw_data, then separate user_classification from
user_partner_pairs:

```sql
WITH raw_data AS (
  SELECT user_id, liveops_id, partner_user_id, attraction_id,
    player_contribution_attraction_points, max_bar_attraction_points
  FROM `dwh-prod-tophat-exp.looker_sandbox.coop_attraction_progression`
  WHERE liveops_id IN (...)
),
user_classification AS (
  -- Pusher role at USER level (GROUP BY user_id, liveops_id)
  ...
),
user_partner_pairs AS (
  -- DISTINCT pairs (all 4 partners preserved)
  SELECT DISTINCT user_id, liveops_id, partner_user_id
  FROM raw_data
  WHERE partner_user_id IS NOT NULL
),
classified_pairs AS (
  -- Join classification + attributes + event metadata
  SELECT upp.*, uc.player_role, attr.f_last_7d_active_days, ...
  FROM user_partner_pairs upp
  INNER JOIN user_classification uc ON ...
  LEFT JOIN dim_intraday_live_minigames c ON ...
  LEFT JOIN d_minigame_user_attributes attr ON ...
  WHERE COALESCE(attr.is_cheater_first_day, false) = false
)
```

### Pattern 2: Relationship Score Join

Join with `f_relationship_score_net` using the canonical pair ID at the event
start date:

```sql
rel_scores AS (
  SELECT group_id, snapshot_date, f_relationship_score, f_minigames_score
  FROM `dwh-prod-tophat.DM.f_relationship_score_net`
  WHERE snapshot_date IN (DATE '2025-06-17', ...) -- event start dates
),
pair_scores AS (
  SELECT cp.*, r.f_relationship_score, r.f_minigames_score
  FROM classified_pairs cp
  LEFT JOIN rel_scores r
    ON cp.pair_group_id = r.group_id
    AND r.snapshot_date = cp.event_start_date
)
```

### Pattern 3: Friend Type Join

Use `v_active_friendships` checking both directions:

```sql
-- Deduplicate pairs first (canonical ordering)
deduped_pairs AS (
  SELECT DISTINCT player_role,
    LEAST(user_id, partner_user_id) AS user_a,
    GREATEST(user_id, partner_user_id) AS user_b
  FROM classified_pairs
),
pair_friends AS (
  SELECT dp.*,
    COALESCE(f1.friend_source_type, f2.friend_source_type) AS friend_source_type
  FROM deduped_pairs dp
  LEFT JOIN v_active_friendships f1
    ON dp.user_a = f1.user_id AND dp.user_b = f1.friend_id
  LEFT JOIN v_active_friendships f2
    ON dp.user_b = f2.user_id AND dp.user_a = f2.friend_id
    AND f1.user_id IS NULL
)
```

---

## Cheater Filtering

Always apply cheater filter on the user attributes table:

```sql
WHERE COALESCE(attr.is_cheater_first_day, false) = false
```

This filters out users flagged as cheaters on their first day. Apply to the
focal user, not necessarily the partner.

---

## Common Pitfalls

1. **MAX(partner_user_id)** — NEVER aggregate partners. Each user has up to 4
   distinct partners. Using MAX loses 75% of the pair data.

2. **Pair-level vs user-level confusion** — Pusher classification is USER-level
   (aggregate all attractions across all partners). Social metrics are
   PAIR-level (score between specific user-partner pair). Build in separate
   CTEs, join later.

3. **Directional friendships** — `v_active_friendships` may store friendship
   in one direction only. Always check both `(user_a, user_b)` and
   `(user_b, user_a)`.

4. **Relationship score snapshot timing** — Use the event's `start_date` as
   the snapshot date. The score represents the pair's relationship at the
   moment the event began.

5. **Canonical pair ID format** — Must be `LEAST|GREATEST` as STRING to match
   `f_relationship_score_net.group_id`. Numeric comparison order differs from
   string order for large IDs.

---

## Carry-Partner Classification (Alternative to Pusher)

The **carry-partner** classification is a newer, more sensitive method than the
original pusher classification. It removes the attraction count requirement and
uses a pure contribution ratio threshold.

### Definition

A **carry-partner** is a user whose `overall_contribution_pct` exceeds a given
threshold. There is NO attraction count requirement — just contribution ratio.

```sql
carry_partner_classification AS (
  SELECT
    user_id, liveops_id,
    -- Overall contribution percentage across all attractions
    SAFE_DIVIDE(
      SUM(player_contribution_attraction_points),
      SUM(max_bar_attraction_points)
    ) AS overall_contribution_pct,
    CASE
      WHEN SAFE_DIVIDE(
        SUM(player_contribution_attraction_points),
        SUM(max_bar_attraction_points)
      ) > 0.60  -- threshold (adjustable: 0.50 to 0.90 in 5pp steps)
      THEN 'Carry-Partner'
      ELSE 'Non-Carry-Partner'
    END AS carry_role
  FROM raw_data
  WHERE attraction_id IS NOT NULL AND attraction_id != 'None'
    AND max_bar_attraction_points > 40000
  GROUP BY user_id, liveops_id
)
```

### Key Distinction from Pusher

| Property | Pusher (Original) | Carry-Partner (New) |
|----------|-------------------|---------------------|
| Threshold | >80% contribution | Adjustable (default >60%) |
| Attraction count req | 3+ attractions above 40K | None |
| Sensitivity | Low (~1.8% of users) | Higher (~19.5% at 60%) |
| Revenue capture | ~5% of revenue | ~51% at 60% threshold |
| Use case | Identifying extreme carriers | Broad at-risk segment detection |

### Threshold Sensitivity Reference

| Threshold | % of Regulars | % of Revenue | Lapse Gap (pp) |
|-----------|---------------|--------------|----------------|
| >50% | ~35% | ~68% | +0.6pp |
| >55% | ~26% | ~60% | +1.8pp |
| >60% | ~19.5% | ~51% | +3.8pp |
| >65% | ~14% | ~42% | +5.5pp |
| >70% | ~9.5% | ~32% | +7.4pp |
| >75% | ~5.5% | ~18% | +9.6pp |
| >80% | ~2.5% | ~6% | +11.6pp |
| >85% | ~1.2% | ~3% | +13.2pp |
| >90% | ~0.5% | ~1.2% | +14.9pp |

**Default recommended threshold: 60%** — best trade-off between coverage (19.5%
of regulars, 51% of revenue) and signal strength (+3.8pp lapse gap).

The lapse gap is **monotonically increasing** with threshold — any threshold
above 50% captures meaningful retention signal.

---

## Carry-Partner Behavioral Profile (May 2026 Findings)

Key findings from the carry-partner threshold sensitivity analysis that explain
WHY carry-partners lapse at higher rates:

### 1. Pre-Existing Lower Retention

Carry-partners have ~2pp lower daily active rate **BEFORE** the event starts.
The gap exists before the event — it is NOT caused by the event. This is a
selection effect: players who are already slightly declining are more likely to
end up contributing >60%.

### 2. Social Profile — Weak Signal for Regulars

For regular players (7d active): relationship scores are only -0.02 lower.
Friend type distribution is nearly identical. "Not Friends" rate is the same
(~7%). **Social connectivity does NOT explain the gap for regular carry-partners.**

### 3. Social IS a Factor for Casuals

For casual players (1-4 day active): 25% "Not Friends" rate (+10pp vs others),
lower social interaction scores. Casual carry-partners are genuinely more
isolated, but this is a small sub-population.

### 4. Cornerstone Segment — Not Coop Lovers

Carry-partners are significantly LESS likely to be "Coop Lovers":
- Regulars: -3.3pp Coop Lovers
- Overall: -4.1pp Coop Lovers

They are more likely to be Racers Lovers, Dig Lovers, or Prize Drop Lovers.
**These are players who don't intrinsically love the coop format** but still
participate and contribute disproportionately.

### 5. Partner Profile is NORMAL

Partners of carry-partners have an identical cornerstone distribution compared
to partners of non-carry-partners. The partner assignment is not the problem —
carry-partners are NOT systematically matched with worse partners.

### 6. Active Days During Event — No Frequency Difference

For regulars, BOTH carry-partners and their partners play nearly every day of
the event (~5.9/6 days). There is zero meaningful difference. The gap is NOT
about one side playing fewer days.

### 7. Continuous Engagement (CE) — Intensity, Not Duration

Carry-partners have LOWER CE than others (-1.5pp: 88.1% vs 89.5%). Their
partners actually have slightly HIGHER CE (88.4%) than the carry-partners
themselves. **The partner is NOT giving up earlier.** The carry-partner does
more per-session (higher contribution per day played) rather than staying
engaged longer.

### 8. The Real Story (Synthesis)

Carry-partners are players who:
- Don't intrinsically love coop (not Coop Lovers)
- Have slightly declining baseline engagement (pre-existing)
- Front-load intensity per session (high contribution per day)
- Their partner plays steadily but with less per-session intensity

They contribute >60% **not because they grind harder overall**, but because
per-session they do more while their partner plays more steadily with less
intensity. It's a **selection/composition artifact** (at-risk players naturally
sort into the high-contribution bucket), **not event-induced burnout**.

**Implication:** Interventions should target the pre-existing engagement decline
(a retention problem) rather than trying to rebalance coop contribution
(which is a symptom, not a cause).

---

## Continuous Engagement (CE)

### What is CE?

Continuous Engagement measures how deep into an event a player remained active.
A CE of 88% means the player's last currency spend occurred at 88% of the way
through the event duration. Higher = stayed engaged longer.

### Source and Schema

- **Table:** `dwh-prod-tophat.BIZ.f_minigame_continuous_engagement`
- **Key column:** `f_timestamp_last_currency_spent` (FLOAT, 0-1 range)
- **WARNING:** Despite the column name containing "timestamp", this is NOT a
  timestamp. It's a ratio representing the last % of event duration at which
  the player spent event currency.
- **Grain:** One row per `(user_id, liveops_id)` — 1:1 with user×event

### Usage Pattern

```sql
LEFT JOIN `dwh-prod-tophat.BIZ.f_minigame_continuous_engagement` ce
  ON t1.user_id = ce.user_id
  AND t1.liveops_id = ce.liveops_id
```

Use LEFT JOIN — not all users have CE data (some may not have spent currency).

### Interpreting CE

- **Group averages** (AVG across users) give the segment's continuous engagement rate
- **Comparison:** carry-partner CE vs non-carry-partner CE reveals whether one
  group gives up earlier
- **May 2026 finding:** Carry-partners have ~1.5pp LOWER CE (88.1% vs 89.5%),
  but their partners have HIGHER CE (88.4%). Neither side "gives up" — it's
  about per-session intensity differences.

---

## Cornerstone Minigame Segment

### What is Cornerstone?

The cornerstone segment identifies a player's preferred minigame type based on
their historical play patterns. It classifies players into one dominant
preference category.

### Source and Schema

- **Table:** `dwh-prod-data-science.pub.v_f_user_rpt_cornerstone_minigame`
- **Key column:** `cornerstone_minigame_segment`
- **Partition:** `snapshot_date` (daily snapshots)
- **Values:**
  - `'0. Mixed preference'`
  - `'1. Social Lovers'`
  - `'2. Coop Lovers'`
  - `'3. Racers Lovers'`
  - `'4. Dig Lovers'`
  - `'5. Prize Drop Lovers'`
  - `'6. Carnival Lovers'`
  - `'7. Undetected preference - High tier'`
  - `'8. Undetected preference - Mid and Low tier'`

### Usage Pattern — Segment at Event Time

To get a player's cornerstone segment at the time of an event, join on the
most recent snapshot BEFORE (or at) event start:

```sql
cornerstone AS (
  SELECT user_id, cornerstone_minigame_segment,
    ROW_NUMBER() OVER (
      PARTITION BY user_id
      ORDER BY snapshot_date DESC
    ) AS rn
  FROM `dwh-prod-data-science.pub.v_f_user_rpt_cornerstone_minigame`
  WHERE snapshot_date BETWEEN DATE_SUB(event_start_date, INTERVAL 7 DAY)
    AND event_start_date
)
SELECT * FROM cornerstone WHERE rn = 1
```

### Key Findings (May 2026)

- Carry-partners are significantly LESS likely to be Coop Lovers (-3.3pp for
  regulars, -4.1pp overall)
- They over-index on Racers Lovers, Dig Lovers, and Prize Drop Lovers
- Partners OF carry-partners have a completely normal cornerstone distribution
  (identical to partners of non-carry-partners)

---

## Analysis Lenses for Coop

Coop events can be analyzed from multiple angles. Each lens uses the same base
tables but different metrics and joins.

### 1. Degradation / Carry-Partner Health

Are carry-partners churning? Is the burden growing over time?

- **Primary metric:** Lapse rate gap (carry vs non-carry, 7d post-event)
- **Key tables:** coop_attraction_progression + v_f_user_standard_kpis
- **Classification:** carry-partner at >60% threshold (default)
- **Time axis:** across multiple events to detect trend
- **Reference analysis:** May 2026 threshold sensitivity study

### 2. Progression Analysis

How do players progress through attractions? Completion rates by attraction.

- **Primary metric:** Completion rate, time-to-complete, early completers %
- **Key tables:** coop_attraction_progression
- **Segmentation:** By activity segment, by partner quality

### 3. Revenue Analysis

ARPDAU during event, revenue concentration, payer behavior.

- **Primary metric:** ARPDAU, payer rate, revenue per user
- **Key tables:** coop_attraction_progression + revenue tables
- **Segmentation:** By carry-partner status, by activity segment

### 4. Social Health

Partner matching quality, relationship strength, friend type trends.

- **Primary metric:** Relationship score, Not Friends %, friend source type
- **Key tables:** f_relationship_score_net + v_active_friendships
- **Segmentation:** By carry-partner status, by activity pairing (3×3 grid)

### 5. Cross-Event Comparison

Performance across iterations, seasonal effects, diminishing returns.

- **Primary metric:** Participation rate, completion rate, revenue per event
- **Key tables:** dim_intraday_live_minigames + coop_attraction_progression
- **Time axis:** 8+ events (Jun 2025 – Mar 2026)

### 6. Matchmaking Analysis

How are partners assigned? Optimal vs suboptimal matching patterns.

- **Primary metric:** Activity-segment pairing distribution, mismatch rate
- **Key tables:** d_minigame_user_attributes (joined twice: user + partner)
- **Segmentation:** 3×3 grid of user-activity × partner-activity

**Cross-cutting dimension:** The carry-partner classification (>60% contribution)
is useful across ALL lenses as a segmentation cut. Apply it as an additional
dimension in any coop analysis.

---

## Key Findings Reference

### Apr 2026: Pusher Composition Analysis

From the 8-event pusher composition analysis:

- **Pushers are ~37% Invite-connected** vs ~12% for non-pushers — structurally
  different connection patterns
- **Non-pushers are ~57% In-Game friends** vs ~26% for pushers
- **Pushers have 28% Not Friends** rate vs 16% for non-pushers
- **Relationship scores are comparable** between pushers and non-pushers in
  the same activity pairing — pushers are NOT systematically paired with
  strangers, but their friend composition is different
- **Pair count ratio:** ~1.08M pusher pairs vs ~59.3M non-pusher pairs across
  8 events (~1.8% pusher rate)

Charts and queries are archived in `working/coop-partner-composition/`.

### May 2026: Carry-Partner Threshold Sensitivity Analysis

- Contribution threshold is monotonically related to lapse gap (50%→+0.6pp, 60%→+3.8pp, 80%→+11.6pp, 90%→+14.9pp)
- Carry-partners are a pre-existing at-risk segment, NOT burned out by the event
- The signal is selection (lower baseline engagement) not causation (event damage)
- For regulars, gap widening post-event is minimal (~flat) — event doesn't add incremental damage
- Repeat carry-partner overlap: same players tend to be flagged across events
- Hex project: https://app.hex.tech/0195fa0d-a0b5-7001-b18f-ec09baa16d1a/hex/Coop-Health---Carry-Partner-Threshold-Sensitivity-033G4RRjEfGpnvdfGTznUN/draft/logic
