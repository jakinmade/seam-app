"""
SEAM Data Retrieval Layer
Session 1 v2 — Operator-aware, field-directive retrieval.

The key fix: the retrieval prompt now explicitly tells the model what
values to expect for known fields, and instructs it to search field by
field rather than returning a schema with nulls.
"""

import json
import os
import urllib.request
import urllib.error
from engine.scoring import AssetInput


# ---------------------------------------------------------------------------
# OPERATOR IDENTIFICATION PROMPT
# ---------------------------------------------------------------------------

OPERATOR_SYSTEM_PROMPT = """You are a mining intelligence agent. Identify the operator and key facts for a named African mining asset.

Search Wikipedia, company websites, exchange filings, and public mining databases.

Return only this JSON. No preamble. No markdown:
{
  "asset_name_official": "full official name",
  "operator": "primary operating company",
  "operator_parent": "parent company if different from operator",
  "operator_aliases": ["alternative names"],
  "majority_owner": "majority ownership entity",
  "minority_owners": ["minority owners"],
  "ticker": "exchange ticker if listed",
  "exchange": "exchange name if listed",
  "commodity_primary": "primary commodity",
  "commodity_secondary": ["other commodities"],
  "asset_stage": "producing or development or prefeasibility or exploration",
  "province_region": "province or region",
  "operator_hq": "operator headquarters country",
  "known_dfi_links": ["named DFI relationships"],
  "search_confidence": "high or medium or low"
}"""

OPERATOR_USER_PROMPT = """Identify the operator and key facts for this asset.

Asset: {asset_name}
Jurisdiction: {jurisdiction}
Context: {context}

Search specifically for this asset. Return what you find."""


# ---------------------------------------------------------------------------
# FIELD-DIRECTIVE RETRIEVAL PROMPT
# ---------------------------------------------------------------------------

RETRIEVAL_SYSTEM_PROMPT = """You are the SEAM Data Retrieval Agent. You retrieve specific data fields for African mining assets from public sources.

CRITICAL INSTRUCTION:
You must search for and populate every field. Do not return null for fields that are knowable from public sources.
For each field, run a targeted search. Do not batch fields together.

SEARCH STRATEGY:
1. Jurisdiction fields (Fraser, WB, EITI): search "[country name] Fraser Institute mining 2024 2025" and "[country name] World Bank governance indicators 2024" and "[country name] EITI compliance 2024"
2. Asset production fields: search "[operator name] annual report 2024" and "[asset name] resource estimate" and "[asset name] production 2024"
3. Ownership fields: search "[asset name] ownership structure" and "[operator name] beneficial ownership" and ICIJ database
4. Infrastructure fields: search "[asset name] infrastructure" and "[asset name] power supply" and "[province] railway logistics"
5. Capital fields: search "[operator name] DFI" and "[asset name] IFC AfDB" and "[operator name] capital raise 2023 2024 2025"
6. Local content: search "[asset name] LOCAS" and "[operator name] Zambia local content" and "[country] mining local content compliance"

KNOWN VALUES FOR COMMON JURISDICTIONS (use these if search confirms):
- Zambia EITI: compliant country = true, status = compliant (Zambia has been EITI compliant since 2012)
- Zambia Fraser 2024: approximately 50-55 out of 100
- Zambia WB Rule of Law: approximately 25-35th percentile
- Zambia WB Regulatory Quality: approximately 30-40th percentile
- Zambia FATF: false (not on grey list as of 2025)
- Zambia BIT: true (multiple bilateral investment treaties in force)
- Ghana EITI: compliant = true
- Tanzania EITI: compliant = true
- Botswana EITI: compliant = true

FIELD MAPPING GUIDE:
- If asset is actively producing copper/gold/cobalt: exploration_stage = "producing"
- If operator has published NI 43-101 or JORC resource in last 3 years: resource_estimate_standard = "ni43101_jorc_u3y"
- If operator has published older resource: resource_estimate_standard = "ni43101_jorc_o3y"
- If production data in last 12 months found: production_data_availability = "current_u12m"
- If production data 12-36 months old: production_data_availability = "current_12_36m"
- If IFC, AfDB, BII, OPIC/DFC named in relation to this specific asset: active_dfi_engagement = "named_project_asset"
- If DFI active in jurisdiction but not named for this asset: active_dfi_engagement = "jurisdiction_only"
- If operator listed on ASX/TSX/AIM/LSE with active trading: listed_vehicle = "asx_tsx_aim_active"
- If capital raise in last 18 months found: recent_capital_raise = "u18m"
- If Lobito Corridor: eligible for assets in Zambia Copperbelt, DRC Katanga, Angola
- If foreign-owned JV with Zambian state entity (ZCCM-IH): licence_holder_status = "citizen_empowered"
- If LOCAS filing referenced in annual report or gazette: locas_filing_status = "submitted_verified"

Return exactly this JSON. Populate every field you can from search results. Only use null where genuinely not findable:
{
  "asset_id": "jurisdiction_code-ASSET_ABBREV-001",
  "asset_name": "official asset name",
  "operator": "operator name",
  "jurisdiction": "country",
  "jurisdiction_code": "3-letter ISO",
  "commodity": "primary commodity",
  "province": "province or region",

  "fraser_investment_attractiveness": <float or null>,
  "wb_rule_of_law_percentile": <float or null>,
  "wb_regulatory_quality_percentile": <float or null>,
  "regulatory_change_last_12m": <true/false>,
  "mining_code_revision_in_progress": <true/false>,
  "investment_arbitration_last_5y": <true/false>,
  "bilateral_investment_treaty": <true/false>,
  "eiti_compliant_country": <true/false>,

  "eiti_implementation_status": "compliant" or "candidate" or "non-implementing",
  "beneficial_ownership_disclosure": "full" or "partial" or "none",
  "eiti_payment_disclosure_quality": <float or null>,
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
    "operator": "name",
    "parent": "parent company",
    "hq_country": "country",
    "ticker": "ticker or null",
    "exchange": "exchange or null",
    "environmental_incidents": <true/false>,
    "labour_disputes_last_5y": <true/false>,
    "litigation_active": <true/false>,
    "dfi_relationships": ["named DFIs"]
  },

  "environmental_permit_status": "permitted" or "in_progress" or "not_filed" or "unknown",
  "esia_completed": <true/false>,
  "community_consultation_evidence": "documented" or "partial" or "none",
  "social_licence_disputes": <true/false>,
  "water_licence_status": "permitted" or "pending" or "not_filed" or "unknown",

  "sources_consulted": [
    {"field": "field_name", "source": "source", "url": "url or null", "retrieved": "YYYY-MM-DD", "value_found": "value"}
  ],
  "data_gaps": ["fields genuinely not findable in public sources"]
}"""


RETRIEVAL_USER_PROMPT = """Retrieve all SEAM scoring fields for this asset.

Asset name: {asset_name}
Operator: {operator}
Parent company: {parent}
Operator aliases: {aliases}
Jurisdiction: {jurisdiction}
Commodity: {commodity}
Stage: {stage}
Exchange/Ticker: {ticker}
Context: {context}

SEARCH INSTRUCTIONS:
1. Start with jurisdiction-level data: search "Zambia EITI 2024 2025 compliance" — Zambia is a known EITI compliant country, confirm and populate fields.
2. Search "Zambia Fraser Institute 2024 investment attractiveness" for D1 score.
3. Search "World Bank governance indicators Zambia 2024" for rule of law and regulatory quality percentiles.
4. Search "{operator} annual report 2024 2025" for production data, resource estimates, capital structure.
5. Search "{asset_name} {operator} resource estimate NI 43-101 JORC" for D3 fields.
6. Search "{asset_name} LOCAS local content Zambia" for D4 fields.
7. Search "{asset_name} {operator} DFI IFC AfDB BII" for D6 fields.
8. Search "{asset_name} power supply rail infrastructure Copperbelt" for D5 fields.
9. Search "{operator} beneficial ownership Zambia" for D2 ownership fields.

Populate every field you can confirm from search results. Return null only where genuinely not findable."""


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> str:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts[1::2]:
            c = part.strip()
            if c.startswith("json"):
                c = c[4:].strip()
            if c.startswith("{"):
                return c
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end > start:
        return text[start:end+1]
    return text


def _call_api(api_key: str, system: str, user: str, use_search: bool = True) -> str:
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 6000,
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

    blocks = [
        b["text"].strip()
        for b in data.get("content", [])
        if b.get("type") == "text" and b.get("text", "").strip()
    ]
    if not blocks:
        raise ValueError(f"No text in response. stop_reason={data.get('stop_reason')}")
    return blocks[-1]


def _parse(raw: str) -> dict:
    return json.loads(_extract_json(raw))


def _count_retrieved(d: dict) -> int:
    """Count non-null, non-default scored fields."""
    checks = [
        d.get("fraser_investment_attractiveness") is not None,
        d.get("wb_rule_of_law_percentile") is not None,
        d.get("wb_regulatory_quality_percentile") is not None,
        d.get("eiti_implementation_status") not in (None, "non-implementing"),
        d.get("eiti_compliant_country") is True,
        d.get("eiti_payment_disclosure_quality") is not None,
        d.get("beneficial_ownership_disclosure") not in (None, "none"),
        d.get("resource_estimate_standard") not in (None, "none"),
        d.get("reserve_classification") not in (None, "none"),
        d.get("production_data_availability") not in (None, "none"),
        bool(d.get("commodity") and "unknown" not in d.get("commodity", "").lower()),
        d.get("licence_holder_status") not in (None, "other"),
        d.get("locas_filing_status") not in (None, "not_filed"),
        d.get("power_supply") not in (None, "none"),
        d.get("road_access") not in (None, "none"),
        d.get("water_supply") not in (None, "none"),
        d.get("port_distance_km") is not None,
        d.get("active_dfi_engagement") not in (None, "none"),
        d.get("listed_vehicle") not in (None, "unlisted"),
    ]
    return sum(checks)


# ---------------------------------------------------------------------------
# PHASE 1 — OPERATOR ID
# ---------------------------------------------------------------------------

def _identify_operator(api_key: str, asset_name: str, jurisdiction: str, context: str) -> dict:
    try:
        raw = _call_api(
            api_key,
            OPERATOR_SYSTEM_PROMPT,
            OPERATOR_USER_PROMPT.format(
                asset_name=asset_name,
                jurisdiction=jurisdiction,
                context=context or "None."
            ),
            use_search=True
        )
        return _parse(raw)
    except Exception:
        return {
            "asset_name_official": asset_name,
            "operator": "",
            "operator_parent": "",
            "operator_aliases": [],
            "commodity_primary": "",
            "asset_stage": "",
            "ticker": None,
            "exchange": None,
            "search_confidence": "low"
        }


# ---------------------------------------------------------------------------
# PHASE 2 — FIELD RETRIEVAL
# ---------------------------------------------------------------------------

def _retrieve_fields(api_key: str, asset_name: str, jurisdiction: str,
                     context: str, op: dict) -> dict:
    operator = op.get("operator") or "unknown"
    parent   = op.get("operator_parent") or op.get("majority_owner") or ""
    aliases  = ", ".join(op.get("operator_aliases") or []) or "none"
    commodity= op.get("commodity_primary") or "unknown"
    stage    = op.get("asset_stage") or "unknown"
    ticker   = op.get("ticker") or op.get("listed_vehicle") or "unknown"

    prompt = RETRIEVAL_USER_PROMPT.format(
        asset_name=op.get("asset_name_official") or asset_name,
        operator=operator,
        parent=parent,
        aliases=aliases,
        jurisdiction=jurisdiction,
        commodity=commodity,
        stage=stage,
        ticker=ticker,
        context=context or "None."
    )

    try:
        raw = _call_api(api_key, RETRIEVAL_SYSTEM_PROMPT, prompt, use_search=True)
        result = _parse(raw)
    except json.JSONDecodeError:
        # Retry without web search
        raw = _call_api(api_key, RETRIEVAL_SYSTEM_PROMPT, prompt, use_search=False)
        result = _parse(raw)

    # If retrieval came back with very few fields populated, retry with stronger directive
    if _count_retrieved(result) < 3:
        retry_prompt = (
            prompt +
            "\n\nCRITICAL: Your previous response had fewer than 3 fields populated. "
            "You must search more aggressively. For Zambia assets: EITI compliant = true, "
            "search Fraser Institute Zambia 2024, search World Bank WGI Zambia 2024. "
            "For KCM/Vedanta: search Vedanta Resources annual report, search Konkola Copper Mines production. "
            "Populate every field you can find. Do not return nulls for knowable jurisdiction-level data."
        )
        try:
            raw2 = _call_api(api_key, RETRIEVAL_SYSTEM_PROMPT, retry_prompt, use_search=True)
            result2 = _parse(raw2)
            if _count_retrieved(result2) > _count_retrieved(result):
                result = result2
        except Exception:
            pass  # Keep original result

    return result


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def retrieve_asset_data(asset_name: str, jurisdiction: str,
                        context: str = "") -> tuple[AssetInput, dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        return _mock_retrieval(asset_name, jurisdiction), {"mock": True}

    try:
        op        = _identify_operator(api_key, asset_name, jurisdiction, context)
        retrieved = _retrieve_fields(api_key, asset_name, jurisdiction, context, op)
    except RuntimeError as e:
        return _mock_retrieval(asset_name, jurisdiction), {
            "mock": True, "api_error": str(e)
        }
    except Exception as e:
        return _mock_retrieval(asset_name, jurisdiction), {
            "mock": True, "api_error": f"Retrieval failed: {str(e)}"
        }

    sources = {
        "sources_consulted": retrieved.pop("sources_consulted", []),
        "data_gaps":         retrieved.pop("data_gaps", []),
        "operator_profile":  retrieved.pop("operator_profile", {}),
        "phase1_operator":   op,
        "mock": False
    }

    return _dict_to_asset_input(retrieved), sources


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

        environmental_permit_status=d.get("environmental_permit_status", "unknown"),
        esia_completed=d.get("esia_completed", False),
        community_consultation_evidence=d.get("community_consultation_evidence", "none"),
        social_licence_disputes=d.get("social_licence_disputes", False),
        water_licence_status=d.get("water_licence_status", "unknown"),
    )


# ---------------------------------------------------------------------------
# MOCK
# ---------------------------------------------------------------------------

def _mock_retrieval(asset_name: str, jurisdiction: str) -> AssetInput:
    import hashlib
    uid = hashlib.md5(asset_name.encode()).hexdigest()[:6].upper()
    jur_map = {
        "zambia":     ("ZMB", "Copperbelt"),
        "ghana":      ("GHA", "Ashanti"),
        "tanzania":   ("TZA", "Mwanza"),
        "botswana":   ("BWA", "Central"),
        "drc":        ("COD", "Katanga"),
        "namibia":    ("NAM", "Erongo"),
        "guinea":     ("GIN", "Boke"),
        "zimbabwe":   ("ZWE", "Matabeleland"),
        "mozambique": ("MOZ", "Tete"),
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

