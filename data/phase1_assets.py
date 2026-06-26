"""
SEAM Phase 1 — Pre-loaded Asset Data
Three Zambian assets for initial scoring validation.

Data sourced manually from:
- EITI Zambia 2023 Report
- USGS Zambia Geodatabase
- Fraser Institute Annual Survey 2025
- World Bank WGI 2024
- Zambia MRC LOCAS Portal (public data)
- ASX/TSX/AIM public filings
- Company public disclosures (supplementary only)

All fields represent publicly available data at time of loading.
"""

from engine.scoring import AssetInput


# ---------------------------------------------------------------------------
# ASSET 1 — KCM / CopperTech (Konkola Copper Mines)
# Copperbelt Province, Zambia
# One of Zambia's largest copper producers. Complex ownership history.
# Reverted to ZCCM-IH / Zambian state after Vedanta dispute.
# ---------------------------------------------------------------------------

KCM = AssetInput(
    asset_id="ZMB-001",
    asset_name="Konkola Copper Mines (KCM / CopperTech)",
    jurisdiction="Zambia",
    jurisdiction_code="ZMB",
    commodity="Copper",
    province="Copperbelt",

    # D1 — Jurisdiction Stability
    # Zambia Fraser IAI 2025: 47.3 (mid-tier, down from prior years)
    # WB Governance 2023: Rule of Law 36th percentile, Reg Quality 41st percentile
    fraser_investment_attractiveness=47.3,
    wb_rule_of_law_percentile=36.0,
    wb_regulatory_quality_percentile=41.0,
    regulatory_change_last_12m=True,     # New mining royalty SI gazetted 2025
    mining_code_revision_in_progress=True,  # Mines and Minerals Act review ongoing
    investment_arbitration_last_5y=True,  # Vedanta arbitration 2023
    bilateral_investment_treaty=True,     # UK-Zambia BIT in force
    eiti_compliant_country=True,          # Zambia EITI compliant

    # D2 — Revenue Transparency
    eiti_implementation_status="compliant",
    beneficial_ownership_disclosure="partial",   # ZCCM-IH disclosed, minority unclear
    eiti_payment_disclosure_quality=68.0,        # EITI Zambia 2023 validation score
    pep_in_ownership_chain=False,
    fatf_grey_list_jurisdiction=False,
    payment_data_gap_over_24m=False,

    # D3 — Asset Data Quality
    resource_estimate_standard="ni43101_jorc_o3y",  # Last NI43-101 > 3 years old
    reserve_classification="proven_probable",
    production_data_availability="current_u12m",
    exploration_stage="producing",
    unresolved_resource_conflict=True,   # USGS vs government gazette conflict on reserve estimate
    estimate_by_company_employee=False,
    no_independent_technical_report=False,

    # D4 — Local Content (SI68 baseline)
    licence_holder_status="citizen_owned",  # ZCCM-IH majority post-reversion
    locas_filing_status="submitted_verified",
    local_procurement_evidence="effort_sub_20pct",
    supplier_development_programme="in_development",
    reserved_services_non_local=False,

    # D5 — Infrastructure Readiness
    power_supply="grid_no_redundancy",     # ZESCO connected, load shedding risk
    road_access="paved_u50km",
    rail_access="operating_capacity_constrained",  # TAZARA operational but constrained
    water_supply="permitted_documented",
    port_distance_km=1900.0,              # Distance to Dar es Salaam
    lobito_corridor_eligible=True,        # Copperbelt province

    # D6 — Capital Access Signals
    active_dfi_engagement="jurisdiction_only",  # IFC active in Zambia, not this asset specifically
    listed_vehicle="unlisted",            # State-owned post-reversion
    recent_capital_raise="none",
    gulf_western_investor_linked=False,
)


# ---------------------------------------------------------------------------
# ASSET 2 — Mingomba (KoBold Metals)
# North-Western Province, Zambia
# KoBold exploration asset. Strong institutional backing. Pre-production.
# ---------------------------------------------------------------------------

MINGOMBA = AssetInput(
    asset_id="ZMB-002",
    asset_name="Mingomba Copper Project (KoBold Metals)",
    jurisdiction="Zambia",
    jurisdiction_code="ZMB",
    commodity="Copper",
    province="North-Western",

    # D1 — Jurisdiction Stability
    fraser_investment_attractiveness=47.3,
    wb_rule_of_law_percentile=36.0,
    wb_regulatory_quality_percentile=41.0,
    regulatory_change_last_12m=True,
    mining_code_revision_in_progress=True,
    investment_arbitration_last_5y=False,    # No arbitration linked to this asset
    bilateral_investment_treaty=True,
    eiti_compliant_country=True,

    # D2 — Revenue Transparency
    eiti_implementation_status="compliant",
    beneficial_ownership_disclosure="partial",  # KoBold LLC structure — US Delaware, beneficial owners not all public
    eiti_payment_disclosure_quality=68.0,
    pep_in_ownership_chain=False,
    fatf_grey_list_jurisdiction=False,
    payment_data_gap_over_24m=False,

    # D3 — Asset Data Quality
    resource_estimate_standard="ni43101_jorc_u3y",  # Recent drilling results published 2024
    reserve_classification="resource_only",           # Resource declared, no reserve yet
    production_data_availability="none",              # Pre-production
    exploration_stage="development",
    unresolved_resource_conflict=False,
    estimate_by_company_employee=False,
    no_independent_technical_report=False,

    # D4 — Local Content (SI68 baseline)
    licence_holder_status="foreign_jv",    # Foreign-owned with local JV partner
    locas_filing_status="submitted_unverified",
    local_procurement_evidence="effort_sub_20pct",
    supplier_development_programme="documented",
    reserved_services_non_local=False,

    # D5 — Infrastructure Readiness
    power_supply="diesel_solar",          # Off-grid at exploration stage
    road_access="paved_50_200km",
    rail_access="rail_o100km",
    water_supply="present_no_permit",
    port_distance_km=2100.0,
    lobito_corridor_eligible=True,        # North-Western province

    # D6 — Capital Access Signals
    active_dfi_engagement="named_project_asset",  # BII / IFC linked to KoBold pipeline
    listed_vehicle="unlisted",
    recent_capital_raise="u18m",          # KoBold Series C 2024
    gulf_western_investor_linked=True,    # Western strategic investors publicly named
)


# ---------------------------------------------------------------------------
# ASSET 3 — Lumwana (Barrick Gold)
# North-Western Province, Zambia
# Large operating copper mine. Barrick-owned. Strong infrastructure.
# ---------------------------------------------------------------------------

LUMWANA = AssetInput(
    asset_id="ZMB-003",
    asset_name="Lumwana Copper Mine (Barrick Gold)",
    jurisdiction="Zambia",
    jurisdiction_code="ZMB",
    commodity="Copper",
    province="North-Western",

    # D1 — Jurisdiction Stability
    fraser_investment_attractiveness=47.3,
    wb_rule_of_law_percentile=36.0,
    wb_regulatory_quality_percentile=41.0,
    regulatory_change_last_12m=True,
    mining_code_revision_in_progress=True,
    investment_arbitration_last_5y=False,
    bilateral_investment_treaty=True,
    eiti_compliant_country=True,

    # D2 — Revenue Transparency
    eiti_implementation_status="compliant",
    beneficial_ownership_disclosure="full",     # Barrick Gold — NYSE listed, full BO disclosure
    eiti_payment_disclosure_quality=68.0,
    pep_in_ownership_chain=False,
    fatf_grey_list_jurisdiction=False,
    payment_data_gap_over_24m=False,

    # D3 — Asset Data Quality
    resource_estimate_standard="ni43101_jorc_u3y",  # Barrick annual reserve update 2024
    reserve_classification="proven_probable",
    production_data_availability="current_u12m",
    exploration_stage="producing",
    unresolved_resource_conflict=False,
    estimate_by_company_employee=False,
    no_independent_technical_report=False,

    # D4 — Local Content (SI68 baseline)
    licence_holder_status="foreign_jv",    # Barrick foreign-owned with ZCCM-IH minority
    locas_filing_status="submitted_verified",
    local_procurement_evidence="confirmed_20pct_plus",  # EITI Zambia local procurement data
    supplier_development_programme="documented",
    reserved_services_non_local=False,

    # D5 — Infrastructure Readiness
    power_supply="grid_with_redundancy",   # ZESCO + dedicated substation
    road_access="paved_u50km",
    rail_access="rail_o100km",
    water_supply="permitted_documented",
    port_distance_km=2100.0,
    lobito_corridor_eligible=True,

    # D6 — Capital Access Signals
    active_dfi_engagement="jurisdiction_only",
    listed_vehicle="asx_tsx_aim_active",   # Barrick NYSE listed (equivalent tier)
    recent_capital_raise="u18m",           # Barrick expansion capex announcement 2024
    gulf_western_investor_linked=True,
)


ALL_ASSETS = {
    "ZMB-001": KCM,
    "ZMB-002": MINGOMBA,
    "ZMB-003": LUMWANA,
}
