import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.enc_dec_library.config import ROOT


FIGURE_RE = re.compile(r"(?im)^\s*(fig(?:ure)?\.?\s*\d+[a-z]?\s*[:.]?\s*.+)$")
TABLE_RE = re.compile(r"(?im)^\s*(table\s+\d+[a-z]?\s*[:.]?\s*.+)$")
KEYWORDS = {
    "architecture": ["architecture", "autoencoder", "encoder", "decoder", "tokenizer"],
    "compression": ["compression ratio", "downsample", "downsampling", "latent channel", "latent dimension"],
    "training": ["training objective", "loss function", "reconstruction loss", "perceptual loss", "adversarial"],
    "dataset": ["dataset", "training data", "data processing", "crop", "frame sampling"],
    "ablation": ["ablation"],
    "limitations": ["limitation", "failure case", "failure cases"],
}


def clean(text):
    text = (text or "").replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{4,}", "\n\n\n", text).strip()


def extract(pdf):
    reader = PdfReader(str(pdf))
    pages = []
    figures = []
    tables = []
    keyword_pages = {key: [] for key in KEYWORDS}
    for number, page in enumerate(reader.pages, start=1):
        text = clean(page.extract_text())
        pages.append(text)
        for match in FIGURE_RE.finditer(text):
            figures.append({"page": number, "caption": re.sub(r"\s+", " ", match.group(1))[:700]})
        for match in TABLE_RE.finditer(text):
            tables.append({"page": number, "caption": re.sub(r"\s+", " ", match.group(1))[:700]})
        lowered = text.lower()
        for key, terms in KEYWORDS.items():
            if any(term in lowered for term in terms):
                keyword_pages[key].append(number)
    return pages, figures, tables, keyword_pages


def main():
    output = ROOT / "text"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for pdf in sorted((ROOT / "papers").rglob("*.pdf")):
        key = pdf.stem.rsplit("_", 1)[0]
        pages, figures, tables, keyword_pages = extract(pdf)
        text_path = output / f"{key}.txt"
        evidence_path = output / f"{key}.evidence.json"
        text_path.write_text(
            "\n\n".join(f"=== PAGE {i} ===\n{text}" for i, text in enumerate(pages, start=1)),
            encoding="utf-8",
        )
        evidence = {
            "key": key,
            "pdf": str(pdf),
            "page_count": len(pages),
            "text_path": str(text_path),
            "first_page_excerpt": pages[0][:5000] if pages else "",
            "figure_candidates": figures,
            "table_candidates": tables,
            "keyword_pages": keyword_pages,
        }
        evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        records.append(evidence)
        print(f"{key}: pages={len(pages)} figures={len(figures)} tables={len(tables)}")
    (ROOT / "metadata" / "corpus_index.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"extracted={len(records)}")


if __name__ == "__main__":
    main()
