"""
User recipe management: save, load, and delete recipes added by the user.
Each saved recipe is also upserted into ChromaDB so it appears in recommendations.
"""

import json
import uuid
from pathlib import Path

from thyme_machine.ingestion import _build_metadata, _build_recipe_document, get_collection
from thyme_machine.models import Recipe

USER_RECIPES_PATH = Path("./data/user_recipes.json")


def load_user_recipes() -> list[Recipe]:
    if not USER_RECIPES_PATH.exists():
        return []
    with open(USER_RECIPES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return [Recipe(**r) for r in data]


def save_user_recipe(recipe: Recipe) -> None:
    USER_RECIPES_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if USER_RECIPES_PATH.exists():
        with open(USER_RECIPES_PATH, encoding="utf-8") as f:
            existing = json.load(f)

    found = False
    for i, r in enumerate(existing):
        if r["id"] == recipe.id:
            existing[i] = recipe.model_dump()
            found = True
            break
    if not found:
        existing.append(recipe.model_dump())

    with open(USER_RECIPES_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    # Upsert into ChromaDB so it appears in recommendations immediately
    collection = get_collection()
    collection.upsert(
        ids=[recipe.id],
        documents=[_build_recipe_document(recipe)],
        metadatas=[_build_metadata(recipe)],
    )


def delete_user_recipe(recipe_id: str) -> bool:
    if not USER_RECIPES_PATH.exists():
        return False

    with open(USER_RECIPES_PATH, encoding="utf-8") as f:
        existing = json.load(f)

    updated = [r for r in existing if r["id"] != recipe_id]
    if len(updated) == len(existing):
        return False

    with open(USER_RECIPES_PATH, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2, ensure_ascii=False)

    try:
        get_collection().delete(ids=[recipe_id])
    except Exception:
        pass

    return True


def generate_recipe_id() -> str:
    return f"usr-{uuid.uuid4().hex[:8]}"
