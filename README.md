<p align="center">
  <!-- HERO BANNER IMAGE HERE -->
</p>

<p align="center">
  <a href="#overview"><img src="https://img.shields.io/badge/status-active%20development-10b981?style=flat-square"/></a>
  <a href="#ai-models"><img src="https://img.shields.io/badge/models-5%20AI%20models-8b5cf6?style=flat-square"/></a>
  <a href="#classes-reference"><img src="https://img.shields.io/badge/crops-30%20types-3b82f6?style=flat-square"/></a>
  <a href="#classes-reference"><img src="https://img.shields.io/badge/diseases-9%20classes-ef4444?style=flat-square"/></a>
  <img src="https://img.shields.io/badge/python-3.9+-f59e0b?style=flat-square"/>
</p>

---

> **Upload a plant photo. Get a diagnosis, crop identification, and ranked treatment products — in one call.**
>
> LeafGuard is a multi-stage AI pipeline that chains a binary health classifier, YOLO segmentation, disease classification, and crop identification into a single structured JSON response. An LLM-orchestrated agent layer adds conversational Q&A using a RAG knowledge base.

---

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [AI Models](#ai-models)
- [Agent Architecture](#agent-architecture)
- [Sample Output](#sample-output)
- [Modules](#modules)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Classes Reference](#classes-reference)
- [Model Weights](#model-weights)
- [Roadmap](#roadmap)

---

## Overview

LeafGuard solves a real problem: a farmer takes a photo of a sick leaf and doesn't know what to do next. The system handles the full chain — *is it sick? what crop is it? what disease? what treatment?* — without the user needing to know anything about AI.

**Two entry points:**

| Entry Point | Use case |
|-------------|----------|
| `pipeline.py` | Python API and CLI — clean, fast, batchable |
| `agent.py` | Conversational agent (GPT-4o-mini) — handles images AND free-text questions |

---

## Pipeline Architecture

<p align="center">
  <img width="680" height="660" alt="Pipeline Architecture" src="https://github.com/user-attachments/assets/9b5343d4-979e-4df9-b47a-5cf6b1462612" />
</p>

The pipeline is a **conditional branching flow** — what happens after the health check depends entirely on the result. On the **healthy path**, only the crop identifier runs, then growth-support recommendations are returned. On the **diseased path**, YOLO segmentation localises the lesion region, the disease classifier identifies the type, and the crop identifier runs in parallel via `ThreadPoolExecutor` to save latency — the recommendation engine then combines both results. A `--datepalm` flag swaps the 9-class disease classifier for a specialist 3-class model (`brown_spots`, `healthy`, `white_scale`).

---

## AI Models

<!-- MODEL CARDS IMAGE HERE -->

<!-- ACCURACY CHART IMAGE HERE -->

| Step | Model | Architecture | Classes | Score | Weight |
|------|-------|-------------|---------|-------|--------|
| Step 0 | Binary Health Classifier | EfficientNetV2-S | 2 | **99% acc** | `best_binary_classifier.pt` |
| Step 1a | YOLO Segmentation | YOLO11s-seg | 9 regions | **57.4% mAP50** | `best_yolo_seg.pt` |
| Step 1b | Disease Classifier | EfficientNetV2-S | 9 diseases | **81% acc** | `best_classifier.pt` |
| Step 2 | Crop Identifier | EfficientNetV2-S | 30 crops | **80% acc** | `best_crop_classifier_200.pt` |
| Special | Date Palm Classifier | EfficientNetV2-S | 3 | **93% acc** | `best_datepalm_classifier.pt` |

> Model training code is not included in this repo. Only exported `.pt` weights are distributed. See [Model Weights](#model-weights).

---

## Agent Architecture

<!-- AGENT DIAGRAM IMAGE HERE -->

The agent uses GPT-4o-mini with OpenAI's function calling API and `parallel_tool_calls=True`. It handles four distinct scenarios automatically:

| Scenario | Trigger | Tool chain |
|----------|---------|------------|
| **A** | Image + disease implied ("diagnose", "sick", "infected") | `classify_crop` + `classify_disease` in parallel → `get_product_recommendations` |
| **B** | Image + health question ("is this okay?", "does this look healthy?") | `check_health_status` → if diseased: `classify_crop` + `classify_disease` → recommendations |
| **C** | Text only — crop and disease stated explicitly | `get_product_recommendations` directly, no image tools called |
| **D** | General knowledge question (dosage, safety, application, logistics) | `answer_agricultural_question` → AgroRAG knowledge base |

**Design details worth noting:**
- `torch` / `torchvision` / `timm` are lazily imported — they only load when an image tool actually fires, keeping startup fast for text-only queries
- All tool calls in a single LLM round are dispatched to a `ThreadPoolExecutor` so parallel calls (e.g. crop + disease) run concurrently
- The agent never calls the same tool twice per turn, and never calls both `classify_disease` and `classify_datepalm_disease` in the same turn

---

## Sample Output

<!-- SAMPLE OUTPUT IMAGE HERE -->

**Full output schema from `pipeline.analyze()`:**

```json
{
  "image": "tomato_leaf.jpg",
  "is_healthy": false,
  "binary_confidence": 0.97,
  "crop_type": "tomato",
  "crop_confidence": 0.89,
  "disease": "Leaf_Blight",
  "disease_confidence": 0.84,
  "recommendations": [
    {
      "product": "Bacteria Clear",
      "category": "Fungicide",
      "dosage": "2 ml/L",
      "application": "Foliar spray",
      "score": 0.95
    },
    {
      "product": "FungiStop Pro",
      "score": 0.88
    }
  ],
  "warnings": [],
  "incompatibilities": []
}
```

---

## Modules

### `pipeline.py` — The Core API

Loads all models once via `LeafGuardPipeline`, exposes `analyze()` for repeated use. Designed to be wrapped directly in a FastAPI endpoint.

```python
from pipeline import LeafGuardPipeline

pipe = LeafGuardPipeline()
result = pipe.analyze("leaf.jpg")                          # standard
result = pipe.analyze("palm.jpg", datepalm_mode=True)      # date palm
result = pipe.analyze("leaf.jpg", top_k=3)                 # limit products
```

**CLI:**
```bash
python pipeline.py --image leaf.jpg --pretty
python pipeline.py --image palm.jpg --datepalm --top_k 3 --pretty
```

---

### `agent.py` — The Conversational Layer

LLM-orchestrated agent. Handles images, text, and mixed queries in a single `chat()` call.

```python
from agent import LeafGuardAgent

agent = LeafGuardAgent()

# Image diagnosis
result = agent.chat("What disease does my plant have?", image_path="leaf.jpg")

# Text-only — no models loaded
result = agent.chat("My citrus has downy mildew, what product?")

# Knowledge question → RAG
result = agent.chat("How do I mix Bacteria Clear safely?")

print(result["answer"])        # LLM's final response
print(result["tools_used"])    # which tools fired
print(result["tool_results"])  # raw tool outputs
```

**CLI:**
```bash
python agent.py --message "diagnose this" --image leaf.jpg --pretty
python agent.py --message "my tomato has rust, what product?" --pretty
python agent.py   # interactive mode
```

---

### `recommendation Engine/` — Product Recommender

Rule-based recommender covering ~30 crop types × 9 disease classes.

- Returns ranked products with dosage, application method, and safety classification
- Generates warnings for overdose risk and soil/crop mismatches
- Detects mixing incompatibilities between recommended products
- Healthy plants receive preventive / growth-support suggestions

---

### Knowledge Base Q&A

Retrieval-Augmented Generation for free-text agricultural questions.

- **Knowledge base:** ~430 Q&A pairs (230 real + 200 synthetic)
- **Topics:** product usage, mixing ratios, safety/toxicity, order logistics, disease biology
- **Stack:** LangChain + ChromaDB + OpenAI embeddings
- **Intent routing:** classifies question type before retrieval for better precision
- Called via `answer_agricultural_question` tool in `agent.py`

---

## Repository Structure
