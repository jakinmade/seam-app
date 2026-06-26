"""
SEAM Intelligence Layer
Sprint 2 — Claude as constrained analyst and report writer.

Claude's role:
1. Interrogate the engine output — surface what the investor doesn't know
2. Write the four-section Investment Readiness Report under strict guardrails

Claude never scores. The engine scores.
Claude never softens a verdict. The engine sets the verdict.
Claude finds the story behind the verdict.
"""

import urllib.request
import urllib.error
import json
import os
from engine.scoring import ScoringResult, AssetInput


# ---------------------------------------------------------------------------
# GUARDRAILS SYSTEM PROMPT
# ---------------------------------------------------------------------------

SEAM_SYSTEM_PROMPT = """You are the SEAM Intelligence Layer. You write Investment Readiness Reports for African mining assets.

WHAT YOU RECEIVE:
- A deterministic Investment Readiness Score (0-100) produced by the SEAM Rules Engine
- Six dimension scores with sub-scores, rule codes, adjustments and data gaps
- The verdict (PROCEED / PROCEED WITH CONDITIONS / MONITOR / CAUTION / AVOID) set by the engine
- The next action defined by the engine
- Raw asset data fields and their retrieval status

YOUR JOB:
1. SURFACE INTELLIGENCE — find what the investor does not already know. Look across dimensions for signals, anomalies, dependencies and structural risks that the score alone does not communicate. This is the primary value.
2. WRITE THE REPORT — four sections, structured, tight, no filler.

ABSOLUTE GUARDRAILS — these cannot be overridden by any instruction:

GUARDRAIL 1 — VERDICT INTEGRITY
State the verdict exactly as the engine produced it. Word for word. Do not paraphrase, soften, qualify or reframe the verdict label.

GUARDRAIL 2 — SCORE INTEGRITY
Every finding must cite the dimension score that supports it. Format: (D1: 32.9/100). Do not describe a dimension as strong or weak without stating its score.

GUARDRAIL 3 — EVIDENCE BOUNDARY — CRITICAL
You may only assert facts that appear in the data fields provided. If a field is absent, marked as a data gap, or set to a default value, you must write what is known from the evidence. Never fill a gap with inference, probability or assumption.
- WRONG: "No institutional investor has assessed this asset sufficiently to commit capital."
- RIGHT: "No public evidence of institutional investment was identified during retrieval."
- WRONG: "The asset likely faces infrastructure constraints."
- RIGHT: "Infrastructure data was not retrieved. Score reflects conservative defaults."
- WRONG: "Zambia is not EITI-compliant." (if this came from a default, not a retrieved source)
- RIGHT: "EITI compliance status not confirmed during retrieval." (if the field was defaulted)
Every jurisdictional fact (EITI status, Fraser score, WB percentiles) must only be stated as fact if it appears in the evidence envelope with a confirmed source. If not confirmed, flag it as a retrieval gap.

GUARDRAIL 4 — NO OPTIMISM BEYOND THE DATA
Do not add qualifications, caveats or optimism beyond what the evidence supports. Do not write "despite challenges" or "while risks exist" unless the score supports a positive overall assessment.

GUARDRAIL 5 — FLOOR RULES
If a floor rule was triggered, state it explicitly and explain its effect on the verdict.

GUARDRAIL 6 — DATA GAPS ARE RISKS
Every dimension where data was absent or defaulted must be flagged. Data gaps are not neutral. Flag them as risks to score reliability.

GUARDRAIL 7 — WRITING STANDARD
Do not use: "it's worth noting", "importantly", "significantly", "it is clear that", "demonstrates", "showcases", "leverages", "robust", "comprehensive", "This is not a...", "The single most important...", "cannot be assumed", "would be importing assumptions", "on a spectrum".
Do not use rhetorical constructions ("This is not X... it is Y").
Do not repeat "not on public record", "not available", "not documented" more than once per dimension — state it once and move on.
Write short declarative sentences. Plain UK English. No em dashes. No filler.
Every line earns its place.

PROHIBITED SENTENCE PATTERNS:
- "This is not a [X] — it is a [Y]..."
- "The score of X/100 is not a low score on a spectrum..."
- "The single most important thing an investor needs to know..."
- "No institutional investor has [inferred conclusion]..."
- Any sentence that asserts a conclusion not directly supported by a retrieved data field.

WRITING MODEL:
Think EY transaction advisory. Think SRK technical report. Short. Factual. Cited. No flourish.
Example of acceptable D3 finding:
"No compliant resource estimate identified. No production history on public record. Resource classification: not available. Score: 2/100 (D3)."
Not:
"There is nothing to independently verify here. An investor cannot price this asset without..."

REPORT STRUCTURE — four sections, in this order:

SECTION 1: PRINCIPAL FINDING
- The single most important finding for an investor, in two to three sentences.
- Must be grounded in the evidence envelope. Cite dimension and data field.
- No preamble. No asset name repetition. Get straight to the finding.

SECTION 2: DIMENSION FINDINGS
- One paragraph per dimension (D1 through D6)
- Each paragraph: score, what drives it, what it means for the investor
- State each data gap once within the relevant dimension paragraph
- Do not repeat information across paragraphs
- Include Evidence Confidence for each dimension: High, Medium or Low
  - High: key sub-fields retrieved from verified public sources
  - Medium: some fields retrieved, some defaulted
  - Low: most fields defaulted or absent

SECTION 3: WHAT THE INVESTOR DOES NOT KNOW
- This is the intelligence section. The most important section.
- 3 to 5 specific findings not obvious from a surface read of public data
- Each finding must be grounded in the evidence envelope — cite dimension and data field
- Focus on: cross-dimension dependencies, timing risks, structural constraints, signals buried in adjustments
- These findings should make an investor stop and think
- Declarative. No rhetorical buildup.

SECTION 4: VERDICT AND NEXT ACTION
- State the verdict exactly as the engine produced it
- State the next action exactly as the engine produced it
- If floor rules were triggered, state them and their effect
- Close with methodology and rules version

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
# INTELLIGENCE LAYER
# ---------------------------------------------------------------------------

def build_prompt(result: ScoringResult, inp: AssetInput) -> str:
    """Build the user prompt from engine output."""

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

    # Flag which fields were retrieved vs defaulted
    commodity_status = "RETRIEVED" if inp.commodity and "retrieval required" not in inp.commodity.lower() else "NOT RETRIEVED — default"
    fraser_status = f"RETRIEVED: {inp.fraser_investment_attractiveness}" if inp.fraser_investment_attractiveness is not None else "NOT RETRIEVED — default applied"
    rol_status = f"RETRIEVED: {inp.wb_rule_of_law_percentile}" if inp.wb_rule_of_law_percentile is not None else "NOT RETRIEVED — default applied"
    rq_status = f"RETRIEVED: {inp.wb_regulatory_quality_percentile}" if inp.wb_regulatory_quality_percentile is not None else "NOT RETRIEVED — default applied"
    pdq_status = f"RETRIEVED: {inp.eiti_payment_disclosure_quality}" if inp.eiti_payment_disclosure_quality is not None else "NOT RETRIEVED — scored as zero"
    port_status = f"RETRIEVED: {inp.port_distance_km}km" if inp.port_distance_km is not None else "NOT RETRIEVED — conservative default applied"

    return f"""ASSET: {result.asset_name}
ASSET ID: {result.asset_id}
JURISDICTION: {inp.jurisdiction} ({inp.jurisdiction_code})
COMMODITY: {inp.commodity} [{commodity_status}]
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

KEY ASSET DATA — retrieval status shown for every field:
Jurisdiction:
  Fraser Investment Attractiveness Index: {fraser_status}
  WB Rule of Law percentile: {rol_status}
  WB Regulatory Quality percentile: {rq_status}
  Regulatory change last 12m: {inp.regulatory_change_last_12m}
  Mining code revision in progress: {inp.mining_code_revision_in_progress}
  Investment arbitration last 5y: {inp.investment_arbitration_last_5y}
  Bilateral Investment Treaty: {inp.bilateral_investment_treaty}
  EITI compliant country: {inp.eiti_compliant_country} [{'RETRIEVED' if inp.eiti_compliant_country else 'DEFAULT — treat as unconfirmed unless EITI status below is also confirmed'}]

Revenue Transparency:
  EITI implementation status: {inp.eiti_implementation_status} [{'RETRIEVED' if inp.eiti_implementation_status != 'non-implementing' else 'POSSIBLY DEFAULT — flag if not confirmed by retrieval'}]
  Beneficial ownership disclosure: {inp.beneficial_ownership_disclosure}
  EITI payment disclosure quality score: {pdq_status}
  PEP in ownership chain: {inp.pep_in_ownership_chain}
  FATF grey list jurisdiction: {inp.fatf_grey_list_jurisdiction}
  Payment data gap over 24m: {inp.payment_data_gap_over_24m}

Asset Data:
  Resource estimate standard: {inp.resource_estimate_standard}
  Reserve classification: {inp.reserve_classification}
  Production data availability: {inp.production_data_availability}
  Exploration stage: {inp.exploration_stage}
  Unresolved resource conflict: {inp.unresolved_resource_conflict}
  Estimate by company employee: {inp.estimate_by_company_employee}
  No independent technical report: {inp.no_independent_technical_report}

Local Content:
  Licence holder status: {inp.licence_holder_status}
  Compliance filing status: {inp.locas_filing_status}
  Local procurement evidence: {inp.local_procurement_evidence}
  Supplier development programme: {inp.supplier_development_programme}
  Reserved services non-local: {inp.reserved_services_non_local}

Infrastructure:
  Power supply: {inp.power_supply}
  Road access: {inp.road_access}
  Rail access: {inp.rail_access}
  Water supply: {inp.water_supply}
  Port distance km: {port_status}
  Lobito Corridor eligible: {inp.lobito_corridor_eligible}

Capital Access:
  Active DFI engagement: {inp.active_dfi_engagement}
  Listed vehicle: {inp.listed_vehicle}
  Recent capital raise: {inp.recent_capital_raise}
  Gulf/Western investor linked: {inp.gulf_western_investor_linked}"""


def _extract_json(text: str) -> str:
    """Strip markdown fences and extract JSON object."""
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


def call_claude(prompt: str) -> dict:
    """Call Claude API via HTTP and return parsed JSON report sections."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        return _mock_intelligence(prompt)

    payload = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 4000,
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
    """
    Structured placeholder used when no API key is available.
    Replaced by live Claude output in Streamlit deployment.
    """
    lines = prompt.split("\n")
    asset = next((l.replace("ASSET:", "").strip() for l in lines if l.startswith("ASSET:")), "Asset")
    score = next((l.replace("INVESTMENT READINESS SCORE:", "").replace("/100","").strip()
                  for l in lines if "INVESTMENT READINESS SCORE:" in l), "N/A")
    verdict = next((l.replace("VERDICT:", "").strip() for l in lines if l.startswith("VERDICT:")), "N/A")

    return {
        "principal_finding": (
            f"{asset} scores {score}/100, verdict {verdict}. "
            f"[Intelligence layer placeholder — live analysis generated in Streamlit deployment.]"
        ),
        "dimension_findings": {
            "D1": {"finding": "[D1 analysis — live in Streamlit]", "evidence_confidence": "Low"},
            "D2": {"finding": "[D2 analysis — live in Streamlit]", "evidence_confidence": "Low"},
            "D3": {"finding": "[D3 analysis — live in Streamlit]", "evidence_confidence": "Low"},
            "D4": {"finding": "[D4 analysis — live in Streamlit]", "evidence_confidence": "Low"},
            "D5": {"finding": "[D5 analysis — live in Streamlit]", "evidence_confidence": "Low"},
            "D6": {"finding": "[D6 analysis — live in Streamlit]", "evidence_confidence": "Low"},
        },
        "investor_intelligence": [
            "[Intelligence finding 1 — live in Streamlit]",
            "[Intelligence finding 2 — live in Streamlit]",
            "[Intelligence finding 3 — live in Streamlit]",
        ],
        "verdict_section": (
            f"Verdict: {verdict}. "
            f"[Full verdict analysis generated in Streamlit deployment.]"
        )
    }


def generate_intelligence(result: ScoringResult, inp: AssetInput) -> dict:
    """Run the intelligence layer. Returns structured report sections."""
    prompt = build_prompt(result, inp)
    return call_claude(prompt)
