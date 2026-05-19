# Minigame Performance Monitoring & Assessment Framework

Source: Hex notebook "Minigames Performance Monitoring and Assessment" (Manuel Arroyo)
Exported from Block Boutique AB Tests fork (project 019d8d22-24cb-7001-8503-909c7191edec)

---

## Notebook Structure & Cell Sequence

The notebook has two major sections:
1. **Minigames General** — cross-event performance assessment framework
2. **AB Test Statistical Analysis** — full AB testing pipeline with pre-analysis checks, significance testing, and heterogeneity analysis

---

## Section 1: Minigames General

### KPI Definitions (from the notebook's text cell)

| KPI | Definition |
|-----|-----------|
| **7-Day Return Rate** | % of players returning to MGo game, 7 days after the last day they played Minigame Event X |
| **Continuous Engagement (CE)** | Avg % of timespan into event X played by all participating players |
| **Activation Rate** | Out of players active 7 days prior to event X, what % came back and participated |
| **Reactivation Rate** | Out of players NOT active 7 days prior to event X, what % became active and participated |
| **Momentum Rate** | % of players who INCREASED or KEPT the number of play-days they had at the beginning of event X, the next week after event X |

### Filter Parameters (Input Cells)

| Filter | Variable | Type | Options |
|--------|----------|------|---------|
| Minigame Type | `minigame_type` | MULTISELECT | coop_event, prize_drop, adventure, minigame_dig, boutique, tycoon_race, carnival_games |
| Liveops Event | `liveops_event_selector` | MULTISELECT (dynamic) | Populated from `values_for_filters.liveops_id_cleaned` |
| Segmentation Type | `segmentation_type_selector` | DROPDOWN | Activity Segment, Liveops Segment, Last 7 Day Active Segment, None |
| Activity Segment | `activity_segment_selector` | MULTISELECT (dynamic) | Populated from `events_data.player_type` |
| Tenure | `tenure_selector` | MULTISELECT | D0-D6, D7-D14, D15-D30, D31-D90, D91-D180, D181-D365, D365+ |
| Cheater | `cheater_selector` | MULTISELECT | 0, 1 |
| Event Completer | `is_event_completer` | MULTISELECT | 0, 1 |

### Segmentation Logic

The notebook supports 3 segmentation schemes, switched via `segmentation_type_selector`:

**Activity Segment** (from `d_minigame_user_attributes.start_activity_segment`):
1. Always Regular → '1. Always Regular'
2. Almost Regular → '2. Almost Regular'
3. Casual → '3. Casual'
4. Volatile Activity → '4. Volatile Activity'
5. Occasional → '5. Occasional'
6. Funnel → '6. Funnel'
7. Reactivation → '7. Reactivation'
8. Returning Reactivation → '8. Returning Reactivation'
9. Path to Churn → '9. Path to Churn'

**Liveops Segment** (from `d_minigame_user_attributes`):
1. Loyal Payer (`is_loyal_payer_first_day`)
2. Regular Customer (`is_regular_customer_first_day`)
3. F2P Regular (`is_regular_first_day`)
4. Other

**Last 7 Day Active Segment** (from `d_minigame_user_attributes.f_last_7d_active_days`):
1. 1-4 day active
2. 5-6 day active
3. Regular (7 days)

### liveops_id Cleaning Logic

```sql
CASE WHEN liveops_id LIKE '%@%' 
  THEN CONCAT(
    DATE(liveops_start_time),
    REPLACE(
      RIGHT(
        SPLIT(liveops_id,'@')[1], 
        LENGTH(SPLIT(liveops_id,'@')[1]) - LENGTH(SPLIT(SPLIT(liveops_id, '@')[1],'_')[0])
      ),
      'SE_',''
    )
  ) 
  ELSE liveops_id 
END AS liveops_id_cleaned
```

### Core Query: Events Data

The main query (`events_data`) is the backbone. It:
1. Aggregates from `fac_intraday_minigame_snapshot_daily` at user × liveops_id level
2. Joins to `v_f_user_standard_kpis` for daily KPIs (product_id = 105)
3. Left joins to dimension/fact tables for completers, CE, attributes
4. Groups by: liveops_id_cleaned, minigame_type, player_type, tenure_segment, is_cheater, is_event_completer, momentum_type

**Tables used:**
- `dwh-prod-tophat.DM.fac_intraday_minigame_snapshot_daily` t1 — daily snapshot per user per event
- `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` t2 — standard KPIs (join on user_id, product_id=105, snapshot_date)
- `dwh-prod-tophat.BIZ.f_minigame_continuous_engagement` b — CE numerator
- `dwh-prod-tophat.BIZ.dim_intraday_live_minigames` c — event metadata (start/end dates)
- `dwh-prod-tophat.DM.d_intraday_minigame_completers` d — completer flag
- `dwh-prod-tophat.DM.d_minigame_user_attributes` e — user attributes per event

**Metrics computed (per group):**
- `distinct_users` — COUNT of all users
- `distinct_event_players` — users with currency_sink ≠ 0
- `distinct_completers` — users in completers dim table
- `session_length_minute`
- `revenue` (SUM f_iap_revenue)
- `revenue_regular_customers`
- `completers_revenue`
- `distinct_payers` (revenue > 0)
- `distinct_loyal_payers`
- `distinct_regular_customers`
- `distinct_customers` (customer_days_active > 0)
- `distinct_payers_completers`
- `free_rolls_source`, `rolls_sink`, `rolls_source`
- `currency_sink`, `currency_source`
- `currency_sink_to_complete`, `roll_sink_to_complete`
- `successful_payments`
- `continuous_engagement_numerator` (f_timestamp_last_currency_spent)
- `sum_first_roll_balance`, `sum_last_roll_balance`
- `early_completers` (completion within 2 days of event start)
- `user_days_active`, `payer_days_active`, `customer_days_active`
- `d7_returners`, `event_player_d7_returners`

**Key definitions:**
- **Event player** = user with currency_sink ≠ 0 (spent currency during event)
- **Completer** = user in d_intraday_minigame_completers
- **Early completer** = completed within 2 days of event start
- **Momentum** = upgrade (next_7d > last_7d), downgrade (next_7d < last_7d), stay (equal)

### Derived Metric Cells

**Events Data Filtered** — applies activity_segment_selector filter

**Data for Momentum Rate:**
- Adds window functions: `distinct_event_players_momentum_rate` and `distinct_players_momentum_rate` partitioned by liveops_id + player_type

**Currency Metrics per Player - Unpivoted:**
```sql
SUM(currency_source) / NULLIF(ABS(SUM(currency_sink_to_complete)), 0) AS currency_source_to_complete_ratio
```
Grouped by liveops_id_cleaned, player_type

**Data for Summary Table:**
- Collapses momentum_type by summing distinct_event_players where momentum_type in ('upgrade','stay') → `momentum_players`

### Engagement Section

**Validation: Cross-Source Completer Counts** — validates completer counts across 3 sources:
1. `d_intraday_minigame_completers` 
2. `fac_intraday_minigame_snapshot_daily` (f_event_completion_time IS NOT NULL)
3. `fac_intraday_boutique_hourly_progression` (is_completer = TRUE) [boutique-specific]

**Last Level with Currency Spend** — for boutique: where did non-completers stop spending?
- Joins `fac_intraday_boutique_level_progression` to find last level with f_total_currency_sink ≠ 0
- Groups into: No currency spent / level N / Completer

**High-level completion breakdown:**
- No level completed (last_level_sort = -1)
- Played but didn't complete
- Completer (last_level_sort = 999)

---

## Section 2: AB Test Statistical Analysis

### Pre-Analysis Checks (critical — always run before AB results)

**1. Day-by-Day Metrics by Variant** — daily snapshot query with:
- event_players, total_users, revenue, payers, rolls_sink, currency_sink, session_minutes
- Segmented by player_type (Activity Segment)
- Purpose: check for novelty effects, data quality issues

**2. Daily Metrics — All Segments** — computes daily per-variant:
- ARPDAU = revenue / event_players
- Conversion = payers / event_players  
- ARPPAU = revenue / payers
- Roll sink per player
- Currency sink per player
- Playtime per player

**3. Treatment Effect Stability Charts** — line charts (ARPDAU, Conversion, Roll Sink, Playtime) by variant over event days. Look for:
- Consistent lift (no novelty decay)
- No divergence over time

**4. Denominator Validation by Arm** — checks segment composition stability:
- participation_rate = event_players / total_users
- % each activity segment per variant per day
- Must match within ~1pp across arms

**5. Pre-Analysis Checks Summary** — markdown cell documenting pass/fail:
- Denominator Validation: segment composition matches?
- Day-by-Day Stability: lift consistent across days?
- Data Reconciliation: ETL vs direct query match?

### AB Test Significance Tests

**Rate Metrics (Z-test for proportions):**
- Completion Rate = completers / event_players
- Early Completion Rate = early_completers / event_players
- D7 Return Rate = event_player_d7_returners / event_players
- Conversion (Event) = payers / event_players
- Participation Rate = event_players / users

Method: pooled proportion Z-test, BH-corrected p-values
Output: Delta (pp), % Change, Z-stat, p-value (raw & BH), significance stars

**Ratio Metrics (Welch t-test):**
Uses user-level sufficient statistics query that computes per-segment:
- n_players, n_payers, n_completers, n_customers, n_regular_customers
- mean + variance for: ARPDAU, ARPDAU_winsorized, ARPDAP (per day), ARPDAP (event), ARPDAC, ARPDARC, CE, roll_sink, roll_source, currency_sink, currency_source, playtime, rolls_to_complete, currency_to_complete, revenue, revenue_winsorized

Winsorization: clip at p01/p99 per liveops_id_cleaned

Method: Welch's t-test with Satterthwaite degrees of freedom
- SE = sqrt(var_c/n_c + var_t/n_t)
- 95% CI = diff ± t_crit * SE
- BH correction for multiple testing

### Visualization: Significance Heatmaps

**Rate metrics heatmap:** rows = metrics, columns = segments (All, Always Regular, Almost Regular, Casual, Occasional)
- Color: RdBu_r diverging, centered at 0
- Annotations: delta in pp + raw/BH significance stars

**Ratio metrics heatmap:** same structure with % change + 95% CI + significance

**Forest Plot:** horizontal bar chart with CI whiskers for All Segments
- Blue = significant positive, Red = significant negative, Gray = not significant
- Annotations: % change + absolute CI + significance

### ETL vs AB Test KPI Reconciliation

Compares aggregate-ratio (ETL formula: total_revenue / total_days) vs per-user-mean (AB test formula: AVG(user_revenue / user_days)) for:
- ARPDAU, ARPDAP, ARPDAC, CE, Completion Rate, Conversion
- Flags discrepancies: green (<1%), yellow (1-5%), red (>5%)

### Bootstrap Confidence Intervals

User-level resampling (9999 iterations) for:
- ARPDAU, ARPDAP, ARPDARC, CE, Roll/Currency Sink/Source, Playtime
- 10% subsample of control for speed (FARM_FINGERPRINT mod 10 = 0)
- BCa-style percentile CIs

### Heterogeneity Analysis

Cuts treatment effects by:
1. **Payer Segment**: Loyal Payer, Regular Customer, F2P Regular, Other
2. **Tenure Segment**: D0-D6 through D365+

Computes per-dimension × variant: n_players, n_completers, n_payers, mean/var for ARPDAU, revenue, roll_sink, currency_sink
Then runs Welch t-tests per dimension slice.

---

## Metric Computation Sequence (Summary Table)

When producing a minigame summary table, the sequence is:

1. **Population counts:** distinct_users, distinct_event_players, distinct_completers
2. **Engagement:** CE (continuous_engagement_numerator / event_players), Momentum Rate
3. **Completion:** completion_rate, early_completion_rate, last_level_distribution
4. **Revenue:** revenue, ARPDAU, ARPDAP, conversion, completers_revenue
5. **Economy:** rolls_sink, rolls_source, currency_sink, currency_source, currency_source_to_complete_ratio
6. **Retention:** d7_return_rate, activation_rate, reactivation_rate
7. **Playtime:** session_length_minute per player

### Derived KPI Formulas

| Metric | Formula | Denominator |
|--------|---------|-------------|
| ARPDAU | revenue / user_days_active | All users |
| ARPDAP | revenue / payer_days_active | Payers only |
| ARPDAC | revenue / customer_days_active | Customers only |
| ARPDARC | revenue / customer_days_active | Regular customers only |
| CE | continuous_engagement_numerator / distinct_event_players | Event players |
| Completion Rate | distinct_completers / distinct_event_players | Event players |
| Early Completion Rate | early_completers / distinct_event_players | Event players |
| Conversion | distinct_payers / distinct_event_players | Event players |
| Participation Rate | distinct_event_players / distinct_users | All users |
| D7 Return Rate | event_player_d7_returners / distinct_event_players | Event players |
| Momentum Rate | momentum_players / distinct_event_players | Event players |
| Currency Source to Complete Ratio | currency_source / abs(currency_sink_to_complete) | Completers |

---

## AB Test Analysis Sequence

When performing AB test analysis on minigame events:

### Pre-Analysis Phase
1. Pull day-by-day metrics by variant (daily_by_variant query)
2. Compute daily KPIs aggregated across segments (daily_metrics_all)
3. Chart treatment effect stability (ARPDAU, Conversion, Roll Sink, Playtime lines by variant)
4. Validate denominators (participation rate + segment composition by arm)
5. Summarize pre-analysis checks (pass/fail each)

### Analysis Phase
6. Aggregate AB test data from events_data (ab_test_agg)
7. Run Z-tests on rate metrics per segment (completion, early completion, D7 return, conversion, participation)
8. Query user-level sufficient statistics (means + variances per segment per arm)
9. Run Welch t-tests on ratio metrics (ARPDAU variants, ARPDAP, ARPDAC, CE, economy, playtime)
10. Apply BH correction for multiple testing
11. Reconcile ETL vs AB test formulas

### Validation Phase
12. Bootstrap CIs on key metrics (9999 resamples)
13. Heterogeneity analysis (payer segment × tenure cuts)
14. Visualize: significance heatmaps (rate + ratio), forest plots

### Key Chart Types
- Line chart: daily metric by variant (treatment effect stability)
- Heatmap: metric × segment significance matrix (RdBu_r, delta + stars)
- Forest plot: treatment effects with 95% CIs (blue/red/gray)
- Styled table: ETL vs AB test reconciliation (green/yellow/red color coding)
