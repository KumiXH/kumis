# PortraitSR 人像超分与人脸细节恢复研究库

截至 2026-08-07：在原 45 篇 PortraitSR 核心候选基础上，新增 11 篇已校验的
mask conditioning、human parsing、matting、重光照、阴影编辑和 virtual try-on PDF；
23 项数据集记录、20 项官方页快照及原有公司归属证据继续保留。

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
- [Word 阶段性洞察](report/人像超分与人脸细节恢复_阶段性洞察_20260806.docx)：新增 Mask 条件专章、区域 LOSS、数据制作、多任务训练及原文架构/效果页。
- [Markdown 阶段性洞察](report/人像超分与人脸细节恢复_阶段性洞察_20260806.md)：可搜索、可追踪来源的报告正文，区分论文事实与跨论文综合建议。
- [论文 PDF](papers/)：按任务线整理的已校验论文原文。
- [全文与页码证据](text/)：带页码全文和每篇论文的图表候选证据。
- [原文代表页](figures/representative_pages/)：代表论文架构页与效果页。
- [数据集官方页快照](datasets/official_docs/)：仅保存页面和元数据，不包含受限人脸数据。
- [PDF 校验清单](metadata/download_manifest.json)：下载状态、页数、字节数和 SHA-256。
- [训练证据矩阵](metadata/training_evidence_matrix.json)：11 篇重点论文的训练阶段、冻结/解冻模块、数据构造、退化、LOSS、优化器、页码和证据等级。
- [Mask 论文 PDF](papers/07_mask_conditioning/)：已校验的空间条件、人像效果和边界建模论文原文。
- [Mask 原文图页](figures/mask_conditioning/)：15 张架构、解析、matting、重光照和阴影效果原文页面。
- [Mask 证据矩阵](metadata/mask_conditioning_evidence_matrix.json)：14 篇论文的 mask 表示、注入方式、LOSS、训练数据、局限和原文页码。

## Evidence rules

- Company attribution requires a paper first page or formal author-affiliation list.
- A deployment chip, challenge sponsor, citation, or benchmark participant is recorded separately from author affiliation.
- Dataset availability, license, and redistribution rights are separate fields.
- Quantitative results are not compared across papers unless dataset, degradation, resolution, metric, and hardware settings match.
