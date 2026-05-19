# Weekly KPI Meeting — Template

This template defines the structure for the weekly exec-level KPI review
deck. Based on 5 weekly meeting decks from Mar-Apr 2026.

---

## Purpose

A weekly status update for MGO leadership covering revenue performance,
audience health, monetization trends, and focused analytical deep-dives.
Rotates between analysts for different sections.

**Audience:** Studio leadership, finance, product leads.
**Cadence:** Weekly (typically Monday/Tuesday).
**Format:** 10" x 5.6" slides (compact Google Slides format).

---

## Deck Structure

### 1. Cover Slide
- "Weekly KPI Review" in Quicksand 30pt Bold
- Date in Quicksand 26pt Bold, color `#B45F06` (amber)
- MGO game art background images

### 2. Improvements & Future Schedule (hidden/internal)
- Tracking slide for analytical improvements and ownership
- Not presented — kept for team reference

### 3. Agenda
- Bulleted: owner per section
- Standard items: Performance vs forecast, Finance update, Audience & Monetization KPIs
- "Focused Insights" section rotates topics weekly

### 4. Performance vs Forecast
- Monthly revenue tracker: actual vs target, with event-by-event breakdown
- Format: revenue headline in Jost ExtraBold 16pt, color `#38761D` (green) when positive
- Event callouts: event name in Jost 9pt Bold, key findings below
- Visual: cumulative revenue chart with event markers

### 5. Event-Specific KPI Comparisons
- For the most recent minigame event(s):
  - Engagement and Economy comparison (completion rates, roll sink)
  - Monetization comparison (ARPDAC, ARPDAP, conversion by segment)
- Comparison format: small multiples or side-by-side tables

### 6. Season over Season Overview
- Cumulative performance at matched day count (e.g., "First 39 Days")
- Comparison across recent seasons with start dates
- Annotated with: economy changes, solo/social day mix
- Revenue bridge decomposition (DAU × CR × Payments × ASP × Margin)

### 7. Finance Section
Section divider: title in Quicksand 26pt Bold

Standard slides:
1. **Monthly Financial To-Date** — Gross Bookings, D2C %, Marketing, Adj EBITDA
2. **Monthly Financial Trend** — month-over-month trajectory chart
3. **Cumulative vs AOP** — year-to-date performance vs annual plan

### 8. KPIs Section
Section divider: "KPIs" in Quicksand 34pt Bold, color `#660000`

#### 8a. Executive Summary
Four sections, each with header in Jost 16pt Bold and detail in Quicksand 11pt:
- **Audience [Decline/Engagement/Growth]** — WAU D30+ trend, regulars trend
- **Audience Inflows** — Reactivation volume, Funnel (New DAU) baseline
- **Monetization** — vs expectations, web share trajectory
- **Recommendation/Opportunities** — actionable next step

#### 8b. WAU D30+ Trend
- Chart: WAU D30+ over time with Delta WoW 4 Week Rolling annotation
- Title format: "WAU D30+: [headline finding]" in Jost ExtraBold 15pt

#### 8c. WAU D30+ Decomposition
- Stacked area or waterfall showing: Returning + Reactivations + Funnel
- Title: "WAU D30+: [Increased/Declined] WoW driven by [component]"

#### 8d. Inflow Detail
- Two side-by-side charts:
  - Reactivated WAU D30+ (with target line at 13.5% of 12-week avg)
  - WAU From Funnel D30+ (with target line)
- New DAU & D7 Retention chart (when relevant)

#### 8e. Return Rates
- "WAU D30+ Return Rates (%)" by segment
- Time series with segment breakdown

#### 8f. Momentum Rates
- 2x2 grid: one chart per playday bucket (1, 2-4, 5-6, 7)
- Title: "MOMENTUM RATES [trend description]"

#### 8g. Weekly Regulars D30+
- Absolute trend + Delta WoW 4 Week Rolling
- Narrative on trajectory

#### 8h. Weekly RCs & Conversion
- Two side-by-side: Weekly RCs D30+ (with % over Regulars) and Converted RC %
- Title: "WEEKLY REGULAR CUSTOMERS D30+ & CONVERTED RCs"

#### 8i. ARPWARC & Web Revenue
- Two side-by-side: ARPWARC D30+ trend and % of Web Revenue
- Web revenue share trajectory is a key strategic metric

### 9. Focused Insights (rotating)
1-3 slides on a specific topic, varies weekly. Examples:
- Reactivation retention deep-dive (mix vs. retention analysis)
- Seasons Measuring Framework
- MMR Bug impact & preventive measures
- Ecosystem Analytics Framework
- Racer long-term trends

### 10. Annex
- Supporting cuts and hidden slides
- Season-over-season monetization detail
- Return rates by activity segment (granular view)

---

## Typography (Weekly KPI variant)

Same font stack as readouts, with these additions:

| Element | Font | Size | Color |
|---------|------|------|-------|
| Cover title | Quicksand Bold | 30pt | default |
| Cover date | Quicksand Bold | 26pt | `#B45F06` |
| Section divider | Quicksand Bold | 34pt | `#660000` |
| Slide title | Jost ExtraBold | 15-17pt | default |
| Chart title/label | Jost | 10pt | `#3B3447` |
| Executive summary header | Jost Bold | 16pt | default |
| Executive summary body | Quicksand Bold | 11pt | default |
| Revenue headline | Jost ExtraBold | 16pt | `#38761D` (green, when positive) |
| Event callout | Jost | 9pt | default |
| Data footnote | Quicksand | 6-7pt | default |
| Target definition | Quicksand Bold | 8pt | `#3B3447` |

---

## Naming Convention

Files: `Weekly KPI meeting - YYYY.MM.DD.pptx`
Prefix with `_` for working/draft versions.

---

## Source Files

5 reference decks in `.knowledge/references/weekly-updates/`
