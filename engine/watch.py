"""
SEAM Watch
Session 2 — Decision Stability, persistent storage, change intelligence.

Decision Stability: Stable / Improving / Deteriorating based on score trend.
Storage: Streamlit persistent storage (window.storage equivalent via st.session_state
         with JSON serialisation to allow future persistence upgrade).
"""

import json
import hashlib
from datetime import datetime, timezone
from engine.scoring import ScoringResult


SCORE_DELTA_THRESHOLD = 5
VERDICT_ORDER = ["PROCEED", "PROCEED WITH CONDITIONS", "MONITOR", "CAUTION", "AVOID"]


def envelope_fingerprint(envelope: dict) -> str:
    canonical = json.dumps(envelope, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()


def decision_stability(history: list) -> dict:
    """
    Compute Decision Stability from score history.
    Returns: label (Stable / Improving / Deteriorating), direction, delta.
    """
    if len(history) < 2:
        return {"label": "First assessment", "direction": None, "delta": None}

    scores = [h["score"] for h in history]
    latest = scores[-1]
    previous = scores[-2]
    delta = latest - previous

    # Trend across all history if 3+ runs
    if len(scores) >= 3:
        trend = scores[-1] - scores[0]
        if trend > SCORE_DELTA_THRESHOLD:
            label = "Improving"
            direction = "up"
        elif trend < -SCORE_DELTA_THRESHOLD:
            label = "Deteriorating"
            direction = "down"
        else:
            label = "Stable"
            direction = "flat"
    else:
        if delta > SCORE_DELTA_THRESHOLD:
            label = "Improving"
            direction = "up"
        elif delta < -SCORE_DELTA_THRESHOLD:
            label = "Deteriorating"
            direction = "down"
        else:
            label = "Stable"
            direction = "flat"

    return {
        "label": label,
        "direction": direction,
        "delta": round(delta, 1),
        "prev_score": previous,
        "curr_score": latest,
        "run_count": len(history)
    }


def diff_envelopes(prev: dict, curr: dict) -> list[dict]:
    changes = []
    prev_dims = prev.get("dimensions", {})
    curr_dims = curr.get("dimensions", {})

    for code in curr_dims:
        prev_score = prev_dims.get(code, {}).get("adjusted_score", 0)
        curr_score = curr_dims.get(code, {}).get("adjusted_score", 0)
        delta = curr_score - prev_score
        if abs(delta) >= 1:
            changes.append({
                "dimension": code,
                "dimension_name": curr_dims[code].get("name", code),
                "prev_score": prev_score,
                "curr_score": curr_score,
                "delta": round(delta, 1),
                "direction": "up" if delta > 0 else "down"
            })

    return sorted(changes, key=lambda x: abs(x["delta"]), reverse=True)


def assess_alert(prev_result: dict, curr_result: ScoringResult) -> dict:
    prev_score   = prev_result["score"]
    curr_score   = curr_result.investment_readiness_score
    prev_verdict = prev_result["verdict"]
    curr_verdict = curr_result.verdict

    score_delta          = curr_score - prev_score
    verdict_changed      = prev_verdict != curr_verdict
    material_score_change = abs(score_delta) >= SCORE_DELTA_THRESHOLD

    prev_vi = VERDICT_ORDER.index(prev_verdict) if prev_verdict in VERDICT_ORDER else 2
    curr_vi = VERDICT_ORDER.index(curr_verdict) if curr_verdict in VERDICT_ORDER else 2
    verdict_direction = "deteriorated" if curr_vi > prev_vi else "improved"

    alert = {
        "fires": verdict_changed or material_score_change,
        "severity": None,
        "score_delta": score_delta,
        "verdict_changed": verdict_changed,
        "prev_verdict": prev_verdict,
        "curr_verdict": curr_verdict,
        "verdict_direction": verdict_direction if verdict_changed else None,
        "reasons": [],
        "recommended_action": ""
    }

    if verdict_changed and curr_vi > prev_vi:
        alert["severity"] = "HIGH"
        alert["reasons"].append(f"Verdict deteriorated: {prev_verdict} to {curr_verdict}")
        alert["recommended_action"] = "Review Evidence Envelope. Verdict change affects capital allocation."
    elif verdict_changed and curr_vi < prev_vi:
        alert["severity"] = "POSITIVE"
        alert["reasons"].append(f"Verdict improved: {prev_verdict} to {curr_verdict}")
        alert["recommended_action"] = "Asset conditions improved. Refresh investment thesis."
    elif material_score_change and score_delta < 0:
        alert["severity"] = "MEDIUM"
        alert["reasons"].append(f"Score declined {abs(score_delta)} points ({prev_score} to {curr_score})")
        alert["recommended_action"] = "Review dimension changes in updated Evidence Envelope."
    elif material_score_change and score_delta > 0:
        alert["severity"] = "POSITIVE"
        alert["reasons"].append(f"Score improved {score_delta} points ({prev_score} to {curr_score})")
        alert["recommended_action"] = "Conditions improved. Asset may warrant re-assessment."

    return alert


def record_assessment(watch_list: dict, result: ScoringResult) -> dict:
    asset_id = result.asset_id
    entry = {
        "asset_id":            asset_id,
        "asset_name":          result.asset_name,
        "score":               result.investment_readiness_score,
        "evidence_completeness": getattr(result, "evidence_completeness_score", 0),
        "verdict":             result.verdict,
        "generated_at":        result.generated_at,
        "envelope_fingerprint": envelope_fingerprint(result.evidence_envelope),
        "envelope":            result.evidence_envelope,
    }

    if asset_id not in watch_list:
        watch_list[asset_id] = {"history": [], "alert": None, "stability": None}

    watch_list[asset_id]["history"].append(entry)
    watch_list[asset_id]["latest"] = entry

    history = watch_list[asset_id]["history"]

    # Decision Stability
    watch_list[asset_id]["stability"] = decision_stability(history)

    # Diff and alert
    if len(history) >= 2:
        prev = history[-2]
        dim_changes = diff_envelopes(prev["envelope"], entry["envelope"])
        alert = assess_alert(prev, result)
        alert["dim_changes"] = dim_changes
        alert["checked_at"]  = datetime.now(timezone.utc).isoformat()
        watch_list[asset_id]["alert"] = alert
    else:
        watch_list[asset_id]["alert"] = None

    return watch_list
