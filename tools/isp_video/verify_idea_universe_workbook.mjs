import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.argv[2] || "D:/Repository/ReadPaper/daily/20260826_后处理调研";
const xlsxPath = path.join(root, "matrix", "手机录像后处理_IDEA全量宇宙_20260827.xlsx");
const renderDir = path.join(root, "matrix", "idea_universe_rendered");
await fs.mkdir(renderDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(xlsxPath));
const sheets = [
  { name: "Summary", range: "A1:H55" },
  { name: "Core_Ideas", range: "A1:P12" },
  { name: "Variants", range: "A1:N12" },
  { name: "Legacy_112", range: "A1:P12" },
  { name: "New_Ideas", range: "A1:P12" },
  { name: "By_Family", range: "A1:G32" },
  { name: "By_Scene", range: "A1:D32" },
  { name: "Variant_Dictionary", range: "A1:E34" },
];
const summary = (await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 16000, tableMaxRows: 3, tableMaxCols: 8, tableMaxCellChars: 100 })).ndjson;
const errors = (await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, summary: "formula error scan" })).ndjson;
const renders = [];
for (const sheet of sheets) {
  const blob = await workbook.render({ sheetName: sheet.name, range: sheet.range, scale: 1, format: "png" });
  const target = path.join(renderDir, `${sheet.name}.png`);
  await fs.writeFile(target, new Uint8Array(await blob.arrayBuffer()));
  renders.push({ sheet: sheet.name, range: sheet.range, target });
}
await fs.writeFile(path.join(renderDir, "verify.ndjson"), [summary, errors, JSON.stringify({ renders })].join("\n"), "utf8");
console.log(JSON.stringify({ xlsxPath, renders, errorScan: errors }, null, 2));
