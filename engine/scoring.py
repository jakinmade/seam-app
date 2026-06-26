"""
SEAM Scoring Engine
Version: reads from SEAM-R-v1.0.yaml
Methodology: SEAM-M-v1.0

Deterministic scoring engine for African mining asset investment readiness.
No LLM in this path. Same inputs always produce the same outputs.
All rules, weightings and thresholds loaded from versioned YAML.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone
import hashlib
import json

from engine.rules_loader import get_active_rules, ACTIVE_VERSION
from engine.local_content_regimes import get_regime


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
    asset_id: str
    asset_name: str
    jurisdiction: str
    jurisdiction_code: str
    commodity: str
    province: str

    fraser_investment_attractiveness: Optional[float] = None
    wb_rule_of_law_percentile: Optional[float] = None
    wb_regulatory_quality_percentile: Optional[float] = None
    regulatory_change_last_12m: bool = False
    mining_code_revision_in_progress: bool = False
    investment_arbitration_last_5y: bool = False
    bilateral_investment_treaty: bool = False
    eiti_compliant_country: bool = False

    eiti_implementation_status: str = "non-implementing"
    beneficial_ownership_disclosure: str = "none"
    eiti_payment_disclosure_quality: Optional[float] = None
    pep_in_ownership_chain: bool = False
    fatf_grey_list_jurisdiction: bool = False
    payment_data_gap_over_24m: bool = False

    resource_estimate_standard: str = "none"
    reserve_classification: str = "none"
    production_data_availability: str = "none"
    exploration_stage: str = "exploration"
    unresolved_resource_conflict: bool = False
    estimate_by_company_employee: bool = False
    no_independent_technical_report: bool = False

    licence_holder_status: str = "other"
    locas_filing_status: str = "not_filed"
    local_procurement_evidence: str = "none"
    supplier_development_programme: str = "none"
    reserved_services_non_local: bool = False

    power_supply: str = "none"
    road_access: str = "none"
    rail_access: str = "none"
    water_supply: str = "none"
    port_distance_km: Optional[float] = None
    lobito_corridor_eligible: bool = False

    active_dfi_engagement: str = "none"
    listed_vehicle: str = "unlisted"
    recent_capital_raise: str = "none"
    gulf_western_investor_linked: bool = False

    # Bankability Constraints — retrieved from public sources, not scored
    # These are binary flags surfaced as constraints, not dimensions
    environmental_permit_status: str = "unknown"   # "permitted" | "in_progress" | "not_filed" | "unknown"
    esia_completed: bool = False                    # Environmental & Social Impact Assessment on public record
    community_consultation_evidence: str = "none"  # "documented" | "partial" | "none"
    social_licence_disputes: bool = False           # Active community/NGO opposition on record
    water_licence_status: str = "unknown"           # "permitted" | "pending" | "not_filed" | "unknown"


@dataclass
class EvidenceField:
    """Structured provenance for a single retrieved data field."""
    field_name: str
    value: object
    source: Optional[str] = None
    source_url: Optional[str] = None
    retrieved_date: Optional[str] = None
    publication_date: Optional[str] = None
    confidence: str = "medium"
    verified: bool = False
    rule_code: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class DimensionScore:
    code: str
    name: str
    weight: float
    raw_score: float
    adjusted_score: float
    weighted_contribution: float
    sub_scores: dict = field(default_factory=dict)
    adjustments: list = field(default_factory=list)
    rules_applied: list = field(default_factory=list)
    data_gaps: list = field(default_factory=list)
    evidence_fields: list = field(default_factory=list)


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
    envelope_hash: str
    evidence_completeness_score: int = 0


# ---------------------------------------------------------------------------
# DIMENSION SCORERS
# ---------------------------------------------------------------------------

def score_d1(inp, R):
    sub, adjs, rules, gaps, ef = {}, [], [], [], []
    sw = R["d1_sub_weights"]

    fraser = inp.fraser_investment_attractiveness if inp.fraser_investment_attractiveness is not None else 50.0
    if inp.fraser_investment_attractiveness is None:
        gaps.append("Fraser Investment Attractiveness Index not available — neutral default applied")
    else:
        rules.append("D1-FRASER-001 v1.0")
        ef.append(EvidenceField("fraser_investment_attractiveness", fraser, source="Fraser Institute Annual Survey", confidence="high", verified=True, rule_code="D1-FRASER-001"))

    rol = inp.wb_rule_of_law_percentile if inp.wb_rule_of_law_percentile is not None else 40.0
    if inp.wb_rule_of_law_percentile is None:
        gaps.append("World Bank Rule of Law percentile not available — conservative default applied")
    else:
        rules.append("D1-WB-ROL-001 v1.0")
        ef.append(EvidenceField("wb_rule_of_law_percentile", rol, source="World Bank WGI", confidence="high", verified=True, rule_code="D1-WB-ROL-001"))

    rq = inp.wb_regulatory_quality_percentile if inp.wb_regulatory_quality_percentile is not None else 40.0
    if inp.wb_regulatory_quality_percentile is None:
        gaps.append("World Bank Regulatory Quality percentile not available — conservative default applied")
    else:
        rules.append("D1-WB-RQ-001 v1.0")
        ef.append(EvidenceField("wb_regulatory_quality_percentile", rq, source="World Bank WGI", confidence="high", verified=True, rule_code="D1-WB-RQ-001"))

    sub["fraser_institute_score"] = {"score": fraser, "weight": sw["fraser_institute"]}
    sub["wb_rule_of_law"]         = {"score": rol,    "weight": sw["wb_rule_of_law"]}
    sub["wb_regulatory_quality"]  = {"score": rq,     "weight": sw["wb_regulatory_quality"]}

    base = (fraser * sw["fraser_institute"]) + (rol * sw["wb_rule_of_law"]) + (rq * sw["wb_regulatory_quality"])
    adj_total = 0.0
    for flag, pts in R["d1_adjustments"].items():
        if getattr(inp, flag, False):
            adj_total += pts
            adjs.append({"rule": f"D1-ADJ-{flag} v1.0", "adjustment": pts, "reason": flag.replace("_"," ").capitalize()})

    adjusted = min(100, max(0, base + adj_total))
    fl = R["d1_floor"]
    if rol < fl["wb_rule_of_law_threshold"] and adjusted > fl["max_score_when_triggered"]:
        adjusted = fl["max_score_when_triggered"]
        adjs.append({"rule": f"{fl['rule']} v1.0", "adjustment": None, "reason": fl["description"]})

    # Provenance for boolean D1 fields
    ef.append(EvidenceField("regulatory_change_last_12m", inp.regulatory_change_last_12m,
        source="Government gazette / Ministry of Mines announcements", confidence="medium",
        verified=inp.regulatory_change_last_12m is not None, rule_code="D1-ADJ-regulatory_change_last_12m"))
    ef.append(EvidenceField("mining_code_revision_in_progress", inp.mining_code_revision_in_progress,
        source="Government gazette / legislative tracker", confidence="medium",
        verified=True, rule_code="D1-ADJ-mining_code_revision_in_progress"))
    ef.append(EvidenceField("investment_arbitration_last_5y", inp.investment_arbitration_last_5y,
        source="ICSID / PCA arbitration register", confidence="medium",
        verified=True, rule_code="D1-ADJ-investment_arbitration_last_5y"))
    ef.append(EvidenceField("bilateral_investment_treaty", inp.bilateral_investment_treaty,
        source="UNCTAD BIT database (investmentpolicy.unctad.org)", confidence="high",
        verified=True, rule_code="D1-ADJ-bilateral_investment_treaty"))
    ef.append(EvidenceField("eiti_compliant_country", inp.eiti_compliant_country,
        source="EITI — eiti.org/countries", confidence="high",
        verified=True, rule_code="D1-ADJ-eiti_compliant_country"))

    w = R["dimensions"]["D1"]["weight"]
    return DimensionScore("D1","Jurisdiction Stability",w,round(base,2),round(adjusted,2),round(adjusted*w,4),sub,adjs,rules,gaps,ef)


def score_d2(inp, R):
    sub, adjs, rules, gaps, ef = {}, [], [], [], []
    sw = R["d2_sub_weights"]

    eiti_score = R["d2_eiti_scores"].get(inp.eiti_implementation_status, 0.0)
    sub["eiti_implementation_status"] = {"score": eiti_score, "weight": sw["eiti_implementation"]}
    rules.append("D2-EITI-001 v1.0")
    ef.append(EvidenceField("eiti_implementation_status", inp.eiti_implementation_status, source="EITI — eiti.org", confidence="high", verified=True, rule_code="D2-EITI-001"))

    bo_score = R["d2_bo_scores"].get(inp.beneficial_ownership_disclosure, 0.0)
    sub["beneficial_ownership_disclosure"] = {"score": bo_score, "weight": sw["beneficial_ownership"]}
    rules.append("D2-BO-001 v1.0")

    if inp.eiti_payment_disclosure_quality is not None:
        pdq = inp.eiti_payment_disclosure_quality * sw["payment_disclosure_quality"]
        sub["eiti_payment_disclosure_quality"] = {"score": inp.eiti_payment_disclosure_quality, "weight": sw["payment_disclosure_quality"]}
        rules.append("D2-PDQ-001 v1.0")
    else:
        pdq = 0.0
        sub["eiti_payment_disclosure_quality"] = {"score": 0, "weight": sw["payment_disclosure_quality"]}
        gaps.append("EITI payment disclosure quality score not available — scored as zero")

    base = eiti_score + bo_score + pdq
    adj_total = 0.0
    for flag, pts in R["d2_adjustments"].items():
        if getattr(inp, flag, False):
            adj_total += pts
            adjs.append({"rule": f"D2-ADJ-{flag} v1.0", "adjustment": pts, "reason": flag.replace("_"," ").capitalize()})

    adjusted = min(100, max(0, base + adj_total))
    ef.append(EvidenceField("beneficial_ownership_disclosure", inp.beneficial_ownership_disclosure,
        source="National beneficial ownership register / EITI beneficial ownership annex",
        confidence="high", verified=True, rule_code="D2-BO-001"))
    if inp.eiti_payment_disclosure_quality is not None:
        ef.append(EvidenceField("eiti_payment_disclosure_quality", inp.eiti_payment_disclosure_quality,
            source="EITI country report — payment disclosure annex", confidence="high",
            verified=True, rule_code="D2-PDQ-001"))
    ef.append(EvidenceField("pep_in_ownership_chain", inp.pep_in_ownership_chain,
        source="ICIJ Offshore Leaks / national PEP register", confidence="medium",
        verified=True, rule_code="D2-ADJ-pep_in_ownership_chain"))
    ef.append(EvidenceField("fatf_grey_list_jurisdiction", inp.fatf_grey_list_jurisdiction,
        source="FATF public statement (fatf-gafi.org)", confidence="high",
        verified=True, rule_code="D2-ADJ-fatf_grey_list_jurisdiction"))
    ef.append(EvidenceField("payment_data_gap_over_24m", inp.payment_data_gap_over_24m,
        source="EITI country report timeline", confidence="medium",
        verified=True, rule_code="D2-ADJ-payment_data_gap_over_24m"))

    w = R["dimensions"]["D2"]["weight"]
    return DimensionScore("D2","Revenue Transparency",w,round(base,2),round(adjusted,2),round(adjusted*w,4),sub,adjs,rules,gaps,ef)


def score_d3(inp, R):
    sub, adjs, rules, gaps, ef = {}, [], [], [], []
    sw = R["d3_sub_weights"]

    res = R["d3_resource_standard_scores"].get(inp.resource_estimate_standard, 0.0)
    sub["resource_estimate_standard"] = {"score": res, "weight": sw["resource_standard"]}
    rules.append("D3-RES-001 v1.0")
    if inp.resource_estimate_standard == "none":
        gaps.append("No compliant resource estimate on record")

    rc = R["d3_reserve_scores"].get(inp.reserve_classification, 0.0)
    sub["reserve_classification"] = {"score": rc, "weight": sw["reserve_classification"]}
    rules.append("D3-RC-001 v1.0")

    pd = R["d3_production_scores"].get(inp.production_data_availability, 0.0)
    sub["production_data_availability"] = {"score": pd, "weight": sw["production_data"]}
    rules.append("D3-PD-001 v1.0")
    if inp.production_data_availability == "none":
        gaps.append("No production data in public domain")

    es = R["d3_stage_scores"].get(inp.exploration_stage, 2.0)
    sub["exploration_stage"] = {"score": es, "weight": sw["exploration_stage"]}
    rules.append("D3-ES-001 v1.0")

    base = res + rc + pd + es
    adj_total = 0.0
    for flag, pts in R["d3_adjustments"].items():
        if getattr(inp, flag, False):
            adj_total += pts
            adjs.append({"rule": f"D3-ADJ-{flag} v1.0", "adjustment": pts, "reason": flag.replace("_"," ").capitalize()})

    adjusted = min(100, max(0, base + adj_total))
    ef.append(EvidenceField("resource_estimate_standard", inp.resource_estimate_standard,
        source="NI 43-101 / JORC filing — exchange regulatory announcement",
        confidence="high", verified=inp.resource_estimate_standard != "none", rule_code="D3-RES-001"))
    ef.append(EvidenceField("reserve_classification", inp.reserve_classification,
        source="Technical report / competent person report",
        confidence="high", verified=inp.reserve_classification != "none", rule_code="D3-RC-001"))
    ef.append(EvidenceField("production_data_availability", inp.production_data_availability,
        source="Operator annual report / quarterly production release",
        confidence="high", verified=inp.production_data_availability != "none", rule_code="D3-PD-001"))
    ef.append(EvidenceField("exploration_stage", inp.exploration_stage,
        source="Operator disclosure / exchange filing",
        confidence="high", verified=True, rule_code="D3-ES-001"))
    ef.append(EvidenceField("unresolved_resource_conflict", inp.unresolved_resource_conflict,
        source="Court records / mining ministry gazette", confidence="medium",
        verified=True, rule_code="D3-ADJ-unresolved_resource_conflict"))
    ef.append(EvidenceField("no_independent_technical_report", inp.no_independent_technical_report,
        source="Exchange filing / SEDAR / ASX announcements", confidence="high",
        verified=True, rule_code="D3-ADJ-no_independent_technical_report"))

    w = R["dimensions"]["D3"]["weight"]
    return DimensionScore("D3","Asset Data Quality",w,round(base,2),round(adjusted,2),round(adjusted*w,4),sub,adjs,rules,gaps,ef)


def score_d4(inp, R):
    sub, adjs, rules, gaps, ef = {}, [], [], [], []
    sw = R["d4_sub_weights"]
    regime = get_regime(inp.jurisdiction_code)

    rules.append(f"D4-REGIME-{inp.jurisdiction_code} v1.0 | {regime['baseline_instrument']}")

    lh = R["d4_licence_holder_scores"].get(inp.licence_holder_status, 0.0)
    sub["licence_holder_status"] = {"score": lh, "weight": sw["licence_holder"],
        "regime_citizen_threshold_pct": regime["citizen_ownership_threshold_pct"]}
    rules.append("D4-LH-001 v1.0")

    fs = R["d4_filing_scores"].get(inp.locas_filing_status, 0.0)
    sub["compliance_filing_status"] = {"score": fs, "weight": sw["compliance_filing"],
        "compliance_portal": regime["compliance_portal"]}
    rules.append("D4-FILING-001 v1.0")
    if inp.locas_filing_status == "not_filed":
        gaps.append(f"Compliance filing not on record — {regime['compliance_portal']}")

    lp = R["d4_procurement_scores"].get(inp.local_procurement_evidence, 0.0)
    sub["local_procurement_evidence"] = {"score": lp, "weight": sw["local_procurement"],
        "regime_procurement_target_pct": regime["local_procurement_target_pct"]}
    rules.append("D4-LP-001 v1.0")

    sdp = R["d4_sdp_scores"].get(inp.supplier_development_programme, 0.0)
    sub["supplier_development_programme"] = {"score": sdp, "weight": sw["supplier_development"]}
    rules.append("D4-SDP-001 v1.0")

    base = lh + fs + lp + sdp
    adj_total = 0.0
    if inp.reserved_services_non_local:
        pts = R["d4_adjustments"]["reserved_services_non_local"]
        adj_total += pts
        adjs.append({"rule": "D4-ADJ-001 v1.0", "adjustment": pts,
                     "reason": f"Reserved services non-local — {regime['reserved_services_rule']}"})

    adjusted = min(100, max(0, base + adj_total))
    ef.append(EvidenceField("licence_holder_status", inp.licence_holder_status,
        source=f"Mining licence register — {regime['compliance_portal']}",
        confidence="high", verified=inp.licence_holder_status != "other", rule_code="D4-LH-001"))
    ef.append(EvidenceField("locas_filing_status", inp.locas_filing_status,
        source=f"Local content compliance portal — {regime['compliance_portal']}",
        confidence="high", verified=inp.locas_filing_status != "not_filed", rule_code="D4-FILING-001"))
    ef.append(EvidenceField("local_procurement_evidence", inp.local_procurement_evidence,
        source="Operator sustainability report / local content audit",
        confidence="medium", verified=inp.local_procurement_evidence != "none", rule_code="D4-LP-001"))
    ef.append(EvidenceField("supplier_development_programme", inp.supplier_development_programme,
        source="Operator CSR report / government local content register",
        confidence="medium", verified=inp.supplier_development_programme != "none", rule_code="D4-SDP-001"))
    ef.append(EvidenceField("reserved_services_non_local", inp.reserved_services_non_local,
        source=f"Reserved services gazette — {regime['reserved_services_rule']}",
        confidence="medium", verified=True, rule_code="D4-ADJ-001"))

    w = R["dimensions"]["D4"]["weight"]
    return DimensionScore("D4","Local Content Compliance Posture",w,round(base,2),round(adjusted,2),round(adjusted*w,4),sub,adjs,rules,gaps,ef)


def score_d5(inp, R):
    sub, adjs, rules, gaps, ef = {}, [], [], [], []
    sw = R["d5_sub_weights"]
    pt = R["d5_port_thresholds"]

    pw = R["d5_power_scores"].get(inp.power_supply, 0.0)
    sub["power_supply"] = {"score": pw, "weight": sw["power"]}
    rules.append("D5-PWR-001 v1.0")
    if inp.power_supply == "none":
        gaps.append("Power supply not documented")

    rd = R["d5_road_scores"].get(inp.road_access, 0.0)
    sub["road_access"] = {"score": rd, "weight": sw["road"]}
    rules.append("D5-ROAD-001 v1.0")

    rl = R["d5_rail_scores"].get(inp.rail_access, 0.0)
    if inp.lobito_corridor_eligible and inp.rail_access in ["operating_capacity_constrained","rail_o100km","none"]:
        bonus = R["d5_lobito_rail_bonus"]
        rl = min(20.0, rl + bonus)
        adjs.append({"rule": "D5-LOBITO-001 v1.0", "adjustment": bonus, "reason": "Lobito Corridor eligibility (NW/Copperbelt province)"})
    sub["rail_access"] = {"score": rl, "weight": sw["rail"]}
    rules.append("D5-RAIL-001 v1.0")

    ws = R["d5_water_scores"].get(inp.water_supply, 0.0)
    sub["water_supply"] = {"score": ws, "weight": sw["water"]}
    rules.append("D5-WATER-001 v1.0")
    if inp.water_supply == "none":
        gaps.append("Water supply not documented")

    if inp.port_distance_km is not None:
        if inp.port_distance_km < pt["near"]:   ps = R["d5_port_scores"]["u500km"]
        elif inp.port_distance_km <= pt["mid"]: ps = R["d5_port_scores"]["u1000km"]
        else:                                   ps = R["d5_port_scores"]["over1000km"]
        rules.append("D5-PORT-001 v1.0")
    else:
        ps = R["d5_port_scores"]["over1000km"]
        gaps.append("Port distance not documented — conservative default applied")
    sub["port_distance"] = {"score": ps, "weight": sw["port"]}

    base = pw + rd + rl + ws + ps
    adjusted = min(100, max(0, base))
    ef.append(EvidenceField("power_supply", inp.power_supply,
        source="Operator technical report / government energy regulator",
        confidence="medium", verified=inp.power_supply != "none", rule_code="D5-PWR-001"))
    ef.append(EvidenceField("road_access", inp.road_access,
        source="Government road authority / operator site disclosure",
        confidence="medium", verified=inp.road_access != "none", rule_code="D5-ROAD-001"))
    ef.append(EvidenceField("rail_access", inp.rail_access,
        source="National railway operator / Lobito Corridor project registry",
        confidence="medium", verified=inp.rail_access != "none", rule_code="D5-RAIL-001"))
    ef.append(EvidenceField("water_supply", inp.water_supply,
        source="Water licence register / environmental permit",
        confidence="medium", verified=inp.water_supply != "none", rule_code="D5-WATER-001"))
    ef.append(EvidenceField("port_distance_km", inp.port_distance_km,
        source="Geographic calculation — nearest deep water port",
        confidence="high", verified=inp.port_distance_km is not None, rule_code="D5-PORT-001"))
    ef.append(EvidenceField("lobito_corridor_eligible", inp.lobito_corridor_eligible,
        source="Lobito Corridor project registry / US DFC infrastructure mandate",
        confidence="high", verified=True, rule_code="D5-LOBITO-001"))

    w = R["dimensions"]["D5"]["weight"]
    return DimensionScore("D5","Infrastructure Readiness",w,round(base,2),round(adjusted,2),round(adjusted*w,4),sub,adjs,rules,gaps,ef)


def score_d6(inp, R):
    sub, adjs, rules, gaps, ef = {}, [], [], [], []
    sw = R["d6_sub_weights"]

    dfi = R["d6_dfi_scores"].get(inp.active_dfi_engagement, 0.0)
    sub["active_dfi_engagement"] = {"score": dfi, "weight": sw["dfi_engagement"]}
    rules.append("D6-DFI-001 v1.0")
    ef.append(EvidenceField("active_dfi_engagement", inp.active_dfi_engagement, source="IFC/AfDB/BII project portals", confidence="high", rule_code="D6-DFI-001"))

    lv = R["d6_listed_scores"].get(inp.listed_vehicle, 0.0)
    sub["listed_vehicle"] = {"score": lv, "weight": sw["listed_vehicle"]}
    rules.append("D6-LV-001 v1.0")

    cr = R["d6_capital_raise_scores"].get(inp.recent_capital_raise, 0.0)
    sub["recent_capital_raise"] = {"score": cr, "weight": sw["capital_raise"]}
    rules.append("D6-CR-001 v1.0")

    gw = R["d6_gulf_western_score"] if inp.gulf_western_investor_linked else 0.0
    sub["gulf_western_investor"] = {"score": gw, "weight": sw["gulf_western"]}
    rules.append("D6-GW-001 v1.0")

    base = dfi + lv + cr + gw
    adjusted = min(100, max(0, base))
    ef.append(EvidenceField("listed_vehicle", inp.listed_vehicle,
        source="ASX / TSX / AIM / LSE exchange announcements",
        confidence="high", verified=inp.listed_vehicle != "unlisted", rule_code="D6-LV-001"))
    ef.append(EvidenceField("recent_capital_raise", inp.recent_capital_raise,
        source="Exchange regulatory announcement / investor presentation",
        confidence="high", verified=inp.recent_capital_raise != "none", rule_code="D6-CR-001"))
    ef.append(EvidenceField("gulf_western_investor_linked", inp.gulf_western_investor_linked,
        source="Investor register / Bloomberg / Refinitiv ownership data",
        confidence="medium", verified=True, rule_code="D6-GW-001"))

    w = R["dimensions"]["D6"]["weight"]
    return DimensionScore("D6","Capital Access Signals",w,round(base,2),round(adjusted,2),round(adjusted*w,4),sub,adjs,rules,gaps,ef)


# ---------------------------------------------------------------------------
# VERDICT + FLOOR RULES
# ---------------------------------------------------------------------------

VERDICT_ORDER = ["PROCEED","PROCEED WITH CONDITIONS","MONITOR","CAUTION","AVOID"]


def apply_floor_rules(score, dimensions, inp, R):
    raw = "AVOID"
    for v in R["verdicts"]:
        if v["min"] <= score <= v["max"]:
            raw = v["code"]
            break

    triggered, constrained = [], raw
    dim_map = {d.code: d.adjusted_score for d in dimensions}

    for rule in R["floor_rules"]:
        fire = False
        if rule["condition"] == "score_below":
            if dim_map.get(rule["dimension"], 100) < rule["threshold"]:
                fire = True
        elif rule["condition"] == "beneficial_ownership_none":
            if inp.beneficial_ownership_disclosure == "none":
                fire = True
        if fire:
            triggered.append(rule)
            mv = rule["max_verdict"]
            if VERDICT_ORDER.index(mv) > VERDICT_ORDER.index(constrained):
                constrained = mv

    return constrained, triggered


def get_verdict_text(verdict, R):
    for v in R["verdicts"]:
        if v["code"] == verdict:
            return v["label"], v["next_action"]
    return "", ""


# ---------------------------------------------------------------------------
# EVIDENCE ENVELOPE
# ---------------------------------------------------------------------------

def build_evidence_envelope(inp, dimensions, meta):
    envelope = {
        "schema_version": "SEAM-ENV-v1.0",
        "asset_id": inp.asset_id,
        "asset_name": inp.asset_name,
        "jurisdiction": inp.jurisdiction,
        "jurisdiction_code": inp.jurisdiction_code,
        "commodity": inp.commodity,
        "province": inp.province,
        "methodology_version": meta["methodology_version"],
        "rules_version": meta["rules_version"],
        "generated_at": meta["generated_at"],
        "investment_readiness_score": meta["score"],
        "verdict": meta["verdict"],
        "dimensions": {
            d.code: {
                "name": d.name, "weight": d.weight,
                "raw_score": d.raw_score,
                "adjusted_score": d.adjusted_score,
                "weighted_contribution": d.weighted_contribution,
                "sub_scores": d.sub_scores,
                "adjustments": d.adjustments,
                "rules_applied": d.rules_applied,
                "data_gaps": d.data_gaps,
                "evidence_fields": [
                    {"field": e.field_name, "value": e.value, "source": e.source,
                     "source_url": e.source_url, "retrieved_date": e.retrieved_date,
                     "publication_date": e.publication_date, "confidence": e.confidence,
                     "verified": e.verified, "rule_code": e.rule_code, "notes": e.notes}
                    for e in d.evidence_fields
                ]
            }
            for d in dimensions
        },
        "floor_rules_triggered": [r["code"] for r in meta["floor_rules"]],
        "data_gaps_summary": [g for d in dimensions for g in d.data_gaps],
    }
    canonical = json.dumps(envelope, sort_keys=True, default=str)
    fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
    envelope["envelope_hash"] = fingerprint
    return envelope, fingerprint


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def compute_evidence_completeness(inp: AssetInput) -> int:
    """
    Score 0-100 reflecting how much of the evidence envelope was retrieved
    from public sources vs defaulted due to absence.

    Each field is weighted by its scoring impact.
    Defaulted fields score 0. Retrieved fields score their weight.
    """
    checks = [
        # (retrieved?, weight)
        (inp.fraser_investment_attractiveness is not None, 8),
        (inp.wb_rule_of_law_percentile is not None, 6),
        (inp.wb_regulatory_quality_percentile is not None, 6),
        (inp.eiti_implementation_status != "non-implementing", 8),
        (inp.eiti_compliant_country is True, 4),
        (inp.eiti_payment_disclosure_quality is not None, 6),
        (inp.beneficial_ownership_disclosure != "none", 6),
        (inp.resource_estimate_standard != "none", 8),
        (inp.reserve_classification != "none", 6),
        (inp.production_data_availability != "none", 6),
        (inp.commodity and "retrieval required" not in inp.commodity.lower(), 6),
        (inp.licence_holder_status != "other", 5),
        (inp.locas_filing_status != "not_filed", 5),
        (inp.power_supply != "none", 4),
        (inp.road_access != "none", 4),
        (inp.water_supply != "none", 3),
        (inp.port_distance_km is not None, 3),
        (inp.active_dfi_engagement != "none", 4),
        (inp.listed_vehicle != "unlisted", 2),
    ]
    total_weight = sum(w for _, w in checks)
    retrieved_weight = sum(w for ok, w in checks if ok)
    return round((retrieved_weight / total_weight) * 100)


def score_asset(inp: AssetInput, rules_version: str = None) -> ScoringResult:
    """Score an asset. Optional rules_version for historical reconstruction."""
    from engine.rules_loader import load_rules
    R = load_rules(rules_version or ACTIVE_VERSION)
    generated_at = datetime.now(timezone.utc).isoformat()

    dimensions = [
        score_d1(inp, R), score_d2(inp, R), score_d3(inp, R),
        score_d4(inp, R), score_d5(inp, R), score_d6(inp, R),
    ]

    raw_score = sum(d.weighted_contribution for d in dimensions)
    final_score = round(raw_score)
    verdict, floor_rules = apply_floor_rules(final_score, dimensions, inp, R)
    verdict_label, next_action = get_verdict_text(verdict, R)

    meta = {
        "methodology_version": R["methodology_version"],
        "rules_version": R["version"],
        "generated_at": generated_at,
        "score": final_score,
        "verdict": verdict,
        "floor_rules": floor_rules,
    }

    envelope, fingerprint = build_evidence_envelope(inp, dimensions, meta)

    evidence_completeness = compute_evidence_completeness(inp)

    return ScoringResult(
        asset_id=inp.asset_id,
        asset_name=inp.asset_name,
        methodology_version=R["methodology_version"],
        rules_version=R["version"],
        generated_at=generated_at,
        investment_readiness_score=final_score,
        verdict=verdict,
        verdict_label=verdict_label,
        next_action=next_action,
        dimensions=dimensions,
        floor_rules_triggered=floor_rules,
        evidence_envelope=envelope,
        envelope_hash=fingerprint,
        evidence_completeness_score=evidence_completeness,
    )




