# 2026 Lifecycle Roadmap

## Strategy

**RENEW AND SIMPLIFY THE NEW USER EXPERIENCE**
- Holistic review of the new user experience
- Focus on D30+ retention by solving D1-D14 drop-offs
- 63% of inactive players churned before board 5
- Major contribution from D1

**CONTINUE FOCUS ON REACTIVATIONS**
- Rich Returns Release improved Reactivated WAU Return Rates by +1.9 p.p (+11% growth)
- Better returning experiences can benefit all stages: D7 churners, occasionals, casuals

---

## Features In Progress

### 1. Home Authentication Improvement

**Problem:** ~14% user drop-off at Home Auth — one of the largest single drop points before any gameplay.
- iOS: -3.4% drop at home_auth screen
- Android: -18.5% drop at home_auth screen

**Solution:**
- Remove delay in "Play As Guest"
- Include Google Play connect option
- Make auth feel optional, never block player from starting

**KPIs:**
- Primary: Drop-off rate at Home Auth, % users reaching FTUE
- Secondary: Time to enter first gameplay, FTUE completion rate, D1 retention (guardrail)

---

### 2. FTUE Tutorial Simplification

**Problem:** -34% iOS users and -25% absolute drop during FTUE tutorial. ~3min duration with text-heavy screens.

**FTUE Definition:** Starts after user auth, ends at first independent roll (narrative_onboarding → bank_heist).

**Solution — Flow Reorder:**
- OLD: Landmark → Token Selection → Rolling → Shutdown → Shield → Bank Heist
- NEW: Board intro → Token Selection + Rolling → Landmark → Shutdown → Shield → Bank Heist
- 26 steps vs 31 current steps to reach "free rolling" on BL1

**Changes:**
- Config ability to skip/remove intro video
- Remove unnecessary storyline content
- Shorten/simplify text, combine tutorial screens
- Reorder to introduce token selection and rolling before landmark

**KPIs:**
- Primary: FTUE Completion Rate, D1 Retention, Session 1→2 Retention
- Secondary: Early Board Drop-off (Boards 1-2), Time to Complete FTUE, First-time Conversion (guardrail)

---

### 3. FTUE Unlock/Lock (Feature Pacing)

**Problem:** Board 1 has 52.3% drop-off with core loop tutorials all at once.

**Board Progression Design:**
| Board | Drop-off | Unlocks |
|-------|----------|---------|
| 1 | 52.3% | Core Loop: Landmarks, Shutdowns, Shields, Bank Heist, Networth |
| 2 | 28.5% | Supporting: Albums, Offers, 4 Flash Events, Quick Wins, Daily Treats |
| 3 | 8.3% | Tentpole Events: Milestones, More Offers, 2 Flash Events |
| 4 | 12.2% | Social: Tournaments, Social Minigames, Social Flash Events |
| 5 | 9.7% | Solo Minigames, High Value Flash Events |

**V1 Feature: Community Chest Move**
- Currently unlocked at Board 2, but 84% of users have NO friends at Board 2
- Moving CC unlock to Board 6 (where ~17% have 5+ friends)
- CC requires 5 friends to unlock, 3 partners to engage

**KPIs:**
- Primary: D1-D7 retention, Board 1→Board 10 retention
- Guardrail: Album interaction, Friend invites, %Users with 1-6+ friends

---

### 4. New User Monetisation

**Current State:**
- First monetisation touchpoint is Out of Cash (OOC) at ~8 minutes for $1.99
- Starter Pack surfaces within OOR loop (mostly Board 2)
- Up to D7, Starter Pack is most converted SKU
- Most first purchases on earlier stages/low seniority

**Starter Pack Journey:**
| Day | Price | Pack | Roll Value | Total Value |
|-----|-------|------|-----------|-------------|
| D0 | $2.99 | 525 rolls + cash (cap 2) | 130% | 165% |
| D1 | $2.99 | 675 rolls + cash (cap 2) | 200% | 235% |
| D2-3 | $2.99 | 950 rolls (cap 1) | 325% | 325% |
| D4 | $1.99 | 525 rolls + cash + 2 star pack (cap 1) | 265% | 305% |
| D5-6 | $1.99 | 600 rolls + cash + 2 star pack (cap 1) | 325% | 365% |

**Rolls Value Hierarchy (Non-Payer):**
- Progressive Offer: 500%
- Piggy Bank: 350%
- Seasonal Sale: 180-250%
- Starter Pack: 130-325%
- FTPB/OOR: 200-220%
- Decoy/Buy all: 160-180%
- Baseline/Store Bundles: 50-150%
- Store: 0%

**Proposed Changes:**
- No Board 1 monetisation (handled by economy)
- Surface Starter Pack instead of OOC for initial boards
- Remove OOC offers during SP duration (D0-D6)
- SP trigger: OOR → [SP → OOR → Invite Friends], OOC → don't show, Login
- Make SP one-time purchasable (currently cap 2, ~10% reach 2nd cap)
- Make SP visible (sticky) in Store
- Fix incorrect OOR offers (currently showing $7.99 instead of $1.99-$3.99)
- Introduce Endless/Decoy offers earlier (currently D7+, Royal Match does it in first village)

**KPIs:**
- Primary: D1-D7 Retention, New User Conversion Rate, New User ARPU
- Secondary: Board retention, Time to second purchase

---

### 5. New User Economy

**Problem:** New user economy has not been evaluated. ~15% of users run out of rolls in BL1. Users reach OOC in BL1.

**Approach:**
1. Assess behavior: Roll balance & RTP, platform variance, roll depletion timing, roll regen
2. Identify friction points
3. Design and launch economy A/B tests

**KPIs:**
- Primary: D1/D3/D7 Retention, Playtime, Sessions per User (D0-D7)
- Guardrail: ARPU (D1-D14), Conversion Rate

---

### 6. Mini Game Duration Adjustment

**Problem:** Current FTUE/RTUE minigames use dynamic tech for duration — complex, hard to scale, risk of misconfiguration.

**Solution:** Move duration logic from dynamic tech to configuration. Test config-level changes.

**KPIs:**
- North Star: D1-D30 Retention (New + Reactivation)
- Primary: Early Retention (D1/D3/D7), Minigame engagement rate

---

### 7. Forcefield (Reactivation)

**Problem:** Current Rich Return blocks specific systems requiring constant coordination. Can miss cases (first-time exposure to Leagues, Tycoon Club, Album turnover).

**Prerequisite:** Tech investigation on React start-up times for reactivated users.

**Solution:** Shift from "what to block" → "block all, except" framework.

**KPIs:**
- North Star: D1-D30 Retention (Reactivation)
- Primary: Load time, Time to first roll, Reactivation Retention (D0-D1), D0 Playtime

---

### 8. Daily Treats Segmentability

**Problem:** Same experience for all users. Limits relevance for New and Reactivated users.

**Solution:** Segment-based configuration (title, rewards, duration) for New and Reactivated users. Shorter calendar for habit formation.

**KPIs:**
- North Star: D1-D30 Retention (New + Reactivation)
- Primary: Early Retention (D1/D3/D7), Daily Treats claim rate

---

## Backlog

| Feature | Goal | Primary KPI |
|---------|------|-------------|
| New User Album Unlock | Progressive collection unlock to reduce overwhelm | D1-D30 Retention, Album engagement |
| Onboarding Theming | Theme FTUE based on acquisition source/IP ads | Early retention |
| Album Intro Video | Show to right users at right time | Retention, Album engagement |
| Co-Op Bots for New Users | Bots for users with low friend counts (71% have 0 friends at BL4) | D1-D30 Retention, Co-Op engagement |
| Constant Starter Pack | Sticky SP always available in shop | FTD Conversion Rate |
| Friend-Fueled Reactivation | Active players invite churned friends with rewards | Reactivated users, Success % |
| OOR & OOC Behaviours | Fix BL1 monetisation experience | Early retention |
| Invite Friends Flow Polish | Shorter milestones, better reward communication | Invites per user, %Users with 1+ friend |

---

## Key Data Points

- 63% of inactive players churned before Board 5
- Board 1 drop-off: 52.3%
- Board 2 drop-off: 28.5%
- Home Auth drop: 14% (3.4% iOS, 18.5% Android)
- FTUE drop: 34% iOS, 25% Android
- 84% of Board 2 users have NO friends
- ~15% of users run out of rolls in BL1
- Rich Returns improved Reactivated WAU by +1.9pp (+11%)
- $1.99 FTPB is second most converting offer D0-D3
- ~10% of users reach SP 2nd cap
