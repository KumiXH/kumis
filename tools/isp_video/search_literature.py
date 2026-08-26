"""Low-concurrency OpenAlex literature collector for mobile video post-processing."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"D:\Repository\ReadPaper\daily\20260826_后处理调研"
)
RAW_DIR = ROOT / "sources" / "papers" / "openalex_raw"
PDF_DIR = ROOT / "sources" / "papers" / "open_access"
RECORDS = ROOT / "sources" / "papers" / "paper_records.jsonl"
LOG = ROOT / "metadata" / "search_log.jsonl"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

QUERIES = [
    ("video_restoration", "video restoration"),
    ("video_deblurring", "video deblurring"),
    ("video_super_resolution", "video super resolution"),
    ("video_denoising", "video denoising"),
    ("low_light_video", "low light video enhancement"),
    ("video_hdr", "high dynamic range video enhancement"),
    ("video_relighting", "video relighting"),
    ("computational_video", "computational photography video"),
    ("depth_video_effects", "depth aware video editing"),
    ("video_matting", "video matting"),
    ("video_object_removal", "video object removal"),
    ("video_stabilization", "learned video stabilization"),
    ("rolling_shutter", "rolling shutter correction video"),
    ("virtual_camera", "virtual camera video generation"),
    ("video_diffusion_editing", "video diffusion editing"),
    ("portrait_video", "portrait video enhancement"),
    ("face_restoration_video", "face restoration video identity"),
    ("edge_video", "mobile video enhancement edge inference"),
    ("learned_isp", "learned image signal processor"),
    ("raw_video_isp", "raw video image signal processing"),
    ("virtual_bokeh", "video portrait relighting bokeh"),
    ("neural_cinematography", "neural cinematography camera"),
    ("audio_visual_camera", "audio visual camera control video"),
    ("gaussian_video", "3D Gaussian splatting video editing"),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def run_curl(url: str) -> tuple[int, str]:
    cmd = [
        "curl.exe", "-L", "--max-time", "20", "--connect-timeout", "6",
        "-A", "ReadPaper-ISPVideoResearch/1.0", "-sS", "-w", "\n__STATUS__%{http_code}", url,
    ]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=28)
    except subprocess.TimeoutExpired:
        return 0, ""
    text = p.stdout
    marker = "\n__STATUS__"
    if marker not in text:
        return 0, text
    body, status = text.rsplit(marker, 1)
    try:
        return int(status.strip()), body
    except ValueError:
        return 0, body


def normalize(work: dict, query_id: str, query: str) -> dict:
    oa = work.get("open_access") or {}
    locations = work.get("locations") or []
    pdf_url = ""
    landing_url = work.get("doi") or work.get("id") or ""
    for location in [oa] + locations:
        if not isinstance(location, dict):
            continue
        pdf_url = pdf_url or ((location.get("pdf_url") or "").strip())
        landing_url = landing_url or ((location.get("landing_page_url") or "").strip())
    authors = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        if author.get("display_name"):
            authors.append(author["display_name"])
    primary = work.get("primary_location") or {}
    source = primary.get("source") or {}
    return {
        "canonical_id": work.get("id", ""),
        "openalex_id": work.get("id", ""),
        "doi": work.get("doi", "") or "",
        "title": work.get("title", "") or "",
        "publication_year": work.get("publication_year"),
        "publication_date": work.get("publication_date", "") or "",
        "type": work.get("type", ""),
        "venue": source.get("display_name", "") or "",
        "authors": authors[:20],
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "cited_by_count": work.get("cited_by_count", 0),
        "open_access": bool(oa.get("is_oa")),
        "pdf_url": pdf_url,
        "landing_url": landing_url,
        "search_query_id": query_id,
        "search_query": query,
        "retrieved_at": now(),
        "evidence_level": "E3",
        "verification_status": "metadata_verified",
    }


def reconstruct_abstract(index: dict | None) -> str:
    if not index:
        return ""
    words = []
    for word, positions in index.items():
        for position in positions:
            words.append((position, word))
    return " ".join(word for _, word in sorted(words))


def main() -> None:
    all_records: dict[str, dict] = {}
    query_log = []
    for idx, (query_id, query) in enumerate(QUERIES, 1):
        url = "https://api.openalex.org/works?search=" + quote(query) + "&filter=from_publication_date:2021-01-01,to_publication_date:2026-12-31&per-page=25&sort=cited_by_count:desc"
        status, body = run_curl(url)
        raw_path = RAW_DIR / f"{query_id}.json"
        raw_path.write_text(body, encoding="utf-8")
        query_log.append({"event": "openalex_query", "query_id": query_id, "query": query, "status": status, "raw_path": str(raw_path), "retrieved_at": now()})
        print(f"[{idx:02d}/{len(QUERIES):02d}] {query_id} HTTP {status}", flush=True)
        if status == 200:
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = {}
            for work in payload.get("results") or []:
                record = normalize(work, query_id, query)
                key = record["doi"].lower() or record["title"].strip().lower()
                if key and key not in all_records:
                    all_records[key] = record
        time.sleep(1.25)
    RECORDS.write_text("\n".join(json.dumps(v, ensure_ascii=False) for v in all_records.values()) + "\n", encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        for row in query_log:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(all_records)} deduplicated records to {RECORDS}")


if __name__ == "__main__":
    main()
