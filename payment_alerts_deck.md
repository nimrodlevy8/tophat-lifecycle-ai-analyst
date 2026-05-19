# Monopoly GO! Payment & Economy Alert System
## Proposal Deck — Slide-by-Slide Content

**Point of Contact:** Nimrod Levy
**Date:** April 2026

---

## SLIDE 1 — Title Slide
[Use purple gradient background with Monopoly GO! logo]

**Title:** Payment & Economy Alert System
**Subtitle:** Proactive Revenue Protection for Monopoly GO!
**Point of Contact:** Nimrod Levy
**Date:** April 2026

---

## SLIDE 2 — Executive Summary: Why We Need Automated Alerts

[White background, Jost headline, Quicksand body]

### The Core Insight

**We are currently flying blind on payment and economy health.** When issues occur — broken app versions, store outages, economy misconfigurations — we find out hours or days later, after revenue has already been lost.

An analysis of the last two months of payment and transaction data reveals that **multiple incidents went undetected for extended periods**, each representing significant revenue at risk:

- **Feb 5:** An ApiError spike caused 60,000 failed payments in a single day — a **600x increase** over normal levels
- **Mar 1:** A ChanceCard reward misconfiguration flooded **4.8B extra rolls** into the economy in one day (5x normal)
- **Android API-29 emulator traffic:** 8,000–60,000 daily payment attempts with **0% success rate**, running undetected for months

**Estimated revenue at risk without alerts: $1M–$5M per incident, with potential for multi-day compounding.**

We propose a **39-alert system** across three categories — Operational, Revenue, and Behavioral — designed to catch these issues within hours, not days.

---

## SLIDE 3 — Divider Slide
[Purple gradient background]

**The Problem: What We're Missing Today**

---

## SLIDE 4 — Limitations: No Systematic Payment Monitoring

[White background, two-column layout]

### What Isn't Working

**Left column:**

**No real-time anomaly detection on payments**
Today, payment health is monitored manually or through dashboards that require someone to actively look. When a store outage hits at 2 AM or an app version ships with broken payment flows, no one is notified until user complaints surface.

**Economy changes go unnoticed**
When a rolls reward source is misconfigured (like the ChanceCard 5x spike on Mar 1), the economy absorbs billions of excess currency before anyone notices. This devalues purchased rolls and erodes monetization.

**Right column:**

**No cross-dimensional visibility**
Issues that only affect one platform, one country, one app version, or one currency are invisible at the aggregate level. A 0% success rate on a specific Android OS version ran for months undetected because total numbers looked acceptable.

**Reactive, not proactive**
By the time an issue is identified through manual review, the damage — lost revenue, inflated economy, degraded user experience — has already compounded.

---

## SLIDE 5 — The Revenue at Stake: Real Incidents from the Last 2 Months

[White background, big numbers on right side]

### Header: Every day without alerts is revenue left on the table

**Feb 5 — ApiError Spike**
60,000 API errors in one day (vs. ~100 normal). Payment success rate dropped to 42.6%. Estimated lost transactions: ~50,000 successful payments.
**$500K+** Estimated Revenue Impact

**Feb 9–10 — PurchasingDisabled Surge**
PurchasingDisabled errors spiked to 111,000 (vs. ~30,000 normal). Success rate cratered to 37.6%. Two full days before stabilizing.
**$2M+** Estimated Revenue Impact (2-day)

**Mar 9 — Hourly Volume Cliff**
At hour 17 UTC, payment volume dropped 72% mid-peak (111K to 31K). ARPU crashed to $14.82 (vs. $29 average). Revenue that day: $3.4M vs. $11M the day before.
**$7M+** Single-Day Revenue Gap

---

## SLIDE 6 — Economy Impact: The Hidden Cost of Late Detection

[White background, text + big number layout]

### Header: Payment failures are visible. Economy leaks are silent.

**Mar 1 — ChanceCard Reward Misconfiguration**
ChanceCard/board quantity spiked to **5.78 billion rolls** in one day — **5x the normal ~1 billion**. Transaction count barely changed, meaning each card was paying out 5x the intended reward.

Net economy impact: **+3.45 billion excess rolls injected** (sink ratio dropped to 87.6% vs. typical 97-100%).

**Why this matters:**
- Excess free rolls **devalue purchased rolls**, reducing willingness to pay
- Economy inflation takes weeks to correct through rebalancing
- **Every billion excess rolls = ~$250K–$500K in deferred revenue erosion** through reduced purchase pressure

**$1M+** Estimated Deferred Revenue Erosion

---

## SLIDE 7 — Divider Slide
[Purple gradient background]

**The Solution: A 39-Alert System**

---

## SLIDE 8 — Overview: Three Pillars of Protection

[White background, three textbox cards]

### OPERATIONAL / TECHNICAL — 15 Alerts
*Subtitle: Catch system failures in real-time*

Detects infrastructure issues, store outages, app version bugs, and OS-specific failures. Monitors success rates, error spikes, hourly volume cliffs, and platform divergences. Catches issues like the Feb 5 ApiError spike and the Android emulator 0%-success traffic.

### REVENUE / FINANCIAL — 12 Alerts
*Subtitle: Protect the top line*

Guards against revenue anomalies, ARPU shifts, pricing misconfigurations, FX rate changes, VAT errors, and whale revenue drops. Monitors each store (Apple, Google, Playgami, Flexion) and currency independently. Would have caught the Mar 9 $7M revenue gap same-day.

### USER / BEHAVIORAL — 12 Alerts
*Subtitle: Detect engagement shifts early*

Tracks conversion rates, unique payer counts, country-level collapses, language-specific degradation, and user behavior patterns. Surfaces issues like China's 1.13% success rate anomaly and the Spanish-language 19% success rate.

---

## SLIDE 9 — Operational Alerts: What We Monitor

[White background, full-width text]

### Operational / Technical Alerts — 15 Total

**Infrastructure & Store Health**
- Success rate drop (excl. UserCancelled) — hourly, vs. 7-day same-hour average
- ApiError spike — >1,000/hour or >3x average (would have caught Feb 5)
- PurchasingDisabled surge — >2x rolling 7-day average
- MalformedReceipt spike — >100/day absolute (caught the Mar 7–16 bad build)
- Timeout rate increase — >2x trailing average
- Network/Billing infrastructure combined alert
- Hourly volume cliff — >60% hour-over-hour drop during peak (13–19 UTC)
- Web/Playgami success rate drop — <99% (your infrastructure, not store-dependent)

**App & Device Health**
- OS version zero success rate — >500 attempts with 0% (catches emulator/fraud traffic)
- OS version success rate regression — >20% relative drop
- App version success rate gap — >15pp between versions on same platform
- New store appearance — flags unknown store values

**Cross-Dimensional**
- Platform success rate divergence — one platform drops while others hold
- Language-specific success rate drop — vs. each language's own baseline
- Flexion store volatility — >30% drop in its own success rate

---

## SLIDE 10 — Revenue Alerts: What We Protect

[White background, full-width text]

### Revenue / Financial Alerts — 12 Total

**Revenue Volume**
- Daily revenue anomaly — >30% below same-weekday 4-week average
- Web/Playgami revenue drop — >25% below 7-day average (pure demand signal)
- Whale revenue drop ($100+ txns) — >40% below average
- Currency-specific revenue drop — >40% for top-10 currencies by revenue

**Pricing & Monetization**
- ARPU shift — >25% deviation from 7-day average
- Avg transaction value shift per platform — >30% change
- Price tier distribution shift — any tier's share changes >50%
- Platform revenue mix shift — >10pp change in any store's share

**Financial Integrity**
- FX rate sudden shift — >3% day-over-day for top-15 currencies
- VAT rate anomaly per country — >2pp shift (tax rates are fixed by law)
- amount_us vs. amount_us_old ratio drift — >0.1pp from 30-day average
- Store revenue share shift — >10pp in any store's daily share

---

## SLIDE 11 — Behavioral Alerts: What We Watch

[White background, full-width text]

### User / Behavioral Alerts — 12 Total

**Conversion & Engagement**
- Conversion rate drop — >15% below same-weekday average
- Unique payer count drop — >20% below expected
- Transactions per payer anomaly — outside 1.3–2.0 range
- Peak hour volume shift — >20% below expected during 13–19 UTC

**Geographic Health**
- Country-level success rate collapse — >50% drop for top-15 countries
- Country revenue disappearance — <10% of average for top-10 countries
- Low-success-rate language degradation — further drops in already-struggling markets

**Platform & Device**
- Store-specific user drop (Flexion) — <50% of 7-day average
- Android emulator/fraud detection — >2x increase in 0%-success traffic
- New users vs. returning payer ratio shift — >25% change
- Country-level FX arbitrage/pricing mismatch — USD value shifts with stable local prices
- Peak hour user volume shift — engagement pattern breakdowns

---

## SLIDE 12 — Divider Slide
[Orange/yellow gradient background with Mr. Monopoly]

**Before vs. After: Real Examples**

---

## SLIDE 13 — Application Example: Feb 5 ApiError Spike

[White background, two-column before/after layout with callout boxes]

### Before vs. After — The Feb 5 ApiError Incident

**WITHOUT ALERTS (What Actually Happened)**

ApiErrors spiked from ~100/day to **60,440** on Feb 5. Payment success rate dropped to **42.6%**.

- No automated notification was triggered
- The issue was likely identified through manual dashboard review or user complaints
- By the time it was addressed, **~50,000 successful payments were lost**
- Estimated revenue impact: **$500K–$1M**

**WITH ALERTS (What Would Have Happened)**

The **ApiError Spike alert** would have fired within the first hour, when hourly errors exceeded 1,000 (3x the threshold).

- Team notified at **hour 1** instead of hours/days later
- Investigation begins immediately, root cause identified
- If resolved within 2 hours: **~90% of lost revenue is recovered**
- Estimated savings: **$450K–$900K**

---

## SLIDE 14 — Application Example: ChanceCard Economy Leak

[White background, two-column before/after layout]

### Before vs. After — The Mar 1 Economy Misconfiguration

**WITHOUT ALERTS (What Actually Happened)**

ChanceCard/board qty per transaction jumped from ~80 to **~405** on Mar 1, injecting **4.8 billion extra rolls** into the economy.

- The sink ratio dropped to **87.6%** (vs. typical 97–100%)
- Net rolls surplus: **+3.45 billion** — the largest single-day injection in the 2-month window
- No alert was triggered; the misconfiguration may have persisted into subsequent days
- Economy inflation reduces purchase pressure for days/weeks afterward

**WITH ALERTS (What Would Have Happened)**

The **Avg Quantity Per Transaction Anomaly alert** would have flagged ChanceCard's 5x qty shift within the first daily check.

- Config error identified and rolled back within hours
- Excess rolls injected: reduced from **4.8B to ~500M** (before rollback)
- Economy remains balanced, purchase pressure preserved
- Estimated protected revenue: **$500K–$1M** in avoided deferred erosion

---

## SLIDE 15 — The Numbers: Revenue Protection Summary

[White background, big numbers with supporting text — 3 rows]

### Header: What this system is designed to protect

**$2.6M–$13M** Daily Revenue
Our daily revenue ranges from $2.6M (worst day) to $13M (best day). A single undetected incident during a peak day can erase millions.

**$374M** Two-Month Revenue (Feb–Mar 2026)
Across all platforms and stores. Even protecting 1% through faster incident detection = **$3.7M** in preserved revenue per two-month cycle.

**39** Automated Alerts
Covering operational health, revenue integrity, and user behavior — monitored continuously, alerting within hours instead of days.

---

## SLIDE 16 — The Scale of What We're Monitoring

[White background, 4 textbox cards in 2x2 grid]

### PAYMENTS
**~900K daily transactions**
Across Apple, Google, Playgami, and Flexion stores, spanning 230+ countries and 25+ currencies

### ECONOMY
**~1.2B daily rolls transactions**
56 billion rolls spent and 20+ billion earned daily through 30+ distinct reward and cost sources

### PLATFORMS
**4 stores, 10+ OS versions, 3+ app versions**
Each with its own success rate baseline, failure modes, and revenue characteristics

### GEOGRAPHIES
**232 countries, 25+ languages, 25+ currencies**
Each with distinct VAT rates, FX rates, success rates, and payment infrastructure reliability

---

## SLIDE 17 — Recommendations & Next Steps

[White background, Jost headline, structured list]

### What We Should Do

**Phase 1 — Critical Alerts (Week 1–2)**
Implement the top-5 highest-impact alerts first:
1. Daily revenue anomaly (>30% drop)
2. ApiError spike (>3x hourly average)
3. Hourly volume cliff (>60% drop during peak)
4. Web/Playgami success rate drop (<99%)
5. Avg quantity per transaction anomaly (economy)

**Phase 2 — Revenue Protection (Week 3–4)**
Add the remaining revenue and financial alerts:
- ARPU shifts, whale revenue drops, FX rate changes, VAT anomalies
- Platform and store-level revenue monitoring

**Phase 3 — Full Coverage (Week 5–6)**
Deploy all 39 alerts including behavioral and cross-dimensional monitoring:
- Country-level health, language segmentation, OS version tracking
- Economy sink ratio and event-source monitoring

**Delivery:**
- SQL queries running as scheduled BigQuery jobs
- Alerts delivered via Slack (#tophat_analytics_internal) and email
- Dashboard in Looker for real-time monitoring and drill-down

---

## SLIDE 18 — Traffic Light Status

[White background, Orange Hammer icon with status card]

### Analysis Maturity Status — Ongoing Investigation

**Orange Hammer**

**What this means:** We're building confidence in the analysis. The alert definitions and thresholds are based on 2 months of real data, but validation is still in progress.

**Why is this the case:** We've analyzed daily, hourly, and dimensional patterns across payments and economy transactions. We've identified anomalies and proposed thresholds. However, backtesting against known incidents and threshold tuning still need to be completed.

**What can you expect from us:** Implementation of Phase 1 alerts within 2 weeks, with iterative refinement based on false-positive rates and stakeholder feedback.

---

*Source Data: sys_payment and sys_gti_nodedup tables from dwh-prod-tophat.STD_tophat, build_type = 1, date range: Feb 1 – Apr 2, 2026*
