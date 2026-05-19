# Monopoly Go — Key Metrics & KPIs

## Primary Metrics

| Metric | Description | Level |
|--------|-------------|-------|
| Continuous Engagement (CE) | Sustained play sessions / consistent daily activity | Player, Event |
| Momentum Rate | CE metric tuned for regular players (avoids reactivation noise) | Segment |
| 7-Day Return Rate | % of players returning within 7 days | Cohort, Event |
| ARPDAU | Average Revenue Per Daily Active User | Game, Segment |
| Completion Rate (CR) | % of players completing a minigame event | Event |
| Net Worth | Sum of all landmarks built (primary progression metric) | Player |

## Minigame-Specific Metrics

| Metric | Applies To | Description |
|--------|-----------|-------------|
| Attraction completion % | Coop | Per-attraction fill rate (out of 80,000 points) |
| Token earn rate | All minigames | Tokens earned per day from tournaments/milestones |
| Token sink rate | All minigames | Tokens spent per session in the minigame |
| Currency sink to complete | All minigames | Total tokens needed for full event completion |
| Match funnel | Battleship | Match start → match complete conversion |
| Matchmaking time | Battleship | Time to find an opponent |
| CR volatility | Boutique | Ratio of low-engaged to high-engaged completion rates |

## Segmentation

| Segment | Definition | Why It Matters |
|---------|-----------|----------------|
| Regulars | Consistently active players | Core revenue and engagement base |
| Low-engaged | Below-threshold activity (at risk) | Key target for social minigame impact |
| Reactivations | Returned after absence | Must be separated — inflates metrics if mixed with regulars |
| "Pushers" (Coop) | 3–4 attractions at 50%+, 80%+ participation | ~3% of regulars, ~5% of revenue — declining, masked by aggregates |

**Critical rule:** Always include Reactivations as its own segment. Never mix with regulars.

## Analytical Patterns (from past analyses)

| ID | Finding | Implication |
|----|---------|-------------|
| PAT-001 | CE correlates with retention and spend | Primary mechanics-level health metric |
| PAT-002 | Low-engaged benefit more from Adventures V2/V3 | ~2 regular teammates is the sweet spot |
| PAT-003 | Coop "pushers" degrading despite flat aggregates | Simpson's Paradox — always sub-segment |
| PAT-004 | Boutique CR volatility correlates with return rate | Difficulty levers > economy levers |
| PAT-005 | Return rate sensitive to player composition | Use Momentum Rate for regulars |
| PAT-006 | June 2025 economy change = step-function shift | Always split pre/post |
| PAT-007 | Compare via iterations + benchmarks + forecast | Check progressive offer confounds |

## Analytical Conventions

### Tenure Field
Use `f_days_since_first_activity` for player tenure — NOT `f_days_since_install`.
First activity is the meaningful tenure anchor (installs without activity are noise).

### Activity Segment Source
Use `d_minigame_user_attributes` (columns: `start_activity_segment`,
`end_activity_segment`) — NOT `v_f_user_standard_kpis.v_f_user_rpt.activity_segment`.
The KPI table is a daily snapshot and causes double-counting across event windows.
`d_minigame_user_attributes` gives exactly one row per user per event.

### liveops_id_cleaned for Display
Never show raw `liveops_id` to users — it is not chronologically sortable.
Always compute `liveops_id_cleaned` (CK-002 pattern prepends start date) and
use it for labels, legends, and sort order. Keep raw `liveops_id` for joins only.

### Event Profile Table — First Step
Every minigame analysis must begin with a profile table showing all events per
category: liveops_id_cleaned, dates, duration, sample size (n). This reveals
A/B test splits, tiny control groups, and uneven category sizes before any
aggregate metrics are computed.

## Key Analytical Cautions

1. **Simpson's Paradox:** Always run segment-first checks before concluding on aggregate trends (especially Coop)
2. **Reactivation noise:** IP seasons inflate reactivations; following non-IP season looks like decline but is baseline reversion
3. **Progressive offer confounds:** Running during benchmark but not target period skews comparison
4. **Season normalization:** Compare at same day count ("First 39 Days"), not calendar dates
5. **June 2025 breakpoint:** All trend analysis must account for VfM economy change
