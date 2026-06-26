"""
SEAM Source Adapters
Sprint 3+ scaffold — Phase 2 will replace Claude retrieval with structured adapters.

Each adapter:
- Handles exactly one public data source
- Normalises to canonical AssetInput fields
- Returns EvidenceField objects with full provenance
- Is independently testable and replaceable

Current status: scaffolded. Claude retrieval (engine/retrieval.py) is the live path.
Phase 2: each adapter fetches, parses and normalises its source directly.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone


@dataclass
class AdapterResult:
    """Output from a source adapter — structured field values with provenance."""
    source_name: str
    source_url: str
    retrieved_at: str
    fields: dict          # field_name -> AdapterField
    raw_response: Optional[str] = None
    errors: list = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class AdapterField:
    """A single field value with full provenance from a source adapter."""
    value: object
    confidence: str = "medium"     # high | medium | low
    verified: bool = False
    publication_date: Optional[str] = None
    notes: Optional[str] = None


class BaseAdapter:
    """Abstract base. All adapters inherit from this."""
    source_name: str = "Unknown"
    source_url: str = ""
    confidence_level: str = "medium"

    def fetch(self, **kwargs) -> AdapterResult:
        raise NotImplementedError

    def _result(self, fields: dict, raw: str = None) -> AdapterResult:
        return AdapterResult(
            source_name=self.source_name,
            source_url=self.source_url,
            retrieved_at=datetime.now(timezone.utc).isoformat(),
            fields=fields,
            raw_response=raw
        )


# ---------------------------------------------------------------------------
# FRASER INSTITUTE ADAPTER
# Phase 2: fetch Investment Attractiveness Index from Fraser annual survey API/PDF
# ---------------------------------------------------------------------------

class FraserInstituteAdapter(BaseAdapter):
    source_name = "Fraser Institute Annual Survey of Mining Companies"
    source_url = "https://www.fraserinstitute.org/studies/annual-survey-of-mining-companies"
    confidence_level = "high"

    def fetch(self, jurisdiction: str, year: int = None) -> AdapterResult:
        """
        Phase 2: fetch IAI score for jurisdiction from Fraser survey.
        Currently returns scaffold — Claude retrieval is live path.
        """
        # Phase 2 implementation:
        # 1. Download Fraser survey PDF or CSV for year
        # 2. Parse Investment Attractiveness Index for jurisdiction
        # 3. Return structured AdapterField
        return self._result({
            "fraser_investment_attractiveness": AdapterField(
                value=None,
                confidence="high",
                notes=f"Phase 2: fetch Fraser IAI for {jurisdiction}"
            )
        })


# ---------------------------------------------------------------------------
# WORLD BANK WGI ADAPTER
# Phase 2: fetch Rule of Law and Regulatory Quality percentiles from WB API
# ---------------------------------------------------------------------------

class WorldBankWGIAdapter(BaseAdapter):
    source_name = "World Bank Governance Indicators"
    source_url = "https://info.worldbank.org/governance/wgi/"
    confidence_level = "high"
    API_URL = "https://api.worldbank.org/v2/country/{iso2}/indicator/{indicator}?format=json&mrv=1"

    INDICATORS = {
        "wb_rule_of_law_percentile":       "RL.EST",
        "wb_regulatory_quality_percentile": "RQ.EST",
    }

    def fetch(self, jurisdiction_iso2: str) -> AdapterResult:
        """
        Phase 2: call WB API for Rule of Law and Regulatory Quality.
        Returns percentile ranks scaled 0-100.
        """
        # Phase 2 implementation:
        # import urllib.request, json
        # for field, indicator in self.INDICATORS.items():
        #     url = self.API_URL.format(iso2=jurisdiction_iso2, indicator=indicator)
        #     with urllib.request.urlopen(url) as r:
        #         data = json.loads(r.read())[1][0]
        #     value = (data["value"] + 2.5) / 5.0 * 100  # scale to 0-100
        return self._result({
            k: AdapterField(value=None, confidence="high",
                notes=f"Phase 2: fetch {v} for {jurisdiction_iso2}")
            for k, v in self.INDICATORS.items()
        })


# ---------------------------------------------------------------------------
# EITI ADAPTER
# Phase 2: fetch country implementation status and payment disclosure quality
# ---------------------------------------------------------------------------

class EITIAdapter(BaseAdapter):
    source_name = "EITI — Extractive Industries Transparency Initiative"
    source_url = "https://eiti.org/countries"
    confidence_level = "high"

    IMPLEMENTATION_STATUS = {
        "ZMB": "compliant", "GHA": "compliant", "TZA": "compliant",
        "DRC": "compliant", "MOZ": "compliant", "GIN": "compliant",
        "NAM": "candidate", "ZWE": "candidate", "BWA": "non-implementing",
    }

    def fetch(self, jurisdiction_code: str) -> AdapterResult:
        """
        Phase 2: fetch EITI implementation status and payment disclosure score.
        Phase 1: status known from registry above.
        """
        status = self.IMPLEMENTATION_STATUS.get(jurisdiction_code.upper(), "non-implementing")
        return self._result({
            "eiti_implementation_status": AdapterField(
                value=status, confidence="high", verified=True,
                notes=f"EITI implementation status for {jurisdiction_code} — registry v1.0"
            ),
            "eiti_compliant_country": AdapterField(
                value=(status == "compliant"), confidence="high", verified=True
            ),
            "eiti_payment_disclosure_quality": AdapterField(
                value=None, confidence="high",
                notes="Phase 2: fetch EITI Secretariat validation score from country report"
            ),
        })


# ---------------------------------------------------------------------------
# EXCHANGE FILINGS ADAPTER (ASX / TSX / AIM)
# Phase 2: search exchange announcements for resource estimates and capital raises
# ---------------------------------------------------------------------------

class ExchangeFilingsAdapter(BaseAdapter):
    source_name = "Exchange Regulatory Filings (ASX / TSX / AIM)"
    source_url = "https://www.asx.com.au/asx/statistics/announcements.do"
    confidence_level = "high"

    def fetch(self, company_name: str, ticker: str = None) -> AdapterResult:
        """
        Phase 2: search ASX/TSX/AIM for NI43-101, JORC filings, capital raises.
        Returns resource standard, reserve classification, capital raise recency.
        """
        return self._result({
            "resource_estimate_standard": AdapterField(value=None, confidence="high",
                notes=f"Phase 2: search exchange filings for {company_name or ticker}"),
            "reserve_classification": AdapterField(value=None, confidence="high",
                notes="Phase 2: extract from most recent technical report filing"),
            "recent_capital_raise": AdapterField(value=None, confidence="high",
                notes="Phase 2: check capital raise announcements in past 36 months"),
            "listed_vehicle": AdapterField(value=None, confidence="high",
                notes="Phase 2: confirm listing status and trading activity"),
        })


# ---------------------------------------------------------------------------
# ZAMBIA LOCAS ADAPTER
# Phase 2: fetch licence compliance status from Zambia MRC LOCAS portal
# ---------------------------------------------------------------------------

class ZambiaLOCASAdapter(BaseAdapter):
    source_name = "Zambia MRC — LOCAS Compliance Portal"
    source_url = "https://locas.mrc.gov.zm"
    confidence_level = "high"

    def fetch(self, licence_holder: str) -> AdapterResult:
        """
        Phase 2: check LOCAS quarterly compliance filing status.
        """
        return self._result({
            "locas_filing_status": AdapterField(value=None, confidence="high",
                notes=f"Phase 2: check LOCAS portal for {licence_holder}"),
            "licence_holder_status": AdapterField(value=None, confidence="medium",
                notes="Phase 2: extract citizen empowerment status from licence record"),
        })


# ---------------------------------------------------------------------------
# DFI ADAPTER
# Phase 2: check IFC, AfDB, BII project databases for active engagements
# ---------------------------------------------------------------------------

class DFIAdapter(BaseAdapter):
    source_name = "DFI Project Databases (IFC, AfDB, BII)"
    source_url = "https://disclosures.ifc.org"
    confidence_level = "high"

    DFI_SOURCES = [
        ("IFC", "https://disclosures.ifc.org/project-detail"),
        ("AfDB", "https://projectsportal.afdb.org/dataportal/VProject/show"),
        ("BII",  "https://www.bii.co.uk/en/our-impact/our-portfolio/"),
    ]

    def fetch(self, asset_name: str, jurisdiction: str) -> AdapterResult:
        """
        Phase 2: search IFC, AfDB and BII for named asset or direct comparator.
        """
        return self._result({
            "active_dfi_engagement": AdapterField(value=None, confidence="high",
                notes=f"Phase 2: search DFI databases for {asset_name}, {jurisdiction}"),
            "gulf_western_investor_linked": AdapterField(value=None, confidence="medium",
                notes="Phase 2: check for named Gulf SWF or Western strategic investor"),
        })


# ---------------------------------------------------------------------------
# ADAPTER REGISTRY
# ---------------------------------------------------------------------------

ADAPTER_REGISTRY = {
    "fraser":   FraserInstituteAdapter,
    "wb_wgi":   WorldBankWGIAdapter,
    "eiti":     EITIAdapter,
    "exchange": ExchangeFilingsAdapter,
    "locas":    ZambiaLOCASAdapter,
    "dfi":      DFIAdapter,
}


def get_adapter(name: str) -> BaseAdapter:
    cls = ADAPTER_REGISTRY.get(name)
    if not cls:
        raise ValueError(f"No adapter registered for '{name}'. Available: {list(ADAPTER_REGISTRY.keys())}")
    return cls()
