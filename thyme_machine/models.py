from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DietaryTag(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten-free"
    DAIRY_FREE = "dairy-free"
    LOW_CARB = "low-carb"
    KETO = "keto"
    PALEO = "paleo"
    NUT_FREE = "nut-free"
    HALAL = "halal"
    KOSHER = "kosher"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Recipe(BaseModel):
    id: str
    name: str
    description: str
    cuisine: str
    dietary_tags: list[str]
    difficulty: Difficulty
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    ingredients: list[str]
    ingredient_quantities: dict[str, str]
    instructions: list[str]
    flavor_profile: list[str]
    tips: Optional[str] = None
    course: Optional[str] = None  # e.g. "Main Course", "Appetizer", "Dessert", "Basics"


class RecommendationRequest(BaseModel):
    available_ingredients: list[str] = Field(
        ...,
        description="Ingredients you currently have",
        examples=[["chicken breast", "garlic", "lemon", "olive oil", "rosemary"]],
    )
    dietary_preferences: list[str] = Field(
        default=[],
        description="Dietary restrictions or preferences",
        examples=[["gluten-free", "dairy-free"]],
    )
    cuisine_preference: Optional[str] = Field(
        default=None,
        description="Preferred regional cuisine (optional)",
        examples=["Italian"],
    )
    servings: Optional[int] = Field(
        default=None, description="Desired number of servings", ge=1, le=20
    )
    max_cook_time_minutes: Optional[int] = Field(
        default=None, description="Maximum total cook + prep time in minutes", ge=5
    )
    flavor_profile: Optional[list[str]] = Field(
        default=None,
        description="Desired flavor notes (e.g. spicy, umami, fresh)",
        examples=[["spicy", "savory"]],
    )
    n_recommendations: int = Field(default=3, ge=1, le=5, description="Number of recommendations to return")
    course_preference: Optional[str] = Field(default=None, description="Preferred meal course")


class IngredientMatch(BaseModel):
    have: list[str]
    need: list[str]
    match_percentage: float
    substitutions: dict[str, str]


class RecommendedRecipe(BaseModel):
    recipe: Recipe
    match_score: float
    ingredient_match: IngredientMatch
    why_it_fits: str
    personalization_notes: str
    thyme_machine_says: str


class RecommendationResponse(BaseModel):
    query_summary: str
    recommendations: list[RecommendedRecipe]
    general_tip: str
    total_recipes_considered: int
