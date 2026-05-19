"""Hex API integration — read projects and push results via BigQuery staging tables."""

import os
import time

import requests

HEX_BASE_URL = "https://app.hex.tech/api/v1"


def _token() -> str:
    token = os.getenv("HEX_API_TOKEN")
    if not token:
        raise ValueError("HEX_API_TOKEN environment variable is not set")
    return token


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
    }


def list_projects(limit: int = 25, status: str | None = None) -> list[dict]:
    """List projects in the workspace."""
    params: dict = {"limit": limit}
    if status:
        params["statuses[]"] = status

    resp = requests.get(f"{HEX_BASE_URL}/projects", headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json().get("values", [])


def get_project(project_id: str) -> dict:
    """Get details for a specific project."""
    resp = requests.get(f"{HEX_BASE_URL}/projects/{project_id}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def run_project(
    project_id: str,
    input_params: dict | None = None,
    update_published: bool = False,
) -> dict:
    """Trigger a Hex project run, optionally passing input parameters."""
    body = {
        "dryRun": False,
        "updatePublishedResults": update_published,
        "useCachedSqlResults": False,
    }
    if input_params:
        body["inputParams"] = input_params

    resp = requests.post(
        f"{HEX_BASE_URL}/projects/{project_id}/runs",
        headers=_headers(),
        json=body,
    )
    resp.raise_for_status()
    return resp.json()


def get_run_status(project_id: str, run_id: str) -> dict:
    """Check the status of a project run."""
    resp = requests.get(
        f"{HEX_BASE_URL}/projects/{project_id}/runs/{run_id}",
        headers=_headers(),
    )
    resp.raise_for_status()
    return resp.json()


def run_and_wait(
    project_id: str,
    input_params: dict | None = None,
    timeout_seconds: int = 300,
    poll_interval: int = 5,
) -> dict:
    """Trigger a project run and poll until completion."""
    run = run_project(project_id, input_params)
    run_id = run["runId"]
    pid = run["projectId"]

    deadline = time.time() + timeout_seconds
    status = run
    while time.time() < deadline:
        status = get_run_status(pid, run_id)
        if status.get("status") in ("COMPLETED", "ERRORED", "KILLED"):
            return status
        time.sleep(poll_interval)

    return {"error": "timeout", "runId": run_id, "lastStatus": status}


def push_to_hex(
    project_id: str,
    staging_table: str,
    input_params: dict | None = None,
    update_published: bool = True,
) -> dict:
    """
    Push results to Hex by triggering a project that reads from a BigQuery staging table.

    Assumes the caller has already written data to `staging_table` via BigQuery.
    This function triggers the Hex project to pick up the fresh data.
    """
    result = run_and_wait(project_id, input_params)
    return {
        "source_table": staging_table,
        "hex_project_id": project_id,
        "run_status": result.get("status"),
        "run_url": result.get("runUrl"),
    }
