"""Security enforcer — unified enforcement of CLAUDE.md rules 16-21.

Validates tool inputs/outputs against data boundary, credential exposure,
deletion prevention, and query logging rules.

Usage:
    from helpers.security_enforcer import (
        check_credential_exposure,
        check_file_deletion,
        check_data_boundary,
        check_outbound_transfer,
        enforce_all,
    )

Also usable as CLI:
    python helpers/security_enforcer.py --check-output "command output text"
    python helpers/security_enforcer.py --check-command "rm -rf /data"
    python helpers/security_enforcer.py --check-url "https://example.com/api"
"""

import re
import sys
import json


class SecurityViolation(Exception):
    """Raised when a security rule is violated."""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        super().__init__(f"[Rule {rule}] {message}")


# --- Rule 16: Never expose credentials in terminal output ---

CREDENTIAL_PATTERNS = [
    (r'\bya29\.[A-Za-z0-9_\-]{20,}', 'OAuth access token'),
    (r'\b1//[A-Za-z0-9_\-]{20,}', 'OAuth refresh token'),
    (r'\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}', 'JWT'),
    (r'\bAKIA[0-9A-Z]{16}\b', 'AWS access key'),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', 'Private key'),
    (r'(password|passwd|pwd)\s*[:=]\s*\S+', 'Password in output'),
    (r'(api[_-]?key|apikey)\s*[:=]\s*\S+', 'API key in output'),
    (r'(secret[_-]?key|client[_-]?secret)\s*[:=]\s*\S+', 'Secret key in output'),
    (r'(access[_-]?token|auth[_-]?token|bearer)\s*[:=]\s*\S{20,}', 'Token in output'),
]

COMPILED_CRED_PATTERNS = [(re.compile(p, re.IGNORECASE), desc) for p, desc in CREDENTIAL_PATTERNS]


def check_credential_exposure(text: str) -> list[str]:
    """Rule 16: Check if text contains exposed credentials.

    Args:
        text: Command output or text to scan.

    Returns:
        List of violation descriptions. Empty if clean.
    """
    violations = []
    for pattern, desc in COMPILED_CRED_PATTERNS:
        if pattern.search(text):
            violations.append(f"Rule 16: Credential exposure detected — {desc}")
    return violations


# --- Rule 17: Log every data-touching query ---

def is_data_query(command: str) -> bool:
    """Rule 17: Check if a command is a data-touching query that needs logging.

    Args:
        command: The bash command string.

    Returns:
        True if this command touches data and should be logged.
    """
    indicators = [
        r'bq\s+query',
        r'SELECT\s+',
        r'psql\s+',
        r'duckdb\s+',
        r'motherduck',
    ]
    return any(re.search(p, command, re.IGNORECASE) for p in indicators)


# --- Rule 18: No file deletion without explicit instruction ---

DELETION_PATTERNS = [
    (r'\brm\s+(-[a-zA-Z]*\s+)*', 'rm command'),
    (r'\brmdir\b', 'rmdir command'),
    (r'\bdel\s+', 'del command'),
    (r'\bRemove-Item\b', 'PowerShell Remove-Item'),
    (r'\bunlink\b', 'unlink command'),
    (r'\bshred\b', 'shred command'),
]

COMPILED_DELETE_PATTERNS = [(re.compile(p, re.IGNORECASE), desc) for p, desc in DELETION_PATTERNS]


def check_file_deletion(command: str) -> list[str]:
    """Rule 18: Check if a command deletes files.

    Args:
        command: The bash command string.

    Returns:
        List of violation descriptions. Empty if clean.
    """
    violations = []
    for pattern, desc in COMPILED_DELETE_PATTERNS:
        if pattern.search(command):
            violations.append(f"Rule 18: File deletion detected — {desc}. Requires explicit user instruction.")
    return violations


def check_cloud_deletion(tool_name: str, tool_input: dict) -> list[str]:
    """Rule 18: Check if an MCP tool call deletes cloud resources.

    Args:
        tool_name: The MCP tool name.
        tool_input: The tool input parameters.

    Returns:
        List of violation descriptions. Empty if clean.
    """
    violations = []

    delete_tools = [
        'delete', 'remove', 'trash', 'destroy', 'purge',
    ]
    tool_lower = tool_name.lower()
    if any(d in tool_lower for d in delete_tools):
        violations.append(
            f"Rule 18: Cloud resource deletion attempted — {tool_name}. "
            f"Requires explicit user instruction."
        )

    return violations


# --- Rules 19, 20, 21: Data boundary enforcement ---

ALLOWED_OUTBOUND_HOSTS = [
    'googleapis.com',
    'google.com',
    'drive.google.com',
    'docs.google.com',
    'slides.google.com',
    'sheets.google.com',
    'storage.googleapis.com',
    'bigquery.googleapis.com',
    'oauth2.googleapis.com',
    'accounts.google.com',
    'scopely.atlassian.net',
    'hex.tech',
    'app.hex.tech',
    'hooks.slack.com',
]

OUTBOUND_INDICATORS = [
    (r'curl\s+.*(-X\s*(POST|PUT|PATCH)|--data|-d\s)', 'curl POST/PUT'),
    (r'wget\s+.*--post', 'wget POST'),
    (r'requests\.(post|put|patch)\s*\(', 'Python requests write'),
    (r'httpx\.(post|put|patch)\s*\(', 'Python httpx write'),
    (r'fetch\s*\(.*method.*POST', 'fetch POST'),
    (r'\bscp\s+', 'scp transfer'),
    (r'\brsync\s+', 'rsync transfer'),
    (r'\bsftp\s+', 'sftp transfer'),
    (r'\bftp\s+', 'ftp transfer'),
    (r'smtplib|send_mail|sendgrid', 'email sending'),
    (r'boto3|s3\.put_object|azure\.storage', 'non-GCP cloud upload'),
]

COMPILED_OUTBOUND = [(re.compile(p, re.IGNORECASE), desc) for p, desc in OUTBOUND_INDICATORS]


def check_data_boundary(command: str) -> list[str]:
    """Rules 19-21: Check if a command transfers data outside Scopely boundaries.

    Args:
        command: The bash command or code string.

    Returns:
        List of violation descriptions. Empty if clean.
    """
    violations = []

    for pattern, desc in COMPILED_OUTBOUND:
        if pattern.search(command):
            # Check if destination is an allowed host
            is_allowed = any(host in command.lower() for host in ALLOWED_OUTBOUND_HOSTS)
            if not is_allowed:
                violations.append(
                    f"Rule 19/20: Outbound data transfer detected — {desc}. "
                    f"Data must stay within Scopely boundaries."
                )

    return violations


def check_outbound_transfer(url: str) -> list[str]:
    """Rules 19-21: Check if a URL points outside Scopely boundaries.

    Args:
        url: URL to validate.

    Returns:
        List of violation descriptions. Empty if clean.
    """
    from urllib.parse import urlparse

    violations = []
    parsed = urlparse(url)
    host = parsed.hostname

    if not host:
        return violations

    is_allowed = any(host == h or host.endswith(f'.{h}') for h in ALLOWED_OUTBOUND_HOSTS)
    if not is_allowed:
        violations.append(
            f"Rule 19: URL outside Scopely boundaries — {host}. "
            f"Only Scopely Google Cloud and approved services allowed."
        )

    return violations


# --- Unified enforcement ---

def enforce_bash_command(command: str) -> list[str]:
    """Run all applicable checks against a Bash command.

    Args:
        command: The bash command to validate.

    Returns:
        List of all violation descriptions. Empty if clean.
    """
    violations = []
    violations.extend(check_file_deletion(command))
    violations.extend(check_data_boundary(command))
    return violations


def enforce_bash_output(output: str) -> list[str]:
    """Run all applicable checks against Bash command output (Rule 16).

    Args:
        output: The command's stdout/stderr.

    Returns:
        List of credential exposure violations. Empty if clean.
    """
    return check_credential_exposure(output)


def enforce_mcp_call(tool_name: str, tool_input: dict) -> list[str]:
    """Run all applicable checks against an MCP tool call.

    Args:
        tool_name: The MCP tool name.
        tool_input: The tool input dict.

    Returns:
        List of all violation descriptions. Empty if clean.
    """
    violations = []
    violations.extend(check_cloud_deletion(tool_name, tool_input))

    # Check URLs in tool input
    for key in ['url', 'fileUrl', 'webhook_url', 'endpoint']:
        url = tool_input.get(key)
        if url:
            violations.extend(check_outbound_transfer(url))

    return violations


def enforce_all(tool_name: str, tool_input: dict, command: str = "",
                output: str = "") -> list[str]:
    """Run all security enforcement checks.

    Args:
        tool_name: Tool name (e.g., "Bash", "mcp__google-workspace__...").
        tool_input: Tool input parameters.
        command: Bash command string (if applicable).
        output: Command output (for post-execution checks).

    Returns:
        List of all violations found. Empty if everything is clean.
    """
    violations = []

    if command:
        violations.extend(enforce_bash_command(command))
    if output:
        violations.extend(enforce_bash_output(output))
    if tool_name.startswith('mcp__'):
        violations.extend(enforce_mcp_call(tool_name, tool_input))

    return violations


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python security_enforcer.py --check-output <text>")
        print("       python security_enforcer.py --check-command <command>")
        print("       python security_enforcer.py --check-url <url>")
        print("       python security_enforcer.py --check-json <json_input>")
        sys.exit(1)

    flag = sys.argv[1]
    value = sys.argv[2]

    violations = []

    if flag == '--check-output':
        violations = enforce_bash_output(value)
    elif flag == '--check-command':
        violations = enforce_bash_command(value)
    elif flag == '--check-url':
        violations = check_outbound_transfer(value)
    elif flag == '--check-json':
        data = json.loads(value)
        tool_name = data.get('tool_name', '')
        tool_input = data.get('tool_input', {})
        command = tool_input.get('command', '')
        violations = enforce_all(tool_name, tool_input, command=command)
    else:
        print(f"Unknown flag: {flag}", file=sys.stderr)
        sys.exit(1)

    if violations:
        for v in violations:
            print(f"VIOLATION: {v}", file=sys.stderr)
        sys.exit(2)
    else:
        print("OK: All security checks passed.")
        sys.exit(0)
