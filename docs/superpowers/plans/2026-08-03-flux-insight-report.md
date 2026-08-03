# FLUX Insight Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a verified FLUX paper library and a visually checked bilingual Word study guide under `D:\Repository\ReadPaper\daily\Flux`.

**Architecture:** A resumable metadata-first pipeline discovers candidate papers, downloads PDFs, extracts text, verifies explicit FLUX usage, and records inclusion or exclusion evidence. A separate report builder consumes only the verified manifest, crops original paper figures, produces an Excel index and DOCX, then exports the DOCX to PDF for page-by-page visual QA.

**Tech Stack:** PowerShell, bundled Python, requests, feedparser/XML, pypdf/pdfplumber, Poppler, Pillow, python-docx, openpyxl, Microsoft Word COM for PDF export.

---

### Task 1: Create the FLUX library skeleton and canonical seed list

**Files:**
- Create: `daily/Flux/metadata/seed_papers.json`
- Create: `daily/Flux/metadata/README.md`
- Create: `tools/flux_library/config.py`
- Test: `tools/flux_library/tests/test_config.py`

- [ ] **Step 1: Write a test asserting the five category directories and canonical reading order.**
- [ ] **Step 2: Run the test and confirm it fails because the configuration does not exist.**
- [ ] **Step 3: Implement path constants, category mapping, cutoff date `2026-08-03`, and seed records for DiT, Rectified Flow, Flow Matching, SD3, FLUX official material, FluxSR, DreamSR, OP4KSR, FoA-SR, LucidFlux, ResFlow-Tuner, and previously identified restoration papers.**
- [ ] **Step 4: Run the test and verify all expected directories and identifiers are represented.**
- [ ] **Step 5: Create the physical directory skeleton without modifying existing DreamSR files.**

### Task 2: Implement resumable academic discovery

**Files:**
- Create: `tools/flux_library/discover.py`
- Create: `tools/flux_library/normalize.py`
- Create: `tools/flux_library/tests/test_normalize.py`
- Output: `daily/Flux/metadata/candidates.json`

- [ ] **Step 1: Add title, arXiv ID, DOI, and URL normalization tests, including false-positive biomedical uses of the word flux.**
- [ ] **Step 2: Run tests and confirm normalization functions are missing.**
- [ ] **Step 3: Implement arXiv and OpenAlex searches with conservative rate limits, retries, raw-response caching, and query provenance.**
- [ ] **Step 4: Deduplicate by arXiv ID, DOI, then normalized title while preserving every discovery source.**
- [ ] **Step 5: Run discovery for foundations, SR/restoration, and efficiency queries through the cutoff date.**

### Task 3: Download and validate PDFs and official model material

**Files:**
- Create: `tools/flux_library/download.py`
- Create: `tools/flux_library/tests/test_download_validation.py`
- Output: `daily/Flux/metadata/download_manifest.json`
- Output: `daily/Flux/papers/**.pdf`
- Output: `daily/Flux/model_cards/**`

- [ ] **Step 1: Add tests for PDF magic bytes, minimum size, page count, HTML masquerading as PDF, stable filenames, and SHA-256 recording.**
- [ ] **Step 2: Run tests and confirm validation helpers are missing.**
- [ ] **Step 3: Implement resumable downloads with temporary files, source fallback, and existing-file hash verification.**
- [ ] **Step 4: Copy the verified DreamSR PDF into `03_super_resolution` and record its original local source.**
- [ ] **Step 5: Download official FLUX model cards/pages as HTML or Markdown snapshots with retrieval dates.**
- [ ] **Step 6: Reopen every PDF and record page count, hash, size, and final status.**

### Task 4: Extract text and verify explicit FLUX usage

**Files:**
- Create: `tools/flux_library/extract_and_verify.py`
- Create: `tools/flux_library/tests/test_flux_evidence.py`
- Output: `daily/Flux/metadata/flux_papers.json`
- Output: `daily/Flux/metadata/flux_papers.csv`
- Output: `daily/Flux/metadata/excluded_candidates.csv`
- Output: `daily/Flux/text/**.txt`

- [ ] **Step 1: Add evidence tests distinguishing explicit model use from citations, related-work mentions, and unrelated scientific flux terminology.**
- [ ] **Step 2: Run tests and confirm evidence classification is missing.**
- [ ] **Step 3: Extract complete text with page markers and first-page metadata.**
- [ ] **Step 4: Record evidence snippets, page numbers, FLUX version, role, task, and confidence.**
- [ ] **Step 5: Mark ambiguous candidates for manual inspection and inspect each before inclusion.**
- [ ] **Step 6: Produce final included and excluded manifests with reasons.**

### Task 5: Extract original figures and experimental evidence

**Files:**
- Create: `tools/flux_library/extract_figures.py`
- Create: `daily/Flux/metadata/figure_manifest.json`
- Output: `daily/Flux/figures/**.png`

- [ ] **Step 1: Render relevant PDF pages at a readable DPI.**
- [ ] **Step 2: Crop original architecture, pipeline, qualitative-result, quantitative-table, ablation, and efficiency figures for the main reading sequence.**
- [ ] **Step 3: Record paper key, Figure/Table number, PDF page, crop coordinates, and caption.**
- [ ] **Step 4: Visually inspect every crop and correct wrong pages, clipped captions, or unreadable text.**

### Task 6: Build and verify the Excel paper index

**Files:**
- Create: `tools/flux_library/build_index_xlsx.py`
- Create: `tools/flux_library/tests/test_index_xlsx.py`
- Output: `daily/Flux/FLUX论文索引.xlsx`

- [ ] **Step 1: Add workbook tests for the six required sheets and mandatory evidence/download columns.**
- [ ] **Step 2: Run tests and confirm the workbook does not exist.**
- [ ] **Step 3: Build `阅读主线`, `全量论文`, `超分与复原`, `效率优化`, `下载清单`, and `排除记录` sheets from verified manifests.**
- [ ] **Step 4: Apply filters, frozen headers, deliberate widths, wrapping, and links to local PDFs and public sources.**
- [ ] **Step 5: Reopen the workbook with openpyxl and validate formulas, counts, links, and sheet names.**

### Task 7: Write the bilingual FLUX study guide

**Files:**
- Create: `tools/flux_library/build_report_docx.py`
- Create: `daily/Flux/report/FLUX系列模型与超分辨率技术深度洞察报告.md`
- Output: `daily/Flux/report/FLUX系列模型与超分辨率技术深度洞察报告.docx`

- [ ] **Step 1: Draft the report in the approved sequence, separating paper facts, author explanations, and report analysis.**
- [ ] **Step 2: Include full deep-dive chapters for the foundation sequence, FluxSR, DreamSR, OP4KSR, FoA-SR, LucidFlux, ResFlow-Tuner, and major efficiency families.**
- [ ] **Step 3: Include every verified efficiency paper in a structured matrix even when it does not receive a full narrative case study.**
- [ ] **Step 4: Insert original paper screenshots with source paper, Figure/Table number, and local PDF page.**
- [ ] **Step 5: Add formulas, bilingual terminology, model/version comparison, hardware results, reproducibility audit, camera/mobile insight, limitations, and staged reading exercises.**
- [ ] **Step 6: Generate a compact-reference-guide DOCX using Calibri and Microsoft YaHei with explicit table geometry and page numbers.**

### Task 8: Render and perform visual QA

**Files:**
- Output: `daily/Flux/report/FLUX系列模型与超分辨率技术深度洞察报告.pdf`
- Output: `daily/Flux/report/qa_render/page-*.png`

- [ ] **Step 1: Export the DOCX to PDF using Microsoft Word or the canonical documents renderer when available.**
- [ ] **Step 2: Render every PDF page to PNG.**
- [ ] **Step 3: Inspect every page for wrong figures, clipping, overlap, small text, broken Chinese glyphs, table overflow, bad page breaks, and inconsistent headers/footers.**
- [ ] **Step 4: Revise the report builder and repeat export/render until the entire document passes visual inspection.**

### Task 9: Final audit

**Files:**
- Create: `daily/Flux/README.md`

- [ ] **Step 1: Verify every included record has a valid PDF or an explicitly documented official-material exception.**
- [ ] **Step 2: Verify every full-report citation resolves to the local library and public source.**
- [ ] **Step 3: Verify the report, index, manifests, model cards, figures, and papers all reside under `daily/Flux`.**
- [ ] **Step 4: Record final counts, excluded candidates, known retrieval failures, and the recommended daily reading order in the README.**
