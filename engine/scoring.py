"""
SEAM Scoring Engine
Version: 1.0
Methodology: SEAM-M-v1.0 | Rules: SEAM-R-v1.0

Deterministic scoring engine for African mining asset investment readiness.
No LLM in this path. Same inputs always produce the same outputs.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone
import json
from engine.local_content_regimes import get_regime, SUPPORTED_JURISDICTIONS


# ---------------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class AssetInput:
    """
    All data fields required to score an asset.
    Every field maps directly to a scoring rule.
    None = data not available (triggers absence penalties where applicable).
    """

    # Asset identity
    asset_id: str
    asset_name: str
    jurisdiction: str       # e.g. "Zambia"
    jurisdiction_code: str  # ISO-style code: "ZMB" | "DRC" | "BWA" | "GHA" | "TZA" | "NAM" | "GIN" | "ZWE" | "MOZ"
    commodity: str          # e.g. "Copper"
    province: str           # e.g. "Copperbelt"

    # D1 — Jurisdiction Stability
    fraser_investment_attractiveness: Optional[float] = None   # 0–100
    wb_rule_of_law_percentile: Optional[float] = None          # 0–100
    wb_regulatory_quality_percentile: Optional[float] = None   # 0–100
    regulatory_change_last_12m: bool = False
    mining_code_revision_in_progress: bool = False
    investment_arbitration_last_5y: bool = False
    bilateral_investment_treaty: bool = False
    eiti_compliant_country: bool = False

    # D2 — Revenue Transparency
    eiti_implementation_status: str = "non-implementing"  # "compliant" | "candidate" | "non-implementing"
    beneficial_ownership_disclosure: str = "none"          # "full" | "partial" | "none"
    eiti_payment_disclosure_quality: Optional[float] = None  # 0–100 (EITI Secretariat validation score)
    pep_in_ownership_chain: bool = False
    fatf_grey_list_jurisdiction: bool = False
    payment_data_gap_over_24m: bool = False

    # D3 — Asset Data Quality
    resource_estimate_standard: str = "none"   # "ni43101_jorc_u3y" | "ni43101_jorc_o3y" | "samrec" | "none"
    reserve_classification: str = "none"       # "proven_probable" | "resource_only" | "historical" | "none"
    production_data_availability: str = "none" # "current_u12m" | "current_12_36m" | "none"
    exploration_stage: str = "exploration"     # "producing" | "development" | "prefeasibility" | "exploration"
    unresolved_resource_conflict: bool = False
    estimate_by_company_employee: bool = False
    no_independent_technical_report: bool = False

    # D4 — Local Content Compliance Posture (Zambia SI68 baseline)
    licence_holder_status: str = "other"         # "citizen_owned" | "citizen_empowered" | "foreign_jv" | "other"
    locas_filing_status: str = "not_filed"       # "submitted_verified" | "submitted_unverified" | "not_filed"
    local_procurement_evidence: str = "none"     # "confirmed_20pct_plus" | "effort_sub_20pct" | "none"
    supplier_development_programme: str = "none" # "documented" | "in_development" | "none"
    reserved_services_non_local: bool = False    # haulage/catering/security contracted to non-local entities

    # D5 — Infrastructure Readiness
    power_supply: str = "none"      # "grid_with_redundancy" | "grid_no_redundancy" | "diesel_solar" | "none"
    road_access: str = "none"       # "paved_u50km" | "paved_50_200km" | "unsealed" | "none"
    rail_access: str = "none"       # "operating_u100km" | "operating_capacity_constrained" | "rail_o100km" | "none"
    water_supply: str = "none"      # "permitted_documented" | "present_no_permit" | "none"
    port_distance_km: Optional[float] = None
    lobito_corridor_eligible: bool = False  # NW or Copperbelt province, post Q3 2026

    # D6 — Capital Access Signals
    active_dfi_engagement: str = "none"    # "named_project_asset" | "jurisdiction_only" | "none"
    listed_vehicle: str = "unlisted"       # "asx_tsx_aim_active" | "otc_listed" | "unlisted"
    recent_capital_raise: str = "none"     # "u18m" | "18_36m" | "none"
    gulf_western_investor_linked: bool = False


@dataclass
class DimensionScore:
    code: str
    name: str
    weight: float
    raw_score: float          # 0–100 before floor/ceiling
    adjusted_score: float     # 0–100 after adjustments
    weighted_contribution: float
    sub_scores: dict = field(default_factory=dict)
    adjustments: list = field(default_factory=list)
    rules_applied: list = field(default_factory=list)
    data_gaps: list = field(default_factory=list)


@dataclass
class ScoringResult:
    asset_id: str
    asset_name: str
    methodology_version: str
    rules_version: str
    generated_at: str
    investment_readiness_score: int
    verdict: str
    verdict_label: str
    next_action: str
    dimensions: list
    floor_rules_triggered: list
    evidence_envelope: dict


# ---------------------------------------------------------------------------
# DIMENSION SCORERS
# ---------------------------------------------------------------------------

def score_d1_jurisdiction_stability(inp: AssetInput) -> DimensionScore:
    sub = {}
    adjustments = []
    rules = []
    gaps = []

    # Base: Fraser Institute (50%)
    if inp.fraser_investment_attractiveness is not None:
        fraser = inp.fraser_investment_attractiveness
        rules.append("D1-FRASER-001 v1.0")
    else:
        fraser = 50.0  # neutral default when absent
        gaps.append("Fraser Investment Attractiveness Index not available — neutral default applied")

    # Base: WB Rule of Law (25%)
    if inp.wb_rule_of_law_percentile is not None:
        rol = inp.wb_rule_of_law_percentile
        rules.append("D1-WB-ROL-001 v1.0")
    else:
        rol = 40.0
        gaps.append("World Bank Rule of Law percentile not available — conservative default applied")

    # Base: WB Regulatory Quality (25%)
    if inp.wb_regulatory_quality_percentile is not None:
        rq = inp.wb_regulatory_quality_percentile
        rules.append("D1-WB-RQ-001 v1.0")
    else:
        rq = 40.0
        gaps.append("World Bank Regulatory Quality percentile not available — conservative default applied")

    sub["fraser_institute_score"] = {"score": fraser, "weight": 0.50}
    sub["wb_rule_of_law"] = {"score": rol, "weight": 0.25}
    sub["wb_regulatory_quality"] = {"score": rq, "weight": 0.25}

    base = (fraser * 0.50) + (rol * 0.25) + (rq * 0.25)

    # Adjustments
    adj_total = 0.0
    if inp.regulatory_change_last_12m:
        adj_total -= 5
        adjustments.append({"rule": "D1-ADJ-001 v1.0", "adjustment": -5, "reason": "Regulatory change in past 12 months affecting commodity"})
    if inp.mining_code_revision_in_progress:
        adj_total -= 3
        adjustments.append({"rule": "D1-ADJ-002 v1.0", "adjustment": -3, "reason": "Active mining code revision in progress"})
    if inp.investment_arbitration_last_5y:
        adj_total -= 8
        adjustments.append({"rule": "D1-ADJ-003 v1.0", "adjustment": -8, "reason": "Investment arbitration against host government in past 5 years"})
    if inp.bilateral_investment_treaty:
        adj_total += 3
        adjustments.append({"rule": "D1-ADJ-004 v1.0", "adjustment": +3, "reason": "Bilateral Investment Treaty with UK, US or UAE in force"})
    if inp.eiti_compliant_country:
        adj_total += 3
        adjustments.append({"rule": "D1-ADJ-005 v1.0", "adjustment": +3, "reason": "EITI compliant country"})

    adjusted = min(100, max(0, base + adj_total))

    # Floor rule: score cannot exceed 85 if WB Rule of Law < 40
    if rol < 40 and adjusted > 85:
        adjusted = 85
        adjustments.append({"rule": "D1-FLOOR-001 v1.0", "adjustment": None, "reason": "Floor rule applied: WB Rule of Law below 40 — score capped at 85"})

    return DimensionScore(
        code="D1",
        name="Jurisdiction Stability",
        weight=0.25,
        raw_score=round(base, 2),
        adjusted_score=round(adjusted, 2),
        weighted_contribution=round(adjusted * 0.25, 4),
        sub_scores=sub,
        adjustments=adjustments,
        rules_applied=rules,
        data_gaps=gaps
    )


def score_d2_revenue_transparency(inp: AssetInput) -> DimensionScore:
    sub = {}
    adjustments = []
    rules = []
    gaps = []

    # EITI Implementation Status (40%)
    eiti_map = {"compliant": 40.0, "candidate": 25.0, "non-implementing": 0.0}
    eiti_score = eiti_map.get(inp.eiti_implementation_status, 0.0)
    sub["eiti_implementation_status"] = {"score": eiti_score, "weight": 0.40}
    rules.append("D2-EITI-001 v1.0")

    # Beneficial Ownership Disclosure (35%)
    bo_map = {"full": 35.0, "partial": 15.0, "none": 0.0}
    bo_score = bo_map.get(inp.beneficial_ownership_disclosure, 0.0)
    sub["beneficial_ownership_disclosure"] = {"score": bo_score, "weight": 0.35}
    rules.append("D2-BO-001 v1.0")

    # EITI Payment Disclosure Quality (25%)
    if inp.eiti_payment_disclosure_quality is not None:
        pdq = inp.eiti_payment_disclosure_quality * 0.25
        sub["eiti_payment_disclosure_quality"] = {"score": inp.eiti_payment_disclosure_quality, "weight": 0.25}
        rules.append("D2-PDQ-001 v1.0")
    else:
        pdq = 0.0
        sub["eiti_payment_disclosure_quality"] = {"score": 0, "weight": 0.25}
        gaps.append("EITI payment disclosure quality score not available — scored as zero")

    base = eiti_score + bo_score + pdq

    # Adjustments
    adj_total = 0.0
    if inp.pep_in_ownership_chain:
        adj_total -= 15
        adjustments.append({"rule": "D2-ADJ-001 v1.0", "adjustment": -15, "reason": "PEP identified in ownership chain"})
    if inp.fatf_grey_list_jurisdiction:
        adj_total -= 10
        adjustments.append({"rule": "D2-ADJ-002 v1.0", "adjustment": -10, "reason": "Asset in FATF grey list jurisdiction"})
    if inp.payment_data_gap_over_24m:
        adj_total -= 8
        adjustments.append({"rule": "D2-ADJ-003 v1.0", "adjustment": -8, "reason": "Payment data gap exceeding 24 months in most recent EITI report"})

    adjusted = min(100, max(0, base + adj_total))

    return DimensionScore(
        code="D2",
        name="Revenue Transparency",
        weight=0.20,
        raw_score=round(base, 2),
        adjusted_score=round(adjusted, 2),
        weighted_contribution=round(adjusted * 0.20, 4),
        sub_scores=sub,
        adjustments=adjustments,
        rules_applied=rules,
        data_gaps=gaps
    )


def score_d3_asset_data_quality(inp: AssetInput) -> DimensionScore:
    sub = {}
    adjustments = []
    rules = []
    gaps = []

    # Resource Estimate Standard (40%)
    res_map = {
        "ni43101_jorc_u3y": 40.0,
        "ni43101_jorc_o3y": 25.0,
        "samrec": 30.0,
        "none": 0.0
    }
    res_score = res_map.get(inp.resource_estimate_standard, 0.0)
    sub["resource_estimate_standard"] = {"score": res_score, "weight": 0.40}
    rules.append("D3-RES-001 v1.0")
    if inp.resource_estimate_standard == "none":
        gaps.append("No compliant resource estimate on record")

    # Reserve Classification (30%)
    rc_map = {
        "proven_probable": 30.0,
        "resource_only": 15.0,
        "historical": 5.0,
        "none": 0.0
    }
    rc_score = rc_map.get(inp.reserve_classification, 0.0)
    sub["reserve_classification"] = {"score": rc_score, "weight": 0.30}
    rules.append("D3-RC-001 v1.0")

    # Production Data Availability (20%)
    pd_map = {
        "current_u12m": 20.0,
        "current_12_36m": 10.0,
        "none": 0.0
    }
    pd_score = pd_map.get(inp.production_data_availability, 0.0)
    sub["production_data_availability"] = {"score": pd_score, "weight": 0.20}
    rules.append("D3-PD-001 v1.0")
    if inp.production_data_availability == "none":
        gaps.append("No production data in public domain")

    # Exploration Stage (10%)
    es_map = {
        "producing": 10.0,
        "development": 8.0,
        "prefeasibility": 5.0,
        "exploration": 2.0
    }
    es_score = es_map.get(inp.exploration_stage, 2.0)
    sub["exploration_stage"] = {"score": es_score, "weight": 0.10}
    rules.append("D3-ES-001 v1.0")

    base = res_score + rc_score + pd_score + es_score

    # Adjustments
    adj_total = 0.0
    if inp.unresolved_resource_conflict:
        adj_total -= 8
        adjustments.append({"rule": "D3-ADJ-001 v1.0", "adjustment": -8, "reason": "Unresolved conflict between resource estimates — conservative value applied"})
    if inp.estimate_by_company_employee:
        adj_total -= 10
        adjustments.append({"rule": "D3-ADJ-002 v1.0", "adjustment": -10, "reason": "Resource estimate produced by company employee rather than independent QP"})
    if inp.no_independent_technical_report:
        adj_total -= 15
        adjustments.append({"rule": "D3-ADJ-003 v1.0", "adjustment": -15, "reason": "No independent technical report in existence"})

    adjusted = min(100, max(0, base + adj_total))

    return DimensionScore(
        code="D3",
        name="Asset Data Quality",
        weight=0.20,
        raw_score=round(base, 2),
        adjusted_score=round(adjusted, 2),
        weighted_contribution=round(adjusted * 0.20, 4),
        sub_scores=sub,
        adjustments=adjustments,
        rules_applied=rules,
        data_gaps=gaps
    )


def score_d4_local_content(inp: AssetInput) -> DimensionScore:
    sub = {}
    adjustments = []
    rules = []
    gaps = []

    # Load jurisdiction-specific local content regime
    regime = get_regime(inp.jurisdiction_code)
    regime_note = f"Baseline: {regime['baseline_instrument']}"
    rules.append(f"D4-REGIME-{inp.jurisdiction_code} v1.0 | {regime['baseline_instrument']}")

    # Licence Holder Status (35%) — thresholds from regime
    citizen_threshold = regime["citizen_ownership_threshold_pct"]
    citizen_empowered_min = regime["citizen_empowered_min_pct"]

    lh_map = {
        "citizen_owned": 35.0,
        "citizen_empowered": 20.0,
        "foreign_jv": 10.0,
        "other": 0.0
    }
    lh_score = lh_map.get(inp.licence_holder_status, 0.0)
    sub["licence_holder_status"] = {
        "score": lh_score,
        "weight": 0.35,
        "regime_citizen_threshold_pct": citizen_threshold,
        "regime_empowered_min_pct": citizen_empowered_min
    }
    rules.append("D4-LH-001 v1.0")

    # Compliance Filing (30%) — mechanism varies by jurisdiction
    locas_map = {
        "submitted_verified": 30.0,
        "submitted_unverified": 15.0,
        "not_filed": 0.0
    }
    locas_score = locas_map.get(inp.locas_filing_status, 0.0)
    sub["compliance_filing_status"] = {
        "score": locas_score,
        "weight": 0.30,
        "compliance_portal": regime["compliance_portal"],
        "filing_frequency": regime["filing_frequency"]
    }
    rules.append("D4-FILING-001 v1.0")
    if inp.locas_filing_status == "not_filed":
        gaps.append(f"Compliance filing not on record — {regime['compliance_portal']}")

    # Local Procurement Evidence (20%) — target from regime
    procurement_target = regime["local_procurement_target_pct"]
    lp_map = {
        "confirmed_20pct_plus": 20.0,
        "effort_sub_20pct": 10.0,
        "none": 0.0
    }
    lp_score = lp_map.get(inp.local_procurement_evidence, 0.0)
    sub["local_procurement_evidence"] = {
        "score": lp_score,
        "weight": 0.20,
        "regime_procurement_target_pct": procurement_target
    }
    rules.append("D4-LP-001 v1.0")

    # Supplier Development Programme (15%)
    sdp_map = {
        "documented": 15.0,
        "in_development": 7.0,
        "none": 0.0
    }
    sdp_score = sdp_map.get(inp.supplier_development_programme, 0.0)
    sub["supplier_development_programme"] = {"score": sdp_score, "weight": 0.15}
    rules.append("D4-SDP-001 v1.0")

    base = lh_score + locas_score + lp_score + sdp_score

    # Adjustments
    adj_total = 0.0
    if inp.reserved_services_non_local:
        adj_total -= 20
        adjustments.append({
            "rule": "D4-ADJ-001 v1.0",
            "adjustment": -20,
            "reason": f"Reserved services contracted to non-local entities without documented exception — {regime['reserved_services_rule']}"
        })

    adjusted = min(100, max(0, base + adj_total))

    return DimensionScore(
        code="D4",
        name="Local Content Compliance Posture",
        weight=0.15,
        raw_score=round(base, 2),
        adjusted_score=round(adjusted, 2),
        weighted_contribution=round(adjusted * 0.15, 4),
        sub_scores=sub,
        adjustments=adjustments,
        rules_applied=rules,
        data_gaps=gaps
    )


def score_d5_infrastructure(inp: AssetInput) -> DimensionScore:
    sub = {}
    adjustments = []
    rules = []
    gaps = []

    # Power Supply (30%)
    pw_map = {
        "grid_with_redundancy": 30.0,
        "grid_no_redundancy": 20.0,
        "diesel_solar": 10.0,
        "none": 0.0
    }
    pw_score = pw_map.get(inp.power_supply, 0.0)
    sub["power_supply"] = {"score": pw_score, "weight": 0.30}
    rules.append("D5-PWR-001 v1.0")
    if inp.power_supply == "none":
        gaps.append("Power supply not documented")

    # Road Access (20%)
    rd_map = {
        "paved_u50km": 20.0,
        "paved_50_200km": 15.0,
        "unsealed": 5.0,
        "none": 0.0
    }
    rd_score = rd_map.get(inp.road_access, 0.0)
    sub["road_access"] = {"score": rd_score, "weight": 0.20}
    rules.append("D5-ROAD-001 v1.0")

    # Rail Access (20%)
    rl_map = {
        "operating_u100km": 20.0,
        "operating_capacity_constrained": 12.0,
        "rail_o100km": 6.0,
        "none": 0.0
    }
    rl_score = rl_map.get(inp.rail_access, 0.0)
    sub["rail_access"] = {"score": rl_score, "weight": 0.20}
    rules.append("D5-RAIL-001 v1.0")

    # Lobito Corridor adjustment
    if inp.lobito_corridor_eligible and inp.rail_access in ["operating_capacity_constrained", "rail_o100km", "none"]:
        rl_score = min(20.0, rl_score + 5.0)
        sub["rail_access"]["score"] = rl_score
        adjustments.append({"rule": "D5-LOBITO-001 v1.0", "adjustment": +5, "reason": "Lobito Corridor eligibility adjustment (NW/Copperbelt province)"})

    # Water Supply (15%)
    ws_map = {
        "permitted_documented": 15.0,
        "present_no_permit": 8.0,
        "none": 0.0
    }
    ws_score = ws_map.get(inp.water_supply, 0.0)
    sub["water_supply"] = {"score": ws_score, "weight": 0.15}
    rules.append("D5-WATER-001 v1.0")
    if inp.water_supply == "none":
        gaps.append("Water supply not documented")

    # Port Distance (15%)
    if inp.port_distance_km is not None:
        if inp.port_distance_km < 500:
            pt_score = 15.0
        elif inp.port_distance_km <= 1000:
            pt_score = 10.0
        else:
            pt_score = 5.0
        rules.append("D5-PORT-001 v1.0")
    else:
        pt_score = 5.0  # conservative default
        gaps.append("Port distance not documented — conservative default applied")
    sub["port_distance"] = {"score": pt_score, "weight": 0.15}

    base = pw_score + rd_score + rl_score + ws_score + pt_score
    adjusted = min(100, max(0, base))

    return DimensionScore(
        code="D5",
        name="Infrastructure Readiness",
        weight=0.12,
        raw_score=round(base, 2),
        adjusted_score=round(adjusted, 2),
        weighted_contribution=round(adjusted * 0.12, 4),
        sub_scores=sub,
        adjustments=adjustments,
        rules_applied=rules,
        data_gaps=gaps
    )


def score_d6_capital_access(inp: AssetInput) -> DimensionScore:
    sub = {}
    adjustments = []
    rules = []
    gaps = []

    # Active DFI Engagement (40%)
    dfi_map = {
        "named_project_asset": 40.0,
        "jurisdiction_only": 20.0,
        "none": 0.0
    }
    dfi_score = dfi_map.get(inp.active_dfi_engagement, 0.0)
    sub["active_dfi_engagement"] = {"score": dfi_score, "weight": 0.40}
    rules.append("D6-DFI-001 v1.0")

    # Listed Vehicle (30%)
    lv_map = {
        "asx_tsx_aim_active": 30.0,
        "otc_listed": 15.0,
        "unlisted": 0.0
    }
    lv_score = lv_map.get(inp.listed_vehicle, 0.0)
    sub["listed_vehicle"] = {"score": lv_score, "weight": 0.30}
    rules.append("D6-LV-001 v1.0")

    # Recent Capital Raise (20%)
    cr_map = {
        "u18m": 20.0,
        "18_36m": 10.0,
        "none": 0.0
    }
    cr_score = cr_map.get(inp.recent_capital_raise, 0.0)
    sub["recent_capital_raise"] = {"score": cr_score, "weight": 0.20}
    rules.append("D6-CR-001 v1.0")

    # Gulf/Western Investor (10%)
    gw_score = 10.0 if inp.gulf_western_investor_linked else 0.0
    sub["gulf_western_investor"] = {"score": gw_score, "weight": 0.10}
    rules.append("D6-GW-001 v1.0")

    base = dfi_score + lv_score + cr_score + gw_score
    adjusted = min(100, max(0, base))

    return DimensionScore(
        code="D6",
        name="Capital Access Signals",
        weight=0.08,
        raw_score=round(base, 2),
        adjusted_score=round(adjusted, 2),
        weighted_contribution=round(adjusted * 0.08, 4),
        sub_scores=sub,
        adjustments=adjustments,
        rules_applied=rules,
        data_gaps=gaps
    )


# ---------------------------------------------------------------------------
# DECISION ENGINE
# ---------------------------------------------------------------------------

VERDICT_THRESHOLDS = [
    (80, 100, "PROCEED",
     "Public data confirms the asset meets minimum thresholds across all six dimensions. The evidence base is sufficient to support commissioning full technical due diligence.",
     "Commission independent NI43-101 or JORC compliant resource estimate verification. Estimated cost £150k–£300k. Estimated timeline 8–12 weeks."),
    (65, 79, "PROCEED WITH CONDITIONS",
     "Asset meets threshold on at least four of six dimensions. Specific gaps are identified and cited in the Evidence Envelope. These gaps are resolvable before full commitment.",
     "Address the named conditions identified in the Evidence Envelope. Return for re-score once conditions are met."),
    (45, 64, "MONITOR",
     "Asset has genuine potential but one or more dimensions are in flux. Premature to commit due diligence spend.",
     "SEAM places this asset on 90-day monitoring cycle. Act when the data moves — not when an advisor remembers to call."),
    (25, 44, "CAUTION",
     "Specific red flags identified in the evidence base. Named, cited and reproducible. Some flags may be resolvable — SEAM distinguishes structural from addressable problems.",
     "Review the named red flags in the Evidence Envelope. Identify which are resolvable at asset level and which are structural."),
    (0, 24, "AVOID",
     "Evidence base shows fundamental problems across multiple dimensions that cannot be resolved at asset level.",
     "Stand down. The Evidence Envelope provides documented rationale for declining — ready to present to an investment committee as the basis for a no-go decision without further spend."),
]

FLOOR_RULES = [
    {
        "code": "FLOOR-D2-001",
        "dimension": "D2",
        "threshold": 20,
        "max_verdict": "CAUTION",
        "description": "D2 (Revenue Transparency) below 20 — maximum verdict is CAUTION regardless of aggregate score"
    },
    {
        "code": "FLOOR-D1-001",
        "dimension": "D1",
        "threshold": 25,
        "max_verdict": "MONITOR",
        "description": "D1 (Jurisdiction Stability) below 25 — maximum verdict is MONITOR regardless of aggregate score"
    },
    {
        "code": "FLOOR-D3-001",
        "dimension": "D3",
        "threshold": 15,
        "max_verdict": "CAUTION",
        "description": "D3 (Asset Data Quality) below 15 — maximum verdict is CAUTION regardless of aggregate score"
    },
    {
        "code": "FLOOR-BO-001",
        "dimension": "D2",
        "threshold": None,
        "condition": "beneficial_ownership_none",
        "max_verdict": "CAUTION",
        "description": "Beneficial ownership cannot be traced to individual natural persons — maximum verdict is CAUTION"
    },
]

VERDICT_ORDER = ["PROCEED", "PROCEED WITH CONDITIONS", "MONITOR", "CAUTION", "AVOID"]


def apply_floor_rules(score: float, dimensions: list, inp: AssetInput) -> tuple[str, list]:
    """
    Determine raw verdict from score, then apply floor rules.
    Returns (final_verdict, [triggered_floor_rules])
    """
    # Raw verdict from score
    raw_verdict = "AVOID"
    for low, high, verdict, _, _ in VERDICT_THRESHOLDS:
        if low <= score <= high:
            raw_verdict = verdict
            break

    triggered = []
    constrained_verdict = raw_verdict
    dim_map = {d.code: d.adjusted_score for d in dimensions}

    for rule in FLOOR_RULES:
        triggered_flag = False

        if rule.get("condition") == "beneficial_ownership_none":
            if inp.beneficial_ownership_disclosure == "none":
                triggered_flag = True
        elif rule["threshold"] is not None:
            if dim_map.get(rule["dimension"], 100) < rule["threshold"]:
                triggered_flag = True

        if triggered_flag:
            triggered.append(rule)
            max_v = rule["max_verdict"]
            # Apply the most restrictive constraint
            if VERDICT_ORDER.index(max_v) > VERDICT_ORDER.index(constrained_verdict):
                constrained_verdict = max_v

    return constrained_verdict, triggered


def get_verdict_text(verdict: str) -> tuple[str, str]:
    for _, _, v, label, action in VERDICT_THRESHOLDS:
        if v == verdict:
            return label, action
    return "", ""


# ---------------------------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------------------------

def score_asset(inp: AssetInput) -> ScoringResult:
    """
    Run full SEAM scoring against an AssetInput.
    Returns a complete ScoringResult with evidence envelope.
    """
    generated_at = datetime.now(timezone.utc).isoformat()

    # Score all six dimensions
    d1 = score_d1_jurisdiction_stability(inp)
    d2 = score_d2_revenue_transparency(inp)
    d3 = score_d3_asset_data_quality(inp)
    d4 = score_d4_local_content(inp)
    d5 = score_d5_infrastructure(inp)
    d6 = score_d6_capital_access(inp)

    dimensions = [d1, d2, d3, d4, d5, d6]

    # Weighted aggregate
    raw_score = sum(d.weighted_contribution for d in dimensions)
    final_score = round(raw_score)

    # Verdict + floor rules
    verdict, floor_rules_triggered = apply_floor_rules(final_score, dimensions, inp)
    verdict_label, next_action = get_verdict_text(verdict)

    # Evidence envelope
    envelope = {
        "asset_id": inp.asset_id,
        "asset_name": inp.asset_name,
        "methodology_version": "SEAM-M-v1.0",
        "rules_version": "SEAM-R-v1.0",
        "generated_at": generated_at,
        "investment_readiness_score": final_score,
        "verdict": verdict,
        "dimensions": {
            d.code: {
                "name": d.name,
                "weight": d.weight,
                "adjusted_score": d.adjusted_score,
                "weighted_contribution": d.weighted_contribution,
                "sub_scores": d.sub_scores,
                "adjustments": d.adjustments,
                "rules_applied": d.rules_applied,
                "data_gaps": d.data_gaps
            }
            for d in dimensions
        },
        "floor_rules_triggered": [r["code"] for r in floor_rules_triggered],
        "data_gaps_summary": [gap for d in dimensions for gap in d.data_gaps]
    }

    return ScoringResult(
        asset_id=inp.asset_id,
        asset_name=inp.asset_name,
        methodology_version="SEAM-M-v1.0",
        rules_version="SEAM-R-v1.0",
        generated_at=generated_at,
        investment_readiness_score=final_score,
        verdict=verdict,
        verdict_label=verdict_label,
        next_action=next_action,
        dimensions=dimensions,
        floor_rules_triggered=floor_rules_triggered,
        evidence_envelope=envelope
    )
