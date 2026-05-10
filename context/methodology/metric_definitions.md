# Metric Definitions

Canonical definitions for all KPIs used in Lifecycle and EE analysis. Every analyst query should use these definitions — no ad hoc reinterpretation.

<!-- 
NEEDS INPUT: This is the most critical file to fill. For each metric, provide:
- Name
- Definition (exact calculation logic)
- BigQuery source table + columns
- Segmentation dimensions it's typically cut by
- Any gotchas (e.g., "exclude bot accounts", "use server timestamp not client")

Priority metrics to define:

## Retention
- D1, D7, D14, D30 retention
  - How exactly is "return" defined? (Any session? Minimum session length?)
  - Is it calendar-day or 24-hour window?
  - How are new users vs returning users handled?

## Revenue
- ARPDAU (Average Revenue Per Daily Active User)
- ARPPU (Average Revenue Per Paying User)
- Payer conversion rate
- LTV definitions by cohort window

## Engagement
- DAU / WAU / MAU definitions
- Session count, session length
- Playtime (daily, weekly)
- Rolls consumed per day
- Feature participation rates (flash events, tournaments, albums, minigames)

## Progression
- Board level distribution
- Board advancement rate
- FTUE completion rate

## Segment Migration
- How is segment transition measured? (Week over week? Rolling?)
- "Higher segment migration" definition

## Reactivation
- What defines a "reactivated" user?
- Reactivation D1/D7 survival rates
- Rich Returns bucket assignment logic

## Economy
- Out of Rolls (OOR) rate
- Out of Cash (OOC) rate
- Rolls/Cash earn vs spend balance

## Social
- Social Score definition
- Active Social Network (ASN) calculation
- Friend invite conversion

Add each metric below using this format:

### Metric Name
- **Definition**: Exact calculation
- **Source**: `project.dataset.table` + column names
- **Default segments**: tenure, activity_segment, geo_tier, platform
- **Gotchas**: Any caveats
-->
