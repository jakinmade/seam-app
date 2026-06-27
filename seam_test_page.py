"""
SEAM Test Harness — Streamlit page
Included in app.py via: if page == "test": render_test_page()
Access via: ?page=test in the URL (not surfaced in navigation)
"""

import streamlit as st
from seam_test_harness import run_harness, TEST_CASES


def render_test_page():
    st.set_page_config(page_title="SEAM Test Harness", layout="wide")
    st.markdown("## SEAM Engine Test Harness")
    st.caption("Seed-only scoring. No API calls. Runs deterministically every time.")

    if st.button("Run Tests", type="primary"):
        _run_and_display()
    else:
        st.info("Press Run Tests to execute the harness against all test assets.")


def _run_and_display():
    with st.spinner("Running..."):
        results = run_harness()

    total_fail = sum(r.failed for r in results)
    total_warn = sum(r.warned for r in results)
    total_pass = sum(r.passed for r in results)

    if total_fail:
        st.error(f"FAIL — {total_fail} errors across {len(results)} assets")
    elif total_warn:
        st.warning(f"WARN — {total_warn} warnings, no errors")
    else:
        st.success(f"ALL PASS — {total_pass} checks across {len(results)} assets")

    for r in results:
        colour = "🔴" if r.failed else ("🟡" if r.warned else "🟢")
        header = f"{colour} {r.label}  —  {r.score}/100  {r.verdict}"

        with st.expander(header, expanded=bool(r.failed)):
            col1, col2, col3 = st.columns(3)
            col1.metric("Score", f"{r.score}/100")
            col2.metric("Verdict", r.verdict)
            col3.metric("Completeness", f"{r.evidence_completeness}/100")

            # Dimension bar
            dim_cols = st.columns(6)
            for i, (code, score) in enumerate(r.dimension_scores.items()):
                dim_cols[i].metric(code, round(score, 1))

            if r.floor_rules:
                st.warning(f"Floor rules triggered: {', '.join(r.floor_rules)}")

            # Check results table
            rows = []
            for c in r.checks:
                status = "✓" if c.passed else ("✗" if c.severity == "ERROR" else "!")
                rows.append({"Status": status, "Check": c.name, "Detail": c.detail})

            st.dataframe(rows, use_container_width=True, hide_index=True)

            if r.notes:
                st.caption(f"Notes: {r.notes}")
