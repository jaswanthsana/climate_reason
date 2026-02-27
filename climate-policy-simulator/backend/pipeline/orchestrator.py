"""
Async generator that runs all 5 stages sequentially, yielding an SSEEvent
after each stage starts (status=running) and after it completes (status=complete).

The frontend consumes these events via Server-Sent Events to update the UI
incrementally rather than waiting for the full analysis to complete.
"""
from __future__ import annotations

import json
import logging
from typing import AsyncIterator

from models import (
    AnalyzeRequest,
    GraphEdge,
    GraphNode,
    PipelineState,
    SSEEvent,
)
from pipeline.stages import run_stage1, run_stage2, run_stage3, run_stage4, run_stage5
from rag.store import rag_store

logger = logging.getLogger(__name__)

STAGE_LABELS = {
    1: "Parse Policy",
    2: "Direct Impact Analysis",
    3: "Cascade & Cross-Sector Effects",
    4: "Validate & Score Confidence",
    5: "Synthesize & Recommend",
}


def _event_json(event: SSEEvent) -> str:
    """Serialise SSEEvent to a data: line for SSE."""
    return f"data: {event.model_dump_json()}\n\n"


async def run_pipeline(request: AnalyzeRequest) -> AsyncIterator[str]:
    """
    Yields SSE-formatted strings. Each yield is either a "running" notification
    (stage started) or a "complete" notification (stage done, with full data).
    """
    state = PipelineState(request=request)

    # ── Load RAG context ──────────────────────────────────────────────────────
    try:
        country_profile = await rag_store.get_country_profile(request.country)
        state.country_profile = country_profile

        emission_factors = await rag_store.get_emission_factors(
            sectors=[]  # get all for now
        )
        policy_mechanisms = await rag_store.get_policy_mechanisms(request.policy_text)
        state.rag_context = {
            "emission_factors": emission_factors,
            "policy_mechanisms": policy_mechanisms,
        }
    except Exception as exc:
        logger.warning("RAG load failed, continuing with empty context: %s", exc)
        state.country_profile = {}
        state.rag_context = {}

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 1
    # ══════════════════════════════════════════════════════════════════════════
    yield _event_json(SSEEvent(
        stage=1, status="running", label=STAGE_LABELS[1],
        data={}, reasoning=""
    ))

    try:
        s1 = await run_stage1(
            policy_text=request.policy_text,
            country_profile=state.country_profile,
            rag_context=state.rag_context,
        )
        state.stage1 = s1
        yield _event_json(SSEEvent(
            stage=1, status="complete", label=STAGE_LABELS[1],
            data=s1.model_dump(exclude={"raw_reasoning"}),
            reasoning=s1.raw_reasoning,
        ))
    except Exception as exc:
        logger.error("Stage 1 failed: %s", exc)
        yield _event_json(SSEEvent(
            stage=1, status="error", label=STAGE_LABELS[1],
            data={"error": str(exc)}, reasoning=""
        ))
        return

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 2
    # ══════════════════════════════════════════════════════════════════════════
    yield _event_json(SSEEvent(
        stage=2, status="running", label=STAGE_LABELS[2],
        data={}, reasoning=""
    ))

    try:
        s2 = await run_stage2(
            stage1=state.stage1,
            country_profile=state.country_profile,
            rag_context=state.rag_context,
        )
        state.stage2 = s2
        yield _event_json(SSEEvent(
            stage=2, status="complete", label=STAGE_LABELS[2],
            data=s2.model_dump(exclude={"raw_reasoning"}),
            reasoning=s2.raw_reasoning,
            graph_nodes=s2.graph_nodes,
            graph_edges=s2.graph_edges,
        ))
    except Exception as exc:
        logger.error("Stage 2 failed: %s", exc)
        yield _event_json(SSEEvent(
            stage=2, status="error", label=STAGE_LABELS[2],
            data={"error": str(exc)}, reasoning=""
        ))
        return

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 3
    # ══════════════════════════════════════════════════════════════════════════
    yield _event_json(SSEEvent(
        stage=3, status="running", label=STAGE_LABELS[3],
        data={}, reasoning=""
    ))

    try:
        s3 = await run_stage3(
            stage1=state.stage1,
            stage2=state.stage2,
            country_profile=state.country_profile,
        )
        state.stage3 = s3

        # Merge cross-sector edges into the event
        all_new_edges = s3.cross_sector_edges
        yield _event_json(SSEEvent(
            stage=3, status="complete", label=STAGE_LABELS[3],
            data=s3.model_dump(exclude={"raw_reasoning", "cross_sector_edges"}),
            reasoning=s3.raw_reasoning,
            graph_edges=all_new_edges,
        ))
    except Exception as exc:
        logger.error("Stage 3 failed: %s", exc)
        yield _event_json(SSEEvent(
            stage=3, status="error", label=STAGE_LABELS[3],
            data={"error": str(exc)}, reasoning=""
        ))
        return

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 4
    # ══════════════════════════════════════════════════════════════════════════
    yield _event_json(SSEEvent(
        stage=4, status="running", label=STAGE_LABELS[4],
        data={}, reasoning=""
    ))

    try:
        s4 = await run_stage4(
            stage1=state.stage1,
            stage2=state.stage2,
            stage3=state.stage3,
        )
        state.stage4 = s4

        # Build updated nodes with confidence scores from stage 4
        confidence_map = {
            ca.node_id: ca.confidence_score
            for ca in s4.confidence_assignments
        }
        updated_nodes = []
        for node in state.stage2.graph_nodes:
            updated = node.model_copy(
                update={"confidence": confidence_map.get(node.id, 0.5)}
            )
            updated_nodes.append(updated)

        yield _event_json(SSEEvent(
            stage=4, status="complete", label=STAGE_LABELS[4],
            data=s4.model_dump(exclude={"raw_reasoning"}),
            reasoning=s4.raw_reasoning,
            graph_nodes=updated_nodes,   # nodes now have confidence
        ))
    except Exception as exc:
        logger.error("Stage 4 failed: %s", exc)
        yield _event_json(SSEEvent(
            stage=4, status="error", label=STAGE_LABELS[4],
            data={"error": str(exc)}, reasoning=""
        ))
        return

    # ══════════════════════════════════════════════════════════════════════════
    # STAGE 5
    # ══════════════════════════════════════════════════════════════════════════
    yield _event_json(SSEEvent(
        stage=5, status="running", label=STAGE_LABELS[5],
        data={}, reasoning=""
    ))

    try:
        s5 = await run_stage5(
            policy_text=request.policy_text,
            country=request.country,
            stage1=state.stage1,
            stage2=state.stage2,
            stage3=state.stage3,
            stage4=state.stage4,
        )
        state.stage5 = s5
        yield _event_json(SSEEvent(
            stage=5, status="complete", label=STAGE_LABELS[5],
            data=s5.model_dump(exclude={"raw_reasoning"}),
            reasoning=s5.raw_reasoning,
        ))
    except Exception as exc:
        logger.error("Stage 5 failed: %s", exc)
        yield _event_json(SSEEvent(
            stage=5, status="error", label=STAGE_LABELS[5],
            data={"error": str(exc)}, reasoning=""
        ))
        return

    # Signal pipeline completion
    yield "data: {\"done\": true}\n\n"
