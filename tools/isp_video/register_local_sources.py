"""Register already collected local papers and project documents as evidence sources."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\Repository\ReadPaper\daily\20260826_后处理调研")
MANIFEST = ROOT / "sources" / "source_manifest.json"

LOCAL_ITEMS = [
    ("local_flashvsr", "paper", "FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation", "ReadPaper local ENC_DEC library", "FlashVSR case", "D:/Repository/ReadPaper/daily/20260821_ENC_DEC/papers/05_flashvsr_case/flashvsr_2510.12747.pdf", "E3", "Local verified paper copy used for video restoration and one-step inference study.", "Paper source is local; external publication metadata should be checked separately."),
    ("local_magvit", "paper", "MAGVIT: Masked Generative Video Transformer", "ReadPaper local ENC_DEC library", "video tokenizer", "D:/Repository/ReadPaper/daily/20260821_ENC_DEC/papers/03_video_vae/magvit_2212.05199.pdf", "E3", "Local paper copy used for video tokenizer and temporal latent representation study.", "The paper is a general video generation/tokenizer source, not a phone product claim."),
    ("local_wfvae", "paper", "WF-VAE: Wavelet Flow VAE for Video Compression", "ReadPaper local ENC_DEC library", "video VAE", "D:/Repository/ReadPaper/daily/20260821_ENC_DEC/papers/03_video_vae/wfvae_2411.17459.pdf", "E3", "Local paper copy used for wavelet and video VAE analysis.", "General codec/latent source; phone deployment is a research interpretation."),
    ("local_dit", "paper", "Scalable Diffusion Models with Transformers", "ReadPaper local Flux library", "DiT foundation", "D:/Repository/ReadPaper/daily/Flux/papers/01_foundations/dit_2212.09748.pdf", "E3", "Local paper copy used for DiT and latent-space transformer foundations.", "General foundation paper; does not itself prove mobile video feasibility."),
    ("local_fluxsr", "paper", "FluxSR", "ReadPaper local Flux library", "FLUX super-resolution", "D:/Repository/ReadPaper/daily/Flux/papers/03_super_resolution/fluxsr_2502.01993.pdf", "E3", "Local paper copy used for FLUX-based super-resolution study.", "Image restoration source; video extension is a proposed direction."),
    ("local_dreamsr", "paper", "DreamSR", "ReadPaper local Flux library", "FLUX super-resolution", "D:/Repository/ReadPaper/daily/Flux/papers/03_super_resolution/dreamsr_2605.15682.pdf", "E3", "Local paper copy used for diffusion/FLUX super-resolution study.", "Image restoration source; video extension is a proposed direction."),
    ("local_op4ksr", "paper", "OP4KSR", "ReadPaper local Flux library", "4K super-resolution", "D:/Repository/ReadPaper/daily/Flux/papers/03_super_resolution/op4ksr_2605.13457.pdf", "E3", "Local paper copy used for high-resolution super-resolution study.", "Image restoration source; video extension is a proposed direction."),
    ("local_foa_sr", "paper", "FoA-SR", "ReadPaper local Flux library", "FLUX super-resolution", "D:/Repository/ReadPaper/daily/Flux/papers/03_super_resolution/foa_sr_2606.10275.pdf", "E3", "Local paper copy used for FLUX-based restoration study.", "Image restoration source; video extension is a proposed direction."),
    ("local_fluxir", "paper", "Acquire and then Adapt / FluxIR", "ReadPaper local Flux library", "FLUX image restoration", "D:/Repository/ReadPaper/daily/Flux/papers/04_image_restoration/acquire_adapt_fluxir_2504.15159.pdf", "E3", "Local paper copy used for FLUX restoration and adaptation study.", "Image restoration source; video extension is a proposed direction."),
    ("local_lucidflux", "paper", "LucidFlux", "ReadPaper local Flux library", "FLUX restoration", "D:/Repository/ReadPaper/daily/Flux/papers/04_image_restoration/lucidflux_2509.22414.pdf", "E3", "Local paper copy used for FLUX restoration study.", "Image restoration source; video extension is a proposed direction."),
    ("local_resflow_tuner", "paper", "ResFlow-Tuner", "ReadPaper local Flux library", "FLUX restoration", "D:/Repository/ReadPaper/daily/Flux/papers/04_image_restoration/resflow_tuner_2603.22027.pdf", "E3", "Local paper copy used for flow-based restoration adaptation study.", "Image restoration source; video extension is a proposed direction."),
    ("local_tiger", "paper", "TIGER: A Training Framework for Video Face Restoration", "ReadPaper local PortraitSR library", "video face restoration", "D:/Repository/ReadPaper/daily/PortraitSR/papers/04_video_face/tiger_2606.24336.pdf", "E3", "Local paper copy used for temporal face restoration and data construction study.", "Portrait restoration source; not a phone product claim."),
    ("local_svfr", "paper", "SVFR", "ReadPaper local PortraitSR library", "video face restoration", "D:/Repository/ReadPaper/daily/PortraitSR/papers/04_video_face/svfr_2501.01235.pdf", "E3", "Local paper copy used for video face restoration study.", "Portrait restoration source; not a phone product claim."),
    ("local_geomar", "paper", "GeoMar", "ReadPaper local PortraitSR library", "face restoration", "D:/Repository/ReadPaper/daily/PortraitSR/papers/01_single_face/geomar_2608.03923.pdf", "E3", "Local paper copy used for geometry-aware face restoration study.", "Portrait restoration source; not a phone product claim."),
    ("local_authface", "paper", "AuthFace", "ReadPaper local PortraitSR library", "identity-preserving face restoration", "D:/Repository/ReadPaper/daily/PortraitSR/papers/01_single_face/authface_2410.09864.pdf", "E3", "Local paper copy used for identity-aware face restoration study.", "Identity preservation source; not a phone product claim."),
    ("local_heads_up", "paper", "Heads Up", "ReadPaper local PortraitSR library", "portrait restoration", "D:/Repository/ReadPaper/daily/PortraitSR/papers/02_portrait_scene/heads_up_2510.09924.pdf", "E3", "Local paper copy used for portrait scene restoration study.", "Portrait restoration source; not a phone product claim."),
]


def main() -> None:
    if MANIFEST.exists():
        records = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        records = []
    existing = {row.get("source_id") for row in records}
    stamp = datetime.now(timezone.utc).isoformat()
    for source_id, source_type, title, publisher, product, path, level, quote, scope in LOCAL_ITEMS:
        if source_id in existing:
            continue
        local = Path(path)
        records.append(
            {
                "source_id": source_id,
                "source_type": source_type,
                "title": title,
                "publisher_or_authors": publisher,
                "product_or_venue": product,
                "date": "",
                "url": "",
                "local_path": str(local) if local.exists() else "",
                "evidence_level": level,
                "access_status": "local_cache",
                "verification_status": "verified" if local.exists() else "pending",
                "evidence_quote": quote,
                "scope_limit": scope,
                "retrieved_at": stamp,
                "sha256": "",
            }
        )
    MANIFEST.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registered local sources; total manifest records: {len(records)}")


if __name__ == "__main__":
    main()
