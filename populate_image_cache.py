"""
Pre-populate data/image_cache.json for all recipes in the data directory.

Run once after adding new recipes or when the cache is empty:
    python populate_image_cache.py

Uses conservative rate limiting (1.5 s between recipe lookups) to avoid
hitting Wikipedia's request limits. Takes ~3 minutes for 108 recipes.
Results are saved to data/image_cache.json so the Streamlit app never
needs to call the API at render time.
"""
import json
import os
import time

DATA_DIR = "./data"
EXCLUDE = {"user_recipes.json", "chat_history.json", "image_cache.json"}


def load_recipes():
    recipes = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith(".json") and f not in EXCLUDE:
            path = os.path.join(DATA_DIR, f)
            with open(path, encoding="utf-8-sig") as fh:
                recipes.extend(json.load(fh))
    return recipes


def main():
    # Import after defining helpers to avoid stale module state
    import importlib
    import thyme_machine.images as img_mod

    recipes = load_recipes()
    print(f"Pre-populating image cache for {len(recipes)} recipes...\n")

    hits, gradients = 0, 0
    for i, r in enumerate(recipes, 1):
        name = r["name"]
        key = name.lower().strip()

        # Only skip recipes that already have a real URL in cache.
        # Nulls are not persisted to disk, so nothing to skip for no-image recipes.
        if img_mod._mem_cache.get(key):
            print(f"  {i:3d}/{len(recipes)}  cached        {name!r}")
            hits += 1
            continue

        result = img_mod.get_recipe_image(name, r.get("cuisine", ""))
        if result:
            hits += 1
            src = "wikipedia" if "wikimedia" in result else "themealdb"
            print(f"  {i:3d}/{len(recipes)}  {src:12s}  {name!r}")
        else:
            gradients += 1
            print(f"  {i:3d}/{len(recipes)}  gradient      {name!r}")

        # Polite delay — 2 s between fetches (Wikipedia allows ~200 req/min; we have
        # 2 requests per recipe = ~30 recipes/min well within limits, but being cautious)
        time.sleep(2.0)

    total = hits + gradients
    print(f"\n{'='*60}")
    print(f"Images:    {hits}/{total}  ({hits/total*100:.0f}%)")
    print(f"Gradients: {gradients}/{total}")
    print(f"Cache saved to {img_mod._CACHE_PATH}")


if __name__ == "__main__":
    main()
