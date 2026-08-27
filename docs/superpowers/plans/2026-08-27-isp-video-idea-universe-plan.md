# 手机录像后处理 IDEA 全量宇宙 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在已有后处理调研目录中建立保留旧方向、包含大规模新增基础创意及可控变体的手机录像 IDEA 数据库。

**Architecture:** 使用一个确定性 Python 生成器维护创意簇、基础创意模板和单轴变体规则，输出 JSONL、统计 JSON 与 Markdown。使用 `@oai/artifact-tool` 将同一数据导出为可筛选 Excel，并对每个工作表渲染代表性区域进行验证。

**Tech Stack:** Bundled Python 3.12、JSONL、Markdown、Node.js、`@oai/artifact-tool`、Git。

---

### Task 1: 建立创意生成器

**Files:**
- Create: `tools/isp_video/build_idea_universe.py`
- Create: `tools/isp_video/test_idea_universe.py`

- [ ] 定义基础 IDEA、变体和统计记录的必需字段。
- [ ] 导入 `metadata/opportunities.jsonl` 中的全部 112 条旧机会。
- [ ] 建立涵盖计算底片、曝光、时间、稳定、光学、打光、多摄、人像、场景、声音、生成、编解码、交互和新传感器的创意模板。
- [ ] 使用稳定 slug 和序号生成唯一 ID，不以标题文本作为唯一键。
- [ ] 加入关键方向检索断言：动态星芒、虚拟打光、计算底片、对象级快门、多摄协同、声音驱动、Event Camera、可信生成必须存在。
- [ ] 运行测试，确认旧机会无遗漏、字段完整且基础 IDEA 无重复 ID。

### Task 2: 生成单轴变体库

**Files:**
- Modify: `tools/isp_video/build_idea_universe.py`
- Modify: `tools/isp_video/test_idea_universe.py`

- [ ] 定义处理阶段、真实性、输入、场景、时间规格、处理范围和交付形态七个变体轴。
- [ ] 为每个基础 IDEA 分别生成全部单轴变体。
- [ ] 在变体解释中说明该轴如何改变实现，而不重复宣称新的基础功能。
- [ ] 校验每个基础 IDEA 对七个轴均有覆盖，变体 ID 唯一且指向有效基础 ID。

### Task 3: 输出 Markdown 与统计数据

**Files:**
- Create: `daily/20260826_后处理调研/metadata/idea_universe/core_ideas.jsonl`
- Create: `daily/20260826_后处理调研/metadata/idea_universe/idea_variants.jsonl`
- Create: `daily/20260826_后处理调研/metadata/idea_universe/idea_universe_stats.json`
- Create: `daily/20260826_后处理调研/report/手机录像后处理_IDEA全量宇宙_20260827.md`

- [ ] 输出按来源层、能力族和创意簇组织的基础 IDEA 清单。
- [ ] 输出七个变体轴的定义、计数和使用边界。
- [ ] 在报告开头明确这些记录是创意池，不是论文结论或量产事实。
- [ ] 校验 Markdown 无占位符且所有核心 ID 都可检索。

### Task 4: 导出 Excel 全量库

**Files:**
- Create: `tools/isp_video/build_idea_universe_workbook.mjs`
- Create: `tools/isp_video/verify_idea_universe_workbook.mjs`
- Create: `daily/20260826_后处理调研/matrix/手机录像后处理_IDEA全量宇宙_20260827.xlsx`

- [ ] 创建 `Summary`、`Core_Ideas`、`Variants`、`Legacy_112`、`New_Ideas`、`By_Family`、`By_Scene` 和 `Variant_Dictionary` 工作表。
- [ ] 设置微软雅黑、冻结表头、筛选、换行、稳定列宽和真实性/来源层字段。
- [ ] 导入工作簿检查行数并扫描公式错误。
- [ ] 对八个工作表分别渲染代表性区域并检查标题、表头、文字截断和异常行高。

### Task 5: 最终核验与提交

**Files:**
- Modify: `daily/20260826_后处理调研/README.md`
- Create: `daily/20260826_后处理调研/notes/idea_universe_audit_20260827.md`

- [ ] 核验旧 112 条全部出现，基础 IDEA 与变体 ID 唯一。
- [ ] 核验 JSONL、Markdown 与 Excel 的基础条数和变体条数一致。
- [ ] 运行 Python 编译、JSON 解析、XLSX ZIP、`git diff --check` 和本轮目录状态检查。
- [ ] 精确暂存 IDEA 宇宙文件和生成脚本，不暂存工作区其他未跟踪内容。
- [ ] 提交为 `research: expand mobile video post-processing idea universe`。
