# Skill: JIRA Incident Report by Minigame

## Trigger

Invoked as `/jira-incidents` or when the user asks for an incident report,
incident summary, or incident dashboard for the Tophat (Monopoly GO!) project.

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `date_from` | 30 days ago | Start of the reporting window (YYYY-MM-DD) |
| `date_to` | today | End of the reporting window (YYYY-MM-DD) |
| `project` | TOP | JIRA project key |
| `output` | table | `table` for inline, `deck` for PowerPoint |

## What This Skill Produces

A **chronological, per-minigame-event** incident report. Each row is one
minigame event instance (e.g., "RaceCup WL27 | Apr 8-12"), sorted by
start_date ascending. The report answers:
- How many incidents occurred **during this specific event's live window**?
- Which incidents are **minigame-related** vs. coincidental (other)?
- What was the **severity breakdown** (Code Red / Yellow / White)?
- What was the **total TTR** and **average TTR** for incidents in each window?
- For minigame-related incidents: a **narrative summary** of what went wrong.

**Aggregation level:** Per event instance + date. NOT rolled up by minigame
type. Each row = one event name + its date window. Rows are sorted
chronologically by start_date.

## Workflow

### Step 1: Fetch minigame event windows from BigQuery

Query `dwh-prod-tophat.BIZ.dim_intraday_live_minigames` for all events
in the date range. This gives the live window (start_date, end_date) for
each minigame event.

```
bq query --use_legacy_sql=false --project_id=dwh-adev-tophat --format=csv \
  "SELECT
     minigame_type,
     event_type,
     liveops_id,
     start_date,
     end_date,
     start_time,
     end_time
   FROM \`dwh-prod-tophat.BIZ.dim_intraday_live_minigames\`
   WHERE start_date >= '{date_from}'
     AND start_date <= '{date_to}'
   ORDER BY start_date"
```

**Deduplication rules:**
- Merge `_solo` / `_Cheaters` Racers variants into the main RaceCup event
  (same window, different bracket — treat as one event)
- Merge Boutique A/B test variants (same window) into one event
- Keep all other events as-is

**Friendly name mapping** (from `minigame_type` to display name):
| `minigame_type` | Display Name |
|-----------------|-------------|
| `adventure` | Adventures |
| `boutique` | Boutique |
| `coop_event` | Coop Partners |
| `minigame_dig` | Treasure Dig |
| `prize_drop` | Plinko / Prize Drop |
| `tycoon_race` | Tycoon Racers |

### Step 2: Fetch JIRA incidents

Use the Atlassian MCP to search for incidents in the date range:

```
JQL: project = {project} AND issuetype = Incident
     AND created >= "{date_from}" ORDER BY created ASC
```

Fields to fetch:
- `summary`, `created`, `status`, `statuscategorychangedate`, `labels`,
  `components`, `description`, `priority`

Fetch in pages of 100. Respect JIRA Access skill rules (read-only).

### Step 3: Parse severity from ticket summary

Severity is encoded in the ticket summary as a color code pattern:
- `Code Red` or `🔴` → **Red** (critical, player-impacting at scale)
- `Code Orange` or `🟠` → **Orange** (significant, limited impact)
- `Code Yellow` or `🟡` → **Yellow** (moderate, localized impact)
- `Code White` or `⚪` → **White** (low, minor or no player impact)

If no color code is found, classify as **Unknown**.

### Step 4: Classify minigame-related incidents

An incident is **minigame-related** if it meets ANY of these criteria:

1. **Explicit minigame name in summary** — scan for these keywords
   (case-insensitive):
   - Adventures, Adventure Event
   - Coop, Partners, Coop Partners
   - Racers, Tycoon Race, Tycoon Racers, RaceCup, MMR (in Racers context)
   - Dig, Treasure Dig
   - Boutique, Block Boutique
   - Plinko, Prize Drop
   - Carnival, Juggle Jam, Battleship, Fortune Teller
   - Leaderboard + (Racers|event) — Racers leaderboard issues

2. **Minigame mechanics in description** — if summary is ambiguous, check
   the description for references to:
   - Event tokens, event currency, milestones, attractions
   - Matchmaking (MMR), brackets, team formation
   - Lootbox, reward tiers, completion rates
   - Specific `liveops_id` patterns from the BQ data

3. **Labels or components** — check for minigame-related labels/components

For each minigame-related incident, also tag the **specific minigame type**
(`adventure`, `boutique`, `coop_event`, `minigame_dig`, `prize_drop`,
`tycoon_race`) and write a **1-sentence narrative summary** of what happened.

**Important:** An incident can happen during a minigame's live window but
NOT be minigame-related (e.g., a server outage during Racers week is
coincidental). Only classify as minigame-related if the incident's root
cause or impact is specific to minigame mechanics.

### Step 5: Compute Time to Resolution (TTR)

TTR = `statuscategorychangedate` - `created`

- `resolutiondate` is typically null for Tophat incidents — use
  `statuscategorychangedate` as the resolution proxy (when status category
  changed to "Done")
- If the ticket is still open (In Progress / To Do), TTR = "Open"
- Report both **Total TTR** (sum of all resolved) and **Avg TTR**

**TTR caveats to include in output:**
- Some tickets show inflated TTR because they stay open for postmortem/repair
  item tracking after the incident is actually resolved
- TTR measures ticket lifecycle, not actual incident resolution time

### Step 6: Match incidents to minigame windows

For each minigame event from Step 1, find all incidents where:
`incident.created_date >= event.start_date AND incident.created_date <= event.end_date`

**Type-matching rule (CRITICAL):** An MG incident only counts as "MG" for
an event if the incident's minigame type matches the event's minigame type.
A Boutique incident during an Adventures window is NOT an Adventures MG
incident — it counts as "Other" for that event.

MG incidents that occur when no matching event type is live are **orphans**.
Report orphans separately in the executive summary.

**Note:** A non-MG incident (infrastructure, payments, etc.) can appear
under multiple concurrent minigame events. This is intentional — it shows
the incident landscape during each event.

### Step 7: Produce output

**Primary output is per-event chronological.** Each row is one minigame
event instance, sorted by start_date ascending. Do NOT roll up by type.

#### Table output (default)

Chronological table — one row per minigame event:

| Event Name | Type | Window | Days | Total | MG | Other | R | Y | W | Total TTR | Avg TTR | MG Narrative |
|------------|------|--------|------|-------|----|-------|---|---|---|-----------|---------|--------------|

Followed by a totals row.

#### Deck output (`/jira-incidents deck`)

Build a PowerPoint using the MGO deck template (see design-system.md):
1. **Cover slide** — "Incident Report: Minigame Windows" + date range
2. **Methodology slide** — How incidents were matched to minigames, severity
   parsing, TTR calculation, minigame classification logic
3. **Chronological event table (1-2 slides)** — The full per-event table,
   split across slides if >12 rows per slide
4. **Key findings slide** — Top observations, patterns, recommendations

**Slide layout rules:**
- Brand mark (`mgo_brand_mark.png`) goes top-right only, small (2.1" x 0.5")
- Do NOT use `mgo_artwork.png` or `mgo_logo.png` on content slides
- No image may overlap with any text element
- Cover slide uses layout 0 (TITLE) with no artwork image
- All content slides use layout 5 (BLANK) with brand mark only

Save to `outputs/incident-minigame-report/` following file-organization skill.

## Data Sources

| Source | What | How |
|--------|------|-----|
| JIRA (Atlassian MCP) | Incident tickets | JQL search, read-only |
| BigQuery (`BIZ.dim_intraday_live_minigames`) | Minigame event windows | `bq query` via CLI |
| `.knowledge/.../minigames.md` | Minigame taxonomy | File read for keyword list |

## Caveats & Known Limitations

1. **Severity is parsed from summary text**, not a structured JIRA field.
   If the naming convention changes, classification will break.
2. **TTR uses statuscategorychangedate**, which may lag behind actual
   incident resolution. Some tickets inflate TTR due to postmortem tracking.
3. **Minigame classification is keyword-based** from the summary. Ambiguous
   incidents (e.g., "server error" during Racers) default to "Other" unless
   the description explicitly ties it to minigame mechanics.
4. **Overlapping events** mean the same incident can appear under multiple
   minigame windows. The per-type aggregate deduplicates.
5. **Cheater/solo Racers brackets** are merged with the main race event.
