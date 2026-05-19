#!/bin/bash
# Hook: Block Confluence writes UNLESS targeting the approved page.
# Only page 1627553978 (Ad Hoc Output Examples in TOP space) is writable.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Only check Confluence write tools
case "$TOOL" in
  mcp__atlassian__createConfluencePage|\
  mcp__atlassian__updateConfluencePage|\
  mcp__atlassian__createConfluenceFooterComment|\
  mcp__atlassian__createConfluenceInlineComment)
    ;;
  *)
    exit 0
    ;;
esac

# For updateConfluencePage, check if it's the allowed page
if [ "$TOOL" = "mcp__atlassian__updateConfluencePage" ]; then
  PAGE_ID=$(echo "$INPUT" | jq -r '.tool_input.pageId // .tool_input.page_id // empty')
  if [ "$PAGE_ID" = "1627553978" ]; then
    exit 0
  fi
fi

echo "BLOCKED: Confluence is read-only except page 1627553978 (Ad Hoc Output Examples)." >&2
echo "Tool attempted: $TOOL" >&2
exit 2
