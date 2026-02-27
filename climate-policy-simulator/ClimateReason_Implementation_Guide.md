# Climate Policy Impact Simulator — Full Implementation Guide

## Project Overview

**Name:** ClimateReason — AI-Powered Climate Policy Impact Simulator
**Tagline:** "See the reasoning behind every climate policy impact"
**Model:** K2 Think V2 (70B open reasoning model) via API
**Stack:** FastAPI (Python) + React frontend + ChromaDB (RAG)
**Build time:** ~2 weeks

---

## Architecture: The 5-Stage Reasoning Pipeline

```
┌──────────────────────────────────────────────────────┐
│                    FRONTEND (React)                   │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  Policy   │  │  Live Stage  │  │  Causal Graph  │ │
│  │  Input    │  │  Progress    │  │  Visualization │ │
│  │  Form     │  │  Feed        │  │  (D3.js)       │ │
│  └────┬─────┘  └──────▲───────┘  └───────▲────────┘ │
│       │               │                  │           │
│       │          SSE (Server-Sent Events) │           │
└───────┼───────────────┼──────────────────┼───────────┘
        │               │                  │
        ▼               │                  │
┌──────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                     │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │              Pipeline Orchestrator               │ │
│  │                                                   │ │
│  │  Stage 1 ──► Stage 2 ──► Stage 3 ──► Stage 4 ──►│ │
│  │  Parse       Direct      Cascade     Validate    │ │
│  │  (low)       (high)      (high)      (medium)    │ │
│  │                                           │      │ │
│  │                                    Stage 5 ◄─────│ │
│  │                                    Synthesize    │ │
│  │                                    (medium)      │ │
│  └──────────────────┬──────────────────────────────┘ │
│                     │                                 │
│  ┌──────────────────▼──────────────────────────────┐ │
│  │              K2 Think V2 Client                  │ │
│  │  - OpenAI-compatible API wrapper                 │ │
│  │  - reasoning_effort parameter control            │ │
│  │  - Structured output parsing                     │ │
│  └──────────────────┬──────────────────────────────┘ │
│                     │                                 │
│  ┌──────────────────▼──────────────────────────────┐ │
│  │              RAG Layer (ChromaDB)                 │ │
│  │  Collections:                                    │ │
│  │  - emission_factors (DEFRA, EPA, IEA)            │ │
│  │  - country_profiles (energy mix, GDP, NDCs)      │ │
│  │  - policy_mechanisms (carbon tax, ETS, subsidies)│ │
│  │  - uae_specific (DoE data, Net Zero 2050)        │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## Project Structure

```
climate-policy-simulator/
├── backend/
│   ├── main.py                    # FastAPI app + SSE endpoint
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Runs the 5-stage pipeline
│   │   ├── stages.py              # Individual stage logic
│   │   └── prompts.py             # All K2 prompt templates
│   ├── k2_client.py               # K2 Think V2 API wrapper
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── store.py               # ChromaDB setup + queries
│   │   └── ingest.py              # Script to load reference data
│   ├── data/
│   │   ├── emission_factors.json  # DEFRA/EPA emission factors
│   │   ├── country_profiles.json  # Energy mix, GDP, emissions by country
│   │   ├── uae_context.json       # UAE-specific data
│   │   └── policy_templates.json  # Known policy mechanism templates
│   ├── models.py                  # Pydantic schemas
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── PolicyInput.jsx     # Policy description form
│   │   │   ├── StageProgress.jsx   # Live stage-by-stage feed
│   │   │   ├── CausalGraph.jsx     # D3.js interactive graph
│   │   │   ├── ReasoningPanel.jsx  # Expandable reasoning chains
│   │   │   ├── ConfidenceBadge.jsx # Confidence level indicators
│   │   │   └── SynthesisReport.jsx # Final executive summary
│   │   └── hooks/
│   │       └── useSSE.js           # Server-Sent Events hook
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   ├── seed_data.py               # Populate RAG with reference data
│   └── test_pipeline.py           # Test with sample policies
├── README.md
└── .env                           # K2 API key
```

---

## Tech Stack Decisions

| Component | Choice | Why |
|-----------|--------|-----|
| Backend | FastAPI (Python) | Async support for SSE streaming, Pydantic for structured data, fastest to build |
| Frontend | React + Vite | Component-based UI for progressive rendering, D3.js integration |
| K2 Client | OpenAI Python SDK | K2 Think V2 is OpenAI-compatible, zero custom code needed |
| RAG | ChromaDB | Lightweight, no server needed, perfect for static reference data |
| Graph Viz | D3.js (force-directed) | Best library for interactive causal graphs, animate node additions |
| Streaming | Server-Sent Events (SSE) | Simpler than WebSockets for one-way server→client updates |
| Styling | Tailwind CSS | Fast, clean UI without custom CSS |

---

## Data Sources (All Free, Public)

### Emission Factors
- **DEFRA 2024 conversion factors**: UK government publishes annually, covers all scopes
- **EPA eGRID**: US power grid emission factors by region
- **IEA Emission Factors**: Country-level electricity emission factors (free summary data)

### Country Profiles
- **Our World in Data (OWID)**: Energy mix, CO2 emissions, GDP — all downloadable CSV
- **Climate Action Tracker**: Country NDC targets, policy ratings
- **IRENA Data & Statistics**: Renewable energy capacity by country (free portal)

### UAE-Specific
- **UAE Net Zero 2050 Strategic Initiative**: Public government document
- **Abu Dhabi DoE Annual Statistical Report**: Energy consumption data
- **UAE NDC (2nd update, 2023)**: Emission reduction targets submitted to UNFCCC
- **ADNOC Sustainability Report 2024**: Public, covers emissions data

### Policy Mechanism Reference
- **World Bank Carbon Pricing Dashboard**: All active carbon pricing mechanisms globally
- **IMF Climate Policy Assessment Tool data**: Policy impact estimates
- **IPCC AR6 WGIII**: Mitigation policy effectiveness evidence (open access chapters)

---

## The 5 Stages: Detailed Prompt Templates

### Stage 1 — Policy Parsing & Scope Identification

**Purpose:** Extract structured information from the user's natural language policy description.
**K2 reasoning_effort:** `low`
**Input context:** User's policy text + target country profile from RAG
**Expected latency:** ~3-5 seconds

```
SYSTEM PROMPT:
You are a climate policy analyst. Your task is to parse a proposed climate
policy and produce a structured breakdown. Be precise and concise.

Analyze the following policy proposal and extract:
1. POLICY_TYPE: What mechanism is being proposed? (carbon tax, cap-and-trade,
   regulation, subsidy, ban, mandate, etc.)
2. SECTORS_AFFECTED: Which economic sectors does this directly affect?
   (energy, transport, industry, buildings, agriculture, waste, land use)
3. GEOGRAPHIC_SCOPE: Country/region this applies to
4. TIMELINE: When does it take effect? What are the milestones?
5. QUANTITATIVE_PARAMETERS: Any specific numbers (tax rate, emission cap,
   reduction target, subsidy amount)
6. MECHANISM_DETAILS: How does enforcement/implementation work?
7. STATED_GOALS: What is the policy trying to achieve?

COUNTRY CONTEXT:
{country_profile_from_rag}

POLICY PROPOSAL:
{user_input}

Respond ONLY in this JSON format:
{
  "policy_type": "...",
  "sectors_affected": ["...", "..."],
  "geographic_scope": "...",
  "timeline": {"start": "...", "milestones": [...]},
  "quantitative_parameters": {"...": "..."},
  "mechanism_details": "...",
  "stated_goals": ["...", "..."],
  "ambiguities": ["anything unclear or unspecified in the proposal"]
}
```

### Stage 2 — Direct Impact Analysis

**Purpose:** Trace first-order causal effects of the policy on each affected sector.
**K2 reasoning_effort:** `high`
**Input context:** Stage 1 output + emission factors + sector-specific data from RAG
**Expected latency:** ~15-25 seconds

```
SYSTEM PROMPT:
You are a climate economics researcher performing first-order impact analysis
of a climate policy. For each affected sector, trace the DIRECT causal chain
from policy mechanism to measurable outcome.

CRITICAL INSTRUCTIONS:
- Show your reasoning step-by-step for EACH causal link
- Cite specific numbers where possible (emission factors, costs, capacities)
- Each causal chain should be 3-5 steps from policy input to measurable output
- Quantify where possible, acknowledge uncertainty where you cannot
- Do NOT consider second-order or cross-sector effects yet — only direct impacts

POLICY STRUCTURE (from Stage 1):
{stage_1_output}

REFERENCE DATA:
- Emission factors: {relevant_emission_factors}
- Sector data: {sector_data_from_rag}
- Current energy mix: {energy_mix}
- Current emissions breakdown: {emissions_data}

For EACH affected sector, produce a causal chain in this format:

{
  "sector": "...",
  "causal_chain": [
    {
      "step": 1,
      "cause": "Policy mechanism X is applied",
      "effect": "Y changes by Z amount",
      "reasoning": "Because [detailed reasoning with cited data]...",
      "quantitative_estimate": "±X% or ±Y tonnes CO2e",
      "data_source": "what data supports this estimate",
      "confidence": "high|medium|low"
    },
    ...
  ],
  "net_direct_impact": {
    "emissions_change": "...",
    "cost_impact": "...",
    "timeline": "..."
  }
}

Produce one causal chain per affected sector.
```

### Stage 3 — Second-Order Cascade & Cross-Sector Effects

**Purpose:** Identify feedback loops, spillovers, unintended consequences, and cross-sector interactions.
**K2 reasoning_effort:** `high`
**Input context:** Stage 1 + Stage 2 outputs + broader economic/social context
**Expected latency:** ~15-25 seconds

```
SYSTEM PROMPT:
You are a systems thinking expert analyzing second-order and cross-sector
effects of a climate policy. You have already identified the direct impacts.
Now trace the CASCADING effects — how direct impacts in one sector trigger
changes in other sectors, create feedback loops, or produce unintended
consequences.

CRITICAL INSTRUCTIONS:
- Focus on connections BETWEEN sectors (e.g., energy costs → water →
  agriculture → food prices)
- Identify feedback loops (reinforcing or balancing)
- Flag potential unintended consequences
- Consider behavioral responses (how do firms/consumers adapt?)
- Consider trade and competitiveness effects (carbon leakage, CBAM)
- Consider equity and distributional effects (who bears the cost?)
- Each cascade should be 2-4 additional steps beyond the direct impact

POLICY STRUCTURE:
{stage_1_output}

DIRECT IMPACTS (from Stage 2):
{stage_2_output}

BROADER CONTEXT:
- Trade relationships: {trade_data}
- Social indicators: {social_data}
- Regional policy landscape: {regional_context}

Produce your analysis in this format:

{
  "cross_sector_cascades": [
    {
      "trigger_sector": "energy",
      "affected_sector": "water",
      "cascade_chain": [
        {
          "step": 1,
          "from": "Energy price increase of X%",
          "to": "Desalination cost increase of Y%",
          "reasoning": "Because [detailed reasoning]...",
          "quantitative_estimate": "...",
          "confidence": "high|medium|low"
        },
        ...
      ]
    }
  ],
  "feedback_loops": [
    {
      "type": "reinforcing|balancing",
      "description": "...",
      "sectors_involved": ["...", "..."],
      "reasoning": "..."
    }
  ],
  "unintended_consequences": [
    {
      "description": "...",
      "mechanism": "...",
      "severity": "high|medium|low",
      "mitigation": "..."
    }
  ],
  "equity_effects": {
    "who_bears_cost": "...",
    "distributional_analysis": "...",
    "vulnerable_groups": ["..."]
  }
}
```

### Stage 4 — Contradiction Detection & Confidence Assessment

**Purpose:** Validate the full analysis chain, find internal contradictions, assign confidence levels.
**K2 reasoning_effort:** `medium`
**Input context:** Stages 1-3 outputs (summarized to fit context)
**Expected latency:** ~8-12 seconds

```
SYSTEM PROMPT:
You are a critical reviewer and quality assessor. You have a complete climate
policy impact analysis (direct impacts + cascading effects). Your job is to:

1. Find INTERNAL CONTRADICTIONS — places where different parts of the
   analysis make conflicting assumptions or reach incompatible conclusions
2. Assess the CONFIDENCE LEVEL of each major finding using IPCC-style language
3. Identify KEY UNCERTAINTIES — what assumptions drive the results most?
4. Flag any claims that seem UNSUPPORTED or where reasoning gaps exist

IPCC Confidence Scale:
- Very high: Multiple independent lines of evidence, strong agreement
- High: Robust evidence, general agreement
- Medium: Some evidence, partial agreement
- Low: Limited evidence or significant disagreement
- Very low: Speculative, minimal evidence

FULL ANALYSIS TO REVIEW:
Policy: {stage_1_output}
Direct Impacts: {stage_2_output}
Cascading Effects: {stage_3_output}

Produce your assessment in this format:

{
  "contradictions": [
    {
      "finding_a": "...",
      "finding_b": "...",
      "nature_of_conflict": "...",
      "resolution_or_note": "..."
    }
  ],
  "confidence_assessments": [
    {
      "finding": "short description of the finding",
      "confidence": "very_high|high|medium|low|very_low",
      "justification": "why this confidence level",
      "key_assumption": "what assumption, if wrong, would change this"
    }
  ],
  "key_uncertainties": [
    {
      "uncertainty": "...",
      "impact_if_different": "how would results change",
      "reducibility": "can this uncertainty be reduced with more data?"
    }
  ],
  "unsupported_claims": [
    {
      "claim": "...",
      "issue": "why it seems unsupported",
      "suggestion": "what evidence would strengthen it"
    }
  ],
  "overall_assessment_quality": "high|medium|low",
  "quality_note": "..."
}
```

### Stage 5 — Synthesis & Policy Recommendations

**Purpose:** Produce the final executive summary with actionable recommendations.
**K2 reasoning_effort:** `medium`
**Input context:** Stages 1-4 outputs (structured summaries)
**Expected latency:** ~8-12 seconds

```
SYSTEM PROMPT:
You are a senior climate policy advisor producing an executive briefing.
Synthesize the full analysis into a clear, actionable summary for a
policymaker. Be direct, specific, and honest about limitations.

ANALYSIS INPUTS:
Policy: {stage_1_output}
Direct Impacts: {stage_2_summary}
Cascading Effects: {stage_3_summary}
Quality Assessment: {stage_4_output}

Produce your synthesis in this format:

{
  "executive_summary": "2-3 sentence overview of the policy's likely impact",
  "headline_findings": [
    {
      "finding": "clear statement",
      "confidence": "IPCC level from Stage 4",
      "implication": "what this means for the policymaker"
    }
  ],
  "net_impact_estimate": {
    "emissions": "expected change in CO2e",
    "economic": "GDP/cost impact range",
    "social": "key social effects",
    "timeline": "when effects materialize"
  },
  "complementary_policies_needed": [
    {
      "policy": "what additional policy is needed",
      "reason": "why — what gap or unintended consequence does it address",
      "urgency": "high|medium|low"
    }
  ],
  "comparison_to_alternatives": "how does this compare to other approaches",
  "bottom_line": "1 sentence — should the policymaker proceed, modify, or reconsider?"
}
```

---

## K2 Think V2 API Client

```python
# k2_client.py — Wrapper for K2 Think V2 API (OpenAI-compatible)

from openai import AsyncOpenAI
import json
import os

class K2Client:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=os.getenv("K2_API_BASE_URL"),  # e.g., Cerebras endpoint
            api_key=os.getenv("K2_API_KEY"),
        )
        self.model = os.getenv("K2_MODEL_NAME", "k2-think-v2")

    async def reason(
        self,
        system_prompt: str,
        user_message: str,
        reasoning_effort: str = "high",  # low | medium | high
        temperature: float = 0.6,
        max_tokens: int = 8192,
    ) -> dict:
        """
        Make a single K2 Think V2 reasoning call.
        Returns both the reasoning trace and the final answer.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            # NOTE: reasoning_effort may be passed differently depending
            # on the exact API spec. Check K2 docs. Options:
            # Option A: as an extra body parameter
            extra_body={"reasoning_effort": reasoning_effort},
            # Option B: some APIs use this in the model name or headers
        )

        content = response.choices[0].message.content

        # Try to extract JSON from the response
        try:
            # K2 may wrap JSON in markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            parsed = json.loads(json_str)
            return {
                "success": True,
                "data": parsed,
                "raw_response": content,
                "reasoning_trace": content,  # Full response includes CoT
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                }
            }
        except (json.JSONDecodeError, IndexError):
            return {
                "success": False,
                "data": None,
                "raw_response": content,
                "error": "Failed to parse JSON from K2 response"
            }
```

---

## Pipeline Orchestrator

```python
# pipeline/orchestrator.py

import asyncio
from typing import AsyncGenerator
from .stages import (
    stage_1_parse_policy,
    stage_2_direct_impacts,
    stage_3_cascade_effects,
    stage_4_validate,
    stage_5_synthesize,
)

async def run_pipeline(
    policy_text: str,
    country: str = "UAE",
) -> AsyncGenerator[dict, None]:
    """
    Runs the 5-stage reasoning pipeline, yielding results
    after each stage for real-time streaming to the frontend.
    """

    # Stage 1: Parse
    yield {"stage": 1, "status": "running", "label": "Parsing policy scope..."}
    s1_result = await stage_1_parse_policy(policy_text, country)
    yield {
        "stage": 1,
        "status": "complete",
        "label": "Policy scope identified",
        "data": s1_result["data"],
        "reasoning": s1_result.get("reasoning_trace", ""),
    }

    # Stage 2: Direct impacts
    yield {"stage": 2, "status": "running", "label": "Analyzing direct impacts..."}
    s2_result = await stage_2_direct_impacts(s1_result["data"], country)
    yield {
        "stage": 2,
        "status": "complete",
        "label": "Direct impacts mapped",
        "data": s2_result["data"],
        "reasoning": s2_result.get("reasoning_trace", ""),
        "graph_nodes": extract_graph_nodes(s2_result["data"]),  # For D3
    }

    # Stage 3: Cascade
    yield {"stage": 3, "status": "running", "label": "Tracing cascading effects..."}
    s3_result = await stage_3_cascade_effects(
        s1_result["data"], s2_result["data"], country
    )
    yield {
        "stage": 3,
        "status": "complete",
        "label": "Cross-sector cascades identified",
        "data": s3_result["data"],
        "reasoning": s3_result.get("reasoning_trace", ""),
        "graph_edges": extract_graph_edges(s3_result["data"]),  # For D3
    }

    # Stage 4: Validate
    yield {"stage": 4, "status": "running", "label": "Assessing confidence levels..."}
    s4_result = await stage_4_validate(
        s1_result["data"], s2_result["data"], s3_result["data"]
    )
    yield {
        "stage": 4,
        "status": "complete",
        "label": "Confidence scores assigned",
        "data": s4_result["data"],
        "reasoning": s4_result.get("reasoning_trace", ""),
    }

    # Stage 5: Synthesize
    yield {"stage": 5, "status": "running", "label": "Generating synthesis..."}
    s5_result = await stage_5_synthesize(
        s1_result["data"], s2_result["data"],
        s3_result["data"], s4_result["data"]
    )
    yield {
        "stage": 5,
        "status": "complete",
        "label": "Analysis complete",
        "data": s5_result["data"],
        "reasoning": s5_result.get("reasoning_trace", ""),
    }


def extract_graph_nodes(stage_2_data: dict) -> list:
    """Convert Stage 2 output into D3-compatible nodes."""
    nodes = []
    if not stage_2_data:
        return nodes
    for sector_analysis in stage_2_data:
        for step in sector_analysis.get("causal_chain", []):
            nodes.append({
                "id": f"s2-{sector_analysis['sector']}-{step['step']}",
                "label": step["effect"][:80],
                "sector": sector_analysis["sector"],
                "confidence": step.get("confidence", "medium"),
                "type": "direct_impact",
            })
    return nodes


def extract_graph_edges(stage_3_data: dict) -> list:
    """Convert Stage 3 output into D3-compatible edges."""
    edges = []
    if not stage_3_data:
        return edges
    for cascade in stage_3_data.get("cross_sector_cascades", []):
        for i, step in enumerate(cascade.get("cascade_chain", [])):
            edges.append({
                "source": step["from"][:60],
                "target": step["to"][:60],
                "label": f"causes",
                "confidence": step.get("confidence", "medium"),
                "type": "cascade",
            })
    return edges
```

---

## FastAPI SSE Endpoint

```python
# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from pipeline.orchestrator import run_pipeline

app = FastAPI(title="ClimateReason API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PolicyRequest(BaseModel):
    policy_text: str
    country: str = "UAE"


@app.post("/api/analyze")
async def analyze_policy(request: PolicyRequest):
    """
    SSE endpoint that streams pipeline results stage-by-stage.
    Each stage result is sent as a Server-Sent Event.
    """
    async def event_stream():
        async for stage_result in run_pipeline(
            policy_text=request.policy_text,
            country=request.country,
        ):
            data = json.dumps(stage_result)
            yield f"data: {data}\n\n"
        yield f"data: {json.dumps({'stage': 'done', 'status': 'complete'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/example-policies")
async def example_policies():
    """Pre-loaded example policies for the demo."""
    return [
        {
            "title": "UAE Carbon Tax",
            "country": "UAE",
            "text": "The UAE implements a $75 per tonne carbon tax on all industrial emissions starting January 2029, with revenue earmarked for renewable energy investment and a just transition fund for affected workers.",
        },
        {
            "title": "EU CBAM Expansion",
            "country": "EU",
            "text": "The European Union expands its Carbon Border Adjustment Mechanism to cover all manufactured goods by 2030, requiring importers to purchase certificates matching the embedded carbon at the EU ETS price.",
        },
        {
            "title": "Global Methane Pledge Enforcement",
            "country": "Global",
            "text": "A binding international agreement requires all signatory nations to reduce methane emissions by 30% below 2020 levels by 2030, with mandatory monitoring, reporting, and verification, and trade penalties for non-compliance.",
        },
        {
            "title": "UAE Coal-to-Solar Mandate",
            "country": "UAE",
            "text": "Abu Dhabi mandates that all new industrial facilities must source 80% of electricity from solar by 2030, with existing facilities required to reach 50% by 2032. A green financing facility provides low-interest loans for compliance.",
        },
    ]
```

---

## Frontend Key Component: SSE Hook

```javascript
// frontend/src/hooks/useSSE.js

import { useState, useCallback } from 'react';

export function usePipelineSSE() {
  const [stages, setStages] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });

  const analyze = useCallback(async (policyText, country = 'UAE') => {
    setStages([]);
    setIsRunning(true);
    setGraphData({ nodes: [], edges: [] });

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ policy_text: policyText, country }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.stage === 'done') {
              setIsRunning(false);
              continue;
            }

            // Update stages
            setStages(prev => {
              const existing = prev.findIndex(s => s.stage === data.stage);
              if (existing >= 0) {
                const updated = [...prev];
                updated[existing] = data;
                return updated;
              }
              return [...prev, data];
            });

            // Update graph data
            if (data.graph_nodes) {
              setGraphData(prev => ({
                ...prev,
                nodes: [...prev.nodes, ...data.graph_nodes],
              }));
            }
            if (data.graph_edges) {
              setGraphData(prev => ({
                ...prev,
                edges: [...prev.edges, ...data.graph_edges],
              }));
            }
          }
        }
      }
    } catch (error) {
      console.error('Pipeline error:', error);
      setIsRunning(false);
    }
  }, []);

  return { stages, isRunning, graphData, analyze };
}
```

---

## Sample Reference Data Structure

```json
// data/country_profiles.json (excerpt for UAE)
{
  "UAE": {
    "name": "United Arab Emirates",
    "population_2024": 10200000,
    "gdp_2024_usd_bn": 509,
    "emissions": {
      "total_co2e_mt": 210,
      "per_capita_tonnes": 21.8,
      "by_sector": {
        "energy_industries": "38%",
        "manufacturing_construction": "15%",
        "transport": "20%",
        "buildings": "12%",
        "waste": "5%",
        "agriculture": "2%",
        "other": "8%"
      }
    },
    "energy_mix_2024": {
      "natural_gas": "61%",
      "oil": "1%",
      "nuclear": "19%",
      "solar": "14%",
      "other_renewables": "5%"
    },
    "climate_targets": {
      "ndc_target": "31% reduction below BAU by 2030",
      "net_zero_target": "2050",
      "key_policies": [
        "UAE Energy Strategy 2050",
        "UAE Net Zero 2050",
        "Barakah Nuclear (5.6 GW)",
        "Mohammed bin Rashid Solar Park (5 GW target)"
      ]
    },
    "water": {
      "desalination_share": "42% of water supply",
      "daily_production_mgd": 490,
      "energy_cost_share": "50% of water production cost"
    },
    "trade": {
      "oil_exports_pct_gdp": "30%",
      "food_imports_pct": "90%",
      "key_export_partners": ["India", "Japan", "China", "South Korea"],
      "key_import_partners": ["China", "India", "US", "Germany"]
    }
  }
}
```

---

## Claude Code Prompt — Copy This to Start Building

Below is the exact prompt to give Claude Code in your terminal. It contains everything
needed to scaffold the full project, install dependencies, and set up the basic structure.
You would then iterate from there, filling in the prompts and components.

---

### PROMPT FOR CLAUDE CODE:

```
I'm building a Climate Policy Impact Simulator for the MBZUAI "Build with K2 Think V2"
hackathon showcase. The project is called "ClimateReason" — users describe a climate
policy in plain text, and K2 Think V2 (a 70B open reasoning model) analyzes its impact
through a 5-stage reasoning pipeline, with results streaming to the frontend in real time.

Please scaffold the full project with this architecture:

## Tech Stack
- Backend: FastAPI (Python 3.11+), async throughout
- Frontend: React 18 + Vite + Tailwind CSS
- K2 API client: Use the OpenAI Python SDK (openai package) since K2 Think V2 is OpenAI-compatible
- RAG: ChromaDB for reference data (emission factors, country profiles)
- Streaming: Server-Sent Events (SSE) from backend to frontend
- Graph visualization: D3.js force-directed graph for the causal impact chain

## Project Structure
climate-policy-simulator/
├── backend/
│   ├── main.py                    # FastAPI app with SSE /api/analyze endpoint
│   ├── pipeline/
│   │   ├── orchestrator.py        # Async generator that runs 5 stages sequentially,
│   │   │                          # yielding results after each for streaming
│   │   ├── stages.py              # 5 stage functions, each calling K2 with different
│   │   │                          # reasoning_effort levels
│   │   └── prompts.py             # All prompt templates for the 5 stages
│   ├── k2_client.py               # Async wrapper around OpenAI SDK for K2 API
│   │                              # with reasoning_effort parameter support
│   ├── rag/
│   │   ├── store.py               # ChromaDB setup with 3 collections:
│   │   │                          # emission_factors, country_profiles, policy_mechanisms
│   │   └── ingest.py              # Script to seed ChromaDB from JSON files
│   ├── data/
│   │   ├── country_profiles.json  # UAE, EU, US, India, China profiles with:
│   │   │                          # emissions by sector, energy mix, GDP, climate targets,
│   │   │                          # water stats, trade data
│   │   ├── emission_factors.json  # Common emission factors from DEFRA/EPA
│   │   └── policy_templates.json  # Reference data on carbon tax, ETS, regulations etc.
│   ├── models.py                  # Pydantic models for all stage inputs/outputs
│   └── requirements.txt           # fastapi, uvicorn, openai, chromadb, pydantic
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main layout: left panel (input + stages) + right panel (graph)
│   │   ├── components/
│   │   │   ├── PolicyInput.jsx    # Textarea + country selector + "Analyze" button
│   │   │   │                      # Include 4 pre-loaded example policies
│   │   │   ├── StageProgress.jsx  # Vertical timeline showing 5 stages
│   │   │   │                      # Each stage: icon + label + status (waiting/running/complete)
│   │   │   │                      # Running = spinner, Complete = green check + expandable reasoning
│   │   │   ├── CausalGraph.jsx    # D3.js force-directed graph that builds incrementally
│   │   │   │                      # Nodes appear when Stage 2 completes
│   │   │   │                      # Edges animate in when Stage 3 completes
│   │   │   │                      # Confidence colors applied when Stage 4 completes
│   │   │   │                      # Click any node to see its full reasoning chain
│   │   │   ├── ReasoningPanel.jsx # Expandable panel showing K2's step-by-step reasoning
│   │   │   │                      # for any selected graph node or stage
│   │   │   ├── ConfidenceBadge.jsx # Small colored badge: green=high, yellow=medium, red=low
│   │   │   └── SynthesisReport.jsx # Final executive summary card with:
│   │   │                           # headline findings, net impact, recommendations
│   │   └── hooks/
│   │       └── useSSE.js           # Custom hook that consumes the SSE stream,
│   │                               # updates stage states, and builds graph data
│   ├── package.json
│   └── vite.config.js              # Proxy /api to backend on port 8000
├── scripts/
│   └── seed_data.py               # Run once to populate ChromaDB
└── .env.example                    # K2_API_BASE_URL, K2_API_KEY, K2_MODEL_NAME

## The 5-Stage Pipeline
Each stage makes one K2 Think V2 API call with a specific reasoning_effort level:

Stage 1 - Parse Policy (reasoning_effort: low, ~5s)
  Input: user's policy text + country profile from RAG
  Output: structured JSON with policy_type, sectors_affected, timeline, parameters
  Purpose: Extract structured info from natural language

Stage 2 - Direct Impact Analysis (reasoning_effort: high, ~20s)
  Input: Stage 1 output + emission factors + sector data from RAG
  Output: per-sector causal chains (3-5 steps each) with quantitative estimates
  Purpose: Trace first-order effects on each affected sector

Stage 3 - Cascade & Cross-Sector Effects (reasoning_effort: high, ~20s)
  Input: Stages 1+2 outputs + trade/social context
  Output: cross-sector cascades, feedback loops, unintended consequences
  Purpose: How impacts in one sector ripple to others

Stage 4 - Validate & Score Confidence (reasoning_effort: medium, ~10s)
  Input: Stages 1-3 outputs
  Output: contradictions found, IPCC-style confidence levels, key uncertainties
  Purpose: Quality check the reasoning, assign confidence

Stage 5 - Synthesize & Recommend (reasoning_effort: medium, ~10s)
  Input: Stages 1-4 outputs (summarized)
  Output: executive summary, headline findings, complementary policies needed
  Purpose: Produce actionable policymaker briefing

## Key Implementation Details

1. K2 Client: The K2 Think V2 API is OpenAI-compatible. Use AsyncOpenAI from the
   openai package. The reasoning_effort parameter should be passed via extra_body.
   The model may return JSON wrapped in markdown code blocks — handle both cases.

2. SSE Streaming: The /api/analyze POST endpoint returns a StreamingResponse with
   media_type="text/event-stream". Each stage yields a JSON event with:
   {stage: number, status: "running"|"complete", label: string, data: object,
    reasoning: string, graph_nodes?: array, graph_edges?: array}

3. Causal Graph: Use D3 force-directed layout. Nodes are color-coded by sector
   (energy=blue, water=cyan, agriculture=green, transport=orange, industry=gray).
   Edge thickness indicates confidence. The graph should animate — nodes fly in
   when Stage 2 completes, edges draw when Stage 3 completes, colors update when
   Stage 4 assigns confidence.

4. Example policies to pre-load (for demo):
   - "UAE implements $75/tonne carbon tax on industrial emissions by 2029"
   - "EU expands CBAM to all manufactured goods by 2030"
   - "Global binding methane reduction of 30% by 2030"
   - "Abu Dhabi mandates 80% solar for new industrial facilities by 2030"

5. Country profiles: Start with UAE (most detailed), EU, US, India, China.
   UAE should include water-energy nexus data since it's critical for their context.

6. Design: Clean, professional, dark theme. The feel should be like a command center
   for policy analysis — not playful, not generic SaaS. Think Bloomberg Terminal
   meets climate science. Header: "ClimateReason" with subtitle "Powered by K2 Think V2".

Please create the full project structure, install all dependencies, write the core
backend (main.py, orchestrator, stages, k2_client, prompts), the frontend with all
components, seed data, and make sure I can run it with:
  cd backend && uvicorn main:app --reload
  cd frontend && npm run dev

Start by setting up the project structure and all dependencies, then implement
each file. Make the prompt templates detailed and effective — they're the most
important part of the whole system.
```

---

## Implementation Sequence (2-Week Plan)

### Week 1: Core Pipeline + Basic UI
| Day | Task |
|-----|------|
| 1-2 | Project scaffold, dependencies, K2 client, test API connection |
| 3-4 | All 5 prompt templates written and tested individually via CLI script |
| 5-6 | Pipeline orchestrator + SSE endpoint working end-to-end |
| 7   | Basic React frontend: input form + stage progress timeline |

### Week 2: Visualization + Polish + Demo
| Day | Task |
|-----|------|
| 8-9 | D3.js causal graph with animated node/edge additions |
| 10  | Reasoning panel (click any node → see K2's step-by-step reasoning) |
| 11  | Confidence badges, synthesis report card, example policies |
| 12  | Seed complete UAE data, test with all 4 example policies |
| 13  | Polish UI, fix edge cases, optimize prompts based on testing |
| 14  | Record 2-3 minute demo video |

### Demo Video Script (2:30)
0:00 — "Current tools tell you a carbon tax reduces temperature by 0.3°C. ClimateReason tells you WHY — every step of the reasoning, transparent and auditable."
0:15 — Type in: "UAE implements $75/tonne carbon tax on industrial emissions by 2029"
0:25 — Stage 1 completes: "Policy scope identified — industrial + energy sectors"
0:35 — Stage 2 builds: First causal chain nodes appear on graph
0:55 — Stage 3 cascades: Cross-sector links animate (energy→water→agriculture)
1:15 — Stage 4 validates: Confidence badges appear on each node
1:30 — Stage 5 synthesizes: Executive summary card drops in
1:45 — Click a graph node → show the full K2 reasoning chain
2:00 — "Built on K2 Think V2. Every reasoning step visible. Every conclusion auditable."
2:15 — Show the reasoning_effort toggle (quick scan vs. deep analysis)
2:30 — End card: "ClimateReason — See the reasoning behind every climate policy impact"
