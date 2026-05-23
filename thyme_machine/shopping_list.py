"""Shopping list — persisted to data/shopping_list.json."""

import json
from pathlib import Path

_PATH = Path("./data/shopping_list.json")


def load() -> list[dict]:
    if not _PATH.exists():
        return []
    try:
        return json.loads(_PATH.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return []


def _save(items: list[dict]) -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(
        json.dumps({"items": items}, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_items(new_items: list[dict]) -> list[dict]:
    """Add items (dicts with 'ingredient', 'qty', 'recipe') avoiding exact duplicates."""
    items = load()
    existing = {(i["ingredient"].lower(), i.get("recipe", "")) for i in items}
    for item in new_items:
        key = (item["ingredient"].lower(), item.get("recipe", ""))
        if key not in existing:
            items.append({**item, "checked": False})
            existing.add(key)
    _save(items)
    return items


def toggle(index: int) -> list[dict]:
    items = load()
    if 0 <= index < len(items):
        items[index]["checked"] = not items[index].get("checked", False)
        _save(items)
    return items


def remove_checked() -> list[dict]:
    items = [i for i in load() if not i.get("checked", False)]
    _save(items)
    return items


def clear_all() -> None:
    _save([])


def as_text() -> str:
    """Export as a plain-text shopping list."""
    items = load()
    if not items:
        return ""
    groups: dict[str, list[str]] = {}
    for item in items:
        recipe = item.get("recipe", "Other")
        groups.setdefault(recipe, []).append(
            f"{'[x]' if item.get('checked') else '[ ]'} {item['qty']}  {item['ingredient']}"
        )
    lines = []
    for recipe, ing_lines in groups.items():
        lines.append(f"# {recipe}")
        lines.extend(ing_lines)
        lines.append("")
    return "\n".join(lines)
