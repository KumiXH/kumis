# Portrait Mask Conditioning Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a detailed, source-verifiable portrait mask conditioning chapter to the existing PortraitSR Markdown and Word reports.

**Architecture:** Build a small local evidence corpus first, normalize paper evidence into JSON, render selected original pages, then generate the same chapter in Markdown and DOCX from verified facts plus explicitly labeled cross-paper recommendations.

**Tech Stack:** PowerShell, arXiv/OpenAlex APIs, Poppler, Python, PyMuPDF/pypdf, python-docx, JSON.

---

### Task 1: Build the mask-conditioning source corpus

**Files:**
- Create: `daily/PortraitSR/papers/07_mask_conditioning/*.pdf`
- Create: `daily/PortraitSR/sources/mask_conditioning/*.json`

- [ ] Download the selected primary PDFs sequentially from arXiv or official open-access sources.
- [ ] Record title, authors, date, venue, URL, local path, page count, size, and SHA-256.
- [ ] Reject HTML error pages and incomplete PDFs.

### Task 2: Extract paper-level evidence

**Files:**
- Create: `daily/PortraitSR/text/mask_*.txt`
- Create: `daily/PortraitSR/metadata/mask_conditioning_evidence_matrix.json`

- [ ] Extract page-delimited text from every downloaded PDF.
- [ ] Record mask representation, model injection, losses, data, training, affiliations, page evidence, and limitations.
- [ ] Mark each field as original-paper evidence or cross-paper synthesis.

### Task 3: Render original architecture and result pages

**Files:**
- Create: `daily/PortraitSR/figures/mask_conditioning/*.png`
- Modify: `tools/portrait_sr/render_representative_pages.py`

- [ ] Select pages that show mask-conditioned architecture, regional losses, parsing labels, relighting controls, or qualitative effects.
- [ ] Render each page at readable resolution with Poppler.
- [ ] Visually inspect every new page and correct any page-number mismatch.

### Task 4: Expand the Markdown report

**Files:**
- Modify: `daily/PortraitSR/report/人像超分与人脸细节恢复_阶段性洞察_20260806.md`

- [ ] Add the mask taxonomy and effect matrix.
- [ ] Add conditioning architectures and equations.
- [ ] Add region-normalized loss recipes and conflict analysis.
- [ ] Add data construction, mask corruption, multi-task training, ablations, failure handling, and mobile-camera recommendations.
- [ ] Add original-paper screenshots and references.

### Task 5: Expand and rebuild the Word report

**Files:**
- Modify: `tools/portrait_sr/build_report_docx.py`
- Modify: `daily/PortraitSR/report/人像超分与人脸细节恢复_阶段性洞察_20260806.docx`

- [ ] Mirror the Markdown chapter with compact prose, comparison tables, equations, and original figures.
- [ ] Preserve the existing visual system and Chinese-first technical terminology.
- [ ] Rebuild the DOCX and verify media relationships and required text.

### Task 6: Final verification and index update

**Files:**
- Modify: `daily/PortraitSR/README.md`

- [ ] Verify every new PDF hash and cited page.
- [ ] Verify Markdown image references and DOCX media relationships.
- [ ] Attempt DOCX rendering and disclose any unavailable renderer.
- [ ] Update the README with the new mask-conditioning corpus and chapter.
