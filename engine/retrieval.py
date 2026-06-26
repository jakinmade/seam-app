"""
SEAM Data Retrieval Layer
Session 1 — Operator-aware retrieval. Two-phase search.

Phase 1: Identify the operator, aliases and listed vehicle for the named asset.
Phase 2: Use operator + asset name together to retrieve all SEAM scoring fields.

KCM searches for "Konkola Copper Mines" AND "Vedanta Resources Zambia".
That unlocks annual reports, exchange filings, EITI records, DFI data.
"""

import json
import os
import urllib.request
import urllib.error
from engine.scoring import AssetInput


# ---------------------------------------------------------------------------
# PHASE 1 — OPERATOR IDENTIFICATION
# ---------------------------------------------------------------------------

OPERATOR_SYSTEM_PROMPT = """You are a mining intelligence agent. Your job is to identify the operator and key identifiers for a named mining asset.

Search public sources and return structured JSON only. No preamble. No explanation.

Return exactly this JSON structure:
{
  "asset_name_official": "the full official name of the asset",
  "operator": "primary operator / management company name",
  "operator_aliases": ["any alternative names or previous names for the operator"],
  "majority_owner": "majority ownership entity",
  "minority_owners": ["list of known minority owners"],
  "listed_vehicle": "ASX/TSX/AIM/LSE ticker if listed, else null",
  "exchange": "exchange name if listed, else null",
  "commodity_primary": "primary commodity produced or being explored for",
  "commodity_secondary": ["secondary commodities if any"],
  "asset_stage": "producing or development or prefeasibility or exploration",
  "province_region": "province or region within the jurisdiction",
  "operator_hq_country": "country where operator is headquartered",
  "known_dfi_links": ["any known DFI relationships e.g. IFC, AfDB, BII, OPIC/DFC"],
  "search_confidence": "high or medium or low"
}

If any field cannot be found, set it to null or empty list. Never invent data."""

OPERATOR_USER_PROMPT = """Identify the operator and key identifiers for this mining asset.

Asset name: {asset_name}
Jurisdiction: {jurisdiction}
Additional context: {context}

Search for the asset name, any known aliases, and the operating company. For well-known assets, check Wikipedia, company websites, exchange filings, and mining databases."""


# ---------------------------------------------------------------------------
# PHASE 2 — FULL FIELD RETRIEVAL
# ---------------------------------------------------------------------------

RETRIEVAL_SYSTEM_PROMPT = """You are the SEAM Data Retrieval Agent for African mining assets.

You have been given the asset name AND the operator name. Search for both together.
For KCM, search "Konkola Copper Mines" AND "Vedanta Resources Zambia".
For Lumwana, search "Lumwana Mine" AND "Barrick Gold Zambia".
This doubles the evidence you can find.

SOURCES TO SEARCH (in priority order):
1. EITI country reports (eiti.org) — revenues, beneficial ownership, payment data, compliance status
2. Fraser Institute Annual Survey (fraserinstitute.org) — Investment Attractiveness Index by jurisdiction
3. World Bank Governance Indicators (info.worldbank.org/governance/wgi) — Rule of Law, Regulatory Quality percentiles
4. Exchange filings (ASX, TSX, AIM, LSE) — annual reports, regulatory announcements, resource estimates
5. Operator annual reports and investor presentations — production data, capital structure, DFI relationships
6. ICIJ Offshore Leaks database (offshoreleaks.icij.org) — beneficial ownership, PEP screening
7. Government cadastre portals — licence status, holder name, compliance filings
8. USGS mineral resources data (mrdata.usgs.gov) — resource estimates, commodity data
9. World Bank Projects database (projects.worldbank.org) — DFI engagement
10. African Development Bank database (afdb.org) — DFI engagement in jurisdiction
11. Lobito Corridor project registry — infrastructure eligibility for Copperbelt/DRC assets
12. Mining ministry and gazette publications — local content compliance, LOCAS filings
13. Financial press and newswires — capital raises, disputes, regulatory changes

RETRIEVAL RULES:
- Search asset name AND operator name. Use both.
- Jurisdiction-level fields (Fraser, WB, EITI country status): retrieve for the jurisdiction.
- Asset-level fields (resource estimates, production, licence, capital raises): retrieve for this specific asset and operator.
- Record every source. Record what was found and when.
- If a field cannot be found, set to null/default and add to data_gaps.
- Never invent data. Never estimate. Not found means not found.
- Prefer data from the last 3 years. Flag older data.

JURISDICTION CODES:
ZMB=Zambia, COD=DRC, BWA=Botswana, GHA=Ghana, TZA=Tanzania,
NAM=Namibia, GIN=Guinea, ZWE=Zimbabwe, MOZ=Mozambique, CIV=Cote d'Ivoire

Return exactly this JSON. No preamble. No markdown. No explanation:
{
  "asset_id": "e.g. ZMB-KCM-001",
  "asset_name": "full official asset name",
  "operator": "operator name",
  "jurisdiction": "country name",
  "jurisdiction_code": "3-letter ISO code",
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

  "operator_profile": {
    "operator": "operator name",
    "hq_country": "country",
    "listed_on": "exchange or null",
    "ticker": "ticker or null",
    "environmental_incidents": <true/false>,
    "labour_disputes_last_5y": <true/false>,
    "litigation_active": <true/false>,
    "dfi_relationships": ["list of DFIs with active relationships"]
  },

  "sources_consulted": [
    {"field": "field_name", "source": "source name", "url": "url or null", "retrieved": "YYYY-MM-DD", "value_found": "what was found"}
  ],
  "data_gaps": ["fields not found in public sources"]
}"""


RETRIEVAL_USER_PROMPT = """Retrieve public data for this mining asset.

Asset name: {asset_name}
Operator: {operator}
Operator aliases: {operator_aliases}
Jurisdiction: {jurisdiction}
Commodity (if known): {commodity}
Listed vehicle: {listed_vehicle}
Additional context: {context}

Search for BOTH the asset name AND the operator name. Use the operator's exchange filings, annual reports and investor presentations as primary sources for production data, resource estimates and capital structure. Use EITI and World Bank for jurisdiction-level governance data.

Return only valid JSON matching the schema exactly."""


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> str:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts[1::2]:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                return candidate
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def _call_api(api_key: str, system: str, user: str, use_search: bool = True) -> str:
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 4000,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": user}]
    }
    if use_search:
        payload["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
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
            msg = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise RuntimeError(f"API error {e.code}: {msg}") from None

    text_blocks = [
        b["text"].strip()
        for b in data.get("content", [])
        if b.get("type") == "text" and b.get("text", "").strip()
    ]
    if not text_blocks:
        raise ValueError(f"No text in response. stop_reason={data.get('stop_reason')}")
    return text_blocks[-1]


def _parse_json(raw: str) -> dict:
    raw = _extract_json(raw)
    return json.loads(raw)


# ---------------------------------------------------------------------------
# PHASE 1 — OPERATOR IDENTIFICATION
# ---------------------------------------------------------------------------

def _identify_operator(api_key: str, asset_name: str, jurisdiction: str, context: str) -> dict:
    """Phase 1: identify operator, commodity, aliases before full retrieval."""
    prompt = OPERATOR_USER_PROMPT.format(
        asset_name=asset_name,
        jurisdiction=jurisdiction,
        context=context or "None provided."
    )
    try:
        raw = _call_api(api_key, OPERATOR_SYSTEM_PROMPT, prompt, use_search=True)
        return _parse_json(raw)
    except Exception:
        # Non-fatal — Phase 2 proceeds with asset name only
        return {
            "asset_name_official": asset_name,
            "operator": "",
            "operator_aliases": [],
            "commodity_primary": "",
            "listed_vehicle": None,
            "exchange": None,
            "search_confidence": "low"
        }


# ---------------------------------------------------------------------------
# PHASE 2 — FULL FIELD RETRIEVAL
# ---------------------------------------------------------------------------

def _retrieve_fields(api_key: str, asset_name: str, jurisdiction: str,
                     context: str, op: dict) -> dict:
    """Phase 2: full field retrieval using operator context from Phase 1."""
    operator = op.get("operator") or ""
    aliases   = ", ".join(op.get("operator_aliases") or []) or "none"
    commodity = op.get("commodity_primary") or "unknown"
    listed    = op.get("listed_vehicle") or "unknown"

    prompt = RETRIEVAL_USER_PROMPT.format(
        asset_name=op.get("asset_name_official") or asset_name,
        operator=operator or "unknown — search for operator",
        operator_aliases=aliases,
        jurisdiction=jurisdiction,
        commodity=commodity,
        listed_vehicle=listed,
        context=context or "None provided."
    )

    try:
        raw = _call_api(api_key, RETRIEVAL_SYSTEM_PROMPT, prompt, use_search=True)
        return _parse_json(raw)
    except json.JSONDecodeError:
        # Retry without web search tool
        raw = _call_api(api_key, RETRIEVAL_SYSTEM_PROMPT, prompt, use_search=False)
        return _parse_json(raw)


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def retrieve_asset_data(asset_name: str, jurisdiction: str,
                        context: str = "") -> tuple[AssetInput, dict]:
    """
    Two-phase operator-aware retrieval.
    Phase 1: identify operator, commodity, listed vehicle.
    Phase 2: retrieve all SEAM scoring fields using operator + asset name.
    Returns (AssetInput, sources_metadata).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        return _mock_retrieval(asset_name, jurisdiction), {"mock": True}

    try:
        # Phase 1
        op = _identify_operator(api_key, asset_name, jurisdiction, context)

        # Phase 2
        retrieved = _retrieve_fields(api_key, asset_name, jurisdiction, context, op)

    except RuntimeError as e:
        return _mock_retrieval(asset_name, jurisdiction), {
            "mock": True, "api_error": str(e)
        }
    except Exception as e:
        return _mock_retrieval(asset_name, jurisdiction), {
            "mock": True, "api_error": f"Retrieval failed: {str(e)}"
        }

    # Merge operator profile from Phase 1 into sources metadata
    sources = {
        "sources_consulted": retrieved.pop("sources_consulted", []),
        "data_gaps":         retrieved.pop("data_gaps", []),
        "operator_profile":  retrieved.pop("operator_profile",
                                           op.get("operator_profile", {})),
        "phase1_operator":   op,
        "mock": False
    }

    asset_input = _dict_to_asset_input(retrieved)
    return asset_input, sources


# ---------------------------------------------------------------------------
# DICT TO AssetInput
# ---------------------------------------------------------------------------

def _dict_to_asset_input(d: dict) -> AssetInput:
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


# ---------------------------------------------------------------------------
# MOCK
# ---------------------------------------------------------------------------

def _mock_retrieval(asset_name: str, jurisdiction: str) -> AssetInput:
    import hashlib
    uid    = hashlib.md5(asset_name.encode()).hexdigest()[:6].upper()
    jur_map = {
        "zambia":    ("ZMB", "Copperbelt"),
        "ghana":     ("GHA", "Ashanti"),
        "tanzania":  ("TZA", "Mwanza"),
        "botswana":  ("BWA", "Central"),
        "drc":       ("COD", "Katanga"),
        "namibia":   ("NAM", "Erongo"),
        "guinea":    ("GIN", "Boke"),
        "zimbabwe":  ("ZWE", "Matabeleland"),
        "mozambique":("MOZ", "Tete"),
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
