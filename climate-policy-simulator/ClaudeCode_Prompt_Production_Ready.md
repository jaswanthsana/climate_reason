# Claude Code Prompt: Evolve ClimateReason to Production-Ready

Paste this into Claude Code to upgrade the existing scaffolded project:

---

We need to evolve the ClimateReason project from a demo with hardcoded data
to a production-ready system that works well for ANY country and ANY climate
policy. Here are the changes needed:

## 1. Replace Static RAG with a Hybrid Knowledge System

The current approach uses static JSON files in ChromaDB for only 5 countries.
We need a 3-tier knowledge system:

### Tier 1: K2's parametric knowledge (always available, no code needed)
- The prompts should be written so K2 can produce useful analysis purely
  from its training knowledge when no external data is available
- Prompts should distinguish between "I have verified data" and "I'm
  reasoning from general knowledge"

### Tier 2: Curated reference data (expand significantly)
Keep ChromaDB but expand the data:

a) Download and index Our World in Data (OWID) CO2 dataset:
   - Source: https://github.com/owid/co2-data (owid-co2-data.csv)
   - This single CSV covers 200+ countries with: CO2 emissions, per capita,
     by fuel type, energy mix, GDP, population — yearly from 1750 to 2023
   - Write an ingest script that loads this CSV, creates per-country documents
     in ChromaDB with the most recent 5 years of data for each country
   - Tag each document with country code, year, and data type

b) Create a policy_precedents collection with ~30 real-world examples:
   - Each entry: policy name, country, year implemented, mechanism type,
     documented outcome (emissions change, GDP impact, public response)
   - Examples to include:
     - British Columbia carbon tax (2008): revenue-neutral, 5-15% reduction
     - EU ETS phases I-IV: price evolution, cap tightening, results
     - Sweden carbon tax (1991): highest in world, 27% reduction with GDP growth
     - UK carbon price floor (2013): coal phase-out accelerated
     - China national ETS (2021): world's largest, coverage and early results
     - India's PAT scheme: energy efficiency trading
     - Costa Rica carbon tax + PES: reforestation success
     - Australia carbon tax (2012-2014): implemented then repealed, lessons
     - California cap-and-trade: results and revenue recycling
     - South Korea ETS: Asian context results
     ... and about 20 more covering different mechanism types and regions

c) Expand emission_factors to be comprehensive:
   - All major fuels (coal types, natural gas, oil products, biofuels)
   - Electricity grid factors for top 50 countries (from IEA/OWID)
   - Industrial process emissions (cement, steel, aluminum, chemicals)
   - Land use change factors (deforestation, reforestation, soil carbon)
   - Transport factors (per km by vehicle type)
   - Source each factor with a citation

### Tier 3: Dynamic data fetching (for countries not in Tier 2)
Create a data_fetcher.py module that can query open APIs at runtime:

a) World Bank Climate Data API:
   - Endpoint: https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json
   - Key indicators:
     - EN.ATM.CO2E.KT (CO2 emissions, kt)
     - EN.ATM.CO2E.PC (CO2 per capita)
     - EG.USE.ELEC.KH.PC (Electric power consumption per capita)
     - EG.FEC.RNEW.ZS (Renewable energy % of consumption)
     - NY.GDP.MKTP.CD (GDP current USD)
     - SP.POP.TOTL (Population)
   - Fetch latest available year, cache results in ChromaDB for reuse

b) Fallback strategy in each pipeline stage:
   ```python
   async def get_country_data(country: str) -> dict:
       # Try Tier 2 first (curated, high confidence)
       curated = await rag_store.get_curated(country)
       if curated:
           return {"source": "curated", "confidence": "high", "data": curated}
       
       # Try Tier 3 (API fetch, medium confidence)  
       try:
           api_data = await data_fetcher.fetch_country(country)
           # Cache for future use
           await rag_store.cache_api_data(country, api_data)
           return {"source": "api", "confidence": "medium", "data": api_data}
       except Exception:
           pass
       
       # Fall back to Tier 1 (K2 parametric knowledge, lower confidence)
       return {"source": "parametric", "confidence": "low", "data": None}
   ```

## 2. Update ALL Prompt Templates for Generalization

Every stage prompt needs these changes:

a) Add a DATA AVAILABILITY section at the top of each prompt:
```
DATA CONTEXT FOR THIS ANALYSIS:
- Country data source: {CURATED (verified) | API-FETCHED (recent) | PARAMETRIC (model knowledge)}
- Data confidence: {HIGH | MEDIUM | LOW}
- Available data points: {list what specific data we have}
- Missing data: {list what we don't have}

INSTRUCTIONS ON DATA USAGE:
- When using CURATED data, cite specific numbers with their source
- When using API-FETCHED data, cite but note the data may have 1-2 year lag
- When using PARAMETRIC knowledge, explicitly state "Based on general knowledge"
  and reduce confidence by one level for any claim relying on this
- When data is missing, state what data would improve the analysis
- NEVER present uncertain estimates as precise facts
```

b) Add a "Similar Policy Precedents" section to Stage 2's prompt:
```
RELEVANT POLICY PRECEDENTS:
{retrieved precedents from the policy_precedents collection}

When analyzing impacts, reference these precedents where relevant.
For example: "British Columbia's $50/tonne carbon tax (2008) resulted in
5-15% emission reduction — suggesting a $75/tonne tax would likely achieve
at least comparable reductions, adjusted for UAE's different energy mix."
```

c) Make Stage 4 (Validation) explicitly check for data-dependent claims:
```
ADDITIONAL VALIDATION TASK:
For each finding, assess whether it depends on:
a) Verified data (high confidence regardless)
b) General knowledge that is likely accurate (medium confidence)
c) Assumptions that could be wrong (low confidence, flag explicitly)

If the analysis used PARAMETRIC knowledge for a specific claim,
check: "Is this the kind of fact K2 would reliably know from training?"
- Country's primary energy source: likely reliable
- Exact emission percentage to one decimal: likely unreliable
- Whether a specific policy exists: could be outdated
```

## 3. Add Document Upload Support

Create a new endpoint and processing pipeline:

a) Backend endpoint:
```python
@app.post("/api/upload-document")
async def upload_document(file: UploadFile):
    """
    Accept PDF or text documents (policy papers, NDCs, reports).
    Extract text and return a document_id for use in analysis.
    """
    # Extract text using pdfplumber (for PDFs) or direct read (for .txt/.md)
    # Store extracted text in a session cache (dict in memory is fine)
    # Return document_id that frontend passes with the analyze request
```

b) Install pdfplumber: `pip install pdfplumber`

c) Modify the analyze endpoint to accept an optional document_id:
```python
class PolicyRequest(BaseModel):
    policy_text: str
    country: str = "UAE"
    document_id: Optional[str] = None  # If provided, inject doc text into context
```

d) When document_id is provided, inject the document text into Stage 1's
   context so K2 can parse the ACTUAL policy language, not just the user's
   summary. Use the first 50K tokens of the document (well within K2's 262K limit).

e) Frontend: Add a file upload area (drag-and-drop) above the text input.
   When a file is uploaded, show the filename with a green badge.
   The text input changes its placeholder to "Describe what you want to
   analyze about this document, or leave blank for full analysis."

## 4. Add Policy Precedent Retrieval

Create a precedent retrieval function that runs between Stage 1 and Stage 2:

```python
async def retrieve_precedents(policy_type: str, sectors: list) -> list:
    """
    After Stage 1 identifies the policy type and sectors,
    retrieve the 3-5 most relevant historical precedents.
    """
    query = f"{policy_type} {' '.join(sectors)} climate policy outcomes"
    results = precedent_collection.query(
        query_texts=[query],
        n_results=5,
    )
    return format_precedents(results)
```

Inject these into Stage 2's prompt as grounding examples. This makes the
analysis much more credible — K2 isn't just reasoning abstractly, it's
referencing what actually happened in similar real-world cases.

## 5. Add PDF Report Export

After the full pipeline completes, offer a "Download Report" button.

a) Install: `pip install fpdf2` or use reportlab

b) Create a report_generator.py that takes all 5 stage outputs and produces
   a clean PDF with:
   - Title: "Climate Policy Impact Analysis"
   - Subtitle: the policy text
   - Date and model attribution ("Powered by K2 Think V2")
   - Executive Summary (from Stage 5)
   - Direct Impacts (from Stage 2) with the causal chains
   - Cascading Effects (from Stage 3)  
   - Confidence Assessment (from Stage 4)
   - Recommendations (from Stage 5)
   - Data Sources section listing what data was used and its provenance
   - A disclaimer about AI-generated analysis

c) Backend endpoint:
```python
@app.post("/api/export-pdf")
async def export_pdf(analysis_data: FullAnalysis):
    pdf_bytes = generate_report(analysis_data)
    return Response(content=pdf_bytes, media_type="application/pdf",
                   headers={"Content-Disposition": "attachment; filename=climate-analysis.pdf"})
```

d) Frontend: Add a "Download PDF Report" button that appears after Stage 5
   completes. It sends all stage data to the export endpoint.

## 6. Improve Frontend for Generalization

a) Replace the country dropdown with a searchable input that accepts any
   country name. Autocomplete from a list of all UN member states.
   Show a badge next to the selected country:
   - Green: "Detailed data available" (Tier 2 countries)
   - Yellow: "Basic data available" (can fetch from APIs)
   - Gray: "Limited data — analysis uses general knowledge"

b) Add a "Data Sources" panel that shows exactly what data was used in
   the analysis and where it came from. This transparency is critical for
   trust and directly addresses the judging criteria.

c) Add a loading skeleton for the causal graph area so it doesn't look
   empty while Stage 1 is running.

d) The example policies should show diverse countries, not just UAE:
   - UAE carbon tax (existing)
   - EU CBAM expansion (existing)
   - Brazil deforestation moratorium
   - India renewable energy mandate
   - US methane regulation for oil and gas
   - Nigeria clean cooking fuel subsidy
   This demonstrates the system works globally.

## 7. Caching Layer

Add a simple caching system so:
- World Bank API responses are cached locally (SQLite or just a JSON file)
  with a 24-hour TTL. Don't re-fetch data we already have.
- OWID data is loaded once at startup and stays in memory.
- Policy precedent matches are cached by policy_type.

This makes the system fast on repeated queries and resilient to API downtime.

## Implementation Order

1. First: Expand the data layer (OWID ingest, policy precedents, emission factors)
2. Second: Update all prompts with data-awareness and precedent sections
3. Third: Add the data fetcher with World Bank API + fallback logic
4. Fourth: Add document upload (PDF parsing + context injection)
5. Fifth: Add PDF export
6. Sixth: Update frontend (searchable country input, data sources panel, new examples)
7. Last: Caching and error handling

Please implement these changes to the existing project structure. Start with
the data layer expansion since everything else depends on it.
