"""Build bounded evidence records and three-frame concept storyboards."""

from __future__ import annotations

import hashlib
import json
import math
import textwrap
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from tools.video_effects import schema


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "daily" / "20260827_录像特效调研"
OLD_PROJECT = ROOT / "daily" / "20260826_后处理调研"
PRIORITY_PATH = PROJECT / "metadata" / "priority_effects.jsonl"
IDEA_PATH = PROJECT / "metadata" / "effect_ideas.jsonl"
REFERENCE_PATH = PROJECT / "references" / "reference_manifest.jsonl"
STORYBOARD_DIR = PROJECT / "figures" / "effect_storyboards"
REAL_REFERENCE_DIR = PROJECT / "figures" / "real_references"
STORYBOARD_MANIFEST = STORYBOARD_DIR / "storyboard_manifest.jsonl"

FAMILY_LABELS = {
    "light_trails_optics": "光轨与可编程光学",
    "body_motion_clones": "身体运动与分身",
    "face_gaze_expression": "面部、视线与表情",
    "time_editing": "局部时间编辑",
    "spatial_portals": "空间入口与传送门",
    "virtual_light_shadow": "虚拟光影",
    "material_morph": "材质变形",
    "particles_weather": "粒子与天气",
    "world_style": "世界风格化",
    "audio_lyrics": "音频与歌词",
    "effect_cinematography": "特效摄影",
    "multi_person_interaction": "多人互动",
}

FAMILY_COLORS = {
    "light_trails_optics": (0, 194, 255),
    "body_motion_clones": (255, 89, 94),
    "face_gaze_expression": (0, 173, 132),
    "time_editing": (255, 183, 3),
    "spatial_portals": (109, 94, 252),
    "virtual_light_shadow": (255, 127, 17),
    "material_morph": (18, 168, 168),
    "particles_weather": (72, 149, 239),
    "world_style": (247, 37, 133),
    "audio_lyrics": (131, 56, 236),
    "effect_cinematography": (67, 97, 238),
    "multi_person_interaction": (239, 71, 111),
}

FONT_PATHS = (
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/msyhbd.ttc"),
    Path("C:/Windows/Fonts/simhei.ttf"),
)


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(rows: Iterable[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = list(FONT_PATHS)
    if bold:
        candidates.insert(0, Path("C:/Windows/Fonts/msyhbd.ttc"))
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def _family_effect_ids() -> dict[str, list[str]]:
    idea_map = {row["effect_id"]: row for row in read_jsonl(IDEA_PATH)}
    grouped: dict[str, list[str]] = defaultdict(list)
    for priority in read_jsonl(PRIORITY_PATH):
        grouped[idea_map[priority["effect_id"]]["family"]].append(priority["effect_id"])
    return dict(grouped)


def _all_effect_ids(grouped: dict[str, list[str]], families: Iterable[str]) -> list[str]:
    return [effect_id for family in families for effect_id in grouped[family]]


def _reference_specifications() -> list[dict]:
    """Return explicit source specs; effect IDs are resolved from families later."""

    return [
        {
            "reference_id": "REF-APPLE-CINEMATIC-MODE",
            "title": "Apple Cinematic mode",
            "source_type": "official_product",
            "product_work_paper": "iPhone Cinematic mode official support material",
            "publisher": "Apple",
            "year": 2021,
            "original_source": "https://support.apple.com/en-us/HT212778",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_apple_cinematic_mode.html",
            "families": ["face_gaze_expression", "effect_cinematography"],
            "demonstrates": "消费级手机录像已经支持主体识别、拍摄中焦点切换以及录后重新调整焦点，说明语义轨迹和可编辑录像元数据可以进入产品链路。",
            "does_not_prove": "不证明瞳孔重定向、任意特效摄影或本报告方案已经由 Apple 实现，也不公开具体神经网络和设备预算。",
            "implementation_boundary": "mobile_realtime",
        },
        {
            "reference_id": "REF-DJI-SUBJECT-TRACKING",
            "title": "DJI subject tracking",
            "source_type": "official_product",
            "product_work_paper": "Osmo Pocket subject tracking product material",
            "publisher": "DJI",
            "year": 2023,
            "original_source": "https://www.dji.com/osmo-pocket-3",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_dji_subject_tracking.html",
            "families": ["light_trails_optics", "body_motion_clones", "virtual_light_shadow", "multi_person_interaction"],
            "demonstrates": "消费级影像产品能够持续锁定人物主体，为光轨附着、分身身份维持、追光和多人交互提供基础跟踪参照。",
            "does_not_prove": "不证明这些创意特效本身、遮挡重建质量或手机端生成式合成性能。",
            "implementation_boundary": "mobile_realtime",
        },
        {
            "reference_id": "REF-FINAL-CUT-OBJECT-TRACKER",
            "title": "Final Cut Pro object tracking",
            "source_type": "official_software",
            "product_work_paper": "Final Cut Pro official object tracking documentation",
            "publisher": "Apple",
            "year": 2020,
            "original_source": "https://support.apple.com/guide/final-cut-pro/track-objects-ver2a5f7f2d/mac",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_final_cut_object_tracker.html",
            "families": ["material_morph", "particles_weather", "audio_lyrics", "virtual_light_shadow"],
            "demonstrates": "桌面后期软件已经把对象跟踪与标题、颜色校正及效果附着结合，证明对象级时序轨迹是可编辑特效的重要中间表示。",
            "does_not_prove": "这是桌面录后工作流，不证明手机取景器实时预览、功耗或边缘质量。",
            "implementation_boundary": "desktop_offline",
        },
        {
            "reference_id": "REF-CAPCUT-VIDEO-CUTOUT",
            "title": "CapCut video background removal",
            "source_type": "official_software",
            "product_work_paper": "CapCut official video cutout product page",
            "publisher": "CapCut",
            "year": 2023,
            "original_source": "https://www.capcut.com/tools/video-background-remover",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_capcut_video_cutout.html",
            "families": ["spatial_portals", "material_morph", "world_style", "effect_cinematography"],
            "demonstrates": "视频主体抠像和背景替换已进入大众创作工具，支持把人物、手掌或物体作为空间入口和转场边界。",
            "does_not_prove": "官方页面没有披露算法，也不证明复杂遮挡、透明材质或录像中实时运行。",
            "implementation_boundary": "mobile_offline",
        },
        {
            "reference_id": "REF-APPLE-PHOTOGRAPHIC-STYLES",
            "title": "Apple Photographic Styles",
            "source_type": "official_product",
            "product_work_paper": "iPhone Photographic Styles official support material",
            "publisher": "Apple",
            "year": 2021,
            "original_source": "https://support.apple.com/en-us/HT212788",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_apple_photographic_styles.html",
            "families": ["world_style", "virtual_light_shadow"],
            "demonstrates": "场景感知的影调和色彩控制可以被产品化为拍摄风格入口，为录像世界风格和虚拟光色控制提供交互参考。",
            "does_not_prove": "原始能力以静态摄影为主，不证明视频时序一致性或生成式世界改写。",
            "implementation_boundary": "mobile_realtime",
        },
        {
            "reference_id": "REF-SAMSUNG-SINGLE-TAKE",
            "title": "Samsung Single Take",
            "source_type": "official_product",
            "product_work_paper": "Galaxy Single Take official support material",
            "publisher": "Samsung",
            "year": 2020,
            "original_source": "https://www.samsung.com/us/support/answer/ANS00087284/",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_samsung_single_take.html",
            "families": ["time_editing", "multi_person_interaction"],
            "demonstrates": "一次录像可以派生多种结果，支持把原视频、事件轨迹和多个后处理版本作为同一拍摄资产管理。",
            "does_not_prove": "不证明局部时间冻结、倒放、分身或多人能量特效的具体实现。",
            "implementation_boundary": "mobile_offline",
        },
        {
            "reference_id": "REF-BLACKMAGIC-CAMERA-APP",
            "title": "Blackmagic Camera app",
            "source_type": "official_software",
            "product_work_paper": "Blackmagic Camera official mobile app material",
            "publisher": "Blackmagic Design",
            "year": 2023,
            "original_source": "https://www.blackmagicdesign.com/products/blackmagiccamera",
            "access_status": "official page cached and hash verified",
            "local_file": OLD_PROJECT / "sources" / "official_products" / "official_blackmagic_camera_app.html",
            "families": ["light_trails_optics", "audio_lyrics", "effect_cinematography"],
            "demonstrates": "专业录像控制、编码和素材管理能够下沉到手机应用，为保留原片、代理预览和录后重算提供产品参照。",
            "does_not_prove": "不证明本报告任何特效模型、交互或性能预算已经实现。",
            "implementation_boundary": "mobile_realtime",
        },
        {
            "reference_id": "REF-RVM-TEMPORAL-MATTING",
            "title": "Robust High-Resolution Video Matting with Temporal Guidance",
            "source_type": "paper_project",
            "product_work_paper": "WACV 2022 research paper",
            "publisher": "WACV",
            "year": 2022,
            "original_source": "https://doi.org/10.1109/WACV51458.2022.00319",
            "access_status": "metadata verified in local source library",
            "local_file": None,
            "families": ["body_motion_clones", "spatial_portals", "virtual_light_shadow", "particles_weather", "effect_cinematography", "multi_person_interaction"],
            "demonstrates": "时间引导的视频抠像可稳定人物边界，是分身、虚拟光、粒子遮挡、传送门和人物擦镜的基础研究证据。",
            "does_not_prove": "论文任务是视频抠像，不证明本报告的创意玩法、目标设备速度或生成式结果真实性。",
            "implementation_boundary": "research_prototype",
        },
        {
            "reference_id": "REF-MODNET-PORTRAIT-MATTING",
            "title": "MODNet: Real-Time Trimap-Free Portrait Matting via Objective Decomposition",
            "source_type": "paper_project",
            "product_work_paper": "AAAI 2022 research paper",
            "publisher": "AAAI",
            "year": 2022,
            "original_source": "https://doi.org/10.1609/AAAI.V36I1.19999",
            "access_status": "metadata verified in local source library",
            "local_file": None,
            "families": ["face_gaze_expression", "virtual_light_shadow", "material_morph"],
            "demonstrates": "无 trimap 人像抠像与目标分解可以为脸部、头发和服装特效提供轻量语义边界。",
            "does_not_prove": "单帧或人像抠像能力不等于复杂特效的时序稳定、身份保持和量产质量。",
            "implementation_boundary": "research_prototype",
        },
        {
            "reference_id": "REF-MAGVIT-VIDEO-TOKENS",
            "title": "MAGVIT: Masked Generative Video Transformer",
            "source_type": "paper_project",
            "product_work_paper": "CVPR 2023 research paper",
            "publisher": "CVPR",
            "year": 2023,
            "original_source": "https://doi.org/10.48550/arXiv.2212.05199",
            "access_status": "paper PDF verified in local library",
            "local_file": ROOT / "daily" / "20260821_ENC_DEC" / "papers" / "03_video_vae" / "magvit_2212.05199.pdf",
            "families": ["time_editing", "spatial_portals", "material_morph", "particles_weather", "world_style"],
            "demonstrates": "时空 tokenizer 和掩码建模能够统一帧预测、插值、补全和外扩等视频生成任务，为局部时间和空间改写提供理论参照。",
            "does_not_prove": "论文不是手机录像产品，也不保证身份、几何和事实在任意生成式特效中保持不变。",
            "implementation_boundary": "research_prototype",
        },
        {
            "reference_id": "REF-SVFR-FACE-CONSISTENCY",
            "title": "SVFR: A Unified Framework for Generalized Video Face Restoration",
            "source_type": "paper_project",
            "product_work_paper": "2025 video face restoration research paper",
            "publisher": "arXiv",
            "year": 2025,
            "original_source": "https://doi.org/10.48550/arXiv.2501.01235",
            "access_status": "paper PDF verified in local library",
            "local_file": ROOT / "daily" / "PortraitSR" / "papers" / "04_video_face" / "svfr_2501.01235.pdf",
            "families": ["face_gaze_expression", "world_style"],
            "demonstrates": "视频人脸恢复研究明确处理脸部结构、身份和时间一致性问题，可作为视线、眼神光和人脸风格效果的质量约束参照。",
            "does_not_prove": "人脸恢复不等于视线矫正；论文不证明瞳孔编辑的伦理可接受性或手机端实时性能。",
            "implementation_boundary": "research_prototype",
        },
        {
            "reference_id": "REF-AUTHFACE-IDENTITY",
            "title": "AuthFace",
            "source_type": "paper_project",
            "product_work_paper": "2024 identity-preserving face restoration paper",
            "publisher": "arXiv",
            "year": 2024,
            "original_source": "https://doi.org/10.48550/arXiv.2410.09864",
            "access_status": "paper PDF verified in local library",
            "local_file": ROOT / "daily" / "PortraitSR" / "papers" / "01_single_face" / "authface_2410.09864.pdf",
            "families": ["face_gaze_expression", "body_motion_clones"],
            "demonstrates": "身份表征与身份保持损失可以约束人脸细节恢复，为视线编辑和人像分身避免换脸提供方法参考。",
            "does_not_prove": "身份相似度指标不能证明表情、凝视方向、真实性或用户主观接受度完全保持。",
            "implementation_boundary": "research_prototype",
        },
        {
            "reference_id": "REF-DIT-GENERATIVE-BACKBONE",
            "title": "Scalable Diffusion Models with Transformers",
            "source_type": "paper_project",
            "product_work_paper": "ICCV 2023 DiT research paper",
            "publisher": "ICCV",
            "year": 2023,
            "original_source": "https://doi.org/10.48550/arXiv.2212.09748",
            "access_status": "paper PDF verified in local library",
            "local_file": ROOT / "daily" / "Flux" / "papers" / "01_foundations" / "dit_2212.09748.pdf",
            "families": ["spatial_portals", "material_morph", "particles_weather", "world_style"],
            "demonstrates": "Transformer 可以作为潜空间扩散骨干，为高表达力的材质、天气、世界风格和空间生成效果提供基础架构。",
            "does_not_prove": "基础图像生成论文不证明视频连续性、条件可控性、手机运行或事实保持。",
            "implementation_boundary": "research_prototype",
        },
        {
            "reference_id": "REF-LDM-LATENT-EDITING",
            "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
            "source_type": "paper_project",
            "product_work_paper": "CVPR 2022 latent diffusion research paper",
            "publisher": "CVPR",
            "year": 2022,
            "original_source": "https://doi.org/10.48550/arXiv.2112.10752",
            "access_status": "paper PDF verified in local library",
            "local_file": ROOT / "daily" / "20260821_ENC_DEC" / "papers" / "01_history_and_tokenizers" / "ldm_2112.10752.pdf",
            "families": ["spatial_portals", "material_morph", "particles_weather", "world_style"],
            "demonstrates": "潜空间生成降低高分辨率建模成本并支持条件控制，是录后生成式特效和高质量精修的重要基础。",
            "does_not_prove": "图像潜扩散不能直接证明视频时序一致性、低延迟或移动端部署可行。",
            "implementation_boundary": "research_prototype",
        },
    ]


def build_reference_records() -> list[dict]:
    grouped = _family_effect_ids()
    records = []
    for spec in _reference_specifications():
        local_file = spec.pop("local_file")
        families = spec.pop("families")
        files = []
        digest = ""
        if local_file is not None and local_file.exists():
            files = [repo_path(local_file)]
            digest = sha256(local_file)
        record = {
            **spec,
            "local_files": files,
            "effect_ids": _all_effect_ids(grouped, families),
            "sha256": digest,
        }
        schema.validate_reference(record)
        records.append(record)
    return records


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for char in paragraph:
            candidate = current + char
            if draw.textlength(candidate, font=font) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
    return lines


def _draw_person(draw: ImageDraw.ImageDraw, cx: int, floor_y: int, color=(224, 232, 240), pose=0) -> None:
    head_y = floor_y - 210
    draw.ellipse((cx - 38, head_y - 38, cx + 38, head_y + 38), fill=color, outline=(255, 255, 255), width=3)
    draw.line((cx, head_y + 40, cx, floor_y - 70), fill=color, width=24)
    arm = 70 + pose * 12
    draw.line((cx, head_y + 80, cx - arm, head_y + 125 - pose * 12), fill=color, width=18)
    draw.line((cx, head_y + 80, cx + arm, head_y + 110 + pose * 10), fill=color, width=18)
    draw.line((cx, floor_y - 75, cx - 60, floor_y), fill=color, width=20)
    draw.line((cx, floor_y - 75, cx + 58, floor_y), fill=color, width=20)


def _draw_scene(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], seed: int) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=18, fill=(18, 25, 38), outline=(67, 82, 104), width=2)
    horizon = y0 + int((y1 - y0) * 0.63)
    draw.rectangle((x0 + 2, horizon, x1 - 2, y1 - 2), fill=(29, 37, 49))
    for index in range(6):
        bx = x0 + 18 + index * ((x1 - x0 - 50) // 6)
        height = 75 + ((seed * 17 + index * 31) % 85)
        draw.rectangle((bx, horizon - height, bx + 52, horizon), fill=(31 + index * 3, 43, 62))
        if index % 2 == 0:
            draw.rectangle((bx + 10, horizon - height + 18, bx + 18, horizon - height + 28), fill=(255, 195, 92))
    draw.line((x0 + 8, horizon, x1 - 8, horizon), fill=(76, 91, 111), width=2)


def _draw_effect(draw: ImageDraw.ImageDraw, family: str, box: tuple[int, int, int, int], phase: int, accent, seed: int) -> None:
    x0, y0, x1, y1 = box
    floor_y = y1 - 48
    cx = (x0 + x1) // 2
    if family == "face_gaze_expression":
        cy = y0 + 190
        draw.ellipse((cx - 120, cy - 135, cx + 120, cy + 135), fill=(203, 173, 151), outline=(245, 226, 211), width=4)
        for eye_x in (cx - 48, cx + 48):
            draw.ellipse((eye_x - 30, cy - 28, eye_x + 30, cy + 12), fill=(247, 247, 242))
            pupil_shift = 0 if phase == 0 else int((1 - min(phase, 2) / 2) * 16)
            draw.ellipse((eye_x - 9 + pupil_shift, cy - 17, eye_x + 9 + pupil_shift, cy + 1), fill=accent)
            draw.ellipse((eye_x - 3 + pupil_shift, cy - 11, eye_x + 3 + pupil_shift, cy - 5), fill=(18, 24, 32))
        draw.arc((cx - 45, cy + 20, cx + 45, cy + 82), 10, 170, fill=(116, 63, 65), width=4)
        if phase >= 1:
            draw.line((cx, cy - 10, cx, y0 + 20), fill=accent, width=3)
            draw.ellipse((cx - 14, y0 + 8, cx + 14, y0 + 36), outline=accent, width=3)
        return

    _draw_person(draw, cx, floor_y, pose=(seed + phase) % 3)
    if phase == 0:
        return
    if family == "light_trails_optics":
        points = []
        for step in range(10):
            px = x0 + 70 + step * 39
            py = y0 + 245 + int(math.sin(step * 0.8 + seed) * 58) - phase * 12
            points.append((px, py))
        draw.line(points, fill=accent, width=8 + phase * 3, joint="curve")
        for px, py in points[::3]:
            draw.ellipse((px - 11, py - 11, px + 11, py + 11), fill=(255, 245, 194), outline=accent, width=3)
    elif family == "body_motion_clones":
        for offset, alpha_color in ((-105, (accent[0], accent[1], accent[2])), (105, (105, 183, 255))):
            _draw_person(draw, cx + offset, floor_y, color=alpha_color, pose=(seed + phase + offset) % 3)
    elif family == "time_editing":
        rx0, ry0, rx1, ry1 = cx - 135, y0 + 90, cx + 145, y1 - 30
        draw.rounded_rectangle((rx0, ry0, rx1, ry1), radius=22, outline=accent, width=6)
        for index in range(4):
            px = rx0 + 40 + index * 58
            draw.line((px, ry0 + 24, px, ry1 - 20), fill=(accent[0], accent[1], accent[2]), width=2)
        draw.polygon([(rx0 + 18, (ry0 + ry1)//2), (rx0 + 54, (ry0 + ry1)//2 - 24), (rx0 + 54, (ry0 + ry1)//2 + 24)], fill=accent)
    elif family == "spatial_portals":
        r = 70 + phase * 24
        draw.ellipse((cx - r, y0 + 90, cx + r, y0 + 90 + 2*r), outline=accent, width=14)
        draw.ellipse((cx - r + 22, y0 + 112, cx + r - 22, y0 + 68 + 2*r), fill=(42, 77, 118))
        draw.line((cx - r, y0 + 90 + r, cx + r, y0 + 90 + r), fill=(255, 255, 255), width=2)
    elif family == "virtual_light_shadow":
        draw.polygon([(cx - 170, y0 + 10), (cx + 160, floor_y), (cx - 60, floor_y)], fill=(accent[0], accent[1], accent[2]))
        draw.ellipse((cx - 85, floor_y - 28, cx + 120, floor_y + 18), fill=(8, 12, 18))
        _draw_person(draw, cx, floor_y, pose=(seed + phase) % 3)
    elif family == "material_morph":
        draw.rounded_rectangle((cx - 125, y0 + 110, cx + 125, y0 + 300), radius=28, outline=accent, width=5)
        for index in range(28):
            px = cx - 120 + (index * 37 + seed * 11) % 245
            py = y0 + 120 + (index * 53 + phase * 17) % 180
            draw.polygon([(px, py), (px + 15, py + 4), (px + 6, py + 18)], fill=accent)
    elif family == "particles_weather":
        for index in range(45):
            px = x0 + 28 + (index * 71 + seed * 19) % (x1 - x0 - 56)
            py = y0 + 28 + (index * 47 + phase * 37) % (y1 - y0 - 90)
            radius = 2 + (index % 5)
            draw.ellipse((px-radius, py-radius, px+radius, py+radius), fill=accent)
    elif family == "world_style":
        draw.rectangle((x0 + 2, y0 + 2, cx, y1 - 2), outline=accent, width=5)
        for index in range(8):
            px = x0 + 20 + index * 28
            draw.line((px, y0 + 24, px + 55, y1 - 35), fill=accent, width=4)
        draw.text((x0 + 28, y0 + 30), "STYLE", font=_font(30, True), fill=accent)
    elif family == "audio_lyrics":
        for index, height in enumerate((34, 72, 48, 106, 62, 88, 40, 70)):
            px = x0 + 65 + index * 45
            draw.rounded_rectangle((px, floor_y - height, px + 18, floor_y), radius=7, fill=accent)
        draw.text((x0 + 55, y0 + 42), "LYRIC / BEAT", font=_font(28, True), fill=(245, 246, 250))
    elif family == "effect_cinematography":
        r = 54 + phase * 42
        draw.ellipse((cx-r, y0+185-r, cx+r, y0+185+r), outline=accent, width=9)
        for index in range(10):
            angle = 2 * math.pi * index / 10
            draw.line((cx + int(r*math.cos(angle)), y0+185 + int(r*math.sin(angle)), cx + int((r+45)*math.cos(angle)), y0+185 + int((r+45)*math.sin(angle))), fill=accent, width=3)
    elif family == "multi_person_interaction":
        _draw_person(draw, cx - 115, floor_y, color=(226, 232, 240), pose=phase)
        _draw_person(draw, cx + 115, floor_y, color=(215, 225, 236), pose=2-phase)
        draw.line((cx - 60, y0 + 235, cx + 60, y0 + 235), fill=accent, width=13)
        draw.ellipse((cx - 25, y0 + 210, cx + 25, y0 + 260), fill=(255, 246, 195), outline=accent, width=5)


def _draw_storyboard(priority: dict, idea: dict, index: int, path: Path) -> None:
    width, height = 1800, 760
    image = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(image)
    family = idea["family"]
    accent = FAMILY_COLORS[family]
    draw.rectangle((0, 0, width, 92), fill=(22, 31, 45))
    draw.text((48, 22), f"{index:02d}  {idea['name_zh']}", font=_font(30, True), fill=(255, 255, 255))
    badge_text = "本项目概念分镜"
    badge_font = _font(22, True)
    badge_w = int(draw.textlength(badge_text, font=badge_font)) + 42
    draw.rounded_rectangle((width - badge_w - 44, 22, width - 44, 70), radius=12, fill=accent)
    draw.text((width - badge_w - 23, 31), badge_text, font=badge_font, fill=(16, 22, 32))

    panel_width, panel_height, gap = 520, 470, 55
    start_x, y0 = 65, 135
    labels = ("录制前：建立对象与边界", "触发中：低成本预览反馈", "成片后：高质量重算结果")
    summaries = (
        priority["interaction_timeline"][0],
        priority["interaction_timeline"][2],
        priority["post_refinement"],
    )
    for phase in range(3):
        x0 = start_x + phase * (panel_width + gap)
        scene_box = (x0, y0 + 58, x0 + panel_width, y0 + panel_height)
        draw.text((x0, y0), labels[phase], font=_font(22, True), fill=(28, 39, 55))
        _draw_scene(draw, scene_box, index + phase)
        _draw_effect(draw, family, scene_box, phase, accent, index)
        text_box_y = y0 + panel_height + 18
        lines = _wrap(draw, summaries[phase], _font(17), panel_width)
        for line_index, line in enumerate(lines[:3]):
            draw.text((x0, text_box_y + line_index * 27), line, font=_font(17), fill=(61, 72, 88))
        if phase < 2:
            arrow_x = x0 + panel_width + 13
            arrow_y = y0 + 275
            draw.line((arrow_x, arrow_y, arrow_x + 30, arrow_y), fill=accent, width=7)
            draw.polygon([(arrow_x + 30, arrow_y), (arrow_x + 18, arrow_y - 10), (arrow_x + 18, arrow_y + 10)], fill=accent)

    footer = f"{FAMILY_LABELS[family]} | {priority['priority_id']} | 概念图不代表既有产品、论文结果或已测性能"
    draw.rectangle((0, height - 54, width, height), fill=(229, 234, 240))
    draw.text((48, height - 39), footer, font=_font(17), fill=(54, 65, 80))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, quality=94)


def _draw_reference_card(record: dict, path: Path) -> None:
    width, height = 1600, 720
    image = Image.new("RGB", (width, height), (247, 249, 252))
    draw = ImageDraw.Draw(image)
    accent = (27, 107, 147)
    draw.rectangle((0, 0, width, 88), fill=(20, 38, 55))
    draw.text((48, 21), "可核实参考卡", font=_font(30, True), fill=(255, 255, 255))
    draw.rounded_rectangle((1240, 21, 1550, 68), radius=12, fill=(225, 235, 242))
    draw.text((1270, 31), record["implementation_boundary"], font=_font(20, True), fill=(20, 57, 78))
    draw.text((48, 122), record["title"], font=_font(34, True), fill=(24, 34, 48))
    draw.text((48, 176), f"{record['publisher']} | {record['year']} | {record['product_work_paper']}", font=_font(20), fill=(82, 94, 108))

    sections = (
        ("它能够证明什么", record["demonstrates"], (224, 242, 236), (24, 105, 76)),
        ("它不能证明什么", record["does_not_prove"], (255, 239, 225), (158, 77, 24)),
    )
    section_y = 238
    for title, body, fill, title_color in sections:
        draw.rounded_rectangle((48, section_y, 1552, section_y + 154), radius=16, fill=fill)
        draw.text((78, section_y + 18), title, font=_font(23, True), fill=title_color)
        lines = _wrap(draw, body, _font(20), 1400)
        for line_index, line in enumerate(lines[:3]):
            draw.text((78, section_y + 62 + line_index * 31), line, font=_font(20), fill=(45, 55, 67))
        section_y += 178

    local = record["local_files"][0] if record["local_files"] else "仅核验元数据，未缓存正文"
    draw.text((48, 616), f"本地证据：{local}", font=_font(18), fill=(66, 78, 94))
    draw.text((48, 656), f"绑定重点玩法：{len(record['effect_ids'])} 项", font=_font(18, True), fill=accent)
    draw.text((1245, 656), "不是产品效果截图", font=_font(18, True), fill=(158, 77, 24))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, quality=94)


def build() -> dict:
    references = build_reference_records()
    write_jsonl(references, REFERENCE_PATH)

    priorities = read_jsonl(PRIORITY_PATH)
    ideas = {row["effect_id"]: row for row in read_jsonl(IDEA_PATH)}
    storyboard_rows = []
    for index, priority in enumerate(priorities, 1):
        idea = ideas[priority["effect_id"]]
        image_path = STORYBOARD_DIR / f"{index:02d}_{priority['priority_id'].lower()}.png"
        _draw_storyboard(priority, idea, index, image_path)
        storyboard_rows.append({
            "priority_id": priority["priority_id"],
            "effect_id": priority["effect_id"],
            "name_zh": idea["name_zh"],
            "family": idea["family"],
            "visual_status": "本项目概念分镜",
            "image_path": repo_path(image_path),
            "panels": ["录制前", "触发中", "成片后"],
        })
    write_jsonl(storyboard_rows, STORYBOARD_MANIFEST)

    reference_cards = []
    for index, record in enumerate(references, 1):
        image_path = REAL_REFERENCE_DIR / f"{index:02d}_{record['reference_id'].lower()}.png"
        _draw_reference_card(record, image_path)
        reference_cards.append(repo_path(image_path))

    return {
        "references": len(references),
        "storyboards": len(storyboard_rows),
        "reference_cards": len(reference_cards),
        "reference_manifest": repo_path(REFERENCE_PATH),
        "storyboard_manifest": repo_path(STORYBOARD_MANIFEST),
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
