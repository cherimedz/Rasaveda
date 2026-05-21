"""Quick test — check Wikipedia image coverage for a sample of recipes."""
import time
import requests

HEADERS = {"User-Agent": "Rasaveda-RecipeApp/1.0 (educational)"}

SAMPLES = [
    "Homemade Ghee", "Homemade Paneer", "Dal Makhani", "Rajma",
    "Butter Chicken", "Hyderabadi Dum Biryani", "Masala Dosa",
    "Kashmiri Rogan Josh", "Aloo Paratha", "Gulab Jamun",
    "Kheer", "Sambar", "Kerala Fish Curry", "Seekh Kebab",
    "Chicken Stock", "Basic Roti", "Garam Masala", "Mint Chutney",
    "Tadka", "Pho Bo", "Kimchi Jjigae", "Moroccan Chicken Tagine",
    "Beef Rendang", "Doro Wat", "Mango Lassi", "Medu Vada",
    "Shoyu Ramen", "Pozole Rojo", "Spanakopita", "Japchae",
]


def wiki_search(term):
    try:
        s = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "opensearch", "search": term, "limit": 1, "format": "json"},
            timeout=4, headers=HEADERS,
        )
        titles = s.json()[1]
        if not titles:
            return None, ""
        title = titles[0]
        p = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "titles": title, "prop": "pageimages",
                    "pithumbsize": 640, "format": "json", "redirects": 1},
            timeout=4, headers=HEADERS,
        )
        for pid, page in p.json().get("query", {}).get("pages", {}).items():
            if pid != "-1":
                img = page.get("thumbnail", {}).get("source")
                return (img, page.get("title", title)) if img else (None, title)
    except Exception as e:
        print(f"  ERROR: {e}")
    return None, ""


def words(s, min_len=4):
    return {w.lower() for w in s.split() if len(w) >= min_len}


def related(query, wiki_title):
    q, w = words(query), words(wiki_title)
    if not q or not w:
        return False
    return w.issubset(q) or len(q & w) / len(q | w) >= 0.25


hits, misses = 0, 0
for name in SAMPLES:
    img, title = wiki_search(name)
    time.sleep(0.2)
    if img and related(name, title):
        hits += 1
        print(f"  OK  {name!r:40s} -> {title!r}")
    else:
        misses += 1
        status = f"title={title!r}" if title else "no result"
        print(f"  --  {name!r:40s} ({status})")

print(f"\nHits: {hits}/{len(SAMPLES)}  ({hits/len(SAMPLES)*100:.0f}%)")
