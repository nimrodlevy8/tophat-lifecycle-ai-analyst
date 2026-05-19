# Monopoly Go — Economy & Currencies

## Currency Overview

| Currency | Type | Role |
|----------|------|------|
| Rolls | Hard / premium | Primary engagement & monetization currency |
| Cash | Soft | Progression currency (build landmarks) |
| Minigame tokens | Event | Per-minigame currencies for event participation |
| Stickers | Collection | Album progression & social trading |

---

## Rolls (Hard Currency)

### Sources

| Source | Details |
|--------|---------|
| Time-based regeneration | ~30–50 free rolls/hour; caps at ~100–200 balance |
| Level-up rewards | Lump sum per board level-up |
| Tournament rewards | Placement-based; escalating with tier |
| Milestone rewards | Checkpoint awards along milestone tracks |
| Event completion | Significant amounts for minigame completion |
| Album completion | Major source for set/album completion |
| Daily login bonus | Streak-based |
| Chance / Community Chest | Random board spaces |
| Friends / links | Social sharing links; daily friend gifts |
| IAP purchases | Primary monetization product |

### Sinks

| Sink | Details |
|------|---------|
| Board rolling | Primary sink — every roll at multiplier |
| Tournament progress | Rolls consumed to earn tournament points |
| Minigame token earning | Tournaments requiring roll consumption produce tokens |

**Internal fields:** `f_rolls_source_free`, `f_rolls_source`, `f_rolls_sink`, `f_rolls_sink_to_complete`, `f_first_rolls_balance`, `f_last_rolls_balance`

---

## Cash (Soft Currency)

**Sources:** Rent, Bank Heists, Smashdown attacks, Chance/Community Chest, passing Go, tournaments/events.

**Sinks:** Building/upgrading landmarks (primary), tax spaces.

Cash does NOT directly purchase minigame tokens.

---

## Minigame Currencies (Event Tokens)

| Minigame | Token Type | Primary Earning Source |
|----------|------------|----------------------|
| Adventures | Adventure tokens/dice | Tournaments, Milestones |
| Coop / Partners | Coop tokens/points | Tournaments, Milestones |
| Tycoon Race | Race points | Gameplay actions, Tournaments |
| Treasure Dig | Dig tokens/shovels | Tournaments, Milestones |
| Boutique | Boutique tokens/ingredients | Tournaments, Milestones |
| Prize Drop | Drop tokens | Tournaments, Milestones |
| Carnival Games | Carnival tokens | Tournaments, Milestones |

**Internal fields:** `f_currency_source`, `f_currency_sink`, `f_currency_sink_to_complete`

---

## Core Economy Loop

```
Rolls → Board Rolling → Tournament Points → Minigame Tokens → Minigame → Rewards (incl. Rolls) → ...
```

Tournaments/Milestones are the **bridge** between core gameplay (rolling) and minigame participation. Without tournament play, players cannot effectively earn minigame tokens.

---

## Stickers

Collection currency tied to album system. Earned from: tournament tiers, milestone completions, events, Chance/Community Chest, board completions, IAP. See `albums-seasons.md` for details.

---

## Economy Breakpoint: June 2025

**PAT-006:** Roll regeneration rates and/or progressive offers adjusted → step-function increase in engagement metrics. This is a structural breakpoint:
- All pre/post trend comparisons must account for it
- Progressive offers running during benchmarks but not target periods create significant confounds (PAT-007)
- Compare via: iterations + benchmarks + forecast approach

---

## Monetization

### Roll Pack Pricing (approximate, varies by region/offer)

| Pack | Price (USD) | Rolls | Extras |
|------|-------------|-------|--------|
| Starter/Small | $0.99–$1.99 | 80–175 | None or small cash |
| Basic | $2.99–$4.99 | 300–630 | Sticker pack, cash |
| Standard | $4.99–$9.99 | 800–1,600 | Sticker pack(s), event tokens |
| Premium | $9.99–$19.99 | 2,000–5,000 | Multiple packs, tokens, shields |
| Whale | $19.99–$49.99 | 6,000–20,000+ | Golden sticker pack, large token bundle |
| Mega Pack | $49.99–$99.99 | 25,000–75,000+ | Multiple golden packs, max tokens |

- Rolls/dollar increases at higher tiers (volume discount)
- "First purchase" offers: 3–5x standard value (loss leader)

### Event-Specific Offers

| Offer | Description |
|-------|-------------|
| Event Token Pack | Purchase minigame tokens directly (bypass grinding) |
| Event Starter Bundle | Discounted first purchase (rolls + tokens + pack) |
| **Progressive Offer** | Multi-stage purchase chain; each buy unlocks next (better) offer. **Major monetization driver and analytical confound.** |
| Milestone Boost | Advance milestone progress directly |
| Shield Pack | Purchase shields |
| Multiplier Boost | Temporary multiplier increase |

### Community Value Consensus
- **Good value:** First-purchase bonuses, season starter bundles, wild sticker cards near completion, roll packs during rush events
- **Poor value:** Standard roll packs at full price, small sticker packs (too random), cash-only packs
