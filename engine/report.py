"""
SEAM PDF Report Generator
Sprint 2 — WeasyPrint PDF from engine scores + Claude intelligence layer.

Style: CLEARANCE-equivalent. Professional. Clean. Amber #C8962E / Navy #0B1929.

Report order:
  1. Principal Finding  (promoted — this is the moat)
  2. What the Investor Does Not Know
  3. Dimension Findings  (with Evidence Confidence)
  4. Verdict and Next Action
  5. Evidence Reference
"""

from weasyprint import HTML
from engine.scoring import ScoringResult
from datetime import datetime
import os

AMBER = "#C8962E"
NAVY = "#0B1929"

VERDICT_COLOURS = {
    "PROCEED": "#1A7A3A",
    "PROCEED WITH CONDITIONS": "#B8860B",
    "MONITOR": "#1A5FA8",
    "CAUTION": "#C65C00",
    "AVOID": "#CC0000",
}

CONFIDENCE_COLOURS = {
    "High": "#1A7A3A",
    "Medium": "#B8860B",
    "Low": "#CC0000",
}


def score_bar(score: float, width: int = 200) -> str:
    filled = int((score / 100) * width)
    return f"""
    <div style="background:#e8e8e8;border-radius:3px;height:10px;width:{width}px;display:inline-block;vertical-align:middle;">
      <div style="background:{AMBER};border-radius:3px;height:10px;width:{filled}px;"></div>
    </div>"""


def confidence_badge(level: str) -> str:
    colour = CONFIDENCE_COLOURS.get(level, "#888")
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:3px;'
        f'background:{colour};color:white;font-size:10px;font-weight:bold;'
        f'letter-spacing:0.5px;margin-left:8px;">Evidence: {level}</span>'
    )


def build_html(result: ScoringResult, intel: dict, asset_input) -> str:
    verdict_color = VERDICT_COLOURS.get(result.verdict, "#333333")
    generated = datetime.fromisoformat(result.generated_at).strftime("%d %B %Y, %H:%M UTC")

    # --- Dimension rows (Section 3) ---
    dim_rows = ""
    for d in result.dimensions:
        gaps_html = ""
        if d.data_gaps:
            gaps_html = "<br>" + "<br>".join(
                f'<span style="color:#C65C00;font-size:11px;">&#9888; {g}</span>'
                for g in d.data_gaps
            )
        adj_html = ""
        if d.adjustments:
            for a in d.adjustments:
                if a.get("adjustment") is not None:
                    sign = "+" if a["adjustment"] > 0 else ""
                    color = "#1A7A3A" if a["adjustment"] > 0 else "#CC0000"
                    adj_html += f'<br><span style="font-size:11px;color:{color};">{sign}{a["adjustment"]}pts: {a["reason"]}</span>'

        # New structure: dimension_findings is now a dict with "finding" and "evidence_confidence"
        dim_intel = intel.get("dimension_findings", {}).get(d.code, {})
        if isinstance(dim_intel, dict):
            finding_text = dim_intel.get("finding", "")
            conf_level = dim_intel.get("evidence_confidence", "Low")
        else:
            # backward compat if plain string
            finding_text = dim_intel
            conf_level = "Low"

        conf_html = confidence_badge(conf_level) if conf_level else ""

        finding_html = ""
        if finding_text:
            finding_html = f'<div style="margin-top:6px;font-size:12px;color:#444;line-height:1.5;">{finding_text}</div>'

        dim_rows += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e8e8;vertical-align:top;width:40px;">
            <span style="font-weight:bold;color:{NAVY};font-size:13px;">{d.code}</span>
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e8e8;vertical-align:top;">
            <div style="font-weight:bold;color:#222;font-size:13px;">{d.name}{conf_html}</div>
            <div style="color:#888;font-size:11px;margin-top:2px;">Weight: {int(d.weight*100)}%</div>
            {adj_html}{gaps_html}
            {finding_html}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #e8e8e8;vertical-align:middle;text-align:right;white-space:nowrap;">
            <span style="font-size:20px;font-weight:bold;color:{NAVY};">{d.adjusted_score:.1f}</span>
            <span style="color:#888;font-size:12px;">/100</span>
            <div style="margin-top:4px;">{score_bar(d.adjusted_score, 120)}</div>
          </td>
        </tr>"""

    # --- Investor intelligence items (Section 2) ---
    intel_items = ""
    for i, finding in enumerate(intel.get("investor_intelligence", []), 1):
        intel_items += f"""
        <div style="display:flex;margin-bottom:14px;align-items:flex-start;">
          <div style="min-width:28px;height:28px;background:{AMBER};border-radius:50%;
                      display:flex;align-items:center;justify-content:center;
                      font-weight:bold;color:white;font-size:13px;margin-right:12px;margin-top:1px;">{i}</div>
          <div style="font-size:13px;color:#333;line-height:1.6;">{finding}</div>
        </div>"""

    # --- Floor rules ---
    floor_html = ""
    if result.floor_rules_triggered:
        rules_text = " ".join(
            f'<div style="background:#fff3cd;border-left:4px solid #C65C00;padding:8px 12px;margin-top:8px;font-size:12px;color:#333;">'
            f'<strong>{r["code"]}</strong> — {r["description"]}</div>'
            for r in result.floor_rules_triggered
        )
        floor_html = f"""
        <div style="margin-top:16px;">
          <div style="font-weight:bold;color:#C65C00;font-size:13px;margin-bottom:4px;">Floor Rules Triggered</div>
          {rules_text}
        </div>"""

    # Principal finding
    principal = intel.get("principal_finding", intel.get("executive_summary", ""))

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-center {{
      content: "SEAM  |  {result.asset_id}  |  {result.methodology_version}  |  CONFIDENTIAL  |  Page " counter(page) " of " counter(pages);
      font-family: Arial, sans-serif;
      font-size: 9px;
      color: #999;
    }}
  }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 13px;
    color: #222;
    margin: 0;
    padding: 0;
    line-height: 1.5;
  }}
  h1 {{ font-size: 22px; color: {NAVY}; margin: 0 0 4px 0; }}
  h2 {{ font-size: 15px; color: {NAVY}; margin: 24px 0 8px 0; border-bottom: 2px solid {AMBER}; padding-bottom: 4px; }}
  h3 {{ font-size: 13px; color: {NAVY}; margin: 16px 0 6px 0; }}
  table {{ border-collapse: collapse; width: 100%; }}
  .label {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
</style>
</head>
<body>

<!-- HEADER BAR -->
<table style="width:100%;margin-bottom:20px;">
  <tr>
    <td style="vertical-align:middle;">
      <div style="font-size:28px;font-weight:bold;color:{AMBER};letter-spacing:1px;">SEAM</div>
      <div style="font-size:11px;color:{NAVY};letter-spacing:0.5px;">STRUCTURED EVIDENCE FOR AFRICAN MINING</div>
    </td>
    <td style="text-align:right;vertical-align:middle;">
      <div style="font-size:11px;color:#888;">Investment Readiness Report</div>
      <div style="font-size:11px;color:#888;">{generated}</div>
      <div style="font-size:11px;color:#888;">{result.methodology_version}  |  {result.rules_version}</div>
    </td>
  </tr>
</table>
<div style="height:3px;background:{NAVY};margin-bottom:20px;"></div>

<!-- ASSET IDENTITY -->
<h1>{result.asset_name}</h1>
<div style="color:#666;font-size:12px;margin-bottom:16px;">
  {asset_input.jurisdiction}  &nbsp;|&nbsp;  {asset_input.province}  &nbsp;|&nbsp;  {asset_input.commodity}  &nbsp;|&nbsp;  {result.asset_id}
</div>

<!-- SCORE AND VERDICT BANNER -->
<table style="width:100%;margin-bottom:20px;border-collapse:collapse;">
  <tr>
    <td style="background:{NAVY};padding:16px 20px;width:50%;vertical-align:middle;">
      <div class="label" style="color:#aaa;">Investment Readiness Score</div>
      <div style="font-size:48px;font-weight:bold;color:{AMBER};line-height:1.1;">{result.investment_readiness_score}</div>
      <div style="color:#aaa;font-size:13px;">out of 100</div>
    </td>
    <td style="background:{verdict_color};padding:16px 20px;width:50%;vertical-align:middle;">
      <div class="label" style="color:rgba(255,255,255,0.7);">Verdict</div>
      <div style="font-size:24px;font-weight:bold;color:white;line-height:1.2;">{result.verdict}</div>
    </td>
  </tr>
</table>

<!-- SECTION 1: PRINCIPAL FINDING -->
<h2>1. Principal Finding</h2>
<div style="background:#f4f0e8;border-left:4px solid {AMBER};padding:14px 18px;font-size:13px;color:#333;line-height:1.7;">
  {principal.replace(chr(10), "<br>")}
</div>

<!-- SECTION 2: WHAT THE INVESTOR DOES NOT KNOW -->
<h2>2. What the Investor Does Not Know</h2>
<div style="font-size:12px;color:#666;margin-bottom:14px;">
  Signals, dependencies and structural risks not visible from a surface read of public data. Each finding is grounded in the evidence envelope.
</div>
{intel_items}

<!-- SECTION 3: DIMENSION FINDINGS -->
<h2>3. Dimension Findings</h2>
<table style="width:100%;border:1px solid #e8e8e8;">
  <thead>
    <tr style="background:{NAVY};">
      <th style="padding:8px 12px;color:white;text-align:left;font-size:12px;width:40px;">Code</th>
      <th style="padding:8px 12px;color:white;text-align:left;font-size:12px;">Dimension</th>
      <th style="padding:8px 12px;color:white;text-align:right;font-size:12px;width:140px;">Score</th>
    </tr>
  </thead>
  <tbody>
    {dim_rows}
  </tbody>
</table>

<!-- SECTION 4: VERDICT AND NEXT ACTION -->
<h2>4. Verdict and Next Action</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
  <tr>
    <td style="background:{verdict_color};padding:14px 20px;vertical-align:middle;">
      <div class="label" style="color:rgba(255,255,255,0.7);">Verdict — {result.methodology_version}</div>
      <div style="font-size:22px;font-weight:bold;color:white;margin-top:4px;">{result.verdict}</div>
    </td>
  </tr>
</table>
<div style="font-size:13px;color:#333;line-height:1.6;">
  {intel.get("verdict_section", "").replace(chr(10), "<br>")}
</div>
{floor_html}

<div style="margin-top:20px;padding:14px;background:#f8f8f8;border-left:4px solid {AMBER};">
  <div class="label" style="margin-bottom:6px;">Next Action</div>
  <div style="font-size:13px;color:#333;font-weight:bold;">{result.next_action}</div>
</div>

<!-- SECTION 5: EVIDENCE REFERENCE -->
<h2>5. Evidence Reference</h2>
<table style="width:100%;font-size:11px;color:#666;">
  <tr>
    <td style="padding:4px 0;width:40%;"><strong>Methodology Version</strong></td>
    <td>{result.methodology_version}</td>
  </tr>
  <tr>
    <td style="padding:4px 0;"><strong>Rules Version</strong></td>
    <td>{result.rules_version}</td>
  </tr>
  <tr>
    <td style="padding:4px 0;"><strong>Generated</strong></td>
    <td>{generated}</td>
  </tr>
  <tr>
    <td style="padding:4px 0;"><strong>Asset ID</strong></td>
    <td>{result.asset_id}</td>
  </tr>
  <tr>
    <td style="padding:4px 0;"><strong>Scoring Engine</strong></td>
    <td>Deterministic rules engine. No LLM in scoring path. Identical inputs always produce identical outputs.</td>
  </tr>
  <tr>
    <td style="padding:4px 0;"><strong>Intelligence Layer</strong></td>
    <td>Claude (Anthropic) — constrained to evidence envelope. Cannot alter scores or verdicts.</td>
  </tr>
  <tr>
    <td style="padding:4px 0;"><strong>Data sources</strong></td>
    <td>EITI, Fraser Institute, World Bank WGI, USGS, ASX/TSX/AIM filings, Ministry of Mines publications, cadastre portals</td>
  </tr>
</table>

<div style="margin-top:24px;padding-top:12px;border-top:1px solid #e8e8e8;font-size:10px;color:#aaa;text-align:center;">
  SEAM Investment Readiness Reports are produced for informational purposes only. They do not constitute investment advice, legal advice or financial advice.
  They do not constitute due diligence and are not a substitute for independent technical, legal or financial assessment.
  akinmade.co.uk  |  CONFIDENTIAL
</div>

</body>
</html>"""

    return html


def generate_pdf(result: ScoringResult, intel: dict, asset_input, output_dir: str = "output") -> str:
    """Generate PDF report. Returns path to output file."""
    os.makedirs(output_dir, exist_ok=True)
    html = build_html(result, intel, asset_input)
    output_path = os.path.join(output_dir, f"{result.asset_id}_SEAM_Report.pdf")
    HTML(string=html).write_pdf(output_path)
    return output_path
