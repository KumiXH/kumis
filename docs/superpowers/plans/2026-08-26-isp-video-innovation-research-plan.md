# ISP Video Innovation Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an evidence-backed, extensible opportunity map of innovative mobile-video functions, including 100+ candidates, 30 technical deep dives, 10 combined concepts, a searchable Excel workbook, and a Chinese-English Word report.

**Architecture:** Use a source-first pipeline. Official product pages/manuals, papers, patents, code repositories, and dataset pages are cached locally and assigned evidence levels E1-E4; E5 concepts are generated only after the evidence table exists. Normalized JSON/TSV records feed the Excel workbook and the Word/Markdown report so that counts, names, source status, and classifications remain consistent.

**Tech Stack:** PowerShell for controlled downloads and file checks; Python for JSON/TSV normalization, OpenAlex/arXiv/Crossref queries, XLSX generation, PDF text/figure extraction, and DOCX generation; PyMuPDF for PDF evidence; `python-docx` and the repository document-rendering workflow for Word; Git with explicit path staging.

---

## 0. Execution Rules

**Files:**
- Read: `D:/Repository/ReadPaper/docs/superpowers/specs/2026-08-26-isp-video-innovation-design.md`
- Create or modify only under: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/`
- Create tools only under: `D:/Repository/ReadPaper/tools/isp_video/`

- [ ] Before each batch, run `git status --short --branch` and record the starting state in the batch log.
- [ ] Never use `git add -A`; stage only the exact research directory, tool files, and plan/spec files created by this project.
- [ ] Keep all downloaded pages, PDFs, metadata, and screenshots under the project directory; do not cite a web page that is not listed in `sources/source_manifest.json`.
- [ ] Use one request at a time for arXiv and low-rate scholarly endpoints; set a descriptive User-Agent and pause between requests.
- [ ] Mark inaccessible, unverified, or paywalled sources as `pending` or `unverified`; never convert missing evidence into a positive product claim.

## 1. Create the Project Skeleton and Schemas

**Files:**
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/README.md`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/project_config.json`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/opportunity_schema.json`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/source_schema.json`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/search_log.jsonl`
- Create directories: `report`, `matrix`, `sources/official_products`, `sources/papers`, `sources/patents`, `sources/code`, `sources/datasets`, `figures`, `notes`

- [ ] Create the directory tree with `New-Item -ItemType Directory -Force` and verify each directory with `Test-Path`.
- [ ] Define the opportunity record fields exactly as specified in the design: `id`, `name_zh`, `name_en`, `family`, `scenarios`, `source_type`, `evidence_level`, `prototype_status`, `video_mode`, `input_signals`, `pipeline_stage`, `algorithm_family`, `temporal_strategy`, `data_needs`, `loss_or_objective`, `quality_metrics`, `failure_modes`, `truth_boundary`, `feasibility_tags`, `novelty`, `video_fit`, `edge_feasibility`, `product_differentiation`, `risk`, `priority`, `evidence_ids`, `notes`, and `last_verified`.
- [ ] Define the source record fields exactly as `source_id`, `source_type`, `title`, `publisher_or_authors`, `product_or_venue`, `date`, `url`, `local_path`, `evidence_level`, `access_status`, `verification_status`, `evidence_quote`, `scope_limit`, and `retrieved_at`.
- [ ] Add controlled vocabularies for the 14 capability families, E1-E5 evidence levels, four video modes, and three truth boundaries (`faithful`, `perceptual`, `generative`).
- [ ] Add a README explaining that `sources/` is cached evidence, `metadata/` is normalized data, `matrix/` is analysis output, and `report/` is derived narrative.
- [ ] Run a JSON parse check with the bundled Python runtime and verify that all required keys exist.
- [ ] Commit only the skeleton and schemas with `git add -- <project-dir> && git commit -m "docs: scaffold ISP video innovation research"`.

## 2. Build the Initial Official-Product Source Map

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/collect_official_sources.ps1`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/sources/source_manifest.json`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/notes/official_product_screening.md`

- [ ] Create a source list covering phone vendors: Apple, Samsung, Google, Huawei, Honor, vivo, OPPO, Xiaomi, Sony, and other vendors with official camera/video documentation.
- [ ] Add camera and cinema sources for Sony Alpha/Cinema Line, Canon, Nikon, Panasonic/LUMIX, Fujifilm, Leica, ARRI, RED, and Blackmagic.
- [ ] Add action-camera and aerial-imaging sources for DJI, GoPro, and Insta360.
- [ ] Add software sources for DaVinci Resolve, Adobe Premiere/After Effects, Final Cut Pro, Blackmagic Camera, CapCut, and other official mobile-video products when a concrete feature can be verified.
- [ ] For each source, record a stable page or document URL, product/version, retrieval date, local cache path, and the exact feature statement to be cited.
- [ ] Use `Invoke-WebRequest` with a descriptive User-Agent, retry once after a delay, and write HTTP status plus content hash to the manifest.
- [ ] Separate official feature pages, manuals, release notes, SDK documents, and marketing pages in `source_type`; a marketing page cannot be used alone for a quantitative capability claim.
- [ ] Screen the sources into the initial 14 capability families and write one paragraph per family explaining what is verified and what is not.
- [ ] Run a source-manifest validation that checks every `local_path` with `Test-Path`, every URL is nonempty, every evidence level is in `E1..E4`, and every source has `retrieved_at`.
- [ ] Commit the source map and collector with `git add -- tools/isp_video/collect_official_sources.ps1 <project-dir>/sources <project-dir>/notes/official_product_screening.md && git commit -m "research: map official mobile video prototypes"`.

## 3. Search the Academic Literature and Public Code

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/search_literature.py`
- Create: `D:/Repository/ReadPaper/tools/isp_video/collect_code_sources.ps1`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/sources/papers/paper_records.jsonl`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/sources/datasets/dataset_records.jsonl`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/sources/code/code_records.jsonl`

- [ ] Query OpenAlex, arXiv, Crossref, and Semantic Scholar only with a low request rate and cache raw responses before normalization.
- [ ] Search separate query groups for video restoration, video super-resolution, video deblurring, rolling-shutter correction, video HDR, video relighting, neural rendering, depth-aware video effects, virtual camera, computational cinematography, video matting, face restoration, identity consistency, generative video editing, video diffusion, DiT video, and mobile/edge inference.
- [ ] Add venue, year, DOI/arXiv ID, abstract, open-access URL, code URL, dataset names, and evidence status to each paper record.
- [ ] Prefer papers from the last five years for the main opportunity pool, but retain older seminal papers for history and architecture context.
- [ ] Download only open-access PDFs or official supplementary files into `sources/papers/`; retain a manifest entry for failed downloads rather than retrying indefinitely.
- [ ] Extract first-page metadata and searchable text with PyMuPDF or `pdftotext`; do not claim a method uses video unless the abstract or body provides video evidence.
- [ ] Search GitHub repository metadata for official or author-released implementations, checkpoints, demos, and mobile inference code; mark unverified third-party ports separately.
- [ ] Normalize duplicate preprint/conference/journal versions under one `canonical_id`, keeping all known identifiers in an `aliases` field.
- [ ] Run a deduplication check by DOI, arXiv ID, and normalized title; emit a report of collisions and unresolved records.
- [ ] Commit the literature/code index and search log with `git add -- tools/isp_video/search_literature.py tools/isp_video/collect_code_sources.ps1 <project-dir>/sources && git commit -m "research: collect video imaging literature and code"`.

## 4. Search Public Patents and Technical Disclosures

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/collect_patent_sources.ps1`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/sources/patents/patent_records.jsonl`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/notes/patent_scope.md`

- [ ] Search public patent databases and official patent portals for combinations of video relighting, computational bokeh, camera effects, multi-camera fusion, stabilization, neural rendering, image signal processing, video enhancement, and mobile camera.
- [ ] Search by assignee for major phone vendors, camera vendors, action-camera vendors, and SoC vendors, but do not infer product availability from the assignee alone.
- [ ] Record publication number, title, applicant/assignee, filing/publication date, claims or relevant paragraph, status when available, URL, local cache, and evidence level `E4`.
- [ ] Classify each patent as product-adjacent, algorithmic, hardware/interface, or interaction design.
- [ ] Mark expired, abandoned, pending, granted, and unclear status separately; do not use legal status to assert technical feasibility.
- [ ] Extract only the claims or technical paragraphs needed to establish the proposed capability; avoid copying entire patent documents into the report.
- [ ] Write a scope note explaining that patents are idea evidence and not proof of implementation.
- [ ] Commit the patent index with `git add -- tools/isp_video/collect_patent_sources.ps1 <project-dir>/sources/patents <project-dir>/notes/patent_scope.md && git commit -m "research: index public mobile imaging patents"`.

## 5. Create the 100+ Candidate Opportunity Pool

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/build_opportunity_pool.py`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/opportunities.jsonl`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/opportunity_evidence_matrix.json`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/notes/opportunity_pool_screening.md`

- [ ] Convert verified product prototypes, paper capabilities, and patent concepts into normalized opportunity records; never copy a source description into `E5` without labeling the transformation as an extension.
- [ ] Ensure all 14 capability families have candidates and that the pool contains at least 100 unique records.
- [ ] For each candidate, write a concrete video use case and specify whether it is preview, online recording, offline device processing, or cloud processing.
- [ ] For each candidate, record the minimum signal set: single-camera YUV, RAW, multi-camera, depth, IMU, audio, semantic mask, or a combination.
- [ ] Assign a first-pass temporal difficulty from `T1` to `T5`: frame-local, short-window, reference-frame, long-range, or 3D/4D consistency.
- [ ] Assign truth boundary and evidence level independently. An E1 product can still be generative; an E5 idea can still be faithful in principle.
- [ ] Add failure-mode labels: flicker, ghosting, texture crawl, identity drift, mask leakage, exposure breathing, lens-switch discontinuity, hallucination, latency, thermal throttling, and user-control complexity.
- [ ] Create 10-20 combination candidates by joining complementary capabilities, such as semantic long exposure plus HDR, voice-driven framing plus focus, or multi-camera depth plus relighting.
- [ ] Produce counts by family, source type, evidence level, video mode, truth boundary, and priority; verify they sum to the total number of unique candidate IDs.
- [ ] Commit the candidate pool and screening notes with `git add -- tools/isp_video/build_opportunity_pool.py <project-dir>/metadata <project-dir>/notes/opportunity_pool_screening.md && git commit -m "research: build mobile video opportunity pool"`.

## 6. Develop 30 Technical Deep-Dive Records

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/build_deep_dive_records.py`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/deep_dive_30.jsonl`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/notes/deep_dive_30.md`

- [ ] Select 30 candidates across the capability families using a balanced rule: include high product value, high novelty, a range of evidence levels, and at least one low-risk, one medium-risk, and one frontier direction per major technical cluster.
- [ ] For each deep dive, write the concrete dataflow from sensor/ISP output to encoded video, including tensor or feature resolution when the source provides it.
- [ ] Describe the candidate model family: CNN/UNet, transformer, recurrent/causal network, optical-flow/warping, neural renderer, diffusion/DiT, flow matching, or hybrid ISP model.
- [ ] Record training data requirements, degradation synthesis, paired/unpaired setup, temporal sampling, mask/depth/IMU supervision, and any identity or perceptual embedding.
- [ ] Record losses or objectives by role: reconstruction, perceptual, adversarial/diffusion, temporal warp, identity, mask/boundary, color/photometric, exposure, smoothness, and rate/latency regularization.
- [ ] Do not invent loss weights. Use source-reported weights when available and otherwise describe weights as starting hypotheses requiring gradient and ablation checks.
- [ ] Define at least one causal online path and one higher-quality offline path when the function naturally supports both.
- [ ] Estimate resource requirements qualitatively unless a verified benchmark exists; label unmeasured FPS, latency, memory, and power as `not measured`.
- [ ] Define objective metrics and a human test: temporal flicker, warping error, LPIPS/PSNR/SSIM where relevant, identity similarity for portraits, exposure stability, boundary quality, user preference, and failure rate.
- [ ] Attach one or more source IDs and local PDF/page anchors or official document anchors to every technical claim.
- [ ] Commit the 30 deep dives with `git add -- tools/isp_video/build_deep_dive_records.py <project-dir>/metadata/deep_dive_30.jsonl <project-dir>/notes/deep_dive_30.md && git commit -m "research: analyze 30 mobile video opportunities"`.

## 7. Define and Analyze 10 Combined Innovation Concepts

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/build_priority_concepts.py`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/priority_10.jsonl`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/notes/priority_10.md`

- [ ] Select 10 combinations that produce a distinct user-visible capability rather than a list of independent toggles.
- [ ] For each concept, define one user story, a default interaction, real-time preview behavior, recording behavior, post-processing behavior, and a clear disable/rollback path.
- [ ] Draw a text architecture showing sensor inputs, ISP interfaces, semantic analysis, temporal memory, rendering/enhancement, color management, encoder, and metadata.
- [ ] Specify a minimum viable prototype using existing open-source models or a lightweight proxy; identify which component is the actual research risk.
- [ ] Define data collection and annotation: scene type, motion, illumination, subject identity, depth, masks, camera motion, audio events, and synthetic degradation when needed.
- [ ] Define quantitative acceptance criteria without fabricating values: state the metric, comparison baseline, target direction, and what must be measured on the target device.
- [ ] Explain the truth boundary and how the UI or metadata distinguishes restoration, enhancement, and generation.
- [ ] Add a competitor/prototype comparison using only verified source records; keep the proposed combination in a separate E5 column.
- [ ] Commit the 10 concepts with `git add -- tools/isp_video/build_priority_concepts.py <project-dir>/metadata/priority_10.jsonl <project-dir>/notes/priority_10.md && git commit -m "research: define priority mobile video concepts"`.

## 8. Build the Excel Opportunity Workbook

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/build_workbook.py`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/matrix/手机录像创新功能机会库.xlsx`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/matrix/手机录像创新功能机会库.xlsx.inspect.ndjson`

- [ ] Create the sheets specified in the design: `Opportunity_Map`, `Deep_Dive_30`, `Priority_10`, `Industry_Prototypes`, `Papers`, `Patents`, `Datasets`, and `Source_Manifest`.
- [ ] Keep one row per normalized record and use stable IDs so future batches can append without duplicating existing entries.
- [ ] Add filters, frozen headers, wrapped text, controlled-value columns, visible evidence level, verification status, and local source path.
- [ ] Add summary rows or a summary sheet with candidate counts by family, evidence level, video mode, truth boundary, and priority. Ensure formulas or generated counts match the source JSONL.
- [ ] Include a `Why this is a company/device` or `Why this is a source` field wherever a product or company attribution is used.
- [ ] Use a non-COM XLSX writer and validate the resulting ZIP package, workbook relationships, sheet names, row counts, and representative rows.
- [ ] Check that no source URL, local path, or paper ID is silently dropped during export.
- [ ] Commit only the workbook, inspection output, and builder with `git add -- tools/isp_video/build_workbook.py <project-dir>/matrix && git commit -m "docs: export ISP video opportunity workbook"`.

## 9. Write the Markdown and Word Reports

**Files:**
- Create: `D:/Repository/ReadPaper/tools/isp_video/build_report.py`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/report/手机录像创新功能与ISP技术机会洞察.md`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/report/手机录像创新功能与ISP技术机会洞察.docx`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/figures/` generated figures and source crops

- [ ] Write the report in Chinese with English terms in parentheses, defining specialized terms on first use.
- [ ] Include the research method, evidence grades, technology evolution, 14 capability families, the 100+ opportunity map summary, 30 deep dives, and 10 combined concepts.
- [ ] For each deep dive, include user effect, verified prototype, video conversion, algorithm/dataflow, temporal strategy, training data and losses, failure modes, truth boundary, and MVP.
- [ ] Include tables for cross-family comparison, real-time/online/offline modes, signal requirements, model families, and risk types.
- [ ] Use source-linked figures only when they are legally and technically appropriate: official diagrams/screenshots, paper figures, locally generated charts, and architecture diagrams derived from cited sources. Mark adapted diagrams as adapted rather than original.
- [ ] Include a separate section for research gaps: temporal identity stability, controllable generative rendering, low-light motion, lens-switch continuity, power-aware quality scaling, and joint audio-video control.
- [ ] Explicitly distinguish measured results, source-reported results, qualitative judgments, and unmeasured hypotheses.
- [ ] Generate the DOCX using the repository documents workflow, set readable Chinese fonts, use consistent heading levels, captions, source notes, and page numbering.
- [ ] Render the DOCX to page images/PDF with `render_docx.py` when available; inspect representative first, middle, table-heavy, figure-heavy, and final pages for overflow, missing glyphs, clipped images, and unreadable tables.
- [ ] Commit the reports and figures with `git add -- tools/isp_video/build_report.py <project-dir>/report <project-dir>/figures && git commit -m "docs: write ISP video innovation insight report"`.

## 10. Final Cross-Artifact Verification

**Files:**
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/metadata/validation_report.json`
- Create: `D:/Repository/ReadPaper/daily/20260826_ISP_VIDEO_INNOVATION/notes/final_audit.md`

- [ ] Verify the candidate count is at least 100 and every capability family is represented.
- [ ] Verify exactly 30 deep-dive IDs and exactly 10 priority-concept IDs exist, with all IDs present in the base opportunity pool.
- [ ] Verify every E1-E4 claim in Excel and Word has a source ID, source URL, local path, and verification status.
- [ ] Verify every E5 record is explicitly labeled as a report proposal and is not counted as an existing product.
- [ ] Verify counts and names match across JSONL, Excel, Markdown, and DOCX source tables.
- [ ] Verify all local paths with `Test-Path`; verify all PDFs with a page count and text extraction check; verify all images have nonzero dimensions.
- [ ] Run `git diff --check` on text files and inspect the final `git status --short --branch`.
- [ ] Write a final audit that states what was verified, what was not accessible, what was not measured, and which claims are hypotheses.
- [ ] Commit the validation artifacts with `git add -- <project-dir>/metadata/validation_report.json <project-dir>/notes/final_audit.md && git commit -m "qa: validate ISP video research artifacts"`.

## Self-Review Against the Design

- The 14 capability families are covered in Tasks 2, 5, 6, and 7.
- The E1-E5 evidence boundary is implemented in Tasks 2, 3, 4, 5, and 10.
- The 100+ / 30 / 10 deliverable levels are implemented in Tasks 5, 6, and 7.
- The video-first requirement is enforced in Tasks 5, 6, 7, and 10.
- Training data, losses, temporal stability, ISP placement, and edge constraints are covered in Task 6 and carried into Task 9.
- The Excel sheet structure and non-COM verification are covered in Task 8.
- The Word report structure, source figure handling, and visual QA are covered in Task 9.
- Local evidence, cross-artifact consistency, and explicit unmeasured claims are covered in Task 10.
- No task contains unresolved placeholder markers or a vague implementation instruction; every implementation step has a target file or an explicit validation command.
