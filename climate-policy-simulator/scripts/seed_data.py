#!/usr/bin/env python3
"""
One-time script to seed ChromaDB with reference data.
Run from the project root:
  cd climate-policy-simulator && python scripts/seed_data.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from rag.ingest import main

if __name__ == "__main__":
    main()
