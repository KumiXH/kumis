"""Build a visual Markdown atlas for the mobile-video idea universe."""

from __future__ import annotations

import json
import os
import re
from collections import OrderedDict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "daily" / "20260826_后处理调研"
CORE_PATH = PROJECT / "metadata" / "idea_universe" / "core_ideas.jsonl"
SOURCE_PATH = PROJECT / "sources" / "source_manifest.json"
FIGURE_ROOT = PROJECT / "figures" / "idea_atlas"
CONTACT_ROOT = FIGURE_ROOT / "contact_sheets"
PANEL_ROOT = FIGURE_ROOT / "panels"
REPORT_ROOT = PROJECT / "report"
PAGE_ROOT = REPORT_ROOT / "idea_atlas_pages"


PANEL_MAP = OrderedDict(
    [
        ("legacy_112", (1, 1)),
        ("prior_brainstorm", (1, 2)),
        ("raw_asset", (1, 3)),
        ("object_exposure", (1, 4)),
        ("temporal_canvas", (1, 5)),
        ("intent_stabilization", (1, 6)),
        ("motion_recovery", (2, 1)),
        ("virtual_optics", (2, 2)),
        ("lens_surface", (2, 3)),
        ("light_decomposition", (2, 4)),
        ("complex_lights", (2, 5)),
        ("multi_camera_continuity", (2, 6)),
        ("spatial_reframe", (3, 1)),
        ("portrait_regions", (3, 2)),
        ("body_action", (3, 3)),
        ("reflection_material", (3, 4)),
        ("scene_memory", (3, 5)),
        ("weather_atmosphere", (3, 6)),
        ("semantic_color", (4, 1)),
        ("audio_camera", (4, 2)),
        ("trusted_generation", (4, 3)),
        ("semantic_codec", (4, 4)),
        ("power_scheduler", (4, 5)),
        ("event_sensor", (4, 6)),
        ("focus_phase", (5, 1)),
        ("privacy_safety", (5, 2)),
        ("concert_capture", (5, 3)),
        ("sports_capture", (5, 4)),
        ("children_pet", (5, 5)),
        ("vehicle_cabin", (5, 6)),
        ("live_stream", (6, 1)),
        ("commerce_product", (6, 2)),
        ("travel_story", (6, 3)),
        ("interview_meeting", (6, 4)),
        ("accessibility", (6, 5)),
        ("education_science", (6, 6)),
        ("ar_overlay", (7, 1)),
        ("memory_narrative", (7, 2)),
        ("collaborative_capture", (7, 3)),
        ("social_creation", (7, 4)),
        ("drone_action", (7, 5)),
        ("cinema_language", (7, 6)),
        ("quality_guard", (8, 1)),
        ("multi_spectral", (8, 2)),
    ]
)


SOURCE_MAP = {
    "legacy_112": ["official_apple_cinematic_mode", "official_final_cut_object_tracker"],
    "prior_brainstorm": ["local_flashvsr", "local_fluxir", "local_magvit"],
    "raw_asset": ["local_magvit", "local_wfvae", "local_flashvsr"],
    "object_exposure": ["official_apple_cinematic_mode", "local_fluxir"],
    "temporal_canvas": ["local_flashvsr", "official_final_cut_object_tracker"],
    "intent_stabilization": ["official_dji_horizon_steady", "official_dji_rocksteady"],
    "motion_recovery": ["local_flashvsr", "local_vrt"],
    "virtual_optics": ["official_apple_cinematic_mode", "official_apple_photographic_styles"],
    "lens_surface": ["official_apple_cinematic_mode", "official_apple_photographic_styles"],
    "light_decomposition": ["local_fluxir", "local_authface"],
    "complex_lights": ["official_blackmagic_gen5_color", "official_samsung_super_steady"],
    "multi_camera_continuity": ["official_insta360_me_mode", "official_samsung_single_take"],
    "spatial_reframe": ["official_final_cut_object_tracker", "official_capcut_video_cutout"],
    "portrait_regions": ["local_authface", "local_svfr", "local_tiger", "local_vfhq"],
    "body_action": ["local_tiger", "local_svfr", "local_vfhq"],
    "reflection_material": ["official_apple_cinematic_mode", "local_fluxir"],
    "scene_memory": ["official_final_cut_object_tracker", "official_capcut_video_cutout"],
    "weather_atmosphere": ["official_apple_photographic_styles", "official_capcut_video_cutout"],
    "semantic_color": ["official_blackmagic_gen5_color", "official_apple_photographic_styles"],
    "audio_camera": ["local_hdtf", "official_final_cut_object_tracker"],
    "trusted_generation": ["official_capcut_video_cutout", "local_fluxir"],
    "semantic_codec": ["local_wfvae", "local_magvit"],
    "power_scheduler": ["local_flashvsr", "local_magvit"],
    "event_sensor": [],
    "focus_phase": ["official_dji_subject_tracking", "official_final_cut_object_tracker"],
    "privacy_safety": [],
    "concert_capture": ["official_samsung_super_steady", "official_blackmagic_camera_app"],
    "sports_capture": ["official_dji_active_track", "official_dji_subject_tracking"],
    "children_pet": ["official_samsung_single_take", "official_dji_subject_tracking"],
    "vehicle_cabin": ["official_apple_cinematic_mode", "official_apple_photographic_styles"],
    "live_stream": ["official_blackmagic_camera_app", "official_capcut_video_cutout"],
    "commerce_product": ["official_blackmagic_camera_app", "official_blackmagic_gen5_color"],
    "travel_story": ["official_insta360_me_mode", "official_apple_cinematic_mode"],
    "interview_meeting": ["local_hdtf", "official_final_cut_object_tracker"],
    "accessibility": [],
    "education_science": [],
    "ar_overlay": [],
    "memory_narrative": ["official_samsung_single_take", "official_apple_cinematic_mode"],
    "collaborative_capture": ["official_insta360_me_mode", "official_samsung_single_take"],
    "social_creation": ["official_capcut_video_cutout", "official_samsung_single_take"],
    "drone_action": ["official_dji_active_track", "official_dji_horizon_steady", "official_dji_rocksteady"],
    "cinema_language": ["official_apple_cinematic_mode", "official_final_cut_object_tracker"],
    "quality_guard": ["official_dji_horizon_steady", "official_blackmagic_camera_app"],
    "multi_spectral": [],
}


CLUSTER_READINGS = {
    "legacy_112": "这是此前证据型机会库的完整映射。图中用手机取景、夜景光源、运动主体和分层信息表达旧方向如何落到录像链路；页面下方保留全部 112 条原始机会，便于从概念图回查历史记录。",
    "prior_brainstorm": "这是此前对话中明确提出的重点主线。图中把计算底片、对象级时间控制、光照层和运动状态放在同一条可重算录像链路中，强调这些是跨功能基础设施，而不是单个滤镜。",
    "raw_asset": "核心问题是把录像保存成可以重新计算的影像资产：除了 RGB/YUV，还保存深度、Mask、运动、曝光和相机状态。这样录后才能重新选择 ISP、光照、景深、构图或生成边界。",
    "object_exposure": "把整帧曝光和快门推广为对象级时间控制。人物、背景、高亮、运动轨迹可以使用不同的等效曝光策略，用户最终看到的是清晰主体与可控运动质感的组合。",
    "temporal_canvas": "把时间从不可逆的连续帧变成可编辑画布。局部慢动作、时间拖影、事件回放和关键帧重算都可以在同一条时间轴上选择性发生。",
    "intent_stabilization": "稳定算法不再只追求‘越稳越好’，而是识别摇摄、跟拍、甩镜和升降等创作者意图，抑制手抖同时保留主动运动。",
    "motion_recovery": "重点是恢复运动主体的结构与细节，并显式处理运动模糊、滚动快门、遮挡和跨帧纹理传播。适合人脸、手部、器械、车辆文字等高价值 ROI。",
    "virtual_optics": "把物理镜头特性参数化为可编辑的时序渲染：星芒、flare、焦外、柔焦、暗角、像差和镜头呼吸都可以由光源、深度与相机姿态驱动。",
    "lens_surface": "镜头表面和透明介质本身也可以成为可处理对象。雨滴、雾气、污渍、保护壳反射与玻璃折射需要区分场景内容，才能实现可逆抑制或创作增强。",
    "light_decomposition": "图中的人物被拆成主光、轮廓光、屏幕光、环境光和阴影层。用户效果不是简单提亮，而是让虚拟光受深度、遮挡、材质和真实阴影约束。",
    "complex_lights": "演唱会、LED 屏幕、霓虹和车灯要求同时处理高光、频闪、颜色、烟雾和主体曝光。手机录像需要把光源频率与主体语义放进同一个时序模型。",
    "multi_camera_continuity": "多摄的关键不是单次切镜，而是跨镜头持续保持曝光、白平衡、肤色、噪声、纹理、运动和景深风格。连续焦段是一个系统一致性问题。",
    "spatial_reframe": "空间录像和录后运镜依赖深度、SLAM、IMU 与多摄信息。优先在已观测区域内做受约束重投影，只有在明确授权时才使用生成式画外补全。",
    "portrait_regions": "人像不应只用一个全脸强度。眼睛、皮肤、嘴唇、牙齿、头发、眼镜和服装需要不同的恢复与真实性约束，并持续检查身份、几何和时序纹理。",
    "body_action": "人体动作录像的难点是手指、衣摆、器械和快速姿态。姿态、部件 Mask、高帧率缓存和局部清晰窗口可以共同保护这些细节。",
    "reflection_material": "玻璃、金属、水面、纱帘和半透明介质不能按普通纹理处理。需要把反射、透射、散射和材质高光分层，才能做可信的抑制、增强或替换。",
    "scene_memory": "持续场景记忆允许用历史真实背景恢复短时遮挡，也支持路人移除、污点清理和遮挡因果判断。只有没有真实观测时，才应进入生成式补全。",
    "weather_atmosphere": "天气编辑不只是给画面加雨雾。天空、空气透视、地面湿润反射、阴影和人物光照需要联动，并把生成区域和可信度保存下来。",
    "semantic_color": "语义色彩把肤色、天空、植被、灯光、高光和阴影分区处理，同时维持跨帧、跨镜头和跨显示设备的连续性。",
    "audio_camera": "手机麦克风阵列可以成为摄影控制信号：声源方向、对白轮次、节拍和突发声音事件可驱动跟焦、构图、运镜、缓存和自动成片。",
    "trusted_generation": "生成式录像的核心不是‘全部重画’，而是保护区、世界状态和不确定性管理。脸、文字、商标、建筑几何和事件事实应默认锁定。",
    "semantic_codec": "编码器可以根据人脸、手部、文字和运动主体分配码率，并复用运动矢量和轻量特征。用户看到的结果是低码率下主体可读、背景可压缩。",
    "power_scheduler": "长时间录像需要把 ISP、DSP、NPU、GPU 和 VPU 当成一个系统调度问题。温度、功耗、ROI、关键帧和代理模型共同决定质量如何稳定下降。",
    "event_sensor": "事件传感器提供普通 RGB 帧之间的高时间分辨率变化，适合高速运动、低照、频闪、去模糊、插帧和高频稳定。当前页面是前沿概念方向，未绑定量产器件。",
    "focus_phase": "对焦和光学机构信息可以进入算法链。预测焦点平面、对焦速度、OIS/OIS 状态和逐行时间有助于减少失焦、呼吸、滚动快门和空间层级错误。",
    "privacy_safety": "录像后处理还应处理隐私、匿名和证据链。保护区、可逆替换、分级导出和审计日志可以让效果增强与个人安全同时存在。",
    "concert_capture": "演唱会录像要优先保护远距离歌手、LED 内容、肤色、高光和声音关联，再叠加虚拟追光、节拍光效和稳定导播。",
    "sports_capture": "体育录像的对象不是整场画面，而是球、运动员、器械、规则事件和精彩瞬间。跟踪、轨迹、缓存、慢动作和多机位可以组成自动导播链。",
    "children_pet": "儿童和宠物动作不可预测，适合使用录制前环形缓存、声音触发、行为预测、低机位构图和人脸/毛发双路恢复。",
    "vehicle_cabin": "车内和移动空间同时存在玻璃反射、道路振动、内外曝光差、乘员人像和快速光照变化，适合做空间分层与稳像协同。",
    "live_stream": "直播要求长时间稳定、低延迟、低发热和可持续的主体质量。代理路径、ROI 优先、自动构图和录后母版可以形成双轨系统。",
    "commerce_product": "商品和美食录像强调材质、反射、高光、蒸汽、色彩和细节可读性。用户需要的是可控的展示光和真实材质，不是泛化的锐化。",
    "travel_story": "旅行录像可以把主体、城市、地标和路线组织成连续叙事，并跨焦段、跨片段维护色彩、构图和运动风格。",
    "interview_meeting": "采访和会议适合让声音、说话人身份、视线和构图共同决定自动导播，同时保护屏幕文字和多人时序一致性。",
    "accessibility": "无障碍录像把画面质量守护扩展为方向、触觉、主体确认和语音反馈，让拍摄辅助成为可访问的系统功能。",
    "education_science": "教育和科学记录强调测量标记、实验器材、事件时刻和可回放证据，生成式增强必须服从事实保护。",
    "ar_overlay": "AR 与现实融合录像需要稳定的空间锚点、遮挡关系、真实阴影和材质响应，否则虚拟内容会漂浮在画面上。",
    "memory_narrative": "个人记忆录像可以跨时间、地点和季节维护人物、构图与声音线索，形成可检索、可重混、可持续更新的长期叙事资产。",
    "collaborative_capture": "多设备协同的重点是时间码、颜色、位姿、主体轨迹、声音和导播策略共享，让多部手机像一台分布式电影机。",
    "social_creation": "社交创作可以从一次表演自动派生多个裁切、节奏、效果和分享版本，但应保存原始事实帧和生成修改边界。",
    "drone_action": "无人机和运动相机的跟拍、地平线锁定、轨迹镜头和空间移动可以迁移到手机，重点是利用手机自身 IMU、多摄和裁切余量。",
    "cinema_language": "手机录像可以提供镜头语言辅助：景别、视线、推拉、滑轨、环绕、节奏和反应镜头被作为可编辑的拍摄意图。",
    "quality_guard": "质量守护不是简单报错，而是预测失焦、过曝、遮挡、抖动、噪声和生成不确定性，并在拍摄前、录制中和录后给出可执行的补救。",
    "multi_spectral": "多光谱、近红外、热成像和深度可以作为 RGB 的辅助证据，改善夜景、低照、遮挡和材质识别；这里强调的是融合潜力，不代表当前手机普遍具备这些传感器。",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def load_sources() -> dict[str, dict]:
    raw = json.loads(SOURCE_PATH.read_text(encoding="utf-8-sig"))
    return {row["source_id"]: row for row in raw}


def safe_slug(text: str) -> str:
    value = re.sub(r"[^0-9A-Za-z一-鿿]+", "_", text).strip("_")
    return value[:80] or "cluster"


def relative_local_link(value: str, from_dir: Path) -> str | None:
    if not value:
        return None
    normalized = Path(value.replace("\\", "/"))
    if normalized.is_absolute() and normalized.exists():
        return Path(os.path.relpath(normalized, from_dir)).as_posix()
    return None


def crop_panels() -> dict[str, str]:
    PANEL_ROOT.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}
    for cluster, (contact_id, panel_id) in PANEL_MAP.items():
        source = CONTACT_ROOT / f"contact_{contact_id:02d}.png"
        target = PANEL_ROOT / f"{cluster}.png"
        image = Image.open(source).convert("RGB")
        width, height = image.size
        col = (panel_id - 1) % 3
        row = (panel_id - 1) // 3
        left = round(col * width / 3)
        right = round((col + 1) * width / 3)
        top = round(row * height / 2)
        bottom = round((row + 1) * height / 2)
        image.crop((left, top, right, bottom)).save(target, optimize=True)
        paths[cluster] = target.relative_to(PROJECT).as_posix()
    return paths


def source_lines(cluster: str, source_map: dict[str, dict]) -> list[str]:
    lines = []
    for source_id in SOURCE_MAP.get(cluster, []):
        source = source_map.get(source_id)
        if not source:
            continue
        links = []
        if source.get("url"):
            links.append(f"[外部来源]({source['url']})")
        local = relative_local_link(source.get("local_path", ""), PAGE_ROOT)
        if local:
            links.append(f"[本地缓存]({local})")
        link_text = " / ".join(links) or "来源链接未保存"
        status = source.get("verification_status", "未记录")
        lines.append(f"- **{source['title']}**（{source.get('evidence_level', '未分级')}，{status}）：{link_text}")
    return lines or ["- 本簇暂未绑定具体论文或产品来源；图像用于解释概念外观，不能作为已实现功能证据。"]


def cluster_summary(rows: list[dict]) -> str:
    truths = {row.get("default_truth") for row in rows}
    scenes = []
    for row in rows:
        for scene in row.get("scenarios", []):
            if scene not in scenes:
                scenes.append(scene)
    return f"本簇收录 {len(rows)} 条基础 IDEA，默认真实性边界包括 {', '.join(sorted(t for t in truths if t))}；代表场景：{', '.join(scenes[:8]) or '通用录像'}。"


def render_cluster_page(
    index: int,
    cluster: str,
    rows: list[dict],
    image_path: str,
    source_map: dict[str, dict],
    cluster_to_page: dict[str, str],
) -> str:
    title = rows[0]["cluster_zh"]
    lines = [
        f"# {index:02d}. {title}",
        "",
        f"> `idea_only` 图文页面。图片是概念示意，不代表已量产效果；来源链接用于理解相关技术或产品边界。",
        "",
        f"![{title}概念示意](../../{image_path})",
        "",
        f"*图 {index:02d}：{title}的概念示意。画面用于帮助理解用户最终看到的效果，不是论文原图或真实产品截图。*",
        "",
        "## 看图理解",
        "",
        CLUSTER_READINGS.get(cluster, "本簇把多个录像功能放在同一个用户效果和时序处理框架中理解。"),
        "",
        cluster_summary(rows),
        "",
        "## 本簇 IDEA",
        "",
    ]
    for row in rows:
        signals = "、".join(row.get("input_signals", [])) or "未指定"
        scenes = "、".join(row.get("scenarios", [])) or "通用录像"
        risks = "、".join(row.get("risks", [])) or "需通过实验确认"
        lines.extend(
            [
                f"### {row['idea_id']}｜{row['name_zh']}",
                "",
                f"- **用户效果**：{row.get('user_effect', '')}",
                f"- **核心机制**：{row.get('core_mechanism', '')}",
                f"- **手机输入**：{signals}",
                f"- **适用场景**：{scenes}",
                f"- **真实性边界**：`{row.get('default_truth', '')}`",
                f"- **主要风险**：{risks}",
                "",
            ]
        )
    lines.extend(["## 相关来源", ""])
    lines.extend(source_lines(cluster, source_map))
    lines.extend(
        [
            "",
            "## 阅读建议",
            "",
            "先看图判断用户效果，再回到上面的 `idea_id` 了解处理对象和输入信号；需要落地时，再从来源、数据、时序一致性、端侧预算和真实性边界分别建立验证任务。",
            "",
            "[返回图文图鉴总览](../手机录像后处理_IDEA图文图鉴_20260827.md)",
            "",
        ]
    )
    return "\n".join(lines)


def build() -> dict:
    rows = read_jsonl(CORE_PATH)
    sources = load_sources()
    grouped: OrderedDict[str, list[dict]] = OrderedDict()
    for row in rows:
        grouped.setdefault(row["idea_cluster"], []).append(row)
    assert list(grouped) == list(PANEL_MAP), (list(grouped), list(PANEL_MAP))
    image_paths = crop_panels()
    PAGE_ROOT.mkdir(parents=True, exist_ok=True)
    for old in PAGE_ROOT.glob("*.md"):
        old.unlink()
    cluster_to_page = {
        cluster: f"idea_atlas_pages/{index:02d}_{safe_slug(rows[0]['cluster_zh'])}.md"
        for index, (cluster, rows) in enumerate(grouped.items(), 1)
    }
    page_entries = []
    for index, (cluster, cluster_rows) in enumerate(grouped.items(), 1):
        page_path = PAGE_ROOT / Path(cluster_to_page[cluster]).name
        page_path.write_text(
            render_cluster_page(index, cluster, cluster_rows, image_paths[cluster], sources, cluster_to_page),
            encoding="utf-8",
        )
        page_entries.append((index, cluster, cluster_rows, image_paths[cluster], page_path))

    main = [
        "# 手机录像后处理 IDEA 图文图鉴",
        "",
        "日期：2026-08-27",
        "",
        "> 这是一份个人阅读用的概念图鉴。它把手机录像后处理创意与视觉示意放在一起，帮助读者先理解‘用户会看到什么’，再回看算法、输入信号、数据和风险。",
        "",
        "## 使用边界",
        "",
        "- 全量基础 IDEA：1,154 条；创意簇：44 个。",
        "- 每个创意簇配置一张概念示意图，并保留该簇全部基础 IDEA。",
        "- 图像由统一的概念视觉母图裁切得到，不是论文原图，也不是厂商真实产品截图。",
        "- 旧 112 条机会的来源证据与新创意的概念推演分开表达；新增创意统一标记为 `idea_only`。",
        "- 实时预览、录制在线、录后端侧、云端、30/60 fps、ROI 等属于实现变体，请继续查看[变体全量报告](手机录像后处理_IDEA变体全量_20260827.md)。",
        "",
        "## 总体图谱",
        "",
        "```mermaid",
        "flowchart LR",
        "  A[手机录像输入] --> B[时序状态与语义对象]",
        "  B --> C[恢复与增强]",
        "  B --> D[光学与时间重构]",
        "  B --> E[生成式编辑与事实保护]",
        "  B --> F[编码、功耗与交付]",
        "  C --> G[可重算录像资产]",
        "  D --> G",
        "  E --> G",
        "  F --> G",
        "```",
        "",
        "## 图文入口",
        "",
    ]
    for index, cluster, cluster_rows, image_path, page_path in page_entries:
        title = cluster_rows[0]["cluster_zh"]
        rel_page = Path("idea_atlas_pages", page_path.name).as_posix()
        main.extend(
            [
                f"### {index:02d}. [{title}]({rel_page})",
                "",
                f"![{title}概念示意](../{image_path})",
                "",
                f"{CLUSTER_READINGS.get(cluster, '')} {cluster_summary(cluster_rows)}",
                "",
                f"该簇包含：`{len(cluster_rows)}` 条基础 IDEA。",
                "",
            ]
        )
    main.extend(
        [
            "## 数据与索引",
            "",
            "- [基础 IDEA 全量 JSONL](../metadata/idea_universe/core_ideas.jsonl)",
            "- [单轴变体全量 JSONL](../metadata/idea_universe/idea_variants.jsonl)",
            "- [基础 IDEA 全量纯文本报告](手机录像后处理_IDEA全量宇宙_20260827.md)",
            "- [实现变体全量纯文本报告](手机录像后处理_IDEA变体全量_20260827.md)",
            "- [Excel 全量数据库](../matrix/手机录像后处理_IDEA全量宇宙_20260827.xlsx)",
            "- [视觉资产目录](../figures/idea_atlas/)",
            "",
            "## 图片说明",
            "",
            "本图鉴中的图像用于建立视觉直觉：动态星芒、虚拟打光、对象级快门、多摄切镜、声音驱动、语义编码等功能分别对应用户可观察的画面或交互变化。涉及编解码、功耗、可信生成和多光谱的图像会使用可视化界面或分层表达，因为这些能力不能仅靠普通摄影画面直接呈现。",
            "",
            "每张图片都应与页面中的文字、`idea_id`、来源状态和风险一起阅读；不能把概念图解读为已实现性能。",
            "",
        ]
    )
    main_path = REPORT_ROOT / "手机录像后处理_IDEA图文图鉴_20260827.md"
    main_path.write_text("\n".join(main), encoding="utf-8")
    manifest = {
        "status": "concept_visuals_only",
        "core_ideas": len(rows),
        "clusters": len(grouped),
        "cluster_pages": len(page_entries),
        "contact_sheets": 8,
        "panel_images": len(image_paths),
        "source_policy": "verified source links when available; otherwise explicit no-source note",
        "main_report": str(main_path),
    }
    (FIGURE_ROOT / "visual_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
