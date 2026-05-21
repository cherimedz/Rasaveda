"""
Retrieval layer: builds a semantic query from user preferences,
searches ChromaDB, and post-filters by dietary tags.
Also resolves user-added recipe IDs from the user_recipes store.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from thyme_machine.config import settings
from thyme_machine.ingestion import get_collection, load_recipes
from thyme_machine.models import Recipe, RecommendationRequest

USER_RECIPES_PATH = Path("./data/user_recipes.json")


@dataclass
class RetrievedRecipe:
    recipe: Recipe
    similarity_score: float
    document: str


def _load_all_recipes() -> dict[str, Recipe]:
    """
    Build a complete ID→Recipe map from base dataset + user recipes.
    Used to reconstruct full Recipe objects from ChromaDB result IDs.
    """
    data_dir = Path(settings.recipes_path).parent
    all_recipes = {r.id: r for r in load_recipes(str(data_dir))}

    if USER_RECIPES_PATH.exists():
        with open(USER_RECIPES_PATH, encoding="utf-8") as f:
            user_data = json.load(f)
        for r in user_data:
            recipe = Recipe(**r)
            all_recipes[recipe.id] = recipe

    return all_recipes


def _build_query_text(request: RecommendationRequest) -> str:
    """Convert a user request into a descriptive query string for embedding."""
    parts = []
    if request.available_ingredients:
        parts.append(f"Ingredients available: {', '.join(request.available_ingredients)}.")
    if request.dietary_preferences:
        parts.append(f"Dietary requirements: {', '.join(request.dietary_preferences)}.")
    if request.cuisine_preference:
        parts.append(f"Cuisine preference: {request.cuisine_preference}.")
    if request.flavor_profile:
        parts.append(f"Desired flavors: {', '.join(request.flavor_profile)}.")
    if request.max_cook_time_minutes:
        parts.append(f"Maximum total cooking time: {request.max_cook_time_minutes} minutes.")
    return " ".join(parts) if parts else "Indian recipe"


def _build_where_filter(request: RecommendationRequest) -> dict | None:
    conditions = []
    if request.cuisine_preference:
        conditions.append({"cuisine": {"$eq": request.cuisine_preference.lower()}})
    if request.max_cook_time_minutes:
        conditions.append({"total_time": {"$lte": request.max_cook_time_minutes}})
    if not conditions:
        return None
    return conditions[0] if len(conditions) == 1 else {"$and": conditions}


_MEAT_INGREDIENTS: frozenset[str] = frozenset({
    # Poultry
    "chicken", "turkey", "duck", "goose", "quail", "hen", "murgh",
    # Red meat
    "beef", "pork", "lamb", "mutton", "veal", "venison", "bison", "rabbit", "goat",
    "keema", "kheema", "gosht", "mince",
    # Processed
    "bacon", "ham", "sausage", "pepperoni", "salami", "chorizo", "prosciutto",
    "steak", "ribs", "lard",
    # Seafood
    "fish", "salmon", "tuna", "cod", "tilapia", "halibut", "bass", "trout",
    "shrimp", "prawn", "crab", "lobster", "clam", "oyster", "mussel",
    "squid", "octopus", "anchovy", "sardine", "mackerel", "herring",
    "machi", "machli", "jhinga",
})

_VEG_TAGS: frozenset[str] = frozenset({"vegetarian", "vegan"})


def _user_wants_meat(ingredients: list[str]) -> bool:
    """Return True if any ingredient is a meat, poultry, or seafood product."""
    for ing in ingredients:
        tokens = {w.strip(".,()").lower() for w in ing.split()}
        if tokens & _MEAT_INGREDIENTS:
            return True
    return False


def _recipe_is_vegetarian_or_vegan(dietary_tags_str: str) -> bool:
    tags = {t.strip().lower() for t in dietary_tags_str.split(",") if t.strip()}
    return bool(tags & _VEG_TAGS)


def _passes_dietary_filter(recipe_dietary_tags: str, required: list[str]) -> bool:
    if not required:
        return True
    recipe_tags = {t.strip().lower() for t in recipe_dietary_tags.split(",") if t.strip()}
    return all(req.lower() in recipe_tags for req in required)


def search_by_text(query: str, n: int = 3) -> str:
    """
    Free-text semantic search against the recipe collection.
    Returns a formatted string of top-n matches for chatbot context injection.
    """
    collection = get_collection()
    if collection.count() == 0:
        return ""
    n = min(n, collection.count())
    results = collection.query(
        query_texts=[query],
        n_results=n,
        include=["documents", "metadatas"],
    )
    lines = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        name = meta.get("name", "Unknown")
        cuisine = meta.get("cuisine", "")
        lines.append(f"- {name} ({cuisine}): {doc[:200]}")
    return "\n".join(lines)


def retrieve_recipes(request: RecommendationRequest) -> list[RetrievedRecipe]:
    """
    Query ChromaDB semantically, apply metadata pre-filters,
    then post-filter for dietary requirements and course preference.
    Returns extra results beyond n_recommendations so the UI can offer a browse-more list.
    """
    collection = get_collection()
    if collection.count() == 0:
        raise RuntimeError(
            "No recipes in the database. Run `python ingest.py` first."
        )

    query_text = _build_query_text(request)
    where_filter = _build_where_filter(request)

    # Fetch enough candidates to survive post-filters and still leave browse-more extras
    fetch_n = min(max(settings.top_k_results * 4, request.n_recommendations * 6), collection.count())
    # Cap on how many to return (AI gets n_recommendations*3; rest go to browse-more in the UI)
    return_cap = max(settings.top_k_results * 2, request.n_recommendations * 4)

    query_kwargs: dict = {
        "query_texts": [query_text],
        "n_results": fetch_n,
        "include": ["metadatas", "distances", "documents"],
    }
    if where_filter:
        query_kwargs["where"] = where_filter

    results = collection.query(**query_kwargs)

    all_recipes = _load_all_recipes()
    wants_meat = _user_wants_meat(request.available_ingredients)

    retrieved: list[RetrievedRecipe] = []
    for recipe_id, distance, metadata, document in zip(
        results["ids"][0],
        results["distances"][0],
        results["metadatas"][0],
        results["documents"][0],
    ):
        if not _passes_dietary_filter(
            metadata.get("dietary_tags", ""), request.dietary_preferences
        ):
            continue

        # Meat intent filter: exclude vegetarian/vegan recipes when user listed meat
        if wants_meat and _recipe_is_vegetarian_or_vegan(metadata.get("dietary_tags", "")):
            continue

        # Course post-filter
        if request.course_preference and request.course_preference not in ("Any", "Any course"):
            recipe_course = metadata.get("course", "Main Course")
            if recipe_course != request.course_preference:
                continue

        recipe = all_recipes.get(recipe_id)
        if recipe:
            retrieved.append(
                RetrievedRecipe(
                    recipe=recipe,
                    similarity_score=round(1.0 - distance, 4),
                    document=document,
                )
            )

        if len(retrieved) >= return_cap:
            break

    return retrieved
