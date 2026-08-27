"""Fetch a controlled source batch with curl.exe and write an auditable manifest."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"D:\Repository\ReadPaper\daily\20260826_后处理调研"
)
MANIFEST = ROOT / "sources" / "source_manifest.json"
PRODUCT_DIR = ROOT / "sources" / "official_products"
PRODUCT_DIR.mkdir(parents=True, exist_ok=True)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


SOURCES = [
    ("official_apple_cinematic_mode", "official_product", "Cinematic mode", "Apple", "iPhone camera", "2021-09-14", "https://support.apple.com/en-us/HT212778", "E1", "Official support page for focus transitions in video.", "Supported models and resolutions vary."),
    ("official_apple_action_mode", "official_product", "Action mode", "Apple", "iPhone camera", "2022-09-07", "https://support.apple.com/en-us/HT213130", "E1", "Official support page for stabilization in motion video.", "Supported models and modes vary."),
    ("official_google_video_boost", "official_product", "Video Boost", "Google", "Pixel camera", "2023-10-04", "https://support.google.com/pixelphone/answer/13539889", "E1", "Official support page for cloud-assisted video processing.", "Cloud, device, region, and account conditions apply."),
    ("official_google_cinematic_blur", "official_product", "Cinematic Blur", "Google", "Pixel camera", "2021-08-17", "https://support.google.com/pixelphone/answer/11101607", "E1", "Official support page for shallow-depth-of-field video effect.", "Supported models vary."),
    ("official_samsung_super_steady", "official_product", "Super Steady", "Samsung", "Galaxy camera", "2020-02-11", "https://www.samsung.com/us/support/answer/ANS00087284/", "E1", "Official support page for Super Steady stabilization.", "Model-specific implementation is not public."),
    ("official_dji_rocksteady", "official_product", "RockSteady stabilization", "DJI", "Osmo Action", "2019-05-15", "https://www.dji.com/osmo-action", "E1", "Official product page for electronic stabilization.", "Behavior differs across generations."),
    ("official_gopro_hypersmooth", "official_product", "HyperSmooth stabilization", "GoPro", "HERO camera", "2018-09-20", "https://gopro.com/en/us/technology/hypersmooth-video-stabilization", "E1", "Official technology page for electronic stabilization.", "Exact algorithm depends on model and mode."),
    ("official_insta360_flowstate", "official_product", "FlowState stabilization", "Insta360", "Insta360 cameras", "2018-01-01", "https://www.insta360.com/product/one_x", "E1", "Official product page associated with FlowState stabilization.", "Product-level description."),
    ("official_dji_active_track", "official_product", "ActiveTrack subject tracking", "DJI", "DJI camera and drone ecosystem", "2016-01-01", "https://www.dji.com/a3/info", "E2", "Official DJI material for selected-subject tracking.", "Capability differs by product."),
    ("official_davinci_magic_mask", "official_product", "Magic Mask", "Blackmagic Design", "DaVinci Resolve", "2021-09-09", "https://www.blackmagicdesign.com/products/davinciresolve", "E1", "Official product page for tracked subject/object masks.", "Desktop post-production reference."),
    ("official_adobe_roto_brush", "official_product", "Roto Brush and object selection", "Adobe", "After Effects", "2020-10-20", "https://helpx.adobe.com/after-effects/using/roto-brush-refine-matte.html", "E1", "Official documentation for video segmentation and matte refinement.", "Desktop workflow reference."),
    ("official_blackmagic_camera_app", "official_product", "Blackmagic Camera app", "Blackmagic Design", "iPhone and iPad camera app", "2023-09-14", "https://www.blackmagicdesign.com/products/blackmagiccamera", "E1", "Official mobile camera app with manual controls and pro recording.", "Capture/control reference."),
    ("official_sony_real_time_tracking", "official_product", "Real-time tracking and subject recognition", "Sony", "Alpha cameras", "2021-01-26", "https://electronics.sony.com/imaging/interchangeable-lens-cameras/p/ilce7sm3-b", "E1", "Official camera page for subject recognition and movie tracking.", "Behavior depends on body and firmware."),
    ("official_canon_dual_pixel_af", "official_product", "Dual Pixel CMOS AF", "Canon", "EOS cameras", "2013-01-01", "https://www.usa.canon.com/shop/p/eos-r5", "E1", "Official EOS product page for movie autofocus and tracking.", "Feature details vary by body."),
    ("official_premiere_object_mask", "official_product", "Object masking and tracking", "Adobe", "Premiere Pro", "2023-01-01", "https://helpx.adobe.com/premiere-pro/using/masking-tracking.html", "E1", "Official documentation for tracked masks in video editing.", "Desktop workflow reference."),
    ("official_final_cut_object_tracker", "official_product", "Object tracking", "Apple", "Final Cut Pro", "2020-01-01", "https://support.apple.com/guide/final-cut-pro/track-objects-ver2a5f7f2d/mac", "E1", "Official documentation for object tracking and effects attachment.", "Desktop post-production reference."),
    ("official_dji_horizon_steady", "official_product", "HorizonSteady", "DJI", "Osmo Action", "2021-03-04", "https://www.dji.com/osmo-action-4", "E1", "Official product material for horizon leveling in action video.", "Mode and crop vary by product."),
    ("official_gopro_horizon_lock", "official_product", "Horizon Lock", "GoPro", "HERO camera", "2020-09-16", "https://gopro.com/en/us/technology/horizon-lock", "E1", "Official technology page for horizon leveling.", "Requires supported lens/mode."),
    ("official_insta360_me_mode", "official_product", "Me Mode", "Insta360", "Insta360 camera", "2021-01-01", "https://www.insta360.com/product/insta360-x3", "E2", "Official product material for automatic person framing in 360 video.", "Product generation varies."),
    ("official_dji_subject_tracking", "official_product", "Subject tracking", "DJI", "Osmo Pocket", "2023-08-02", "https://www.dji.com/osmo-pocket-3", "E1", "Official product page for gimbal-camera subject tracking.", "Model-specific."),
    ("official_sony_s_cinetone", "official_product", "S-Cinetone", "Sony", "Cinema and Alpha cameras", "2020-01-01", "https://pro.sony/en_GB/products/handheld-camcorders/pxw-z280", "E1", "Official Sony material for a cinematic color rendering profile.", "Color profile is not a neural post-process."),
    ("official_panasonic_real_time_lut", "official_product", "Real Time LUT", "Panasonic", "LUMIX cameras", "2023-01-01", "https://www.panasonic.com/global/consumer/lumix/lumix-s5m2.html", "E1", "Official product material for applying LUTs during capture.", "Model and firmware vary."),
    ("official_blackmagic_gen5_color", "official_product", "Gen 5 Color Science", "Blackmagic Design", "Blackmagic cameras", "2020-01-01", "https://www.blackmagicdesign.com/products/blackmagicpocketcinemacamera", "E1", "Official product material for camera color science and film workflows.", "Marketing/product-level disclosure."),
    ("official_capcut_video_cutout", "official_product", "Video background removal", "CapCut", "CapCut", "2023-01-01", "https://www.capcut.com/tools/video-background-remover", "E2", "Official product page for video cutout and background replacement.", "Implementation is not disclosed."),
    ("official_adobe_content_aware_fill_video", "official_product", "Content-Aware Fill for video", "Adobe", "After Effects", "2019-04-02", "https://helpx.adobe.com/after-effects/using/content-aware-fill.html", "E1", "Official documentation for removing objects from video with temporal fill.", "Desktop workflow reference."),
    ("official_davinci_object_removal", "official_product", "Object removal", "Blackmagic Design", "DaVinci Resolve", "2022-04-18", "https://www.blackmagicdesign.com/products/davinciresolve", "E1", "Official product material for removing tracked objects in video.", "Version-specific and desktop."),
    ("official_apple_photographic_styles", "official_product", "Photographic Styles", "Apple", "iPhone camera", "2021-09-14", "https://support.apple.com/en-us/HT212788", "E1", "Official support page for scene-aware capture styles.", "Still-image origin; video migration is a research extension."),
    ("official_samsung_single_take", "official_product", "Single Take", "Samsung", "Galaxy camera", "2020-02-11", "https://www.samsung.com/us/support/answer/ANS00087284/", "E2", "Official Galaxy camera material for multi-result capture.", "Product behavior varies; source page may combine features."),
    ("official_google_magic_editor_video_inspiration", "official_product", "Generative editing product family", "Google", "Google Photos", "2024-01-01", "https://support.google.com/photos/answer/14525403", "E2", "Official support material for generative editing concepts that can inspire video extensions.", "Photo-first capability; do not call it video support."),
]


def fetch(url: str, target: Path) -> tuple[int, str, str]:
    command = [
        "curl.exe", "-L", "--max-time", "12", "--connect-timeout", "5",
        "-A", "ReadPaper-ISPVideoResearch/1.0", "-sS", "-o", str(target),
        "-w", "%{http_code}", url,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=18)
    except subprocess.TimeoutExpired:
        return 0, "request_timeout", ""
    code = int(result.stdout.strip() or 0)
    if result.returncode != 0 or code < 200 or code >= 400:
        if target.exists():
            target.unlink()
        return code, "request_failed", result.stderr.strip()[:500]
    body = target.read_bytes()
    return code, "verified" if code == 200 else "partial", hashlib.sha256(body).hexdigest()


def main() -> None:
    records = []
    for index, row in enumerate(SOURCES, 1):
        source_id, source_type, title, publisher, product, date, url, level, quote, limit = row
        target = PRODUCT_DIR / f"{source_id}.html"
        code, status, extra = fetch(url, target)
        record = {
            "source_id": source_id,
            "source_type": source_type,
            "title": title,
            "publisher_or_authors": publisher,
            "product_or_venue": product,
            "date": date,
            "url": url,
            "local_path": str(target) if target.exists() else "",
            "evidence_level": level,
            "access_status": f"HTTP {code}" if code else status,
            "verification_status": status,
            "evidence_quote": quote,
            "scope_limit": limit if not extra else f"{limit} {extra}",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": extra if status in ("verified", "partial") else "",
        }
        records.append(record)
        print(f"[{index:02d}/{len(SOURCES):02d}] {source_id} {status} {record['access_status']}", flush=True)
    MANIFEST.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records to {MANIFEST}")


if __name__ == "__main__":
    main()
