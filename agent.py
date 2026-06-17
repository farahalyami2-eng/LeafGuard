"""
LeafGuardAgent — LLM-orchestrated agent that connects image classifiers,
product recommender, and RAG Q&A into one conversational interface.

The LLM (GPT-4o-mini with tool calling) decides which tools to invoke based
on the user's message and whether an image was provided:

  Scenario A — image + "what disease?"
      → classify_crop  ─┐  (parallel)
      → classify_disease─┘  → get_product_recommendations

  Scenario B — image + "is this healthy?"
      → check_health_status → if diseased → classify_crop + classify_disease (parallel)
        → get_product_recommendations

  Scenario C — text only: "my citrus has downy mildew"
      → get_product_recommendations(crop_type="citrus", disease="Downy_Mildew")

  Scenario D — text question: "how do I apply this fungicide?"
      → answer_agricultural_question

All components are lazily loaded — only the tools actually called in a turn
trigger their respective model/service loads.

Usage:
    from agent import LeafGuardAgent

    agent = LeafGuardAgent()
    result = agent.chat("What disease does my plant have?", image_path="leaf.jpg")
    print(result["answer"])

CLI:
    python agent.py --message "my citrus has rust, what product?" --pretty
    python agent.py --message "diagnose this" --image leaf.jpg
    python agent.py          # interactive mode
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import threading
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# ── Path setup (must happen before project imports) ─────────────────────────
_ROOT = Path(__file__).parent
load_dotenv(_ROOT / "AgroRAG" / ".env")

sys.path.insert(0, str(_ROOT / "AI Models"))
sys.path.insert(0, str(_ROOT / "recommendation Engine"))
sys.path.insert(0, str(_ROOT / "AgroRAG"))

import anthropic as _anthropic                   # noqa: E402

# Recommender and RAG are imported at module level (no heavy deps at import time).
# model_inference is imported lazily inside _get_models() because it pulls in
# torch/torchvision/timm — expensive at startup and only needed when image tools fire.
from recommender import Recommender             # noqa: E402
from rag_with_intent import RAGChatbot          # noqa: E402


# ── Tool schemas (Anthropic tool-calling format) ────────────────────────────

_TOOLS = [
    {
        "name": "check_health_status",
        "description": (
            "Determines whether the plant in the provided image is healthy or diseased. "
            "Use ONLY when the user explicitly asks about health status "
            "(e.g. 'is this plant okay?', 'does this look healthy?'). "
            "Skip this tool if the user's message already implies the plant is sick "
            "(e.g. they mention symptoms, use words like 'infected', 'sick', 'disease')."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "classify_crop",
        "description": (
            "Identifies the crop or plant type shown in the provided image. "
            "Returns one of 30 types: apple, banana, basil, bean, bell_pepper, "
            "blueberry, broccoli, cabbage, carrot, cherry, citrus, coffee, corn, "
            "cucumber, eggplant, garlic, ginger, grape, lettuce, peach, plum, potato, "
            "raspberry, rice, soybean, squash, strawberry, tomato, wheat, zucchini. "
            "Use when the crop type is not stated in the user's message."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "classify_disease",
        "description": (
            "Detects which of 9 plant diseases is visible in the provided image. "
            "Possible results: Canker_Wilt, Downy_Mildew, Leaf_Blight, Leaf_Spot, "
            "Mosaic_Virus, Powdery_Mildew, Rot, Rust, Scab_Smut. "
            "Use when the plant is known or implied to be diseased. "
            "Do NOT use for date palm plants — use classify_datepalm_disease instead."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "classify_datepalm_disease",
        "description": (
            "Specialised date palm disease detector. "
            "Results: brown_spots (fungal), healthy, or white_scale (scale insects). "
            "Use ONLY when the crop is confirmed to be a date palm."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_product_recommendations",
        "description": (
            "Retrieves ranked agricultural product recommendations for a specific "
            "crop + disease combination. "
            "Call this after you know the crop type and disease status — whether "
            "those came from image tools or from the user's own text. "
            "Also call for healthy plants to get preventive / growth-support products."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "crop_type": {
                    "type": "string",
                    "description": (
                        "Crop or plant type. Use the exact classifier output when "
                        "available, or the crop name from the user's text."
                    ),
                },
                "disease": {
                    "type": "string",
                    "description": (
                        "Exact disease name. Use these normalised forms: "
                        "Canker_Wilt, Downy_Mildew, Leaf_Blight, Leaf_Spot, "
                        "Mosaic_Virus, Powdery_Mildew, Rot, Rust, Scab_Smut, "
                        "brown_spots, white_scale. "
                        "Omit this field if the plant is healthy."
                    ),
                },
                "is_healthy": {
                    "type": "boolean",
                    "description": (
                        "True if the plant is healthy (returns preventive / "
                        "growth-support products). False or omit when diseased."
                    ),
                },
            },
            "required": ["is_healthy"],
        },
    },
    {
        "name": "answer_agricultural_question",
        "description": (
            "Answers text-based agricultural questions using the LeafGuard knowledge base. "
            "Covers: product usage / dosage / mixing ratios, safety and toxicity, "
            "order / delivery / logistics, disease and pest explanations. "
            "Use for any question that does NOT require image analysis or a product lookup. "
            "When crop or disease context is already known, enrich the question string "
            "with that context before calling this tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "The full question to answer. If crop/disease context is known "
                        "from earlier in this conversation, incorporate it here "
                        "(e.g. 'How do I apply Bacteria Clear for Downy_Mildew on citrus?')."
                    ),
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "get_location_advice",
        "description": (
            "Returns climate zone, seasonal conditions, soil type, water quality, "
            "and active agricultural risks for the user's location. "
            "ALWAYS call this tool when the message contains a [User location: ...] prefix. "
            "Use the result to: tailor product recommendations to local stressors, "
            "add heat/humidity/frost/salinity notes, adjust irrigation timing advice, "
            "and mention locally common diseases or pests for the current season."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name extracted from the [User location: City, Country] prefix.",
                },
                "country": {
                    "type": "string",
                    "description": "Country name extracted from the [User location: City, Country] prefix.",
                },
            },
            "required": ["city"],
        },
    },
]

_SYSTEM_PROMPT = """\
You are LeafGuard, an intelligent agricultural assistant. You help farmers and gardeners
diagnose plant diseases and find the right products and treatments.

━━ Available tools ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Image analysis (requires an image):
  • check_health_status      — healthy vs diseased
  • classify_crop            — identifies one of 30 crop types from image
  • classify_disease         — identifies one of 9 disease types (NOT for date palms)
  • classify_datepalm_disease— date palm ONLY: brown_spots / white_scale / healthy

Knowledge tools (always available):
  • get_product_recommendations  — ranked products for a crop + disease
  • answer_agricultural_question — knowledge-base Q&A (usage, safety, logistics)
  • get_location_advice          — climate, soil, seasonal risks for the user's location

━━ Decision rules ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE 1 — Image + disease implied (user mentions symptoms / "disease" / "diagnose" / "sick"):
  → call classify_crop AND classify_disease IN PARALLEL in one round
  → skip check_health_status (it is already implied)
  → then call get_product_recommendations

RULE 2 — Image + "is this healthy?" or "does this look okay?":
  → call check_health_status first (one round)
  → if result is diseased: call classify_crop + classify_disease in parallel (next round)
  → then call get_product_recommendations

RULE 3 — Text only (user states crop AND disease, no image):
  → call get_product_recommendations directly with the extracted crop and disease
  → do NOT run any image tools

RULE 4 — General knowledge question (dosage, safety, how-to, logistics):
  → call answer_agricultural_question with the full question
  → enrich it with any crop/disease context already known

━━ Date palm rule ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

classify_datepalm_disease is a SPECIALIST tool. Call it ONLY when:
  • the user explicitly writes "date palm" / "نخل" in their message, OR
  • classify_crop already returned "date_palm" in a PREVIOUS round of this turn.

classify_crop CANNOT return "date_palm" (it is not in its 30-class list).
Therefore, when the image shows an unknown crop, call classify_crop + classify_disease
in parallel — NEVER call classify_datepalm_disease unless the user mentioned date palm.

━━ Strict deduplication rules ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• NEVER call the same tool more than once per conversation turn.
• NEVER call both classify_disease and classify_datepalm_disease in the same turn.
• If a tool returns an error, do NOT retry it — report the issue to the user instead.
• NEVER call image tools when no image is available.

━━ Location-aware advice ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE 5 — When the message contains [User location: City, Country]:
  → ALWAYS call get_location_advice(city, country) in your first tool round,
    in parallel with any other first-round tools.
  → Use the returned data to enrich your final response:
      • Mention active seasonal risks relevant to the diagnosed crop/disease
      • Add location-specific application timing (e.g. "avoid spraying 10am-4pm in Riyadh heat")
      • Note relevant soil/water adjustments (chelated nutrients for alkaline soil, drip irrigation)
      • Flag locally dominant pests or stressors not captured by generic recommendations

━━ Always end by calling get_product_recommendations ━━━━━━━━━━━━━━━━━━━━━

After any diagnosis (from image or text), always call get_product_recommendations
so the user receives actionable treatment products.

━━ Disease name normalisation ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Always pass disease names in this exact form:
  Canker_Wilt  Downy_Mildew  Leaf_Blight  Leaf_Spot  Mosaic_Virus
  Powdery_Mildew  Rot  Rust  Scab_Smut  brown_spots  white_scale

━━ Response style ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After gathering all tool results, reply concisely:
  1. Diagnosis: crop type + disease (with confidence if from image)
  2. Top 3 recommended products with brief usage notes
  3. Any safety warnings or mixing incompatibilities
  4. Actionable next step"""


# ── Agent ───────────────────────────────────────────────────────────────────

class LeafGuardAgent:
    """
    LLM-orchestrated agent.

    Components are loaded lazily — image models only load when an image tool
    is actually called; the recommender and RAG load on first use.
    Thread-safe lazy loading lets image tools run in parallel safely.
    """

    def __init__(self) -> None:
        self._client = _anthropic.Anthropic()
        self._models     = None   # LeafGuardModels — loaded lazily on first image tool call
        self._recommender: Optional[Recommender] = None
        self._rag: Optional[RAGChatbot] = None
        self._models_lock      = threading.Lock()
        self._recommender_lock = threading.Lock()
        self._rag_lock         = threading.Lock()

    # ── Public entry point ─────────────────────────────────────────────────

    def chat(
        self,
        message: str,
        image_path: Optional[str] = None,
    ) -> dict:
        """
        Process a user message and return a structured response.

        Args:
            message:    User's natural-language message.
            image_path: Optional path to a plant image.

        Returns:
            {
              "answer":       str,        # LLM's final synthesised response
              "tools_used":   list[str],  # Tool names that were called
              "tool_results": dict,       # Raw tool outputs keyed by tool name
            }
        """
        image_note = (
            f"\n\n[Image provided: {image_path}]"
            if image_path
            else "\n\n[No image provided — image analysis tools are not available]"
        )

        messages: list[dict] = [
            {"role": "user", "content": message + image_note},
        ]

        tools_used:   list[str] = []
        tool_results: dict      = {}
        final_text = ""

        # ── Agentic loop ───────────────────────────────────────────────────
        # The LLM may call tools in multiple rounds (e.g. check health first,
        # then based on the result decide to classify disease).
        while True:
            response = self._client.messages.create(
                model      = "claude-haiku-4-5-20251001",
                max_tokens = 4096,
                system     = _SYSTEM_PROMPT,
                messages   = messages,
                tools      = _TOOLS,
                temperature= 0,
            )

            # Collect any text from this turn
            for block in response.content:
                if block.type == "text":
                    final_text = block.text

            if response.stop_reason != "tool_use":
                break  # LLM is done — no more tool calls

            # ── Append assistant turn (preserving all content blocks) ──────
            messages.append({"role": "assistant", "content": response.content})

            # ── Execute all tool_use blocks for this round in parallel ─────
            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

            with concurrent.futures.ThreadPoolExecutor() as pool:
                futures = {
                    b.id: (
                        b.name,
                        pool.submit(
                            self._execute_tool,
                            b.name,
                            b.input,   # already a dict, no json.loads needed
                            image_path,
                        ),
                    )
                    for b in tool_use_blocks
                }

            # Collect results and bundle them into a single user turn
            tool_result_content: list[dict] = []
            for b in tool_use_blocks:
                name, future = futures[b.id]
                try:
                    result = future.result()
                except Exception as exc:
                    result = {"error": str(exc)}

                tools_used.append(name)
                tool_results[name] = result

                tool_result_content.append({
                    "type":        "tool_result",
                    "tool_use_id": b.id,
                    "content":     json.dumps(result, ensure_ascii=False, default=str),
                })

            messages.append({"role": "user", "content": tool_result_content})

        return {
            "answer":       final_text,
            "tools_used":   tools_used,
            "tool_results": tool_results,
        }

    # ── Thread-safe lazy loaders ───────────────────────────────────────────

    def _get_models(self):
        if self._models is None:
            with self._models_lock:
                if self._models is None:
                    # Lazy import: torch/torchvision/timm only load when an image
                    # tool is first called, not at agent startup.
                    from model_inference import LeafGuardModels
                    self._models = LeafGuardModels()
        return self._models

    def _get_recommender(self) -> Recommender:
        if self._recommender is None:
            with self._recommender_lock:
                if self._recommender is None:
                    self._recommender = Recommender()
        return self._recommender

    def _get_rag(self) -> RAGChatbot:
        if self._rag is None:
            with self._rag_lock:
                if self._rag is None:
                    self._rag = RAGChatbot()
        return self._rag

    # ── Tool dispatcher ────────────────────────────────────────────────────

    def _execute_tool(
        self,
        tool_name: str,
        args: dict,
        image_path: Optional[str],
    ) -> dict:
        """Dispatch a single tool call. Returns a JSON-serialisable dict."""

        # ── Guard: image tools need an image ──────────────────────────────
        _image_tools = {
            "check_health_status",
            "classify_crop",
            "classify_disease",
            "classify_datepalm_disease",
        }
        if tool_name in _image_tools:
            if not image_path:
                return {"error": "No image provided. Cannot run image analysis."}

        # ── Image tools ────────────────────────────────────────────────────
        if tool_name == "check_health_status":
            label, conf = self._get_models().predict_binary(image_path)
            return {
                "is_healthy": label == "healthy",
                "label":      label,
                "confidence": conf,
            }

        if tool_name == "classify_crop":
            label, conf = self._get_models().predict_crop(image_path)
            return {"crop_type": label, "confidence": conf}

        if tool_name == "classify_disease":
            label, conf = self._get_models().predict_disease(image_path)
            return {"disease": label, "confidence": conf}

        if tool_name == "classify_datepalm_disease":
            label, conf = self._get_models().predict_datepalm(image_path)
            return {
                "disease":    label,
                "confidence": conf,
                "is_healthy": label == "healthy",
            }

        # ── Knowledge tools ────────────────────────────────────────────────
        if tool_name == "get_product_recommendations":
            result = self._get_recommender().recommend(
                crop_type  = args.get("crop_type"),
                disease    = args.get("disease"),
                is_healthy = args.get("is_healthy", False),
                top_k      = 5,
            )
            return result

        if tool_name == "answer_agricultural_question":
            result = self._get_rag().ask(args.get("question", ""))
            return result

        if tool_name == "get_location_advice":
            from location_advisor import get_location_context
            return get_location_context(
                city    = args.get("city", ""),
                country = args.get("country", ""),
            )

        return {"error": f"Unknown tool: {tool_name}"}


# ── CLI ────────────────────────────────────────────────────────────────────

def _run_interactive(agent: LeafGuardAgent) -> None:
    print("LeafGuard Agent  |  type 'exit' to quit\n")
    while True:
        msg = input("You: ").strip()
        if msg.lower() in ("exit", "quit", "q", ""):
            break
        img = input("Image path (Enter to skip): ").strip() or None
        result = agent.chat(msg, image_path=img)
        print(f"\n[Tools used: {', '.join(result['tools_used']) or 'none'}]")
        print(f"\n{result['answer']}\n")
        print("─" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LeafGuard Agent — plant disease diagnosis + product recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py --message "diagnose this leaf" --image leaf.jpg
  python agent.py --message "my citrus has downy mildew, what product?" --pretty
  python agent.py --message "how do I mix Bacteria Clear?" --pretty
  python agent.py          # interactive mode
        """,
    )
    parser.add_argument("--message", "-m", help="User message")
    parser.add_argument("--image",   "-i", help="Path to plant image (optional)")
    parser.add_argument("--pretty",        action="store_true", help="Pretty-print JSON")
    parser.add_argument("--json",          action="store_true", help="Output raw JSON only")
    args = parser.parse_args()

    agent = LeafGuardAgent()

    if args.message:
        result = agent.chat(args.message, image_path=args.image)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            if args.pretty:
                print(f"\n[Tools used: {', '.join(result['tools_used']) or 'none'}]")
            print(f"\n{result['answer']}")
    else:
        _run_interactive(agent)


if __name__ == "__main__":
    main()
