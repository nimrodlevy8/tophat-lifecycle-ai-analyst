#!/bin/bash
# Hook: Rule 18 — Block file deletion commands unless explicitly instructed.
# Catches rm, rmdir, del, unlink, shred in Bash commands.
# Also catches MCP tools that delete cloud resources (Drive, GCS, BQ, JIRA).
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

if [ "$TOOL" = "Bash" ]; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

  # Check for file deletion commands
  if echo "$COMMAND" | grep -qiE '^\s*(rm|rmdir|del|unlink|shred)\s'; then
    echo "BLOCKED: File deletion requires explicit user instruction (Rule 18)." >&2
    echo "Command: $COMMAND" >&2
    echo "Ask the user to confirm before deleting files." >&2
    exit 2
  fi

  # Also catch rm inside pipes or after && / ;
  if echo "$COMMAND" | grep -qiE '(&&|;|\|)\s*(rm|rmdir|del|unlink)\s'; then
    echo "BLOCKED: File deletion in compound command requires explicit user instruction (Rule 18)." >&2
    echo "Command: $COMMAND" >&2
    exit 2
  fi

  # Catch Google Cloud deletion commands
  if echo "$COMMAND" | grep -qiE '(gcloud.*delete|gsutil\s+rm|bq\s+rm)'; then
    echo "BLOCKED: Cloud resource deletion requires explicit user instruction (Rule 18)." >&2
    echo "Command: $COMMAND" >&2
    exit 2
  fi

fi

# Check MCP tools with "delete" in the name
if echo "$TOOL" | grep -qiE '(delete|remove|trash|destroy|purge)'; then
  echo "BLOCKED: Cloud resource deletion via $TOOL requires explicit user instruction (Rule 18)." >&2
  echo "Never delete files from Google Cloud, JIRA, or any external system without user confirmation." >&2
  exit 2
fi

exit 0
