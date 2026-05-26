"""
Per-step recipe improvement: analyzes each instruction step and suggests
technique, timing, and flavor improvements using the configured LLM.
"""

import json
import re
from dataclasses import dataclass

from thyme_machine.llm_client import chat_complete
from thyme_machine.models import Recipe


@dataclass
class StepImprovement:
    step_number: int
    original: str
    improved: str
    reasoning: str
    has_improvement: bool


@dataclass
class RecipeImprovement:
    overall_assessment: str
    improvements: list[StepImprovement]
    general_tips: list[str]


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Cannot parse JSON from model output:\n{text[:400]}")


def suggest_improvements(recipe: Recipe) -> RecipeImprovement:
    """
    Send all recipe steps to the LLM and get back a structured
    improvement analysis per step.
    """
    steps_text = "\n".join(
        f"{i + 1}. {step}" for i, step in enumerate(recipe.instructions)
    )
    ingredients_text = ", ".join(recipe.ingredients)

    system_prompt = (
        "You are Rasaveda (रसवेद) — a master of Indian cuisine and classical cooking technique. "
        "You analyze recipe steps and suggest specific, actionable improvements grounded in technique: "
        "caramelization, Maillard reaction, spice blooming, emulsification, tempering, "
        "bhunao, dum cooking, deglazing, and heat management. "
        "Be honest — if a step is already perfect, say so. "
        "Output ONLY a single valid JSON object with no markdown or preamble."
    )

    user_prompt = f"""Analyze this recipe step by step and suggest improvements:

Recipe Name: {recipe.name}
Cuisine: {recipe.cuisine}
Description: {recipe.description}
Key Ingredients: {ingredients_text}

Steps to analyze:
{steps_text}

Respond with ONLY this JSON structure:
{{
  "overall_assessment": "2-3 sentence honest assessment of the recipe's technique level and main opportunities",
  "improvements": [
    {{
      "step_number": 1,
      "original": "the exact original step text",
      "improved": "your improved version, or the same text if no change is needed",
      "reasoning": "specific, technical explanation of why this change matters, OR why the original is already correct",
      "has_improvement": true
    }}
  ],
  "general_tips": [
    "3-5 broader tips relevant to this recipe type"
  ]
}}

For Indian recipes, address where relevant: onion caramelization depth, bhunao technique (frying out the masala),
spice tempering order, dum cooking sealing, hydration of dough, oil separation as doneness indicator,
yogurt addition technique (to prevent curdling), and salt timing."""

    raw = chat_complete(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=3000,
        temperature=0.25,
    )
    parsed = _extract_json(raw)

    improvements = [
        StepImprovement(
            step_number=imp.get("step_number", i + 1),
            original=imp.get("original", ""),
            improved=imp.get("improved", ""),
            reasoning=imp.get("reasoning", ""),
            has_improvement=bool(imp.get("has_improvement", False)),
        )
        for i, imp in enumerate(parsed.get("improvements", []))
    ]

    return RecipeImprovement(
        overall_assessment=parsed.get("overall_assessment", ""),
        improvements=improvements,
        general_tips=parsed.get("general_tips", []),
    )
