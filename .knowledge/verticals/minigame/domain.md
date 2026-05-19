# Minigame Vertical — Domain Context

## What This Vertical Covers

The minigame vertical owns analysis of all LiveOps minigame events in Monopoly GO.
This includes event health assessment, iteration comparison, deep-dive
investigations, and PM-facing ad-hoc questions about minigame performance.

## Key Concepts

- **Minigame event**: A time-limited game mode activated via LiveOps (e.g., Boutique, Carnival, Adventures)
- **liveops_id / liveops_id_cleaned**: Event identifier; always use `liveops_id_cleaned` (CK-002 format) for display and sorting
- **Event profile table**: Every analysis starts with a table of all events (cleaned liveops_id, dates, duration, n) per category
- **Activity segment**: Use `d_minigame_user_attributes` for stable per-user-per-event segmentation (not daily KPI table)
- **Tenure**: Use `f_days_since_first_activity` (not `f_days_since_install`)
- **Maturity filter**: event_end_date + 7D before including in trend analysis
- **Success metric**: If missing, exclude the event — never impute as zero

## Primary Tables

- `d_minigame_user_attributes` — one row per user × event, stable activity segment
- `f_minigame_daily_kpis` — daily aggregated KPIs per event
- `d_minigame_events` — event metadata (dates, type, config)
- Coop-specific: `f_coop_partners`, `d_coop_attractions`

## Specialized Agents

- **Minigame Health Assessor** (`agents/minigame-health-assessor.md`) — PM front door with 4 modes: health-check, comparison, deep-dive, pm-question

## Specialized Skills

- **Coop Analysis** (`.claude/skills/coop-analysis/skill.md`) — pusher classification, partner structure, social metrics
- **JIRA Incidents** (`.claude/skills/jira-incidents/skill.md`) — per-minigame incident reports

## Routing Rule

When the active vertical is `minigame`, any question about event performance,
minigame health, event comparison, or feature investigation routes through the
Minigame Health Assessor agent before falling through to generic agents.

## Visualization Standards

- Colors: Hex-aligned palette per minigame type
- Lines: PCHIP interpolation (not cubic spline)
- Markers: small (s=25 scatter, s=15 line)
- Always filter by maturity (event_end_date + 7D)

## Known Patterns

- PAT-001 through PAT-007 (documented in minigame health assessor agent)
- See `.knowledge/analyses/_patterns.yaml` for recurring findings

## Event Filtering Defaults

Exclude non-main events by default:
- SL, TSL, AB, MVT, Internal, Dark Launch, Control/Variant, cheater splits
- Include only when explicitly requested
