# New User Economy Analysis

## Hypothesis
Economy testing has not happened for new users. There is a potential lack of generosity needed to progress in first few sessions.

## Goal
Run different economy tunings to improve new user experience, similar to broader econ tests already completed.

## KPIs
- **Primary:** D1 / D3 / D7 Retention, Session Length, Sessions per User (D0-D7)
- **Guardrail:** ARPDAU (D1-D14), Conversion Rate for new users

---

## Product Questions

### 1. Session End Reasons
- When a new user ends a session, what is the primary reason?
- Are sessions ending due to OOR, OOC, or other economy constraints?
- In the last session before churn: what were roll balance and cash balance?

### 2. Out of Rolls (OOR) Frequency
- Frequency of OOR by board and DSFA
- When do users first experience OOR → relation to retention
- Is there a correlation between early OOR and lower retention?
- Do users churn because of early OOR?
- Post-OOR behavior: churn immediately, purchase, wait for regen, or end session?

### 3. Out of Cash (OOC) Timing
- When do users first experience OOC (by board and DSFA)?
- Does OOC have measurable impact on churn similar to OOR?
- Post-OOC behavior: churn immediately, purchase, roll dice, or end session?

### 4. Roll Balances & Retention
- Do roll balances impact retention? (day average, starting balance, end balance)
- Does higher/lower roll balance in early days correlate with DSFA & board retention?

### 5. RTP Curve
- How does RTP evolve by board and DSFA for new users?
- Are users with lower RTP in early boards more likely to churn?
- Is there a specific RTP threshold that predicts retention outcomes?

### 6. Platform Differences (iOS vs Android)
- iOS users get extra dice with Apple ID login — does this translate to higher retention?
- How long does the platform-based roll advantage persist?
- At what point do iOS and Android users behave similarly?

### 7. Regen Cap
- Does increasing regen cap improve retention?
- Do users play longer or return more frequently with higher cap?
- How often do users hit regen cap? Relationship to retention?

### 8. Regen Speed
- Do users with higher effective regen rates retain better?
- If not determinable from observational data → design A/B test

---

## Analysis Framework

### Roll Economy Balance & RTP
- Roll balance D1-D14 (variance by iOS/Android, Organic/Paid)
- RTP D1-D14 (variance by iOS/Android, Organic/Paid)
- RTP curve evolution
- Comparison vs intended economy design

### Economy Variance by Platform
- Platform-specific reward impact (Sign in with Apple)
- Duration of platform roll gap

### Roll Depletion
- Frequency of OOR by board (1-10)
- OOR cadence D1-D14
- First OOR timing (board, session)
- First OOC timing (board, session)
- Alignment with intended economy design

### Roll Regeneration
- Regen cap assessment D1-D14
- Frequency hitting regen cap by board and day
- Regen speed distribution by board
- Is early roll income (earned + regen) sufficient for D1-D3 progression?

### Post First Purchase
- Are we more generous after first purchase?
- How long after Starter Pack purchase does user hit OOR?

---

## Status
- Prior analysis: Funnel Health Opportunity Assessment (Nov 2025, Slides 16-22)
- Collaboration: Economy team (Shlomi Nezry, Amit Alon, Yanir Ashkenazi)
- Product owners: Richa Manurkar, Nikita Dave
