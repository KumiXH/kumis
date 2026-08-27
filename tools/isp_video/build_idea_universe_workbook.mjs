import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.argv[2] || "D:/Repository/ReadPaper/daily/20260826_后处理调研";
const metadataDir = path.join(root, "metadata", "idea_universe");
const outputDir = path.join(root, "matrix");
const outputPath = path.join(outputDir, "手机录像后处理_IDEA全量宇宙_20260827.xlsx");
const inspectPath = `${outputPath}.inspect.ndjson`;

async function readJson(file) {
  return JSON.parse(await fs.readFile(file, "utf8"));
}

async function readJsonl(file) {
  return (await fs.readFile(file, "utf8")).split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
}

function value(row, key) {
  const item = row[key];
  if (Array.isArray(item)) return item.join("; ");
  if (item === undefined || item === null) return "";
  return item;
}

function colName(index) {
  let value = index;
  let result = "";
  while (value > 0) {
    value -= 1;
    result = String.fromCharCode(65 + (value % 26)) + result;
    value = Math.floor(value / 26);
  }
  return result;
}

function setHeader(sheet, range) {
  sheet.getRange(range).format = {
    fill: "#0B3A53",
    font: { bold: true, color: "#FFFFFF", name: "Microsoft YaHei" },
    wrapText: true,
    verticalAlignment: "center",
    horizontalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#9FBAD0" },
  };
}

function setBody(sheet, range) {
  sheet.getRange(range).format = {
    font: { name: "Microsoft YaHei", color: "#1F2933" },
    wrapText: true,
    verticalAlignment: "top",
    borders: {
      insideHorizontal: { style: "thin", color: "#D9E3E8" },
      insideVertical: { style: "thin", color: "#D9E3E8" },
    },
  };
}

function configureTable(sheet, headers, rows, tableName, widths) {
  const endCol = colName(headers.length);
  const endRow = rows.length + 1;
  sheet.getRange(`A1:${endCol}${endRow}`).values = [headers, ...rows];
  setHeader(sheet, `A1:${endCol}1`);
  setBody(sheet, `A2:${endCol}${endRow}`);
  sheet.getRange(`A1:${endCol}1`).format.rowHeight = 34;
  sheet.freezePanes.freezeRows(1);
  sheet.showGridLines = false;
  const table = sheet.tables.add(`A1:${endCol}${endRow}`, true, tableName);
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  for (const [column, width] of Object.entries(widths)) {
    sheet.getRange(`${column}:${column}`).format.columnWidth = width;
  }
  return { endCol, endRow };
}

const [ideas, variants, stats] = await Promise.all([
  readJsonl(path.join(metadataDir, "core_ideas.jsonl")),
  readJsonl(path.join(metadataDir, "idea_variants.jsonl")),
  readJson(path.join(metadataDir, "idea_universe_stats.json")),
]);

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const core = workbook.worksheets.add("Core_Ideas");
const variantSheet = workbook.worksheets.add("Variants");
const legacySheet = workbook.worksheets.add("Legacy_112");
const newSheet = workbook.worksheets.add("New_Ideas");
const familySheet = workbook.worksheets.add("By_Family");
const sceneSheet = workbook.worksheets.add("By_Scene");
const dictionarySheet = workbook.worksheets.add("Variant_Dictionary");

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["手机录像后处理 IDEA 全量宇宙 | 2026-08-27"]];
summary.getRange("A1:H1").format = {
  fill: "#0B3A53",
  font: { bold: true, color: "#FFFFFF", size: 16, name: "Microsoft YaHei" },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
summary.getRange("A1:H1").format.rowHeight = 34;
summary.getRange("A3:B10").values = [
  ["统计项", "数量"],
  ["基础 IDEA", stats.counts.core_ideas],
  ["单轴变体", stats.counts.variants],
  ["既有方向", stats.counts.legacy_ideas],
  ["此前重点方向", stats.counts.prior_brainstorm],
  ["新增原生创意", stats.counts.new_native_ideas],
  ["变体轴", stats.counts.variant_axes],
  ["单轴取值", stats.counts.variant_values],
];
summary.getRange("D3:E7").values = [
  ["真实性", "基础 IDEA 数"],
  ["faithful", stats.by_truth.faithful || 0],
  ["perceptual", stats.by_truth.perceptual || 0],
  ["generative", stats.by_truth.generative || 0],
  ["idea_only", stats.counts.core_ideas],
];
summary.getRange("A3:B3").format = { fill: "#DDEBF2", font: { bold: true, name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#9FBAD0" } };
summary.getRange("D3:E3").format = { fill: "#DDEBF2", font: { bold: true, name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#9FBAD0" } };
summary.getRange("A4:B10").format = { font: { name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#D9E3E8" } };
summary.getRange("D4:E7").format = { font: { name: "Microsoft YaHei" }, borders: { preset: "all", style: "thin", color: "#D9E3E8" } };
summary.getRange("A12:H13").merge();
summary.getRange("A12").values = [["边界：本工作簿是创意池，不代表论文结论、量产能力或端侧性能。基础 IDEA 与实现变体分开记录；旧 112 条方向全部保留。"]];
summary.getRange("A12:H13").format = { fill: "#FFF4D6", font: { name: "Microsoft YaHei", color: "#7A4B00" }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A12:H13").format.rowHeight = 28;
const familyRows = Object.entries(stats.by_family).sort((a, b) => b[1] - a[1]);
summary.getRange("A15:B15").values = [["能力族", "基础 IDEA 数"]];
summary.getRange(`A16:B${15 + familyRows.length}`).values = familyRows;
setHeader(summary, "A15:B15");
setBody(summary, `A16:B${15 + familyRows.length}`);
summary.getRange("A:A").format.columnWidth = 32;
summary.getRange("B:B").format.columnWidth = 14;
summary.getRange("D:D").format.columnWidth = 20;
summary.getRange("E:E").format.columnWidth = 14;
summary.getRange("A1:H60").format.font.name = "Microsoft YaHei";

const ideaHeaders = ["Idea ID", "旧ID", "功能名称", "能力族", "创意簇", "来源层", "用户效果", "核心机制", "手机独有价值", "输入信号", "适用场景", "默认真实性", "时序跨度", "风险", "标签", "状态"];
const ideaRows = ideas.map((row) => [
  value(row, "idea_id"), value(row, "legacy_id"), value(row, "name_zh"), value(row, "family_zh"),
  value(row, "cluster_zh"), value(row, "source_layer"), value(row, "user_effect"), value(row, "core_mechanism"),
  value(row, "mobile_unique_value"), value(row, "input_signals"), value(row, "scenarios"), value(row, "default_truth"),
  value(row, "temporal_span"), value(row, "risks"), value(row, "tags"), value(row, "status"),
]);
const ideaWidths = { A: 18, B: 12, C: 34, D: 24, E: 28, F: 22, G: 54, H: 50, I: 48, J: 34, K: 30, L: 16, M: 18, N: 34, O: 36, P: 28 };
configureTable(core, ideaHeaders, ideaRows, "CoreIdeaTable", ideaWidths);

const variantHeaders = ["Variant ID", "基础 Idea ID", "基础名称", "能力族", "创意簇", "变体轴", "轴中文", "变体值", "值中文", "变体名称", "实现解释", "基础真实性", "来源层", "状态"];
const variantRows = variants.map((row) => [
  value(row, "variant_id"), value(row, "base_idea_id"), value(row, "base_name_zh"), value(row, "family_zh"),
  value(row, "idea_cluster"), value(row, "variant_axis"), value(row, "variant_axis_zh"), value(row, "variant_value"),
  value(row, "variant_value_zh"), value(row, "variant_name_zh"), value(row, "implementation_note"), value(row, "base_truth"),
  value(row, "source_layer"), value(row, "status"),
]);
configureTable(variantSheet, variantHeaders, variantRows, "VariantIdeaTable", { A: 18, B: 18, C: 34, D: 24, E: 24, F: 22, G: 16, H: 22, I: 18, J: 42, K: 72, L: 16, M: 22, N: 24 });

const legacyIdeas = ideas.filter((row) => row.source_layer === "legacy_112");
configureTable(legacySheet, ideaHeaders, legacyIdeas.map((row) => ideaRows[ideas.indexOf(row)]), "LegacyIdeaTable", ideaWidths);

const newIdeas = ideas.filter((row) => row.source_layer !== "legacy_112");
configureTable(newSheet, ideaHeaders, newIdeas.map((row) => ideaRows[ideas.indexOf(row)]), "NewIdeaTable", ideaWidths);

const familyMap = new Map();
for (const idea of ideas) {
  const current = familyMap.get(idea.family_zh) || { count: 0, legacy: 0, prior: 0, fresh: 0, clusters: new Set(), samples: [] };
  current.count += 1;
  if (idea.source_layer === "legacy_112") current.legacy += 1;
  if (idea.source_layer === "prior_brainstorm") current.prior += 1;
  if (idea.source_layer === "new_native_idea") current.fresh += 1;
  current.clusters.add(idea.cluster_zh);
  if (current.samples.length < 8) current.samples.push(idea.name_zh);
  familyMap.set(idea.family_zh, current);
}
const familySummary = Array.from(familyMap.entries()).sort((a, b) => b[1].count - a[1].count).map(([name, item]) => [name, item.count, item.legacy, item.prior, item.fresh, Array.from(item.clusters).join("; "), item.samples.join("; ")]);
configureTable(familySheet, ["能力族", "总数", "既有", "此前重点", "新增", "创意簇", "示例"], familySummary, "FamilyTable", { A: 30, B: 12, C: 10, D: 12, E: 12, F: 50, G: 72 });

const sceneMap = new Map();
for (const idea of ideas) {
  for (const scene of idea.scenarios) {
    const current = sceneMap.get(scene) || { count: 0, families: new Set(), samples: [] };
    current.count += 1;
    current.families.add(idea.family_zh);
    if (current.samples.length < 10) current.samples.push(idea.name_zh);
    sceneMap.set(scene, current);
  }
}
const sceneRows = Array.from(sceneMap.entries()).sort((a, b) => b[1].count - a[1].count).map(([name, item]) => [name, item.count, Array.from(item.families).join("; "), item.samples.join("; ")]);
configureTable(sceneSheet, ["场景", "基础 IDEA 数", "涉及能力族", "示例"], sceneRows, "SceneTable", { A: 24, B: 16, C: 60, D: 80 });

const dictionaryRows = [];
for (const [axis, info] of Object.entries({
  processing_stage: { label: "处理阶段", values: [["preview", "实时预览"], ["online_recording", "录制在线"], ["offline_device", "录后端侧"], ["cloud_render", "云端高质量"]] },
  truth_boundary: { label: "真实性边界", values: [["faithful", "忠实恢复"], ["perceptual", "感知增强"], ["generative", "生成式创作"]] },
  input_mode: { label: "输入信号", values: [["single_camera", "单摄"], ["dual_camera", "双摄"], ["depth", "深度"], ["imu", "IMU"], ["audio", "音频"], ["multi_device", "多设备"]] },
  scene: { label: "用户场景", values: [["portrait", "人像"], ["pet", "宠物"], ["children", "儿童"], ["sports", "运动"], ["night", "夜景"], ["concert", "演唱会"], ["travel", "旅行"], ["live", "直播"]] },
  temporal_spec: { label: "时间规格", values: [["30fps", "30 fps"], ["60fps", "60 fps"], ["high_fps", "高帧率慢动作"], ["long_recording", "长时间录像"]] },
  processing_scope: { label: "处理范围", values: [["full_frame", "全画面"], ["roi", "ROI"], ["keyframe", "关键帧"], ["proxy", "低功耗代理"]] },
  delivery: { label: "交付形态", values: [["instant_share", "即时分享"], ["master", "专业母版"], ["editable_project", "可编辑工程"], ["edge_cloud", "端云协同"]] },
})) {
  for (const [valueCode, valueLabel] of info.values) {
    dictionaryRows.push([axis, info.label, valueCode, valueLabel, "单轴变体；不改变基础 IDEA 的核心用户效果"]);
  }
}
configureTable(dictionarySheet, ["轴代码", "轴中文", "值代码", "值中文", "说明"], dictionaryRows, "VariantDictionaryTable", { A: 24, B: 20, C: 24, D: 24, E: 54 });

for (const sheet of [core, variantSheet, legacySheet, newSheet, familySheet, sceneSheet, dictionarySheet]) {
  sheet.getUsedRange().format.font.name = "Microsoft YaHei";
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
const inspect = [];
inspect.push((await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 16000, tableMaxRows: 3, tableMaxCols: 8, tableMaxCellChars: 100 })).ndjson);
inspect.push((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, summary: "formula error scan" })).ndjson);
inspect.push(JSON.stringify({ outputPath, core_ideas: ideas.length, variants: variants.length, legacy: legacyIdeas.length, new_ideas: newIdeas.length, families: familyRows.length, scenes: sceneRows.length }, null, 2));
await fs.writeFile(inspectPath, inspect.join("\n"), "utf8");
console.log(JSON.stringify({ outputPath, inspectPath, coreIdeas: ideas.length, variants: variants.length, legacy: legacyIdeas.length, newIdeas: newIdeas.length }, null, 2));
