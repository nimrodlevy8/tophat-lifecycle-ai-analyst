#!/bin/bash
# Hook: Ensure all MCP tool calls use @scopely.com emails for authentication.
# Blocks any Google Workspace or Atlassian tool call using a non-Scopely email.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Only check MCP tools that accept email parameters
case "$TOOL" in
  mcp__google-workspace__*|mcp__google-docs__*|mcp__google-slides__*|mcp__atlassian__*)
    ;;
  *)
    exit 0
    ;;
esac

# Check all known email parameter names
for KEY in user_google_email email emailAddress user_email account; do
  EMAIL=$(echo "$INPUT" | jq -r ".tool_input.${KEY} // empty")
  if [ -n "$EMAIL" ]; then
    # Verify it ends with @scopely.com (case-insensitive)
    if ! echo "$EMAIL" | grep -qi '@scopely\.com$'; then
      echo "BLOCKED: Non-Scopely email in MCP tool call: ${EMAIL}" >&2
      echo "Only @scopely.com accounts are allowed for authentication." >&2
      echo "Tool: $TOOL, Parameter: $KEY" >&2
      exit 2
    fi
  fi
done

exit 0
