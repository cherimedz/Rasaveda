"""
Generation layer: builds a grounded RAG prompt and calls Qwen2.5 via the
HuggingFace Inference API to produce personalized, explainable recommendations.
"""

import json
import re

from huggingface_hub import InferenceClient

from thyme_machine.config import settings
from thyme_machine.models import (
    IngredientMatch,
    RecommendationRequest,
    RecommendationResponse,
    RecommendedRecipe,
    Recipe,
)
from thyme_machine.retrieval import RetrievedRecipe


# ---------------------------------------------------------------------------
# Ingredient matching
# ---------------------------------------------------------------------------

_SUBSTITUTION_MAP = {
    "heavy cream": "coconut cream or Greek yogurt",
    "butter": "olive oil or vegan butter",
    "eggs": "flax egg (1 tbsp ground flax + 3 tbsp water)",
    "milk": "any plant-based milk",
    "soy sauce": "tamari (gluten-free) or coconut aminos",
    "fish sauce": "soy sauce + a dash of lime",
    "parmesan": "nutritional yeast or Pecorino",
    "pecorino romano": "parmesan or aged Manchego",
    "guanciale": "pancetta or thick-cut bacon",
    "pancetta": "bacon or smoked ham",
    "mirin": "dry sherry + a pinch of sugar",
    "sake": "dry white wine or rice vinegar",
    "shaoxing wine": "dry sherry or Chinese rice wine",
    "tamarind paste": "lime juice + brown sugar",
    "palm sugar": "brown sugar or coconut sugar",
    "paneer": "firm tofu or halloumi",
    "ghee": "clarified butter or coconut oil",
    "arborio rice": "short-grain rice or even barley",
    "phyllo pastry": "puff pastry (different texture but works)",
    "tahini": "almond butter or sunflower seed butter",
    "amchur powder": "extra lemon or lime juice",
    "gochujang": "sriracha + a little miso paste",
    "kaffir lime leaves": "lime zest + a bay leaf",
}


def _compute_ingredient_match(user_ingredients: list[str], recipe: Recipe) -> IngredientMatch:
    user_set = {i.lower().strip() for i in user_ingredients}

    have, need = [], []
    for ingredient in recipe.ingredients:
        ing_lower = ingredient.lower().strip()
        matched = any(
            ing_lower in user_item or user_item in ing_lower
            for user_item in user_set
        )
        if matched:
            have.append(ingredient)
        else:
            need.append(ingredient)

    pct = round(len(have) / len(recipe.ingredients) * 100, 1) if recipe.ingredients else 0.0
    substitutions = {
        ing: sub
        for ing in need
        for key, sub in _SUBSTITUTION_MAP.items()
        if key in ing.lower()
    }

    return IngredientMatch(
        have=have,
        need=need,
        match_percentage=pct,
        substitutions=substitutions,
    )


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _format_retrieved_context(retrieved: list[RetrievedRecipe]) -> str:
    blocks = []
    for i, r in enumerate(retrieved, 1):
        rec = r.recipe
        total_time = rec.prep_time_minutes + rec.cook_time_minutes
        blocks.append(
            f"--- RECIPE {i} (similarity: {r.similarity_score:.2f}) ---\n"
            f"ID: {rec.id}\n"
            f"Name: {rec.name}\n"
            f"Cuisine: {rec.cuisine}\n"
            f"Description: {rec.description}\n"
            f"Ingredients: {', '.join(rec.ingredients)}\n"
            f"Dietary tags: {', '.join(rec.dietary_tags) or 'none'}\n"
            f"Flavor profile: {', '.join(rec.flavor_profile)}\n"
            f"Difficulty: {rec.difficulty.value}\n"
            f"Total time: {total_time} min\n"
            f"Servings: {rec.servings}"
        )
    return "\n\n".join(blocks)


def _build_system_prompt() -> str:
    return (
        "You are Rasaveda (रसवेद) — Knowledge of Flavors. "
        "You are a wise, poetic, and deeply knowledgeable recipe guide who finds the perfect meal "
        "in whatever ingredients someone has. You draw connections between ingredients and culture, "
        "and your advice is always grounded, practical, and gently inspiring.\n\n"
        "Rules you always follow:\n"
        "1. Only recommend recipes from the provided context — never invent new ones.\n"
        "2. Be explicit about why each recipe fits the user's ingredients and dietary needs.\n"
        "3. Always note what ingredients are missing and how they can be substituted.\n"
        "4. Output ONLY a single valid JSON object — no markdown, no preamble, no trailing text."
    )


def _build_user_prompt(
    request: RecommendationRequest,
    retrieved: list[RetrievedRecipe],
    ingredient_matches: dict[str, IngredientMatch],
) -> str:
    dietary_str = ", ".join(request.dietary_preferences) if request.dietary_preferences else "none"
    cuisine_str = request.cuisine_preference or "any"
    flavor_str = ", ".join(request.flavor_profile) if request.flavor_profile else "not specified"
    time_str = f"{request.max_cook_time_minutes} min" if request.max_cook_time_minutes else "no limit"

    match_summary = ""
    for recipe_id, match in ingredient_matches.items():
        name = next((r.recipe.name for r in retrieved if r.recipe.id == recipe_id), recipe_id)
        match_summary += (
            f"\n{name}: have {len(match.have)}/{len(match.have)+len(match.need)} ingredients "
            f"({match.match_percentage}%). "
            f"Missing: {', '.join(match.need) or 'nothing'}. "
            f"Substitutions: {json.dumps(match.substitutions) if match.substitutions else 'none'}."
        )

    return f"""User pantry and preferences:
- Available ingredients: {', '.join(request.available_ingredients)}
- Dietary preferences: {dietary_str}
- Cuisine preference: {cuisine_str}
- Desired flavors: {flavor_str}
- Max cooking time: {time_str}
- Servings: {request.servings or 'any'}

Pre-computed ingredient matches:{match_summary}

Retrieved recipe candidates:
{_format_retrieved_context(retrieved)}

Respond with ONLY this JSON structure (no markdown, no extra text):
{{
  "query_summary": "one sentence summarizing what the user is looking for",
  "general_tip": "one practical cooking tip relevant to their situation",
  "recommendations": [
    {{
      "recipe_id": "<id from context>",
      "match_score": <float 0.0-1.0>,
      "why_it_fits": "<2-3 sentences on ingredient and preference fit>",
      "personalization_notes": "<how to adapt for their dietary needs or serving size>",
      "rasaveda_says": "<one short, poetic or warm remark — Rasaveda's signature for this pick>"
    }}
  ]
}}

Include exactly {request.n_recommendations} recommendation{'s' if request.n_recommendations != 1 else ''}, best fit first. Use only recipe IDs from the context."""


# ---------------------------------------------------------------------------
# JSON extraction (robust against model adding fences or trailing text)
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from model response. Raw output (first 300 chars):\n{text[:300]}")


# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------

def generate_recommendations(
    request: RecommendationRequest,
    retrieved: list[RetrievedRecipe],
) -> RecommendationResponse:
    if not retrieved:
        raise ValueError("No recipes retrieved. Try broadening your search criteria.")

    client = InferenceClient(
        model=settings.hf_model,
        token=settings.huggingface_token,
    )

    ingredient_matches = {
        r.recipe.id: _compute_ingredient_match(request.available_ingredients, r.recipe)
        for r in retrieved
    }

    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": _build_user_prompt(request, retrieved, ingredient_matches)},
    ]

    response = client.chat_completion(
        messages=messages,
        max_tokens=2048,
        temperature=0.25,   # low temp = consistent JSON structure
        stream=False,
    )

    raw_text = response.choices[0].message.content
    parsed = _extract_json(raw_text)

    recipe_lookup = {r.recipe.id: r for r in retrieved}
    recommendations: list[RecommendedRecipe] = []

    for rec in parsed.get("recommendations", []):
        recipe_id = rec.get("recipe_id", "")
        if recipe_id not in recipe_lookup:
            continue

        retrieved_recipe = recipe_lookup[recipe_id]
        match = ingredient_matches[recipe_id]

        recommendations.append(
            RecommendedRecipe(
                recipe=retrieved_recipe.recipe,
                match_score=float(rec.get("match_score", retrieved_recipe.similarity_score)),
                ingredient_match=match,
                why_it_fits=rec.get("why_it_fits", ""),
                personalization_notes=rec.get("personalization_notes", ""),
                thyme_machine_says=rec.get("rasaveda_says", rec.get("thyme_machine_says", "")),
            )
        )

    return RecommendationResponse(
        query_summary=parsed.get("query_summary", ""),
        recommendations=recommendations,
        general_tip=parsed.get("general_tip", ""),
        total_recipes_considered=len(retrieved),
    )
