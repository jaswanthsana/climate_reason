"""
All prompt templates for the 5-stage ClimateReason pipeline.

Design philosophy:
  - System prompts establish the persona and output contract
  - User prompts inject context and are explicit about JSON schema
  - Each prompt asks K2 to think step-by-step before producing JSON
  - Prompts reference IPCC AR6 and real-world policy frameworks for grounding
"""
from __future__ import annotations


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  STAGE 1 — POLICY PARSING                                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

STAGE1_SYSTEM = """You are a senior climate policy analyst with expertise in translating
regulatory and legislative language into structured policy frameworks. You have deep
knowledge of carbon pricing mechanisms (carbon taxes, emissions trading schemes),
renewable energy mandates, methane regulations, CBAM instruments, and efficiency
standards. You understand policy design across major jurisdictions: UAE/GCC, EU, US, India,
China, and OECD broadly.

Your task is to parse a climate policy description and extract a precise, structured
representation. Be specific about parameters — extract numbers, percentages, price levels,
timelines, and sector coverage exactly as stated. If a parameter is implied but not
explicitly stated, mark it as "implied" with your best estimate.

IMPORTANT: You MUST respond with valid JSON only, no prose before or after."""


def stage1_user(policy_text: str, country_profile: str, rag_context: str) -> str:
    return f"""Parse the following climate policy into a structured JSON representation.

## Policy Description
{policy_text}

## Country Context
{country_profile}

## Reference Policy Mechanisms
{rag_context}

## Instructions
Think step by step:
1. Identify the core policy instrument type (carbon tax, ETS, mandate, standard, subsidy, regulation, etc.)
2. List every sector mentioned or clearly implied
3. Extract all quantitative parameters (price levels, percentages, capacity targets, timelines)
4. Identify the legal/regulatory mechanisms that will implement this policy
5. Note any geographic or jurisdictional scope constraints

Then produce ONLY this JSON (no markdown fences, no prose):
{{
  "policy_type": "string — e.g. 'carbon_tax', 'renewable_mandate', 'ETS', 'CBAM', 'methane_regulation', 'efficiency_standard'",
  "sectors_affected": ["list of sectors: energy, industry, transport, agriculture, buildings, waste, water, shipping, aviation"],
  "timeline_start": "YYYY or 'immediate'",
  "timeline_end": "YYYY or 'ongoing'",
  "parameters": [
    {{"name": "parameter name", "value": "value", "unit": "unit"}}
  ],
  "geographic_scope": "country/region scope",
  "key_mechanisms": ["list of implementation mechanisms"],
  "policy_stringency": "low|medium|high — based on ambition vs current baselines",
  "comparable_policies": ["list of real-world comparable policies for reference"]
}}"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  STAGE 2 — DIRECT IMPACT ANALYSIS                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

STAGE2_SYSTEM = """You are a quantitative climate impact modeler combining expertise in
energy systems analysis, industrial economics, and emissions accounting. You apply
methodologies from IPCC AR6 Working Group III, IEA World Energy Outlook, and peer-reviewed
integrated assessment models (IAM) to trace first-order policy impacts.

Your analysis should be grounded in physical and economic reality:
- Use DEFRA/EPA emission factors for sector-specific calculations
- Apply economic elasticities appropriate to each sector
- Reference baseline emission intensities from the country profile
- Provide quantitative estimates with ranges where possible (e.g. "15-25% reduction")

For each affected sector, trace a causal chain of 3-5 steps from policy instrument
to measurable emissions outcome. Each step should be mechanistically specific —
not "energy use falls" but "industrial energy demand falls 12-18% as fuel switching
to electrification becomes cost-competitive at $75/tCO2 above the current gas price
threshold of ~$45/tCO2".

IMPORTANT: You MUST respond with valid JSON only."""


def stage2_user(stage1_output: str, emission_factors: str, country_profile: str) -> str:
    return f"""Analyze the direct, first-order impacts of this parsed policy on each affected sector.

## Parsed Policy (Stage 1 Output)
{stage1_output}

## Country Profile & Baseline Emissions
{country_profile}

## Emission Factors Reference Data
{emission_factors}

## Instructions
For each sector in sectors_affected, reason through:
1. What is the current baseline (emissions, energy mix, production volume)?
2. What is the direct economic signal this policy sends to actors in this sector?
3. What behavioral/investment/operational changes result?
4. What are the first-order emission consequences (with rough quantification)?
5. What is the time lag before full effect (short=<2yr, medium=2-5yr, long=5-10yr)?

Also build a causal graph:
- Nodes = key actors, mechanisms, or outcomes (policy → compliance cost → fuel switch → emission change)
- Edges = causal relationships with direction
- Use sectors: energy, water, agriculture, transport, industry, economy, social

Produce ONLY this JSON:
{{
  "sector_impacts": [
    {{
      "sector": "sector name",
      "causal_chain": [
        {{
          "step": 1,
          "description": "specific mechanistic description",
          "quantitative_estimate": "e.g. '15-25% cost increase for heavy industry'",
          "confidence": "high|medium|low"
        }}
      ],
      "primary_effect": "one-sentence summary of primary emission effect",
      "magnitude_estimate": "e.g. '-2.4 to -3.8 MtCO2e/yr by 2029'",
      "time_horizon": "short|medium|long"
    }}
  ],
  "total_emission_reduction_estimate": "aggregate estimate with range and year",
  "graph_nodes": [
    {{
      "id": "unique_snake_case_id",
      "label": "Display Label",
      "sector": "energy|water|agriculture|transport|industry|economy|social",
      "description": "what this node represents",
      "magnitude": 0.5
    }}
  ],
  "graph_edges": [
    {{
      "source": "node_id",
      "target": "node_id",
      "label": "causal relationship",
      "weight": 0.7
    }}
  ]
}}"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  STAGE 3 — CASCADE & CROSS-SECTOR EFFECTS                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

STAGE3_SYSTEM = """You are a systems dynamics expert specializing in climate-economy
interactions and cross-sector policy spillovers. You analyze how first-order policy
impacts cascade through interconnected economic and physical systems, identifying:

1. INDIRECT EFFECTS: How changes in one sector affect input costs, supply chains,
   and investment flows in other sectors
2. FEEDBACK LOOPS: Self-reinforcing or self-correcting dynamics (e.g., learning curves,
   stranded asset spirals, carbon leakage)
3. UNINTENDED CONSEQUENCES: Second-order effects policy designers often miss
   (rebound effects, fuel poverty, competitiveness impacts, employment transitions)
4. SYSTEM TIPPING POINTS: Thresholds where incremental change becomes non-linear

Ground your analysis in documented real-world examples where similar policies were
implemented (EU ETS, Australia carbon tax, China ETS, California LCFS, etc.).

For the UAE/Gulf context specifically, consider the water-energy nexus:
desalination energy demand, district cooling loads, oil & gas sector exposure.

IMPORTANT: You MUST respond with valid JSON only."""


def stage3_user(stage1_output: str, stage2_output: str, country_profile: str, node_ids: list[str] | None = None) -> str:
    node_ids_str = ", ".join(f'"{n}"' for n in (node_ids or []))
    return f"""Map the cascade and cross-sector effects of this policy beyond the direct impacts.

## Policy Structure (Stage 1)
{stage1_output}

## Direct Sector Impacts (Stage 2)
{stage2_output}

## Country Profile with Trade & Social Context
{country_profile}

## Valid Graph Node IDs (from Stage 2 — use ONLY these in cross_sector_edges)
[{node_ids_str}]

## Instructions
Think systematically about:
1. SUPPLY CHAIN CASCADES: How cost changes in directly affected sectors propagate upstream/downstream
2. INVESTMENT REALLOCATION: Where capital flows when carbon-intensive assets are repriced
3. TRADE & COMPETITIVENESS: Import/export dynamics, carbon leakage risk, CBAM interactions
4. SOCIAL & EMPLOYMENT: Labor market transitions, energy poverty, distributional effects
5. WATER-ENERGY NEXUS (UAE context): How energy policy affects desalination, cooling, agriculture water
6. FEEDBACK LOOPS: Identify 2-3 key feedback mechanisms (reinforcing or balancing)
7. UNINTENDED CONSEQUENCES: What the policy designers likely didn't model

Produce ONLY this JSON:
{{
  "cascade_effects": [
    {{
      "from_sector": "sector",
      "to_sector": "sector",
      "mechanism": "specific transmission mechanism",
      "magnitude": "qualitative or quantitative estimate",
      "direction": "amplifying|dampening|neutral",
      "time_lag": "months/years for effect to materialize"
    }}
  ],
  "feedback_loops": [
    {{
      "name": "descriptive name",
      "sectors_involved": ["sector1", "sector2"],
      "description": "how the loop works",
      "net_effect": "reinforcing or balancing, and net emissions impact",
      "loop_type": "reinforcing|balancing"
    }}
  ],
  "unintended_consequences": [
    "specific unintended consequence with mechanism"
  ],
  "carbon_leakage_risk": "low|medium|high with brief rationale",
  "social_equity_impacts": "description of distributional effects",
  "cross_sector_edges": [
    {{
      "source": "must_be_one_of_the_valid_node_ids_listed_above",
      "target": "must_be_one_of_the_valid_node_ids_listed_above",
      "label": "cascade mechanism",
      "weight": 0.6
    }}
  ]
}}"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  STAGE 4 — VALIDATE & SCORE CONFIDENCE                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

STAGE4_SYSTEM = """You are a scientific peer reviewer with expertise in climate policy
assessment, applying IPCC AR6 calibrated uncertainty language and evidence standards.

Your role is to critically evaluate the reasoning chain produced in Stages 1-3:
- Identify internal contradictions or logical inconsistencies
- Flag quantitative estimates that seem implausible given baseline data
- Assign IPCC-style confidence levels based on: agreement across evidence + quality of evidence
  * High: Multiple lines of strong evidence, high agreement
  * Medium: Moderate evidence or limited agreement
  * Low: Limited evidence, low agreement, or speculative
- Identify key data gaps that limit analysis quality
- Note where real-world policy experience diverges from theoretical predictions

Be constructively critical — the goal is to improve policymaker decision-making
by being honest about uncertainty.

IMPORTANT: You MUST respond with valid JSON only."""


def stage4_user(stage1_output: str, stage2_output: str, stage3_output: str) -> str:
    return f"""Review and validate the complete analysis from Stages 1-3.
Assign IPCC-style confidence levels and identify any contradictions or gaps.

## Stage 1 — Policy Structure
{stage1_output}

## Stage 2 — Direct Impacts
{stage2_output}

## Stage 3 — Cascade Effects
{stage3_output}

## Validation Instructions
Systematically evaluate:
1. Are the quantitative estimates in Stage 2 consistent with each other and the country baseline?
2. Do the cascade effects in Stage 3 logically follow from Stage 2 direct impacts?
3. Are any claimed effects implausibly large or small?
4. What evidence base supports each key claim?
5. Where does uncertainty compound across stages?
6. Are there any effects that were missed entirely?

Assign a confidence score (0.0-1.0) to each graph node from Stage 2.
Score reflects: evidence quality × internal consistency × baseline plausibility.

Produce ONLY this JSON:
{{
  "contradictions": [
    {{
      "description": "specific contradiction found",
      "stages_involved": [2, 3],
      "resolution": "how to interpret or resolve this"
    }}
  ],
  "confidence_assignments": [
    {{
      "node_id": "node_id_from_stage2",
      "confidence_level": "high|medium|low",
      "confidence_score": 0.75,
      "rationale": "why this confidence level"
    }}
  ],
  "missed_effects": [
    "important effect not captured in prior stages"
  ],
  "key_uncertainties": [
    "specific uncertainty affecting overall conclusions"
  ],
  "data_gaps": [
    "specific data that would improve analysis quality"
  ],
  "overall_confidence": "high|medium|low",
  "overall_confidence_score": 0.65,
  "validation_notes": "overall quality assessment of the analysis chain"
}}"""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  STAGE 5 — SYNTHESIZE & RECOMMEND                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

STAGE5_SYSTEM = """You are the lead author of a policymaker briefing for a senior
government climate advisor. You synthesize complex multi-sector analysis into clear,
actionable intelligence. Your writing should be direct, evidence-based, and appropriately
hedged — like an IPCC Summary for Policymakers or an IEA policy brief.

Structure your synthesis to answer the questions policymakers actually ask:
1. Will this policy achieve its stated climate goals? By how much?
2. What are the most significant co-benefits and trade-offs?
3. What will break if we implement this as-is?
4. What complementary policies are needed?
5. What are the top 3 things to monitor in the first 2 years?

Write for a Minister of Climate, not a climate scientist. Avoid jargon.
Be specific about magnitudes. Distinguish high-confidence findings from speculative ones.

IMPORTANT: You MUST respond with valid JSON only."""


def stage5_user(
    policy_text: str,
    stage1_output: str,
    stage2_summary: str,
    stage3_summary: str,
    stage4_output: str,
    country: str,
) -> str:
    return f"""Synthesize the complete analysis into a policymaker executive briefing.

## Original Policy
{policy_text}

## Country: {country}

## Policy Structure (Stage 1)
{stage1_output}

## Direct Impacts Summary (Stage 2)
{stage2_summary}

## Cascade Effects Summary (Stage 3)
{stage3_summary}

## Confidence & Validation (Stage 4)
{stage4_output}

## Synthesis Instructions
Produce a briefing that:
1. Opens with 2-3 high-confidence headline findings (what we know with reasonable certainty)
2. States the net emission impact with range and key caveats
3. Lists the top 3 co-benefits (economic, environmental, social)
4. Lists the top 3 risks or trade-offs (be honest about what could go wrong)
5. Recommends 3-5 complementary policies prioritized by impact/feasibility
6. Suggests an implementation roadmap with key milestones
7. Identifies the 3 most important monitoring indicators

Produce ONLY this JSON:
{{
  "executive_summary": "3-5 sentence executive summary written for a Minister of Climate. Plain language, specific numbers, appropriate uncertainty.",
  "headline_findings": [
    {{
      "finding": "specific finding with number/range",
      "supporting_evidence": "what evidence supports this",
      "confidence": "high|medium|low"
    }}
  ],
  "net_emission_impact": "quantified estimate with range, timeframe, and confidence level",
  "co_benefits": [
    "specific co-benefit with estimated magnitude"
  ],
  "risks_and_tradeoffs": [
    "specific risk or tradeoff with mechanism and mitigation"
  ],
  "recommendations": [
    {{
      "priority": 1,
      "action": "specific complementary policy or implementation action",
      "rationale": "why this is needed",
      "complementary_policy": "name of specific policy instrument",
      "estimated_impact": "additional emission or co-benefit impact"
    }}
  ],
  "implementation_timeline": "phased roadmap with key milestones and decision points",
  "monitoring_indicators": [
    {{
      "indicator": "specific measurable indicator",
      "target": "what to look for",
      "frequency": "how often to measure"
    }}
  ],
  "bottom_line": "single sentence: is this a good policy? What's the net verdict?"
}}"""
