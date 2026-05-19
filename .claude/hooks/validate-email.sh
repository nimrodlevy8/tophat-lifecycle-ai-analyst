#!/bin/bash
# Hook: Block non-@scopely.com emails from being written to files.
# Fires on PreToolUse for Edit and Write tools.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Extract content to check based on tool type
if [ "$TOOL" = "Write" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')
elif [ "$TOOL" = "Edit" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // empty')
else
  exit 0
fi

# Skip if no content
if [ -z "$CONTENT" ]; then
  exit 0
fi

# Find emails that are NOT @scopely.com
# Pattern: word chars/dots/etc @ domain . tld
BAD_EMAILS=$(echo "$CONTENT" | grep -oP '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | grep -iv '@scopely\.com' || true)

if [ -n "$BAD_EMAILS" ]; then
  echo "BLOCKED: Non-Scopely email address detected in content:" >&2
  echo "$BAD_EMAILS" | head -5 >&2
  echo "Only @scopely.com email addresses are allowed." >&2
  exit 2
fi

exit 0
