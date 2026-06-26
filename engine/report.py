"""
SEAM PDF Report Generator
Sprint 3 layout — visual hierarchy over essay.

Structure:
  Cover band: Score | Verdict
  Section 1: Principal Finding
  Section 2: What the Investor Does Not Know
  Section 3: Dimension Cards (2-column grid)
  Section 4: Verdict and Next Action
  Section 5: Evidence Reference
"""

from weasyprint import HTML
from engine.scoring import ScoringResult
from datetime import datetime
import os

AMBER = "#C8962E"
NAVY  = "#0B1929"

VERDICT_COLOURS = {
    "PROCEED":                "#1A7A3A",
    "PROCEED WITH CONDITIONS": "#B8860B",
    "MONITOR":                "#1A5FA8",
    "CAUTION":                "#C65C00",
    "AVOID":                  "#CC0000",
}

CONFIDENCE_COLOURS = {
    "High":   "#1A7A3A",
    "Medium": "#B8860B",
    "Low":    "#CC0000",
}


def score_bar(score: float, width: int = 160) -> str:
    filled = int((score / 100) * width)
    return (
        f'<div style="background:#e0e0e0;border-radius:3px;height:8px;width:{width}px;margin-top:4px;">'
        f'<div style="background:{AMBER};border-radius:3px;height:8px;width:{filled}px;"></div>'
        f'</div>'
    )


def confidence_pill(level: str) -> str:
    colour = CONFIDENCE_COLOURS.get(level, "#888")
    return (
        f'<span style="display:inline-block;padding:1px 7px;border-radius:10px;'
        f'background:{colour};color:white;font-size:9px;font-weight:bold;'
        f'letter-spacing:0.4px;vertical-align:middle;margin-left:6px;">Evidence: {level}</span>'
    )


def build_html(result: ScoringResult, intel: dict, asset_input) -> str:
    verdict_color = VERDICT_COLOURS.get(result.verdict, "#333")
    generated = datetime.fromisoformat(result.generated_at).strftime("%d %B %Y, %H:%M UTC")

    # --- Dimension cards (2-column grid) ---
    dim_cards_html = ""
    dims = result.dimensions
    for i in range(0, len(dims), 2):
        row_cards = ""
        for d in dims[i:i+2]:
            dim_intel = intel.get("dimension_findings", {}).get(d.code, {})
            if isinstance(dim_intel, dict):
                finding_text = dim_intel.get("finding", "")
                conf_level   = dim_intel.get("evidence_confidence", "Low")
            else:
                finding_text = str(dim_intel)
                conf_level   = "Low"

            gaps_html = ""
            if d.data_gaps:
                gaps_html = "".join(
                    f'<div style="font-size:10px;color:#C65C00;margin-top:3px;">&#9888; {g}</div>'
                    for g in d.data_gaps
                )

            adj_html = ""
            if d.adjustments:
                for a in d.adjustments:
                    if a.get("adjustment") is not None:
                        sign  = "+" if a["adjustment"] > 0 else ""
                        col   = "#1A7A3A" if a["adjustment"] > 0 else "#CC0000"
                        adj_html += f'<div style="font-size:10px;color:{col};margin-top:2px;">{sign}{a["adjustment"]}pts: {a["reason"]}</div>'

            # Format finding text: lines starting with "Gap:" become coloured
            formatted_finding = ""
            if finding_text:
                for line in finding_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if line.lower().startswith("gap:"):
                        formatted_finding += f'<div style="font-size:11px;color:#C65C00;margin-top:3px;">&#9888; {line[4:].strip()}</div>'
                    else:
                        formatted_finding += f'<div style="font-size:11px;color:#444;margin-top:3px;line-height:1.45;">{line}</div>'

            row_cards += f"""
            <td style="width:50%;padding:4px;">
              <div style="border:1px solid #e0e0e0;border-radius:4px;padding:12px 14px;height:100%;box-sizing:border-box;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
                  <div>
                    <span style="font-size:11px;font-weight:bold;color:{NAVY};letter-spacing:0.3px;">{d.code}</span>
                    <span style="font-size:11px;color:#555;margin-left:4px;">{d.name}</span>
                    {confidence_pill(conf_level)}
                  </div>
                  <div style="text-align:right;min-width:60px;">
                    <span style="font-size:20px;font-weight:bold;color:{NAVY};">{d.adjusted_score:.0f}</span>
                    <span style="font-size:10px;color:#888;">/100</span>
                  </div>
                </div>
                {score_bar(d.adjusted_score, 160)}
                <div style="font-size:10px;color:#aaa;margin-top:2px;margin-bottom:6px;">Weight: {int(d.weight*100)}%{adj_html}</div>
                {gaps_html}
                {formatted_finding}
              </div>
            </td>"""

        # pad odd row
        if len(dims[i:i+2]) == 1:
            row_cards += '<td style="width:50%;padding:4px;"></td>'

        dim_cards_html += f'<tr style="vertical-align:top;">{row_cards}</tr>'

    # --- Intelligence findings ---
    intel_items = ""
    for idx, finding in enumerate(intel.get("investor_intelligence", []), 1):
        intel_items += f"""
        <div style="display:flex;margin-bottom:12px;align-items:flex-start;">
          <div style="min-width:24px;height:24px;background:{NAVY};border-radius:50%;
                      display:flex;align-items:center;justify-content:center;
                      font-weight:bold;color:white;font-size:11px;
                      margin-right:10px;margin-top:1px;flex-shrink:0;">{idx}</div>
          <div style="font-size:12px;color:#333;line-height:1.55;">{finding}</div>
        </div>"""

    # --- Floor rules ---
    floor_html = ""
    if result.floor_rules_triggered:
        rows = "".join(
            f'<tr><td style="padding:5px 10px;font-weight:bold;color:#C65C00;font-size:11px;white-space:nowrap;">{r["code"]}</td>'
            f'<td style="padding:5px 10px;font-size:11px;color:#333;">{r["description"]}</td></tr>'
            for r in result.floor_rules_triggered
        )
        floor_html = f"""
        <div style="margin-top:14px;">
          <div style="font-size:11px;font-weight:bold;color:#C65C00;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.4px;">Floor Rules Triggered</div>
          <table style="border:1px solid #f0d0a0;border-radius:3px;width:100%;border-collapse:collapse;background:#fffaf0;">
            {rows}
          </table>
        </div>"""

    principal = intel.get("principal_finding", "")
    verdict_text = intel.get("verdict_section", "")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{
    size: A4;
    margin: 15mm 14mm 15mm 14mm;
    @bottom-center {{
      content: "SEAM  |  {result.asset_id}  |  {result.methodology_version}  |  CONFIDENTIAL  |  Page " counter(page) " of " counter(pages);
      font-family: Arial, sans-serif;
      font-size: 8px;
      color: #bbb;
    }}
  }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 12px;
    color: #222;
    margin: 0;
    padding: 0;
    line-height: 1.45;
  }}
  h2 {{
    font-size: 12px;
    color: {NAVY};
    margin: 18px 0 7px 0;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-bottom: 1.5px solid {AMBER};
    padding-bottom: 3px;
  }}
  .label {{ color: #aaa; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }}
</style>
</head>
<body>

<!-- HEADER -->
<table style="width:100%;margin-bottom:14px;">
  <tr>
    <td style="vertical-align:middle;">
      <div style="font-size:24px;font-weight:bold;color:{AMBER};letter-spacing:1px;line-height:1;">SEAM</div>
      <div style="font-size:9px;color:{NAVY};letter-spacing:0.5px;margin-top:2px;">STRUCTURED EVIDENCE FOR AFRICAN MINING</div>
    </td>
    <td style="text-align:right;vertical-align:middle;">
      <div style="font-size:10px;color:#888;">Investment Readiness Report</div>
      <div style="font-size:10px;color:#888;">{generated}</div>
      <div style="font-size:10px;color:#888;">{result.methodology_version} | {result.rules_version}</div>
    </td>
  </tr>
</table>
<div style="height:2px;background:{NAVY};margin-bottom:12px;"></div>

<!-- ASSET NAME -->
<div style="font-size:17px;font-weight:bold;color:{NAVY};margin-bottom:2px;">{result.asset_name}</div>
<div style="font-size:10px;color:#888;margin-bottom:12px;">
  {asset_input.jurisdiction} &nbsp;|&nbsp; {asset_input.province} &nbsp;|&nbsp; {asset_input.commodity} &nbsp;|&nbsp; {result.asset_id}
</div>

<!-- SCORE + VERDICT BAND -->
<table style="width:100%;border-collapse:collapse;margin-bottom:14px;">
  <tr>
    <td style="background:{NAVY};padding:14px 18px;width:48%;vertical-align:middle;">
      <div class="label" style="color:#888;">Investment Readiness Score</div>
      <div style="font-size:44px;font-weight:bold;color:{AMBER};line-height:1;">{result.investment_readiness_score}</div>
      <div style="color:#888;font-size:11px;">out of 100</div>
      <div style="margin-top:6px;">{score_bar(result.investment_readiness_score, 180)}</div>
    </td>
    <td style="background:{verdict_color};padding:14px 18px;width:52%;vertical-align:middle;">
      <div class="label" style="color:rgba(255,255,255,0.6);">Verdict</div>
      <div style="font-size:26px;font-weight:bold;color:white;line-height:1.1;margin-top:4px;">{result.verdict}</div>
      <div style="font-size:10px;color:rgba(255,255,255,0.75);margin-top:8px;">{result.next_action[:90]}{'...' if len(result.next_action) > 90 else ''}</div>
    </td>
  </tr>
</table>

<!-- SECTION 1: PRINCIPAL FINDING -->
<h2>1. Principal Finding</h2>
<div style="background:#f5f0e8;border-left:3px solid {AMBER};padding:11px 14px;font-size:12px;color:#333;line-height:1.55;">
  {principal.replace(chr(10), "<br>")}
</div>

<!-- SECTION 2: WHAT THE INVESTOR DOES NOT KNOW -->
<h2>2. What the Investor Does Not Know</h2>
<div style="font-size:10px;color:#888;margin-bottom:10px;font-style:italic;">
  Cross-dimension signals not visible from individual scores. Each finding is grounded in the evidence envelope.
</div>
{intel_items}

<!-- SECTION 3: DIMENSION FINDINGS -->
<h2>3. Dimension Findings</h2>
<table style="width:100%;border-collapse:collapse;">
  {dim_cards_html}
</table>

<!-- SECTION 4: VERDICT AND NEXT ACTION -->
<h2>4. Verdict and Next Action</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:12px;">
  <tr>
    <td style="background:{verdict_color};padding:11px 16px;">
      <div class="label" style="color:rgba(255,255,255,0.6);">Verdict</div>
      <div style="font-size:18px;font-weight:bold;color:white;margin-top:3px;">{result.verdict}</div>
    </td>
  </tr>
</table>
<div style="font-size:12px;color:#333;line-height:1.55;margin-bottom:10px;">
  {verdict_text.replace(chr(10), "<br>")}
</div>
{floor_html}
<div style="margin-top:12px;padding:11px 14px;background:#f8f8f8;border-left:3px solid {AMBER};">
  <div class="label" style="margin-bottom:4px;">Next Action</div>
  <div style="font-size:12px;color:#222;font-weight:bold;">{result.next_action}</div>
</div>

<!-- SECTION 5: EVIDENCE REFERENCE -->
<h2>5. Evidence Reference</h2>
<table style="width:100%;font-size:10px;color:#666;border-collapse:collapse;">
  <tr><td style="padding:3px 0;width:38%;"><strong>Methodology</strong></td><td>{result.methodology_version}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Rules Version</strong></td><td>{result.rules_version}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Generated</strong></td><td>{generated}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Asset ID</strong></td><td>{result.asset_id}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Scoring Engine</strong></td><td>Deterministic rules engine. No LLM in scoring path. Identical inputs produce identical outputs.</td></tr>
  <tr><td style="padding:3px 0;"><strong>Intelligence Layer</strong></td><td>Claude (Anthropic) — constrained to evidence envelope. Cannot alter scores or verdicts.</td></tr>
  <tr><td style="padding:3px 0;"><strong>Data Sources</strong></td><td>EITI, Fraser Institute, World Bank WGI, USGS, ASX/TSX/AIM filings, Ministry of Mines publications, cadastre portals</td></tr>
</table>

<div style="margin-top:18px;padding-top:10px;border-top:1px solid #eee;font-size:9px;color:#bbb;text-align:center;">
  SEAM Investment Readiness Reports are produced for informational purposes only and do not constitute investment advice, legal advice or financial advice.
  Not a substitute for independent technical, legal or financial assessment. &nbsp; akinmade.co.uk &nbsp;|&nbsp; CONFIDENTIAL
</div>

</body>
</html>"""

    return html


def generate_pdf(result: ScoringResult, intel: dict, asset_input, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    html = build_html(result, intel, asset_input)
    output_path = os.path.join(output_dir, f"{result.asset_id}_SEAM_Report.pdf")
    HTML(string=html).write_pdf(output_path)
    return output_path
