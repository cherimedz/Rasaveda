"""
Visual themes for Rasaveda — 5 Indian regional aesthetic systems.
Each theme defines CSS custom properties, background patterns, and decorative text.
"""

THEMES: dict[str, dict] = {
    "saffron": {
        "name": "Saffron Palace",
        "emoji": "🪔",
        "region": "Mughal · North India",
        "tagline": "Of grand durbars and royal kitchens",
        "swatches": ["#FF9933", "#D4A017", "#8B1A1A"],
        "welcome_quote": "The spice-laden air of the darbar carries the soul of Mughal cuisine.",
        "header_deco": "🪔  ·  🌙  ·  ✦  ·  🌙  ·  🪔",
        "vars": {
            "--t-primary":         "#FF9933",
            "--t-secondary":       "#D4A017",
            "--t-accent":          "#8B1A1A",
            "--t-bg":              "#fffdf7",
            "--t-sidebar":         "#1a0800",
            "--t-card":            "#ffffff",
            "--t-card-border":     "#D4A017",
            "--t-text":            "#2c1a0e",
            "--t-muted":           "#8b6040",
            "--t-banner-a":        "#7a1212",
            "--t-banner-b":        "#b22222",
            "--t-heading":         "#8B1A1A",
            "--t-sans":            "#D4A017",
            "--t-input-bg":        "#fffef8",
            "--t-input-text":      "#2c1a0e",
            "--t-tag-bg":          "#f7ede0",
            "--t-tag-text":        "#5a3a1a",
            "--t-prog-a":          "#FF9933",
            "--t-prog-b":          "#D4A017",
            "--t-step-ok-bg":      "#f0faf4",
            "--t-step-ok-border":  "#28a745",
            "--t-step-imp-bg":     "#fff8e7",
            "--t-step-imp-border": "#D4A017",
            "--t-divider":         "#f0d8b0",
            "--t-empty-color":     "#9e7c5a",
            "--t-pattern-size":    "40px 40px",
        },
        "pattern": (
            "radial-gradient(circle at 20% 20%, rgba(212,160,23,0.08) 0%, transparent 55%), "
            "radial-gradient(circle at 80% 80%, rgba(139,26,26,0.06) 0%, transparent 55%), "
            "repeating-linear-gradient(45deg, rgba(212,160,23,0.025) 0, rgba(212,160,23,0.025) 1px, transparent 0, transparent 50%)"
        ),
    },
    "malabar": {
        "name": "Malabar Coast",
        "emoji": "🌴",
        "region": "Kerala · South India",
        "tagline": "Where spices meet the monsoon sea",
        "swatches": ["#2D8A4E", "#F5C518", "#1E5F8A"],
        "welcome_quote": "In the land of coconut and cardamom, every meal is a gift from the earth.",
        "header_deco": "🌴  ·  🥥  ·  🌿  ·  🐟  ·  🌴",
        "vars": {
            "--t-primary":         "#2D8A4E",
            "--t-secondary":       "#F5C518",
            "--t-accent":          "#1E5F8A",
            "--t-bg":              "#f0fff4",
            "--t-sidebar":         "#0D2818",
            "--t-card":            "#ffffff",
            "--t-card-border":     "#2D8A4E",
            "--t-text":            "#0D2818",
            "--t-muted":           "#4a7a5a",
            "--t-banner-a":        "#0D5C2E",
            "--t-banner-b":        "#1a8a4e",
            "--t-heading":         "#0D5C2E",
            "--t-sans":            "#F5C518",
            "--t-input-bg":        "#f8fffa",
            "--t-input-text":      "#0D2818",
            "--t-tag-bg":          "#e8f5e9",
            "--t-tag-text":        "#1b5e20",
            "--t-prog-a":          "#2D8A4E",
            "--t-prog-b":          "#F5C518",
            "--t-step-ok-bg":      "#f0faf4",
            "--t-step-ok-border":  "#2D8A4E",
            "--t-step-imp-bg":     "#fffde7",
            "--t-step-imp-border": "#F5C518",
            "--t-divider":         "#b2dfdb",
            "--t-empty-color":     "#4a7a5a",
            "--t-pattern-size":    "30px 30px",
        },
        "pattern": (
            "repeating-linear-gradient(120deg, rgba(45,138,78,0.05) 0, rgba(45,138,78,0.05) 1px, transparent 0, transparent 30px), "
            "repeating-linear-gradient(60deg,  rgba(45,138,78,0.05) 0, rgba(45,138,78,0.05) 1px, transparent 0, transparent 30px)"
        ),
    },
    "rajputana": {
        "name": "Rajputana",
        "emoji": "🌺",
        "region": "Rajasthan · West India",
        "tagline": "Bold colors, bolder flavors, timeless spirit",
        "swatches": ["#C2185B", "#FF8F00", "#4A148C"],
        "welcome_quote": "Like the desert blooms after rain, Rajasthani food bursts with unexpected richness.",
        "header_deco": "🌺  ·  🐪  ·  ✦  ·  🏰  ·  🌺",
        "vars": {
            "--t-primary":         "#C2185B",
            "--t-secondary":       "#FF8F00",
            "--t-accent":          "#4A148C",
            "--t-bg":              "#fff9fc",
            "--t-sidebar":         "#1a0010",
            "--t-card":            "#ffffff",
            "--t-card-border":     "#C2185B",
            "--t-text":            "#1a0010",
            "--t-muted":           "#7a3060",
            "--t-banner-a":        "#880E4F",
            "--t-banner-b":        "#C2185B",
            "--t-heading":         "#880E4F",
            "--t-sans":            "#FF8F00",
            "--t-input-bg":        "#fff8fc",
            "--t-input-text":      "#1a0010",
            "--t-tag-bg":          "#fce4ec",
            "--t-tag-text":        "#880E4F",
            "--t-prog-a":          "#C2185B",
            "--t-prog-b":          "#FF8F00",
            "--t-step-ok-bg":      "#f3e5f5",
            "--t-step-ok-border":  "#4A148C",
            "--t-step-imp-bg":     "#fff3e0",
            "--t-step-imp-border": "#FF8F00",
            "--t-divider":         "#f8bbd0",
            "--t-empty-color":     "#7a3060",
            "--t-pattern-size":    "24px 24px",
        },
        "pattern": (
            "radial-gradient(rgba(194,24,91,0.06) 1.5px, transparent 1.5px), "
            "radial-gradient(rgba(255,143,0,0.04) 1px, transparent 1px)"
        ),
    },
    "bengal": {
        "name": "Bengal Ochre",
        "emoji": "🪷",
        "region": "Bengal · East India",
        "tagline": "Where culture and mustard oil season every dish",
        "swatches": ["#C8970A", "#8B3A3A", "#1A5276"],
        "welcome_quote": "In Bengal, food is poetry — each dish tells a story of rivers and seasons.",
        "header_deco": "🪷  ·  🐟  ·  🌸  ·  🎨  ·  🪷",
        "vars": {
            "--t-primary":         "#C8970A",
            "--t-secondary":       "#8B3A3A",
            "--t-accent":          "#1A5276",
            "--t-bg":              "#fffff0",
            "--t-sidebar":         "#1a1000",
            "--t-card":            "#fffef8",
            "--t-card-border":     "#C8970A",
            "--t-text":            "#1a0a00",
            "--t-muted":           "#7a6030",
            "--t-banner-a":        "#7a5800",
            "--t-banner-b":        "#C8970A",
            "--t-heading":         "#7a5800",
            "--t-sans":            "#C8970A",
            "--t-input-bg":        "#fffef5",
            "--t-input-text":      "#1a0a00",
            "--t-tag-bg":          "#fff8e1",
            "--t-tag-text":        "#7a5800",
            "--t-prog-a":          "#C8970A",
            "--t-prog-b":          "#8B3A3A",
            "--t-step-ok-bg":      "#e8f5e9",
            "--t-step-ok-border":  "#1A5276",
            "--t-step-imp-bg":     "#fffde7",
            "--t-step-imp-border": "#C8970A",
            "--t-divider":         "#f0d080",
            "--t-empty-color":     "#7a6030",
            "--t-pattern-size":    "20px 20px",
        },
        "pattern": (
            "radial-gradient(rgba(200,151,10,0.09) 1px, transparent 1px)"
        ),
    },
    "tandoor": {
        "name": "Tandoor Night",
        "emoji": "🔥",
        "region": "Dhaba · North India",
        "tagline": "Smoky, charred, and deeply satisfying",
        "swatches": ["#E64A19", "#FF8F00", "#2a2a2a"],
        "welcome_quote": "Under the night sky, the tandoor glows — the original fire that forged a cuisine.",
        "header_deco": "🔥  ·  🫙  ·  ✦  ·  🫙  ·  🔥",
        "vars": {
            "--t-primary":         "#E64A19",
            "--t-secondary":       "#FF8F00",
            "--t-accent":          "#FFCC02",
            "--t-bg":              "#1a1a1a",
            "--t-sidebar":         "#0d0d0d",
            "--t-card":            "#252020",
            "--t-card-border":     "#E64A19",
            "--t-text":            "#f0e0cc",
            "--t-muted":           "#a09080",
            "--t-banner-a":        "#BF360C",
            "--t-banner-b":        "#E64A19",
            "--t-heading":         "#FF8F00",
            "--t-sans":            "#FF8F00",
            "--t-input-bg":        "#352525",
            "--t-input-text":      "#f0e0cc",
            "--t-tag-bg":          "#352525",
            "--t-tag-text":        "#f0d0a0",
            "--t-prog-a":          "#E64A19",
            "--t-prog-b":          "#FF8F00",
            "--t-step-ok-bg":      "#1a2a1a",
            "--t-step-ok-border":  "#4CAF50",
            "--t-step-imp-bg":     "#2a1f0d",
            "--t-step-imp-border": "#FF8F00",
            "--t-divider":         "#3a2a1a",
            "--t-empty-color":     "#a09080",
            "--t-pattern-size":    "cover",
        },
        "pattern": (
            "radial-gradient(ellipse at 25% 85%, rgba(230,74,25,0.22) 0%, transparent 55%), "
            "radial-gradient(ellipse at 78% 12%, rgba(255,143,0,0.15) 0%, transparent 55%), "
            "radial-gradient(ellipse at 50% 50%, rgba(60,20,10,0.5) 0%, transparent 80%)"
        ),
    },
}

# Dish thumbnail gradients — shown as colored bar on each recipe card
DISH_GRADIENTS: dict[str, str] = {
    "Indian":         "linear-gradient(135deg, #FF9933 0%, #c0392b 100%)",
    "Italian":        "linear-gradient(135deg, #c0392b 0%, #f5c518 100%)",
    "Mexican":        "linear-gradient(135deg, #27ae60 0%, #f39c12 100%)",
    "Japanese":       "linear-gradient(135deg, #c0392b 0%, #f5f0e8 100%)",
    "Thai":           "linear-gradient(135deg, #27ae60 0%, #f1c40f 100%)",
    "Chinese":        "linear-gradient(135deg, #c0392b 0%, #e67e22 100%)",
    "French":         "linear-gradient(135deg, #2c3e50 0%, #f5c518 100%)",
    "Mediterranean":  "linear-gradient(135deg, #2980b9 0%, #27ae60 100%)",
    "Greek":          "linear-gradient(135deg, #2980b9 0%, #ecf0f1 100%)",
    "Korean":         "linear-gradient(135deg, #c0392b 0%, #922b21 100%)",
    "Middle Eastern": "linear-gradient(135deg, #d4a017 0%, #8b4513 100%)",
    "American":       "linear-gradient(135deg, #c0392b 0%, #2980b9 100%)",
    "Contemporary":   "linear-gradient(135deg, #8e44ad 0%, #2980b9 100%)",
    "Vietnamese":     "linear-gradient(135deg, #c0392b 0%, #f5c518 100%)",
    "Moroccan":       "linear-gradient(135deg, #c0392b 0%, #e67e22 100%)",
    "Spanish":        "linear-gradient(135deg, #c0392b 0%, #f39c12 100%)",
    "Indonesian":     "linear-gradient(135deg, #27ae60 0%, #c0392b 100%)",
    "Turkish":        "linear-gradient(135deg, #c0392b 0%, #ecf0f1 100%)",
    "Ethiopian":      "linear-gradient(135deg, #27ae60 0%, #f1c40f 100%)",
    "Lebanese":       "linear-gradient(135deg, #27ae60 0%, #c0392b 100%)",
}

# Regional Indian sub-type → gradient override
INDIAN_REGIONAL_GRADIENTS: dict[str, str] = {
    "Mughal":    "linear-gradient(135deg, #8B1A1A 0%, #D4A017 100%)",
    "Punjabi":   "linear-gradient(135deg, #FF9933 0%, #8B1A1A 100%)",
    "Bengali":   "linear-gradient(135deg, #C8970A 0%, #1A5276 100%)",
    "Rajasthani":"linear-gradient(135deg, #C2185B 0%, #FF8F00 100%)",
    "Gujarati":  "linear-gradient(135deg, #FF8F00 0%, #27ae60 100%)",
    "Keralan":   "linear-gradient(135deg, #2D8A4E 0%, #1E5F8A 100%)",
    "Hyderabadi":"linear-gradient(135deg, #8B1A1A 0%, #FF9933 100%)",
    "Kashmiri":  "linear-gradient(135deg, #c0392b 0%, #2980b9 100%)",
    "Goan":      "linear-gradient(135deg, #1E5F8A 0%, #f39c12 100%)",
    "Chettinad": "linear-gradient(135deg, #2c1a0e 0%, #c0392b 100%)",
}


def build_theme_css(theme_key: str) -> str:
    """
    Return a complete <style> block injecting all CSS custom properties
    for the chosen theme, plus a few global overrides for Streamlit elements.
    """
    theme = THEMES[theme_key]
    vars_str = "\n".join(f"  {k}: {v};" for k, v in theme["vars"].items())
    pattern = theme["pattern"]

    return f"""<style>
:root {{
{vars_str}
}}
[data-testid="stAppViewContainer"] > .main {{
  background-color: var(--t-bg) !important;
}}
[data-testid="stAppViewContainer"] {{
  background-color: var(--t-bg) !important;
  background-image: {pattern} !important;
  background-size: {theme['vars']['--t-pattern-size']}, {theme['vars']['--t-pattern-size']}, cover !important;
}}
[data-testid="stSidebar"] {{
  background-color: var(--t-sidebar) !important;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {{
  color: #f5deb3 !important;
}}
[data-testid="stSidebar"] .stRadio label span {{
  color: #f5deb3 !important;
}}
.stTabs [data-baseweb="tab"] span {{
  color: var(--t-muted) !important;
}}
.stTabs [aria-selected="true"] span {{
  color: var(--t-primary) !important;
}}
.stTabs [data-baseweb="tab-highlight"] {{
  background: var(--t-primary) !important;
}}
.stTextInput input, .stTextArea textarea {{
  background-color: var(--t-input-bg) !important;
  color: var(--t-input-text) !important;
  border-color: var(--t-divider) !important;
}}
.stSelectbox div[data-baseweb="select"] > div {{
  background-color: var(--t-input-bg) !important;
  color: var(--t-input-text) !important;
}}
.stMultiSelect div[data-baseweb="select"] > div {{
  background-color: var(--t-input-bg) !important;
}}
.stSlider [role="slider"] {{
  background-color: var(--t-primary) !important;
  border-color: var(--t-primary) !important;
}}
.stButton > button[kind="primary"] {{
  background: linear-gradient(90deg, var(--t-primary), var(--t-banner-b)) !important;
  border-color: var(--t-primary) !important;
  color: white !important;
}}
.stButton > button[kind="primary"]:hover {{
  filter: brightness(1.1) !important;
}}
div[data-testid="stNumberInput"] input {{
  background-color: var(--t-input-bg) !important;
  color: var(--t-input-text) !important;
}}
p, li, span, label {{
  color: var(--t-text);
}}
h1, h2, h3, h4 {{
  color: var(--t-heading) !important;
}}
hr {{
  border-color: var(--t-divider) !important;
}}
[data-testid="stExpander"] {{
  background: var(--t-card) !important;
  border-color: var(--t-divider) !important;
}}
[data-testid="stExpander"] summary span {{
  color: var(--t-text) !important;
}}
</style>"""


def get_dish_gradient(cuisine: str, recipe_name: str = "") -> str:
    """Return the CSS gradient string for a given cuisine / recipe name."""
    # Check for Indian regional hints in the name
    name_lower = recipe_name.lower()
    for region, grad in INDIAN_REGIONAL_GRADIENTS.items():
        if region.lower() in name_lower:
            return grad
    return DISH_GRADIENTS.get(cuisine, "linear-gradient(135deg, #888 0%, #444 100%)")
