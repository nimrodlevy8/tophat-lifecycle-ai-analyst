# Monopoly Go — Core Mechanics

## Board & Rolling

- Player has a **roll** balance (premium currency); each tap of "Roll" consumes rolls
- **Multiplier** settings: 1x, 2x, 3x, 5x, 10x — higher = more rolls consumed, proportionally higher rewards
- Two dice → 2–12 → token moves that many spaces on a circular track (~40 spaces)

### Roll Regeneration
- Free rolls regenerate over time (~30–50 per hour; varies by level/tuning)
- Caps at ~100–200 balance (varies by player level)
- Additional sources: level-ups, tournament/milestone rewards, daily login, events, album completion, IAP

### Space Types

| Space | Effect | Frequency |
|-------|--------|-----------|
| Property (Color Set) | Earns rent (cash); build landmarks here | ~60% |
| Railroad | Triggers **Smashdown** (attack) | 4 per board |
| Utility | Triggers **Bank Heist** (steal) | 2 per board |
| Chance / Community Chest | Random reward: cash, rolls, sticker packs, shields, tokens | ~4–6 |
| Tax (Income / Luxury) | Removes % of current cash (sink) | 2 |
| Go | Cash bonus on pass/land | 1 |
| Jail / Just Visiting | Go to Jail = skip turns or pay | 1–2 |
| Free Parking | Small cash or nothing | 1 |

## Smashdown (Attack)

**Trigger:** Landing on Railroad.

1. Game selects random opponent (friends or matched strangers)
2. Player sees opponent's board with landmarks
3. Player smashes one landmark — damage based on multiplier × landmark value
4. Awards cash + tournament points
5. Opponent's landmark reverts one upgrade level

**Shields:**
- Hold up to 3–5 shields (varies by update)
- Shield absorbs hit — landmark NOT damaged
- Sources: Chance/Community Chest, daily rewards, purchases
- Auto-deploy (no manual activation)
- At 0 shields → most valuable landmark is damaged

## Bank Heist (Steal)

**Trigger:** Landing on Utility.

1. Random opponent selected
2. Vault/safe interface with tiles/doors
3. Player picks a tile → reveals stolen cash amount
4. Amounts scale with target's cash balance and player level
5. Higher multiplier = higher potential steal
6. Opponents matched by similar progression level

## Collecting Rent

- Landing on or passing properties earns rent (cash)
- Rent increases as landmarks on that set are upgraded
- Higher multiplier = higher rent
- Primary passive cash source → feeds landmark building

## Tax (Currency Sink)

- Income Tax / Luxury Tax spaces remove % of current cash
- Scales with cash balance and multiplier
- Encourages spending on landmarks rather than hoarding

## Building Landmarks (Progression)

- Each board has property sets (2–4 same-colored properties)
- Each property builds through ~5 levels (houses → hotel equivalent)
- Completing ALL landmarks on a board → advance to next board
- Each board has a unique theme; hundreds exist, continuously added
- Board completion awards: large cash bonus, rolls, sticker packs
- Costs increase exponentially with board number
- **Net Worth** (sum of all landmarks built) = primary progression metric
