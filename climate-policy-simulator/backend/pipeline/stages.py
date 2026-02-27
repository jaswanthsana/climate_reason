"""
5-stage pipeline functions. Each stage:
  1. Builds prompts from prior stage outputs + RAG context
  2. Calls K2 via k2_client with the appropriate reasoning_effort
  3. Parses the response into a typed Pydantic model
  4. Returns the model (or raises on failure)
"""
from __future__ import annotations

import json
import logging
from typing import Any

from k2_client import k2
from models import (
    ConfidenceAssignment,
    GraphEdge,
    GraphNode,
    HeadlineFinding,
    MonitoringIndicator,
    PolicyParameter,
    Recommendation,
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
    Stage5Output,
    CausalStep,
    SectorImpact,
    CascadeEffect,
    FeedbackLoop,
    Contradiction,
)
from pipeline.prompts import (
    STAGE1_SYSTEM,
    STAGE2_SYSTEM,
    STAGE3_SYSTEM,
    STAGE4_SYSTEM,
    STAGE5_SYSTEM,
    stage1_user,
    stage2_user,
    stage3_user,
    stage4_user,
    stage5_user,
)

logger = logging.getLogger(__name__)


def _compact(obj: Any) -> str:
    """Compact JSON for prompt injection (saves tokens)."""
    if isinstance(obj, dict):
        return json.dumps(obj, separators=(",", ":"))
    return json.dumps(obj.model_dump(), separators=(",", ":"))


def _summarise_stage2(s2: Stage2Output) -> str:
    """Produce a token-efficient summary of stage 2 for later stages."""
    lines = [f"Total emission estimate: {s2.total_emission_reduction_estimate}"]
    for imp in s2.sector_impacts:
        lines.append(
            f"- {imp.sector}: {imp.primary_effect} | {imp.magnitude_estimate} | {imp.time_horizon}"
        )
    return "\n".join(lines)


def _summarise_stage3(s3: Stage3Output) -> str:
    lines = [f"Carbon leakage risk: {s3.carbon_leakage_risk}"]
    for c in s3.cascade_effects[:6]:  # top 6
        lines.append(f"- {c.from_sector}→{c.to_sector}: {c.mechanism} ({c.direction})")
    for f in s3.feedback_loops:
        lines.append(f"- Loop: {f.name}: {f.net_effect}")
    lines.append("Unintended: " + "; ".join(s3.unintended_consequences[:3]))
    return "\n".join(lines)


# ── Stage 1 ───────────────────────────────────────────────────────────────────

async def run_stage1(
    policy_text: str,
    country_profile: dict[str, Any],
    rag_context: dict[str, Any],
) -> Stage1Output:
    country_str = json.dumps(country_profile, indent=2)
    rag_str = json.dumps(rag_context.get("policy_mechanisms", []), indent=2)

    data, reasoning = await k2.complete_json(
        system_prompt=STAGE1_SYSTEM,
        user_prompt=stage1_user(policy_text, country_str, rag_str),
        reasoning_effort="low",
        temperature=0.2,
        max_tokens=2048,
    )

    params = [PolicyParameter(**p) for p in data.get("parameters", [])]

    return Stage1Output(
        policy_type=data.get("policy_type", "unknown"),
        sectors_affected=data.get("sectors_affected", []),
        timeline_start=data.get("timeline_start", "unknown"),
        timeline_end=data.get("timeline_end", "unknown"),
        parameters=params,
        geographic_scope=data.get("geographic_scope", ""),
        key_mechanisms=data.get("key_mechanisms", []),
        raw_reasoning=reasoning,
    )


# ── Stage 2 ───────────────────────────────────────────────────────────────────

async def run_stage2(
    stage1: Stage1Output,
    country_profile: dict[str, Any],
    rag_context: dict[str, Any],
) -> Stage2Output:
    s1_str = _compact(stage1)
    ef_str = json.dumps(rag_context.get("emission_factors", []), indent=2)
    country_str = json.dumps(country_profile, indent=2)

    data, reasoning = await k2.complete_json(
        system_prompt=STAGE2_SYSTEM,
        user_prompt=stage2_user(s1_str, ef_str, country_str),
        reasoning_effort="high",
        temperature=0.3,
        max_tokens=16000,
    )

    sector_impacts = []
    for si in data.get("sector_impacts", []):
        chain = [CausalStep(**step) for step in si.get("causal_chain", [])]
        sector_impacts.append(SectorImpact(
            sector=si["sector"],
            causal_chain=chain,
            primary_effect=si.get("primary_effect", ""),
            magnitude_estimate=si.get("magnitude_estimate", ""),
            time_horizon=si.get("time_horizon", "medium"),
        ))

    nodes = [GraphNode(**n) for n in data.get("graph_nodes", [])]
    edges = [GraphEdge(**e) for e in data.get("graph_edges", [])]

    return Stage2Output(
        sector_impacts=sector_impacts,
        total_emission_reduction_estimate=data.get("total_emission_reduction_estimate", ""),
        graph_nodes=nodes,
        graph_edges=edges,
        raw_reasoning=reasoning,
    )


# ── Stage 3 ───────────────────────────────────────────────────────────────────

async def run_stage3(
    stage1: Stage1Output,
    stage2: Stage2Output,
    country_profile: dict[str, Any],
) -> Stage3Output:
    s1_str = _compact(stage1)
    s2_str = _summarise_stage2(stage2)
    country_str = json.dumps(country_profile, indent=2)
    node_ids = [n.id for n in stage2.graph_nodes]

    data, reasoning = await k2.complete_json(
        system_prompt=STAGE3_SYSTEM,
        user_prompt=stage3_user(s1_str, s2_str, country_str, node_ids),
        reasoning_effort="high",
        temperature=0.3,
        max_tokens=12000,
    )

    cascades = [CascadeEffect(**c) for c in data.get("cascade_effects", [])]
    loops = [FeedbackLoop(**f) for f in data.get("feedback_loops", [])]
    cross_edges = [GraphEdge(**e) for e in data.get("cross_sector_edges", [])]

    return Stage3Output(
        cascade_effects=cascades,
        feedback_loops=loops,
        unintended_consequences=data.get("unintended_consequences", []),
        cross_sector_edges=cross_edges,
        carbon_leakage_risk=data.get("carbon_leakage_risk", "medium"),
        social_equity_impacts=data.get("social_equity_impacts", ""),
        raw_reasoning=reasoning,
    )


# ── Stage 4 ───────────────────────────────────────────────────────────────────

async def run_stage4(
    stage1: Stage1Output,
    stage2: Stage2Output,
    stage3: Stage3Output,
) -> Stage4Output:
    s1_str = _compact(stage1)
    s2_str = _summarise_stage2(stage2)
    s3_str = _summarise_stage3(stage3)

    data, reasoning = await k2.complete_json(
        system_prompt=STAGE4_SYSTEM,
        user_prompt=stage4_user(s1_str, s2_str, s3_str),
        reasoning_effort="medium",
        temperature=0.2,
        max_tokens=12000,
    )

    contradictions = [Contradiction(**c) for c in data.get("contradictions", [])]
    confidence_assignments = [
        ConfidenceAssignment(**ca) for ca in data.get("confidence_assignments", [])
    ]

    return Stage4Output(
        contradictions=contradictions,
        confidence_assignments=confidence_assignments,
        key_uncertainties=data.get("key_uncertainties", []),
        overall_confidence=data.get("overall_confidence", "medium"),
        data_gaps=data.get("data_gaps", []),
        raw_reasoning=reasoning,
    )


# ── Stage 5 ───────────────────────────────────────────────────────────────────

async def run_stage5(
    policy_text: str,
    country: str,
    stage1: Stage1Output,
    stage2: Stage2Output,
    stage3: Stage3Output,
    stage4: Stage4Output,
) -> Stage5Output:
    s1_str = _compact(stage1)
    s2_summary = _summarise_stage2(stage2)
    s3_summary = _summarise_stage3(stage3)
    s4_str = _compact(stage4)

    data, reasoning = await k2.complete_json(
        system_prompt=STAGE5_SYSTEM,
        user_prompt=stage5_user(policy_text, s1_str, s2_summary, s3_summary, s4_str, country),
        reasoning_effort="medium",
        temperature=0.3,
        max_tokens=12000,
    )

    findings = [HeadlineFinding(**f) for f in data.get("headline_findings", [])]
    recs = [Recommendation(**r) for r in data.get("recommendations", [])]
    monitors = [MonitoringIndicator(**m) for m in data.get("monitoring_indicators", [])]

    return Stage5Output(
        executive_summary=data.get("executive_summary", ""),
        headline_findings=findings,
        net_emission_impact=data.get("net_emission_impact", ""),
        co_benefits=data.get("co_benefits", []),
        risks_and_tradeoffs=data.get("risks_and_tradeoffs", []),
        recommendations=recs,
        implementation_timeline=data.get("implementation_timeline", ""),
        monitoring_indicators=monitors,
        bottom_line=data.get("bottom_line", ""),
        raw_reasoning=reasoning,
    )
