import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const root = path.join(repoRoot, "daily", "20260821_ENC_DEC");
const metadataDir = path.join(root, "metadata");
const output = path.join(root, "编解码器论文与来源索引.xlsx");
const previewsDir = path.join(metadataDir, "workbook_previews");
const payload = JSON.parse(await fs.readFile(path.join(metadataDir, "workbook_data.json"), "utf8"));

const widths = {
  "来源索引": [6, 20, 54, 14, 24, 9, 18, 30, 10, 18, 22, 64, 8, 8, 34, 28, 22, 54, 54],
  "架构比较": [6, 22, 28, 9, 46, 40, 46, 28, 28, 10, 48, 24, 46, 48],
  "训练损失": [6, 24, 30, 42, 36, 62, 48, 38, 26, 46, 52],
  "数据输入": [6, 24, 52, 48, 42, 54, 50, 48, 24, 46, 48],
  "FlashVSR 模块": [6, 22, 22, 38, 54, 38, 34, 46, 46, 52, 52],
  "术语表": [6, 24, 24, 70, 70],
};

const rowHeights = {
  "来源索引": 56,
  "架构比较": 92,
  "训练损失": 104,
  "数据输入": 110,
  "FlashVSR 模块": 122,
  "术语表": 72,
};

const previewRanges = {
  "来源索引": "A1:S8",
  "架构比较": "A1:N8",
  "训练损失": "A1:K8",
  "数据输入": "A1:K8",
  "FlashVSR 模块": "A1:K5",
  "术语表": "A1:E10",
};

const tableNames = {
  "来源索引": "EncDecSources",
  "架构比较": "EncDecArchitecture",
  "训练损失": "EncDecTraining",
  "数据输入": "EncDecDatasets",
  "FlashVSR 模块": "FlashVSRModules",
  "术语表": "EncDecTerminology",
};

const statusFills = [
  ["undisclosed", "#FFF2CC", "#7A5A00"],
  ["code-verified", "#E2F0D9", "#2E5D34"],
  ["paper-verified", "#DDEBF7", "#1F4E78"],
  ["paper-downloaded", "#DDEBF7", "#1F4E78"],
  ["analysis", "#E7E6E6", "#4A4A4A"],
  ["not-downloaded", "#FCE4D6", "#8A2D19"],
  ["missing", "#FCE4D6", "#8A2D19"],
];

function colLetters(count) {
  let n = count;
  let result = "";
  while (n > 0) {
    n -= 1;
    result = String.fromCharCode(65 + (n % 26)) + result;
    n = Math.floor(n / 26);
  }
  return result;
}

const wb = Workbook.create();
for (const sheetData of payload.sheets) {
  const sheet = wb.worksheets.add(sheetData.name);
  sheet.showGridLines = false;
  const allRows = [sheetData.headers, ...sheetData.rows];
  const lastCol = colLetters(sheetData.headers.length);
  const lastRow = allRows.length;
  const fullRange = `A1:${lastCol}${lastRow}`;
  sheet.getRange(fullRange).values = allRows;
  sheet.getRange(fullRange).format = {
    font: { name: "Microsoft YaHei", size: sheetData.name === "来源索引" ? 9 : 10, color: "#17212B" },
    verticalAlignment: "center",
    wrapText: true,
  };
  sheet.getRange(`A1:${lastCol}1`).format = {
    fill: "#16324F",
    font: { name: "Microsoft YaHei", size: 10, bold: true, color: "#FFFFFF" },
    rowHeight: 30,
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "bottom", style: "medium", color: "#7890A4" },
  };
  if (lastRow > 1) sheet.getRange(`A2:${lastCol}${lastRow}`).format.rowHeight = rowHeights[sheetData.name];
  widths[sheetData.name].forEach((width, index) => {
    sheet.getRangeByIndexes(0, index, lastRow, 1).format.columnWidth = width;
  });
  if (sheetData.name === "来源索引" && lastRow > 1) {
    sheet.getRange(`P2:P${lastRow}`).format.numberFormat = "yyyy-mm-dd hh:mm";
  }
  sheet.freezePanes.freezeRows(1);
  sheet.freezePanes.freezeColumns(sheetData.name === "术语表" ? 2 : 3);
  sheet.tables.add(fullRange, true, tableNames[sheetData.name]).style = "TableStyleMedium2";

  const statusIndex = sheetData.headers.findIndex((header) => header === "证据状态");
  if (statusIndex >= 0) {
    for (let rowIndex = 0; rowIndex < sheetData.rows.length; rowIndex += 1) {
      const status = String(sheetData.rows[rowIndex][statusIndex] ?? "");
      const match = statusFills.find(([needle]) => status.includes(needle));
      if (match) {
        sheet.getCell(rowIndex + 1, statusIndex).format = {
          fill: match[1],
          font: { name: "Microsoft YaHei", size: 9, bold: true, color: match[2] },
          verticalAlignment: "center",
          wrapText: true,
        };
      }
    }
  }
}

await fs.mkdir(previewsDir, { recursive: true });
for (const sheetData of payload.sheets) {
  const rendered = await wb.render({
    sheetName: sheetData.name,
    range: previewRanges[sheetData.name],
    scale: 1,
    format: "png",
  });
  const slug = sheetData.name.replaceAll(" ", "_");
  await fs.writeFile(path.join(previewsDir, `${slug}.png`), new Uint8Array(await rendered.arrayBuffer()));
}

const inspection = await wb.inspect({
  kind: "workbook,sheet,table",
  maxChars: 6000,
  tableMaxRows: 3,
  tableMaxCols: 8,
  tableMaxCellChars: 100,
});
console.log(inspection.ndjson);

const errors = await wb.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 200 },
  summary: "final formula error scan",
  maxChars: 2500,
});
console.log(errors.ndjson);

const file = await SpreadsheetFile.exportXlsx(wb);
await file.save(output);
console.log(output);
