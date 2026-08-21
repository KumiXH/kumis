import json
import re
import sys
from html import unescape
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.enc_dec_library.config import ROOT


TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"(?is)<(script|style).*?>.*?</\1>")
SPACE_RE = re.compile(r"[ \t]+")
BLANK_RE = re.compile(r"\n{3,}")
FIG_RE = re.compile(r'(?is)<figure[^>]*>(.*?)</figure>')
IMG_RE = re.compile(r'(?is)<img[^>]+src="([^"]+)"')
CAPTION_RE = re.compile(r'(?is)<figcaption[^>]*>(.*?)</figcaption>')


def plain_text(html):
    html = SCRIPT_RE.sub("", html)
    html = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</section>|</li>|</h[1-6]>", "\n", html)
    text = unescape(TAG_RE.sub(" ", html))
    text = "\n".join(SPACE_RE.sub(" ", line).strip() for line in text.splitlines())
    return BLANK_RE.sub("\n\n", text).strip()


def main():
    records = []
    for source in sorted((ROOT / "metadata" / "raw").glob("ar5iv_*.html")):
        html = source.read_text(encoding="utf-8", errors="replace")
        identifier = source.stem.replace("ar5iv_", "")
        converted = len(html) > 20000 and "Conversion failed" not in html
        text = plain_text(html) if converted else ""
        text_path = ROOT / "text" / f"ar5iv_{identifier}.txt"
        text_path.write_text(text, encoding="utf-8")
        figures = []
        if converted:
            for block in FIG_RE.findall(html):
                image = IMG_RE.search(block)
                caption = CAPTION_RE.search(block)
                if image:
                    figures.append({
                        "src": unescape(image.group(1)),
                        "caption": plain_text(caption.group(1))[:1000] if caption else "",
                    })
        records.append({
            "arxiv_id": identifier,
            "html_path": str(source),
            "text_path": str(text_path),
            "html_bytes": source.stat().st_size,
            "converted": converted,
            "text_chars": len(text),
            "figures": figures,
        })
        print(f"{identifier}: converted={converted} text={len(text)} figures={len(figures)}")
    (ROOT / "metadata" / "html_corpus_index.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
