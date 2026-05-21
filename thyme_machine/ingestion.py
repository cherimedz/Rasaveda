"""
Ingestion pipeline: loads all recipe JSON files from the data directory,
creates text representations, and stores them in ChromaDB.
"""

import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from rich.console import Console
from rich.progress import track

from thyme_machine.config import settings
from thyme_machine.models import Recipe

console = Console()

# Files in the data directory that are NOT recipe datasets
_EXCLUDE_FILES = {"user_recipes.json", "image_cache.json"}


def load_recipes(path: str = None) -> list[Recipe]:
    """
    Load recipes from a file or from all JSON files in a directory.
    Excludes user_recipes.json (managed separately by user_recipes.py).
    """
    p = Path(path or settings.recipes_path)

    if p.is_dir():
        files = sorted(f for f in p.glob("*.json") if f.name not in _EXCLUDE_FILES)
    elif p.is_file():
        # Also load siblings in the same directory for discovery
        files = sorted(
            f for f in p.parent.glob("*.json") if f.name not in _EXCLUDE_FILES
        )
    else:
        return []

    recipes: list[Recipe] = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        recipes.extend(Recipe(**r) for r in data)
    return recipes


def _build_recipe_document(recipe: Recipe) -> str:
    """Rich text representation for embedding — used by both ingestion and user_recipes."""
    ingredient_list = ", ".join(recipe.ingredients)
    dietary = ", ".join(recipe.dietary_tags) if recipe.dietary_tags else "no dietary restrictions"
    flavor = ", ".join(recipe.flavor_profile)
    total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
    course = recipe.course or "Main Course"

    return (
        f"{recipe.name} — {recipe.cuisine} cuisine. "
        f"Course: {course}. "
        f"{recipe.description} "
        f"Ingredients: {ingredient_list}. "
        f"Dietary: {dietary}. "
        f"Flavors: {flavor}. "
        f"Difficulty: {recipe.difficulty.value}. "
        f"Total time: {total_time} minutes. "
        f"Serves {recipe.servings}."
    )


def _build_metadata(recipe: Recipe) -> dict:
    """ChromaDB-compatible flat metadata (strings and ints only, no lists)."""
    return {
        "name": recipe.name,
        "cuisine": recipe.cuisine.lower(),
        "dietary_tags": ",".join(recipe.dietary_tags),
        "difficulty": recipe.difficulty.value,
        "prep_time": recipe.prep_time_minutes,
        "cook_time": recipe.cook_time_minutes,
        "total_time": recipe.prep_time_minutes + recipe.cook_time_minutes,
        "servings": recipe.servings,
        "flavor_profile": ",".join(recipe.flavor_profile),
        "ingredients": ",".join(recipe.ingredients),
        "course": recipe.course or "Main Course",
    }


def get_collection() -> chromadb.Collection:
    """Return (or create) the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    return client.get_or_create_collection(
        name=settings.collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )


def ingest_recipes(force: bool = False) -> int:
    """
    Ingest all recipes from the data directory into ChromaDB.
    Skips if already populated unless force=True.
    Returns number of recipes ingested.
    """
    collection = get_collection()

    if not force and collection.count() > 0:
        console.print(
            f"[yellow]Collection already has {collection.count()} recipes. "
            "Pass force=True to re-ingest.[/yellow]"
        )
        return 0

    if force and collection.count() > 0:
        console.print("[yellow]Force re-ingestion: clearing existing data...[/yellow]")
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        client.delete_collection(settings.collection_name)
        collection = get_collection()

    data_dir = Path(settings.recipes_path).parent
    recipes = load_recipes(str(data_dir))
    console.print(f"[green]Loaded {len(recipes)} base recipes from {data_dir}[/green]")

    ids, documents, metadatas = [], [], []
    for recipe in track(recipes, description="Embedding recipes..."):
        ids.append(recipe.id)
        documents.append(_build_recipe_document(recipe))
        metadatas.append(_build_metadata(recipe))

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    console.print(f"[bold green]Done! Ingested {len(recipes)} recipes into ChromaDB.[/bold green]")
    return len(recipes)


def get_recipe_count() -> int:
    return get_collection().count()
