# Portrait Mask Conditioning Report Expansion Design

## Goal

Expand the existing PortraitSR learning manual with an evidence-backed chapter explaining how portrait masks can control restoration, enhancement, relighting, background processing, local editing, virtual try-on, and video consistency, with particular emphasis on loss design and training data construction.

## Scope

The chapter treats mask conditioning as a spatial control system rather than a single binary input. It covers four representations:

1. Binary foreground or edit masks.
2. Multi-class semantic parsing masks for face, skin, hair, facial parts, clothes, body, accessories, and background.
3. Soft alpha, boundary, uncertainty, and occlusion maps.
4. Per-region confidence and edit-strength maps.

The primary scope is portrait restoration and photographic effects. Generative local editing is included only where its architecture or loss design transfers directly to portrait systems. Identity preservation, unchanged-region preservation, boundary quality, and factual-detail safety remain mandatory constraints.

## Evidence Model

Each paper record must include bibliographic metadata, author affiliations, task, mask representation, mask injection point, loss terms, data construction, source pages, PDF hash, and evidence level. Original paper statements are separated from cross-paper synthesis and recommended recipes.

Core local evidence includes AuthFace, HeadsUp, GeoMAR, and NTIRE 2026. New external evidence targets BrushNet, PowerPaint, AnyDoor, CosmicMan, StableVITON, IDM-VTON, Sapiens, SAM 2, MatAnyone, SynthLight, Text2Relight, and Generative Portrait Shadow Removal.

## Report Structure

The new chapter will contain:

1. Mask taxonomy and the effects enabled by each representation.
2. Conditioning architectures: channel concatenation, ControlNet or adapter injection, region tokens, attention gating, latent blending, and multi-branch conditioning.
3. Region-normalized losses, unchanged-region preservation, boundary and alpha losses, face identity and component losses, region adversarial and frequency losses, and temporal mask consistency.
4. Training data creation: parsing, matting, confidence calibration, mask corruption, region-aware degradation, edit-pair synthesis, and identity-disjoint splits.
5. A recommended multi-task training recipe and ablation matrix for mobile portrait imaging.
6. Failure modes, safety gates, and effect-by-effect deployment recommendations.

## Output Files

- Extend `daily/PortraitSR/report/人像超分与人脸细节恢复_阶段性洞察_20260806.md`.
- Rebuild `daily/PortraitSR/report/人像超分与人脸细节恢复_阶段性洞察_20260806.docx`.
- Add PDFs under `daily/PortraitSR/papers/07_mask_conditioning/`.
- Add source metadata under `daily/PortraitSR/sources/mask_conditioning/`.
- Add `daily/PortraitSR/metadata/mask_conditioning_evidence_matrix.json`.
- Add original paper pages under `daily/PortraitSR/figures/mask_conditioning/`.

## Verification

Verify downloaded PDFs by header, page count, size, and SHA-256. Verify that cited screenshots exist and match the intended page. Rebuild the Word document and check OOXML media relationships, paragraph and table counts, required chapter keywords, and image count. Attempt full DOCX rendering; if Word or LibreOffice remains unavailable, disclose that visual page rendering could not be completed.
