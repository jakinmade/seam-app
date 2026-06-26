"""
SEAM Sprint 1 Runner
Scores all three Phase 1 assets and writes results to output/.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.scoring import score_asset
from data.phase1_assets import ALL_ASSETS


VERDICT_COLOURS = {
    "PROCEED": "✅",
    "PROCEED WITH CONDITIONS": "🟡",
    "MONITOR": "🔵",
    "CAUTION": "🟠",
    "AVOID": "🔴",
}


def print_result(result):
    icon = VERDICT_COLOURS.get(result.verdict, "⚪")
    print(f"\n{'='*65}")
    print(f"  {result.asset_name}")
    print(f"  {result.asset_id}  |  {result.methodology_version}  |  {result.rules_version}")
    print(f"{'='*65}")
    print(f"  INVESTMENT READINESS SCORE : {result.investment_readiness_score} / 100")
    print(f"  VERDICT                    : {icon}  {result.verdict}")
    print(f"{'='*65}")
    print(f"\n  DIMENSION SCORES\n")
    for d in result.dimensions:
        bar = "█" * int(d.adjusted_score / 5)
        print(f"  {d.code}  {d.name:<36} {d.adjusted_score:>5.1f}  {bar}")
    print()

    if result.floor_rules_triggered:
        print(f"  FLOOR RULES TRIGGERED")
        for rule in result.floor_rules_triggered:
            print(f"    • {rule['code']}: {rule['description']}")
        print()

    gaps = [g for d in result.dimensions for g in d.data_gaps]
    if gaps:
        print(f"  DATA GAPS")
        for gap in gaps:
            print(f"    • {gap}")
        print()

    print(f"  NEXT ACTION")
    print(f"    {result.next_action}")
    print()


def main():
    os.makedirs("output", exist_ok=True)

    print("\n  SEAM — Structured Evidence for African Mining")
    print("  Sprint 1 Scoring Run  |  Methodology v1.0\n")

    all_results = []

    for asset_id, asset_input in ALL_ASSETS.items():
        result = score_asset(asset_input)
        print_result(result)
        all_results.append(result)

        # Write evidence envelope to output/
        envelope_path = f"output/{asset_id}_evidence_envelope.json"
        with open(envelope_path, "w") as f:
            json.dump(result.evidence_envelope, f, indent=2)
        print(f"  Evidence envelope written → {envelope_path}\n")

    # Summary table
    print(f"\n{'='*65}")
    print(f"  SPRINT 1 SUMMARY")
    print(f"{'='*65}")
    print(f"  {'Asset':<42} {'Score':>5}  {'Verdict'}")
    print(f"  {'-'*60}")
    for r in all_results:
        icon = VERDICT_COLOURS.get(r.verdict, "⚪")
        print(f"  {r.asset_name:<42} {r.investment_readiness_score:>5}  {icon} {r.verdict}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
