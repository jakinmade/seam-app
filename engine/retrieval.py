"""
SEAM Data Retrieval Layer
Sprint 3 — Claude retrieves live public source data for a named asset.

User enters an asset name and jurisdiction.
Claude searches EITI, Fraser, World Bank, cadastre, ASX/TSX filings.
Extracts the relevant fields.
Returns a populated AssetInput ready for the scoring engine.

This is the layer that makes SEAM autonomous.
No manual data entry. No pre-loaded assets.
"""

import json
import os
import urllib.request
import urllib.error
from engine.scoring import AssetInput


# ---------------------------------------------------------------------------
# RETRIEVAL SYSTEM PROMPT
# ---------------------------------------------------------------------------

RETRIEVAL_SYSTEM_PROMPT = """You are the SEAM Data Retrieval Agent for African mining assets.

YOUR JOB:
Search public sources and extract the specific data fields required to score a mining asset under the SEAM Investment Readiness Methodology v1.0.

SOURCES TO SEARCH (in priority order):
1. EITI country reports (eiti.org) — revenues, beneficial ownership, payment data, compliance status
2. Fraser Institute Annual Survey (fraserinstitute.org) — Investment Attractiveness Index by jurisdiction
3. World Bank Governance Indicators (info.worldbank.org/governance/wgi) — Rule of Law, Regulatory Quality percentiles
4. Exchange filings — ASX, TSX, AIM, LSE regulatory announcements, annual reports, investor presentations
5. S&P Capital IQ public data — company profiles, capital structure, investor lists (public portions)
6. Refinitiv/LSEG public data — ownership, DFI linkages, capital raises
7. ICIJ Offshore Leaks database (offshoreleaks.icij.org) — beneficial ownership, PEP screening
8. Government cadastre portals — licence status, holder name, compliance filings
9. USGS mineral resources data (mrdata.usgs.gov) — resource estimates, commodity classification
10. World Bank Projects database (projects.worldbank.org) — DFI engagement, active projects
11. African Development Bank project database (afdb.org) — DFI engagement in jurisdiction
12. Lobito Corridor project registry (where applicable) — infrastructure eligibility
13. Mining ministry and gazette publications — local content compliance, LOCAS filings
14. Financial press and newswires — capital raises, DFI announcements, regulatory changes, disputes

RETRIEVAL RULES:
- Search for each data field systematically
- Record what you found, where you found it, and when
- If a field cannot be found in public sources, set it to the default/unknown value and flag it as a data gap
- Never invent data. Never estimate. If not found, say not found.
- Company-submitted data is supplementary only — never use as sole source for any dimension
- Prefer recent data (within 3 years) over older data

JURISDICTION CODES:
ZMB = Zambia, DRC = Democratic Republic of Congo, BWA = Botswana,
GHA = Ghana, TZA = Tanzania, NAM = Namibia, GIN = Guinea,
ZWE = Zimbabwe, MOZ = Mozambique

Return your response as a JSON object with exactly this structure:
{
  "asset_id": "auto-generated e.g. ZMB-AUTO-001",
  "asset_name": "full official name of the asset",
  "jurisdiction": "country name",
  "jurisdiction_code": "3-letter code",
  "commodity": "primary commodity",
  "province": "province or region",

  "fraser_investment_attractiveness": <float 0-100 or null>,
  "wb_rule_of_law_percentile": <float 0-100 or null>,
  "wb_regulatory_quality_percentile": <float 0-100 or null>,
  "regulatory_change_last_12m": <true/false>,
  "mining_code_revision_in_progress": <true/false>,
  "investment_arbitration_last_5y": <true/false>,
  "bilateral_investment_treaty": <true/false>,
  "eiti_compliant_country": <true/false>,

  "eiti_implementation_status": "compliant" or "candidate" or "non-implementing",
  "beneficial_ownership_disclosure": "full" or "partial" or "none",
  "eiti_payment_disclosure_quality": <float 0-100 or null>,
  "pep_in_ownership_chain": <true/false>,
  "fatf_grey_list_jurisdiction": <true/false>,
  "payment_data_gap_over_24m": <true/false>,

  "resource_estimate_standard": "ni43101_jorc_u3y" or "ni43101_jorc_o3y" or "samrec" or "none",
  "reserve_classification": "proven_probable" or "resource_only" or "historical" or "none",
  "production_data_availability": "current_u12m" or "current_12_36m" or "none",
  "exploration_stage": "producing" or "development" or "prefeasibility" or "exploration",
  "unresolved_resource_conflict": <true/false>,
  "estimate_by_company_employee": <true/false>,
  "no_independent_technical_report": <true/false>,

  "licence_holder_status": "citizen_owned" or "citizen_empowered" or "foreign_jv" or "other",
  "locas_filing_status": "submitted_verified" or "submitted_unverified" or "not_filed",
  "local_procurement_evidence": "confirmed_20pct_plus" or "effort_sub_20pct" or "none",
  "supplier_development_programme": "documented" or "in_development" or "none",
  "reserved_services_non_local": <true/false>,

  "power_supply": "grid_with_redundancy" or "grid_no_redundancy" or "diesel_solar" or "none",
  "road_access": "paved_u50km" or "paved_50_200km" or "unsealed" or "none",
  "rail_access": "operating_u100km" or "operating_capacity_constrained" or "rail_o100km" or "none",
  "water_supply": "permitted_documented" or "present_no_permit" or "none",
  "port_distance_km": <float or null>,
  "lobito_corridor_eligible": <true/false>,

  "active_dfi_engagement": "named_project_asset" or "jurisdiction_only" or "none",
  "listed_vehicle": "asx_tsx_aim_active" or "otc_listed" or "unlisted",
  "recent_capital_raise": "u18m" or "18_36m" or "none",
  "gulf_western_investor_linked": <true/false>,

  "sources_consulted": [
    {"field": "field_name", "source": "source name", "url": "url", "retrieved": "date", "value_found": "what was found"}
  ],
  "data_gaps": ["list of fields not found in public sources"]
}

Return only the JSON object. No preamble. No markdown fences. No explanation."""


RETRIEVAL_USER_PROMPT = """Retrieve public data for the following mining asset and populate all SEAM scoring fields.

Asset name: {asset_name}
Jurisdiction: {jurisdiction}
Additional context: {context}

Search systematically across all required sources. For jurisdiction-level data (Fraser, World Bank WGI, EITI country status) retrieve the most recent available values for {jurisdiction}.

For asset-level data (resource estimates, licence status, capital raises, DFI engagement) search specifically for this asset and operator.

Flag every field where public data was not found."""


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _extract_json_from_text(text: str) -> str:
    """
    Strip markdown fences and find the outermost JSON object.
    Handles cases where Claude wraps JSON in ```json ... ``` or adds preamble.
    """
    text = text.strip()

    # Strip markdown fences
    if "```" in text:
        parts = text.split("```")
        # parts[1] is the content between the first pair of fences
        for part in parts[1::2]:  # every odd part is inside fences
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                return candidate
        # fallback: try the whole stripped version
        text = parts[1].strip()
        if text.startswith("json"):
            text = text[4:].strip()
        return text

    # Find the first { and last } to extract the JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


def _call_claude(api_key: str, payload_dict: dict) -> str:
    """
    POST to Claude API and return the final text content block.
    Handles multi-turn tool use by taking the last text block in the response.
    """
    payload = json.dumps(payload_dict).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key,
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(body)
            msg = err.get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise RuntimeError(f"Anthropic API error {e.code}: {msg}") from None

    # Collect ALL text blocks; take the last non-empty one.
    # After web search tool use, Claude emits tool_use + tool_result blocks
    # then a final text block with the actual answer.
    text_blocks = [
        block["text"].strip()
        for block in data.get("content", [])
        if block.get("type") == "text" and block.get("text", "").strip()
    ]

    if not text_blocks:
        raise ValueError(
            f"No text content in Claude response. stop_reason={data.get('stop_reason')} "
            f"blocks={[b.get('type') for b in data.get('content', [])]}"
        )

    return text_blocks[-1]


# ---------------------------------------------------------------------------
# RETRIEVAL ENGINE
# ---------------------------------------------------------------------------

def retrieve_asset_data(asset_name: str, jurisdiction: str, context: str = "") -> tuple[AssetInput, dict]:
    """
    Call Claude with web search to retrieve live public data for a named asset.
    Returns (AssetInput, sources_metadata).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    prompt = RETRIEVAL_USER_PROMPT.format(
        asset_name=asset_name,
        jurisdiction=jurisdiction,
        context=context or "No additional context provided."
    )

    if not api_key:
        return _mock_retrieval(asset_name, jurisdiction), {"mock": True}

    # First attempt: with web search
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 4000,
        "system": RETRIEVAL_SYSTEM_PROMPT,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        raw = _call_claude(api_key, payload)
    except RuntimeError as e:
        # API-level error (e.g. out of credits, auth failure) — fall back to mock
        mock_input = _mock_retrieval(asset_name, jurisdiction)
        return mock_input, {"mock": True, "api_error": str(e)}

    raw = _extract_json_from_text(raw)

    # If still not parseable, retry without web search tool
    # (sometimes Claude adds preamble when web search is enabled)
    try:
        retrieved = json.loads(raw)
    except json.JSONDecodeError:
        try:
            payload_no_search = {
                "model": "claude-sonnet-4-6",
                "max_tokens": 4000,
                "system": RETRIEVAL_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}]
            }
            raw = _call_claude(api_key, payload_no_search)
            raw = _extract_json_from_text(raw)
            retrieved = json.loads(raw)
        except (RuntimeError, json.JSONDecodeError) as e:
            mock_input = _mock_retrieval(asset_name, jurisdiction)
            return mock_input, {"mock": True, "api_error": str(e)}

    sources = {
        "sources_consulted": retrieved.pop("sources_consulted", []),
        "data_gaps": retrieved.pop("data_gaps", []),
        "mock": False
    }

    asset_input = _dict_to_asset_input(retrieved)
    return asset_input, sources


def _dict_to_asset_input(d: dict) -> AssetInput:
    """Convert retrieved dict to AssetInput dataclass."""
    return AssetInput(
        asset_id=d.get("asset_id", "AUTO-001"),
        asset_name=d.get("asset_name", "Unknown Asset"),
        jurisdiction=d.get("jurisdiction", "Unknown"),
        jurisdiction_code=d.get("jurisdiction_code", "ZMB"),
        commodity=d.get("commodity", "Unknown"),
        province=d.get("province", "Unknown"),

        fraser_investment_attractiveness=d.get("fraser_investment_attractiveness"),
        wb_rule_of_law_percentile=d.get("wb_rule_of_law_percentile"),
        wb_regulatory_quality_percentile=d.get("wb_regulatory_quality_percentile"),
        regulatory_change_last_12m=d.get("regulatory_change_last_12m", False),
        mining_code_revision_in_progress=d.get("mining_code_revision_in_progress", False),
        investment_arbitration_last_5y=d.get("investment_arbitration_last_5y", False),
        bilateral_investment_treaty=d.get("bilateral_investment_treaty", False),
        eiti_compliant_country=d.get("eiti_compliant_country", False),

        eiti_implementation_status=d.get("eiti_implementation_status", "non-implementing"),
        beneficial_ownership_disclosure=d.get("beneficial_ownership_disclosure", "none"),
        eiti_payment_disclosure_quality=d.get("eiti_payment_disclosure_quality"),
        pep_in_ownership_chain=d.get("pep_in_ownership_chain", False),
        fatf_grey_list_jurisdiction=d.get("fatf_grey_list_jurisdiction", False),
        payment_data_gap_over_24m=d.get("payment_data_gap_over_24m", False),

        resource_estimate_standard=d.get("resource_estimate_standard", "none"),
        reserve_classification=d.get("reserve_classification", "none"),
        production_data_availability=d.get("production_data_availability", "none"),
        exploration_stage=d.get("exploration_stage", "exploration"),
        unresolved_resource_conflict=d.get("unresolved_resource_conflict", False),
        estimate_by_company_employee=d.get("estimate_by_company_employee", False),
        no_independent_technical_report=d.get("no_independent_technical_report", False),

        licence_holder_status=d.get("licence_holder_status", "other"),
        locas_filing_status=d.get("locas_filing_status", "not_filed"),
        local_procurement_evidence=d.get("local_procurement_evidence", "none"),
        supplier_development_programme=d.get("supplier_development_programme", "none"),
        reserved_services_non_local=d.get("reserved_services_non_local", False),

        power_supply=d.get("power_supply", "none"),
        road_access=d.get("road_access", "none"),
        rail_access=d.get("rail_access", "none"),
        water_supply=d.get("water_supply", "none"),
        port_distance_km=d.get("port_distance_km"),
        lobito_corridor_eligible=d.get("lobito_corridor_eligible", False),

        active_dfi_engagement=d.get("active_dfi_engagement", "none"),
        listed_vehicle=d.get("listed_vehicle", "unlisted"),
        recent_capital_raise=d.get("recent_capital_raise", "none"),
        gulf_western_investor_linked=d.get("gulf_western_investor_linked", False),
    )


def _mock_retrieval(asset_name: str, jurisdiction: str) -> AssetInput:
    """Mock retrieval for testing without API key. Returns conservative defaults."""
    import hashlib
    uid = hashlib.md5(asset_name.encode()).hexdigest()[:6].upper()

    jur_map = {
        "zambia": ("ZMB", "Copperbelt"),
        "ghana": ("GHA", "Ashanti"),
        "tanzania": ("TZA", "Mwanza"),
        "botswana": ("BWA", "Central"),
        "drc": ("DRC", "Katanga"),
        "namibia": ("NAM", "Erongo"),
    }
    jcode, province = jur_map.get(jurisdiction.lower(), ("ZMB", "Unknown"))

    return AssetInput(
        asset_id=f"{jcode}-AUTO-{uid}",
        asset_name=asset_name,
        jurisdiction=jurisdiction,
        jurisdiction_code=jcode,
        commodity="Unknown — live retrieval required",
        province=province,
        fraser_investment_attractiveness=None,
        wb_rule_of_law_percentile=None,
        wb_regulatory_quality_percentile=None,
    )

