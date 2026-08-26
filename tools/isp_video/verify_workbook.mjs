import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const root = process.argv[2] || "D:/Repository/ReadPaper/daily/20260826_后处理调研";
const xlsxPath = path.join(root, "matrix", "手机录像创新功能机会库.xlsx");
const renderDir = path.join(root, "matrix", "rendered");
await fs.mkdir(renderDir, { recursive: true });
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(xlsxPath));
const summary = (await wb.inspect({ kind: "workbook,sheet,table", maxChars: 12000, tableMaxRows: 3, tableMaxCols: 8 })).ndjson;
const errors = (await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" })).ndjson;
const sheets = [
  { name: "Summary", range: "A1:H30" },
  { name: "Opportunity_Map", range: "A1:AA12" },
  { name: "Deep_Dive_30", range: "A1:S10" },
  { name: "Priority_10", range: "A1:L11" },
  { name: "Industry_Prototypes", range: "A1:K12" },
  { name: "Papers", range: "A1:L12" },
  { name: "Paper_Discovery_381", range: "A1:M12" },
  { name: "Patents", range: "A1:J3" },
  { name: "Datasets", range: "A1:G9" },
  { name: "Source_Manifest", range: "A1:O12" },
];
const renders = [];
for (const sheet of sheets) {
  const blob = await wb.render({ sheetName: sheet.name, range: sheet.range, scale: 1, format: "png" });
  const target = path.join(renderDir, `${sheet.name}.png`);
  await fs.writeFile(target, new Uint8Array(await blob.arrayBuffer()));
  renders.push({ sheet: sheet.name, range: sheet.range, target });
}
await fs.writeFile(path.join(renderDir, "verify.ndjson"), [summary, errors, JSON.stringify({ renders })].join("\n"), "utf8");
console.log(JSON.stringify({ xlsxPath, renders, error_scan: errors }, null, 2));
