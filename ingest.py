"""
Rasaveda — Standalone ingestion CLI.
Run once before starting the app, or after updating the recipe dataset.

Usage:
    python ingest.py           # ingest if not already done
    python ingest.py --force   # clear and re-ingest everything
"""

import typer
from rich.console import Console

from thyme_machine.ingestion import get_recipe_count, ingest_recipes

console = Console()
app = typer.Typer(help="Rasaveda -- Recipe Ingestion CLI")


@app.command()
def main(force: bool = typer.Option(False, "--force", "-f", help="Clear and re-ingest all recipes")):
    console.print("\n[bold magenta]Rasaveda[/bold magenta]  [dim]-- Knowledge of Flavors[/dim]")
    console.print(f"Current index size: [cyan]{get_recipe_count()}[/cyan] recipes\n")

    count = ingest_recipes(force=force)

    if count == 0:
        console.print("[yellow]Nothing new ingested. Use --force to rebuild the index.[/yellow]")
    else:
        console.print(f"\n[bold green]{get_recipe_count()} recipes indexed and ready![/bold green]")


if __name__ == "__main__":
    app()
