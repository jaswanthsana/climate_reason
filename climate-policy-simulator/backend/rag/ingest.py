"""
Ingest all JSON data files into ChromaDB collections.
Run once (or re-run to refresh) before starting the server.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Allow running from anywhere
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.store import rag_store

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # Country profiles
    cp_file = DATA_DIR / "country_profiles.json"
    if cp_file.exists():
        profiles = json.loads(cp_file.read_text())
        rag_store.ingest_country_profiles(profiles)
    else:
        logger.error("Missing: %s", cp_file)

    # Emission factors
    ef_file = DATA_DIR / "emission_factors.json"
    if ef_file.exists():
        factors = json.loads(ef_file.read_text())
        rag_store.ingest_emission_factors(factors)
    else:
        logger.error("Missing: %s", ef_file)

    # Policy templates
    pt_file = DATA_DIR / "policy_templates.json"
    if pt_file.exists():
        mechanisms = json.loads(pt_file.read_text())
        rag_store.ingest_policy_mechanisms(mechanisms)
    else:
        logger.error("Missing: %s", pt_file)

    logger.info("RAG ingestion complete.")


if __name__ == "__main__":
    main()
