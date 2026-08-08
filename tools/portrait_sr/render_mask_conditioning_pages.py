import json
import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "daily" / "PortraitSR"
PDF_DIR = ROOT / "papers" / "07_mask_conditioning"
OUTPUT = ROOT / "figures" / "mask_conditioning"
INDEX = ROOT / "metadata" / "mask_conditioning_figure_index.json"
PDFTOPPM = os.environ.get("PDFTOPPM") or shutil.which("pdftoppm")

SELECTIONS = [
    ("brushnet_architecture", "brushnet_2403.06976.pdf", 6, "BrushNet dual-branch mask conditioning"),
    ("powerpaint_tasks", "powerpaint_2312.03594.pdf", 5, "PowerPaint task-prompt architecture"),
    ("anydoor_architecture", "anydoor_2307.09481.pdf", 3, "AnyDoor ID, detail-map and shape-mask conditioning"),
    ("cosmicman_parsing", "cosmicman_2404.01294.pdf", 5, "CosmicMan human parsing and region-text labels"),
    ("stableviton_architecture", "stableviton_2312.01725.pdf", 4, "StableVITON agnostic mask and semantic correspondence"),
    ("idm_vton_architecture", "idm_vton_2403.05139.pdf", 5, "IDM-VTON garment conditioning architecture"),
    ("sapiens_parsing", "sapiens_2408.12569.pdf", 6, "Sapiens 28-class human parsing"),
    ("matanyone_architecture", "matanyone_2501.14677.pdf", 4, "MatAnyone alpha-matting memory architecture"),
    ("matanyone_results", "matanyone_2501.14677.pdf", 6, "MatAnyone temporal matting results"),
    ("synthlight_architecture", "synthlight_2501.09756.pdf", 4, "SynthLight synthetic-to-real relighting training"),
    ("synthlight_results", "synthlight_2501.09756.pdf", 6, "SynthLight portrait relighting effects"),
    ("compose_architecture", "compose_2406.12013.pdf", 4, "COMPOSE portrait shadow editing pipeline"),
    ("compose_results", "compose_2406.12013.pdf", 11, "COMPOSE controllable shadow editing"),
    ("softshadow_architecture", "softshadow_2409.07041.pdf", 3, "SoftShadow soft-mask architecture and losses"),
    ("softshadow_results", "softshadow_2409.07041.pdf", 7, "SoftShadow penumbra-aware results"),
]


def main() -> None:
    if not PDFTOPPM:
        raise SystemExit("pdftoppm not found; install Poppler or set PDFTOPPM")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for key, filename, page, purpose in SELECTIONS:
        pdf_path = PDF_DIR / filename
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        prefix = OUTPUT / f"{key}_p{page:02d}"
        subprocess.run(
            [PDFTOPPM, "-f", str(page), "-l", str(page), "-png", "-r", "180", str(pdf_path), str(prefix)],
            check=True,
            capture_output=True,
            text=True,
            timeout=240,
        )
        rendered = next(OUTPUT.glob(f"{prefix.name}-*.png"))
        final = OUTPUT / f"{key}_page_{page:02d}.png"
        if final.exists():
            final.unlink()
        rendered.replace(final)
        records.append(
            {
                "key": key,
                "paper": filename,
                "page": page,
                "purpose": purpose,
                "pdf": pdf_path.relative_to(ROOT).as_posix(),
                "image": final.relative_to(ROOT).as_posix(),
            }
        )
        print(f"rendered {key} page {page}", flush=True)

    INDEX.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"records={len(records)} output={INDEX}")


if __name__ == "__main__":
    main()
