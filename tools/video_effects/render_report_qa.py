"""Render the DOCX when possible and always build source-image contact sheets."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "daily" / "20260827_录像特效调研"
REPORT = PROJECT / "report" / "手机录像特效重点玩法图文洞察_20260827.docx"
QA_DIR = PROJECT / "report" / "qa"
CONTACT_DIR = QA_DIR / "source_visual_contact_sheets"
STATUS_PATH = QA_DIR / "render_qa_status.json"
RENDER_SCRIPT = Path(
    "D:/ProgramFiles/codex/.codex/plugins/cache/openai-primary-runtime/"
    "documents/26.819.11345/skills/documents/render_docx.py"
)
PYTHON = Path(
    "C:/Users/xh932/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/python/python.exe"
)


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc") if bold else Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def build_contact_sheets(paths: list[Path], prefix: str, columns=4, rows=4) -> list[str]:
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    page_size = columns * rows
    outputs = []
    for page_index in range(0, len(paths), page_size):
        batch = paths[page_index:page_index + page_size]
        width, height = 2000, 1420
        margin, gap = 40, 24
        cell_w = (width - margin * 2 - gap * (columns - 1)) // columns
        cell_h = (height - margin * 2 - gap * (rows - 1)) // rows
        sheet = Image.new("RGB", (width, height), (238, 242, 246))
        draw = ImageDraw.Draw(sheet)
        for local_index, image_path in enumerate(batch):
            row, column = divmod(local_index, columns)
            x0 = margin + column * (cell_w + gap)
            y0 = margin + row * (cell_h + gap)
            draw.rounded_rectangle(
                (x0, y0, x0 + cell_w, y0 + cell_h),
                radius=12,
                fill=(255, 255, 255),
                outline=(190, 202, 213),
                width=2,
            )
            with Image.open(image_path) as source:
                image = source.convert("RGB")
                image.thumbnail((cell_w - 20, cell_h - 52))
                px = x0 + (cell_w - image.width) // 2
                py = y0 + 10
                sheet.paste(image, (px, py))
            label = f"{page_index + local_index + 1:02d} {image_path.stem[:42]}"
            draw.text((x0 + 10, y0 + cell_h - 34), label, font=font(16), fill=(42, 55, 70))
        target = CONTACT_DIR / f"{prefix}_{page_index // page_size + 1:02d}.png"
        sheet.save(target, quality=92)
        outputs.append(target.resolve().relative_to(ROOT.resolve()).as_posix())
    return outputs


def find_office_renderer() -> str | None:
    for command in ("soffice", "libreoffice"):
        executable = shutil.which(command)
        if executable:
            return executable
    for path in (
        Path("C:/Program Files/LibreOffice/program/soffice.exe"),
        Path("C:/Program Files (x86)/LibreOffice/program/soffice.exe"),
    ):
        if path.exists():
            return str(path)
    return None


def build() -> dict:
    storyboard_paths = sorted((PROJECT / "figures" / "effect_storyboards").glob("*.png"))
    reference_paths = sorted((PROJECT / "figures" / "real_references").glob("*.png"))
    contact_sheets = [
        *build_contact_sheets(storyboard_paths, "storyboards"),
        *build_contact_sheets(reference_paths, "references"),
    ]

    renderer = find_office_renderer()
    rendered_pages = []
    status = "not_run_renderer_unavailable"
    reason = "LibreOffice/soffice is not installed or on PATH. Microsoft Word is also unavailable on this host."
    if renderer and RENDER_SCRIPT.exists() and PYTHON.exists():
        output_dir = QA_DIR / "rendered_pages"
        command = [
            str(PYTHON),
            str(RENDER_SCRIPT),
            str(REPORT),
            "--output_dir",
            str(output_dir),
            "--width",
            "1600",
            "--height",
            "2100",
            "--emit_pdf",
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode == 0:
            status = "rendered"
            reason = ""
            rendered_pages = [
                path.resolve().relative_to(ROOT.resolve()).as_posix()
                for path in sorted(output_dir.glob("page-*.png"))
            ]
        else:
            status = "render_failed"
            reason = (completed.stderr or completed.stdout).strip()

    result = {
        "docx": REPORT.resolve().relative_to(ROOT.resolve()).as_posix(),
        "status": status,
        "reason": reason,
        "storyboard_sources": len(storyboard_paths),
        "reference_card_sources": len(reference_paths),
        "contact_sheets": contact_sheets,
        "rendered_pages": rendered_pages,
    }
    QA_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
