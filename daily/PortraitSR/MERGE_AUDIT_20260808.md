# PortraitSR 合入 main 审计记录

日期：2026-08-08

## 对比对象

- 目标基线：`origin/main`，提交 `7e3186a`
- 来源分支：`codex/portrait-sr-training-report`，提交 `402d704`

## 同源判定

对 `daily/PortraitSR` 的 Git blob 哈希逐文件比较结果：

- 25 个双方共有文件内容完全相同；
- 1 个双方共有文件内容不同：`README.md`；
- 来源分支另有 195 个 PortraitSR 文件；
- `main` 没有来源分支缺失的 PortraitSR 独有文件。

`README.md` 的来源版本完整保留了 `main` 原有 scope、时间窗口和证据规则，并新增论文库、数据集、报告及 Mask 专章入口。因此两套内容属于同一研究库的递进版本，不需要改名或迁移到另一个 `daily` 子目录。

## 合入决策

- 保持统一目录：`daily/PortraitSR`；
- 保留 `main` 中 25 个同哈希基础文件；
- 使用增强版 `README.md`；
- 加入论文 PDF、数据集官方页快照、Excel 索引、Word/Markdown 报告、全文证据、原文图页和 Mask 证据矩阵；
- 加入 6 个 Mask 资料维护与验证工具；
- 将工具中的固定本机路径改为从仓库位置动态解析；
- 将 Mask 清单中的本地文件路径改为 `daily/PortraitSR` 相对路径；
- 排除未完成下载文件 `hdrface_2605.14821.pdf.directpart`。

## 验证范围

- 29 篇 PDF 均可解析，共 421 页；
- Mask 清单中的 11 篇 PDF 已核对文件大小、页数与 SHA-256；
- Word 报告包含 33 张图片、14 条 Mask 证据记录和 15 张原文页，内部关系无缺失；
- Excel 索引为有效 OpenXML 包，包含 5 个工作表；
- README 中列出的主要相对入口均存在；
- 本次合入不包含 Flux、缓存、锁文件、备份文件或下载残片。

本机未安装 LibreOffice 或 Microsoft Word，因此本次未重新执行 DOCX 全页视觉渲染；结构、媒体关系、正文关键项、Markdown 图片引用和关联 PDF 哈希均已独立验证。
