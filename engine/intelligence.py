"""
SEAM Intelligence Layer
Constrained technical editor. Institutional documentation register.

Role: surface what the investor does not know, grounded in the evidence envelope.
Produce investment documentation. Not prose. Not analysis. Documentation.

The intelligence engine never scores. The rules engine scores.
The intelligence engine never softens a verdict. The rules engine sets the verdict.
"""

import urllib.request
import urllib.error
import json
import os
from engine.scoring import ScoringResult, AssetInput


SEAM_SYSTEM_PROMPT = """You are producing investment documentation for a professional investor considering an African mining asset.

REGISTER: Wood Mackenzie. S&P Global Commodity Insights. SRK technical memorandum.
Cold. Factual. No personality. No persuasion. No flourish. No explanation of methodology.

THE READER:
A senior investment professional. They assume the scoring system works. They do not need it explained.
They want to know: Can I invest? Why not? What is missing? What do I do next?
Nothing else.

YOUR OUTPUT: Five blocks. Strict format. No deviation.

---

BLOCK 1 — INVESTMENT DECISION
One line per item. No sentences. No connectives.

Format exactly:
Verdict: [VERDICT]
Score: [X]/100
Evidence Completeness: [X]/100
Verdict Confidence: [High|Medium|Low]
Critical Risks: [number of floor rules triggered]
Recommended Action: [next action verbatim from engine]

Verdict Confidence rules:
- High: verdict driven by confirmed retrieved evidence, not defaults
- Medium: verdict driven by mix of retrieved evidence and defaults
- Low: verdict driven primarily by defaults — score may change materially with better retrieval

---

BLOCK 2 — CRITICAL RISKS
Only include if floor rules were triggered. Otherwise omit this block entirely.
One line per floor rule. Format:

[Rule code]: [one plain sentence stating what failed and why it matters to the investor]

No engine language. No "caps the verdict". No "maximum permissible".
State what it means for the investor. Example:
FLOOR-D2-001: Revenue transparency score is zero. Payment flows cannot be traced.
FLOOR-BO-001: Beneficial ownership is unresolved. AML/KYC compliance cannot be established.

---

BLOCK 3 — INVESTMENT DRIVERS
Three columns of facts. No essays.

Positive findings (confirmed evidence supporting investment):
- [fact]. [D-code]

Negative findings (confirmed evidence against investment):
- [fact]. [D-code]

Unknown (material fields absent from public record):
- [field or topic not retrieved]. [D-code]

Maximum five items per column. Cite dimension. One line each.

---

BLOCK 4 — EVIDENCE SUMMARY
One short paragraph. Three sentences maximum.
State: how many fields were assessed, how many retrieved, how many defaulted.
State which dimensions have Low evidence confidence and what that means for score reliability.
Do not explain the methodology. State the facts about this specific assessment.

---

BLOCK 5 — BANKABILITY CONSTRAINTS
These are binary facts from the evidence envelope. Not scored. Not opinions.
State what was found in public sources for each constraint.
If not found, state "Not confirmed in public sources."

Environmental permit: is an environmental permit or ESIA on the public record?
Community consultation: is there evidence of community engagement or FPIC process?
Social licence disputes: is there active community or NGO opposition on record?
Water licence: is a water use permit on the public record?
DFI readiness: based on the above constraints, is the asset DFI-ready, conditional, or not ready?

One sentence each. Factual. No inference.

---

BLOCK 6 — COMMODITY CONTEXT
This is context only. It does not affect the score or verdict.
State: commodity name, 12-month price trend, whether it is on a critical minerals list, primary demand driver.
Two sentences maximum. Factual. No opinion.
If commodity is unknown, state: "Commodity not identified during retrieval."
Critical mineral lists: EU Critical Raw Materials Act 2024, US DOE Critical Materials 2023, UK Critical Minerals List 2023.

---

BLOCK 6 — VERDICT AND NEXT ACTION
Two to four sentences. Decision-first.
First sentence: verdict and recommended action.
Remaining sentences: material conditions or risks relevant to that action only.
No floor rule code numbers in this block. Plain language only.

---

WRITING RULES — ABSOLUTE:
No em dashes. Use full stops.
No semicolons for listing. Use full stops.
No: "This means", "This reflects", "Therefore", "Thus", "Hence", "As such"
No: "Combined with", "Each of which", "Independently", "Moreover", "Furthermore"
No: "It should be noted", "It is worth noting", "Importantly"
No: "Floor rule", "aggregate score", "maximum permissible", "caps the verdict"
No: "Standalone", "disqualifying condition", "conservative outcome"
No explanatory sentences about how the engine works.
UK English. Short declarative sentences. Every word earns its place.

EVIDENCE BOUNDARY:
Only assert facts present in the provided data fields.
If a field is defaulted (marked NOT RETRIEVED), say what is absent. Never state it as confirmed fact.
WRONG: "Zambia is not EITI-compliant."
RIGHT: "EITI status: not confirmed."
WRONG: "No institutional investor has assessed this asset."
RIGHT: "DFI engagement: no evidence found."

---

Return exactly this JSON. No preamble. No markdown. No explanation:
{
  "investment_decision": {
    "verdict": "...",
    "score": 0,
    "evidence_completeness": 0,
    "verdict_confidence": "High|Medium|Low",
    "critical_risks": 0,
    "recommended_action": "..."
  },
  "critical_risks": ["risk 1", "risk 2"],
  "investment_drivers": {
    "positive": ["fact (D-code)", "fact (D-code)"],
    "negative": ["fact (D-code)", "fact (D-code)"],
    "unknown": ["field absent (D-code)", "field absent (D-code)"]
  },
  "evidence_summary": "...",
  "dimension_findings": {
    "D1": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D2": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D3": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D4": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D5": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D6": {"finding": "...", "evidence_confidence": "High|Medium|Low"}
  },
  "verdict_section": "...",
  "commodity_context": {
    "commodity": "primary commodity name",
    "outlook": "Bullish or Neutral or Bearish",
    "outlook_rationale": "one sentence — why, from public data",
    "critical_mineral": true or false,
    "critical_mineral_lists": ["EU CRM", "US DOE", "UK CML"],
    "lobito_corridor_relevant": true or false,
    "price_trend_12m": "Rising or Stable or Falling",
    "demand_driver": "one sentence on primary demand driver"
  },
  "bankability_constraints": {
    "environmental_permit": "Permitted | In Progress | Not Filed | Unknown",
    "esia_on_record": true or false,
    "community_consultation": "Documented | Partial | None",
    "social_licence_disputes": true or false,
    "water_licence": "Permitted | Pending | Not Filed | Unknown",
    "constraint_summary": "one sentence — overall bankability constraint status",
    "dfi_readiness": "Ready | Conditional | Not Ready"
  },
  "ic_summary": {
    "phase_recommendation": "Proceed to Phase II Due Diligence | Proceed with Conditions to Phase II | Place on Watch | Do Not Proceed",
    "rationale": "one sentence — direct IC language, no hedging.",
    "time_to_decision": "e.g. 30–60 days | 60–90 days | 90+ days | Not recommended",
    "investment_strength": "Strong | Moderate | Weak",
    "operational_risk": "Low | Medium | High | Critical",
    "governance_risk": "Low | Medium | High | Critical",
    "political_risk": "Low | Medium | High | Critical",
    "capital_readiness": "Ready | Conditional | Not Ready"
  },
  "priority_actions": [
    {
      "rank": 1,
      "action": "short imperative",
      "dimension": "D2",
      "effort": "Low | Medium | High",
      "diligence_delay_days": 14
    }
  ],
  "priority_actions_note": "Maximum 3 actions. Rank by materiality to verdict.",
  "remediation": {
    "expected_score_after": 0,
    "score_sensitivity": 3,
    "estimated_effort": "Low | Medium | High",
    "estimated_diligence_delay": "e.g. 30–45 days"
  }
}"""


def build_prompt(result: ScoringResult, inp: AssetInput) -> str:

    dim_summary = []
    for d in result.dimensions:
        gaps = f" GAPS: {'; '.join(d.data_gaps)}" if d.data_gaps else ""
        adjs = ""
        if d.adjustments:
            adjs = " ADJ: " + "; ".join(
                f"{a['reason']} ({'+' if (a['adjustment'] or 0) > 0 else ''}{a['adjustment']}pts)"
                for a in d.adjustments if a.get('adjustment') is not None
            )
        dim_summary.append(
            f"{d.code} {d.name} (weight {d.weight*100:.0f}%): {d.adjusted_score}/100{adjs}{gaps}"
        )

    floor_text = ""
    if result.floor_rules_triggered:
        floor_text = "\nFLOOR RULES TRIGGERED:\n" + "\n".join(
            f"- {r['code']}: {r['description']}" for r in result.floor_rules_triggered
        )

    def rs(val, default_note="default"):
        if val is None:
            return f"NOT RETRIEVED ({default_note})"
        return f"RETRIEVED: {val}"

    commodity_ok = inp.commodity and "retrieval required" not in inp.commodity.lower()
    eiti_status_ok = inp.eiti_implementation_status != "non-implementing"
    eiti_country_ok = inp.eiti_compliant_country is True

    total_fields = 19
    retrieved_count = sum([
        inp.fraser_investment_attractiveness is not None,
        inp.wb_rule_of_law_percentile is not None,
        inp.wb_regulatory_quality_percentile is not None,
        eiti_status_ok,
        eiti_country_ok,
        inp.eiti_payment_disclosure_quality is not None,
        inp.beneficial_ownership_disclosure != "none",
        inp.resource_estimate_standard != "none",
        inp.reserve_classification != "none",
        inp.production_data_availability != "none",
        commodity_ok,
        inp.licence_holder_status != "other",
        inp.locas_filing_status != "not_filed",
        inp.power_supply != "none",
        inp.road_access != "none",
        inp.water_supply != "none",
        inp.port_distance_km is not None,
        inp.active_dfi_engagement != "none",
        inp.listed_vehicle != "unlisted",
    ])
    defaulted_count = total_fields - retrieved_count

    return f"""ASSET: {result.asset_name}
ASSET ID: {result.asset_id}
JURISDICTION: {inp.jurisdiction} ({inp.jurisdiction_code})
COMMODITY: {inp.commodity} [{'RETRIEVED' if commodity_ok else 'NOT RETRIEVED'}]
PROVINCE: {inp.province}
METHODOLOGY: {result.methodology_version} | RULES: {result.rules_version}
GENERATED: {result.generated_at}

INVESTMENT READINESS SCORE: {result.investment_readiness_score}/100
EVIDENCE COMPLETENESS: {result.evidence_completeness_score}/100
VERDICT: {result.verdict}
NEXT ACTION: {result.next_action}
FLOOR RULES TRIGGERED: {len(result.floor_rules_triggered)}
FIELDS ASSESSED: {total_fields} | RETRIEVED: {retrieved_count} | DEFAULTED: {defaulted_count}

DIMENSION SCORES:
{chr(10).join(dim_summary)}
{floor_text}

FIELD DATA (RETRIEVED vs NOT RETRIEVED):

D1 Jurisdiction:
  Fraser Investment Attractiveness: {rs(inp.fraser_investment_attractiveness, 'neutral default 50')}
  WB Rule of Law: {rs(inp.wb_rule_of_law_percentile, 'conservative default 40')}
  WB Regulatory Quality: {rs(inp.wb_regulatory_quality_percentile, 'conservative default 40')}
  Regulatory change 12m: RETRIEVED: {inp.regulatory_change_last_12m}
  Mining code revision: RETRIEVED: {inp.mining_code_revision_in_progress}
  Investment arbitration 5y: RETRIEVED: {inp.investment_arbitration_last_5y}
  Bilateral Investment Treaty: RETRIEVED: {inp.bilateral_investment_treaty}
  EITI compliant country: {'RETRIEVED: True' if eiti_country_ok else 'NOT RETRIEVED (default False)'}

D2 Revenue Transparency:
  EITI status: {'RETRIEVED: ' + inp.eiti_implementation_status if eiti_status_ok else 'NOT RETRIEVED (default: non-implementing)'}
  Beneficial ownership: RETRIEVED: {inp.beneficial_ownership_disclosure}
  EITI payment quality: {rs(inp.eiti_payment_disclosure_quality, 'scored zero')}
  PEP in ownership chain: RETRIEVED: {inp.pep_in_ownership_chain}
  FATF grey list: RETRIEVED: {inp.fatf_grey_list_jurisdiction}
  Payment data gap 24m: RETRIEVED: {inp.payment_data_gap_over_24m}

D3 Asset Data:
  Resource estimate standard: RETRIEVED: {inp.resource_estimate_standard}
  Reserve classification: RETRIEVED: {inp.reserve_classification}
  Production data: RETRIEVED: {inp.production_data_availability}
  Exploration stage: RETRIEVED: {inp.exploration_stage}
  Resource conflict: RETRIEVED: {inp.unresolved_resource_conflict}
  Employee estimate: RETRIEVED: {inp.estimate_by_company_employee}
  No technical report: RETRIEVED: {inp.no_independent_technical_report}

D4 Local Content:
  Licence holder: RETRIEVED: {inp.licence_holder_status}
  Compliance filing: RETRIEVED: {inp.locas_filing_status}
  Local procurement: RETRIEVED: {inp.local_procurement_evidence}
  Supplier development: RETRIEVED: {inp.supplier_development_programme}
  Reserved services non-local: RETRIEVED: {inp.reserved_services_non_local}

D5 Infrastructure:
  Power supply: RETRIEVED: {inp.power_supply}
  Road access: RETRIEVED: {inp.road_access}
  Rail access: RETRIEVED: {inp.rail_access}
  Water supply: RETRIEVED: {inp.water_supply}
  Port distance: {rs(inp.port_distance_km, 'conservative default')}
  Lobito Corridor: RETRIEVED: {inp.lobito_corridor_eligible}

D6 Capital Access:
  DFI engagement: RETRIEVED: {inp.active_dfi_engagement}
  Listed vehicle: RETRIEVED: {inp.listed_vehicle}
  Capital raise: RETRIEVED: {inp.recent_capital_raise}
  Gulf/Western investor: RETRIEVED: {inp.gulf_western_investor_linked}"""


def _extract_json(text: str) -> str:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts[1::2]:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                return candidate
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def call_intelligence_engine(prompt: str, cache_key: str = None) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return _mock_intelligence(prompt)

    # Cache check — same inputs = same output, skip API call
    if cache_key and cache_key in _NARRATIVE_CACHE:
        return _NARRATIVE_CACHE[cache_key]

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 2000,
        "temperature": 0,
        "system": SEAM_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": api_key,
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(body)
            msg = err.get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise RuntimeError(f"API error {e.code}: {msg}") from None

    text_blocks = [
        block["text"].strip()
        for block in data.get("content", [])
        if block.get("type") == "text" and block.get("text", "").strip()
    ]
    if not text_blocks:
        raise ValueError(f"No text in response. stop_reason={data.get('stop_reason')}")

    raw = _extract_json(text_blocks[-1])
    result_data = json.loads(raw)
    if cache_key:
        _NARRATIVE_CACHE[cache_key] = result_data
    return result_data


def _mock_intelligence(prompt: str) -> dict:
    lines = prompt.split("\n")
    score = next((l.replace("INVESTMENT READINESS SCORE:", "").replace("/100","").strip()
                  for l in lines if "INVESTMENT READINESS SCORE:" in l), "N/A")
    verdict = next((l.replace("VERDICT:", "").strip() for l in lines if l.startswith("VERDICT:")), "N/A")
    action = next((l.replace("NEXT ACTION:", "").strip() for l in lines if l.startswith("NEXT ACTION:")), "")

    return {
        "investment_decision": {
            "verdict": verdict,
            "score": int(score) if score.isdigit() else 0,
            "evidence_completeness": 0,
            "verdict_confidence": "Low",
            "critical_risks": 0,
            "recommended_action": action
        },
        "critical_risks": [],
        "investment_drivers": {
            "positive": ["[Live in Streamlit]"],
            "negative": ["[Live in Streamlit]"],
            "unknown": ["[Live in Streamlit]"]
        },
        "evidence_summary": "[Live in Streamlit]",
        "dimension_findings": {
            "D1": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D2": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D3": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D4": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D5": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D6": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
        },
        "verdict_section": f"Verdict: {verdict}. [Live in Streamlit]",
        "bankability_constraints": {
            "environmental_permit": "Unknown",
            "esia_on_record": False,
            "community_consultation": "None",
            "social_licence_disputes": False,
            "water_licence": "Unknown",
            "constraint_summary": "Live in Streamlit",
            "dfi_readiness": "Not Ready"
        },
        "commodity_context": {
            "commodity": "Unknown",
            "outlook": "Neutral",
            "outlook_rationale": "Live in Streamlit",
            "critical_mineral": False,
            "critical_mineral_lists": [],
            "lobito_corridor_relevant": False,
            "price_trend_12m": "Stable",
            "demand_driver": "Live in Streamlit"
        },
        "ic_summary": {
            "phase_recommendation": "Live in Streamlit",
            "rationale": "Live in Streamlit",
            "time_to_decision": "Live in Streamlit",
            "investment_strength": "Moderate",
            "operational_risk": "Medium",
            "governance_risk": "Medium",
            "political_risk": "Medium",
            "capital_readiness": "Conditional"
        },
        "priority_actions": [],
        "remediation": {
            "expected_score_after": 0,
            "score_sensitivity": 3,
            "estimated_effort": "Medium",
            "estimated_diligence_delay": "Live in Streamlit"
        }
    }


# Narrative cache — keyed on envelope hash.
# Same score = same narrative. Avoids redundant API calls on re-renders.
_NARRATIVE_CACHE: dict = {}


def generate_intelligence(result: ScoringResult, inp: AssetInput) -> dict:
    prompt = build_prompt(result, inp)
    return call_intelligence_engine(prompt, cache_key=result.envelope_hash)




