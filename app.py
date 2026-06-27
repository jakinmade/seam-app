"""
SEAM — Structured Evidence for African Mining
Streamlit App  |  Sprints 4-5-6

Sprint 4: Polish + PDF download on completion
Sprint 5: SEAM Watch — diff evidence envelopes, flag material changes
Sprint 6: Free snippet — D1/D2/D3 + cited sources, full report gated
"""

import streamlit as st
from seam_test_page import render_test_page
import json, os, sys, base64, uuid, hashlib
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.scoring import score_asset
from engine.intelligence import generate_intelligence
from engine.retrieval import retrieve_asset_data
from engine.report import generate_pdf
from engine.watch import record_assessment, diff_envelopes, assess_alert
from engine.asset_store import save_assessment, compute_benchmarks, get_all_assessments
from engine.evidence_book import generate_evidence_book
from engine.snippet import generate_snippet
from data.phase1_assets import ALL_ASSETS

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

# Hidden test page — ?page=test
_qp = st.query_params.get("page", "")
if _qp == "test":
    render_test_page()
    st.stop()

st.set_page_config(
    page_title="SEAM — Structured Evidence for African Mining",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

AMBER  = "#C8962E"
NAVY   = "#0B1929"
VERDICT_COLOUR = {
    "PROCEED":                  "#1A7A3A",
    "PROCEED WITH CONDITIONS":  "#B8860B",
    "MONITOR":                  "#1A5FA8",
    "CAUTION":                  "#C65C00",
    "AVOID":                    "#CC0000",
}

JURISDICTIONS = [
    "Zambia","Democratic Republic of Congo","Botswana","Ghana",
    "Tanzania","Namibia","Guinea","Zimbabwe","Mozambique"
]

PRELOADED = {
    "-- Select a pre-loaded asset --": None,
    "Konkola Copper Mines (KCM / CopperTech) — Zambia": "ZMB-001",
    "Mingomba Copper Project (KoBold Metals) — Zambia":  "ZMB-002",
    "Lumwana Copper Mine (Barrick Gold) — Zambia":       "ZMB-003",
}

# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------

st.markdown(f"""
<style>
html, body, [class*="css"] {{ font-family: Arial, sans-serif; }}

.seam-header {{
  background:{NAVY}; padding:22px 32px; margin:-1rem -1rem 1.8rem -1rem;
  display:flex; align-items:center; justify-content:space-between;
}}
.seam-logo  {{ font-size:30px; font-weight:700; color:{AMBER}; letter-spacing:2px; }}
.seam-sub   {{ font-size:11px; color:#aaa; letter-spacing:1px; margin-top:2px; }}
.seam-ver   {{ font-size:11px; color:#666; text-align:right; line-height:1.7; }}

.banner {{ display:flex; margin-bottom:18px; border-radius:4px; overflow:hidden; }}
.ban-l  {{ background:{NAVY}; padding:18px 24px; flex:1; }}
.ban-r  {{ padding:18px 24px; flex:1; display:flex; flex-direction:column; justify-content:center; }}
.ban-score {{ font-size:52px; font-weight:700; color:{AMBER}; line-height:1; }}
.ban-denom {{ font-size:16px; color:#888; }}
.ban-lbl   {{ font-size:11px; color:#aaa; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }}
.ban-verdict {{ font-size:24px; font-weight:700; color:white; }}

.dim-row {{ display:flex; align-items:flex-start; padding:10px 0;
            border-bottom:1px solid #f0f0f0; gap:10px; }}
.dim-code {{ font-weight:700; color:{NAVY}; width:34px; font-size:13px; flex-shrink:0; padding-top:2px; }}
.dim-body {{ flex:1; }}
.dim-name {{ font-size:13px; font-weight:600; color:#222; }}
.dim-wt   {{ font-size:11px; color:#aaa; }}
.dim-adj  {{ font-size:11px; margin-top:2px; }}
.dim-gap  {{ font-size:11px; color:#C65C00; margin-top:2px; }}
.dim-text {{ font-size:12px; color:#444; line-height:1.55; margin-top:5px; }}
.dim-right {{ text-align:right; flex-shrink:0; }}
.dim-num  {{ font-size:18px; font-weight:700; color:{NAVY}; }}
.dim-bar-bg   {{ width:90px; height:7px; background:#e8e8e8; border-radius:3px; margin-top:5px; display:inline-block; }}
.dim-bar-fill {{ height:7px; background:{AMBER}; border-radius:3px; }}

.intel-item {{ display:flex; align-items:flex-start; margin-bottom:14px; gap:10px; }}
.intel-num  {{ min-width:26px; height:26px; background:{AMBER}; border-radius:50%;
               display:flex; align-items:center; justify-content:center;
               font-weight:700; color:white; font-size:12px; flex-shrink:0; }}
.intel-text {{ font-size:13px; color:#333; line-height:1.6; padding-top:2px; }}

.snip-dim {{ background:#f8f8f8; border-radius:4px; padding:14px 16px; margin-bottom:10px;
             border-left:4px solid {AMBER}; }}
.snip-score {{ font-size:28px; font-weight:700; color:{NAVY}; }}
.snip-src   {{ font-size:11px; color:#888; margin-top:6px; }}

.cert-block {{ background:{NAVY}; color:white; padding:16px 20px; border-radius:4px;
               margin-top:16px; font-size:12px; line-height:1.8; }}
.cert-title {{ font-size:13px; font-weight:700; color:{AMBER}; margin-bottom:8px; letter-spacing:1px; }}

.watch-alert-high {{ background:#fff0f0; border-left:4px solid #CC0000;
                     padding:12px 16px; border-radius:0 4px 4px 0; margin-bottom:12px; }}
.watch-alert-pos  {{ background:#f0fff4; border-left:4px solid #1A7A3A;
                     padding:12px 16px; border-radius:0 4px 4px 0; margin-bottom:12px; }}
.watch-alert-med  {{ background:#fff8e1; border-left:4px solid #B8860B;
                     padding:12px 16px; border-radius:0 4px 4px 0; margin-bottom:12px; }}

.next-action {{ background:#f8f8f8; border-left:4px solid {AMBER};
                padding:14px 16px; border-radius:0 4px 4px 0; margin-top:14px; }}
.na-lbl {{ font-size:11px; color:#888; text-transform:uppercase; letter-spacing:1px; margin-bottom:5px; }}
.na-txt {{ font-size:13px; font-weight:600; color:#222; }}

.disclaimer {{ font-size:10px; color:#bbb; margin-top:28px; padding-top:14px;
               border-top:1px solid #eee; line-height:1.7; }}

div[data-testid="stButton"] > button {{
  background:{AMBER}; color:white; border:none; font-weight:600;
  padding:10px 28px; border-radius:4px; font-size:14px;
}}
div[data-testid="stButton"] > button:hover {{ background:#b07d24; color:white; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------

if "watch_list"   not in st.session_state: st.session_state.watch_list = {}
if "asset_store"  not in st.session_state: st.session_state.asset_store = {}
if "last_result"  not in st.session_state: st.session_state.last_result = None
if "last_intel"   not in st.session_state: st.session_state.last_intel = None
if "last_input"   not in st.session_state: st.session_state.last_input = None
if "report_ready" not in st.session_state: st.session_state.report_ready = False
if "pdf_path"     not in st.session_state: st.session_state.pdf_path = None
if "snippet"           not in st.session_state: st.session_state.snippet = None
if "evidence_book_path" not in st.session_state: st.session_state.evidence_book_path = None

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def vc(verdict): return VERDICT_COLOUR.get(verdict, "#333")

def render_banner(score, verdict, evidence_completeness=None):
    ec_html = ""
    if evidence_completeness is not None:
        ec_html = f"""
      <div class="ban-m" style="background:#1e2e40;border-left:1px solid #2a3f55;">
        <div class="ban-lbl">Evidence Completeness</div>
        <div><span class="ban-score" style="color:#7eb8d4;">{evidence_completeness}</span><span class="ban-denom"> / 100</span></div>
      </div>"""
    st.markdown(f"""
    <div class="banner">
      <div class="ban-l">
        <div class="ban-lbl">Investment Readiness</div>
        <div><span class="ban-score">{score}</span><span class="ban-denom"> / 100</span></div>
      </div>
      {ec_html}
      <div class="ban-r" style="background:{vc(verdict)};">
        <div class="ban-lbl" style="color:rgba(255,255,255,0.7);">Verdict</div>
        <div class="ban-verdict">{verdict}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def render_dims(dimensions, findings):
    for d in dimensions:
        bar = int(d.adjusted_score)
        finding = findings.get(d.code, "")
        adjs = "".join(
            f'<div class="dim-adj" style="color:{"#1A7A3A" if (a.get("adjustment") or 0)>0 else "#CC0000"};">'
            f'{"+" if (a.get("adjustment") or 0)>0 else ""}{a.get("adjustment")}pts: {a["reason"]}</div>'
            for a in d.adjustments if a.get("adjustment") is not None
        )
        gaps = "".join(f'<div class="dim-gap">&#9888; {g}</div>' for g in d.data_gaps)
        st.markdown(f"""
        <div class="dim-row">
          <div class="dim-code">{d.code}</div>
          <div class="dim-body">
            <span class="dim-name">{d.name}</span>
            <span class="dim-wt"> &nbsp;{int(d.weight*100)}%</span>
            {adjs}{gaps}
            {f'<div class="dim-text">{finding}</div>' if finding else ''}
          </div>
          <div class="dim-right">
            <div class="dim-num">{d.adjusted_score:.1f}</div>
            <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{bar}%;"></div></div>
          </div>
        </div>""", unsafe_allow_html=True)

def render_intel(items):
    for i, f in enumerate(items, 1):
        st.markdown(f"""
        <div class="intel-item">
          <div class="intel-num">{i}</div>
          <div class="intel-text">{f}</div>
        </div>""", unsafe_allow_html=True)

def cert_block(result):
    report_id = hashlib.sha256(f"{result.asset_id}{result.generated_at}".encode()).hexdigest()[:16].upper()
    ts = datetime.fromisoformat(result.generated_at).strftime("%d %B %Y %H:%M UTC")
    st.markdown(f"""
    <div class="cert-block">
      <div class="cert-title">SEAM CERTIFICATION</div>
      Asset: {result.asset_name}<br>
      Asset ID: {result.asset_id}<br>
      Score: {result.investment_readiness_score} / 100<br>
      Evidence Completeness: {result.evidence_completeness_score} / 100<br>
      Verdict: {result.verdict}<br>
      Methodology: {result.methodology_version} | Rules: {result.rules_version}<br>
      Generated: {ts}<br>
      Report ID: SEAM-{report_id}
    </div>""", unsafe_allow_html=True)

def dl_button(pdf_path, asset_id):
    with open(pdf_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    fname = f"SEAM_{asset_id}_Report.pdf"
    st.markdown(
        f'<a href="data:application/pdf;base64,{b64}" download="{fname}" '
        f'style="background:{AMBER};color:white;padding:11px 28px;border-radius:4px;'
        f'text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">'
        f'Download Full Report (PDF)</a>',
        unsafe_allow_html=True
    )

def render_snippet(snippet):
    st.markdown(f"### Free Snippet — {snippet['asset_name']}")
    st.caption("Three public scores. Every source cited. Verify before you spend a penny.")
    for dim in snippet["snippet_dimensions"]:
        gaps = "".join(f'<div style="color:#C65C00;font-size:11px;">&#9888; {g}</div>' for g in dim.get("data_gaps",[]))
        src = dim.get("source", {})
        st.markdown(f"""
        <div class="snip-dim">
          <div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;">{dim['code']} — {dim['name']}</div>
          <div class="snip-score">{dim['score']:.1f} <span style="font-size:16px;color:#aaa;">/ 100</span></div>
          {gaps}
          <div class="snip-src">
            Source: <strong>{src.get('name','')}</strong> — {src.get('what','')}<br>
            <a href="{src.get('url','#')}" target="_blank" style="color:{AMBER};">{src.get('url','')}</a>
          </div>
        </div>""", unsafe_allow_html=True)
    st.info(f"**Full Report includes:** D4 Local Content, D5 Infrastructure Readiness, D6 Capital Access Signals, aggregate score, verdict, next action and full Evidence Envelope.")

def render_watch_alert(alert, asset_name):
    if not alert or not alert.get("fires"):
        return
    sev = alert.get("severity","")
    cls = {"HIGH":"watch-alert-high","MEDIUM":"watch-alert-med","POSITIVE":"watch-alert-pos"}.get(sev,"watch-alert-med")
    icon = {"HIGH":"🔴","MEDIUM":"🟠","POSITIVE":"🟢"}.get(sev,"🔵")
    reasons = " ".join(f"<div>{r}</div>" for r in alert.get("reasons",[]))
    changes = ""
    for c in alert.get("dim_changes",[]):
        arrow = "▲" if c["direction"]=="up" else "▼"
        col = "#1A7A3A" if c["direction"]=="up" else "#CC0000"
        changes += f'<div style="font-size:12px;color:{col};">{arrow} {c["dimension"]} {c["dimension_name"]}: {c["prev_score"]} → {c["curr_score"]} ({c["delta"]:+.1f})</div>'
    st.markdown(f"""
    <div class="{cls}">
      <div style="font-weight:700;margin-bottom:6px;">{icon} SEAM Watch Alert — {asset_name}</div>
      {reasons}
      <div style="margin-top:8px;">{changes}</div>
      <div style="margin-top:8px;font-size:12px;font-weight:600;">{alert.get('recommended_action','')}</div>
    </div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------

st.markdown(f"""
<div class="seam-header">
  <div>
    <div class="seam-logo">SEAM</div>
    <div class="seam-sub">STRUCTURED EVIDENCE FOR AFRICAN MINING</div>
  </div>
  <div class="seam-ver">
    Methodology SEAM-M-v1.0 &nbsp;|&nbsp; Rules SEAM-R-v1.0<br>
    Deterministic. Evidence-verifiable. Auditable. &nbsp;|&nbsp; 9 jurisdictions &nbsp;|&nbsp; akinmade.co.uk
  </div>
</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# NAV
# ---------------------------------------------------------------------------

page = st.radio("", ["Assessment", "SEAM Watch", "Free Snippet"], horizontal=True, label_visibility="collapsed")
st.markdown("---")

# ===========================================================================
# PAGE: ASSESSMENT
# ===========================================================================

if page == "Assessment":

    st.markdown("**The first deterministic, evidence-verifiable bankability assessment platform for African mining assets.**")
    st.caption("Every conclusion is traceable to a named public source. Every score is produced by deterministic rules. No analyst opinion in the scoring path.")
    st.markdown("")

    mode = st.radio("Mode", ["Live retrieval", "Pre-loaded asset"], horizontal=True)

    if mode == "Live retrieval":
        c1, c2 = st.columns([2,1])
        with c1: asset_name_input = st.text_input("Asset name", placeholder="e.g. Kansanshi Mine, Obuasi Gold Mine, Kamoa-Kakula...")
        with c2: jurisdiction_input = st.selectbox("Jurisdiction", JURISDICTIONS)
        context_input = st.text_area(
            "Supporting information (optional)",
            placeholder="Paste operator details, ASX/TSX ticker, recent news, technical report extracts, or any other relevant information. The more context you provide, the richer the evidence envelope.",
            height=80
        )
        uploaded_file = st.file_uploader("Attach a document (optional — PDF, TXT)", type=["pdf", "txt"])
        if uploaded_file is not None:
            try:
                import io
                if uploaded_file.type == "application/pdf":
                    st.caption("PDF attached. Text will be extracted and used as supporting context.")
                    file_text = uploaded_file.read().decode("utf-8", errors="ignore")
                else:
                    file_text = uploaded_file.read().decode("utf-8", errors="ignore")
                context_input = (context_input + "\n\nATTACHED DOCUMENT:\n" + file_text[:3000]).strip()
                st.caption(f"Document loaded: {len(file_text)} characters. First 3,000 characters will be used.")
            except Exception as e:
                st.warning(f"Could not read file: {e}")
        use_preloaded = False
    else:
        choice = st.selectbox("Select asset", list(PRELOADED.keys()))
        use_preloaded = PRELOADED.get(choice)
        asset_name_input = jurisdiction_input = context_input = ""

    st.markdown("")
    run = st.button("Run SEAM Assessment")

    if run:
        if not use_preloaded and not asset_name_input.strip():
            st.error("Enter an asset name.")
            st.stop()

        st.session_state.report_ready = False
        st.session_state.pdf_path = None

        with st.spinner("Running SEAM assessment..."):

            # STEP 1 — Data
            sources_meta = {}
            if use_preloaded:
                asset_input = ALL_ASSETS[use_preloaded]
            else:
                with st.status("Locating asset records...", expanded=True) as s:
                    st.write(f"Retrieving public evidence: {asset_name_input} | {jurisdiction_input}")
                    st.write("Consulting: EITI, Fraser Institute, World Bank WGI, exchange filings, government cadastre, USGS")
                    asset_input, sources_meta = retrieve_asset_data(asset_name_input, jurisdiction_input, context_input)
                    if sources_meta.get("mock"):
                        if sources_meta.get("api_error"):
                            st.warning(f"Live data retrieval unavailable: {sources_meta['api_error']}. Showing conservative defaults — score is indicative only.")
                        else:
                            st.write("Live retrieval active in deployed app with ANTHROPIC_API_KEY.")
                    s.update(label="Evidence envelope assembled.", state="complete")

            # STEP 2 — Score
            with st.status("Scoring engine...", expanded=False) as s:
                result = score_asset(asset_input)
                s.update(label=f"Score: {result.investment_readiness_score}/100 | Evidence: {result.evidence_completeness_score}/100 | {result.verdict}", state="complete")

            # STEP 3 — Snippet (always free)
            snippet = generate_snippet(result)
            st.session_state.snippet = snippet

            # STEP 4 — Intelligence
            with st.status("Intelligence analysis (Claude)...", expanded=False) as s:
                intel = generate_intelligence(result, asset_input)
                s.update(label="Analysis complete.", state="complete")

            # STEP 5 — PDF (generated, not yet shown)
            with st.status("Preparing report...", expanded=False) as s:
                os.makedirs("/tmp/seam", exist_ok=True)
                pdf_path = generate_pdf(result, intel, asset_input, "/tmp/seam")
                s.update(label="Report ready.", state="complete")

            # STEP 6 — Watch list
            # Generate Evidence Book
            try:
                eb_path = generate_evidence_book(result, output_dir="/tmp/seam")
                st.session_state.evidence_book_path = eb_path
            except Exception as _eb_err:
                st.session_state.evidence_book_path = None
                st.session_state.evidence_book_error = str(_eb_err)
                st.warning(f"Evidence Book generation failed: {str(_eb_err)[:200]}")

            st.session_state.watch_list = record_assessment(st.session_state.watch_list, result)
            alert = st.session_state.watch_list.get(result.asset_id, {}).get("alert")
            save_assessment(st.session_state, result, asset_input)
            benchmarks = compute_benchmarks(st.session_state, result, asset_input)
            # Inject benchmarks into intel for report generation
            intel["_benchmarks"] = benchmarks

            st.session_state.last_result = result
            st.session_state.last_intel  = intel
            st.session_state.last_input  = asset_input
            st.session_state.pdf_path    = pdf_path
            st.session_state.report_ready = True

        # Watch alert
        if alert:
            render_watch_alert(alert, result.asset_name)

        # Floor rules
        for rule in result.floor_rules_triggered:
            st.warning(f"**Floor Rule {rule['code']}** — {rule['description']}")

        # Asset header
        st.markdown(f"### {result.asset_name}")
        st.caption(f"{asset_input.jurisdiction} · {asset_input.province} · {asset_input.commodity} · {result.asset_id} · {result.generated_at[:10]}")

        # ── FREE SNIPPET ─────────────────────────────────────────────────────
        st.markdown("#### Free Scores")
        for dim in snippet["snippet_dimensions"]:
            src = dim.get("source", {})
            c1, c2, c3 = st.columns([1, 2, 2])
            with c1:
                st.markdown(f"**{dim['code']}** {dim['name']}")
            with c2:
                st.markdown(f"**{dim['score']:.1f} / 100**")
            with c3:
                st.markdown(f"[{src.get('name','')}]({src.get('url','#')})")

        st.markdown("---")
        # ── FULL REPORT ───────────────────────────────────────────────
        render_banner(result.investment_readiness_score, result.verdict, getattr(result, "evidence_completeness_score", None))

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Investment Decision", "Dimension Detail",
            "Material Unknowns", "Verdict & Next Action",
            "Commodity Context", "Bankability"
        ])

        with tab1:
            inv_dec = intel.get("investment_decision", {})
            if inv_dec:
                v_conf = inv_dec.get("verdict_confidence", "Low")
                conf_col = {"High": "#1A7A3A", "Medium": "#B8860B", "Low": "#CC0000"}.get(v_conf, "#888")
                st.markdown(f"""
                <div style="background:#f5f0e8;border-left:3px solid #C8962E;padding:12px 16px;margin-bottom:12px;font-size:13px;line-height:1.6;">
                <b>Verdict:</b> {inv_dec.get('verdict', result.verdict)}<br>
                <b>Score:</b> {inv_dec.get('score', result.investment_readiness_score)}/100 &nbsp;|&nbsp;
                <b>Evidence Completeness:</b> {inv_dec.get('evidence_completeness', result.evidence_completeness_score)}/100<br>
                <b>Verdict Confidence:</b> <span style="color:{conf_col};font-weight:bold;">{v_conf}</span><br>
                <b>Critical Risks:</b> {inv_dec.get('critical_risks', len(result.floor_rules_triggered))}<br>
                <b>Recommended Action:</b> {inv_dec.get('recommended_action', result.next_action)}
                </div>""", unsafe_allow_html=True)
                risks = intel.get("critical_risks", [])
                if risks:
                    st.markdown("**Critical Risks**")
                    for r in risks:
                        st.markdown(f"- {r}")
                drivers = intel.get("investment_drivers", {})
                if drivers:
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown("**Positive**")
                        for p in drivers.get("positive", []):
                            st.markdown(f"- {p}")
                    with c2:
                        st.markdown("**Negative**")
                        for n in drivers.get("negative", []):
                            st.markdown(f"- {n}")
                    with c3:
                        st.markdown("**Unknown**")
                        for u in drivers.get("unknown", []):
                            st.markdown(f"- {u}")
            else:
                st.markdown(intel.get("principal_finding", intel.get("executive_summary","")))
            cert_block(result)

        with tab2:
            render_dims(result.dimensions, intel.get("dimension_findings", {}))

        with tab3:
            st.markdown('<div style="font-size:12px;color:#888;margin-bottom:14px;font-style:italic;">Material unknowns: fields absent from public record that are relevant to investment assessment.</div>', unsafe_allow_html=True)
            render_intel(intel.get("investor_intelligence", []))

        with tab4:
            vcolor = vc(result.verdict)
            st.markdown(f"""
            <div style="background:{vcolor};color:white;padding:14px 20px;border-radius:4px;margin-bottom:14px;">
              <div style="font-size:11px;opacity:0.7;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Verdict — {result.methodology_version}</div>
              <div style="font-size:22px;font-weight:700;">{result.verdict}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(intel.get("verdict_section",""))
            st.markdown(f'<div class="next-action"><div class="na-lbl">Next Action</div><div class="na-txt">{result.next_action}</div></div>', unsafe_allow_html=True)

        with tab5:
            cc = intel.get("commodity_context", {})
            if cc and cc.get("commodity") and cc.get("commodity") != "Unknown":
                AMBER_COL = "#C8962E"
                NAVY_COL  = "#0B1929"
                outlook_col = {"Bullish":"#1A7A3A","Neutral":"#B8860B","Bearish":"#CC0000"}.get(cc.get("outlook","Neutral"),"#888")
                st.markdown(f"### {cc.get('commodity','')}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Outlook", cc.get("outlook",""))
                with col2:
                    st.metric("12m Price Trend", cc.get("price_trend_12m",""))
                with col3:
                    st.metric("Critical Mineral", "Yes" if cc.get("critical_mineral") else "No")
                if cc.get("critical_mineral_lists"):
                    st.caption(f"Listed on: {', '.join(cc['critical_mineral_lists'])}")
                if cc.get("lobito_corridor_relevant"):
                    st.info("Lobito Corridor eligible asset.")
                st.markdown(f"**Market context:** {cc.get('outlook_rationale','')}")
                st.markdown(f"**Demand driver:** {cc.get('demand_driver','')}")
                st.caption("Commodity context does not affect the Investment Readiness Score or Verdict.")
            else:
                st.info("Commodity not identified during retrieval. Run assessment with additional context to populate this panel.")

        with tab6:
            bc = intel.get("bankability_constraints", {})
            if bc and bc.get("constraint_summary") and bc.get("constraint_summary") != "Live in Streamlit":
                dfi_col = {"Ready":"#1A7A3A","Conditional":"#B8860B","Not Ready":"#CC0000"}.get(bc.get("dfi_readiness",""),"#888")
                st.markdown(f'**DFI Readiness:** <span style="color:{dfi_col};font-weight:bold;">{bc.get("dfi_readiness","")}</span>', unsafe_allow_html=True)
                st.markdown(bc.get("constraint_summary",""))
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Environmental Permit:** {bc.get('environmental_permit','Unknown')}")
                    st.markdown(f"**ESIA on Record:** {'Yes' if bc.get('esia_on_record') else 'No'}")
                    st.markdown(f"**Water Licence:** {bc.get('water_licence','Unknown')}")
                with col2:
                    st.markdown(f"**Community Consultation:** {bc.get('community_consultation','None')}")
                    st.markdown(f"**Social Licence Disputes:** {'Active' if bc.get('social_licence_disputes') else 'None identified'}")
                st.caption("Bankability constraints reflect public evidence only. They do not affect the Investment Readiness Score.")
            else:
                st.info("Bankability constraints will populate with live retrieval data.")

            # Benchmarks
            bm = intel.get("_benchmarks", {})
            if bm and not bm.get("insufficient_data"):
                st.markdown("---")
                st.markdown("**Benchmark**")
                glob = bm.get("global")
                jur  = bm.get("jurisdiction")
                com  = bm.get("commodity")
                this = bm.get("asset_score", result.investment_readiness_score)
                rows_data = []
                if glob: rows_data.append(("All assets", this, glob["average"], glob["top_quartile"], glob["count"]))
                if jur:  rows_data.append((asset_input.jurisdiction, this, jur["average"], jur["top_quartile"], jur["count"]))
                if com:  rows_data.append((asset_input.commodity, this, com["average"], com["top_quartile"], com["count"]))
                for label, score, avg, tq, n in rows_data:
                    st.markdown(f"**{label}** (n={n}): This asset **{score}** | Average {avg} | Top quartile {tq}")
            elif bm and bm.get("insufficient_data"):
                st.caption(f"Benchmarks available after 2+ assets scored. Currently {bm.get('count',0)} in store.")

        st.markdown("")
        col_dl1, col_dl2 = st.columns([1, 1])
        with col_dl1:
            dl_button(pdf_path, result.asset_id)
        with col_dl2:
            eb_path = st.session_state.get("evidence_book_path")
            if eb_path:
                try:
                    with open(eb_path, "rb") as f:
                        eb64 = base64.b64encode(f.read()).decode()
                    eb_fname = f"SEAM_{result.asset_id}_EvidenceBook.pdf"
                    st.markdown(
                        f'<a href="data:application/pdf;base64,{eb64}" download="{eb_fname}" '
                        f'style="background:{NAVY};color:white;padding:11px 28px;border-radius:4px;'
                        f'text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">'
                        f'Download Evidence Book (PDF)</a>',
                        unsafe_allow_html=True
                    )
                    st.caption("Complete provenance register. Every finding traceable to a named public source.")
                except Exception:
                    pass

        with st.expander("Evidence Envelope (JSON)"):
            st.json(result.evidence_envelope)

        op = sources_meta.get("phase1_operator", {})
        if op and op.get("operator"):
            with st.expander(f"Operator: {op.get('operator','Unknown')}"):
                st.markdown(f"**Asset (official):** {op.get('asset_name_official','')}")
                st.markdown(f"**Operator:** {op.get('operator','')}")
                st.markdown(f"**Majority owner:** {op.get('majority_owner','')}")
                if op.get("minority_owners"):
                    st.markdown(f"**Minority owners:** {', '.join(op['minority_owners'])}")
                st.markdown(f"**Commodity:** {op.get('commodity_primary','')}")
                st.markdown(f"**Stage:** {op.get('asset_stage','')}")
                if op.get("listed_vehicle"):
                    st.markdown(f"**Listed:** {op.get('listed_vehicle','')} on {op.get('exchange','')}")
                if op.get("known_dfi_links"):
                    st.markdown(f"**Known DFI links:** {', '.join(op['known_dfi_links'])}")
                st.markdown(f"**Search confidence:** {op.get('search_confidence','')}")

        if sources_meta.get("sources_consulted"):
            with st.expander(f"Sources consulted ({len(sources_meta['sources_consulted'])})"):
                for s in sources_meta["sources_consulted"]:
                    st.markdown(f"**{s.get('field','')}** — {s.get('source','')} | Found: {s.get('value_found','')}")

        if sources_meta.get("data_gaps"):
            with st.expander(f"Data gaps ({len(sources_meta['data_gaps'])})"):
                for g in sources_meta["data_gaps"]:
                    st.markdown(f"- {g}")

    elif st.session_state.report_ready and st.session_state.last_result:
        result  = st.session_state.last_result
        intel   = st.session_state.last_intel
        snippet = st.session_state.snippet
        if st.session_state.pdf_path:
            render_banner(result.investment_readiness_score, result.verdict, getattr(result, "evidence_completeness_score", None))
            col_dl1b, col_dl2b = st.columns([1, 1])
            with col_dl1b:
                dl_button(st.session_state.pdf_path, result.asset_id)
            with col_dl2b:
                eb_path2 = st.session_state.get("evidence_book_path")
                if eb_path2:
                    try:
                        with open(eb_path2, "rb") as f:
                            eb64b = base64.b64encode(f.read()).decode()
                        eb_fname2 = f"SEAM_{result.asset_id}_EvidenceBook.pdf"
                        st.markdown(
                            f'<a href="data:application/pdf;base64,{eb64b}" download="{eb_fname2}" '
                            f'style="background:{NAVY};color:white;padding:11px 28px;border-radius:4px;'
                            f'text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">'
                            f'Download Evidence Book (PDF)</a>',
                            unsafe_allow_html=True
                        )
                    except Exception:
                        pass

    else:
        # Landing state
        c1, c2, c3 = st.columns(3)
        props = [
            ("Deterministic Engine", f"Six dimensions. Fixed weightings. Published rules. Same inputs always produce the same outputs."),
            ("Full Evidence Envelope", f"Every number traces to a named public source. EITI, Fraser, World Bank WGI, exchange filings, cadastre."),
            ("What You Don't Know", f"Signals and anomalies buried in the evidence that the score alone does not communicate."),
        ]
        for col, (title, text) in zip([c1,c2,c3], props):
            with col:
                st.markdown(f"""
                <div style="padding:18px;background:#f8f9fa;border-radius:4px;border-left:4px solid {AMBER};height:100%;">
                  <div style="font-weight:700;color:{NAVY};margin-bottom:8px;">{title}</div>
                  <div style="font-size:13px;color:#555;">{text}</div>
                </div>""", unsafe_allow_html=True)

# ===========================================================================
# PAGE: SEAM WATCH
# ===========================================================================

elif page == "SEAM Watch":
    st.markdown("### SEAM Watch")
    st.caption("Run any asset multiple times to track changes. Decision Stability shows direction of travel.")

    watch = st.session_state.watch_list
    all_assessed = get_all_assessments(st.session_state)
    if all_assessed and len(all_assessed) > 1:
        with st.expander(f"Benchmark table ({len(all_assessed)} assets scored this session)"):
            for rec in all_assessed:
                vc_col = {"PROCEED":"#1A7A3A","PROCEED WITH CONDITIONS":"#B8860B",
                          "MONITOR":"#1A5FA8","CAUTION":"#C65C00","AVOID":"#CC0000"}.get(rec["verdict"],"#888")
                st.markdown(
                    f'`{rec["asset_name"]}` &nbsp; **{rec["score"]}/100** &nbsp; '
                    f'<span style="color:{vc_col};">{rec["verdict"]}</span> &nbsp; '
                    f'EC: {rec["evidence_completeness"]}/100 &nbsp; {rec["jurisdiction"]}',
                    unsafe_allow_html=True
                )

    if not watch:
        st.info("No assets on watch yet. Run an assessment to add an asset to the watch list.")
    else:
        for asset_id, entry in watch.items():
            latest = entry.get("latest", {})
            alert  = entry.get("alert")
            history = entry.get("history", [])

            stability = entry.get("stability", {})
            stab_label = stability.get("label", "First assessment")
            stab_col = {"Improving": "#1A7A3A", "Deteriorating": "#CC0000",
                        "Stable": "#B8860B", "First assessment": "#888"}.get(stab_label, "#888")
            stab_delta = stability.get("delta")
            delta_str = f" ({stab_delta:+.1f}pts)" if stab_delta is not None else ""

            with st.expander(f"{latest.get('asset_name',asset_id)}  —  {latest.get('score','?')}/100  —  {latest.get('verdict','?')}", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Score:** {latest.get('score','?')}/100")
                with c2:
                    st.markdown(f"**Evidence:** {latest.get('evidence_completeness', '?')}/100")
                with c3:
                    st.markdown(
                        f'**Stability:** <span style="color:{stab_col};font-weight:bold;">{stab_label}{delta_str}</span>',
                        unsafe_allow_html=True
                    )
                st.markdown("")
                if alert and alert.get("fires"):
                    render_watch_alert(alert, latest.get("asset_name", asset_id))
                else:
                    st.success("No material change detected since last assessment.")

                if len(history) >= 2:
                    st.markdown("**Score history**")
                    for h in history:
                        ts = h["generated_at"][:16].replace("T"," ")
                        vcolor = vc(h["verdict"])
                        st.markdown(f'`{ts}` &nbsp; **{h["score"]}/100** &nbsp; <span style="color:{vcolor};font-weight:600;">{h["verdict"]}</span>', unsafe_allow_html=True)

                if alert and alert.get("dim_changes"):
                    st.markdown("**Dimension changes**")
                    for c in alert["dim_changes"]:
                        arrow = "▲" if c["direction"]=="up" else "▼"
                        color = "#1A7A3A" if c["direction"]=="up" else "#CC0000"
                        st.markdown(f'<span style="color:{color};">{arrow} {c["dimension"]} {c["dimension_name"]}: {c["prev_score"]} → {c["curr_score"]} ({c["delta"]:+.1f}pts)</span>', unsafe_allow_html=True)

# ===========================================================================
# PAGE: FREE SNIPPET
# ===========================================================================

elif page == "Free Snippet":
    st.markdown("### Free Snippet")
    st.caption("A bankability signal on any asset scored in this session. Every score is traceable to a named public source.")

    watch = st.session_state.watch_list
    if not watch:
        st.info("Run an assessment first. The free snippet appears here for every scored asset.")
    else:
        for asset_id, entry in watch.items():
            latest = entry.get("latest", {})
            st.markdown(f"**{latest.get('asset_name', asset_id)}**")
            result = st.session_state.last_result
            if result and result.asset_id == asset_id:
                snippet = generate_snippet(result)
                render_snippet(snippet)
            st.markdown("---")

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------

st.markdown(f"""
<div class="disclaimer">
SEAM Investment Readiness Reports are produced for informational purposes only. They do not constitute investment advice, legal advice or financial advice.
They do not constitute due diligence and are not a substitute for independent technical, legal or financial assessment.
Every investor must conduct their own assessment appropriate to their mandate, jurisdiction and risk appetite.
Methodology SEAM-M-v1.0 | Rules SEAM-R-v1.0 | akinmade.co.uk | CONFIDENTIAL
</div>""", unsafe_allow_html=True)












