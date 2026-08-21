import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const workbookPath = path.join(repoRoot, "daily", "20260821_ENC_DEC", "编解码器论文与来源索引.xlsx");
const qaPath = path.join(repoRoot, "daily", "20260821_ENC_DEC", "metadata", "workbook_qa.json");
const file = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(file);

const sheets = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 3000 });
const sources = await workbook.inspect({ kind: "table", range: "来源索引!A1:S6", include: "values,formulas", tableMaxRows: 6, tableMaxCols: 19, maxChars: 3500 });
const architecture = await workbook.inspect({ kind: "table", range: "架构比较!A1:N6", include: "values,formulas", tableMaxRows: 6, tableMaxCols: 14, maxChars: 3500 });
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 200 }, summary: "formula error scan", maxChars: 2500 });

const qa = {
  workbook: path.relative(repoRoot, workbookPath),
  expected_sheets: ["来源索引", "架构比较", "训练损失", "数据输入", "FlashVSR 模块", "术语表"],
  sheets: sheets.ndjson,
  source_sample: sources.ndjson,
  architecture_sample: architecture.ndjson,
  formula_error_scan: errors.ndjson,
};
await fs.writeFile(qaPath, JSON.stringify(qa, null, 2), "utf8");
console.log(JSON.stringify({ workbook: workbookPath, qa: qaPath }, null, 2));
