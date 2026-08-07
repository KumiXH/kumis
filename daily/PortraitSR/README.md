# PortraitSR 人像超分与人脸细节恢复研究库

截至 2026-08-06：45 篇核心候选，30 篇来自 2025-2026，18 篇 PDF 已完成
页数与 SHA-256 校验，27 篇待处理；23 项数据集记录，20 项官方页已归档；
12 篇论文的公司归属已经论文作者机构证据核验。

Scope:

- face restoration and face super-resolution;
- full-portrait restoration, detail recovery, and portrait enhancement;
- identity-preserving, personalized, and reference-based restoration;
- video portrait/face restoration when temporal consistency is central;
- datasets used for training, evaluation, identity verification, and real-world degradation tests.

Primary review window: 2023-01-01 through 2026-08-06. Earlier papers and datasets
are included only when they remain important baselines or data sources.

Every included paper should retain a primary paper/venue URL, an original PDF when
available, and official project/code links. Dataset records should retain the official
homepage or original repository, license or terms-of-use status, access conditions,
and the paper that introduced the dataset.

## 当前入口

- [论文与数据集索引](PortraitSR论文与数据集索引.xlsx)：论文、机构/公司归属、原文证据、数据集许可和检索来源。
- [Word 阶段性洞察](report/人像超分与人脸细节恢复_阶段性洞察_20260806.docx)：含 18 张原文架构、数据、退化、消融或效果页面；新增 LOSS、数据制作和四阶段训练章节。
- [Markdown 阶段性洞察](report/人像超分与人脸细节恢复_阶段性洞察_20260806.md)：可搜索、可追踪来源的报告正文，区分论文事实与跨论文综合建议。
- [论文 PDF](papers/)：按任务线整理的已校验论文原文。
- [全文与页码证据](text/)：带页码全文和每篇论文的图表候选证据。
- [原文代表页](figures/representative_pages/)：代表论文架构页与效果页。
- [数据集官方页快照](datasets/official_docs/)：仅保存页面和元数据，不包含受限人脸数据。
- [PDF 校验清单](metadata/download_manifest.json)：下载状态、页数、字节数和 SHA-256。
- [训练证据矩阵](metadata/training_evidence_matrix.json)：11 篇重点论文的训练阶段、冻结/解冻模块、数据构造、退化、LOSS、优化器、页码和证据等级。

## Evidence rules

- Company attribution requires a paper first page or formal author-affiliation list.
- A deployment chip, challenge sponsor, citation, or benchmark participant is recorded separately from author affiliation.
- Dataset availability, license, and redistribution rights are separate fields.
- Quantitative results are not compared across papers unless dataset, degradation, resolution, metric, and hardware settings match.
