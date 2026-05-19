#!/bin/bash
# Hook: Rule 16 — Check command output for exposed credentials.
# Fires on PostToolUse for Bash commands. Non-blocking (warning only)
# because the output already happened — but logs the violation.

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Only check Bash command outputs
if [ "$TOOL" != "Bash" ]; then
  exit 0
fi

# Get the command that was run (for context)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Skip if this is a credential-management command (user intentionally viewing)
if echo "$COMMAND" | grep -qiE '(cat.*\.env|echo.*TOKEN|printenv|env\s*$)'; then
  echo "WARNING: Credential-adjacent command detected. Ensure no secrets are exposed in output." >&2
  # Don't block — just warn
  exit 0
fi

# The actual output checking happens via the audit logger + sanitizer
# This hook serves as a runtime reminder — the real enforcement is that
# Rule 16 in CLAUDE.md prevents Claude from running commands that would
# expose credentials in the first place (no echo $TOKEN, no cat .env, etc.)

# Check if the command itself would expose credentials
if echo "$COMMAND" | grep -qiE '(echo.*\$(.*TOKEN|.*SECRET|.*KEY|.*PASS)|cat.*(\.env|credential|secret|token|\.key|\.pem))'; then
  echo "BLOCKED: Command would expose credentials in terminal output (Rule 16)." >&2
  echo "Never display passwords, tokens, or secrets. Store in .env via Write/Edit tool." >&2
  exit 2
fi

# Check for credential-as-argument (visible in ps)
if echo "$COMMAND" | grep -qiE '(--(password|token|secret|api-key|apikey)\s*[=\s]\S+)'; then
  echo "BLOCKED: Credentials passed as command-line arguments are visible in process list (Rule 16)." >&2
  echo "Source credentials from environment variables instead." >&2
  exit 2
fi

exit 0
