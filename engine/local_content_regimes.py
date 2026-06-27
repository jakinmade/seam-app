"""
SEAM Local Content Regime Registry
Version: SEAM-LC-v1.0

Each jurisdiction entry defines:
- The statutory baseline for D4 scoring
- Licence holder status classification rules
- Compliance filing mechanism
- Reserved services rule

Add new jurisdictions here. D4 scorer branches on regime_code.
"""

LOCAL_CONTENT_REGIMES = {

    "ZMB": {
        "regime_code": "ZMB",
        "jurisdiction": "Zambia",
        "baseline_instrument": "SI No. 68 of 2025 — Geological and Minerals Development (Local Content) Regulations",
        "effective_date": "2026-01-01",
        "compliance_portal": "LOCAS (Zambia MRC)",
        "reserved_services_rule": "Haulage, catering, security and other non-core services reserved 100% for local companies",
        "citizen_ownership_threshold_pct": 50.1,
        "citizen_empowered_min_pct": 25.0,
        "local_procurement_target_pct": 20.0,
        "filing_frequency": "Quarterly",
        "notes": "SI68 effective 1 January 2026. LOCAS portal is the compliance verification mechanism.",
    },

    "DRC": {
        "regime_code": "DRC",
        "jurisdiction": "Democratic Republic of Congo",
        "baseline_instrument": "Code Minier 2018 (Loi n° 18/001) — Articles 64–72 Local Content",
        "effective_date": "2018-03-09",
        "compliance_portal": "CAMI (Cadastre Minier) + EITI DRC",
        "reserved_services_rule": "Preference for Congolese companies in procurement; security services must use local firms",
        "citizen_ownership_threshold_pct": 10.0,   # 10% minimum Congolese equity required
        "citizen_empowered_min_pct": 5.0,
        "local_procurement_target_pct": 40.0,       # 40% local procurement target under Code Minier
        "filing_frequency": "Annual",
        "notes": "Code Minier 2018 significantly tightened local content vs 2002 code. EITI DRC active. CAMI cadastre publicly accessible.",
    },

    "BWA": {
        "regime_code": "BWA",
        "jurisdiction": "Botswana",
        "baseline_instrument": "Mines and Minerals Act (Cap 66:01) + Citizens Economic Empowerment Policy 2012",
        "effective_date": "2012-01-01",
        "compliance_portal": "Department of Mines (DoM) — Gaborone",
        "reserved_services_rule": "Citizens empowerment policy — preference for citizen-owned businesses in services",
        "citizen_ownership_threshold_pct": 50.0,
        "citizen_empowered_min_pct": 25.0,
        "local_procurement_target_pct": 30.0,
        "filing_frequency": "Annual",
        "notes": "Botswana local content framework less prescriptive than Zambia SI68. Enforcement varies. New minerals policy under review 2025.",
    },

    "GHA": {
        "regime_code": "GHA",
        "jurisdiction": "Ghana",
        "baseline_instrument": "Minerals and Mining (Local Content and Local Participation) Regulations 2012 (LI 2173)",
        "effective_date": "2012-01-01",
        "compliance_portal": "Minerals Commission Ghana + GHEITI",
        "reserved_services_rule": "Reserved list of services for Ghanaian companies including drilling, blasting, catering, security",
        "citizen_ownership_threshold_pct": 51.0,
        "citizen_empowered_min_pct": 20.0,
        "local_procurement_target_pct": 40.0,
        "filing_frequency": "Annual",
        "notes": "LI 2173 one of Africa's more detailed local content frameworks. GHEITI active and well-regarded. Strong gold sector data availability.",
    },

    "TZA": {
        "regime_code": "TZA",
        "jurisdiction": "Tanzania",
        "baseline_instrument": "Mining (Local Content) Regulations 2018 (GN No. 3 of 2018)",
        "effective_date": "2018-01-10",
        "compliance_portal": "Mining Commission Tanzania + TEITI",
        "reserved_services_rule": "100% local ownership required for support services including catering, cleaning, security, transport",
        "citizen_ownership_threshold_pct": 51.0,
        "citizen_empowered_min_pct": 20.0,
        "local_procurement_target_pct": 30.0,
        "filing_frequency": "Annual",
        "notes": "2018 regulations significantly strengthened local content post-Magufuli reforms. State participation via STAMICO. TEITI active.",
    },

    "NAM": {
        "regime_code": "NAM",
        "jurisdiction": "Namibia",
        "baseline_instrument": "Minerals (Prospecting and Mining) Act 33 of 1992 + New Equitable Economic Empowerment Framework (NEEEF)",
        "effective_date": "2016-01-01",
        "compliance_portal": "Ministry of Mines and Energy (MME) Namibia",
        "reserved_services_rule": "NEEEF preference for Namibian-owned businesses; no hard reservation list",
        "citizen_ownership_threshold_pct": 51.0,
        "citizen_empowered_min_pct": 25.0,
        "local_procurement_target_pct": 25.0,
        "filing_frequency": "Annual",
        "notes": "NEEEF 2016 introduced empowerment targets. Uranium sector well-documented. EITI Namibia candidate status.",
    },

    "GIN": {
        "regime_code": "GIN",
        "jurisdiction": "Guinea",
        "baseline_instrument": "Code Minier 2013 (Loi L/2013/053/CNT) — Articles on Local Content",
        "effective_date": "2013-09-09",
        "compliance_portal": "ANAIM (Agence Nationale pour l'Amélioration des Investissements Miniers)",
        "reserved_services_rule": "Preference for Guinean companies; security services must use local firms",
        "citizen_ownership_threshold_pct": 15.0,   # State typically takes 15% free carry
        "citizen_empowered_min_pct": 10.0,
        "local_procurement_target_pct": 30.0,
        "filing_frequency": "Annual",
        "notes": "Guinea bauxite and iron ore dominant. EITI Guinea compliant. Political instability risk (JNTA rule — post-2021 coup).",
    },

    "ZWE": {
        "regime_code": "ZWE",
        "jurisdiction": "Zimbabwe",
        "baseline_instrument": "Indigenisation and Economic Empowerment Act (Chapter 14:33) + Mines and Minerals Amendment Act 2019",
        "effective_date": "2019-01-01",
        "compliance_portal": "Zimbabwe Mining Development Corporation (ZMDC) + ZEITI",
        "reserved_services_rule": "Localisation requirements for specific services under indigenisation framework",
        "citizen_ownership_threshold_pct": 51.0,
        "citizen_empowered_min_pct": 20.0,
        "local_procurement_target_pct": 25.0,
        "filing_frequency": "Annual",
        "notes": "Indigenisation rules significantly relaxed post-2018 but sector-specific requirements remain. Lithium sector growing rapidly. ZEITI active.",
    },

    "MOZ": {
        "regime_code": "MOZ",
        "jurisdiction": "Mozambique",
        "baseline_instrument": "Lei de Minas (Lei 14/2002) + Regulamento de Conteúdo Local (Decreto 21/2016)",
        "effective_date": "2016-06-01",
        "compliance_portal": "INAMI (Instituto Nacional de Minas) + EITIM",
        "reserved_services_rule": "Local content decree requires preference for Mozambican goods and services",
        "citizen_ownership_threshold_pct": 20.0,
        "citizen_empowered_min_pct": 10.0,
        "local_procurement_target_pct": 20.0,
        "filing_frequency": "Annual",
        "notes": "Graphite and coal dominant. EITIM active. Security risk in Cabo Delgado affects northern assets.",
    },

}


def get_regime(jurisdiction_code: str) -> dict:
    """Return local content regime for a jurisdiction code. Returns generic if unknown."""
    regime = LOCAL_CONTENT_REGIMES.get(jurisdiction_code.upper())
    if regime:
        return regime
    # Generic fallback for unlisted jurisdictions
    return {
        "regime_code": "GENERIC",
        "jurisdiction": jurisdiction_code,
        "baseline_instrument": "Jurisdiction-specific local content rules not yet loaded in SEAM-LC-v1.0",
        "citizen_ownership_threshold_pct": 50.0,
        "citizen_empowered_min_pct": 25.0,
        "local_procurement_target_pct": 25.0,
        "filing_frequency": "Annual",
        "compliance_portal": "National mining authority — jurisdiction-specific portal not yet loaded",
        "reserved_services_rule": "Jurisdiction-specific reserved services rule not yet loaded",
        "notes": "Generic regime applied. Add jurisdiction to local_content_regimes.py for full scoring.",
    }


SUPPORTED_JURISDICTIONS = list(LOCAL_CONTENT_REGIMES.keys())
