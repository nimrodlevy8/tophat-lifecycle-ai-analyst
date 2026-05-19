#!/bin/bash
# Hook: Validate SQL in bq query commands.
# 1. Block destructive operations (DELETE, UPDATE, DROP, etc.)
# 2. Warn on queries likely to return >1M rows (SELECT * without LIMIT on large tables)
# Fires on PreToolUse for Bash commands containing "bq query".
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only check bq query commands
if ! echo "$COMMAND" | grep -qi 'bq.*query'; then
  exit 0
fi

# Extract the SQL portion (everything after the flags, typically in quotes)
SQL_UPPER=$(echo "$COMMAND" | tr '[:lower:]' '[:upper:]')

# --- Rule 1: Block destructive operations ---

for KEYWORD in DELETE UPDATE DROP TRUNCATE ALTER MERGE; do
  if echo "$SQL_UPPER" | grep -qwE "\b${KEYWORD}\b"; then
    echo "BLOCKED: BigQuery write operation detected: ${KEYWORD}. This project is read-only." >&2
    exit 2
  fi
done

# Check INSERT (blocked by default)
if echo "$SQL_UPPER" | grep -qwE "\bINSERT\b"; then
  echo "BLOCKED: INSERT not allowed. This project is read-only." >&2
  exit 2
fi

# Check CREATE (only TEMP allowed)
if echo "$SQL_UPPER" | grep -qwE "\bCREATE\b"; then
  if ! echo "$SQL_UPPER" | grep -qE "CREATE\s+(TEMP|TEMPORARY)"; then
    echo "BLOCKED: Only CREATE TEMP TABLE allowed. Permanent table creation is blocked." >&2
    exit 2
  fi
fi

# --- Rule 2: Warn on unbounded SELECT * (likely >1M rows) ---

# Detect SELECT * without LIMIT on raw/large tables (STD_tophat, fac_, dim_ prefixed)
if echo "$SQL_UPPER" | grep -qE "SELECT\s+\*"; then
  if ! echo "$SQL_UPPER" | grep -qE "\bLIMIT\b"; then
    # Check if querying known large tables
    if echo "$SQL_UPPER" | grep -qiE "(STD_TOPHAT|FAC_|V_F_USER_STANDARD)"; then
      echo "WARNING: SELECT * without LIMIT on a large table. This may return >1M rows." >&2
      echo "Add a LIMIT clause, use COUNT(*) first to estimate, or aggregate in SQL." >&2
      echo "Run with --dry_run flag to check bytes scanned before executing." >&2
      exit 2
    fi
  fi
fi

# Detect queries missing GROUP BY on large date ranges (>30 days) without LIMIT
# This catches user-level pulls that should be aggregated
if echo "$SQL_UPPER" | grep -qiE "(STD_TOPHAT|FAC_INTRADAY|FAC_DAILY)"; then
  if ! echo "$SQL_UPPER" | grep -qE "\b(GROUP BY|LIMIT|COUNT\(|APPROX_)\b"; then
    echo "WARNING: Query on large table without GROUP BY or LIMIT." >&2
    echo "Aggregate at the SQL level — do not pull raw rows into memory." >&2
    echo "Add GROUP BY, LIMIT, or use COUNT(*) to estimate row count first." >&2
    exit 2
  fi
fi

exit 0
