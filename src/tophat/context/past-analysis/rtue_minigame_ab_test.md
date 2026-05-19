# RTUE Minigame AB Test

**Date:** May 2025
**Analyst:** Kelly Raas

## Executive Summary

**The RTUE Minigame significantly improved early Reactivation Retention (D1, D3, D7).** Results statistically significant with large effect sizes, no major downsides observed.

**Verdict:** Roll out WWL.

## Feature Overview
- When a lapsed player returns → assigned tailored solo minigame ("Dig")
- Main LiveOps calendar muted during RTUE period
- Players reintegrated with next scheduled minigame after RTUE ends

**Target:** Reactivated users inactive ≥21 days, board level ≥5

**Mechanics:**
- Only solo minigames muted/replaced; Social (Coop) only muted on last day
- Dynamic duration configs: D1 (10 levels), D2 (15 levels), D3 (20 levels)
- Currency sourcing via Custom Milestone + Quick Wins
- 21-day cooldown between RTUE triggers

## Test Setup
- **Countries:** GB, FR, IT, DE, CA
- **Split:** 50/50 via Player Journey
- **Control:** Default LiveOps calendar + Milestone
- **Variant:** RTUE Dig Minigame + RTUE Milestone
- **Start:** May 9, 2025 (May 9 excluded due to Player Journey issue)
- **Valid treatment days:** 12 (Coop overlap days excluded)
- **IP Integration:** Star Wars theming

## Results

| Metric | Control | Variant | Uplift | p-value | Sig? |
|--------|---------|---------|--------|---------|------|
| D1 Retention | 30.8% (n=91,941) | 36.7% (n=55,851) | +19.3% | <0.001 | Yes |
| D3 Retention | 21.3% (n=76,486) | 25.9% (n=43,145) | +22.0% | <0.001 | Yes |
| D7 Retention | 19.1% (n=43,929) | 22.3% (n=28,703) | +16.1% | <0.001 | Yes |

## Progression Comparison
| Config | Levels | Participation | Completion |
|--------|--------|--------------|------------|
| RTUE D1 | 10 | 76.3% | 35.8% |
| RTUE D2 | 15 | 77.4% | 26.8% |
| RTUE D3 | 20 | 81.3% | 21.7% |
| Tatooine Treasures (regular) | 20 | 94.7% (DAU) | 2.7% |
| Cash Treasures (regular) | 12 | 93.1% (DAU) | 5.1% |
| Roll Treasures (regular) | 12 | 91.5% (DAU) | 9.5% |

RTUE completion rates ~5x higher than regular Dig events (easier configs + tailored experience).

## Caveats
- Only 12 valid treatment days (Coop overlap)
- D7 based on only 5 reactivation days
- Not all minigame types covered in test period
- Generalizability across full LiveOps calendar limited but no major deviations expected

## Next Steps (at time of test)
- WWL with 80/20 split (80% with IP integration, 20% without) to measure IP impact
- Continue monitoring retention + monetization for long-term value
