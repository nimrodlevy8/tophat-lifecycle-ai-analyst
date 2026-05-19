---
name: file-organization
description: Enforce consistent folder structure across working/, outputs/, and .knowledge/ so every analysis is self-contained and discoverable. Apply this skill at the START of any new analysis (before writing the first file), when resuming an existing analysis, or when the user invokes /organize. Feature readouts are named after the feature (e.g., Boutique, Carnival, Adventures). Thematic analyses use a descriptive slug (e.g., wau-audience-analysis, ce-metric-deep-dive). This skill ensures that scattered files never accumulate in root directories — everything belongs to a named analysis folder.
---

# Skill: File Organization

## Purpose
Keep every analysis self-contained in one named folder that mirrors across
`working/`, `outputs/`, and `.knowledge/analyses/`. No loose files in root
directories. Every artifact is findable by analysis name.

## When to Apply
- **Auto:** At the START of any new analysis, before creating the first file
- **Auto:** When resuming work on an existing analysis
- **Auto:** After any pipeline step that produces files
- **Manual:** User says `/organize` — scan and reorganize existing loose files
- **Manual:** User says "clean up" or "organize" referring to file structure

## Naming Convention

### Date Prefix Rule (applies to all analysis types)
Every analysis folder is prefixed with the **date when the analysis was first
created**, in `dd_mm_yyyy_` format. The date is set once — when the triad is
first created — and never changes, even if work continues into later days or
months.

### Rule 1: Feature Readouts Use the Feature Name
If the analysis is a **New Feature Readout** (assessing a minigame, event, or
product feature), the folder name is `dd_mm_yyyy_` + **feature name in kebab-case**:

| Feature | Folder Name (created 15 Apr 2026) |
|---------|-------------|
| Boutique | `15_04_2026_boutique` |
| Carnival | `15_04_2026_carnival` |
| Adventures V3 | `15_04_2026_adventures-v3` |
| Coop Dig | `15_04_2026_coop-dig` |
| Junkyard Journey | `15_04_2026_junkyard-journey` |

**Do NOT** prefix with "readout-", "analysis-", or "feature-". Just the date
and the feature name. If there are multiple readouts for the same feature (e.g.,
Boutique WWL3 vs WWL4), append the iteration: `15_04_2026_boutique-wwl3`,
`15_04_2026_boutique-wwl4`.

### Rule 2: Thematic Analyses Use a Descriptive Slug
Non-feature analyses (root cause investigations, metric deep-dives, audience
analyses) use `dd_mm_yyyy_` + a short descriptive kebab-case slug:

| Analysis | Folder Name (created 15 Apr 2026) |
|----------|-------------|
| WAU audience composition study | `15_04_2026_wau-audience-analysis` |
| CE metric framework validation | `15_04_2026_ce-metric-deep-dive` |
| Q3 activation drop investigation | `15_04_2026_q3-activation-drop` |
| Economy rebalance impact | `15_04_2026_economy-rebalance-impact` |

### Rule 3: Demo/Example Analyses Use a Prefix
Non-production analyses (demos, examples, sandbox work) use `dd_mm_yyyy_` +
a descriptive name that makes their nature obvious:

| Analysis | Folder Name (created 15 Apr 2026) |
|----------|-------------|
| NovaMart demo run | `15_04_2026_novamart-demo` |
| Sample funnel walkthrough | `15_04_2026_sample-funnel-walkthrough` |

## Folder Structure

When starting a new analysis named `{name}`:

```
working/{name}/          # Scripts, intermediate CSVs, query logs
outputs/{name}/          # Final deliverables (decks, final charts)
outputs/{name}/charts/   # Chart PNGs for the analysis
outputs/{name}/archive/  # Superseded versions (v1, v2, v3...)
```

### Mandatory Deliverables (The Analysis Triad)

Every analysis — pipeline or ad hoc — MUST produce these 3 artifacts stored
together in `outputs/{name}/`:

| # | Artifact | Contents | When to Create |
|---|----------|----------|----------------|
| 1 | `{name}_process.md` | Analysis thinking: question framing, hypotheses, methodology choices, key decisions, dead ends, validation notes. Must link to the Hex project URL. | Continuously during analysis — start at step 1, append as you go |
| 2 | **Hex project** | All SQL and Python code in execution order with labels. Created via `wsl bash -lc "hex project create ..."`. Replaces the old `{name}_queries.md` file. | Create at analysis start, add cells as you go |
| 3 | `{name}_readout.pptx` | The final PowerPoint deck with findings. Must link to the Hex project URL on the source/appendix slide. | End of analysis |

**The old `{name}_queries.md` pattern is DEPRECATED.** All code lives in Hex
so teammates can run cells interactively, build visualizations on top, and
share the notebook.

**Naming:** Use the analysis slug (the part after `dd_mm_yyyy_`) as the file
prefix. Examples (analysis created Apr 2026):
- `outputs/15_04_2026_boutique/boutique_process.md`
- `outputs/15_04_2026_boutique/boutique_readout_v2.pptx`
- Hex project: created via CLI, URL linked in both files above

**Hex project structure:**
1. Markdown overview cell (analysis goal, methodology summary, key findings)
2. SQL cells in execution order (with BQ connection, each labeled with purpose)
3. Python cells (feature engineering, regression, clustering, PCA)
4. Markdown summary cell (results table, key insights)

**Process markdown structure:**
```markdown
# {Analysis Title} — Process Log

**Hex project:** [URL]

## Question & Decision Context
<!-- What question are we answering? What decision does it inform? -->

## Hypotheses
<!-- What did we expect to find and why? -->

## Methodology
<!-- What analytical approach did we take? Why this over alternatives? -->

## Key Findings (with reasoning)
<!-- What did the data show? What was surprising? -->

## Dead Ends & Pivots
<!-- What didn't work? What did we try and abandon? Why? -->

## Validation Notes
<!-- How did we verify the findings? Any caveats? -->
```

**No deck, still deliver 2 of 3.** If the analysis doesn't warrant a full deck
(e.g., quick L2 answer, exploratory work), the process markdown and Hex project
are still required. Note in the process file why no deck was produced.

### Root-Level Cleanliness Rule

The `outputs/{name}/` root may contain **at most 3 files** — the Analysis
Triad (code lives in Hex, not in a local file):

1. `{slug}_process.md`
2. `{slug}_readout.md`
3. `{slug}_readout.pptx` (only when the user explicitly asks for a deck)

**Everything else** lives in a subfolder:

| Subfolder | Contents |
|-----------|----------|
| `charts/` | Latest chart PNGs for the analysis |
| `archive/` | Superseded versions of any file (v1, v2, v3...) |
| `scripts/` | Python build scripts (`build_deck.py`, `generate_charts.py`, etc.) |
| `data/` | SQL files, CSVs, intermediate extracts used by scripts |

No loose PNGs, CSVs, `.sql` files, or Python scripts at the root of
`outputs/{name}/`. If a file doesn't fit the 4 triad slots, it goes in a
subfolder.

### What Goes Where

| Location | Contents |
|----------|----------|
| `working/{name}/` | Python scripts, intermediate CSVs, data extracts, draft SQL, session state |
| `outputs/{name}/` | **Only** the Analysis Triad files (process, queries, readout.md, readout.pptx) |
| `outputs/{name}/charts/` | Latest chart PNGs |
| `outputs/{name}/archive/` | Old versions of triad files or charts |
| `outputs/{name}/scripts/` | Build scripts (deck builders, chart generators) |
| `outputs/{name}/data/` | SQL files, CSVs, result extracts |
| `outputs/{name}/archive/` | Old versions — when you create v2, move v1 here |

### Knowledge Artifacts
The `.knowledge/analyses/` index references analyses by folder name. When
archiving (via archive-analysis skill), use the same `{name}` in the
`output_files` paths so they match:

```yaml
output_files:
  - outputs/15_04_2026_boutique/boutique_readout_v2.pptx
  - outputs/15_04_2026_boutique/charts/completion_rates.png
  - working/15_04_2026_boutique/kpi_extract.csv
```

## Instructions

### At Analysis Start (Auto-trigger)

1. **Determine the analysis name** by applying Rules 1-3 above
2. **Check if the folder already exists** in `working/` and `outputs/`
   - If yes: this is a continuation — use the existing folder
   - If no: create `working/{name}/` and `outputs/{name}/charts/`
3. **Announce the folder name** to the user:
   `Analysis folder: {name} (working/{name}/, outputs/{name}/)`
4. **All subsequent file writes** for this analysis MUST go into these folders

### When Writing Files

- Scripts and intermediate data: `working/{name}/`
- Charts: `outputs/{name}/charts/`
- Final decks: `outputs/{name}/`
- When creating a new version of a file, move the old version to
  `outputs/{name}/archive/` (create the dir if needed)

### /organize Command

When the user says `/organize`:

1. **Scan `working/` root** for loose files (anything not in a subfolder)
2. **Scan `outputs/` root** for loose files
3. **Group files by analysis** — use filename prefixes, timestamps, and content
   to determine which analysis each file belongs to
4. **Propose the move plan** to the user:
   ```
   Proposed reorganization:
   - wau_*.csv, analyze_wau.py → working/wau-audience-analysis/
   - boutique_*.png → outputs/boutique/charts/
   - 3 files unmatched (list them)
   ```
5. **Wait for confirmation** before moving anything
6. **Execute moves** and report the final structure

## Rules

1. **Never write files to working/ or outputs/ root.** Always use an analysis
   subfolder. The only exception is `.gitkeep`.
2. **One analysis = one folder name** used identically across working/ and
   outputs/. No mismatches (e.g., `working/wau-analysis/` vs
   `outputs/wau-audience-analysis/`).
3. **Feature readouts use the date prefix + feature name.** Not the analysis
   type. `15_04_2026_boutique`, not `15_04_2026_boutique-readout`.
4. **Versioned files go to archive/.** When v4 exists, v1-v3 live in
   `outputs/{name}/archive/`. Keep only the latest version at top level.
5. **runs/ is separate.** The `working/runs/` directory is managed by the
   run-pipeline skill and is NOT subject to this naming convention. Pipeline
   runs use their own `{date}_{dataset}_{slug}` format.
6. **Don't rename existing folders** without user confirmation. If you find
   an existing folder that doesn't match the convention, propose the rename
   rather than silently doing it.
7. **Archive, don't delete.** When reorganizing, move superseded files to
   archive/ rather than deleting them.
