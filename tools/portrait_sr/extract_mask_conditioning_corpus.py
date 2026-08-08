import json
import re
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "daily" / "PortraitSR"
PDF_DIR = ROOT / "papers" / "07_mask_conditioning"
TEXT_DIR = ROOT / "text"
MANIFEST = ROOT / "metadata" / "mask_conditioning_download_manifest.json"
OUTPUT = ROOT / "metadata" / "mask_conditioning_corpus_index.json"

FIGURE_RE = re.compile(r"(?im)^\s*(fig(?:ure)?\.?\s*\d+[a-z]?\s*[:.]?\s*.+)$")
TABLE_RE = re.compile(r"(?im)^\s*(table\s+\d+[a-z]?\s*[:.]?\s*.+)$")
KEYWORDS = {
    "mask_representation": ["mask", "matte", "alpha", "trimap", "parsing", "segmentation", "shadow map"],
    "conditioning": ["concatenate", "condition", "cross-attention", "self-attention", "controlnet", "reference unet"],
    "loss": ["loss", "objective", "l1", "l2", "lpips", "perceptual", "adversarial", "identity"],
    "data": ["dataset", "training data", "data synthesis", "synthetic", "light stage", "lightstage"],
    "limitations": ["limitation", "failure case", "failure cases", "fails", "challenging case"],
}


def clean_text(value: str) -> str:
    value = value.replace("\x00", "")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n{4,}", "\n\n\n", value)
    return value.encode("utf-8", errors="replace").decode("utf-8").strip()


def compact(match: re.Match) -> str:
    return re.sub(r"\s+", " ", match.group(1)).strip()[:800]


def main() -> None:
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        record["key"]: record
        for record in json.loads(MANIFEST.read_text(encoding="utf-8"))
        if record.get("valid")
    }
    records = []
    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        key = pdf_path.stem.rsplit("_", 1)[0]
        reader = PdfReader(str(pdf_path))
        pages = []
        figures = []
        tables = []
        keyword_pages = {name: [] for name in KEYWORDS}
        for page_number, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")
            pages.append(text)
            figures.extend({"page": page_number, "caption": compact(match)} for match in FIGURE_RE.finditer(text))
            tables.extend({"page": page_number, "caption": compact(match)} for match in TABLE_RE.finditer(text))
            lowered = text.lower()
            for name, terms in KEYWORDS.items():
                if any(term in lowered for term in terms):
                    keyword_pages[name].append(page_number)

        text_path = TEXT_DIR / f"mask_{key}.txt"
        text_path.write_text(
            "\n\n".join(f"=== PAGE {number} ===\n{text}" for number, text in enumerate(pages, start=1)),
            encoding="utf-8",
        )
        source = manifest.get(key, {})
        records.append(
            {
                "key": key,
                "title": source.get("title"),
                "arxiv_id": source.get("arxiv_id"),
                "file": pdf_path.relative_to(ROOT).as_posix(),
                "page_count": len(pages),
                "sha256": source.get("sha256"),
                "source_url": source.get("download_url") or source.get("abs_url"),
                "first_page_excerpt": pages[0][:8000] if pages else "",
                "figure_candidates": figures,
                "table_candidates": tables,
                "keyword_pages": keyword_pages,
                "text_path": text_path.relative_to(ROOT).as_posix(),
            }
        )
        print(f"extracted {key}: {len(pages)} pages", flush=True)

    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"records={len(records)} output={OUTPUT}")


if __name__ == "__main__":
    main()
