"""
SEAM Sprint 2 Runner
Score all three assets -> Claude intelligence layer -> PDF reports.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.scoring import score_asset
from engine.intelligence import generate_intelligence
from engine.report import generate_pdf
from data.phase1_assets import ALL_ASSETS


def main():
    print("\n  SEAM — Sprint 2 Run")
    print("  Engine + Intelligence Layer + PDF Reports\n")

    for asset_id, asset_input in ALL_ASSETS.items():

        print(f"  [{asset_id}] Scoring engine...")
        result = score_asset(asset_input)
        print(f"         Score: {result.investment_readiness_score}/100  |  Verdict: {result.verdict}")

        print(f"  [{asset_id}] Intelligence layer (Claude)...")
        intel = generate_intelligence(result, asset_input)
        print(f"         Intelligence sections generated.")

        print(f"  [{asset_id}] Generating PDF...")
        pdf_path = generate_pdf(result, intel, asset_input)
        print(f"         Report written -> {pdf_path}\n")

    print("  Sprint 2 complete. All reports in /output/\n")


if __name__ == "__main__":
    main()
