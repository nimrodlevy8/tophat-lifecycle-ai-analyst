#!/bin/bash
# Hook: Verify all security hooks are functional.
# This hook MUST NOT depend on jq or any external tool that might be missing.
# If security infrastructure is broken, BLOCK (exit 2) immediately.
set -eo pipefail

HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCKFILE="/tmp/.claude_hooks_verified"

# Only run the full test once per session (check lockfile with PID)
if [ -f "$LOCKFILE" ]; then
  STORED_PPID=$(cat "$LOCKFILE" 2>/dev/null)
  if [ "$STORED_PPID" = "$PPID" ]; then
    # Already verified this session — consume stdin and pass through
    cat > /dev/null
    exit 0
  fi
fi

# Consume stdin (required by hook protocol)
cat > /dev/null

# --- CHECK 1: jq must be available (all hooks depend on it) ---
JQ_BIN="$HOOKS_DIR/jq.exe"
if [ ! -f "$JQ_BIN" ]; then
  # Try system jq
  if ! command -v jq &>/dev/null; then
    echo "BLOCKED: Security hooks cannot function — jq is not available." >&2
    echo "Expected at: $JQ_BIN" >&2
    echo "Install jq or restore .claude/hooks/jq.exe before continuing." >&2
    exit 2
  fi
fi

# Verify jq actually runs
if ! "$JQ_BIN" --version &>/dev/null; then
  echo "BLOCKED: jq binary at $JQ_BIN is not executable or corrupted." >&2
  exit 2
fi

# --- CHECK 2: All critical hook files must exist ---
CRITICAL_HOOKS=(
  "validate-sql.sh"
  "block-external-transfer.sh"
  "block-notebook-exfil.sh"
  "block-file-deletion.sh"
  "check-credential-exposure.sh"
  "block-jira-writes.sh"
  "block-confluence-writes.sh"
  "block-permission-changes.sh"
)

MISSING=()
for hook in "${CRITICAL_HOOKS[@]}"; do
  if [ ! -f "$HOOKS_DIR/$hook" ]; then
    MISSING+=("$hook")
  fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "BLOCKED: Critical security hook files are missing:" >&2
  for m in "${MISSING[@]}"; do
    echo "  - $m" >&2
  done
  echo "Restore these files before continuing." >&2
  exit 2
fi

# --- CHECK 3: Test one hook end-to-end to confirm the full chain works ---
TEST_INPUT='{"tool_name":"Bash","tool_input":{"command":"echo selftest"}}'
TEST_RESULT=$(echo "$TEST_INPUT" | bash "$HOOKS_DIR/validate-sql.sh" 2>&1)
TEST_EXIT=$?

# Exit 0 = hook parsed input and found no violation (correct)
# Exit 2 = hook parsed input and blocked something (also means it works)
# Exit 1 = hook itself is broken
if [ $TEST_EXIT -eq 1 ]; then
  echo "BLOCKED: Security hook self-test failed (validate-sql.sh returned exit 1)." >&2
  echo "Output: $TEST_RESULT" >&2
  echo "Hooks are not functional — fix before continuing." >&2
  exit 2
fi

# All checks passed — record for this session
echo "$PPID" > "$LOCKFILE"
exit 0
