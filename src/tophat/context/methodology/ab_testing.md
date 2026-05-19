# AB Test Analysis Standards

## Required Inputs
- Start date
- Population per variant
- Vertical
- Days since test start
- Link to GDD / Deck / Test details / Playgami console
- If any information is unavailable, request it from the user before proceeding

## Hypotheses
- Document hypotheses before analysis
- Readout must validate/invalidate each hypothesis
- All product questions must be answered

## Summary Table
Test vs. control main KPIs with:
- Absolute values per variant
- % Difference (uplift)
- Statistical significance (yes/no)

### Main KPIs to report:
- **Retention:** Dx retention (D1, D7, D14, D30)
- **Monetization:** ARPDAU, ARPDAP, % Conversion
- **Engagement:** Rolls spent per user, Playtime, Number of sessions

## Trend Charts
For each KPI:
- **Line chart:** x-axis = snapshot_date, y-axis = KPI value, lines = variant name
- **Area chart:** % difference between variant(s) and control over time
- **Commentary** on each chart explaining what's shown and conclusions

## Other KPIs
- Specific to the AB test being evaluated
- Tied to product questions
