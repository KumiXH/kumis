import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

from tools.enc_dec_library.config import ROOT


PDF = ROOT / "report" / "DiT编解码器发展架构训练与数据工程深度洞察_QA.pdf"
OUT = ROOT / "rendered_report"
PDFTOPPM = Path(
    r"C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe"
)


def page_number(path):
    return int(path.stem.split("-")[-1])


def main():
    if OUT.exists():
        for page in OUT.glob("page-*.png"):
            page.unlink()
        for contact in OUT.glob("contact-*.png"):
            contact.unlink()
    OUT.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [str(PDFTOPPM), "-r", "110", "-png", str(PDF), str(OUT / "page")],
        check=True,
        timeout=900,
    )
    pages = sorted(OUT.glob("page-*.png"), key=page_number)
    records = []
    for page in pages:
        with Image.open(page) as image:
            gray = image.convert("L")
            stat = ImageStat.Stat(gray)
            pixels = gray.resize((120, 156))
            dark = sum(1 for value in pixels.getdata() if value < 245)
            ink_ratio = dark / (120 * 156)
            records.append(
                {
                    "page": page_number(page),
                    "path": str(page),
                    "width": image.width,
                    "height": image.height,
                    "mean_luma": round(stat.mean[0], 3),
                    "std_luma": round(stat.stddev[0], 3),
                    "ink_ratio": round(ink_ratio, 5),
                    "possible_blank": ink_ratio < 0.012,
                }
            )

    thumb_w, thumb_h = 306, 396
    cols, per_sheet = 4, 16
    contacts = []
    for contact_index in range(math.ceil(len(pages) / per_sheet)):
        subset = pages[contact_index * per_sheet : (contact_index + 1) * per_sheet]
        rows = math.ceil(len(subset) / cols)
        sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 26)), "#D8DDE3")
        draw = ImageDraw.Draw(sheet)
        for index, page in enumerate(subset):
            with Image.open(page) as source:
                image = source.convert("RGB")
                image.thumbnail((thumb_w - 12, thumb_h - 12))
            x = (index % cols) * thumb_w + (thumb_w - image.width) // 2
            y = (index // cols) * (thumb_h + 26) + 6
            sheet.paste(image, (x, y))
            draw.text((x, y + image.height + 3), f"Page {contact_index * per_sheet + index + 1}", fill="#111827")
        destination = OUT / f"contact-{contact_index + 1}.png"
        sheet.save(destination, optimize=True)
        contacts.append(str(destination))

    qa = {
        "pdf": str(PDF),
        "page_count": len(pages),
        "pages": records,
        "possible_blank_pages": [row["page"] for row in records if row["possible_blank"]],
        "dimension_variants": sorted({f"{row['width']}x{row['height']}" for row in records}),
        "contacts": contacts,
    }
    (ROOT / "metadata" / "qa_report.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"pages": len(pages), "contacts": len(contacts), "possible_blank_pages": qa["possible_blank_pages"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
