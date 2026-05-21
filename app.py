"""
Rasaveda (रसवेद) — Knowledge of Flavors
Streamlit app: Find · Add (with image crop) · Improve · Browse · Library · Chat  +  5 Indian visual themes
"""

import html as _html
import io
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Rasaveda · रसवेद",
    page_icon="🍛",
    layout="wide",
    initial_sidebar_state="expanded",
)

from thyme_machine.config import settings
from thyme_machine.generation import generate_recommendations
from thyme_machine.improvement import RecipeImprovement, suggest_improvements
from thyme_machine.ingestion import get_recipe_count, ingest_recipes, load_recipes
from thyme_machine.models import Difficulty, Recipe, RecommendationRequest
from thyme_machine.retrieval import retrieve_recipes
from thyme_machine.chatbot import chat_response
from thyme_machine.chat_history import clear_chat_history, load_chat_history, save_chat_history
from thyme_machine.images import get_recipe_image as _fetch_image, get_user_image_data_url
from thyme_machine.retrieval import search_by_text
from thyme_machine.themes import DISH_GRADIENTS, THEMES, build_theme_css, get_dish_gradient
from thyme_machine.user_recipes import (
    delete_user_recipe,
    generate_recipe_id,
    load_user_recipes,
    save_user_recipe,
    save_user_image,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Icon HTML snippets (Font Awesome 6 Free, loaded via CDN in main())
_FA_UTENSILS  = '<i class="fa-solid fa-utensils fa-sm"></i>'
_FA_CLOCK     = '<i class="fa-regular fa-clock fa-sm"></i>'
_FA_USERS     = '<i class="fa-solid fa-users fa-sm"></i>'
_FA_CHECK     = '<i class="fa-solid fa-check fa-sm"></i>'
_FA_CART      = '<i class="fa-solid fa-cart-shopping fa-sm"></i>'
_FA_BULB      = '<i class="fa-solid fa-lightbulb fa-sm"></i>'
_FA_FIRE      = '<i class="fa-solid fa-fire fa-sm"></i>'
_FA_HOURGLASS = '<i class="fa-solid fa-hourglass-half fa-sm"></i>'
_FA_KNIFE     = '<i class="fa-solid fa-kitchen-set fa-sm"></i>'
_FA_TREND     = '<i class="fa-solid fa-arrow-trend-up fa-sm"></i>'
_FA_DOT       = '<i class="fa-solid fa-circle-dot fa-sm"></i>'
_FA_CIRCLEOK  = '<i class="fa-solid fa-circle-check fa-sm"></i>'
_FA_CHART     = '<i class="fa-solid fa-chart-bar fa-sm"></i>'

RANK_BADGES = ["1", "2", "3", "4", "5"]
ALL_COURSES = [
    "Main Course", "Appetizer", "Soup", "Dessert",
    "Bread", "Side Dish", "Breakfast", "Beverage",
    "Basics", "Condiment",
]
ALL_DIETARY   = [
    "vegan", "vegetarian", "gluten-free", "dairy-free",
    "low-carb", "keto", "paleo", "nut-free", "halal", "kosher",
]
ALL_FLAVORS   = [
    "spicy", "savory", "umami", "sweet", "tangy", "earthy",
    "fresh", "smoky", "creamy", "rich", "aromatic", "pungent", "light",
]
ALL_CUISINES  = [
    "Indian", "Italian", "Mexican", "Japanese", "Thai", "Chinese",
    "French", "Mediterranean", "Greek", "Korean", "Middle Eastern",
    "American", "Contemporary",
    "Vietnamese", "Moroccan", "Spanish", "Indonesian", "Turkish", "Ethiopian", "Lebanese",
]
INDIAN_REGIONS = [
    "North Indian", "South Indian", "East Indian", "West Indian",
    "Mughlai", "Punjabi", "Bengali", "Rajasthani", "Gujarati",
    "Maharashtrian", "Keralan", "Hyderabadi", "Kashmiri", "Goan", "Chettinad",
]
DEFAULT_THEME = "saffron"


def _safe_html(text: str) -> str:
    """Escape text for safe embedding inside an HTML block. Newlines must be collapsed
    because a blank line in a Streamlit markdown HTML block terminates the block,
    causing everything after to render as raw text."""
    return _html.escape(str(text)).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

# ---------------------------------------------------------------------------
# Base CSS — uses CSS variables; themes override :root values
# ---------------------------------------------------------------------------

BASE_CSS = """
<style>
/* ── Typography & global ─────────────────────────────── */
.ras-header {
  text-align: center;
  padding: 1.4rem 1rem 0.8rem;
  border-bottom: 2px solid var(--t-secondary);
  margin-bottom: 1.5rem;
  position: relative;
}
.ras-deco {
  font-size: 1.05rem;
  letter-spacing: .2em;
  color: var(--t-muted);
  margin-bottom: .5rem;
}
.ras-title {
  font-size: 2.8rem;
  font-weight: 900;
  color: var(--t-heading);
  letter-spacing: .04em;
  margin: 0;
  line-height: 1;
}
.ras-sans {
  font-size: 1.35rem;
  color: var(--t-sans);
  margin: .25rem 0 0;
  letter-spacing: .18em;
}
.ras-tag {
  font-size: .88rem;
  color: var(--t-muted);
  font-style: italic;
  margin-top: .4rem;
}

/* ── Theme selector ──────────────────────────────────── */
.theme-swatch-row {
  display: flex;
  gap: 6px;
  margin: .4rem 0 .6rem;
  border-radius: 8px;
  overflow: hidden;
}
.swatch-seg {
  height: 6px;
  flex: 1;
  border-radius: 3px;
}

/* ── Recipe card ─────────────────────────────────────── */
.rec-card {
  background: var(--t-card);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 1.4rem;
  box-shadow: 0 3px 14px rgba(0,0,0,0.09);
  border-left: 5px solid var(--t-card-border);
}
.rec-thumb {
  width: 100%;
  height: 7px;
}
.rec-body {
  padding: 1.2rem 1.4rem 1.4rem;
}
.card-head {
  display: flex;
  align-items: center;
  gap: .7rem;
  margin-bottom: .65rem;
}
.rank-b {
  min-width: 32px;
  height: 32px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: .88rem;
  font-weight: 900;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,.2);
  letter-spacing: 0;
}
.rank-pos-1 { background: linear-gradient(135deg, #b8860b, #ffd700); }
.rank-pos-2 { background: linear-gradient(135deg, #9e9e9e, #e0e0e0); color: #333 !important; }
.rank-pos-3 { background: linear-gradient(135deg, #8b5e3c, #cd7f32); }
.rank-pos-4 { background: linear-gradient(135deg, #2e7d4f, #4caf7d); }
.rank-pos-5 { background: linear-gradient(135deg, #1565c0, #4285f4); }
.rec-name { font-size: 1.3rem; font-weight: 800; color: var(--t-text); }
.score-b  {
  margin-left: auto;
  background: var(--t-tag-bg);
  color: var(--t-tag-text);
  padding: .15rem .65rem;
  border-radius: 20px;
  font-size: .82rem;
  font-weight: 700;
}

/* ── Meta tags ───────────────────────────────────────── */
.meta-row { display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: .9rem; }
.m-tag  {
  background: var(--t-tag-bg);
  color: var(--t-tag-text);
  padding: .2rem .6rem;
  border-radius: 10px;
  font-size: .78rem;
  font-weight: 500;
}
.m-easy   { background:#d4edda; color:#155724; }
.m-medium { background:#fff3cd; color:#856404; }
.m-hard   { background:#f8d7da; color:#721c24; }

/* ── Ingredient match ────────────────────────────────── */
.match-bar-wrap {
  background: rgba(0,0,0,.07);
  border-radius: 8px;
  height: 9px;
  overflow: hidden;
  margin: .3rem 0 .8rem;
}
.match-bar-fill {
  height: 100%;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--t-prog-a), var(--t-prog-b));
  transition: width .6s ease;
}
.ing-grid  { display:grid; grid-template-columns:1fr 1fr; gap:.6rem; margin-bottom:.7rem; }
.ing-box   { background: rgba(0,0,0,.035); border-radius:9px; padding:.5rem .7rem; }
.ing-box.hv { border-top: 3px solid #28a745; }
.ing-box.nd { border-top: 3px solid #dc3545; }
.ing-ttl   {
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--t-muted);
  margin-bottom: .3rem;
}
.ing-pill {
  display: inline-block;
  padding: .12rem .45rem;
  border-radius: 7px;
  font-size: .76rem;
  margin: .12rem .08rem;
}
.hv-p { background:#d4edda; color:#155724; }
.nd-p { background:#f8d7da; color:#721c24; }

.sub-box {
  background: rgba(0,0,0,.04);
  border-radius: 8px;
  padding: .45rem .65rem;
  font-size: .78rem;
  color: var(--t-muted);
  margin-top: .4rem;
  border-left: 3px solid var(--t-secondary);
}

/* ── Section labels ──────────────────────────────────── */
.sec-lbl {
  font-size: .74rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .09em;
  color: var(--t-primary);
  margin: .65rem 0 .25rem;
}
.sec-body {
  font-size: .92rem;
  color: var(--t-text);
  line-height: 1.65;
  margin-bottom: .5rem;
}

/* ── Rasaveda quote ──────────────────────────────────── */
.ras-q {
  background: linear-gradient(135deg, var(--t-tag-bg), rgba(0,0,0,.02));
  border-left: 4px solid var(--t-secondary);
  border-radius: 0 10px 10px 0;
  padding: .65rem .9rem;
  font-style: italic;
  color: var(--t-muted);
  font-size: .88rem;
  margin-top: .8rem;
}
.ras-q::before {
  content: "✦ Rasaveda: ";
  font-weight: 700;
  font-style: normal;
  color: var(--t-heading);
}

/* ── Summary banner ──────────────────────────────────── */
.banner {
  background: linear-gradient(90deg, var(--t-banner-a), var(--t-banner-b));
  color: #fff;
  padding: .9rem 1.3rem;
  border-radius: 12px;
  margin-bottom: 1.2rem;
}
.ban-tip  { opacity:.82; font-size:.85rem; margin-top:.25rem; }
.ban-meta { opacity:.55; font-size:.76rem; margin-top:.3rem; }

/* ── Step improvements ───────────────────────────────── */
.step-ok {
  background: var(--t-step-ok-bg);
  border-left: 4px solid var(--t-step-ok-border);
  border-radius: 0 9px 9px 0;
  padding: .6rem .9rem;
  margin: .5rem 0;
}
.step-imp {
  background: var(--t-step-imp-bg);
  border-left: 4px solid var(--t-step-imp-border);
  border-radius: 0 9px 9px 0;
  padding: .6rem .9rem;
  margin: .5rem 0;
}
.step-orig { font-size:.82rem; color:var(--t-muted); margin-bottom:.3rem; }
.step-new  { font-size:.9rem;  color:var(--t-text);  font-weight:500; margin-bottom:.25rem; }
.step-why  { font-size:.8rem;  color:var(--t-muted); font-style:italic; }

.tip-chip {
  background: var(--t-tag-bg);
  color: var(--t-tag-text);
  padding: .35rem .75rem;
  border-radius: 20px;
  font-size: .82rem;
  display: inline-block;
  margin: .2rem;
  border: 1px solid var(--t-divider);
}

/* ── Sidebar section labels ──────────────────────────── */
.sb-sect {
  font-size: .72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: .1em !important;
  color: var(--t-sans) !important;
  margin: 1rem 0 .15rem !important;
}

/* ── Empty state ─────────────────────────────────────── */
.empty-s   { text-align:center; padding:3rem 1rem; color:var(--t-empty-color); }
.empty-s .ico { font-size:3.5rem; color:var(--t-muted); margin-bottom:.5rem; }

/* ── Library card ────────────────────────────────────── */
.lib-thumb {
  width: 100%;
  height: 5px;
  border-radius: 4px 4px 0 0;
}

/* ── Recipe image thumbnail ──────────────────────────── */
.rec-img {
  width: 100%;
  height: 240px;
  object-fit: cover;
  display: block;
}

/* ── Cookbook full-recipe view ───────────────────────── */
.cookbook-page { padding: .2rem 0; }
.cb-times {
  display: flex;
  flex-wrap: wrap;
  gap: .4rem;
  margin-bottom: 1.1rem;
}
.cb-time-chip {
  background: var(--t-tag-bg);
  color: var(--t-tag-text);
  border: 1px solid var(--t-divider);
  border-radius: 20px;
  padding: .25rem .75rem;
  font-size: .82rem;
  font-weight: 600;
}
.cb-section { margin-bottom: 1.5rem; }
.cb-section-title {
  font-size: .8rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: var(--t-primary);
  border-bottom: 2px solid var(--t-divider);
  padding-bottom: .4rem;
  margin-bottom: .9rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cb-serves {
  font-size: .78rem;
  color: var(--t-muted);
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0;
}
.cb-ingredients {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 1.2rem;
}
.cb-ing-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: .3rem 0;
  border-bottom: 1px dotted var(--t-divider);
  font-size: .87rem;
  gap: .5rem;
}
.cb-ing-name { color: var(--t-text); font-weight: 500; }
.cb-ing-qty  { color: var(--t-muted); font-style: italic; white-space: nowrap; }
.cb-steps { display: flex; flex-direction: column; gap: .75rem; }
.cb-step {
  display: flex;
  gap: .9rem;
  align-items: flex-start;
}
.cb-step-num {
  min-width: 30px;
  height: 30px;
  background: linear-gradient(135deg, var(--t-primary), var(--t-banner-b));
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .78rem;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: .1rem;
  box-shadow: 0 2px 6px rgba(0,0,0,.15);
}
.cb-step-text {
  font-size: .9rem;
  color: var(--t-text);
  line-height: 1.7;
  padding-top: .2rem;
}
.cb-tip {
  background: linear-gradient(135deg, var(--t-tag-bg), rgba(0,0,0,.01));
  border-left: 4px solid var(--t-secondary);
  border-radius: 0 10px 10px 0;
  padding: .75rem 1.1rem;
  margin-top: .5rem;
}
.cb-tip-label {
  font-size: .72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--t-secondary);
  margin-bottom: .35rem;
}
.cb-tip-text {
  font-size: .88rem;
  color: var(--t-text);
  line-height: 1.65;
}

/* ── Chat tab ────────────────────────────────────────── */
.chat-welcome {
  background: linear-gradient(135deg, var(--t-tag-bg), rgba(0,0,0,.02));
  border-radius: 14px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--t-divider);
}
.chat-welcome h3 {
  color: var(--t-heading) !important;
  margin-bottom: .4rem;
}
.chat-suggestion {
  display: inline-block;
  background: var(--t-tag-bg);
  color: var(--t-tag-text);
  border: 1px solid var(--t-divider);
  border-radius: 20px;
  padding: .3rem .8rem;
  font-size: .83rem;
  margin: .2rem;
  cursor: default;
}
</style>
"""

# ---------------------------------------------------------------------------
# Startup & caching
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Rasaveda is awakening — indexing recipes...")
def startup() -> int:
    from pathlib import Path as _P
    file_count = len(load_recipes(str(_P(settings.recipes_path).parent)))
    db_count = get_recipe_count()
    if db_count < file_count:
        ingest_recipes(force=(db_count > 0))
    return get_recipe_count()


@st.cache_data(ttl=600)
def cached_base_recipes() -> list[Recipe]:
    from pathlib import Path
    return load_recipes(str(Path(settings.recipes_path).parent))


def _active_theme() -> str:
    return st.session_state.get("rasaveda_theme", DEFAULT_THEME)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def _header():
    t = THEMES[_active_theme()]
    st.markdown(f"""
<div class="ras-header">
  <div class="ras-deco">{t['header_deco']}</div>
  <p class="ras-title">Rasaveda</p>
  <p class="ras-sans">&#x930;&#x938;&#x935;&#x947;&#x926;</p>
  <p class="ras-tag">{t['region']} &mdash; {t['tagline']}</p>
</div>""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Theme selector — rendered at the top of the sidebar
# ---------------------------------------------------------------------------

def _theme_selector():
    with st.sidebar:
        # Logo
        st.markdown(
            '<p style="font-size:1.4rem;font-weight:900;color:#FF9933;margin:0;">'
            '<i class="fa-solid fa-mortar-pestle"></i>&nbsp; Rasaveda</p>'
            '<p style="font-size:.72rem;color:#c09060;margin:0 0 .5rem;letter-spacing:.08em;">Knowledge of Flavors</p>',
            unsafe_allow_html=True,
        )

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-palette fa-xs"></i>&nbsp; Visual Theme</p>', unsafe_allow_html=True)

        # Theme radio
        chosen = st.radio(
            "theme_radio",
            options=list(THEMES.keys()),
            format_func=lambda k: f"{THEMES[k]['emoji']}  {THEMES[k]['name']}",
            index=list(THEMES.keys()).index(_active_theme()),
            label_visibility="collapsed",
        )
        if chosen != _active_theme():
            st.session_state["rasaveda_theme"] = chosen
            st.rerun()

        # Color swatch preview for active theme
        t = THEMES[chosen]
        segs = "".join(
            f'<div class="swatch-seg" style="background:{c};"></div>'
            for c in t["swatches"]
        )
        st.markdown(
            f'<div class="theme-swatch-row">{segs}</div>'
            f'<p style="font-size:.75rem;color:#c09060;font-style:italic;margin:0 0 .5rem;">'
            f'{t["welcome_quote"]}</p>',
            unsafe_allow_html=True,
        )
        st.markdown('<hr style="border-color:#3a2010;margin:.6rem 0;">', unsafe_allow_html=True)


# ===========================================================================
# TAB 1 — FIND A RECIPE
# ===========================================================================

def _sidebar_find() -> dict | None:
    """Render Find inputs below the theme selector. Returns inputs dict or None."""
    with st.sidebar:
        st.markdown('<p class="sb-sect"><i class="fa-solid fa-basket-shopping fa-xs"></i>&nbsp; Your Pantry</p>', unsafe_allow_html=True)
        ings_raw = st.text_area(
            "Ingredients",
            placeholder="chicken, garlic, onion, garam masala, yogurt...",
            height=100, label_visibility="collapsed",
        )

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-leaf fa-xs"></i>&nbsp; Dietary Preferences</p>', unsafe_allow_html=True)
        dietary = st.multiselect("Dietary", ALL_DIETARY, default=[], label_visibility="collapsed")

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-globe fa-xs"></i>&nbsp; Cuisine</p>', unsafe_allow_html=True)
        cuisine_opts = ["Any (show all)"] + ALL_CUISINES
        cuisine = st.selectbox("Cuisine", cuisine_opts, index=1, label_visibility="collapsed")

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-pepper-hot fa-xs"></i>&nbsp; Flavor Profile</p>', unsafe_allow_html=True)
        flavors = st.multiselect("Flavors", ALL_FLAVORS, default=[], label_visibility="collapsed")

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-bowl-food fa-xs"></i>&nbsp; Course</p>', unsafe_allow_html=True)
        course_opts = ["Any course"] + ALL_COURSES
        course_pref = st.selectbox("Course", course_opts, index=0, label_visibility="collapsed")

        st.markdown('<p class="sb-sect"><i class="fa-regular fa-clock fa-xs"></i>&nbsp; Max Cooking Time</p>', unsafe_allow_html=True)
        max_time = st.slider("minutes", 10, 300, 120, 10, label_visibility="collapsed")

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-users fa-xs"></i>&nbsp; Servings</p>', unsafe_allow_html=True)
        servings = st.number_input("Servings", 1, 20, 4, label_visibility="collapsed")

        st.markdown('<p class="sb-sect"><i class="fa-solid fa-star fa-xs"></i>&nbsp; Recommendations</p>', unsafe_allow_html=True)
        n_recs = st.slider("How many", 1, 5, 3, 1, label_visibility="collapsed")

        st.markdown("---")
        clicked = st.button("Find My Recipe", use_container_width=True, type="primary")
        st.caption(f"Searching {get_recipe_count()} recipes · Qwen2.5-7B")

    if not clicked:
        return None
    ings = [i.strip() for i in ings_raw.replace("\n", ",").split(",") if i.strip()]
    if not ings:
        st.sidebar.error("Enter at least one ingredient.")
        return None
    return {
        "available_ingredients": ings,
        "dietary_preferences": dietary,
        "cuisine_preference": None if "Any" in cuisine else cuisine,
        "flavor_profile": flavors or None,
        "max_cook_time_minutes": max_time,
        "servings": servings,
        "n_recommendations": n_recs,
        "course_preference": None if course_pref == "Any course" else course_pref,
    }


def _progress_bar(pct: float) -> str:
    return (
        f'<div class="match-bar-wrap">'
        f'<div class="match-bar-fill" style="width:{pct}%;"></div>'
        f'</div>'
    )


def _pills(items: list[str], cls: str) -> str:
    return "".join(
        f'<span class="ing-pill {cls}">{i}</span>' for i in items
    ) or f'<span style="font-size:.76rem;color:var(--t-muted);">{"none" if cls=="nd-p" else "You have it all!"}</span>'


def _make_thumb_html(img_url: str | None, gradient: str, name: str) -> str:
    if img_url:
        return f'<img src="{img_url}" class="rec-img" alt="{_safe_html(name)}">'
    return (
        f'<div style="background:{gradient};height:240px;display:flex;'
        f'align-items:center;justify-content:center;">'
        f'<span style="color:rgba(255,255,255,0.92);font-size:1.15rem;font-weight:800;'
        f'text-shadow:0 2px 10px rgba(0,0,0,0.55);padding:1rem;text-align:center;'
        f'letter-spacing:.02em;">{_safe_html(name)}</span>'
        f'</div>'
    )


def _recipe_card(rec, rank: int):
    r = rec.recipe
    badge   = RANK_BADGES[rank]
    rank_cls = f"rank-pos-{rank + 1}"
    score   = int(rec.match_score * 100)
    total   = r.prep_time_minutes + r.cook_time_minutes
    diff    = r.difficulty.value
    thumb   = get_dish_gradient(r.cuisine, r.name)
    match   = rec.ingredient_match
    pct     = match.match_percentage
    tags    = "".join(f'<span class="m-tag">{_safe_html(t)}</span>' for t in r.dietary_tags[:3])

    sub_html = ""
    if match.substitutions:
        rows = "".join(
            f"<b>{_safe_html(k)}</b> &rarr; {_safe_html(v)}<br>"
            for k, v in match.substitutions.items()
        )
        sub_html = f'<div class="sub-box">{_FA_BULB} Substitutions:<br>{rows}</div>'

    img_url = _fetch_image(r.name, r.cuisine, image_path=getattr(r, "image_path", None))
    thumb_html = _make_thumb_html(img_url, thumb, r.name)

    # Escape all LLM-generated text — newlines inside an HTML block break Streamlit's renderer
    why_html      = _safe_html(rec.why_it_fits)
    personal_html = _safe_html(rec.personalization_notes)
    ras_html      = _safe_html(rec.thyme_machine_says)

    # Build card HTML as a single string — avoids blank lines from empty f-string substitutions
    # (blank lines in a Streamlit unsafe_allow_html block terminate the CommonMark HTML block)
    card_html = (
        f'<div class="rec-card">'
        f'{thumb_html}'
        f'<div class="rec-body">'
        f'<div class="card-head">'
        f'<span class="rank-b {rank_cls}">{badge}</span>'
        f'<span class="rec-name">{_safe_html(r.name)}</span>'
        f'<span class="score-b">{score}% fit</span>'
        f'</div>'
        f'<div class="meta-row">'
        f'<span class="m-tag">{_FA_UTENSILS} {_safe_html(r.cuisine)}</span>'
        f'<span class="m-tag m-{diff}">{diff.capitalize()}</span>'
        f'<span class="m-tag">{_FA_CLOCK} {total} min</span>'
        f'<span class="m-tag">{_FA_USERS} {r.servings} servings</span>'
        + (f'{tags}' if tags else '')
        + (f'<span class="m-tag" style="background:var(--t-tag-bg);color:var(--t-tag-text);">'
           f'{_FA_UTENSILS} {_safe_html(r.course)}</span>' if r.course else '')
        + f'</div>'
        f'<div class="sec-lbl">Ingredient Match &mdash; {pct}%</div>'
        f'{_progress_bar(pct)}'
        f'<div class="ing-grid">'
        f'<div class="ing-box hv">'
        f'<div class="ing-ttl">{_FA_CHECK} You Have ({len(match.have)})</div>'
        f'{_pills(match.have, "hv-p")}'
        f'</div>'
        f'<div class="ing-box nd">'
        f'<div class="ing-ttl">{_FA_CART} You Need ({len(match.need)})</div>'
        f'{_pills(match.need, "nd-p")}'
        f'</div>'
        f'</div>'
        + (sub_html if sub_html else '')
        + f'<div class="sec-lbl">Why it fits</div>'
        f'<div class="sec-body">{why_html}</div>'
        f'<div class="sec-lbl">Personalization</div>'
        f'<div class="sec-body">{personal_html}</div>'
        f'<div class="ras-q">{ras_html}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # Cookbook-style full recipe expander
    with st.expander(f"Full Recipe — {r.name}"):
        ing_rows = "".join(
            f'<div class="cb-ing-row">'
            f'<span class="cb-ing-name">{_safe_html(ing)}</span>'
            f'<span class="cb-ing-qty">{_safe_html(qty)}</span>'
            f'</div>'
            for ing, qty in r.ingredient_quantities.items()
        )
        step_rows = "".join(
            f'<div class="cb-step">'
            f'<div class="cb-step-num">{i}</div>'
            f'<div class="cb-step-text">{_safe_html(step)}</div>'
            f'</div>'
            for i, step in enumerate(r.instructions, 1)
        )
        tip_block = ""
        if r.tips:
            tip_block = (
                f'<div class="cb-tip">'
                f'<div class="cb-tip-label">{_FA_BULB} Chef\'s Tip</div>'
                f'<div class="cb-tip-text">{_safe_html(r.tips)}</div>'
                f'</div>'
            )
        time_chips = (
            f'<div class="cb-times">'
            f'<span class="cb-time-chip">{_FA_KNIFE} Prep: {r.prep_time_minutes} min</span>'
            f'<span class="cb-time-chip">{_FA_FIRE} Cook: {r.cook_time_minutes} min</span>'
            f'<span class="cb-time-chip">{_FA_HOURGLASS} Total: {total} min</span>'
            f'</div>'
        )
        st.markdown(f"""<div class="cookbook-page">
          {time_chips}
          <div class="cb-section">
            <div class="cb-section-title">
              Ingredients
              <span class="cb-serves">Serves {r.servings}</span>
            </div>
            <div class="cb-ingredients">{ing_rows}</div>
          </div>
          <div class="cb-section">
            <div class="cb-section-title">Method</div>
            <div class="cb-steps">{step_rows}</div>
          </div>
          {tip_block}
        </div>""", unsafe_allow_html=True)


def _simple_recipe_card(retrieved_recipe, idx: int):
    """Compact card for the browse-more section — no AI description, just metadata."""
    r = retrieved_recipe.recipe
    total = r.prep_time_minutes + r.cook_time_minutes
    diff = r.difficulty.value
    thumb = get_dish_gradient(r.cuisine, r.name)
    score = int(retrieved_recipe.similarity_score * 100)
    tags = "".join(f'<span class="m-tag">{_safe_html(t)}</span>' for t in r.dietary_tags[:2])
    course_tag = (f'<span class="m-tag" style="font-style:italic;">{_safe_html(r.course)}</span>'
                  if r.course else "")
    card = (
        f'<div class="rec-card" style="opacity:0.92;">'
        f'<div style="background:{thumb};height:5px;"></div>'
        f'<div class="rec-body" style="padding:.9rem 1.2rem;">'
        f'<div class="card-head" style="margin-bottom:.4rem;">'
        f'<span style="font-size:.78rem;font-weight:700;color:var(--t-muted);min-width:28px;">#{idx}</span>'
        f'<span class="rec-name" style="font-size:1.05rem;">{_safe_html(r.name)}</span>'
        f'<span class="score-b">{score}%</span>'
        f'</div>'
        f'<div class="meta-row" style="margin-bottom:.5rem;">'
        f'<span class="m-tag">{_FA_UTENSILS} {_safe_html(r.cuisine)}</span>'
        f'<span class="m-tag m-{diff}">{diff.capitalize()}</span>'
        f'<span class="m-tag">{_FA_CLOCK} {total} min</span>'
        f'<span class="m-tag">{_FA_USERS} {r.servings} srv</span>'
        f'{course_tag}{tags}'
        f'</div>'
        f'<div style="font-size:.84rem;color:var(--t-muted);line-height:1.55;">{_safe_html(r.description[:180])}…</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card, unsafe_allow_html=True)
    with st.expander(f"Full Recipe — {r.name}"):
        ing_rows = "".join(
            f'<div class="cb-ing-row">'
            f'<span class="cb-ing-name">{_safe_html(ing)}</span>'
            f'<span class="cb-ing-qty">{_safe_html(qty)}</span>'
            f'</div>'
            for ing, qty in r.ingredient_quantities.items()
        )
        step_rows = "".join(
            f'<div class="cb-step">'
            f'<div class="cb-step-num">{i}</div>'
            f'<div class="cb-step-text">{_safe_html(step)}</div>'
            f'</div>'
            for i, step in enumerate(r.instructions, 1)
        )
        tip_block = ""
        if r.tips:
            tip_block = (
                f'<div class="cb-tip">'
                f'<div class="cb-tip-label">{_FA_BULB} Chef\'s Tip</div>'
                f'<div class="cb-tip-text">{_safe_html(r.tips)}</div>'
                f'</div>'
            )
        total_html = (
            f'<div class="cb-times">'
            f'<span class="cb-time-chip">{_FA_KNIFE} Prep: {r.prep_time_minutes} min</span>'
            f'<span class="cb-time-chip">{_FA_FIRE} Cook: {r.cook_time_minutes} min</span>'
            f'<span class="cb-time-chip">{_FA_HOURGLASS} Total: {total} min</span>'
            f'</div>'
        )
        st.markdown(
            f'<div class="cookbook-page">{total_html}'
            f'<div class="cb-section"><div class="cb-section-title">Ingredients'
            f'<span class="cb-serves">Serves {r.servings}</span></div>'
            f'<div class="cb-ingredients">{ing_rows}</div></div>'
            f'<div class="cb-section"><div class="cb-section-title">Method</div>'
            f'<div class="cb-steps">{step_rows}</div></div>'
            f'{tip_block}</div>',
            unsafe_allow_html=True,
        )


def render_find_tab():
    inputs = _sidebar_find()

    if inputs is None:
        t = THEMES[_active_theme()]
        st.markdown(f"""<div class="empty-s">
          <div class="ico">{t['emoji']}</div>
          <p><strong>Open the sidebar</strong> — enter your ingredients and let Rasaveda find your meal.</p>
          <p style="font-size:.85rem;font-style:italic;">{t['welcome_quote']}</p>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.info(f"**{get_recipe_count()} Recipes** across Indian & world cuisines")
        c2.info("**Vector Search** — semantic ingredient matching")
        c3.info("**AI Explanations** — grounded, personalized picks")
        return

    with st.spinner("Searching the world's pantry..."):
        try:
            req = RecommendationRequest(**inputs)
            retrieved = retrieve_recipes(req)
        except RuntimeError as e:
            st.error(str(e)); return

    if not retrieved:
        st.warning("No matches found — try relaxing dietary filters or expanding your ingredient list.")
        return

    n_recs = inputs.get("n_recommendations", 3)
    # Give the AI enough candidates without bloating the prompt
    gen_context = retrieved[:max(n_recs * 3, 6)]

    with st.spinner("Rasaveda is seeking wisdom..."):
        try:
            response = generate_recommendations(req, gen_context)
        except Exception as e:
            st.error(f"Generation error: {e}"); return

    n_found = len(response.recommendations)
    banner_html = (
        f'<div class="banner">'
        f'<strong>{_FA_CHART} {_safe_html(response.query_summary)}</strong>'
        f'<div class="ban-tip">{_FA_BULB} {_safe_html(response.general_tip)}</div>'
        f'<div class="ban-meta">{response.total_recipes_considered} recipes searched &middot; '
        f'{n_found} recommendation{"s" if n_found != 1 else ""} generated</div>'
        f'</div>'
    )
    st.markdown(banner_html, unsafe_allow_html=True)

    tabs = st.tabs([
        f"#{i+1}  {rec.recipe.name}"
        for i, rec in enumerate(response.recommendations)
    ])
    for i, (tab, rec) in enumerate(zip(tabs, response.recommendations)):
        with tab:
            _recipe_card(rec, i)

    # Browse-more: retrieved recipes the AI didn't feature
    ai_ids = {rec.recipe.id for rec in response.recommendations}
    remaining = [r for r in retrieved if r.recipe.id not in ai_ids]
    if remaining:
        st.markdown("---")
        with st.expander(f"Browse {len(remaining)} more matches — not featured by AI"):
            st.caption("These recipes matched your search but weren't selected as top picks. Full cookbook view available inside each card.")
            cols = st.columns(2)
            for idx, r in enumerate(remaining):
                with cols[idx % 2]:
                    _simple_recipe_card(r, idx + n_found + 1)


# ===========================================================================
# TAB 2 — ADD YOUR RECIPE
# ===========================================================================

def _init_form_state():
    defaults = {
        "form_ings":        [{"name": "", "qty": ""}],
        "form_steps":       [""],
        "add_success":      None,
        "cropped_img_bytes": None,  # final JPEG bytes after crop
        "upload_key":       0,      # bumped on reset to clear the uploader widget
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _image_uploader_section():
    """Image upload → crop → preview panel. Returns (bytes | None, suffix)."""
    from streamlit_cropper import st_cropper

    st.markdown("**Recipe Photo** *(optional)*")
    uploaded = st.file_uploader(
        "Upload a photo",
        type=["jpg", "jpeg", "png", "webp"],
        key=f"img_upload_{st.session_state.upload_key}",
        label_visibility="collapsed",
    )

    if uploaded is None:
        if st.session_state.cropped_img_bytes:
            st.image(st.session_state.cropped_img_bytes, caption="Current photo", use_container_width=True)
            if st.button("Remove photo", key="rm_photo"):
                st.session_state.cropped_img_bytes = None
                st.rerun()
        return st.session_state.cropped_img_bytes, ".jpg"

    pil_img = Image.open(uploaded).convert("RGB")
    suffix = "." + (uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else "jpg")
    if suffix == ".jpeg":
        suffix = ".jpg"

    st.caption("Drag the handles to crop, then click **Use this crop**.")
    cropped: Image.Image = st_cropper(
        pil_img,
        realtime_update=True,
        box_color="#FF9933",
        aspect_ratio=(4, 3),
    )

    # Live preview
    st.markdown("**Preview**")
    st.image(cropped, use_container_width=True)

    if st.button("Use this crop", type="primary", key="use_crop"):
        buf = io.BytesIO()
        cropped.save(buf, format="JPEG", quality=88)
        st.session_state.cropped_img_bytes = buf.getvalue()
        st.session_state.upload_key += 1
        st.rerun()

    return st.session_state.cropped_img_bytes, ".jpg"


def render_add_tab():
    _init_form_state()

    st.subheader("Add Your Own Recipe")
    st.markdown(
        "Your recipe is saved to your personal library and "
        "**immediately appears in recommendations** — searched alongside the built-in dataset."
    )
    st.markdown("---")

    if st.session_state.add_success:
        st.success(st.session_state.add_success)
        st.session_state.add_success = None

    # Layout: left = photo; right = metadata
    meta_col, photo_col = st.columns([3, 2])

    with photo_col:
        cropped_bytes, img_suffix = _image_uploader_section()

    with meta_col:
        col1, col2 = st.columns(2)
        with col1:
            name        = st.text_input("Recipe Name *", placeholder="e.g. Nani's Dal Tadka")
            cuisine     = st.selectbox("Cuisine *", ALL_CUISINES, index=0)
            region      = st.selectbox("Regional Style (optional)", ["—"] + INDIAN_REGIONS)
            description = st.text_area("Description *", placeholder="A short evocative description", height=90)
        with col2:
            difficulty  = st.selectbox("Difficulty *", ["easy", "medium", "hard"])
            prep_time   = st.number_input("Prep Time (minutes)", 0, 480, 15)
            cook_time   = st.number_input("Cook Time (minutes)", 0, 720, 30)
            servings    = st.number_input("Servings", 1, 50, 4)
            tips        = st.text_area("Chef's Tip (optional)", height=68)

    # Dietary + flavor
    st.markdown("---")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("**Dietary Tags**")
        dietary = st.multiselect("Dietary", ALL_DIETARY, key="add_dietary")
    with fc2:
        st.markdown("**Flavor Profile** *")
        flavors = st.multiselect("Flavors", ALL_FLAVORS, key="add_flavors")

    # Ingredients
    st.markdown("---")
    st.markdown("**Ingredients** — name + quantity for each")

    for i, row in enumerate(st.session_state.form_ings):
        cA, cB, cDel = st.columns([4, 3, 1])
        with cA:
            st.session_state.form_ings[i]["name"] = st.text_input(
                f"Ing {i+1}", value=row["name"], key=f"in_{i}",
                placeholder="e.g. basmati rice", label_visibility="collapsed",
            )
        with cB:
            st.session_state.form_ings[i]["qty"] = st.text_input(
                f"Qty {i+1}", value=row["qty"], key=f"iq_{i}",
                placeholder="e.g. 300g", label_visibility="collapsed",
            )
        with cDel:
            if len(st.session_state.form_ings) > 1 and st.button("✕", key=f"di_{i}"):
                st.session_state.form_ings.pop(i); st.rerun()

    if st.button("+ Add Ingredient"):
        st.session_state.form_ings.append({"name": "", "qty": ""}); st.rerun()

    # Instructions
    st.markdown("---")
    st.markdown("**Instructions** — one step per row")

    for i, step in enumerate(st.session_state.form_steps):
        cStep, cDel2 = st.columns([10, 1])
        with cStep:
            st.session_state.form_steps[i] = st.text_area(
                f"Step {i+1}", value=step, key=f"st_{i}", height=65,
                placeholder=f"Step {i+1}: ...", label_visibility="collapsed",
            )
        with cDel2:
            if len(st.session_state.form_steps) > 1 and st.button("✕", key=f"ds_{i}"):
                st.session_state.form_steps.pop(i); st.rerun()

    if st.button("+ Add Step"):
        st.session_state.form_steps.append(""); st.rerun()

    # Submit
    st.markdown("---")
    if st.button("Save Recipe", type="primary", use_container_width=True):
        errors = []
        if not name.strip():          errors.append("Recipe Name is required.")
        if not description.strip():   errors.append("Description is required.")
        if not flavors:               errors.append("Select at least one Flavor Profile.")
        ings_clean  = [r for r in st.session_state.form_ings  if r["name"].strip()]
        steps_clean = [s.strip() for s in st.session_state.form_steps if s.strip()]
        if not ings_clean:            errors.append("Add at least one ingredient.")
        if not steps_clean:           errors.append("Add at least one instruction step.")

        for e in errors:
            st.error(e)

        if not errors:
            display_name = f"{name.strip()} ({region})" if region != "—" else name.strip()
            recipe_id = generate_recipe_id()
            img_path = None
            if cropped_bytes:
                img_path = save_user_image(recipe_id, cropped_bytes, img_suffix)
            recipe = Recipe(
                id=recipe_id,
                name=display_name,
                description=description.strip(),
                cuisine=cuisine,
                dietary_tags=dietary,
                difficulty=Difficulty(difficulty),
                prep_time_minutes=int(prep_time),
                cook_time_minutes=int(cook_time),
                servings=int(servings),
                ingredients=[r["name"].strip() for r in ings_clean],
                ingredient_quantities={r["name"].strip(): r["qty"].strip() for r in ings_clean},
                instructions=steps_clean,
                flavor_profile=flavors,
                tips=tips.strip() or None,
                image_path=img_path,
            )
            with st.spinner("Saving and embedding your recipe..."):
                save_user_recipe(recipe)
            st.session_state.form_ings        = [{"name": "", "qty": ""}]
            st.session_state.form_steps       = [""]
            st.session_state.cropped_img_bytes = None
            st.session_state.upload_key       += 1
            st.session_state.add_success      = f"'{recipe.name}' saved and added to recommendations!"
            st.rerun()


# ===========================================================================
# TAB 3 — IMPROVE A RECIPE  (AI analysis + Admin editor)
# ===========================================================================

def _init_edit_state(recipe):
    """Seed edit session state from a recipe — resets when recipe changes."""
    if st.session_state.get("edit_recipe_id") == recipe.id:
        return  # already seeded for this recipe
    st.session_state["edit_recipe_id"]      = recipe.id
    st.session_state["edit_ings"]           = [
        {"name": k, "qty": v} for k, v in recipe.ingredient_quantities.items()
    ] or [{"name": "", "qty": ""}]
    st.session_state["edit_steps"]          = list(recipe.instructions) or [""]
    st.session_state["edit_cropped_bytes"]  = None
    st.session_state["edit_upload_key"]     = 0
    st.session_state["edit_save_msg"]       = None


def _edit_image_section(recipe):
    """Image upload + crop for the editor; pre-shows existing image."""
    from streamlit_cropper import st_cropper

    st.markdown("**Recipe Photo**")
    existing_url = _fetch_image(recipe.name, recipe.cuisine, image_path=getattr(recipe, "image_path", None))
    if existing_url and not st.session_state.edit_cropped_bytes:
        st.image(existing_url, caption="Current image", use_container_width=True)

    uploaded = st.file_uploader(
        "Replace photo",
        type=["jpg", "jpeg", "png", "webp"],
        key=f"edit_img_{st.session_state.edit_upload_key}",
        label_visibility="collapsed",
    )
    if uploaded:
        pil_img = Image.open(uploaded).convert("RGB")
        st.caption("Drag handles to crop, then **Use this crop**.")
        cropped = st_cropper(pil_img, realtime_update=True, box_color="#FF9933", aspect_ratio=(4, 3))
        st.markdown("**Preview**")
        st.image(cropped, use_container_width=True)
        if st.button("Use this crop", key="edit_use_crop"):
            buf = io.BytesIO()
            cropped.save(buf, format="JPEG", quality=88)
            st.session_state.edit_cropped_bytes = buf.getvalue()
            st.session_state.edit_upload_key += 1
            st.rerun()
    elif st.session_state.edit_cropped_bytes:
        st.image(st.session_state.edit_cropped_bytes, caption="New photo (unsaved)", use_container_width=True)
        if st.button("Remove new photo", key="edit_rm_photo"):
            st.session_state.edit_cropped_bytes = None
            st.rerun()


def _render_ai_analysis(chosen):
    """AI step-by-step analysis — the original Improve functionality."""
    thumb = get_dish_gradient(chosen.cuisine, chosen.name)
    st.markdown(f"""
<div style="background:{thumb};border-radius:10px;padding:1px;margin-bottom:.8rem;">
  <div style="background:var(--t-card);border-radius:9px;padding:.8rem 1rem;">
    <strong style="color:var(--t-heading);font-size:1.1rem;">{chosen.name}</strong>
    <span style="color:var(--t-muted);font-size:.85rem;margin-left:.5rem;">
      {_FA_UTENSILS} {chosen.cuisine} &nbsp;·&nbsp;
      {chosen.difficulty.value.capitalize()} &nbsp;·&nbsp;
      {_FA_CLOCK} {chosen.prep_time_minutes + chosen.cook_time_minutes} min
    </span>
  </div>
</div>""", unsafe_allow_html=True)

    with st.expander("Current Steps", expanded=True):
        for i, step in enumerate(chosen.instructions, 1):
            st.markdown(f"**{i}.** {step}")

    analyze = st.button("Analyze with AI", type="primary")
    if not analyze:
        return

    with st.spinner(f"Rasaveda is studying '{chosen.name}'... (20-40 seconds)"):
        try:
            result: RecipeImprovement = suggest_improvements(chosen)
        except Exception as e:
            st.error(f"Could not analyze recipe: {e}"); return

    st.markdown("---")
    st.markdown(f"""<div class="banner">
      <strong>{_FA_CHART} Overall Assessment</strong>
      <div class="ban-tip">{_safe_html(result.overall_assessment)}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Step-by-Step Analysis")
    improved_count = sum(1 for s in result.improvements if s.has_improvement)
    st.caption(f"{improved_count} of {len(result.improvements)} steps have suggested improvements")

    for imp in result.improvements:
        if imp.has_improvement:
            st.markdown(f"""<div class="step-imp">
              <div class="step-orig">{_FA_DOT} Original: {_safe_html(imp.original)}</div>
              <div class="step-new">{_FA_TREND} Improved: {_safe_html(imp.improved)}</div>
              <div class="step-why">{_FA_BULB} {_safe_html(imp.reasoning)}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="step-ok">
              <div class="step-new">{_FA_CIRCLEOK} Step {imp.step_number}: {_safe_html(imp.original)}</div>
              <div class="step-why">{_FA_CHECK} {_safe_html(imp.reasoning)}</div>
            </div>""", unsafe_allow_html=True)

    if result.general_tips:
        st.markdown("### Tips for this Recipe")
        tips_html = "".join(f'<span class="tip-chip">{_FA_BULB} {_safe_html(tip)}</span>' for tip in result.general_tips)
        st.markdown(tips_html, unsafe_allow_html=True)

    if improved_count > 0:
        st.markdown("---")
        if st.button("Save improved version", type="secondary"):
            improved_steps = [
                imp.improved if imp.has_improvement else imp.original
                for imp in result.improvements
            ]
            save_user_recipe(chosen.model_copy(update={"instructions": improved_steps}))
            st.success(f"'{chosen.name}' updated with improved steps!")


def _render_edit_form(chosen):
    """Full admin editor for any recipe field."""
    _init_edit_state(chosen)

    if st.session_state.edit_save_msg:
        st.success(st.session_state.edit_save_msg)
        st.session_state.edit_save_msg = None

    is_base = not chosen.id.startswith("usr-")
    if is_base:
        st.info(
            "This is a **built-in recipe**. Saving creates an editable personal copy "
            "that overrides the original in all searches and recommendations.",
            icon="ℹ️",
        )

    # ── Metadata ─────────────────────────────────────────────────────────────
    meta_col, photo_col = st.columns([3, 2])

    with photo_col:
        _edit_image_section(chosen)

    with meta_col:
        c1, c2 = st.columns(2)
        with c1:
            ed_name    = st.text_input("Recipe Name *", value=chosen.name, key="ed_name")
            ed_cuisine = st.selectbox("Cuisine *", ALL_CUISINES,
                                      index=ALL_CUISINES.index(chosen.cuisine) if chosen.cuisine in ALL_CUISINES else 0,
                                      key="ed_cuisine")
            ed_course  = st.selectbox("Course", ["—"] + ALL_COURSES,
                                      index=(ALL_COURSES.index(chosen.course) + 1) if chosen.course in ALL_COURSES else 0,
                                      key="ed_course")
            ed_desc    = st.text_area("Description *", value=chosen.description, height=90, key="ed_desc")
        with c2:
            ed_diff    = st.selectbox("Difficulty *", ["easy", "medium", "hard"],
                                      index=["easy", "medium", "hard"].index(chosen.difficulty.value),
                                      key="ed_diff")
            ed_prep    = st.number_input("Prep Time (min)", 0, 480, chosen.prep_time_minutes, key="ed_prep")
            ed_cook    = st.number_input("Cook Time (min)", 0, 720, chosen.cook_time_minutes, key="ed_cook")
            ed_serve   = st.number_input("Servings", 1, 50, chosen.servings, key="ed_serve")
            ed_tips    = st.text_area("Chef's Tip", value=chosen.tips or "", height=68, key="ed_tips")

    # ── Dietary + flavor ─────────────────────────────────────────────────────
    st.markdown("---")
    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown("**Dietary Tags**")
        ed_dietary = st.multiselect("Dietary", ALL_DIETARY,
                                    default=[t for t in chosen.dietary_tags if t in ALL_DIETARY],
                                    key="ed_dietary")
    with dc2:
        st.markdown("**Flavor Profile** *")
        ed_flavors = st.multiselect("Flavors", ALL_FLAVORS,
                                    default=[f for f in chosen.flavor_profile if f in ALL_FLAVORS],
                                    key="ed_flavors")

    # ── Ingredients ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Ingredients**")
    for i, row in enumerate(st.session_state.edit_ings):
        cA, cB, cDel = st.columns([4, 3, 1])
        with cA:
            st.session_state.edit_ings[i]["name"] = st.text_input(
                f"EI {i+1}", value=row["name"], key=f"ein_{i}",
                placeholder="ingredient name", label_visibility="collapsed",
            )
        with cB:
            st.session_state.edit_ings[i]["qty"] = st.text_input(
                f"EQ {i+1}", value=row["qty"], key=f"eiq_{i}",
                placeholder="quantity", label_visibility="collapsed",
            )
        with cDel:
            if len(st.session_state.edit_ings) > 1 and st.button("✕", key=f"edi_{i}"):
                st.session_state.edit_ings.pop(i); st.rerun()
    if st.button("+ Add Ingredient", key="edit_add_ing"):
        st.session_state.edit_ings.append({"name": "", "qty": ""}); st.rerun()

    # ── Instructions ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Instructions**")
    for i, step in enumerate(st.session_state.edit_steps):
        cS, cD = st.columns([10, 1])
        with cS:
            st.session_state.edit_steps[i] = st.text_area(
                f"ES {i+1}", value=step, key=f"est_{i}", height=65,
                placeholder=f"Step {i+1}", label_visibility="collapsed",
            )
        with cD:
            if len(st.session_state.edit_steps) > 1 and st.button("✕", key=f"eds_{i}"):
                st.session_state.edit_steps.pop(i); st.rerun()
    if st.button("+ Add Step", key="edit_add_step"):
        st.session_state.edit_steps.append(""); st.rerun()

    # ── Save ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    if st.button("Save Changes", type="primary", use_container_width=True, key="edit_save"):
        errors = []
        if not ed_name.strip():    errors.append("Recipe Name is required.")
        if not ed_desc.strip():    errors.append("Description is required.")
        if not ed_flavors:         errors.append("Select at least one Flavor Profile.")
        ings_clean  = [r for r in st.session_state.edit_ings  if r["name"].strip()]
        steps_clean = [s.strip() for s in st.session_state.edit_steps if s.strip()]
        if not ings_clean:         errors.append("Add at least one ingredient.")
        if not steps_clean:        errors.append("Add at least one instruction step.")
        for e in errors:
            st.error(e)

        if not errors:
            # Resolve image: new upload > existing path > None
            img_path = getattr(chosen, "image_path", None)
            if st.session_state.edit_cropped_bytes:
                img_path = save_user_image(chosen.id, st.session_state.edit_cropped_bytes, ".jpg")

            course_val = ed_course if ed_course != "—" else None
            updated = Recipe(
                id=chosen.id,
                name=ed_name.strip(),
                description=ed_desc.strip(),
                cuisine=ed_cuisine,
                dietary_tags=ed_dietary,
                difficulty=Difficulty(ed_diff),
                prep_time_minutes=int(ed_prep),
                cook_time_minutes=int(ed_cook),
                servings=int(ed_serve),
                ingredients=[r["name"].strip() for r in ings_clean],
                ingredient_quantities={r["name"].strip(): r["qty"].strip() for r in ings_clean},
                instructions=steps_clean,
                flavor_profile=ed_flavors,
                tips=ed_tips.strip() or None,
                course=course_val,
                image_path=img_path,
            )
            with st.spinner("Saving changes..."):
                save_user_recipe(updated)
            # Reset edit state to reflect saved values
            st.session_state.edit_recipe_id     = None  # forces re-seed on next render
            st.session_state.edit_cropped_bytes = None
            st.session_state.edit_save_msg = f"'{updated.name}' saved successfully."
            st.rerun()


def render_improve_tab():
    st.subheader("Improve · Edit")
    st.markdown("---")

    all_recipes = cached_base_recipes() + load_user_recipes()
    recipe_map  = {r.name: r for r in all_recipes}

    if not recipe_map:
        st.info("No recipes available yet."); return

    chosen_name = st.selectbox("Choose a recipe", sorted(recipe_map.keys()), key="improve_select")
    chosen = recipe_map[chosen_name]

    ai_tab, edit_tab = st.tabs(["AI Analysis", "Edit Recipe"])

    with ai_tab:
        _render_ai_analysis(chosen)

    with edit_tab:
        _render_edit_form(chosen)


# ===========================================================================
# TAB 4 — MY LIBRARY
# ===========================================================================

def render_library_tab():
    st.subheader("My Recipe Library")
    st.markdown("All recipes you have added — searchable in recommendations alongside the built-in dataset.")
    st.markdown("---")

    user_recipes = load_user_recipes()

    if not user_recipes:
        st.markdown("""<div class="empty-s">
          <div class="ico"><i class="fa-solid fa-book-open fa-4x"></i></div>
          <p>Your library is empty. Head to <strong>Add Your Recipe</strong> to begin.</p>
        </div>""", unsafe_allow_html=True)
        return

    st.caption(f"{len(user_recipes)} personal recipe{'s' if len(user_recipes) != 1 else ''}")

    for recipe in user_recipes:
        total  = recipe.prep_time_minutes + recipe.cook_time_minutes
        thumb  = get_dish_gradient(recipe.cuisine, recipe.name)
        dtags  = " · ".join(recipe.dietary_tags) if recipe.dietary_tags else "No restrictions"

        with st.expander(f"{recipe.name}  —  {recipe.difficulty.value.capitalize()} · {total} min"):
            st.markdown(
                f'<div class="lib-thumb" style="background:{thumb};margin-bottom:.8rem;"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"*{recipe.description}*")
            st.caption(
                f"**Cuisine:** {recipe.cuisine} &nbsp;|&nbsp; "
                f"**Flavors:** {', '.join(recipe.flavor_profile)} &nbsp;|&nbsp; "
                f"**Dietary:** {dtags}"
            )

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Ingredients**")
                for ing, qty in recipe.ingredient_quantities.items():
                    st.markdown(f"- **{ing}**: {qty}")
            with c2:
                st.markdown("**Instructions**")
                for i, step in enumerate(recipe.instructions, 1):
                    st.markdown(f"{i}. {step}")

            if recipe.tips:
                st.info(recipe.tips)

            if st.button(f"Delete '{recipe.name}'", key=f"del_{recipe.id}"):
                if delete_user_recipe(recipe.id):
                    st.success(f"Removed '{recipe.name}' from your library.")
                    st.rerun()


# ===========================================================================
# TAB 5 — BROWSE ALL RECIPES
# ===========================================================================

_BROWSE_COURSES = [
    "All", "Main Course", "Appetizer", "Soup", "Dessert",
    "Bread", "Side Dish", "Breakfast", "Beverage", "Basics", "Condiment",
]

_DIFF_COLORS = {"easy": "#d4edda", "medium": "#fff3cd", "hard": "#f8d7da"}
_DIFF_TEXT   = {"easy": "#155724", "medium": "#856404", "hard": "#721c24"}


def _browse_recipe_card(recipe, idx: int):
    """Compact browse card — image (if available), metadata, expandable full view."""
    total  = recipe.prep_time_minutes + recipe.cook_time_minutes
    diff   = recipe.difficulty.value
    thumb  = get_dish_gradient(recipe.cuisine, recipe.name)
    img_url = _fetch_image(recipe.name, recipe.cuisine, image_path=getattr(recipe, "image_path", None))
    thumb_html = _make_thumb_html(img_url, thumb, recipe.name)

    dtags  = " · ".join(recipe.dietary_tags[:2]) if recipe.dietary_tags else ""
    course = recipe.course or "Main Course"
    dc = _DIFF_COLORS.get(diff, "#eee")
    dt = _DIFF_TEXT.get(diff, "#333")
    flavors_str = ", ".join(recipe.flavor_profile[:3]) if recipe.flavor_profile else ""

    card_html = (
        f'<div class="rec-card" style="margin-bottom:1rem;">'
        f'{thumb_html}'
        f'<div class="rec-body" style="padding:.9rem 1.1rem 1rem;">'
        f'<div class="rec-name" style="font-size:1.05rem;margin-bottom:.4rem;">{_safe_html(recipe.name)}</div>'
        f'<div class="meta-row" style="margin-bottom:.5rem;">'
        f'<span class="m-tag">{_FA_UTENSILS} {_safe_html(recipe.cuisine)}</span>'
        f'<span class="m-tag" style="background:{dc};color:{dt};">{diff.capitalize()}</span>'
        f'<span class="m-tag">{_FA_CLOCK} {total} min</span>'
        f'<span class="m-tag">{_FA_USERS} {recipe.servings} srv</span>'
        + (f'<span class="m-tag" style="font-style:italic;">{_safe_html(course)}</span>' if course else '')
        + (f'<span class="m-tag" style="font-size:.72rem;color:var(--t-muted);">{_safe_html(dtags)}</span>' if dtags else '')
        + f'</div>'
        f'<div style="font-size:.82rem;color:var(--t-muted);line-height:1.5;margin-bottom:.3rem;">'
        f'{_safe_html(recipe.description[:160])}{"…" if len(recipe.description) > 160 else ""}'
        f'</div>'
        + (f'<div style="font-size:.75rem;color:var(--t-muted);font-style:italic;">{_FA_FIRE} {_safe_html(flavors_str)}</div>' if flavors_str else '')
        + f'</div></div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    with st.expander(f"Full Recipe — {recipe.name}"):
        ing_rows = "".join(
            f'<div class="cb-ing-row">'
            f'<span class="cb-ing-name">{_safe_html(ing)}</span>'
            f'<span class="cb-ing-qty">{_safe_html(qty)}</span>'
            f'</div>'
            for ing, qty in recipe.ingredient_quantities.items()
        )
        step_rows = "".join(
            f'<div class="cb-step">'
            f'<div class="cb-step-num">{i}</div>'
            f'<div class="cb-step-text">{_safe_html(step)}</div>'
            f'</div>'
            for i, step in enumerate(recipe.instructions, 1)
        )
        tip_block = ""
        if recipe.tips:
            tip_block = (
                f'<div class="cb-tip"><div class="cb-tip-label">{_FA_BULB} Chef\'s Tip</div>'
                f'<div class="cb-tip-text">{_safe_html(recipe.tips)}</div></div>'
            )
        time_chips = (
            f'<div class="cb-times">'
            f'<span class="cb-time-chip">{_FA_KNIFE} Prep: {recipe.prep_time_minutes} min</span>'
            f'<span class="cb-time-chip">{_FA_FIRE} Cook: {recipe.cook_time_minutes} min</span>'
            f'<span class="cb-time-chip">{_FA_HOURGLASS} Total: {total} min</span>'
            f'</div>'
        )
        st.markdown(
            f'<div class="cookbook-page">{time_chips}'
            f'<div class="cb-section"><div class="cb-section-title">Ingredients'
            f'<span class="cb-serves">Serves {recipe.servings}</span></div>'
            f'<div class="cb-ingredients">{ing_rows}</div></div>'
            f'<div class="cb-section"><div class="cb-section-title">Method</div>'
            f'<div class="cb-steps">{step_rows}</div></div>'
            f'{tip_block}</div>',
            unsafe_allow_html=True,
        )


def render_browse_tab():
    st.subheader("Browse All Recipes")
    st.markdown("Explore the full library by category, cuisine, or search — click any card to see the full recipe.")
    st.markdown("---")

    all_recipes = cached_base_recipes() + load_user_recipes()
    if not all_recipes:
        st.info("No recipes loaded yet."); return

    # ── Filter bar ────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    with fc1:
        course_filter = st.selectbox(
            "Category", _BROWSE_COURSES, index=0, key="browse_course",
            label_visibility="visible",
        )
    with fc2:
        cuisine_opts = ["All cuisines"] + sorted({r.cuisine for r in all_recipes})
        cuisine_filter = st.selectbox(
            "Cuisine", cuisine_opts, index=0, key="browse_cuisine",
        )
    with fc3:
        search_q = st.text_input(
            "Search", placeholder="e.g. butter chicken, lentil, quick…",
            key="browse_search",
        )

    diff_filter = st.radio(
        "Difficulty", ["Any", "easy", "medium", "hard"],
        horizontal=True, key="browse_diff", label_visibility="visible",
    )

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = all_recipes
    if course_filter != "All":
        filtered = [r for r in filtered if (r.course or "Main Course") == course_filter]
    if cuisine_filter != "All cuisines":
        filtered = [r for r in filtered if r.cuisine == cuisine_filter]
    if diff_filter != "Any":
        filtered = [r for r in filtered if r.difficulty.value == diff_filter]
    if search_q.strip():
        q = search_q.strip().lower()
        filtered = [
            r for r in filtered
            if q in r.name.lower()
            or q in r.description.lower()
            or any(q in ing.lower() for ing in r.ingredients)
            or q in r.cuisine.lower()
        ]

    # ── Course summary chips ──────────────────────────────────────────────────
    from collections import Counter
    course_counts = Counter((r.course or "Main Course") for r in filtered)
    chips = "".join(
        f'<span class="m-tag" style="font-size:.78rem;">'
        f'{c} <strong>({n})</strong></span>'
        for c, n in sorted(course_counts.items())
    )
    st.markdown(
        f'<div class="meta-row" style="margin-bottom:.8rem;">{chips}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"{len(filtered)} recipe{'s' if len(filtered) != 1 else ''} shown")

    if not filtered:
        st.warning("No recipes match your filters — try broadening the search.")
        return

    # ── Grid: 3 columns ───────────────────────────────────────────────────────
    cols = st.columns(3)
    for idx, recipe in enumerate(filtered):
        with cols[idx % 3]:
            _browse_recipe_card(recipe, idx)


# ===========================================================================
# TAB 6 — CHAT WITH RASAVEDA
# ===========================================================================

_CHAT_SUGGESTIONS = [
    "What can I make with leftover dal?",
    "How do I make biryani less spicy?",
    "Tell me about Kerala cuisine",
    "What spices define North Indian cooking?",
    "How do I get crispy dosa?",
    "Substitute for tamarind?",
]


def render_chat_tab():
    t = THEMES[_active_theme()]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history()

    # Welcome banner (shown when history is empty)
    if not st.session_state.chat_history:
        suggestions_html = "".join(
            f'<span class="chat-suggestion">{s}</span>' for s in _CHAT_SUGGESTIONS
        )
        st.markdown(f"""<div class="chat-welcome">
          <h3>{t['emoji']} Chat with Rasaveda</h3>
          <p style="color:var(--t-muted);font-size:.9rem;margin-bottom:.7rem;">
            Ask me anything about Indian cuisine, ingredients, techniques, or substitutions.
            I search our recipe database to ground my answers.
          </p>
          {suggestions_html}
        </div>""", unsafe_allow_html=True)

    # Render chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if user_msg := st.chat_input("Ask Rasaveda anything about food..."):
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_msg)
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        # Generate response with RAG context
        with st.chat_message("assistant"):
            with st.spinner("Rasaveda is reflecting..."):
                context = search_by_text(user_msg, n=3)
                reply = chat_response(
                    user_msg,
                    st.session_state.chat_history[:-1],
                    context,
                )
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        save_chat_history(st.session_state.chat_history)

    # Clear button (only when there's history)
    if st.session_state.chat_history:
        st.markdown("---")
        col_clr, col_info = st.columns([2, 5])
        with col_clr:
            if st.button("Clear conversation", use_container_width=True):
                clear_chat_history()
                st.session_state.chat_history = []
                st.rerun()
        with col_info:
            st.caption(f"{len(st.session_state.chat_history) // 2} exchange{'s' if len(st.session_state.chat_history) // 2 != 1 else ''} saved · history persists across sessions")


# ===========================================================================
# Main
# ===========================================================================

def main():
    startup()

    # Font Awesome 6 Free — required for FA icons in unsafe_allow_html blocks
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">',
        unsafe_allow_html=True,
    )

    # 1. Theme selector (renders top of sidebar + sets session state)
    _theme_selector()

    # 2. Inject theme CSS variables + override global Streamlit styles
    active = _active_theme()
    st.markdown(build_theme_css(active), unsafe_allow_html=True)

    # 3. Base component CSS (uses variables from step 2)
    st.markdown(BASE_CSS, unsafe_allow_html=True)

    # 4. Header
    _header()

    # 5. Main tabs
    tab_find, tab_add, tab_improve, tab_browse, tab_library, tab_chat = st.tabs([
        "Find a Recipe",
        "Add Your Recipe",
        "Improve",
        "Browse",
        "My Library",
        "Chat",
    ])

    with tab_find:
        render_find_tab()
    with tab_add:
        render_add_tab()
    with tab_improve:
        render_improve_tab()
    with tab_browse:
        render_browse_tab()
    with tab_library:
        render_library_tab()
    with tab_chat:
        render_chat_tab()


if __name__ == "__main__":
    main()
