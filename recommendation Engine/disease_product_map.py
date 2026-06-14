"""
Static mapping tables for the LeafGuard recommendation engine.

Three sections:
  1. DISEASE_TO_CATEGORIES        — disease class → ordered list of target secondary product categories
  2. DISEASE_TO_PRODUCT_KEYWORDS  — disease class → keywords that appear in product names / usage text
  3. CROP_TO_SPECIFIC_PRODUCTS    — crop class    → crop-specific product name substrings (highest priority)
  4. INCOMPATIBILITY_RULES        — pairs/groups of products that must not be mixed or need timing separation
"""

# ── 1. Disease → secondary product categories ──────────────────────────────
# Listed in descending priority. The recommender scores products matching
# earlier entries in the list more highly.

DISEASE_TO_CATEGORIES: dict[str, list[str]] = {
    # Fungal + bacterial diseases
    "Canker_Wilt": [
        "Bacillus Fungicides",   # biological first (safer, broad-spectrum)
        "Fungicides",            # chemical backup
    ],
    "Downy_Mildew": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "Leaf_Blight": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "Leaf_Spot": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "Powdery_Mildew": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "Rot": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "Rust": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "Scab_Smut": [
        "Bacillus Fungicides",
        "Fungicides",
    ],
    # Viral — no direct cure; strengthen plant immunity & prevent spread
    "Mosaic_Virus": [
        "Biostimulants/Regulators",   # brassinolides boost systemic resistance
        "Bacillus Fungicides",        # reduce secondary infections
        "Insecticides",               # control aphid/whitefly virus vectors
    ],
    # ── Date palm specific ──────────────────────────────────────────────────
    "brown_spots": [   # fungal leaf spots on date palm
        "Bacillus Fungicides",
        "Fungicides",
    ],
    "white_scale": [   # armored scale insect (Parlatoria blanchardii)
        "Insecticides",
    ],
    # ── Healthy plant: preventive / growth-support products ─────────────────
    "healthy": [
        "Foliar Fertilizers/Nutrient Solutions",
        "Macronutrient Water-Soluble Fertilizers",
        "Bacillus Fungicides",          # preventive biological spray
        "Secondary Nutrient Water-Soluble Fertilizers",
        "Biostimulants/Regulators",
    ],
}

# ── 2. Disease → product-name / usage-text keywords ─────────────────────────
# Used as a secondary scoring signal to pull through products whose names or
# usage descriptions mention the relevant active ingredient / target.

DISEASE_TO_PRODUCT_KEYWORDS: dict[str, list[str]] = {
    "Canker_Wilt": [
        "bacteria clear", "kasugamycin", "pyraclostrobin", "carbendazim",
        "metalaxyl", "canker", "wilt",
    ],
    "Downy_Mildew": [
        "bacteria clear", "metalaxyl", "cymoxanil", "carbendazim", "downy",
    ],
    "Leaf_Blight": [
        "bacteria clear", "carbendazim", "pyraclostrobin", "kasugamycin", "blight",
    ],
    "Leaf_Spot": [
        "bacteria clear", "carbendazim", "pyraclostrobin", "leaf spot",
    ],
    "Mosaic_Virus": [
        "virus no.1", "brassinolide", "brassinosteroid", "bacteria clear",
        "mosaic", "virus",
    ],
    "Powdery_Mildew": [
        "bacteria clear", "carbendazim", "pyraclostrobin", "powdery",
    ],
    "Rot": [
        "bacteria clear", "metalaxyl", "carbendazim", "cymoxanil",
        "anti-rot", "rot",
    ],
    "Rust": [
        "bacteria clear", "pyraclostrobin", "carbendazim", "rust",
    ],
    "Scab_Smut": [
        "bacteria clear", "carbendazim", "metalaxyl", "scab", "smut",
    ],
    "brown_spots": [
        "bacteria clear", "garden full clear", "carbendazim", "pyraclostrobin",
        "brown spot",
    ],
    "white_scale": [
        "bifenazate", "imidacloprid", "abamectin", "scale",
        "spider mite killer", "aphid", "happy citrus",
    ],
    "healthy": [
        "one spray green", "vigorous root", "seedling", "nutrient solution",
        "monopotassium", "root explosion", "green leaf",
    ],
}

# ── 3. Crop → crop-specific product substrings ──────────────────────────────
# Lower-cased substrings matched against product names for highest-priority
# crop-tailored recommendations.  Keys match the CROP_CLASSES list in
# model_inference.py (30 classes from the crop classifier).

CROP_TO_SPECIFIC_PRODUCTS: dict[str, list[str]] = {
    "citrus":       ["citrus bacteria clear", "citrus water-soluble"],
    "strawberry":   ["strawberry bacteria clear"],
    "cucumber":     ["cucumber bacteria clear"],
    "rice":         ["rice bacteria clear", "rice disease clear", "golden wheat"],
    "pepper":       ["chili pepper bacteria clear"],
    "bell_pepper":  ["chili pepper bacteria clear"],
    "tomato":       ["bacteria clear (universal)", "bacteria clear (sachet)"],
    "cabbage":      ["cabbage & kale anti-rot", "cabbage & kale water-soluble"],
    "garlic":       ["onion-ginger-garlic bacteria clear", "onion-ginger-garlic water-soluble"],
    "ginger":       ["onion-ginger-garlic bacteria clear", "onion-ginger-garlic water-soluble"],
    "eggplant":     ["eggplant no.1", "bacteria clear (universal)"],
    "corn":         ["bacteria clear (universal)", "golden wheat"],
    "wheat":        ["golden wheat", "bacteria clear (universal)", "rice disease clear"],
    "soybean":      ["bacteria clear (universal)"],
    "potato":       ["underground root & tuber enlarger", "bacteria clear (universal)"],
    "squash":       ["melon booster", "bacteria clear (universal)"],
    "zucchini":     ["melon booster", "bacteria clear (universal)"],
    "apple":        ["garden full clear", "bacteria clear (universal)"],
    "grape":        ["garden full clear", "bacteria clear (universal)"],
    "cherry":       ["garden full clear", "bacteria clear (universal)"],
    "peach":        ["garden full clear", "bacteria clear (universal)"],
    "plum":         ["garden full clear", "bacteria clear (universal)"],
    "blueberry":    ["garden full clear", "bacteria clear (universal)"],
    "raspberry":    ["garden full clear", "bacteria clear (universal)"],
    "banana":       ["bacteria clear (universal)"],
    "basil":        ["bacteria clear (universal)"],
    "bean":         ["bacteria clear (universal)"],
    "broccoli":     ["bacteria clear (universal)"],
    "carrot":       ["underground root & tuber enlarger", "bacteria clear (universal)"],
    "coffee":       ["garden full clear", "bacteria clear (universal)"],
    "lettuce":      ["bacteria clear (universal)", "one spray green"],
    # Date palm — not in the 30-class crop model; used when force_datepalm=True
    "date_palm":    ["garden full clear", "bacteria clear (universal)"],
}

# ── 4. Incompatibility / safety rules ───────────────────────────────────────
# Each rule is a dict with:
#   name              — unique identifier
#   severity          — "critical" | "high" | "medium" | "low"
#   description       — human-readable explanation shown in output warnings
#   category_group_a  — secondary-category names triggering side A  (optional)
#   category_group_b  — secondary-category names triggering side B  (optional)
#   product_keywords_a— lower-cased product-name substrings for side A (optional)
#   product_keywords_b— lower-cased product-name substrings for side B (optional)
#   action            — what to do when both sides present in recommendation list:
#       "remove_a"        remove group-A products from list
#       "warn_and_separate" keep both but add a strong timing-separation warning
#       "warn"            add advisory warning only
#       "deduplicate"     keep only the highest-scoring product from the overlapping group
#   min_count         — minimum items required in group_a before rule fires (default 1)

INCOMPATIBILITY_RULES: list[dict] = [
    {
        "name": "herbicide_isolation",
        "severity": "critical",
        "description": (
            "Herbicides (weed killers) must NEVER be mixed with fungicides, insecticides, "
            "or fertilizers. Mixing causes phytotoxicity to the target crop and chemical "
            "breakdown of all active ingredients. Herbicides are for weed control only — "
            "they are removed from this disease-treatment recommendation."
        ),
        "category_group_a": ["Herbicides"],
        "category_group_b": [
            "Fungicides", "Insecticides", "Bacillus Fungicides",
            "Foliar Fertilizers/Nutrient Solutions",
            "Macronutrient Water-Soluble Fertilizers",
            "Secondary Nutrient Water-Soluble Fertilizers",
            "Biostimulants/Regulators",
        ],
        "action": "remove_a",
    },
    {
        "name": "biological_vs_chemical_fungicide",
        "severity": "high",
        "description": (
            "Chemical fungicides kill the beneficial Bacillus bacteria in biological "
            "fungicide products, eliminating their efficacy. "
            "Do NOT spray both in the same application or within 7 days of each other. "
            "Recommended sequence: apply the chemical fungicide first to knock down the "
            "disease, then wait 7-10 days before introducing the biological product."
        ),
        "category_group_a": ["Bacillus Fungicides"],
        "category_group_b": ["Fungicides"],
        "action": "warn_and_separate",
    },
    {
        "name": "organophosphate_alkaline_incompatibility",
        "severity": "high",
        "description": (
            "Organophosphate insecticides (Phoxim, Trichlorfon, Bisultap) decompose "
            "rapidly under alkaline pH conditions. Do not mix with alkaline bactericides "
            "(e.g. Kasugamycin) or alkaline fertilizers. Apply on separate days."
        ),
        "product_keywords_a": ["phoxim", "trichlorfon", "bisultap"],
        "product_keywords_b": ["kasugamycin", "bacteria clear"],
        "action": "warn_and_separate",
    },
    {
        "name": "emamectin_alkaline_incompatibility",
        "severity": "high",
        "description": (
            "Emamectin Benzoate is unstable under alkaline conditions and loses efficacy "
            "when mixed with alkaline products such as Carbendazim WP or Kasugamycin. "
            "Apply these products on separate days."
        ),
        "product_keywords_a": ["emamectin"],
        "product_keywords_b": ["carbendazim", "kasugamycin"],
        "action": "warn_and_separate",
    },
    {
        "name": "multiple_herbicides",
        "severity": "high",
        "description": (
            "Never mix two or more herbicides. Combining herbicides does not improve "
            "weed control and causes unpredictable crop phytotoxicity and chemical "
            "reactions. Choose a single herbicide appropriate for the target weed."
        ),
        "category_group_a": ["Herbicides"],
        "category_group_b": ["Herbicides"],
        "action": "deduplicate",
        "min_count": 2,
    },
    {
        "name": "growth_regulator_timing",
        "severity": "medium",
        "description": (
            "Plant growth regulators (Brassinolide) should not be applied at the same "
            "time as strong chemical pesticides, particularly copper-based products or "
            "Kasugamycin. The chemical residues reduce Brassinolide activity. "
            "Apply growth regulators at least 3 days before or after other sprays."
        ),
        "category_group_a": ["Biostimulants/Regulators"],
        "product_keywords_b": ["kasugamycin", "metalaxyl", "cymoxanil"],
        "action": "warn",
    },
    {
        "name": "duplicate_fungicide_mode_of_action",
        "severity": "low",
        "description": (
            "Recommending two chemical fungicides from the same product category is "
            "redundant and increases resistance risk. Only the highest-scoring chemical "
            "fungicide is retained; rotate modes of action between spray cycles."
        ),
        "category_group_a": ["Fungicides"],
        "category_group_b": ["Fungicides"],
        "action": "deduplicate",
        "min_count": 2,
    },
]
