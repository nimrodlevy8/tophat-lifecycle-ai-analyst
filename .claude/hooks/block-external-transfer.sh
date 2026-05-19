#!/bin/bash
# Hook: Block data transfer to external (non-Scopely) destinations.
# Only allowed paths: local laptop <-> Scopely Google Cloud.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Skip if not a Bash command
if [ -z "$COMMAND" ]; then
  exit 0
fi

CMD_UPPER=$(echo "$COMMAND" | tr '[:lower:]' '[:upper:]')

# Block curl/wget POST to non-Google domains
if echo "$COMMAND" | grep -qiE '(curl|wget).*(-X\s*POST|--data|--upload|-d\s)'; then
  # Allow Google APIs
  if echo "$COMMAND" | grep -qi 'googleapis.com\|google.com\|drive.google'; then
    exit 0
  fi
  echo "BLOCKED: Outbound data transfer detected. Data must stay within Scopely boundaries." >&2
  echo "Only local <-> Scopely Google Cloud transfers are allowed." >&2
  exit 2
fi

# Block scp, rsync, ftp to external
if echo "$COMMAND" | grep -qiE '^\s*(scp|rsync|ftp|sftp)\s'; then
  echo "BLOCKED: External file transfer detected. Data must stay within Scopely boundaries." >&2
  exit 2
fi

exit 0
