"""
LocationAdvisor — Climate-aware agricultural context for LeafGuard.

Provides location-specific stressors, seasonal conditions, soil/water notes,
and active disease risks based on the user's city and country.

Public API:
    from location_advisor import get_location_context
    ctx = get_location_context("Riyadh", "Saudi Arabia")
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

# ── Shared seasonal templates for Saudi Arabia ────────────────────────────────

_SA_SUMMER = {
    "season": "Summer (Jun-Sep)",
    "temp_min": 38, "temp_max": 46, "humidity_pct": 10, "rainfall": "None",
    "risks": [
        "Extreme heat stress on all crops",
        "Spider mites — thrive in hot, dry conditions",
        "Heat-induced fungal wilt",
        "Sunscald on exposed fruit",
        "Leaf scorch from dust storms",
    ],
    "advice": (
        "Irrigate at dawn or late evening only. Avoid foliar sprays between 10 am and 4 pm. "
        "Apply anti-stress biostimulants (e.g. Biostimulant Regulator A/B) before peak heat. "
        "Use 30-50% shade netting for sensitive crops."
    ),
}
_SA_SPRING = {
    "season": "Spring (Mar-May)",
    "temp_min": 22, "temp_max": 36, "humidity_pct": 25, "rainfall": "Occasional",
    "risks": [
        "Aphid and whitefly population boom",
        "Late frost on March nights (highland areas)",
        "Powdery mildew onset as humidity rises",
    ],
    "advice": (
        "Monitor aphids and whitefly closely — apply imidacloprid or abamectin early. "
        "Optimal window for systemic fungicide applications."
    ),
}
_SA_AUTUMN = {
    "season": "Autumn (Oct-Nov)",
    "temp_min": 22, "temp_max": 35, "humidity_pct": 25, "rainfall": "Low",
    "risks": [
        "Root rot in over-irrigated plots",
        "Aphid resurgence",
        "Leaf spot diseases",
    ],
    "advice": (
        "Ideal planting season for winter vegetables. "
        "Reduce irrigation frequency as temperatures drop."
    ),
}
_SA_WINTER = {
    "season": "Winter (Dec-Feb)",
    "temp_min": 7, "temp_max": 20, "humidity_pct": 35, "rainfall": "Rare",
    "risks": [
        "Powdery mildew",
        "Downy mildew",
        "Night frost (especially Dec-Jan in central/north KSA)",
        "Root diseases in wet soils",
    ],
    "advice": (
        "Best growing season for most crops. "
        "Protect frost-sensitive plants at night. "
        "Apply copper-based fungicide if humidity exceeds 40%."
    ),
}

_RIYADH_MONTHS: dict[int, dict] = {
    1: _SA_WINTER, 2: _SA_WINTER, 3: _SA_SPRING,
    4: _SA_SPRING, 5: _SA_SPRING, 6: _SA_SUMMER,
    7: _SA_SUMMER, 8: _SA_SUMMER, 9: _SA_SUMMER,
    10: _SA_AUTUMN, 11: _SA_AUTUMN, 12: _SA_WINTER,
}

_COASTAL_SUMMER = {
    "season": "Summer (Jun-Sep)",
    "temp_min": 32, "temp_max": 42, "humidity_pct": 70, "rainfall": "None",
    "risks": [
        "Fungal diseases — Downy Mildew, Gray Mold, Root Rot (high humidity)",
        "Heat + humidity stress on leafy crops",
        "Salt spray leaf burn (coastal plots)",
    ],
    "advice": (
        "Apply systemic fungicides preventively every 10-14 days. "
        "Improve air circulation; prune dense canopies. "
        "Avoid overhead irrigation — use drip only."
    ),
}
_COASTAL_WINTER = {
    "season": "Winter (Dec-Feb)",
    "temp_min": 18, "temp_max": 28, "humidity_pct": 65, "rainfall": "Occasional",
    "risks": ["Downy mildew", "Powdery mildew", "Botrytis gray mold"],
    "advice": "Optimal growing season; maintain weekly fungal spray schedule due to persistent humidity.",
}
_COASTAL_SPRING = {
    "season": "Spring (Mar-May)",
    "temp_min": 25, "temp_max": 35, "humidity_pct": 60, "rainfall": "Low",
    "risks": ["Whitefly", "Scale insects", "Leaf spot"],
    "advice": "Increase irrigation as temperature rises; scout for pest buildup on young growth.",
}

_JEDDAH_MONTHS: dict[int, dict] = {
    1: _COASTAL_WINTER, 2: _COASTAL_WINTER, 3: _COASTAL_SPRING,
    4: _COASTAL_SPRING, 5: {**_COASTAL_SPRING, "temp_max": 38},
    6: _COASTAL_SUMMER, 7: _COASTAL_SUMMER, 8: _COASTAL_SUMMER,
    9: _COASTAL_SUMMER,
    10: _COASTAL_SPRING, 11: _COASTAL_WINTER, 12: _COASTAL_WINTER,
}

_ASIR_SUMMER = {
    "season": "Monsoon Summer (Jun-Sep)",
    "temp_min": 18, "temp_max": 28, "humidity_pct": 80, "rainfall": "High (monsoon)",
    "risks": [
        "Downy Mildew — highest risk in all of KSA",
        "Gray Mold (Botrytis)",
        "Leaf Blight",
        "Root Rot in low-lying areas",
        "Rust on coffee and cereal crops",
    ],
    "advice": (
        "Spray copper-based or systemic fungicide every 7-10 days during monsoon. "
        "Ensure drainage channels are clear before June. "
        "Avoid dense planting — air circulation is critical."
    ),
}
_ASIR_WINTER = {
    "season": "Winter (Dec-Feb)",
    "temp_min": 5, "temp_max": 18, "humidity_pct": 55, "rainfall": "Moderate",
    "risks": ["Frost damage at elevations above 2000m", "Powdery mildew", "Cold-induced root stress"],
    "advice": (
        "Protect frost-sensitive crops at night. "
        "Apply phosphorus fertilizer to improve root cold-hardiness."
    ),
}
_ASIR_SPRING = {
    "season": "Spring (Mar-May)",
    "temp_min": 14, "temp_max": 24, "humidity_pct": 50, "rainfall": "Low-moderate",
    "risks": ["Aphids on new growth", "Whitefly", "Early rust"],
    "advice": "Ideal for planting most crops; monitor aphids on new shoot growth.",
}

_ASIR_MONTHS: dict[int, dict] = {
    1: _ASIR_WINTER, 2: _ASIR_WINTER, 3: _ASIR_SPRING,
    4: _ASIR_SPRING, 5: _ASIR_SPRING,
    6: _ASIR_SUMMER, 7: _ASIR_SUMMER, 8: _ASIR_SUMMER, 9: _ASIR_SUMMER,
    10: _ASIR_SPRING, 11: _ASIR_WINTER, 12: _ASIR_WINTER,
}

_TABUK_WINTER = {
    "season": "Cold Winter (Dec-Feb)",
    "temp_min": 0, "temp_max": 14, "humidity_pct": 40, "rainfall": "Low-moderate",
    "risks": ["Hard frost — citrus and tropical crops at risk", "Powdery mildew", "Cold-induced root damage"],
    "advice": (
        "Mulch root zones of fruit trees. "
        "Apply dormant-season copper spray to stone fruits. "
        "Move frost-sensitive pot plants indoors."
    ),
}
_TABUK_MONTHS: dict[int, dict] = {
    1: _TABUK_WINTER, 2: _TABUK_WINTER,
    3: _SA_SPRING,
    4: _SA_SPRING,
    5: {
        "season": "Late Spring",
        "temp_min": 20, "temp_max": 34, "humidity_pct": 20, "rainfall": "None",
        "risks": ["Heat onset", "Aphids", "Apple rust"],
        "advice": "Monitor aphids; increase irrigation frequency.",
    },
    6: {**_SA_SUMMER, "temp_max": 41},
    7: {**_SA_SUMMER, "temp_max": 42},
    8: {**_SA_SUMMER, "temp_max": 42},
    9: _SA_AUTUMN, 10: _SA_AUTUMN,
    11: _TABUK_WINTER, 12: _TABUK_WINTER,
}

_AHSA_MONTHS: dict[int, dict] = dict(_RIYADH_MONTHS)
_AHSA_SUMMER_HOT = {
    "season": "Summer (Jun-Sep)",
    "temp_min": 38, "temp_max": 48, "humidity_pct": 30, "rainfall": "None",
    "risks": [
        "Date palm white scale (Parlatoria blanchardi) peak activity",
        "Brown spots fungal disease on date palm fronds",
        "Spider mites on vegetables",
        "Extreme heat wilt on non-palms",
    ],
    "advice": (
        "Apply imidacloprid or mineral oil spray for white scale before temperature peaks. "
        "Use copper hydroxide for brown spots on date fronds. "
        "Irrigate vegetable crops at pre-dawn; avoid midday watering."
    ),
}
for m in (6, 7, 8, 9):
    _AHSA_MONTHS[m] = _AHSA_SUMMER_HOT


# ── Climate database ──────────────────────────────────────────────────────────
# Each entry: display, climate, region, soil, water, common_crops,
#             stressors, months (1-12 dict), special_notes

_DB: dict[str, dict] = {

    # ── Saudi Arabia cities ───────────────────────────────────────────────────

    "riyadh": {
        "display": "Riyadh, Saudi Arabia",
        "climate": "Hot Desert (BWh — Köppen)",
        "region": "Najd Plateau, Central Saudi Arabia",
        "elevation_m": 612,
        "annual_temp": "7-46°C",
        "annual_rainfall_mm": 100,
        "soil": "Sandy loam; alkaline (pH 7.5-8.5); often saline in subsoil; very low organic matter",
        "water": "Groundwater (often saline at depth); desalinated municipal supply; treated wastewater for agriculture",
        "common_crops": ["Date palm", "Citrus (protected/greenhouse)", "Tomato", "Pepper", "Cucumber", "Wheat (winter)"],
        "stressors": [
            "Extreme summer heat — 42-46°C from June to September",
            "Very low humidity (8-15%) causing rapid moisture loss",
            "High UV radiation increasing sunscald risk",
            "Frequent dust and sandstorms — physical leaf damage and blocked stomata",
            "Alkaline soil (pH 7.5-8.5) locking out Fe, Mn, Zn micronutrients",
            "Saline irrigation water — sodium accumulation in soil",
            "Water scarcity — groundwater depletion is a long-term risk",
            "Rapid temperature swings (cold nights in winter: 7-10°C)",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Chelated micronutrients (Fe-EDTA, Mn-EDTA, Zn-EDTA) are essential — alkaline pH locks out these elements.",
            "Drip irrigation strongly preferred over sprinkler to conserve water and avoid leaf salt burn.",
            "Apply 30-50% shade netting for heat-sensitive crops during June-September.",
            "Add organic matter (compost) to improve sandy soil structure and water retention.",
            "Best agricultural window: October to March (cool season).",
        ],
    },

    "jeddah": {
        "display": "Jeddah, Saudi Arabia",
        "climate": "Hot Desert with Coastal Humidity (BWh)",
        "region": "Hijaz Coast, Red Sea",
        "elevation_m": 15,
        "annual_temp": "18-42°C",
        "annual_rainfall_mm": 54,
        "soil": "Sandy coastal soil; moderate salinity; poor drainage in low-lying areas",
        "water": "Desalinated seawater; moderate salinity risk in groundwater",
        "common_crops": ["Date palm", "Citrus", "Mango", "Banana", "Vegetables (winter)"],
        "stressors": [
            "High heat combined with high humidity in summer — fungal disease pressure is severe",
            "Salt spray from coastal winds causing leaf burn",
            "Saline irrigation water accelerating soil sodicity",
            "Flash flood risk (November-January) from heavy rain events",
        ],
        "months": _JEDDAH_MONTHS,
        "special_notes": [
            "Coastal humidity (60-80% in summer) creates the highest fungal risk in KSA — Downy Mildew, Gray Mold, Root Rot.",
            "Use copper hydroxide or systemic fungicides (metalaxyl-M, cymoxanil) preventively in summer.",
            "Flash flooding risk in Nov-Jan — ensure drainage channels are clear before winter.",
            "Coastal salt spray can cause leaf tip burn on sensitive crops — rinse foliage after sea-wind events.",
        ],
    },

    "dammam": {
        "display": "Dammam / Eastern Province, Saudi Arabia",
        "climate": "Hot Desert with Gulf Humidity (BWh)",
        "region": "Eastern Province, Arabian Gulf Coast",
        "elevation_m": 10,
        "annual_temp": "10-46°C",
        "annual_rainfall_mm": 80,
        "soil": "Sandy; slightly saline; sabkha (salt flat) areas have very high salinity",
        "water": "Gulf desalination; moderate-to-high salinity in shallow groundwater",
        "common_crops": ["Date palm", "Tomato", "Pepper", "Squash", "Citrus (protected)"],
        "stressors": [
            "Extreme heat combined with Gulf humidity in summer",
            "Saline soil and irrigation water — especially in sabkha (salt flat) areas",
            "Shamal (NW wind) dust storms in spring/early summer",
            "White scale (Parlatoria) and red palm weevil on date palm",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "White scale (Parlatoria blanchardi) is a major date palm pest in Eastern Province — treat with systemic insecticide during crawler stage (spring).",
            "Monitor date palms for Bayoud disease (Fusarium oxysporum f.sp. albedinis) — a serious wilt.",
            "Use mineral oil sprays for white scale; imidacloprid for sucking insects.",
            "Salt-tolerant rootstocks recommended for new plantings in saline areas.",
        ],
    },

    "al ahsa": {
        "display": "Al-Ahsa (Hofuf), Saudi Arabia",
        "climate": "Hot Desert (BWh) — UNESCO Date Palm Capital",
        "region": "Eastern Province inland oasis",
        "elevation_m": 150,
        "annual_temp": "7-48°C",
        "annual_rainfall_mm": 85,
        "soil": "Oasis clay-loam; good natural fertility; moderate salinity in outer zones",
        "water": "Historic artesian springs (declining); treated groundwater for most farms",
        "common_crops": ["Date palm (primary, 3M+ trees)", "Citrus", "Mango", "Vegetables"],
        "stressors": [
            "Extreme summer heat (up to 48°C) — among the hottest in KSA",
            "White scale (Parlatoria blanchardi) on date palm — endemic",
            "Brown spots (Graphiola phoenicis) fungal disease on fronds",
            "Dust storms disrupting date palm pollination in spring",
        ],
        "months": _AHSA_MONTHS,
        "special_notes": [
            "Al-Ahsa has 3 million+ date palms — white scale is the #1 pest concern region-wide.",
            "Treat white scale with systemic insecticide during the crawler emergence stage (April-May).",
            "Brown spots (Graphiola phoenicis) treated with copper-based fungicides before and after summer.",
            "Ensure manual pollination timing (March-April) is not disrupted by dust storms.",
            "The Hassa oasis has naturally fertile soil — reduce nitrogen to avoid excessive vegetative growth.",
        ],
    },

    "hofuf": {
        "display": "Al-Ahsa (Hofuf), Saudi Arabia",
        "climate": "Hot Desert (BWh)",
        "region": "Eastern Province oasis",
        "elevation_m": 150,
        "annual_temp": "7-48°C",
        "annual_rainfall_mm": 85,
        "soil": "Oasis clay-loam; moderate salinity",
        "water": "Treated groundwater",
        "common_crops": ["Date palm", "Citrus", "Mango", "Vegetables"],
        "stressors": ["Extreme summer heat (48°C)", "White scale on date palm", "Brown spots disease", "Dust storms"],
        "months": _AHSA_MONTHS,
        "special_notes": [
            "Date palm capital of KSA — white scale and brown spots are primary disease-pest concerns.",
            "Use imidacloprid systemic treatment for white scale (crawler stage: April-May).",
        ],
    },

    "madinah": {
        "display": "Madinah (Al-Madinah Al-Munawwarah), Saudi Arabia",
        "climate": "Hot Desert (BWh)",
        "region": "Hejaz region, northwestern Saudi Arabia",
        "elevation_m": 608,
        "annual_temp": "8-43°C",
        "annual_rainfall_mm": 40,
        "soil": "Sandy loam; alkaline; very low organic matter (<0.5%)",
        "water": "Deep groundwater; treated wastewater for agriculture; drip irrigation standard",
        "common_crops": ["Date palm (Ajwa, Safawi varieties)", "Wheat (winter)", "Barley", "Vegetables"],
        "stressors": [
            "Extreme heat in summer (40-43°C)",
            "Very low rainfall — essentially all irrigation is artificial",
            "Alkaline sandy soil limiting micronutrient availability",
            "Dust storms in spring (May-June)",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Madinah is famous for Ajwa and Safawi premium dates — protect fronds from brown spots and dust damage.",
            "Drip irrigation is standard — sprinkler use would accelerate soil salinization.",
            "Very low soil organic matter requires regular composting or humic acid amendments.",
        ],
    },

    "makkah": {
        "display": "Makkah (Mecca), Saudi Arabia",
        "climate": "Hot Desert (BWh) — arid rocky terrain",
        "region": "Hijaz Mountains, western Saudi Arabia",
        "elevation_m": 277,
        "annual_temp": "18-43°C",
        "annual_rainfall_mm": 90,
        "soil": "Rocky, shallow sandy soil; very low fertility; low water retention",
        "water": "Desalinated water; rainwater harvesting historically",
        "common_crops": ["Date palm", "Container/protected horticulture (limited)"],
        "stressors": ["Extreme heat", "Rocky/shallow soil limiting root depth", "Very low rainfall"],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Very limited agricultural land due to rocky Hijaz terrain.",
            "Focus on date palm and container/protected horticulture.",
            "Use deep-drip or sub-surface irrigation to reach rock crevices where roots grow.",
        ],
    },

    "tabuk": {
        "display": "Tabuk, Saudi Arabia",
        "climate": "Cold Desert (BWk) — KSA's coolest inland climate",
        "region": "Northwest Saudi Arabia (bordering Jordan)",
        "elevation_m": 768,
        "annual_temp": "0-41°C",
        "annual_rainfall_mm": 33,
        "soil": "Sandy loam with volcanic basalt patches; moderate alkalinity (pH 7.0-7.8)",
        "water": "Groundwater (Disi aquifer); limited rainfall recharge",
        "common_crops": ["Apple (unique to KSA)", "Grape", "Date palm", "Wheat", "Tomato", "Potato"],
        "stressors": [
            "Winter frost (0-5°C nights, December-February) — damaging to citrus and tropicals",
            "Hot dry summer (up to 41°C)",
            "Low rainfall — groundwater-dependent agriculture",
            "Apple and grape rust diseases",
            "Powdery mildew on apple and grape",
        ],
        "months": _TABUK_MONTHS,
        "special_notes": [
            "Tabuk is the only major apple-producing region in Saudi Arabia — rust (Gymnosporangium) and powdery mildew are primary concerns.",
            "Winter frost protection is critical for citrus, mango, and other tropicals.",
            "Grapes require a full fungicide program: Downy Mildew + Powdery Mildew + Botrytis.",
            "Best planting window for most crops: March-May and September-October.",
        ],
    },

    "abha": {
        "display": "Abha, Saudi Arabia",
        "climate": "Semi-arid Highland (BSh/BSk) — greenest city in KSA",
        "region": "Asir Mountains, southwest Saudi Arabia",
        "elevation_m": 2270,
        "annual_temp": "5-28°C",
        "annual_rainfall_mm": 300,
        "soil": "Volcanic loam; slightly acidic (pH 6.0-7.0); moderate fertility",
        "water": "Seasonal monsoon rainfall (Jun-Sep); mountain springs; limited groundwater",
        "common_crops": ["Sorghum", "Vegetables (tomato, pepper)", "Pomegranate", "Citrus", "Khawlani coffee"],
        "stressors": [
            "High humidity during monsoon season (Jun-Sep) — highest fungal disease pressure in KSA",
            "Frost risk at elevations above 2000m (December-January)",
            "Steep terrain — soil erosion and nutrient runoff during heavy rains",
            "Coffee leaf rust (Hemileia vastatrix) on Khawlani coffee",
        ],
        "months": _ASIR_MONTHS,
        "special_notes": [
            "Asir monsoon (Jun-Sep) creates the heaviest fungal disease pressure in all of Saudi Arabia.",
            "Downy Mildew, Rust, and Gray Mold are primary concerns — preventive spray programs (copper + systemic) are essential every 7-10 days.",
            "Khawlani coffee is a heritage crop unique to Asir — protect from leaf rust with copper fungicide before monsoon.",
            "Terrace farming requires contour bunding to prevent soil erosion.",
            "Unlike most of KSA, Asir soil is slightly acidic — standard nutrient availability is better but still benefit from Mg and B supplements.",
        ],
    },

    "asir": {
        "display": "Asir Region, Saudi Arabia",
        "climate": "Semi-arid Highland with Summer Monsoon",
        "region": "Asir Mountains, southwest Saudi Arabia",
        "elevation_m": 1500,
        "annual_temp": "8-32°C",
        "annual_rainfall_mm": 250,
        "soil": "Volcanic loam; slightly acidic (pH 6.2-7.0)",
        "water": "Monsoon rainfall (Jun-Sep); springs",
        "common_crops": ["Sorghum", "Vegetables", "Fruit trees", "Coffee (Khawlani)"],
        "stressors": ["High humidity in monsoon season", "Frost at high elevations", "Fungal diseases", "Soil erosion"],
        "months": _ASIR_MONTHS,
        "special_notes": [
            "Highest rainfall in KSA — manage fungal diseases aggressively during Jun-Sep.",
            "Copper fungicide or systemic fungicide every 10-14 days is minimum in monsoon.",
        ],
    },

    "al qassim": {
        "display": "Al-Qassim (Buraidah/Unaizah), Saudi Arabia",
        "climate": "Hot Desert (BWh) — Saudi Arabia's breadbasket",
        "region": "Qassim Province, north-central Saudi Arabia",
        "elevation_m": 650,
        "annual_temp": "4-45°C",
        "annual_rainfall_mm": 110,
        "soil": "Sandy loam; alkaline; moderate-to-good fertility (better than Riyadh)",
        "water": "Extensive groundwater pivot irrigation; salinity risk from over-extraction",
        "common_crops": ["Wheat (primary)", "Alfalfa", "Barley", "Date palm", "Tomato", "Pepper", "Citrus"],
        "stressors": [
            "Extreme summer heat (up to 45°C)",
            "Cold winter nights (4-10°C) risking frost on citrus/mango",
            "Groundwater salinity — long-term sustainability concern",
            "Dust storms in spring",
            "Spider mites on vegetables in summer",
            "Wheat stripe rust (Puccinia striiformis) in Feb-April",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Al-Qassim is Saudi Arabia's agricultural heartland — largest wheat and alfalfa production area.",
            "Center-pivot irrigation is standard; monitor for soil salinity buildup over time.",
            "Wheat yellow stripe rust (Puccinia striiformis) is a major risk in February-April — scout weekly.",
            "Alfalfa weevil monitoring is recommended in spring.",
            "Best soil in KSA for vegetables — use in autumn/winter season (Sep-Apr).",
        ],
    },

    "qassim": {
        "display": "Al-Qassim, Saudi Arabia",
        "climate": "Hot Desert — Major Agricultural Region",
        "region": "Qassim Province, central Saudi Arabia",
        "elevation_m": 650,
        "annual_temp": "4-45°C",
        "annual_rainfall_mm": 110,
        "soil": "Sandy loam; alkaline",
        "water": "Groundwater pivot irrigation",
        "common_crops": ["Wheat", "Alfalfa", "Date palm", "Tomato", "Pepper"],
        "stressors": ["Extreme heat", "Cold winter nights", "Groundwater salinity", "Wheat stripe rust"],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Largest wheat region in KSA — stripe rust (Puccinia striiformis) is the primary disease (Feb-Apr).",
            "Center-pivot irrigation: beware of long-term salinity buildup.",
        ],
    },

    "buraidah": {
        "display": "Buraidah (Al-Qassim), Saudi Arabia",
        "climate": "Hot Desert — Agricultural Hub",
        "region": "Qassim Province",
        "elevation_m": 650,
        "annual_temp": "4-45°C",
        "annual_rainfall_mm": 110,
        "soil": "Sandy loam; alkaline",
        "water": "Groundwater",
        "common_crops": ["Wheat", "Date palm", "Vegetables"],
        "stressors": ["Extreme heat", "Cold winter nights", "Dust storms", "Stripe rust on wheat"],
        "months": _RIYADH_MONTHS,
        "special_notes": ["Major wheat region — monitor for yellow stripe rust every February-April."],
    },

    "najran": {
        "display": "Najran, Saudi Arabia",
        "climate": "Hot Semi-arid (BSh)",
        "region": "Najran Province, southwest Saudi Arabia",
        "elevation_m": 1220,
        "annual_temp": "10-40°C",
        "annual_rainfall_mm": 90,
        "soil": "Sandy clay; moderate alkalinity; better moisture retention than Riyadh",
        "water": "Wadi flash floods; groundwater wells",
        "common_crops": ["Date palm", "Pomegranate", "Citrus", "Sorghum", "Alfalfa"],
        "stressors": [
            "Hot summers (up to 40°C)",
            "Flash flood risk during wadi (valley) farming",
            "Dust storms",
            "Date palm pests (white scale, red palm weevil)",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Wadi agriculture benefits from flash flood moisture retention — manage drainage carefully.",
            "Pomegranate is a major crop — monitor for Cercospora leaf spot and pomegranate butterfly.",
            "Avoid planting in wadi flood paths during rain season.",
        ],
    },

    "hail": {
        "display": "Hail (Ha'il), Saudi Arabia",
        "climate": "Cold Desert (BWk) — coolest central KSA city",
        "region": "Hail Province, northern Saudi Arabia",
        "elevation_m": 970,
        "annual_temp": "1-41°C",
        "annual_rainfall_mm": 90,
        "soil": "Sandy loam; low-to-moderate alkalinity; slightly better organic matter than Riyadh",
        "water": "Groundwater; limited seasonal rainfall",
        "common_crops": ["Wheat", "Barley", "Date palm", "Pomegranate", "Vegetables"],
        "stressors": [
            "Hard winter frost (December-January, 1-4°C nights) damaging fruit trees",
            "Hot dry summer (up to 41°C)",
            "Dust storms in spring",
            "Frost damage on stone fruit and citrus",
        ],
        "months": {
            **_RIYADH_MONTHS,
            1: {**_TABUK_WINTER, "temp_min": 1,
                "advice": "Hard frost risk — protect fruit trees and tender crops with frost cloth/mulch."},
            2: {**_TABUK_WINTER, "temp_min": 3},
            12: {**_TABUK_WINTER, "temp_min": 2},
        },
        "special_notes": [
            "Hard winter frosts require cold-hardy rootstocks and frost protection measures for stone fruits.",
            "Wheat is the primary crop — monitor for yellow stripe rust in February-March.",
            "Barley performs well in the cooler Hail climate compared to central KSA.",
        ],
    },

    # ── Generic Saudi Arabia / KSA fallback ───────────────────────────────────

    "saudi arabia": {
        "display": "Saudi Arabia (general)",
        "climate": "Predominantly Hot Desert (BWh)",
        "region": "Arabian Peninsula",
        "elevation_m": 600,
        "annual_temp": "7-46°C (varies widely by region)",
        "annual_rainfall_mm": 100,
        "soil": "Sandy loam; alkaline (pH 7.5-8.5); low organic matter; often saline",
        "water": "Groundwater and desalination; salinity risk in many areas",
        "common_crops": ["Date palm", "Wheat", "Vegetables (tomato, pepper, cucumber)", "Citrus", "Alfalfa"],
        "stressors": [
            "Extreme summer heat (Jun-Sep, reaching 46°C inland)",
            "Very low humidity and drought conditions",
            "Alkaline and often saline soil",
            "Dust and sandstorms",
            "Water scarcity — depleting aquifers",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Use chelated micronutrients to counter alkaline soil nutrient lockout (Fe, Mn, Zn deficiency).",
            "Drip irrigation is the recommended standard to conserve water.",
            "Apply anti-stress biostimulants before and during peak summer heat.",
            "Best agricultural growing season: October to March for most vegetable crops.",
        ],
    },

    "ksa": {
        "display": "Saudi Arabia",
        "climate": "Hot Desert (BWh)",
        "region": "Arabian Peninsula",
        "elevation_m": 600,
        "annual_temp": "7-46°C",
        "annual_rainfall_mm": 100,
        "soil": "Sandy loam; alkaline",
        "water": "Groundwater; desalination",
        "common_crops": ["Date palm", "Wheat", "Vegetables", "Citrus"],
        "stressors": ["Extreme heat", "Low humidity", "Alkaline saline soil", "Dust storms"],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Anti-stress biostimulants and chelated micronutrients are essential agricultural inputs in KSA.",
        ],
    },

    # ── Gulf / Middle East ────────────────────────────────────────────────────

    "uae": {
        "display": "United Arab Emirates",
        "climate": "Hot Desert (BWh) with Gulf humidity",
        "region": "Arabian Gulf",
        "elevation_m": 10,
        "annual_temp": "14-48°C",
        "annual_rainfall_mm": 100,
        "soil": "Sandy; highly saline; very low fertility",
        "water": "Desalinated seawater; very saline groundwater",
        "common_crops": ["Date palm", "Vegetables (greenhouse/hydroponic)", "Citrus (greenhouse)"],
        "stressors": [
            "Extreme heat (up to 48°C)",
            "High Gulf humidity in summer — fungal disease pressure",
            "Saline soil and irrigation water",
            "Red palm weevil (Rhynchophorus ferrugineus) on date palm — critical pest",
        ],
        "months": _RIYADH_MONTHS,
        "special_notes": [
            "Red palm weevil (Rhynchophorus ferrugineus) is the most destructive date palm pest in the UAE.",
            "Hydroponic and controlled-environment agriculture are standard due to extreme conditions.",
            "Use saline-tolerant rootstocks; monitor EC (electrical conductivity) of soil regularly.",
        ],
    },

    "jordan": {
        "display": "Jordan",
        "climate": "Mediterranean/Semi-arid mix",
        "region": "Levant (Jordan Valley + highlands)",
        "elevation_m": 700,
        "annual_temp": "4-36°C",
        "annual_rainfall_mm": 200,
        "soil": "Clay-loam; calcareous; moderate-to-good fertility in Jordan Valley",
        "water": "Scarce — Jordan Valley irrigation canals; groundwater in highlands",
        "common_crops": ["Wheat", "Olive", "Grape", "Tomato", "Citrus (Jordan Valley)"],
        "stressors": [
            "Water scarcity — one of the most water-stressed countries globally",
            "Hot dry summers in lowlands",
            "Late frost risk on highland farms (March-April)",
            "Powdery mildew on olive and grape",
            "Tuta absoluta (tomato leaf miner)",
        ],
        "months": {
            1:  {"season":"Winter",      "temp_min":4,  "temp_max":13, "humidity_pct":60, "rainfall":"Moderate",   "risks":["Downy mildew","Frost in highlands"],           "advice":"Dormant pruning; apply copper before rain."},
            2:  {"season":"Late Winter", "temp_min":5,  "temp_max":15, "humidity_pct":58, "rainfall":"Moderate",   "risks":["Downy mildew","Late frost"],                   "advice":"Monitor bud break; protect from frost."},
            3:  {"season":"Spring",      "temp_min":9,  "temp_max":20, "humidity_pct":50, "rainfall":"Moderate",   "risks":["Powdery mildew onset","Aphids"],               "advice":"Apply sulfur-based fungicide for powdery mildew."},
            4:  {"season":"Spring",      "temp_min":13, "temp_max":25, "humidity_pct":40, "rainfall":"Low",        "risks":["Aphids","Spider mites onset","Rust"],           "advice":"Ideal planting window; scout weekly."},
            5:  {"season":"Late Spring", "temp_min":17, "temp_max":30, "humidity_pct":30, "rainfall":"Very low",   "risks":["Spider mites","Whitefly","Early heat stress"],  "advice":"Begin heat-stress management."},
            6:  {"season":"Summer",      "temp_min":21, "temp_max":34, "humidity_pct":20, "rainfall":"None",       "risks":["Spider mites","Fruit sunburn","Powdery mildew"],"advice":"Irrigate early morning; apply miticide."},
            7:  {"season":"Summer",      "temp_min":24, "temp_max":36, "humidity_pct":20, "rainfall":"None",       "risks":["Spider mites","Sunburn","Root rot if over-watered"],"advice":"Reduce irrigation frequency; increase depth."},
            8:  {"season":"Summer",      "temp_min":24, "temp_max":36, "humidity_pct":22, "rainfall":"None",       "risks":["Spider mites","Late blight (highland areas)","Botrytis"],"advice":"Monitor late blight in humid highland areas."},
            9:  {"season":"Autumn",      "temp_min":20, "temp_max":32, "humidity_pct":30, "rainfall":"None",       "risks":["Late blight","Botrytis","Downy mildew return"], "advice":"Apply preventive fungicide before autumn rains."},
            10: {"season":"Autumn",      "temp_min":15, "temp_max":27, "humidity_pct":45, "rainfall":"Low-moderate","risks":["Downy mildew","Leaf blight","Root diseases"],  "advice":"Monitor drainage; apply copper fungicide."},
            11: {"season":"Autumn",      "temp_min":10, "temp_max":20, "humidity_pct":55, "rainfall":"Moderate",   "risks":["Downy mildew","Root rot","Frost (highlands)"], "advice":"Reduce watering; prepare for highland frost."},
            12: {"season":"Winter",      "temp_min":5,  "temp_max":14, "humidity_pct":62, "rainfall":"High",       "risks":["Root diseases","Frost","Botrytis"],             "advice":"Ensure drainage; protect frost-sensitive crops."},
        },
        "special_notes": [
            "Jordan Valley is warm year-round — ideal for winter vegetable production.",
            "Highland olive and grape producers: full fungicide program for powdery + downy mildew.",
            "Tuta absoluta (tomato leaf miner) is one of the most destructive pests in Jordan.",
        ],
    },

    "egypt": {
        "display": "Egypt",
        "climate": "Desert / Mediterranean northern strip",
        "region": "North Africa — Nile Valley",
        "elevation_m": 30,
        "annual_temp": "10-42°C",
        "annual_rainfall_mm": 25,
        "soil": "Nile alluvial clay-loam (fertile Delta/Valley); desert sand in reclamation lands",
        "water": "Nile irrigation canals; groundwater in desert lands",
        "common_crops": ["Cotton", "Wheat", "Rice", "Tomato", "Potato", "Sugarcane", "Citrus", "Mango"],
        "stressors": [
            "Summer heat in Upper Egypt (40-42°C)",
            "Waterlogging in Delta rice fields",
            "Delta soil salinization — ongoing problem",
            "Tuta absoluta (tomato leaf miner)",
            "Fusarium wilt on cotton",
            "Wheat stripe rust (Feb-April)",
        ],
        "months": {
            1:  {"season":"Cool Winter",  "temp_min":9,  "temp_max":19, "humidity_pct":65, "rainfall":"Very low",  "risks":["Powdery mildew","Downy mildew","Frost (Sinai/highlands)"],"advice":"Good wheat season; monitor mildew."},
            2:  {"season":"Winter",       "temp_min":10, "temp_max":21, "humidity_pct":60, "rainfall":"Very low",  "risks":["Powdery mildew","Aphids onset","Wheat rust"],              "advice":"Scout for wheat stripe rust."},
            3:  {"season":"Spring",       "temp_min":14, "temp_max":25, "humidity_pct":55, "rainfall":"None",      "risks":["Aphids","Rust","Tuta absoluta on tomato"],                "advice":"Apply systemic insecticide for Tuta."},
            4:  {"season":"Spring",       "temp_min":18, "temp_max":30, "humidity_pct":45, "rainfall":"None",      "risks":["Tuta absoluta","Whitefly","Spider mites"],                 "advice":"Increase pest scouting frequency."},
            5:  {"season":"Late Spring",  "temp_min":22, "temp_max":35, "humidity_pct":35, "rainfall":"None",      "risks":["Spider mites","Whitefly","Heat stress on tomato"],         "advice":"Harvest wheat; prepare summer crops."},
            6:  {"season":"Summer",       "temp_min":25, "temp_max":38, "humidity_pct":30, "rainfall":"None",      "risks":["Heat stress","Spider mites","Root rot"],                   "advice":"Shade greenhouses; ensure irrigation schedule."},
            7:  {"season":"Summer",       "temp_min":26, "temp_max":40, "humidity_pct":28, "rainfall":"None",      "risks":["Extreme heat (Upper Egypt)","Whitefly","Fusarium wilt"],   "advice":"Monitor Fusarium wilt on cotton."},
            8:  {"season":"Summer",       "temp_min":26, "temp_max":40, "humidity_pct":30, "rainfall":"None",      "risks":["Tuta absoluta","Whitefly","Root rot"],                     "advice":"Maximize pest control on summer tomato."},
            9:  {"season":"Autumn",       "temp_min":23, "temp_max":36, "humidity_pct":35, "rainfall":"None",      "risks":["Downy mildew onset","Spider mites","Leaf spot"],           "advice":"Prepare autumn planting."},
            10: {"season":"Autumn",       "temp_min":19, "temp_max":31, "humidity_pct":55, "rainfall":"None",      "risks":["Downy mildew","Botrytis","Root diseases"],                "advice":"Ideal season for autumn vegetables."},
            11: {"season":"Late Autumn",  "temp_min":14, "temp_max":26, "humidity_pct":65, "rainfall":"Very low",  "risks":["Powdery mildew","Downy mildew","Late blight"],            "advice":"Apply preventive fungicide."},
            12: {"season":"Winter",       "temp_min":10, "temp_max":21, "humidity_pct":68, "rainfall":"Very low",  "risks":["Powdery mildew","Botrytis","Root diseases"],              "advice":"Monitor humidity in greenhouses."},
        },
        "special_notes": [
            "Tuta absoluta (tomato leaf miner) is the most destructive tomato pest in Egypt.",
            "Nile Delta soil is very fertile but faces progressive salinization — manage drainage.",
            "Wheat stripe rust (Puccinia striiformis) is monitored nationally — scout in Feb-April.",
        ],
    },
}

# ── City name aliases ─────────────────────────────────────────────────────────

_ALIASES: dict[str, str] = {
    # Riyadh
    "riad": "riyadh", "ar-riyadh": "riyadh", "ar riyadh": "riyadh",
    # Jeddah
    "jiddah": "jeddah", "jidda": "jeddah", "jedda": "jeddah",
    # Eastern Province
    "eastern province": "dammam", "khobar": "dammam", "al khobar": "dammam",
    "al-khobar": "dammam", "jubail": "dammam", "dhahran": "dammam",
    # Al-Ahsa
    "al-ahsa": "al ahsa", "lahsa": "al ahsa", "ahsa": "al ahsa",
    "hufuf": "hofuf", "al-hufuf": "hofuf", "al hufuf": "hofuf",
    # Madinah
    "medina": "madinah", "al-madinah": "madinah", "al madinah": "madinah",
    "medina al-munawwarah": "madinah",
    # Makkah
    "mecca": "makkah", "al-makkah": "makkah", "al makkah": "makkah",
    # Hail
    "ha'il": "hail", "haail": "hail",
    # Al-Qassim
    "al-qassim": "al qassim", "alqassim": "al qassim", "qasim": "al qassim",
    "unaizah": "al qassim", "buraydah": "buraidah",
    # Abha / Asir
    "khamis mushait": "abha", "khamis mushayt": "abha",
    # KSA generic
    "saudi": "saudi arabia", "ksa": "saudi arabia",
    # Arabic transliterations (common)
    "الرياض": "riyadh", "جدة": "jeddah", "مكة": "makkah",
    "المدينة": "madinah", "الدمام": "dammam", "الأحساء": "al ahsa",
    "تبوك": "tabuk", "أبها": "abha", "حائل": "hail",
    "القصيم": "al qassim", "نجران": "najran",
    # Gulf neighbors (approximate similar climate entries)
    "abu dhabi": "uae", "dubai": "uae", "sharjah": "uae",
    "ajman": "uae", "muscat": "uae", "oman": "uae",
    "bahrain": "dammam", "manama": "dammam",
    "qatar": "dammam", "doha": "dammam",
    # Levant / North Africa
    "cairo": "egypt", "alexandria": "egypt", "giza": "egypt",
    "amman": "jordan",
}


def _normalize(name: str) -> str:
    k = name.strip().lower()
    return _ALIASES.get(k, k)


def get_location_context(
    city: str,
    country: str = "",
    month: Optional[int] = None,
) -> dict:
    """
    Return structured agricultural context for a location.

    Lookup order: city key → city alias → country key → partial match → generic KSA fallback.

    Returns a JSON-serialisable dict for use as an LLM tool result.
    """
    if month is None:
        month = datetime.now().month

    entry = (
        _DB.get(_normalize(city))
        or _DB.get(_normalize(country))
        or next(
            (v for k, v in _DB.items()
             if city.lower() in k or k in city.lower()),
            None,
        )
        or _DB["saudi arabia"]
    )

    seasonal = entry["months"].get(month, entry["months"][6])

    return {
        "location":              entry["display"],
        "climate_zone":          entry["climate"],
        "soil_type":             entry["soil"],
        "water_source":          entry["water"],
        "annual_temp_range":     entry.get("annual_temp", "—"),
        "annual_rainfall":       f"{entry.get('annual_rainfall_mm', '—')} mm/year",
        "common_crops_in_region": entry["common_crops"],
        "permanent_stressors":   entry["stressors"],
        "current_season":        seasonal["season"],
        "current_conditions": {
            "temperature_range": f"{seasonal['temp_min']}-{seasonal['temp_max']}°C",
            "humidity":          f"~{seasonal['humidity_pct']}%",
            "rainfall":          seasonal["rainfall"],
        },
        "active_seasonal_risks": seasonal["risks"],
        "seasonal_action_advice": seasonal["advice"],
        "location_notes":        entry.get("special_notes", []),
    }


# ── Self-test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    for city, country in [
        ("Riyadh", "Saudi Arabia"),
        ("Jeddah", "Saudi Arabia"),
        ("Abha", "Saudi Arabia"),
        ("Tabuk", "Saudi Arabia"),
        ("Al-Ahsa", "Saudi Arabia"),
        ("Cairo", "Egypt"),
        ("Amman", "Jordan"),
        ("Dubai", "UAE"),
    ]:
        ctx = get_location_context(city, country)
        print(f"\n{'='*60}")
        print(f"  {ctx['location']}  |  {ctx['current_season']}")
        print(f"  Temp: {ctx['current_conditions']['temperature_range']}  "
              f"Humidity: {ctx['current_conditions']['humidity']}")
        print(f"  Risks: {', '.join(ctx['active_seasonal_risks'][:3])}")
        print(f"  Notes: {ctx['location_notes'][0] if ctx['location_notes'] else '—'}")
