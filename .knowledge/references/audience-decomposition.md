# MGO Audience Decomposition Framework

How DAU and WAU are broken down for executive reporting. This is the standard
framework used in Weekly KPI meetings and Season readouts.

---

## Top-Level Decomposition

**WAU** (Weekly Active Users) is the north star audience metric. It splits
by tenure into two cohorts, each with distinct inflow sources:

```
WAU = WAU D30- + WAU D30+
```

- **WAU D30-** — players with tenure < 30 days (new, early lifecycle)
- **WAU D30+** — players with tenure >= 30 days (established base)

WAU D30+ receives the most exec attention because it represents the
established, monetizable base. But WAU D30- is where the acquisition
pipeline lives — ignoring it means missing the funnel entirely.

### Inflow sources by tenure cohort

```
WAU D30-  ← Funnel (New Users)              — this is where new installs live
            Reactivations (D30- returning)   — rare but possible

WAU D30+  ← Returning Players               — carried over from prior week/season
            Reactivations (D30+)             — lapsed players coming back
            Graduation from D30-             — funnel survivors aging past 30 days
```

The "WAU From Funnel D30+" metric tracked in weekly meetings represents
funnel players who have graduated — survived past 30 days. This is a lagging
indicator of funnel health; the leading indicators are New DAU and D7
Retention, which live in the D30- cohort.

---

## WAU D30- Components

### Funnel (New Users)

**Definition:** Players who install during the season. For most of their
early lifecycle they live in the D30- cohort. Only after surviving 30 days
do they graduate into D30+ and appear in "WAU From Funnel D30+".

**Leading indicators (D30-):**
- **New DAU** — raw daily new user count (acquisition volume)
- **D7 Retention** — 7-day retention of new installs (early quality signal)

**Lagging indicator (D30+):**
- **WAU From Funnel D30+** — new installs that survived to 30+ days

**Targets:**
- WAU From Funnel target = **10% increase from a baseline of ~120K**

**Typical behavior:** Funnel volume trends down over time (baseline erosion).
Currently ~15% lower than Cozy Comforts / Bon Appetit seasons. D7 retention
has been ~6% higher despite lower volume, suggesting better-quality but
fewer installs.

---

## WAU D30+ Components

### 1. Returning Players

**Definition:** Players who experienced the previous season and made it to
the end. They are the "carried-over" audience from the prior period.

**Sub-segmentation by monetization tier:**
- **Loyal Payers (LPs)** — highest-value segment
- **Regular Customers (RCs)** — regular purchasers
- **Regulars** — 7-day active (F2P regulars)
- **Casual** — 5-6 day active
- **Occasional** — 1-4 day active

**Key metrics:**
- WAU D30+ Return Rates (%) — by segment
- Momentum Rates — by playday bucket (1, 2-4, 5-6, 7 playdays)
- Weekly Regulars D30+ — absolute count + Delta WoW 4 Week Rolling
- Weekly Regular Customers D30+ — absolute + % of RCs over Regulars
- % of Converted over RCs D30+ — conversion rate within RCs

**Typical behavior:** Returning player volume is the largest WAU D30+
component and the main driver of WoW changes. Return rates fluctuate with
event type (social events like Coop boost return rates; solo events see dips).

### 2. Reactivations

**Definition:** Players who reactivate during the season (were previously
inactive, came back). Primarily D30+ since they are older accounts returning.

**Sub-types:**
- **Reactivated WAU D30+** — reactivated players with 30+ day tenure
- **Returning Reactivations** — players who reactivated in a prior period
  and continue returning (a second-order retention metric)

**Targets:**
- Reactivated WAU target = **13.5% of 12-week rolling average D30+ WAU**

**Key metrics:**
- Reactivated WAU D30+ (absolute, vs. target)
- D7 Retention after reactivation
- Mix vs. Retention analysis — decompose retention changes into
  compositional shifts vs. true behavioral change

**Typical behavior:** Reactivation volume spikes with branded events
(Hello Kitty, Harry Potter) and season starts. It has been holding
healthier than funnel inflow in recent periods.

### 3. Funnel Graduates

**Definition:** Players from the funnel (new installs) who survived past
30 days and graduated into the D30+ cohort. This is the pipeline from
WAU D30- feeding into WAU D30+.

**Key metric:**
- WAU From Funnel D30+ — the graduation volume

This is a **lagging** indicator. By the time it moves, the root cause
(New DAU volume or early retention) happened 30+ days ago.

---

## Audience Health Metrics

### Return Rates

**WAU D30+ Return Rates (%)** — the % of last week's WAU who returned this
week. Broken out by:
- Overall
- Returning players
- Reactivated players

Return rates are sensitive to event type: social events (Coop, Racers) lift
return rates; solo events (Dig, Boutique) see lower rates.

### Momentum Rates

**Momentum Rate** = % of returning players who maintained or increased their
number of play-days, week over week. Broken out by playday bucket:

| Bucket | Definition | What it measures |
|--------|-----------|------------------|
| 1 playday | Played 1 day last week | Lightest touch — are they escalating? |
| 2-4 playdays | Played 2-4 days | Mid-tier engagement trajectory |
| 5-6 playdays | Played 5-6 days | Almost-regulars — are they converting? |
| 7 playdays | Played all 7 days (Regulars) | Are regulars staying regular? |

Momentum rate for Regulars (7 playdays) behaves differently from other
buckets — it can only go down or stay, making it a churn signal.

### Delta WoW 4 Week Rolling

A smoothed trend metric: average WoW delta for the past 4 weeks. For
instance, -0.4% means on average the audience lost 0.4% each week over the
past 4 weeks. Used for WAU D30+ and Weekly Regulars D30+ to show trajectory
direction.

---

## Revenue Decomposition

**Avg Daily Net Revenue** is decomposed multiplicatively:

```
Avg Daily Net Rev = DAU × CR × Payments per DAP × GrossRev/Purchase × Franchise Net Rev%
```

Where:
- **DAU** — daily active users (D30+)
- **CR** — conversion rate (% of DAU who pay)
- **Payments per DAP** — purchase frequency per daily active payer
- **GrossRev/Purchase** — average selling price (ASP)
- **Franchise Net Rev%** — net revenue margin (platform fees, D2C benefit)

This allows bridge analysis between seasons to isolate whether changes come
from audience size, conversion, frequency, pricing, or margin.

---

## Season-Level Framework

The Seasons Measuring Framework applies the same decomposition at a longer
time horizon. Core principles:

### Principle 1: Audience Groups
Each season's audience = Returning Players + New Users + Reactivations
(same as weekly, but measured over the full season duration)

### Principle 2: Retention Focus
Priority order: **Retention > Engagement > Monetization**
A season is healthy if it retains players, regardless of short-term
monetization fluctuations.

### Season-over-Season Comparison
Seasons are compared at the same day count (e.g., "First 39 Days") to
normalize for duration. Key context includes:
- Solo vs. Social minigame day mix (e.g., "22d / 17d Solo/Social")
- Economy change breakpoints
- IP vs. Non-IP season effects

---

## Common Confounds

When interpreting audience metrics, watch for:

1. **Event type mix** — Social events (Coop, Racers) boost return rates
   and momentum; solo events see dips. Don't compare a solo week to a
   social week without noting this.

2. **IP vs. Non-IP seasons** — IP seasons (Harry Potter, Hello Kitty)
   inflate reactivations and LP spending. Following non-IP season often
   looks like a decline but may be reversion to baseline.

3. **Progressive offers** — Running during benchmarks but not the target
   period inflates the comparison. Always check offer calendar.

4. **Suspicious users** — All audience metrics should exclude suspicious
   users (susp.users). D30+ filter also excludes very new accounts.

5. **Economy changes** — Jun 2025 VfM increase is a structural breakpoint.
   Pre/post comparisons must account for this.

---

## Source Files

Reference decks:
- `.knowledge/references/weekly-updates/` — 5 weekly KPI meeting decks (Mar-Apr 2026)
