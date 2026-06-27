"""
SEAM PDF Report Generator
Typography-first. Breathing room. Navy / White / Gold / Red only.
Decision ID. Assessment Integrity panel. Evidence bar graphic.
"""

from weasyprint import HTML
from engine.scoring import ScoringResult
from datetime import datetime
import os
import hashlib

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

IMPACT_MAP = {
    "D1": ("High",   "25%"),
    "D2": ("High",   "20%"),
    "D3": ("High",   "20%"),
    "D4": ("Medium", "15%"),
    "D5": ("Medium", "12%"),
    "D6": ("Low",    "8%"),
}


def decision_id(result: ScoringResult) -> str:
    h = hashlib.sha256(f"{result.asset_id}{result.generated_at}".encode()).hexdigest()[:6].upper()
    year = result.generated_at[:4]
    return f"SEAM-{year}-{result.jurisdiction_code if hasattr(result, 'jurisdiction_code') else result.asset_id[:3]}-{h}"


def evidence_bar_svg(retrieved: int, total: int, width: int = 320) -> str:
    """Single horizontal evidence bar. Navy/gold only."""
    pct = retrieved / total if total > 0 else 0
    filled = int(pct * width)
    defaulted = total - retrieved
    pct_label = f"{round(pct * 100)}%" if pct > 0 else "None retrieved"
    return f"""
    <div style="margin:16px 0 8px 0;">
      <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Evidence Coverage</div>
      <div style="background:#e8e8e8;border-radius:3px;height:12px;width:{width}px;">
        <div style="background:{AMBER};border-radius:3px;height:12px;width:{filled}px;"></div>
      </div>
      <div style="display:flex;margin-top:5px;font-size:10px;color:#555;">
        <span style="margin-right:16px;"><strong style="color:{NAVY};">{total}</strong> assessed</span>
        <span style="margin-right:16px;"><strong style="color:{AMBER if retrieved > 0 else '#aaa'};">{retrieved}</strong> retrieved</span>
        <span><strong style="color:#aaa;">{defaulted}</strong> defaulted</span>
      </div>
    </div>"""


def score_bar(score: float, width: int = 140, dark: bool = True) -> str:
    filled = max(0, int((score / 100) * width))
    bg = "#2a3f55" if dark else "#e0e0e0"
    return (
        f'<div style="background:{bg};border-radius:2px;height:5px;width:{width}px;margin-top:5px;">'
        f'<div style="background:{AMBER};border-radius:2px;height:5px;width:{filled}px;"></div>'
        f'</div>'
    )


def build_html(result: ScoringResult, intel: dict, asset_input) -> str:
    vc_colour = VERDICT_COLOURS.get(result.verdict, "#333")
    gen       = datetime.fromisoformat(result.generated_at).strftime("%d %B %Y, %H:%M UTC")
    ec        = result.evidence_completeness_score
    did       = decision_id(result)

    inv_dec        = intel.get("investment_decision", {})
    v_conf         = inv_dec.get("verdict_confidence", "Low")
    cr_count       = len(result.floor_rules_triggered)
    critical_risks = intel.get("critical_risks", [])
    drivers        = intel.get("investment_drivers", {})
    ev_summary     = intel.get("evidence_summary", "")
    commodity_ctx   = intel.get("commodity_context", {})
    bc              = intel.get("bankability_constraints", {})
    benchmarks      = intel.get("_benchmarks", {})  # injected by app.py
    intel_items    = intel.get("investor_intelligence", [])
    verdict_text   = intel.get("verdict_section", "")
    ic_sum         = intel.get("ic_summary", {})
    priority_acts  = intel.get("priority_actions", [])
    remediation    = intel.get("remediation", {})

    # Field counts
    total_fields = 19
    retrieved_count = sum([
        asset_input.fraser_investment_attractiveness is not None,
        asset_input.wb_rule_of_law_percentile is not None,
        asset_input.wb_regulatory_quality_percentile is not None,
        asset_input.eiti_implementation_status != "non-implementing",
        asset_input.eiti_compliant_country is True,
        asset_input.eiti_payment_disclosure_quality is not None,
        asset_input.beneficial_ownership_disclosure != "none",
        asset_input.resource_estimate_standard != "none",
        asset_input.reserve_classification != "none",
        asset_input.production_data_availability != "none",
        bool(asset_input.commodity and "retrieval required" not in asset_input.commodity.lower()),
        asset_input.licence_holder_status != "other",
        asset_input.locas_filing_status != "not_filed",
        asset_input.power_supply != "none",
        asset_input.road_access != "none",
        asset_input.water_supply != "none",
        asset_input.port_distance_km is not None,
        asset_input.active_dfi_engagement != "none",
        asset_input.listed_vehicle != "unlisted",
    ])

    # Evidence coverage label
    if retrieved_count == 0:
        coverage_label = "None retrieved"
    elif ec < 20:
        coverage_label = "Very low"
    elif ec < 50:
        coverage_label = "Partial"
    elif ec < 80:
        coverage_label = "Moderate"
    else:
        coverage_label = "High"

    # --- Decision panel (4 cells, navy/gold/red only) ---
    decision_panel = f"""
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
      <tr>
        <td style="background:{NAVY};padding:20px 22px;width:25%;vertical-align:top;border-right:1px solid #2a3f55;">
          <div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Investment Readiness</div>
          <div style="font-size:46px;font-weight:bold;color:{AMBER};line-height:1;">{result.investment_readiness_score}</div>
          <div style="font-size:10px;color:#555;margin-top:4px;">out of 100</div>
          {score_bar(result.investment_readiness_score, 120, dark=True)}
        </td>
        <td style="background:#0f1e2e;padding:20px 22px;width:25%;vertical-align:top;border-right:1px solid #2a3f55;">
          <div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Evidence Completeness</div>
          <div style="font-size:46px;font-weight:bold;color:#7eb8d4;line-height:1;">{ec}</div>
          <div style="font-size:10px;color:#555;margin-top:4px;">{coverage_label}</div>
          {score_bar(ec, 120, dark=True)}
        </td>
        <td style="background:{vc_colour};padding:20px 22px;width:28%;vertical-align:top;border-right:1px solid rgba(255,255,255,0.1);">
          <div style="font-size:9px;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Verdict</div>
          <div style="font-size:26px;font-weight:bold;color:{WHITE};line-height:1.1;">{result.verdict}</div>
          <div style="margin-top:10px;font-size:10px;color:rgba(255,255,255,0.6);">Evidence Confidence</div>
          <div style="font-size:13px;font-weight:bold;color:{WHITE};margin-top:2px;">{v_conf}</div>
        </td>
        <td style="background:#f9f6f0;padding:20px 22px;width:22%;vertical-align:top;">
          <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px;">At a Glance</div>
          <div style="margin-bottom:7px;">
            <div style="font-size:10px;color:#888;">Critical risks</div>
            <div style="font-size:18px;font-weight:bold;color:{RED if cr_count > 0 else NAVY};">{cr_count}</div>
          </div>
          <div style="margin-bottom:7px;">
            <div style="font-size:10px;color:#888;">Evidence fields</div>
            <div style="font-size:13px;font-weight:bold;color:{NAVY};">{retrieved_count} / {total_fields}</div>
          </div>
          <div style="margin-top:10px;font-size:10px;font-weight:bold;color:{vc_colour};line-height:1.3;">{result.next_action.split('.')[0]}.</div>
        </td>
      </tr>
    </table>"""

    # --- Evidence bar ---
    ev_bar = evidence_bar_svg(retrieved_count, total_fields)

    # --- IC Summary panel ---
    def _risk_colour(level):
        return {"Low": "#1A7A3A", "Strong": "#1A7A3A", "Ready": "#1A7A3A",
                "Medium": "#B8860B", "Moderate": "#B8860B", "Conditional": "#B8860B",
                "High": "#C65C00", "Weak": "#C65C00",
                "Critical": "#CC0000", "Not Ready": "#CC0000"}.get(level, "#888")

    def _risk_cell(label, value):
        col = _risk_colour(value)
        return (
            f'<td style="padding:10px 14px;border-right:1px solid #2a3f55;vertical-align:top;">'
            f'<div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:5px;">{label}</div>'
            f'<div style="font-size:13px;font-weight:bold;color:{col};">{value or "—"}</div>'
            f'</td>'
        )

    ic_panel = ""
    if ic_sum:
        phase_rec = ic_sum.get("phase_recommendation", "")
        rationale = ic_sum.get("rationale", "")
        ttd       = ic_sum.get("time_to_decision", "")
        phase_col = vc_colour

        risk_cells = (
            _risk_cell("Investment Strength", ic_sum.get("investment_strength", "")) +
            _risk_cell("Operational Risk",    ic_sum.get("operational_risk", "")) +
            _risk_cell("Governance Risk",     ic_sum.get("governance_risk", "")) +
            _risk_cell("Political Risk",      ic_sum.get("political_risk", "")) +
            f'<td style="padding:10px 14px;vertical-align:top;">'
            f'<div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:5px;">Capital Readiness</div>'
            f'<div style="font-size:13px;font-weight:bold;color:{_risk_colour(ic_sum.get("capital_readiness",""))};">{ic_sum.get("capital_readiness","—")}</div>'
            f'</td>'
        )

        ic_panel = f"""
    <div style="margin-bottom:20px;border:1.5px solid {NAVY};border-radius:3px;overflow:hidden;">
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="background:{NAVY};padding:12px 18px;width:60%;vertical-align:top;">
            <div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:6px;">Investment Committee View</div>
            <div style="font-size:15px;font-weight:bold;color:{AMBER};line-height:1.2;margin-bottom:8px;">{phase_rec}</div>
            <div style="font-size:10px;color:#bbb;line-height:1.5;">{rationale}</div>
          </td>
          <td style="background:#0f1e2e;padding:12px 18px;width:40%;vertical-align:top;">
            <div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:6px;">Time to Investment Decision</div>
            <div style="font-size:15px;font-weight:bold;color:{WHITE};">{ttd}</div>
            <div style="font-size:9px;color:#666;margin-top:10px;text-transform:uppercase;letter-spacing:0.5px;">Evidence Confidence</div>
            <div style="font-size:13px;font-weight:bold;color:{WHITE};margin-top:3px;">{v_conf}</div>
          </td>
        </tr>
        <tr style="background:#f4f4f4;">
          {risk_cells}
        </tr>
      </table>
    </div>"""

    # --- Critical risks ---
    risks_html = ""
    if critical_risks:
        rows = "".join(
            f'<div style="display:flex;align-items:flex-start;margin-bottom:10px;">'
            f'<div style="min-width:20px;height:20px;background:{RED};border-radius:50%;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:9px;font-weight:bold;color:{WHITE};margin-right:10px;margin-top:1px;flex-shrink:0;">{i}</div>'
            f'<div style="font-size:11px;color:#333;line-height:1.5;">{r}</div>'
            f'</div>'
            for i, r in enumerate(critical_risks, 1)
        )
        risks_html = f"""
        <div style="margin-bottom:24px;">
          <div style="font-size:10px;font-weight:bold;color:{RED};text-transform:uppercase;letter-spacing:0.5px;border-bottom:1.5px solid {RED};padding-bottom:4px;margin-bottom:12px;">Exclusion Conditions</div>
          {rows}
        </div>"""

    # --- Investment Drivers (hierarchy: negative dominates) ---
    def driver_list(items, col, size="11px", weight="normal"):
        if not items:
            return '<div style="font-size:10px;color:#aaa;font-style:italic;">None identified</div>'
        return "".join(
            f'<div style="display:flex;align-items:flex-start;margin-bottom:6px;">'
            f'<div style="min-width:7px;height:7px;background:{col};border-radius:50%;margin-right:8px;margin-top:4px;flex-shrink:0;"></div>'
            f'<div style="font-size:{size};font-weight:{weight};color:#333;line-height:1.4;">{item}</div>'
            f'</div>'
            for item in items
        )

    drivers_html = ""
    if drivers:
        pos_items = drivers.get("positive", [])
        neg_items = drivers.get("negative", [])
        unk_items = drivers.get("unknown", [])
        drivers_html = f"""
        <div style="margin-bottom:24px;">
          <div style="font-size:10px;font-weight:bold;color:{NAVY};text-transform:uppercase;letter-spacing:0.5px;border-bottom:1.5px solid {AMBER};padding-bottom:4px;margin-bottom:14px;">Investment Drivers</div>
          <table style="width:100%;border-collapse:collapse;">
            <tr style="vertical-align:top;">
              <td style="width:40%;padding-right:16px;border-right:1px solid #eee;">
                <div style="font-size:9px;font-weight:bold;color:{RED};text-transform:uppercase;letter-spacing:0.4px;margin-bottom:8px;">Negative</div>
                {driver_list(neg_items, RED, "12px", "bold")}
              </td>
              <td style="width:30%;padding:0 16px;border-right:1px solid #eee;">
                <div style="font-size:9px;font-weight:bold;color:{NAVY};text-transform:uppercase;letter-spacing:0.4px;margin-bottom:8px;">Positive</div>
                {driver_list(pos_items, AMBER, "11px")}
              </td>
              <td style="width:30%;padding-left:16px;">
                <div style="font-size:9px;font-weight:bold;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:8px;">Unknown</div>
                {driver_list(unk_items, "#aaa", "11px")}
              </td>
            </tr>
          </table>
        </div>"""

    # --- Material unknowns ---
    unknowns_html = ""
    if intel_items:
        rows = "".join(
            f'<div style="display:flex;align-items:flex-start;margin-bottom:10px;">'
            f'<div style="min-width:20px;height:20px;background:{NAVY};border-radius:50%;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:9px;font-weight:bold;color:{WHITE};margin-right:10px;margin-top:1px;flex-shrink:0;">{idx}</div>'
            f'<div style="font-size:11px;color:#444;line-height:1.5;">{f}</div>'
            f'</div>'
            for idx, f in enumerate(intel_items, 1)
        )
        unknowns_html = f"""
        <div style="margin-bottom:24px;">
          <div style="font-size:10px;font-weight:bold;color:{NAVY};text-transform:uppercase;letter-spacing:0.5px;border-bottom:1.5px solid {AMBER};padding-bottom:4px;margin-bottom:12px;">Material Unknowns</div>
          {rows}
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
            impact, _ = IMPACT_MAP.get(d.code, ("Low", ""))

            conf_col   = {NAVY: NAVY, "High": "#1A7A3A", "Medium": "#B8860B", "Low": RED}.get(conf, "#888")
            impact_col = {"High": RED, "Medium": AMBER, "Low": "#888"}.get(impact, "#888")

            gaps_html = "".join(
                f'<div style="font-size:10px;color:{RED};margin-top:3px;">&#9888; {g}</div>'
                for g in d.data_gaps
            )

            formatted = ""
            for line in finding.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.lower().startswith("gap:"):
                    formatted += f'<div style="font-size:10px;color:{RED};margin-top:3px;">&#9888; {line[4:].strip()}</div>'
                else:
                    formatted += f'<div style="font-size:10px;color:#444;margin-top:4px;line-height:1.45;">{line}</div>'

            row += f"""
            <td style="width:50%;padding:4px;">
              <div style="border:1px solid #e8e8e8;border-radius:3px;padding:12px 14px;background:{WHITE};">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px;">
                  <div>
                    <span style="font-size:11px;font-weight:bold;color:{NAVY};">{d.code}</span>
                    <span style="font-size:10px;color:#555;margin-left:5px;">{d.name}</span>
                  </div>
                  <div style="text-align:right;">
                    <span style="font-size:19px;font-weight:bold;color:{NAVY};">{d.adjusted_score:.0f}<span style="font-size:9px;color:#aaa;font-weight:normal;">/100</span></span>
                    <div style="font-size:9px;color:#aaa;margin-top:1px;">±3 pts sensitivity</div>
                  </div>
                </div>
                {score_bar(d.adjusted_score, 160, dark=False)}
                <div style="display:flex;gap:10px;margin-top:5px;margin-bottom:6px;">
                  <span style="font-size:9px;color:{conf_col};">Evidence: {conf}</span>
                  <span style="font-size:9px;color:{impact_col};">Impact: {impact}</span>
                </div>
                {gaps_html}
                {formatted}
              </div>
            </td>"""

        if len(dims[i:i+2]) == 1:
            row += '<td style="width:50%;padding:4px;"></td>'
        dim_cards += f'<tr style="vertical-align:top;">{row}</tr>'

    # --- Floor rules ---
    floor_html = ""
    if result.floor_rules_triggered:
        rows = "".join(
            f'<tr>'
            f'<td style="padding:5px 12px;font-size:10px;font-weight:bold;color:{RED};white-space:nowrap;">{r["code"]}</td>'
            f'<td style="padding:5px 12px;font-size:10px;color:#333;">{r["description"]}</td>'
            f'</tr>'
            for r in result.floor_rules_triggered
        )
        floor_html = f"""
        <div style="margin-top:14px;">
          <div style="font-size:9px;font-weight:bold;color:{RED};text-transform:uppercase;letter-spacing:0.4px;margin-bottom:6px;">Exclusion Conditions Detail</div>
          <table style="width:100%;border-collapse:collapse;background:#fff8f8;border:1px solid #f0c0c0;">
            {rows}
          </table>
        </div>"""

    # --- Assessment Integrity panel ---
    integrity_html = f"""
    <div style="margin-top:20px;padding:14px 18px;background:{NAVY};border-radius:3px;">
      <div style="font-size:9px;color:#666;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;">Assessment Integrity</div>
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          {''.join(
            f'<td style="width:25%;padding:0 8px;text-align:center;">'
            f'<div style="font-size:16px;color:{AMBER};">&#10003;</div>'
            f'<div style="font-size:9px;color:#999;margin-top:3px;">{label}</div>'
            f'</td>'
            for label in ['Deterministic', 'Evidence Referenced', 'Replayable', 'Version Locked']
          )}
        </tr>
      </table>
    </div>"""

    # --- Commodity Context panel ---
    def _outlook_colour(outlook):
        return {"Bullish": "#1A7A3A", "Neutral": "#B8860B", "Bearish": "#CC0000"}.get(outlook, "#888")

    def _trend_arrow(trend):
        return {"Rising": "&#9650;", "Stable": "&#9654;", "Falling": "&#9660;"}.get(trend, "")

    commodity_panel = ""
    if commodity_ctx and commodity_ctx.get("commodity") and commodity_ctx.get("commodity") != "Unknown":
        c = commodity_ctx
        outlook_col = _outlook_colour(c.get("outlook", "Neutral"))
        trend_arrow = _trend_arrow(c.get("price_trend_12m", "Stable"))
        crit_html = ""
        if c.get("critical_mineral"):
            lists = c.get("critical_mineral_lists", [])
            crit_html = f'''<span style="display:inline-block;padding:1px 7px;border-radius:8px;background:{AMBER};color:white;font-size:9px;font-weight:bold;margin-left:6px;">Critical Mineral</span>'''
            if lists:
                crit_html += f'''<span style="font-size:9px;color:#888;margin-left:6px;">{", ".join(lists)}</span>'''
        lobito_html = ""
        if c.get("lobito_corridor_relevant"):
            lobito_html = '''<span style="display:inline-block;padding:1px 7px;border-radius:8px;background:#1A5FA8;color:white;font-size:9px;font-weight:bold;margin-left:6px;">Lobito Corridor</span>'''

        commodity_panel = f'''
        <h2>Commodity Context</h2>
        <table style="width:100%;border-collapse:collapse;background:#f9f6f0;border:1px solid #e8e0d0;border-radius:3px;">
          <tr>
            <td style="padding:12px 16px;width:25%;border-right:1px solid #e8e0d0;vertical-align:middle;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:4px;">Commodity</div>
              <div style="font-size:16px;font-weight:bold;color:{NAVY};">{c.get("commodity","")}</div>
              {crit_html}{lobito_html}
            </td>
            <td style="padding:12px 16px;width:20%;border-right:1px solid #e8e0d0;vertical-align:middle;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:4px;">Outlook</div>
              <div style="font-size:14px;font-weight:bold;color:{outlook_col};">{c.get("outlook","")}</div>
              <div style="font-size:9px;color:#888;margin-top:2px;">{trend_arrow} {c.get("price_trend_12m","")}</div>
            </td>
            <td style="padding:12px 16px;vertical-align:middle;">
              <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:4px;">Context</div>
              <div style="font-size:10px;color:#333;line-height:1.5;">{c.get("outlook_rationale","")}</div>
              <div style="font-size:10px;color:#555;margin-top:4px;">{c.get("demand_driver","")}</div>
            </td>
          </tr>
        </table>
        <div style="font-size:9px;color:#aaa;margin-top:4px;font-style:italic;">Commodity context is provided for reference only. It does not affect the Investment Readiness Score or Verdict.</div>
        '''

    # --- Bankability Constraints panel ---
    def _bc_colour(val, good_vals, bad_vals):
        if val in good_vals: return "#1A7A3A"
        if val in bad_vals:  return "#CC0000"
        return "#B8860B"

    bc_html = ""
    if bc and bc.get("constraint_summary") and bc.get("constraint_summary") != "Live in Streamlit":
        dfi_col = {"Ready": "#1A7A3A", "Conditional": "#B8860B", "Not Ready": "#CC0000"}.get(bc.get("dfi_readiness",""), "#888")

        def _flag(val, good, bad):
            col = _bc_colour(val, good, bad)
            return f'<span style="font-size:10px;font-weight:bold;color:{col};">{val}</span>'

        bc_html = f"""
        <h2>Bankability Constraints</h2>
        <table style="width:100%;border-collapse:collapse;background:#f9f9f9;border:1px solid #e8e8e8;">
          <tr style="background:{NAVY};">
            <th style="padding:6px 12px;color:white;font-size:9px;text-align:left;text-transform:uppercase;letter-spacing:0.4px;">Constraint</th>
            <th style="padding:6px 12px;color:white;font-size:9px;text-align:left;text-transform:uppercase;letter-spacing:0.4px;">Status</th>
          </tr>
          <tr><td style="padding:6px 12px;font-size:10px;color:#555;border-bottom:1px solid #eee;">Environmental Permit</td>
              <td style="padding:6px 12px;border-bottom:1px solid #eee;">{_flag(bc.get("environmental_permit","Unknown"),["Permitted"],["Not Filed"])}</td></tr>
          <tr><td style="padding:6px 12px;font-size:10px;color:#555;border-bottom:1px solid #eee;">ESIA on Record</td>
              <td style="padding:6px 12px;border-bottom:1px solid #eee;">{_flag("Yes" if bc.get("esia_on_record") else "No",["Yes"],["No"])}</td></tr>
          <tr><td style="padding:6px 12px;font-size:10px;color:#555;border-bottom:1px solid #eee;">Community Consultation</td>
              <td style="padding:6px 12px;border-bottom:1px solid #eee;">{_flag(bc.get("community_consultation","None"),["Documented"],["None"])}</td></tr>
          <tr><td style="padding:6px 12px;font-size:10px;color:#555;border-bottom:1px solid #eee;">Social Licence Disputes</td>
              <td style="padding:6px 12px;border-bottom:1px solid #eee;">{_flag("Active" if bc.get("social_licence_disputes") else "None identified",["None identified"],["Active"])}</td></tr>
          <tr><td style="padding:6px 12px;font-size:10px;color:#555;">Water Licence</td>
              <td style="padding:6px 12px;">{_flag(bc.get("water_licence","Unknown"),["Permitted"],["Not Filed"])}</td></tr>
        </table>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;">
          <div style="font-size:10px;color:#444;">{bc.get("constraint_summary","")}</div>
          <div style="font-size:10px;font-weight:bold;color:{dfi_col};">DFI Readiness: {bc.get("dfi_readiness","")}</div>
        </div>
        <div style="font-size:9px;color:#aaa;margin-top:3px;font-style:italic;">Bankability constraints reflect public evidence only. They do not affect the Investment Readiness Score.</div>
        """

    # --- Benchmarking panel ---
    benchmark_html = ""
    if benchmarks and not benchmarks.get("insufficient_data"):
        asset_score = benchmarks.get("asset_score", result.investment_readiness_score)
        glob  = benchmarks.get("global")
        jur   = benchmarks.get("jurisdiction")
        com   = benchmarks.get("commodity")

        def _bench_bar(score, avg, width=200):
            s_x = int((score/100)*width)
            a_x = int((avg/100)*width) if avg else 0
            return (
                f'<div style="position:relative;background:#e8e8e8;border-radius:2px;height:8px;width:{width}px;margin-top:3px;">' +
                f'<div style="background:{AMBER};border-radius:2px;height:8px;width:{s_x}px;"></div>' +
                (f'<div style="position:absolute;top:-2px;left:{a_x}px;width:2px;height:12px;background:{NAVY};"></div>' if avg else "") +
                '</div>'
            )

        rows = ""
        if glob:
            rows += f'''<tr>
              <td style="padding:5px 10px;font-size:10px;color:#555;width:28%;">All assets</td>
              <td style="padding:5px 10px;font-size:11px;font-weight:bold;color:{NAVY};width:12%;">{asset_score}</td>
              <td style="padding:5px 10px;font-size:10px;color:#888;width:12%;">Avg: {glob["average"]}</td>
              <td style="padding:5px 10px;font-size:10px;color:#888;width:12%;">Top Q: {glob["top_quartile"]}</td>
              <td style="padding:5px 10px;">{_bench_bar(asset_score, glob["average"])}</td>
            </tr>'''
        if jur:
            rows += f'''<tr>
              <td style="padding:5px 10px;font-size:10px;color:#555;">{asset_input.jurisdiction}</td>
              <td style="padding:5px 10px;font-size:11px;font-weight:bold;color:{NAVY};">{asset_score}</td>
              <td style="padding:5px 10px;font-size:10px;color:#888;">Avg: {jur["average"]}</td>
              <td style="padding:5px 10px;font-size:10px;color:#888;">Top Q: {jur["top_quartile"]}</td>
              <td style="padding:5px 10px;">{_bench_bar(asset_score, jur["average"])}</td>
            </tr>'''
        if com:
            rows += f'''<tr>
              <td style="padding:5px 10px;font-size:10px;color:#555;">{asset_input.commodity}</td>
              <td style="padding:5px 10px;font-size:11px;font-weight:bold;color:{NAVY};">{asset_score}</td>
              <td style="padding:5px 10px;font-size:10px;color:#888;">Avg: {com["average"]}</td>
              <td style="padding:5px 10px;font-size:10px;color:#888;">Top Q: {com["top_quartile"]}</td>
              <td style="padding:5px 10px;">{_bench_bar(asset_score, com["average"])}</td>
            </tr>'''

        if rows:
            benchmark_html = f"""
        <h2>Benchmark</h2>
        <div style="font-size:9px;color:#888;margin-bottom:6px;">Navy marker = average. Scored from {glob["count"] if glob else "?"} assessments in this session.</div>
        <table style="width:100%;border-collapse:collapse;border:1px solid #e8e8e8;">
          <tr style="background:{NAVY};">
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Group</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">This Asset</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Average</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Top Quartile</th>
            <th style="padding:5px 10px;color:white;font-size:9px;text-align:left;">Position</th>
          </tr>
          {rows}
        </table>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-center {{
      content: "{did}  |  CONFIDENTIAL  |  Page " counter(page) " of " counter(pages);
      font-family: Arial, sans-serif;
      font-size: 8px;
      color: #bbb;
    }}
  }}
  body {{
    font-family: Arial, sans-serif;
    font-size: 11px;
    color: #222;
    margin: 0;
    padding: 0;
    line-height: 1.5;
  }}
  h2 {{
    font-size: 10px;
    color: {NAVY};
    margin: 24px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    border-bottom: 1.5px solid {AMBER};
    padding-bottom: 4px;
  }}
</style>
</head>
<body>

<!-- HEADER -->
<table style="width:100%;margin-bottom:14px;">
  <tr>
    <td style="vertical-align:middle;">
      <span style="font-size:24px;font-weight:bold;color:{AMBER};letter-spacing:1.5px;">SEAM</span>
      <span style="font-size:9px;color:{NAVY};letter-spacing:0.4px;margin-left:10px;vertical-align:middle;">STRUCTURED EVIDENCE FOR AFRICAN MINING</span>
    </td>
    <td style="text-align:right;vertical-align:middle;">
      <div style="font-size:9px;color:#888;">Investment Readiness Report</div>
      <div style="font-size:9px;color:#888;">{gen}</div>
      <div style="font-size:9px;color:#888;">{result.methodology_version} &nbsp;|&nbsp; {result.rules_version}</div>
    </td>
  </tr>
</table>
<div style="height:2px;background:{NAVY};margin-bottom:16px;"></div>

<!-- DECISION ID + ASSET -->
<table style="width:100%;margin-bottom:16px;">
  <tr>
    <td style="vertical-align:bottom;">
      <div style="font-size:17px;font-weight:bold;color:{NAVY};margin-bottom:3px;">{result.asset_name}</div>
      <div style="font-size:9px;color:#888;">{asset_input.jurisdiction} &nbsp;|&nbsp; {asset_input.province} &nbsp;|&nbsp; {asset_input.commodity}</div>
    </td>
    <td style="text-align:right;vertical-align:bottom;">
      <div style="font-size:9px;color:#aaa;text-transform:uppercase;letter-spacing:0.4px;">Decision ID</div>
      <div style="font-size:11px;font-weight:bold;color:{NAVY};font-family:monospace;">{did}</div>
      <div style="font-size:9px;color:#888;margin-top:3px;">See Evidence Book for full provenance register</div>
    </td>
  </tr>
</table>

<!-- IC SUMMARY -->
{ic_panel}

<!-- DECISION PANEL -->
{decision_panel}

<!-- EVIDENCE BAR -->
{ev_bar}

<!-- EXCLUSION CONDITIONS -->
{risks_html}

<!-- INVESTMENT DRIVERS -->
{drivers_html}

<!-- MATERIAL UNKNOWNS -->
{unknowns_html}

<!-- DIMENSION DETAIL -->
<h2>Dimension Detail</h2>
<table style="width:100%;border-collapse:collapse;">
  {dim_cards}
</table>

<!-- VERDICT -->
<h2>Verdict and Next Action</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:14px;">
  <tr>
    <td style="background:{vc_colour};padding:14px 20px;width:60%;">
      <div style="font-size:9px;color:rgba(255,255,255,0.55);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Verdict</div>
      <div style="font-size:20px;font-weight:bold;color:{WHITE};">{result.verdict}</div>
    </td>
    <td style="background:#f4f4f4;padding:14px 20px;width:40%;vertical-align:middle;">
      {''.join([
        f'<div style="margin-bottom:4px;"><span style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;">Expected score after remediation</span></div>'
        f'<div style="font-size:20px;font-weight:bold;color:{NAVY};">{remediation.get("expected_score_after","—")}<span style="font-size:9px;color:#aaa;font-weight:normal;"> / 100</span></div>'
        f'<div style="font-size:10px;color:#888;margin-top:4px;">Sensitivity: ±{remediation.get("score_sensitivity", 3)} pts &nbsp;|&nbsp; Effort: {remediation.get("estimated_effort","—")} &nbsp;|&nbsp; Delay: {remediation.get("estimated_diligence_delay","—")}</div>'
      ]) if remediation else ''}
    </td>
  </tr>
</table>
<div style="font-size:11px;color:#333;line-height:1.6;margin-bottom:12px;">{verdict_text.replace(chr(10), "<br>")}</div>

{''.join([
  f'<div style="margin-bottom:20px;">'
  f'<div style="font-size:10px;font-weight:bold;color:{NAVY};text-transform:uppercase;letter-spacing:0.5px;border-bottom:1.5px solid {AMBER};padding-bottom:4px;margin-bottom:12px;">Priority Actions Before Due Diligence</div>'
  + ''.join([
    f'<div style="display:flex;align-items:flex-start;margin-bottom:10px;">'
    f'<div style="min-width:22px;height:22px;background:{NAVY};border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:bold;color:{WHITE};margin-right:10px;flex-shrink:0;">{a["rank"]}</div>'
    f'<div style="flex:1;">'
    f'<div style="font-size:11px;font-weight:bold;color:#222;">{a["action"]}</div>'
    f'<div style="font-size:9px;color:#888;margin-top:2px;">{a.get("dimension","")} &nbsp;|&nbsp; Effort: {a.get("effort","—")} &nbsp;|&nbsp; Est. delay: {a.get("diligence_delay_days","—")} days</div>'
    f'</div></div>'
    for a in priority_acts
  ]) +
  f'</div>'
]) if priority_acts else ''}

{floor_html}
<div style="margin-top:14px;padding:12px 16px;background:#f8f8f8;border-left:3px solid {AMBER};">
  <div style="font-size:9px;color:#888;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:4px;">Next Action</div>
  <div style="font-size:12px;font-weight:bold;color:{NAVY};">{result.next_action}</div>
</div>

<!-- COMMODITY CONTEXT -->
{commodity_panel}

{bc_html}

{benchmark_html}

<!-- EVIDENCE SUMMARY -->
<h2>Evidence Summary</h2>
<div style="font-size:11px;color:#444;line-height:1.6;margin-bottom:12px;">{ev_summary}</div>

<!-- EVIDENCE REFERENCE -->
<h2>Evidence Reference</h2>
<table style="width:100%;font-size:10px;color:#666;border-collapse:collapse;">
  <tr><td style="padding:4px 0;width:36%;color:#888;"><strong>Decision ID</strong></td><td style="font-family:monospace;">{did}</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Methodology</strong></td><td>{result.methodology_version}</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Rules Version</strong></td><td>{result.rules_version}</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Generated</strong></td><td>{gen}</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Evidence Completeness</strong></td><td>{ec}/100 ({coverage_label}). {retrieved_count} of {total_fields} key fields retrieved from public sources.</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Scoring Engine</strong></td><td>Deterministic rules engine. No language model in scoring path. Identical inputs always produce identical scores, verdicts and floor rule outcomes.</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Intelligence Engine</strong></td><td>SEAM Intelligence Engine, constrained to the evidence envelope. Cannot alter scores, verdicts or floor rules.</td></tr>
  <tr><td style="padding:4px 0;color:#888;"><strong>Data Sources</strong></td><td>EITI, Fraser Institute, World Bank WGI, USGS, ASX/TSX/AIM/LSE filings, Ministry of Mines publications, government cadastre portals, S&P Capital IQ (public), Refinitiv Eikon (public), ICIJ Offshore Leaks</td></tr>
</table>

{integrity_html}

<div style="margin-top:20px;padding-top:10px;border-top:1px solid #eee;font-size:9px;color:#ccc;text-align:center;">
  For informational purposes only. Not investment, legal or financial advice. Not a substitute for independent due diligence. &nbsp; akinmade.co.uk &nbsp;|&nbsp; CONFIDENTIAL
</div>

</body>
</html>"""

    return html


def generate_pdf(result: ScoringResult, intel: dict, asset_input, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    html = build_html(result, intel, asset_input)
    safe_name = result.asset_id.replace("/", "-")
    output_path = os.path.join(output_dir, f"{safe_name}_SEAM_Report.pdf")
    HTML(string=html).write_pdf(output_path)
    return output_path



