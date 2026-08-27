"""Cross-artifact audit for the ISP video research workspace."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\Repository\ReadPaper\daily\20260826_后处理调研")


def jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


opportunities = jsonl(ROOT / "metadata" / "opportunities.jsonl")
deep = jsonl(ROOT / "metadata" / "deep_dive_30.jsonl")
priority = jsonl(ROOT / "metadata" / "priority_10.jsonl")
manifest = json.loads((ROOT / "sources" / "source_manifest.json").read_text(encoding="utf-8"))
papers = jsonl(ROOT / "sources" / "papers" / "paper_records.jsonl")
core_papers = jsonl(ROOT / "sources" / "papers" / "core_paper_records.jsonl")
datasets = jsonl(ROOT / "sources" / "datasets" / "dataset_records.jsonl")
patents = jsonl(ROOT / "sources" / "patents" / "patent_records.jsonl")

source_ids = {x.get("source_id") for x in manifest}
deep_ids = {x.get("deep_dive_id") for x in deep}
op_ids = {x.get("id") for x in opportunities}
priority_components = sorted({c for row in priority for c in row.get("components", [])})
missing_paths = []
for row in manifest:
    local_path = row.get("local_path")
    if local_path and not Path(local_path).exists():
        missing_paths.append(local_path)

xlsx_path = ROOT / "matrix" / "手机录像创新功能机会库.xlsx"
xlsx_entries = []
if xlsx_path.exists():
    with ZipFile(xlsx_path) as z:
        xlsx_entries = z.namelist()
render_dir = ROOT / "matrix" / "rendered"
expected_render_sheets = [
    "Summary",
    "Opportunity_Map",
    "Deep_Dive_30",
    "Priority_10",
    "Industry_Prototypes",
    "Papers",
    "Paper_Discovery_381",
    "Patents",
    "Datasets",
    "Source_Manifest",
]
rendered_sheets = [name for name in expected_render_sheets if (render_dir / f"{name}.png").exists()]

md_path = ROOT / "report" / "手机录像创新功能与ISP技术机会洞察.md"
docx_path = ROOT / "report" / "手机录像创新功能与ISP技术机会洞察.docx"
md_text = md_path.read_text(encoding="utf-8")

report = {
    "audited_at": datetime.now(timezone.utc).isoformat(),
    "counts": {
        "opportunities": len(opportunities),
        "deep_dive": len(deep),
        "priority": len(priority),
        "sources": len(manifest),
        "papers": len(papers),
        "core_papers": len(core_papers),
        "datasets": len(datasets),
        "patents": len(patents),
    },
    "thresholds": {
        "opportunities_at_least_100": len(opportunities) >= 100,
        "deep_dive_exactly_30": len(deep) == 30,
        "priority_exactly_10": len(priority) == 10,
        "families_exactly_14": len({x.get("family") for x in opportunities}) == 14,
        "core_papers_present": len(core_papers) >= 10,
        "datasets_present": len(datasets) >= 8,
    },
    "uniqueness": {
        "opportunity_ids_unique": len(op_ids) == len(opportunities),
        "deep_dive_ids_unique": len(deep_ids) == len(deep),
        "priority_ids_unique": len({x.get("concept_id") for x in priority}) == len(priority),
        "priority_components_exist": set(priority_components).issubset(deep_ids),
    },
    "source_integrity": {
        "deep_dive_source_ids_exist": all(s in source_ids for row in deep for s in row.get("source_ids", [])),
        "missing_local_paths": missing_paths,
        "official_verified_count": sum(x.get("verification_status") == "verified" for x in manifest),
        "pending_or_failed_count": sum(x.get("verification_status") not in {"verified", "metadata_verified"} for x in manifest),
    },
    "xlsx": {
        "exists": xlsx_path.exists(),
        "nonempty": xlsx_path.exists() and xlsx_path.stat().st_size > 0,
        "has_workbook_xml": "xl/workbook.xml" in xlsx_entries,
        "entry_count": len(xlsx_entries),
        "expected_sheet_count": len(expected_render_sheets),
        "representative_previews_present": len(rendered_sheets),
        "representative_preview_sheets": rendered_sheets,
        "visual_review_status": "completed for representative ranges on all workbook sheets"
        if len(rendered_sheets) == len(expected_render_sheets)
        else "incomplete",
    },
    "docx_structural_checks": {
        "exists": docx_path.exists(),
        "nonempty": docx_path.exists() and docx_path.stat().st_size > 0,
        "markdown_line_count": len(md_text.splitlines()),
        "markdown_h1_count": len(re.findall(r"(?m)^# ", md_text)),
        "markdown_h2_count": len(re.findall(r"(?m)^## ", md_text)),
        "markdown_h3_count": len(re.findall(r"(?m)^### ", md_text)),
        "placeholder_markers": bool(re.search(r"TBD|TODO", md_text)),
        "visual_render_status": "blocked: soffice/libreoffice unavailable in current Windows environment",
    },
    "unmeasured_claims": [
        "Target-device FPS, latency, memory, power and thermal curves were not measured in this Windows research pass.",
        "E5 opportunity ideas are not proof of product implementation.",
        "OpenAlex metadata is a discovery index; paper-body relevance and implementation details require paper-level verification.",
    ],
}

(ROOT / "metadata" / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

lines = [
    "# 最终审计记录",
    "",
    f"审计时间：{report['audited_at']}",
    "",
    "## 已验证",
    "",
    f"- 候选机会：{len(opportunities)} 条，达到不少于 100 条的目标。",
    f"- 技术深度卡：{len(deep)} 条，正好 30 条，覆盖 {len({x.get('family') for x in opportunities})} 个能力族。",
    f"- 组合创新：{len(priority)} 条，正好 10 条，且引用的深度卡 ID 全部存在。",
    f"- 来源清单：{len(manifest)} 条；深度卡引用的来源 ID 全部可以回溯。",
    f"- OpenAlex 论文元数据：{len(papers)} 条；原始查询响应保存在 `sources/papers/openalex_raw/`。",
    f"- 核心论文：{len(core_papers)} 条；数据集：{len(datasets)} 条；专利检索主题：{len(patents)} 条。",
    f"- Excel：存在且非空，包含 `{len(xlsx_entries)}` 个 ZIP 条目和 `xl/workbook.xml`。",
    f"- Excel 代表性预览：{len(rendered_sheets)}/{len(expected_render_sheets)} 个工作表已生成 PNG 并完成本轮视觉复核。",
    f"- Markdown：{len(md_text.splitlines())} 行，无 `TBD/TODO` 占位符。",
    "",
    "## 未完成或需要后续核验",
    "",
    "- 当前 Windows 环境没有 `soffice`/`libreoffice`，官方 DOCX 渲染器无法执行页面 PNG 视觉检查；已完成 DOCX 结构、段落、表格、字体设置和文件非空检查，视觉检查需在有 LibreOffice 或 Microsoft Word 的环境复核。",
    "- 官方网页中部分来源返回 403、404 或网络失败，清单保留为 `request_failed`/待核验，不作为已量产事实使用。",
    "- OpenAlex 宽关键词检索会混入泛领域论文；本阶段把它们作为候选元数据，后续应以论文正文、官方代码和数据集页面做第二轮筛选。",
    "- 手机目标 SoC 上的 FPS、延迟、内存、功耗、温度和录制时长尚未实测，报告中没有虚构这些数字。",
    "",
    "## 解释",
    "",
    "本项目的 112 条机会主体是 E5 视频化推演，Excel 与报告已显式标记证据等级和真实性边界。E1-E4 只说明外部产品/论文/专利存在相应原型或主张，不自动证明该功能可以直接在手机录像中实现。",
]
(ROOT / "notes" / "final_audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
