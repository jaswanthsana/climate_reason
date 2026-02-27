from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ── Request / Response shells ────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    policy_text: str = Field(..., min_length=10, max_length=4000)
    country: str = Field(default="UAE")


class SSEEvent(BaseModel):
    stage: int
    status: Literal["running", "complete", "error"]
    label: str
    data: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""
    graph_nodes: list[GraphNode] = Field(default_factory=list)
    graph_edges: list[GraphEdge] = Field(default_factory=list)


# ── Graph primitives ─────────────────────────────────────────────────────────

class GraphNode(BaseModel):
    id: str
    label: str
    sector: str  # energy | water | agriculture | transport | industry | economy | social
    description: str = ""
    confidence: Optional[float] = None   # 0–1, added in stage 4
    magnitude: Optional[float] = None    # relative impact magnitude for node sizing


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""
    weight: float = 0.5   # 0–1, maps to edge thickness
    confidence: Optional[float] = None


# ── Stage 1 output ───────────────────────────────────────────────────────────

class PolicyParameter(BaseModel):
    name: str
    value: str
    unit: str = ""

    @field_validator("value", mode="before")
    @classmethod
    def coerce_value_to_str(cls, v: Any) -> str:
        return str(v)


class Stage1Output(BaseModel):
    policy_type: str
    sectors_affected: list[str]
    timeline_start: str
    timeline_end: str
    parameters: list[PolicyParameter]
    geographic_scope: str
    key_mechanisms: list[str]
    raw_reasoning: str = ""


# ── Stage 2 output ───────────────────────────────────────────────────────────

class CausalStep(BaseModel):
    step: int
    description: str
    quantitative_estimate: str = ""
    confidence: str = "medium"  # high | medium | low


class SectorImpact(BaseModel):
    sector: str
    causal_chain: list[CausalStep]
    primary_effect: str
    magnitude_estimate: str
    time_horizon: str


class Stage2Output(BaseModel):
    sector_impacts: list[SectorImpact]
    total_emission_reduction_estimate: str
    graph_nodes: list[GraphNode]
    graph_edges: list[GraphEdge]
    raw_reasoning: str = ""


# ── Stage 3 output ───────────────────────────────────────────────────────────

class CascadeEffect(BaseModel):
    from_sector: str
    to_sector: str
    mechanism: str
    magnitude: str
    direction: Literal["amplifying", "dampening", "neutral"]

    @field_validator("direction", mode="before")
    @classmethod
    def normalize_direction(cls, v: Any) -> str:
        v = str(v).lower()
        for keyword in ("amplifying", "dampening", "neutral"):
            if keyword in v:
                return keyword
        return "neutral"


class FeedbackLoop(BaseModel):
    name: str
    sectors_involved: list[str]
    description: str
    net_effect: str


class Stage3Output(BaseModel):
    cascade_effects: list[CascadeEffect]
    feedback_loops: list[FeedbackLoop]
    unintended_consequences: list[str]
    cross_sector_edges: list[GraphEdge]
    carbon_leakage_risk: str = "medium"
    social_equity_impacts: str = ""
    raw_reasoning: str = ""


# ── Stage 4 output ───────────────────────────────────────────────────────────

class Contradiction(BaseModel):
    description: str
    stages_involved: list[int]
    resolution: str


class ConfidenceAssignment(BaseModel):
    node_id: str
    confidence_level: Literal["high", "medium", "low"]
    confidence_score: float  # 0–1
    rationale: str

    @field_validator("confidence_level", mode="before")
    @classmethod
    def normalize_confidence_level(cls, v: Any) -> str:
        v = str(v).lower()
        for keyword in ("high", "medium", "low"):
            if keyword in v:
                return keyword
        return "medium"


class Stage4Output(BaseModel):
    contradictions: list[Contradiction]
    confidence_assignments: list[ConfidenceAssignment]
    key_uncertainties: list[str]
    overall_confidence: Literal["high", "medium", "low"]
    overall_confidence_score: float = 0.5
    data_gaps: list[str]
    validation_notes: str = ""
    raw_reasoning: str = ""

    @field_validator("overall_confidence", mode="before")
    @classmethod
    def normalize_overall_confidence(cls, v: Any) -> str:
        v = str(v).lower()
        for keyword in ("high", "medium", "low"):
            if keyword in v:
                return keyword
        return "medium"


# ── Stage 5 output ───────────────────────────────────────────────────────────

class HeadlineFinding(BaseModel):
    finding: str
    supporting_evidence: str
    confidence: Literal["high", "medium", "low"]

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        v = str(v).lower()
        for keyword in ("high", "medium", "low"):
            if keyword in v:
                return keyword
        return "medium"


class Recommendation(BaseModel):
    priority: int  # 1 = highest
    action: str
    rationale: str
    complementary_policy: str = ""
    estimated_impact: str = ""


class MonitoringIndicator(BaseModel):
    indicator: str
    target: str = ""
    frequency: str = ""


class Stage5Output(BaseModel):
    executive_summary: str
    headline_findings: list[HeadlineFinding]
    net_emission_impact: str
    co_benefits: list[str]
    risks_and_tradeoffs: list[str]
    recommendations: list[Recommendation]
    implementation_timeline: str
    monitoring_indicators: list[MonitoringIndicator] = Field(default_factory=list)
    bottom_line: str = ""
    raw_reasoning: str = ""


# ── Aggregate pipeline state ─────────────────────────────────────────────────

class PipelineState(BaseModel):
    request: AnalyzeRequest
    country_profile: dict[str, Any] = Field(default_factory=dict)
    rag_context: dict[str, Any] = Field(default_factory=dict)
    stage1: Optional[Stage1Output] = None
    stage2: Optional[Stage2Output] = None
    stage3: Optional[Stage3Output] = None
    stage4: Optional[Stage4Output] = None
    stage5: Optional[Stage5Output] = None
