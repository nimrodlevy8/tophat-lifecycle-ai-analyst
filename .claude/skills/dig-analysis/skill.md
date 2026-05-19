# Skill: Dig Event Analysis

## Trigger

Apply when analyzing **Dig** events in Monopoly GO!. This includes
questions about dig progression, dig rewards, excavation patterns,
or dig-specific engagement metrics.

---

## Dig Event Structure

### What is a Dig Event?

A **Dig event** is a solo excavation minigame where players spend rolls to dig
through layers/tiles and uncover rewards. Players progress through a grid or
layered structure.

### Key Dimensions

- Dig depth / layer progression
- Tile/reward discovery patterns
- Spending per dig layer
- Completion rates
- Reward value vs cost efficiency

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

1. **Progression** — Layer/depth completion rates, where players stop digging
2. **Revenue** — Spending per layer, IAP conversion at depth walls
3. **Engagement** — CE patterns, session intensity during dig events
4. **Cross-event comparison** — Dig iteration performance, difficulty tuning
5. **Reward efficiency** — Value extracted vs rolls spent per layer

---

## Key Findings Reference

(No dedicated Dig analyses completed yet — scaffold ready for enrichment)

---

## Common Pitfalls

1. **Solo minigame** — No partner/team dynamics; analysis is individual-focused
2. **Progression columns** — verify dig-specific depth/layer tracking fields
3. **RNG component** — Dig has randomness in rewards; account for variance in completion metrics
