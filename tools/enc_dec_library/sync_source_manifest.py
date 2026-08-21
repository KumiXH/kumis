import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.enc_dec_library.config import OFFICIAL_FILES, PAPERS, ROOT


def load_json(path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def source_status(record, source_type):
    if record and record.get("valid"):
        return "paper-downloaded" if source_type == "paper" else "code-verified"
    return "indexed-not-downloaded" if source_type == "paper" else "code-missing"


def main():
    metadata = ROOT / "metadata"
    paper_records = {row.get("key", ""): row for row in load_json(metadata / "download_manifest.json")}
    code_records = {
        f"{row.get('group', '')}/{row.get('name', '')}": row
        for row in load_json(metadata / "code_manifest.json")
    }

    records = []
    for paper in PAPERS:
        downloaded = paper_records.get(paper["key"], {})
        records.append({
            **paper,
            "evidence_status": source_status(downloaded, "paper"),
            "local_path": downloaded.get("local_path", ""),
            "valid": bool(downloaded.get("valid")),
            "page_count": downloaded.get("page_count", ""),
            "sha256": downloaded.get("sha256", ""),
            "retrieved_at": downloaded.get("retrieved_at", ""),
            "repository_commit": "",
        })

    for source in OFFICIAL_FILES:
        identity = f"{source['group']}/{source['name']}"
        downloaded = code_records.get(identity, {})
        records.append({
            "key": f"code_{source['group']}_{Path(source['name']).stem}",
            "title": source["purpose"],
            "arxiv_id": "",
            "category": "source_code",
            "year": "",
            "venue": "official repository",
            "role": source["purpose"],
            "priority": "core",
            "source_type": "official_code",
            "source_url": source["url"],
            "pdf_url": "",
            "evidence_status": source_status(downloaded, "official_code"),
            "local_path": downloaded.get("local_path", ""),
            "valid": bool(downloaded.get("valid")),
            "page_count": "",
            "sha256": downloaded.get("sha256", ""),
            "retrieved_at": downloaded.get("retrieved_at", ""),
            "repository_commit": downloaded.get("repository_commit", ""),
        })

    json_path = metadata / "source_manifest.json"
    csv_path = metadata / "source_manifest.csv"
    json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print(f"sources={len(records)}")
    print(f"papers_local={sum(row['source_type'] == 'paper' and row['valid'] for row in records)}")
    print(f"code_local={sum(row['source_type'] == 'official_code' and row['valid'] for row in records)}")


if __name__ == "__main__":
    main()
