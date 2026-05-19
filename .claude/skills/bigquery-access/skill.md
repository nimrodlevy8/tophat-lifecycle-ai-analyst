# Skill: BigQuery Access

## Trigger
Before running ANY BigQuery query — applies to all data access in this project.

## Connection

- **CLI:** `bq query --use_legacy_sql=false --project_id=dwh-adev-tophat`
- **Job project:** `dwh-adev-tophat` (dev — has job creation permission)
- **Data project:** `dwh-prod-tophat` (prod — read access via cross-project queries)
- **Auth:** `gcloud` pre-authenticated, no setup needed
- **Query pattern:** Always backtick-escape fully qualified table names:
  ```
  bq query --use_legacy_sql=false --project_id=dwh-adev-tophat \
    "SELECT ... FROM \`dwh-prod-tophat.BIZ.table_name\` WHERE ..."
  ```

## Schemas

| Schema | Contents | Access Rules |
|---|---|---|
| `dwh-prod-tophat.BIZ` | Business views and tables | Free to query. Default 7-day date limit. Can go back to 2025-01-01 for analysis. |
| `dwh-prod-tophat.DM` | Data mart tables | Free to query. Default 7-day date limit. Can go back to 2025-01-01 for analysis. |
| `dwh-prod-tophat.STD_tophat` | Raw data tables | **ASK USER BEFORE QUERYING.** Max 3 months lookback. Date filter required: `snapshot_date` or `date(collector_time)`. |
| `dwh-prod-tophat.exp` | Analyst-created custom tables | Free to query. These are ad-hoc tables created by the analytics team. |

## Hard Rules

1. **READ ONLY.** Never run UPDATE, ALTER, DELETE, DROP, INSERT, MERGE, CREATE, or any mutating statement. If the user explicitly asks for a mutation, **ask twice to confirm** before executing. Enforced by `helpers/sql_validator.py` and `.claude/hooks/validate-sql.sh`.
2. **Date filters are mandatory.** Every query MUST have a date filter in the WHERE clause — typically `snapshot_date` or `date(collector_time)`.
3. **Default lookback: 7 days.** Use `snapshot_date >= current_date - 7` unless the analysis requires more.
4. **Max lookback for BIZ/DM: 2025-01-01.** For analysis needs, can extend to `snapshot_date >= '2025-01-01'` but not earlier.
5. **Max lookback for STD_tophat: 3 months.** Raw data queries must not go back more than 3 months from today.
6. **Always ask before querying STD_tophat.** Confirm with the user before running any query against raw data tables.
7. **Row count gate: 1M row warning.** Before executing any query expected to
   return >1M rows, STOP and ask the user for approval. State the estimated row
   count. To estimate, run a `SELECT COUNT(*)` with the same WHERE/JOIN logic
   first (or use `--dry_run` to check bytes scanned). If the count exceeds 1M,
   report: "This query will return ~X rows. Approve?" and wait for confirmation.
   Enforced by `.claude/hooks/validate-sql.sh` (dry-run check).

## Aggregation-First Principle

**Never pull raw large datasets into memory.** Always aggregate at the SQL/BQ
level and bring only summary data into Python/local memory.

| Approach | When to use |
|----------|-------------|
| `GROUP BY` + aggregates in SQL | Default for everything. Bring back <100K rows. |
| `APPROX_COUNT_DISTINCT`, `APPROX_QUANTILES` | When exact counts aren't needed |
| Window functions in SQL | Rankings, running totals, lag/lead — compute in BQ, not pandas |
| `LIMIT` + sampling (`TABLESAMPLE`) | Exploratory/profiling only |
| Temp tables for multi-step | Break complex logic into CTEs or temp tables in BQ |

**Anti-patterns (never do these):**
- `SELECT *` without `LIMIT` on tables with >100K rows
- Pulling user-level raw data to aggregate in pandas
- Loading millions of rows to then `df.groupby()` locally
- Multiple round-trips that could be one SQL query

**Workflow:**
1. Estimate row count first (`COUNT(*)` or `--dry_run`)
2. If >1M rows: redesign query to aggregate in BQ, or ask user for approval
3. If 100K–1M rows: acceptable for detailed analysis, proceed with awareness
4. If <100K rows: safe to pull into memory freely

## Programmatic Validation

Before executing any BigQuery query in Python scripts, import and call the validator:

```python
from helpers.sql_validator import validate_bigquery_sql
validate_bigquery_sql(sql)  # raises SecurityError if blocked
```

The CLI hook (`.claude/hooks/validate-sql.sh`) also validates every `bq query` command automatically at the harness level — queries that contain blocked keywords will be rejected before execution.

## SQL Formatting Rules

Every query must follow these four rules:

1. **Comments:** Every CTE gets a header comment. Non-obvious filters, CASE
   logic, JOINs, and business-logic aggregations get inline comments. Top-level
   block comment with purpose, key tables, scope, and assumptions.

2. **Table aliases:** Use `t1`, `t2`, `t3` — never single letters (`s`, `u`).
   Number sequentially in order of appearance.
   ```
   -- Wrong: FROM fac_intraday_minigame_snapshot_daily s
   -- Right: FROM fac_intraday_minigame_snapshot_daily t1
   ```

3. **SELECT:** One field per line, never sequential on one line.
   ```sql
   SELECT
       user_id,
       liveops_id,
       snapshot_date
   ```

4. **JOIN ... ON:** ON clause goes on its own line, indented under the JOIN.
   ```sql
   LEFT JOIN d_minigame_user_attributes t2
       ON t1.user_id = t2.user_id
       AND t1.snapshot_date = t2.snapshot_date
   ```

## Data Notes

- Tables use STRUCT/nested columns. Example: `v_f_user_rpt.is_active` inside `v_f_user_standard_kpis`.
- BigQuery suggests correct field names on typos — check error messages for hints.
- **CRITICAL: `v_f_user_standard_kpis` contains ALL players, not just active ones.**
  When using this table to determine if a user was active on a given day, you MUST
  filter `v_f_user_rpt.is_active = true` (nested inside the `v_f_user_rpt` struct).
  A row existing in this table does NOT mean the user was active — it means they
  exist in the player base. Without this filter, denominators are inflated and
  activity rates are meaningless.
