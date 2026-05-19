"""CLI entry point for Tophat."""

import typer
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

from tophat.agent import ask_agent

app = typer.Typer(help="Monopoly GO! Lifecycle AI Analyst")
console = Console()


@app.command()
def ask(
    question: str = typer.Argument(help="Your analytical question"),
    skill: str | None = typer.Option(None, "--skill", "-s", help="Force a specific skill (adhoc, ab-test, alert, deep-dive, research, measure)"),
):
    """Ask the lifecycle analyst a question."""
    console.print(f"\n[bold]Question:[/bold] {question}\n")
    with console.status("[bold green]Thinking..."):
        response = ask_agent(question, skill=skill)
    console.print(response)


@app.command()
def query(
    sql: str = typer.Argument(help="SQL query to run against BigQuery"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Estimate bytes scanned without executing"),
):
    """Run a BigQuery query directly."""
    from tophat.bigquery import run_query

    with console.status("[bold green]Running query..."):
        result = run_query(sql, dry_run=dry_run)
    console.print(result)


@app.command()
def hex_projects(
    limit: int = typer.Option(25, "--limit", "-n", help="Number of projects to list"),
):
    """List Hex projects in the workspace."""
    from tophat.hex import list_projects

    with console.status("[bold green]Fetching Hex projects..."):
        projects = list_projects(limit=limit)

    for p in projects:
        title = p.get("title", "Untitled")
        pid = p["id"]
        console.print(f"  [bold]{title}[/bold]  [dim]({pid})[/dim]")
        if desc := p.get("description"):
            console.print(f"    {desc[:100]}")

    console.print(f"\n[dim]{len(projects)} projects shown[/dim]")


@app.command()
def hex_run(
    project_id: str = typer.Argument(help="Hex project UUID to trigger"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for run to complete"),
):
    """Trigger a Hex project run."""
    from tophat.hex import run_project, run_and_wait

    with console.status("[bold green]Running Hex project..."):
        if wait:
            result = run_and_wait(project_id)
        else:
            result = run_project(project_id)

    status = result.get("status", "unknown")
    run_url = result.get("runUrl", "")
    console.print(f"Status: [bold]{status}[/bold]")
    if run_url:
        console.print(f"URL: {run_url}")


if __name__ == "__main__":
    app()
