# Rasaveda · रसवेद
### *Knowledge of Flavors*

> "Tell us what's in your pantry — we'll handle the rest."

Rasaveda is a RAG-powered recipe recommendation app that turns whatever's sitting in your fridge into a personalized, explainable meal. It uses semantic vector search over a curated library of 108+ global recipes (with a deep focus on Indian regional cuisine), then calls **Qwen2.5-7B** via the HuggingFace Inference API to generate grounded, poetic recommendations — ranked by pantry match, dietary needs, and flavor preference.

---

## Features

| Tab | What it does |
|---|---|
| **Find a Recipe** | Enter your pantry ingredients — get AI-ranked recipe picks with match % bars, ingredient gap analysis, substitution suggestions, and full cookbook-style instructions |
| **Add Your Recipe** | Submit your own recipe with full metadata; it's immediately embedded into ChromaDB and searchable alongside the built-in dataset |
| **Improve** | Pick any recipe and get a step-by-step AI analysis — each cooking step is either validated or improved with reasoning rooted in classical technique |
| **My Library** | Browse and manage all personal recipes you've added |
| **Chat** | Conversational culinary guide — ask about techniques, substitutions, regional traditions, or anything food-related; RAG-grounded answers |

### Visual Themes
Five hand-crafted Indian regional aesthetics, switchable from the sidebar:

- 🪔 **Saffron Palace** — Mughal · North India
- 🌴 **Malabar Coast** — Kerala · South India
- 🏰 **Rajputana Desert** — Rajasthan · West India
- 🌸 **Bengal Delta** — West Bengal · East India
- 🔥 **Tandoor Nights** — Punjab · North India

---

## Architecture

```
Rasaveda
├── app.py                  — Streamlit UI (5 tabs, 5 themes, custom HTML/CSS)
├── main.py                 — FastAPI server entry point (optional REST API)
├── data/                   — Recipe JSON datasets (108 recipes)
│   ├── recipes.json
│   ├── indian_recipes.json
│   ├── foundational_recipes.json
│   └── ...
└── thyme_machine/          — Core library
    ├── config.py           — Pydantic settings (env vars)
    ├── models.py           — Recipe, RecommendationRequest, RecommendationResponse
    ├── ingestion.py        — JSON → ChromaDB pipeline (sentence-transformers)
    ├── retrieval.py        — Vector + metadata search
    ├── generation.py       — RAG prompt builder + Qwen2.5 call
    ├── improvement.py      — Step-by-step recipe analysis
    ├── chatbot.py          — Conversational RAG chat
    ├── images.py           — Wikipedia dish image fetcher with local cache
    ├── themes.py           — 5 CSS variable theme systems
    ├── user_recipes.py     — Personal recipe CRUD + ChromaDB sync
    └── chat_history.py     — Persistent chat history
```

**Stack:** Streamlit · ChromaDB · Sentence Transformers (`all-MiniLM-L6-v2`) · HuggingFace Inference API (Qwen2.5-7B-Instruct) · FastAPI · Pydantic · Python 3.10+

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/your-username/rasaveda.git
cd rasaveda
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your HuggingFace token (free — needs Inference API access):

```env
HUGGINGFACE_TOKEN=hf_your_token_here
```

Get one at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — "Read" access is sufficient.

### 3. Run the app

```bash
streamlit run app.py
```

On first launch, Rasaveda auto-indexes all 108 recipes into ChromaDB (takes ~30 seconds to download and run the embedding model). Subsequent starts are instant.

### Optional: FastAPI REST server

```bash
python main.py
# or
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`.

---

## How it works

1. **Ingest** — Recipe JSON files are converted to rich text documents and embedded with `all-MiniLM-L6-v2` into a ChromaDB collection with cosine similarity.
2. **Retrieve** — Your pantry input is embedded and queried against ChromaDB. Metadata filters (cuisine, dietary, time, course) narrow the candidate set.
3. **Match** — Ingredient overlap is computed per recipe: what you have, what you need, and known substitutions.
4. **Generate** — A grounded prompt (system persona + user context + retrieved recipes + ingredient matches) is sent to Qwen2.5-7B-Instruct. The model returns structured JSON: ranked recommendations with `why_it_fits`, personalization notes, and a signature "Rasaveda says" line.
5. **Display** — Cards render with match bars, ingredient pills, full cookbook view, and Wikipedia dish images.

---

## Configuration

All settings are environment variables (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `HUGGINGFACE_TOKEN` | *(required)* | HuggingFace API token |
| `HF_MODEL` | `Qwen/Qwen2.5-7B-Instruct` | Generation model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `COLLECTION_NAME` | `rasaveda_recipes` | ChromaDB collection name |
| `TOP_K_RESULTS` | `8` | Candidate recipes retrieved per search |
| `RECIPES_PATH` | `./data/recipes.json` | Path used to resolve the data directory |

---

## Dataset

108 recipes across Indian and world cuisines, organized in six JSON files:

- **Indian** (32 recipes) — dal, biryani, curries, breads, snacks, desserts
- **Indian regional** (32 recipes) — Kerala, Bengal, Rajasthan, Punjab, South India
- **Foundational** (15 recipes) — pantry basics: ghee, paneer, garam masala, stocks
- **World** (29 recipes) — Italian, Japanese, Mexican, French, Mediterranean, Korean, and more

Each recipe carries: ingredients + quantities, step-by-step instructions, dietary tags, flavor profile, difficulty, prep/cook time, servings, cuisine, course, and tips.

---

## Requirements

- Python 3.10+
- HuggingFace account (free tier works)
- ~500 MB disk for the embedding model (`all-MiniLM-L6-v2`, downloaded on first run)

```
huggingface_hub>=0.26.0
chromadb>=0.5.0
streamlit>=1.40.0
pydantic>=2.10.0
pydantic-settings>=2.0.0
sentence-transformers>=3.0.0
python-dotenv>=1.0.0
rich>=13.0.0
typer>=0.12.0
```

---

## Project structure notes

- `chroma_db/` is generated on first run and gitignored — do not commit it
- `data/image_cache.json` caches Wikipedia image URLs so repeat lookups are instant
- User recipes are stored in `data/user_recipes.json` and synced into ChromaDB at runtime
- Chat history persists in `data/chat_history.json`

---

## License

Apache License 2.0
