import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.enc_dec_library.config import (
    CATEGORIES,
    OFFICIAL_FILES,
    PAPERS,
    PREFERRED_PDF_URLS,
    ROOT,
    ensure_directories,
)


USER_AGENT = "ReadPaper-EncoderDecoder-Study/1.0 (academic research)"

LOCAL_REUSE = {
    "dit": REPO_ROOT / "daily" / "20260804_DIT" / "source" / "Scalable_Diffusion_Models_with_Transformers_DiT.pdf",
    "sd3": REPO_ROOT / "daily" / "Flux" / "papers" / "01_foundations" / "sd3_mmdit_2403.03206.pdf",
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_pdf(path):
    path = Path(path)
    if not path.exists():
        return {"valid": False, "reason": "missing"}
    if path.read_bytes()[:5] != b"%PDF-":
        return {"valid": False, "reason": "invalid_magic", "size": path.stat().st_size}
    try:
        pages = len(PdfReader(str(path)).pages)
    except Exception as exc:
        return {"valid": False, "reason": f"parse_error:{exc}", "size": path.stat().st_size}
    return {
        "valid": pages > 0,
        "reason": "ok" if pages > 0 else "zero_pages",
        "size": path.stat().st_size,
        "page_count": pages,
        "sha256": sha256(path),
    }


def download(url, destination, is_pdf=False):
    destination.parent.mkdir(parents=True, exist_ok=True)
    incoming = destination.with_suffix(destination.suffix + ".part")
    errors = []
    for transport in ("curl", "urllib"):
        try:
            if incoming.exists():
                incoming.unlink()
            if transport == "curl":
                subprocess.run(
                    [
                        r"C:\Windows\System32\curl.exe",
                        "-L",
                        "--fail",
                        "--silent",
                        "--show-error",
                        "--connect-timeout",
                        "15",
                        "--max-time",
                        "90",
                        "--retry",
                        "2",
                        "--retry-delay",
                        "2",
                        "-A",
                        USER_AGENT,
                        "-o",
                        str(incoming),
                        url,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=110,
                )
            else:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=45) as response, incoming.open("wb") as output:
                    shutil.copyfileobj(response, output)
            if is_pdf:
                result = validate_pdf(incoming)
                if not result["valid"]:
                    raise ValueError(result["reason"])
            incoming.replace(destination)
            return {"ok": True, "http_status": 200, "transport": transport}
        except Exception as exc:
            errors.append(f"{transport}:{exc}")
            if incoming.exists():
                incoming.unlink()
    return {"ok": False, "error": " | ".join(errors)}


def pdf_name(paper):
    return f"{paper['key']}_{paper['arxiv_id']}.pdf"


def download_papers(keys=None, preferred_only=False):
    records = []
    selected = [paper for paper in PAPERS if not keys or paper["key"] in keys]
    if preferred_only:
        selected = [
            paper for paper in selected
            if paper["key"] in PREFERRED_PDF_URLS or paper["key"] in LOCAL_REUSE
        ]
    for index, paper in enumerate(selected, start=1):
        destination = CATEGORIES[paper["category"]] / pdf_name(paper)
        reused = False
        local = LOCAL_REUSE.get(paper["key"])
        if local and local.exists() and not destination.exists():
            shutil.copy2(local, destination)
            reused = True
        validation = validate_pdf(destination)
        transport = "local-reuse" if validation["valid"] and reused else "existing"
        if not validation["valid"]:
            print(f"[{index}/{len(selected)}] download {paper['key']}", flush=True)
            selected_url = PREFERRED_PDF_URLS.get(paper["key"], paper["pdf_url"])
            result = download(selected_url, destination, is_pdf=True)
            validation = validate_pdf(destination)
            transport = f"official-{result.get('transport', '')}" if result["ok"] else f"failed:{result.get('error', '')}"
        else:
            print(f"[{index}/{len(selected)}] verified {paper['key']}", flush=True)
        records.append({
            **paper,
            "selected_pdf_url": PREFERRED_PDF_URLS.get(paper["key"], paper["pdf_url"]),
            "local_path": str(destination),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "transport": transport,
            **validation,
        })
        time.sleep(0.8)
    return records


def github_commit_sha(group):
    repos = {
        "flux": "black-forest-labs/flux",
        "sd3": "Stability-AI/sd3-ref",
        "ldm": "CompVis/latent-diffusion",
        "dit": "facebookresearch/DiT",
        "flashvsr": "OpenImagingLab/FlashVSR",
        "wan": "Wan-Video/Wan2.1",
        "cogvideox": "THUDM/CogVideo",
        "hunyuanvideo": "Tencent-Hunyuan/HunyuanVideo",
    }
    repo = repos.get(group)
    if not repo:
        return ""
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/commits/HEAD", headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response).get("sha", "")
    except Exception:
        return ""


def download_code():
    shas = {group: github_commit_sha(group) for group in sorted({row["group"] for row in OFFICIAL_FILES})}
    records = []
    for item in OFFICIAL_FILES:
        destination = ROOT / "source_code" / item["group"] / item["name"]
        result = download(item["url"], destination)
        records.append({
            **item,
            "local_path": str(destination),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "repository_commit": shas.get(item["group"], ""),
            "valid": result["ok"] and destination.exists() and destination.stat().st_size > 0,
            "size": destination.stat().st_size if destination.exists() else 0,
            "sha256": sha256(destination) if destination.exists() else "",
            "error": result.get("error", ""),
        })
        print(f"code {item['group']}/{item['name']}: {records[-1]['valid']}")
    return records


def load_records(path):
    path = Path(path)
    if not path.exists():
        return []
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return records if isinstance(records, list) else []


def merge_records(existing, updates, configured, identity):
    merged = {identity(row): row for row in existing if identity(row)}
    merged.update({identity(row): row for row in updates if identity(row)})
    ordered = []
    for item in configured:
        key = identity(item)
        record = merged.get(key)
        if record is None:
            record = {
                **item,
                "valid": False,
                "reason": "not_downloaded",
                "retrieved_at": "",
            }
        ordered.append(record)
    return ordered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preferred-only", action="store_true")
    parser.add_argument("--keys", default="", help="Comma-separated paper keys")
    parser.add_argument("--skip-code", action="store_true")
    args = parser.parse_args()
    ensure_directories()
    keys = {key.strip() for key in args.keys.split(",") if key.strip()} or None
    paper_records = download_papers(keys=keys, preferred_only=args.preferred_only)
    code_records = [] if args.skip_code else download_code()
    metadata = ROOT / "metadata"
    paper_manifest = metadata / "download_manifest.json"
    code_manifest = metadata / "code_manifest.json"
    paper_records = merge_records(
        load_records(paper_manifest),
        paper_records,
        PAPERS,
        lambda row: row.get("key", ""),
    )
    if args.skip_code:
        code_records = load_records(code_manifest)
    else:
        code_records = merge_records(
            load_records(code_manifest),
            code_records,
            OFFICIAL_FILES,
            lambda row: f"{row.get('group', '')}/{row.get('name', '')}",
        )
    paper_manifest.write_text(
        json.dumps(paper_records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    code_manifest.write_text(
        json.dumps(code_records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"papers_valid={sum(row['valid'] for row in paper_records)}/{len(paper_records)}")
    print(f"code_valid={sum(row['valid'] for row in code_records)}/{len(code_records)}")


if __name__ == "__main__":
    main()
