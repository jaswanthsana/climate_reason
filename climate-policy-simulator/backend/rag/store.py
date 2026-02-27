"""
ChromaDB RAG store with three collections:
  - country_profiles  : macroeconomic + emissions + energy data per country
  - emission_factors  : sector-specific CO2e factors from DEFRA/EPA
  - policy_mechanisms : reference data on carbon pricing instruments

The store provides simple async wrappers that retrieve relevant context
for injection into K2 prompts.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings as app_settings

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"

# Collection names
COUNTRY_PROFILES_COL = "country_profiles"
EMISSION_FACTORS_COL = "emission_factors"
POLICY_MECHANISMS_COL = "policy_mechanisms"


class RAGStore:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(
            path=app_settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._country_col = self._client.get_or_create_collection(COUNTRY_PROFILES_COL)
        self._ef_col = self._client.get_or_create_collection(EMISSION_FACTORS_COL)
        self._policy_col = self._client.get_or_create_collection(POLICY_MECHANISMS_COL)

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_country_profiles(self, profiles: list[dict[str, Any]]) -> None:
        ids, docs, metas = [], [], []
        for p in profiles:
            cid = p["country_code"]
            ids.append(cid)
            docs.append(
                f"{p['name']} climate profile: {p.get('description', '')} "
                f"Emissions: {json.dumps(p.get('emissions_by_sector', {}))} "
                f"Energy mix: {json.dumps(p.get('energy_mix', {}))} "
                f"Climate targets: {json.dumps(p.get('climate_targets', {}))}"
            )
            metas.append({"country_code": cid, "name": p["name"]})

        self._country_col.upsert(ids=ids, documents=docs, metadatas=metas)
        logger.info("Ingested %d country profiles", len(profiles))

    def ingest_emission_factors(self, factors: list[dict[str, Any]]) -> None:
        ids, docs, metas = [], [], []
        for i, f in enumerate(factors):
            fid = f.get("id", f"ef_{i}")
            ids.append(fid)
            docs.append(
                f"{f['source']} — {f['activity']}: {f['factor']} {f['unit']} "
                f"Sector: {f['sector']}. Notes: {f.get('notes', '')}"
            )
            metas.append({"sector": f["sector"], "source": f["source"]})

        self._ef_col.upsert(ids=ids, documents=docs, metadatas=metas)
        logger.info("Ingested %d emission factors", len(factors))

    def ingest_policy_mechanisms(self, mechanisms: list[dict[str, Any]]) -> None:
        ids, docs, metas = [], [], []
        for m in mechanisms:
            mid = m["id"]
            ids.append(mid)
            docs.append(
                f"{m['name']} ({m['type']}): {m['description']} "
                f"Real-world examples: {', '.join(m.get('examples', []))} "
                f"Typical parameters: {json.dumps(m.get('typical_parameters', {}))}"
            )
            metas.append({"type": m["type"], "name": m["name"]})

        self._policy_col.upsert(ids=ids, documents=docs, metadatas=metas)
        logger.info("Ingested %d policy mechanisms", len(mechanisms))

    # ── Retrieval ─────────────────────────────────────────────────────────────

    async def get_country_profile(self, country: str) -> dict[str, Any]:
        """Return full country profile dict from the JSON data file."""
        data_file = DATA_DIR / "country_profiles.json"
        if not data_file.exists():
            logger.warning("country_profiles.json not found, returning empty profile")
            return {"name": country, "country_code": country}

        profiles = json.loads(data_file.read_text())
        # Try exact match on country_code or name (case-insensitive)
        for p in profiles:
            if (
                p.get("country_code", "").upper() == country.upper()
                or p.get("name", "").lower() == country.lower()
            ):
                return p

        logger.warning("Country '%s' not found in profiles, using first available", country)
        return profiles[0] if profiles else {"name": country}

    async def get_emission_factors(
        self, sectors: list[str], n_results: int = 20
    ) -> list[dict[str, Any]]:
        """Return emission factors relevant to the given sectors."""
        if not sectors:
            # Return all if no filter
            data_file = DATA_DIR / "emission_factors.json"
            if data_file.exists():
                return json.loads(data_file.read_text())
            return []

        query = " ".join(sectors)
        try:
            results = self._ef_col.query(
                query_texts=[query],
                n_results=min(n_results, self._ef_col.count()),
            )
            # Reconstruct dicts from metadata + document
            factors = []
            for doc, meta in zip(
                results["documents"][0], results["metadatas"][0]
            ):
                factors.append({"text": doc, **meta})
            return factors
        except Exception as exc:
            logger.warning("Emission factor query failed: %s", exc)
            data_file = DATA_DIR / "emission_factors.json"
            if data_file.exists():
                return json.loads(data_file.read_text())
            return []

    async def get_policy_mechanisms(
        self, policy_text: str, n_results: int = 5
    ) -> list[dict[str, Any]]:
        """Return policy mechanism reference docs most relevant to the policy text."""
        try:
            count = self._policy_col.count()
            if count == 0:
                raise ValueError("empty collection")
            results = self._policy_col.query(
                query_texts=[policy_text],
                n_results=min(n_results, count),
            )
            mechanisms = []
            for doc, meta in zip(
                results["documents"][0], results["metadatas"][0]
            ):
                mechanisms.append({"text": doc, **meta})
            return mechanisms
        except Exception as exc:
            logger.warning("Policy mechanism query failed: %s", exc)
            data_file = DATA_DIR / "policy_templates.json"
            if data_file.exists():
                return json.loads(data_file.read_text())
            return []


# Singleton
rag_store = RAGStore()
