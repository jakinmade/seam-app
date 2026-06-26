"""
SEAM Asset Store
Session 3 — Persist scored assets. Compute benchmarks.

Stores every assessment in Streamlit session state with JSON serialisation.
Benchmarks computed on-the-fly from accumulated scores.
Future: upgrade storage to database without changing the interface.
"""

import json
from datetime import datetime, timezone
from engine.scoring import ScoringResult


# ---------------------------------------------------------------------------
# STORAGE INTERFACE
# ---------------------------------------------------------------------------

def _get_store(session_state) -> dict:
    """Get or initialise the asset store from session state."""
    if "asset_store" not in session_state:
        session_state.asset_store = {}
    return session_state.asset_store


def save_assessment(session_state, result: ScoringResult, asset_input) -> None:
    """Persist a scored assessment to the store."""
    store = _get_store(session_state)

    record = {
        "asset_id":               result.asset_id,
        "asset_name":             result.asset_name,
        "jurisdiction":           asset_input.jurisdiction,
        "jurisdiction_code":      getattr(asset_input, "jurisdiction_code", ""),
        "commodity":              asset_input.commodity,
        "score":                  result.investment_readiness_score,
        "evidence_completeness":  getattr(result, "evidence_completeness_score", 0),
        "verdict":                result.verdict,
        "methodology":            result.methodology_version,
        "rules":                  result.rules_version,
        "scored_at":              result.generated_at,
        "dimension_scores": {
            d.code: d.adjusted_score
            for d in result.dimensions
        }
    }

    # Keep history per asset; latest is always first
    if result.asset_id not in store:
        store[result.asset_id] = []
    store[result.asset_id].insert(0, record)

    # Keep max 10 runs per asset
    store[result.asset_id] = store[result.asset_id][:10]


# ---------------------------------------------------------------------------
# BENCHMARK COMPUTATION
# ---------------------------------------------------------------------------

def compute_benchmarks(session_state, result: ScoringResult, asset_input) -> dict:
    """
    Compute benchmark scores for this asset against:
    - All scored assets in the store
    - Same jurisdiction
    - Same commodity

    Returns dict with benchmark values, or None if insufficient data.
    """
    store = _get_store(session_state)

    # Flatten all latest records (one per asset)
    all_records = []
    for asset_id, history in store.items():
        if history:
            all_records.append(history[0])

    if len(all_records) < 2:
        return {"insufficient_data": True, "count": len(all_records)}

    scores = [r["score"] for r in all_records]
    jurisdiction = asset_input.jurisdiction.lower()
    commodity_raw = (asset_input.commodity or "").lower()
    # Normalise commodity — strip retrieval notes
    commodity = commodity_raw.replace("unknown", "").replace("live retrieval required", "").strip()

    jur_scores = [
        r["score"] for r in all_records
        if r.get("jurisdiction", "").lower() == jurisdiction
    ]
    com_scores = [
        r["score"] for r in all_records
        if commodity and commodity in (r.get("commodity") or "").lower()
    ]

    def _stats(arr):
        if not arr:
            return None
        arr_s = sorted(arr)
        n = len(arr_s)
        return {
            "count":   n,
            "average": round(sum(arr_s) / n, 1),
            "min":     arr_s[0],
            "max":     arr_s[-1],
            "top_quartile": arr_s[max(0, int(n * 0.75))]
        }

    return {
        "insufficient_data": False,
        "global":       _stats(scores),
        "jurisdiction": _stats(jur_scores) if len(jur_scores) >= 2 else None,
        "commodity":    _stats(com_scores) if len(com_scores) >= 2 else None,
        "asset_score":  result.investment_readiness_score,
    }


def get_all_assessments(session_state) -> list:
    """Return flat list of all latest assessments, sorted by score descending."""
    store = _get_store(session_state)
    records = []
    for asset_id, history in store.items():
        if history:
            records.append(history[0])
    return sorted(records, key=lambda r: r["score"], reverse=True)
