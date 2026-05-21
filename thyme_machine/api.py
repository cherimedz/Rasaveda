"""
FastAPI routes for the Thyme Machine API.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from thyme_machine.generation import generate_recommendations
from thyme_machine.ingestion import get_recipe_count, ingest_recipes, load_recipes
from thyme_machine.models import RecommendationRequest, RecommendationResponse, Recipe
from thyme_machine.retrieval import retrieve_recipes
from thyme_machine.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check — confirms the vector store is populated."""
    count = get_recipe_count()
    return {
        "status": "ok",
        "service": "Thyme Machine",
        "version": "1.0.0",
        "recipes_indexed": count,
        "model": settings.claude_model,
        "ready": count > 0,
    }


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    """
    Core recommendation endpoint.

    Provide your available ingredients and preferences; Thyme Machine
    retrieves semantically similar recipes and uses Claude to generate
    grounded, explainable, personalized recommendations.
    """
    try:
        retrieved = retrieve_recipes(request)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not retrieved:
        raise HTTPException(
            status_code=404,
            detail=(
                "No matching recipes found for your criteria. "
                "Try relaxing dietary filters or broadening your ingredient list."
            ),
        )

    try:
        response = generate_recommendations(request, retrieved)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation error: {str(e)}"
        )

    return response


@router.get("/recipes", response_model=list[Recipe])
async def list_recipes(
    cuisine: str | None = Query(default=None, description="Filter by cuisine"),
    dietary: str | None = Query(default=None, description="Filter by dietary tag"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Browse all indexed recipes with optional filters."""
    recipes = load_recipes(settings.recipes_path)

    if cuisine:
        recipes = [r for r in recipes if r.cuisine.lower() == cuisine.lower()]

    if dietary:
        recipes = [
            r for r in recipes
            if any(dietary.lower() in tag.lower() for tag in r.dietary_tags)
        ]

    return recipes[:limit]


@router.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    """Fetch a single recipe by its ID."""
    recipes = load_recipes(settings.recipes_path)
    for recipe in recipes:
        if recipe.id == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail=f"Recipe '{recipe_id}' not found.")


@router.get("/cuisines")
async def list_cuisines():
    """List all available cuisines in the dataset."""
    recipes = load_recipes(settings.recipes_path)
    cuisines = sorted({r.cuisine for r in recipes})
    return {"cuisines": cuisines, "count": len(cuisines)}


@router.get("/dietary-tags")
async def list_dietary_tags():
    """List all available dietary tags in the dataset."""
    recipes = load_recipes(settings.recipes_path)
    tags: set[str] = set()
    for r in recipes:
        tags.update(r.dietary_tags)
    return {"dietary_tags": sorted(tags), "count": len(tags)}


@router.post("/admin/ingest")
async def trigger_ingest(force: bool = Query(default=False)):
    """
    Admin endpoint to (re-)ingest the recipe dataset into ChromaDB.
    Set force=true to clear and rebuild the index.
    """
    count = ingest_recipes(force=force)
    return {
        "message": f"Ingestion complete. {count} recipes processed.",
        "total_indexed": get_recipe_count(),
    }
