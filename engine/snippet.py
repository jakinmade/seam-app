"""
SEAM Free Snippet
Sprint 6 — D1, D2, D3 scores only. Three cited sources. No registration. No payment.

The free snippet is not a marketing tool. It is a proof of integrity.
Every investor who verifies a cited source becomes a believer before they become a buyer.
"""

from engine.scoring import ScoringResult, DimensionScore


SNIPPET_DIMENSIONS = ["D1", "D2", "D3"]

SNIPPET_SOURCES = {
    "D1": {
        "name": "Fraser Institute Annual Survey of Mining Companies",
        "url": "https://www.fraserinstitute.org/studies/annual-survey-of-mining-companies",
        "what": "Investment Attractiveness Index by jurisdiction"
    },
    "D2": {
        "name": "EITI — Extractive Industries Transparency Initiative",
        "url": "https://eiti.org/countries",
        "what": "Country implementation status and payment disclosure quality"
    },
    "D3": {
        "name": "USGS Mineral Resources Data System",
        "url": "https://mrdata.usgs.gov/mineral-resources/",
        "what": "Mineral deposit classification and resource data"
    },
}


def generate_snippet(result: ScoringResult) -> dict:
    """
    Extract the free snippet from a full scoring result.
    Returns D1, D2, D3 scores with one cited source each.
    Does not include D4, D5, D6, aggregate score, verdict or evidence envelope.
    """
    dim_map = {d.code: d for d in result.dimensions}

    snippet_dims = []
    for code in SNIPPET_DIMENSIONS:
        d = dim_map.get(code)
        if d:
            snippet_dims.append({
                "code": code,
                "name": d.name,
                "score": d.adjusted_score,
                "data_gaps": d.data_gaps,
                "source": SNIPPET_SOURCES.get(code, {})
            })

    return {
        "asset_id": result.asset_id,
        "asset_name": result.asset_name,
        "methodology_version": result.methodology_version,
        "generated_at": result.generated_at,
        "snippet_dimensions": snippet_dims,
        "gated_message": (
            "D4 Local Content, D5 Infrastructure Readiness, D6 Capital Access Signals, "
            "the aggregate Investment Readiness Score, verdict, next action and full "
            "Evidence Envelope are available in the Full Report."
        )
    }
