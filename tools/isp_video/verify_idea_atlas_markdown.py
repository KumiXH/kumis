"""Verify local assets and ID coverage for the visual IDEA atlas."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "daily" / "20260826_后处理调研"
REPORT = PROJECT / "report"
MAIN = REPORT / "手机录像后处理_IDEA图文图鉴_20260827.md"
PAGES = REPORT / "idea_atlas_pages"
PANELS = PROJECT / "figures" / "idea_atlas" / "panels"
CORE = PROJECT / "metadata" / "idea_universe" / "core_ideas.jsonl"


def jsonl_ids(path: Path) -> set[str]:
    return {
        json.loads(line)["idea_id"]
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    }


def resolve_local_links(markdown_path: Path) -> list[tuple[str, Path]]:
    text = markdown_path.read_text(encoding="utf-8-sig")
    links = re.findall(r"\]\((?!https?://|#)([^)]+)\)", text)
    resolved = []
    for link in links:
        link_path = Path(link.replace("/", "\\"))
        resolved.append((link, (markdown_path.parent / link_path).resolve()))
    return resolved


def verify() -> dict:
    expected_ids = jsonl_ids(CORE)
    pages = sorted(PAGES.glob("*.md"))
    panel_files = sorted(PANELS.glob("*.png"))
    assert MAIN.exists()
    assert len(pages) == 44, len(pages)
    assert len(panel_files) == 44, len(panel_files)
    page_ids: set[str] = set()
    missing_assets: list[str] = []
    pages_without_images: list[str] = []
    for page in pages:
        text = page.read_text(encoding="utf-8-sig")
        page_ids.update(re.findall(r"### ((?:LEGACY-OP|PRIOR|NATIVE)-\d+)｜", text))
        if not re.search(r"!\[[^]]+\]\(([^)]+\.png)\)", text):
            pages_without_images.append(page.name)
        for link, target in resolve_local_links(page):
            if not target.exists():
                missing_assets.append(f"{page.name}: {link}")
    for link, target in resolve_local_links(MAIN):
        if not target.exists():
            missing_assets.append(f"{MAIN.name}: {link}")
    assert page_ids == expected_ids, {
        "missing": sorted(expected_ids - page_ids)[:10],
        "extra": sorted(page_ids - expected_ids)[:10],
    }
    assert not pages_without_images, pages_without_images
    assert not missing_assets, missing_assets[:10]
    return {
        "core_ideas": len(expected_ids),
        "cluster_pages": len(pages),
        "panel_images": len(panel_files),
        "local_links_checked": sum(len(resolve_local_links(p)) for p in [MAIN, *pages]),
        "missing_assets": 0,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
