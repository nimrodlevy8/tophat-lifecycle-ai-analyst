# Verticals

A **vertical** is an analytical domain within Monopoly GO. Each vertical has its
own tables, metrics, domain knowledge, and (optionally) specialized agents/skills.

## How It Works

1. `.knowledge/active.yaml` contains a `vertical` field (e.g., `minigame`).
2. At session start, Knowledge Bootstrap loads context from the active vertical's
   folder: `.knowledge/verticals/{vertical}/`.
3. Skills and agents tagged with a vertical scope only activate when that vertical
   is active.
4. Universal skills/agents work for all verticals.

## Available Verticals

| Vertical | Folder | Description |
|----------|--------|-------------|
| `minigame` | `verticals/minigame/` | Minigame performance, event health, coop analysis, liveops events |
| `economy` | `verticals/economy/` | Currency flows, sinks/sources, inflation, shop conversion |
| `retention` | `verticals/retention/` | Player lifecycle, churn prediction, reactivation, DAU/WAU/MAU |
| `ua` | `verticals/ua/` | User acquisition, campaign ROI, channel mix, LTV payback |
| `social` | `verticals/social/` | Social features, friend graphs, gifting, team mechanics |
| `general` | _(no folder needed)_ | Cross-cutting analysis, no domain-specific context loaded |

## Adding a New Vertical

1. Create a folder: `.knowledge/verticals/{your-vertical}/`
2. Add at minimum:
   - `domain.md` — key concepts, mechanics, terminology
   - `tables.md` — primary tables and columns you use
   - `metrics.md` — vertical-specific KPIs and how they're calculated
3. Optionally add:
   - `quirks.md` — data gotchas specific to your domain
   - `patterns.md` — known behavioral patterns in your data
   - `routing.yaml` — custom agent routing rules
4. Set your vertical in `.knowledge/active.yaml`:
   ```yaml
   vertical: your-vertical
   ```
5. Skills/agents you create can be scoped with `scope: your-vertical` in their
   frontmatter to prevent them from activating for other verticals.

## Vertical vs. Dataset

- **Dataset** = which tables/database you're connected to (set via `/switch-dataset`)
- **Vertical** = which analytical domain you work in (set via `/switch-vertical` or in active.yaml)

Most analysts have one vertical and one dataset. But you could have the same
dataset (e.g., BigQuery MGO tables) used by multiple verticals (minigame team
queries event tables, economy team queries currency tables).
