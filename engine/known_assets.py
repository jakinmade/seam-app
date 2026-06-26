"""
SEAM Known Assets Registry
Pre-loaded facts for well-documented African mining assets.

These are publicly verifiable facts that do not change run-to-run.
They seed the retrieval layer so the web search enriches rather than replaces.

Every entry here must be verifiable from a named public source.
If in doubt, leave it out — the retrieval layer will find it or default conservatively.
"""

# Structure: asset_name_lower -> dict of confirmed fields
# Fields match AssetInput field names exactly.
# Only include fields that are stable public facts.

KNOWN_ASSETS: dict = {

    "kcm": {
        "asset_name": "Konkola Copper Mines Plc",
        "operator": "Vedanta Resources",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "commodity": "Copper",
        "province": "Copperbelt Province",
        "exploration_stage": "producing",
        "lobito_corridor_eligible": True,
        "_sources": {
            "asset_name": "Vedanta Resources annual report / Companies House Zambia",
            "commodity": "USGS Minerals Yearbook — Zambia",
            "exploration_stage": "Vedanta Resources production report 2024",
            "lobito_corridor_eligible": "Lobito Corridor project registry — Copperbelt Province eligible",
        }
    },

    "konkola": {
        "asset_name": "Konkola Copper Mines Plc",
        "operator": "Vedanta Resources",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "commodity": "Copper",
        "province": "Copperbelt Province",
        "exploration_stage": "producing",
        "lobito_corridor_eligible": True,
        "_sources": {
            "commodity": "USGS Minerals Yearbook — Zambia",
            "exploration_stage": "Vedanta Resources production report 2024",
        }
    },

    "lumwana": {
        "asset_name": "Lumwana Copper Mine",
        "operator": "Barrick Gold Corporation",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "commodity": "Copper",
        "province": "North-Western Province",
        "exploration_stage": "producing",
        "lobito_corridor_eligible": True,
        "resource_estimate_standard": "ni43101_jorc_u3y",
        "reserve_classification": "proven_probable",
        "production_data_availability": "current_u12m",
        "listed_vehicle": "asx_tsx_aim_active",
        "_sources": {
            "operator": "Barrick Gold 2024 Annual Report",
            "commodity": "USGS Minerals Yearbook — Zambia",
            "resource_estimate_standard": "Barrick Gold NI 43-101 Technical Report 2023",
            "listed_vehicle": "TSX: ABX / NYSE: GOLD",
        }
    },

    "kamoa": {
        "asset_name": "Kamoa-Kakula Copper Complex",
        "operator": "Ivanhoe Mines / Zijin Mining",
        "jurisdiction": "DRC",
        "jurisdiction_code": "COD",
        "commodity": "Copper",
        "province": "Lualaba Province",
        "exploration_stage": "producing",
        "resource_estimate_standard": "ni43101_jorc_u3y",
        "reserve_classification": "proven_probable",
        "production_data_availability": "current_u12m",
        "listed_vehicle": "asx_tsx_aim_active",
        "_sources": {
            "operator": "Ivanhoe Mines press release 2024",
            "resource_estimate_standard": "Ivanhoe Mines NI 43-101 Technical Report 2023",
            "listed_vehicle": "TSX: IVN",
        }
    },

    "kamoa-kakula": {
        "asset_name": "Kamoa-Kakula Copper Complex",
        "operator": "Ivanhoe Mines / Zijin Mining",
        "jurisdiction": "DRC",
        "jurisdiction_code": "COD",
        "commodity": "Copper",
        "province": "Lualaba Province",
        "exploration_stage": "producing",
        "resource_estimate_standard": "ni43101_jorc_u3y",
        "reserve_classification": "proven_probable",
        "production_data_availability": "current_u12m",
        "listed_vehicle": "asx_tsx_aim_active",
        "_sources": {}
    },

    "mingomba": {
        "asset_name": "Mingomba Copper Project",
        "operator": "KoBold Metals",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "commodity": "Copper",
        "province": "Copperbelt Province",
        "exploration_stage": "exploration",
        "lobito_corridor_eligible": True,
        "_sources": {
            "operator": "KoBold Metals press release 2023",
            "commodity": "USGS / KoBold exploration announcement",
        }
    },

    "kansanshi": {
        "asset_name": "Kansanshi Copper-Gold Mine",
        "operator": "First Quantum Minerals",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "commodity": "Copper",
        "province": "North-Western Province",
        "exploration_stage": "producing",
        "resource_estimate_standard": "ni43101_jorc_u3y",
        "reserve_classification": "proven_probable",
        "production_data_availability": "current_u12m",
        "listed_vehicle": "asx_tsx_aim_active",
        "lobito_corridor_eligible": True,
        "_sources": {
            "operator": "First Quantum Minerals 2024 Annual Report",
            "listed_vehicle": "TSX: FM",
        }
    },

    "obuasi": {
        "asset_name": "Obuasi Gold Mine",
        "operator": "AngloGold Ashanti",
        "jurisdiction": "Ghana",
        "jurisdiction_code": "GHA",
        "commodity": "Gold",
        "province": "Ashanti Region",
        "exploration_stage": "producing",
        "resource_estimate_standard": "ni43101_jorc_u3y",
        "reserve_classification": "proven_probable",
        "production_data_availability": "current_u12m",
        "listed_vehicle": "asx_tsx_aim_active",
        "_sources": {
            "operator": "AngloGold Ashanti 2024 Annual Report",
            "listed_vehicle": "NYSE: AU / JSE: ANG",
        }
    },
}


# Known jurisdiction-level facts — applied before web search for any asset in that jurisdiction
KNOWN_JURISDICTIONS: dict = {

    "ZMB": {
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "_sources": {
            "eiti_compliant_country": "EITI — eiti.org/countries/zambia (compliant since 2012)",
            "fatf_grey_list_jurisdiction": "FATF public statement June 2025",
            "bilateral_investment_treaty": "UNCTAD BIT database — Zambia has 18 BITs in force",
        }
    },

    "GHA": {
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "_sources": {
            "eiti_compliant_country": "EITI — eiti.org/countries/ghana (compliant since 2010)",
        }
    },

    "TZA": {
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "_sources": {
            "eiti_compliant_country": "EITI — eiti.org/countries/tanzania (compliant since 2012)",
        }
    },

    "BWA": {
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "_sources": {
            "eiti_compliant_country": "EITI — eiti.org/countries/botswana (compliant since 2012)",
        }
    },

    "NAM": {
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "_sources": {
            "eiti_compliant_country": "EITI — eiti.org/countries/namibia",
        }
    },

    "COD": {
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "_sources": {
            "eiti_compliant_country": "EITI — eiti.org/countries/drc (compliant since 2014)",
        }
    },
}


def get_known_asset_seed(asset_name: str) -> dict:
    """
    Return known facts for a named asset.
    Matches on asset name substring (case-insensitive).
    Returns empty dict if no match found.
    """
    name_lower = asset_name.lower().strip()

    # Exact key match first
    if name_lower in KNOWN_ASSETS:
        return {k: v for k, v in KNOWN_ASSETS[name_lower].items() if not k.startswith("_")}

    # Substring match
    for key, data in KNOWN_ASSETS.items():
        if key in name_lower or name_lower in key:
            return {k: v for k, v in data.items() if not k.startswith("_")}

    return {}


def get_known_jurisdiction_seed(jurisdiction_code: str) -> dict:
    """Return known jurisdiction-level facts."""
    data = KNOWN_JURISDICTIONS.get(jurisdiction_code.upper(), {})
    return {k: v for k, v in data.items() if not k.startswith("_")}
