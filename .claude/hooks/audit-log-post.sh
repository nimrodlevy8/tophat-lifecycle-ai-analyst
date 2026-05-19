#!/bin/bash
# Hook: Log MCP operations AFTER execution for audit trail.
# Fires on all MCP tool calls (Google, Atlassian, Hex, Slack).
# Non-blocking — always exits 0.

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

# Log via Python helper (non-blocking — swallow errors)
echo "$INPUT" | python helpers/audit_logger.py --post 2>/dev/null || true

exit 0
