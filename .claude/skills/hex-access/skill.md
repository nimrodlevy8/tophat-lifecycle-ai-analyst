# Skill: Hex Access

## Trigger
Before ANY Hex interaction — creating projects, managing cells/worksheets,
running notebooks, listing connections, or any Hex CLI operation.

## Platform Detection

Before running any `hex` command, detect the host platform and pick the
matching invocation pattern below:

- **macOS / Linux:** run `hex ...` directly in the shell.
- **Windows (Git Bash / PowerShell):** the CLI is installed inside WSL; all
  commands must be prefixed with `wsl bash -lc "hex ..."`.

A quick heuristic: `uname` returns `Darwin` on macOS, `Linux` on Linux, and on
Windows Git Bash it returns `MINGW*`/`MSYS*` — in that case, use the WSL
wrapper.

## Connection

| Field | macOS | Windows (WSL) |
|---|---|---|
| CLI version | v1.3.0 | v1.2.1 |
| Install path | `~/.local/bin/hex` | `/home/<wsl-user>/.local/bin/hex` |
| Invocation | `hex ...` | `wsl bash -lc "hex ..."` |
| Auth profile | `scopely` | default |
| Auth user | Scopely SSO account | Scopely SSO account |

Shared:
- **Workspace:** Scopely (`0195fa0d-a0b5-7001-b18f-ec09baa16d1a`)
- **Hostname:** `https://app.hex.tech`
- **JSON mode:** Add `--json` to any command for scripted/parseable output

## Installation & Auth

### macOS (one-time setup)

Install via Hex's official installer:
```bash
curl -fsSL https://hex.tech/install.sh | sh
```

Auth uses a personal access token stored in `.env` as `HEX_CLI_LOGIN_TOKEN`
(gitignored). To (re-)authenticate non-interactively:
```bash
set -a && source .env && set +a
hex auth login scopely --token-from-env
```

Interactive re-auth (opens browser):
```bash
hex auth login scopely
```

### Windows (WSL)

The CLI is pre-installed inside WSL; no install step needed on the host.
Interactive re-auth when the token expires:
```bash
wsl bash -lc "hex auth login"
```
The user completes browser OAuth to finish.

## CLI Commands Reference

Commands are identical on both platforms. On Windows, wrap every command
with `wsl bash -lc "..."` (examples shown in both forms for the first block
only; subsequent blocks show the bare form — apply the wrapper on Windows).

### Projects

macOS / Linux:
```bash
hex project list                      # List all accessible projects
hex project create                    # Create a new project
hex project get <id>                  # Get project details
hex project open <id>                 # Open in browser
hex project run <id>                  # Run draft notebook
hex project export <id>               # Export as YAML
hex project import <file>             # Import from YAML
```

Windows (WSL) equivalent:
```bash
wsl bash -lc "hex project list"
wsl bash -lc "hex project create"
# ...etc.
```

### Cells (Worksheets)
```bash
hex cell list <project-id>                   # List cells in project
hex cell get <project-id> <cell-id>          # Get single cell
hex cell create <project-id>                 # Create new cell
hex cell update <project-id> <cell-id>       # Update cell source/connection
hex cell delete <project-id> <cell-id>       # Delete cell
hex cell run <project-id> <cell-id>          # Run cell + dependencies
```

### Connections
```bash
hex connection list                   # List data connections
hex connection get <id>               # Get connection details
```

### Runs
```bash
hex run list <project-id>             # List runs for a project
hex run status <run-id>               # Get run status
hex run cancel <run-id>               # Cancel a running project
```

### Auth & Config
```bash
hex auth status                       # Check auth status
hex auth switch <profile>             # Switch active profile (macOS multi-profile)
hex config                            # Manage CLI config
```

### Apps
```bash
hex app list
hex app run <project-id>              # Run the published app
```

## Known Data Connections

| ID | Name | Type |
|----|------|------|
| `0195fa0d-aa20-7001-b190-b075186ec2c0` | [Demo] Hex Public Data | snowflake |
| `019716db-b370-7002-be76-8c8ea1b7bce8` | Hex to BQ | bigquery (dwh-prod-core, dwh-prod-m...) |

Use `hex connection list --json` to refresh.

## Hard Rules

1. **Scopely workspace only.** Never connect to or interact with any
   non-Scopely Hex workspace.

2. **Confirm before destructive operations.** Before deleting cells, projects,
   or cancelling runs, confirm with the user.

3. **Always use `--json` when parsing output programmatically.** For display
   to the user, default (table) format is fine.

4. **Use the correct invocation for the host.** On Windows, never run `hex`
   bare — it is not installed in Git Bash. Always prefix with
   `wsl bash -lc "..."`. On macOS, never prefix with `wsl` — WSL doesn't exist
   there.

5. **Never print the PAT.** On macOS, `HEX_CLI_LOGIN_TOKEN` lives in `.env`
   (gitignored). Do not echo it, commit it, or pass it as a CLI argument
   (visible in `ps`). Only load via `set -a && source .env && set +a`.

6. **No external sharing or publishing.** Never create cells or code that:
   - Shares/publishes notebooks to external URLs or public links
   - Sends data to external APIs, webhooks, or endpoints
   - Exports data to non-Scopely destinations
   - Schedules external notifications outside Scopely channels
   - Uses `requests.post()`, `urllib`, `httpx`, or any HTTP client
     to send data to non-Scopely URLs
   - Embeds external API keys, tokens, or credentials in notebook code

   All Hex project outputs must stay within Scopely boundaries (Hex workspace,
   Google Drive, BigQuery). Enforced by `.claude/hooks/block-notebook-exfil.sh`.

## Code Quality Standards

All SQL and Python cells written to Hex MUST be thoroughly commented. This is
non-negotiable — Hex projects are shared artifacts read by PMs, data scientists,
and future-you.

### SQL Cells

- **Header comment:** 2-3 lines stating purpose and expected output
- **Every CTE:** comment block explaining what it produces and why
- **Non-obvious expressions:** inline comment on CASE, window functions, HAVING
  conditions, and any filter that isn't self-evident
- **Magic numbers:** explain thresholds (e.g., `>= 5` events — why 5?)
- **Data quirks:** reference correction IDs (e.g., CORR-001) and explain
  why specific rows/events are excluded

### Python Cells

- **Module header:** 5-10 line block explaining purpose, inputs, outputs,
  and how this cell fits into the overall analysis flow
- **Every transformation:** inline comment explaining WHAT it does and WHY
  (not just labeling — explain the reasoning)
- **Statistical choices:** explain why this window size, why this model type,
  why these features were included/excluded
- **Key findings:** annotate where results connect to analysis conclusions
  (e.g., "ce_trend = #1 predictor, coefficient +0.117 in Model A")
- **Output variables:** document what downstream cells consume

### Anti-patterns (never do these)

- Block labels only (`# Rolling averages`) without explaining reasoning
- Assuming the reader knows why a parameter was chosen
- Leaving transformation steps unexplained because "it's obvious"
- Writing comments that describe WHAT the code does syntactically instead
  of WHY it does it analytically

## Known Gotcha: Backticks in SQL

BigQuery table names use backticks (`` `project.dataset.table` ``), which get
eaten by shell quoting. On Windows this is especially bad because the call
passes through two shell layers (Git Bash → WSL → hex CLI). HEREDOCs, escaped
backticks, and `$(cat file)` all fail intermittently on Windows.

### Proven fix: Python subprocess (works 100% on Windows)

Bypass shell quoting entirely by calling the hex CLI through Python's
`subprocess.run()` inside WSL. Arguments are passed as a list — no shell
interpretation occurs, so backticks survive intact.

**Step 1:** Write the SQL/Python source to a local file (using Claude's Write
tool or any method that doesn't involve shell interpretation):
```
# Write to: working/my_cell.sql (or .py for code cells)
# Backticks are preserved as-is in the file contents.
```

**Step 2:** Call hex via Python subprocess inside WSL:
```bash
wsl bash -lc "python3 -c \"
import subprocess, sys

# Read the source file from the mounted Windows filesystem
source = open('/mnt/c/Users/alireza.hamidi/AI Analyst Plus/scopely-mgo-ai-analyst/working/my_cell.sql').read()

# Call hex CLI with arguments as a list — no shell escaping needed
result = subprocess.run([
    'hex', 'cell', 'create', '<PROJECT_ID>',
    '-t', 'sql',
    '-l', 'My Cell Label',
    '--data-connection-id', '019716db-b370-7002-be76-8c8ea1b7bce8',
    '--output-dataframe', 'df_name',
    '-s', source,
    '--json'
], capture_output=True, text=True)

print(result.stdout)
print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
\""
```

For **updating** an existing cell (same pattern):
```bash
wsl bash -lc "python3 -c \"
import subprocess, sys
source = open('/mnt/c/Users/.../working/my_cell.sql').read()
result = subprocess.run([
    'hex', 'cell', 'update', '<CELL_ID>',
    '-t', 'sql',
    '-s', source,
    '--json'
], capture_output=True, text=True)
print(result.stdout)
print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
\""
```

### Why this works

- `subprocess.run([...])` passes each argument directly to the process without
  shell expansion — backticks, quotes, and special characters are untouched.
- The file is read from the mounted Windows path (`/mnt/c/...`) so the Write
  tool on the Windows side can create it without any escaping concerns.
- Only the outer `wsl bash -lc "python3 -c ..."` layer needs escaping (just
  the Python string delimiters).

### macOS alternative

On macOS (single shell layer), the simpler file-based approach usually works:
```bash
hex cell create <PROJECT_ID> -t sql -l "Label" \
  --data-connection-id <CONN_ID> \
  --output-dataframe df_name \
  -s "$(cat working/my_cell.sql)" --json
```
But if backticks still get stripped, use the same Python subprocess pattern
(without the `wsl bash -lc` wrapper).

### Anti-patterns (never do these on Windows)

- `wsl bash -lc "hex cell create ... -s \"$(cat /tmp/file.txt)\""` — the
  nested `$()` re-enters shell expansion and strips backticks.
- HEREDOCs with backtick-containing SQL — bash interprets backticks as
  command substitution even inside single-quoted HEREDOCs when nested in
  `wsl bash -lc "..."`.
- Escaping backticks with `\`` — unreliable across the two shell layers.

## Troubleshooting

| Problem | Platform | Fix |
|---------|----------|-----|
| `hex: command not found` | macOS | Ensure `~/.local/bin` is on PATH. Installer adds it; new shells pick it up. Fallback: `export PATH="$HOME/.local/bin:$PATH"` |
| `hex: command not found` | Windows | You're running bare `hex` in Git Bash. Use the `wsl bash -lc` prefix. |
| WSL not responding | Windows | Check status: `wsl --status`. Restart: `wsl --shutdown` then rerun the command. |
| Auth expired | macOS | `set -a && source .env && set +a && hex auth login scopely --token-from-env --update` |
| Auth expired | Windows | `wsl bash -lc "hex auth login"` — complete browser OAuth. |
| Token invalid | macOS | Generate a new PAT at https://app.hex.tech → Settings → Integrations → API keys, then update `.env`. |
| Slow response | both | Add `--quiet` flag to suppress non-essential output. |
| Backticks stripped from SQL | both | Use Python subprocess method — see "Known Gotcha: Backticks in SQL" above. Never pass SQL with backticks through shell expansion. |
