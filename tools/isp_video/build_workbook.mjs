import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.argv[2] || "D:/Repository/ReadPaper/daily/20260826_后处理调研";
const outputDir = path.join(root, "matrix");
const outPath = path.join(outputDir, "手机录像创新功能机会库.xlsx");
const inspectPath = path.join(outputDir, "手机录像创新功能机会库.xlsx.inspect.ndjson");
const runtimeNodeModules = "C:/Users/xh932/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";

async function readJson(file) {
  return JSON.parse(await fs.readFile(file, "utf8"));
}

async function readJsonl(file) {
  const text = await fs.readFile(file, "utf8");
  return text.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
}

function matrix(rows, keys) {
  return rows.map((row) => keys.map((key) => {
    const value = row[key];
    if (Array.isArray(value)) return value.join("; ");
    if (value === undefined || value === null) return "";
    return value;
  }));
}

function setHeader(sheet, range, fill = "#0B3A53") {
  sheet.getRange(range).format = {
    fill,
    font: { bold: true, color: "#FFFFFF", name: "Microsoft YaHei" },
    wrapText: true,
    verticalAlignment: "center",
    horizontalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#B7C9D3" },
  };
}

function setBody(sheet, range) {
  sheet.getRange(range).format = {
    font: { name: "Microsoft YaHei", color: "#1F2933" },
    wrapText: true,
    verticalAlignment: "top",
    borders: { insideHorizontal: { style: "thin", color: "#D9E3E8" }, insideVertical: { style: "thin", color: "#D9E3E8" } },
  };
}

function addTable(sheet, range, name) {
  const table = sheet.tables.add(range, true, name);
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  table.showBandedColumns = false;
  return table;
}

function configureDataSheet(sheet, headers, rows, tableName, widths = {}) {
  const endCol = String.fromCharCode(64 + headers.length);
  const endRow = rows.length + 1;
  sheet.getRange(`A1:${endCol}${endRow}`).values = [headers, ...rows];
  setHeader(sheet, `A1:${endCol}1`);
  setBody(sheet, `A2:${endCol}${endRow}`);
  sheet.getRange(`A1:${endCol}1`).format.rowHeight = 34;
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  addTable(sheet, `A1:${endCol}${endRow}`, tableName);
  for (const [col, width] of Object.entries(widths)) sheet.getRange(`${col}:${col}`).format.columnWidth = width;
  return { endCol, endRow };
}

const [config, opportunities, deepDive, priority, manifest, papers, corePapers, datasets, patents] = await Promise.all([
  readJson(path.join(root, "metadata/project_config.json")),
  readJsonl(path.join(root, "metadata/opportunities.jsonl")),
  readJsonl(path.join(root, "metadata/deep_dive_30.jsonl")),
  readJsonl(path.join(root, "metadata/priority_10.jsonl")),
  readJson(path.join(root, "sources/source_manifest.json")),
  readJsonl(path.join(root, "sources/papers/paper_records.jsonl")),
  readJsonl(path.join(root, "sources/papers/core_paper_records.jsonl")),
  readJsonl(path.join(root, "sources/datasets/dataset_records.jsonl")),
  readJsonl(path.join(root, "sources/patents/patent_records.jsonl")),
]);

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const opportunitySheet = workbook.worksheets.add("Opportunity_Map");
const deepSheet = workbook.worksheets.add("Deep_Dive_30");
const prioritySheet = workbook.worksheets.add("Priority_10");
const prototypeSheet = workbook.worksheets.add("Industry_Prototypes");
const paperSheet = workbook.worksheets.add("Papers");
const paperDiscoverySheet = workbook.worksheets.add("Paper_Discovery_381");
const patentSheet = workbook.worksheets.add("Patents");
const datasetSheet = workbook.worksheets.add("Datasets");
const sourceSheet = workbook.worksheets.add("Source_Manifest");

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["手机录像创新功能机会图谱 | ISP 后处理调研"]];
summary.getRange("A1:H1").format = { fill: "#0B3A53", font: { bold: true, color: "#FFFFFF", size: 16, name: "Microsoft YaHei" }, horizontalAlignment: "left", verticalAlignment: "center" };
summary.getRange("A1:H1").format.rowHeight = 32;
summary.getRange("A3:B11").values = [
  ["统计项", "数量"],
  ["候选机会", opportunities.length],
  ["技术深挖", deepDive.length],
  ["组合创新", priority.length],
  ["核心论文", corePapers.length],
  ["论文发现池", papers.length],
  ["数据集", datasets.length],
  ["专利检索主题", patents.length],
  ["来源总数", manifest.length],
];
summary.getRange("D3:E8").values = [
  ["分类", "数量"],
  ["在线录像", opportunities.filter((x) => x.video_mode === "online_recording").length],
  ["录后设备", opportunities.filter((x) => x.video_mode === "offline_device").length],
  ["忠实增强", opportunities.filter((x) => x.truth_boundary === "faithful").length],
  ["感知增强", opportunities.filter((x) => x.truth_boundary === "perceptual").length],
  ["生成式创作", opportunities.filter((x) => x.truth_boundary === "generative").length],
];
summary.getRange("A3:B3").format = { fill: "#DDEBF2", font: { bold: true, name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#9FBAD0" } };
summary.getRange("D3:E3").format = { fill: "#DDEBF2", font: { bold: true, name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#9FBAD0" } };
summary.getRange("A4:B11").format = { font: { name: "Microsoft YaHei", color: "#1F2933" }, borders: { preset: "all", style: "thin", color: "#D9E3E8" } };
summary.getRange("D4:E8").format = { font: { name: "Microsoft YaHei", color: "#1F2933" }, borders: { preset: "all", style: "thin", color: "#D9E3E8" } };
summary.getRange("A13:H13").merge();
summary.getRange("A13").values = [["口径：E1-E4 是外部产品/论文/专利证据；E5 是本报告视频化推演。生成式方向不等同于真实恢复，所有关键方案都需保留原片和可回退信息。"]];
summary.getRange("A13:H13").format = { fill: "#FFF4D6", font: { name: "Microsoft YaHei", color: "#7A4B00" }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A13:H13").format.rowHeight = 42;
summary.getRange("A15:B15").values = [["能力族", "候选数"]];
const familyRows = Object.entries(opportunities.reduce((acc, x) => { acc[x.family_zh] = (acc[x.family_zh] || 0) + 1; return acc; }, {}));
summary.getRange(`A16:B${15 + familyRows.length}`).values = familyRows;
summary.getRange("A15:B15").format = { fill: "#DDEBF2", font: { bold: true, name: "Microsoft YaHei" } };
summary.getRange(`A16:B${15 + familyRows.length}`).format = { font: { name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#D9E3E8" } };
summary.getRange("A:A").format.columnWidth = 28;
summary.getRange("B:B").format.columnWidth = 12;
summary.getRange("D:D").format.columnWidth = 18;
summary.getRange("E:E").format.columnWidth = 12;
summary.getRange("A1:H40").format.font.name = "Microsoft YaHei";

const opportunityHeaders = ["ID", "功能名称", "English", "能力族", "场景", "来源类型", "证据等级", "原型状态", "录像形态", "输入信号", "算法链路位置", "算法族", "时序策略", "数据需求", "LOSS/目标", "评价指标", "失败模式", "真实性边界", "新颖度", "录像适配度", "端侧可行性", "产品差异化", "风险", "优先级", "证据ID", "备注", "核验日期"];
configureDataSheet(opportunitySheet, opportunityHeaders, matrix(opportunities, ["id", "name_zh", "name_en", "family_zh", "scenarios", "source_type", "evidence_level", "prototype_status", "video_mode", "input_signals", "pipeline_stage", "algorithm_family", "temporal_strategy", "data_needs", "loss_or_objective", "quality_metrics", "failure_modes", "truth_boundary", "novelty", "video_fit", "edge_feasibility", "product_differentiation", "risk", "priority", "evidence_ids", "notes", "last_verified"]), "OpportunityTable", {"A": 10, "B": 24, "C": 28, "D": 18, "E": 24, "F": 18, "G": 10, "H": 18, "I": 16, "J": 24, "K": 22, "L": 24, "M": 30, "N": 32, "O": 36, "P": 28, "Q": 28, "R": 14, "S": 10, "T": 12, "U": 14, "V": 14, "W": 28, "X": 10, "Y": 24, "Z": 44, "AA": 14});

const deepHeaders = ["Deep Dive ID", "Opportunity ID", "标题", "English", "能力族", "模式", "真实性边界", "证据ID", "研究问题", "技术方案", "输入信号", "模型链路", "训练数据", "LOSS/目标", "时序策略", "端侧落点", "风险", "MVP", "核验日期"];
configureDataSheet(deepSheet, deepHeaders, matrix(deepDive, ["deep_dive_id", "op_id", "title", "english", "family", "mode", "truth", "source_ids", "problem", "solution", "inputs", "model", "training", "loss", "temporal", "edge", "risks", "mvp", "last_verified"]), "DeepDiveTable", {"A": 14, "B": 12, "C": 24, "D": 32, "E": 18, "F": 16, "G": 14, "H": 28, "I": 36, "J": 44, "K": 34, "L": 42, "M": 42, "N": 44, "O": 36, "P": 34, "Q": 36, "R": 34, "S": 14});

const priorityHeaders = ["Concept ID", "名称", "English", "组成深挖", "用户故事", "交互", "系统链路", "MVP", "数据", "指标", "风险", "真实性边界"];
configureDataSheet(prioritySheet, priorityHeaders, matrix(priority, ["concept_id", "name", "english", "components", "user_story", "interaction", "pipeline", "mvp", "data", "metrics", "risk", "truth_boundary"]), "PriorityTable", {"A": 14, "B": 24, "C": 30, "D": 22, "E": 42, "F": 34, "G": 48, "H": 38, "I": 40, "J": 34, "K": 36, "L": 20});

const prototypes = manifest.filter((x) => x.source_type === "official_product" || x.source_type === "manual" || x.source_type === "demo");
const prototypeHeaders = ["来源ID", "厂商/作者", "产品/平台", "原型名称", "来源类型", "证据等级", "核验状态", "证据摘要", "边界说明", "URL", "本地缓存"];
configureDataSheet(prototypeSheet, prototypeHeaders, matrix(prototypes, ["source_id", "publisher_or_authors", "product_or_venue", "title", "source_type", "evidence_level", "verification_status", "evidence_quote", "scope_limit", "url", "local_path"]), "PrototypeTable", {"A": 32, "B": 22, "C": 28, "D": 30, "E": 18, "F": 10, "G": 16, "H": 48, "I": 42, "J": 52, "K": 58});

const patentHeaders = ["Patent ID", "标题", "申请人/权利人", "状态", "能力族", "摘要", "URL", "本地缓存", "核验状态", "证据等级"];
configureDataSheet(patentSheet, patentHeaders, matrix(patents, ["patent_id", "title", "assignee", "status", "family", "abstract", "url", "local_path", "verification_status", "evidence_level"]), "PatentTable", {"A": 22, "B": 42, "C": 28, "D": 14, "E": 26, "F": 60, "G": 52, "H": 48, "I": 18, "J": 12});

const datasetHeaders = ["数据集ID", "名称", "用途/说明", "官方地址", "本地文档", "访问/许可", "核验状态"];
configureDataSheet(datasetSheet, datasetHeaders, matrix(datasets, ["dataset_id", "name", "task", "official_url", "local_doc", "license_or_access", "verification_status"]), "DatasetTable", {"A": 22, "B": 34, "C": 50, "D": 48, "E": 48, "F": 42, "G": 22});

const corePaperHeaders = ["Canonical ID", "标题", "年份", "会议/期刊", "作者", "DOI/URL", "论文地址", "本地路径", "能力族", "为什么相关", "核验状态", "证据等级"];
configureDataSheet(paperSheet, corePaperHeaders, matrix(corePapers, ["canonical_id", "title", "year", "venue", "authors", "doi", "url", "local_path", "family", "why_relevant", "verification_status", "evidence_level"]), "CorePaperTable", {"A": 28, "B": 46, "C": 10, "D": 28, "E": 28, "F": 38, "G": 42, "H": 64, "I": 22, "J": 60, "K": 24, "L": 12});

const discoveryPaperHeaders = ["Canonical ID", "标题", "年份", "会议/期刊", "作者", "DOI", "开放获取", "PDF URL", "搜索主题", "摘要节选", "OpenAlex ID", "元数据状态", "主题筛选状态"];
const discoveryPaperRows = papers.map((row) => {
  const abstract = row.abstract || "";
  const abstractExcerpt = abstract.length > 180 ? `${abstract.slice(0, 180)}...` : abstract;
  return [
    row.canonical_id,
    row.title,
    row.publication_year,
    row.venue,
    Array.isArray(row.authors) ? row.authors.join("; ") : row.authors,
    row.doi,
    row.open_access,
    row.pdf_url,
    row.search_query,
    abstractExcerpt,
    row.openalex_id,
    row.verification_status,
    "宽搜候选，待主题筛选与正文核验",
  ];
});
configureDataSheet(paperDiscoverySheet, discoveryPaperHeaders, discoveryPaperRows, "PaperDiscoveryTable", {"A": 30, "B": 44, "C": 10, "D": 28, "E": 32, "F": 34, "G": 12, "H": 52, "I": 24, "J": 56, "K": 30, "L": 18, "M": 30});

const sourceHeaders = ["来源ID", "来源类型", "标题", "厂商/作者", "产品/会议", "日期", "证据等级", "访问状态", "核验状态", "证据摘要", "边界说明", "URL", "本地路径", "SHA256", "检索时间"];
configureDataSheet(sourceSheet, sourceHeaders, matrix(manifest, ["source_id", "source_type", "title", "publisher_or_authors", "product_or_venue", "date", "evidence_level", "access_status", "verification_status", "evidence_quote", "scope_limit", "url", "local_path", "sha256", "retrieved_at"]), "SourceTable", {"A": 32, "B": 18, "C": 42, "D": 24, "E": 28, "F": 14, "G": 10, "H": 20, "I": 18, "J": 54, "K": 54, "L": 52, "M": 64, "N": 68, "O": 26});

for (const sheet of [opportunitySheet, deepSheet, prioritySheet, prototypeSheet, paperSheet, paperDiscoverySheet, datasetSheet, patentSheet, sourceSheet]) {
  const used = sheet.getUsedRange();
  used.format.font.name = "Microsoft YaHei";
}

await fs.mkdir(outputDir, { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outPath);

const inspect = [];
inspect.push((await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 12000, tableMaxRows: 5, tableMaxCols: 8 })).ndjson);
inspect.push((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" })).ndjson);
inspect.push(JSON.stringify({ sheet_counts: { opportunities: opportunities.length, deep_dive: deepDive.length, priority: priority.length, prototypes: prototypes.length, core_papers: corePapers.length, paper_discovery: papers.length, patents: patents.length, datasets: datasets.length, sources: manifest.length }, outPath }, null, 2));
await fs.writeFile(inspectPath, inspect.join("\n"), "utf8");
console.log(JSON.stringify({ outPath, inspectPath, opportunities: opportunities.length, deepDive: deepDive.length, priority: priority.length, corePapers: corePapers.length, discoveryPapers: papers.length, datasets: datasets.length, patents: patents.length, sources: manifest.length }, null, 2));
