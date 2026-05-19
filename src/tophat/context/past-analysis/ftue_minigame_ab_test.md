# FTUE Minigame AB Test

**Date:** April 2026
**Analyst:** Kelly Raas

## Feature Overview
- First solo minigame for all new users (Plinko, easier config)
- Not scheduled in LiveOps calendar
- Dynamic duration adjusting to next minigame start
- Accompanied by custom milestone event
- Triggered at Board 4, temporarily replaces LiveOps minigames

## Executive Summary

**TLDR:** FTUE Minigame improved early engagement and progression but did NOT drive meaningful retention uplift.

- Significantly increased early board progression and playtime
- Retention impact limited to D1 (+1.2%), no significant lift at D3 or D7
- Drives more in-session engagement but not stronger return behavior

**Conclusion:** Improves early session depth and accelerates progression, but does not materially increase likelihood to return.

## Test Setup
- **Hypothesis:** Curated FTUE solo minigame at Board 4 will improve early engagement and D1-D7 retention
- **Control:** No FTUE Minigame (standard LiveOps)
- **Variant:** FTUE Minigame (Plinko, easier config) + FTUE Milestone event
- **Primary KPI:** D1/D3/D7 Retention (anchored at Board 4)

## Results

### Sessions & Playtime
| Metric | Control | Variant | Uplift |
|--------|---------|---------|--------|
| D1 Sessions | 8.3 | 8.4 | +0.45% |
| D7 Sessions | 20 | 20 | -0.27% |
| D1 Playtime | 156 min | 175 min | +12.41% |
| D3 Playtime | 230 min | 245 min | +6.88% |
| D7 Playtime | 316 min | 329 min | +4.16% |

**Insight:** Playtime increased significantly but sessions flat — more time per session, not more returns.

### Retention
| Metric | Control | Variant | Uplift | Sig? |
|--------|---------|---------|--------|------|
| D1 Retention | 69.7% | 70.6% | +1.21% | Yes (p<0.001) |
| D3 Retention | 54.8% | 55.2% | +0.66% | No |
| D7 Retention | 43.9% | 44.0% | +0.22% | No |

### Board Progression
- FTUE Minigame significantly improves early game progression
- Impact most pronounced at Board 4→5
- Faster progression driven by longer sessions

## Key Learnings

1. Progression lifts driven by session depth (playtime), not frequency (returns)
2. FTUE Minigame improves engagement but does not create sustained return motivation
3. **Does not validate prior assumption** that solo minigame first experience drives stronger retention
4. Retention impact appears driven by earlier exposure timing (Board 4 vs 5) rather than the FTUE Minigame itself
5. Retention only significant on solo minigame days — contrasts with earlier analysis

## Hypotheses for Limited Impact

1. **Design based on legacy behavior** — Game has evolved (tournaments, themes, diverse minigames); assumptions may not hold
2. **Lacks thematic pull** — UA leverages seasonal themes; FTUE is generic, not aligned with season/narrative
3. **Plinko not strong enough** — Historically lower-performing, optimized for 1-2 day filler events; extended to 3-5 days feels repetitive

## Recommendations
- Refresh concept with current LiveOps standards
- Introduce stronger thematic layer (seasonal/narrative)
- Test alternative minigame types or configs (higher-performing, more engaging for 3-5 day period)

## Appendix Notes
- FTUE Plinko: ~22-36% completion rate (vs 2.7-9.5% for regular Dig events)
- Short configs (1D) don't leave enough time for board progression before event expires
- Longer D4/D5 configs show weaker downstream retention (supports Plinko as short experience)
