# FTUE Simplification — Login Methods Analysis

**Date:** Jan 21, 2026
**Team:** Lifecycle
**Analyst:** Kelly Raas
**PM:** Richa Manurkar

## Login Methods & Retention

### Android
| Login | % Users | D1 Retention | D3 Retention | D7 Retention |
|-------|---------|-------------|-------------|-------------|
| "Guest" | 78.7% | 13.8% | 8.0% | 4.9% |
| Facebook | 15.5% | 28.9% | 18.7% | 12.1% |
| Google | 4.2% | 74.6% | 62.1% | 43.3% |
| ScopelyID | 1.5% | 24.6% | 12.0% | 6.7% |
| **Total** | 100% | 18.9% | 12.0% | 7.7% |

**Key Insights:**
- 80% of Android users are Guests with poorest retention
- Facebook: 2x D1, 3x D7 retention vs Guests
- Google outlier: highest retention but small sample (4%) — possible bias from recovered/ghost accounts

### iOS
| Login | % Users | D1 Retention | D3 Retention | D7 Retention |
|-------|---------|-------------|-------------|-------------|
| iCloud | 49.51% | 19.7% | 13.6% | 9.0% |
| Apple | 32.34% | 37.3% | 28.0% | 18.9% |
| "Guest" | 8.87% | 19.3% | 11.1% | 6.8% |
| Facebook | 7.99% | 45.1% | 35.4% | 25.0% |
| ScopelyID | 1.29% | 32.1% | 18.1% | 10.5% |
| **Total** | 100% | 27.6% | 19.8% | 13.3% |

**Key Insights:**
- ~70% use Apple or iCloud
- "Apple" login significantly higher retention than "iCloud"
- Facebook highest retention (25% D7) but only 8% of users
- <3-5% of users switch login method by D7

## Second Chance Auth Popup

**Context:** Users who select "Play as Guest" see a "Are you sure?" popup.

### Conversion at Popup
- Android: 2.1% convert at popup (total 8% convert by end of day)
- iOS: 6.6% convert at popup (total 88% convert by end of day — mostly via iCloud at Startup)

**Key Insight:** Most conversions happen at next game Startup, not at the popup itself. The popup has low immediate conversion but eventual conversion is high on iOS.

## SQL Queries (Reference)

### Tables Used
- `dwh-prod-tophat.BIZ.v_f_user_standard_kpis` — user KPIs with login type
- `dwh-prod-tophat.BIZ.f_ftue` — FTUE flow events
- `dwh-prod-tophat.BIZ.d_user_suspicious_at_creation` — suspicious user filter
- `dwh-prod-tophat.STD_tophat.sys_connect` — connection/login events

### Key Patterns
- Login type from: `v_f_user_rpt.day_last_social_type`
- New users: `v_f_user_rpt.f_days_since_first_activity = 0 AND v_f_user_rpt.is_active`
- FTUE steps: `tutorial_module = 'home_authentication'`, `step_name = 'home_auth'` or `'home_second_chance_auth_popup'`
- Connection events: `event_source = 'client' AND action = 'Login'`
- Exclude suspicious: LEFT JOIN `d_user_suspicious_at_creation` WHERE user_id IS NULL
- Exclude account recovery: `JSON_EXTRACT(context,"$.placement") != 'AreYouSurePopup'` context check
