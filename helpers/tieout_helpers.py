"""Source Tie-Out Helpers — DEPRECATED.

This module is a backward-compatibility shim. The dual-path (pandas vs DuckDB)
verification paradigm has been replaced by cross-verification (same-source,
different-calculation-path checks).

Migration guide:
    OLD (tieout_helpers)              NEW
    ─────────────────────────────     ────────────────────────────
    compare_profiles()                cross_verification.run_*()
    format_tieout_table()             cross_verification.format_verification_table()
    overall_status()                  cross_verification.overall_status()
    check_null_concentration()        data_quality_extras.check_null_concentration()
    check_outliers()                  data_quality_extras.check_outliers()
    safe_check_outliers()             data_quality_extras.safe_check_outliers()

Functions that remain useful (read_source_direct, profile_dataframe) are kept
here without deprecation — they are source-agnostic utilities.

Usage:
    # New preferred imports:
    from helpers.cross_verification import (
        run_boundary_checks, run_parts_to_whole,
        run_ratio_recompute, run_algebraic_identity,
        format_verification_table, overall_status,
    )
    from helpers.data_quality_extras import (
        check_null_concentration, check_outliers, safe_check_outliers,
    )

    # Legacy imports still work but emit DeprecationWarning:
    from helpers.tieout_helpers import compare_profiles  # warns
"""

import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Re-export from new modules — these are the canonical locations now
from helpers.data_quality_extras import (
    check_null_concentration,
    check_outliers,
    safe_check_outliers,
)
from helpers.cross_verification import (
    format_verification_table,
    overall_status as _new_overall_status,
)


# ---------------------------------------------------------------------------
# Still useful: read source files directly via pandas
# ---------------------------------------------------------------------------

def read_source_direct(path, dtype=None):
    """Read a data file via pandas only — no DuckDB in the code path.

    Supports CSV, Excel (.xlsx/.xls), Parquet, and JSON.

    Args:
        path: File path (str or Path).
        dtype: Optional dict of column name -> dtype for CSV files.

    Returns:
        pandas.DataFrame
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, dtype=dtype)
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif suffix == ".parquet":
        return pd.read_parquet(path)
    elif suffix == ".json":
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


# ---------------------------------------------------------------------------
# Still useful: profile a DataFrame (source-agnostic)
# ---------------------------------------------------------------------------

def profile_dataframe(df, label="source"):
    """Compute foundational metrics for a DataFrame.

    Args:
        df: pandas.DataFrame to profile.
        label: Human-readable label for this profile.

    Returns:
        dict with keys: label, row_count, columns, null_counts,
        numeric_sums, distinct_counts, date_ranges
    """
    profile = {
        "label": label,
        "row_count": len(df),
        "columns": sorted(df.columns.tolist()),
        "null_counts": {},
        "numeric_sums": {},
        "distinct_counts": {},
        "date_ranges": {},
    }

    if len(df) == 0:
        for col in df.columns:
            profile["null_counts"][col] = 0
            profile["distinct_counts"][col] = 0
            if pd.api.types.is_numeric_dtype(df[col]):
                profile["numeric_sums"][col] = 0.0
        profile["warning"] = "EMPTY_DATAFRAME"
        return profile

    for col in df.columns:
        profile["null_counts"][col] = int(df[col].isna().sum())
        profile["distinct_counts"][col] = int(df[col].nunique())

        if pd.api.types.is_numeric_dtype(df[col]):
            profile["numeric_sums"][col] = float(df[col].sum())

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            non_null = df[col].dropna()
            if len(non_null) > 0:
                profile["date_ranges"][col] = {
                    "min": str(non_null.min()),
                    "max": str(non_null.max()),
                }

    return profile


# ---------------------------------------------------------------------------
# DEPRECATED: dual-path comparison functions
# ---------------------------------------------------------------------------

_ROW_TOL = 0
_NUMERIC_TOL = 0.0001
_ABS_FLOOR = 0.01


def compare_profiles(source_profile, duckdb_profile):
    """Compare two profiles and return a list of check results.

    .. deprecated::
        Use ``helpers.cross_verification.run_*()`` functions instead.
        The dual-path paradigm (pandas vs DuckDB) has been replaced by
        same-source, different-calculation-path cross-verification.
    """
    warnings.warn(
        "compare_profiles() is deprecated. Use helpers.cross_verification "
        "run_boundary_checks(), run_parts_to_whole(), run_ratio_recompute(), "
        "and run_algebraic_identity() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    results = []
    src = source_profile
    db = duckdb_profile

    # Empty DataFrame guard
    src_empty = src.get("warning") == "EMPTY_DATAFRAME"
    db_empty = db.get("warning") == "EMPTY_DATAFRAME"
    if src_empty or db_empty:
        empty_labels = []
        if src_empty:
            empty_labels.append(src["label"])
        if db_empty:
            empty_labels.append(db["label"])
        results.append({
            "check": "Empty DataFrame",
            "metric": "row_count",
            "source_value": src["row_count"],
            "duckdb_value": db["row_count"],
            "status": "WARN",
            "detail": f"Empty DataFrame detected in: {', '.join(empty_labels)}",
        })

    # Row count
    results.append(_compare_exact(
        "Row count", "rows", src["row_count"], db["row_count"],
    ))

    # Column names
    missing_in_db = set(src["columns"]) - set(db["columns"])
    missing_in_src = set(db["columns"]) - set(src["columns"])
    if not missing_in_db and not missing_in_src:
        results.append({
            "check": "Column names", "metric": "columns",
            "source_value": len(src["columns"]),
            "duckdb_value": len(db["columns"]),
            "status": "PASS", "detail": "All columns match",
        })
    else:
        detail_parts = []
        if missing_in_db:
            detail_parts.append(f"In source but not DuckDB: {sorted(missing_in_db)}")
        if missing_in_src:
            detail_parts.append(f"In DuckDB but not source: {sorted(missing_in_src)}")
        results.append({
            "check": "Column names", "metric": "columns",
            "source_value": len(src["columns"]),
            "duckdb_value": len(db["columns"]),
            "status": "FAIL", "detail": "; ".join(detail_parts),
        })

    # Null counts per column
    common_cols = set(src["columns"]) & set(db["columns"])
    for col in sorted(common_cols):
        src_nulls = src["null_counts"].get(col, 0)
        db_nulls = db["null_counts"].get(col, 0)
        results.append(_compare_exact("Null count", col, src_nulls, db_nulls))

    # Numeric sums
    common_numeric = set(src["numeric_sums"].keys()) & set(db["numeric_sums"].keys())
    for col in sorted(common_numeric):
        results.append(_compare_within_tolerance(
            "Numeric sum", col,
            src["numeric_sums"][col], db["numeric_sums"][col],
            _NUMERIC_TOL,
        ))

    # Asymmetric numeric columns
    for col in sorted(set(src["numeric_sums"].keys()) - set(db["numeric_sums"].keys())):
        results.append({
            "check": "Numeric sum", "metric": col,
            "source_value": src["numeric_sums"][col],
            "duckdb_value": "N/A (non-numeric)",
            "status": "WARN",
            "detail": f"Column '{col}' is numeric in source but not in DuckDB",
        })
    for col in sorted(set(db["numeric_sums"].keys()) - set(src["numeric_sums"].keys())):
        results.append({
            "check": "Numeric sum", "metric": col,
            "source_value": "N/A (non-numeric)",
            "duckdb_value": db["numeric_sums"][col],
            "status": "WARN",
            "detail": f"Column '{col}' is numeric in DuckDB but not in source",
        })

    # Distinct counts
    for col in sorted(common_cols):
        results.append(_compare_exact(
            "Distinct count", col,
            src["distinct_counts"].get(col, 0),
            db["distinct_counts"].get(col, 0),
        ))

    # Date ranges
    common_dates = set(src["date_ranges"].keys()) & set(db["date_ranges"].keys())
    for col in sorted(common_dates):
        src_min = src["date_ranges"][col]["min"]
        db_min = db["date_ranges"][col]["min"]
        src_max = src["date_ranges"][col]["max"]
        db_max = db["date_ranges"][col]["max"]
        try:
            min_match = pd.to_datetime(src_min).date() == pd.to_datetime(db_min).date()
            max_match = pd.to_datetime(src_max).date() == pd.to_datetime(db_max).date()
        except (ValueError, TypeError):
            min_match = src_min == db_min
            max_match = src_max == db_max
        status = "PASS" if (min_match and max_match) else "FAIL"
        results.append({
            "check": "Date range", "metric": col,
            "source_value": f"{src_min} to {src_max}",
            "duckdb_value": f"{db_min} to {db_max}",
            "status": status,
            "detail": "Range matches" if status == "PASS" else "Date range mismatch",
        })

    return results


def _compare_exact(check, metric, src_val, db_val):
    """Compare two values for exact equality."""
    status = "PASS" if src_val == db_val else "FAIL"
    detail = "Match" if status == "PASS" else f"Mismatch: {src_val} vs {db_val}"
    return {
        "check": check, "metric": metric,
        "source_value": src_val, "duckdb_value": db_val,
        "status": status, "detail": detail,
    }


def _compare_within_tolerance(check, metric, src_val, db_val, tolerance,
                              abs_floor=_ABS_FLOOR):
    """Compare two numeric values within a relative tolerance."""
    src_nan = isinstance(src_val, float) and math.isnan(src_val)
    db_nan = isinstance(db_val, float) and math.isnan(db_val)
    if src_nan and db_nan:
        return {"check": check, "metric": metric,
                "source_value": src_val, "duckdb_value": db_val,
                "status": "WARN", "detail": "Both values are NaN"}
    if src_nan or db_nan:
        nan_side = "source" if src_nan else "duckdb"
        return {"check": check, "metric": metric,
                "source_value": src_val, "duckdb_value": db_val,
                "status": "FAIL",
                "detail": f"NaN in {nan_side} but not the other ({src_val} vs {db_val})"}

    if src_val == 0 and db_val == 0:
        return {"check": check, "metric": metric,
                "source_value": src_val, "duckdb_value": db_val,
                "status": "PASS", "detail": "Both zero"}

    abs_diff = abs(src_val - db_val)
    if abs(src_val) < abs_floor and abs(db_val) < abs_floor:
        scaled_diff = abs_diff / abs_floor
        if abs_diff == 0:
            status, detail = "PASS", "Exact match"
        elif scaled_diff <= tolerance:
            status, detail = "PASS", f"Within abs floor ({abs_diff:.6g} abs diff)"
        elif scaled_diff <= tolerance * 10:
            status, detail = "WARN", f"Near abs floor ({abs_diff:.6g} abs diff)"
        else:
            status, detail = "FAIL", f"Exceeds abs floor ({abs_diff:.6g} abs diff)"
        return {"check": check, "metric": metric,
                "source_value": src_val, "duckdb_value": db_val,
                "status": status, "detail": detail}

    denominator = abs(src_val) if src_val != 0 else abs(db_val)
    diff = abs_diff / denominator
    if diff == 0:
        status, detail = "PASS", "Exact match"
    elif diff <= tolerance:
        status, detail = "PASS", f"Within tolerance ({diff:.6%} diff)"
    elif diff <= tolerance * 10:
        status, detail = "WARN", f"Near tolerance ({diff:.4%} diff)"
    else:
        status, detail = "FAIL", f"Exceeds tolerance ({diff:.4%} diff)"

    return {"check": check, "metric": metric,
            "source_value": src_val, "duckdb_value": db_val,
            "status": status, "detail": detail}


def format_tieout_table(results):
    """Render comparison results as a markdown table.

    .. deprecated:: Use ``format_verification_table()`` from
        ``helpers.cross_verification`` instead.
    """
    warnings.warn(
        "format_tieout_table() is deprecated. Use "
        "helpers.cross_verification.format_verification_table() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    lines = [
        "| Check | Metric | Source | DuckDB | Status | Detail |",
        "|-------|--------|--------|--------|--------|--------|",
    ]
    for r in results:
        status_badge = {
            "PASS": "PASS", "WARN": "**WARN**", "FAIL": "**FAIL**",
        }.get(r["status"], r["status"])
        lines.append(
            f"| {r['check']} | {r['metric']} | {r['source_value']} "
            f"| {r['duckdb_value']} | {status_badge} | {r['detail']} |"
        )
    return "\n".join(lines)


def overall_status(results):
    """Roll up individual check results to a single PASS/WARN/FAIL.

    .. deprecated:: Use ``helpers.cross_verification.overall_status()`` instead.
    """
    warnings.warn(
        "tieout_helpers.overall_status() is deprecated. Use "
        "helpers.cross_verification.overall_status() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    statuses = {r["status"] for r in results}
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def validate_profile_pair(source_profile, duckdb_profile):
    """Pre-validate two profiles before detailed comparison.

    .. deprecated:: The dual-path paradigm is deprecated.
    """
    warnings.warn(
        "validate_profile_pair() is deprecated. Cross-verification "
        "does not require pre-validation of profile pairs.",
        DeprecationWarning,
        stacklevel=2,
    )
    issues = []
    src_empty = source_profile.get("warning") == "EMPTY_DATAFRAME"
    db_empty = duckdb_profile.get("warning") == "EMPTY_DATAFRAME"

    if src_empty and db_empty:
        issues.append("Both DataFrames are empty")
        return {"can_compare": False, "status": "FAIL", "issues": issues}
    if src_empty and not db_empty:
        issues.append(f"Source is empty but other has {duckdb_profile['row_count']:,} rows")
        return {"can_compare": False, "status": "FAIL", "issues": issues}
    if db_empty and not src_empty:
        issues.append(f"Other is empty but source has {source_profile['row_count']:,} rows")
        return {"can_compare": False, "status": "FAIL", "issues": issues}

    src_cols = set(source_profile["columns"])
    db_cols = set(duckdb_profile["columns"])
    overlap = src_cols & db_cols
    if len(overlap) == 0:
        issues.append(f"Zero column overlap — {sorted(src_cols)} vs {sorted(db_cols)}")
        return {"can_compare": False, "status": "FAIL", "issues": issues}
    if len(overlap) < len(src_cols) * 0.5:
        issues.append(f"Low column overlap: {len(overlap)}/{len(src_cols)}")

    return {"can_compare": True, "status": "WARN" if issues else "PASS", "issues": issues}


def safe_profile(df, label="source"):
    """Student-safe wrapper around profile_dataframe(). Never raises."""
    try:
        return profile_dataframe(df, label=label)
    except Exception as exc:
        return {
            "label": label, "error": str(exc),
            "suggestion": "Check that the DataFrame is valid and non-empty.",
            "row_count": 0, "columns": [],
        }


def safe_compare(source_profile, duckdb_profile):
    """Student-safe wrapper around compare_profiles(). Never raises.

    .. deprecated:: Use cross-verification functions instead.
    """
    warnings.warn(
        "safe_compare() is deprecated. Use helpers.cross_verification "
        "safe_run_verification() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    try:
        validation = validate_profile_pair(source_profile, duckdb_profile)
        if not validation["can_compare"]:
            return [{
                "check": "Pre-validation", "metric": "profile_pair",
                "source_value": source_profile.get("row_count", "?"),
                "duckdb_value": duckdb_profile.get("row_count", "?"),
                "status": "FAIL",
                "detail": "; ".join(validation["issues"]),
            }]
        return compare_profiles(source_profile, duckdb_profile)
    except Exception as exc:
        return [{
            "check": "Comparison Error", "metric": "system",
            "source_value": "—", "duckdb_value": "—",
            "status": "FAIL",
            "detail": f"Error during comparison: {exc}",
        }]
