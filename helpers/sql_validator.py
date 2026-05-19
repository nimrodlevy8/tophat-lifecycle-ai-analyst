"""SQL safety validator — blocks destructive operations in BigQuery queries.

Usage:
    from helpers.sql_validator import validate_bigquery_sql
    validate_bigquery_sql(sql)  # raises SecurityError if blocked

Also usable as CLI:
    python helpers/sql_validator.py "SELECT * FROM table"
    python helpers/sql_validator.py --file query.sql
"""

import re
import sys


class SecurityError(Exception):
    pass


def validate_bigquery_sql(sql: str, allow_insert: bool = False) -> str:
    """Block writes except INSERT for temp tables.

    Args:
        sql: The SQL query string to validate.
        allow_insert: If True, allows INSERT statements (default False).

    Returns:
        The original SQL string if validation passes.

    Raises:
        SecurityError: If the SQL contains a blocked operation.
    """
    sql_upper = sql.upper()

    # Strip comments to avoid false positives on commented-out code
    sql_clean = re.sub(r'--.*$', '', sql_upper, flags=re.MULTILINE)
    sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)

    blocked = ['DELETE', 'UPDATE', 'DROP', 'TRUNCATE', 'ALTER', 'MERGE']
    for keyword in blocked:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_clean):
            raise SecurityError(
                f"BigQuery write operation blocked: {keyword}. "
                f"This project is read-only. No data modifications allowed."
            )

    if re.search(r'\bINSERT\b', sql_clean) and not allow_insert:
        raise SecurityError(
            "INSERT not allowed. This project is read-only."
        )

    if re.search(r'\bCREATE\b', sql_clean):
        if not re.search(r'\bCREATE\s+(TEMP|TEMPORARY)\b', sql_clean):
            raise SecurityError(
                "Only CREATE TEMP TABLE allowed. "
                "Permanent table creation is blocked."
            )

    return sql


LARGE_TABLE_PATTERNS = [
    r'\bSTD_tophat\b',
    r'\bfac_intraday\b',
    r'\bfac_daily\b',
    r'\bv_f_user_standard\b',
]


class LargeResultWarning(Exception):
    """Warning (not blocking) for queries likely to return >1M rows."""
    pass


def check_unbounded_query(sql: str) -> str | None:
    """Check if a query is likely to return a very large result set.

    Returns a warning message if the query looks unbounded, or None if OK.
    Does NOT raise — caller decides whether to block or warn.

    Args:
        sql: The SQL query string to check.

    Returns:
        Warning message string if query appears unbounded, None otherwise.
    """
    sql_upper = sql.upper()
    sql_clean = re.sub(r'--.*$', '', sql_upper, flags=re.MULTILINE)
    sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)

    has_select_star = bool(re.search(r'SELECT\s+\*', sql_clean))
    has_limit = bool(re.search(r'\bLIMIT\b', sql_clean))
    has_group_by = bool(re.search(r'\bGROUP\s+BY\b', sql_clean))
    has_count = bool(re.search(r'\b(COUNT\(|APPROX_)', sql_clean))

    is_large_table = any(
        re.search(p, sql, re.IGNORECASE) for p in LARGE_TABLE_PATTERNS
    )

    if is_large_table and has_select_star and not has_limit:
        return (
            "SELECT * without LIMIT on a large table. "
            "This will likely return >1M rows. "
            "Add LIMIT, GROUP BY, or run COUNT(*) first to estimate."
        )

    if is_large_table and not has_group_by and not has_limit and not has_count:
        return (
            "Query on large table without GROUP BY or LIMIT. "
            "Aggregate at the SQL level — do not pull raw rows into memory. "
            "Add GROUP BY, LIMIT, or use COUNT(*) to estimate row count first."
        )

    return None


def generate_count_query(sql: str) -> str:
    """Generate a COUNT(*) wrapper to estimate row count before executing.

    Args:
        sql: The original SQL query.

    Returns:
        A wrapped query that returns the row count.
    """
    sql_stripped = sql.strip().rstrip(';')
    return f"SELECT COUNT(*) AS estimated_rows FROM ({sql_stripped})"


def validate_no_external_email(text: str) -> str:
    """Block non-scopely.com email addresses in content.

    Args:
        text: Content to check for email addresses.

    Returns:
        The original text if validation passes.

    Raises:
        SecurityError: If a non-scopely.com email is found.
    """
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    for email in emails:
        if not email.endswith('@scopely.com'):
            raise SecurityError(
                f"Non-Scopely email blocked: {email}. "
                f"Only @scopely.com addresses are allowed."
            )
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sql_validator.py <sql_string>")
        print("       python sql_validator.py --file <path>")
        sys.exit(1)

    if sys.argv[1] == '--file':
        with open(sys.argv[2], 'r') as f:
            sql = f.read()
    else:
        sql = sys.argv[1]

    try:
        validate_bigquery_sql(sql)
        print("OK: Query passes safety validation.")
        sys.exit(0)
    except SecurityError as e:
        print(f"BLOCKED: {e}", file=sys.stderr)
        sys.exit(1)
