# Skill: Plinko Event Analysis

## Trigger

Apply when analyzing **Plinko** (aka "Prize Drop") events in Monopoly GO!.
This includes questions about plinko drop patterns, reward distribution,
spending efficiency, or prize-drop-specific engagement.

---

## Plinko Event Structure

### What is a Plinko Event?

A **Plinko event** (branded as "Prize Drop" in-game) is a chance-based minigame
where players drop tokens/balls through a plinko board to win prizes. Players
spend event currency to drop, and prizes are distributed based on where the
ball lands.

### Key Dimensions

- Drop count / volume
- Prize distribution and expected value
- Spending patterns (burst vs steady)
- Completion of prize tiers/milestones
- Luck vs spending relationship

---

## Key Tables

| Table | Schema | Purpose |
|-------|--------|---------|
| `fac_intraday_minigame_snapshot_daily` | `dwh-prod-tophat.DM` | Daily snapshots per user per event |
| `d_minigame_user_attributes` | `dwh-prod-tophat.DM` | User attributes per event |
| `dim_intraday_live_minigames` | `dwh-prod-tophat.BIZ` | Event metadata |
| `f_minigame_continuous_engagement` | `dwh-prod-tophat.BIZ` | CE metric per user×event |

---

## Analysis Lenses

1. **Drop patterns** — Volume, timing, burst vs steady dropping behavior
2. **Revenue** — Spending per drop session, IAP conversion
3. **Prize efficiency** — Expected value analysis, reward distribution fairness
4. **Engagement** — CE patterns, when do players stop dropping
5. **Cross-event comparison** — Iteration performance, prize pool changes

---

## Key Findings Reference

(No dedicated Plinko analyses completed yet — scaffold ready for enrichment)

---

## Common Pitfalls

1. **RNG-heavy** — High variance in outcomes; use large samples for reliable metrics
2. **Prize Drop vs Plinko naming** — In code it's often 'prize_drop', in conversation people say 'plinko'
3. **Milestone vs individual drop** — Distinguish between drop-level and milestone-level analysis
4. **Cornerstone segment** — '5. Prize Drop Lovers' in cornerstone data refers to this minigame
