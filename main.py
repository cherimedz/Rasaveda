"""
Thyme Machine — entry point.

Starts the FastAPI server and auto-ingests the recipe dataset on first launch.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.console import Console

from thyme_machine.api import router
from thyme_machine.config import settings
from thyme_machine.ingestion import get_recipe_count, ingest_recipes

console = Console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    console.print("\n[bold magenta]⏱  Thyme Machine is warming up...[/bold magenta]")

    count = get_recipe_count()
    if count == 0:
        console.print("[yellow]No recipes indexed. Running initial ingestion...[/yellow]")
        ingest_recipes()
    else:
        console.print(f"[green]✓ {count} recipes already indexed and ready.[/green]")

    console.print("[bold green]✓ Thyme Machine is ready! Bon appétit.[/bold green]\n")
    yield
    console.print("[dim]Thyme Machine shutting down...[/dim]")


app = FastAPI(
    title="Thyme Machine",
    description=(
        "A whimsical RAG-powered recipe recommendation system. "
        "Tell us what's in your pantry — we'll handle the rest."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "Thyme Machine",
        "tagline": "Your pantry, your palate, our passion.",
        "docs": "/docs",
        "api": "/api/v1",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level="info",
    )
