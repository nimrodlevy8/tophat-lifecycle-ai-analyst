# Skill: Boutique Event Analysis

## Trigger

Apply when analyzing **Boutique** events in Monopoly GO!. This includes
questions about boutique item progression, collection mechanics, spending
patterns, or boutique-specific engagement.

---

## Boutique Event Structure

### What is a Boutique Event?

A **Boutique event** is a collection/shopping minigame where players spend
currency to acquire items from a themed boutique. Players progress through
tiers of items with increasing costs.

### Key Dimensions

- Item acquisition progression
- Tier completion rates
- Spending efficiency (rolls per item)
- Collection completion rates
- Early vs late purchasing patterns

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

1. **Progression** — Tier completion funnel, item acquisition rates
2. **Revenue** — Spending patterns, ARPDAU, conversion optimization
3. **Engagement** — CE curves, early vs late engagement patterns
4. **Cross-event comparison** — Boutique iteration performance
5. **Economy** — Currency sink efficiency, roll cost per tier

---

## Key Findings Reference

(Prior boutique analyses exist in outputs/ — check for date-prefixed folders)

---

## Common Pitfalls

1. **Boutique-specific columns** — verify item/tier progression column names in snapshot table
2. **Short event duration** — Boutique events may be shorter; adjust maturity windows
3. **Multiple items per tier** — don't collapse tiers when analyzing item-level progression
