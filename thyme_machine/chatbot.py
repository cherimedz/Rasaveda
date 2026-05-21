"""
Conversational layer — Rasaveda chat mode.
Uses the same Qwen2.5-7B Inference API with optional RAG context from ChromaDB.
"""

from huggingface_hub import InferenceClient

from thyme_machine.config import settings

_SYSTEM = (
    "You are Rasaveda (रसवेद) — a warm, knowledgeable culinary guide specializing in "
    "Indian cuisine with deep familiarity across all world cuisines. "
    "You help users discover recipes, understand cooking techniques, substitute ingredients, "
    "learn about regional food traditions, troubleshoot cooking problems, and improve their dishes. "
    "Keep responses concise (2-4 short paragraphs max), friendly, and practical. "
    "Use specific dish names, spice names, and regional terms where relevant. "
    "If recipe context is provided, prioritize it — but you may draw on general culinary knowledge too."
)


def chat_response(
    message: str,
    history: list[dict],
    recipe_context: str = "",
) -> str:
    """
    Generate a conversational reply.

    history: list of {"role": "user"|"assistant", "content": str} — last N turns
    recipe_context: formatted text block of semantically relevant recipes from ChromaDB
    """
    client = InferenceClient(model=settings.hf_model, token=settings.huggingface_token)

    system_content = _SYSTEM
    if recipe_context:
        system_content += (
            "\n\nRelevant recipes from the Rasaveda database "
            "(use these as grounding when answering):\n" + recipe_context
        )

    messages = [{"role": "system", "content": system_content}]
    for turn in history[-12:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": message})

    try:
        result = client.chat_completion(
            messages=messages,
            temperature=0.55,
            max_tokens=700,
            stream=False,
        )
        return result.choices[0].message.content.strip()
    except Exception as e:
        return (
            "I find myself momentarily quiet — the stars of flavor are aligning. "
            f"Please try again in a moment. *(Error: {e})*"
        )
