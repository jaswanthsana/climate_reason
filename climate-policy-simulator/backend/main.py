"""
ClimateReason FastAPI backend.

Endpoints:
  POST /api/analyze  — streams SSE events for the 5-stage pipeline
  GET  /api/health   — liveness check
  GET  /api/examples — returns example policy texts for the UI
"""
from __future__ import annotations

import logging
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import settings
from models import AnalyzeRequest
from pipeline.orchestrator import run_pipeline

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ClimateReason API",
    description="Climate Policy Impact Simulator powered by K2 Think V2",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Example policies ──────────────────────────────────────────────────────────
EXAMPLE_POLICIES = [
    {
        "id": "uae-carbon-tax",
        "title": "UAE Carbon Tax",
        "country": "UAE",
        "text": "UAE implements a $75/tonne carbon tax on industrial emissions starting January 2027, "
                "covering oil & gas, petrochemicals, cement, and aluminium sectors. "
                "Revenue to be recycled into a clean energy transition fund. "
                "SMEs below 25,000 tCO2e/yr are exempt. Tax rises 5% annually to 2035.",
    },
    {
        "id": "eu-cbam-expansion",
        "title": "EU CBAM Expansion",
        "country": "EU",
        "text": "The EU expands its Carbon Border Adjustment Mechanism (CBAM) to cover all manufactured "
                "goods — extending beyond the current steel, cement, aluminium, fertilisers, and "
                "electricity scope to include chemicals, plastics, vehicles, and electronics — by 2030. "
                "Importers must purchase CBAM certificates matching the EU ETS carbon price. "
                "Least Developed Countries receive a 5-year phase-in exemption.",
    },
    {
        "id": "global-methane-pledge",
        "title": "Global Methane Reduction",
        "country": "Global",
        "text": "A binding international protocol mandates a 30% reduction in anthropogenic methane "
                "emissions from 2020 baseline levels by 2030, covering oil & gas (venting, flaring, leaks), "
                "coal mining, agriculture (enteric fermentation, rice paddies), and waste (landfills). "
                "Signatories include G20 nations representing 80% of global methane emissions. "
                "Non-compliance triggers trade measures.",
    },
    {
        "id": "abu-dhabi-solar-mandate",
        "title": "Abu Dhabi Solar Mandate",
        "country": "UAE",
        "text": "Abu Dhabi mandates that 80% of energy consumption in new industrial facilities "
                "must be sourced from on-site or contracted solar power by 2030, with the remaining 20% "
                "allowed from the grid (which must itself achieve 60% renewable by 2030 under ADWEA targets). "
                "Existing facilities must retrofit to 50% solar by 2035. "
                "ADNOC, EGA, and EMAL are the primary affected entities. "
                "Masdar provides concessional solar project financing at 3.5% for qualifying facilities.",
    },
]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "model": settings.k2_model_name}


@app.get("/api/examples")
async def examples():
    return {"examples": EXAMPLE_POLICIES}


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    if not request.policy_text.strip():
        raise HTTPException(status_code=400, detail="policy_text is required")

    logger.info("Analysis request | country=%s | len=%d", request.country, len(request.policy_text))

    return StreamingResponse(
        run_pipeline(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering
        },
    )
