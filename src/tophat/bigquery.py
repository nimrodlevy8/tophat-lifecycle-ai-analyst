"""BigQuery client for running queries."""

from google.cloud import bigquery

_client: bigquery.Client | None = None


def get_client() -> bigquery.Client:
    global _client
    if _client is None:
        _client = bigquery.Client()
    return _client


def run_query(sql: str, dry_run: bool = False) -> str:
    """Execute a query and return formatted results."""
    client = get_client()

    job_config = bigquery.QueryJobConfig(dry_run=dry_run)
    query_job = client.query(sql, job_config=job_config)

    if dry_run:
        bytes_scanned = query_job.total_bytes_processed
        gb = bytes_scanned / (1024**3)
        return f"Estimated scan: {gb:.2f} GB ({bytes_scanned:,} bytes)"

    results = query_job.result()
    rows = [dict(row) for row in results]

    if not rows:
        return "Query returned no results."

    return _format_results(rows)


def _format_results(rows: list[dict]) -> str:
    """Format query results as a readable table."""
    if not rows:
        return ""

    headers = list(rows[0].keys())
    lines = [" | ".join(headers), " | ".join("-" * len(h) for h in headers)]

    for row in rows[:100]:
        lines.append(" | ".join(str(row.get(h, "")) for h in headers))

    if len(rows) > 100:
        lines.append(f"\n... and {len(rows) - 100} more rows")

    return "\n".join(lines)
