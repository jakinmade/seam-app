"""
SEAM Known Assets Registry
Comprehensive seed data for deterministic retrieval across Africa.

TWO LAYERS:

1. JURISDICTION DATA — static annual publication values for all SEAM jurisdictions.
   Fraser Index, World Bank WGI, EITI status, FATF, BIT.
   Applied to EVERY asset in that jurisdiction, always.
   Sources: Fraser Institute Annual Survey 2024, World Bank WGI 2023,
            EITI country pages, FATF public statement 2025, UNCTAD BIT database 2024.

2. ASSET DATA — confirmed facts for named African mining assets.
   Commodity, operator, stage, Lobito eligibility, listed vehicle.
   Applied where asset name matches. Does not overwrite retrieved data.
"""

# ── JURISDICTION STATIC DATA ─────────────────────────────────────────────

JURISDICTION_DATA: dict = {

    "ZMB": {  # Zambia
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 51.2,
        "wb_rule_of_law_percentile": 30.3,
        "wb_regulatory_quality_percentile": 33.7,
    },
    "GHA": {  # Ghana
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 62.4,
        "wb_rule_of_law_percentile": 47.6,
        "wb_regulatory_quality_percentile": 50.2,
    },
    "TZA": {  # Tanzania
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 44.8,
        "wb_rule_of_law_percentile": 35.6,
        "wb_regulatory_quality_percentile": 38.2,
    },
    "BWA": {  # Botswana
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 68.3,
        "wb_rule_of_law_percentile": 63.5,
        "wb_regulatory_quality_percentile": 60.1,
    },
    "NAM": {  # Namibia
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 57.6,
        "wb_rule_of_law_percentile": 56.3,
        "wb_regulatory_quality_percentile": 54.8,
    },
    "COD": {  # DRC
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 28.4,
        "wb_rule_of_law_percentile": 4.3,
        "wb_regulatory_quality_percentile": 6.7,
    },
    "GIN": {  # Guinea
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 35.2,
        "wb_rule_of_law_percentile": 14.9,
        "wb_regulatory_quality_percentile": 17.3,
    },
    "ZWE": {  # Zimbabwe
        "eiti_compliant_country": False,
        "eiti_implementation_status": "candidate",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 22.1,
        "wb_rule_of_law_percentile": 12.0,
        "wb_regulatory_quality_percentile": 10.6,
    },
    "MOZ": {  # Mozambique
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 38.9,
        "wb_rule_of_law_percentile": 21.6,
        "wb_regulatory_quality_percentile": 24.5,
    },
    "CIV": {  # Côte d'Ivoire
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 59.1,
        "wb_rule_of_law_percentile": 36.1,
        "wb_regulatory_quality_percentile": 41.3,
    },
    "ZAF": {  # South Africa
        "eiti_compliant_country": False,
        "eiti_implementation_status": "non-implementing",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 41.3,
        "wb_rule_of_law_percentile": 52.9,
        "wb_regulatory_quality_percentile": 54.1,
    },
    "MLI": {  # Mali
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 32.7,
        "wb_rule_of_law_percentile": 11.5,
        "wb_regulatory_quality_percentile": 18.4,
    },
    "BFA": {  # Burkina Faso
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 29.8,
        "wb_rule_of_law_percentile": 13.0,
        "wb_regulatory_quality_percentile": 22.1,
    },
    "SEN": {  # Senegal
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 48.6,
        "wb_rule_of_law_percentile": 43.8,
        "wb_regulatory_quality_percentile": 45.2,
    },
    "MRT": {  # Mauritania
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 40.1,
        "wb_rule_of_law_percentile": 22.6,
        "wb_regulatory_quality_percentile": 28.3,
    },
    "NGA": {  # Nigeria
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 24.3,
        "wb_rule_of_law_percentile": 8.2,
        "wb_regulatory_quality_percentile": 16.7,
    },
    "ETH": {  # Ethiopia
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 31.4,
        "wb_rule_of_law_percentile": 15.9,
        "wb_regulatory_quality_percentile": 21.2,
    },
    "KEN": {  # Kenya
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 43.7,
        "wb_rule_of_law_percentile": 34.1,
        "wb_regulatory_quality_percentile": 42.8,
    },
    "UGA": {  # Uganda
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 36.2,
        "wb_rule_of_law_percentile": 19.7,
        "wb_regulatory_quality_percentile": 29.4,
    },
    "RWA": {  # Rwanda
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 53.8,
        "wb_rule_of_law_percentile": 55.8,
        "wb_regulatory_quality_percentile": 58.2,
    },
    "AGO": {  # Angola
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 27.6,
        "wb_rule_of_law_percentile": 16.3,
        "wb_regulatory_quality_percentile": 19.8,
    },
    "CMR": {  # Cameroon
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 30.5,
        "wb_rule_of_law_percentile": 18.4,
        "wb_regulatory_quality_percentile": 22.7,
    },
    "MDG": {  # Madagascar
        "eiti_compliant_country": True,
        "eiti_implementation_status": "compliant",
        "fatf_grey_list_jurisdiction": False,
        "bilateral_investment_treaty": True,
        "fraser_investment_attractiveness": 33.1,
        "wb_rule_of_law_percentile": 20.2,
        "wb_regulatory_quality_percentile": 26.4,
    },
    "ZMB_LOBITO": None,  # placeholder — Lobito eligibility handled in asset data
}


# ── ASSET SEED DATA ──────────────────────────────────────────────────────
# Keys are lowercase search terms — substring matching used
# Only stable confirmed public facts. No scores, no financial metrics.

ASSET_DATA: dict = {

    # ── ZAMBIA ──────────────────────────────────────────────────────────
    "kcm":              {"asset_name": "Konkola Copper Mines Plc",      "operator": "Vedanta Resources",         "commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_u50km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 1800.0},
    "konkola":          {"asset_name": "Konkola Copper Mines Plc",      "operator": "Vedanta Resources",         "commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_u50km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 1800.0},
    "lumwana":          {"asset_name": "Lumwana Copper Mine",           "operator": "Barrick Gold Corporation",  "commodity": "Copper",    "province": "North-Western Province",  "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZMB", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_50_200km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 2200.0},
    "kansanshi":        {"asset_name": "Kansanshi Copper-Gold Mine",    "operator": "First Quantum Minerals",    "commodity": "Copper",    "province": "North-Western Province",  "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZMB", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_u50km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 2200.0},
    "mingomba":         {"asset_name": "Mingomba Copper Project",       "operator": "KoBold Metals",             "commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "exploration",  "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB", "beneficial_ownership_disclosure": "partial", "road_access": "paved_u50km", "port_distance_km": 1800.0},
    "nchanga":          {"asset_name": "Nchanga Copper Mine",           "operator": "Zambia Consolidated Copper","commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB"},
    "mufulira":         {"asset_name": "Mufulira Copper Mine",          "operator": "Mopani Copper Mines",       "commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB"},
    "mopani":           {"asset_name": "Mopani Copper Mines",           "operator": "Mopani Copper Mines",       "commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_u50km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 1800.0},
    "sentinel":         {"asset_name": "Sentinel Copper Mine",          "operator": "First Quantum Minerals",    "commodity": "Copper",    "province": "North-Western Province",  "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZMB", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_50_200km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 2200.0},
    "enterprise":       {"asset_name": "Enterprise Nickel Project",     "operator": "First Quantum Minerals",    "commodity": "Nickel",    "province": "North-Western Province",  "exploration_stage": "development",  "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB"},
    "munali":           {"asset_name": "Munali Nickel Mine",            "operator": "Consolidated Nickel Mines", "commodity": "Nickel",    "province": "Southern Province",       "exploration_stage": "producing",    "jurisdiction_code": "ZMB"},
    "zccm":             {"asset_name": "ZCCM-IH Portfolio",             "operator": "ZCCM-IH",                   "commodity": "Copper",    "province": "Copperbelt Province",     "exploration_stage": "producing",    "lobito_corridor_eligible": True,  "jurisdiction_code": "ZMB"},

    # ── DRC ─────────────────────────────────────────────────────────────
    "kamoa":            {"asset_name": "Kamoa-Kakula Copper Complex",   "operator": "Ivanhoe Mines",             "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "COD", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "foreign_jv", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_50_200km", "rail_access": "rail_o100km", "water_supply": "permitted_documented", "port_distance_km": 2500.0},
    "kakula":           {"asset_name": "Kamoa-Kakula Copper Complex",   "operator": "Ivanhoe Mines",             "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "COD", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "foreign_jv", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_50_200km", "rail_access": "rail_o100km", "water_supply": "permitted_documented", "port_distance_km": 2500.0},
    "tenke fungurume":  {"asset_name": "Tenke Fungurume Mine",          "operator": "CMOC Group",                "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "jurisdiction_code": "COD", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "tenke":            {"asset_name": "Tenke Fungurume Mine",          "operator": "CMOC Group",                "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "jurisdiction_code": "COD", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "mutanda":          {"asset_name": "Mutanda Mining",                "operator": "Glencore",                  "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "COD", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "kamoto":           {"asset_name": "Kamoto Copper Company",         "operator": "Glencore",                  "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "COD"},
    "ivanhoe":          {"asset_name": "Kamoa-Kakula Copper Complex",   "operator": "Ivanhoe Mines",             "commodity": "Copper",    "province": "Lualaba Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "COD"},
    "twangiza":         {"asset_name": "Twangiza Gold Mine",            "operator": "Banro Corporation",         "commodity": "Gold",      "province": "South Kivu Province",     "exploration_stage": "producing",    "jurisdiction_code": "COD"},
    "kibali":           {"asset_name": "Kibali Gold Mine",              "operator": "Barrick Gold / AngloGold",  "commodity": "Gold",      "province": "Haut-Uele Province",      "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "COD", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── GHANA ────────────────────────────────────────────────────────────
    "obuasi":           {"asset_name": "Obuasi Gold Mine",              "operator": "AngloGold Ashanti",         "commodity": "Gold",      "province": "Ashanti Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_u50km", "rail_access": "operating_capacity_constrained", "water_supply": "permitted_documented", "port_distance_km": 250.0},
    "ahafo":            {"asset_name": "Ahafo Gold Mine",               "operator": "Newmont Corporation",       "commodity": "Gold",      "province": "Brong-Ahafo Region",      "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "akyem":            {"asset_name": "Akyem Gold Mine",               "operator": "Newmont Corporation",       "commodity": "Gold",      "province": "Eastern Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "bonikro":          {"asset_name": "Bonikro Gold Mine",             "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Central Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA"},
    "asanko":           {"asset_name": "Asanko Gold Mine",              "operator": "Galiano Gold / Gold Fields","commodity": "Gold",      "province": "Ashanti Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "chirano":          {"asset_name": "Chirano Gold Mine",             "operator": "Kinross Gold",              "commodity": "Gold",      "province": "Western Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "edikan":           {"asset_name": "Edikan Gold Mine",              "operator": "Perseus Mining",            "commodity": "Gold",      "province": "Central Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GHA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── TANZANIA ─────────────────────────────────────────────────────────
    "geita":            {"asset_name": "Geita Gold Mine",               "operator": "AngloGold Ashanti",         "commodity": "Gold",      "province": "Geita Region",            "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "TZA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m", "licence_holder_status": "citizen_empowered", "beneficial_ownership_disclosure": "partial", "locas_filing_status": "submitted_unverified", "power_supply": "grid_no_redundancy", "road_access": "paved_50_200km", "water_supply": "permitted_documented", "port_distance_km": 110.0},
    "north mara":       {"asset_name": "North Mara Gold Mine",          "operator": "Barrick Gold",              "commodity": "Gold",      "province": "Mara Region",             "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "TZA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "bulyanhulu":       {"asset_name": "Bulyanhulu Gold Mine",          "operator": "Barrick Gold",              "commodity": "Gold",      "province": "Shinyanga Region",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "TZA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "buzwagi":          {"asset_name": "Buzwagi Gold Mine",             "operator": "Barrick Gold",              "commodity": "Gold",      "province": "Shinyanga Region",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "TZA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "mahenge":          {"asset_name": "Mahenge Graphite Project",      "operator": "Magnis Energy Technologies","commodity": "Graphite",  "province": "Morogoro Region",         "exploration_stage": "development",  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "TZA"},
    "epanko":           {"asset_name": "Epanko Graphite Project",       "operator": "EcoGraf",                   "commodity": "Graphite",  "province": "Ulanga District",         "exploration_stage": "development",  "jurisdiction_code": "TZA"},
    "kabanga":          {"asset_name": "Kabanga Nickel Project",        "operator": "Kabanga Nickel",            "commodity": "Nickel",    "province": "Kagera Region",           "exploration_stage": "development",  "jurisdiction_code": "TZA"},
    "nyanzaga":         {"asset_name": "Nyanzaga Gold Project",         "operator": "Perseus Mining",            "commodity": "Gold",      "province": "Mwanza Region",           "exploration_stage": "development",  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "TZA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── NAMIBIA ──────────────────────────────────────────────────────────
    "husab":            {"asset_name": "Husab Uranium Mine",            "operator": "Swakop Uranium",            "commodity": "Uranium",   "province": "Erongo Region",           "exploration_stage": "producing",    "jurisdiction_code": "NAM", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "rossing":          {"asset_name": "Rossing Uranium Mine",          "operator": "China National Uranium",    "commodity": "Uranium",   "province": "Erongo Region",           "exploration_stage": "producing",    "jurisdiction_code": "NAM", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "rosh pinah":       {"asset_name": "Rosh Pinah Zinc Mine",          "operator": "Trevali Mining",            "commodity": "Zinc",      "province": "Karas Region",            "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "NAM", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "otjikoto":         {"asset_name": "Otjikoto Gold Mine",            "operator": "B2Gold Corporation",        "commodity": "Gold",      "province": "Otjozondjupa Region",     "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "NAM", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "navachab":         {"asset_name": "Navachab Gold Mine",            "operator": "QKR Corporation",           "commodity": "Gold",      "province": "Erongo Region",           "exploration_stage": "producing",    "jurisdiction_code": "NAM"},
    "brandberg":        {"asset_name": "Brandberg West Tungsten",       "operator": "Namibia Critical Metals",   "commodity": "Tungsten",  "province": "Kunene Region",           "exploration_stage": "exploration",  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "NAM"},
    "tses":             {"asset_name": "Tses Copper Project",           "operator": "Xemplar Energy",            "commodity": "Copper",    "province": "Hardap Region",           "exploration_stage": "exploration",  "jurisdiction_code": "NAM"},

    # ── BOTSWANA ─────────────────────────────────────────────────────────
    "jwaneng":          {"asset_name": "Jwaneng Diamond Mine",          "operator": "Debswana",                  "commodity": "Diamonds",  "province": "Southern District",       "exploration_stage": "producing",    "jurisdiction_code": "BWA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "orapa":            {"asset_name": "Orapa Diamond Mine",            "operator": "Debswana",                  "commodity": "Diamonds",  "province": "Central District",        "exploration_stage": "producing",    "jurisdiction_code": "BWA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "letlhakane":       {"asset_name": "Letlhakane Diamond Mine",       "operator": "Debswana",                  "commodity": "Diamonds",  "province": "Central District",        "exploration_stage": "producing",    "jurisdiction_code": "BWA"},
    "selebi-phikwe":    {"asset_name": "Selebi-Phikwe Nickel Mine",     "operator": "BCL Ltd",                   "commodity": "Nickel",    "province": "Central District",        "exploration_stage": "producing",    "jurisdiction_code": "BWA"},
    "motheo":           {"asset_name": "Motheo Copper Mine",            "operator": "Sandfire Resources",        "commodity": "Copper",    "province": "Western District",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BWA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "t3":               {"asset_name": "T3 Copper Project",             "operator": "Sandfire Resources",        "commodity": "Copper",    "province": "Western District",        "exploration_stage": "development",  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BWA"},

    # ── GUINEA ───────────────────────────────────────────────────────────
    "simandou":         {"asset_name": "Simandou Iron Ore Project",     "operator": "Rio Tinto / SMB-Winning",   "commodity": "Iron Ore",  "province": "Nzérékoré Prefecture",   "exploration_stage": "development",  "jurisdiction_code": "GIN"},
    "sangaredi":        {"asset_name": "Sangarédi Bauxite Mine",        "operator": "Compagnie des Bauxites",    "commodity": "Bauxite",   "province": "Boké Prefecture",         "exploration_stage": "producing",    "jurisdiction_code": "GIN"},
    "boke":             {"asset_name": "Boké Bauxite Operations",       "operator": "SMB-Winning",               "commodity": "Bauxite",   "province": "Boké Prefecture",         "exploration_stage": "producing",    "jurisdiction_code": "GIN"},
    "fria":             {"asset_name": "Friguia Alumina Refinery",      "operator": "Rusal",                     "commodity": "Bauxite",   "province": "Kindia Prefecture",       "exploration_stage": "producing",    "jurisdiction_code": "GIN"},
    "lefa":             {"asset_name": "Lefa Gold Mine",                "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Siguiri Prefecture",      "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GIN", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "siguiri":          {"asset_name": "Siguiri Gold Mine",             "operator": "AngloGold Ashanti",         "commodity": "Gold",      "province": "Kankan Region",           "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "GIN", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── ZIMBABWE ─────────────────────────────────────────────────────────
    "zimplats":         {"asset_name": "Zimplats",                      "operator": "Implats",                   "commodity": "Platinum",  "province": "Mashonaland West",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZWE", "resource_estimate_standard": "samrec", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "mimosa":           {"asset_name": "Mimosa Platinum Mine",          "operator": "Implats / Sibanye",         "commodity": "Platinum",  "province": "Midlands Province",       "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZWE", "resource_estimate_standard": "samrec", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "ngezi":            {"asset_name": "Ngezi Platinum Mine",           "operator": "Zimplats",                  "commodity": "Platinum",  "province": "Mashonaland West",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZWE"},
    "blanket":          {"asset_name": "Blanket Gold Mine",             "operator": "Caledonia Mining",          "commodity": "Gold",      "province": "Matabeleland South",      "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZWE", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "sabi star":        {"asset_name": "Sabi Star Lithium Mine",        "operator": "Prospect Resources",        "commodity": "Lithium",   "province": "Manicaland Province",     "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZWE"},
    "arcadia":          {"asset_name": "Arcadia Lithium Project",       "operator": "Huayou Cobalt",             "commodity": "Lithium",   "province": "Mashonaland East",        "exploration_stage": "producing",    "jurisdiction_code": "ZWE"},

    # ── MOZAMBIQUE ───────────────────────────────────────────────────────
    "moatize":          {"asset_name": "Moatize Coal Mine",             "operator": "Vale / Vulcan Minerals",    "commodity": "Coal",      "province": "Tete Province",           "exploration_stage": "producing",    "jurisdiction_code": "MOZ"},
    "benga":            {"asset_name": "Benga Coal Project",            "operator": "Vulcan Minerals",           "commodity": "Coal",      "province": "Tete Province",           "exploration_stage": "producing",    "jurisdiction_code": "MOZ"},
    "montepuez":        {"asset_name": "Montepuez Ruby Mining",         "operator": "Gemfields",                 "commodity": "Rubies",    "province": "Cabo Delgado Province",   "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MOZ"},
    "tete coal":        {"asset_name": "Tete Coal Basin",               "operator": "Various",                   "commodity": "Coal",      "province": "Tete Province",           "exploration_stage": "producing",    "jurisdiction_code": "MOZ"},

    # ── SOUTH AFRICA ─────────────────────────────────────────────────────
    "rustenburg":       {"asset_name": "Rustenburg Platinum Mines",     "operator": "Anglo American Platinum",   "commodity": "Platinum",  "province": "North West Province",     "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF", "resource_estimate_standard": "samrec", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "mogalakwena":      {"asset_name": "Mogalakwena Platinum Mine",     "operator": "Anglo American Platinum",   "commodity": "Platinum",  "province": "Limpopo Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF"},
    "impala":           {"asset_name": "Impala Platinum Mines",         "operator": "Implats",                   "commodity": "Platinum",  "province": "North West Province",     "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF"},
    "kumba":            {"asset_name": "Kumba Iron Ore",                "operator": "Anglo American",            "commodity": "Iron Ore",  "province": "Northern Cape",           "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF"},
    "sishen":           {"asset_name": "Sishen Iron Ore Mine",          "operator": "Kumba Iron Ore",            "commodity": "Iron Ore",  "province": "Northern Cape",           "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF", "resource_estimate_standard": "samrec", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "mponeng":          {"asset_name": "Mponeng Gold Mine",             "operator": "AngloGold Ashanti",         "commodity": "Gold",      "province": "Gauteng Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF", "resource_estimate_standard": "samrec", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "south deep":       {"asset_name": "South Deep Gold Mine",          "operator": "Gold Fields",               "commodity": "Gold",      "province": "Gauteng Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF", "resource_estimate_standard": "samrec", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "driefontein":      {"asset_name": "Driefontein Gold Mine",         "operator": "Sibanye Stillwater",        "commodity": "Gold",      "province": "Gauteng Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF"},
    "kloof":            {"asset_name": "Kloof Gold Mine",               "operator": "Sibanye Stillwater",        "commodity": "Gold",      "province": "Gauteng Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF"},
    "nkomati":          {"asset_name": "Nkomati Nickel Mine",           "operator": "Norilsk Nickel / ARM",      "commodity": "Nickel",    "province": "Mpumalanga Province",     "exploration_stage": "producing",    "jurisdiction_code": "ZAF"},
    "qala shallows":    {"asset_name": "Qala Shallows Gold Mine",       "operator": "West Wits Mining",          "commodity": "Gold",      "province": "Gauteng Province",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ZAF"},

    # ── MALI ─────────────────────────────────────────────────────────────
    "loulo":            {"asset_name": "Loulo-Gounkoto Gold Complex",   "operator": "Barrick Gold",              "commodity": "Gold",      "province": "Kayes Region",            "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MLI", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "morila":           {"asset_name": "Morila Gold Mine",              "operator": "Firefinch / Robex",         "commodity": "Gold",      "province": "Sikasso Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MLI"},
    "syama":            {"asset_name": "Syama Gold Mine",               "operator": "Resolute Mining",           "commodity": "Gold",      "province": "Sikasso Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MLI", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "fekola":           {"asset_name": "Fekola Gold Mine",              "operator": "B2Gold Corporation",        "commodity": "Gold",      "province": "Kayes Region",            "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MLI", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── BURKINA FASO ─────────────────────────────────────────────────────
    "essakane":         {"asset_name": "Essakane Gold Mine",            "operator": "IAMGOLD Corporation",      "commodity": "Gold",      "province": "Sahel Region",            "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BFA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "mana":             {"asset_name": "Mana Gold Mine",                "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Boucle du Mouhoun",       "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BFA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "houndé":           {"asset_name": "Houndé Gold Mine",              "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Hauts-Bassins Region",    "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BFA", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "boungou":          {"asset_name": "Boungou Gold Mine",             "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Est Region",              "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BFA"},
    "wahgnion":         {"asset_name": "Wahgnion Gold Mine",            "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Sud-Ouest Region",        "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "BFA"},

    # ── CÔTE D'IVOIRE ────────────────────────────────────────────────────
    "tongon":           {"asset_name": "Tongon Gold Mine",              "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Hambol Region",           "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "CIV", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "ity":              {"asset_name": "Ity Gold Mine",                 "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Dix-Huit Montagnes",      "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "CIV", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "agbaou":           {"asset_name": "Agbaou Gold Mine",              "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Marahoué Region",         "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "CIV"},
    "sissingué":        {"asset_name": "Sissingué Gold Mine",           "operator": "Perseus Mining",            "commodity": "Gold",      "province": "Hambol Region",           "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "CIV", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "yaouré":           {"asset_name": "Yaouré Gold Mine",              "operator": "Perseus Mining",            "commodity": "Gold",      "province": "Lacs Region",             "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "CIV", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── SENEGAL ──────────────────────────────────────────────────────────
    "sabodala":         {"asset_name": "Sabodala-Massawa Gold Complex", "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Kédougou Region",         "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "SEN", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "teranga":          {"asset_name": "Sabodala Gold Mine",            "operator": "Endeavour Mining",          "commodity": "Gold",      "province": "Kédougou Region",         "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "SEN"},

    # ── MAURITANIA ───────────────────────────────────────────────────────
    "tasiast":          {"asset_name": "Tasiast Gold Mine",             "operator": "Kinross Gold",              "commodity": "Gold",      "province": "Inchiri Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MRT", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "guelb moghrein":   {"asset_name": "Guelb Moghrein Copper Mine",    "operator": "Mauritanian Copper Mines",  "commodity": "Copper",    "province": "Inchiri Region",          "exploration_stage": "producing",    "jurisdiction_code": "MRT"},

    # ── MADAGASCAR ───────────────────────────────────────────────────────
    "ambatovy":         {"asset_name": "Ambatovy Nickel Mine",          "operator": "Sherritt International",    "commodity": "Nickel",    "province": "Toamasina Province",      "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MDG", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},
    "qmm":              {"asset_name": "QMM Mineral Sands",             "operator": "Rio Tinto",                 "commodity": "Mineral Sands","province": "Anosy Region",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "MDG"},

    # ── ANGOLA ───────────────────────────────────────────────────────────
    "catoca":           {"asset_name": "Catoca Diamond Mine",           "operator": "Endiama / Alrosa",          "commodity": "Diamonds",  "province": "Lunda Sul Province",      "exploration_stage": "producing",    "jurisdiction_code": "AGO", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── KENYA ────────────────────────────────────────────────────────────
    "kwale":            {"asset_name": "Kwale Mineral Sands Mine",      "operator": "Base Resources",            "commodity": "Mineral Sands","province": "Kwale County",          "exploration_stage": "producing",    "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "KEN", "resource_estimate_standard": "ni43101_jorc_u3y", "reserve_classification": "proven_probable", "production_data_availability": "current_u12m"},

    # ── ETHIOPIA ─────────────────────────────────────────────────────────
    "tulu kapi":        {"asset_name": "Tulu Kapi Gold Project",        "operator": "KEFI Gold and Copper",      "commodity": "Gold",      "province": "Oromia Region",           "exploration_stage": "development",  "listed_vehicle": "asx_tsx_aim_active", "jurisdiction_code": "ETH"},

    # ── RWANDA ───────────────────────────────────────────────────────────
    "bugarama":         {"asset_name": "Bugarama Tin Mine",             "operator": "Rwanda Mines",              "commodity": "Tin",       "province": "Western Province",        "exploration_stage": "producing",    "jurisdiction_code": "RWA"},
}

# Remove placeholder
del JURISDICTION_DATA["ZMB_LOBITO"]


# ── PUBLIC INTERFACE ──────────────────────────────────────────────────────

def get_jurisdiction_data(jurisdiction_code: str) -> dict:
    return dict(JURISDICTION_DATA.get(jurisdiction_code.upper(), {}))


def get_asset_seed(asset_name: str) -> dict:
    name_lower = asset_name.lower().strip()
    if name_lower in ASSET_DATA:
        return dict(ASSET_DATA[name_lower])
    for key, data in ASSET_DATA.items():
        if key in name_lower or name_lower in key:
            return dict(data)
    return {}


def apply_seeds(retrieved: dict, asset_name: str, jurisdiction_code: str) -> dict:
    jur_data   = get_jurisdiction_data(jurisdiction_code)
    asset_seed = get_asset_seed(asset_name)

    # Jurisdiction boolean/status fields always apply
    _jur_always = {"eiti_compliant_country", "eiti_implementation_status",
                   "fatf_grey_list_jurisdiction", "bilateral_investment_treaty"}
    for field, value in jur_data.items():
        if field in _jur_always:
            retrieved[field] = value
        elif retrieved.get(field) is None:
            retrieved[field] = value

    # Asset seed: boolean True always applies; strings fill gaps only
    _default_str = {"none","non-implementing","unknown","other","not_filed","unlisted","exploration",""}
    for field, value in asset_seed.items():
        if field == "jurisdiction_code":
            continue
        if isinstance(value, bool) and value is True:
            if not retrieved.get(field):
                retrieved[field] = value
        else:
            current = retrieved.get(field)
            is_missing = (
                current is None or
                current in _default_str or
                (isinstance(current, str) and (
                    "unknown" in current.lower() or
                    "retrieval required" in current.lower() or
                    "not identified" in current.lower()
                ))
            )
            if is_missing:
                retrieved[field] = value

    return retrieved


