"""
SEAM PDF Report Generator
Decision-first layout. Information hierarchy over essay.

Page 1:  Header | Score band (3 cells) | Investment Decision Summary | Critical Risks
Page 2+: Investment Drivers | Dimension Detail | Verdict | Evidence Reference
"""

from weasyprint import HTML
from engine.scoring import ScoringResult
from datetime import datetime
import os

AMBER  = "#C8962E"
NAVY   = "#0B1929"

VERDICT_COLOURS = {
    "PROCEED":                 "#1A7A3A",
    "PROCEED WITH CONDITIONS": "#B8860B",
    "MONITOR":                 "#1A5FA8",
    "CAUTION":                 "#C65C00",
    "AVOID":                   "#CC0000",
}

CONFIDENCE_COLOURS = {
    "High":   "#1A7A3A",
    "Medium": "#B8860B",
    "Low":    "#CC0000",
}


def mini_bar(score: float, width: int = 140) -> str:
    filled = max(0, int((score / 100) * width))
    return (
        f'<div style="background:#2a3f55;border-radius:2px;height:6px;width:{width}px;margin-top:5px;">'
        f'<div style="background:{AMBER};border-radius:2px;height:6px;width:{filled}px;"></div>'
        f'</div>'
    )


def score_bar_light(score: float, width: int = 150) -> str:
    filled = max(0, int((score / 100) * width))
    return (
        f'<div style="background:#e0e0e0;border-radius:2px;height:6px;width:{width}px;margin-top:4px;">'
        f'<div style="background:{AMBER};border-radius:2px;height:6px;width:{filled}px;"></div>'
        f'</div>'
    )


def confidence_pill(level: str) -> str:
    col = CONFIDENCE_COLOURS.get(level, "#888")
    return (
        f'<span style="display:inline-block;padding:1px 6px;border-radius:8px;'
        f'background:{col};color:white;font-size:9px;font-weight:bold;'
        f'letter-spacing:0.3px;vertical-align:middle;margin-left:6px;">{level}</span>'
    )


def build_html(result: ScoringResult, intel: dict, asset_input) -> str:
    vc     = VERDICT_COLOURS.get(result.verdict, "#333")
    gen    = datetime.fromisoformat(result.generated_at).strftime("%d %B %Y, %H:%M UTC")
    ec     = result.evidence_completeness_score

    # Pull structured intel blocks — graceful fallback for legacy shape
    inv_dec  = intel.get("investment_decision", {})
    v_conf   = inv_dec.get("verdict_confidence", "Low")
    cr_count = inv_dec.get("critical_risks", len(result.floor_rules_triggered))

    drivers      = intel.get("investment_drivers", {})
    positives    = drivers.get("positive", [])
    negatives    = drivers.get("negative", [])
    unknowns     = drivers.get("unknown", [])
    ev_summary   = intel.get("evidence_summary", "")
    critical_risks = intel.get("critical_risks", [])

    # Verdict confidence colour
    vc_colour = CONFIDENCE_COLOURS.get(v_conf, "#888")

    # --- Investment Decision Summary panel ---
    decision_panel = f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;border:1px solid #e0e0e0;">
      <tr>
        <td style="background:{NAVY};padding:14px 18px;width:26%;vertical-align:middle;border-right:1px solid #2a3f55;">
          <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">Investment Readiness</div>
          <div style="font-size:40px;font-weight:bold;color:{AMBER};line-height:1;margin-top:3px;">{result.investment_readiness_score}</div>
          <div style="font-size:9px;color:#666;">out of 100</div>
          {mini_bar(result.investment_readiness_score, 120)}
        </td>
        <td style="background:#162436;padding:14px 18px;width:26%;vertical-align:middle;border-right:1px solid #2a3f55;">
          <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">Evidence Completeness</div>
          <div style="font-size:40px;font-weight:bold;color:#7eb8d4;line-height:1;margin-top:3px;">{ec}</div>
          <div style="font-size:9px;color:#666;">out of 100</div>
          {mini_bar(ec, 120)}
        </td>
        <td style="background:{vc};padding:14px 18px;width:28%;vertical-align:middle;border-right:1px solid rgba(255,255,255,0.15);">
          <div style="font-size:9px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:0.5px;">Verdict</div>
          <div style="font-size:22px;font-weight:bold;color:white;line-height:1.1;margin-top:3px;">{result.verdict}</div>
          <div style="margin-top:6px;">
            <span style="font-size:9px;color:rgba(255,255,255,0.6);">Confidence: </span>
            <span style="display:inline-block;padding:1px 7px;border-radius:8px;background:rgba(255,255,255,0.2);color:white;font-size:9px;font-weight:bold;">{v_conf}</span>
          </div>
        </td>
        <td style="background:#f8f4ec;padding:14px 18px;width:20%;vertical-align:middle;">
          <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">At a Glance</div>
          <div style="font-size:11px;color:#333;margin-bottom:4px;">
            <span style="color:{CONFIDENCE_COLOURS.get('Low','#CC0000') if cr_count > 0 else '#1A7A3A'};font-weight:bold;">{cr_count}</span>
            <span style="color:#666;"> critical risks</span>
          </div>
          <div style="font-size:11px;color:#333;margin-bottom:4px;">
            <span style="font-weight:bold;color:#333;">{ec}%</span>
            <span style="color:#666;"> evidence coverage</span>
          </div>
          <div style="margin-top:8px;font-size:10px;font-weight:bold;color:{vc};">{result.next_action.split('.')[0]}.</div>
        </td>
      </tr>
    </table>"""

    # --- Critical Risks panel ---
    risks_html = ""
    if critical_risks:
        risk_rows = "".join(
            f'<div style="display:flex;margin-bottom:7px;align-items:flex-start;">'
            f'<div style="min-width:18px;height:18px;background:#CC0000;border-radius:50%;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:9px;font-weight:bold;color:white;margin-right:8px;margin-top:1px;flex-shrink:0;">{i}</div>'
            f'<div style="font-size:11px;color:#333;line-height:1.45;">{r}</div>'
            f'</div>'
            for i, r in enumerate(critical_risks, 1)
        )
        risks_html = f"""
        <div style="margin-bottom:16px;">
          <div style="font-size:10px;font-weight:bold;color:#CC0000;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">Critical Risks</div>
          {risk_rows}
        </div>"""

    # --- Investment Drivers (3 columns) ---
    def driver_col(items, label, dot_col):
        if not items:
            return ""
        rows = "".join(
            f'<div style="display:flex;margin-bottom:5px;align-items:flex-start;">'
            f'<div style="min-width:7px;height:7px;background:{dot_col};border-radius:50%;margin-right:7px;margin-top:4px;flex-shrink:0;"></div>'
            f'<div style="font-size:11px;color:#333;line-height:1.4;">{item}</div>'
            f'</div>'
            for item in items
        )
        return f"""
        <td style="width:33%;padding:0 8px;vertical-align:top;">
          <div style="font-size:9px;font-weight:bold;color:{dot_col};text-transform:uppercase;letter-spacing:0.5px;margin-bottom:7px;">{label}</div>
          {rows}
        </td>"""

    drivers_html = ""
    if positives or negatives or unknowns:
        drivers_html = f"""
        <div style="margin-bottom:16px;">
          <div style="font-size:10px;font-weight:bold;color:{NAVY};text-transform:uppercase;letter-spacing:0.5px;border-bottom:1.5px solid {AMBER};padding-bottom:3px;margin-bottom:10px;">Investment Drivers</div>
          <table style="width:100%;border-collapse:collapse;">
            <tr style="vertical-align:top;">
              {driver_col(positives, 'Positive', '#1A7A3A')}
              {driver_col(negatives, 'Negative', '#CC0000')}
              {driver_col(unknowns, 'Unknown', '#888')}
            </tr>
          </table>
        </div>"""

    # --- Dimension cards ---
    dims = result.dimensions
    dim_cards = ""
    for i in range(0, len(dims), 2):
        row = ""
        for d in dims[i:i+2]:
            dim_intel = intel.get("dimension_findings", {}).get(d.code, {})
            finding   = dim_intel.get("finding", "") if isinstance(dim_intel, dict) else str(dim_intel)
            conf      = dim_intel.get("evidence_confidence", "Low") if isinstance(dim_intel, dict) else "Low"

            gaps_html = "".join(
                f'<div style="font-size:10px;color:#C65C00;margin-top:2px;">&#9888; {g}</div>'
                for g in d.data_gaps
            )
            adj_html = ""
            for a in d.adjustments:
                if a.get("adjustment") is not None:
                    col = "#1A7A3A" if a["adjustment"] > 0 else "#CC0000"
                    sign = "+" if a["adjustment"] > 0 else ""
                    adj_html += f'<div style="font-size:10px;color:{col};margin-top:2px;">{sign}{a["adjustment"]}pts: {a["reason"]}</div>'

            # Format Gap: lines in the finding
            formatted = ""
            for line in finding.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.lower().startswith("gap:"):
                    formatted += f'<div style="font-size:10px;color:#C65C00;margin-top:2px;">&#9888; {line[4:].strip()}</div>'
                else:
                    formatted += f'<div style="font-size:10px;color:#444;margin-top:3px;line-height:1.4;">{line}</div>'

            row += f"""
            <td style="width:50%;padding:3px;">
              <div style="border:1px solid #e8e8e8;border-radius:3px;padding:10px 12px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                  <div>
                    <span style="font-size:10px;font-weight:bold;color:{NAVY};">{d.code}</span>
                    <span style="font-size:10px;color:#555;margin-left:4px;">{d.name}</span>
                    {confidence_pill(conf)}
                  </div>
                  <div style="text-align:right;">
                    <span style="font-size:18px;font-weight:bold;color:{NAVY};">{d.adjusted_score:.0f}</span>
                    <span style="font-size:9px;color:#aaa;">/100</span>
                  </div>
                </div>
                {score_bar_light(d.adjusted_score, 150)}
                <div style="font-size:9px;color:#aaa;margin-top:2px;margin-bottom:4px;">Weight {int(d.weight*100)}%{adj_html}</div>
                {gaps_html}
                {formatted}
              </div>
            </td>"""

        if len(dims[i:i+2]) == 1:
            row += '<td style="width:50%;padding:3px;"></td>'
        dim_cards += f'<tr style="vertical-align:top;">{row}</tr>'

    # --- Floor rules detail ---
    floor_html = ""
    if result.floor_rules_triggered:
        rows = "".join(
            f'<tr>'
            f'<td style="padding:4px 10px;font-size:10px;font-weight:bold;color:#C65C00;white-space:nowrap;">{r["code"]}</td>'
            f'<td style="padding:4px 10px;font-size:10px;color:#333;">{r["description"]}</td>'
            f'</tr>'
            for r in result.floor_rules_triggered
        )
        floor_html = f"""
        <div style="margin-top:12px;">
          <div style="font-size:9px;font-weight:bold;color:#C65C00;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:5px;">Floor Rules</div>
          <table style="width:100%;border-collapse:collapse;background:#fffaf0;border:1px solid #f0d0a0;">
            {rows}
          </table>
        </div>"""

    verdict_text = intel.get("verdict_section", "")

    # --- Intelligence items (renamed from "What Investor Does Not Know") ---
    intel_items_html = ""
    intel_items = intel.get("investor_intelligence", [])
    if intel_items:
        items_html = "".join(
            f'<div style="display:flex;margin-bottom:10px;align-items:flex-start;">'
            f'<div style="min-width:20px;height:20px;background:{NAVY};border-radius:50%;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:9px;font-weight:bold;color:white;margin-right:8px;margin-top:1px;flex-shrink:0;">{idx}</div>'
            f'<div style="font-size:11px;color:#333;line-height:1.5;">{f}</div>'
            f'</div>'
            for idx, f in enumerate(intel_items, 1)
        )
        intel_items_html = f"""
        <div style="font-size:10px;font-weight:bold;color:{NAVY};text-transform:uppercase;letter-spacing:0.5px;border-bottom:1.5px solid {AMBER};padding-bottom:3px;margin-bottom:10px;">Material Unknowns</div>
        {items_html}"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{
    size: A4;
    margin: 14mm 13mm 14mm 13mm;
    @bottom-center {{
      content: "SEAM  |  {result.asset_id}  |  {result.methodology_version}  |  CONFIDENTIAL  |  Page " counter(page) " of " counter(pages);
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
    font-size: 10px;
    color: {NAVY};
    margin: 16px 0 7px 0;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-bottom: 1.5px solid {AMBER};
    padding-bottom: 3px;
  }}
</style>
</head>
<body>

<!-- HEADER -->
<table style="width:100%;margin-bottom:12px;">
  <tr>
    <td style="vertical-align:middle;">
      <span style="font-size:22px;font-weight:bold;color:{AMBER};letter-spacing:1px;">SEAM</span>
      <span style="font-size:9px;color:{NAVY};letter-spacing:0.4px;margin-left:8px;">STRUCTURED EVIDENCE FOR AFRICAN MINING</span>
    </td>
    <td style="text-align:right;vertical-align:middle;">
      <div style="font-size:9px;color:#888;">Investment Readiness Report &nbsp;|&nbsp; {gen}</div>
      <div style="font-size:9px;color:#888;">{result.methodology_version} &nbsp;|&nbsp; {result.rules_version}</div>
    </td>
  </tr>
</table>
<div style="height:2px;background:{NAVY};margin-bottom:10px;"></div>

<!-- ASSET IDENTITY -->
<div style="font-size:15px;font-weight:bold;color:{NAVY};margin-bottom:2px;">{result.asset_name}</div>
<div style="font-size:9px;color:#888;margin-bottom:10px;">
  {asset_input.jurisdiction} &nbsp;|&nbsp; {asset_input.province} &nbsp;|&nbsp; {asset_input.commodity} &nbsp;|&nbsp; ID: {result.asset_id}
</div>

<!-- DECISION PANEL -->
{decision_panel}

<!-- CRITICAL RISKS -->
{risks_html}

<!-- INVESTMENT DRIVERS -->
{drivers_html}

<!-- MATERIAL UNKNOWNS -->
{intel_items_html}

<!-- DIMENSION DETAIL -->
<h2>Dimension Detail</h2>
<table style="width:100%;border-collapse:collapse;">
  {dim_cards}
</table>

<!-- VERDICT -->
<h2>Verdict and Next Action</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:10px;">
  <tr>
    <td style="background:{vc};padding:10px 16px;">
      <div style="font-size:9px;color:rgba(255,255,255,0.6);text-transform:uppercase;letter-spacing:0.4px;">Verdict</div>
      <div style="font-size:16px;font-weight:bold;color:white;margin-top:2px;">{result.verdict}</div>
    </td>
  </tr>
</table>
<div style="font-size:11px;color:#333;line-height:1.55;margin-bottom:10px;">
  {verdict_text.replace(chr(10), "<br>")}
</div>
{floor_html}
<div style="margin-top:10px;padding:10px 13px;background:#f8f8f8;border-left:3px solid {AMBER};">
  <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:3px;">Next Action</div>
  <div style="font-size:11px;color:#222;font-weight:bold;">{result.next_action}</div>
</div>

<!-- EVIDENCE SUMMARY -->
<h2>Evidence Summary</h2>
<div style="font-size:11px;color:#444;line-height:1.55;margin-bottom:10px;">{ev_summary}</div>

<!-- EVIDENCE REFERENCE -->
<h2>Evidence Reference</h2>
<table style="width:100%;font-size:10px;color:#666;border-collapse:collapse;">
  <tr><td style="padding:3px 0;width:36%;"><strong>Methodology</strong></td><td>{result.methodology_version}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Rules Version</strong></td><td>{result.rules_version}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Generated</strong></td><td>{gen}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Asset ID</strong></td><td>{result.asset_id}</td></tr>
  <tr><td style="padding:3px 0;"><strong>Evidence Completeness</strong></td><td>{ec}/100. Computed from retrieved vs defaulted fields. Reflects evidence coverage, not asset quality.</td></tr>
  <tr><td style="padding:3px 0;"><strong>Scoring Engine</strong></td><td>Deterministic rules engine. No language model in scoring path. Identical inputs always produce identical scores, verdicts and floor rule outcomes.</td></tr>
  <tr><td style="padding:3px 0;"><strong>Intelligence Engine</strong></td><td>SEAM Intelligence Engine, constrained to the evidence envelope. Cannot alter scores, verdicts or floor rules.</td></tr>
  <tr><td style="padding:3px 0;"><strong>Data Sources</strong></td><td>EITI, Fraser Institute, World Bank WGI, USGS, ASX/TSX/AIM filings, Ministry of Mines, cadastre portals</td></tr>
</table>

<div style="margin-top:16px;padding-top:8px;border-top:1px solid #eee;font-size:9px;color:#bbb;text-align:center;">
  For informational purposes only. Not investment, legal or financial advice. Not a substitute for independent due diligence.
  akinmade.co.uk &nbsp;|&nbsp; CONFIDENTIAL
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
