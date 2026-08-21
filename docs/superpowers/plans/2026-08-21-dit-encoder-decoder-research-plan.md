# DiT Encoder Decoder Research Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an evidence-backed bilingual learning package on authoritative image/video encoders and decoders used with DiT, including architecture, training, dataset construction, tensor input flow, and a code-level FlashVSR case study.

**Architecture:** The deliverable separates tokenizer/VAE pretraining, frozen-latent DiT training, and restoration-specific adaptation. Evidence is stored as source PDFs, official-code snapshots, metadata records, and paper-native figures; a generated DOCX synthesizes those materials and is rendered page by page for QA.

**Tech Stack:** PowerShell, GitHub/arXiv/OpenAlex/Crossref APIs, PyMuPDF, python-docx, openpyxl, Mermaid/PNG diagrams, LibreOffice document rendering.

---

### Task 1: Create the research package structure

**Files:**
- Create: `daily/20260821_ENC_DEC/README.md`
- Create: `daily/20260821_ENC_DEC/metadata/research_scope.md`

- [ ] **Step 1:** Create folders for papers, figures, source code, metadata, report, render output, and scripts.
- [ ] **Step 2:** Record the inclusion criteria: authoritative or widely adopted architecture; primary paper or official implementation; direct relevance to DiT latent representation, image/video tokenization, or restoration decoding.
- [ ] **Step 3:** Record the evidence labels `paper-verified`, `code-verified`, `model-card-verified`, and `analysis`.
- [ ] **Step 4:** Verify all expected directories with `Test-Path`.

### Task 2: Build and verify the source manifest

**Files:**
- Create: `daily/20260821_ENC_DEC/metadata/source_manifest.csv`
- Create: `daily/20260821_ENC_DEC/metadata/source_manifest.json`

- [ ] **Step 1:** Add historical sources for VAE, VQ-VAE, VQGAN, latent diffusion, and DiT.
- [ ] **Step 2:** Add image tokenizer/VAE sources for Stable Diffusion, SDXL, SD3, FLUX, and modern high-compression tokenizers.
- [ ] **Step 3:** Add video tokenizer/VAE sources for MAGVIT, MAGVIT-v2, VideoGPT, CogVideoX, Open-Sora, HunyuanVideo, and Wan.
- [ ] **Step 4:** Add restoration sources and the official FlashVSR paper, repository, code paths, model repository, and VSR-120K dataset page.
- [ ] **Step 5:** Check every source URL and record HTTP status, publication status, venue, year, and source type.

### Task 3: Download primary papers and official code snapshots

**Files:**
- Create: `daily/20260821_ENC_DEC/papers/01_history_and_tokenizers/*.pdf`
- Create: `daily/20260821_ENC_DEC/papers/02_image_vae/*.pdf`
- Create: `daily/20260821_ENC_DEC/papers/03_video_vae/*.pdf`
- Create: `daily/20260821_ENC_DEC/papers/04_dit_training/*.pdf`
- Create: `daily/20260821_ENC_DEC/papers/05_flashvsr_case/*.pdf`
- Create: `daily/20260821_ENC_DEC/source_code/*`

- [ ] **Step 1:** Download PDFs only from arXiv, proceedings, publisher, or author-controlled official sources.
- [ ] **Step 2:** Save FlashVSR `TCDecoder.py`, LQ projection definition, inference pipeline, Wan VAE, and model README with repository commit SHA.
- [ ] **Step 3:** Save official configs or source for LDM/SD, SD3, FLUX, CogVideoX, HunyuanVideo, Open-Sora, and Wan encoders/decoders.
- [ ] **Step 4:** Validate each PDF signature, page count, file size, and SHA-256; flag unavailable files instead of fabricating local evidence.

### Task 4: Extract architecture and training evidence

**Files:**
- Create: `daily/20260821_ENC_DEC/metadata/architecture_matrix.csv`
- Create: `daily/20260821_ENC_DEC/metadata/training_matrix.csv`
- Create: `daily/20260821_ENC_DEC/metadata/dataset_matrix.csv`

- [ ] **Step 1:** Extract spatial and temporal compression ratios, latent channels, quantization type, causality, input range, and output range.
- [ ] **Step 2:** Extract reconstruction, perceptual, KL, codebook, adversarial, temporal, frequency, and task-specific losses with page or code anchors.
- [ ] **Step 3:** Extract dataset sources, cleaning, frame sampling, crop/bucket policy, degradation construction, and image-video mixing.
- [ ] **Step 4:** Separate explicitly reported facts from implementation-derived facts and engineering recommendations.
- [ ] **Step 5:** Cross-check inconsistent values against a second primary source or mark them unresolved.

### Task 5: Create paper-native and explanatory figures

**Files:**
- Create: `daily/20260821_ENC_DEC/figures/paper_figures/*.png`
- Create: `daily/20260821_ENC_DEC/figures/explanatory/*.png`

- [ ] **Step 1:** Crop representative architecture, reconstruction comparison, and ablation figures from the downloaded PDFs with page captions.
- [ ] **Step 2:** Create a chronological encoder/decoder evolution timeline.
- [ ] **Step 3:** Create image and video tensor-flow diagrams with concrete shapes.
- [ ] **Step 4:** Create a FlashVSR diagram distinguishing `LQ_proj_in`, the Wan DiT, the full Wan VAE decoder, and `TCDecoder`.
- [ ] **Step 5:** Verify image dimensions, legibility, source labels, and absence of clipping.

### Task 6: Build the auditable workbook

**Files:**
- Create: `daily/20260821_ENC_DEC/编解码器论文与来源索引.xlsx`

- [ ] **Step 1:** Add sheets for source index, architecture comparison, training losses, datasets and input pipeline, FlashVSR modules, and terminology.
- [ ] **Step 2:** Add paper title, year, venue, model family, official URL, local PDF, evidence status, and notes.
- [ ] **Step 3:** Add filters, frozen headers, deliberate column widths, hyperlinks, and evidence color coding.
- [ ] **Step 4:** Inspect workbook ZIP structure, sheet names, dimensions, formulas, hyperlinks, and representative rows without relying on Excel COM.

### Task 7: Write the bilingual deep-dive report

**Files:**
- Create: `daily/20260821_ENC_DEC/report/DiT编解码器发展架构训练与数据工程深度洞察.docx`

- [ ] **Step 1:** Write the historical evolution and clarify encoder, decoder, tokenizer, VAE, and latent-space terminology.
- [ ] **Step 2:** Analyze each authoritative image and video architecture at module and tensor levels.
- [ ] **Step 3:** Explain tokenizer/VAE pretraining, DiT latent training, and restoration adaptation as separate training regimes.
- [ ] **Step 4:** Explain loss combinations, optimization stages, discriminator scheduling, and failure modes.
- [ ] **Step 5:** Explain image/video/paired-SR dataset construction and exact input transformations.
- [ ] **Step 6:** Add the detailed FlashVSR module case and code anchors for `LQ_proj_in`, `TCDecoder`, and Wan decoder.
- [ ] **Step 7:** Add comparative conclusions, architecture selection guidance, reproducibility checklist, glossary, and references.

### Task 8: Render and verify the final artifacts

**Files:**
- Create: `daily/20260821_ENC_DEC/rendered_report/*.png`
- Create: `daily/20260821_ENC_DEC/report/DiT编解码器发展架构训练与数据工程深度洞察_QA.pdf`
- Create: `daily/20260821_ENC_DEC/metadata/qa_report.json`

- [ ] **Step 1:** Run DOCX structural checks for headings, captions, tables, hyperlinks, image relationships, and bibliography completeness.
- [ ] **Step 2:** Render the DOCX to page images and PDF with the bundled document renderer.
- [ ] **Step 3:** Inspect all pages for overflow, tiny type, broken Chinese fonts, blank pages, clipped tables, and detached captions.
- [ ] **Step 4:** Correct layout defects and rerender until checks pass.
- [ ] **Step 5:** Report exact artifact paths, counts, unresolved source limitations, and validation evidence.
