"""
Diagnostic: test all recipes against TheMealDB and report match quality.
Run with:  python diagnose_images.py
"""
import json
import os
import time

import requests

DATA_DIR = "./data"
EXCLUDE = {"user_recipes.json", "chat_history.json"}
SIM_THRESHOLD = 0.5


def query_mealdb(term: str) -> str | None:
    try:
        r = requests.get(
            "https://www.themealdb.com/api/json/v1/1/search.php",
            params={"s": term},
            timeout=4,
        )
        meals = r.json().get("meals")
        if meals:
            return meals[0]["strMeal"]
    except Exception:
        pass
    return None


def similarity(a: str, b: str) -> float:
    aw = {w.lower() for w in a.split() if len(w) >= 3}
    bw = {w.lower() for w in b.split() if len(w) >= 3}
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / len(aw | bw)


def load_all_recipes():
    recipes = []
    for f in sorted(os.listdir(DATA_DIR)):
        if f.endswith(".json") and f not in EXCLUDE:
            with open(os.path.join(DATA_DIR, f), encoding="utf-8") as fh:
                recipes.extend(json.load(fh))
    return recipes


def main():
    recipes = load_all_recipes()
    print(f"Testing {len(recipes)} recipes against TheMealDB...\n")

    passed, failed, no_match = [], [], []

    for i, r in enumerate(recipes, 1):
        name = r["name"]
        matched = query_mealdb(name)
        time.sleep(0.12)  # ~8 req/sec, well within free tier limits

        if matched:
            s = similarity(name, matched)
            if s >= SIM_THRESHOLD:
                passed.append((name, matched, s))
            else:
                failed.append((name, matched, s))
        else:
            no_match.append(name)

        if i % 10 == 0:
            print(f"  ... {i}/{len(recipes)} checked")

    print("\n=== WILL SHOW IMAGE (similarity >= 0.5) ===")
    for name, matched, s in passed:
        print(f"  OK   {name!r:45s} -> {matched!r} (sim={s:.2f})")

    print(f"\n=== REJECTED — too loose (sim < 0.5, would use gradient) ===")
    for name, matched, s in failed:
        print(f"  FAIL {name!r:45s} -> {matched!r} (sim={s:.2f})")

    print(f"\n=== NO MATCH IN THEMEALDB (will use gradient) — {len(no_match)} recipes ===")
    for n in no_match:
        print(f"  --   {n}")

    print(f"\nSummary: {len(passed)} images / {len(failed)+len(no_match)} gradients")


if __name__ == "__main__":
    main()
