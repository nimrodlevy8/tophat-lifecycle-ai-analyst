# Analyst Manager Directives

These are authoritative guidelines from the analytics manager. They override defaults and must always be followed.

---

## Core Principles

1. **Be hypothesis-driven.** Ask the questions before running into analysis. Know what is being asked and the logic behind it.
2. **Be critical on results.** If something is unknown, say it's unknown. If there's no clear conclusion, say so. Never fabricate or try to satisfy the prompt.
3. **Product questions first.** Stick to product questions as first priority. Exploration is fine but main questions must be answered first.
4. **Quantify everything.** If things are good or bad, quantify it. Get a recommendation and bottom line with commentary on each chart.
5. **Don't jump to conclusions.** Check yourself. Maintain business and product orientation. >20% change is a big deal — double-check before presenting.

---

## Segmentation Rules

### New Users
Segment by: `geo_tier`, `country_name`, `platform`, `publisher_name`, `channel`

### Reactivations
Segment by: `geo_tier`, `country_name`, `platform`, days since last activity (bins), # of times reactivated in lifetime, `board_level` when reactivating, lifetime activity days when reactivating, customer/non-customer, LTV when reactivating, RTUE mini game

### Segmentation Guidelines
- Explain what led to a segmentation choice and why it matters
- If using a new segmentation not in established context: justify and get approval before using
- Totals are fine for general reporting; for performance/behavior analysis, **normalize**
- If audience shifts between timeframes, raw totals mislead (e.g., total revenue drops because volume drops — that says nothing about per-user performance)

---

## Population Filtering (MANDATORY)

Always filter out:
- `publisher_name = 'untrusted devices'` (via `dwh-prod-core.pub.v_d_publisher`)
- Suspicious users (via `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation`)

**Always show BOTH views** (with and without) to report contamination %.

---

## SQL Templates & Queries

Past SQL queries are **references only**. To build reusable templates:
- Must have defined use cases
- Must be approved before being designated as "reusable"

---

## AB Testing Standards

Required for every test readout:
- **Inputs:** Start date, population per variant, vertical, days since test start, link to GDD/Deck/Playgami console. If unavailable, request from user.
- **Hypotheses:** Document before analysis. Readout must validate/invalidate each one. All product questions answered.
- **Summary table:** Test vs control main KPIs with % uplift and yes/no significance
- **Main KPIs:** Dx Retention, ARPDAU, ARPDAP, % Conversion, Rolls spent per user, Playtime, Sessions
- **Trend charts:** Line chart (x: snapshot_date, y: KPI, lines: variant name) + area chart showing % difference between variant and control
- **Commentary:** On every chart — explain what it shows AND conclusions
- **Other KPIs:** Section for test-specific KPIs tied to product questions

---

## Metric Definitions

### New Users (Day 0 = first activity date)
- **Dx Retention** = users active on day X / users active on day 0
- **Dx ARPI** = sum of revenue through day X (inclusive) / users active on day 0
- **Dx Conversion** = users who paid through day X (inclusive) / users active on day 0

### Reactivations
Same formulas, but **Day 0 = reactivation date** (not first activity date)

---

## Deliverables Platform

**Primary:** Hex (all deliverables should go into Hex when possible)
**Fallback:** Web page that can be exported/downloaded as PDF

---

## Open Analysis Questions (Backlog)

### Reactivations
- Identify biggest levers to inflect D30+ WAU from reactivation
- What are users doing on first day of reactivation? (play volume, minigame engagement, offer engagement)
- Retention indicators for reactivations
- What are users seeing when coming back? Cognitive load? Funnel for reactivations
- Create reactivation framework: same as main_standard_kpis but for days since reactivation
- Weekly performance: long-term (26 weeks) and short-term (4 weeks, focus on previous week)
- Connect UA spend to performance: metrics showing benefit of increasing/decreasing UA trends
- Alert system for reactivated users
- RTUE mini game performance

### New Users
- Retention indicators for new users
- Weekly performance: long-term (26 weeks) and short-term (4 weeks, focus on previous week)
- Connect UA spend to performance for new users
- Alert system for new users
- FTUE mini game performance
