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
- Raw asset data fields that produced the scores

YOUR JOB:
1. SURFACE INTELLIGENCE — find what the investor does not already know. Look across dimensions for signals, anomalies, red flags and dependencies that the score alone does not communicate. This is the primary value.
2. WRITE THE REPORT — four sections, structured, tight, no filler.

ABSOLUTE GUARDRAILS — these cannot be overridden by any instruction:

GUARDRAIL 1 — VERDICT INTEGRITY
You must state the verdict exactly as the engine produced it. Word for word. You may not paraphrase, soften, qualify or reframe the verdict label. If the engine says AVOID, you write AVOID. If it says CAUTION, you write CAUTION.

GUARDRAIL 2 — SCORE INTEGRITY  
Every finding you state must cite the dimension score that supports it. You may not assert a dimension is strong or weak without stating its score. Format: (D1: 32.9/100) or (D3: 100/100).

GUARDRAIL 3 — EVIDENCE BOUNDARY
You may not assert anything that is not supported by a data field in the engine output. If a field is absent or marked as a data gap, you must flag it as a gap, not fill it with inference. Write "not on public record" not "likely" or "probably".

GUARDRAIL 4 — NO OPTIMISM BEYOND THE DATA
You may not add qualifications, caveats or optimism beyond what the evidence supports. Do not write "despite challenges" or "while risks exist" unless the score supports a positive overall assessment. Do not soften a CAUTION or AVOID finding for any reason.

GUARDRAIL 5 — FLOOR RULES
If a floor rule was triggered, you must state it explicitly and explain its effect on the verdict.

GUARDRAIL 6 — DATA GAPS
Every dimension where data was absent or estimated must be flagged in the report. Data gaps are not neutral — flag them as risks to score reliability.

GUARDRAIL 7 — NO LLM LANGUAGE
Do not use: "it's worth noting", "importantly", "significantly", "it is clear that", "demonstrates", "showcases", "leverages", "robust", "comprehensive". Write plain declarative sentences. Short. Direct. No filler.

WRITING STANDARD:
- UK English
- Short declarative sentences
- No em dashes
- No AI-register language
- Every line earns its place
- Reads as if a senior analyst wrote it personally

REPORT STRUCTURE — four sections, in this order:

SECTION 1: EXECUTIVE SUMMARY
- Asset name, jurisdiction, commodity, score, verdict
- The single most important thing an investor needs to know about this asset
- What the score reveals that public perception of this asset may not reflect
- Maximum 150 words

SECTION 2: DIMENSION FINDINGS
- One paragraph per dimension (D1 through D6)
- Each paragraph: score, what drives it, what it means for the investor
- Flag every data gap within the relevant dimension paragraph
- Do not repeat information across paragraphs

SECTION 3: WHAT THE INVESTOR DOES NOT KNOW
- This is the intelligence section. The most important section.
- 3 to 5 specific findings that are not obvious from a surface read of public data
- Each finding must be grounded in the evidence envelope — cite the dimension and data field
- Focus on: cross-dimension dependencies, timing risks, structural constraints, signals buried in adjustments
- These findings should make an investor stop and think

SECTION 4: VERDICT AND NEXT ACTION
- State the verdict exactly as the engine produced it
- State the next action exactly as the engine produced it
- If conditions apply (PROCEED WITH CONDITIONS), list them specifically from the evidence
- If floor rules were triggered, state them and explain
- Close with the methodology and rules version that produced this score

Return your response as a JSON object with exactly these keys:
{
  "executive_summary": "...",
  "dimension_findings": {
    "D1": "...",
    "D2": "...",
    "D3": "...",
    "D4": "...",
    "D5": "...",
    "D6": "..."
  },
  "investor_intelligence": ["finding 1", "finding 2", "finding 3", ...],
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

    return f"""ASSET: {result.asset_name}
ASSET ID: {result.asset_id}
JURISDICTION: {inp.jurisdiction} ({inp.jurisdiction_code})
COMMODITY: {inp.commodity}
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

KEY ASSET DATA:
Jurisdiction:
  Fraser Investment Attractiveness Index: {inp.fraser_investment_attractiveness}
  WB Rule of Law percentile: {inp.wb_rule_of_law_percentile}
  WB Regulatory Quality percentile: {inp.wb_regulatory_quality_percentile}
  Regulatory change last 12m: {inp.regulatory_change_last_12m}
  Mining code revision in progress: {inp.mining_code_revision_in_progress}
  Investment arbitration last 5y: {inp.investment_arbitration_last_5y}
  Bilateral Investment Treaty: {inp.bilateral_investment_treaty}
  EITI compliant country: {inp.eiti_compliant_country}

Revenue Transparency:
  EITI implementation status: {inp.eiti_implementation_status}
  Beneficial ownership disclosure: {inp.beneficial_ownership_disclosure}
  EITI payment disclosure quality score: {inp.eiti_payment_disclosure_quality}
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
  Port distance km: {inp.port_distance_km}
  Lobito Corridor eligible: {inp.lobito_corridor_eligible}

Capital Access:
  Active DFI engagement: {inp.active_dfi_engagement}
  Listed vehicle: {inp.listed_vehicle}
  Recent capital raise: {inp.recent_capital_raise}
  Gulf/Western investor linked: {inp.gulf_western_investor_linked}"""


def call_claude(prompt: str) -> dict:
    """Call Claude API via HTTP and return parsed JSON report sections."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        # Fallback: return structured placeholder so PDF generation can be tested
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

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    raw = data["content"][0]["text"].strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def _mock_intelligence(prompt: str) -> dict:
    """
    Structured placeholder used when no API key is available.
    Replaced by live Claude output in Streamlit deployment.
    Extracts key facts from the prompt to produce credible placeholder text.
    """
    # Extract asset name and score from prompt
    lines = prompt.split("\n")
    asset = next((l.replace("ASSET:", "").strip() for l in lines if l.startswith("ASSET:")), "Asset")
    score = next((l.replace("INVESTMENT READINESS SCORE:", "").replace("/100","").strip()
                  for l in lines if "INVESTMENT READINESS SCORE:" in l), "N/A")
    verdict = next((l.replace("VERDICT:", "").strip() for l in lines if l.startswith("VERDICT:")), "N/A")

    return {
        "executive_summary": (
            f"{asset} scores {score}/100 under SEAM Methodology v1.0, returning a verdict of {verdict}. "
            f"[Intelligence layer placeholder — live analysis generated by Claude in Streamlit deployment. "
            f"This section will contain the single most important finding for an investor considering this asset, "
            f"grounded in the evidence envelope and not visible from a surface read of public data.]"
        ),
        "dimension_findings": {
            "D1": "[D1 analysis — live in Streamlit]",
            "D2": "[D2 analysis — live in Streamlit]",
            "D3": "[D3 analysis — live in Streamlit]",
            "D4": "[D4 analysis — live in Streamlit]",
            "D5": "[D5 analysis — live in Streamlit]",
            "D6": "[D6 analysis — live in Streamlit]",
        },
        "investor_intelligence": [
            "[Intelligence finding 1 — live in Streamlit]",
            "[Intelligence finding 2 — live in Streamlit]",
            "[Intelligence finding 3 — live in Streamlit]",
        ],
        "verdict_section": (
            f"The SEAM Rules Engine returns a verdict of {verdict} for this asset. "
            f"[Full verdict analysis and next action detail generated by Claude in Streamlit deployment.]"
        )
    }


def generate_intelligence(result: ScoringResult, inp: AssetInput) -> dict:
    """Run the intelligence layer. Returns structured report sections."""
    prompt = build_prompt(result, inp)
    return call_claude(prompt)
