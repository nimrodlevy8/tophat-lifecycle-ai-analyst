#!/bin/bash
# Hook: Block public sharing — only allow domain-restricted (scopely.com) permissions.
# Never set type="anyone" on any Drive file. Only type="domain" with domain="scopely.com" is allowed.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Only check Drive permission tools
if [ "$TOOL" != "mcp__google-workspace__set_drive_file_permissions" ]; then
  # Block any other tool with "permission" in the name
  if echo "$TOOL" | grep -qi 'permission'; then
    echo "BLOCKED: Permission changes are not allowed on external systems." >&2
    echo "Tool attempted: $TOOL" >&2
    exit 2
  fi
  exit 0
fi

# For Drive permissions: only allow type="domain" with domain="scopely.com"
PERM_TYPE=$(echo "$INPUT" | jq -r '.tool_input.type // empty')
DOMAIN=$(echo "$INPUT" | jq -r '.tool_input.domain // empty')

if [ "$PERM_TYPE" = "anyone" ]; then
  echo "BLOCKED: Public sharing (type=\"anyone\") is not allowed." >&2
  echo "Use type=\"domain\" with domain=\"scopely.com\" instead." >&2
  exit 2
fi

if [ "$PERM_TYPE" = "domain" ] && [ "$DOMAIN" = "scopely.com" ]; then
  exit 0
fi

if [ "$PERM_TYPE" = "domain" ] && [ "$DOMAIN" != "scopely.com" ]; then
  echo "BLOCKED: Only scopely.com domain sharing is allowed, not \"$DOMAIN\"." >&2
  exit 2
fi

# Allow user/group sharing (for specific Scopely users)
if [ "$PERM_TYPE" = "user" ] || [ "$PERM_TYPE" = "group" ]; then
  # Check that email is scopely.com
  EMAIL=$(echo "$INPUT" | jq -r '.tool_input.emailAddress // .tool_input.email // empty')
  if [ -n "$EMAIL" ]; then
    if echo "$EMAIL" | grep -qi '@scopely\.com$'; then
      exit 0
    else
      echo "BLOCKED: Can only share with @scopely.com addresses, not \"$EMAIL\"." >&2
      exit 2
    fi
  fi
  exit 0
fi

# Default: block unknown permission types
echo "BLOCKED: Unknown permission type \"$PERM_TYPE\". Only domain/user/group allowed." >&2
exit 2
