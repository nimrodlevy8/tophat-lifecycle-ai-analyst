# Skill: Racers Event Analysis

## Trigger

Apply when analyzing **Racers** (aka "Tycoon Race") events in Monopoly GO!.
This includes questions about race team composition, position/performance analysis,
chat activity, social dynamics within race teams, or any racers-specific metrics.

---

## Racers Event Structure

### What is a Racers Event?

A **Racers event** (branded as "Tycoon Race" in-game) is a competitive social
minigame where players are grouped into teams and race against each other on a
track. Teams progress by spending rolls, and individual positions within teams
determine milestone rewards.

### Team Structure

- Teams of multiple players compete on a shared track
- Each player contributes individually but team performance is collective
- Individual position within team determines reward tier
- Teams are matchmade based on activity level

### Key Dimensions

- Team composition (activity segments of team members)
- Individual position/rank within team
- Team vs team performance
- Chat/social engagement within team
- Canned message usage

---

## Key Tables

| Table | Schema | Purpose |
|-------|--------|---------|
| `fac_intraday_minigame_snapshot_daily` | `dwh-prod-tophat.DM` | Daily snapshots per user per event |
| `d_minigame_user_attributes` | `dwh-prod-tophat.DM` | User attributes per event |
| `dim_intraday_live_minigames` | `dwh-prod-tophat.BIZ` | Event metadata |
| `f_minigame_continuous_engagement` | `dwh-prod-tophat.BIZ` | CE metric per user×event |
| `f_chat_activity` | `dwh-prod-tophat.DM` | Daily chat messages per user×group |
| `chat_interactions_companion` | `dwh-prod-tophat.STD_tophat` | Individual message events (requires user approval) |

---

## Activity Segments

Same as coop: `f_last_7d_active_days` from `d_minigame_user_attributes`
- 1-4 days: '1. 1-4 day active'
- 5-6 days: '2. 5-6 day active'
- 7 days: '3. regular'

---

## Analysis Lenses

1. **Team health** — Team composition, activity balance, contribution inequality
2. **Position analysis** — What determines individual rank? Activity vs spending
3. **Social/chat engagement** — Message volume, canned vs custom, emoji usage patterns
4. **Revenue** — ARPDAU, payer distribution, revenue by team rank
5. **Cross-event comparison** — Iteration performance, seasonal effects
6. **Continuous engagement** — CE patterns, when do players stop racing

---

## Key Findings Reference

### Apr 2026: Racers Canned Messages Analysis
- Chat activity analysis using f_chat_activity and chat_interactions_companion
- Archived in: outputs/16_04_2026_racers-canned-messages/

---

## Common Pitfalls

1. **Chat tables are in STD_tophat** — requires user approval before querying, 3-month max lookback
2. **Team assignment is not in a dedicated table** — must be derived from event data
3. **Position/rank** — verify how rank is stored; may need to be computed from point totals
