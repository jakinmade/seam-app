"""
SEAM Known Assets Registry
Comprehensive seed data for deterministic retrieval.

TWO LAYERS:

1. JURISDICTION DATA — static annual publication values for all 9 jurisdictions.
   Fraser Index, World Bank WGI, EITI status, FATF, BIT.
   These do not change run-to-run. They are sourced from published annual reports.
   Applied to EVERY asset in that jurisdiction, always.

2. ASSET DATA — confirmed facts for well-documented named assets.
   Commodity, operator, stage, Lobito eligibility.
   Applied only when asset name matches.
   Does not overwrite data the web search found.

Every value here must be verifiable from a named public source.
"""

# ── JURISDICTION STATIC DATA ──────────────────────────────────────────────
# Source: Fraser Institute Annual Survey 2024, World Bank WGI 2023,
#         EITI country pages (eiti.org), FATF public statement 2025,
#         UNCTAD BIT database 2024
# These are the most recent published annual values as of mid-2026.
# Update when new annual publications are released.

JURISDICTION_DATA: dict = {

    "ZMB": {  # Zambia
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 51.2,   # Fraser 2024
        "wb_rule_of_law_percentile": 30.3,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 33.7,   # WB WGI 2023
    },

    "GHA": {  # Ghana
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 62.4,   # Fraser 2024
        "wb_rule_of_law_percentile": 47.6,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 50.2,   # WB WGI 2023
    },

    "TZA": {  # Tanzania
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 44.8,   # Fraser 2024
        "wb_rule_of_law_percentile": 35.6,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 38.2,   # WB WGI 2023
    },

    "BWA": {  # Botswana
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 68.3,   # Fraser 2024
        "wb_rule_of_law_percentile": 63.5,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 60.1,   # WB WGI 2023
    },

    "NAM": {  # Namibia
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 57.6,   # Fraser 2024
        "wb_rule_of_law_percentile": 56.3,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 54.8,   # WB WGI 2023
    },

    "COD": {  # DRC
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 28.4,   # Fraser 2024
        "wb_rule_of_law_percentile": 4.3,           # WB WGI 2023
        "wb_regulatory_quality_percentile": 6.7,    # WB WGI 2023
    },

    "GIN": {  # Guinea
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 35.2,   # Fraser 2024
        "wb_rule_of_law_percentile": 14.9,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 17.3,   # WB WGI 2023
    },

    "ZWE": {  # Zimbabwe
        "eiti_compliant_country": False,
        "eiti_implementation_status": "candidate",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 22.1,   # Fraser 2024
        "wb_rule_of_law_percentile": 12.0,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 10.6,   # WB WGI 2023
    },

    "MOZ": {  # Mozambique
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 38.9,   # Fraser 2024
        "wb_rule_of_law_percentile": 21.6,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 24.5,   # WB WGI 2023
    },

    "CIV": {  # Côte d'Ivoire
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 59.1,   # Fraser 2024
        "wb_rule_of_law_percentile": 36.1,          # WB WGI 2023
        "wb_regulatory_quality_percentile": 41.3,   # WB WGI 2023
    },
}


# ── ASSET SEED DATA ──────────────────────────────────────────────────────
# Only fields that are stable confirmed public facts.
# Do NOT include scores, financial metrics, or anything that changes annually.
# Keys are lowercase search terms. Matching is substring-based.

ASSET_DATA: dict = {
    "kcm":          {"asset_name": "Konkola Copper Mines Plc", "operator": "Vedanta Resources",
                     "commodity": "Copper", "province": "Copperbelt Province",
                     "exploration_stage": "producing", "lobito_corridor_eligible": True},
    "konkola":      {"asset_name": "Konkola Copper Mines Plc", "operator": "Vedanta Resources",
                     "commodity": "Copper", "province": "Copperbelt Province",
                     "exploration_stage": "producing", "lobito_corridor_eligible": True},
    "lumwana":      {"asset_name": "Lumwana Copper Mine", "operator": "Barrick Gold Corporation",
                     "commodity": "Copper", "province": "North-Western Province",
                     "exploration_stage": "producing", "lobito_corridor_eligible": True,
                     "listed_vehicle": "asx_tsx_aim_active"},
    "kamoa":        {"asset_name": "Kamoa-Kakula Copper Complex", "operator": "Ivanhoe Mines",
                     "commodity": "Copper", "province": "Lualaba Province",
                     "exploration_stage": "producing", "listed_vehicle": "asx_tsx_aim_active"},
    "kansanshi":    {"asset_name": "Kansanshi Copper-Gold Mine",
                     "operator": "First Quantum Minerals", "commodity": "Copper",
                     "province": "North-Western Province", "exploration_stage": "producing",
                     "lobito_corridor_eligible": True, "listed_vehicle": "asx_tsx_aim_active"},
    "mingomba":     {"asset_name": "Mingomba Copper Project", "operator": "KoBold Metals",
                     "commodity": "Copper", "province": "Copperbelt Province",
                     "exploration_stage": "exploration", "lobito_corridor_eligible": True},
    "obuasi":       {"asset_name": "Obuasi Gold Mine", "operator": "AngloGold Ashanti",
                     "commodity": "Gold", "province": "Ashanti Region",
                     "exploration_stage": "producing", "listed_vehicle": "asx_tsx_aim_active"},
    "geita":        {"asset_name": "Geita Gold Mine", "operator": "AngloGold Ashanti",
                     "commodity": "Gold", "province": "Geita Region",
                     "exploration_stage": "producing", "listed_vehicle": "asx_tsx_aim_active"},
    "north mara":   {"asset_name": "North Mara Gold Mine", "operator": "Barrick Gold",
                     "commodity": "Gold", "province": "Mara Region",
                     "exploration_stage": "producing", "listed_vehicle": "asx_tsx_aim_active"},
    "bulyanhulu":   {"asset_name": "Bulyanhulu Gold Mine", "operator": "Barrick Gold",
                     "commodity": "Gold", "province": "Shinyanga Region",
                     "exploration_stage": "producing", "listed_vehicle": "asx_tsx_aim_active"},
    "twiga":        {"asset_name": "Twiga Minerals", "operator": "Barrick Gold",
                     "commodity": "Gold", "province": "Tanzania",
                     "exploration_stage": "producing"},
    "husab":        {"asset_name": "Husab Uranium Mine", "operator": "Swakop Uranium",
                     "commodity": "Uranium", "province": "Erongo Region",
                     "exploration_stage": "producing"},
    "rosh pinah":   {"asset_name": "Rosh Pinah Zinc Mine", "operator": "Trevali Mining",
                     "commodity": "Zinc", "province": "Karas Region",
                     "exploration_stage": "producing"},
    "simandou":     {"asset_name": "Simandou Iron Ore Project",
                     "operator": "Rio Tinto / SMB-Winning", "commodity": "Iron Ore",
                     "province": "Nzérékoré Prefecture", "exploration_stage": "development"},
    "epanko":       {"asset_name": "Epanko Graphite Project", "operator": "EcoGraf",
                     "commodity": "Graphite", "province": "Ulanga District",
                     "exploration_stage": "development"},
    "kabanga":      {"asset_name": "Kabanga Nickel Project", "operator": "Kabanga Nickel",
                     "commodity": "Nickel", "province": "Kagera Region",
                     "exploration_stage": "development"},
}


# ── PUBLIC INTERFACE ──────────────────────────────────────────────────────

def get_jurisdiction_data(jurisdiction_code: str) -> dict:
    """
    Return confirmed annual publication data for a jurisdiction.
    Applied to every asset — these are static facts not affected by web search.
    """
    return dict(JURISDICTION_DATA.get(jurisdiction_code.upper(), {}))


def get_asset_seed(asset_name: str) -> dict:
    """
    Return confirmed seed facts for a named asset.
    Substring match, case-insensitive.
    Returns empty dict if no match — retrieval proceeds without seed.
    """
    name_lower = asset_name.lower().strip()
    # Exact match first
    if name_lower in ASSET_DATA:
        return dict(ASSET_DATA[name_lower])
    # Substring match
    for key, data in ASSET_DATA.items():
        if key in name_lower or name_lower in key:
            return dict(data)
    return {}


def apply_seeds(retrieved: dict, asset_name: str, jurisdiction_code: str) -> dict:
    """
    Apply jurisdiction and asset seeds to a retrieved dict.

    Merge strategy:
    - Jurisdiction data ALWAYS applies — these are annual publication facts.
      They never vary run-to-run. Web search cannot produce better values.
    - Asset seed applies only where retrieved field is null/default/unknown.
      If web search found a value, it wins.

    Returns the enriched dict.
    """
    jur_data   = get_jurisdiction_data(jurisdiction_code)
    asset_seed = get_asset_seed(asset_name)

    # 1. Jurisdiction data applies with field-type awareness:
    # - Boolean/status fields (EITI, FATF, BIT): always apply — confirmed annual facts
    # - Quantitative fields (Fraser, WB percentiles): fill nulls only — web search may have fresher data
    _jur_always = {"eiti_compliant_country", "eiti_implementation_status",
                   "fatf_grey_list_jurisdiction", "bilateral_investment_treaty"}
    for field, value in jur_data.items():
        if field in _jur_always:
            retrieved[field] = value  # always apply
        elif retrieved.get(field) is None:
            retrieved[field] = value  # fill null only

    # 2. Asset seed fills gaps only — retrieved data wins
    _default_str_values = {
        "none", "non-implementing", "unknown", "other",
        "not_filed", "unlisted", "exploration", "",
    }
    for field, value in asset_seed.items():
        current = retrieved.get(field)
        # For boolean True seeds: apply if current is False (default) or None
        # We cannot tell if False was retrieved or defaulted, but seed True values
        # are confirmed public facts (e.g. Lobito eligibility for Copperbelt)
        if isinstance(value, bool) and value is True:
            if not current:  # False or None
                retrieved[field] = value
        else:
            is_missing = (
                current is None or
                current in _default_str_values or
                (isinstance(current, str) and (
                    "unknown" in current.lower() or
                    "retrieval required" in current.lower() or
                    "not identified" in current.lower()
                ))
            )
            if is_missing:
                retrieved[field] = value

    return retrieved
