#!/bin/bash
# Hook: Block notebook/code creation that exports data to external URLs.
# Fires on Edit, Write (for code files), and Bash (for hex cell create/update).
# Blocks: requests.post/put/patch to non-Scopely URLs, webhook calls,
# external API keys, publish/share commands to external services.
set -e
# Use local jq binary
JQ_BIN="$(cd "$(dirname "$0")" && pwd)/jq.exe"
jq() { "$JQ_BIN" "$@"; }

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Determine content to inspect based on tool type
CONTENT=""
if [ "$TOOL" = "Write" ]; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
  # Only check code files (py, ipynb, sql, hex yaml)
  case "$FILE_PATH" in
    *.py|*.ipynb|*.yaml|*.yml|*.sql|*.sh)
      CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')
      ;;
    *)
      exit 0
      ;;
  esac
elif [ "$TOOL" = "Edit" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // empty')
elif [ "$TOOL" = "Bash" ]; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  # Check hex cell create/update commands
  if echo "$COMMAND" | grep -qi 'hex.*cell.*\(create\|update\)'; then
    CONTENT="$COMMAND"
  else
    exit 0
  fi
else
  exit 0
fi

# Skip if no content to check
if [ -z "$CONTENT" ]; then
  exit 0
fi

# --- Check for external data exfiltration patterns ---

# 1. HTTP client calls to non-Scopely URLs
# Match requests.post/put/patch/delete with URLs that aren't Google/Scopely
if echo "$CONTENT" | grep -qiE 'requests\.(post|put|patch|delete)\s*\('; then
  # Check if the URL is to an allowed domain
  if echo "$CONTENT" | grep -iE 'requests\.(post|put|patch|delete)' | grep -qivE '(googleapis\.com|google\.com|scopely|hex\.tech|atlassian\.net)'; then
    echo "BLOCKED: Notebook code contains HTTP write to external URL." >&2
    echo "All data must stay within Scopely boundaries. No requests.post/put/patch to external APIs." >&2
    exit 2
  fi
fi

# 2. urllib/httpx/aiohttp POST to external
if echo "$CONTENT" | grep -qiE '(urlopen|httpx\.(post|put|patch)|aiohttp.*session\.(post|put|patch))'; then
  if echo "$CONTENT" | grep -iE '(urlopen|httpx|aiohttp)' | grep -qivE '(googleapis\.com|google\.com|scopely|hex\.tech|atlassian\.net)'; then
    echo "BLOCKED: Notebook code contains HTTP client sending data externally." >&2
    exit 2
  fi
fi

# 3. Webhook URLs (Slack incoming webhooks are OK if Scopely workspace)
if echo "$CONTENT" | grep -qiE 'webhook.*http[s]?://'; then
  if echo "$CONTENT" | grep -iE 'webhook' | grep -qivE '(hooks\.slack\.com|scopely|googleapis\.com)'; then
    echo "BLOCKED: Notebook code contains external webhook call." >&2
    exit 2
  fi
fi

# 4. smtp/email sending
if echo "$CONTENT" | grep -qiE '(smtplib|send_mail|sendgrid|mailgun|ses_client)'; then
  echo "BLOCKED: Notebook code contains email sending capability." >&2
  echo "Use Scopely Slack or Google Docs for sharing analysis outputs." >&2
  exit 2
fi

# 5. S3/Azure/non-GCP cloud uploads
if echo "$CONTENT" | grep -qiE '(boto3|s3\.put_object|azure\.storage|upload_blob)'; then
  echo "BLOCKED: Notebook code contains non-GCP cloud upload (AWS/Azure)." >&2
  echo "Only Scopely Google Cloud (Drive, GCS, BigQuery) is allowed." >&2
  exit 2
fi

# 6. FTP/SCP/rsync in code
if echo "$CONTENT" | grep -qiE '(ftplib|paramiko|subprocess.*scp|subprocess.*rsync)'; then
  echo "BLOCKED: Notebook code contains file transfer protocol (FTP/SCP/rsync)." >&2
  exit 2
fi

# 7. Public sharing/publish commands
if echo "$CONTENT" | grep -qiE '(publish_public|make_public|share_link.*anyone|visibility.*public)'; then
  echo "BLOCKED: Notebook code contains public sharing/publishing." >&2
  echo "All outputs must be domain-restricted to scopely.com." >&2
  exit 2
fi

exit 0
