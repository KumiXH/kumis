import fs from "node:fs/promises";
import path from "node:path";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = process.argv[2] || "D:/Repository/ReadPaper/.codex_worktrees/video_effects_20260828";
const projectRoot = path.join(repoRoot, "daily", "20260827_录像特效调研");
const outputDir = path.join(projectRoot, "matrix");
const outputPath = path.join(outputDir, "手机录像特效玩法库_20260827.xlsx");
const inspectPath = path.join(outputDir, "手机录像特效玩法库_20260827.inspect.ndjson");

const FAMILY_LABELS = {
  light_trails_optics: "光轨与可编程光学",
  body_motion_clones: "身体运动与分身",
  face_gaze_expression: "面部、视线与表情",
  time_editing: "局部时间编辑",
  spatial_portals: "空间入口与传送门",
  virtual_light_shadow: "虚拟光影",
  material_morph: "材质变形",
  particles_weather: "粒子与天气",
  world_style: "世界风格化",
  audio_lyrics: "音频与歌词",
  effect_cinematography: "特效摄影",
  multi_person_interaction: "多人互动",
};

const TRIGGER_RULES = [
  ["触摸/拖拽", /触摸|拖动|点按|按下|tap|touch/i],
  ["手势/手部", /手势|手掌|指尖|双手|手部|gesture|hand/i],
  ["视线/眨眼", /视线|凝视|眨眼|瞳孔|虹膜|gaze|eye/i],
  ["音频/节拍", /音频|节拍|强拍|人声|歌词|说话|声音|beat|audio|voice/i],
  ["人体/姿态", /人体|身体|姿态|动作|脚步|转身|走位|pose|body/i],
  ["对象/光源", /物体|对象|主体|光源|灯棒|目标|object|subject/i],
  ["空间/深度", /平面|深度|镜面|地面|墙面|空间|portal|depth/i],
  ["相机/设备运动", /手机|镜头|相机|旋转|平移|变焦|camera|zoom/i],
];

async function readJsonl(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  return text.split(/\r?\n/).filter(Boolean).map((line) => JSON.parse(line));
}

function joinValue(value) {
  if (Array.isArray(value)) return value.join("；");
  if (value === undefined || value === null) return "";
  return value;
}

function classifyTrigger(idea) {
  const text = [...idea.trigger_signals, idea.interaction, ...idea.required_signals].join(" ");
  const hit = TRIGGER_RULES.find(([, pattern]) => pattern.test(text));
  return hit ? hit[0] : "自动/场景事件";
}

function excelCol(index) {
  let number = index + 1;
  let result = "";
  while (number > 0) {
    const remainder = (number - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    number = Math.floor((number - 1) / 26);
  }
  return result;
}

function matrix(rows, keys) {
  return rows.map((row) => keys.map((key) => joinValue(row[key])));
}

function setHeader(sheet, range) {
  sheet.getRange(range).format = {
    fill: "#16324F",
    font: { name: "Microsoft YaHei", color: "#FFFFFF", bold: true, size: 10 },
    wrapText: true,
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#AFC0CF" },
  };
}

function setBody(sheet, range) {
  sheet.getRange(range).format = {
    font: { name: "Microsoft YaHei", color: "#243447", size: 10 },
    wrapText: true,
    verticalAlignment: "top",
    borders: {
      insideHorizontal: { style: "thin", color: "#D9E1E8" },
      insideVertical: { style: "thin", color: "#E2E8EE" },
    },
  };
}

function configureDataSheet(sheet, headers, rows, tableName, widths = {}) {
  const endCol = excelCol(headers.length - 1);
  const endRow = rows.length + 1;
  sheet.getRange(`A1:${endCol}${endRow}`).values = [headers, ...rows];
  setHeader(sheet, `A1:${endCol}1`);
  if (rows.length) setBody(sheet, `A2:${endCol}${endRow}`);
  sheet.getRange(`A1:${endCol}1`).format.rowHeight = 36;
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

const [atoms, ideas, recipes, priorities, references, storyboards] = await Promise.all([
  readJsonl(path.join(projectRoot, "metadata", "effect_atoms.jsonl")),
  readJsonl(path.join(projectRoot, "metadata", "effect_ideas.jsonl")),
  readJsonl(path.join(projectRoot, "metadata", "effect_recipes.jsonl")),
  readJsonl(path.join(projectRoot, "metadata", "priority_effects.jsonl")),
  readJsonl(path.join(projectRoot, "references", "reference_manifest.jsonl")),
  readJsonl(path.join(projectRoot, "figures", "effect_storyboards", "storyboard_manifest.jsonl")),
]);

const ideaById = new Map(ideas.map((row) => [row.effect_id, row]));
const priorityByEffect = new Map(priorities.map((row) => [row.effect_id, row]));
const storyboardByPriority = new Map(storyboards.map((row) => [row.priority_id, row]));
const referencesByEffect = new Map();
for (const reference of references) {
  for (const effectId of reference.effect_ids) {
    const items = referencesByEffect.get(effectId) || [];
    items.push(reference.reference_id);
    referencesByEffect.set(effectId, items);
  }
}

const enrichedIdeas = ideas.map((idea) => ({
  ...idea,
  family_zh: FAMILY_LABELS[idea.family],
  trigger_class: classifyTrigger(idea),
  priority_id: priorityByEffect.get(idea.effect_id)?.priority_id || "",
  bounded_reference_ids: referencesByEffect.get(idea.effect_id) || [],
}));

const enrichedPriorities = priorities.map((priority) => {
  const idea = ideaById.get(priority.effect_id);
  const storyboard = storyboardByPriority.get(priority.priority_id);
  return {
    ...priority,
    name_zh: idea.name_zh,
    family: idea.family,
    family_zh: FAMILY_LABELS[idea.family],
    visible_effect: idea.visible_effect,
    trigger_class: classifyTrigger(idea),
    generation_level: idea.generation_level,
    edge_difficulty: idea.edge_difficulty,
    reference_ids: referencesByEffect.get(priority.effect_id) || [],
    storyboard_path: storyboard?.image_path || "",
  };
});

const workbook = Workbook.create();
const summary = workbook.worksheets.add("总览");
const atomSheet = workbook.worksheets.add("特效原子");
const ideaSheet = workbook.worksheets.add("完整玩法");
const recipeSheet = workbook.worksheets.add("组合配方");
const prioritySheet = workbook.worksheets.add("重点50");
const referenceSheet = workbook.worksheets.add("真实参考");
const familySheet = workbook.worksheets.add("按特效族");
const triggerSheet = workbook.worksheets.add("按触发方式");
const generationSheet = workbook.worksheets.add("按生成程度");
const dictionarySheet = workbook.worksheets.add("字段字典");

const atomHeaders = ["原子ID", "中文名", "English", "能力族", "原子类型", "可见原语", "所需信号", "时序状态", "可调参数", "失败模式", "端侧说明"];
configureDataSheet(atomSheet, atomHeaders, matrix(atoms, ["atom_id", "name_zh", "name_en", "family", "primitive_type", "visible_primitive", "required_signals", "temporal_state", "parameters", "failure_modes", "mobile_notes"]), "EffectAtomsTable", {
  A: 38, B: 24, C: 32, D: 22, E: 22, F: 46, G: 36, H: 42, I: 30, J: 42, K: 48,
});

const ideaHeaders = ["玩法ID", "中文名", "English", "特效族", "特效族中文", "可见结果", "场景", "目标对象", "空间范围", "触发信号", "触发分类", "交互", "用户控制", "实时预览", "录后重算", "所需信号", "原子ID", "时间窗口", "连续性难点", "端侧难度", "执行目标", "生成程度", "风险", "新颖性", "传播性", "产品价值", "重点ID", "边界参考ID", "组合入口", "状态"];
configureDataSheet(ideaSheet, ideaHeaders, matrix(enrichedIdeas, ["effect_id", "name_zh", "name_en", "family", "family_zh", "visible_effect", "scenarios", "target_objects", "spatial_scope", "trigger_signals", "trigger_class", "interaction", "user_controls", "preview_pipeline", "post_pipeline", "required_signals", "atom_ids", "temporal_window", "continuity_challenges", "edge_difficulty", "execution_targets", "generation_level", "risks", "novelty", "shareability", "product_value", "priority_id", "bounded_reference_ids", "combinable_effect_ids", "status"]), "EffectIdeasTable", {
  A: 42, B: 32, C: 42, D: 24, E: 22, F: 58, G: 28, H: 28, I: 28, J: 40, K: 18, L: 52, M: 28, N: 52, O: 54, P: 38, Q: 54, R: 30, S: 42, T: 14, U: 25, V: 20, W: 46, X: 46, Y: 44, Z: 44, AA: 36, AB: 52, AC: 52, AD: 16,
});

const recipeHeaders = ["配方ID", "中文名", "原子组件", "玩法组件", "触发逻辑", "组合后可见结果", "为什么是新玩法", "预览行为", "录后行为", "风险", "目标场景"];
configureDataSheet(recipeSheet, recipeHeaders, matrix(recipes, ["recipe_id", "name_zh", "component_atom_ids", "component_effect_ids", "trigger_logic", "combined_effect", "why_new", "preview_behavior", "post_behavior", "risks", "target_scenarios"]), "EffectRecipesTable", {
  A: 40, B: 34, C: 54, D: 58, E: 46, F: 56, G: 58, H: 64, I: 68, J: 50, K: 56,
});

const priorityHeaders = ["重点ID", "玩法ID", "中文名", "特效族", "特效族中文", "可见效果", "触发分类", "问题", "体验故事", "交互时间线", "模块链路", "张量/信号流", "预览预算口径", "录制元数据", "录后精修", "可调参数", "失败与降级", "手机产品形态", "生成程度", "端侧难度", "边界参考ID", "概念分镜"];
configureDataSheet(prioritySheet, priorityHeaders, matrix(enrichedPriorities, ["priority_id", "effect_id", "name_zh", "family", "family_zh", "visible_effect", "trigger_class", "problem", "experience_story", "interaction_timeline", "module_pipeline", "tensor_or_signal_flow", "preview_budget", "recorded_metadata", "post_refinement", "adjustable_parameters", "failure_and_fallback", "mobile_product_form", "generation_level", "edge_difficulty", "reference_ids", "storyboard_path"]), "PriorityEffectsTable", {
  A: 38, B: 42, C: 34, D: 24, E: 22, F: 58, G: 20, H: 52, I: 58, J: 64, K: 66, L: 64, M: 50, N: 50, O: 62, P: 46, Q: 62, R: 54, S: 18, T: 14, U: 58, V: 70,
});

const referenceHeaders = ["参考ID", "标题", "来源类型", "产品/作品/论文", "发布方", "年份", "原始来源", "访问状态", "本地证据", "绑定玩法ID", "能够证明", "不能证明", "实现边界", "SHA256"];
configureDataSheet(referenceSheet, referenceHeaders, matrix(references, ["reference_id", "title", "source_type", "product_work_paper", "publisher", "year", "original_source", "access_status", "local_files", "effect_ids", "demonstrates", "does_not_prove", "implementation_boundary", "sha256"]), "RealReferencesTable", {
  A: 40, B: 42, C: 20, D: 44, E: 22, F: 10, G: 52, H: 34, I: 70, J: 64, K: 64, L: 64, M: 24, N: 68,
});

const familyKeys = Object.keys(FAMILY_LABELS);
familySheet.getRange(`A1:G${familyKeys.length + 1}`).values = [
  ["特效族", "中文名", "完整玩法数", "重点案例数", "研究级难度数", "高难度数", "代表重点玩法"],
  ...familyKeys.map((family) => [family, FAMILY_LABELS[family], "", "", "", "", enrichedPriorities.filter((row) => row.family === family).slice(0, 3).map((row) => row.name_zh).join("；")]),
];
for (let row = 2; row <= familyKeys.length + 1; row += 1) {
  familySheet.getRange(`C${row}`).formulas = [[`=COUNTIF('完整玩法'!$D$2:$D$${ideas.length + 1},A${row})`]];
  familySheet.getRange(`D${row}`).formulas = [[`=COUNTIF('重点50'!$D$2:$D$${priorities.length + 1},A${row})`]];
  familySheet.getRange(`E${row}`).formulas = [[`=COUNTIFS('完整玩法'!$D$2:$D$${ideas.length + 1},A${row},'完整玩法'!$T$2:$T$${ideas.length + 1},"research")`]];
  familySheet.getRange(`F${row}`).formulas = [[`=COUNTIFS('完整玩法'!$D$2:$D$${ideas.length + 1},A${row},'完整玩法'!$T$2:$T$${ideas.length + 1},"high")`]];
}
setHeader(familySheet, "A1:G1");
setBody(familySheet, `A2:G${familyKeys.length + 1}`);
familySheet.freezePanes.freezeRows(1);
familySheet.showGridLines = false;
familySheet.tables.add(`A1:G${familyKeys.length + 1}`, true, "FamilySummaryTable").style = "TableStyleMedium2";
for (const [column, width] of Object.entries({ A: 28, B: 24, C: 14, D: 14, E: 16, F: 14, G: 70 })) familySheet.getRange(`${column}:${column}`).format.columnWidth = width;

const triggerClasses = [...TRIGGER_RULES.map(([name]) => name), "自动/场景事件"];
triggerSheet.getRange(`A1:D${triggerClasses.length + 1}`).values = [
  ["触发方式", "完整玩法数", "重点案例数", "说明"],
  ...triggerClasses.map((name) => [name, "", "", name === "自动/场景事件" ? "未命中显式触摸、手势、视线、音频、姿态、对象、空间或设备运动规则" : "依据触发信号、交互描述和所需信号做主分类"]),
];
for (let row = 2; row <= triggerClasses.length + 1; row += 1) {
  triggerSheet.getRange(`B${row}`).formulas = [[`=COUNTIF('完整玩法'!$K$2:$K$${ideas.length + 1},A${row})`]];
  triggerSheet.getRange(`C${row}`).formulas = [[`=COUNTIF('重点50'!$G$2:$G$${priorities.length + 1},A${row})`]];
}
setHeader(triggerSheet, "A1:D1");
setBody(triggerSheet, `A2:D${triggerClasses.length + 1}`);
triggerSheet.freezePanes.freezeRows(1);
triggerSheet.showGridLines = false;
triggerSheet.tables.add(`A1:D${triggerClasses.length + 1}`, true, "TriggerSummaryTable").style = "TableStyleMedium2";
for (const [column, width] of Object.entries({ A: 24, B: 16, C: 16, D: 76 })) triggerSheet.getRange(`${column}:${column}`).format.columnWidth = width;

const generationLevels = [
  ["faithful_edit", "忠实编辑", "仅改变明确选区、参数或时序，不主动重写未观察事实"],
  ["perceptual_effect", "感知特效", "目标是明显的创作效果，必须保留原片并允许回退"],
  ["generative_rewrite", "生成式改写", "允许模型补全或重绘内容，需重点管理身份、几何和事实风险"],
];
generationSheet.getRange("A1:E4").values = [["生成程度", "中文口径", "完整玩法数", "重点案例数", "边界说明"], ...generationLevels.map(([level, label, note]) => [level, label, "", "", note])];
for (let row = 2; row <= 4; row += 1) {
  generationSheet.getRange(`C${row}`).formulas = [[`=COUNTIF('完整玩法'!$V$2:$V$${ideas.length + 1},A${row})`]];
  generationSheet.getRange(`D${row}`).formulas = [[`=COUNTIF('重点50'!$S$2:$S$${priorities.length + 1},A${row})`]];
}
setHeader(generationSheet, "A1:E1");
setBody(generationSheet, "A2:E4");
generationSheet.freezePanes.freezeRows(1);
generationSheet.showGridLines = false;
generationSheet.tables.add("A1:E4", true, "GenerationSummaryTable").style = "TableStyleMedium2";
for (const [column, width] of Object.entries({ A: 24, B: 22, C: 16, D: 16, E: 78 })) generationSheet.getRange(`${column}:${column}`).format.columnWidth = width;

const dictionaryRows = [
  ["特效原子", "atom_id", "原子唯一ID", "ATOM-*", "可复用的最低层视觉或交互能力"],
  ["完整玩法", "effect_id", "完整玩法唯一ID", "FX-*", "具有可见结果、触发、控制、预览与录后流程"],
  ["完整玩法", "generation_level", "生成程度", "枚举", "faithful_edit / perceptual_effect / generative_rewrite"],
  ["完整玩法", "edge_difficulty", "端侧难度", "枚举", "low / medium / high / research，不代表已测性能"],
  ["完整玩法", "trigger_class", "主触发方式", "规则分类", "根据触发信号、交互描述和所需信号归入一个主类"],
  ["组合配方", "recipe_id", "组合配方唯一ID", "RECIPE-*", "多个原子或完整玩法的可审计组合"],
  ["重点50", "priority_id", "重点案例唯一ID", "PRIORITY-*", "包含交互时间线、模块链路、信号流和降级策略"],
  ["重点50", "preview_budget", "预览预算口径", "文本", "仅描述分辨率、ROI、更新层级、实例上限和降级顺序；不填未测毫秒/FPS"],
  ["重点50", "storyboard_path", "概念分镜路径", "项目相对路径", "全部标注为本项目概念分镜，不是产品截图"],
  ["真实参考", "demonstrates", "来源能够证明的能力", "文本", "仅陈述来源直接支持的产品能力或研究能力"],
  ["真实参考", "does_not_prove", "来源不能证明的内容", "文本", "防止把桌面、论文或静态图能力误写成手机实时量产"],
  ["真实参考", "implementation_boundary", "实现边界", "枚举", "mobile_realtime / mobile_offline / desktop_offline / research_prototype 等"],
];
configureDataSheet(dictionarySheet, ["所属表", "字段", "中文含义", "格式", "说明"], dictionaryRows, "FieldDictionaryTable", { A: 20, B: 28, C: 34, D: 26, E: 86 });

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["手机录像特效玩法库 | 2026-08-27"]];
summary.getRange("A1:H1").format = { fill: "#16324F", font: { name: "Microsoft YaHei", color: "#FFFFFF", bold: true, size: 16 }, horizontalAlignment: "left", verticalAlignment: "center" };
summary.getRange("A1:H1").format.rowHeight = 38;
summary.getRange("A3:B8").values = [["统计项", "数量"], ["特效原子", ""], ["完整玩法", ""], ["组合配方", ""], ["重点案例", ""], ["真实参考", ""]];
summary.getRange("B4").formulas = [[`=COUNTA('特效原子'!$A$2:$A$${atoms.length + 1})`]];
summary.getRange("B5").formulas = [[`=COUNTA('完整玩法'!$A$2:$A$${ideas.length + 1})`]];
summary.getRange("B6").formulas = [[`=COUNTA('组合配方'!$A$2:$A$${recipes.length + 1})`]];
summary.getRange("B7").formulas = [[`=COUNTA('重点50'!$A$2:$A$${priorities.length + 1})`]];
summary.getRange("B8").formulas = [[`=COUNTA('真实参考'!$A$2:$A$${references.length + 1})`]];
setHeader(summary, "A3:B3");
setBody(summary, "A4:B8");
summary.getRange("D3:E7").values = [["质量边界", "状态"], ["概念分镜", `${storyboards.length} 张，全部显式标注`], ["真实性", "保留原片、可回退、生成式风险单列"], ["性能口径", "未写入未经设备实测的毫秒、FPS、功耗或内存数字"], ["参考口径", "参考能力与本项目创意分离，不冒充产品实现"]];
setHeader(summary, "D3:E3");
setBody(summary, "D4:E7");
summary.getRange("A10:H11").merge();
summary.getRange("A10").values = [["阅读方法：先在“重点50”理解体验与实现链路，再通过“真实参考”核对能力边界；需要扩展创意时查看“完整玩法”和“组合配方”。所有概念分镜只用于建立视觉直觉。"]];
summary.getRange("A10:H11").format = { fill: "#FFF2CC", font: { name: "Microsoft YaHei", color: "#6B4D00", size: 10 }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A13:B13").values = [["特效族", "完整玩法数"]];
summary.getRange(`A14:A${13 + familyKeys.length}`).values = familyKeys.map((family) => [FAMILY_LABELS[family]]);
for (let index = 0; index < familyKeys.length; index += 1) {
  summary.getRange(`B${14 + index}`).formulas = [[`='按特效族'!C${2 + index}`]];
}
setHeader(summary, "A13:B13");
setBody(summary, `A14:B${13 + familyKeys.length}`);
const chart = summary.charts.add("bar", summary.getRange(`A13:B${13 + familyKeys.length}`));
chart.titleText = "12 个特效族的完整玩法分布";
chart.hasLegend = false;
chart.setPosition("D13", "H30");
summary.getRange("A:A").format.columnWidth = 30;
summary.getRange("B:B").format.columnWidth = 16;
summary.getRange("D:D").format.columnWidth = 24;
summary.getRange("E:E").format.columnWidth = 66;
summary.freezePanes.freezeRows(1);
summary.getRange("A1:H35").format.font.name = "Microsoft YaHei";

for (const sheet of [atomSheet, ideaSheet, recipeSheet, prioritySheet, referenceSheet, familySheet, triggerSheet, generationSheet, dictionarySheet]) {
  sheet.getUsedRange().format.font.name = "Microsoft YaHei";
}

await fs.mkdir(outputDir, { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

const inspect = [];
inspect.push((await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 18000, tableMaxRows: 4, tableMaxCols: 8 })).ndjson);
inspect.push((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" })).ndjson);
inspect.push(JSON.stringify({ outputPath, rows: { atoms: atoms.length, ideas: ideas.length, recipes: recipes.length, priorities: priorities.length, references: references.length, storyboards: storyboards.length } }, null, 2));
await fs.writeFile(inspectPath, inspect.join("\n"), "utf8");

console.log(JSON.stringify({ outputPath, inspectPath, atoms: atoms.length, ideas: ideas.length, recipes: recipes.length, priorities: priorities.length, references: references.length }, null, 2));
