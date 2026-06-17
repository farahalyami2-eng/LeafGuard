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

<!-- PIPELINE DIAGRAM IM<svg width="100%" viewBox="0 0 680 660" role="img" style="" xmlns="http://www.w3.org/2000/svg">
  <title style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">Agent architecture — custom palette</title>
  <desc style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">GPT-4o-mini agent routing four scenarios A–D to tool chains, RAG system connected to get_product_recommendations</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- Palette:
    #84B179 — dark green       → primary / LLM core / shared
    #A2CB8B — mid green        → Scenarios A & B (image)
    #CADCAE — light sage       → Scenario C / conditional
    #DBCEA5 — warm sand        → Scenario D
    #F2E2B1 — pale cream       → D tools / strips
    text on dark (#84B179): #1E3A1A
    text on mid  (#A2CB8B): #1E3A1A
    text on sage (#CADCAE): #2A3E1E
    text on sand (#DBCEA5): #3A3010
    text on cream(#F2E2B1): #3A3010
    stroke: one shade darker than fill
  -->

  <!-- ── User input ── -->
  <g onclick="sendPrompt('What kinds of inputs can the agent receive?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="230" y="28" width="220" height="44" rx="8" fill="#84B179" stroke="#5A8A50" stroke-width="0.5" style="fill:rgb(132, 177, 121);stroke:rgb(90, 138, 80);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="340" y="50" text-anchor="middle" dominant-baseline="central" fill="#FFFFFF" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">User input</text>
  </g>
  <line x1="340" y1="72" x2="340" y2="104" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- ── LLM core ── -->
  <g onclick="sendPrompt('How does GPT-4o-mini use function calling?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="160" y="104" width="360" height="56" rx="8" fill="#84B179" stroke="#5A8A50" stroke-width="0.5" style="fill:rgb(132, 177, 121);stroke:rgb(90, 138, 80);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="340" y="125" text-anchor="middle" dominant-baseline="central" fill="#FFFFFF" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">GPT-4o-mini</text>
    <text x="340" y="146" text-anchor="middle" dominant-baseline="central" fill="#E8F5E2" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">function calling · parallel_tool_calls=True</text>
  </g>

  <!-- fork -->
  <line x1="340" y1="160" x2="340" y2="192" stroke="#84B179" stroke-width="0.5" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="72" y1="192" x2="608" y2="192" stroke="#84B179" stroke-width="0.5" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="72" y1="192" x2="72" y2="216" stroke="#84B179" stroke-width="0.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="222" y1="192" x2="222" y2="216" stroke="#84B179" stroke-width="0.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="458" y1="192" x2="458" y2="216" stroke="#84B179" stroke-width="0.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="608" y1="192" x2="608" y2="216" stroke="#84B179" stroke-width="0.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- ── Scenario A ── -->
  <g onclick="sendPrompt('What triggers scenario A?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="22" y="216" width="100" height="56" rx="8" fill="#A2CB8B" stroke="#70A060" stroke-width="0.5" style="fill:rgb(162, 203, 139);stroke:rgb(112, 160, 96);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="72" y="236" text-anchor="middle" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Scenario A</text>
    <text x="72" y="254" text-anchor="middle" dominant-baseline="central" fill="#2A5020" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">Image + disease</text>
  </g>

  <!-- ── Scenario B ── -->
  <g onclick="sendPrompt('What triggers scenario B?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="172" y="216" width="100" height="56" rx="8" fill="#A2CB8B" stroke="#70A060" stroke-width="0.5" style="fill:rgb(162, 203, 139);stroke:rgb(112, 160, 96);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="222" y="236" text-anchor="middle" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Scenario B</text>
    <text x="222" y="254" text-anchor="middle" dominant-baseline="central" fill="#2A5020" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">Image + health?</text>
  </g>

  <!-- ── Scenario C ── -->
  <g onclick="sendPrompt('What happens in scenario C?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="408" y="216" width="100" height="56" rx="8" fill="#CADCAE" stroke="#9AB880" stroke-width="0.5" style="fill:rgb(202, 220, 174);stroke:rgb(154, 184, 128);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="458" y="236" text-anchor="middle" dominant-baseline="central" fill="#2A3E1E" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Scenario C</text>
    <text x="458" y="254" text-anchor="middle" dominant-baseline="central" fill="#3A5028" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">Text only</text>
  </g>

  <!-- ── Scenario D ── -->
  <g onclick="sendPrompt('What knowledge base does scenario D use?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="558" y="216" width="100" height="56" rx="8" fill="#DBCEA5" stroke="#B0A870" stroke-width="0.5" style="fill:rgb(219, 206, 165);stroke:rgb(176, 168, 112);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="608" y="236" text-anchor="middle" dominant-baseline="central" fill="#3A3010" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">Scenario D</text>
    <text x="608" y="254" text-anchor="middle" dominant-baseline="central" fill="#4A4018" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">General question</text>
  </g>

  <!-- arrows to tools -->
  <line x1="72" y1="272" x2="72" y2="304" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="222" y1="272" x2="222" y2="304" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="458" y1="272" x2="458" y2="304" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="608" y1="272" x2="608" y2="304" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- ── A tools ── -->
  <g onclick="sendPrompt('How do classify_crop and classify_disease run in parallel?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="16" y="304" width="112" height="68" rx="8" fill="#A2CB8B" stroke="#70A060" stroke-width="0.5" style="fill:rgb(162, 203, 139);stroke:rgb(112, 160, 96);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="72" y="326" text-anchor="middle" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">classify_crop</text>
    <text x="72" y="342" text-anchor="middle" dominant-baseline="central" fill="#2A5020" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">+</text>
    <text x="72" y="358" text-anchor="middle" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">classify_disease</text>
  </g>
  <rect x="20" y="307" width="46" height="13" rx="3" fill="none" stroke="#3A6030" stroke-width="0.5" style="fill:none;stroke:rgb(58, 96, 48);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="43" y="315" text-anchor="middle" dominant-baseline="central" fill="#1E3A1A" font-size="9" font-family="var(--font-sans)" style="fill:rgb(30, 58, 26);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, sans-serif;font-size:9px;font-weight:400;text-anchor:middle;dominant-baseline:central">parallel</text>

  <!-- ── B tool ── -->
  <g onclick="sendPrompt('What does check_health_status return?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="162" y="304" width="120" height="44" rx="8" fill="#A2CB8B" stroke="#70A060" stroke-width="0.5" style="fill:rgb(162, 203, 139);stroke:rgb(112, 160, 96);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="222" y="318" text-anchor="middle" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">check_health</text>
    <text x="222" y="334" text-anchor="middle" dominant-baseline="central" fill="#2A5020" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">_status</text>
  </g>

  <!-- ── D tool ── -->
  <g onclick="sendPrompt('How does answer_agricultural_question work?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="548" y="304" width="120" height="44" rx="8" fill="#F2E2B1" stroke="#C0B870" stroke-width="0.5" style="fill:rgb(242, 226, 177);stroke:rgb(192, 184, 112);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="608" y="318" text-anchor="middle" dominant-baseline="central" fill="#3A3010" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">answer_agri</text>
    <text x="608" y="334" text-anchor="middle" dominant-baseline="central" fill="#4A4018" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">_question</text>
  </g>

  <!-- B conditional arrow -->
  <line x1="222" y1="348" x2="222" y2="378" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- ── if diseased — widened ── -->
  <g onclick="sendPrompt('What happens when check_health finds disease?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="142" y="378" width="220" height="44" rx="8" fill="#CADCAE" stroke="#9AB880" stroke-width="0.5" style="fill:rgb(202, 220, 174);stroke:rgb(154, 184, 128);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="252" y="392" text-anchor="middle" dominant-baseline="central" fill="#2A3E1E" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">if diseased</text>
    <text x="252" y="408" text-anchor="middle" dominant-baseline="central" fill="#3A5028" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">classify crop + disease</text>
  </g>

  <!-- merge: A, B-conditional, C → shared recommendations -->
  <line x1="72" y1="372" x2="72" y2="452" stroke="#84B179" stroke-width="0.5" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="252" y1="422" x2="252" y2="452" stroke="#84B179" stroke-width="0.5" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="458" y1="304" x2="458" y2="452" stroke="#84B179" stroke-width="0.5" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="72" y1="452" x2="458" y2="452" stroke="#84B179" stroke-width="0.5" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <line x1="265" y1="452" x2="265" y2="468" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- ── Shared recommendations ── -->
  <g onclick="sendPrompt('What does the product recommendation output look like?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="40" y="468" width="450" height="44" rx="8" fill="#84B179" stroke="#5A8A50" stroke-width="0.5" style="fill:rgb(132, 177, 121);stroke:rgb(90, 138, 80);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="265" y="490" text-anchor="middle" dominant-baseline="central" fill="#FFFFFF" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">get_product_recommendations</text>
  </g>

  <!-- ThreadPoolExecutor strip -->
  <rect x="40" y="516" width="450" height="16" rx="4" fill="#F2E2B1" stroke="#C0B870" stroke-width="0.5" style="fill:rgb(242, 226, 177);stroke:rgb(192, 184, 112);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="265" y="524" text-anchor="middle" dominant-baseline="central" fill="#3A3010" font-size="10" font-family="var(--font-sans)" style="fill:rgb(58, 48, 16);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, sans-serif;font-size:10px;font-weight:400;text-anchor:middle;dominant-baseline:central">ThreadPoolExecutor — parallel calls run concurrently</text>

  <!-- ── RAG system — D arrow straight down, then arrow into RAG box ── -->
  <line x1="608" y1="348" x2="608" y2="468" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- ── RAG system box ── -->
  <g onclick="sendPrompt('How does the RAG system answer agricultural questions?')" style="fill:rgb(0, 0, 0);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto">
    <rect x="548" y="468" width="120" height="44" rx="8" fill="#DBCEA5" stroke="#B0A870" stroke-width="0.5" style="fill:rgb(219, 206, 165);stroke:rgb(176, 168, 112);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
    <text x="608" y="490" text-anchor="middle" dominant-baseline="central" fill="#3A3010" style="fill:rgb(250, 249, 245);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:14px;font-weight:500;text-anchor:middle;dominant-baseline:central">RAG system</text>
  </g>

  <!-- RAG → recommendations: left arrow from RAG to rec box right edge -->
  <line x1="548" y1="490" x2="492" y2="490" stroke="#84B179" stroke-width="1.5" marker-end="url(#arrow)" style="fill:rgb(0, 0, 0);stroke:rgb(132, 177, 121);color:rgb(255, 255, 255);stroke-width:1.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>

  <!-- Lazy imports note -->
  <text x="340" y="572" text-anchor="middle" dominant-baseline="central" fill="#3A5028" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:middle;dominant-baseline:central">Lazy imports: torch / torchvision / timm — loaded only when image tools fire</text>

  <!-- Legend -->
  <rect x="40" y="596" width="12" height="12" rx="2" fill="#84B179" stroke="#5A8A50" stroke-width="0.5" style="fill:rgb(132, 177, 121);stroke:rgb(90, 138, 80);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="58" y="603" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">Core / shared</text>
  <rect x="160" y="596" width="12" height="12" rx="2" fill="#A2CB8B" stroke="#70A060" stroke-width="0.5" style="fill:rgb(162, 203, 139);stroke:rgb(112, 160, 96);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="178" y="603" dominant-baseline="central" fill="#1E3A1A" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">Image A/B</text>
  <rect x="270" y="596" width="12" height="12" rx="2" fill="#CADCAE" stroke="#9AB880" stroke-width="0.5" style="fill:rgb(202, 220, 174);stroke:rgb(154, 184, 128);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="288" y="603" dominant-baseline="central" fill="#2A3E1E" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">Scenario C</text>
  <rect x="380" y="596" width="12" height="12" rx="2" fill="#DBCEA5" stroke="#B0A870" stroke-width="0.5" style="fill:rgb(219, 206, 165);stroke:rgb(176, 168, 112);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="398" y="603" dominant-baseline="central" fill="#3A3010" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">Scenario D</text>
  <rect x="490" y="596" width="12" height="12" rx="2" fill="#F2E2B1" stroke="#C0B870" stroke-width="0.5" style="fill:rgb(242, 226, 177);stroke:rgb(192, 184, 112);color:rgb(255, 255, 255);stroke-width:0.5px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:16px;font-weight:400;text-anchor:start;dominant-baseline:auto"/>
  <text x="508" y="603" dominant-baseline="central" fill="#3A3010" style="fill:rgb(194, 192, 182);stroke:none;color:rgb(255, 255, 255);stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;opacity:1;font-family:&quot;Anthropic Sans&quot;, -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, sans-serif;font-size:12px;font-weight:400;text-anchor:start;dominant-baseline:central">D tools</text>
(<img width="680" height="660" alt="agent_architecture_new_palette" src="https://github.com/user-attachments/assets/80bd9b00-f2c7-437b-9f3e-3d7764b5a3ce" />
)


The pipeline is a **conditional branching flow** — what happens after the health check depends entirely on the result:
- **Healthy path:** only the crop identifier runs, then growth-support recommendations are returned
- **Diseased path:** YOLO segmentation localises the disease region → disease classifier identifies the type → crop identifier runs **in parallel** with the disease classifier (using `ThreadPoolExecutor`) to save latency → recommendation engine combines both results
- **Date palm mode:** a `--datepalm` flag swaps the 9-class disease classifier for a specialist 3-class model (`brown_spots`, `healthy`, `white_scale`)

---


The pipeline is a **conditional branching flow** — what happens after the health check depends entirely on the result:

- **Healthy path:** only the crop identifier runs, then growth-support recommendations are returned
- **Diseased path:** YOLO segmentation localises the disease region → disease classifier identifies the type → crop identifier runs **in parallel** with the disease classifier (using `ThreadPoolExecutor`) to save latency → recommendation engine combines both results
- **Date palm mode:** a `--datepalm` flag swaps the 9-class disease classifier for a specialist 3-class model (`brown_spots`, `healthy`, `white_scale`)

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

## Pipeline Architecture <p align="center"> <img width="680" height="660" alt="Pipeline Architecture"src="https://github.com/user-attachments/assets/9b5343d4-979e-4df9-b47a-5cf6b1462612" /> </p> The pipeline is a **conditional branching flow** — what happens after the health check depends entirely on the result: - **Healthy path:** only the crop identifier runs, then growth-support recommendations are returned - **Diseased path:** YOLO segmentation localises the disease region → disease classifier identifies the type → crop identifier runs **in parallel**with the disease classifier (using `ThreadPoolExecutor`) to save latency → recommendation engine combines both results- **Date palm mode:** a `--datepalm` flag swaps the 9-class disease classifier for a specialist 3-class model (`brown_spots`, `healthy`, `white_scale`) ---

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

```
LeafGuard/
├── pipeline.py                  # End-to-end inference API + CLI
├── agent.py                     # LLM agent with tool calling
├── .gitignore
│
├── AI Models/
│   └── model_inference.py       # LeafGuardModels class
│                                # predict_binary / predict_crop /
│                                # predict_disease / predict_datepalm
│
├── recommendation Engine/
│   └── recommender.py           # Recommender class
│
└── AgroRAG/
    ├── rag_with_intent.py       # RAGChatbot class
    ├── .env                     # OPENAI_API_KEY (not committed)
    └── vectorstore/             # ChromaDB index (auto-built on first run)
```

---

## Installation

```bash
git clone https://github.com/farahalyami2-eng/LeafGuard.git
cd LeafGuard

pip install torch torchvision timm ultralytics \
            openai langchain chromadb python-dotenv
```

Place model weights in `AI Models/` — see [Model Weights](#model-weights).

Create `AgroRAG/.env`:
```
OPENAI_API_KEY=sk-...
```

---

## Usage

### Python API

```python
# ── Pipeline (fast, no LLM) ──────────────────────────────────────────
from pipeline import LeafGuardPipeline

pipe = LeafGuardPipeline()
result = pipe.analyze("leaf.jpg", top_k=5)
print(result["disease"], result["crop_type"])

# ── Agent (conversational, GPT-4o-mini) ─────────────────────────────
from agent import LeafGuardAgent

agent = LeafGuardAgent()
result = agent.chat("What's wrong with this plant?", image_path="leaf.jpg")
print(result["answer"])
```

### CLI

```bash
# Pipeline
python pipeline.py --image leaf.jpg --pretty
python pipeline.py --image palm.jpg --datepalm --top_k 3 --pretty

# Agent
python agent.py --message "diagnose this" --image leaf.py --pretty
python agent.py --message "how do I apply Bacteria Clear?" --pretty
python agent.py   # interactive REPL
```

---

## Classes Reference

### Disease Classes (9)

<!-- DISEASE CLASSES IMAGE HERE -->

| Class | Description |
|-------|-------------|
| `Canker_Wilt` | Bacterial or fungal canker causing wilting and dieback |
| `Downy_Mildew` | Water mould producing yellow patches on upper leaf surfaces |
| `Leaf_Blight` | Rapid browning and death of leaf tissue |
| `Leaf_Spot` | Circular lesions from fungal or bacterial infection |
| `Mosaic_Virus` | Viral infection producing mosaic yellowing patterns |
| `Powdery_Mildew` | White powdery fungal coating on leaf surfaces |
| `Rot` | Tissue decay caused by fungal or bacterial pathogens |
| `Rust` | Orange/brown pustules from rust fungi |
| `Scab_Smut` | Rough lesions or dark spore masses on leaves/fruit |

### Date Palm Classes (3) — specialist model

| Class | Description |
|-------|-------------|
| `brown_spots` | Fungal infection causing brown lesion spotting |
| `healthy` | No disease detected |
| `white_scale` | Scale insect (Parlatoria blanchardii) infestation |

### Crop Classes (30)

<!-- CROP CLASSES IMAGE HERE -->

`apple` · `banana` · `basil` · `bean` · `bell_pepper` · `blueberry` · `broccoli` · `cabbage` · `carrot` · `cherry` · `citrus` · `coffee` · `corn` · `cucumber` · `eggplant` · `garlic` · `ginger` · `grape` · `lettuce` · `peach` · `plum` · `potato` · `raspberry` · `rice` · `soybean` · `squash` · `strawberry` · `tomato` · `wheat` · `zucchini`

---

## Model Weights

Weights are not stored in this repository due to file size. Download links will be published here on release.

| Weight File | Model | Size (approx) | Download |
|-------------|-------|---------------|----------|
| `best_binary_classifier.pt` | Binary Health | ~85 MB | _coming soon_ |
| `best_yolo_seg.pt` | YOLO Segmentation | ~22 MB | _coming soon_ |
| `best_classifier.pt` | Disease Classifier | ~85 MB | _coming soon_ |
| `best_crop_classifier_200.pt` | Crop Identifier | ~85 MB | _coming soon_ |
| `best_datepalm_classifier.pt` | Date Palm | ~85 MB | _coming soon_ |

Place all `.pt` files inside `AI Models/`.

---

## Roadmap

- [ ] FastAPI backend with `/analyze` upload endpoint and structured JSON responses
- [ ] Model weight hosting on HuggingFace Hub
- [ ] ONNX / TorchScript export for edge / mobile deployment
- [ ] Expand crop classifier to include date palm natively (currently requires `--datepalm` flag)
- [ ] Web platform integration (AgroMind UI — simulation + shop + dashboard)
- [ ] Batch inference endpoint for processing multiple images

---

> **Status:** Training complete · Pipeline and agent functional · Web deployment in progress
