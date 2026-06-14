"""
LeafGuard end-to-end pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Image  →  binary health check
            │
            ├── healthy ──→  crop classifier  →  growth-support recommendations
            │
            └── diseased ──→  disease classifier  ─┐  (run in parallel)
                               crop classifier     ─┘
                                    │
                                    └──→  recommender  →  ranked products + safety warnings

Date-palm mode (--datepalm flag):
    Replaces the general disease classifier with the specialised date-palm classifier.

CLI:
    python pipeline.py --image path/to/plant.jpg
    python pipeline.py --image path/to/plant.jpg --top_k 5 --datepalm --pretty

Programmatic:
    from pipeline import LeafGuardPipeline
    pipe = LeafGuardPipeline()
    result = pipe.analyze("path/to/plant.jpg")
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
from pathlib import Path

# ── Inject sub-module paths so imports work from any working directory ──────
_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT / "AI Models"))
sys.path.insert(0, str(_ROOT / "recommendation Engine"))

from model_inference import (          # noqa: E402  (after sys.path setup)
    LeafGuardModels,
    BINARY_CLASSES,
    DISEASE_CLASSES,
    DATEPALM_CLASSES,
    CROP_CLASSES,
    predict,
)
from recommender import Recommender    # noqa: E402


# ── Pipeline ───────────────────────────────────────────────────────────────

class LeafGuardPipeline:
    """
    Loads all AI models and the product recommender once, then exposes
    `analyze()` for repeated use.
    """

    def __init__(self) -> None:
        self._models     = LeafGuardModels()
        self._recommender = Recommender()
        print("[LeafGuard] Pipeline ready.")

    # ── Main entry point ───────────────────────────────────────────────────

    def analyze(
        self,
        image_path: str,
        top_k: int = 5,
        datepalm_mode: bool = False,
    ) -> dict:
        """
        Analyse a single plant image and return a structured result.

        Args:
            image_path:    Path to the plant image (JPG, PNG, …).
            top_k:         Maximum number of product recommendations to return.
            datepalm_mode: If True, use the date-palm disease classifier instead
                           of the general 9-class disease classifier.

        Returns:
            {
              "image":               str,
              "is_healthy":          bool,
              "binary_confidence":   float,
              "crop_type":           str | None,
              "crop_confidence":     float | None,
              "disease":             str | None,
              "disease_confidence":  float | None,
              "recommendations":     list[dict],
              "warnings":            list[dict],
              "incompatibilities":   list[dict],
            }
        """
        image_path = str(image_path)

        # ── Step 1: Binary health classification ───────────────────────────
        binary_class, binary_conf = self._models.predict_binary(image_path)
        is_healthy = (binary_class == "healthy")

        result: dict = {
            "image":              image_path,
            "is_healthy":         is_healthy,
            "binary_confidence":  binary_conf,
            "crop_type":          None,
            "crop_confidence":    None,
            "disease":            None,
            "disease_confidence": None,
        }

        if is_healthy:
            # ── Step 2a: Healthy → only identify crop for growth-support recs
            crop_class, crop_conf = self._models.predict_crop(image_path)
            result["crop_type"]       = crop_class
            result["crop_confidence"] = crop_conf

        else:
            # ── Step 2b: Diseased → disease + crop classifiers run in parallel
            disease_fn  = (
                self._models.predict_datepalm
                if datepalm_mode
                else self._models.predict_disease
            )
            disease_labels = DATEPALM_CLASSES if datepalm_mode else DISEASE_CLASSES

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                f_disease = pool.submit(disease_fn, image_path)
                f_crop    = pool.submit(self._models.predict_crop, image_path)

                disease_class, disease_conf = f_disease.result()
                crop_class,    crop_conf    = f_crop.result()

            result["disease"]            = disease_class
            result["disease_confidence"] = disease_conf
            result["crop_type"]          = crop_class
            result["crop_confidence"]    = crop_conf

        # ── Step 3: Product recommendation ────────────────────────────────
        rec = self._recommender.recommend(
            crop_type  = result["crop_type"],
            disease    = result["disease"],
            is_healthy = is_healthy,
            top_k      = top_k,
        )
        result.update(rec)
        return result


# ── CLI ────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="LeafGuard: AI-powered plant disease diagnosis & product recommendation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --image photo.jpg
  python pipeline.py --image photo.jpg --top_k 3 --pretty
  python pipeline.py --image date_palm_leaf.jpg --datepalm --pretty
        """,
    )
    p.add_argument("--image",    required=True,          help="Path to plant image")
    p.add_argument("--top_k",    type=int, default=5,    help="Number of product recommendations (default: 5)")
    p.add_argument("--datepalm", action="store_true",    help="Use date-palm disease classifier (for date palm plants)")
    p.add_argument("--pretty",   action="store_true",    help="Pretty-print JSON output")
    return p


def main() -> None:
    args = _build_parser().parse_args()

    pipe   = LeafGuardPipeline()
    result = pipe.analyze(args.image, top_k=args.top_k, datepalm_mode=args.datepalm)

    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
