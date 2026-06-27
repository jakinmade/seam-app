"""
SEAM Test Harness
=================
Tests the scoring engine against known assets using seed data only (no API calls).
Catches dimension collapse, floor rule misfires, missing seed coverage, and verdict drift.

Two entry points:
  CLI:       python seam_test_harness.py
  Streamlit: import run_harness from this module, call run_harness()
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dataclasses import dataclass, field
from typing import Optional
from engine.known_assets import apply_seeds
from engine.scoring import score_asset, AssetInput


# ---------------------------------------------------------------------------
# TEST ASSET DEFINITIONS
# Each defines: asset name, jurisdiction code, and expected behaviour.
# expected_verdict: exact match required
# min_score / max_score: score must fall within this band
# min_dimension_scores: each dimension must be at least this value
# no_floor_rules: if True, no floor rules should trigger
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "label": "KCM / Konkola Copper Mines (Zambia)",
        "asset_name": "Konkola Copper Mines (KCM)",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "expected_verdict": "PROCEED WITH CONDITIONS",
        "min_score": 60,
        "max_score": 75,
        "min_dimension_scores": {"D1": 30, "D2": 60, "D3": 80, "D4": 15, "D5": 40, "D6": 30},
        "no_floor_rules": True,
        "notes": "Major producing Copperbelt asset. Seeds cover all critical fields.",
    },
    {
        "label": "Lumwana (Zambia)",
        "asset_name": "Lumwana Copper Mine",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "expected_verdict": "PROCEED WITH CONDITIONS",
        "min_score": 62,
        "max_score": 78,
        "min_dimension_scores": {"D1": 30, "D2": 60, "D3": 80, "D4": 15, "D5": 35, "D6": 60},
        "no_floor_rules": True,
        "notes": "Barrick asset. Listed vehicle seeded. Lobito corridor eligible.",
    },
    {
        "label": "Mingomba (Zambia — exploration)",
        "asset_name": "Mingomba Copper Project",
        "jurisdiction": "Zambia",
        "jurisdiction_code": "ZMB",
        "expected_verdict": None,  # No fixed verdict — exploration stage, lower score expected
        "min_score": 20,
        "max_score": 60,
        "min_dimension_scores": {"D1": 30, "D2": 0, "D3": 0, "D4": 0, "D5": 0, "D6": 0},
        "no_floor_rules": False,
        "notes": "KoBold exploration asset. D3/D4/D5 legitimately low — no production data.",
    },
    {
        "label": "Kamoa-Kakula (DRC)",
        "asset_name": "Kamoa-Kakula Copper Complex",
        "jurisdiction": "DRC",
        "jurisdiction_code": "COD",
        "expected_verdict": None,
        "min_score": 35,
        "max_score": 70,
        "min_dimension_scores": {"D1": 5, "D2": 5, "D3": 80, "D4": 5, "D5": 20, "D6": 0},
        "no_floor_rules": False,
        "notes": "DRC jurisdiction drags D1 hard (Fraser 28.4, WB ROL 4.3). D3 should be strong.",
    },
    {
        "label": "Obuasi (Ghana)",
        "asset_name": "Obuasi Gold Mine",
        "jurisdiction": "Ghana",
        "jurisdiction_code": "GHA",
        "expected_verdict": None,
        "min_score": 50,
        "max_score": 80,
        "min_dimension_scores": {"D1": 40, "D2": 60, "D3": 80, "D4": 15, "D5": 50, "D6": 60},
        "no_floor_rules": True,
        "notes": "Ghana is strongest jurisdiction. AngloGold listed. Port distance 250km.",
    },
    {
        "label": "Geita (Tanzania)",
        "asset_name": "Geita Gold Mine",
        "jurisdiction": "Tanzania",
        "jurisdiction_code": "TZA",
        "expected_verdict": None,
        "min_score": 45,
        "max_score": 75,
        "min_dimension_scores": {"D1": 30, "D2": 30, "D3": 80, "D4": 10, "D5": 45, "D6": 10},
        "no_floor_rules": True,
        "notes": "AngloGold listed. Tanzania EITI compliant. Port 110km.",
    },
    {
        "label": "Husab Uranium (Namibia)",
        "asset_name": "Husab Uranium Mine",
        "jurisdiction": "Namibia",
        "jurisdiction_code": "NAM",
        "expected_verdict": None,
        "min_score": 50,
        "max_score": 80,
        "min_dimension_scores": {"D1": 40, "D2": 30, "D3": 80, "D4": 10, "D5": 55, "D6": 0},
        "no_floor_rules": True,
        "notes": "Namibia strong jurisdiction. Port 30km. Operating rail.",
    },
    {
        "label": "Fekola (Mali — security risk context)",
        "asset_name": "Fekola Gold Mine",
        "jurisdiction": "Mali",
        "jurisdiction_code": "MLI",
        "expected_verdict": None,
        "min_score": 30,
        "max_score": 65,
        "min_dimension_scores": {"D1": 15, "D2": 30, "D3": 80, "D4": 10, "D5": 20, "D6": 10},
        "no_floor_rules": False,
        "notes": "Mali Fraser 32.7, WB ROL 11.5. D1 floor likely. D3 strong (B2Gold listed, NI43-101).",
    },
]


# ---------------------------------------------------------------------------
# SEED → AssetInput
# ---------------------------------------------------------------------------

def build_asset_from_seeds(asset_name: str, jurisdiction: str, jurisdiction_code: str) -> AssetInput:
    seed = apply_seeds({}, asset_name, jurisdiction_code)
    return AssetInput(
        asset_id=f"{jurisdiction_code}-TEST",
        asset_name=asset_name,
        jurisdiction=jurisdiction,
        jurisdiction_code=seed.get("jurisdiction_code", jurisdiction_code),
        commodity=seed.get("commodity", "Unknown"),
        province=seed.get("province", "Unknown"),
        fraser_investment_attractiveness=seed.get("fraser_investment_attractiveness"),
        wb_rule_of_law_percentile=seed.get("wb_rule_of_law_percentile"),
        wb_regulatory_quality_percentile=seed.get("wb_regulatory_quality_percentile"),
        regulatory_change_last_12m=seed.get("regulatory_change_last_12m", False),
        mining_code_revision_in_progress=seed.get("mining_code_revision_in_progress", False),
        investment_arbitration_last_5y=seed.get("investment_arbitration_last_5y", False),
        bilateral_investment_treaty=seed.get("bilateral_investment_treaty", False),
        eiti_compliant_country=seed.get("eiti_compliant_country", False),
        eiti_implementation_status=seed.get("eiti_implementation_status", "non-implementing"),
        beneficial_ownership_disclosure=seed.get("beneficial_ownership_disclosure", "none"),
        eiti_payment_disclosure_quality=seed.get("eiti_payment_disclosure_quality"),
        pep_in_ownership_chain=seed.get("pep_in_ownership_chain", False),
        fatf_grey_list_jurisdiction=seed.get("fatf_grey_list_jurisdiction", False),
        payment_data_gap_over_24m=seed.get("payment_data_gap_over_24m", False),
        resource_estimate_standard=seed.get("resource_estimate_standard", "none"),
        reserve_classification=seed.get("reserve_classification", "none"),
        production_data_availability=seed.get("production_data_availability", "none"),
        exploration_stage=seed.get("exploration_stage", "exploration"),
        unresolved_resource_conflict=seed.get("unresolved_resource_conflict", False),
        estimate_by_company_employee=seed.get("estimate_by_company_employee", False),
        no_independent_technical_report=seed.get("no_independent_technical_report", False),
        licence_holder_status=seed.get("licence_holder_status", "other"),
        locas_filing_status=seed.get("locas_filing_status", "not_filed"),
        local_procurement_evidence=seed.get("local_procurement_evidence", "none"),
        supplier_development_programme=seed.get("supplier_development_programme", "none"),
        reserved_services_non_local=seed.get("reserved_services_non_local", False),
        power_supply=seed.get("power_supply", "none"),
        road_access=seed.get("road_access", "none"),
        rail_access=seed.get("rail_access", "none"),
        water_supply=seed.get("water_supply", "none"),
        port_distance_km=seed.get("port_distance_km"),
        lobito_corridor_eligible=seed.get("lobito_corridor_eligible", False),
        active_dfi_engagement=seed.get("active_dfi_engagement", "none"),
        listed_vehicle=seed.get("listed_vehicle", "unlisted"),
        recent_capital_raise=seed.get("recent_capital_raise", "none"),
        gulf_western_investor_linked=seed.get("gulf_western_investor_linked", False),
    )


# ---------------------------------------------------------------------------
# CHECKS
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    severity: str = "ERROR"   # ERROR | WARN


def check_score_band(result, tc) -> CheckResult:
    s = result.investment_readiness_score
    ok = tc["min_score"] <= s <= tc["max_score"]
    return CheckResult(
        "Score within expected band",
        ok,
        f"{s}/100 — expected {tc['min_score']}–{tc['max_score']}",
        "ERROR" if not ok else "ERROR",
    )


def check_verdict(result, tc) -> Optional[CheckResult]:
    if tc["expected_verdict"] is None:
        return None
    ok = result.verdict == tc["expected_verdict"]
    return CheckResult(
        "Verdict matches expected",
        ok,
        f"got {result.verdict}, expected {tc['expected_verdict']}",
        "ERROR",
    )


def check_dimension_floors(result, tc) -> list:
    checks = []
    dim_map = {d.code: d.adjusted_score for d in result.dimensions}
    for code, min_score in tc["min_dimension_scores"].items():
        actual = dim_map.get(code, 0)
        ok = actual >= min_score
        checks.append(CheckResult(
            f"{code} above minimum ({min_score})",
            ok,
            f"{code} scored {round(actual,1)}, minimum {min_score}",
            "ERROR",
        ))
    return checks


def check_floor_rules(result, tc) -> CheckResult:
    triggered = [r["code"] for r in result.floor_rules_triggered]
    if tc["no_floor_rules"]:
        ok = len(triggered) == 0
        return CheckResult(
            "No floor rules triggered",
            ok,
            f"triggered: {triggered}" if triggered else "clean",
            "ERROR",
        )
    return CheckResult(
        "Floor rules (informational)",
        True,
        f"triggered: {triggered}" if triggered else "none",
        "WARN",
    )


def check_zero_dimensions(result, inp) -> list:
    """Flag dimensions scoring zero unless the asset stage or type justifies it."""
    checks = []
    is_exploration = getattr(inp, "exploration_stage", "exploration") == "exploration"
    for d in result.dimensions:
        if d.adjusted_score > 0:
            continue
        # D6 legitimately zero when no DFI/listing/capital raise seeded
        if d.code == "D6":
            continue
        # D4 legitimately zero for exploration assets (no licence holder / LOCAS filing expected)
        if d.code == "D4" and is_exploration:
            continue
        # D3 legitimately low for exploration assets but not zero if stage is seeded
        if d.code == "D3" and is_exploration:
            continue
        checks.append(CheckResult(
            f"{d.code} zero score",
            False,
            f"{d.code} ({d.name}) scored 0 — check seed coverage",
            "ERROR",
        ))
    return checks


def check_evidence_completeness(result) -> CheckResult:
    ec = result.evidence_completeness_score
    ok = ec >= 40
    return CheckResult(
        "Evidence completeness ≥ 40",
        ok,
        f"completeness: {ec}/100",
        "WARN" if not ok else "WARN",
    )


def check_commodity_populated(inp) -> CheckResult:
    bad = not inp.commodity or "unknown" in inp.commodity.lower() or "retrieval" in inp.commodity.lower()
    return CheckResult(
        "Commodity field populated",
        not bad,
        f"commodity: {inp.commodity}",
        "ERROR",
    )


def check_envelope_hash(result) -> CheckResult:
    ok = bool(result.envelope_hash) and len(result.envelope_hash) == 64
    return CheckResult(
        "Evidence envelope hash present",
        ok,
        f"hash: {result.envelope_hash[:16]}..." if ok else "missing or malformed",
        "ERROR",
    )


def check_evidence_book(result) -> CheckResult:
    """Attempt to generate the Evidence Book PDF. Catches silent failures."""
    try:
        import tempfile, os
        from engine.evidence_book import generate_evidence_book
        with tempfile.TemporaryDirectory() as tmpdir:
            path = generate_evidence_book(result, output_dir=tmpdir)
            size = os.path.getsize(path)
            ok = size > 10_000  # Minimum viable PDF
            return CheckResult(
                "Evidence Book PDF generates",
                ok,
                f"{size:,} bytes" if ok else f"PDF too small ({size} bytes) — likely render failure",
                "ERROR",
            )
    except Exception as e:
        return CheckResult(
            "Evidence Book PDF generates",
            False,
            f"{type(e).__name__}: {str(e)[:120]}",
            "ERROR",
        )


# ---------------------------------------------------------------------------
# CORE RUNNER
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    label: str
    asset_name: str
    score: int
    verdict: str
    evidence_completeness: int
    floor_rules: list
    checks: list
    passed: int
    failed: int
    warned: int
    dimension_scores: dict
    notes: str


def run_single(tc: dict) -> TestResult:
    inp = build_asset_from_seeds(tc["asset_name"], tc["jurisdiction"], tc["jurisdiction_code"])
    result = score_asset(inp)

    checks = []
    checks.append(check_score_band(result, tc))

    v = check_verdict(result, tc)
    if v:
        checks.append(v)

    checks += check_dimension_floors(result, tc)
    checks.append(check_floor_rules(result, tc))
    checks += check_zero_dimensions(result, inp)
    checks.append(check_evidence_completeness(result))
    checks.append(check_commodity_populated(inp))
    checks.append(check_envelope_hash(result))
    checks.append(check_evidence_book(result))

    passed  = sum(1 for c in checks if c.passed)
    failed  = sum(1 for c in checks if not c.passed and c.severity == "ERROR")
    warned  = sum(1 for c in checks if not c.passed and c.severity == "WARN")

    dim_scores = {d.code: round(d.adjusted_score, 1) for d in result.dimensions}

    return TestResult(
        label=tc["label"],
        asset_name=tc["asset_name"],
        score=result.investment_readiness_score,
        verdict=result.verdict,
        evidence_completeness=result.evidence_completeness_score,
        floor_rules=[r["code"] for r in result.floor_rules_triggered],
        checks=checks,
        passed=passed,
        failed=failed,
        warned=warned,
        dimension_scores=dim_scores,
        notes=tc["notes"],
    )


def run_harness() -> list:
    return [run_single(tc) for tc in TEST_CASES]


# ---------------------------------------------------------------------------
# CLI OUTPUT
# ---------------------------------------------------------------------------

def _colour(text, code):
    return f"\033[{code}m{text}\033[0m"

def green(t): return _colour(t, "32")
def red(t):   return _colour(t, "31")
def yellow(t):return _colour(t, "33")
def bold(t):  return _colour(t, "1")


def print_cli(results: list):
    total_pass = total_fail = total_warn = 0

    for r in results:
        status = red("FAIL") if r.failed else (yellow("WARN") if r.warned else green("PASS"))
        print(f"\n{bold(r.label)}  [{status}]")
        print(f"  Score: {r.score}/100  Verdict: {r.verdict}  Completeness: {r.evidence_completeness}/100")
        dim_line = "  " + "  ".join(f"{k}:{v}" for k, v in r.dimension_scores.items())
        print(dim_line)
        if r.floor_rules:
            print(f"  Floor rules: {', '.join(r.floor_rules)}")

        for c in r.checks:
            if c.passed:
                print(f"    {green('✓')} {c.name}")
            elif c.severity == "ERROR":
                print(f"    {red('✗')} {c.name} — {c.detail}")
            else:
                print(f"    {yellow('!')} {c.name} — {c.detail}")

        total_pass += r.passed
        total_fail += r.failed
        total_warn += r.warned

    print(f"\n{'─'*60}")
    overall = red("FAIL") if total_fail else (yellow("WARN") if total_warn else green("ALL PASS"))
    print(f"Result: {overall}  |  {total_pass} passed  {total_fail} failed  {total_warn} warned")
    print(f"Assets tested: {len(results)}")
    return total_fail == 0


if __name__ == "__main__":
    results = run_harness()
    ok = print_cli(results)
    sys.exit(0 if ok else 1)
