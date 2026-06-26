"""
SEAM — Structured Evidence for African Mining
Streamlit Front Door  |  Sprint 3

User enters an asset name and jurisdiction.
SEAM retrieves public data, scores the asset, generates the report.
"""

import streamlit as st
import json
import os
import sys
import base64
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.scoring import score_asset
from engine.intelligence import generate_intelligence
from engine.retrieval import retrieve_asset_data
from engine.report import generate_pdf
from data.phase1_assets import ALL_ASSETS

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SEAM — Structured Evidence for African Mining",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

AMBER = "#C8962E"
NAVY = "#0B1929"

VERDICT_COLOURS = {
    "PROCEED": "#1A7A3A",
    "PROCEED WITH CONDITIONS": "#B8860B",
    "MONITOR": "#1A5FA8",
    "CAUTION": "#C65C00",
    "AVOID": "#CC0000",
}

VERDICT_BG = {
    "PROCEED": "#e8f5e9",
    "PROCEED WITH CONDITIONS": "#fffde7",
    "MONITOR": "#e3f2fd",
    "CAUTION": "#fff3e0",
    "AVOID": "#ffebee",
}

# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', Arial, sans-serif;
  }}

  .seam-header {{
    background: {NAVY};
    padding: 24px 32px;
    margin: -1rem -1rem 2rem -1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .seam-logo {{
    font-size: 32px;
    font-weight: 700;
    color: {AMBER};
    letter-spacing: 2px;
  }}
  .seam-tagline {{
    font-size: 12px;
    color: #aaa;
    letter-spacing: 1px;
    margin-top: 2px;
  }}
  .seam-version {{
    font-size: 11px;
    color: #666;
    text-align: right;
  }}

  .score-banner {{
    display: flex;
    margin-bottom: 20px;
    border-radius: 4px;
    overflow: hidden;
  }}
  .score-left {{
    background: {NAVY};
    padding: 20px 28px;
    flex: 1;
  }}
  .score-number {{
    font-size: 56px;
    font-weight: 700;
    color: {AMBER};
    line-height: 1;
  }}
  .score-label {{
    font-size: 11px;
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }}
  .score-denom {{
    font-size: 18px;
    color: #888;
  }}

  .dim-row {{
    display: flex;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
    gap: 12px;
  }}
  .dim-code {{
    font-weight: 700;
    color: {NAVY};
    width: 36px;
    font-size: 13px;
    flex-shrink: 0;
  }}
  .dim-name {{
    flex: 1;
    font-size: 13px;
    color: #333;
  }}
  .dim-score {{
    font-weight: 700;
    color: {NAVY};
    font-size: 16px;
    width: 48px;
    text-align: right;
    flex-shrink: 0;
  }}
  .dim-bar-bg {{
    width: 100px;
    height: 8px;
    background: #e8e8e8;
    border-radius: 4px;
    flex-shrink: 0;
  }}
  .dim-bar-fill {{
    height: 8px;
    background: {AMBER};
    border-radius: 4px;
  }}

  .intel-item {{
    display: flex;
    align-items: flex-start;
    margin-bottom: 16px;
    gap: 12px;
  }}
  .intel-num {{
    min-width: 28px;
    height: 28px;
    background: {AMBER};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: white;
    font-size: 13px;
    flex-shrink: 0;
  }}
  .intel-text {{
    font-size: 13px;
    color: #333;
    line-height: 1.6;
    padding-top: 3px;
  }}

  .source-row {{
    font-size: 11px;
    color: #666;
    padding: 4px 0;
    border-bottom: 1px solid #f5f5f5;
  }}

  .disclaimer {{
    font-size: 11px;
    color: #aaa;
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid #eee;
    line-height: 1.6;
  }}

  div[data-testid="stButton"] button {{
    background: {AMBER};
    color: white;
    border: none;
    font-weight: 600;
    padding: 10px 28px;
    border-radius: 4px;
    font-size: 14px;
    letter-spacing: 0.3px;
  }}
  div[data-testid="stButton"] button:hover {{
    background: #b07d24;
    color: white;
  }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------

st.markdown(f"""
<div class="seam-header">
  <div>
    <div class="seam-logo">SEAM</div>
    <div class="seam-tagline">STRUCTURED EVIDENCE FOR AFRICAN MINING</div>
  </div>
  <div class="seam-version">
    Methodology SEAM-M-v1.0<br>
    Rules SEAM-R-v1.0<br>
    akinmade.co.uk
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# INTRO
# ---------------------------------------------------------------------------

st.markdown("""
**Before committing capital to African mining due diligence, know what the data actually says.**

Enter an asset name below. SEAM retrieves public data from EITI, Fraser Institute, World Bank,
exchange filings and cadastre portals. The rules engine scores six dimensions deterministically.
Claude writes the analysis. Every number traces to a named public source.
""")

st.markdown("---")

# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------

JURISDICTIONS = [
    "Zambia", "Democratic Republic of Congo", "Botswana", "Ghana",
    "Tanzania", "Namibia", "Guinea", "Zimbabwe", "Mozambique"
]

PRELOADED = {
    "-- Select a pre-loaded asset --": None,
    "Konkola Copper Mines (KCM / CopperTech) — Zambia": "ZMB-001",
    "Mingomba Copper Project (KoBold Metals) — Zambia": "ZMB-002",
    "Lumwana Copper Mine (Barrick Gold) — Zambia": "ZMB-003",
}

col1, col2 = st.columns([2, 1])

with col1:
    mode = st.radio(
        "Assessment mode",
        ["Live retrieval — enter any asset name", "Pre-loaded — use a Phase 1 asset"],
        horizontal=True
    )

if mode == "Live retrieval — enter any asset name":
    col_a, col_b = st.columns([2, 1])
    with col_a:
        asset_name_input = st.text_input(
            "Asset name",
            placeholder="e.g. Chibuluma Copper Mine, Kansanshi Mine, Obuasi Gold Mine..."
        )
    with col_b:
        jurisdiction_input = st.selectbox("Jurisdiction", JURISDICTIONS)
    context_input = st.text_input(
        "Additional context (optional)",
        placeholder="e.g. operator name, ASX ticker, known recent developments..."
    )
    use_preloaded = False

else:
    preloaded_choice = st.selectbox("Select asset", list(PRELOADED.keys()))
    use_preloaded = PRELOADED.get(preloaded_choice)
    asset_name_input = ""
    jurisdiction_input = ""
    context_input = ""

st.markdown("")
run_btn = st.button("Run SEAM Assessment")

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def render_score_banner(score, verdict):
    vc = VERDICT_COLOURS.get(verdict, "#333")
    st.markdown(f"""
    <div class="score-banner">
      <div class="score-left">
        <div class="score-label">Investment Readiness Score</div>
        <div>
          <span class="score-number">{score}</span>
          <span class="score-denom"> / 100</span>
        </div>
      </div>
      <div style="background:{vc};padding:20px 28px;flex:1;display:flex;flex-direction:column;justify-content:center;">
        <div style="font-size:11px;color:rgba(255,255,255,0.7);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Verdict</div>
        <div style="font-size:26px;font-weight:700;color:white;">{verdict}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_dimensions(dimensions, dim_findings):
    for d in dimensions:
        bar_width = int(d.adjusted_score)
        finding = dim_findings.get(d.code, "")
        gaps_html = ""
        if d.data_gaps:
            gaps_html = "".join(
                f'<div style="color:#C65C00;font-size:11px;margin-top:3px;">⚠ {g}</div>'
                for g in d.data_gaps
            )
        adj_html = ""
        if d.adjustments:
            for a in d.adjustments:
                if a.get("adjustment") is not None:
                    sign = "+" if a["adjustment"] > 0 else ""
                    color = "#1A7A3A" if a["adjustment"] > 0 else "#CC0000"
                    adj_html += f'<div style="font-size:11px;color:{color};margin-top:2px;">{sign}{a["adjustment"]}pts: {a["reason"]}</div>'

        st.markdown(f"""
        <div class="dim-row">
          <div class="dim-code">{d.code}</div>
          <div class="dim-name">
            <div><strong>{d.name}</strong> <span style="color:#aaa;font-size:11px;">({int(d.weight*100)}%)</span></div>
            {adj_html}{gaps_html}
            {f'<div style="font-size:12px;color:#555;margin-top:5px;line-height:1.5;">{finding}</div>' if finding else ''}
          </div>
          <div class="dim-score">{d.adjusted_score:.1f}</div>
          <div class="dim-bar-bg">
            <div class="dim-bar-fill" style="width:{bar_width}%;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)


def render_intelligence(items):
    for i, finding in enumerate(items, 1):
        st.markdown(f"""
        <div class="intel-item">
          <div class="intel-num">{i}</div>
          <div class="intel-text">{finding}</div>
        </div>
        """, unsafe_allow_html=True)


def pdf_download_button(pdf_path, asset_id):
    with open(pdf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    filename = f"SEAM_{asset_id}_Report.pdf"
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="background:{AMBER};color:white;padding:10px 24px;border-radius:4px;text-decoration:none;font-weight:600;font-size:14px;">Download PDF Report</a>'
    st.markdown(href, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# RUN ASSESSMENT
# ---------------------------------------------------------------------------

if run_btn:

    # Validate input
    if not use_preloaded and not asset_name_input.strip():
        st.error("Enter an asset name to run a live assessment.")
        st.stop()

    with st.spinner("Running SEAM assessment..."):

        # STEP 1 — Get asset input
        sources_meta = {}
        if use_preloaded:
            asset_input = ALL_ASSETS[use_preloaded]
            st.success(f"Pre-loaded asset: {asset_input.asset_name}")
        else:
            with st.status("Retrieving public data...", expanded=True) as status:
                st.write(f"Searching for: {asset_name_input}, {jurisdiction_input}")
                st.write("Checking EITI, Fraser Institute, World Bank WGI, exchange filings...")
                asset_input, sources_meta = retrieve_asset_data(
                    asset_name_input, jurisdiction_input, context_input
                )
                if sources_meta.get("mock"):
                    st.write("Live retrieval requires ANTHROPIC_API_KEY — using conservative defaults.")
                else:
                    st.write(f"Retrieved {len(sources_meta.get('sources_consulted', []))} data points.")
                status.update(label="Data retrieved.", state="complete")

        # STEP 2 — Score
        with st.status("Running rules engine...", expanded=False) as status:
            result = score_asset(asset_input)
            status.update(label=f"Score: {result.investment_readiness_score}/100 — {result.verdict}", state="complete")

        # STEP 3 — Intelligence layer
        with st.status("Generating intelligence analysis (Claude)...", expanded=False) as status:
            intel = generate_intelligence(result, asset_input)
            status.update(label="Analysis complete.", state="complete")

        # STEP 4 — PDF
        with st.status("Generating PDF report...", expanded=False) as status:
            pdf_path = generate_pdf(result, intel, asset_input, output_dir="/tmp/seam_reports")
            status.update(label="PDF ready.", state="complete")

    # ---------------------------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------------------------

    st.markdown("---")

    # Asset identity
    st.markdown(f"### {result.asset_name}")
    st.caption(f"{asset_input.jurisdiction}  ·  {asset_input.province}  ·  {asset_input.commodity}  ·  {result.asset_id}  ·  {result.generated_at[:10]}")

    # Score banner
    render_score_banner(result.investment_readiness_score, result.verdict)

    # Floor rules
    if result.floor_rules_triggered:
        for rule in result.floor_rules_triggered:
            st.warning(f"**Floor Rule {rule['code']}** — {rule['description']}")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Executive Summary",
        "Dimension Findings",
        "What the Investor Does Not Know",
        "Verdict & Next Action"
    ])

    with tab1:
        st.markdown(intel.get("executive_summary", ""))

    with tab2:
        render_dimensions(result.dimensions, intel.get("dimension_findings", {}))

    with tab3:
        st.markdown(f"""
        <div style="font-size:12px;color:#888;margin-bottom:16px;font-style:italic;">
        Signals, dependencies and anomalies not visible from a surface read of public data.
        Every finding is grounded in the evidence envelope.
        </div>
        """, unsafe_allow_html=True)
        render_intelligence(intel.get("investor_intelligence", []))

    with tab4:
        vc = VERDICT_COLOURS.get(result.verdict, "#333")
        st.markdown(f"""
        <div style="background:{vc};color:white;padding:16px 20px;border-radius:4px;margin-bottom:16px;">
          <div style="font-size:11px;opacity:0.7;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Verdict — {result.methodology_version}</div>
          <div style="font-size:22px;font-weight:700;">{result.verdict}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(intel.get("verdict_section", ""))
        st.markdown(f"""
        <div style="background:#f8f8f8;border-left:4px solid {AMBER};padding:14px 16px;margin-top:16px;border-radius:0 4px 4px 0;">
          <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Next Action</div>
          <div style="font-size:13px;font-weight:600;color:#222;">{result.next_action}</div>
        </div>
        """, unsafe_allow_html=True)

    # Sources retrieved
    if sources_meta.get("sources_consulted"):
        with st.expander("Sources consulted during retrieval"):
            for s in sources_meta["sources_consulted"]:
                st.markdown(f"""
                <div class="source-row">
                  <strong>{s.get('field','')}</strong> — {s.get('source','')}
                  {f" | <a href='{s['url']}' target='_blank'>{s['url'][:60]}...</a>" if s.get('url') else ''}
                  {f" | Found: {s.get('value_found','')}" if s.get('value_found') else ''}
                </div>
                """, unsafe_allow_html=True)

    if sources_meta.get("data_gaps"):
        with st.expander(f"Data gaps ({len(sources_meta['data_gaps'])} fields not found in public sources)"):
            for gap in sources_meta["data_gaps"]:
                st.markdown(f"⚠ {gap}")

    # PDF download
    st.markdown("")
    st.markdown("**Download the full report:**")
    pdf_download_button(pdf_path, result.asset_id)

    # Evidence envelope
    with st.expander("Evidence envelope (JSON)"):
        st.json(result.evidence_envelope)

    st.markdown(f"""
    <div class="disclaimer">
    SEAM Investment Readiness Reports are produced for informational purposes only. They do not constitute investment advice, legal advice or financial advice.
    They do not constitute due diligence and are not a substitute for independent technical, legal or financial assessment.
    Methodology {result.methodology_version} | Rules {result.rules_version} | akinmade.co.uk | CONFIDENTIAL
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# FOOTER (when no run yet)
# ---------------------------------------------------------------------------

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="padding:20px;background:#f8f9fa;border-radius:4px;border-left:4px solid {AMBER};">
          <div style="font-weight:700;color:{NAVY};margin-bottom:8px;">Deterministic Engine</div>
          <div style="font-size:13px;color:#555;">Six dimensions. Fixed weightings. Published rules.
          Same inputs always produce the same outputs. No discretionary judgement in the scoring path.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="padding:20px;background:#f8f9fa;border-radius:4px;border-left:4px solid {AMBER};">
          <div style="font-weight:700;color:{NAVY};margin-bottom:8px;">Full Evidence Envelope</div>
          <div style="font-size:13px;color:#555;">Every number traces to a named public source.
          EITI, Fraser Institute, World Bank WGI, exchange filings, cadastre data.</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="padding:20px;background:#f8f9fa;border-radius:4px;border-left:4px solid {AMBER};">
          <div style="font-weight:700;color:{NAVY};margin-bottom:8px;">What You Don't Know</div>
          <div style="font-size:13px;color:#555;">Signals, anomalies and dependencies buried in
          the evidence that the score alone does not communicate. That is the intelligence.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:40px;font-size:11px;color:#aaa;text-align:center;">
    Methodology SEAM-M-v1.0 | Rules SEAM-R-v1.0 | Jurisdictions: Zambia, DRC, Botswana, Ghana, Tanzania, Namibia, Guinea, Zimbabwe, Mozambique | akinmade.co.uk
    </div>
    """, unsafe_allow_html=True)
