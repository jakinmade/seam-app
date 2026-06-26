"""
SEAM Intelligence Layer
Sprint 2 — Constrained technical editor. Institutional documentation register.

Role:
1. Surface what the investor does not know — grounded in the evidence envelope
2. Produce institutional documentation, not intelligent prose

The intelligence engine never scores. The rules engine scores.
The intelligence engine never softens a verdict. The rules engine sets the verdict.
The intelligence engine produces technical documentation.
"""

import urllib.request
import urllib.error
import json
import os
from engine.scoring import ScoringResult, AssetInput


# ---------------------------------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------------------------------

SEAM_SYSTEM_PROMPT = """You are a technical editor producing institutional investment documentation for African mining assets.

You are not writing an essay. You are not writing a narrative. You are producing a due diligence memorandum.

YOUR REGISTER: Bloomberg Intelligence. Fitch Ratings. SRK Consulting technical report. Aircraft incident report.
Cold. Clinical. Factual. Cited. No personality. No persuasion. No flourish.

YOU RECEIVE:
- Deterministic scores and verdicts from the SEAM Rules Engine
- Six dimension scores with sub-scores, adjustments and data gaps
- Raw asset data fields with retrieval status (RETRIEVED vs NOT RETRIEVED)

YOUR OUTPUT: Four documentation blocks. Each block has a strict format defined below.

---

BLOCK 1 — PRINCIPAL FINDING
Two or three sentences maximum.
State the score, the verdict, and the single most material fact that explains both.
No preamble. No asset name repetition. No rhetorical framing.

EXAMPLE OUTPUT:
Score: 12/100. Verdict: AVOID. Three floor rules triggered independently (FLOOR-D2-001, FLOOR-D3-001, FLOOR-BO-001), each capping the maximum permissible verdict at CAUTION. The aggregate score then produced AVOID.

---

BLOCK 2 — DIMENSION FINDINGS
One entry per dimension. Fixed format:

[D-CODE] [Dimension Name]
Score: X/100 | Weight: X% | Evidence Confidence: High / Medium / Low
[Two to four declarative sentences. No more.]
[List data gaps as bullet points, prefixed with "Gap:"]

Evidence Confidence levels:
- High: key sub-fields retrieved from verified public sources
- Medium: some fields retrieved, some defaulted
- Low: most fields defaulted or absent

SENTENCE RULES FOR DIMENSION FINDINGS:
- State the score. State what drives it. State what it means for the investor.
- One fact per sentence.
- No explanatory connectives: no "This means", "This reflects", "This is because", "The combination of", "Each of which".
- No rhetorical negation: no "This is not a retrieval gap", "This is not a low score".
- State gaps factually: "Fraser Index not retrieved. Neutral default applied."
- If a field produced a score of zero and was confirmed (not defaulted), say: "Confirmed: [field] = [value]."
- If a field produced a score from a default, say: "Default applied: [field]. Score reflects missing evidence."

EXAMPLE D6 OUTPUT:
D6 Capital Access Signals
Score: 0/100 | Weight: 8% | Evidence Confidence: High
No DFI engagement identified. Vehicle: unlisted. No capital raise in the last 36 months. No Gulf or Western investor linkage. All four sub-fields confirmed during retrieval.

EXAMPLE D5 OUTPUT:
D5 Infrastructure Readiness
Score: 5/100 | Weight: 12% | Evidence Confidence: Low
Power supply, road access, rail access and water supply: not retrieved. Conservative defaults applied across all four sub-fields. Port distance: not retrieved. Lobito Corridor eligibility: not confirmed.
Gap: Infrastructure data not on public record. Score reflects missing evidence, not confirmed absence.

EXAMPLE D3 OUTPUT:
D3 Asset Data Quality
Score: 2/100 | Weight: 20% | Evidence Confidence: Low
Resource estimate standard: none. Reserve classification: none. Production data: not on public record. Exploration stage: recorded.
Gap: No compliant resource estimate identified.
Gap: No production history on public record.
Triggers: FLOOR-D3-001.

---

BLOCK 3 — WHAT THE INVESTOR DOES NOT KNOW
Three to five findings. Each finding: two to three sentences. No more.
These must be cross-dimension insights — things not visible from reading each dimension score in isolation.
Each finding must cite the dimension code and data field it draws from.
No rhetorical buildup. State the finding. State its implication. Stop.

EXAMPLE FINDING:
Three floor rules triggered independently (D2: 0/100, D3: 2/100, FLOOR-BO-001). Each caps the maximum verdict at CAUTION on its own. The aggregate score of 12/100 then produced AVOID — a more conservative outcome than any single floor rule required.

PROHIBITED IN ALL BLOCKS:
- Em dashes
- "This means..."
- "This reflects..."
- "The distinction matters..."
- "This is not a..."
- "It should be noted..."
- "The combination of..."
- "Each of which..."
- "Persist regardless..."
- "Standalone disqualifying..."
- "The more conservative outcome..."
- "Cannot be assumed..."
- "Would be importing assumptions..."
- Any sentence that asserts a conclusion not directly supported by a retrieved data field.

EVIDENCE BOUNDARY — ABSOLUTE:
Only assert facts present in the data fields provided.
If a field is a default, say so. Never state a jurisdictional fact (EITI status, Fraser score, WB percentile) as confirmed unless it appears in the evidence with retrieval status RETRIEVED.
WRONG: "Zambia is not EITI-compliant."
RIGHT: "EITI compliance status: not confirmed during retrieval. Default applied."
WRONG: "No institutional investor has assessed this asset."
RIGHT: "No DFI engagement identified during retrieval."

---

BLOCK 4 — VERDICT AND NEXT ACTION
State the verdict. State the next action. If floor rules triggered, list them and their effect.
Three to five sentences. No rhetorical framing.

EXAMPLE OUTPUT:
Verdict: AVOID. Next action: Stand down.
Floor rules triggered: FLOOR-D2-001 (D2: 0/100, caps verdict at CAUTION), FLOOR-D3-001 (D3: 2/100, caps verdict at CAUTION), FLOOR-BO-001 (beneficial ownership unresolved, caps verdict at CAUTION).
All three triggered before aggregate scoring. The aggregate score of 12/100 produced AVOID, which supersedes the CAUTION ceiling.
Methodology: SEAM-M-v1.0. Rules: SEAM-R-v1.0.

---

Return your response as a JSON object with exactly these keys:
{
  "principal_finding": "...",
  "dimension_findings": {
    "D1": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D2": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D3": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D4": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D5": {"finding": "...", "evidence_confidence": "High|Medium|Low"},
    "D6": {"finding": "...", "evidence_confidence": "High|Medium|Low"}
  },
  "investor_intelligence": ["finding 1", "finding 2", "finding 3"],
  "verdict_section": "..."
}

Return only the JSON object. No preamble. No markdown fences. No explanation."""


# ---------------------------------------------------------------------------
# PROMPT BUILDER
# ---------------------------------------------------------------------------

def build_prompt(result: ScoringResult, inp: AssetInput) -> str:

    dim_summary = []
    for d in result.dimensions:
        gaps = f" DATA GAPS: {'; '.join(d.data_gaps)}" if d.data_gaps else ""
        adjs = ""
        if d.adjustments:
            adjs = " ADJUSTMENTS: " + "; ".join(
                f"{a['reason']} ({'+' if (a['adjustment'] or 0) > 0 else ''}{a['adjustment']}pts)"
                for a in d.adjustments if a.get('adjustment') is not None
            )
        dim_summary.append(
            f"{d.code} {d.name} (weight {d.weight*100:.0f}%): {d.adjusted_score}/100{adjs}{gaps}"
        )

    floor_rules_text = ""
    if result.floor_rules_triggered:
        floor_rules_text = "\nFLOOR RULES TRIGGERED:\n" + "\n".join(
            f"- {r['code']}: {r['description']}" for r in result.floor_rules_triggered
        )

    def ret(val, name, default_note="default applied"):
        if val is None:
            return f"NOT RETRIEVED — {default_note}"
        return f"RETRIEVED: {val}"

    def ret_bool(val, confirmed=True):
        return f"RETRIEVED: {val}" if confirmed else f"DEFAULT: {val}"

    commodity_retrieved = inp.commodity and "retrieval required" not in inp.commodity.lower()
    eiti_status_retrieved = inp.eiti_implementation_status != "non-implementing"
    eiti_country_retrieved = inp.eiti_compliant_country is True

    return f"""ASSET: {result.asset_name}
ASSET ID: {result.asset_id}
JURISDICTION: {inp.jurisdiction} ({inp.jurisdiction_code})
COMMODITY: {inp.commodity} [{'RETRIEVED' if commodity_retrieved else 'NOT RETRIEVED'}]
PROVINCE: {inp.province}
METHODOLOGY: {result.methodology_version}
RULES: {result.rules_version}
GENERATED: {result.generated_at}

INVESTMENT READINESS SCORE: {result.investment_readiness_score}/100
VERDICT: {result.verdict}
NEXT ACTION: {result.next_action}

DIMENSION SCORES:
{chr(10).join(dim_summary)}
{floor_rules_text}

FIELD DATA — retrieval status shown for every field:

D1 Jurisdiction:
  Fraser Investment Attractiveness Index: {ret(inp.fraser_investment_attractiveness, 'fraser_investment_attractiveness', 'neutral default 50 applied')}
  WB Rule of Law percentile: {ret(inp.wb_rule_of_law_percentile, 'wb_rule_of_law_percentile', 'conservative default 40 applied')}
  WB Regulatory Quality percentile: {ret(inp.wb_regulatory_quality_percentile, 'wb_regulatory_quality_percentile', 'conservative default 40 applied')}
  Regulatory change last 12m: RETRIEVED: {inp.regulatory_change_last_12m}
  Mining code revision in progress: RETRIEVED: {inp.mining_code_revision_in_progress}
  Investment arbitration last 5y: RETRIEVED: {inp.investment_arbitration_last_5y}
  Bilateral Investment Treaty: RETRIEVED: {inp.bilateral_investment_treaty}
  EITI compliant country: {'RETRIEVED: True' if eiti_country_retrieved else 'NOT RETRIEVED — default False applied'}

D2 Revenue Transparency:
  EITI implementation status: {'RETRIEVED: ' + inp.eiti_implementation_status if eiti_status_retrieved else 'NOT RETRIEVED — default non-implementing applied'}
  Beneficial ownership disclosure: RETRIEVED: {inp.beneficial_ownership_disclosure}
  EITI payment disclosure quality: {ret(inp.eiti_payment_disclosure_quality, 'eiti_payment_disclosure_quality', 'scored as zero')}
  PEP in ownership chain: RETRIEVED: {inp.pep_in_ownership_chain}
  FATF grey list jurisdiction: RETRIEVED: {inp.fatf_grey_list_jurisdiction}
  Payment data gap over 24m: RETRIEVED: {inp.payment_data_gap_over_24m}

D3 Asset Data:
  Resource estimate standard: RETRIEVED: {inp.resource_estimate_standard}
  Reserve classification: RETRIEVED: {inp.reserve_classification}
  Production data availability: RETRIEVED: {inp.production_data_availability}
  Exploration stage: RETRIEVED: {inp.exploration_stage}
  Unresolved resource conflict: RETRIEVED: {inp.unresolved_resource_conflict}
  Estimate by company employee: RETRIEVED: {inp.estimate_by_company_employee}
  No independent technical report: RETRIEVED: {inp.no_independent_technical_report}

D4 Local Content:
  Licence holder status: RETRIEVED: {inp.licence_holder_status}
  Compliance filing status: RETRIEVED: {inp.locas_filing_status}
  Local procurement evidence: RETRIEVED: {inp.local_procurement_evidence}
  Supplier development programme: RETRIEVED: {inp.supplier_development_programme}
  Reserved services non-local: RETRIEVED: {inp.reserved_services_non_local}

D5 Infrastructure:
  Power supply: RETRIEVED: {inp.power_supply}
  Road access: RETRIEVED: {inp.road_access}
  Rail access: RETRIEVED: {inp.rail_access}
  Water supply: RETRIEVED: {inp.water_supply}
  Port distance km: {ret(inp.port_distance_km, 'port_distance_km', 'conservative default applied')}
  Lobito Corridor eligible: RETRIEVED: {inp.lobito_corridor_eligible}

D6 Capital Access:
  Active DFI engagement: RETRIEVED: {inp.active_dfi_engagement}
  Listed vehicle: RETRIEVED: {inp.listed_vehicle}
  Recent capital raise: RETRIEVED: {inp.recent_capital_raise}
  Gulf/Western investor linked: RETRIEVED: {inp.gulf_western_investor_linked}"""


# ---------------------------------------------------------------------------
# API CALL
# ---------------------------------------------------------------------------

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


def call_intelligence_engine(prompt: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        return _mock_intelligence(prompt)

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 4000,
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
        raise RuntimeError(f"Anthropic API error {e.code}: {msg}") from None

    text_blocks = [
        block["text"].strip()
        for block in data.get("content", [])
        if block.get("type") == "text" and block.get("text", "").strip()
    ]

    if not text_blocks:
        raise ValueError(f"No text content in Claude response. stop_reason={data.get('stop_reason')}")

    raw = _extract_json(text_blocks[-1])
    return json.loads(raw)


def _mock_intelligence(prompt: str) -> dict:
    lines = prompt.split("\n")
    asset = next((l.replace("ASSET:", "").strip() for l in lines if l.startswith("ASSET:")), "Asset")
    score = next((l.replace("INVESTMENT READINESS SCORE:", "").replace("/100","").strip()
                  for l in lines if "INVESTMENT READINESS SCORE:" in l), "N/A")
    verdict = next((l.replace("VERDICT:", "").strip() for l in lines if l.startswith("VERDICT:")), "N/A")

    return {
        "principal_finding": f"Score: {score}/100. Verdict: {verdict}. [Intelligence layer active in Streamlit deployment.]",
        "dimension_findings": {
            "D1": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D2": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D3": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D4": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D5": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
            "D6": {"finding": "[Live in Streamlit]", "evidence_confidence": "Low"},
        },
        "investor_intelligence": [
            "[Live in Streamlit]",
            "[Live in Streamlit]",
            "[Live in Streamlit]",
        ],
        "verdict_section": f"Verdict: {verdict}. [Live in Streamlit]"
    }


def generate_intelligence(result: ScoringResult, inp: AssetInput) -> dict:
    prompt = build_prompt(result, inp)
    return call_intelligence_engine(prompt)

