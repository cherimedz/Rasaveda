"""Favourites — persisted to data/favourites.json."""

import json
from pathlib import Path

_PATH = Path("./data/favourites.json")


def load() -> set[str]:
    if not _PATH.exists():
        return set()
    try:
        data = json.loads(_PATH.read_text(encoding="utf-8"))
        return set(data.get("ids", []))
    except Exception:
        return set()


def _save(ids: set[str]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(
        json.dumps({"ids": sorted(ids)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def toggle(recipe_id: str) -> bool:
    """Toggle favourite status. Returns True if the recipe is now favourited."""
    ids = load()
    if recipe_id in ids:
        ids.discard(recipe_id)
        _save(ids)
        return False
    ids.add(recipe_id)
    _save(ids)
    return True


def is_favourite(recipe_id: str) -> bool:
    return recipe_id in load()
