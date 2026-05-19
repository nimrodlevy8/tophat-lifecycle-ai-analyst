#!/bin/bash
# Hook: Block ALL JIRA write/modify operations.
# JIRA is strictly read-only — no creates, updates, deletes, transitions.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Block any JIRA MCP tool that modifies state
case "$TOOL" in
  mcp__atlassian__createJiraIssue|\
  mcp__atlassian__editJiraIssue|\
  mcp__atlassian__addCommentToJiraIssue|\
  mcp__atlassian__addWorklogToJiraIssue|\
  mcp__atlassian__transitionJiraIssue|\
  mcp__atlassian__createIssueLink)
    echo "BLOCKED: JIRA is strictly read-only. No modifications allowed." >&2
    echo "Tool attempted: $TOOL" >&2
    exit 2
    ;;
esac

exit 0
