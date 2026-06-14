"""
Core recommendation engine for LeafGuard.

Entry point:
    from recommender import Recommender

    rec = Recommender()
    result = rec.recommend(crop_type="citrus", disease="Downy_Mildew", is_healthy=False)
    # result = {
    #   "recommendations": [...],
    #   "warnings": [...],
    #   "incompatibilities": [...]
    # }
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import pandas as pd

from disease_product_map import (
    CROP_TO_SPECIFIC_PRODUCTS,
    DISEASE_TO_CATEGORIES,
    DISEASE_TO_PRODUCT_KEYWORDS,
    INCOMPATIBILITY_RULES,
)

_CATALOG_DIR = Path(__file__).parent / "products dataset"


# ── Catalog loader ─────────────────────────────────────────────────────────

class _ProductCatalog:
    """
    Loads and merges 01_Product_Catalog.xlsx (taxonomy) and
    02_Product_Catalog.xlsx (full product details) into a single DataFrame.

    Merge strategy:
      - Catalog 02 is the primary source (has usage/dosage/crops/ingredients).
      - Catalog 01 fills in primary_category / secondary_category for products
        in Catalog 02 whose names match (case-insensitive exact match first).
      - Products that are only in Catalog 01 are appended with limited info.
    """

    def __init__(self) -> None:
        self.df = self._build()

    def _build(self) -> pd.DataFrame:
        cat1 = pd.read_excel(_CATALOG_DIR / "01_Product_Catalog.xlsx")
        cat2 = pd.read_excel(_CATALOG_DIR / "02_Product_Catalog.xlsx")

        # ── Normalise Cat 1 ────────────────────────────────────────────────
        cat1.columns = ["primary_category", "secondary_category", "product_name"]
        cat1["_key"] = cat1["product_name"].str.lower().str.strip()

        # ── Normalise Cat 2 ────────────────────────────────────────────────
        cat2.columns = [
            "product_id", "product_name", "english_name", "product_type",
            "usage_instructions", "dilution_method", "applicable_crops",
            "specification", "data_source", "main_ingredients", "dosage",
        ]
        cat2["_key"] = cat2["product_name"].str.lower().str.strip()

        # ── Merge taxonomy into Cat 2 ──────────────────────────────────────
        taxonomy = cat1[["_key", "primary_category", "secondary_category"]]
        merged = cat2.merge(taxonomy, on="_key", how="left")

        # ── Append Cat-1-only rows ─────────────────────────────────────────
        matched_keys = set(merged["_key"].dropna().tolist())
        cat1_only = cat1[~cat1["_key"].isin(matched_keys)].copy()

        for col in merged.columns:
            if col not in cat1_only.columns:
                cat1_only[col] = None

        merged = pd.concat(
            [merged, cat1_only[merged.columns]],
            ignore_index=True,
        )

        merged = merged.drop(columns=["_key"])
        merged = merged.drop_duplicates(subset=["product_name"], keep="first")
        merged = merged.reset_index(drop=True)

        # ── Infer missing taxonomy from product name keywords ──────────────
        # Cat-2 products that didn't name-match Cat-1 have no category yet.
        # Fill them in so scoring is not handicapped.
        for idx in merged.index:
            val = merged.at[idx, "secondary_category"]
            if pd.isnull(val) or str(val).strip() == "":
                pri, sec = self._infer_taxonomy(merged.loc[idx])
                if pri:
                    merged.at[idx, "primary_category"]   = pri
                    merged.at[idx, "secondary_category"] = sec

        # Convert any remaining NaN to None for clean JSON serialisation
        merged = merged.where(pd.notna(merged), other=None)
        return merged

    @staticmethod
    def _infer_taxonomy(row: pd.Series) -> tuple[str | None, str | None]:
        """
        Keyword-based fallback to assign (primary_category, secondary_category)
        for products that did not match any row in Catalog 01.
        """
        name = str(row.get("product_name", "") or "").lower()
        ptype = str(row.get("product_type", "") or "").lower()

        # Biological fungicides (Bacillus-based)
        _bio_fungicide_kw = [
            "bacteria clear", "fungus clear", "disease clear",
            "full clear", "fungicide", "nematode clear",
        ]
        if any(k in name for k in _bio_fungicide_kw):
            return "Biological Pesticides", "Bacillus Fungicides"

        # Herbicides
        _herbicide_kw = [
            "glyphosate", "glufosinate", "diquat", "clethodim",
            "tribenuron", "mcpa", "florasulam", "mesotrione",
            "chlorosulfuron", "metsulfuron", "sulfometuron",
            "fenoxaprop", "haloxyfop", "aminopyralid", "benazolin",
            "hexazinone", "oxyfluorfen", "herbicide",
        ]
        if any(k in name for k in _herbicide_kw):
            return "Chemical Pesticides", "Herbicides"

        # Chemical insecticides / acaricides
        _insecticide_kw = [
            "imidacloprid", "abamectin", "emamectin", "thiamethoxam",
            "bifenazate", "chlorfenapyr", "lufenuron", "spinetoram",
            "lambda-cyhalothrin", "cypermethrin", "trichlorfon",
            "bisultap", "phoxim", "metaldehyde", "insect clear",
            "pest killer", "pest repellent", "aphid", "whitefly",
            "spider mite", "thrips",
        ]
        if any(k in name for k in _insecticide_kw):
            return "Chemical Pesticides", "Insecticides"

        # Bt (biological insecticide)
        if "bacillus thuringiensis" in name or ("bt" in name and "4000" in name):
            return "Biological Pesticides", "Microbial Agents"

        # Chemical fungicides
        _chem_fungicide_kw = [
            "carbendazim", "metalaxyl", "cymoxanil", "kasugamycin",
            "pyraclostrobin", "kairun", "gray mold no.1",
        ]
        if any(k in name for k in _chem_fungicide_kw):
            return "Chemical Pesticides", "Fungicides"

        # Virus inhibitor (biological, boosts plant immunity)
        if "virus no.1" in name or "virus inhibitor" in name:
            return "Biological Pesticides", "Bacillus Fungicides"

        # Plant growth regulators
        if any(k in name for k in ["brassinolide", "brassinosteroid", "epibrassinolide"]):
            return "Plant Growth Regulators", "Biostimulants/Regulators"

        # Adjuvants / synergists
        _adjuvant_kw = ["adjuvant", "silicone", "synergist", "organosilicone"]
        if any(k in name for k in _adjuvant_kw):
            return "Chemical Pesticides", "Adjuvants"

        # Water-soluble macro fertilizers
        if "water-soluble fertilizer" in name or "monopotassium phosphate" in name:
            return "Fertilizers", "Macronutrient Water-Soluble Fertilizers"

        # Secondary/micro nutrient fertilizers
        if any(k in name for k in ["boron", "humic acid", "ca-mg-b", "micronutrient"]):
            return "Fertilizers", "Secondary Nutrient Water-Soluble Fertilizers"

        # Growth-support foliar products (catch-all for product_type = Growth Support)
        if ptype == "growth support":
            return "Fertilizers", "Foliar Fertilizers/Nutrient Solutions"

        return None, None


# ── Recommender ────────────────────────────────────────────────────────────

class Recommender:
    """
    Recommends agricultural products given the LeafGuard AI model outputs.

    Usage:
        rec = Recommender()
        result = rec.recommend(
            crop_type  = "cucumber",      # from crop classifier  (str | None)
            disease    = "Powdery_Mildew",# from disease classifier (str | None)
            is_healthy = False,           # from binary classifier
            top_k      = 5,
        )
    """

    def __init__(self) -> None:
        self._catalog = _ProductCatalog()

    # ── Public API ─────────────────────────────────────────────────────────

    def recommend(
        self,
        crop_type: Optional[str] = None,
        disease: Optional[str] = None,
        is_healthy: bool = False,
        top_k: int = 5,
    ) -> dict:
        """
        Returns a dict with three keys:
            recommendations  — list of dicts, highest relevance first
            warnings         — advisory messages (e.g. timing notes)
            incompatibilities— critical conflicts found in the shortlist
        """
        # Healthy plants use the "healthy" disease key
        effective_disease = "healthy" if is_healthy else (disease or "healthy")

        scored_df = self._score_products(crop_type, effective_disease, is_healthy)
        scored_df = scored_df.sort_values("_score", ascending=False).reset_index(drop=True)

        # Fetch extra candidates so safety filtering (deduplication, removal)
        # doesn't leave us short of top_k results.
        candidates = scored_df.head(max(top_k * 3, 15)).copy()

        # Safety rules: clean up / reorder candidates
        filtered_df, _, _ = self._apply_safety_rules(candidates, report_warnings=False)

        # Final slice
        final = filtered_df.sort_values("_score", ascending=False).head(top_k).copy()

        # Report incompatibilities only for what actually appears in the final list
        _, warnings, incompatibilities = self._apply_safety_rules(
            final, report_warnings=True
        )

        recommendations = self._format(final)

        return {
            "recommendations": recommendations,
            "warnings": warnings,
            "incompatibilities": incompatibilities,
        }

    # ── Scoring ────────────────────────────────────────────────────────────

    def _score_products(
        self,
        crop_type: Optional[str],
        disease: str,
        is_healthy: bool,
    ) -> pd.DataFrame:
        df = self._catalog.df.copy()
        df["_score"] = 0.0

        target_cats   = DISEASE_TO_CATEGORIES.get(disease, [])
        kw_list       = DISEASE_TO_PRODUCT_KEYWORDS.get(disease, [])
        crop_specific = self._crop_product_substrings(crop_type)
        crop_lower    = crop_type.lower().replace("_", " ") if crop_type else ""

        # Categories considered "treatment" vs "nutrition"
        _nutrient_cats = {
            "Foliar Fertilizers/Nutrient Solutions",
            "Macronutrient Water-Soluble Fertilizers",
            "Secondary Nutrient Water-Soluble Fertilizers",
        }

        for idx in df.index:
            score = 0.0
            sec_cat  = str(df.at[idx, "secondary_category"] or "").strip()
            pri_cat  = str(df.at[idx, "primary_category"] or "").strip()
            name_lc  = str(df.at[idx, "product_name"] or "").lower()
            usage_lc = str(df.at[idx, "usage_instructions"] or "").lower()
            crops_lc = str(df.at[idx, "applicable_crops"] or "").lower()

            # ── A. Category relevance ──────────────────────────────────────
            if sec_cat in target_cats:
                priority = len(target_cats) - target_cats.index(sec_cat)
                score += 2.0 + priority * 0.5
            elif pri_cat == "Biological Pesticides" and "Bacillus Fungicides" in target_cats:
                score += 0.5

            # ── B. Disease keyword in product name / usage text ────────────
            if kw_list:
                for kw in kw_list:
                    if kw in name_lc or kw in usage_lc:
                        score += 1.5
                        break

            # ── C. Crop-specific product name match ────────────────────────
            if crop_specific:
                for substr in crop_specific:
                    if substr in name_lc:
                        score += 3.0
                        break

            # ── D. Crop mentioned in "Applicable Crops" field ─────────────
            if crop_lower and crop_lower in crops_lc:
                score += 1.0

            # ── E. Penalty: pure fertilisers are secondary when diseased ───
            # When disease is detected, nutrients are supportive — they should
            # not outrank the actual treatment products.
            if not is_healthy and sec_cat in _nutrient_cats and score > 0:
                score -= 2.0

            df.at[idx, "_score"] = score

        return df[df["_score"] > 0].copy()

    def _crop_product_substrings(self, crop_type: Optional[str]) -> list[str]:
        if not crop_type:
            return []
        key = crop_type.lower().strip()
        if key in CROP_TO_SPECIFIC_PRODUCTS:
            return CROP_TO_SPECIFIC_PRODUCTS[key]
        # Partial match: 'bell pepper' → 'pepper' key
        for map_key, products in CROP_TO_SPECIFIC_PRODUCTS.items():
            if map_key in key or key in map_key:
                return products
        return []

    # ── Safety rules ───────────────────────────────────────────────────────

    def _apply_safety_rules(
        self, df: pd.DataFrame, *, report_warnings: bool = True
    ) -> tuple[pd.DataFrame, list[dict], list[dict]]:
        df = df.reset_index(drop=True)
        warnings: list[dict] = []
        incompatibilities: list[dict] = []
        rows_to_drop: set[int] = set()

        sec_cats  = [str(df.at[i, "secondary_category"] or "") for i in df.index]
        pri_cats  = [str(df.at[i, "primary_category"] or "") for i in df.index]
        names_lc  = [str(df.at[i, "product_name"] or "").lower() for i in df.index]

        for rule in INCOMPATIBILITY_RULES:
            group_a_cats = rule.get("category_group_a", [])
            group_b_cats = rule.get("category_group_b", [])
            kw_a         = rule.get("product_keywords_a", [])
            kw_b         = rule.get("product_keywords_b", [])
            action       = rule.get("action", "warn")
            severity     = rule.get("severity", "medium")
            min_count    = rule.get("min_count", 1)

            # Collect indices for side A
            idx_a: list[int] = []
            for i in range(len(df)):
                if (sec_cats[i] in group_a_cats or pri_cats[i] in group_a_cats) or \
                   any(kw in names_lc[i] for kw in kw_a):
                    idx_a.append(i)

            # Collect indices for side B
            idx_b: list[int] = []
            for i in range(len(df)):
                if (sec_cats[i] in group_b_cats or pri_cats[i] in group_b_cats) or \
                   any(kw in names_lc[i] for kw in kw_b):
                    idx_b.append(i)

            has_conflict = len(idx_a) >= min_count and (
                len(idx_b) > 0 or (min_count == 2 and len(idx_a) >= 2)
            )
            if not has_conflict:
                continue

            names_a = [df.at[i, "product_name"] for i in idx_a]
            names_b = [df.at[i, "product_name"] for i in idx_b]

            if action == "remove_a":
                # Hard removal: these products are irrelevant for the scenario
                # (e.g. herbicides in a disease-treatment recommendation).
                rows_to_drop.update(idx_a)

            elif action == "warn_and_separate":
                # Keep both groups in the recommendation but report the conflict
                # so the user knows they must not be mixed in the same spray.
                if report_warnings:
                    incompatibilities.append({
                        "rule":        rule["name"],
                        "severity":    severity,
                        "message":     rule["description"],
                        "products_a":  names_a,
                        "products_b":  names_b,
                        "advice":      (
                            "Do NOT mix these in the same spray solution. "
                            "Apply on separate days with at least 7 days between treatments."
                        ),
                    })

            elif action == "warn":
                if report_warnings:
                    warnings.append({
                        "rule":     rule["name"],
                        "severity": severity,
                        "message":  rule["description"],
                    })

            elif action == "deduplicate":
                combined = idx_a if not idx_b else idx_a + [i for i in idx_b if i not in idx_a]
                combined_sorted = sorted(combined, key=lambda i: df.at[i, "_score"], reverse=True)
                rows_to_drop.update(combined_sorted[1:])

        if rows_to_drop:
            df = df.drop(index=list(rows_to_drop)).reset_index(drop=True)

        return df, warnings, incompatibilities

    # ── Output formatter ───────────────────────────────────────────────────

    def _format(self, df: pd.DataFrame) -> list[dict]:
        out = []
        for _, row in df.iterrows():
            out.append({
                "product_id":        _safe(row.get("product_id"), "N/A"),
                "product_name":      _safe(row.get("product_name"), "Unknown"),
                "primary_category":  _safe(row.get("primary_category"), "Unknown"),
                "secondary_category":_safe(row.get("secondary_category"), "Unknown"),
                "product_type":      _safe(row.get("product_type"), "Unknown"),
                "main_ingredients":  _safe(row.get("main_ingredients"), "See label"),
                "applicable_crops":  _safe(row.get("applicable_crops"), "General use"),
                "dosage":            _safe(row.get("dosage") or row.get("dilution_method"), "See label"),
                "specification":     _safe(row.get("specification"), "N/A"),
                "usage_summary":     _truncate(row.get("usage_instructions"), 300),
                "relevance_score":   round(float(row.get("_score", 0)), 2),
            })
        return out


# ── Helpers ────────────────────────────────────────────────────────────────

def _safe(value, default: str) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return default
    return str(value).strip() or default


def _truncate(value, max_chars: int) -> str:
    text = _safe(value, "See product label.")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "…"
