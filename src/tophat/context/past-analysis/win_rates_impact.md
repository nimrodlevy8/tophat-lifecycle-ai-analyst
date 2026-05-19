# Win Rates Impact on New & Reactivated Users

## Questions Investigated

1. How does the first minigame exposed to players impact long-term KPIs?
2. How long does it take players to achieve their first win?
3. How does the first win affect long-term KPIs?
4. How do different minigames compare as "first win"?
5. How does winning affect reactivation retention?

---

## Key Findings — New Users

### First Minigame Exposure
- Prize Drop is the most common first minigame (most frequently run)
- 82% of users experience their first minigame before D7
- **Solo minigames produce better long-term retention than Social:**
  - D30 Retention by first minigame type:
    - Generic day: 30%
    - Coop: 30.7%
    - Racers: 31.6%
    - Dig: 36.2%
    - Juggle: 37.3%
    - Prize Drop: 38.2%
  - Hypotheses: friends requirement in social, solo easier to understand

### First Win Timing
- Only 50% of first wins happen by D30
- 90% of first wins happen by D90
- By D30: only 19% of DAU have won (9% excluding Racers)
- By D90: only 52% of DAU have won (31% excluding Racers)
- Racers is most common first win (by design, 25% win rate)

### Impact of First Win on 30d Return Rate (by minigame)
| Minigame | Win Impact on 30d Return Rate |
|----------|------------------------------|
| Coop | +13% higher |
| Dig | +8% higher |
| Prize Drop | +5% higher |
| Racers | No impact (same for winners/non-winners) |

**Methodology:** Segment by Avg Daily Roll Sink to control for engagement bias, compare winners vs non-winners within each segment, average across segments.

### Conclusion
- Winning minigames where Grand Prize includes high amounts of Rolls has better impact on retention
- Racers wins don't help because winning is too easy/common (25% win rate by design)

---

## Key Findings — Reactivated Users

### First Minigame After Reactivation
- Reactivated users more likely to have Coop first (20% vs 16% for new users)
- Late-reactivated users higher share with Jugglesort (novelty effect)
- Higher tenure users reactivate more with Coop and Racers
- Social minigames show higher % of users reactivating on minigame start date (they drive reactivation)
- Completion rates are low except Tycoon Racers and Adventures (by design)
- Rich Return Reward claimers had slightly higher completion rates

### Win Rates
- By D30: ~22% of reactivated users have won (9% excluding Racers)
- By D90: ~45% have won (25% excluding Racers)

### Impact of First Win on 30d Return Rate (by minigame)
| Minigame | Win Impact on D30 Return Rate | Notes |
|----------|------------------------------|-------|
| Dig | +21% higher | Winners show lift from D1 onwards |
| Coop | +12% higher | Similar D14, recovery D14→D30 for winners |
| Prize Drop | +10% higher | Winners show lift from D1 onwards |
| Racers | No impact | Non-winners actually retain better through D7 ("burn-out" effect) |

---

## Recommendations

### New Users
- Allow new users to win earlier (via FTUE minigames or LiveOps segmentation)
- FTUE minigame Grand Prize should include high amounts of Rolls (biggest retention driver)
- Prioritize solo minigame exposure over social for first experience

### Reactivated Users
- Increase opportunities to win early post-reactivation (>50% never win in 90 days)
- Adjust RTUE experience to help users build early win momentum
- Dig and Coop wins are highest-impact for retention — prioritize these

---

## Methodology Notes
- Controlled for engagement bias by segmenting on Avg Daily Roll Sink
- Compared post-minigame Return Rates within engagement segments
- Averaged across Roll Sink segments to get unbiased win impact
