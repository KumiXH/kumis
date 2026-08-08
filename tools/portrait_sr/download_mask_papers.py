import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(r"D:\Repository\ReadPaper\daily\PortraitSR")
OUTPUT = ROOT / "papers" / "07_mask_conditioning"
MANIFEST = ROOT / "metadata" / "mask_conditioning_download_manifest.json"

PAPERS = [
    {
        "key": "brushnet",
        "title": "BrushNet: A Plug-and-Play Image Inpainting Model with Decomposed Dual-Branch Diffusion",
        "arxiv_id": "2403.06976",
        "urls": ["https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/03014.pdf"],
    },
    {
        "key": "powerpaint",
        "title": "A Task Is Worth One Word: Learning with Task Prompts for High-Quality Versatile Image Inpainting",
        "arxiv_id": "2312.03594",
        "urls": ["https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07554.pdf"],
    },
    {
        "key": "anydoor",
        "title": "AnyDoor: Zero-shot Object-level Image Customization",
        "arxiv_id": "2307.09481",
        "urls": ["https://openaccess.thecvf.com/content/CVPR2024/papers/Chen_AnyDoor_Zero-shot_Object-level_Image_Customization_CVPR_2024_paper.pdf"],
    },
    {
        "key": "cosmicman",
        "title": "CosmicMan: A Text-to-Image Foundation Model for Humans",
        "arxiv_id": "2404.01294",
        "urls": ["https://openaccess.thecvf.com/content/CVPR2024/papers/Li_CosmicMan_A_Text-to-Image_Foundation_Model_for_Humans_CVPR_2024_paper.pdf"],
    },
    {
        "key": "stableviton",
        "title": "StableVITON: Learning Semantic Correspondence with Latent Diffusion Model for Virtual Try-On",
        "arxiv_id": "2312.01725",
        "urls": ["https://openaccess.thecvf.com/content/CVPR2024/papers/Kim_StableVITON_Learning_Semantic_Correspondence_with_Latent_Diffusion_Model_for_Virtual_CVPR_2024_paper.pdf"],
    },
    {
        "key": "idm_vton",
        "title": "Improving Diffusion Models for Authentic Virtual Try-on in the Wild",
        "arxiv_id": "2403.05139",
        "urls": ["https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/11626.pdf"],
    },
    {
        "key": "sapiens",
        "title": "Sapiens: Foundation for Human Vision Models",
        "arxiv_id": "2408.12569",
        "urls": ["https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/00529.pdf"],
    },
    {
        "key": "sam2",
        "title": "SAM 2: Segment Anything in Images and Videos",
        "arxiv_id": "2408.00714",
        "urls": [],
    },
    {
        "key": "matanyone",
        "title": "MatAnyone: Stable Video Matting with Consistent Memory Propagation",
        "arxiv_id": "2501.14677",
        "urls": ["https://openaccess.thecvf.com/content/CVPR2025/papers/Yang_MatAnyone_Stable_Video_Matting_with_Consistent_Memory_Propagation_CVPR_2025_paper.pdf"],
    },
    {
        "key": "matte_anything",
        "title": "Matte Anything: Interactive Natural Image Matting with Segment Anything Models",
        "arxiv_id": "2306.04121",
        "urls": [],
    },
    {
        "key": "synthlight",
        "title": "SynthLight: Portrait Relighting with Diffusion Model by Learning to Re-render Synthetic Faces",
        "arxiv_id": "2501.09756",
        "urls": ["https://openaccess.thecvf.com/content/CVPR2025/papers/Chaturvedi_SynthLight_Portrait_Relighting_with_Diffusion_Model_by_Learning_to_Re-render_CVPR_2025_paper.pdf"],
    },
    {
        "key": "text2relight",
        "title": "Text2Relight: Creative Portrait Relighting with Text Guidance",
        "arxiv_id": "2412.13734",
        "urls": [],
    },
    {
        "key": "portrait_shadow",
        "title": "Generative Portrait Shadow Removal",
        "arxiv_id": "2410.05525",
        "urls": [],
    },
    {
        "key": "compose",
        "title": "COMPOSE: Comprehensive Portrait Shadow Editing",
        "arxiv_id": "2406.12013",
        "urls": ["https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07860.pdf"],
    },
    {
        "key": "softshadow",
        "title": "SoftShadow: Leveraging Soft Masks for Penumbra-Aware Shadow Removal",
        "arxiv_id": "2409.07041",
        "urls": ["https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_SoftShadow_Leveraging_Soft_Masks_for_Penumbra-Aware_Shadow_Removal_CVPR_2025_paper.pdf"],
    },
]


def validate_pdf(path: Path) -> dict:
    data = path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ValueError("downloaded content is not a PDF")
    reader = PdfReader(str(path))
    return {
        "size": len(data),
        "page_count": len(reader.pages),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    try:
        records = json.loads(MANIFEST.read_text(encoding="utf-8"))
        return {record["key"]: record for record in records}
    except (KeyError, TypeError, ValueError):
        return {}


def save_manifest(records: dict[str, dict]) -> None:
    ordered = [records[p["key"]] for p in PAPERS if p["key"] in records]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temp = MANIFEST.with_suffix(".json.tmp")
    temp.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, MANIFEST)


def download(url: str, path: Path, timeout: int) -> str:
    partial = path.with_suffix(path.suffix + ".part")
    command = [
        "curl.exe",
        "-L",
        "--fail",
        "--retry",
        "2",
        "--retry-delay",
        "3",
        "--connect-timeout",
        "15",
        "--max-time",
        str(timeout),
        "--continue-at",
        "-",
        "--user-agent",
        "ReadPaper/1.0 academic research archive",
        "--output",
        str(partial),
        "--write-out",
        "%{url_effective}",
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise OSError(result.stderr.strip() or f"curl exited with {result.returncode}")
    os.replace(partial, path)
    return result.stdout.strip() or url


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("paper", nargs="*", help="paper key or arXiv id; default: all")
    parser.add_argument("--timeout", type=int, default=300, help="per-URL transfer timeout in seconds")
    parser.add_argument("--pause", type=float, default=2.0, help="pause between papers")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    selected = set(args.paper)
    papers = [
        paper for paper in PAPERS
        if not selected or paper["key"] in selected or paper["arxiv_id"] in selected
    ]
    if selected and not papers:
        raise SystemExit(f"no paper matched: {', '.join(sorted(selected))}")

    records = load_manifest()
    for index, paper in enumerate(papers):
        key = paper["key"]
        title = paper["title"]
        arxiv_id = paper["arxiv_id"]
        path = OUTPUT / f"{key}_{arxiv_id}.pdf"
        urls = [*paper["urls"],
            f"https://export.arxiv.org/pdf/{arxiv_id}",
            f"https://arxiv.org/pdf/{arxiv_id}",
        ]
        record = {
            "key": key,
            "title": title,
            "arxiv_id": arxiv_id,
            "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
            "local_path": str(path),
        }
        if path.exists():
            try:
                record.update(validate_pdf(path))
                record.update({"valid": True, "transport": "existing"})
                records[key] = record
                save_manifest(records)
                print(f"existing {key}: {record['page_count']} pages")
                continue
            except Exception:
                path.unlink()

        errors = []
        for url in urls:
            try:
                final_url = download(url, path, args.timeout)
                record.update(validate_pdf(path))
                record.update({"valid": True, "download_url": final_url, "transport": "downloaded"})
                print(f"downloaded {key}: {record['page_count']} pages, {record['size']} bytes")
                break
            except (OSError, ValueError) as error:
                errors.append(f"{url}: {error}")
                if path.exists():
                    path.unlink()
        else:
            record.update({"valid": False, "errors": errors})
            print(f"failed {key}: {' | '.join(errors)}")
        records[key] = record
        save_manifest(records)
        if index < len(papers) - 1:
            time.sleep(args.pause)

    valid = sum(1 for record in records.values() if record.get("valid"))
    print(f"valid={valid}/{len(PAPERS)} manifest={MANIFEST}")


if __name__ == "__main__":
    main()
