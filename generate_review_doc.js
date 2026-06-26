const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Footer, Header
} = require('docx');
const fs = require('fs');

const AMBER = "C8962E";
const NAVY = "0B1929";
const LIGHT_GREY = "F5F5F5";
const MID_GREY = "CCCCCC";
const WHITE = "FFFFFF";

const cellBorder = { style: BorderStyle.SINGLE, size: 1, color: MID_GREY };
const allBorders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function cell(text, opts = {}) {
  const {
    bold = false, shade = null, align = AlignmentType.LEFT,
    color = "000000", size = 20, colspan = 1, width = 3120
  } = opts;
  return new TableCell({
    borders: allBorders,
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { fill: shade, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    columnSpan: colspan,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, bold, color, size, font: "Arial" })]
    })]
  });
}

function hdr(text, level = HeadingLevel.HEADING_1) {
  const sizes = { [HeadingLevel.HEADING_1]: 28, [HeadingLevel.HEADING_2]: 24 };
  const colors = { [HeadingLevel.HEADING_1]: NAVY, [HeadingLevel.HEADING_2]: NAVY };
  return new Paragraph({
    spacing: { before: 240, after: 120 },
    children: [new TextRun({
      text, bold: true, font: "Arial",
      size: sizes[level] || 24,
      color: colors[level] || NAVY
    })]
  });
}

function para(text, opts = {}) {
  const { bold = false, color = "333333", size = 20, spacing = { before: 60, after: 60 } } = opts;
  return new Paragraph({
    spacing,
    children: [new TextRun({ text, bold, color, size, font: "Arial" })]
  });
}

function divider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: AMBER, space: 1 } },
    spacing: { before: 120, after: 120 },
    children: []
  });
}

function scoreBar(score) {
  const filled = Math.round(score / 5);
  return "█".repeat(filled) + "░".repeat(20 - filled);
}

function verdictColor(verdict) {
  const map = {
    "PROCEED": "1A7A3A",
    "PROCEED WITH CONDITIONS": "B8860B",
    "MONITOR": "1A5FA8",
    "CAUTION": "C65C00",
    "AVOID": "CC0000"
  };
  return map[verdict] || "333333";
}

// ── ASSET DATA (from Sprint 1 run) ──────────────────────────────────────────

const assets = [
  {
    id: "ZMB-001",
    name: "Konkola Copper Mines (KCM / CopperTech)",
    jurisdiction: "Zambia",
    commodity: "Copper",
    province: "Copperbelt",
    score: 61,
    verdict: "MONITOR",
    dimensions: [
      { code: "D1", name: "Jurisdiction Stability",           weight: "25%", score: 32.9 },
      { code: "D2", name: "Revenue Transparency",             weight: "20%", score: 72.0 },
      { code: "D3", name: "Asset Data Quality",               weight: "20%", score: 77.0 },
      { code: "D4", name: "Local Content Compliance Posture", weight: "15%", score: 82.0 },
      { code: "D5", name: "Infrastructure Readiness",         weight: "12%", score: 77.0 },
      { code: "D6", name: "Capital Access Signals",           weight: "8%",  score: 20.0 },
    ],
    key_findings: [
      "D1 significantly suppressed by Vedanta arbitration penalty (-8pts), active mining code revision (-3pts), and new royalty SI (-5pts). Fraser IAI 47.3 — mid-tier jurisdiction.",
      "D2 strong at 72. Zambia EITI compliant. Beneficial ownership partial — ZCCM-IH disclosed, minority stake holders not fully public.",
      "D3 penalised by resource estimate over 3 years old and unresolved conflict between USGS (30Mt) and government gazette (29Mt) figures.",
      "D4 high at 82 — state majority ownership post-Vedanta reversion satisfies citizen-owned threshold under SI68.",
      "D6 lowest score at 20 — unlisted state asset, no recent capital raise, no named DFI project engagement at asset level.",
    ],
    data_gaps: [
      "No updated NI43-101 or JORC compliant resource estimate within 3 years. Last compliant estimate pre-dates Vedanta dispute resolution.",
      "USGS vs government gazette reserve conflict unresolved — conservative value applied per EVRES-001.",
    ],
    next_action: "SEAM places this asset on 90-day monitoring cycle. Act when the data moves — not when an advisor remembers to call.",
    floor_rules: []
  },
  {
    id: "ZMB-002",
    name: "Mingomba Copper Project (KoBold Metals)",
    jurisdiction: "Zambia",
    commodity: "Copper",
    province: "North-Western",
    score: 56,
    verdict: "MONITOR",
    dimensions: [
      { code: "D1", name: "Jurisdiction Stability",           weight: "25%", score: 40.9 },
      { code: "D2", name: "Revenue Transparency",             weight: "20%", score: 72.0 },
      { code: "D3", name: "Asset Data Quality",               weight: "20%", score: 63.0 },
      { code: "D4", name: "Local Content Compliance Posture", weight: "15%", score: 50.0 },
      { code: "D5", name: "Infrastructure Readiness",         weight: "12%", score: 49.0 },
      { code: "D6", name: "Capital Access Signals",           weight: "8%",  score: 70.0 },
    ],
    key_findings: [
      "D1 at 40.9 — no Vedanta arbitration penalty (unlike KCM) but same jurisdiction-level Fraser/WGI drag. No historical arbitration against this asset.",
      "D3 at 63 — recent NI43-101 drilling results (2024) but resource only, no reserve declared. Pre-production asset with no production data.",
      "D4 at 50 — foreign-owned (KoBold) with local JV, LOCAS filed but unverified, procurement effort below 20% target.",
      "D5 at 49 — off-grid (diesel/solar), road access paved but 50-200km range, rail over 100km. Lobito Corridor adjustment (+5pts on rail) applied — North-Western province eligible.",
      "D6 strongest dimension at 70 — BII/IFC DFI linkage, KoBold Series C 2024, western strategic investors publicly named.",
    ],
    data_gaps: [
      "No production data in public domain — pre-production asset.",
      "Water supply present but no documented permit.",
      "LOCAS compliance filing submitted but not yet verified by MRC.",
    ],
    next_action: "SEAM places this asset on 90-day monitoring cycle. Act when the data moves — not when an advisor remembers to call.",
    floor_rules: []
  },
  {
    id: "ZMB-003",
    name: "Lumwana Copper Mine (Barrick Gold)",
    jurisdiction: "Zambia",
    commodity: "Copper",
    province: "North-Western",
    score: 76,
    verdict: "PROCEED WITH CONDITIONS",
    dimensions: [
      { code: "D1", name: "Jurisdiction Stability",           weight: "25%", score: 40.9 },
      { code: "D2", name: "Revenue Transparency",             weight: "20%", score: 92.0 },
      { code: "D3", name: "Asset Data Quality",               weight: "20%", score: 100.0 },
      { code: "D4", name: "Local Content Compliance Posture", weight: "15%", score: 75.0 },
      { code: "D5", name: "Infrastructure Readiness",         weight: "12%", score: 81.0 },
      { code: "D6", name: "Capital Access Signals",           weight: "8%",  score: 80.0 },
    ],
    key_findings: [
      "D1 at 40.9 — same Zambia jurisdiction drag as all three assets. No asset-specific arbitration. The condition to address: Zambia Fraser score and mining code revision uncertainty.",
      "D2 at 92 — Barrick NYSE-listed, full beneficial ownership disclosure, EITI compliant, no payment data gap. Strongest transparency profile of the three assets.",
      "D3 perfect score at 100 — Barrick annual reserve update 2024 (NI43-101 compliant, under 3 years), proven and probable reserve declared, current production data, producing asset.",
      "D4 at 75 — foreign-owned (Barrick) with ZCCM-IH minority; dragged by licence holder status (10pts vs 35pts ceiling). Offset by verified LOCAS filing and confirmed 20%+ local procurement.",
      "D5 at 81 — grid-connected with redundancy, paved road under 50km, permitted water. Lobito Corridor adjustment applied. Port distance (2,100km) constrains sub-score.",
      "D6 at 80 — NYSE listed vehicle, Barrick expansion capex 2024, western strategic investor linkage. DFI engagement jurisdiction-level only, not asset-specific.",
    ],
    data_gaps: [],
    next_action: "Address the named conditions identified in the Evidence Envelope. Specifically: Zambia jurisdiction stability improvement is a structural constraint not resolvable at asset level. DFI engagement at asset level (not just jurisdiction) would move D6 to maximum sub-score. Return for re-score if Fraser IAI improves post mining code finalisation.",
    floor_rules: []
  }
];

// ── DOCUMENT BUILD ───────────────────────────────────────────────────────────

const children = [];

// Cover block
children.push(new Paragraph({
  spacing: { before: 480, after: 120 },
  children: [new TextRun({ text: "SEAM", bold: true, size: 72, color: AMBER, font: "Arial" })]
}));
children.push(new Paragraph({
  spacing: { before: 0, after: 60 },
  children: [new TextRun({ text: "Structured Evidence for African Mining", size: 28, color: NAVY, font: "Arial" })]
}));
children.push(new Paragraph({
  spacing: { before: 0, after: 480 },
  children: [new TextRun({ text: "Sprint 1 Scoring Results  |  Methodology SEAM-M-v1.0  |  Rules SEAM-R-v1.0  |  June 2026", size: 20, color: "666666", font: "Arial" })]
}));
children.push(divider());

// Purpose
children.push(hdr("Purpose of This Document"));
children.push(para(
  "This document presents the Sprint 1 scoring results for three Zambian copper assets assessed under the SEAM Investment Readiness Methodology v1.0. It is produced for independent review by qualified mining finance, operational, and governance professionals."
));
children.push(para(
  "Reviewers are asked to assess: (1) whether the scoring methodology produces credible relative rankings between assets; (2) whether the dimension scores reflect the known characteristics of each asset; and (3) whether the verdicts are defensible for use in an investment committee discussion."
));
children.push(para(
  "SEAM is a deterministic scoring engine. No LLM or AI system participates in the scoring path. Identical inputs always produce identical outputs. Every score traces to a named public source and a published rule code. Reviewers who disagree with any score are invited to identify the specific rule or data input they would change and the reasoning."
));
children.push(divider());

// Methodology summary
children.push(hdr("Methodology Summary"));
children.push(para("Six dimensions. Fixed weightings. Published thresholds. No discretionary judgement in the scoring path.", { bold: true }));
children.push(new Paragraph({ spacing: { before: 120, after: 80 }, children: [] }));

const methodTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [936, 4212, 936, 3276],
  rows: [
    new TableRow({
      children: [
        cell("Code", { bold: true, shade: NAVY, color: WHITE, width: 936 }),
        cell("Dimension", { bold: true, shade: NAVY, color: WHITE, width: 4212 }),
        cell("Weight", { bold: true, shade: NAVY, color: WHITE, width: 936, align: AlignmentType.CENTER }),
        cell("Measures", { bold: true, shade: NAVY, color: WHITE, width: 3276 }),
      ]
    }),
    ...([
      ["D1", "Jurisdiction Stability", "25%", "Fraser IAI + World Bank WGI + regulatory adjustments"],
      ["D2", "Revenue Transparency", "20%", "EITI status + beneficial ownership + payment disclosure"],
      ["D3", "Asset Data Quality", "20%", "Resource standard + reserve classification + production data"],
      ["D4", "Local Content Compliance Posture", "15%", "Licence holder status + compliance filing + procurement"],
      ["D5", "Infrastructure Readiness", "12%", "Power + road + rail + water + port distance"],
      ["D6", "Capital Access Signals", "8%", "DFI engagement + listed vehicle + capital raises"],
    ].map((r, i) => new TableRow({
      children: [
        cell(r[0], { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 936 }),
        cell(r[1], { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 4212 }),
        cell(r[2], { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 936, align: AlignmentType.CENTER }),
        cell(r[3], { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 3276 }),
      ]
    })))
  ]
});
children.push(methodTable);

children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));
children.push(para("Verdict thresholds: PROCEED (80-100)  |  PROCEED WITH CONDITIONS (65-79)  |  MONITOR (45-64)  |  CAUTION (25-44)  |  AVOID (0-24)", { color: "555555" }));
children.push(para("Floor rules apply regardless of aggregate score. D2 below 20 caps verdict at CAUTION. D1 below 25 caps at MONITOR. D3 below 15 caps at CAUTION.", { color: "555555" }));
children.push(divider());

// Summary table
children.push(hdr("Sprint 1 Results Summary"));
children.push(new Paragraph({ spacing: { before: 60, after: 80 }, children: [] }));

const summaryTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [3744, 936, 936, 3744],
  rows: [
    new TableRow({
      children: [
        cell("Asset", { bold: true, shade: NAVY, color: WHITE, width: 3744 }),
        cell("Score", { bold: true, shade: NAVY, color: WHITE, width: 936, align: AlignmentType.CENTER }),
        cell("/ 100", { bold: true, shade: NAVY, color: WHITE, width: 936, align: AlignmentType.CENTER }),
        cell("Verdict", { bold: true, shade: NAVY, color: WHITE, width: 3744 }),
      ]
    }),
    ...assets.map((a, i) => new TableRow({
      children: [
        cell(a.name, { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 3744 }),
        cell(String(a.score), { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 936, align: AlignmentType.CENTER, bold: true }),
        cell("/ 100", { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 936, align: AlignmentType.CENTER, color: "888888" }),
        cell(a.verdict, { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 3744, bold: true, color: verdictColor(a.verdict) }),
      ]
    }))
  ]
});
children.push(summaryTable);
children.push(divider());

// Per-asset sections
for (const asset of assets) {
  children.push(hdr(`${asset.name}`, HeadingLevel.HEADING_1));
  children.push(para(`${asset.id}  |  ${asset.jurisdiction}, ${asset.province}  |  ${asset.commodity}`, { color: "666666" }));
  children.push(new Paragraph({ spacing: { before: 60, after: 60 }, children: [] }));

  // Score banner
  const bannerTable = new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [4680, 4680],
    rows: [new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: NAVY, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ children: [new TextRun({ text: "INVESTMENT READINESS SCORE", bold: true, size: 18, color: "AAAAAA", font: "Arial" })] }),
            new Paragraph({ children: [new TextRun({ text: `${asset.score} / 100`, bold: true, size: 52, color: AMBER, font: "Arial" })] }),
          ]
        }),
        new TableCell({
          borders: noBorders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: AMBER, type: ShadingType.CLEAR },
          margins: { top: 120, bottom: 120, left: 200, right: 200 },
          children: [
            new Paragraph({ children: [new TextRun({ text: "VERDICT", bold: true, size: 18, color: NAVY, font: "Arial" })] }),
            new Paragraph({ children: [new TextRun({ text: asset.verdict, bold: true, size: 36, color: NAVY, font: "Arial" })] }),
          ]
        }),
      ]
    })]
  });
  children.push(bannerTable);
  children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));

  // Dimension scores table
  children.push(hdr("Dimension Scores", HeadingLevel.HEADING_2));
  const dimTable = new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [624, 3276, 624, 1872, 2964],
    rows: [
      new TableRow({
        children: [
          cell("Code", { bold: true, shade: NAVY, color: WHITE, width: 624 }),
          cell("Dimension", { bold: true, shade: NAVY, color: WHITE, width: 3276 }),
          cell("Wt", { bold: true, shade: NAVY, color: WHITE, width: 624, align: AlignmentType.CENTER }),
          cell("Score", { bold: true, shade: NAVY, color: WHITE, width: 1872, align: AlignmentType.CENTER }),
          cell("Bar", { bold: true, shade: NAVY, color: WHITE, width: 2964 }),
        ]
      }),
      ...asset.dimensions.map((d, i) => new TableRow({
        children: [
          cell(d.code, { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 624, bold: true }),
          cell(d.name, { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 3276 }),
          cell(d.weight, { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 624, align: AlignmentType.CENTER, color: "666666" }),
          cell(`${d.score}`, { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 1872, align: AlignmentType.CENTER, bold: true }),
          cell(scoreBar(d.score), { shade: i % 2 === 0 ? LIGHT_GREY : WHITE, width: 2964, color: AMBER, size: 16 }),
        ]
      }))
    ]
  });
  children.push(dimTable);
  children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));

  // Key findings
  children.push(hdr("Key Findings", HeadingLevel.HEADING_2));
  for (const f of asset.key_findings) {
    children.push(new Paragraph({
      spacing: { before: 60, after: 60 },
      numbering: { reference: "bullets", level: 0 },
      children: [new TextRun({ text: f, size: 20, color: "333333", font: "Arial" })]
    }));
  }

  // Data gaps
  if (asset.data_gaps.length > 0) {
    children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));
    children.push(hdr("Data Gaps", HeadingLevel.HEADING_2));
    for (const g of asset.data_gaps) {
      children.push(new Paragraph({
        spacing: { before: 60, after: 60 },
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun({ text: g, size: 20, color: "CC6600", font: "Arial" })]
      }));
    }
  }

  // Next action
  children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));
  children.push(hdr("Next Action", HeadingLevel.HEADING_2));
  children.push(para(asset.next_action, { bold: true, color: verdictColor(asset.verdict) }));

  children.push(divider());
}

// Reviewer instructions
children.push(hdr("Instructions for Independent Reviewers"));
children.push(para(
  "SEAM produces deterministic scores. If you believe any score is wrong, the correct response is to identify the specific data input or rule that should be changed, not to override the score. SEAM distinguishes between two types of reviewer feedback:"
));
children.push(new Paragraph({
  spacing: { before: 80, after: 40 },
  numbering: { reference: "numbers", level: 0 },
  children: [new TextRun({ text: "Data correction — a specific public source records a different value than what SEAM has used. Identify the source, the field and the correct value.", size: 20, color: "333333", font: "Arial" })]
}));
children.push(new Paragraph({
  spacing: { before: 40, after: 80 },
  numbering: { reference: "numbers", level: 0 },
  children: [new TextRun({ text: "Rule disagreement — a scoring rule produces an outcome that does not reflect investment reality. Identify the rule code, explain why it is wrong, and propose an alternative formulation.", size: 20, color: "333333", font: "Arial" })]
}));
children.push(para(
  "Feedback that says only 'this score feels wrong' cannot be incorporated. Feedback that says 'D3-RES-001 should give partial credit for a SAMREC estimate under 3 years' can be."
));
children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));

const reviewTable = new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [2340, 7020],
  rows: [
    new TableRow({ children: [
      cell("Reviewer", { bold: true, shade: NAVY, color: WHITE, width: 2340 }),
      cell("Primary assessment focus", { bold: true, shade: NAVY, color: WHITE, width: 7020 }),
    ]}),
    new TableRow({ children: [
      cell("Anthony Mukutuma (AM-001)", { shade: LIGHT_GREY, width: 2340 }),
      cell("Operational accuracy — do the scores reflect ground-level reality for these assets?", { shade: LIGHT_GREY, width: 7020 }),
    ]}),
    new TableRow({ children: [
      cell("Mining Finance Reviewer", { width: 2340 }),
      cell("Investor utility — are these scores useful for an investment committee discussion?", { width: 7020 }),
    ]}),
    new TableRow({ children: [
      cell("DFI / Governance Reviewer", { shade: LIGHT_GREY, width: 2340 }),
      cell("Governance credibility — does the methodology meet institutional due diligence standards?", { shade: LIGHT_GREY, width: 7020 }),
    ]}),
  ]
});
children.push(reviewTable);
children.push(new Paragraph({ spacing: { before: 120, after: 60 }, children: [] }));
children.push(para(
  "Sprint 1 gate: at least two of three reviewers confirm the scores are credible enough to influence an investment committee discussion. If the gate passes, SEAM proceeds to Sprint 2 — automated data retrieval.",
  { color: "555555" }
));
children.push(divider());
children.push(para("SEAM  |  akinmade.co.uk  |  Structured Evidence for African Mining  |  CONFIDENTIAL", { color: "999999", size: 18 }));
children.push(para("Methodology SEAM-M-v1.0  |  Rules SEAM-R-v1.0  |  June 2026  |  Not for distribution", { color: "999999", size: 18 }));

// ── ASSEMBLE ────────────────────────────────────────────────────────────────

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
      },
      {
        reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }]
      },
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "SEAM  |  Sprint 1 Review  |  CONFIDENTIAL  |  Page ", size: 16, color: "999999", font: "Arial" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "999999", font: "Arial" }),
          ]
        })]
      })
    },
    children
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("/mnt/user-data/outputs/SEAM_Sprint1_Review_v1_0.docx", buf);
  console.log("Written: SEAM_Sprint1_Review_v1_0.docx");
});
