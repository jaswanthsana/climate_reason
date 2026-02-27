# Phase 1: Claude Code Prompt
# Copy everything below this line into Claude Code

---

I have an existing ClimateReason project (Climate Policy Impact Simulator) with
a FastAPI backend and React frontend. The 5-stage K2 Think V2 reasoning pipeline
is scaffolded but uses hardcoded static data for only ~5 countries.

Phase 1 goal: Make the data layer production-ready so the system works well for
ANY country and ANY climate policy, not just pre-loaded examples.

There are 3 tasks in this phase. Do them in order.

---

## TASK 1: Expand the Curated Data Layer

### 1a) Create the OWID CO2 dataset ingestion

Our World in Data publishes a comprehensive CO2 and energy dataset covering 200+
countries. Download and process it.

Create `backend/data/fetch_owid.py`:
```python
"""
One-time script to download and process the OWID CO2 dataset.
Source: https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv

Run this once: python backend/data/fetch_owid.py
It creates backend/data/owid_processed.json with per-country summaries.
"""
```

This script should:
1. Download owid-co2-data.csv from the GitHub URL above
2. For each country, extract the MOST RECENT year of data available, getting:
   - co2 (annual CO2 emissions in million tonnes)
   - co2_per_capita
   - share_global_co2
   - coal_co2, oil_co2, gas_co2, cement_co2, flaring_co2 (breakdown by source)
   - energy_per_capita
   - energy_per_gdp
   - share_electricity_coal, share_electricity_oil, share_electricity_gas,
     share_electricity_nuclear, share_electricity_renewables (if these columns exist, 
     otherwise derive from primary_energy_consumption and sub-components)
   - gdp, population
   - methane, nitrous_oxide (if available)
3. Also extract the 5-year trend (latest year vs 5 years ago) for co2 and co2_per_capita
4. Save as backend/data/owid_processed.json with structure:
```json
{
  "United Arab Emirates": {
    "iso_code": "ARE",
    "latest_year": 2023,
    "co2_mt": 190.5,
    "co2_per_capita": 18.6,
    "share_global_co2": 0.5,
    "co2_by_source": {
      "coal": 2.1, "oil": 45.3, "gas": 138.7, "cement": 3.8, "flaring": 0.6
    },
    "energy_mix": {
      "coal_pct": null, "oil_pct": null, "gas_pct": 61, 
      "nuclear_pct": 19, "renewables_pct": 14
    },
    "gdp_usd": 509000000000,
    "population": 10200000,
    "trend_5yr": {
      "co2_change_pct": "+5.2%",
      "per_capita_change_pct": "-1.3%"
    }
  },
  ...
}
```
Note: Not all fields will be available for all countries. Use null for missing values.
The script should handle missing data gracefully and log which countries have
incomplete data.

### 1b) Create the Policy Precedents dataset

Create `backend/data/policy_precedents.json` with 30 real-world climate policy
examples. Each entry should have documented, factual outcomes.

Structure per entry:
```json
{
  "id": "bc-carbon-tax",
  "name": "British Columbia Carbon Tax",
  "country": "Canada (British Columbia)",
  "year_implemented": 2008,
  "policy_type": "carbon_tax",
  "mechanism": "Revenue-neutral carbon tax starting at CAD$10/tonne, rising to CAD$50/tonne by 2018, then CAD$65 by 2023",
  "sectors_covered": ["energy", "transport", "industry", "buildings"],
  "documented_outcomes": {
    "emissions_impact": "5-15% reduction in fuel consumption relative to rest of Canada",
    "economic_impact": "GDP growth slightly outperformed Canadian average",
    "revenue_handling": "Revenue-neutral: offset by income and corporate tax cuts",
    "public_response": "Initially controversial, gained broad support over time",
    "key_lessons": ["Revenue neutrality was critical for public acceptance", "Gradual price increase allowed economic adjustment", "Border adjustments not needed within Canada"]
  },
  "relevance_tags": ["carbon_tax", "revenue_neutral", "developed_economy", "fossil_fuel_dependent"]
}
```

Include these 30 precedents (I'll provide the key details, flesh out with accurate data):

Carbon Tax examples:
1. British Columbia carbon tax (2008) - revenue neutral, 5-15% reduction
2. Sweden carbon tax (1991) - highest globally at ~$140/tonne, 27% emission reduction with GDP growth
3. Finland carbon tax (1990) - first in the world, modest impact due to low initial rate
4. France carbon tax attempt (2018) - Yellow Vest protests, social equity failure lesson
5. South Africa carbon tax (2019) - first in Africa, low initial rate with phase-in
6. Singapore carbon tax (2019) - first in Southeast Asia, city-state context
7. Colombia carbon tax (2016) - developing country implementation
8. Chile carbon tax (2017) - power plant focused

Emissions Trading (ETS/Cap-and-Trade):
9. EU ETS Phase I-IV (2005-present) - largest system, price evolution, over-allocation lessons
10. California cap-and-trade (2013) - linked with Quebec, revenue recycling to disadvantaged communities
11. China national ETS (2021) - world's largest by coverage, power sector only initially
12. South Korea ETS (2015) - Asian context, manufacturing economy challenges
13. RGGI (US Northeast, 2009) - regional approach, investment of auction proceeds
14. New Zealand ETS (2008) - agriculture inclusion attempts, price volatility

Regulations and Mandates:
15. UK Climate Change Act (2008) - legally binding carbon budgets, coal phase-out by 2024
16. Germany Energiewende (2010) - renewable mandate, nuclear phase-out, mixed results
17. India PAT scheme (2012) - energy efficiency trading for industrial plants
18. Denmark wind energy mandate (1990s-2000s) - from 0% to 50%+ wind power
19. China coal cap policies (2013) - air quality driven, massive coal reduction in cities
20. EU CO2 standards for cars (2009-present) - drove EV adoption

Subsidies and Incentives:
21. US Inflation Reduction Act (2022) - $370bn clean energy subsidies, manufacturing reshoring
22. Germany feed-in tariff (2000) - launched global solar industry, cost concerns
23. India solar auction system (2010s) - drove world's cheapest solar prices
24. Morocco Noor solar complex - developing country renewable mega-project
25. Costa Rica PES program (1997) - payment for ecosystem services, reforestation success

Fossil Fuel Policies:
26. Australia carbon tax (2012-2014) - implemented then repealed, political lessons
27. Indonesia fossil fuel subsidy reform (2015) - politically difficult, partial success
28. Iran fuel subsidy reform (2010) - cash transfers to offset, inflation challenges
29. Nigeria fuel subsidy removal (2023) - fiscal relief but social unrest

Cross-Cutting:
30. UAE Net Zero 2050 + Barakah nuclear (2017-present) - oil producer transition, nuclear + solar

For each one, make sure the documented_outcomes are factually accurate and include
the actual emission/economic results where documented. This is reference data that
K2 will cite, so accuracy matters.

### 1c) Expand Emission Factors

Create `backend/data/emission_factors_comprehensive.json`:

```json
{
  "stationary_combustion": {
    "natural_gas": {"factor": 56.1, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "coal_bituminous": {"factor": 94.6, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "coal_sub_bituminous": {"factor": 96.1, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "coal_lignite": {"factor": 101.0, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "crude_oil": {"factor": 73.3, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "diesel": {"factor": 74.1, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "gasoline": {"factor": 69.3, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "lpg": {"factor": 63.1, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "kerosene": {"factor": 71.5, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "fuel_oil": {"factor": 77.4, "unit": "kgCO2/GJ", "source": "IPCC 2006"},
    "wood_biomass": {"factor": 112.0, "unit": "kgCO2/GJ", "source": "IPCC 2006", "note": "Considered carbon-neutral under biogenic accounting"}
  },
  "electricity_grids": {
    "description": "Grid emission factors in kgCO2/kWh for major countries. These are loaded from OWID data at runtime where available.",
    "fallback_estimates": {
      "coal_dominated": {"factor": 0.9, "unit": "kgCO2/kWh", "examples": "Poland, India, South Africa"},
      "gas_dominated": {"factor": 0.45, "unit": "kgCO2/kWh", "examples": "UAE, Qatar, USA (average)"},
      "mixed": {"factor": 0.35, "unit": "kgCO2/kWh", "examples": "UK, Germany, Japan"},
      "low_carbon": {"factor": 0.05, "unit": "kgCO2/kWh", "examples": "France, Sweden, Norway"}
    }
  },
  "transport": {
    "passenger_car_gasoline": {"factor": 0.192, "unit": "kgCO2/km", "source": "DEFRA 2024"},
    "passenger_car_diesel": {"factor": 0.171, "unit": "kgCO2/km", "source": "DEFRA 2024"},
    "passenger_car_ev": {"factor": 0.0, "unit": "kgCO2/km direct", "note": "Indirect = grid factor × 0.2 kWh/km"},
    "bus": {"factor": 0.089, "unit": "kgCO2/passenger-km", "source": "DEFRA 2024"},
    "domestic_flight": {"factor": 0.246, "unit": "kgCO2/passenger-km", "source": "DEFRA 2024"},
    "long_haul_flight": {"factor": 0.148, "unit": "kgCO2/passenger-km", "source": "DEFRA 2024"},
    "freight_truck": {"factor": 0.107, "unit": "kgCO2/tonne-km", "source": "DEFRA 2024"},
    "freight_rail": {"factor": 0.028, "unit": "kgCO2/tonne-km", "source": "DEFRA 2024"},
    "freight_ship": {"factor": 0.016, "unit": "kgCO2/tonne-km", "source": "DEFRA 2024"}
  },
  "industrial_processes": {
    "cement_production": {"factor": 0.6, "unit": "tCO2/tonne cement", "source": "IPCC 2006", "note": "Process emissions only, excludes fuel combustion"},
    "steel_blast_furnace": {"factor": 1.8, "unit": "tCO2/tonne steel", "source": "World Steel Association"},
    "steel_electric_arc": {"factor": 0.4, "unit": "tCO2/tonne steel", "source": "World Steel Association"},
    "aluminum_smelting": {"factor": 8.0, "unit": "tCO2/tonne aluminum", "source": "IAI", "note": "Including electricity for electrolysis"},
    "ammonia_production": {"factor": 1.6, "unit": "tCO2/tonne ammonia", "source": "IEA"},
    "ethylene_production": {"factor": 1.0, "unit": "tCO2/tonne ethylene", "source": "IEA"}
  },
  "land_use": {
    "deforestation_tropical": {"factor": 450, "unit": "tCO2/hectare", "source": "IPCC 2006", "note": "One-time release"},
    "reforestation_tropical": {"factor": -11, "unit": "tCO2/hectare/year", "source": "IPCC 2006", "note": "Sequestration rate"},
    "reforestation_temperate": {"factor": -5, "unit": "tCO2/hectare/year", "source": "IPCC 2006"},
    "peatland_drainage": {"factor": 25, "unit": "tCO2/hectare/year", "source": "IPCC Wetlands Supplement"},
    "peatland_restoration": {"factor": -2.5, "unit": "tCO2/hectare/year", "source": "IPCC Wetlands Supplement"}
  },
  "agriculture": {
    "rice_paddy": {"factor": 1.3, "unit": "tCH4/hectare/year", "source": "IPCC 2006"},
    "enteric_fermentation_cattle": {"factor": 70, "unit": "kgCH4/head/year", "source": "IPCC 2006"},
    "manure_management_cattle": {"factor": 2, "unit": "kgCH4/head/year", "source": "IPCC 2006"},
    "synthetic_fertilizer": {"factor": 0.01, "unit": "tN2O-N/tN applied", "source": "IPCC 2006"}
  },
  "gwp_100yr": {
    "co2": 1,
    "ch4": 28,
    "n2o": 265,
    "sf6": 23500,
    "source": "IPCC AR5"
  }
}
```

### 1d) Update the RAG store to handle all three data types

Modify `backend/rag/store.py` to have these collections:
- `country_data` — loaded from owid_processed.json (200+ countries)
- `policy_precedents` — loaded from policy_precedents.json (30 entries)
- `emission_factors` — loaded from emission_factors_comprehensive.json

Modify `backend/rag/ingest.py` to load all three sources.
Each country document should be tagged with ISO code and searchable by country name.
Each precedent should be tagged with policy_type and searchable by mechanism + sector.

---

## TASK 2: Build the Dynamic Data Fetcher

Create `backend/data_fetcher.py`:

```python
"""
Dynamic data fetcher for countries not covered by curated OWID data.
Uses World Bank API as primary source.
Includes caching to avoid repeated API calls.
"""
import httpx
import json
import os
from datetime import datetime, timedelta
from typing import Optional

CACHE_FILE = "backend/data/api_cache.json"
CACHE_TTL_HOURS = 24

WORLD_BANK_INDICATORS = {
    "co2_kt": "EN.ATM.CO2E.KT",
    "co2_per_capita": "EN.ATM.CO2E.PC",
    "electricity_per_capita": "EG.USE.ELEC.KH.PC",
    "renewable_pct": "EG.FEC.RNEW.ZS",
    "gdp_usd": "NY.GDP.MKTP.CD",
    "population": "SP.POP.TOTL",
    "forest_area_pct": "AG.LND.FRST.ZS",
    "energy_use_per_capita": "EG.USE.PCAP.KG.OE",
}

# Map common country names to ISO2 codes for the World Bank API
COUNTRY_NAME_TO_ISO2 = {
    "united states": "US", "usa": "US", "us": "US",
    "united kingdom": "GB", "uk": "GB",
    "united arab emirates": "AE", "uae": "AE",
    "china": "CN", "india": "IN", "brazil": "BR",
    "germany": "DE", "france": "FR", "japan": "JP",
    "canada": "CA", "australia": "AU", "russia": "RU",
    "south korea": "KR", "indonesia": "ID", "mexico": "MX",
    "saudi arabia": "SA", "south africa": "ZA", "nigeria": "NG",
    "egypt": "EG", "turkey": "TR", "italy": "IT", "spain": "ES",
    "poland": "PL", "netherlands": "NL", "sweden": "SE",
    "norway": "NO", "denmark": "DK", "finland": "FI",
    "switzerland": "CH", "austria": "AT", "belgium": "BE",
    "thailand": "TH", "vietnam": "VN", "pakistan": "PK",
    "bangladesh": "BD", "philippines": "PH", "malaysia": "MY",
    "colombia": "CO", "chile": "CL", "argentina": "AR",
    "peru": "PE", "kenya": "KE", "ethiopia": "ET",
    "ghana": "GH", "morocco": "MA", "qatar": "QA",
    "kuwait": "KW", "bahrain": "BH", "oman": "OM",
    "new zealand": "NZ", "singapore": "SG", "ireland": "IE",
    "portugal": "PT", "czech republic": "CZ", "romania": "RO",
    "ukraine": "UA", "costa rica": "CR", "uruguay": "UY",
    "european union": "EU", "eu": "EU",
    # Add more as needed
}
```

The fetcher should:
1. Accept a country name (flexible — "UAE", "United Arab Emirates", "uae" all work)
2. Resolve it to an ISO2 code using the mapping above
3. Check the cache first. If data exists and is less than 24 hours old, return cached.
4. If not cached, query World Bank API for each indicator:
   `https://api.worldbank.org/v2/country/{iso2}/indicator/{indicator}?format=json&per_page=5&date=2018:2023`
5. Extract the most recent non-null value for each indicator
6. Cache the result
7. Return structured data similar to the OWID format
8. Use httpx with a 5-second timeout. If the API fails, return None (don't crash).

Also create the main data retrieval function that the pipeline stages will call:

```python
async def get_country_context(country: str) -> dict:
    """
    Main function called by pipeline stages.
    Returns country data from the best available source.
    
    Returns:
    {
        "source": "curated" | "api" | "parametric",
        "confidence": "high" | "medium" | "low",
        "country_name": "United Arab Emirates",
        "data": { ... } or None,
        "available_fields": ["co2_mt", "gdp", ...],
        "missing_fields": ["energy_mix_detailed", ...],
        "data_year": 2023
    }
    """
    # Step 1: Check curated OWID data
    owid_data = load_owid_country(country)
    if owid_data:
        return {
            "source": "curated",
            "confidence": "high",
            "country_name": owid_data.get("country", country),
            "data": owid_data,
            "available_fields": [k for k, v in owid_data.items() if v is not None],
            "missing_fields": [k for k, v in owid_data.items() if v is None],
            "data_year": owid_data.get("latest_year", "unknown")
        }
    
    # Step 2: Try World Bank API
    api_data = await fetch_from_world_bank(country)
    if api_data:
        return {
            "source": "api",
            "confidence": "medium",
            "country_name": country,
            "data": api_data,
            "available_fields": [k for k, v in api_data.items() if v is not None],
            "missing_fields": [k for k, v in api_data.items() if v is None],
            "data_year": api_data.get("latest_year", "unknown")
        }
    
    # Step 3: Fall back to parametric knowledge
    return {
        "source": "parametric",
        "confidence": "low",
        "country_name": country,
        "data": None,
        "available_fields": [],
        "missing_fields": ["all"],
        "data_year": None
    }
```

---

## TASK 3: Update All Pipeline Stage Prompts

This is the most important task. Every stage prompt needs to become data-aware
and self-aware about confidence.

### Update `backend/pipeline/prompts.py`

For EVERY stage prompt, add this block at the top of the user message
(dynamically filled by the stage function):

```
=== DATA CONTEXT ===
Country: {country_name}
Data source: {source} ({confidence} confidence)
Data year: {data_year}

Available verified data:
{formatted_data_points}

Data NOT available (model should use general knowledge with reduced confidence):
{missing_fields_list}

IMPORTANT INSTRUCTIONS ON DATA USAGE:
- When citing VERIFIED data above, use exact numbers and cite the source
- When using your own knowledge for missing data, prefix with "Based on general knowledge:"
  and reduce your confidence by one level for any claim depending on this
- Never present uncertain estimates as precise facts
- If a critical data point is missing, explicitly note what data would improve the analysis
===
```

### Stage 1 prompt updates:
- Add the data context block above
- No other changes needed — Stage 1 is about parsing, not data-intensive

### Stage 2 prompt updates (most important):
- Add the data context block
- Add a POLICY PRECEDENTS section:
```
=== RELEVANT POLICY PRECEDENTS ===
The following real-world policies are similar to the one being analyzed.
Reference them where relevant to ground your impact estimates in empirical evidence.

{formatted_precedents}

When citing a precedent, specify the country, year, and documented outcome.
Use precedents to calibrate your quantitative estimates — e.g., "BC's carbon tax
at $50/tonne achieved 5-15% emission reduction, suggesting this $75/tonne tax
could achieve proportionally greater reductions, adjusted for differences in
economic structure."
===
```
- Update the emission factors section to use the comprehensive factors

### Stage 3 prompt updates:
- Add the data context block
- Add a section on trade relationships (from OWID data if available):
```
=== TRADE AND REGIONAL CONTEXT ===
{country trade data if available}
If not available: "Trade data not available. Use general knowledge about
{country}'s major trading partners and economic relationships.
Flag trade-dependent findings as MEDIUM confidence."
===
```

### Stage 4 prompt updates:
- Add the data context block
- Add an explicit instruction:
```
ADDITIONAL VALIDATION: DATA SOURCE CHECK
For each major finding in the analysis, verify:
1. Does this claim rely on VERIFIED data or GENERAL KNOWLEDGE?
2. If general knowledge: is this the kind of fact the model would reliably know?
   - A major country's primary energy source → likely reliable
   - An exact percentage to one decimal place → likely unreliable without data
   - Whether a specific recent policy exists → could be outdated
3. Adjust confidence levels accordingly:
   - Claims backed by verified data: maintain original confidence
   - Claims backed by reliable general knowledge: cap at MEDIUM
   - Claims backed by uncertain general knowledge: cap at LOW
```

### Stage 5 prompt updates:
- Add the data context block
- Add a DATA PROVENANCE section to the output format:
```json
{
  "executive_summary": "...",
  "headline_findings": [...],
  "data_provenance": {
    "primary_data_source": "curated/api/parametric",
    "data_confidence": "high/medium/low",
    "verified_data_points_used": ["CO2 emissions: 190 Mt (OWID 2023)", ...],
    "general_knowledge_used_for": ["detailed sector breakdown", ...],
    "data_gaps_that_would_improve_analysis": ["grid emission factor by fuel type", ...]
  },
  ...
}
```

### Update `backend/pipeline/stages.py`

Each stage function needs to be updated to:

1. Call `get_country_context(country)` to get the best available data
2. Call `get_relevant_precedents(policy_type, sectors)` for Stage 2
3. Call `get_emission_factors(sectors)` for Stage 2
4. Format the data context block and inject it into the prompt template
5. Pass the data source/confidence info through to the frontend (so the UI can show it)

The stage result yielded to the orchestrator should include:
```python
{
    "stage": 2,
    "status": "complete",
    "data": s2_result["data"],
    "reasoning": s2_result["reasoning_trace"],
    "data_context": {
        "source": country_context["source"],
        "confidence": country_context["confidence"],
        "data_year": country_context["data_year"],
    },
    "precedents_used": [p["name"] for p in precedents],
    "graph_nodes": extract_graph_nodes(s2_result["data"]),
}
```

---

## After completing all 3 tasks:

1. Run the OWID download script: `python backend/data/fetch_owid.py`
2. Run the ingestion script to load all data into ChromaDB: `python backend/rag/ingest.py`
3. Test the data fetcher with a few countries:
   ```python
   # Quick test
   import asyncio
   from backend.data_fetcher import get_country_context
   
   async def test():
       # Should return "curated" with high confidence
       uae = await get_country_context("UAE")
       print(f"UAE: {uae['source']} ({uae['confidence']})")
       
       # Should return "curated" (OWID covers most countries)
       brazil = await get_country_context("Brazil")
       print(f"Brazil: {brazil['source']} ({brazil['confidence']})")
       
       # Smaller country - might need API fallback
       bhutan = await get_country_context("Bhutan")
       print(f"Bhutan: {bhutan['source']} ({bhutan['confidence']})")
   
   asyncio.run(test())
   ```
4. Test the full pipeline with a non-UAE policy to verify generalization:
   ```
   Policy: "India mandates 50% renewable energy by 2030 for all grid-connected power"
   Country: "India"
   ```

Make sure error handling is solid — if OWID download fails, if World Bank API
is down, if ChromaDB is empty — the system should still work using K2's
parametric knowledge with appropriate confidence flags.
