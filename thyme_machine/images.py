"""
Recipe image fetching — TheMealDB first, Wikipedia fallback.

Priority: TheMealDB (Jaccard >= 0.5) → Wikipedia (related check) → None (CSS gradient).

The Wikipedia query strips parenthetical subtitles and "with ..." suffixes from recipe
names so "Kimchi Jjigae (Kimchi Stew)" searches just "Kimchi Jjigae", and "Miso Soup
with Tofu and Wakame" searches just "Miso Soup".

Results cached to data/image_cache.json so Wikipedia is only fetched once per recipe
across Streamlit restarts.
"""

import json
import re
import time
from pathlib import Path

import requests

_CACHE_PATH = Path("./data/image_cache.json")
_mem_cache: dict[str, str | None] = {}

_MEALDB_THRESHOLD = 0.5
_WIKI_THRESHOLD = 0.35
_WIKI_HEADERS = {"User-Agent": "Rasaveda-RecipeApp/1.0 (educational)"}

_STRIP_PREFIXES = (
    "homemade ", "basic ", "classic ", "easy ", "simple ",
    "traditional ", "authentic ",
)


def _load_disk_cache() -> None:
    if _CACHE_PATH.exists():
        try:
            _mem_cache.update(json.loads(_CACHE_PATH.read_text(encoding="utf-8")))
        except Exception:
            pass


def _flush_disk_cache() -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(
            json.dumps(_mem_cache, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception:
        pass


_load_disk_cache()


def _clean_search_term(name: str) -> str:
    """Simplify a recipe name for Wikipedia search.

    Removes parenthetical subtitles and 'with ...' suffixes that confuse opensearch,
    then strips leading generic adjectives.
    """
    s = re.sub(r"\s*\(.*?\)\s*$", "", name).strip()
    s = re.sub(r"\s+with\b.*$", "", s, flags=re.IGNORECASE).strip()
    lower = s.lower()
    for prefix in _STRIP_PREFIXES:
        if lower.startswith(prefix):
            s = s[len(prefix):]
            break
    return s


def _query_mealdb(term: str) -> tuple[str | None, str]:
    """Returns (image_url, matched_meal_name) or (None, '')."""
    try:
        resp = requests.get(
            "https://www.themealdb.com/api/json/v1/1/search.php",
            params={"s": term},
            timeout=4,
        )
        meals = resp.json().get("meals")
        if meals:
            return meals[0]["strMealThumb"], meals[0]["strMeal"]
    except Exception:
        pass
    return None, ""


_REGIONAL_PREFIXES = re.compile(
    r"^\s*(north|south|east|west|central|indo|punjabi|bengali|keralan|gujarati|"
    r"rajasthani|mughlai|hyderabadi|goan|chettinad|maharashtrian|kashmiri)\s+",
    re.IGNORECASE,
)


def _alt_search_terms(name: str, cuisine: str) -> list[str]:
    """Generate fallback search terms when the exact recipe name fails."""
    terms = []
    cleaned = _REGIONAL_PREFIXES.sub("", _clean_search_term(name)).strip()
    if cleaned and cleaned.lower() != name.lower():
        terms.append(cleaned)
    # First substantial word alone (e.g. "Rogan Josh" → "Rogan Josh" is already clean,
    # but "Murgh Malai Kebab" → "Kebab" is a useful fallback)
    words = [w for w in cleaned.split() if len(w) >= 4]
    if len(words) >= 2:
        terms.append(words[-1])  # last main word (often the dish type)
    if cuisine:
        terms.append(f"{cleaned} {cuisine}")
    return [t for t in terms if t.strip()]


def _wiki_fetch_image_for_title(title: str) -> str | None:
    """Fetch the thumbnail URL for a known Wikipedia article title."""
    try:
        p = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": title,
                "prop": "pageimages",
                "pithumbsize": 640,
                "format": "json",
                "redirects": 1,
            },
            timeout=6,
            headers=_WIKI_HEADERS,
        )
        for pid, page in p.json().get("query", {}).get("pages", {}).items():
            if pid != "-1":
                return page.get("thumbnail", {}).get("source")
    except Exception:
        pass
    return None


def _query_wikipedia(name: str) -> tuple[str | None, str]:
    """Two-step Wikipedia lookup: opensearch (top 3) → pageimages.

    Checks up to 3 candidate titles so niche dish names that aren't the
    top opensearch hit still get matched.
    Returns (thumbnail_url, article_title) or (None, '').
    """
    search_term = _clean_search_term(name)

    for attempt in range(2):
        try:
            s = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "opensearch",
                    "search": search_term,
                    "limit": 3,
                    "format": "json",
                    "redirects": "resolve",
                },
                timeout=6,
                headers=_WIKI_HEADERS,
            )
            data = s.json()
            titles = data[1] if len(data) > 1 else []
            if not titles:
                return None, ""

            time.sleep(0.4)

            for title in titles:
                if not _wiki_related(name, title):
                    continue
                img = _wiki_fetch_image_for_title(title)
                if img:
                    return img, title

            return None, titles[0] if titles else ""

        except Exception:
            if attempt == 0:
                time.sleep(1.5)

    return None, ""


def _jaccard(a: str, b: str, min_len: int = 3) -> float:
    a_words = {w.lower() for w in a.split() if len(w) >= min_len}
    b_words = {w.lower() for w in b.split() if len(w) >= min_len}
    if not a_words or not b_words:
        return 0.0
    return len(a_words & b_words) / len(a_words | b_words)


def _tokenize(s: str, min_len: int = 3) -> set[str]:
    """Split on spaces and hyphens, return lowercased tokens of length >= min_len."""
    tokens = set()
    for part in re.split(r"[\s\-]+", s):
        t = part.lower()
        if len(t) >= min_len:
            tokens.add(t)
    return tokens


def _wiki_related(query: str, wiki_title: str) -> bool:
    """True if the Wikipedia article is plausibly about this recipe.

    Cleans both the query (strip parenthetical/suffix) and the wiki title before
    tokenizing on spaces and hyphens. Accepts when title tokens ⊆ query tokens,
    or Jaccard >= threshold for multi-word matches.
    """
    clean_q = _clean_search_term(query)
    clean_t = re.sub(r"\s*\(.*?\)", "", wiki_title).strip()
    q = _tokenize(clean_q)
    w = _tokenize(clean_t)
    if not w or not q:
        return False
    if w.issubset(q):
        return True
    intersection = q & w
    union = q | w
    return len(q) >= 2 and len(w) >= 2 and len(intersection) / len(union) >= _WIKI_THRESHOLD


def get_recipe_image(name: str, cuisine: str = "") -> str | None:
    """Return an image URL for a recipe, or None to fall back to the CSS gradient.

    Priority:
      1. In-memory / disk cache
      2. TheMealDB  (exact Jaccard match)
      3. Wikipedia  (top-3 candidate titles, relevance-checked)
      4. Wikipedia retry with alternative/simplified search terms
    None is stored in-memory only so transient API failures don't persist.
    """
    key = name.lower().strip()
    if key in _mem_cache:
        return _mem_cache[key]

    # 1. TheMealDB
    img, matched = _query_mealdb(name)
    if img and _jaccard(name, matched) >= _MEALDB_THRESHOLD:
        _mem_cache[key] = img
        _flush_disk_cache()
        return img

    # 2. Wikipedia — exact name, checks top-3 results
    time.sleep(0.35)
    wiki_img, wiki_title = _query_wikipedia(name)
    if wiki_img:
        _mem_cache[key] = wiki_img
        _flush_disk_cache()
        return wiki_img

    # 3. Wikipedia retry with alternative search terms (strip regional prefixes, etc.)
    for alt_term in _alt_search_terms(name, cuisine):
        time.sleep(0.35)
        wiki_img, wiki_title = _query_wikipedia(alt_term)
        if wiki_img and _wiki_related(name, wiki_title):
            _mem_cache[key] = wiki_img
            _flush_disk_cache()
            return wiki_img

    _mem_cache[key] = None
    return None
