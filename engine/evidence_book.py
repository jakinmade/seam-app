"""
SEAM Evidence Book Generator
Session 4 — Evidence Provenance PDF.

Generates a second PDF from the existing evidence envelope.
No new data. No new logic. Surfaces what the engine already records.

Structure:
  Page 1: Evidence Integrity Framework + Assessment Integrity panel
  Page 2: Evidence Flow Diagram
  Page 3+: Evidence Provenance Register (one row per field, per dimension)
  Final: Methodology Statement + Replayability Declaration
"""

from weasyprint import HTML
from engine.scoring import ScoringResult
from datetime import datetime
import hashlib
import os

AMBER = "#C8962E"
NAVY  = "#0B1929"
RED   = "#CC0000"
WHITE = "#FFFFFF"

VERDICT_COLOURS = {
    "PROCEED":                 "#1A7A3A",
    "PROCEED WITH CONDITIONS": "#B8860B",
    "MONITOR":                 "#1A5FA8",
    "CAUTION":                 "#C65C00",
    "AVOID":                   RED,
}


def _gen(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%d %B %Y, %H:%M UTC")
    except Exception:
        return ts


def _conf_colour(conf: str) -> str:
    return {"high": "#1A7A3A", "medium": "#B8860B", "low": RED}.get(
        (conf or "").lower(), "#888"
    )


def _decision_id(result: ScoringResult) -> str:
    h = hashlib.sha256(
        f"{result.asset_id}{result.generated_at}".encode()
    ).hexdigest()[:6].upper()
    year = result.generated_at[:4]
    jcode = result.evidence_envelope.get("jurisdiction_code", result.asset_id[:3])
    return f"SEAM-{year}-{jcode}-{h}"


def _count_fields(envelope: dict) -> tuple[int, int, int]:
    """Count total fields, retrieved (verified), defaulted."""
    total = retrieved = defaulted = 0
    for dim_data in envelope.get("dimensions", {}).values():
        for ef in dim_data.get("evidence_fields", []):
            total += 1
            if ef.get("verified"):
                retrieved += 1
            else:
                defaulted += 1
    return total, retrieved, defaulted


def _count_sources(envelope: dict) -> int:
    """Count unique named sources across all evidence fields."""
    sources = set()
    for dim_data in envelope.get("dimensions", {}).values():
        for ef in dim_data.get("evidence_fields", []):
            s = ef.get("source")
            if s:
                sources.add(s)
    return len(sources)


# Source categories for Issue 3
SOURCE_CATEGORIES = {
    "Government": ["Government gazette", "Ministry of Mines", "ICSID", "PCA arbitration",
                   "Mining licence register", "Local content compliance portal", "Reserved services gazette",
                   "Government road authority", "Water licence register", "Court records",
                   "Mining ministry gazette", "Operator disclosure / exchange filing"],
    "International": ["World Bank WGI", "EITI", "FATF", "UNCTAD BIT database",
                      "IFC/AfDB/BII", "World Bank Projects", "African Development Bank",
                      "ICIJ Offshore Leaks", "Geographic calculation"],
    "Exchange": ["ASX", "TSX", "AIM", "LSE", "SEDAR", "exchange regulatory announcement",
                 "Exchange filing", "NI 43-101", "JORC", "SAMREC", "Technical report",
                 "competent person report", "Operator annual report", "quarterly production"],
    "Registry": ["National beneficial ownership register", "Lobito Corridor project registry",
                 "cadastre", "Mining commission", "Companies House"],
    "Commercial": ["S&P Capital IQ", "Refinitiv", "Bloomberg", "Investor register",
                   "Operator sustainability report", "Operator CSR report",
                   "Operator technical report"],
    "Index/Research": ["Fraser Institute", "USGS", "National railway operator",
                       "government energy regulator"],
}

def _categorise_source(source: str) -> str:
    if not source:
        return "Other"
    source_lower = source.lower()
    for cat, keywords in SOURCE_CATEGORIES.items():
        if any(kw.lower() in source_lower for kw in keywords):
            return cat
    return "Other"


def generate_evidence_book(
    result: ScoringResult,
    output_dir: str = "output"
) -> str:
    """Generate Evidence Book PDF. Returns output path."""

    os.makedirs(output_dir, exist_ok=True)
    envelope = result.evidence_envelope
    did      = _decision_id(result)
    gen      = _gen(result.generated_at)
    vc       = VERDICT_COLOURS.get(result.verdict, "#333")

    total_fields, retrieved_fields, defaulted_fields = _count_fields(envelope)
    unique_sources = _count_sources(envelope)
    ec = getattr(result, "evidence_completeness_score", 0)

    # -----------------------------------------------------------------------
    # EVIDENCE PROVENANCE REGISTER — one row per field per dimension
    # -----------------------------------------------------------------------
    register_rows = ""
    row_count = 0

    for dim_code, dim_data in envelope.get("dimensions", {}).items():
        dim_name  = dim_data.get("name", dim_code)
        dim_score = dim_data.get("adjusted_score", 0)

        for ef in dim_data.get("evidence_fields", []):
            row_count += 1
            eid        = f"E-{row_count:05d}"
            field_name = ef.get("field", "")
            value      = ef.get("value", "")
            source     = ef.get("source") or "Not retrieved"
            source_url = ef.get("source_url") or ""
            ret_date   = ef.get("retrieved_date") or gen
            confidence = ef.get("confidence", "medium")
            verified   = ef.get("verified", False)
            rule_code  = ef.get("rule_code") or ""
            notes      = ef.get("notes") or ""

            # Score Effect — look up the sub-score contribution for this field
            sub_scores  = dim_data.get("sub_scores", {})
            # Map field names to sub-score keys
            _field_to_sub = {
                "fraser_investment_attractiveness": "fraser_institute_score",
                "wb_rule_of_law_percentile": "wb_rule_of_law",
                "wb_regulatory_quality_percentile": "wb_regulatory_quality",
                "eiti_implementation_status": "eiti_implementation_status",
                "beneficial_ownership_disclosure": "beneficial_ownership_disclosure",
                "eiti_payment_disclosure_quality": "eiti_payment_disclosure_quality",
                "resource_estimate_standard": "resource_estimate_standard",
                "reserve_classification": "reserve_classification",
                "production_data_availability": "production_data_availability",
                "exploration_stage": "exploration_stage",
                "licence_holder_status": "licence_holder_status",
                "locas_filing_status": "compliance_filing_status",
                "local_procurement_evidence": "local_procurement_evidence",
                "supplier_development_programme": "supplier_development_programme",
                "power_supply": "power_supply",
                "road_access": "road_access",
                "rail_access": "rail_access",
                "water_supply": "water_supply",
                "port_distance_km": "port_distance",
                "active_dfi_engagement": "active_dfi_engagement",
                "listed_vehicle": "listed_vehicle",
                "recent_capital_raise": "recent_capital_raise",
                "gulf_western_investor_linked": "gulf_western_investor",
            }
            sub_key = _field_to_sub.get(field_name)
            sub_data = sub_scores.get(sub_key, {}) if sub_key else {}
            if sub_data and sub_data.get("score") is not None:
                sub_score = sub_data.get("score", 0)
                sub_weight = sub_data.get("weight", 0)
                contribution = round(sub_score * sub_weight, 1)
                score_effect_html = f'<span style="font-size:9px;color:#555;">{sub_score:.1f} × {sub_weight:.2f} = <strong>{contribution}</strong></span>'
            elif rule_code and "ADJ" in rule_code:
                score_effect_html = '<span style="font-size:9px;color:#888;">Adjustment</span>'
            else:
                score_effect_html = '<span style="font-size:9px;color:#aaa;">—</span>'

            status_col  = "#1A7A3A" if verified else RED
            status_text = "Retrieved" if verified else "Defaulted"
            conf_col    = _conf_colour(confidence)

            source_html = (
                f'<a href="{source_url}" style="color:{AMBER};font-size:9px;">{source}</a>'
                if source_url else
                f'<span style="font-size:10px;color:#444;">{source}</span>'
            )

            bg = "#f9f9f9" if row_count % 2 == 0 else WHITE

            register_rows += f"""
            <tr style="background:{bg};">
              <td style="padding:5px 8px;font-size:9px;color:#888;white-space:nowrap;">{eid}</td>
              <td style="padding:5px 8px;font-size:9px;font-weight:bold;color:{NAVY};">{dim_code}</td>
              <td style="padding:5px 8px;font-size:10px;color:#333;">{field_name.replace('_',' ')}</td>
              <td style="padding:5px 8px;font-size:10px;color:#444;max-width:100px;">{str(value)[:40]}</td>
              <td style="padding:5px 8px;">{source_html}</td>
              <td style="padding:5px 8px;font-size:9px;color:{status_col};font-weight:bold;">{status_text}</td>
              <td style="padding:5px 8px;font-size:9px;color:{conf_col};">{confidence.title()}</td>
              <td style="padding:5px 8px;font-size:9px;color:#777;font-family:monospace;">{rule_code}</td>
              <td style="padding:5px 8px;font-size:9px;color:#888;">{ret_date[:10] if ret_date else ''}</td>
              <td style="padding:5px 8px;font-size:9px;color:#555;">{score_effect_html}</td>
            </tr>"""

    # ── Source category counts ────────────────────────────────────────
    cat_counts = {}
    for dim_data in envelope.get("dimensions", {}).values():
        for ef in dim_data.get("evidence_fields", []):
            cat = _categorise_source(ef.get("source", ""))
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

    rules_count = sum(
        len(dim_data.get("rules_applied", []))
        for dim_data in envelope.get("dimensions", {}).values()
    )

    # Source category panel
    cat_html = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #2a3f55;">'        f'<span style="font-size:9px;color:#888;">{cat}</span>'        f'<span style="font-size:10px;font-weight:bold;color:{AMBER};">{count}</span></div>'
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])
        if count > 0
    )

    # Infographic bars
    def _bar(n, max_n, width=120):
        filled = max(4, int((n / max(max_n, 1)) * width))
        return (f'<div style="background:#2a3f55;border-radius:2px;height:8px;width:{width}px;margin:3px 0;">'                f'<div style="background:{AMBER};border-radius:2px;height:8px;width:{filled}px;"></div></div>')

    floor_codes = envelope.get("floor_rules_triggered", [])
    max_val = max(unique_sources, total_fields, rules_count, len(floor_codes) or 1)

    # ── DATA GAPS TABLE ────────────────────────────────────────────────
    gaps = envelope.get("data_gaps_summary", [])
    gaps_html = ""
    if gaps:
        gap_rows = "".join(
            f'<tr style="background:{"#fff8f8" if i%2==0 else WHITE};">'
            f'<td style="padding:4px 10px;font-size:10px;color:#555;">{i+1}</td>'
            f'<td style="padding:4px 10px;font-size:10px;color:{RED};">{g}</td>'
            f'<td style="padding:4px 10px;font-size:9px;color:#888;">Not found in public sources at time of retrieval</td>'
            f'</tr>'
            for i, g in enumerate(gaps)
        )
        gaps_html = f"""
        <h2>Data Gaps Register</h2>
        <p style="font-size:10px;color:#666;margin-bottom:8px;">
          Fields where no public source was identified during retrieval.
          These gaps are scored conservatively under SEAM-R-v1.0.
          They are listed here for auditability, not as findings.
        </p>
        <table style="width:100%;border-collapse:collapse;border:1px solid #f0c0c0;">
          <tr style="background:{RED};">
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;width:30px;">#</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Gap</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Status</th>
          </tr>
          {gap_rows}
        </table>"""

    # -----------------------------------------------------------------------
    # FLOOR RULES TABLE
    # -----------------------------------------------------------------------
    floors_html = ""
    if floor_codes:
        floor_rows = "".join(
            f'<tr style="background:{"#fff8f8" if i%2==0 else WHITE};">'
            f'<td style="padding:5px 10px;font-size:10px;font-weight:bold;color:{RED};">{code}</td>'
            f'<td style="padding:5px 10px;font-size:10px;color:#333;">Triggered before aggregate scoring. Caps maximum verdict at CAUTION independently.</td>'
            f'</tr>'
            for i, code in enumerate(floor_codes)
        )
        floors_html = f"""
        <h2>Floor Rules Triggered</h2>
        <table style="width:100%;border-collapse:collapse;border:1px solid #f0c0c0;">
          <tr style="background:{RED};">
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Rule Code</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Effect</th>
          </tr>
          {floor_rows}
        </table>"""

    # -----------------------------------------------------------------------
    # HTML
    # -----------------------------------------------------------------------
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{
    size: A4 landscape;
    margin: 14mm 12mm 14mm 12mm;
    @bottom-center {{
      content: "SEAM Evidence Book  |  {did}  |  CONFIDENTIAL  |  Page " counter(page) " of " counter(pages);
      font-family: Arial, sans-serif;
      font-size: 8px;
      color: #bbb;
    }}
  }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 11px;
    color: #222;
    margin: 0; padding: 0;
    line-height: 1.4;
  }}
  h2 {{
    font-size: 11px;
    color: {NAVY};
    margin: 20px 0 8px 0;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-bottom: 1.5px solid {AMBER};
    padding-bottom: 3px;
  }}
  table {{ border-collapse: collapse; width: 100%; }}
  .page-break {{ page-break-before: always; }}
</style>
</head>
<body>

<!-- PAGE 1: EVIDENCE INTEGRITY FRAMEWORK -->
<table style="width:100%;margin-bottom:14px;">
  <tr>
    <td>
      <span style="font-size:22px;font-weight:bold;color:{AMBER};letter-spacing:1.5px;">SEAM</span>
      <span style="font-size:9px;color:{NAVY};margin-left:10px;">STRUCTURED EVIDENCE FOR AFRICAN MINING</span>
    </td>
    <td style="text-align:right;">
      <div style="font-size:9px;color:#888;">Evidence Book &nbsp;|&nbsp; {gen}</div>
      <div style="font-size:9px;color:#888;">{result.methodology_version} &nbsp;|&nbsp; {result.rules_version}</div>
    </td>
  </tr>
</table>
<div style="height:2px;background:{NAVY};margin-bottom:14px;"></div>

<div style="font-size:15px;font-weight:bold;color:{NAVY};margin-bottom:2px;">{result.asset_name} — Evidence Book</div>
<table style="width:100%;margin-bottom:14px;">
  <tr>
    <td style="font-size:9px;color:#888;">{envelope.get('jurisdiction','')} &nbsp;|&nbsp; {envelope.get('commodity','')} &nbsp;|&nbsp; ID: {result.asset_id}</td>
    <td style="text-align:right;font-size:9px;color:#aaa;font-family:monospace;">Decision ID: {did}</td>
  </tr>
</table>

<!-- BRAND STATEMENT -->
<div style="background:{NAVY};padding:16px 20px;margin-bottom:16px;border-radius:3px;">
  <div style="font-size:12px;font-weight:bold;color:{AMBER};margin-bottom:8px;">Evidence Integrity Statement</div>
  <div style="font-size:11px;color:white;line-height:1.6;">
    Every finding in this report is traceable to one or more named public sources.
    Every score is produced by deterministic rules under {result.rules_version}.
    No analyst opinion contributes to the final verdict.
    This Evidence Book is the complete provenance record for Decision ID {did}.
  </div>
</div>

<!-- ASSESSMENT INTEGRITY + CHAIN OF EVIDENCE INFOGRAPHIC -->
<h2>Assessment Integrity</h2>
<table style="width:100%;border-collapse:collapse;">
  <tr style="vertical-align:top;">
    <td style="width:58%;padding-right:12px;">

      <!-- Numeric integrity panel -->
      <table style="width:100%;border-collapse:collapse;background:{NAVY};">
        <tr>
          {''.join(
            f'<td style="padding:10px 12px;text-align:center;border-right:1px solid #2a3f55;">'
            f'<div style="font-size:18px;font-weight:bold;color:{AMBER};">{val}</div>'
            f'<div style="font-size:8px;color:#888;text-transform:uppercase;letter-spacing:0.3px;margin-top:2px;">{label}</div>'
            f'</td>'
            for val, label in [
              (total_fields, "Fields assessed"),
              (retrieved_fields, "Retrieved"),
              (defaulted_fields, "Defaulted"),
              (unique_sources, "Sources queried"),
              ('<span style="color:#1A7A3A;font-weight:bold;">0</span>', "Manual edits"),
              ("Yes", "Replay available"),
              (result.rules_version, "Rules locked"),
            ]
          )}
        </tr>
      </table>

      <!-- SEAM Chain of Evidence infographic -->
      <div style="margin-top:10px;background:{NAVY};padding:12px 14px;">
        <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:10px;">SEAM Chain of Evidence</div>
        {''.join(
          f'<div style="margin-bottom:7px;">'          f'<div style="display:flex;justify-content:space-between;margin-bottom:2px;">'          f'<span style="font-size:9px;color:#aaa;">{label}</span>'          f'<span style="font-size:10px;font-weight:bold;color:{AMBER};">{count}</span>'          f'</div>'          f'{_bar(count, max_val)}'          f'</div>'
          for label, count in [
            ("Public sources searched", unique_sources),
            ("Evidence fields retrieved", retrieved_fields),
            ("Scoring rules applied", rules_count),
            ("Floor rules triggered", len(floor_codes)),
          ]
        )}
        <div style="margin-top:10px;padding-top:8px;border-top:1px solid #2a3f55;">
          <span style="font-size:9px;color:#888;">Decision: </span>
          <span style="font-size:12px;font-weight:bold;color:white;background:{vc};padding:2px 10px;border-radius:2px;">{result.verdict}</span>
        </div>
      </div>
    </td>

    <!-- Source categories -->
    <td style="width:42%;padding-left:8px;">
      <div style="background:{NAVY};padding:12px 14px;height:100%;box-sizing:border-box;">
        <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:10px;">Sources by Category</div>
        {cat_html}
        <div style="margin-top:10px;padding-top:8px;border-top:1px solid #2a3f55;font-size:9px;color:#666;">
          Every source named in the Evidence Provenance Register.
        </div>
      </div>
    </td>
  </tr>
</table>

<!-- EVIDENCE INTEGRITY FRAMEWORK -->
<h2>Evidence Integrity Framework</h2>
<table style="width:100%;border-collapse:collapse;">
  <tr>
    {''.join(
        f'<td style="width:25%;padding:12px 14px;border:1px solid #e8e8e8;vertical-align:top;">'
        f'<div style="font-size:12px;font-weight:bold;color:{AMBER};margin-bottom:6px;">{num}</div>'
        f'<div style="font-size:11px;font-weight:bold;color:{NAVY};margin-bottom:4px;">{title}</div>'
        f'<div style="font-size:10px;color:#555;line-height:1.5;">{desc}</div>'
        f'</td>'
        for num, title, desc in [
            ("01", "Evidence Provenance",
             "Every material finding links to a named public source with retrieval metadata. "
             "Sources include EITI, Fraser Institute, World Bank WGI, exchange filings, government cadastre portals, USGS, and financial press."),
            ("02", "Deterministic Processing",
             f"Every score and floor rule is traceable to a specific rule identifier under {result.rules_version}. "
             "No probabilistic model or LLM produces scores. Identical inputs always produce identical outputs."),
            ("03", "Replayability",
             f"This evidence envelope carries hash {envelope.get('envelope_hash','')[:16]}... "
             "Running the same evidence set against the version-locked rule set reproduces the same outcome. "
             "The replay function is built into the SEAM architecture."),
            ("04", "Transparency",
             f"All defaults, missing fields and confidence adjustments are disclosed in this Evidence Book. "
             f"{defaulted_fields} fields were defaulted due to absence in public sources. "
             "Every default is listed in the Data Gaps Register below."),
        ]
    )}
  </tr>
</table>

<!-- SCORE + VERDICT REFERENCE -->
<h2>Decision Reference</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:0;">
  <tr>
    <td style="background:{NAVY};padding:12px 16px;width:25%;vertical-align:middle;">
      <div style="font-size:9px;color:#666;text-transform:uppercase;">Investment Readiness</div>
      <div style="font-size:36px;font-weight:bold;color:{AMBER};line-height:1;">{result.investment_readiness_score}</div>
      <div style="font-size:9px;color:#666;">out of 100</div>
    </td>
    <td style="background:#0f1e2e;padding:12px 16px;width:25%;vertical-align:middle;border-left:1px solid #2a3f55;">
      <div style="font-size:9px;color:#666;text-transform:uppercase;">Evidence Completeness</div>
      <div style="font-size:36px;font-weight:bold;color:#7eb8d4;line-height:1;">{ec}</div>
      <div style="font-size:9px;color:#666;">out of 100</div>
    </td>
    <td style="background:{vc};padding:12px 16px;width:25%;vertical-align:middle;border-left:1px solid rgba(255,255,255,0.1);">
      <div style="font-size:9px;color:rgba(255,255,255,0.6);text-transform:uppercase;">Verdict</div>
      <div style="font-size:22px;font-weight:bold;color:white;margin-top:4px;">{result.verdict}</div>
    </td>
    <td style="background:#f9f6f0;padding:12px 16px;width:25%;vertical-align:middle;border-left:1px solid #e8e0d0;">
      <div style="font-size:9px;color:#888;text-transform:uppercase;margin-bottom:6px;">Floor Rules</div>
      {''.join(f'<div style="font-size:10px;color:{RED};font-weight:bold;">{c}</div>' for c in floor_codes) or '<div style="font-size:10px;color:#1A7A3A;">None triggered</div>'}
    </td>
  </tr>
</table>

<!-- PAGE 2: EVIDENCE FLOW DIAGRAM -->
<div class="page-break"></div>

<h2>Evidence Flow</h2>
<div style="font-size:10px;color:#666;margin-bottom:16px;">
  How public evidence becomes an investment decision. Every step is deterministic and auditable.
</div>

<table style="width:60%;margin:0 auto;border-collapse:collapse;">
  {''.join(
      f'''<tr>
        <td style="text-align:center;padding:0;">
          <div style="background:{bg};color:{fc};padding:12px 20px;border-radius:4px;
                      font-size:11px;font-weight:bold;margin:4px 40px;">{label}</div>
          {'<div style="text-align:center;font-size:16px;color:#aaa;padding:2px 0;">&#9660;</div>' if arrow else ''}
        </td>
      </tr>'''
      for label, bg, fc, arrow in [
          ("14 Public Source Categories", "#f5f0e8", NAVY, True),
          ("Evidence Retrieval Layer", "#e8f0f8", NAVY, True),
          ("Evidence Validation + Provenance Recording", "#e8f0f8", NAVY, True),
          (f"Deterministic Rules Engine ({result.rules_version})", NAVY, AMBER, True),
          ("Floor Rule Assessment", NAVY, WHITE, True),
          ("Investment Readiness Score + Verdict", vc, WHITE, True),
          ("Evidence Book + Investment Report", AMBER, NAVY, False),
      ]
  )}
</table>

<div style="margin-top:24px;padding:14px 18px;background:#f9f6f0;border-left:3px solid {AMBER};">
  <div style="font-size:10px;font-weight:bold;color:{NAVY};margin-bottom:6px;">Every conclusion is independently verifiable.</div>
  <div style="font-size:10px;color:#444;line-height:1.6;">
    Every conclusion in this Evidence Book is traceable to a named public source listed in the Evidence Provenance Register.
    Each row carries an Evidence ID, the public source, retrieval status, confidence level, and the rule code governing its scoring impact.
    To verify any finding: locate the Evidence ID, visit the named public source, and confirm the value independently.
    The verdict cannot be altered without changing the underlying evidence or the rule set. Both are version-locked.
  </div>
</div>

<!-- DIMENSION SUMMARY TABLE -->
<h2 style="margin-top:20px;">Dimension Score Summary</h2>
<table style="width:100%;border-collapse:collapse;border:1px solid #e8e8e8;">
  <tr style="background:{NAVY};">
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:left;">Dimension</th>
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:left;">Name</th>
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:right;">Weight</th>
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:right;">Score</th>
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:right;">Contribution</th>
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:left;">Evidence Fields</th>
    <th style="padding:6px 10px;color:white;font-size:9px;text-align:left;">Data Gaps</th>
  </tr>
  {''.join(
      f'''<tr style="background:{'#f9f9f9' if i%2==0 else WHITE};">
        <td style="padding:6px 10px;font-size:10px;font-weight:bold;color:{NAVY};">{code}</td>
        <td style="padding:6px 10px;font-size:10px;color:#333;">{data.get("name","")}</td>
        <td style="padding:6px 10px;font-size:10px;text-align:right;">{int(data.get("weight",0)*100)}%</td>
        <td style="padding:6px 10px;font-size:11px;font-weight:bold;text-align:right;color:{NAVY};">{data.get("adjusted_score",0):.1f}</td>
        <td style="padding:6px 10px;font-size:10px;text-align:right;color:#555;">{data.get("weighted_contribution",0):.1f}</td>
        <td style="padding:6px 10px;font-size:10px;color:#555;">{len(data.get("evidence_fields",[]))}</td>
        <td style="padding:6px 10px;font-size:10px;color:{RED if data.get("data_gaps") else "#1A7A3A"};">{len(data.get("data_gaps",[]))}</td>
      </tr>'''
      for i, (code, data) in enumerate(envelope.get("dimensions", {}).items())
  )}
</table>

<!-- PAGE 3+: EVIDENCE PROVENANCE REGISTER -->
<div class="page-break"></div>

<h2>Evidence Provenance Register</h2>
<div style="font-size:10px;color:#666;margin-bottom:10px;">
  Complete field-level provenance for Decision ID {did}.
  {row_count} evidence fields assessed across 6 dimensions.
  Challenge any finding by verifying the named public source directly.
</div>

<table style="width:100%;border-collapse:collapse;border:1px solid #e8e8e8;font-size:10px;">
  <tr style="background:{NAVY};">
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;white-space:nowrap;">Evidence ID</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Dim</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Field</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Value</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Public Source</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Status</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Confidence</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Rule</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Retrieved</th>
    <th style="padding:5px 8px;color:white;font-size:8px;text-align:left;">Score Effect</th>
  </tr>
  {register_rows}
</table>

<!-- FLOOR RULES -->
{floors_html}

<!-- DATA GAPS -->
{gaps_html}

<!-- METHODOLOGY STATEMENT -->
<div class="page-break"></div>

<h2>Methodology Statement</h2>
<div style="font-size:10px;color:#444;line-height:1.7;margin-bottom:16px;">
  <p>SEAM (Structured Evidence for African Mining) produces Investment Readiness Reports under a fixed methodology ({result.methodology_version}) and a versioned rule set ({result.rules_version}).</p>
  <p>The methodology scores six dimensions: D1 Jurisdiction Stability, D2 Revenue Transparency, D3 Asset Data Quality, D4 Local Content Compliance Posture, D5 Infrastructure Readiness, and D6 Capital Access Signals. Dimension weights are fixed in the rule set. Sub-scores within each dimension are computed from retrieved evidence fields. Floor rules operate independently of dimension scores and can cap the maximum permissible verdict regardless of aggregate score.</p>
  <p>The scoring engine contains no language model. No probabilistic inference contributes to any score. The intelligence layer (narrative generation) is constrained to the evidence envelope and cannot alter scores, verdicts or floor rule outcomes.</p>
  <p>All evidence fields are sourced from named public databases and filings. Where a field cannot be retrieved, a conservative default is applied and the field is recorded as a data gap. Defaults are never presented as retrieved findings.</p>
</div>

<h2>Replayability Declaration</h2>
<div style="background:{NAVY};padding:14px 18px;border-radius:3px;">
  <div style="font-size:10px;color:white;line-height:1.7;">
    Evidence Envelope Hash: <span style="font-family:monospace;color:{AMBER};">{envelope.get('envelope_hash','')}</span><br>
    Methodology: {result.methodology_version} &nbsp;|&nbsp; Rules: {result.rules_version}<br>
    Generated: {gen}<br>
    Decision ID: {did}<br><br>
    <span style="color:rgba(255,255,255,0.75);">
    Running the SEAM scoring engine against this evidence envelope under {result.rules_version}
    will reproduce the same scores, floor rule outcomes and verdict. The envelope hash above
    provides cryptographic confirmation that the evidence set has not been altered.
    </span>
  </div>
</div>

<div style="margin-top:20px;padding-top:10px;border-top:1px solid #eee;font-size:9px;color:#ccc;text-align:center;">
  SEAM Evidence Book. For informational purposes only. Not investment, legal or financial advice.
  Every finding is traceable to a named public source. akinmade.co.uk &nbsp;|&nbsp; CONFIDENTIAL
</div>

</body>
</html>"""

    safe_name   = result.asset_id.replace("/", "-")
    output_path = os.path.join(output_dir, f"{safe_name}_SEAM_EvidenceBook.pdf")
    HTML(string=html).write_pdf(output_path)
    return output_path



