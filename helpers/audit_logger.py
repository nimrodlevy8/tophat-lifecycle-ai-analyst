"""MCP operation audit logger — traces all external system interactions.

Logs every MCP operation (BigQuery, Hex, Google Workspace, JIRA, Confluence,
Slack) to a JSONL audit trail for compliance and debugging.

Usage:
    from helpers.audit_logger import log_mcp_operation, log_pre, log_post

    # Manual logging
    log_mcp_operation(
        mcp_server="google-workspace",
        operation="create_doc",
        resource="Doc: Q1 Analysis",
        user="alireza.hamidi@scopely.com",
        data_summary="Created new Google Doc",
        destination="Google Drive"
    )

    # Hook-style logging (called from shell hooks via CLI)
    # python helpers/audit_logger.py --pre '{"tool_name": "...", "tool_input": {...}}'
    # python helpers/audit_logger.py --post '{"tool_name": "...", "tool_input": {...}}'

Log location: working/mcp_audit.jsonl
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from helpers.credential_sanitizer import sanitize, sanitize_dict


AUDIT_LOG_PATH = Path("working/mcp_audit.jsonl")

MCP_SERVER_MAP = {
    "mcp__google-workspace__": "google-workspace",
    "mcp__google-docs__": "google-docs",
    "mcp__google-slides__": "google-slides",
    "mcp__atlassian__": "atlassian",
    "mcp__hex__": "hex",
    "mcp__slack__": "slack",
}

SENSITIVE_KEYS = {'password', 'token', 'secret', 'key', 'credentials', 'auth'}


def _detect_server(tool_name: str) -> str:
    for prefix, server in MCP_SERVER_MAP.items():
        if tool_name.startswith(prefix):
            return server
    if "bq" in tool_name.lower() or "bigquery" in tool_name.lower():
        return "bigquery"
    return "unknown"


def _extract_operation(tool_name: str) -> str:
    for prefix in MCP_SERVER_MAP:
        if tool_name.startswith(prefix):
            return tool_name[len(prefix):]
    return tool_name


def _extract_resource(tool_input: dict, operation: str) -> str:
    resource_keys = [
        'document_id', 'presentation_id', 'file_id', 'page_id', 'pageId',
        'issue_key', 'issueKey', 'project_key', 'projectKey',
        'thread_id', 'project_id', 'file_name', 'title', 'folder_name',
        'channel', 'channel_id',
    ]
    for key in resource_keys:
        val = tool_input.get(key)
        if val:
            return f"{key}={val}"
    return operation


def _extract_user(tool_input: dict) -> str:
    email_keys = ['user_google_email', 'email', 'emailAddress', 'user_email', 'account']
    for key in email_keys:
        val = tool_input.get(key)
        if val:
            return val
    return "unknown"


def _extract_destination(tool_name: str, tool_input: dict) -> str:
    server = _detect_server(tool_name)
    dest_map = {
        "google-workspace": "Google Drive",
        "google-docs": "Google Docs",
        "google-slides": "Google Slides",
        "atlassian": "Atlassian Cloud (scopely.atlassian.net)",
        "hex": "Hex (app.hex.tech)",
        "slack": "Slack (Scopely workspace)",
        "bigquery": "BigQuery (dwh-adev-tophat)",
    }
    return dest_map.get(server, "unknown")


def _summarize_data(tool_input: dict) -> str:
    safe_input = sanitize_dict(tool_input)
    for k, v in safe_input.items():
        if isinstance(v, str) and len(v) > 200:
            safe_input[k] = v[:200] + "..."
    return json.dumps(safe_input, default=str, ensure_ascii=False)[:500]


def log_mcp_operation(
    mcp_server: str,
    operation: str,
    resource: str,
    user: str,
    data_summary: str,
    destination: str,
    status: str = "executed",
    duration_ms: int | None = None,
    result_summary: str | None = None,
    error: str | None = None,
) -> dict:
    """Log an MCP operation to the audit trail.

    Args:
        mcp_server: Which MCP server (google-workspace, atlassian, hex, etc.)
        operation: The specific operation (create_doc, search, get_thread, etc.)
        resource: What resource was accessed/modified (doc ID, issue key, etc.)
        user: The authenticated user email
        data_summary: Brief description of data involved (redacted if sensitive)
        destination: Where the operation targets (Google Drive, JIRA, etc.)
        status: "pre" (about to execute), "post" (completed), "blocked", "error"
        duration_ms: How long the operation took (post only)
        result_summary: Brief result description (post only)
        error: Error message if failed

    Returns:
        The log entry dict that was written.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mcp_server": mcp_server,
        "operation": operation,
        "resource": resource,
        "user": user,
        "data_summary": data_summary,
        "destination": destination,
        "status": status,
    }

    if duration_ms is not None:
        entry["duration_ms"] = duration_ms
    if result_summary:
        entry["result_summary"] = result_summary
    if error:
        entry["error"] = error

    _write_entry(entry)
    return entry


def log_pre(tool_name: str, tool_input: dict) -> dict:
    """Log a pre-execution MCP operation (called from PreToolUse hook).

    Args:
        tool_name: Full MCP tool name (e.g., mcp__google-workspace__create_doc)
        tool_input: The tool input parameters dict.

    Returns:
        The log entry dict.
    """
    server = _detect_server(tool_name)
    operation = _extract_operation(tool_name)
    resource = _extract_resource(tool_input, operation)
    user = _extract_user(tool_input)
    destination = _extract_destination(tool_name, tool_input)
    data_summary = _summarize_data(tool_input)

    return log_mcp_operation(
        mcp_server=server,
        operation=operation,
        resource=resource,
        user=user,
        data_summary=data_summary,
        destination=destination,
        status="pre",
    )


def log_post(tool_name: str, tool_input: dict, duration_ms: int | None = None,
             result_summary: str | None = None, error: str | None = None) -> dict:
    """Log a post-execution MCP operation (called from PostToolUse hook).

    Args:
        tool_name: Full MCP tool name.
        tool_input: The tool input parameters dict.
        duration_ms: Execution duration in milliseconds.
        result_summary: Brief description of the result.
        error: Error message if the operation failed.

    Returns:
        The log entry dict.
    """
    server = _detect_server(tool_name)
    operation = _extract_operation(tool_name)
    resource = _extract_resource(tool_input, operation)
    user = _extract_user(tool_input)
    destination = _extract_destination(tool_name, tool_input)
    data_summary = _summarize_data(tool_input)

    status = "error" if error else "post"

    return log_mcp_operation(
        mcp_server=server,
        operation=operation,
        resource=resource,
        user=user,
        data_summary=data_summary,
        destination=destination,
        status=status,
        duration_ms=duration_ms,
        result_summary=result_summary,
        error=error,
    )


def log_bq_query(sql: str, user: str = "alireza.hamidi@scopely.com",
                 project: str = "dwh-adev-tophat", status: str = "executed",
                 duration_ms: int | None = None, rows_returned: int | None = None,
                 error: str | None = None) -> dict:
    """Log a BigQuery query execution.

    Args:
        sql: The SQL query (will be truncated for logging).
        user: The authenticated user.
        project: The BQ project ID.
        duration_ms: Query duration.
        rows_returned: Number of rows in the result.
        error: Error message if query failed.

    Returns:
        The log entry dict.
    """
    sql_summary = sql.strip()[:300] + ("..." if len(sql.strip()) > 300 else "")

    result_summary = None
    if rows_returned is not None:
        result_summary = f"{rows_returned} rows returned"

    return log_mcp_operation(
        mcp_server="bigquery",
        operation="query",
        resource=f"project={project}",
        user=user,
        data_summary=sql_summary,
        destination=f"BigQuery ({project})",
        status=status,
        duration_ms=duration_ms,
        result_summary=result_summary,
        error=error,
    )


def read_audit_log(last_n: int | None = None) -> list[dict]:
    """Read entries from the audit log.

    Args:
        last_n: If specified, return only the last N entries.

    Returns:
        List of log entry dicts.
    """
    if not AUDIT_LOG_PATH.exists():
        return []

    entries = []
    with open(AUDIT_LOG_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if last_n:
        return entries[-last_n:]
    return entries


def summary_report(entries: list[dict] | None = None) -> str:
    """Generate a summary report of audit log entries.

    Args:
        entries: List of entries to summarize (reads log if None).

    Returns:
        Formatted summary string.
    """
    if entries is None:
        entries = read_audit_log()

    if not entries:
        return "No audit log entries found."

    by_server = {}
    by_status = {}
    for e in entries:
        server = e.get("mcp_server", "unknown")
        status = e.get("status", "unknown")
        by_server[server] = by_server.get(server, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    lines = [
        f"Audit Log Summary ({len(entries)} entries)",
        f"{'='*40}",
        "",
        "By server:",
    ]
    for server, count in sorted(by_server.items(), key=lambda x: -x[1]):
        lines.append(f"  {server}: {count}")

    lines.append("")
    lines.append("By status:")
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        lines.append(f"  {status}: {count}")

    errors = [e for e in entries if e.get("status") == "error"]
    if errors:
        lines.append("")
        lines.append(f"Errors ({len(errors)}):")
        for e in errors[-5:]:
            lines.append(f"  [{e.get('timestamp', '?')}] {e.get('operation', '?')}: {e.get('error', '?')}")

    return "\n".join(lines)


def _write_entry(entry: dict):
    """Append a log entry to the audit file."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, default=str, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python audit_logger.py --pre '<json>'")
        print("       python audit_logger.py --post '<json>'")
        print("       python audit_logger.py --bq '<sql>'")
        print("       python audit_logger.py --summary")
        print("       python audit_logger.py --tail [N]")
        sys.exit(1)

    flag = sys.argv[1]

    if flag == '--summary':
        print(summary_report())
        sys.exit(0)

    if flag == '--tail':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        entries = read_audit_log(last_n=n)
        for e in entries:
            ts = e.get("timestamp", "?")[:19]
            status = e.get("status", "?")
            op = e.get("operation", "?")
            server = e.get("mcp_server", "?")
            print(f"[{ts}] {status:6s} {server}/{op}")
        sys.exit(0)

    if flag == '--pre':
        data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        entry = log_pre(tool_name, tool_input)
        print(json.dumps(entry))
        sys.exit(0)

    if flag == '--post':
        data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        entry = log_post(tool_name, tool_input)
        print(json.dumps(entry))
        sys.exit(0)

    if flag == '--bq':
        sql = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        entry = log_bq_query(sql)
        print(json.dumps(entry))
        sys.exit(0)

    print(f"Unknown flag: {flag}", file=sys.stderr)
    sys.exit(1)
