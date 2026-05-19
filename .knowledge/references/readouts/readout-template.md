# D1/D7 Minigame Readout — Template

This template defines the structure for Day 1 and Day 7 readouts of new
minigame features. Based on the Battleship WWL D1 and Boutique WWL4 D7
readout decks.

---

## Purpose

A D1/D7 readout is a recurring deliverable that assesses the launch
performance of a new or iterated minigame event. It answers:
- Did the event perform as expected on key engagement and monetization KPIs?
- How does it compare to prior iterations and benchmark events?
- Are there concerning patterns that need investigation?

**Audience:** Product team, game designers, economy team, stakeholders.

---

## Readout Structure

### 1. Cover Slide
- Event name + "D1 Readout" or "Day 7 Readout"
- Point of Contact: {analyst name}
- Date: {month year}

### 2. Event Description (D7 only)
- Event dates, duration
- Test configuration (variants, targeting)
- Key definitions specific to this event
  - e.g., "Completion = completing one row and one column on Bingo board"
  - e.g., "Completion Rate Volatility = low-engaged CR / high-engaged CR"

### 3. Executive Summary
- 5-8 bold bullet points covering headline findings
- Format: **Finding** (context/nuance in regular weight)
- Cover: engagement, monetization, feature-specific, comparison to prior
- End with the most important takeaway

### 4. Engagement Section
Divider: "Engagement" or "Engagement & Monetization"

Standard slides in order:
1. **Engagement Funnel** — participation → event players → completers
2. **Participation Rate** — by activity segment, trend vs. prior iterations
3. **Continuous Engagement** — by segment, completers vs. non-completers, vs. benchmark
4. **7 Day Return Rate** — by segment, vs. prior iterations, vs. benchmark events
5. **Momentum Rate** (D7) — better metric than D7RR for regulars
6. **Player Type Composition** — % regular vs. low-engaged, sensitivity analysis

### 5. Feature-Specific Section (varies by event)
Examples:
- **Battleship:** Match analysis, unfinished matches, match funnel, MM times
- **Boutique:** Volatility analysis, completion rate by variant, level progression
- **Coop:** Attraction progression, carry partner analysis

### 6. Monetization Section
Divider: "Monetization"

Standard slides:
1. **ARPDAU** — by segment, vs. prior iterations and benchmark
2. **ARPDAC** — revenue per active customer
3. **ARPPU** — by segment
4. **Conversion Rate** — by segment, vs. prior
5. **Revenue** — total, hourly breakdown, vs. forecast
6. **Test Variants** (if applicable) — ARPDAU/ARPDAC lift per variant

### 7. Economy Section
Divider: "Econ" or "Economy"

Standard slides:
1. **RTP** (Return to Player) — event currency returned
2. **Roll Sink / Roll Source** — by segment
3. **Currency Sink / Currency Source** — by segment
4. **Currency Tuning** — actual vs. target sourcing

### 8. Conclusion
- Divider: "Conclusion"
- Key takeaway in large text (Jost 43pt)

### 9. Next Steps / Follow-ups
- Categorized: "To do" / "Working on" / "Done"
- Each item is specific and actionable
- Cross-team items (e.g., "Connect with econ team to quantify PO impact")

### 10. Appendix
- Supporting data tables and charts not in main flow
- Supplementary cuts (e.g., tenure < 30d)

---

## Standard KPIs in Readouts

| KPI | Definition | Segment By |
|-----|-----------|-----------|
| Participation Rate | % of active players who played the event | Activity segment |
| Completion Rate | % of event players who completed | Activity segment |
| Continuous Engagement | Avg % of event timespan played | Activity segment × completer status |
| 7 Day Return Rate | % returning to MGO 7 days post-event | Activity segment |
| Momentum Rate | % maintaining or increasing play-days next 7d | Activity segment (regulars) |
| Churn Rate | % not returning in 7 days post-event | Activity segment |
| ARPDAU | Avg revenue per daily active user | Activity segment |
| ARPDAC | Avg revenue per daily active customer | Activity segment |
| ARPPU | Avg revenue per paying user | Activity segment |
| Conversion Rate | % of active users who paid | Activity segment |
| RTP | Return to Player (currency returned %) | Activity segment |
| Roll Sink | Rolls spent during event | Activity segment |
| Currency Sink/Source | Event currency spent/earned | Activity segment |

---

## Comparison Framework

Every readout compares the event against:
1. **Prior iterations** of the same event (e.g., WWL3 → WWL4)
2. **Benchmark events** of similar type and duration (e.g., 1-day FF, 1-day JJ)
3. **Forecast** — expected targets for key metrics

Present comparisons as: "WWL ARPDAU underperformed against other 1 day
minigames" with the benchmark names listed below the chart.

---

## Standard Filters

All readout data applies these filters by default:
- **Exclude cheaters:** `COALESCE(is_cheater_first_day, false) = false`
- **Exclude new players:** Tenure > 30 days (`D30+` or `D30-` exclusion)
- **Exclude internal:** `liveops_id NOT LIKE '%Internal%'`

Always note filters in the data footnote on every content slide.

---

## Activity Segments (Standard)

| Segment | Definition | Alternate Names |
|---------|-----------|----------------|
| Low-Engaged | 1-4 days active in past 7 days | Occasional |
| Mid-Engaged | 5-6 days active in past 7 days | Casual |
| Regular / High-Engaged | 7 days active in past 7 days | Regular |

---

## Source Files

Example readouts:
- `Battleship WWL D1 Readout.pptx` — D1 for a new carnival game with match mechanics
- `Boutique WWL4 Day 7 Readout 20260210.pptx` — D7 with A/B test volatility analysis
