import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = process.argv[2] || "D:/Repository/ReadPaper/.codex_worktrees/video_effects_20260828";
const projectRoot = path.join(repoRoot, "daily", "20260827_录像特效调研");
const workbookPath = path.join(projectRoot, "matrix", "手机录像特效玩法库_20260827.xlsx");
const renderDir = path.join(projectRoot, "matrix", "rendered");
const expectedSheets = ["总览", "特效原子", "完整玩法", "组合配方", "重点50", "真实参考", "按特效族", "按触发方式", "按生成程度", "字段字典"];

await fs.mkdir(renderDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(workbookPath));
const sheetInspect = (await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 8000 })).ndjson;
for (const name of expectedSheets) {
  if (!sheetInspect.includes(name)) throw new Error(`missing worksheet: ${name}`);
}

const errors = (await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" })).ndjson;
if (/"matchCount"\s*:\s*[1-9]/.test(errors)) throw new Error(errors);

const renders = [
  ["总览", "A1:H30"],
  ["重点50", "A1:V7"],
  ["真实参考", "A1:N7"],
  ["按特效族", "A1:G13"],
];
const outputs = [];
for (const [sheetName, range] of renders) {
  const image = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  const target = path.join(renderDir, `${sheetName}.png`);
  await fs.writeFile(target, new Uint8Array(await image.arrayBuffer()));
  outputs.push({ sheetName, range, target });
}

const summary = (await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 16000, tableMaxRows: 3, tableMaxCols: 7 })).ndjson;
await fs.writeFile(path.join(renderDir, "verify.ndjson"), [summary, errors, JSON.stringify({ outputs }, null, 2)].join("\n"), "utf8");
console.log(JSON.stringify({ workbookPath, expectedSheets, renders: outputs, errorScan: errors }, null, 2));
