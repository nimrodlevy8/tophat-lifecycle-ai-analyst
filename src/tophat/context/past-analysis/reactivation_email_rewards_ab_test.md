# Engagement Engine - Reactivation Email Rewards AB Test

**Date:** Jul 11, 2025
**Team:** Lifecycle / CRM / Engagement Engine
**Analyst:** Kelly Raas
**Stakeholders:** Andrea Atrio, Nikita Dave

## Hypothesis
More generous email rewards will drive the 2M churned email subscribers to reactivate (currently: 50 rolls 1x/month to users inactive ≥14 days).

## Test Design
- **Launch:** Jun 23, 2025
- **Population:** DSI ≥ 30 days, Last Active ≥ 14 days
- **Split:** 50/50 (~1M per group)
- **Control:** Default 50 Rolls
- **Variant:** Tiered rewards by LTV:
  - $0 LTV: 200 rolls + 4 star pack + sticker boom (20m)
  - $0 < LTV ≤ $250: 500 rolls + 5 star pack + sticker boom (20m)
  - $250+ LTV: 1000 rolls + 5 star pack + 4 star pack + sticker boom (20m)

## Results — Overall

### CRM Funnel
| Metric | Control | Variant | Uplift | Sig? |
|--------|---------|---------|--------|------|
| Email Open Rate | 19.16% | 19.79% | +3.19% | Yes |
| CTR (per Sent) | 1.00% | 1.97% | +95.72% | Yes |
| CTR (per Open) | 5.24% | 9.94% | +95.72% | Yes |
| App Open Rate | 1.27% | 1.96% | +53.72% | Yes |

### Dx Active Users
| Metric | Control | Variant | Uplift | Sig? |
|--------|---------|---------|--------|------|
| D1 Active | 0.93% | 1.29% | +38.36% | Yes |
| D3 Active | 1.04% | 1.22% | +17.19% | Yes |
| D7 Active | 1.58% | 1.74% | +9.74% | Yes |
| D14 Active | 2.60% | 2.73% | +4.79% | Yes |

### Playtime per Active User
| Metric | Control | Variant | Uplift | Sig? |
|--------|---------|---------|--------|------|
| D1 | 26.4 min | 27.7 min | +4.84% | Yes |
| D7 | 31.6 min | 32.5 min | +2.94% | Yes |
| D14 | 38.0 min | 39.2 min | +3.20% | Yes |

### Dx Conversion Rate
| Metric | Control | Variant | Uplift | Sig? |
|--------|---------|---------|--------|------|
| D1 | 0.01% | 0.02% | +71.75% | Yes |
| D7 | 0.05% | 0.07% | +45.72% | Yes |
| D14 | 0.21% | 0.25% | +18.13% | Yes |

## Results — By LTV Segment

### App Open Rate (Reactivation)
| Segment | Control | Variant | Uplift | Sig? |
|---------|---------|---------|--------|------|
| LT NPU ($0) | 1.04% | 1.24% | +19.34% | Yes |
| LTV <250 | 1.51% | 2.38% | +57.43% | Yes |
| LTV 250+ | 1.65% | 3.99% | +141.17% | Yes |

### CTR per Email Sent
| Segment | Control | Variant | Uplift | Sig? |
|---------|---------|---------|--------|------|
| LT NPU | 1.03% | 1.42% | +37.72% | Yes |
| LTV <250 | 0.94% | 2.13% | +126.30% | Yes |
| LTV 250+ | 1.07% | 3.96% | +270.39% | Yes |

### D1 Active Users by Segment
| Segment | Control | Variant | Uplift | Sig? |
|---------|---------|---------|--------|------|
| LT NPU | 0.75% | 0.87% | +15.97% | Yes |
| LTV <250 | 1.11% | 1.54% | +39.11% | Yes |
| LTV 250+ | 1.22% | 2.43% | +98.38% | Yes |

### D14 Conversion by Segment
| Segment | Control | Variant | Uplift | Sig? |
|---------|---------|---------|--------|------|
| LT NPU | 0.0004% | 0.0004% | +10.45% | No |
| LTV <250 | 0.0021% | 0.0023% | +7.91% | No |
| LTV 250+ | 0.0103% | 0.0129% | +24.93% | Yes |

## Key Takeaways

1. **LTV 250+ responded best** across all funnel stages — strong sig uplift in engagement AND conversion
2. **LTV <250** had significant D3/D7 conversion lift but D14 not significant
3. **LT NPUs** showed activity uplift but no conversion gains (low base monetization)
4. Quality of engagement improved: variant users spent more time in-game
5. Uplifts significant despite low base rates thanks to ~1M sample per group
