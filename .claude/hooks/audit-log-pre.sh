#!/bin/bash
# Hook: Log MCP operations BEFORE execution for audit trail.
# Fires on all MCP tool calls (Google, Atlassian, Hex, Slack).
# Non-blocking — always exits 0 (logging failure should not block operations).

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Only log MCP operations
case "$TOOL" in
  mcp__*)
    ;;
  *)
    exit 0
    ;;
esac

# Also log bq query commands
if echo "$TOOL" | grep -qi 'bash'; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  if ! echo "$COMMAND" | grep -qi 'bq.*query'; then
    exit 0
  fi
fi

# Log via Python helper (non-blocking — swallow errors)
echo "$INPUT" | python helpers/audit_logger.py --pre 2>/dev/null || true

exit 0
