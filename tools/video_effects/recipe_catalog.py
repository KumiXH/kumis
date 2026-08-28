"""Build and validate deterministic combinations of reusable video effects."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path

from tools.video_effects import schema


ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "daily" / "20260827_录像特效调研" / "metadata"
ATOM_INPUT = METADATA / "effect_atoms.jsonl"
IDEA_INPUT = METADATA / "effect_ideas.jsonl"
RECIPE_OUTPUT = METADATA / "effect_recipes.jsonl"

RECIPE_FIELDS = (
    "recipe_id",
    "name_zh",
    "component_atom_ids",
    "component_effect_ids",
    "trigger_logic",
    "combined_effect",
    "why_new",
    "preview_behavior",
    "post_behavior",
    "risks",
    "target_scenarios",
)

RECIPE_FAMILY_ORDER = (
    "light_anchor_optics",
    "gaze_expression",
    "time_cloning",
    "shadow_light",
    "audio_lyrics",
    "multi_person",
    "particles_weather",
    "spatial_world",
    "material_generation",
    "effect_cinematography",
)

_DIMENSION_ORDER = (
    "realtime_light_trail",
    "world_anchor",
    "sound",
    "spatial_portal",
    "body_pose",
    "time",
    "gaze",
    "material",
    "expression",
    "multi_person",
    "color_layer",
    "touch_gesture",
    "shadow",
    "action_inverse",
    "particle",
    "generative_world",
    "generative_style",
    "light",
)

MULTIDIMENSION_AXES = frozenset({
    "realtime_light_trail",
    "gaze",
    "expression",
    "time",
    "shadow",
    "sound",
    "multi_person",
})


def _b(
    slug: str,
    family: str,
    title: str,
    atoms: tuple[str, ...],
    effects: tuple[str, ...],
    _dimensions: tuple[str, ...],
    binding: str,
    bridge: str,
    preview: str,
    post: str,
    _scenario: str,
    variants: tuple[dict[str, str], ...],
) -> dict[str, object]:
    if len(variants) != 5:
        raise ValueError(f"blueprint {slug} must have five variants")
    complete_variants = []
    for index, variant in enumerate(variants, start=1):
        if set(variant) != set(RECIPE_FIELDS):
            raise ValueError(f"variant {slug}-V{index} is not a complete recipe")
        complete_variants.append(copy.deepcopy(variant))
    return {
        "slug": slug,
        "family": family,
        "title": title,
        "atoms": atoms,
        "effects": effects,
        "binding": binding,
        "bridge": bridge,
        "preview": preview,
        "post": post,
        "variants": tuple(complete_variants),
    }


# Four blueprints per family make the catalog auditable: each blueprint has one
# fixed component recipe and five explicitly different visible behaviours.
RECIPE_BLUEPRINTS = (
    _b(
        "HAND-ANCHOR-BEAT", "light_anchor_optics", "手迹锚点节拍光绘",
        (
            "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        ),
        (
            "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
            "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE",
            "FX-LIGHT-TRAILS-OPTICS-FINGER-SCREENBEAT",
        ),
        ("realtime_light_trail", "world_anchor", "sound"),
        "手部三维轨迹负责写入路径，世界锚点把路径放入场景坐标，节拍相位决定笔画何时发光",
        "光轨会随真实地面、墙面和遮挡关系改变位置，而不是作为贴在屏幕上的平面滤镜",
        "预览用短历史路径和低密度锚点显示连续笔迹，并在每个强拍更新亮度与颜色",
        "录制后重建完整手部轨迹、锚点深度和遮挡边缘，再细化笔触宽度与节拍曲线",
        "夜景街头用手指引导一条会写入建筑空间的节拍光字",
        (
        {
    "recipe_id": "RECIPE-HAND-ANCHOR-BEAT-V1",
    "name_zh": "手迹锚点节拍光绘·霓虹签名",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE",
        "FX-LIGHT-TRAILS-OPTICS-FINGER-SCREENBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR"
    ],
    "trigger_logic": "用户在空中画出闭合手势且下一次强拍到来",
    "combined_effect": "手指划过的路径在墙面上闭合成霓虹签名，强拍时笔画接缝同时亮起",
    "why_new": "闭合手势把光绘终点变成世界锚点的回扣，形成可读的空间签名而非普通拖尾",
    "preview_behavior": "预览用短历史路径和低密度锚点显示连续笔迹，并在每个强拍更新亮度与颜色。针对霓虹签名，取景器先在“用户在空中画出闭合手势且下一次强拍到来”发生前标出候选轨迹，确认后才显示“手指划过的路径在墙面上闭合成霓虹签名，强拍时笔画接缝同时亮起”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建完整手部轨迹、锚点深度和遮挡边缘，再细化笔触宽度与节拍曲线。录后以“用户在空中画出闭合手势且下一次强拍到来”的首帧为时间锚，重新计算霓虹签名涉及的遮挡和深度，使“手指划过的路径在墙面上闭合成霓虹签名，强拍时笔画接缝同时亮起”在原分辨率下保持连续；检测到快速转腕会让闭合端点漂移，低置信度时保持上一锚点并缩短笔画时仅修补低置信度片段。",
    "risks": [
        "快速转腕会让闭合端点漂移，低置信度时保持上一锚点并缩短笔画"
    ],
    "target_scenarios": [
        "夜间街区的墙面近景适合拍摄霓虹签名：先让主体完成“用户在空中画出闭合手势且下一次强拍到来”，随后缓慢移动手机观察“手指划过的路径在墙面上闭合成霓虹签名，强拍时笔画接缝同时亮起”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-HAND-ANCHOR-BEAT-V2",
    "name_zh": "手迹锚点节拍光绘·地面节拍字",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE",
        "FX-LIGHT-TRAILS-OPTICS-FINGER-SCREENBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST"
    ],
    "trigger_logic": "手部轨迹与地面平面相交并检测到连续两次强拍",
    "combined_effect": "每拍新增一个落在地面的发光字，镜头前进时字仍留在原处并产生前后遮挡",
    "why_new": "轨迹方向、地面坐标和节拍编号共同决定字的落点，使光字参与空间叙事",
    "preview_behavior": "移动端预览从地面节拍字的结果层反推触发：屏幕持续保留对象身份和最近历史，当“手部轨迹与地面平面相交并检测到连续两次强拍”成立时，把“每拍新增一个落在地面的发光字，镜头前进时字仍留在原处并产生前后遮挡”分成进入、保持、退场三段显示。若出现地面估计错误会让字悬浮，无法确认平面时改为脚边短光线，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把地面节拍字拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“手部轨迹与地面平面相交并检测到连续两次强拍”，再细化“每拍新增一个落在地面的发光字，镜头前进时字仍留在原处并产生前后遮挡”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "地面估计错误会让字悬浮，无法确认平面时改为脚边短光线"
    ],
    "target_scenarios": [
        "在音乐节舞台前沿的横向跟拍使用地面节拍字。镜头从未触发状态开始横向移动，人物或物体执行“手部轨迹与地面平面相交并检测到连续两次强拍”后继续穿过画面，以“每拍新增一个落在地面的发光字，镜头前进时字仍留在原处并产生前后遮挡”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-HAND-ANCHOR-BEAT-V3",
    "name_zh": "手迹锚点节拍光绘·空中光桥",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE",
        "FX-LIGHT-TRAILS-OPTICS-FINGER-SCREENBEAT",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "用户从画面左侧向右侧划过并在末端停留半拍",
    "combined_effect": "手指两端之间架起一条带节拍脉冲的光桥，桥身被路人经过时分成前后两段",
    "why_new": "停留事件决定桥的第二锚点，遮挡分段让路径具有可穿行的空间结构",
    "preview_behavior": "拍摄者先看到空中光桥所需的对象边界、方向箭头和时间门；“用户从画面左侧向右侧划过并在末端停留半拍”被连续确认后，预览按由近到远的层次展开“手指两端之间架起一条带节拍脉冲的光桥，桥身被路人经过时分成前后两段”。光轨会随真实地面、墙面和遮挡关系改变位置，而不是作为贴在屏幕上的平面滤镜，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验空中光桥的身份链与事件顺序，再按手部三维轨迹负责写入路径，世界锚点把路径放入场景坐标，节拍相位决定笔画何时发光重建组件关系。“手指两端之间架起一条带节拍脉冲的光桥，桥身被路人经过时分成前后两段”使用完整历史窗口重新渲染，而“用户从画面左侧向右侧划过并在末端停留半拍”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "多人遮挡会切断桥身，跟踪不确定时仅保留端点光核"
    ],
    "target_scenarios": [
        "把空中光桥安排在室内展馆的环绕装置镜头：固定主体身份后执行“用户从画面左侧向右侧划过并在末端停留半拍”，拍摄者绕触发点改变观察角度，用“手指两端之间架起一条带节拍脉冲的光桥，桥身被路人经过时分成前后两段”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-HAND-ANCHOR-BEAT-V4",
    "name_zh": "手迹锚点节拍光绘·指尖星座",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE",
        "FX-LIGHT-TRAILS-OPTICS-FINGER-SCREENBEAT",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "用户连续点出三个空间点且音乐进入副歌",
    "combined_effect": "三个点被光线连接成会随镜头视差移动的星座，副歌时按连线顺序依次闪烁",
    "why_new": "离散点选和连续光绘被统一到同一锚点图，结果不是散点叠加而是可回看的路径拓扑",
    "preview_behavior": "为预览指尖星座，系统只更新与“用户连续点出三个空间点且音乐进入副歌”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“三个点被光线连接成会随镜头视差移动的星座，副歌时按连线顺序依次闪烁”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "指尖星座的后处理从失败点开始：针对“点位过近会造成连线重叠，系统合并近邻节点并降低星芒强度”复核掩码、锚点或时间戳，通过后才将“三个点被光线连接成会随镜头视差移动的星座，副歌时按连线顺序依次闪烁”提升到成片质量。触发逻辑“用户连续点出三个空间点且音乐进入副歌”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "点位过近会造成连线重叠，系统合并近邻节点并降低星芒强度"
    ],
    "target_scenarios": [
        "天台灯光表演的一镜到底可用指尖星座组织一段连续互动。参与者先保持关系稳定，再完成“用户连续点出三个空间点且音乐进入副歌”；镜头不切断，直到“三个点被光线连接成会随镜头视差移动的星座，副歌时按连线顺序依次闪烁”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-HAND-ANCHOR-BEAT-V5",
    "name_zh": "手迹锚点节拍光绘·旋转光篱",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE",
        "FX-LIGHT-TRAILS-OPTICS-FINGER-SCREENBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "用户绕手机画一圈并在旋转终点听到强拍",
    "combined_effect": "环形轨迹竖立在世界空间中成为发光篱笆，强拍让相邻竖线依次向外打开",
    "why_new": "手机旋转只改变观察方向，三维手迹却固定在场景中，节拍进一步赋予篱笆开合节奏",
    "preview_behavior": "旋转光篱的取景反馈以结束状态为目标：预览先保留真实动作，在“用户绕手机画一圈并在旋转终点听到强拍”完成时快速呈现“环形轨迹竖立在世界空间中成为发光篱笆，强拍让相邻竖线依次向外打开”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留旋转光篱的完整生命周期。系统逆向检查“环形轨迹竖立在世界空间中成为发光篱笆，强拍让相邻竖线依次向外打开”是否回到稳定终态，再从“用户绕手机画一圈并在旋转终点听到强拍”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "快速旋转可能积累错误锚点，超过角速度阈值时冻结最近可信环面"
    ],
    "target_scenarios": [
        "以灯棒与人物同框的收束镜头作为旋转光篱的结尾段落：让“用户绕手机画一圈并在旋转终点听到强拍”发生在最后一个动作峰值，保持机位直到“环形轨迹竖立在世界空间中成为发光篱笆，强拍让相邻竖线依次向外打开”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "SOURCE-PORTAL-STAR", "light_anchor_optics", "灯棒门户星芒",
        (
            "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-LIGHT-OPTICS-LUMINOUS-CORE",
            "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        ),
        (
            "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
            "FX-LIGHT-TRAILS-OPTICS-SOURCE-STAR",
            "FX-SPATIAL-PORTALS-MIRROR-MIRRORROTATE",
        ),
        ("realtime_light_trail", "world_anchor", "spatial_portal"),
        "灯棒姿态提供可控的发光核心，空间锚点固定轨迹，镜面门户把轨迹的终点变成可观察的另一侧",
        "灯棒拖尾不再只是跟随物体移动，而会在终点长成具有前后两面的发光入口",
        "预览以灯棒核心和粗粒度镜面边界先显示门户轮廓，移动端只保留最近一段拖尾",
        "录制后重算灯棒六自由度姿态、门户厚度和反射遮挡，补齐入口内外的光线连续性",
        "夜间手持灯棒绕过人物，最后把光线旋成一扇小型镜面门",
        (
        {
    "recipe_id": "RECIPE-SOURCE-PORTAL-STAR-V1",
    "name_zh": "灯棒门户星芒·星芒门把",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LUMINOUS-CORE",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-STAR",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORROTATE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR"
    ],
    "trigger_logic": "灯棒尖端在世界锚点处停留并完成一次顺时针旋转",
    "combined_effect": "灯棒拖出的圆弧收束成门把形星芒，旋转后镜面门户沿圆弧打开并露出反向光轨",
    "why_new": "发光核心的姿态和门户开合共享同一圆弧，入口因此看起来由灯棒亲手拧开",
    "preview_behavior": "预览以灯棒核心和粗粒度镜面边界先显示门户轮廓，移动端只保留最近一段拖尾。针对星芒门把，取景器先在“灯棒尖端在世界锚点处停留并完成一次顺时针旋转”发生前标出候选轨迹，确认后才显示“灯棒拖出的圆弧收束成门把形星芒，旋转后镜面门户沿圆弧打开并露出反向光轨”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重算灯棒六自由度姿态、门户厚度和反射遮挡，补齐入口内外的光线连续性。录后以“灯棒尖端在世界锚点处停留并完成一次顺时针旋转”的首帧为时间锚，重新计算星芒门把涉及的遮挡和深度，使“灯棒拖出的圆弧收束成门把形星芒，旋转后镜面门户沿圆弧打开并露出反向光轨”在原分辨率下保持连续；检测到门把圆弧不闭合时门户会闪断，系统退化为固定星芒而不生成穿越面时仅修补低置信度片段。",
    "risks": [
        "门把圆弧不闭合时门户会闪断，系统退化为固定星芒而不生成穿越面"
    ],
    "target_scenarios": [
        "夜间街区的墙面近景适合拍摄星芒门把：先让主体完成“灯棒尖端在世界锚点处停留并完成一次顺时针旋转”，随后缓慢移动手机观察“灯棒拖出的圆弧收束成门把形星芒，旋转后镜面门户沿圆弧打开并露出反向光轨”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SOURCE-PORTAL-STAR-V2",
    "name_zh": "灯棒门户星芒·侧向星门",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LUMINOUS-CORE",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-STAR",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORROTATE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST"
    ],
    "trigger_logic": "灯棒横向扫过主体侧面并在主体后方捕获稳定平面",
    "combined_effect": "拖尾在主体背后形成一扇侧开的星门，人物经过门前时光线被真实分割",
    "why_new": "拖尾的终点深度与门户朝向共同决定遮挡，光线因此有了主体背后的去向",
    "preview_behavior": "移动端预览从侧向星门的结果层反推触发：屏幕持续保留对象身份和最近历史，当“灯棒横向扫过主体侧面并在主体后方捕获稳定平面”成立时，把“拖尾在主体背后形成一扇侧开的星门，人物经过门前时光线被真实分割”分成进入、保持、退场三段显示。若出现单目深度前后关系反转会让门穿过人物，置信度不足时把门压回背景平面，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把侧向星门拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“灯棒横向扫过主体侧面并在主体后方捕获稳定平面”，再细化“拖尾在主体背后形成一扇侧开的星门，人物经过门前时光线被真实分割”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "单目深度前后关系反转会让门穿过人物，置信度不足时把门压回背景平面"
    ],
    "target_scenarios": [
        "在音乐节舞台前沿的横向跟拍使用侧向星门。镜头从未触发状态开始横向移动，人物或物体执行“灯棒横向扫过主体侧面并在主体后方捕获稳定平面”后继续穿过画面，以“拖尾在主体背后形成一扇侧开的星门，人物经过门前时光线被真实分割”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SOURCE-PORTAL-STAR-V3",
    "name_zh": "灯棒门户星芒·旋转回廊",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LUMINOUS-CORE",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-STAR",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORROTATE",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "用户连续画出两个同心圈且灯棒姿态发生半圈翻转",
    "combined_effect": "两个光圈变成可旋转的短回廊，镜头移动时回廊内壁呈现不同角度的星芒切片",
    "why_new": "同心轨迹被解释为入口深度而非两条独立光环，姿态翻转驱动空间方向切换",
    "preview_behavior": "拍摄者先看到旋转回廊所需的对象边界、方向箭头和时间门；“用户连续画出两个同心圈且灯棒姿态发生半圈翻转”被连续确认后，预览按由近到远的层次展开“两个光圈变成可旋转的短回廊，镜头移动时回廊内壁呈现不同角度的星芒切片”。灯棒拖尾不再只是跟随物体移动，而会在终点长成具有前后两面的发光入口，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验旋转回廊的身份链与事件顺序，再按灯棒姿态提供可控的发光核心，空间锚点固定轨迹，镜面门户把轨迹的终点变成可观察的另一侧重建组件关系。“两个光圈变成可旋转的短回廊，镜头移动时回廊内壁呈现不同角度的星芒切片”使用完整历史窗口重新渲染，而“用户连续画出两个同心圈且灯棒姿态发生半圈翻转”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "同心圈半径差过小会使回廊塌缩，自动保留外圈并提示重新画内圈"
    ],
    "target_scenarios": [
        "把旋转回廊安排在室内展馆的环绕装置镜头：固定主体身份后执行“用户连续画出两个同心圈且灯棒姿态发生半圈翻转”，拍摄者绕触发点改变观察角度，用“两个光圈变成可旋转的短回廊，镜头移动时回廊内壁呈现不同角度的星芒切片”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SOURCE-PORTAL-STAR-V4",
    "name_zh": "灯棒门户星芒·追光裂口",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LUMINOUS-CORE",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-STAR",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORROTATE",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "灯棒快速指向画面外并在指向方向出现镜面高光",
    "combined_effect": "一条追光拖尾划开画面边缘形成裂口，裂口内短暂显示灯棒刚才经过的空间",
    "why_new": "目标指向、发光拖尾和门户采样形成回看式入口，不是简单的边缘擦除",
    "preview_behavior": "为预览追光裂口，系统只更新与“灯棒快速指向画面外并在指向方向出现镜面高光”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“一条追光拖尾划开画面边缘形成裂口，裂口内短暂显示灯棒刚才经过的空间”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "追光裂口的后处理从失败点开始：针对“镜面高光误检会误开裂口，需连续两帧确认方向后才释放入口”复核掩码、锚点或时间戳，通过后才将“一条追光拖尾划开画面边缘形成裂口，裂口内短暂显示灯棒刚才经过的空间”提升到成片质量。触发逻辑“灯棒快速指向画面外并在指向方向出现镜面高光”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "镜面高光误检会误开裂口，需连续两帧确认方向后才释放入口"
    ],
    "target_scenarios": [
        "天台灯光表演的一镜到底可用追光裂口组织一段连续互动。参与者先保持关系稳定，再完成“灯棒快速指向画面外并在指向方向出现镜面高光”；镜头不切断，直到“一条追光拖尾划开画面边缘形成裂口，裂口内短暂显示灯棒刚才经过的空间”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SOURCE-PORTAL-STAR-V5",
    "name_zh": "灯棒门户星芒·星尘回收",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-LIGHT-OPTICS-LUMINOUS-CORE",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-STAR",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORROTATE",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "灯棒回到最初锚点且用户反向挥动一次",
    "combined_effect": "散落在场景中的星芒沿原路径逆向回收，最后压缩为一个可旋转的微型门户",
    "why_new": "回收路径同时依赖物体历史和门户状态，结束动作改变了拖尾的时间方向",
    "preview_behavior": "星尘回收的取景反馈以结束状态为目标：预览先保留真实动作，在“灯棒回到最初锚点且用户反向挥动一次”完成时快速呈现“散落在场景中的星芒沿原路径逆向回收，最后压缩为一个可旋转的微型门户”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留星尘回收的完整生命周期。系统逆向检查“散落在场景中的星芒沿原路径逆向回收，最后压缩为一个可旋转的微型门户”是否回到稳定终态，再从“灯棒回到最初锚点且用户反向挥动一次”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "回收期间丢失灯棒会留下残留星尘，系统冻结终点并在短时衰减"
    ],
    "target_scenarios": [
        "以灯棒与人物同框的收束镜头作为星尘回收的结尾段落：让“灯棒回到最初锚点且用户反向挥动一次”发生在最后一个动作峰值，保持机位直到“散落在场景中的星芒沿原路径逆向回收，最后压缩为一个可旋转的微型门户”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "BODY-LIGHT-POSE", "light_anchor_optics", "姿态轮廓光绘",
        (
            "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
            "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
            "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
            "ATOM-TEMPORAL-STATE-MOTION-HISTORY",
        ),
        (
            "FX-LIGHT-TRAILS-OPTICS-BODY-MOTION",
            "FX-LIGHT-TRAILS-OPTICS-BODY-JOINT",
            "FX-LIGHT-TRAILS-OPTICS-BODY-POSEFREEZE",
        ),
        ("realtime_light_trail", "body_pose", "time"),
        "骨骼关节决定笔画骨架，人体轮廓掩码负责遮挡，运动历史把连续姿态压缩成可读的光绘构图",
        "身体动作会留下带关节语义的光绘雕塑，停止动作时雕塑仍保持最后姿态而不是变成普通残影",
        "预览只保留关节线和轮廓粗边，动作峰值时短暂提高历史样本密度以显示姿态变化",
        "录制后按完整骨骼历史重绘关节连接、轮廓遮挡和姿态峰值，并允许回看每个光绘层",
        "舞蹈录像中让一次转身逐渐写成一座会呼吸的身体光雕",
        (
        {
    "recipe_id": "RECIPE-BODY-LIGHT-POSE-V1",
    "name_zh": "姿态轮廓光绘·舞步骨架",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-TEMPORAL-STATE-MOTION-HISTORY",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-BODY-MOTION",
        "FX-LIGHT-TRAILS-OPTICS-BODY-JOINT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-POSEFREEZE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR"
    ],
    "trigger_logic": "全身进入画面并连续完成三次明显重心转移",
    "combined_effect": "每次重心转移留下一个颜色不同的骨架姿态，三层姿态在脚底对齐成一段舞步谱",
    "why_new": "重心事件把运动历史切成可读的姿态段，轮廓掩码又保留了身体前后关系",
    "preview_behavior": "预览只保留关节线和轮廓粗边，动作峰值时短暂提高历史样本密度以显示姿态变化。针对舞步骨架，取景器先在“全身进入画面并连续完成三次明显重心转移”发生前标出候选轨迹，确认后才显示“每次重心转移留下一个颜色不同的骨架姿态，三层姿态在脚底对齐成一段舞步谱”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后按完整骨骼历史重绘关节连接、轮廓遮挡和姿态峰值，并允许回看每个光绘层。录后以“全身进入画面并连续完成三次明显重心转移”的首帧为时间锚，重新计算舞步骨架涉及的遮挡和深度，使“每次重心转移留下一个颜色不同的骨架姿态，三层姿态在脚底对齐成一段舞步谱”在原分辨率下保持连续；检测到脚部被遮挡时姿态层会错位，系统减弱脚端光线并保持躯干骨架时仅修补低置信度片段。",
    "risks": [
        "脚部被遮挡时姿态层会错位，系统减弱脚端光线并保持躯干骨架"
    ],
    "target_scenarios": [
        "夜间街区的墙面近景适合拍摄舞步骨架：先让主体完成“全身进入画面并连续完成三次明显重心转移”，随后缓慢移动手机观察“每次重心转移留下一个颜色不同的骨架姿态，三层姿态在脚底对齐成一段舞步谱”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-BODY-LIGHT-POSE-V2",
    "name_zh": "姿态轮廓光绘·回身光扇",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-TEMPORAL-STATE-MOTION-HISTORY",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-BODY-MOTION",
        "FX-LIGHT-TRAILS-OPTICS-BODY-JOINT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-POSEFREEZE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST"
    ],
    "trigger_logic": "身体从侧面转向镜头且肩线经过最大旋转角",
    "combined_effect": "肩线和手臂光绘展开成扇面，原姿态按时间顺序排列在扇骨上并在转身后收拢",
    "why_new": "关节路径与轮廓峰值共同构成可收拢的扇面，动作结果取决于转身阶段而非场景",
    "preview_behavior": "移动端预览从回身光扇的结果层反推触发：屏幕持续保留对象身份和最近历史，当“身体从侧面转向镜头且肩线经过最大旋转角”成立时，把“肩线和手臂光绘展开成扇面，原姿态按时间顺序排列在扇骨上并在转身后收拢”分成进入、保持、退场三段显示。若出现侧脸和手臂交叉会造成扇骨串线，置信度下降时只绘制躯干轮廓，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把回身光扇拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“身体从侧面转向镜头且肩线经过最大旋转角”，再细化“肩线和手臂光绘展开成扇面，原姿态按时间顺序排列在扇骨上并在转身后收拢”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "侧脸和手臂交叉会造成扇骨串线，置信度下降时只绘制躯干轮廓"
    ],
    "target_scenarios": [
        "在音乐节舞台前沿的横向跟拍使用回身光扇。镜头从未触发状态开始横向移动，人物或物体执行“身体从侧面转向镜头且肩线经过最大旋转角”后继续穿过画面，以“肩线和手臂光绘展开成扇面，原姿态按时间顺序排列在扇骨上并在转身后收拢”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-BODY-LIGHT-POSE-V3",
    "name_zh": "姿态轮廓光绘·定格光像",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-TEMPORAL-STATE-MOTION-HISTORY",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-BODY-MOTION",
        "FX-LIGHT-TRAILS-OPTICS-BODY-JOINT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-POSEFREEZE",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "用户保持一个高举双手姿态超过设定停留时间",
    "combined_effect": "动作历史收束到当前姿态形成发光人像，恢复移动后人像沿手臂方向裂成光线",
    "why_new": "姿态冻结与动作累积共享同一骨架，静止和运动因此成为同一雕塑的两种状态",
    "preview_behavior": "拍摄者先看到定格光像所需的对象边界、方向箭头和时间门；“用户保持一个高举双手姿态超过设定停留时间”被连续确认后，预览按由近到远的层次展开“动作历史收束到当前姿态形成发光人像，恢复移动后人像沿手臂方向裂成光线”。身体动作会留下带关节语义的光绘雕塑，停止动作时雕塑仍保持最后姿态而不是变成普通残影，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验定格光像的身份链与事件顺序，再按骨骼关节决定笔画骨架，人体轮廓掩码负责遮挡，运动历史把连续姿态压缩成可读的光绘构图重建组件关系。“动作历史收束到当前姿态形成发光人像，恢复移动后人像沿手臂方向裂成光线”使用完整历史窗口重新渲染，而“用户保持一个高举双手姿态超过设定停留时间”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "保持时间不足会生成半成品人像，系统延长上一姿态的淡出时间隐藏断点"
    ],
    "target_scenarios": [
        "把定格光像安排在室内展馆的环绕装置镜头：固定主体身份后执行“用户保持一个高举双手姿态超过设定停留时间”，拍摄者绕触发点改变观察角度，用“动作历史收束到当前姿态形成发光人像，恢复移动后人像沿手臂方向裂成光线”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-BODY-LIGHT-POSE-V4",
    "name_zh": "姿态轮廓光绘·关节分谱",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-TEMPORAL-STATE-MOTION-HISTORY",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-BODY-MOTION",
        "FX-LIGHT-TRAILS-OPTICS-BODY-JOINT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-POSEFREEZE",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "手腕、膝盖和头部同时改变速度并跨过动作阶段阈值",
    "combined_effect": "不同关节留下不同长度和色相的光谱线，身体轮廓仍以单色框住整套关节关系",
    "why_new": "局部速度改变的是关节线的时间长度而不是整张画面颜色，能直接读出动作层级",
    "preview_behavior": "为预览关节分谱，系统只更新与“手腕、膝盖和头部同时改变速度并跨过动作阶段阈值”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“不同关节留下不同长度和色相的光谱线，身体轮廓仍以单色框住整套关节关系”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "关节分谱的后处理从失败点开始：针对“快速动作可能造成颜色跳变，使用阶段滞回保持相邻帧色相连续”复核掩码、锚点或时间戳，通过后才将“不同关节留下不同长度和色相的光谱线，身体轮廓仍以单色框住整套关节关系”提升到成片质量。触发逻辑“手腕、膝盖和头部同时改变速度并跨过动作阶段阈值”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "快速动作可能造成颜色跳变，使用阶段滞回保持相邻帧色相连续"
    ],
    "target_scenarios": [
        "天台灯光表演的一镜到底可用关节分谱组织一段连续互动。参与者先保持关系稳定，再完成“手腕、膝盖和头部同时改变速度并跨过动作阶段阈值”；镜头不切断，直到“不同关节留下不同长度和色相的光谱线，身体轮廓仍以单色框住整套关节关系”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-BODY-LIGHT-POSE-V5",
    "name_zh": "姿态轮廓光绘·双臂回声门",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-TEMPORAL-STATE-MOTION-HISTORY",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-LIGHT-TRAILS-OPTICS-BODY-MOTION",
        "FX-LIGHT-TRAILS-OPTICS-BODY-JOINT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-POSEFREEZE",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "双臂张开后交叉，且身体轮廓与上一姿态有稳定重合",
    "combined_effect": "两次手臂姿态之间生成一扇发光回声门，胸口轮廓作为门轴并保留人物穿过的遮挡",
    "why_new": "姿态差分被转译为空间门的开合宽度，回声不是复制人物而是连接两个姿态状态",
    "preview_behavior": "双臂回声门的取景反馈以结束状态为目标：预览先保留真实动作，在“双臂张开后交叉，且身体轮廓与上一姿态有稳定重合”完成时快速呈现“两次手臂姿态之间生成一扇发光回声门，胸口轮廓作为门轴并保留人物穿过的遮挡”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留双臂回声门的完整生命周期。系统逆向检查“两次手臂姿态之间生成一扇发光回声门，胸口轮廓作为门轴并保留人物穿过的遮挡”是否回到稳定终态，再从“双臂张开后交叉，且身体轮廓与上一姿态有稳定重合”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "双臂交叉会让门轴漂移，系统固定胸口锚点并裁掉低可信门翼"
    ],
    "target_scenarios": [
        "以灯棒与人物同框的收束镜头作为双臂回声门的结尾段落：让“双臂张开后交叉，且身体轮廓与上一姿态有稳定重合”发生在最后一个动作峰值，保持机位直到“两次手臂姿态之间生成一扇发光回声门，胸口轮廓作为门轴并保留人物穿过的遮挡”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "LIGHT-GAZE-MATERIAL", "light_anchor_optics", "视线霓虹材质光轨",
        (
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
            "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
            "ATOM-MATERIAL-APPEARANCE-NEON",
        ),
        (
            "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
            "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHCOLOR",
            "FX-WORLD-STYLE-NEON-NEONGAZE",
        ),
        ("gaze", "realtime_light_trail", "material"),
        "视线向量选定目标，虹膜关键点稳定眼神光中心，霓虹材质把扫视历史染成目标表面的发光纹理",
        "眼神扫过的目标会留下贴合其表面的霓虹纹理，眼神光颜色和纹理方向随视线转移而变化",
        "预览只显示视线射线、粗粒度目标掩码和短霓虹尾迹，注视停留时才提高材质采样",
        "录制后细化目标表面、虹膜高光和视线转移之间的时序关系，修复快速扫视留下的纹理断口",
        "人像扫过街边招牌时，让被注视的字逐个亮起并保留视线经过的痕迹",
        (
        {
    "recipe_id": "RECIPE-LIGHT-GAZE-MATERIAL-V1",
    "name_zh": "视线霓虹材质光轨·招牌扫亮",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-MATERIAL-APPEARANCE-NEON",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHCOLOR",
        "FX-WORLD-STYLE-NEON-NEONGAZE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR"
    ],
    "trigger_logic": "视线从一个招牌字移动到相邻字并在每字停留半秒",
    "combined_effect": "每个被注视的字先亮起眼神光色，再把一条细霓虹纹理留在字面上形成连续阅读轨迹",
    "why_new": "注视停留决定亮点、扫视方向决定纹理流向，文字因此记录了眼神的阅读顺序",
    "preview_behavior": "预览只显示视线射线、粗粒度目标掩码和短霓虹尾迹，注视停留时才提高材质采样。针对招牌扫亮，取景器先在“视线从一个招牌字移动到相邻字并在每字停留半秒”发生前标出候选轨迹，确认后才显示“每个被注视的字先亮起眼神光色，再把一条细霓虹纹理留在字面上形成连续阅读轨迹”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化目标表面、虹膜高光和视线转移之间的时序关系，修复快速扫视留下的纹理断口。录后以“视线从一个招牌字移动到相邻字并在每字停留半秒”的首帧为时间锚，重新计算招牌扫亮涉及的遮挡和深度，使“每个被注视的字先亮起眼神光色，再把一条细霓虹纹理留在字面上形成连续阅读轨迹”在原分辨率下保持连续；检测到反光招牌会产生错误目标，系统只在字符轮廓和视线交点同时稳定时着色时仅修补低置信度片段。",
    "risks": [
        "反光招牌会产生错误目标，系统只在字符轮廓和视线交点同时稳定时着色"
    ],
    "target_scenarios": [
        "夜间街区的墙面近景适合拍摄招牌扫亮：先让主体完成“视线从一个招牌字移动到相邻字并在每字停留半秒”，随后缓慢移动手机观察“每个被注视的字先亮起眼神光色，再把一条细霓虹纹理留在字面上形成连续阅读轨迹”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-LIGHT-GAZE-MATERIAL-V2",
    "name_zh": "视线霓虹材质光轨·虹膜切色",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-MATERIAL-APPEARANCE-NEON",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHCOLOR",
        "FX-WORLD-STYLE-NEON-NEONGAZE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST"
    ],
    "trigger_logic": "用户向左或向右快速扫视并眨眼确认方向",
    "combined_effect": "霓虹材质从虹膜中心向视线方向切换色相，扫视经过的对象保留上一色相的薄边",
    "why_new": "眨眼把连续视线变成颜色切换事件，眼神光和环境目标共同参与颜色分层",
    "preview_behavior": "移动端预览从虹膜切色的结果层反推触发：屏幕持续保留对象身份和最近历史，当“用户向左或向右快速扫视并眨眼确认方向”成立时，把“霓虹材质从虹膜中心向视线方向切换色相，扫视经过的对象保留上一色相的薄边”分成进入、保持、退场三段显示。若出现眨眼检测漏失会让颜色拖长，系统按视线速度限制色带长度，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把虹膜切色拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“用户向左或向右快速扫视并眨眼确认方向”，再细化“霓虹材质从虹膜中心向视线方向切换色相，扫视经过的对象保留上一色相的薄边”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "眨眼检测漏失会让颜色拖长，系统按视线速度限制色带长度"
    ],
    "target_scenarios": [
        "在音乐节舞台前沿的横向跟拍使用虹膜切色。镜头从未触发状态开始横向移动，人物或物体执行“用户向左或向右快速扫视并眨眼确认方向”后继续穿过画面，以“霓虹材质从虹膜中心向视线方向切换色相，扫视经过的对象保留上一色相的薄边”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-LIGHT-GAZE-MATERIAL-V3",
    "name_zh": "视线霓虹材质光轨·目标连线",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-MATERIAL-APPEARANCE-NEON",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHCOLOR",
        "FX-WORLD-STYLE-NEON-NEONGAZE",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "视线依次锁定三个不同深度的物体",
    "combined_effect": "三个物体表面出现不同亮度的霓虹节点，节点之间以视线经过的方向连成折线",
    "why_new": "目标深度参与连线排序，视线轨迹因而成为穿过场景的材质路径而不是屏幕画线",
    "preview_behavior": "拍摄者先看到目标连线所需的对象边界、方向箭头和时间门；“视线依次锁定三个不同深度的物体”被连续确认后，预览按由近到远的层次展开“三个物体表面出现不同亮度的霓虹节点，节点之间以视线经过的方向连成折线”。眼神扫过的目标会留下贴合其表面的霓虹纹理，眼神光颜色和纹理方向随视线转移而变化，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验目标连线的身份链与事件顺序，再按视线向量选定目标，虹膜关键点稳定眼神光中心，霓虹材质把扫视历史染成目标表面的发光纹理重建组件关系。“三个物体表面出现不同亮度的霓虹节点，节点之间以视线经过的方向连成折线”使用完整历史窗口重新渲染，而“视线依次锁定三个不同深度的物体”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "深度排序抖动会使折线翻面，低置信度时只保留节点不连线"
    ],
    "target_scenarios": [
        "把目标连线安排在室内展馆的环绕装置镜头：固定主体身份后执行“视线依次锁定三个不同深度的物体”，拍摄者绕触发点改变观察角度，用“三个物体表面出现不同亮度的霓虹节点，节点之间以视线经过的方向连成折线”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-LIGHT-GAZE-MATERIAL-V4",
    "name_zh": "视线霓虹材质光轨·眼神涟漪",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-MATERIAL-APPEARANCE-NEON",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHCOLOR",
        "FX-WORLD-STYLE-NEON-NEONGAZE",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "视线停留在一个材质边缘并发生一次轻微回看",
    "combined_effect": "眼神光从虹膜扩散到物体边缘形成一圈霓虹涟漪，回看会让旧涟漪与新涟漪相遇并合并",
    "why_new": "回看事件改变涟漪的传播方向，使视线历史能够在物体表面发生交互",
    "preview_behavior": "为预览眼神涟漪，系统只更新与“视线停留在一个材质边缘并发生一次轻微回看”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“眼神光从虹膜扩散到物体边缘形成一圈霓虹涟漪，回看会让旧涟漪与新涟漪相遇并合并”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "眼神涟漪的后处理从失败点开始：针对“玻璃边缘会重复触发涟漪，系统合并同一物体的近邻事件”复核掩码、锚点或时间戳，通过后才将“眼神光从虹膜扩散到物体边缘形成一圈霓虹涟漪，回看会让旧涟漪与新涟漪相遇并合并”提升到成片质量。触发逻辑“视线停留在一个材质边缘并发生一次轻微回看”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "玻璃边缘会重复触发涟漪，系统合并同一物体的近邻事件"
    ],
    "target_scenarios": [
        "天台灯光表演的一镜到底可用眼神涟漪组织一段连续互动。参与者先保持关系稳定，再完成“视线停留在一个材质边缘并发生一次轻微回看”；镜头不切断，直到“眼神光从虹膜扩散到物体边缘形成一圈霓虹涟漪，回看会让旧涟漪与新涟漪相遇并合并”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-LIGHT-GAZE-MATERIAL-V5",
    "name_zh": "视线霓虹材质光轨·视线印章",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-MATERIAL-APPEARANCE-NEON",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHCOLOR",
        "FX-WORLD-STYLE-NEON-NEONGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "用户凝视目标两秒后移开并转向镜头",
    "combined_effect": "目标留下一个由眼神光形状组成的霓虹印章，转向镜头时印章短暂映入瞳孔高光",
    "why_new": "目标注视和镜头对视形成首尾闭环，把环境材质反馈回人脸而非只点亮目标",
    "preview_behavior": "视线印章的取景反馈以结束状态为目标：预览先保留真实动作，在“用户凝视目标两秒后移开并转向镜头”完成时快速呈现“目标留下一个由眼神光形状组成的霓虹印章，转向镜头时印章短暂映入瞳孔高光”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留视线印章的完整生命周期。系统逆向检查“目标留下一个由眼神光形状组成的霓虹印章，转向镜头时印章短暂映入瞳孔高光”是否回到稳定终态，再从“用户凝视目标两秒后移开并转向镜头”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "正面高光过强会遮住瞳孔，系统限制印章在眼白区域的亮度"
    ],
    "target_scenarios": [
        "以灯棒与人物同框的收束镜头作为视线印章的结尾段落：让“用户凝视目标两秒后移开并转向镜头”发生在最后一个动作峰值，保持机位直到“目标留下一个由眼神光形状组成的霓虹印章，转向镜头时印章短暂映入瞳孔高光”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "GAZE-CATCH-DIALOGUE", "gaze_expression", "对话视线眼神光接力",
        (
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
            "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        ),
        (
            "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE",
            "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
            "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHDOUBLE",
        ),
        ("gaze", "expression", "multi_person"),
        "镜头对视矫正提供自然视线基准，对话对象识别选择接收者，双眼眼神光把发话者与接收者连成可见接力",
        "人物视线会自然落向实际对话对象，同时眼神光像光核一样在说话者和听者之间传递",
        "预览先用人脸框和粗略视线向量确定对话边，确认说话者后才渲染双眼高光",
        "录制后重估每个说话片段的目标脸、瞳孔高光形状和视线转移，修复多人交叉遮挡",
        "双人访谈中让每次发言都带着一颗眼神光在两人之间移动",
        (
        {
    "recipe_id": "RECIPE-GAZE-CATCH-DIALOGUE-V1",
    "name_zh": "对话视线眼神光接力·问答光核",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-BLINK"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE",
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHDOUBLE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK"
    ],
    "trigger_logic": "一个人开口且视线稳定落在另一人的脸部区域",
    "combined_effect": "说话者的眼神光凝成光核并沿对话边滑到听者瞳孔，听者回看时光核扩大",
    "why_new": "说话事件决定光核出发点，视线矫正让光核终点贴近真实接收者，形成对话节奏",
    "preview_behavior": "预览先用人脸框和粗略视线向量确定对话边，确认说话者后才渲染双眼高光。针对问答光核，取景器先在“一个人开口且视线稳定落在另一人的脸部区域”发生前标出候选轨迹，确认后才显示“说话者的眼神光凝成光核并沿对话边滑到听者瞳孔，听者回看时光核扩大”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重估每个说话片段的目标脸、瞳孔高光形状和视线转移，修复多人交叉遮挡。录后以“一个人开口且视线稳定落在另一人的脸部区域”的首帧为时间锚，重新计算问答光核涉及的遮挡和深度，使“说话者的眼神光凝成光核并沿对话边滑到听者瞳孔，听者回看时光核扩大”在原分辨率下保持连续；检测到多人同时说话会产生竞争光核，系统按声源置信度保留主光核时仅修补低置信度片段。",
    "risks": [
        "多人同时说话会产生竞争光核，系统按声源置信度保留主光核"
    ],
    "target_scenarios": [
        "双人访谈的肩上机位适合拍摄问答光核：先让主体完成“一个人开口且视线稳定落在另一人的脸部区域”，随后缓慢移动手机观察“说话者的眼神光凝成光核并沿对话边滑到听者瞳孔，听者回看时光核扩大”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-CATCH-DIALOGUE-V2",
    "name_zh": "对话视线眼神光接力·沉默接话",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE",
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHDOUBLE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWBLINK"
    ],
    "trigger_logic": "前一说话者停声后，另一人先抬眼再开始说话",
    "combined_effect": "光核停在两人之间的对话边，接话者抬眼后把它吸入自己的眼神光并继续向镜头发亮",
    "why_new": "停声、抬眼和开口被组合为交接协议，沉默也因此成为可见的等待状态",
    "preview_behavior": "移动端预览从沉默接话的结果层反推触发：屏幕持续保留对象身份和最近历史，当“前一说话者停声后，另一人先抬眼再开始说话”成立时，把“光核停在两人之间的对话边，接话者抬眼后把它吸入自己的眼神光并继续向镜头发亮”分成进入、保持、退场三段显示。若出现抬眼顺序不明确会让光核悬停，系统延长中间态并降低亮度，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把沉默接话拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“前一说话者停声后，另一人先抬眼再开始说话”，再细化“光核停在两人之间的对话边，接话者抬眼后把它吸入自己的眼神光并继续向镜头发亮”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "抬眼顺序不明确会让光核悬停，系统延长中间态并降低亮度"
    ],
    "target_scenarios": [
        "在自拍视频中的镜头到对象切换使用沉默接话。镜头从未触发状态开始横向移动，人物或物体执行“前一说话者停声后，另一人先抬眼再开始说话”后继续穿过画面，以“光核停在两人之间的对话边，接话者抬眼后把它吸入自己的眼神光并继续向镜头发亮”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-CATCH-DIALOGUE-V3",
    "name_zh": "对话视线眼神光接力·三人轮询",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE",
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHDOUBLE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-CONFIRM"
    ],
    "trigger_logic": "三张脸依次成为说话者且视线目标形成闭合关系",
    "combined_effect": "眼神光按关系图绕三人轮转，每次换人时保留一条短弧线显示上一条对话边",
    "why_new": "多人关系图决定光核的路由，视线矫正负责显示谁看谁，结果不是简单多人高光",
    "preview_behavior": "拍摄者先看到三人轮询所需的对象边界、方向箭头和时间门；“三张脸依次成为说话者且视线目标形成闭合关系”被连续确认后，预览按由近到远的层次展开“眼神光按关系图绕三人轮转，每次换人时保留一条短弧线显示上一条对话边”。人物视线会自然落向实际对话对象，同时眼神光像光核一样在说话者和听者之间传递，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验三人轮询的身份链与事件顺序，再按镜头对视矫正提供自然视线基准，对话对象识别选择接收者，双眼眼神光把发话者与接收者连成可见接力重建组件关系。“眼神光按关系图绕三人轮转，每次换人时保留一条短弧线显示上一条对话边”使用完整历史窗口重新渲染，而“三张脸依次成为说话者且视线目标形成闭合关系”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "脸部出画会断开闭环，系统把光核降级为最近两人之间的直线"
    ],
    "target_scenarios": [
        "把三人轮询安排在桌面产品口播的中近景：固定主体身份后执行“三张脸依次成为说话者且视线目标形成闭合关系”，拍摄者绕触发点改变观察角度，用“眼神光按关系图绕三人轮转，每次换人时保留一条短弧线显示上一条对话边”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-CATCH-DIALOGUE-V4",
    "name_zh": "对话视线眼神光接力·镜头旁听",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE",
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHDOUBLE",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH"
    ],
    "trigger_logic": "说话者看向对话对象后短暂看镜头",
    "combined_effect": "光核先到听者再折返镜头旁，形成一条可见的旁听弧线，回到听者时高光恢复原形",
    "why_new": "镜头视线被当作关系图中的特殊节点，让观众进入对话网络而非只被校正目光",
    "preview_behavior": "为预览镜头旁听，系统只更新与“说话者看向对话对象后短暂看镜头”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“光核先到听者再折返镜头旁，形成一条可见的旁听弧线，回到听者时高光恢复原形”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "镜头旁听的后处理从失败点开始：针对“镜头反光可能误判为镜头节点，需连续视线停留确认”复核掩码、锚点或时间戳，通过后才将“光核先到听者再折返镜头旁，形成一条可见的旁听弧线，回到听者时高光恢复原形”提升到成片质量。触发逻辑“说话者看向对话对象后短暂看镜头”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "镜头反光可能误判为镜头节点，需连续视线停留确认"
    ],
    "target_scenarios": [
        "剧情对视的正反打连续镜头可用镜头旁听组织一段连续互动。参与者先保持关系稳定，再完成“说话者看向对话对象后短暂看镜头”；镜头不切断，直到“光核先到听者再折返镜头旁，形成一条可见的旁听弧线，回到听者时高光恢复原形”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-CATCH-DIALOGUE-V5",
    "name_zh": "对话视线眼神光接力·情绪转交",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE",
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHDOUBLE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP"
    ],
    "trigger_logic": "说话者表情强度上升且视线完成一次目标切换",
    "combined_effect": "光核颜色随表情强度改变，并在目标切换时把颜色和亮度一并交给下一人的眼神光",
    "why_new": "表情改变光核能量，视线改变它的路由，两个维度同时影响交互结果",
    "preview_behavior": "情绪转交的取景反馈以结束状态为目标：预览先保留真实动作，在“说话者表情强度上升且视线完成一次目标切换”完成时快速呈现“光核颜色随表情强度改变，并在目标切换时把颜色和亮度一并交给下一人的眼神光”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留情绪转交的完整生命周期。系统逆向检查“光核颜色随表情强度改变，并在目标切换时把颜色和亮度一并交给下一人的眼神光”是否回到稳定终态，再从“说话者表情强度上升且视线完成一次目标切换”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "表情识别过敏会造成颜色闪变，使用短时平滑并保留上一色相"
    ],
    "target_scenarios": [
        "以多人合拍结束前的视线交接作为情绪转交的结尾段落：让“说话者表情强度上升且视线完成一次目标切换”发生在最后一个动作峰值，保持机位直到“光核颜色随表情强度改变，并在目标切换时把颜色和亮度一并交给下一人的眼神光”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "GAZE-EXPRESSION-ECHO", "gaze_expression", "表情视线回声",
        (
            "ATOM-SEGMENTATION-MASKS-FACE-REGION",
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-INTERACTION-TRIGGERS-EXPRESSION",
            "ATOM-CLONING-ECHOES-EXPRESSION-ECHO",
        ),
        (
            "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWPULSE",
            "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
            "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        ),
        ("gaze", "expression", "time"),
        "面部掩码限定表情回声边界，视线选择回声落点，表情强度控制脉冲幅度和回声的传播距离",
        "一个表情会沿视线指向在画面中留下可追踪的情绪回声，回声位置和强度都由脸部交互决定",
        "预览使用脸部区域和短时表情历史，只有超过强度门限的表情才生成一层回声",
        "录制后重建表情峰值、视线方向和回声衰减，让回声边缘不穿出脸部或目标物体",
        "自拍时用一个挑眉或微笑把情绪投向画面中的不同位置",
        (
        {
    "recipe_id": "RECIPE-GAZE-EXPRESSION-ECHO-V1",
    "name_zh": "表情视线回声·挑眉点亮",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION",
        "ATOM-CLONING-ECHOES-EXPRESSION-ECHO",
        "ATOM-INTERACTION-TRIGGERS-BLINK"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWPULSE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK"
    ],
    "trigger_logic": "用户挑眉并把视线停在一个背景物体上",
    "combined_effect": "眉眼区域产生一圈脉冲，脉冲沿视线到达背景物体并留下同形小回声",
    "why_new": "表情峰值决定发射能量，视线决定落点，脸部和环境因此共享同一表情事件",
    "preview_behavior": "预览使用脸部区域和短时表情历史，只有超过强度门限的表情才生成一层回声。针对挑眉点亮，取景器先在“用户挑眉并把视线停在一个背景物体上”发生前标出候选轨迹，确认后才显示“眉眼区域产生一圈脉冲，脉冲沿视线到达背景物体并留下同形小回声”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建表情峰值、视线方向和回声衰减，让回声边缘不穿出脸部或目标物体。录后以“用户挑眉并把视线停在一个背景物体上”的首帧为时间锚，重新计算挑眉点亮涉及的遮挡和深度，使“眉眼区域产生一圈脉冲，脉冲沿视线到达背景物体并留下同形小回声”在原分辨率下保持连续；检测到背景物体分割不稳会让回声漂浮，系统将其限制在最近可信平面时仅修补低置信度片段。",
    "risks": [
        "背景物体分割不稳会让回声漂浮，系统将其限制在最近可信平面"
    ],
    "target_scenarios": [
        "双人访谈的肩上机位适合拍摄挑眉点亮：先让主体完成“用户挑眉并把视线停在一个背景物体上”，随后缓慢移动手机观察“眉眼区域产生一圈脉冲，脉冲沿视线到达背景物体并留下同形小回声”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-EXPRESSION-ECHO-V2",
    "name_zh": "表情视线回声·笑意扩散",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION",
        "ATOM-CLONING-ECHOES-EXPRESSION-ECHO",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWPULSE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWBLINK"
    ],
    "trigger_logic": "微笑强度连续上升且视线从镜头转向侧方",
    "combined_effect": "笑意先在脸部边缘闪烁，再沿侧方视线拉出三层逐渐稀释的表情回声",
    "why_new": "连续表情曲线控制层数，视线转向控制扩散方向，不是固定的表情贴纸",
    "preview_behavior": "移动端预览从笑意扩散的结果层反推触发：屏幕持续保留对象身份和最近历史，当“微笑强度连续上升且视线从镜头转向侧方”成立时，把“笑意先在脸部边缘闪烁，再沿侧方视线拉出三层逐渐稀释的表情回声”分成进入、保持、退场三段显示。若出现笑容被口罩遮挡时层数下降，保留眼部微笑信号，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把笑意扩散拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“微笑强度连续上升且视线从镜头转向侧方”，再细化“笑意先在脸部边缘闪烁，再沿侧方视线拉出三层逐渐稀释的表情回声”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "笑容被口罩遮挡时层数下降，保留眼部微笑信号"
    ],
    "target_scenarios": [
        "在自拍视频中的镜头到对象切换使用笑意扩散。镜头从未触发状态开始横向移动，人物或物体执行“微笑强度连续上升且视线从镜头转向侧方”后继续穿过画面，以“笑意先在脸部边缘闪烁，再沿侧方视线拉出三层逐渐稀释的表情回声”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-EXPRESSION-ECHO-V3",
    "name_zh": "表情视线回声·惊讶反射",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION",
        "ATOM-CLONING-ECHOES-EXPRESSION-ECHO",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWPULSE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-FACE-GAZE-EXPRESSION-SELECT-CONFIRM"
    ],
    "trigger_logic": "嘴型张开达到峰值并快速回看镜头",
    "combined_effect": "惊讶峰值在目标区域形成一次向外弹开的脸部轮廓，回看镜头后轮廓反弹回自拍者",
    "why_new": "同一表情在目标和镜头两个节点间往返，回看动作改变了回声的时间方向",
    "preview_behavior": "拍摄者先看到惊讶反射所需的对象边界、方向箭头和时间门；“嘴型张开达到峰值并快速回看镜头”被连续确认后，预览按由近到远的层次展开“惊讶峰值在目标区域形成一次向外弹开的脸部轮廓，回看镜头后轮廓反弹回自拍者”。一个表情会沿视线指向在画面中留下可追踪的情绪回声，回声位置和强度都由脸部交互决定，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验惊讶反射的身份链与事件顺序，再按面部掩码限定表情回声边界，视线选择回声落点，表情强度控制脉冲幅度和回声的传播距离重建组件关系。“惊讶峰值在目标区域形成一次向外弹开的脸部轮廓，回看镜头后轮廓反弹回自拍者”使用完整历史窗口重新渲染，而“嘴型张开达到峰值并快速回看镜头”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "回看过快会导致轮廓双影，系统合并相邻峰值"
    ],
    "target_scenarios": [
        "把惊讶反射安排在桌面产品口播的中近景：固定主体身份后执行“嘴型张开达到峰值并快速回看镜头”，拍摄者绕触发点改变观察角度，用“惊讶峰值在目标区域形成一次向外弹开的脸部轮廓，回看镜头后轮廓反弹回自拍者”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-EXPRESSION-ECHO-V4",
    "name_zh": "表情视线回声·怒意折线",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION",
        "ATOM-CLONING-ECHOES-EXPRESSION-ECHO",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWPULSE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH"
    ],
    "trigger_logic": "眉眼表情强度超过阈值且视线连续扫过两个对象",
    "combined_effect": "怒意以折线形式依次击中两个对象，每个对象保留不同长度的红色表情回声",
    "why_new": "对象顺序由视线决定、长度由表情强度决定，回声因此表达了目标关系",
    "preview_behavior": "为预览怒意折线，系统只更新与“眉眼表情强度超过阈值且视线连续扫过两个对象”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“怒意以折线形式依次击中两个对象，每个对象保留不同长度的红色表情回声”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "怒意折线的后处理从失败点开始：针对“高强度表情可能溢出脸部，设置最大能量并软化边界”复核掩码、锚点或时间戳，通过后才将“怒意以折线形式依次击中两个对象，每个对象保留不同长度的红色表情回声”提升到成片质量。触发逻辑“眉眼表情强度超过阈值且视线连续扫过两个对象”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "高强度表情可能溢出脸部，设置最大能量并软化边界"
    ],
    "target_scenarios": [
        "剧情对视的正反打连续镜头可用怒意折线组织一段连续互动。参与者先保持关系稳定，再完成“眉眼表情强度超过阈值且视线连续扫过两个对象”；镜头不切断，直到“怒意以折线形式依次击中两个对象，每个对象保留不同长度的红色表情回声”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-EXPRESSION-ECHO-V5",
    "name_zh": "表情视线回声·眨眼收束",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION",
        "ATOM-CLONING-ECHOES-EXPRESSION-ECHO",
        "ATOM-GEOMETRY-TRACKING-SURFACE-NORMALS"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWPULSE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP"
    ],
    "trigger_logic": "一次强表情后完成连续两次眨眼",
    "combined_effect": "脸部回声在第一次眨眼时冻结，在第二次眨眼时沿原视线压缩成一个小光点",
    "why_new": "眨眼被用作回声的时间控制器，让用户可以主动收束已经发生的表情",
    "preview_behavior": "眨眼收束的取景反馈以结束状态为目标：预览先保留真实动作，在“一次强表情后完成连续两次眨眼”完成时快速呈现“脸部回声在第一次眨眼时冻结，在第二次眨眼时沿原视线压缩成一个小光点”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留眨眼收束的完整生命周期。系统逆向检查“脸部回声在第一次眨眼时冻结，在第二次眨眼时沿原视线压缩成一个小光点”是否回到稳定终态，再从“一次强表情后完成连续两次眨眼”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "眨眼漏检会使冻结层残留，超时后自动淡出"
    ],
    "target_scenarios": [
        "以多人合拍结束前的视线交接作为眨眼收束的结尾段落：让“一次强表情后完成连续两次眨眼”发生在最后一个动作峰值，保持机位直到“脸部回声在第一次眨眼时冻结，在第二次眨眼时沿原视线压缩成一个小光点”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "GAZE-PORTAL", "gaze_expression", "凝视门户显影",
        (
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
            "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
            "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        ),
        (
            "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE",
            "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
            "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        ),
        ("gaze", "spatial_portal", "world_anchor"),
        "视线向量提供门户显影方向，单目深度决定门户所在平面，虚拟追光圈出正在被凝视的入口",
        "被注视的真实表面会逐渐显露一扇具有厚度的门户，视线移开后门户沿原深度退回表面",
        "预览用视线射线和深度粗层确定候选平面，再以追光亮度提示门户即将出现",
        "录制后细化门户边缘、视线转移动画和入口内外的深度遮挡，保证显影与焦点一致",
        "旅行短片里凝视一面墙，让墙后短暂出现另一段已录场景",
        (
        {
    "recipe_id": "RECIPE-GAZE-PORTAL-V1",
    "name_zh": "凝视门户显影·墙面显影",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-INTERACTION-TRIGGERS-BLINK"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK"
    ],
    "trigger_logic": "视线在平整墙面停留一秒并完成一次眨眼",
    "combined_effect": "墙面被注视区域先出现追光边，再剥离成一扇薄门户，眨眼后露出另一段空间",
    "why_new": "眨眼是确认动作，深度平面是入口边界，凝视不再只是选择滤镜",
    "preview_behavior": "预览用视线射线和深度粗层确定候选平面，再以追光亮度提示门户即将出现。针对墙面显影，取景器先在“视线在平整墙面停留一秒并完成一次眨眼”发生前标出候选轨迹，确认后才显示“墙面被注视区域先出现追光边，再剥离成一扇薄门户，眨眼后露出另一段空间”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化门户边缘、视线转移动画和入口内外的深度遮挡，保证显影与焦点一致。录后以“视线在平整墙面停留一秒并完成一次眨眼”的首帧为时间锚，重新计算墙面显影涉及的遮挡和深度，使“墙面被注视区域先出现追光边，再剥离成一扇薄门户，眨眼后露出另一段空间”在原分辨率下保持连续；检测到墙面纹理不足会使边缘漂移，退回固定矩形并降低入口厚度时仅修补低置信度片段。",
    "risks": [
        "墙面纹理不足会使边缘漂移，退回固定矩形并降低入口厚度"
    ],
    "target_scenarios": [
        "双人访谈的肩上机位适合拍摄墙面显影：先让主体完成“视线在平整墙面停留一秒并完成一次眨眼”，随后缓慢移动手机观察“墙面被注视区域先出现追光边，再剥离成一扇薄门户，眨眼后露出另一段空间”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-PORTAL-V2",
    "name_zh": "凝视门户显影·地面出口",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWBLINK"
    ],
    "trigger_logic": "视线从人物脚下扫到远处地面并停留",
    "combined_effect": "追光沿地面扫出一条亮线，亮线尽头向下折成出口，前景脚步会遮住出口边缘",
    "why_new": "视线的扫掠路径决定入口方向，深度遮挡使出口和脚步形成真实先后关系",
    "preview_behavior": "移动端预览从地面出口的结果层反推触发：屏幕持续保留对象身份和最近历史，当“视线从人物脚下扫到远处地面并停留”成立时，把“追光沿地面扫出一条亮线，亮线尽头向下折成出口，前景脚步会遮住出口边缘”分成进入、保持、退场三段显示。若出现地面倾斜估计错误会让出口翻转，保持最近可信地面法线，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把地面出口拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“视线从人物脚下扫到远处地面并停留”，再细化“追光沿地面扫出一条亮线，亮线尽头向下折成出口，前景脚步会遮住出口边缘”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "地面倾斜估计错误会让出口翻转，保持最近可信地面法线"
    ],
    "target_scenarios": [
        "在自拍视频中的镜头到对象切换使用地面出口。镜头从未触发状态开始横向移动，人物或物体执行“视线从人物脚下扫到远处地面并停留”后继续穿过画面，以“追光沿地面扫出一条亮线，亮线尽头向下折成出口，前景脚步会遮住出口边缘”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-PORTAL-V3",
    "name_zh": "凝视门户显影·镜中回望",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-CONFIRM"
    ],
    "trigger_logic": "用户注视镜面反射中的自己并缓慢转头",
    "combined_effect": "镜中脸部区域生成只对镜内可见的门户，转头时门户边界随反射视角偏移",
    "why_new": "门户只响应镜内视线节点，真实脸和镜像脸的视线关系共同塑造入口",
    "preview_behavior": "拍摄者先看到镜中回望所需的对象边界、方向箭头和时间门；“用户注视镜面反射中的自己并缓慢转头”被连续确认后，预览按由近到远的层次展开“镜中脸部区域生成只对镜内可见的门户，转头时门户边界随反射视角偏移”。被注视的真实表面会逐渐显露一扇具有厚度的门户，视线移开后门户沿原深度退回表面，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验镜中回望的身份链与事件顺序，再按视线向量提供门户显影方向，单目深度决定门户所在平面，虚拟追光圈出正在被凝视的入口重建组件关系。“镜中脸部区域生成只对镜内可见的门户，转头时门户边界随反射视角偏移”使用完整历史窗口重新渲染，而“用户注视镜面反射中的自己并缓慢转头”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "镜面反射追踪丢失时冻结最后一帧门户并短时淡出"
    ],
    "target_scenarios": [
        "把镜中回望安排在桌面产品口播的中近景：固定主体身份后执行“用户注视镜面反射中的自己并缓慢转头”，拍摄者绕触发点改变观察角度，用“镜中脸部区域生成只对镜内可见的门户，转头时门户边界随反射视角偏移”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-PORTAL-V4",
    "name_zh": "凝视门户显影·焦点穿门",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH"
    ],
    "trigger_logic": "视线从近处物体切到远处目标且目标深度稳定",
    "combined_effect": "近物体的追光圈收缩成门框，焦点跳到远处时门内视野同步切换到远处目标",
    "why_new": "焦点变化和门户显影共用深度顺序，视觉注意力的跳转变成空间穿越",
    "preview_behavior": "为预览焦点穿门，系统只更新与“视线从近处物体切到远处目标且目标深度稳定”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“近物体的追光圈收缩成门框，焦点跳到远处时门内视野同步切换到远处目标”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "焦点穿门的后处理从失败点开始：针对“远近目标重叠会产生错误门框，保留高置信度目标并延迟切换”复核掩码、锚点或时间戳，通过后才将“近物体的追光圈收缩成门框，焦点跳到远处时门内视野同步切换到远处目标”提升到成片质量。触发逻辑“视线从近处物体切到远处目标且目标深度稳定”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "远近目标重叠会产生错误门框，保留高置信度目标并延迟切换"
    ],
    "target_scenarios": [
        "剧情对视的正反打连续镜头可用焦点穿门组织一段连续互动。参与者先保持关系稳定，再完成“视线从近处物体切到远处目标且目标深度稳定”；镜头不切断，直到“近物体的追光圈收缩成门框，焦点跳到远处时门内视野同步切换到远处目标”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-GAZE-PORTAL-V5",
    "name_zh": "凝视门户显影·移开闭门",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP"
    ],
    "trigger_logic": "用户凝视入口后快速移开视线并向下看",
    "combined_effect": "门户先沿原边缘保持半透明，视线向下时入口从上到下折回墙面并留下短暂光痕",
    "why_new": "关闭方向由新的视线向量控制，门户结束状态因此响应用户动作而非固定淡出",
    "preview_behavior": "移开闭门的取景反馈以结束状态为目标：预览先保留真实动作，在“用户凝视入口后快速移开视线并向下看”完成时快速呈现“门户先沿原边缘保持半透明，视线向下时入口从上到下折回墙面并留下短暂光痕”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留移开闭门的完整生命周期。系统逆向检查“门户先沿原边缘保持半透明，视线向下时入口从上到下折回墙面并留下短暂光痕”是否回到稳定终态，再从“用户凝视入口后快速移开视线并向下看”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "快速移开会造成关闭不完整，超时使用原路逆向收束"
    ],
    "target_scenarios": [
        "以多人合拍结束前的视线交接作为移开闭门的结尾段落：让“用户凝视入口后快速移开视线并向下看”发生在最后一个动作峰值，保持机位直到“门户先沿原边缘保持半透明，视线向下时入口从上到下折回墙面并留下短暂光痕”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "BLINK-SOUND-FACE", "gaze_expression", "眨眼声压脸部灯",
        (
            "ATOM-SEGMENTATION-MASKS-FACE-REGION",
            "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
            "ATOM-INTERACTION-TRIGGERS-BLINK",
            "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        ),
        (
            "FX-FACE-GAZE-EXPRESSION-CAMERA-CAMERABLINK",
            "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK",
            "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        ),
        ("expression", "sound", "gaze"),
        "眨眼把脸部光效切成明确事件，虹膜关键点保持高光位置，声音音量把事件扩展为面部周围的动态光层",
        "眨眼会切换面部灯光状态，声音越强光层越厚，眼神光则在每次切换中保留可辨识的瞳孔反射",
        "预览用脸部掩码、眨眼事件和低频音量包络驱动少量光层，避免小屏上光效糊成一片",
        "录制后细化眨眼起止帧、音量曲线和双眼高光形状，修复侧脸与快速说话造成的断续",
        "口播自拍中用眨眼切换声音驱动的脸部灯光情绪",
        (
        {
    "recipe_id": "RECIPE-BLINK-SOUND-FACE-V1",
    "name_zh": "眨眼声压脸部灯·眨眼开灯",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-INTERACTION-TRIGGERS-BLINK",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-EXPRESSION"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CAMERABLINK",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWBLINK"
    ],
    "trigger_logic": "用户第一次眨眼且当前音量高于安静门限",
    "combined_effect": "双眼眼神光同时点亮，脸部边缘出现随声音厚度变化的半透明光环",
    "why_new": "眨眼负责离散开关，音量负责连续厚度，二者共同形成可操作的脸部灯状态",
    "preview_behavior": "预览用脸部掩码、眨眼事件和低频音量包络驱动少量光层，避免小屏上光效糊成一片。针对眨眼开灯，取景器先在“用户第一次眨眼且当前音量高于安静门限”发生前标出候选轨迹，确认后才显示“双眼眼神光同时点亮，脸部边缘出现随声音厚度变化的半透明光环”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化眨眼起止帧、音量曲线和双眼高光形状，修复侧脸与快速说话造成的断续。录后以“用户第一次眨眼且当前音量高于安静门限”的首帧为时间锚，重新计算眨眼开灯涉及的遮挡和深度，使“双眼眼神光同时点亮，脸部边缘出现随声音厚度变化的半透明光环”在原分辨率下保持连续；检测到环境噪声会误增光环，使用人声频段门控并保留上一帧厚度时仅修补低置信度片段。",
    "risks": [
        "环境噪声会误增光环，使用人声频段门控并保留上一帧厚度"
    ],
    "target_scenarios": [
        "双人访谈的肩上机位适合拍摄眨眼开灯：先让主体完成“用户第一次眨眼且当前音量高于安静门限”，随后缓慢移动手机观察“双眼眼神光同时点亮，脸部边缘出现随声音厚度变化的半透明光环”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-BLINK-SOUND-FACE-V2",
    "name_zh": "眨眼声压脸部灯·眨眼换色",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-INTERACTION-TRIGGERS-BLINK",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CAMERABLINK",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-FACE-GAZE-EXPRESSION-SELECT-CONFIRM"
    ],
    "trigger_logic": "连续两次眨眼之间音量从低到高上升",
    "combined_effect": "第一次眨眼收起冷色高光，第二次眨眼释放暖色高光，音量上升让换色边界向脸颊扩散",
    "why_new": "眨眼间隔成为颜色选择信号，声音又改变扩散范围，用户动作可直接编排色彩",
    "preview_behavior": "移动端预览从眨眼换色的结果层反推触发：屏幕持续保留对象身份和最近历史，当“连续两次眨眼之间音量从低到高上升”成立时，把“第一次眨眼收起冷色高光，第二次眨眼释放暖色高光，音量上升让换色边界向脸颊扩散”分成进入、保持、退场三段显示。若出现眨眼间隔过短会误触发，设置最小事件间隔，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把眨眼换色拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“连续两次眨眼之间音量从低到高上升”，再细化“第一次眨眼收起冷色高光，第二次眨眼释放暖色高光，音量上升让换色边界向脸颊扩散”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "眨眼间隔过短会误触发，设置最小事件间隔"
    ],
    "target_scenarios": [
        "在自拍视频中的镜头到对象切换使用眨眼换色。镜头从未触发状态开始横向移动，人物或物体执行“连续两次眨眼之间音量从低到高上升”后继续穿过画面，以“第一次眨眼收起冷色高光，第二次眨眼释放暖色高光，音量上升让换色边界向脸颊扩散”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-BLINK-SOUND-FACE-V3",
    "name_zh": "眨眼声压脸部灯·静音闭合",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-INTERACTION-TRIGGERS-BLINK",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CAMERABLINK",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH"
    ],
    "trigger_logic": "说话停止且用户保持闭眼超过短时窗口",
    "combined_effect": "面部光环在停声时向瞳孔收缩，闭眼确认后变成两点微光并暂时隐藏嘴部光谱",
    "why_new": "声音停止和闭眼不是两个淡出条件，而是共同完成光层的空间收束",
    "preview_behavior": "拍摄者先看到静音闭合所需的对象边界、方向箭头和时间门；“说话停止且用户保持闭眼超过短时窗口”被连续确认后，预览按由近到远的层次展开“面部光环在停声时向瞳孔收缩，闭眼确认后变成两点微光并暂时隐藏嘴部光谱”。眨眼会切换面部灯光状态，声音越强光层越厚，眼神光则在每次切换中保留可辨识的瞳孔反射，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验静音闭合的身份链与事件顺序，再按眨眼把脸部光效切成明确事件，虹膜关键点保持高光位置，声音音量把事件扩展为面部周围的动态光层重建组件关系。“面部光环在停声时向瞳孔收缩，闭眼确认后变成两点微光并暂时隐藏嘴部光谱”使用完整历史窗口重新渲染，而“说话停止且用户保持闭眼超过短时窗口”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "闭眼持续过长会丢失脸部跟踪，保留最后可信眼神光并渐隐"
    ],
    "target_scenarios": [
        "把静音闭合安排在桌面产品口播的中近景：固定主体身份后执行“说话停止且用户保持闭眼超过短时窗口”，拍摄者绕触发点改变观察角度，用“面部光环在停声时向瞳孔收缩，闭眼确认后变成两点微光并暂时隐藏嘴部光谱”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-BLINK-SOUND-FACE-V4",
    "name_zh": "眨眼声压脸部灯·笑声波纹",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-INTERACTION-TRIGGERS-BLINK",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-GEOMETRY-TRACKING-SURFACE-NORMALS"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CAMERABLINK",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP"
    ],
    "trigger_logic": "笑声音量出现两个连续峰值并伴随快速眨眼",
    "combined_effect": "两个音量峰值在脸部轮廓形成同心波纹，眨眼让波纹穿过眼神光时短暂闪白",
    "why_new": "声音峰值提供波纹节奏，眨眼提供穿越时刻，脸部区域因此成为声画共振面",
    "preview_behavior": "为预览笑声波纹，系统只更新与“笑声音量出现两个连续峰值并伴随快速眨眼”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“两个音量峰值在脸部轮廓形成同心波纹，眨眼让波纹穿过眼神光时短暂闪白”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "笑声波纹的后处理从失败点开始：针对“高亮波纹可能遮挡眼睛，限制波纹在眼周的能量”复核掩码、锚点或时间戳，通过后才将“两个音量峰值在脸部轮廓形成同心波纹，眨眼让波纹穿过眼神光时短暂闪白”提升到成片质量。触发逻辑“笑声音量出现两个连续峰值并伴随快速眨眼”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "高亮波纹可能遮挡眼睛，限制波纹在眼周的能量"
    ],
    "target_scenarios": [
        "剧情对视的正反打连续镜头可用笑声波纹组织一段连续互动。参与者先保持关系稳定，再完成“笑声音量出现两个连续峰值并伴随快速眨眼”；镜头不切断，直到“两个音量峰值在脸部轮廓形成同心波纹，眨眼让波纹穿过眼神光时短暂闪白”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-BLINK-SOUND-FACE-V5",
    "name_zh": "眨眼声压脸部灯·镜头回应",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-INTERACTION-TRIGGERS-BLINK",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CAMERABLINK",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-CATCHBLINK",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-FACE-GAZE-EXPRESSION-CAMERA-CALIBRATE"
    ],
    "trigger_logic": "用户看镜头、提高音量并在句尾眨眼",
    "combined_effect": "眼神光先朝镜头聚焦，句尾眨眼把音量光层推出画面边缘形成一次镜头回应闪光",
    "why_new": "视线目标、音量包络和句尾事件共同定义结束动作，效果不依赖固定节拍",
    "preview_behavior": "镜头回应的取景反馈以结束状态为目标：预览先保留真实动作，在“用户看镜头、提高音量并在句尾眨眼”完成时快速呈现“眼神光先朝镜头聚焦，句尾眨眼把音量光层推出画面边缘形成一次镜头回应闪光”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留镜头回应的完整生命周期。系统逆向检查“眼神光先朝镜头聚焦，句尾眨眼把音量光层推出画面边缘形成一次镜头回应闪光”是否回到稳定终态，再从“用户看镜头、提高音量并在句尾眨眼”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "句尾检测不稳定会延迟闪光，使用最近音量峰值作为后备触发"
    ],
    "target_scenarios": [
        "以多人合拍结束前的视线交接作为镜头回应的结尾段落：让“用户看镜头、提高音量并在句尾眨眼”发生在最后一个动作峰值，保持机位直到“眼神光先朝镜头聚焦，句尾眨眼把音量光层推出画面边缘形成一次镜头回应闪光”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "TIME-POSE-COLOR", "time_cloning", "时间姿态分层",
        (
            "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
            "ATOM-CLONING-ECHOES-POSE-SLICES",
            "ATOM-TEMPORAL-STATE-MOTION-PHASE",
            "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        ),
        (
            "FX-BODY-MOTION-CLONES-TIME-DELAY",
            "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
            "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        ),
        ("time", "body_pose", "color_layer"),
        "人体时间克隆保存前后姿态，姿态切片找出动作差分，动作阶段为每一层分配颜色并维持人体轮廓遮挡",
        "同一个人会以不同颜色的姿态层同时出现在画面中，颜色不是装饰而是编码动作先后与姿态差异",
        "预览保留三到五个历史姿态层，按动作阶段使用有限色板并优先保持身体轮廓清晰",
        "录制后从完整时间克隆中重新选取姿态峰值，细化层间遮挡、颜色渐变和动作差分边界",
        "舞蹈或运动录像中把一个连贯动作展开成可读的彩色姿态谱",
        (
        {
    "recipe_id": "RECIPE-TIME-POSE-COLOR-V1",
    "name_zh": "时间姿态分层·起跳分层",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-TEMPORAL-STATE-MOTION-PHASE",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-DELAY",
        "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-TIME-EDITING-LOOP-LOOPBEAT"
    ],
    "trigger_logic": "身体由下蹲进入起跳并经过最高点",
    "combined_effect": "下蹲、离地和最高点三层姿态以冷到暖的颜色排列，腿部差分被保留为细亮边",
    "why_new": "姿态峰值而非等间隔抽帧决定层次，颜色直接编码动作阶段",
    "preview_behavior": "预览保留三到五个历史姿态层，按动作阶段使用有限色板并优先保持身体轮廓清晰。针对起跳分层，取景器先在“身体由下蹲进入起跳并经过最高点”发生前标出候选轨迹，确认后才显示“下蹲、离地和最高点三层姿态以冷到暖的颜色排列，腿部差分被保留为细亮边”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后从完整时间克隆中重新选取姿态峰值，细化层间遮挡、颜色渐变和动作差分边界。录后以“身体由下蹲进入起跳并经过最高点”的首帧为时间锚，重新计算起跳分层涉及的遮挡和深度，使“下蹲、离地和最高点三层姿态以冷到暖的颜色排列，腿部差分被保留为细亮边”在原分辨率下保持连续；检测到最高点检测抖动会让暖色层重复，使用运动相位滞回时仅修补低置信度片段。",
    "risks": [
        "最高点检测抖动会让暖色层重复，使用运动相位滞回"
    ],
    "target_scenarios": [
        "舞蹈排练室的全身固定机位适合拍摄起跳分层：先让主体完成“身体由下蹲进入起跳并经过最高点”，随后缓慢移动手机观察“下蹲、离地和最高点三层姿态以冷到暖的颜色排列，腿部差分被保留为细亮边”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-POSE-COLOR-V2",
    "name_zh": "时间姿态分层·转身彩页",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-TEMPORAL-STATE-MOTION-PHASE",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-DELAY",
        "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "身体完成半圈转身且肩线方向发生一次反转",
    "combined_effect": "转身前后的姿态像翻页一样错开，旧层变冷、新层变暖，重合躯干只保留一条轮廓",
    "why_new": "姿态差分决定翻页位置，颜色分层同时表达时间方向和身体朝向",
    "preview_behavior": "移动端预览从转身彩页的结果层反推触发：屏幕持续保留对象身份和最近历史，当“身体完成半圈转身且肩线方向发生一次反转”成立时，把“转身前后的姿态像翻页一样错开，旧层变冷、新层变暖，重合躯干只保留一条轮廓”分成进入、保持、退场三段显示。若出现肩部遮挡会使翻页缝穿过头部，优先使用躯干锚点修正，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把转身彩页拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“身体完成半圈转身且肩线方向发生一次反转”，再细化“转身前后的姿态像翻页一样错开，旧层变冷、新层变暖，重合躯干只保留一条轮廓”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "肩部遮挡会使翻页缝穿过头部，优先使用躯干锚点修正"
    ],
    "target_scenarios": [
        "在街头跑跳动作的侧向跟拍使用转身彩页。镜头从未触发状态开始横向移动，人物或物体执行“身体完成半圈转身且肩线方向发生一次反转”后继续穿过画面，以“转身前后的姿态像翻页一样错开，旧层变冷、新层变暖，重合躯干只保留一条轮廓”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-POSE-COLOR-V3",
    "name_zh": "时间姿态分层·挥臂彩虹",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-TEMPORAL-STATE-MOTION-PHASE",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-DELAY",
        "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-TIME-EDITING-BORROW-BORROWOBJECT"
    ],
    "trigger_logic": "手臂从低位挥到高位并经过两个速度峰值",
    "combined_effect": "手臂历史按速度峰值切成五段颜色，身体主体保持当前帧，形成从慢到快的彩虹弧",
    "why_new": "局部姿态差分与全身时间克隆分开合成，局部动作因此能脱离整身重影",
    "preview_behavior": "拍摄者先看到挥臂彩虹所需的对象边界、方向箭头和时间门；“手臂从低位挥到高位并经过两个速度峰值”被连续确认后，预览按由近到远的层次展开“手臂历史按速度峰值切成五段颜色，身体主体保持当前帧，形成从慢到快的彩虹弧”。同一个人会以不同颜色的姿态层同时出现在画面中，颜色不是装饰而是编码动作先后与姿态差异，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验挥臂彩虹的身份链与事件顺序，再按人体时间克隆保存前后姿态，姿态切片找出动作差分，动作阶段为每一层分配颜色并维持人体轮廓遮挡重建组件关系。“手臂历史按速度峰值切成五段颜色，身体主体保持当前帧，形成从慢到快的彩虹弧”使用完整历史窗口重新渲染，而“手臂从低位挥到高位并经过两个速度峰值”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "手臂交叉时层会粘连，丢弃交叉区低置信度像素"
    ],
    "target_scenarios": [
        "把挥臂彩虹安排在室内物体拿放的连续长镜头：固定主体身份后执行“手臂从低位挥到高位并经过两个速度峰值”，拍摄者绕触发点改变观察角度，用“手臂历史按速度峰值切成五段颜色，身体主体保持当前帧，形成从慢到快的彩虹弧”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-POSE-COLOR-V4",
    "name_zh": "时间姿态分层·落步印记",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-TEMPORAL-STATE-MOTION-PHASE",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-DELAY",
        "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER"
    ],
    "trigger_logic": "脚步依次落在三个不同位置且躯干保持连续",
    "combined_effect": "每个落脚点留下一个对应颜色的半透明姿态印记，印记之间以躯干方向排序而不是按屏幕位置排序",
    "why_new": "空间位置与时间顺序共同决定姿态层，避免成为简单的多重复制",
    "preview_behavior": "为预览落步印记，系统只更新与“脚步依次落在三个不同位置且躯干保持连续”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“每个落脚点留下一个对应颜色的半透明姿态印记，印记之间以躯干方向排序而不是按屏幕位置排序”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "落步印记的后处理从失败点开始：针对“地面遮挡会截断脚印层，保留脚踝和小范围轮廓作为替代”复核掩码、锚点或时间戳，通过后才将“每个落脚点留下一个对应颜色的半透明姿态印记，印记之间以躯干方向排序而不是按屏幕位置排序”提升到成片质量。触发逻辑“脚步依次落在三个不同位置且躯干保持连续”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "地面遮挡会截断脚印层，保留脚踝和小范围轮廓作为替代"
    ],
    "target_scenarios": [
        "人物绕柱移动的空间回看可用落步印记组织一段连续互动。参与者先保持关系稳定，再完成“脚步依次落在三个不同位置且躯干保持连续”；镜头不切断，直到“每个落脚点留下一个对应颜色的半透明姿态印记，印记之间以躯干方向排序而不是按屏幕位置排序”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-POSE-COLOR-V5",
    "name_zh": "时间姿态分层·停顿渐层",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-TEMPORAL-STATE-MOTION-PHASE",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-CLONING-ECHOES-DELAYED-CLONE"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-DELAY",
        "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL"
    ],
    "trigger_logic": "动作中出现短暂停顿后再次加速",
    "combined_effect": "停顿姿态形成最厚的中间色层，再次加速时前后姿态向两侧变薄，画面呈现一次时间呼吸",
    "why_new": "停顿改变层透明度而不是只增加克隆数量，使动作节奏可由颜色密度读出",
    "preview_behavior": "停顿渐层的取景反馈以结束状态为目标：预览先保留真实动作，在“动作中出现短暂停顿后再次加速”完成时快速呈现“停顿姿态形成最厚的中间色层，再次加速时前后姿态向两侧变薄，画面呈现一次时间呼吸”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留停顿渐层的完整生命周期。系统逆向检查“停顿姿态形成最厚的中间色层，再次加速时前后姿态向两侧变薄，画面呈现一次时间呼吸”是否回到稳定终态，再从“动作中出现短暂停顿后再次加速”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "停顿过短会被噪声吸收，要求相位稳定后再成层"
    ],
    "target_scenarios": [
        "以动作回到起点的结尾镜头作为停顿渐层的结尾段落：让“动作中出现短暂停顿后再次加速”发生在最后一个动作峰值，保持机位直到“停顿姿态形成最厚的中间色层，再次加速时前后姿态向两侧变薄，画面呈现一次时间呼吸”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "TIME-GESTURE-MATERIAL", "time_cloning", "手势时间材质循环",
        (
            "ATOM-CLONING-ECHOES-GESTURE-ECHO",
            "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
            "ATOM-TEMPORAL-STATE-TIME-LOOP",
            "ATOM-MATERIAL-APPEARANCE-PIXEL",
        ),
        (
            "FX-BODY-MOTION-CLONES-GESTURE-GESTURELOOP",
            "FX-TIME-EDITING-LOOP-LOOPMOVE",
            "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        ),
        ("time", "touch_gesture", "material"),
        "手部二维轨迹定义循环区域，手势回声保存动作样本，时间循环把样本贴回像素材质并允许沿手势移动",
        "用户画出的手势会把一小块画面变成可移动的时间材质，材质在循环中反向溶解而不是机械重复",
        "预览只缓存手势附近的短循环片段，移动时采用像素化边缘提示循环区域的空间范围",
        "录制后重建手势路径和局部时间循环，细化循环首尾、材质碎片与对象遮挡关系",
        "手指圈出一块画面，让其中的动作像可拖动的动态贴片一样循环",
        (
        {
    "recipe_id": "RECIPE-TIME-GESTURE-MATERIAL-V1",
    "name_zh": "手势时间材质循环·拖动笑脸",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-GESTURE-ECHO",
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-MATERIAL-APPEARANCE-PIXEL",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-GESTURE-GESTURELOOP",
        "FX-TIME-EDITING-LOOP-LOOPMOVE",
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-LOOP-LOOPBEAT"
    ],
    "trigger_logic": "手指圈出脸部局部并沿水平方向拖动",
    "combined_effect": "圈内笑容动作沿手指方向重复移动，边缘像像素碎片一样反向凝结回脸部",
    "why_new": "手势同时定义循环内容和搬运方向，时间效果因而具有可操纵的空间轨迹",
    "preview_behavior": "预览只缓存手势附近的短循环片段，移动时采用像素化边缘提示循环区域的空间范围。针对拖动笑脸，取景器先在“手指圈出脸部局部并沿水平方向拖动”发生前标出候选轨迹，确认后才显示“圈内笑容动作沿手指方向重复移动，边缘像像素碎片一样反向凝结回脸部”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建手势路径和局部时间循环，细化循环首尾、材质碎片与对象遮挡关系。录后以“手指圈出脸部局部并沿水平方向拖动”的首帧为时间锚，重新计算拖动笑脸涉及的遮挡和深度，使“圈内笑容动作沿手指方向重复移动，边缘像像素碎片一样反向凝结回脸部”在原分辨率下保持连续；检测到圈选穿过眼睛会造成脸部碎片错位，系统缩小到稳定脸部掩码时仅修补低置信度片段。",
    "risks": [
        "圈选穿过眼睛会造成脸部碎片错位，系统缩小到稳定脸部掩码"
    ],
    "target_scenarios": [
        "舞蹈排练室的全身固定机位适合拍摄拖动笑脸：先让主体完成“手指圈出脸部局部并沿水平方向拖动”，随后缓慢移动手机观察“圈内笑容动作沿手指方向重复移动，边缘像像素碎片一样反向凝结回脸部”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-GESTURE-MATERIAL-V2",
    "name_zh": "手势时间材质循环·指尖回放",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-GESTURE-ECHO",
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-MATERIAL-APPEARANCE-PIXEL",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-GESTURE-GESTURELOOP",
        "FX-TIME-EDITING-LOOP-LOOPMOVE",
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "手指画出短线后在终点停留半拍",
    "combined_effect": "短线区域回放最近一次指尖动作，停留越久循环片段越清晰，结束时碎片倒序收回",
    "why_new": "停留时间决定循环清晰度，手势回声提供内容，结果不是固定的GIF贴片",
    "preview_behavior": "移动端预览从指尖回放的结果层反推触发：屏幕持续保留对象身份和最近历史，当“手指画出短线后在终点停留半拍”成立时，把“短线区域回放最近一次指尖动作，停留越久循环片段越清晰，结束时碎片倒序收回”分成进入、保持、退场三段显示。若出现短线太短难以估计方向，使用最后可信切线作为循环方向，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把指尖回放拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“手指画出短线后在终点停留半拍”，再细化“短线区域回放最近一次指尖动作，停留越久循环片段越清晰，结束时碎片倒序收回”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "短线太短难以估计方向，使用最后可信切线作为循环方向"
    ],
    "target_scenarios": [
        "在街头跑跳动作的侧向跟拍使用指尖回放。镜头从未触发状态开始横向移动，人物或物体执行“手指画出短线后在终点停留半拍”后继续穿过画面，以“短线区域回放最近一次指尖动作，停留越久循环片段越清晰，结束时碎片倒序收回”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-GESTURE-MATERIAL-V3",
    "name_zh": "手势时间材质循环·局部翻页",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-GESTURE-ECHO",
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-MATERIAL-APPEARANCE-PIXEL",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-GESTURE-GESTURELOOP",
        "FX-TIME-EDITING-LOOP-LOOPMOVE",
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-BORROW-BORROWOBJECT"
    ],
    "trigger_logic": "手指从上向下划过物体并画出闭合小框",
    "combined_effect": "框内物体动作按时间循环翻页，翻页边缘由像素碎片向内折叠，框外时间正常推进",
    "why_new": "闭合框成为时间窗口，像素材质把窗口边界做成可见的翻页结构",
    "preview_behavior": "拍摄者先看到局部翻页所需的对象边界、方向箭头和时间门；“手指从上向下划过物体并画出闭合小框”被连续确认后，预览按由近到远的层次展开“框内物体动作按时间循环翻页，翻页边缘由像素碎片向内折叠，框外时间正常推进”。用户画出的手势会把一小块画面变成可移动的时间材质，材质在循环中反向溶解而不是机械重复，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验局部翻页的身份链与事件顺序，再按手部二维轨迹定义循环区域，手势回声保存动作样本，时间循环把样本贴回像素材质并允许沿手势移动重建组件关系。“框内物体动作按时间循环翻页，翻页边缘由像素碎片向内折叠，框外时间正常推进”使用完整历史窗口重新渲染，而“手指从上向下划过物体并画出闭合小框”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "物体快速出框会留下残片，系统在对象消失时提前结束循环"
    ],
    "target_scenarios": [
        "把局部翻页安排在室内物体拿放的连续长镜头：固定主体身份后执行“手指从上向下划过物体并画出闭合小框”，拍摄者绕触发点改变观察角度，用“框内物体动作按时间循环翻页，翻页边缘由像素碎片向内折叠，框外时间正常推进”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-GESTURE-MATERIAL-V4",
    "name_zh": "手势时间材质循环·双点循环",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-GESTURE-ECHO",
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-MATERIAL-APPEARANCE-PIXEL",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-GESTURE-GESTURELOOP",
        "FX-TIME-EDITING-LOOP-LOOPMOVE",
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER"
    ],
    "trigger_logic": "用户连续点选两个手部位置并在两点间来回划动",
    "combined_effect": "两点之间的动作片段在来回路径上交替播放，交替时像素材质发生一次方向相反的溶解",
    "why_new": "两个采样点构成循环端点，手势方向控制时间正反而非只控制位置",
    "preview_behavior": "为预览双点循环，系统只更新与“用户连续点选两个手部位置并在两点间来回划动”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“两点之间的动作片段在来回路径上交替播放，交替时像素材质发生一次方向相反的溶解”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "双点循环的后处理从失败点开始：针对“两点过近会让循环抖动，合并为单点短循环”复核掩码、锚点或时间戳，通过后才将“两点之间的动作片段在来回路径上交替播放，交替时像素材质发生一次方向相反的溶解”提升到成片质量。触发逻辑“用户连续点选两个手部位置并在两点间来回划动”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "两点过近会让循环抖动，合并为单点短循环"
    ],
    "target_scenarios": [
        "人物绕柱移动的空间回看可用双点循环组织一段连续互动。参与者先保持关系稳定，再完成“用户连续点选两个手部位置并在两点间来回划动”；镜头不切断，直到“两点之间的动作片段在来回路径上交替播放，交替时像素材质发生一次方向相反的溶解”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-TIME-GESTURE-MATERIAL-V5",
    "name_zh": "手势时间材质循环·抹除重写",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-GESTURE-ECHO",
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-MATERIAL-APPEARANCE-PIXEL",
        "ATOM-CLONING-ECHOES-DELAYED-CLONE"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-GESTURE-GESTURELOOP",
        "FX-TIME-EDITING-LOOP-LOOPMOVE",
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL"
    ],
    "trigger_logic": "手指先圈选局部循环，再反向擦过循环区域",
    "combined_effect": "擦过的部分按历史顺序倒放并逐点消失，未擦区域继续循环，形成局部重写效果",
    "why_new": "同一手势路径既是选择器又是时间反向控制器，擦除动作改变了内容本身",
    "preview_behavior": "抹除重写的取景反馈以结束状态为目标：预览先保留真实动作，在“手指先圈选局部循环，再反向擦过循环区域”完成时快速呈现“擦过的部分按历史顺序倒放并逐点消失，未擦区域继续循环，形成局部重写效果”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留抹除重写的完整生命周期。系统逆向检查“擦过的部分按历史顺序倒放并逐点消失，未擦区域继续循环，形成局部重写效果”是否回到稳定终态，再从“手指先圈选局部循环，再反向擦过循环区域”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "擦除路径断裂会留下孤立碎片，使用邻近路径连接并降低残留透明度"
    ],
    "target_scenarios": [
        "以动作回到起点的结尾镜头作为抹除重写的结尾段落：让“手指先圈选局部循环，再反向擦过循环区域”发生在最后一个动作峰值，保持机位直到“擦过的部分按历史顺序倒放并逐点消失，未擦区域继续循环，形成局部重写效果”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "CLONE-WORLD-ANCHOR", "time_cloning", "世界锚定时间分身",
        (
            "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
            "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY",
        ),
        (
            "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
            "FX-LIGHT-TRAILS-OPTICS-WORLD-PARALLAX",
            "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        ),
        ("time", "world_anchor", "spatial_portal"),
        "时序身份记忆保持同一对象，物体姿态把分身放回世界锚点，时间路径和视差让每个分身拥有不同历史位置",
        "同一对象的多个时间分身会留在它经过的真实空间位置，镜头移动时分身产生视差并可穿过锚定的时间页",
        "预览保留少量身份稳定的时间分身，以粗粒度深度层处理前后遮挡和页面边界",
        "录制后重追踪对象身份和世界位姿，重排分身深度、时间路径以及穿页时的边缘遮挡",
        "街拍中让行走者把刚才走过的几个空间位置保留成一条时间走廊",
        (
        {
    "recipe_id": "RECIPE-CLONE-WORLD-ANCHOR-V1",
    "name_zh": "世界锚定时间分身·脚步走廊",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-PARALLAX",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-TIME-EDITING-LOOP-LOOPBEAT"
    ],
    "trigger_logic": "对象连续走过三个可见位置且身份置信度保持稳定",
    "combined_effect": "每个位置留下一个不同时间的半透明分身，分身之间形成随镜头视差展开的走廊",
    "why_new": "身份记忆防止分身串人，世界锚点让历史位置不随屏幕移动",
    "preview_behavior": "预览保留少量身份稳定的时间分身，以粗粒度深度层处理前后遮挡和页面边界。针对脚步走廊，取景器先在“对象连续走过三个可见位置且身份置信度保持稳定”发生前标出候选轨迹，确认后才显示“每个位置留下一个不同时间的半透明分身，分身之间形成随镜头视差展开的走廊”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重追踪对象身份和世界位姿，重排分身深度、时间路径以及穿页时的边缘遮挡。录后以“对象连续走过三个可见位置且身份置信度保持稳定”的首帧为时间锚，重新计算脚步走廊涉及的遮挡和深度，使“每个位置留下一个不同时间的半透明分身，分身之间形成随镜头视差展开的走廊”在原分辨率下保持连续；检测到行人被遮挡后可能串轨，恢复身份前冻结旧分身而不新增时仅修补低置信度片段。",
    "risks": [
        "行人被遮挡后可能串轨，恢复身份前冻结旧分身而不新增"
    ],
    "target_scenarios": [
        "舞蹈排练室的全身固定机位适合拍摄脚步走廊：先让主体完成“对象连续走过三个可见位置且身份置信度保持稳定”，随后缓慢移动手机观察“每个位置留下一个不同时间的半透明分身，分身之间形成随镜头视差展开的走廊”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-CLONE-WORLD-ANCHOR-V2",
    "name_zh": "世界锚定时间分身·回头页面",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-PARALLAX",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "对象走远后回头看镜头并触发一次局部翻页",
    "combined_effect": "回头姿态在原地固定成时间页，页面翻开时显示对象几秒前经过的空间位置",
    "why_new": "回头是时间页的内容选择器，空间锚点决定页面展示的历史地点",
    "preview_behavior": "移动端预览从回头页面的结果层反推触发：屏幕持续保留对象身份和最近历史，当“对象走远后回头看镜头并触发一次局部翻页”成立时，把“回头姿态在原地固定成时间页，页面翻开时显示对象几秒前经过的空间位置”分成进入、保持、退场三段显示。若出现回头帧不足会产生空页，退化为最近可信姿态的短页，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把回头页面拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“对象走远后回头看镜头并触发一次局部翻页”，再细化“回头姿态在原地固定成时间页，页面翻开时显示对象几秒前经过的空间位置”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "回头帧不足会产生空页，退化为最近可信姿态的短页"
    ],
    "target_scenarios": [
        "在街头跑跳动作的侧向跟拍使用回头页面。镜头从未触发状态开始横向移动，人物或物体执行“对象走远后回头看镜头并触发一次局部翻页”后继续穿过画面，以“回头姿态在原地固定成时间页，页面翻开时显示对象几秒前经过的空间位置”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-CLONE-WORLD-ANCHOR-V3",
    "name_zh": "世界锚定时间分身·交错穿行",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-PARALLAX",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-TIME-EDITING-BORROW-BORROWOBJECT"
    ],
    "trigger_logic": "两个对象在同一世界平面交叉并随后分开",
    "combined_effect": "两条时间路径在交叉点短暂叠成一座双重分身门，分开后各自回到所属路径",
    "why_new": "身份图和世界路径共同处理交叉关系，结果表达两条历史轨迹的相遇",
    "preview_behavior": "拍摄者先看到交错穿行所需的对象边界、方向箭头和时间门；“两个对象在同一世界平面交叉并随后分开”被连续确认后，预览按由近到远的层次展开“两条时间路径在交叉点短暂叠成一座双重分身门，分开后各自回到所属路径”。同一对象的多个时间分身会留在它经过的真实空间位置，镜头移动时分身产生视差并可穿过锚定的时间页，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验交错穿行的身份链与事件顺序，再按时序身份记忆保持同一对象，物体姿态把分身放回世界锚点，时间路径和视差让每个分身拥有不同历史位置重建组件关系。“两条时间路径在交叉点短暂叠成一座双重分身门，分开后各自回到所属路径”使用完整历史窗口重新渲染，而“两个对象在同一世界平面交叉并随后分开”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "交叉遮挡可能交换身份，依靠颜色和姿态一致性维持路径归属"
    ],
    "target_scenarios": [
        "把交错穿行安排在室内物体拿放的连续长镜头：固定主体身份后执行“两个对象在同一世界平面交叉并随后分开”，拍摄者绕触发点改变观察角度，用“两条时间路径在交叉点短暂叠成一座双重分身门，分开后各自回到所属路径”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-CLONE-WORLD-ANCHOR-V4",
    "name_zh": "世界锚定时间分身·物体回声台",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-PARALLAX",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER"
    ],
    "trigger_logic": "可跟踪物体被拿起、放下并再次拿起",
    "combined_effect": "物体在两个真实锚点留下前后两次姿态，移动镜头时两个姿态像舞台布景一样产生视差",
    "why_new": "物体姿态而非人物剪影成为时间分身内容，锚点使拿放过程可被空间化观看",
    "preview_behavior": "为预览物体回声台，系统只更新与“可跟踪物体被拿起、放下并再次拿起”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“物体在两个真实锚点留下前后两次姿态，移动镜头时两个姿态像舞台布景一样产生视差”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "物体回声台的后处理从失败点开始：针对“反光物体姿态不稳时只保留位置回声并缩小材质范围”复核掩码、锚点或时间戳，通过后才将“物体在两个真实锚点留下前后两次姿态，移动镜头时两个姿态像舞台布景一样产生视差”提升到成片质量。触发逻辑“可跟踪物体被拿起、放下并再次拿起”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "反光物体姿态不稳时只保留位置回声并缩小材质范围"
    ],
    "target_scenarios": [
        "人物绕柱移动的空间回看可用物体回声台组织一段连续互动。参与者先保持关系稳定，再完成“可跟踪物体被拿起、放下并再次拿起”；镜头不切断，直到“物体在两个真实锚点留下前后两次姿态，移动镜头时两个姿态像舞台布景一样产生视差”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-CLONE-WORLD-ANCHOR-V5",
    "name_zh": "世界锚定时间分身·时间页合拢",
    "component_atom_ids": [
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY",
        "ATOM-CLONING-ECHOES-DELAYED-CLONE"
    ],
    "component_effect_ids": [
        "FX-BODY-MOTION-CLONES-TIME-TIMEPATH",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-PARALLAX",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL"
    ],
    "trigger_logic": "用户走回最初锚点并做出合掌动作",
    "combined_effect": "沿途分身按时间逆序穿回页面，最后一层在合掌位置合拢为当前对象",
    "why_new": "合掌把多个历史状态变成可见的回收动作，时间路径因此有了明确的开始与结束",
    "preview_behavior": "时间页合拢的取景反馈以结束状态为目标：预览先保留真实动作，在“用户走回最初锚点并做出合掌动作”完成时快速呈现“沿途分身按时间逆序穿回页面，最后一层在合掌位置合拢为当前对象”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留时间页合拢的完整生命周期。系统逆向检查“沿途分身按时间逆序穿回页面，最后一层在合掌位置合拢为当前对象”是否回到稳定终态，再从“用户走回最初锚点并做出合掌动作”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "回收途中对象出框会留下页面残影，使用锚点间插值补齐"
    ],
    "target_scenarios": [
        "以动作回到起点的结尾镜头作为时间页合拢的结尾段落：让“用户走回最初锚点并做出合掌动作”发生在最后一个动作峰值，保持机位直到“沿途分身按时间逆序穿回页面，最后一层在合掌位置合拢为当前对象”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "FREEZE-SHADOW", "time_cloning", "冻结影子时间窗",
        (
            "ATOM-SEGMENTATION-MASKS-SHADOW",
            "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
            "ATOM-TEMPORAL-STATE-FRAME-DELAY",
            "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        ),
        (
            "FX-TIME-EDITING-FREEZE-FREEZEHAND",
            "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY",
            "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWMERGE",
        ),
        ("time", "shadow", "touch_gesture"),
        "影子分割隔离地面影子，局部冻结锁住选定时间，帧延迟让影子继续以旧姿态移动并由影子重渲染补光",
        "人物继续移动时影子会停留在过去，随后以延迟姿态追上并在接触点重新贴回主体",
        "预览只冻结影子区域并保留短延迟队列，边界采用软遮罩避免人物脚底出现硬切",
        "录制后重建影子历史、地面受光方向和合并时刻，细化脚底接触与影子边缘的时序连续性",
        "走廊或夕阳场景中把影子变成会迟到、会回家的第二个角色",
        (
        {
    "recipe_id": "RECIPE-FREEZE-SHADOW-V1",
    "name_zh": "冻结影子时间窗·迟到影子",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-FREEZE-FREEZEHAND",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWMERGE",
        "FX-TIME-EDITING-LOOP-LOOPBEAT"
    ],
    "trigger_logic": "人物迈出第一步而影子区域仍被稳定分割",
    "combined_effect": "影子停在起步前的位置，经过两拍延迟后沿人物旧姿态追到脚下并重新贴合",
    "why_new": "冻结、延迟和接触合并形成完整角色行为，影子不是简单复制人物",
    "preview_behavior": "预览只冻结影子区域并保留短延迟队列，边界采用软遮罩避免人物脚底出现硬切。针对迟到影子，取景器先在“人物迈出第一步而影子区域仍被稳定分割”发生前标出候选轨迹，确认后才显示“影子停在起步前的位置，经过两拍延迟后沿人物旧姿态追到脚下并重新贴合”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建影子历史、地面受光方向和合并时刻，细化脚底接触与影子边缘的时序连续性。录后以“人物迈出第一步而影子区域仍被稳定分割”的首帧为时间锚，重新计算迟到影子涉及的遮挡和深度，使“影子停在起步前的位置，经过两拍延迟后沿人物旧姿态追到脚下并重新贴合”在原分辨率下保持连续；检测到地面阴影不完整时影子会断裂，退化为脚边短轮廓时仅修补低置信度片段。",
    "risks": [
        "地面阴影不完整时影子会断裂，退化为脚边短轮廓"
    ],
    "target_scenarios": [
        "舞蹈排练室的全身固定机位适合拍摄迟到影子：先让主体完成“人物迈出第一步而影子区域仍被稳定分割”，随后缓慢移动手机观察“影子停在起步前的位置，经过两拍延迟后沿人物旧姿态追到脚下并重新贴合”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-FREEZE-SHADOW-V2",
    "name_zh": "冻结影子时间窗·反向迈步",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-FREEZE-FREEZEHAND",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWMERGE",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "人物向前走三步后在影子边缘做一次反向动作",
    "combined_effect": "影子先按旧方向追赶，再把最后一步反向回放，人物与影子短暂面对面",
    "why_new": "延迟队列和动作反相在同一影子层中交替，产生主体与过去动作的对话",
    "preview_behavior": "移动端预览从反向迈步的结果层反推触发：屏幕持续保留对象身份和最近历史，当“人物向前走三步后在影子边缘做一次反向动作”成立时，把“影子先按旧方向追赶，再把最后一步反向回放，人物与影子短暂面对面”分成进入、保持、退场三段显示。若出现反向动作幅度过大可能穿出地面，限制在影子掩码内，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把反向迈步拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“人物向前走三步后在影子边缘做一次反向动作”，再细化“影子先按旧方向追赶，再把最后一步反向回放，人物与影子短暂面对面”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "反向动作幅度过大可能穿出地面，限制在影子掩码内"
    ],
    "target_scenarios": [
        "在街头跑跳动作的侧向跟拍使用反向迈步。镜头从未触发状态开始横向移动，人物或物体执行“人物向前走三步后在影子边缘做一次反向动作”后继续穿过画面，以“影子先按旧方向追赶，再把最后一步反向回放，人物与影子短暂面对面”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-FREEZE-SHADOW-V3",
    "name_zh": "冻结影子时间窗·踩影合并",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-FREEZE-FREEZEHAND",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWMERGE",
        "FX-TIME-EDITING-BORROW-BORROWOBJECT"
    ],
    "trigger_logic": "人物脚尖触碰延迟影子且保持接触半拍",
    "combined_effect": "被踩到的影子区域冻结，其余影子继续延迟移动，接触点逐步把两者吸回同一姿态",
    "why_new": "触碰点成为局部时间同步门，合并不是全画面同时回到当前帧",
    "preview_behavior": "拍摄者先看到踩影合并所需的对象边界、方向箭头和时间门；“人物脚尖触碰延迟影子且保持接触半拍”被连续确认后，预览按由近到远的层次展开“被踩到的影子区域冻结，其余影子继续延迟移动，接触点逐步把两者吸回同一姿态”。人物继续移动时影子会停留在过去，随后以延迟姿态追上并在接触点重新贴回主体，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验踩影合并的身份链与事件顺序，再按影子分割隔离地面影子，局部冻结锁住选定时间，帧延迟让影子继续以旧姿态移动并由影子重渲染补光重建组件关系。“被踩到的影子区域冻结，其余影子继续延迟移动，接触点逐步把两者吸回同一姿态”使用完整历史窗口重新渲染，而“人物脚尖触碰延迟影子且保持接触半拍”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "脚部被遮挡时接触点不稳定，改用膝踝连线估计"
    ],
    "target_scenarios": [
        "把踩影合并安排在室内物体拿放的连续长镜头：固定主体身份后执行“人物脚尖触碰延迟影子且保持接触半拍”，拍摄者绕触发点改变观察角度，用“被踩到的影子区域冻结，其余影子继续延迟移动，接触点逐步把两者吸回同一姿态”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-FREEZE-SHADOW-V4",
    "name_zh": "冻结影子时间窗·墙影回声",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-CLONING-ECHOES-DELAYED-CLONE"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-FREEZE-FREEZEHAND",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWMERGE",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER"
    ],
    "trigger_logic": "人物靠近墙面且影子从地面转移到墙面",
    "combined_effect": "墙上的影子保留人物上一动作，地面影子继续延迟追踪，两个影子在墙角处交换时间层",
    "why_new": "影子分割、空间表面和时间延迟一起决定影子分布，形成墙地连续的时间窗",
    "preview_behavior": "为预览墙影回声，系统只更新与“人物靠近墙面且影子从地面转移到墙面”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“墙上的影子保留人物上一动作，地面影子继续延迟追踪，两个影子在墙角处交换时间层”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "墙影回声的后处理从失败点开始：针对“墙角法线估计错误会让影子穿面，降低墙面层的延迟长度”复核掩码、锚点或时间戳，通过后才将“墙上的影子保留人物上一动作，地面影子继续延迟追踪，两个影子在墙角处交换时间层”提升到成片质量。触发逻辑“人物靠近墙面且影子从地面转移到墙面”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "墙角法线估计错误会让影子穿面，降低墙面层的延迟长度"
    ],
    "target_scenarios": [
        "人物绕柱移动的空间回看可用墙影回声组织一段连续互动。参与者先保持关系稳定，再完成“人物靠近墙面且影子从地面转移到墙面”；镜头不切断，直到“墙上的影子保留人物上一动作，地面影子继续延迟追踪，两个影子在墙角处交换时间层”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-FREEZE-SHADOW-V5",
    "name_zh": "冻结影子时间窗·停步分叉",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-FREEZE-FREEZEHAND",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWMERGE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL"
    ],
    "trigger_logic": "人物突然停下而延迟影子仍有明显速度",
    "combined_effect": "主体停在当前帧，影子分叉成前后两条旧姿态，随后较远的一条反向收回脚下",
    "why_new": "停顿将延迟状态显性化并引入反向回收，影子因此表现出选择过去的动作",
    "preview_behavior": "停步分叉的取景反馈以结束状态为目标：预览先保留真实动作，在“人物突然停下而延迟影子仍有明显速度”完成时快速呈现“主体停在当前帧，影子分叉成前后两条旧姿态，随后较远的一条反向收回脚下”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留停步分叉的完整生命周期。系统逆向检查“主体停在当前帧，影子分叉成前后两条旧姿态，随后较远的一条反向收回脚下”是否回到稳定终态，再从“人物突然停下而延迟影子仍有明显速度”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "停步检测迟滞会产生短暂三叉，使用运动相位确认停顿"
    ],
    "target_scenarios": [
        "以动作回到起点的结尾镜头作为停步分叉的结尾段落：让“人物突然停下而延迟影子仍有明显速度”发生在最后一个动作峰值，保持机位直到“主体停在当前帧，影子分叉成前后两条旧姿态，随后较远的一条反向收回脚下”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "SHADOW-DELAY-REVERSE", "shadow_light", "影子延迟动作反相",
        (
            "ATOM-SEGMENTATION-MASKS-SHADOW",
            "ATOM-TEMPORAL-STATE-FRAME-DELAY",
            "ATOM-TEMPORAL-STATE-TIME-REVERSE",
            "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        ),
        (
            "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWCLOCK",
            "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
            "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        ),
        ("shadow", "time", "action_inverse"),
        "影子分割给出独立合成区域，帧延迟提供过去姿态，局部反转只在影子掩码内回放动作并保持受光方向",
        "主体向前移动时影子会迟到，迟到影子随后把主体刚才的动作倒着演一遍，最后回到脚下",
        "预览使用短延迟队列和影子低分辨率掩码，只有运动阶段稳定时才启用反相回放",
        "录制后在完整影子区域内重建延迟与逆序帧，细化影子接触、墙地投影和动作回放边缘",
        "舞步或走路视频中制造一个只在影子里倒着跳舞的过去自己",
        (
        {
    "recipe_id": "RECIPE-SHADOW-DELAY-REVERSE-V1",
    "name_zh": "影子延迟动作反相·倒走影子",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWCLOCK",
        "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "主体向前迈步且连续捕获到三帧清晰脚步",
    "combined_effect": "影子延迟一拍后反向完成同一脚步，主体与影子朝相反方向短暂错位",
    "why_new": "延迟给出历史素材，反相改变历史动作方向，二者共同创造影子角色",
    "preview_behavior": "预览使用短延迟队列和影子低分辨率掩码，只有运动阶段稳定时才启用反相回放。针对倒走影子，取景器先在“主体向前迈步且连续捕获到三帧清晰脚步”发生前标出候选轨迹，确认后才显示“影子延迟一拍后反向完成同一脚步，主体与影子朝相反方向短暂错位”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后在完整影子区域内重建延迟与逆序帧，细化影子接触、墙地投影和动作回放边缘。录后以“主体向前迈步且连续捕获到三帧清晰脚步”的首帧为时间锚，重新计算倒走影子涉及的遮挡和深度，使“影子延迟一拍后反向完成同一脚步，主体与影子朝相反方向短暂错位”在原分辨率下保持连续；检测到脚步遮挡会导致反相脚踝穿插，降低脚端透明度时仅修补低置信度片段。",
    "risks": [
        "脚步遮挡会导致反相脚踝穿插，降低脚端透明度"
    ],
    "target_scenarios": [
        "低角度夕阳下的人影全景适合拍摄倒走影子：先让主体完成“主体向前迈步且连续捕获到三帧清晰脚步”，随后缓慢移动手机观察“影子延迟一拍后反向完成同一脚步，主体与影子朝相反方向短暂错位”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-DELAY-REVERSE-V2",
    "name_zh": "影子延迟动作反相·挥手回卷",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWCLOCK",
        "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-LONG-LONGBEAT"
    ],
    "trigger_logic": "主体挥手结束并停住手腕",
    "combined_effect": "影子先慢半拍完成挥手，再从最高点倒序回卷到垂下位置，主体保持静止",
    "why_new": "主体停顿让影子的旧动作独立播放，反转窗口由手腕阶段而不是整段视频决定",
    "preview_behavior": "移动端预览从挥手回卷的结果层反推触发：屏幕持续保留对象身份和最近历史，当“主体挥手结束并停住手腕”成立时，把“影子先慢半拍完成挥手，再从最高点倒序回卷到垂下位置，主体保持静止”分成进入、保持、退场三段显示。若出现手腕追踪丢失会截断回卷，使用肩肘方向补估，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把挥手回卷拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“主体挥手结束并停住手腕”，再细化“影子先慢半拍完成挥手，再从最高点倒序回卷到垂下位置，主体保持静止”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "手腕追踪丢失会截断回卷，使用肩肘方向补估"
    ],
    "target_scenarios": [
        "在墙地交界处的侧向移动镜头使用挥手回卷。镜头从未触发状态开始横向移动，人物或物体执行“主体挥手结束并停住手腕”后继续穿过画面，以“影子先慢半拍完成挥手，再从最高点倒序回卷到垂下位置，主体保持静止”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-DELAY-REVERSE-V3",
    "name_zh": "影子延迟动作反相·跳跃逆落",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWCLOCK",
        "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY"
    ],
    "trigger_logic": "主体完成跳跃并落地，影子在落地前保持延迟",
    "combined_effect": "影子从落地姿态反向回到空中最高点，再以淡化轮廓回到脚下",
    "why_new": "局部反转只作用于影子运动峰值，视觉上形成违背主体重力的影子轨迹",
    "preview_behavior": "拍摄者先看到跳跃逆落所需的对象边界、方向箭头和时间门；“主体完成跳跃并落地，影子在落地前保持延迟”被连续确认后，预览按由近到远的层次展开“影子从落地姿态反向回到空中最高点，再以淡化轮廓回到脚下”。主体向前移动时影子会迟到，迟到影子随后把主体刚才的动作倒着演一遍，最后回到脚下，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验跳跃逆落的身份链与事件顺序，再按影子分割给出独立合成区域，帧延迟提供过去姿态，局部反转只在影子掩码内回放动作并保持受光方向重建组件关系。“影子从落地姿态反向回到空中最高点，再以淡化轮廓回到脚下”使用完整历史窗口重新渲染，而“主体完成跳跃并落地，影子在落地前保持延迟”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "影子接触面不稳定时会漂浮，限制最高点高度"
    ],
    "target_scenarios": [
        "把跳跃逆落安排在舞台追光中的人物独舞：固定主体身份后执行“主体完成跳跃并落地，影子在落地前保持延迟”，拍摄者绕触发点改变观察角度，用“影子从落地姿态反向回到空中最高点，再以淡化轮廓回到脚下”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-DELAY-REVERSE-V4",
    "name_zh": "影子延迟动作反相·双影辩论",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-CLONING-ECHOES-MOTION-AFTERIMAGE"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWCLOCK",
        "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "主体左右摆头两次且影子分割置信度稳定",
    "combined_effect": "延迟影子先反向摆向左，再由另一层影子反向摆向右，两个影子在主体两侧对看",
    "why_new": "动作反相后的两个时间片被分成对话双方，影子层具有角色关系而非一条残影",
    "preview_behavior": "为预览双影辩论，系统只更新与“主体左右摆头两次且影子分割置信度稳定”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“延迟影子先反向摆向左，再由另一层影子反向摆向右，两个影子在主体两侧对看”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "双影辩论的后处理从失败点开始：针对“两层影子过近会粘连，增加最小分离距离”复核掩码、锚点或时间戳，通过后才将“延迟影子先反向摆向左，再由另一层影子反向摆向右，两个影子在主体两侧对看”提升到成片质量。触发逻辑“主体左右摆头两次且影子分割置信度稳定”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "两层影子过近会粘连，增加最小分离距离"
    ],
    "target_scenarios": [
        "两人影子发生接触的地面俯拍可用双影辩论组织一段连续互动。参与者先保持关系稳定，再完成“主体左右摆头两次且影子分割置信度稳定”；镜头不切断，直到“延迟影子先反向摆向左，再由另一层影子反向摆向右，两个影子在主体两侧对看”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-DELAY-REVERSE-V5",
    "name_zh": "影子延迟动作反相·回到脚下",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-CLONING-ECHOES-SHADOW-DOUBLE"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWCLOCK",
        "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE"
    ],
    "trigger_logic": "用户向后走回原位置并在影子上停步",
    "combined_effect": "所有延迟与逆序动作按时间反向压缩，影子边缘从远处收回到脚底并熄灭",
    "why_new": "回到原位成为逆序时间线的终止条件，让效果由用户动作完成闭环",
    "preview_behavior": "回到脚下的取景反馈以结束状态为目标：预览先保留真实动作，在“用户向后走回原位置并在影子上停步”完成时快速呈现“所有延迟与逆序动作按时间反向压缩，影子边缘从远处收回到脚底并熄灭”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留回到脚下的完整生命周期。系统逆向检查“所有延迟与逆序动作按时间反向压缩，影子边缘从远处收回到脚底并熄灭”是否回到稳定终态，再从“用户向后走回原位置并在影子上停步”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "原位置漂移会留下残影，使用最近锚点完成收束"
    ],
    "target_scenarios": [
        "以人物停步后影子收回的结尾作为回到脚下的结尾段落：让“用户向后走回原位置并在影子上停步”发生在最后一个动作峰值，保持机位直到“所有延迟与逆序动作按时间反向压缩，影子边缘从远处收回到脚底并熄灭”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "SHADOW-RIM-BEAT", "shadow_light", "节拍影子轮廓光",
        (
            "ATOM-SEGMENTATION-MASKS-SHADOW",
            "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT",
            "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
            "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        ),
        (
            "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT",
            "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWBEAT",
            "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        ),
        ("shadow", "sound", "body_pose"),
        "影子掩码限制受光范围，虚拟轮廓光定义方向，节拍相位控制影子翻面与人体轮廓光的同步扩张",
        "每个强拍都让影子短暂翻面并把轮廓光推到新方向，主体动作被夹在两次虚拟受光之间",
        "预览只渲染影子低频轮廓和强拍脉冲，拍间保留基础受光以避免画面跳黑",
        "录制后重算每个节拍的影子方向、轮廓光遮挡和动作峰值，细化拍间过渡与边缘颜色",
        "舞台或日落人像中让影子随着音乐完成一次有方向的换光",
        (
        {
    "recipe_id": "RECIPE-SHADOW-RIM-BEAT-V1",
    "name_zh": "节拍影子轮廓光·翻面强拍",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "检测到强拍且主体轮廓保持稳定两帧",
    "combined_effect": "影子在强拍瞬间翻到主体另一侧，轮廓光沿新侧面扩张并在拍间回落",
    "why_new": "影子方向改变和轮廓光扩张共享拍点，形成明确的空间翻面动作",
    "preview_behavior": "预览只渲染影子低频轮廓和强拍脉冲，拍间保留基础受光以避免画面跳黑。针对翻面强拍，取景器先在“检测到强拍且主体轮廓保持稳定两帧”发生前标出候选轨迹，确认后才显示“影子在强拍瞬间翻到主体另一侧，轮廓光沿新侧面扩张并在拍间回落”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重算每个节拍的影子方向、轮廓光遮挡和动作峰值，细化拍间过渡与边缘颜色。录后以“检测到强拍且主体轮廓保持稳定两帧”的首帧为时间锚，重新计算翻面强拍涉及的遮挡和深度，使“影子在强拍瞬间翻到主体另一侧，轮廓光沿新侧面扩张并在拍间回落”在原分辨率下保持连续；检测到强拍过密会造成影子闪翻，限制最小拍间隔时仅修补低置信度片段。",
    "risks": [
        "强拍过密会造成影子闪翻，限制最小拍间隔"
    ],
    "target_scenarios": [
        "低角度夕阳下的人影全景适合拍摄翻面强拍：先让主体完成“检测到强拍且主体轮廓保持稳定两帧”，随后缓慢移动手机观察“影子在强拍瞬间翻到主体另一侧，轮廓光沿新侧面扩张并在拍间回落”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-RIM-BEAT-V2",
    "name_zh": "节拍影子轮廓光·肩线闪耀",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-LONG-LONGBEAT"
    ],
    "trigger_logic": "肩线动作峰值与音乐强拍同时出现",
    "combined_effect": "肩部轮廓光在峰值处变亮，影子边缘向肩线反向拉长，形成一条对称的光影扇",
    "why_new": "身体动作峰值决定形状，节拍只决定释放时刻，结果不会退化为音乐频闪",
    "preview_behavior": "移动端预览从肩线闪耀的结果层反推触发：屏幕持续保留对象身份和最近历史，当“肩线动作峰值与音乐强拍同时出现”成立时，把“肩部轮廓光在峰值处变亮，影子边缘向肩线反向拉长，形成一条对称的光影扇”分成进入、保持、退场三段显示。若出现肩部遮挡会让扇形断开，使用人体轮廓补齐短缺口，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把肩线闪耀拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“肩线动作峰值与音乐强拍同时出现”，再细化“肩部轮廓光在峰值处变亮，影子边缘向肩线反向拉长，形成一条对称的光影扇”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "肩部遮挡会让扇形断开，使用人体轮廓补齐短缺口"
    ],
    "target_scenarios": [
        "在墙地交界处的侧向移动镜头使用肩线闪耀。镜头从未触发状态开始横向移动，人物或物体执行“肩线动作峰值与音乐强拍同时出现”后继续穿过画面，以“肩部轮廓光在峰值处变亮，影子边缘向肩线反向拉长，形成一条对称的光影扇”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-RIM-BEAT-V3",
    "name_zh": "节拍影子轮廓光·脚下换位",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY"
    ],
    "trigger_logic": "脚步在强拍前后交换支撑脚",
    "combined_effect": "支撑脚影子先冻结，强拍后另一侧影子亮起并带出短轮廓光，像影子完成换位",
    "why_new": "动作阶段和影子受光共同表达支撑脚转换，音乐成为动作结构而非背景音",
    "preview_behavior": "拍摄者先看到脚下换位所需的对象边界、方向箭头和时间门；“脚步在强拍前后交换支撑脚”被连续确认后，预览按由近到远的层次展开“支撑脚影子先冻结，强拍后另一侧影子亮起并带出短轮廓光，像影子完成换位”。每个强拍都让影子短暂翻面并把轮廓光推到新方向，主体动作被夹在两次虚拟受光之间，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验脚下换位的身份链与事件顺序，再按影子掩码限制受光范围，虚拟轮廓光定义方向，节拍相位控制影子翻面与人体轮廓光的同步扩张重建组件关系。“支撑脚影子先冻结，强拍后另一侧影子亮起并带出短轮廓光，像影子完成换位”使用完整历史窗口重新渲染，而“脚步在强拍前后交换支撑脚”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "脚步检测不稳会重复换位，使用骨盆速度确认"
    ],
    "target_scenarios": [
        "把脚下换位安排在舞台追光中的人物独舞：固定主体身份后执行“脚步在强拍前后交换支撑脚”，拍摄者绕触发点改变观察角度，用“支撑脚影子先冻结，强拍后另一侧影子亮起并带出短轮廓光，像影子完成换位”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-RIM-BEAT-V4",
    "name_zh": "节拍影子轮廓光·日落三色",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE"
    ],
    "trigger_logic": "连续三个强拍到来且人物头肩方向不变",
    "combined_effect": "三拍分别把影子边缘和轮廓光染成金、红、紫，颜色沿影子长度渐变而不是覆盖主体",
    "why_new": "节拍序号、影子长度和受光方向共同决定颜色空间，保留日落的方向感",
    "preview_behavior": "为预览日落三色，系统只更新与“连续三个强拍到来且人物头肩方向不变”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“三拍分别把影子边缘和轮廓光染成金、红、紫，颜色沿影子长度渐变而不是覆盖主体”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "日落三色的后处理从失败点开始：针对“颜色叠加可能过饱和，限制影子层最大亮度”复核掩码、锚点或时间戳，通过后才将“三拍分别把影子边缘和轮廓光染成金、红、紫，颜色沿影子长度渐变而不是覆盖主体”提升到成片质量。触发逻辑“连续三个强拍到来且人物头肩方向不变”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "颜色叠加可能过饱和，限制影子层最大亮度"
    ],
    "target_scenarios": [
        "两人影子发生接触的地面俯拍可用日落三色组织一段连续互动。参与者先保持关系稳定，再完成“连续三个强拍到来且人物头肩方向不变”；镜头不切断，直到“三拍分别把影子边缘和轮廓光染成金、红、紫，颜色沿影子长度渐变而不是覆盖主体”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-RIM-BEAT-V5",
    "name_zh": "节拍影子轮廓光·反向追光",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-LIGHT-TRAILS-OPTICS-FINGER-REVERSE"
    ],
    "trigger_logic": "强拍后主体突然转身，虚拟轮廓光收到新的身体侧面",
    "combined_effect": "轮廓光先追向转身前方向，下一拍才跳到新方向，影子在两拍之间留下一个延迟轮廓",
    "why_new": "转身延迟和节拍门控让追光看起来有惯性，影子承担了转身过程的时间证据",
    "preview_behavior": "反向追光的取景反馈以结束状态为目标：预览先保留真实动作，在“强拍后主体突然转身，虚拟轮廓光收到新的身体侧面”完成时快速呈现“轮廓光先追向转身前方向，下一拍才跳到新方向，影子在两拍之间留下一个延迟轮廓”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留反向追光的完整生命周期。系统逆向检查“轮廓光先追向转身前方向，下一拍才跳到新方向，影子在两拍之间留下一个延迟轮廓”是否回到稳定终态，再从“强拍后主体突然转身，虚拟轮廓光收到新的身体侧面”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "转身过快会错配侧面，保持上一可信法线一拍"
    ],
    "target_scenarios": [
        "以人物停步后影子收回的结尾作为反向追光的结尾段落：让“强拍后主体突然转身，虚拟轮廓光收到新的身体侧面”发生在最后一个动作峰值，保持机位直到“轮廓光先追向转身前方向，下一拍才跳到新方向，影子在两拍之间留下一个延迟轮廓”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "SHADOW-PORTAL", "shadow_light", "影子门户投影",
        (
            "ATOM-SEGMENTATION-MASKS-SHADOW",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
            "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        ),
        (
            "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENCAST",
            "FX-SPATIAL-PORTALS-FLOOR-FLOORDROP",
            "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENLIGHT",
        ),
        ("shadow", "spatial_portal", "world_anchor"),
        "影子分割提供投影内容，世界锚点固定影子所在表面，门户形变把影子边界折成立体入口",
        "人物影子会从地面或墙面撑开成一扇薄门户，门户内部仍显示影子的受光方向和动作轮廓",
        "预览先用影子轮廓显示门户候选，低分辨率投影只在锚点稳定后短暂打开",
        "录制后细化投影表面、门户厚度、主体遮挡与影子重渲染，保证影子边界不穿过人物",
        "利用墙面或地面影子拍一段像从影子里掉出物体的空间转场",
        (
        {
    "recipe_id": "RECIPE-SHADOW-PORTAL-V1",
    "name_zh": "影子门户投影·地影开门",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENCAST",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORDROP",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENLIGHT",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "人物抬脚时地面影子边缘出现稳定的长轴方向",
    "combined_effect": "长影沿长轴撑开成地面门，脚步落下时门缝被压窄并吐出一片影子碎光",
    "why_new": "影子长度定义门轴、脚步定义门缝变化，投影和动作形成同一空间机关",
    "preview_behavior": "预览先用影子轮廓显示门户候选，低分辨率投影只在锚点稳定后短暂打开。针对地影开门，取景器先在“人物抬脚时地面影子边缘出现稳定的长轴方向”发生前标出候选轨迹，确认后才显示“长影沿长轴撑开成地面门，脚步落下时门缝被压窄并吐出一片影子碎光”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化投影表面、门户厚度、主体遮挡与影子重渲染，保证影子边界不穿过人物。录后以“人物抬脚时地面影子边缘出现稳定的长轴方向”的首帧为时间锚，重新计算地影开门涉及的遮挡和深度，使“长影沿长轴撑开成地面门，脚步落下时门缝被压窄并吐出一片影子碎光”在原分辨率下保持连续；检测到地面法线错误会使门向上翻，回退到平面矩形时仅修补低置信度片段。",
    "risks": [
        "地面法线错误会使门向上翻，回退到平面矩形"
    ],
    "target_scenarios": [
        "低角度夕阳下的人影全景适合拍摄地影开门：先让主体完成“人物抬脚时地面影子边缘出现稳定的长轴方向”，随后缓慢移动手机观察“长影沿长轴撑开成地面门，脚步落下时门缝被压窄并吐出一片影子碎光”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-PORTAL-V2",
    "name_zh": "影子门户投影·墙影投屏",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENCAST",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORDROP",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENLIGHT",
        "FX-VIRTUAL-LIGHT-SHADOW-LONG-LONGBEAT"
    ],
    "trigger_logic": "人物靠近墙面并做出一次明确手势",
    "combined_effect": "墙上影子变成投影幕，手势轨迹在幕面上留下第二层影子，主体动作仍遮住幕边",
    "why_new": "墙影同时承载人物和手势两种历史，门户把投影关系显式化",
    "preview_behavior": "移动端预览从墙影投屏的结果层反推触发：屏幕持续保留对象身份和最近历史，当“人物靠近墙面并做出一次明确手势”成立时，把“墙上影子变成投影幕，手势轨迹在幕面上留下第二层影子，主体动作仍遮住幕边”分成进入、保持、退场三段显示。若出现墙面纹理复杂会干扰幕边，使用影子掩码内缩，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把墙影投屏拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“人物靠近墙面并做出一次明确手势”，再细化“墙上影子变成投影幕，手势轨迹在幕面上留下第二层影子，主体动作仍遮住幕边”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "墙面纹理复杂会干扰幕边，使用影子掩码内缩"
    ],
    "target_scenarios": [
        "在墙地交界处的侧向移动镜头使用墙影投屏。镜头从未触发状态开始横向移动，人物或物体执行“人物靠近墙面并做出一次明确手势”后继续穿过画面，以“墙上影子变成投影幕，手势轨迹在幕面上留下第二层影子，主体动作仍遮住幕边”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-PORTAL-V3",
    "name_zh": "影子门户投影·影子落物",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENCAST",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORDROP",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENLIGHT",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY"
    ],
    "trigger_logic": "用户把一个可跟踪物体举到影子上方并松手",
    "combined_effect": "物体在现实中落下时，影子门户先打开，物体的影子版本先落入门内再与真实物体重合",
    "why_new": "世界锚点连接物体姿态、影子表面和门户时刻，产生影子先行的空间错位",
    "preview_behavior": "拍摄者先看到影子落物所需的对象边界、方向箭头和时间门；“用户把一个可跟踪物体举到影子上方并松手”被连续确认后，预览按由近到远的层次展开“物体在现实中落下时，影子门户先打开，物体的影子版本先落入门内再与真实物体重合”。人物影子会从地面或墙面撑开成一扇薄门户，门户内部仍显示影子的受光方向和动作轮廓，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验影子落物的身份链与事件顺序，再按影子分割提供投影内容，世界锚点固定影子所在表面，门户形变把影子边界折成立体入口重建组件关系。“物体在现实中落下时，影子门户先打开，物体的影子版本先落入门内再与真实物体重合”使用完整历史窗口重新渲染，而“用户把一个可跟踪物体举到影子上方并松手”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "物体跟踪中断会使影子版本消失，保留最后可信落点"
    ],
    "target_scenarios": [
        "把影子落物安排在舞台追光中的人物独舞：固定主体身份后执行“用户把一个可跟踪物体举到影子上方并松手”，拍摄者绕触发点改变观察角度，用“物体在现实中落下时，影子门户先打开，物体的影子版本先落入门内再与真实物体重合”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-PORTAL-V4",
    "name_zh": "影子门户投影·影门折返",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENCAST",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORDROP",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENLIGHT",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "主体沿影子边缘横向移动并回到起点",
    "combined_effect": "影子门随主体移动折叠成窄缝，回到起点时窄缝反向展开并恢复完整影子",
    "why_new": "门的开合由主体和影子的相对运动决定，形成可执行的空间折返动作",
    "preview_behavior": "为预览影门折返，系统只更新与“主体沿影子边缘横向移动并回到起点”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“影子门随主体移动折叠成窄缝，回到起点时窄缝反向展开并恢复完整影子”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "影门折返的后处理从失败点开始：针对“影子边缘断裂会让窄缝跳变，使用上一帧轮廓插值”复核掩码、锚点或时间戳，通过后才将“影子门随主体移动折叠成窄缝，回到起点时窄缝反向展开并恢复完整影子”提升到成片质量。触发逻辑“主体沿影子边缘横向移动并回到起点”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "影子边缘断裂会让窄缝跳变，使用上一帧轮廓插值"
    ],
    "target_scenarios": [
        "两人影子发生接触的地面俯拍可用影门折返组织一段连续互动。参与者先保持关系稳定，再完成“主体沿影子边缘横向移动并回到起点”；镜头不切断，直到“影子门随主体移动折叠成窄缝，回到起点时窄缝反向展开并恢复完整影子”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-PORTAL-V5",
    "name_zh": "影子门户投影·双面投影",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-LIGHT-OPTICS-SHADOW-RERENDER",
        "ATOM-CLONING-ECHOES-MOTION-AFTERIMAGE"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENCAST",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORDROP",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENLIGHT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE"
    ],
    "trigger_logic": "场景中同时出现地影和墙影且两者方向可估计",
    "combined_effect": "地影变成入口，墙影变成出口，人物转身时两个影面通过一条亮边短暂连通",
    "why_new": "两个投影面共享人物身份和世界锚点，门户因此具有入口、出口和方向",
    "preview_behavior": "双面投影的取景反馈以结束状态为目标：预览先保留真实动作，在“场景中同时出现地影和墙影且两者方向可估计”完成时快速呈现“地影变成入口，墙影变成出口，人物转身时两个影面通过一条亮边短暂连通”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留双面投影的完整生命周期。系统逆向检查“地影变成入口，墙影变成出口，人物转身时两个影面通过一条亮边短暂连通”是否回到稳定终态，再从“场景中同时出现地影和墙影且两者方向可估计”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "两面法线冲突会造成连通边穿墙，关闭低置信度的一面"
    ],
    "target_scenarios": [
        "以人物停步后影子收回的结尾作为双面投影的结尾段落：让“场景中同时出现地影和墙影且两者方向可估计”发生在最后一个动作峰值，保持机位直到“地影变成入口，墙影变成出口，人物转身时两个影面通过一条亮边短暂连通”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "SHADOW-TOUCH-ENERGY", "shadow_light", "触碰影子能量",
        (
            "ATOM-SEGMENTATION-MASKS-SHADOW",
            "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
            "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
            "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        ),
        (
            "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWTOUCH",
            "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
            "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        ),
        ("shadow", "multi_person", "touch_gesture"),
        "多人触碰事件把能量从一人的影子接触点传给另一人，三维手部轨迹确定路径，火花粒子沿影子表面传播",
        "两个人不必直接碰到身体，只要触碰彼此的影子，能量粒子就会沿地面影子传递并改变影子姿态",
        "预览用双人影子掩码和手部接触点生成低密度火花，接触确认后才开启完整传递",
        "录制后重建双人关系、影子表面和粒子路径，细化触碰起止、遮挡以及能量回流",
        "双人舞或朋友互动中用踩影、碰影完成一段可见的能量接力",
        (
        {
    "recipe_id": "RECIPE-SHADOW-TOUCH-ENERGY-V1",
    "name_zh": "触碰影子能量·踩影传电",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-TIME-EDITING-REVERSE-REVERSEBEAT"
    ],
    "trigger_logic": "两人的脚步影子接触且多人触碰事件在同一时刻成立",
    "combined_effect": "火花从第一人的影脚沿接触边传到第二人的影脚，第二人的影子短暂抬起并回落",
    "why_new": "触碰事件发生在影子而非身体，粒子路径和影子形变共同证明能量真的跨人传递",
    "preview_behavior": "预览用双人影子掩码和手部接触点生成低密度火花，接触确认后才开启完整传递。针对踩影传电，取景器先在“两人的脚步影子接触且多人触碰事件在同一时刻成立”发生前标出候选轨迹，确认后才显示“火花从第一人的影脚沿接触边传到第二人的影脚，第二人的影子短暂抬起并回落”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建双人关系、影子表面和粒子路径，细化触碰起止、遮挡以及能量回流。录后以“两人的脚步影子接触且多人触碰事件在同一时刻成立”的首帧为时间锚，重新计算踩影传电涉及的遮挡和深度，使“火花从第一人的影脚沿接触边传到第二人的影脚，第二人的影子短暂抬起并回落”在原分辨率下保持连续；检测到脚影重叠过宽会误触发，要求接触区域和脚步方向同时稳定时仅修补低置信度片段。",
    "risks": [
        "脚影重叠过宽会误触发，要求接触区域和脚步方向同时稳定"
    ],
    "target_scenarios": [
        "低角度夕阳下的人影全景适合拍摄踩影传电：先让主体完成“两人的脚步影子接触且多人触碰事件在同一时刻成立”，随后缓慢移动手机观察“火花从第一人的影脚沿接触边传到第二人的影脚，第二人的影子短暂抬起并回落”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-TOUCH-ENERGY-V2",
    "name_zh": "触碰影子能量·手影接球",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-VIRTUAL-LIGHT-SHADOW-LONG-LONGBEAT"
    ],
    "trigger_logic": "一人用手指在影子上点按，另一人伸手接近对应影点",
    "combined_effect": "点按产生一颗影子能量球，沿两人的手部轨迹飞到接收影点并炸成细火花",
    "why_new": "手部三维路径把影点连接成可预测的抛接轨迹，影子承担了球的落点",
    "preview_behavior": "移动端预览从手影接球的结果层反推触发：屏幕持续保留对象身份和最近历史，当“一人用手指在影子上点按，另一人伸手接近对应影点”成立时，把“点按产生一颗影子能量球，沿两人的手部轨迹飞到接收影点并炸成细火花”分成进入、保持、退场三段显示。若出现手部深度错误会让能量球穿地，限制飞行高度，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把手影接球拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“一人用手指在影子上点按，另一人伸手接近对应影点”，再细化“点按产生一颗影子能量球，沿两人的手部轨迹飞到接收影点并炸成细火花”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "手部深度错误会让能量球穿地，限制飞行高度"
    ],
    "target_scenarios": [
        "在墙地交界处的侧向移动镜头使用手影接球。镜头从未触发状态开始横向移动，人物或物体执行“一人用手指在影子上点按，另一人伸手接近对应影点”后继续穿过画面，以“点按产生一颗影子能量球，沿两人的手部轨迹飞到接收影点并炸成细火花”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-TOUCH-ENERGY-V3",
    "name_zh": "触碰影子能量·双向回流",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-VIRTUAL-LIGHT-SHADOW-SCREEN-SCREENDELAY"
    ],
    "trigger_logic": "两人的影子同时触碰后又各自向相反方向收手",
    "combined_effect": "能量先分成两股传开，再沿相反手势回流到两人的脚下，火花在中点短暂交汇",
    "why_new": "同一触碰事件被解释为双向网络流，回流方向由两条手势轨迹共同决定",
    "preview_behavior": "拍摄者先看到双向回流所需的对象边界、方向箭头和时间门；“两人的影子同时触碰后又各自向相反方向收手”被连续确认后，预览按由近到远的层次展开“能量先分成两股传开，再沿相反手势回流到两人的脚下，火花在中点短暂交汇”。两个人不必直接碰到身体，只要触碰彼此的影子，能量粒子就会沿地面影子传递并改变影子姿态，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验双向回流的身份链与事件顺序，再按多人触碰事件把能量从一人的影子接触点传给另一人，三维手部轨迹确定路径，火花粒子沿影子表面传播重建组件关系。“能量先分成两股传开，再沿相反手势回流到两人的脚下，火花在中点短暂交汇”使用完整历史窗口重新渲染，而“两人的影子同时触碰后又各自向相反方向收手”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "两人动作不同步会破坏交汇，保留先到的一股并延迟另一股"
    ],
    "target_scenarios": [
        "把双向回流安排在舞台追光中的人物独舞：固定主体身份后执行“两人的影子同时触碰后又各自向相反方向收手”，拍摄者绕触发点改变观察角度，用“能量先分成两股传开，再沿相反手势回流到两人的脚下，火花在中点短暂交汇”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-TOUCH-ENERGY-V4",
    "name_zh": "触碰影子能量·影子拉链",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-LIGHT-OPTICS-VIRTUAL-RIM-LIGHT"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-VIRTUAL-LIGHT-SHADOW-SUNSET-SUNSETBEAT"
    ],
    "trigger_logic": "两人平行移动并交替触碰对方影子边缘",
    "combined_effect": "每次触碰都拉开一节发光影子拉链，拉链随两人的步伐延展并在最后一次触碰时合拢",
    "why_new": "重复触碰事件产生结构化连接，不是连续粒子喷射，互动节拍可被看见",
    "preview_behavior": "为预览影子拉链，系统只更新与“两人平行移动并交替触碰对方影子边缘”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“每次触碰都拉开一节发光影子拉链，拉链随两人的步伐延展并在最后一次触碰时合拢”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "影子拉链的后处理从失败点开始：针对“触碰频率过高会合并齿节，限制单位时间的连接数”复核掩码、锚点或时间戳，通过后才将“每次触碰都拉开一节发光影子拉链，拉链随两人的步伐延展并在最后一次触碰时合拢”提升到成片质量。触发逻辑“两人平行移动并交替触碰对方影子边缘”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "触碰频率过高会合并齿节，限制单位时间的连接数"
    ],
    "target_scenarios": [
        "两人影子发生接触的地面俯拍可用影子拉链组织一段连续互动。参与者先保持关系稳定，再完成“两人平行移动并交替触碰对方影子边缘”；镜头不切断，直到“每次触碰都拉开一节发光影子拉链，拉链随两人的步伐延展并在最后一次触碰时合拢”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SHADOW-TOUCH-ENERGY-V5",
    "name_zh": "触碰影子能量·能量交换",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-SHADOW",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-PULSE"
    ],
    "trigger_logic": "第一人触碰第二人影子后，第二人反向触碰第一人影子",
    "combined_effect": "第一人的影子先变亮，反向触碰后亮度和火花颜色交换，两个影子恢复同一强度",
    "why_new": "双向触碰改变的是能量归属和颜色，不只是把粒子从一边移动到另一边",
    "preview_behavior": "能量交换的取景反馈以结束状态为目标：预览先保留真实动作，在“第一人触碰第二人影子后，第二人反向触碰第一人影子”完成时快速呈现“第一人的影子先变亮，反向触碰后亮度和火花颜色交换，两个影子恢复同一强度”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留能量交换的完整生命周期。系统逆向检查“第一人的影子先变亮，反向触碰后亮度和火花颜色交换，两个影子恢复同一强度”是否回到稳定终态，再从“第一人触碰第二人影子后，第二人反向触碰第一人影子”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "影子身份交换错误时会出现亮度跳变，使用关系图保持角色 ID"
    ],
    "target_scenarios": [
        "以人物停步后影子收回的结尾作为能量交换的结尾段落：让“第一人触碰第二人影子后，第二人反向触碰第一人影子”发生在最后一个动作峰值，保持机位直到“第一人的影子先变亮，反向触碰后亮度和火花颜色交换，两个影子恢复同一强度”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "LYRIC-MOUTH-RING", "audio_lyrics", "歌词口型空间文字环",
        (
            "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
            "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
            "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
            "ATOM-GEOMETRY-TRACKING-HEAD-POSE",
        ),
        (
            "FX-AUDIO-LYRICS-ORBIT-ORBITTIME",
            "FX-AUDIO-LYRICS-MASK-MASKMOUTH",
            "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT",
        ),
        ("sound", "expression", "world_anchor"),
        "歌词时间戳确定当前字，嘴型位置决定文字环的前后层，头部姿态把文字环放在头肩空间并保持遮挡",
        "歌词字符不再固定在字幕栏，而是沿头肩空间环绕；唱到哪个字，哪个字会贴近口型并改变环的相位",
        "预览只显示当前词和相邻词的低密度环，口型估计稳定时才把当前字推到前景",
        "录制后用精确歌词时间戳、口型峰值和头部姿态重排每个字符的空间轨迹与遮挡",
        "唱歌自拍或对唱录像中让歌词像围绕歌手旋转的可读舞台装置",
        (
        {
    "recipe_id": "RECIPE-LYRIC-MOUTH-RING-V1",
    "name_zh": "歌词口型空间文字环·逐字靠唇",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-ORBIT-ORBITTIME",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT",
        "FX-AUDIO-LYRICS-ORBIT-ORBITBEAT"
    ],
    "trigger_logic": "歌词进入新字时间戳且嘴型从闭合转为张开",
    "combined_effect": "当前字从文字环前侧滑到嘴边并随口型开合放大，唱完后回到环上原位",
    "why_new": "时间戳决定字符身份，嘴型峰值决定靠近和缩放，文字环因此响应实际发音",
    "preview_behavior": "预览只显示当前词和相邻词的低密度环，口型估计稳定时才把当前字推到前景。针对逐字靠唇，取景器先在“歌词进入新字时间戳且嘴型从闭合转为张开”发生前标出候选轨迹，确认后才显示“当前字从文字环前侧滑到嘴边并随口型开合放大，唱完后回到环上原位”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后用精确歌词时间戳、口型峰值和头部姿态重排每个字符的空间轨迹与遮挡。录后以“歌词进入新字时间戳且嘴型从闭合转为张开”的首帧为时间锚，重新计算逐字靠唇涉及的遮挡和深度，使“当前字从文字环前侧滑到嘴边并随口型开合放大，唱完后回到环上原位”在原分辨率下保持连续；检测到歌词与口型错位会使字提前移动，使用相邻时间戳的软对齐时仅修补低置信度片段。",
    "risks": [
        "歌词与口型错位会使字提前移动，使用相邻时间戳的软对齐"
    ],
    "target_scenarios": [
        "单人清唱的脸部中近景适合拍摄逐字靠唇：先让主体完成“歌词进入新字时间戳且嘴型从闭合转为张开”，随后缓慢移动手机观察“当前字从文字环前侧滑到嘴边并随口型开合放大，唱完后回到环上原位”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MOUTH-RING-V2",
    "name_zh": "歌词口型空间文字环·副歌扩环",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-ORBIT-ORBITTIME",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONBEAT"
    ],
    "trigger_logic": "歌词进入副歌段且头部向一侧转动",
    "combined_effect": "副歌字符沿头部转向扩成更大的空间环，当前字在环前方短暂停留后继续旋转",
    "why_new": "段落状态控制半径，头部姿态控制环的偏移，文字结构与表演方向绑定",
    "preview_behavior": "移动端预览从副歌扩环的结果层反推触发：屏幕持续保留对象身份和最近历史，当“歌词进入副歌段且头部向一侧转动”成立时，把“副歌字符沿头部转向扩成更大的空间环，当前字在环前方短暂停留后继续旋转”分成进入、保持、退场三段显示。若出现快速转头会让环脱离头肩，按头部速度限制半径增长，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把副歌扩环拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“歌词进入副歌段且头部向一侧转动”，再细化“副歌字符沿头部转向扩成更大的空间环，当前字在环前方短暂停留后继续旋转”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "快速转头会让环脱离头肩，按头部速度限制半径增长"
    ],
    "target_scenarios": [
        "在副歌段落的环绕自拍使用副歌扩环。镜头从未触发状态开始横向移动，人物或物体执行“歌词进入副歌段且头部向一侧转动”后继续穿过画面，以“副歌字符沿头部转向扩成更大的空间环，当前字在环前方短暂停留后继续旋转”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MOUTH-RING-V3",
    "name_zh": "歌词口型空间文字环·口型分层",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-ORBIT-ORBITTIME",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT",
        "FX-AUDIO-LYRICS-SUBTITLE-SUBTIME"
    ],
    "trigger_logic": "检测到连续三个不同嘴型并对应三个歌词时间戳",
    "combined_effect": "三个字符分别位于嘴前、脸侧和头后，嘴型切换时字符依次穿过前后层并留下短光痕",
    "why_new": "口型序列被转译为空间深度序列，歌词可见顺序与发音动作同时被编码",
    "preview_behavior": "拍摄者先看到口型分层所需的对象边界、方向箭头和时间门；“检测到连续三个不同嘴型并对应三个歌词时间戳”被连续确认后，预览按由近到远的层次展开“三个字符分别位于嘴前、脸侧和头后，嘴型切换时字符依次穿过前后层并留下短光痕”。歌词字符不再固定在字幕栏，而是沿头肩空间环绕；唱到哪个字，哪个字会贴近口型并改变环的相位，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验口型分层的身份链与事件顺序，再按歌词时间戳确定当前字，嘴型位置决定文字环的前后层，头部姿态把文字环放在头肩空间并保持遮挡重建组件关系。“三个字符分别位于嘴前、脸侧和头后，嘴型切换时字符依次穿过前后层并留下短光痕”使用完整历史窗口重新渲染，而“检测到连续三个不同嘴型并对应三个歌词时间戳”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "侧脸会丢失后层位置，退回头肩平面并降低深度差"
    ],
    "target_scenarios": [
        "把口型分层安排在双人对唱的交替机位：固定主体身份后执行“检测到连续三个不同嘴型并对应三个歌词时间戳”，拍摄者绕触发点改变观察角度，用“三个字符分别位于嘴前、脸侧和头后，嘴型切换时字符依次穿过前后层并留下短光痕”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MOUTH-RING-V4",
    "name_zh": "歌词口型空间文字环·停顿悬字",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-ORBIT-ORBITTIME",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT",
        "FX-AUDIO-LYRICS-DUET-DUETTOUCH"
    ],
    "trigger_logic": "歌词时间戳进入间奏而嘴型保持闭合",
    "combined_effect": "上一字悬停在口型前方并缓慢自转，环上其余文字继续按上一圈速度移动",
    "why_new": "间奏不再清空字幕，时间戳和嘴型共同决定字符的暂停状态",
    "preview_behavior": "为预览停顿悬字，系统只更新与“歌词时间戳进入间奏而嘴型保持闭合”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“上一字悬停在口型前方并缓慢自转，环上其余文字继续按上一圈速度移动”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "停顿悬字的后处理从失败点开始：针对“间奏过长会遮挡脸部，设置最大悬停时长”复核掩码、锚点或时间戳，通过后才将“上一字悬停在口型前方并缓慢自转，环上其余文字继续按上一圈速度移动”提升到成片质量。触发逻辑“歌词时间戳进入间奏而嘴型保持闭合”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "间奏过长会遮挡脸部，设置最大悬停时长"
    ],
    "target_scenarios": [
        "说唱手势与字幕同框的半身镜头可用停顿悬字组织一段连续互动。参与者先保持关系稳定，再完成“歌词时间戳进入间奏而嘴型保持闭合”；镜头不切断，直到“上一字悬停在口型前方并缓慢自转，环上其余文字继续按上一圈速度移动”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MOUTH-RING-V5",
    "name_zh": "歌词口型空间文字环·回唱反环",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-ORBIT-ORBITTIME",
        "FX-AUDIO-LYRICS-MASK-MASKMOUTH",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICVOICE"
    ],
    "trigger_logic": "用户拖动录后时间游标回到上一句且口型重新匹配",
    "combined_effect": "文字环按逆向顺序回转，字符沿相反方向依次回到嘴边并保持头部遮挡",
    "why_new": "时间游标改变文字环的时序方向，口型匹配防止反向回放变成单纯倒放字幕",
    "preview_behavior": "回唱反环的取景反馈以结束状态为目标：预览先保留真实动作，在“用户拖动录后时间游标回到上一句且口型重新匹配”完成时快速呈现“文字环按逆向顺序回转，字符沿相反方向依次回到嘴边并保持头部遮挡”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留回唱反环的完整生命周期。系统逆向检查“文字环按逆向顺序回转，字符沿相反方向依次回到嘴边并保持头部遮挡”是否回到稳定终态，再从“用户拖动录后时间游标回到上一句且口型重新匹配”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "回放时间戳缺失会让字乱序，使用句级顺序作为后备"
    ],
    "target_scenarios": [
        "以歌曲尾句停声后的静止收束作为回唱反环的结尾段落：让“用户拖动录后时间游标回到上一句且口型重新匹配”发生在最后一个动作峰值，保持机位直到“文字环按逆向顺序回转，字符沿相反方向依次回到嘴边并保持头部遮挡”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "VOICE-MATERIAL", "audio_lyrics", "声压材质融化",
        (
            "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
            "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
            "ATOM-MATERIAL-APPEARANCE-LIQUID",
            "ATOM-PARTICLES-ATMOSPHERE-MUSIC-SPECTRUM",
        ),
        (
            "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
            "FX-MATERIAL-MORPH-METAL-METALMELT",
            "FX-WORLD-STYLE-NEON-NEONVOICE",
        ),
        ("sound", "expression", "material"),
        "音量包络控制液体材质的流速，嘴型决定材质从口部发射的形状，频谱粒子把不同频段映射为不同流色",
        "声音会从口型位置流出可见的液态材质，音量改变流量、频段改变颜色，停声后材质在空间中凝回",
        "预览以音量和低频频谱驱动嘴边少量液体粒子，先显示流向再增加材质高光",
        "录制后重建嘴型边缘、音频频段与液体表面反射，细化停声凝回和人物遮挡",
        "口播、唱歌或喊叫视频中把声音变成会流动又会凝固的材质",
        (
        {
    "recipe_id": "RECIPE-VOICE-MATERIAL-V1",
    "name_zh": "声压材质融化·低声滴落",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-PARTICLES-ATMOSPHERE-MUSIC-SPECTRUM",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-METAL-METALMELT",
        "FX-WORLD-STYLE-NEON-NEONVOICE",
        "FX-AUDIO-LYRICS-ORBIT-ORBITBEAT"
    ],
    "trigger_logic": "说话音量从静音缓慢升到低声且嘴型保持窄开",
    "combined_effect": "一条细液流从嘴边滴落，低频粒子像小水滴附着在液流表面并随停声凝固",
    "why_new": "嘴型决定出口宽度，音量决定流量，频谱粒子提供可识别的声画材质细节",
    "preview_behavior": "预览以音量和低频频谱驱动嘴边少量液体粒子，先显示流向再增加材质高光。针对低声滴落，取景器先在“说话音量从静音缓慢升到低声且嘴型保持窄开”发生前标出候选轨迹，确认后才显示“一条细液流从嘴边滴落，低频粒子像小水滴附着在液流表面并随停声凝固”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建嘴型边缘、音频频段与液体表面反射，细化停声凝回和人物遮挡。录后以“说话音量从静音缓慢升到低声且嘴型保持窄开”的首帧为时间锚，重新计算低声滴落涉及的遮挡和深度，使“一条细液流从嘴边滴落，低频粒子像小水滴附着在液流表面并随停声凝固”在原分辨率下保持连续；检测到嘴部掩码抖动会让液流跳点，限制出口变化速度时仅修补低置信度片段。",
    "risks": [
        "嘴部掩码抖动会让液流跳点，限制出口变化速度"
    ],
    "target_scenarios": [
        "单人清唱的脸部中近景适合拍摄低声滴落：先让主体完成“说话音量从静音缓慢升到低声且嘴型保持窄开”，随后缓慢移动手机观察“一条细液流从嘴边滴落，低频粒子像小水滴附着在液流表面并随停声凝固”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-VOICE-MATERIAL-V2",
    "name_zh": "声压材质融化·高声喷泉",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-PARTICLES-ATMOSPHERE-MUSIC-SPECTRUM",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-METAL-METALMELT",
        "FX-WORLD-STYLE-NEON-NEONVOICE",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONBEAT"
    ],
    "trigger_logic": "音量出现连续上升峰值且嘴型快速张合",
    "combined_effect": "液体从口型喷成短喷泉，频谱颜色沿喷流分段，峰值过后喷泉向下融回肩前空间",
    "why_new": "声音峰值改变的是材质形态和回收方向，不只是让滤镜变亮",
    "preview_behavior": "移动端预览从高声喷泉的结果层反推触发：屏幕持续保留对象身份和最近历史，当“音量出现连续上升峰值且嘴型快速张合”成立时，把“液体从口型喷成短喷泉，频谱颜色沿喷流分段，峰值过后喷泉向下融回肩前空间”分成进入、保持、退场三段显示。若出现高声峰值可能生成过大喷流，设置最大半径并保留脸部清晰度，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把高声喷泉拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“音量出现连续上升峰值且嘴型快速张合”，再细化“液体从口型喷成短喷泉，频谱颜色沿喷流分段，峰值过后喷泉向下融回肩前空间”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "高声峰值可能生成过大喷流，设置最大半径并保留脸部清晰度"
    ],
    "target_scenarios": [
        "在副歌段落的环绕自拍使用高声喷泉。镜头从未触发状态开始横向移动，人物或物体执行“音量出现连续上升峰值且嘴型快速张合”后继续穿过画面，以“液体从口型喷成短喷泉，频谱颜色沿喷流分段，峰值过后喷泉向下融回肩前空间”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-VOICE-MATERIAL-V3",
    "name_zh": "声压材质融化·金属融歌",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-PARTICLES-ATMOSPHERE-MUSIC-SPECTRUM",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-METAL-METALMELT",
        "FX-WORLD-STYLE-NEON-NEONVOICE",
        "FX-AUDIO-LYRICS-SUBTITLE-SUBTIME"
    ],
    "trigger_logic": "人声频谱从低频滑向高频且嘴型持续张开",
    "combined_effect": "嘴边液体先呈金属高光，随频谱上移变成彩色熔融金属丝，闭口后在空中凝成小片",
    "why_new": "频谱方向控制材质相变，嘴型持续时间控制凝固时机，形成可听见的材质叙事",
    "preview_behavior": "拍摄者先看到金属融歌所需的对象边界、方向箭头和时间门；“人声频谱从低频滑向高频且嘴型持续张开”被连续确认后，预览按由近到远的层次展开“嘴边液体先呈金属高光，随频谱上移变成彩色熔融金属丝，闭口后在空中凝成小片”。声音会从口型位置流出可见的液态材质，音量改变流量、频段改变颜色，停声后材质在空间中凝回，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验金属融歌的身份链与事件顺序，再按音量包络控制液体材质的流速，嘴型决定材质从口部发射的形状，频谱粒子把不同频段映射为不同流色重建组件关系。“嘴边液体先呈金属高光，随频谱上移变成彩色熔融金属丝，闭口后在空中凝成小片”使用完整历史窗口重新渲染，而“人声频谱从低频滑向高频且嘴型持续张开”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "高频噪声会误触发相变，要求人声置信度"
    ],
    "target_scenarios": [
        "把金属融歌安排在双人对唱的交替机位：固定主体身份后执行“人声频谱从低频滑向高频且嘴型持续张开”，拍摄者绕触发点改变观察角度，用“嘴边液体先呈金属高光，随频谱上移变成彩色熔融金属丝，闭口后在空中凝成小片”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-VOICE-MATERIAL-V4",
    "name_zh": "声压材质融化·声纹环流",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-PARTICLES-ATMOSPHERE-MUSIC-SPECTRUM",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-METAL-METALMELT",
        "FX-WORLD-STYLE-NEON-NEONVOICE",
        "FX-AUDIO-LYRICS-DUET-DUETTOUCH"
    ],
    "trigger_logic": "用户连续说出三个音节并在每个音节末端短停",
    "combined_effect": "每个音节生成一圈不同厚度的液体声纹，三圈相遇时被频谱粒子穿成螺旋流",
    "why_new": "音节停顿决定环的分段，频谱粒子把独立声纹组合成连续流体结构",
    "preview_behavior": "为预览声纹环流，系统只更新与“用户连续说出三个音节并在每个音节末端短停”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“每个音节生成一圈不同厚度的液体声纹，三圈相遇时被频谱粒子穿成螺旋流”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "声纹环流的后处理从失败点开始：针对“音节边界不清会合并声纹，使用音量谷值切分”复核掩码、锚点或时间戳，通过后才将“每个音节生成一圈不同厚度的液体声纹，三圈相遇时被频谱粒子穿成螺旋流”提升到成片质量。触发逻辑“用户连续说出三个音节并在每个音节末端短停”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "音节边界不清会合并声纹，使用音量谷值切分"
    ],
    "target_scenarios": [
        "说唱手势与字幕同框的半身镜头可用声纹环流组织一段连续互动。参与者先保持关系稳定，再完成“用户连续说出三个音节并在每个音节末端短停”；镜头不切断，直到“每个音节生成一圈不同厚度的液体声纹，三圈相遇时被频谱粒子穿成螺旋流”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-VOICE-MATERIAL-V5",
    "name_zh": "声压材质融化·停声回凝",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-PARTICLES-ATMOSPHERE-MUSIC-SPECTRUM",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-METAL-METALMELT",
        "FX-WORLD-STYLE-NEON-NEONVOICE",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICVOICE"
    ],
    "trigger_logic": "长句结束后音量快速降到静音且嘴型闭合",
    "combined_effect": "所有悬浮液体沿原流线逆向回到嘴边，最后凝成一颗带频谱色环的材质珠",
    "why_new": "停声与闭口共同触发逆向凝回，结束动作保留了声音的空间路径",
    "preview_behavior": "停声回凝的取景反馈以结束状态为目标：预览先保留真实动作，在“长句结束后音量快速降到静音且嘴型闭合”完成时快速呈现“所有悬浮液体沿原流线逆向回到嘴边，最后凝成一颗带频谱色环的材质珠”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留停声回凝的完整生命周期。系统逆向检查“所有悬浮液体沿原流线逆向回到嘴边，最后凝成一颗带频谱色环的材质珠”是否回到稳定终态，再从“长句结束后音量快速降到静音且嘴型闭合”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "残余噪声会阻止凝回，使用静音门限和超时回收"
    ],
    "target_scenarios": [
        "以歌曲尾句停声后的静止收束作为停声回凝的结尾段落：让“长句结束后音量快速降到静音且嘴型闭合”发生在最后一个动作峰值，保持机位直到“所有悬浮液体沿原流线逆向回到嘴边，最后凝成一颗带频谱色环的材质珠”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "BEAT-PARTICLE-MOTION", "audio_lyrics", "节拍动作粒子轨迹",
        (
            "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
            "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
            "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
            "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        ),
        (
            "FX-PARTICLES-WEATHER-RAIN-RAINBEAT",
            "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
            "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBEAT",
        ),
        ("sound", "body_pose", "realtime_light_trail"),
        "节拍相位时钟提供统一拍点，骨骼动作阶段决定粒子发射关节，火花与雨线沿动作轨迹留下短时历史",
        "每个强拍会从动作关节喷出与姿态方向一致的粒子轨迹，拍间粒子下落或回收，构成可跳舞的动态轨道",
        "预览只追踪关键关节和少量粒子，强拍时提高发射密度，拍间用衰减保持动作轮廓",
        "录制后按完整节拍与骨骼历史重排粒子轨迹，细化手脚交叉、雨线深度和节拍回收",
        "舞蹈、街舞或运动视频中让每个动作峰值喷出有方向的粒子",
        (
        {
    "recipe_id": "RECIPE-BEAT-PARTICLE-MOTION-V1",
    "name_zh": "节拍动作粒子轨迹·手腕火花",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBEAT",
        "FX-AUDIO-LYRICS-ORBIT-ORBITBEAT"
    ],
    "trigger_logic": "手腕速度峰值与强拍同时出现",
    "combined_effect": "火花从手腕沿挥动方向喷出，下一拍前逐粒回收成一条细光线",
    "why_new": "关节速度给出方向，节拍给出发射时刻，粒子轨迹因此追随动作而非随机散落",
    "preview_behavior": "预览只追踪关键关节和少量粒子，强拍时提高发射密度，拍间用衰减保持动作轮廓。针对手腕火花，取景器先在“手腕速度峰值与强拍同时出现”发生前标出候选轨迹，确认后才显示“火花从手腕沿挥动方向喷出，下一拍前逐粒回收成一条细光线”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后按完整节拍与骨骼历史重排粒子轨迹，细化手脚交叉、雨线深度和节拍回收。录后以“手腕速度峰值与强拍同时出现”的首帧为时间锚，重新计算手腕火花涉及的遮挡和深度，使“火花从手腕沿挥动方向喷出，下一拍前逐粒回收成一条细光线”在原分辨率下保持连续；检测到手腕遮挡会让火花突然断裂，使用肘腕方向插值时仅修补低置信度片段。",
    "risks": [
        "手腕遮挡会让火花突然断裂，使用肘腕方向插值"
    ],
    "target_scenarios": [
        "单人清唱的脸部中近景适合拍摄手腕火花：先让主体完成“手腕速度峰值与强拍同时出现”，随后缓慢移动手机观察“火花从手腕沿挥动方向喷出，下一拍前逐粒回收成一条细光线”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-BEAT-PARTICLE-MOTION-V2",
    "name_zh": "节拍动作粒子轨迹·脚步雨线",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBEAT",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONBEAT"
    ],
    "trigger_logic": "脚踝连续落地且每次落地都与拍点对齐",
    "combined_effect": "每个脚步落点向下生成一束短雨线，脚步间的雨线按时间顺序连接成地面节奏格",
    "why_new": "脚步事件改变粒子落点，节拍相位保持网格，雨线变成动作记录",
    "preview_behavior": "移动端预览从脚步雨线的结果层反推触发：屏幕持续保留对象身份和最近历史，当“脚踝连续落地且每次落地都与拍点对齐”成立时，把“每个脚步落点向下生成一束短雨线，脚步间的雨线按时间顺序连接成地面节奏格”分成进入、保持、退场三段显示。若出现地面估计错误会让雨线漂浮，限制在脚底平面，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把脚步雨线拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“脚踝连续落地且每次落地都与拍点对齐”，再细化“每个脚步落点向下生成一束短雨线，脚步间的雨线按时间顺序连接成地面节奏格”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "地面估计错误会让雨线漂浮，限制在脚底平面"
    ],
    "target_scenarios": [
        "在副歌段落的环绕自拍使用脚步雨线。镜头从未触发状态开始横向移动，人物或物体执行“脚踝连续落地且每次落地都与拍点对齐”后继续穿过画面，以“每个脚步落点向下生成一束短雨线，脚步间的雨线按时间顺序连接成地面节奏格”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-BEAT-PARTICLE-MOTION-V3",
    "name_zh": "节拍动作粒子轨迹·骨架喷发",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBEAT",
        "FX-AUDIO-LYRICS-SUBTITLE-SUBTIME"
    ],
    "trigger_logic": "身体进入全身动作峰值且强拍持续两拍",
    "combined_effect": "全身关节同时喷出不同颜色火花，火花沿骨骼连接形成一次短暂的发光骨架",
    "why_new": "粒子发射和骨骼拓扑同时出现，粒子不是覆盖而是揭示动作结构",
    "preview_behavior": "拍摄者先看到骨架喷发所需的对象边界、方向箭头和时间门；“身体进入全身动作峰值且强拍持续两拍”被连续确认后，预览按由近到远的层次展开“全身关节同时喷出不同颜色火花，火花沿骨骼连接形成一次短暂的发光骨架”。每个强拍会从动作关节喷出与姿态方向一致的粒子轨迹，拍间粒子下落或回收，构成可跳舞的动态轨道，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验骨架喷发的身份链与事件顺序，再按节拍相位时钟提供统一拍点，骨骼动作阶段决定粒子发射关节，火花与雨线沿动作轨迹留下短时历史重建组件关系。“全身关节同时喷出不同颜色火花，火花沿骨骼连接形成一次短暂的发光骨架”使用完整历史窗口重新渲染，而“身体进入全身动作峰值且强拍持续两拍”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "全身发射过密会遮挡主体，按关节重要性限流"
    ],
    "target_scenarios": [
        "把骨架喷发安排在双人对唱的交替机位：固定主体身份后执行“身体进入全身动作峰值且强拍持续两拍”，拍摄者绕触发点改变观察角度，用“全身关节同时喷出不同颜色火花，火花沿骨骼连接形成一次短暂的发光骨架”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-BEAT-PARTICLE-MOTION-V4",
    "name_zh": "节拍动作粒子轨迹·回拍残响",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBEAT",
        "FX-AUDIO-LYRICS-DUET-DUETTOUCH"
    ],
    "trigger_logic": "强拍结束后动作仍在延续且下一拍被延迟检测",
    "combined_effect": "上一拍的粒子轨迹延迟半拍跟随，下一拍到来时两套轨迹在关节处交错并合并",
    "why_new": "节拍延迟把拍间动作变成可见残响，用户能看见节奏的前后层",
    "preview_behavior": "为预览回拍残响，系统只更新与“强拍结束后动作仍在延续且下一拍被延迟检测”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“上一拍的粒子轨迹延迟半拍跟随，下一拍到来时两套轨迹在关节处交错并合并”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "回拍残响的后处理从失败点开始：针对“节拍抖动会造成双重拍点，使用相位滞回”复核掩码、锚点或时间戳，通过后才将“上一拍的粒子轨迹延迟半拍跟随，下一拍到来时两套轨迹在关节处交错并合并”提升到成片质量。触发逻辑“强拍结束后动作仍在延续且下一拍被延迟检测”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "节拍抖动会造成双重拍点，使用相位滞回"
    ],
    "target_scenarios": [
        "说唱手势与字幕同框的半身镜头可用回拍残响组织一段连续互动。参与者先保持关系稳定，再完成“强拍结束后动作仍在延续且下一拍被延迟检测”；镜头不切断，直到“上一拍的粒子轨迹延迟半拍跟随，下一拍到来时两套轨迹在关节处交错并合并”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-BEAT-PARTICLE-MOTION-V5",
    "name_zh": "节拍动作粒子轨迹·停格喷泉",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BODY-BODYBEAT",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICVOICE"
    ],
    "trigger_logic": "舞者在强拍处定格姿态并保持超过一拍",
    "combined_effect": "关节粒子在定格期间向上形成喷泉，恢复动作后喷泉沿骨骼方向倒流回身体",
    "why_new": "姿态冻结改变粒子生命周期，回流又把定格和运动连接为同一个动作状态",
    "preview_behavior": "停格喷泉的取景反馈以结束状态为目标：预览先保留真实动作，在“舞者在强拍处定格姿态并保持超过一拍”完成时快速呈现“关节粒子在定格期间向上形成喷泉，恢复动作后喷泉沿骨骼方向倒流回身体”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留停格喷泉的完整生命周期。系统逆向检查“关节粒子在定格期间向上形成喷泉，恢复动作后喷泉沿骨骼方向倒流回身体”是否回到稳定终态，再从“舞者在强拍处定格姿态并保持超过一拍”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "定格姿态轻微漂移会使喷泉抖动，锁定骨盆参考"
    ],
    "target_scenarios": [
        "以歌曲尾句停声后的静止收束作为停格喷泉的结尾段落：让“舞者在强拍处定格姿态并保持超过一拍”发生在最后一个动作峰值，保持机位直到“关节粒子在定格期间向上形成喷泉，恢复动作后喷泉沿骨骼方向倒流回身体”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "LYRIC-MULTI-HANDOFF", "audio_lyrics", "多人歌词接唱传球",
        (
            "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
            "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
            "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        ),
        (
            "FX-AUDIO-LYRICS-DUET-DUETHANDOFF",
            "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT",
            "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT",
        ),
        ("sound", "multi_person", "touch_gesture"),
        "歌词时间戳决定接唱球的内容，多人关系图选择下一位歌手，触碰和节拍共同确认传球路径",
        "当前歌词字符包在发光球里，唱段切换时沿关系图传给下一人，触碰或强拍会把球变成可见的歌词环",
        "预览只显示当前字、两个人之间的关系边和简化发光球，确认接唱后才展开文字环",
        "录制后精确对齐歌词、说话人和触碰事件，重排传球弧线、字符遮挡与节拍弹跳",
        "多人合唱或隔屏接唱中用歌词光球表现谁接过了哪一句",
        (
        {
    "recipe_id": "RECIPE-LYRIC-MULTI-HANDOFF-V1",
    "name_zh": "多人歌词接唱传球·逐句传球",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT",
        "FX-AUDIO-LYRICS-ORBIT-ORBITBEAT"
    ],
    "trigger_logic": "歌词进入下一句且关系图识别下一位说话者",
    "combined_effect": "整句歌词压缩成光球沿两人关系边飞行，到达下一人时展开成文字环",
    "why_new": "整句内容、说话人路由和空间传递共同决定球的行为，避免字幕瞬移",
    "preview_behavior": "预览只显示当前字、两个人之间的关系边和简化发光球，确认接唱后才展开文字环。针对逐句传球，取景器先在“歌词进入下一句且关系图识别下一位说话者”发生前标出候选轨迹，确认后才显示“整句歌词压缩成光球沿两人关系边飞行，到达下一人时展开成文字环”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后精确对齐歌词、说话人和触碰事件，重排传球弧线、字符遮挡与节拍弹跳。录后以“歌词进入下一句且关系图识别下一位说话者”的首帧为时间锚，重新计算逐句传球涉及的遮挡和深度，使“整句歌词压缩成光球沿两人关系边飞行，到达下一人时展开成文字环”在原分辨率下保持连续；检测到说话人重叠会让球选错目标，使用音量与脸部位置联合确认时仅修补低置信度片段。",
    "risks": [
        "说话人重叠会让球选错目标，使用音量与脸部位置联合确认"
    ],
    "target_scenarios": [
        "单人清唱的脸部中近景适合拍摄逐句传球：先让主体完成“歌词进入下一句且关系图识别下一位说话者”，随后缓慢移动手机观察“整句歌词压缩成光球沿两人关系边飞行，到达下一人时展开成文字环”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MULTI-HANDOFF-V2",
    "name_zh": "多人歌词接唱传球·触碰接唱",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONBEAT"
    ],
    "trigger_logic": "两人的手部区域在当前歌词字末端发生多人触碰",
    "combined_effect": "当前字从第一人的环上脱离，沿触碰点连接线进入第二人的环并在下一字时换色",
    "why_new": "触碰是歌词交接的明确手势，文字环保留了交接前后的归属",
    "preview_behavior": "移动端预览从触碰接唱的结果层反推触发：屏幕持续保留对象身份和最近历史，当“两人的手部区域在当前歌词字末端发生多人触碰”成立时，把“当前字从第一人的环上脱离，沿触碰点连接线进入第二人的环并在下一字时换色”分成进入、保持、退场三段显示。若出现手部被遮挡时交接会延迟，保留上一位歌词球直到确认，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把触碰接唱拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“两人的手部区域在当前歌词字末端发生多人触碰”，再细化“当前字从第一人的环上脱离，沿触碰点连接线进入第二人的环并在下一字时换色”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "手部被遮挡时交接会延迟，保留上一位歌词球直到确认"
    ],
    "target_scenarios": [
        "在副歌段落的环绕自拍使用触碰接唱。镜头从未触发状态开始横向移动，人物或物体执行“两人的手部区域在当前歌词字末端发生多人触碰”后继续穿过画面，以“当前字从第一人的环上脱离，沿触碰点连接线进入第二人的环并在下一字时换色”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MULTI-HANDOFF-V3",
    "name_zh": "多人歌词接唱传球·副歌分环",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-HEAD-POSE"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT",
        "FX-AUDIO-LYRICS-SUBTITLE-SUBTIME"
    ],
    "trigger_logic": "副歌时间戳到来且三人关系图形成三角连接",
    "combined_effect": "歌词球在三人之间连续跳转，每跳一次分出一圈字符，三圈按拍点同步弹跳",
    "why_new": "多人关系图把副歌结构变成空间网络，分环记录了每次传球历史",
    "preview_behavior": "拍摄者先看到副歌分环所需的对象边界、方向箭头和时间门；“副歌时间戳到来且三人关系图形成三角连接”被连续确认后，预览按由近到远的层次展开“歌词球在三人之间连续跳转，每跳一次分出一圈字符，三圈按拍点同步弹跳”。当前歌词字符包在发光球里，唱段切换时沿关系图传给下一人，触碰或强拍会把球变成可见的歌词环，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验副歌分环的身份链与事件顺序，再按歌词时间戳决定接唱球的内容，多人关系图选择下一位歌手，触碰和节拍共同确认传球路径重建组件关系。“歌词球在三人之间连续跳转，每跳一次分出一圈字符，三圈按拍点同步弹跳”使用完整历史窗口重新渲染，而“副歌时间戳到来且三人关系图形成三角连接”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "三人距离过近会使环重叠，按深度排序错开环面"
    ],
    "target_scenarios": [
        "把副歌分环安排在双人对唱的交替机位：固定主体身份后执行“副歌时间戳到来且三人关系图形成三角连接”，拍摄者绕触发点改变观察角度，用“歌词球在三人之间连续跳转，每跳一次分出一圈字符，三圈按拍点同步弹跳”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MULTI-HANDOFF-V4",
    "name_zh": "多人歌词接唱传球·反向应答",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT",
        "FX-AUDIO-LYRICS-DUET-DUETTOUCH"
    ],
    "trigger_logic": "下一句歌词由上一位歌手重新接回且触碰事件方向相反",
    "combined_effect": "光球沿原路反向飞回并把字符按相反顺序排列，回到原歌手时恢复正序",
    "why_new": "接唱回路改变歌词时间呈现而非只改变移动方向，回声关系清晰可见",
    "preview_behavior": "为预览反向应答，系统只更新与“下一句歌词由上一位歌手重新接回且触碰事件方向相反”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“光球沿原路反向飞回并把字符按相反顺序排列，回到原歌手时恢复正序”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "反向应答的后处理从失败点开始：针对“反向歌词时间戳缺失时使用句内字符倒序”复核掩码、锚点或时间戳，通过后才将“光球沿原路反向飞回并把字符按相反顺序排列，回到原歌手时恢复正序”提升到成片质量。触发逻辑“下一句歌词由上一位歌手重新接回且触碰事件方向相反”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "反向歌词时间戳缺失时使用句内字符倒序"
    ],
    "target_scenarios": [
        "说唱手势与字幕同框的半身镜头可用反向应答组织一段连续互动。参与者先保持关系稳定，再完成“下一句歌词由上一位歌手重新接回且触碰事件方向相反”；镜头不切断，直到“光球沿原路反向飞回并把字符按相反顺序排列，回到原歌手时恢复正序”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-LYRIC-MULTI-HANDOFF-V5",
    "name_zh": "多人歌词接唱传球·空拍悬球",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICVOICE"
    ],
    "trigger_logic": "一句歌词结束而下一句延迟超过一拍",
    "combined_effect": "光球悬在两人关系边中点，节拍每次让它轻弹，下一位开口时再完成传球",
    "why_new": "空拍成为多人互动的可见等待态，歌词内容没有被错误地提前归属",
    "preview_behavior": "空拍悬球的取景反馈以结束状态为目标：预览先保留真实动作，在“一句歌词结束而下一句延迟超过一拍”完成时快速呈现“光球悬在两人关系边中点，节拍每次让它轻弹，下一位开口时再完成传球”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留空拍悬球的完整生命周期。系统逆向检查“光球悬在两人关系边中点，节拍每次让它轻弹，下一位开口时再完成传球”是否回到稳定终态，再从“一句歌词结束而下一句延迟超过一拍”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "长时间无声会让球遮挡主体，超时缩小为单字光点"
    ],
    "target_scenarios": [
        "以歌曲尾句停声后的静止收束作为空拍悬球的结尾段落：让“一句歌词结束而下一句延迟超过一拍”发生在最后一个动作峰值，保持机位直到“光球悬在两人关系边中点，节拍每次让它轻弹，下一位开口时再完成传球”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "GRAPH-TOUCH-ENERGY", "multi_person", "关系图触碰能量粒子",
        (
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
            "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
            "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
            "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        ),
        (
            "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
            "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW",
            "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        ),
        ("multi_person", "touch_gesture", "sound"),
        "多人关系图决定可连接的节点，触碰事件是能量生成门，手部三维轨迹提供传递曲线，火花粒子显示能量状态",
        "多人之间的关系边会在触碰时被点亮，能量沿真实手势轨迹传递、分叉或回流，粒子数量表示连接强度",
        "预览使用关系图和低密度火花，只在触碰确认后生成连接边，避免多人画面常驻线框",
        "录制后重建人物身份、触碰时刻和三维手势曲线，细化能量粒子碰撞、分叉及遮挡",
        "朋友聚会、舞蹈接力或多人挑战中让触碰成为可视化的互动语言",
        (
        {
    "recipe_id": "RECIPE-GRAPH-TOUCH-ENERGY-V1",
    "name_zh": "关系图触碰能量粒子·掌心点火",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT"
    ],
    "trigger_logic": "两人掌部靠近并在同一帧发生触碰确认",
    "combined_effect": "触碰点生成一颗能量核心，火花沿关系边传到两人的肩部并短暂点亮整条边",
    "why_new": "触碰事件决定能量起点，关系图决定传播对象，视觉上真正表达了两人的连接",
    "preview_behavior": "预览使用关系图和低密度火花，只在触碰确认后生成连接边，避免多人画面常驻线框。针对掌心点火，取景器先在“两人掌部靠近并在同一帧发生触碰确认”发生前标出候选轨迹，确认后才显示“触碰点生成一颗能量核心，火花沿关系边传到两人的肩部并短暂点亮整条边”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建人物身份、触碰时刻和三维手势曲线，细化能量粒子碰撞、分叉及遮挡。录后以“两人掌部靠近并在同一帧发生触碰确认”的首帧为时间锚，重新计算掌心点火涉及的遮挡和深度，使“触碰点生成一颗能量核心，火花沿关系边传到两人的肩部并短暂点亮整条边”在原分辨率下保持连续；检测到掌部交叉可能重复点火，设置单次触碰冷却时仅修补低置信度片段。",
    "risks": [
        "掌部交叉可能重复点火，设置单次触碰冷却"
    ],
    "target_scenarios": [
        "两人面对面的全身互动镜头适合拍摄掌心点火：先让主体完成“两人掌部靠近并在同一帧发生触碰确认”，随后缓慢移动手机观察“触碰点生成一颗能量核心，火花沿关系边传到两人的肩部并短暂点亮整条边”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-GRAPH-TOUCH-ENERGY-V2",
    "name_zh": "关系图触碰能量粒子·隔空抛接",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORTOUCH"
    ],
    "trigger_logic": "一人做出向外抛手势，另一人的手部轨迹在目标方向稳定",
    "combined_effect": "能量核心沿抛出手势的三维曲线飞向接收者，接近手掌时分解成环形火花",
    "why_new": "抛出和接收是两个不同手势状态，能量运动因此受双方动作共同约束",
    "preview_behavior": "移动端预览从隔空抛接的结果层反推触发：屏幕持续保留对象身份和最近历史，当“一人做出向外抛手势，另一人的手部轨迹在目标方向稳定”成立时，把“能量核心沿抛出手势的三维曲线飞向接收者，接近手掌时分解成环形火花”分成进入、保持、退场三段显示。若出现接收手移动过快会错过核心，核心在最近可信目标处减速，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把隔空抛接拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“一人做出向外抛手势，另一人的手部轨迹在目标方向稳定”，再细化“能量核心沿抛出手势的三维曲线飞向接收者，接近手掌时分解成环形火花”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "接收手移动过快会错过核心，核心在最近可信目标处减速"
    ],
    "target_scenarios": [
        "在三人围成半圈的固定机位使用隔空抛接。镜头从未触发状态开始横向移动，人物或物体执行“一人做出向外抛手势，另一人的手部轨迹在目标方向稳定”后继续穿过画面，以“能量核心沿抛出手势的三维曲线飞向接收者，接近手掌时分解成环形火花”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-GRAPH-TOUCH-ENERGY-V3",
    "name_zh": "关系图触碰能量粒子·关系分叉",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEPOSE"
    ],
    "trigger_logic": "一个人同时触碰两人的影像区域或两条关系边被连续激活",
    "combined_effect": "单颗核心在节点处分成两股火花，分别沿两条边传递，亮度按关系顺序逐级衰减",
    "why_new": "关系图拓扑决定能量分叉，粒子衰减让多人互动具有可读的网络层次",
    "preview_behavior": "拍摄者先看到关系分叉所需的对象边界、方向箭头和时间门；“一个人同时触碰两人的影像区域或两条关系边被连续激活”被连续确认后，预览按由近到远的层次展开“单颗核心在节点处分成两股火花，分别沿两条边传递，亮度按关系顺序逐级衰减”。多人之间的关系边会在触碰时被点亮，能量沿真实手势轨迹传递、分叉或回流，粒子数量表示连接强度，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验关系分叉的身份链与事件顺序，再按多人关系图决定可连接的节点，触碰事件是能量生成门，手部三维轨迹提供传递曲线，火花粒子显示能量状态重建组件关系。“单颗核心在节点处分成两股火花，分别沿两条边传递，亮度按关系顺序逐级衰减”使用完整历史窗口重新渲染，而“一个人同时触碰两人的影像区域或两条关系边被连续激活”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "边数量过多会造成视觉拥挤，限制每个节点同时激活的边数"
    ],
    "target_scenarios": [
        "把关系分叉安排在朋友接力动作的横向跟拍：固定主体身份后执行“一个人同时触碰两人的影像区域或两条关系边被连续激活”，拍摄者绕触发点改变观察角度，用“单颗核心在节点处分成两股火花，分别沿两条边传递，亮度按关系顺序逐级衰减”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-GRAPH-TOUCH-ENERGY-V4",
    "name_zh": "关系图触碰能量粒子·回流握手",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF"
    ],
    "trigger_logic": "第一人和第二人先后触碰对方区域并在短窗内再次交换方向",
    "combined_effect": "能量沿第一条边传出后反向回流，回流经过的火花变成另一色，最后在两人之间合成握手环",
    "why_new": "方向序列改变粒子颜色与路径，双向互动被编码为回流而不是两次独立触发",
    "preview_behavior": "为预览回流握手，系统只更新与“第一人和第二人先后触碰对方区域并在短窗内再次交换方向”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“能量沿第一条边传出后反向回流，回流经过的火花变成另一色，最后在两人之间合成握手环”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "回流握手的后处理从失败点开始：针对“事件时间窗过长会误把新触碰合并，缩短关系边窗口”复核掩码、锚点或时间戳，通过后才将“能量沿第一条边传出后反向回流，回流经过的火花变成另一色，最后在两人之间合成握手环”提升到成片质量。触发逻辑“第一人和第二人先后触碰对方区域并在短窗内再次交换方向”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "事件时间窗过长会误把新触碰合并，缩短关系边窗口"
    ],
    "target_scenarios": [
        "舞台队形变化的高机位录像可用回流握手组织一段连续互动。参与者先保持关系稳定，再完成“第一人和第二人先后触碰对方区域并在短窗内再次交换方向”；镜头不切断，直到“能量沿第一条边传出后反向回流，回流经过的火花变成另一色，最后在两人之间合成握手环”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-GRAPH-TOUCH-ENERGY-V5",
    "name_zh": "关系图触碰能量粒子·多人接力",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREMIRROR"
    ],
    "trigger_logic": "三人按顺序触碰并保持关系图中的链状排列",
    "combined_effect": "能量核心按链条逐人传递，每次接触都留下一个节点火花，最后三个节点被一条粒子链串起",
    "why_new": "触碰顺序成为空间链路，结果记录了多人互动的过程而非只展示终点",
    "preview_behavior": "多人接力的取景反馈以结束状态为目标：预览先保留真实动作，在“三人按顺序触碰并保持关系图中的链状排列”完成时快速呈现“能量核心按链条逐人传递，每次接触都留下一个节点火花，最后三个节点被一条粒子链串起”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留多人接力的完整生命周期。系统逆向检查“能量核心按链条逐人传递，每次接触都留下一个节点火花，最后三个节点被一条粒子链串起”是否回到稳定终态，再从“三人按顺序触碰并保持关系图中的链状排列”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "中间人出框会断链，保留已点亮节点并等待重新接入"
    ],
    "target_scenarios": [
        "以多人触碰完成后的关系图收束作为多人接力的结尾段落：让“三人按顺序触碰并保持关系图中的链状排列”发生在最后一个动作峰值，保持机位直到“能量核心按链条逐人传递，每次接触都留下一个节点火花，最后三个节点被一条粒子链串起”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "MIRROR-BEAT-LIGHT", "multi_person", "双人节拍镜像光舞",
        (
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
            "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
            "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
            "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        ),
        (
            "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORBEAT",
            "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST",
            "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        ),
        ("multi_person", "sound", "body_pose"),
        "关系图选择镜像搭档，骨骼拓扑比较动作，节拍触发同步窗口，动态星芒和追光圈标记谁在领舞",
        "两人不必完全同步，节拍会在两人的动作差异上生成镜像光束，领舞者的追光圈在关系图中移交",
        "预览只比较关键骨骼和主拍点，用少量星芒标出动作差分并限制追光切换频率",
        "录制后重建两套骨骼、节拍相位和领舞交接，细化镜像偏差光束与人物遮挡",
        "双人舞或合拍挑战中把同步、错拍和领舞变化做成可见光舞",
        (
        {
    "recipe_id": "RECIPE-MIRROR-BEAT-LIGHT-V1",
    "name_zh": "双人节拍镜像光舞·同拍星芒",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW"
    ],
    "trigger_logic": "两人同一拍完成相似抬臂动作",
    "combined_effect": "两套手臂骨骼在空中合成一颗双核星芒，星芒沿两人之间的关系边闪出对称光束",
    "why_new": "动作相似度决定双核是否合成，关系边把同步结果放在两人之间",
    "preview_behavior": "预览只比较关键骨骼和主拍点，用少量星芒标出动作差分并限制追光切换频率。针对同拍星芒，取景器先在“两人同一拍完成相似抬臂动作”发生前标出候选轨迹，确认后才显示“两套手臂骨骼在空中合成一颗双核星芒，星芒沿两人之间的关系边闪出对称光束”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建两套骨骼、节拍相位和领舞交接，细化镜像偏差光束与人物遮挡。录后以“两人同一拍完成相似抬臂动作”的首帧为时间锚，重新计算同拍星芒涉及的遮挡和深度，使“两套手臂骨骼在空中合成一颗双核星芒，星芒沿两人之间的关系边闪出对称光束”在原分辨率下保持连续；检测到骨骼角度差异过大时星芒会分裂，使用角度阈值控制合成时仅修补低置信度片段。",
    "risks": [
        "骨骼角度差异过大时星芒会分裂，使用角度阈值控制合成"
    ],
    "target_scenarios": [
        "两人面对面的全身互动镜头适合拍摄同拍星芒：先让主体完成“两人同一拍完成相似抬臂动作”，随后缓慢移动手机观察“两套手臂骨骼在空中合成一颗双核星芒，星芒沿两人之间的关系边闪出对称光束”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-MIRROR-BEAT-LIGHT-V2",
    "name_zh": "双人节拍镜像光舞·错拍闪线",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT"
    ],
    "trigger_logic": "一人提前半拍完成动作而另一人仍在上一姿态",
    "combined_effect": "提前者获得短追光，错拍方向被一条反向星芒线标出，下一拍两条线交汇",
    "why_new": "节拍相位和姿态差分共同显示错拍来源，避免把所有人都做成同色闪光",
    "preview_behavior": "移动端预览从错拍闪线的结果层反推触发：屏幕持续保留对象身份和最近历史，当“一人提前半拍完成动作而另一人仍在上一姿态”成立时，把“提前者获得短追光，错拍方向被一条反向星芒线标出，下一拍两条线交汇”分成进入、保持、退场三段显示。若出现节拍漂移会放大误差，使用局部相位估计，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把错拍闪线拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“一人提前半拍完成动作而另一人仍在上一姿态”，再细化“提前者获得短追光，错拍方向被一条反向星芒线标出，下一拍两条线交汇”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "节拍漂移会放大误差，使用局部相位估计"
    ],
    "target_scenarios": [
        "在三人围成半圈的固定机位使用错拍闪线。镜头从未触发状态开始横向移动，人物或物体执行“一人提前半拍完成动作而另一人仍在上一姿态”后继续穿过画面，以“提前者获得短追光，错拍方向被一条反向星芒线标出，下一拍两条线交汇”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-MIRROR-BEAT-LIGHT-V3",
    "name_zh": "双人节拍镜像光舞·领舞移交",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORTOUCH"
    ],
    "trigger_logic": "领舞者完成一个动作峰值后另一人接续同方向动作",
    "combined_effect": "追光圈在峰值时从第一人切换到第二人，星芒沿关系边传递并保留一拍尾光",
    "why_new": "领舞不是固定角色，而由动作峰值和接续关系共同决定",
    "preview_behavior": "拍摄者先看到领舞移交所需的对象边界、方向箭头和时间门；“领舞者完成一个动作峰值后另一人接续同方向动作”被连续确认后，预览按由近到远的层次展开“追光圈在峰值时从第一人切换到第二人，星芒沿关系边传递并保留一拍尾光”。两人不必完全同步，节拍会在两人的动作差异上生成镜像光束，领舞者的追光圈在关系图中移交，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验领舞移交的身份链与事件顺序，再按关系图选择镜像搭档，骨骼拓扑比较动作，节拍触发同步窗口，动态星芒和追光圈标记谁在领舞重建组件关系。“追光圈在峰值时从第一人切换到第二人，星芒沿关系边传递并保留一拍尾光”使用完整历史窗口重新渲染，而“领舞者完成一个动作峰值后另一人接续同方向动作”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "同时峰值会导致追光竞争，按动作置信度择一并保留边缘光"
    ],
    "target_scenarios": [
        "把领舞移交安排在朋友接力动作的横向跟拍：固定主体身份后执行“领舞者完成一个动作峰值后另一人接续同方向动作”，拍摄者绕触发点改变观察角度，用“追光圈在峰值时从第一人切换到第二人，星芒沿关系边传递并保留一拍尾光”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-MIRROR-BEAT-LIGHT-V4",
    "name_zh": "双人节拍镜像光舞·反向镜舞",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEPOSE"
    ],
    "trigger_logic": "两人面对面做相反方向的手势且强拍成立",
    "combined_effect": "镜像骨骼被翻到对方空间，反向手势形成交叉星芒，交叉点在强拍时爆亮",
    "why_new": "关系图和骨骼镜像共同决定交叉点，视觉呈现两人共享一面看不见的镜子",
    "preview_behavior": "为预览反向镜舞，系统只更新与“两人面对面做相反方向的手势且强拍成立”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“镜像骨骼被翻到对方空间，反向手势形成交叉星芒，交叉点在强拍时爆亮”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "反向镜舞的后处理从失败点开始：针对“面对方向估计错误会把镜像翻错，使用肩线和脸朝向联合判断”复核掩码、锚点或时间戳，通过后才将“镜像骨骼被翻到对方空间，反向手势形成交叉星芒，交叉点在强拍时爆亮”提升到成片质量。触发逻辑“两人面对面做相反方向的手势且强拍成立”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "面对方向估计错误会把镜像翻错，使用肩线和脸朝向联合判断"
    ],
    "target_scenarios": [
        "舞台队形变化的高机位录像可用反向镜舞组织一段连续互动。参与者先保持关系稳定，再完成“两人面对面做相反方向的手势且强拍成立”；镜头不切断，直到“镜像骨骼被翻到对方空间，反向手势形成交叉星芒，交叉点在强拍时爆亮”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-MIRROR-BEAT-LIGHT-V5",
    "name_zh": "双人节拍镜像光舞·散场余光",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORBEAT",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-BURST",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF"
    ],
    "trigger_logic": "音乐段落结束且两人向相反方向离开",
    "combined_effect": "追光圈分别缩小为两颗星点，沿各自离开方向留下不同长度的尾光后熄灭",
    "why_new": "段落结束改变互动拓扑，余光长度记录两人的离场动作差异",
    "preview_behavior": "散场余光的取景反馈以结束状态为目标：预览先保留真实动作，在“音乐段落结束且两人向相反方向离开”完成时快速呈现“追光圈分别缩小为两颗星点，沿各自离开方向留下不同长度的尾光后熄灭”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留散场余光的完整生命周期。系统逆向检查“追光圈分别缩小为两颗星点，沿各自离开方向留下不同长度的尾光后熄灭”是否回到稳定终态，再从“音乐段落结束且两人向相反方向离开”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "人物快速出框会截断尾光，使用最后速度方向补齐短尾"
    ],
    "target_scenarios": [
        "以多人触碰完成后的关系图收束作为散场余光的结尾段落：让“音乐段落结束且两人向相反方向离开”发生在最后一个动作峰值，保持机位直到“追光圈分别缩小为两颗星点，沿各自离开方向留下不同长度的尾光后熄灭”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "TRIO-STATUE-TIME", "multi_person", "三人队形时间雕像",
        (
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
            "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
            "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
            "ATOM-CLONING-ECHOES-POSE-SLICES",
        ),
        (
            "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEFREEZE",
            "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEBEAT",
            "FX-BODY-MOTION-CLONES-POSE-POSEDEPTH",
        ),
        ("multi_person", "time", "body_pose"),
        "多人关系图维护队形拓扑，骨骼姿态组成雕像，局部冻结锁住成形瞬间，姿态切片把三人放入不同时间深度",
        "三人动作会在队形成立时冻结成一座有前后层次的活体雕像，下一次节拍让雕像只替换一部分姿态",
        "预览只保留三人的关键骨骼和一个冻结层，用队形边显示谁是支点、谁是被支撑者",
        "录制后重建队形、冻结窗口和姿态深度层，细化多人交叉遮挡、换姿和雕像分体",
        "三人合拍、队形舞或家庭录像中做出会逐拍换姿的多人雕像",
        (
        {
    "recipe_id": "RECIPE-TRIO-STATUE-TIME-V1",
    "name_zh": "三人队形时间雕像·支点定格",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEFREEZE",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEBEAT",
        "FX-BODY-MOTION-CLONES-POSE-POSEDEPTH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW"
    ],
    "trigger_logic": "三人形成稳定三角队形并在强拍上同时停住",
    "combined_effect": "三角支点被冻结成雕像，前层人物保持亮色，后层人物以姿态切片压入雕像内部",
    "why_new": "队形拓扑决定雕像结构，冻结时刻与深度层共同定义立体感",
    "preview_behavior": "预览只保留三人的关键骨骼和一个冻结层，用队形边显示谁是支点、谁是被支撑者。针对支点定格，取景器先在“三人形成稳定三角队形并在强拍上同时停住”发生前标出候选轨迹，确认后才显示“三角支点被冻结成雕像，前层人物保持亮色，后层人物以姿态切片压入雕像内部”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建队形、冻结窗口和姿态深度层，细化多人交叉遮挡、换姿和雕像分体。录后以“三人形成稳定三角队形并在强拍上同时停住”的首帧为时间锚，重新计算支点定格涉及的遮挡和深度，使“三角支点被冻结成雕像，前层人物保持亮色，后层人物以姿态切片压入雕像内部”在原分辨率下保持连续；检测到三角边抖动会使雕像塌陷，保持骨盆节点固定时仅修补低置信度片段。",
    "risks": [
        "三角边抖动会使雕像塌陷，保持骨盆节点固定"
    ],
    "target_scenarios": [
        "两人面对面的全身互动镜头适合拍摄支点定格：先让主体完成“三人形成稳定三角队形并在强拍上同时停住”，随后缓慢移动手机观察“三角支点被冻结成雕像，前层人物保持亮色，后层人物以姿态切片压入雕像内部”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-TRIO-STATUE-TIME-V2",
    "name_zh": "三人队形时间雕像·逐人换姿",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEFREEZE",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEBEAT",
        "FX-BODY-MOTION-CLONES-POSE-POSEDEPTH",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT"
    ],
    "trigger_logic": "雕像冻结后下一拍只有一人改变姿态",
    "combined_effect": "改变姿态的人像从雕像中替换出来，其余两人保持上一层，替换边缘显示一条时间切片",
    "why_new": "局部时间冻结让多人可以不同步更新，换姿过程可读而不切断队形",
    "preview_behavior": "移动端预览从逐人换姿的结果层反推触发：屏幕持续保留对象身份和最近历史，当“雕像冻结后下一拍只有一人改变姿态”成立时，把“改变姿态的人像从雕像中替换出来，其余两人保持上一层，替换边缘显示一条时间切片”分成进入、保持、退场三段显示。若出现多人同时变化会破坏局部更新，退化为全体短冻结，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把逐人换姿拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“雕像冻结后下一拍只有一人改变姿态”，再细化“改变姿态的人像从雕像中替换出来，其余两人保持上一层，替换边缘显示一条时间切片”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "多人同时变化会破坏局部更新，退化为全体短冻结"
    ],
    "target_scenarios": [
        "在三人围成半圈的固定机位使用逐人换姿。镜头从未触发状态开始横向移动，人物或物体执行“雕像冻结后下一拍只有一人改变姿态”后继续穿过画面，以“改变姿态的人像从雕像中替换出来，其余两人保持上一层，替换边缘显示一条时间切片”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-TRIO-STATUE-TIME-V3",
    "name_zh": "三人队形时间雕像·纵深旋台",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEFREEZE",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEBEAT",
        "FX-BODY-MOTION-CLONES-POSE-POSEDEPTH",
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORTOUCH"
    ],
    "trigger_logic": "三人围成弧线并同步向同一侧转身",
    "combined_effect": "三人的姿态切片按深度旋转，前人短暂成为侧面支点，后人从其轮廓后显露",
    "why_new": "关系图顺序、身体朝向和姿态深度共同生成旋转雕像",
    "preview_behavior": "拍摄者先看到纵深旋台所需的对象边界、方向箭头和时间门；“三人围成弧线并同步向同一侧转身”被连续确认后，预览按由近到远的层次展开“三人的姿态切片按深度旋转，前人短暂成为侧面支点，后人从其轮廓后显露”。三人动作会在队形成立时冻结成一座有前后层次的活体雕像，下一次节拍让雕像只替换一部分姿态，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验纵深旋台的身份链与事件顺序，再按多人关系图维护队形拓扑，骨骼姿态组成雕像，局部冻结锁住成形瞬间，姿态切片把三人放入不同时间深度重建组件关系。“三人的姿态切片按深度旋转，前人短暂成为侧面支点，后人从其轮廓后显露”使用完整历史窗口重新渲染，而“三人围成弧线并同步向同一侧转身”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "弧线深度估计错误会让后人穿前，降低纵深差"
    ],
    "target_scenarios": [
        "把纵深旋台安排在朋友接力动作的横向跟拍：固定主体身份后执行“三人围成弧线并同步向同一侧转身”，拍摄者绕触发点改变观察角度，用“三人的姿态切片按深度旋转，前人短暂成为侧面支点，后人从其轮廓后显露”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-TRIO-STATUE-TIME-V4",
    "name_zh": "三人队形时间雕像·分体重组",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEFREEZE",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEBEAT",
        "FX-BODY-MOTION-CLONES-POSE-POSEDEPTH",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEPOSE"
    ],
    "trigger_logic": "队形被一人打破后两人仍保持相邻关系",
    "combined_effect": "雕像沿被打破的关系边分成两块，剩余两人携带旧姿态层移动，重新靠近时合成新雕像",
    "why_new": "队形变化直接改变雕像拓扑，时间层随关系边迁移而不是固定在屏幕位置",
    "preview_behavior": "为预览分体重组，系统只更新与“队形被一人打破后两人仍保持相邻关系”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“雕像沿被打破的关系边分成两块，剩余两人携带旧姿态层移动，重新靠近时合成新雕像”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "分体重组的后处理从失败点开始：针对“断边误检会造成频繁分体，使用关系稳定窗口”复核掩码、锚点或时间戳，通过后才将“雕像沿被打破的关系边分成两块，剩余两人携带旧姿态层移动，重新靠近时合成新雕像”提升到成片质量。触发逻辑“队形被一人打破后两人仍保持相邻关系”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "断边误检会造成频繁分体，使用关系稳定窗口"
    ],
    "target_scenarios": [
        "舞台队形变化的高机位录像可用分体重组组织一段连续互动。参与者先保持关系稳定，再完成“队形被一人打破后两人仍保持相邻关系”；镜头不切断，直到“雕像沿被打破的关系边分成两块，剩余两人携带旧姿态层移动，重新靠近时合成新雕像”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-TRIO-STATUE-TIME-V5",
    "name_zh": "三人队形时间雕像·雕像呼吸",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-TEMPORAL-STATE-LOCAL-TIME-FREEZE",
        "ATOM-CLONING-ECHOES-POSE-SLICES",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE"
    ],
    "component_effect_ids": [
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEFREEZE",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEBEAT",
        "FX-BODY-MOTION-CLONES-POSE-POSEDEPTH",
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF"
    ],
    "trigger_logic": "三人保持姿态但胸肩有细微周期运动",
    "combined_effect": "主体姿态保持冻结，轮廓中的呼吸周期逐层向外扩散，三人的呼吸层在中心相遇",
    "why_new": "冻结只锁住大姿态，细微运动作为时间差分保留，雕像因此仍有生命感",
    "preview_behavior": "雕像呼吸的取景反馈以结束状态为目标：预览先保留真实动作，在“三人保持姿态但胸肩有细微周期运动”完成时快速呈现“主体姿态保持冻结，轮廓中的呼吸周期逐层向外扩散，三人的呼吸层在中心相遇”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留雕像呼吸的完整生命周期。系统逆向检查“主体姿态保持冻结，轮廓中的呼吸周期逐层向外扩散，三人的呼吸层在中心相遇”是否回到稳定终态，再从“三人保持姿态但胸肩有细微周期运动”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "呼吸信号过弱会消失，保留最近稳定周期"
    ],
    "target_scenarios": [
        "以多人触碰完成后的关系图收束作为雕像呼吸的结尾段落：让“三人保持姿态但胸肩有细微周期运动”发生在最后一个动作峰值，保持机位直到“主体姿态保持冻结，轮廓中的呼吸周期逐层向外扩散，三人的呼吸层在中心相遇”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "RELATION-GAZE", "multi_person", "关系图对视追光",
        (
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-SEGMENTATION-MASKS-FACE-REGION",
            "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        ),
        (
            "FX-FACE-GAZE-EXPRESSION-DIALOGUE-SPEAKERSWAP",
            "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
            "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYRETURN",
        ),
        ("multi_person", "gaze", "sound"),
        "关系图定义人物之间的边，视线向量识别当前接收者，脸部掩码保护人物，追光圈和能量回流共同显示关系变化",
        "追光会沿真实对视关系切换，目光离开时光圈不立即消失，而是沿关系边回流到上一个说话者",
        "预览显示少量候选关系边和一个追光圈，只有稳定对视才允许光圈换人",
        "录制后细化视线目标、说话人交接、追光过渡和回流粒子，处理三人交叉遮挡",
        "多人聊天、聚会或采访中把目光和发言关系做成可见的光网",
        (
        {
    "recipe_id": "RECIPE-RELATION-GAZE-V1",
    "name_zh": "关系图对视追光·对视换灯",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-SPEAKERSWAP",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYRETURN",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTHROW"
    ],
    "trigger_logic": "说话者停止发声并与另一人完成稳定对视",
    "combined_effect": "追光从说话者移到被注视者，上一条关系边保留一条回流亮线后熄灭",
    "why_new": "说话交接和对视交接同时改变光路，观众能看见关系如何被接管",
    "preview_behavior": "预览显示少量候选关系边和一个追光圈，只有稳定对视才允许光圈换人。针对对视换灯，取景器先在“说话者停止发声并与另一人完成稳定对视”发生前标出候选轨迹，确认后才显示“追光从说话者移到被注视者，上一条关系边保留一条回流亮线后熄灭”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化视线目标、说话人交接、追光过渡和回流粒子，处理三人交叉遮挡。录后以“说话者停止发声并与另一人完成稳定对视”的首帧为时间锚，重新计算对视换灯涉及的遮挡和深度，使“追光从说话者移到被注视者，上一条关系边保留一条回流亮线后熄灭”在原分辨率下保持连续；检测到说话者和目标同时看镜头会产生歧义，保持上一条边时仅修补低置信度片段。",
    "risks": [
        "说话者和目标同时看镜头会产生歧义，保持上一条边"
    ],
    "target_scenarios": [
        "两人面对面的全身互动镜头适合拍摄对视换灯：先让主体完成“说话者停止发声并与另一人完成稳定对视”，随后缓慢移动手机观察“追光从说话者移到被注视者，上一条关系边保留一条回流亮线后熄灭”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-RELATION-GAZE-V2",
    "name_zh": "关系图对视追光·三角回流",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-SPEAKERSWAP",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYRETURN",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYBEAT"
    ],
    "trigger_logic": "三人依次看向下一人并在最后回看第一人",
    "combined_effect": "追光沿三角关系边循环，最后一次回看触发能量沿整圈反向回流并汇入起点",
    "why_new": "视线闭环让多人关系具有方向和回程，回流是闭环完成的可见反馈",
    "preview_behavior": "移动端预览从三角回流的结果层反推触发：屏幕持续保留对象身份和最近历史，当“三人依次看向下一人并在最后回看第一人”成立时，把“追光沿三角关系边循环，最后一次回看触发能量沿整圈反向回流并汇入起点”分成进入、保持、退场三段显示。若出现闭环时间过长会让光网残留，按最近三次稳定视线截断，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把三角回流拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“三人依次看向下一人并在最后回看第一人”，再细化“追光沿三角关系边循环，最后一次回看触发能量沿整圈反向回流并汇入起点”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "闭环时间过长会让光网残留，按最近三次稳定视线截断"
    ],
    "target_scenarios": [
        "在三人围成半圈的固定机位使用三角回流。镜头从未触发状态开始横向移动，人物或物体执行“三人依次看向下一人并在最后回看第一人”后继续穿过画面，以“追光沿三角关系边循环，最后一次回看触发能量沿整圈反向回流并汇入起点”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-RELATION-GAZE-V3",
    "name_zh": "关系图对视追光·旁观者接入",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-SPEAKERSWAP",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYRETURN",
        "FX-MULTI-PERSON-INTERACTION-MIRROR-MIRRORTOUCH"
    ],
    "trigger_logic": "两人对话时第三人持续注视其中一人超过停留门限",
    "combined_effect": "第三人的追光圈沿新关系边接入，原对话光圈缩小为边缘光并等待新的说话事件",
    "why_new": "注视停留能改变关系图拓扑，旁观者成为可见的互动节点",
    "preview_behavior": "拍摄者先看到旁观者接入所需的对象边界、方向箭头和时间门；“两人对话时第三人持续注视其中一人超过停留门限”被连续确认后，预览按由近到远的层次展开“第三人的追光圈沿新关系边接入，原对话光圈缩小为边缘光并等待新的说话事件”。追光会沿真实对视关系切换，目光离开时光圈不立即消失，而是沿关系边回流到上一个说话者，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验旁观者接入的身份链与事件顺序，再按关系图定义人物之间的边，视线向量识别当前接收者，脸部掩码保护人物，追光圈和能量回流共同显示关系变化重建组件关系。“第三人的追光圈沿新关系边接入，原对话光圈缩小为边缘光并等待新的说话事件”使用完整历史窗口重新渲染，而“两人对话时第三人持续注视其中一人超过停留门限”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "背景人脸可能误接入，要求脸部区域和视线同时稳定"
    ],
    "target_scenarios": [
        "把旁观者接入安排在朋友接力动作的横向跟拍：固定主体身份后执行“两人对话时第三人持续注视其中一人超过停留门限”，拍摄者绕触发点改变观察角度，用“第三人的追光圈沿新关系边接入，原对话光圈缩小为边缘光并等待新的说话事件”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-RELATION-GAZE-V4",
    "name_zh": "关系图对视追光·目光错开",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-PARTICLES-ATMOSPHERE-SPARKS"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-SPEAKERSWAP",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYRETURN",
        "FX-MULTI-PERSON-INTERACTION-STATUE-STATUEPOSE"
    ],
    "trigger_logic": "两人互相看向对方但说话声源来自第三人",
    "combined_effect": "追光在两人之间形成虚线，真正声源获得实体光圈，三条关系边用不同亮度区分",
    "why_new": "视线关系和声音关系被同时呈现，视觉不会把看向谁误当成谁在说话",
    "preview_behavior": "为预览目光错开，系统只更新与“两人互相看向对方但说话声源来自第三人”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“追光在两人之间形成虚线，真正声源获得实体光圈，三条关系边用不同亮度区分”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "目光错开的后处理从失败点开始：针对“声源定位不准时实体光圈闪动，使用人声置信度平滑”复核掩码、锚点或时间戳，通过后才将“追光在两人之间形成虚线，真正声源获得实体光圈，三条关系边用不同亮度区分”提升到成片质量。触发逻辑“两人互相看向对方但说话声源来自第三人”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "声源定位不准时实体光圈闪动，使用人声置信度平滑"
    ],
    "target_scenarios": [
        "舞台队形变化的高机位录像可用目光错开组织一段连续互动。参与者先保持关系稳定，再完成“两人互相看向对方但说话声源来自第三人”；镜头不切断，直到“追光在两人之间形成虚线，真正声源获得实体光圈，三条关系边用不同亮度区分”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-RELATION-GAZE-V5",
    "name_zh": "关系图对视追光·关系断线",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-SEGMENTATION-MASKS-FACE-REGION",
        "ATOM-LIGHT-OPTICS-VIRTUAL-SPOTLIGHT",
        "ATOM-TEMPORAL-STATE-IDENTITY-MEMORY"
    ],
    "component_effect_ids": [
        "FX-FACE-GAZE-EXPRESSION-DIALOGUE-SPEAKERSWAP",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTSWAP",
        "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYRETURN",
        "FX-AUDIO-LYRICS-DUET-DUETHANDOFF"
    ],
    "trigger_logic": "目标移开视线并转身离开关系图范围",
    "combined_effect": "光圈沿原关系边回流到最近说话者，断开的边变成短暂虚线并从脸部边界外消失",
    "why_new": "离开动作改变关系图而不是简单淡出，回流保留了关系断开的方向",
    "preview_behavior": "关系断线的取景反馈以结束状态为目标：预览先保留真实动作，在“目标移开视线并转身离开关系图范围”完成时快速呈现“光圈沿原关系边回流到最近说话者，断开的边变成短暂虚线并从脸部边界外消失”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留关系断线的完整生命周期。系统逆向检查“光圈沿原关系边回流到最近说话者，断开的边变成短暂虚线并从脸部边界外消失”是否回到稳定终态，再从“目标移开视线并转身离开关系图范围”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "出框检测延迟会留下孤立光圈，超时强制回到最近节点"
    ],
    "target_scenarios": [
        "以多人触碰完成后的关系图收束作为关系断线的结尾段落：让“目标移开视线并转身离开关系图范围”发生在最后一个动作峰值，保持机位直到“光圈沿原关系边回流到最近说话者，断开的边变成短暂虚线并从脸部边界外消失”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "PARTICLE-GAZE-LIGHT", "particles_weather", "凝视尘光追踪",
        (
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-PARTICLES-ATMOSPHERE-DUST",
            "ATOM-LIGHT-OPTICS-VOLUMETRIC-LIGHT",
            "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS",
        ),
        (
            "FX-PARTICLES-WEATHER-DUST-DUSTGAZE",
            "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTFOLLOW",
            "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        ),
        ("gaze", "particle", "realtime_light_trail"),
        "凝视触发选择尘埃聚焦区域，视线方向控制体积光束，尘埃粒子沿光束和视线历史形成可见路径",
        "视线扫过空气时会把尘埃聚成一束可见的光路，停留点形成亮核，移开后尘埃缓慢散回",
        "预览使用低密度尘埃和短视线轨迹，停留确认后增加体积光，不持续渲染整幅粒子场",
        "录制后细化尘埃深度、光束体积和视线扫掠路径，修复人物遮挡与粒子边界",
        "逆光人像、室内窗光或演唱会烟尘中用目光捞起一束尘光",
        (
        {
    "recipe_id": "RECIPE-PARTICLE-GAZE-LIGHT-V1",
    "name_zh": "凝视尘光追踪·视线捞光",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-PARTICLES-ATMOSPHERE-DUST",
        "ATOM-LIGHT-OPTICS-VOLUMETRIC-LIGHT",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS",
        "ATOM-PARTICLES-ATMOSPHERE-RAIN"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-DUST-DUSTGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTFOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE"
    ],
    "trigger_logic": "视线从地面扫向一束可见逆光并停留",
    "combined_effect": "尘埃沿扫视方向聚拢成细光束，停留点形成发光尘核并照亮附近粒子",
    "why_new": "扫视提供路径、停留提供聚焦，体积光把视线变成有空间厚度的动作",
    "preview_behavior": "预览使用低密度尘埃和短视线轨迹，停留确认后增加体积光，不持续渲染整幅粒子场。针对视线捞光，取景器先在“视线从地面扫向一束可见逆光并停留”发生前标出候选轨迹，确认后才显示“尘埃沿扫视方向聚拢成细光束，停留点形成发光尘核并照亮附近粒子”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化尘埃深度、光束体积和视线扫掠路径，修复人物遮挡与粒子边界。录后以“视线从地面扫向一束可见逆光并停留”的首帧为时间锚，重新计算视线捞光涉及的遮挡和深度，使“尘埃沿扫视方向聚拢成细光束，停留点形成发光尘核并照亮附近粒子”在原分辨率下保持连续；检测到尘埃稀少时光束空洞，使用粒子密度上限和柔光替代时仅修补低置信度片段。",
    "risks": [
        "尘埃稀少时光束空洞，使用粒子密度上限和柔光替代"
    ],
    "target_scenarios": [
        "雨后街道的人物跟拍适合拍摄视线捞光：先让主体完成“视线从地面扫向一束可见逆光并停留”，随后缓慢移动手机观察“尘埃沿扫视方向聚拢成细光束，停留点形成发光尘核并照亮附近粒子”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-PARTICLE-GAZE-LIGHT-V2",
    "name_zh": "凝视尘光追踪·人物穿束",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-PARTICLES-ATMOSPHERE-DUST",
        "ATOM-LIGHT-OPTICS-VOLUMETRIC-LIGHT",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS",
        "ATOM-PARTICLES-ATMOSPHERE-SNOW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-DUST-DUSTGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTFOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "视线锁定人物肩侧且人物从光束前经过",
    "combined_effect": "光束被人物轮廓切成前后两段，后段尘埃保持更暗并在人物离开后重新接通",
    "why_new": "凝视目标、体积光和人物遮挡共同决定光路连续性，不是屏幕上的光带",
    "preview_behavior": "移动端预览从人物穿束的结果层反推触发：屏幕持续保留对象身份和最近历史，当“视线锁定人物肩侧且人物从光束前经过”成立时，把“光束被人物轮廓切成前后两段，后段尘埃保持更暗并在人物离开后重新接通”分成进入、保持、退场三段显示。若出现肩部掩码错误会让光束穿体，扩大边界羽化，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把人物穿束拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“视线锁定人物肩侧且人物从光束前经过”，再细化“光束被人物轮廓切成前后两段，后段尘埃保持更暗并在人物离开后重新接通”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "肩部掩码错误会让光束穿体，扩大边界羽化"
    ],
    "target_scenarios": [
        "在逆光窗边的手势近景使用人物穿束。镜头从未触发状态开始横向移动，人物或物体执行“视线锁定人物肩侧且人物从光束前经过”后继续穿过画面，以“光束被人物轮廓切成前后两段，后段尘埃保持更暗并在人物离开后重新接通”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-PARTICLE-GAZE-LIGHT-V3",
    "name_zh": "凝视尘光追踪·双点聚尘",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-PARTICLES-ATMOSPHERE-DUST",
        "ATOM-LIGHT-OPTICS-VOLUMETRIC-LIGHT",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-DUST-DUSTGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTFOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-PARTICLES-WEATHER-SNOW-SNOWTOUCH"
    ],
    "trigger_logic": "视线在两个背景点之间来回切换",
    "combined_effect": "两个停留点各自形成尘核，视线轨迹把两核连接成一条呼吸光线，切换时亮度交替",
    "why_new": "离散凝视点和连续视线轨迹组合成粒子结构，能表现目光往返",
    "preview_behavior": "拍摄者先看到双点聚尘所需的对象边界、方向箭头和时间门；“视线在两个背景点之间来回切换”被连续确认后，预览按由近到远的层次展开“两个停留点各自形成尘核，视线轨迹把两核连接成一条呼吸光线，切换时亮度交替”。视线扫过空气时会把尘埃聚成一束可见的光路，停留点形成亮核，移开后尘埃缓慢散回，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验双点聚尘的身份链与事件顺序，再按凝视触发选择尘埃聚焦区域，视线方向控制体积光束，尘埃粒子沿光束和视线历史形成可见路径重建组件关系。“两个停留点各自形成尘核，视线轨迹把两核连接成一条呼吸光线，切换时亮度交替”使用完整历史窗口重新渲染，而“视线在两个背景点之间来回切换”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "两个点距离过远会使连线稀疏，降低中段粒子数"
    ],
    "target_scenarios": [
        "把双点聚尘安排在雪地步行动作的侧面机位：固定主体身份后执行“视线在两个背景点之间来回切换”，拍摄者绕触发点改变观察角度，用“两个停留点各自形成尘核，视线轨迹把两核连接成一条呼吸光线，切换时亮度交替”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-PARTICLE-GAZE-LIGHT-V4",
    "name_zh": "凝视尘光追踪·尘光回声",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-PARTICLES-ATMOSPHERE-DUST",
        "ATOM-LIGHT-OPTICS-VOLUMETRIC-LIGHT",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-DUST-DUSTGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTFOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT"
    ],
    "trigger_logic": "用户凝视后快速移开并再次看回原点",
    "combined_effect": "第一次视线留下淡尘带，第二次凝视让尘带从远处回流并在原点重聚",
    "why_new": "二次凝视改变粒子时间方向，视线历史因此可回看而非只产生即时亮点",
    "preview_behavior": "为预览尘光回声，系统只更新与“用户凝视后快速移开并再次看回原点”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“第一次视线留下淡尘带，第二次凝视让尘带从远处回流并在原点重聚”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "尘光回声的后处理从失败点开始：针对“回流路径受遮挡影响会断裂，沿旧路径插值”复核掩码、锚点或时间戳，通过后才将“第一次视线留下淡尘带，第二次凝视让尘带从远处回流并在原点重聚”提升到成片质量。触发逻辑“用户凝视后快速移开并再次看回原点”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "回流路径受遮挡影响会断裂，沿旧路径插值"
    ],
    "target_scenarios": [
        "花瓣与人物视线同框的环绕镜头可用尘光回声组织一段连续互动。参与者先保持关系稳定，再完成“用户凝视后快速移开并再次看回原点”；镜头不切断，直到“第一次视线留下淡尘带，第二次凝视让尘带从远处回流并在原点重聚”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-PARTICLE-GAZE-LIGHT-V5",
    "name_zh": "凝视尘光追踪·追光交接",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-PARTICLES-ATMOSPHERE-DUST",
        "ATOM-LIGHT-OPTICS-VOLUMETRIC-LIGHT",
        "ATOM-INTERACTION-TRIGGERS-GAZE-FOCUS",
        "ATOM-PARTICLES-ATMOSPHERE-SMOKE"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-DUST-DUSTGAZE",
        "FX-VIRTUAL-LIGHT-SHADOW-FOLLOW-SPOTFOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRAIL",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW"
    ],
    "trigger_logic": "视线从一个人脸移向另一人脸且两点深度不同",
    "combined_effect": "体积光先穿过两人之间的尘埃，再在第二张脸侧形成亮核，旧亮核保留一小段尾光",
    "why_new": "深度顺序和视线目标共同决定光束穿越，人物关系被粒子路径暗示",
    "preview_behavior": "追光交接的取景反馈以结束状态为目标：预览先保留真实动作，在“视线从一个人脸移向另一人脸且两点深度不同”完成时快速呈现“体积光先穿过两人之间的尘埃，再在第二张脸侧形成亮核，旧亮核保留一小段尾光”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留追光交接的完整生命周期。系统逆向检查“体积光先穿过两人之间的尘埃，再在第二张脸侧形成亮核，旧亮核保留一小段尾光”是否回到稳定终态，再从“视线从一个人脸移向另一人脸且两点深度不同”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "多人遮挡可能让亮核错脸，要求脸部掩码稳定"
    ],
    "target_scenarios": [
        "以粒子回收到触发点的结尾画面作为追光交接的结尾段落：让“视线从一个人脸移向另一人脸且两点深度不同”发生在最后一个动作峰值，保持机位直到“体积光先穿过两人之间的尘埃，再在第二张脸侧形成亮核，旧亮核保留一小段尾光”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "RAIN-ANCHOR-SOUND", "particles_weather", "锚点雨幕声场",
        (
            "ATOM-PARTICLES-ATMOSPHERE-RAIN",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
            "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION",
        ),
        (
            "FX-PARTICLES-WEATHER-RAIN-RAINDEPTH",
            "FX-PARTICLES-WEATHER-RAIN-RAINVOICE",
            "FX-AUDIO-LYRICS-RIBBON-RIBBONDIRECTION",
        ),
        ("particle", "world_anchor", "sound"),
        "雨滴粒子分层于世界锚点，手机旋转改变雨幕方向，声音音量控制雨量并让声源彩带穿过雨层",
        "雨幕不是覆盖层：雨线固定在空间深度中，声音会把雨量推向声源一侧，手机转动改变其倾斜方向",
        "预览使用三层雨深度和低频音量包络，旋转只更新雨线方向参数并限制粒子数量",
        "录制后重建雨滴深度、手机姿态和声源方向，细化雨线遮挡、雨量曲线与彩带穿层",
        "街头、车窗或夜景录像中做一场会听声、会转向的空间雨",
        (
        {
    "recipe_id": "RECIPE-RAIN-ANCHOR-SOUND-V1",
    "name_zh": "锚点雨幕声场·声源雨帘",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-RAIN",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION",
        "ATOM-PARTICLES-ATMOSPHERE-DUST"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINDEPTH",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONDIRECTION",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "人声从画面右侧出现且音量逐渐升高",
    "combined_effect": "右侧雨线变密并向声源倾斜，声源彩带穿过前景雨层，在人物脸侧形成一片雨帘",
    "why_new": "声音决定雨量和偏移方向，世界深度决定雨帘前后层次",
    "preview_behavior": "预览使用三层雨深度和低频音量包络，旋转只更新雨线方向参数并限制粒子数量。针对声源雨帘，取景器先在“人声从画面右侧出现且音量逐渐升高”发生前标出候选轨迹，确认后才显示“右侧雨线变密并向声源倾斜，声源彩带穿过前景雨层，在人物脸侧形成一片雨帘”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建雨滴深度、手机姿态和声源方向，细化雨线遮挡、雨量曲线与彩带穿层。录后以“人声从画面右侧出现且音量逐渐升高”的首帧为时间锚，重新计算声源雨帘涉及的遮挡和深度，使“右侧雨线变密并向声源倾斜，声源彩带穿过前景雨层，在人物脸侧形成一片雨帘”在原分辨率下保持连续；检测到声源方向不稳会让雨帘摆动，使用短时方向平均时仅修补低置信度片段。",
    "risks": [
        "声源方向不稳会让雨帘摆动，使用短时方向平均"
    ],
    "target_scenarios": [
        "雨后街道的人物跟拍适合拍摄声源雨帘：先让主体完成“人声从画面右侧出现且音量逐渐升高”，随后缓慢移动手机观察“右侧雨线变密并向声源倾斜，声源彩带穿过前景雨层，在人物脸侧形成一片雨帘”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-RAIN-ANCHOR-SOUND-V2",
    "name_zh": "锚点雨幕声场·转手机雨",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-RAIN",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION",
        "ATOM-PARTICLES-ATMOSPHERE-SNOW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINDEPTH",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONDIRECTION",
        "FX-PARTICLES-WEATHER-SNOW-SNOWTOUCH"
    ],
    "trigger_logic": "用户向左旋转手机并保持音量低于门限",
    "combined_effect": "世界锚定的雨线随手机姿态从垂直变成斜落，背景锚点不动，前景雨滴产生相对视差",
    "why_new": "旋转控制雨的方向而非相机画面，锚点让用户能区分世界雨和屏幕滤镜",
    "preview_behavior": "移动端预览从转手机雨的结果层反推触发：屏幕持续保留对象身份和最近历史，当“用户向左旋转手机并保持音量低于门限”成立时，把“世界锚定的雨线随手机姿态从垂直变成斜落，背景锚点不动，前景雨滴产生相对视差”分成进入、保持、退场三段显示。若出现旋转过快会使雨线跳向错误方向，冻结上一可信姿态，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把转手机雨拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“用户向左旋转手机并保持音量低于门限”，再细化“世界锚定的雨线随手机姿态从垂直变成斜落，背景锚点不动，前景雨滴产生相对视差”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "旋转过快会使雨线跳向错误方向，冻结上一可信姿态"
    ],
    "target_scenarios": [
        "在逆光窗边的手势近景使用转手机雨。镜头从未触发状态开始横向移动，人物或物体执行“用户向左旋转手机并保持音量低于门限”后继续穿过画面，以“世界锚定的雨线随手机姿态从垂直变成斜落，背景锚点不动，前景雨滴产生相对视差”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-RAIN-ANCHOR-SOUND-V3",
    "name_zh": "锚点雨幕声场·雨中留白",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-RAIN",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINDEPTH",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONDIRECTION",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT"
    ],
    "trigger_logic": "用户触摸画出一个世界平面区域且雨量开始升高",
    "combined_effect": "触摸区域成为锚定的无雨窗口，周围雨线在窗口边缘分流并形成一圈细声带",
    "why_new": "手势选择和雨滴空间分布形成可互动的天气孔洞，不只是擦除粒子",
    "preview_behavior": "拍摄者先看到雨中留白所需的对象边界、方向箭头和时间门；“用户触摸画出一个世界平面区域且雨量开始升高”被连续确认后，预览按由近到远的层次展开“触摸区域成为锚定的无雨窗口，周围雨线在窗口边缘分流并形成一圈细声带”。雨幕不是覆盖层：雨线固定在空间深度中，声音会把雨量推向声源一侧，手机转动改变其倾斜方向，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验雨中留白的身份链与事件顺序，再按雨滴粒子分层于世界锚点，手机旋转改变雨幕方向，声音音量控制雨量并让声源彩带穿过雨层重建组件关系。“触摸区域成为锚定的无雨窗口，周围雨线在窗口边缘分流并形成一圈细声带”使用完整历史窗口重新渲染，而“用户触摸画出一个世界平面区域且雨量开始升高”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "窗口平面估计错误会漂浮，退回屏幕区域并降低深度效果"
    ],
    "target_scenarios": [
        "把雨中留白安排在雪地步行动作的侧面机位：固定主体身份后执行“用户触摸画出一个世界平面区域且雨量开始升高”，拍摄者绕触发点改变观察角度，用“触摸区域成为锚定的无雨窗口，周围雨线在窗口边缘分流并形成一圈细声带”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-RAIN-ANCHOR-SOUND-V4",
    "name_zh": "锚点雨幕声场·低音积雨",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-RAIN",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINDEPTH",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONDIRECTION",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW"
    ],
    "trigger_logic": "低音音量持续上升且手机保持静止",
    "combined_effect": "地面前景雨滴逐渐拉长并汇成一条低矮水线，声源彩带在水线上反射出暗色边",
    "why_new": "低音影响雨滴生命周期和地面汇流，声音改变了雨的物理观感",
    "preview_behavior": "为预览低音积雨，系统只更新与“低音音量持续上升且手机保持静止”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“地面前景雨滴逐渐拉长并汇成一条低矮水线，声源彩带在水线上反射出暗色边”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "低音积雨的后处理从失败点开始：针对“低频噪声会误积雨，使用音乐或人声频带筛选”复核掩码、锚点或时间戳，通过后才将“地面前景雨滴逐渐拉长并汇成一条低矮水线，声源彩带在水线上反射出暗色边”提升到成片质量。触发逻辑“低音音量持续上升且手机保持静止”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "低频噪声会误积雨，使用音乐或人声频带筛选"
    ],
    "target_scenarios": [
        "花瓣与人物视线同框的环绕镜头可用低音积雨组织一段连续互动。参与者先保持关系稳定，再完成“低音音量持续上升且手机保持静止”；镜头不切断，直到“地面前景雨滴逐渐拉长并汇成一条低矮水线，声源彩带在水线上反射出暗色边”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-RAIN-ANCHOR-SOUND-V5",
    "name_zh": "锚点雨幕声场·回声停雨",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-RAIN",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION",
        "ATOM-PARTICLES-ATMOSPHERE-SMOKE"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-RAIN-RAINDEPTH",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE",
        "FX-AUDIO-LYRICS-RIBBON-RIBBONDIRECTION",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT"
    ],
    "trigger_logic": "声音突然停止且手机向相反方向轻转",
    "combined_effect": "雨量先保持上一方向半拍，再沿相反旋转方向逐层稀疏，最后只剩锚点上的几滴雨",
    "why_new": "停声和反向姿态共同决定天气回收顺序，结束状态有明确动作逻辑",
    "preview_behavior": "回声停雨的取景反馈以结束状态为目标：预览先保留真实动作，在“声音突然停止且手机向相反方向轻转”完成时快速呈现“雨量先保持上一方向半拍，再沿相反旋转方向逐层稀疏，最后只剩锚点上的几滴雨”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留回声停雨的完整生命周期。系统逆向检查“雨量先保持上一方向半拍，再沿相反旋转方向逐层稀疏，最后只剩锚点上的几滴雨”是否回到稳定终态，再从“声音突然停止且手机向相反方向轻转”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "停声检测延迟会留下过多雨滴，使用静音门限超时回收"
    ],
    "target_scenarios": [
        "以粒子回收到触发点的结尾画面作为回声停雨的结尾段落：让“声音突然停止且手机向相反方向轻转”发生在最后一个动作峰值，保持机位直到“雨量先保持上一方向半拍，再沿相反旋转方向逐层稀疏，最后只剩锚点上的几滴雨”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "PETAL-GESTURE-CLONE", "particles_weather", "手势花瓣时间花",
        (
            "ATOM-INTERACTION-TRIGGERS-HAND-GESTURE",
            "ATOM-PARTICLES-ATMOSPHERE-PETALS",
            "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
            "ATOM-TEMPORAL-STATE-TIME-LOOP",
        ),
        (
            "FX-PARTICLES-WEATHER-PETAL-PETALGESTURE",
            "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW",
            "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBURST",
        ),
        ("particle", "touch_gesture", "time"),
        "手势触发花瓣发射方向，花瓣跟随手部轨迹，时间分身保存动作片段，局部循环让花瓣重复一小段表演",
        "手势划过的空间会盛开花瓣，花瓣复制的不是图案而是手势历史，循环段落让花瓣按动作节奏再次开放",
        "预览只显示少量花瓣和一层手势回声，动作峰值才触发花瓣爆发",
        "录制后重建手势曲线、花瓣碰撞和时间循环，细化人物遮挡、花瓣层次与回放首尾",
        "舞蹈、婚礼或春日人像中用手势把动作变成一场有时间回声的花瓣盛开",
        (
        {
    "recipe_id": "RECIPE-PETAL-GESTURE-CLONE-V1",
    "name_zh": "手势花瓣时间花·挥手开花",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-HAND-GESTURE",
        "ATOM-PARTICLES-ATMOSPHERE-PETALS",
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-PARTICLES-ATMOSPHERE-RAIN"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-PETAL-PETALGESTURE",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBURST",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE"
    ],
    "trigger_logic": "用户向上挥手并完成张掌手势",
    "combined_effect": "花瓣从手掌背后沿挥手曲线开放，上一帧手势回声在花瓣中心短暂重复",
    "why_new": "手势方向决定花瓣路径，时间回声决定花心层次，花瓣因此记录动作来源",
    "preview_behavior": "预览只显示少量花瓣和一层手势回声，动作峰值才触发花瓣爆发。针对挥手开花，取景器先在“用户向上挥手并完成张掌手势”发生前标出候选轨迹，确认后才显示“花瓣从手掌背后沿挥手曲线开放，上一帧手势回声在花瓣中心短暂重复”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建手势曲线、花瓣碰撞和时间循环，细化人物遮挡、花瓣层次与回放首尾。录后以“用户向上挥手并完成张掌手势”的首帧为时间锚，重新计算挥手开花涉及的遮挡和深度，使“花瓣从手掌背后沿挥手曲线开放，上一帧手势回声在花瓣中心短暂重复”在原分辨率下保持连续；检测到张掌误检会提前爆发，要求手势持续两帧确认时仅修补低置信度片段。",
    "risks": [
        "张掌误检会提前爆发，要求手势持续两帧确认"
    ],
    "target_scenarios": [
        "雨后街道的人物跟拍适合拍摄挥手开花：先让主体完成“用户向上挥手并完成张掌手势”，随后缓慢移动手机观察“花瓣从手掌背后沿挥手曲线开放，上一帧手势回声在花瓣中心短暂重复”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-PETAL-GESTURE-CLONE-V2",
    "name_zh": "手势花瓣时间花·指尖花链",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-HAND-GESTURE",
        "ATOM-PARTICLES-ATMOSPHERE-PETALS",
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-PARTICLES-ATMOSPHERE-DUST"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-PETAL-PETALGESTURE",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBURST",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "手指从左向右连续点出三个位置",
    "combined_effect": "每个点生成一朵花，三朵花按点选时间连接成会循环开合的花链",
    "why_new": "离散触发和局部时间循环组合成有起点、有顺序的花链",
    "preview_behavior": "移动端预览从指尖花链的结果层反推触发：屏幕持续保留对象身份和最近历史，当“手指从左向右连续点出三个位置”成立时，把“每个点生成一朵花，三朵花按点选时间连接成会循环开合的花链”分成进入、保持、退场三段显示。若出现点位过密会使花链拥挤，合并近邻花心，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把指尖花链拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“手指从左向右连续点出三个位置”，再细化“每个点生成一朵花，三朵花按点选时间连接成会循环开合的花链”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "点位过密会使花链拥挤，合并近邻花心"
    ],
    "target_scenarios": [
        "在逆光窗边的手势近景使用指尖花链。镜头从未触发状态开始横向移动，人物或物体执行“手指从左向右连续点出三个位置”后继续穿过画面，以“每个点生成一朵花，三朵花按点选时间连接成会循环开合的花链”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-PETAL-GESTURE-CLONE-V3",
    "name_zh": "手势花瓣时间花·花瓣分身",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-HAND-GESTURE",
        "ATOM-PARTICLES-ATMOSPHERE-PETALS",
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-PARTICLES-ATMOSPHERE-SNOW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-PETAL-PETALGESTURE",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBURST",
        "FX-PARTICLES-WEATHER-SNOW-SNOWTOUCH"
    ],
    "trigger_logic": "主体转身时手臂形成清晰的动作峰值",
    "combined_effect": "动作峰值复制出三层半透明手势分身，每层分身释放不同方向的花瓣并在循环中错开绽放",
    "why_new": "人体时间克隆承载手势历史，粒子方向保留每一层的姿态差分",
    "preview_behavior": "拍摄者先看到花瓣分身所需的对象边界、方向箭头和时间门；“主体转身时手臂形成清晰的动作峰值”被连续确认后，预览按由近到远的层次展开“动作峰值复制出三层半透明手势分身，每层分身释放不同方向的花瓣并在循环中错开绽放”。手势划过的空间会盛开花瓣，花瓣复制的不是图案而是手势历史，循环段落让花瓣按动作节奏再次开放，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验花瓣分身的身份链与事件顺序，再按手势触发花瓣发射方向，花瓣跟随手部轨迹，时间分身保存动作片段，局部循环让花瓣重复一小段表演重建组件关系。“动作峰值复制出三层半透明手势分身，每层分身释放不同方向的花瓣并在循环中错开绽放”使用完整历史窗口重新渲染，而“主体转身时手臂形成清晰的动作峰值”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "手臂交叉时分身花瓣混层，降低后层粒子密度"
    ],
    "target_scenarios": [
        "把花瓣分身安排在雪地步行动作的侧面机位：固定主体身份后执行“主体转身时手臂形成清晰的动作峰值”，拍摄者绕触发点改变观察角度，用“动作峰值复制出三层半透明手势分身，每层分身释放不同方向的花瓣并在循环中错开绽放”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-PETAL-GESTURE-CLONE-V4",
    "name_zh": "手势花瓣时间花·回收花雨",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-HAND-GESTURE",
        "ATOM-PARTICLES-ATMOSPHERE-PETALS",
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-PETAL-PETALGESTURE",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBURST",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT"
    ],
    "trigger_logic": "用户反向挥手并保持手掌收拢",
    "combined_effect": "花瓣沿最近一次手势轨迹逆向回收，回收到掌心后循环停止并留下一个花心光点",
    "why_new": "反向手势不仅关闭效果，还改变花瓣时间方向并提供可见终点",
    "preview_behavior": "为预览回收花雨，系统只更新与“用户反向挥手并保持手掌收拢”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“花瓣沿最近一次手势轨迹逆向回收，回收到掌心后循环停止并留下一个花心光点”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "回收花雨的后处理从失败点开始：针对“反向路径不完整会留下孤瓣，沿历史曲线自动补齐”复核掩码、锚点或时间戳，通过后才将“花瓣沿最近一次手势轨迹逆向回收，回收到掌心后循环停止并留下一个花心光点”提升到成片质量。触发逻辑“用户反向挥手并保持手掌收拢”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "反向路径不完整会留下孤瓣，沿历史曲线自动补齐"
    ],
    "target_scenarios": [
        "花瓣与人物视线同框的环绕镜头可用回收花雨组织一段连续互动。参与者先保持关系稳定，再完成“用户反向挥手并保持手掌收拢”；镜头不切断，直到“花瓣沿最近一次手势轨迹逆向回收，回收到掌心后循环停止并留下一个花心光点”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-PETAL-GESTURE-CLONE-V5",
    "name_zh": "手势花瓣时间花·双手花门",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-HAND-GESTURE",
        "ATOM-PARTICLES-ATMOSPHERE-PETALS",
        "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
        "ATOM-TEMPORAL-STATE-TIME-LOOP",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-PETAL-PETALGESTURE",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW",
        "FX-BODY-MOTION-CLONES-GESTURE-GESTUREBURST",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICBEAT"
    ],
    "trigger_logic": "双手从两侧向中间打开再停住",
    "combined_effect": "两条手势历史形成花瓣拱门，停住时拱门循环播放开合，人物从门下经过会遮住花瓣",
    "why_new": "双手路径、人体遮挡和循环状态共同生成可穿过的空间花门",
    "preview_behavior": "双手花门的取景反馈以结束状态为目标：预览先保留真实动作，在“双手从两侧向中间打开再停住”完成时快速呈现“两条手势历史形成花瓣拱门，停住时拱门循环播放开合，人物从门下经过会遮住花瓣”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留双手花门的完整生命周期。系统逆向检查“两条手势历史形成花瓣拱门，停住时拱门循环播放开合，人物从门下经过会遮住花瓣”是否回到稳定终态，再从“双手从两侧向中间打开再停住”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "双手深度不一致会让拱门扭曲，采用胸口平面校正"
    ],
    "target_scenarios": [
        "以粒子回收到触发点的结尾画面作为双手花门的结尾段落：让“双手从两侧向中间打开再停住”发生在最后一个动作峰值，保持机位直到“两条手势历史形成花瓣拱门，停住时拱门循环播放开合，人物从门下经过会遮住花瓣”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "SNOW-TIME-COLOR", "particles_weather", "雪片时间色层",
        (
            "ATOM-PARTICLES-ATMOSPHERE-SNOW",
            "ATOM-TEMPORAL-STATE-FRAME-DELAY",
            "ATOM-MATERIAL-APPEARANCE-CRYSTAL",
            "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        ),
        (
            "FX-PARTICLES-WEATHER-SNOW-SNOWDEPTH",
            "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER",
            "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR",
        ),
        ("particle", "time", "color_layer"),
        "雪片按深度分层，帧延迟制造短暂停格，水晶材质放大雪片边缘，颜色光轨为不同时间层提供色相",
        "雪会在不同深度以不同时间速度落下，主体动作的短暂停格被雪片晶体边缘染成分层颜色",
        "预览使用近中远三层雪和短帧延迟，强运动时才显示水晶边缘与颜色差异",
        "录制后重建雪片深度、延迟队列和晶体高光，细化主体遮挡、落速变化与色层衔接",
        "冬日人像或慢动作步行中让雪和人的时间速度彼此错开",
        (
        {
    "recipe_id": "RECIPE-SNOW-TIME-COLOR-V1",
    "name_zh": "雪片时间色层·近雪停格",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-SNOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-MATERIAL-APPEARANCE-CRYSTAL",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-PARTICLES-ATMOSPHERE-RAIN"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-SNOW-SNOWDEPTH",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR",
        "FX-PARTICLES-WEATHER-RAIN-RAINVOICE"
    ],
    "trigger_logic": "主体在近景雪片后突然停住而背景雪仍在下落",
    "combined_effect": "近景雪片短暂停格并折射出亮色边，主体动作保留一层延迟姿态，远景雪继续移动",
    "why_new": "雪片深度决定谁被停格，人体时间层与粒子时间层形成前后错速",
    "preview_behavior": "预览使用近中远三层雪和短帧延迟，强运动时才显示水晶边缘与颜色差异。针对近雪停格，取景器先在“主体在近景雪片后突然停住而背景雪仍在下落”发生前标出候选轨迹，确认后才显示“近景雪片短暂停格并折射出亮色边，主体动作保留一层延迟姿态，远景雪继续移动”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建雪片深度、延迟队列和晶体高光，细化主体遮挡、落速变化与色层衔接。录后以“主体在近景雪片后突然停住而背景雪仍在下落”的首帧为时间锚，重新计算近雪停格涉及的遮挡和深度，使“近景雪片短暂停格并折射出亮色边，主体动作保留一层延迟姿态，远景雪继续移动”在原分辨率下保持连续；检测到近景雪遮挡主体脸部，限制停格雪片数量时仅修补低置信度片段。",
    "risks": [
        "近景雪遮挡主体脸部，限制停格雪片数量"
    ],
    "target_scenarios": [
        "雨后街道的人物跟拍适合拍摄近雪停格：先让主体完成“主体在近景雪片后突然停住而背景雪仍在下落”，随后缓慢移动手机观察“近景雪片短暂停格并折射出亮色边，主体动作保留一层延迟姿态，远景雪继续移动”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SNOW-TIME-COLOR-V2",
    "name_zh": "雪片时间色层·晶体脚步",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-SNOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-MATERIAL-APPEARANCE-CRYSTAL",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-PARTICLES-ATMOSPHERE-DUST"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-SNOW-SNOWDEPTH",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR",
        "FX-PARTICLES-WEATHER-DUST-DUSTLIGHT"
    ],
    "trigger_logic": "脚步经过雪幕且帧延迟检测到一个明显步态峰值",
    "combined_effect": "步态峰值被切成晶体边缘姿态，落在脚边的雪片按颜色顺序闪出短暂轨迹",
    "why_new": "粒子落点和人体姿态共享时间层，脚步因此在雪中留下可读色序",
    "preview_behavior": "移动端预览从晶体脚步的结果层反推触发：屏幕持续保留对象身份和最近历史，当“脚步经过雪幕且帧延迟检测到一个明显步态峰值”成立时，把“步态峰值被切成晶体边缘姿态，落在脚边的雪片按颜色顺序闪出短暂轨迹”分成进入、保持、退场三段显示。若出现脚步遮挡会让轨迹缺段，保留踝部附近粒子，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把晶体脚步拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“脚步经过雪幕且帧延迟检测到一个明显步态峰值”，再细化“步态峰值被切成晶体边缘姿态，落在脚边的雪片按颜色顺序闪出短暂轨迹”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "脚步遮挡会让轨迹缺段，保留踝部附近粒子"
    ],
    "target_scenarios": [
        "在逆光窗边的手势近景使用晶体脚步。镜头从未触发状态开始横向移动，人物或物体执行“脚步经过雪幕且帧延迟检测到一个明显步态峰值”后继续穿过画面，以“步态峰值被切成晶体边缘姿态，落在脚边的雪片按颜色顺序闪出短暂轨迹”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SNOW-TIME-COLOR-V3",
    "name_zh": "雪片时间色层·三色飘雪",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-SNOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-MATERIAL-APPEARANCE-CRYSTAL",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-SNOW-SNOWDEPTH",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR",
        "FX-PARTICLES-WEATHER-SNOW-SNOWTOUCH"
    ],
    "trigger_logic": "画面中前中后景雪层都稳定且人物完成转身",
    "combined_effect": "前景雪呈冷色、中景雪呈中性色、后景雪呈暖色，转身时三层颜色分别延迟半拍切换",
    "why_new": "深度和时间延迟共同决定色层，颜色变化不覆盖全画面而随雪层发生",
    "preview_behavior": "拍摄者先看到三色飘雪所需的对象边界、方向箭头和时间门；“画面中前中后景雪层都稳定且人物完成转身”被连续确认后，预览按由近到远的层次展开“前景雪呈冷色、中景雪呈中性色、后景雪呈暖色，转身时三层颜色分别延迟半拍切换”。雪会在不同深度以不同时间速度落下，主体动作的短暂停格被雪片晶体边缘染成分层颜色，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验三色飘雪的身份链与事件顺序，再按雪片按深度分层，帧延迟制造短暂停格，水晶材质放大雪片边缘，颜色光轨为不同时间层提供色相重建组件关系。“前景雪呈冷色、中景雪呈中性色、后景雪呈暖色，转身时三层颜色分别延迟半拍切换”使用完整历史窗口重新渲染，而“画面中前中后景雪层都稳定且人物完成转身”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "深度层错位会造成颜色跳层，降低远景色差"
    ],
    "target_scenarios": [
        "把三色飘雪安排在雪地步行动作的侧面机位：固定主体身份后执行“画面中前中后景雪层都稳定且人物完成转身”，拍摄者绕触发点改变观察角度，用“前景雪呈冷色、中景雪呈中性色、后景雪呈暖色，转身时三层颜色分别延迟半拍切换”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SNOW-TIME-COLOR-V4",
    "name_zh": "雪片时间色层·雪片回卷",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-SNOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-MATERIAL-APPEARANCE-CRYSTAL",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-SNOW-SNOWDEPTH",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR",
        "FX-PARTICLES-WEATHER-LYRIC-LYRICORBIT"
    ],
    "trigger_logic": "用户向后拖动录后时间游标并选择一片雪作为焦点",
    "combined_effect": "焦点雪片逆向上升，附近雪片按距离依次回卷，主体延迟姿态保持不变",
    "why_new": "局部时间反向只作用于雪层，主体的时间状态成为对照",
    "preview_behavior": "为预览雪片回卷，系统只更新与“用户向后拖动录后时间游标并选择一片雪作为焦点”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“焦点雪片逆向上升，附近雪片按距离依次回卷，主体延迟姿态保持不变”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "雪片回卷的后处理从失败点开始：针对“焦点雪片选择不稳会回卷错误区域，使用最近深度峰值”复核掩码、锚点或时间戳，通过后才将“焦点雪片逆向上升，附近雪片按距离依次回卷，主体延迟姿态保持不变”提升到成片质量。触发逻辑“用户向后拖动录后时间游标并选择一片雪作为焦点”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "焦点雪片选择不稳会回卷错误区域，使用最近深度峰值"
    ],
    "target_scenarios": [
        "花瓣与人物视线同框的环绕镜头可用雪片回卷组织一段连续互动。参与者先保持关系稳定，再完成“用户向后拖动录后时间游标并选择一片雪作为焦点”；镜头不切断，直到“焦点雪片逆向上升，附近雪片按距离依次回卷，主体延迟姿态保持不变”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SNOW-TIME-COLOR-V5",
    "name_zh": "雪片时间色层·融雪换色",
    "component_atom_ids": [
        "ATOM-PARTICLES-ATMOSPHERE-SNOW",
        "ATOM-TEMPORAL-STATE-FRAME-DELAY",
        "ATOM-MATERIAL-APPEARANCE-CRYSTAL",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-PARTICLES-ATMOSPHERE-SMOKE"
    ],
    "component_effect_ids": [
        "FX-PARTICLES-WEATHER-SNOW-SNOWDEPTH",
        "FX-BODY-MOTION-CLONES-TIME-TIMESTUTTER",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-COLOR",
        "FX-PARTICLES-WEATHER-PETAL-PETALFOLLOW"
    ],
    "trigger_logic": "雪片落到被太阳照亮的区域且晶体高光达到峰值",
    "combined_effect": "落点雪片短暂停格后融化成一条彩色光线，原落速被延迟帧拉长并逐渐消失",
    "why_new": "材质相变、时间拉伸和色层释放串成一个落点事件，不是普通雪花叠加",
    "preview_behavior": "融雪换色的取景反馈以结束状态为目标：预览先保留真实动作，在“雪片落到被太阳照亮的区域且晶体高光达到峰值”完成时快速呈现“落点雪片短暂停格后融化成一条彩色光线，原落速被延迟帧拉长并逐渐消失”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留融雪换色的完整生命周期。系统逆向检查“落点雪片短暂停格后融化成一条彩色光线，原落速被延迟帧拉长并逐渐消失”是否回到稳定终态，再从“雪片落到被太阳照亮的区域且晶体高光达到峰值”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "高光区域过多会造成彩线泛滥，设置单位面积上限"
    ],
    "target_scenarios": [
        "以粒子回收到触发点的结尾画面作为融雪换色的结尾段落：让“雪片落到被太阳照亮的区域且晶体高光达到峰值”发生在最后一个动作峰值，保持机位直到“落点雪片短暂停格后融化成一条彩色光线，原落速被延迟帧拉长并逐渐消失”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "PORTAL-TOUCH-PARTICLES", "spatial_world", "触摸掌窗粒子门户",
        (
            "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
            "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
            "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
            "ATOM-PARTICLES-ATMOSPHERE-BUBBLES",
        ),
        (
            "FX-SPATIAL-PORTALS-PALM-PALMTHROW",
            "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
            "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH",
        ),
        ("touch_gesture", "spatial_portal", "particle"),
        "触摸画线先定义门户边界，手部三维轨迹决定掌窗姿态，粒子沿入口边缘流动并响应抛出路径",
        "用户在屏幕上画出的掌窗会脱离屏幕成为空间入口，抛出时带着粒子尾流飞到真实场景平面",
        "预览保留触摸线、掌窗粗边和少量气泡粒子，确认闭合后才尝试三维抛出",
        "录制后重建触摸曲线、手部遮挡、门户厚度和粒子碰撞，细化掌窗飞行与落点",
        "旅行或日常记录中用手指圈出一个小窗口，把另一段空间抛到桌面或墙上",
        (
        {
    "recipe_id": "RECIPE-PORTAL-TOUCH-PARTICLES-V1",
    "name_zh": "触摸掌窗粒子门户·掌中开窗",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-BUBBLES",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PALM-PALMTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELORBIT"
    ],
    "trigger_logic": "用户画出闭合圆形并用手掌覆盖窗口边缘",
    "combined_effect": "圆形触摸线变成掌间薄窗，气泡粒子从窗内向外冒出，手指遮挡窗框一侧",
    "why_new": "触摸路径给出边界，真实手部遮挡决定窗的前后关系，掌窗因此具有厚度",
    "preview_behavior": "预览保留触摸线、掌窗粗边和少量气泡粒子，确认闭合后才尝试三维抛出。针对掌中开窗，取景器先在“用户画出闭合圆形并用手掌覆盖窗口边缘”发生前标出候选轨迹，确认后才显示“圆形触摸线变成掌间薄窗，气泡粒子从窗内向外冒出，手指遮挡窗框一侧”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建触摸曲线、手部遮挡、门户厚度和粒子碰撞，细化掌窗飞行与落点。录后以“用户画出闭合圆形并用手掌覆盖窗口边缘”的首帧为时间锚，重新计算掌中开窗涉及的遮挡和深度，使“圆形触摸线变成掌间薄窗，气泡粒子从窗内向外冒出，手指遮挡窗框一侧”在原分辨率下保持连续；检测到闭合误差过大会生成裂窗，自动连接首尾并降低粒子密度时仅修补低置信度片段。",
    "risks": [
        "闭合误差过大会生成裂窗，自动连接首尾并降低粒子密度"
    ],
    "target_scenarios": [
        "门框前的人物穿越镜头适合拍摄掌中开窗：先让主体完成“用户画出闭合圆形并用手掌覆盖窗口边缘”，随后缓慢移动手机观察“圆形触摸线变成掌间薄窗，气泡粒子从窗内向外冒出，手指遮挡窗框一侧”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-PORTAL-TOUCH-PARTICLES-V2",
    "name_zh": "触摸掌窗粒子门户·抛向桌面",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-BUBBLES",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PALM-PALMTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORROTATE"
    ],
    "trigger_logic": "掌窗闭合后用户向桌面方向做出抛手势",
    "combined_effect": "掌窗沿三维手势曲线飞到桌面，落点展开为可见入口，气泡在落点周围回旋",
    "why_new": "抛手势改变门户的世界锚点和方向，窗口从UI对象变成场景物体",
    "preview_behavior": "移动端预览从抛向桌面的结果层反推触发：屏幕持续保留对象身份和最近历史，当“掌窗闭合后用户向桌面方向做出抛手势”成立时，把“掌窗沿三维手势曲线飞到桌面，落点展开为可见入口，气泡在落点周围回旋”分成进入、保持、退场三段显示。若出现手势深度错误会使窗穿过桌面，使用桌面平面吸附，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把抛向桌面拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“掌窗闭合后用户向桌面方向做出抛手势”，再细化“掌窗沿三维手势曲线飞到桌面，落点展开为可见入口，气泡在落点周围回旋”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "手势深度错误会使窗穿过桌面，使用桌面平面吸附"
    ],
    "target_scenarios": [
        "在长走廊中的纵深推进使用抛向桌面。镜头从未触发状态开始横向移动，人物或物体执行“掌窗闭合后用户向桌面方向做出抛手势”后继续穿过画面，以“掌窗沿三维手势曲线飞到桌面，落点展开为可见入口，气泡在落点周围回旋”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-PORTAL-TOUCH-PARTICLES-V3",
    "name_zh": "触摸掌窗粒子门户·触摸擦门",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-BUBBLES",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PALM-PALMTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE"
    ],
    "trigger_logic": "用户从窗口一侧横向擦过并保持触摸压力连续",
    "combined_effect": "擦过路径把掌窗边缘拉长成一条门缝，粒子沿擦拭方向排队，松手后门缝弹回圆窗",
    "why_new": "擦拭方向同时改变门户形状和粒子排列，交互动作直接塑造空间入口",
    "preview_behavior": "拍摄者先看到触摸擦门所需的对象边界、方向箭头和时间门；“用户从窗口一侧横向擦过并保持触摸压力连续”被连续确认后，预览按由近到远的层次展开“擦过路径把掌窗边缘拉长成一条门缝，粒子沿擦拭方向排队，松手后门缝弹回圆窗”。用户在屏幕上画出的掌窗会脱离屏幕成为空间入口，抛出时带着粒子尾流飞到真实场景平面，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验触摸擦门的身份链与事件顺序，再按触摸画线先定义门户边界，手部三维轨迹决定掌窗姿态，粒子沿入口边缘流动并响应抛出路径重建组件关系。“擦过路径把掌窗边缘拉长成一条门缝，粒子沿擦拭方向排队，松手后门缝弹回圆窗”使用完整历史窗口重新渲染，而“用户从窗口一侧横向擦过并保持触摸压力连续”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "触摸采样稀疏会造成门缝折线，使用路径平滑但保留拐点"
    ],
    "target_scenarios": [
        "把触摸擦门安排在桌面与背景分层的景深镜头：固定主体身份后执行“用户从窗口一侧横向擦过并保持触摸压力连续”，拍摄者绕触发点改变观察角度，用“擦过路径把掌窗边缘拉长成一条门缝，粒子沿擦拭方向排队，松手后门缝弹回圆窗”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-PORTAL-TOUCH-PARTICLES-V4",
    "name_zh": "触摸掌窗粒子门户·双窗相撞",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-BUBBLES",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PALM-PALMTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH"
    ],
    "trigger_logic": "用户连续画出两个窗口并把它们拖向同一点",
    "combined_effect": "两个窗口在碰撞点合成更大的门户，粒子从两侧混色进入，原来的边缘保留为内框",
    "why_new": "两个触摸对象的历史边界被保留并参与合成，结果不是简单放大一扇窗",
    "preview_behavior": "为预览双窗相撞，系统只更新与“用户连续画出两个窗口并把它们拖向同一点”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“两个窗口在碰撞点合成更大的门户，粒子从两侧混色进入，原来的边缘保留为内框”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "双窗相撞的后处理从失败点开始：针对“窗口重叠过早会难以区分，要求两个闭合事件分离”复核掩码、锚点或时间戳，通过后才将“两个窗口在碰撞点合成更大的门户，粒子从两侧混色进入，原来的边缘保留为内框”提升到成片质量。触发逻辑“用户连续画出两个窗口并把它们拖向同一点”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "窗口重叠过早会难以区分，要求两个闭合事件分离"
    ],
    "target_scenarios": [
        "城市墙角的转身一镜到底可用双窗相撞组织一段连续互动。参与者先保持关系稳定，再完成“用户连续画出两个窗口并把它们拖向同一点”；镜头不切断，直到“两个窗口在碰撞点合成更大的门户，粒子从两侧混色进入，原来的边缘保留为内框”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-PORTAL-TOUCH-PARTICLES-V5",
    "name_zh": "触摸掌窗粒子门户·关窗留尘",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-DEFORMATION-SPACE-MIRROR-PORTAL",
        "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
        "ATOM-PARTICLES-ATMOSPHERE-BUBBLES",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PALM-PALMTHROW",
        "FX-PARTICLES-WEATHER-DUST-DUSTTOUCH",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH",
        "FX-WORLD-STYLE-SEASON-SEASONROTATE"
    ],
    "trigger_logic": "用户反向沿窗口边缘擦回起点并抬手",
    "combined_effect": "门户按反向擦线逐段闭合，剩余粒子被吸到最后一点形成一颗悬浮尘核",
    "why_new": "关闭路径控制门户的时间顺序，粒子尘核记录了入口曾经存在的位置",
    "preview_behavior": "关窗留尘的取景反馈以结束状态为目标：预览先保留真实动作，在“用户反向沿窗口边缘擦回起点并抬手”完成时快速呈现“门户按反向擦线逐段闭合，剩余粒子被吸到最后一点形成一颗悬浮尘核”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留关窗留尘的完整生命周期。系统逆向检查“门户按反向擦线逐段闭合，剩余粒子被吸到最后一点形成一颗悬浮尘核”是否回到稳定终态，再从“用户反向沿窗口边缘擦回起点并抬手”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "抬手过早会留下缺口，使用超时自动闭合"
    ],
    "target_scenarios": [
        "以返回原锚点关闭空间层的收尾作为关窗留尘的结尾段落：让“用户反向沿窗口边缘擦回起点并抬手”发生在最后一个动作峰值，保持机位直到“门户按反向擦线逐段闭合，剩余粒子被吸到最后一点形成一颗悬浮尘核”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "WORLD-STYLE-GAZE", "spatial_world", "凝视世界风格切换",
        (
            "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
            "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        ),
        (
            "FX-WORLD-STYLE-SEASON-SEASONGAZE",
            "FX-WORLD-STYLE-COMIC-COMICGAZE",
            "FX-FACE-GAZE-EXPRESSION-SELECT-SELECTDWELL",
        ),
        ("gaze", "generative_world", "world_anchor"),
        "背景世界变换保持场景布局，视线决定先变换的区域，物体姿态保护被注视对象的几何连续，风格变换作为边界内的材质重写",
        "视线停留的区域先进入目标世界风格，视线移开后风格沿物体边缘扩展，主体位置和动作不被抹掉",
        "预览只重写视线附近的低分辨率背景块，物体轮廓保持原始几何并显示扩散边界",
        "录制后对完整背景做时序一致的风格重写，细化视线扩散、物体遮挡与风格边界",
        "旅行、街景或室内漫游中用眼神选择一个区域逐步改变整个世界",
        (
        {
    "recipe_id": "RECIPE-WORLD-STYLE-GAZE-V1",
    "name_zh": "凝视世界风格切换·凝视换季",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-SEASON-SEASONGAZE",
        "FX-WORLD-STYLE-COMIC-COMICGAZE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-SELECTDWELL",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELORBIT"
    ],
    "trigger_logic": "视线停留在一片植物上并保持头部姿态稳定",
    "combined_effect": "植物先变为目标季节的颜色和形态，视线移开后变化沿同一株植物扩展到附近背景",
    "why_new": "凝视位置决定变化起点，物体姿态保持植物空间连续，季节不是全画面一键切换",
    "preview_behavior": "预览只重写视线附近的低分辨率背景块，物体轮廓保持原始几何并显示扩散边界。针对凝视换季，取景器先在“视线停留在一片植物上并保持头部姿态稳定”发生前标出候选轨迹，确认后才显示“植物先变为目标季节的颜色和形态，视线移开后变化沿同一株植物扩展到附近背景”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后对完整背景做时序一致的风格重写，细化视线扩散、物体遮挡与风格边界。录后以“视线停留在一片植物上并保持头部姿态稳定”的首帧为时间锚，重新计算凝视换季涉及的遮挡和深度，使“植物先变为目标季节的颜色和形态，视线移开后变化沿同一株植物扩展到附近背景”在原分辨率下保持连续；检测到细枝分割错误会出现颜色溢出，使用对象实例边界裁切时仅修补低置信度片段。",
    "risks": [
        "细枝分割错误会出现颜色溢出，使用对象实例边界裁切"
    ],
    "target_scenarios": [
        "门框前的人物穿越镜头适合拍摄凝视换季：先让主体完成“视线停留在一片植物上并保持头部姿态稳定”，随后缓慢移动手机观察“植物先变为目标季节的颜色和形态，视线移开后变化沿同一株植物扩展到附近背景”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-WORLD-STYLE-GAZE-V2",
    "name_zh": "凝视世界风格切换·凝视漫画",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-SEASON-SEASONGAZE",
        "FX-WORLD-STYLE-COMIC-COMICGAZE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-SELECTDWELL",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORROTATE"
    ],
    "trigger_logic": "视线从人物转向建筑边缘并停留",
    "combined_effect": "建筑先变成漫画线稿，人物保持真实纹理，移开视线后线稿沿街道透视方向扩散",
    "why_new": "不同对象的风格切换顺序由视线和空间透视共同决定",
    "preview_behavior": "移动端预览从凝视漫画的结果层反推触发：屏幕持续保留对象身份和最近历史，当“视线从人物转向建筑边缘并停留”成立时，把“建筑先变成漫画线稿，人物保持真实纹理，移开视线后线稿沿街道透视方向扩散”分成进入、保持、退场三段显示。若出现建筑纹理重复会引发风格孔洞，使用背景先验填补，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把凝视漫画拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“视线从人物转向建筑边缘并停留”，再细化“建筑先变成漫画线稿，人物保持真实纹理，移开视线后线稿沿街道透视方向扩散”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "建筑纹理重复会引发风格孔洞，使用背景先验填补"
    ],
    "target_scenarios": [
        "在长走廊中的纵深推进使用凝视漫画。镜头从未触发状态开始横向移动，人物或物体执行“视线从人物转向建筑边缘并停留”后继续穿过画面，以“建筑先变成漫画线稿，人物保持真实纹理，移开视线后线稿沿街道透视方向扩散”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-WORLD-STYLE-GAZE-V3",
    "name_zh": "凝视世界风格切换·局部水下",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-SEASON-SEASONGAZE",
        "FX-WORLD-STYLE-COMIC-COMICGAZE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-SELECTDWELL",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE"
    ],
    "trigger_logic": "视线锁定地面反光并缓慢向远处移动",
    "combined_effect": "被注视区域先出现水下焦散与漂浮颗粒，变化沿地面深度层向远处推进",
    "why_new": "视线移动控制世界材质的传播方向，背景世界变换保持原有布局可识别",
    "preview_behavior": "拍摄者先看到局部水下所需的对象边界、方向箭头和时间门；“视线锁定地面反光并缓慢向远处移动”被连续确认后，预览按由近到远的层次展开“被注视区域先出现水下焦散与漂浮颗粒，变化沿地面深度层向远处推进”。视线停留的区域先进入目标世界风格，视线移开后风格沿物体边缘扩展，主体位置和动作不被抹掉，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验局部水下的身份链与事件顺序，再按背景世界变换保持场景布局，视线决定先变换的区域，物体姿态保护被注视对象的几何连续，风格变换作为边界内的材质重写重建组件关系。“被注视区域先出现水下焦散与漂浮颗粒，变化沿地面深度层向远处推进”使用完整历史窗口重新渲染，而“视线锁定地面反光并缓慢向远处移动”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "反光误检会触发错误区域，要求深度与视线交点稳定"
    ],
    "target_scenarios": [
        "把局部水下安排在桌面与背景分层的景深镜头：固定主体身份后执行“视线锁定地面反光并缓慢向远处移动”，拍摄者绕触发点改变观察角度，用“被注视区域先出现水下焦散与漂浮颗粒，变化沿地面深度层向远处推进”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-WORLD-STYLE-GAZE-V4",
    "name_zh": "凝视世界风格切换·霓虹挑选",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-SEASON-SEASONGAZE",
        "FX-WORLD-STYLE-COMIC-COMICGAZE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-SELECTDWELL",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH"
    ],
    "trigger_logic": "视线在多个物体之间扫过并对一个物体停留",
    "combined_effect": "扫过对象只留下细霓虹边，停留对象才被完整点亮并向背景投射同色光",
    "why_new": "扫视和停留是两个不同风格层级，视线历史决定候选与确认",
    "preview_behavior": "为预览霓虹挑选，系统只更新与“视线在多个物体之间扫过并对一个物体停留”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“扫过对象只留下细霓虹边，停留对象才被完整点亮并向背景投射同色光”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "霓虹挑选的后处理从失败点开始：针对“快速扫视会产生过多边线，限制候选数并衰减”复核掩码、锚点或时间戳，通过后才将“扫过对象只留下细霓虹边，停留对象才被完整点亮并向背景投射同色光”提升到成片质量。触发逻辑“视线在多个物体之间扫过并对一个物体停留”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "快速扫视会产生过多边线，限制候选数并衰减"
    ],
    "target_scenarios": [
        "城市墙角的转身一镜到底可用霓虹挑选组织一段连续互动。参与者先保持关系稳定，再完成“视线在多个物体之间扫过并对一个物体停留”；镜头不切断，直到“扫过对象只留下细霓虹边，停留对象才被完整点亮并向背景投射同色光”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-WORLD-STYLE-GAZE-V5",
    "name_zh": "凝视世界风格切换·移开还原",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-SEASON-SEASONGAZE",
        "FX-WORLD-STYLE-COMIC-COMICGAZE",
        "FX-FACE-GAZE-EXPRESSION-SELECT-SELECTDWELL",
        "FX-WORLD-STYLE-SEASON-SEASONROTATE"
    ],
    "trigger_logic": "风格扩散后用户快速把视线移回原点",
    "combined_effect": "扩散区域沿视线逆向收回，最后被凝视物体保留一小块风格印记作为选择反馈",
    "why_new": "撤销由视线运动完成，世界变换有可控的回退路径而不是单纯淡出",
    "preview_behavior": "移开还原的取景反馈以结束状态为目标：预览先保留真实动作，在“风格扩散后用户快速把视线移回原点”完成时快速呈现“扩散区域沿视线逆向收回，最后被凝视物体保留一小块风格印记作为选择反馈”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留移开还原的完整生命周期。系统逆向检查“扩散区域沿视线逆向收回，最后被凝视物体保留一小块风格印记作为选择反馈”是否回到稳定终态，再从“风格扩散后用户快速把视线移回原点”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "回看路径不完整会留下大片风格层，使用最近路径逆向收束"
    ],
    "target_scenarios": [
        "以返回原锚点关闭空间层的收尾作为移开还原的结尾段落：让“风格扩散后用户快速把视线移回原点”发生在最后一个动作峰值，保持机位直到“扩散区域沿视线逆向收回，最后被凝视物体保留一小块风格印记作为选择反馈”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "DEPTH-TIME-WINDOW", "spatial_world", "景深时间窗口",
        (
            "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
            "ATOM-TEMPORAL-STATE-EVENT-WINDOW",
            "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
            "ATOM-DEFORMATION-SPACE-TUNNEL-WARP",
        ),
        (
            "FX-TIME-EDITING-BORROW-BORROWOBJECT",
            "FX-SPATIAL-PORTALS-TUNNEL-TUNNELEND",
            "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH",
        ),
        ("time", "spatial_portal", "world_anchor"),
        "单目深度选择时间窗口的前后层，事件窗口锁定对象历史，隧道形变把目标深度展开为入口，前后景分屏保持比较",
        "用户可以把某个深度层的过去借到当前画面，目标在景深隧道尽头出现，前景仍按实时状态继续",
        "预览用三层深度和短事件窗口，隧道只显示目标轮廓与出口，避免全场景形变",
        "录制后重建对象姿态、深度层和借位窗口，细化隧道出口、分屏边界与前后景遮挡",
        "镜头推进、产品展示或街景中把远处物体的过去拉到眼前比较",
        (
        {
    "recipe_id": "RECIPE-DEPTH-TIME-WINDOW-V1",
    "name_zh": "景深时间窗口·远景借位",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-DEFORMATION-SPACE-TUNNEL-WARP",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-BORROW-BORROWOBJECT",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELEND",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELORBIT"
    ],
    "trigger_logic": "用户点选远处物体并在事件窗口内向前推进镜头",
    "combined_effect": "远处物体的上一状态沿景深隧道借到前景，现实物体仍留在远处形成前后对照",
    "why_new": "时间借位受深度层约束，隧道把历史状态搬运过程显性化",
    "preview_behavior": "预览用三层深度和短事件窗口，隧道只显示目标轮廓与出口，避免全场景形变。针对远景借位，取景器先在“用户点选远处物体并在事件窗口内向前推进镜头”发生前标出候选轨迹，确认后才显示“远处物体的上一状态沿景深隧道借到前景，现实物体仍留在远处形成前后对照”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建对象姿态、深度层和借位窗口，细化隧道出口、分屏边界与前后景遮挡。录后以“用户点选远处物体并在事件窗口内向前推进镜头”的首帧为时间锚，重新计算远景借位涉及的遮挡和深度，使“远处物体的上一状态沿景深隧道借到前景，现实物体仍留在远处形成前后对照”在原分辨率下保持连续；检测到深度估计错层会使借位物体穿过前景，降低借位距离时仅修补低置信度片段。",
    "risks": [
        "深度估计错层会使借位物体穿过前景，降低借位距离"
    ],
    "target_scenarios": [
        "门框前的人物穿越镜头适合拍摄远景借位：先让主体完成“用户点选远处物体并在事件窗口内向前推进镜头”，随后缓慢移动手机观察“远处物体的上一状态沿景深隧道借到前景，现实物体仍留在远处形成前后对照”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-DEPTH-TIME-WINDOW-V2",
    "name_zh": "景深时间窗口·近物穿隧",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-DEFORMATION-SPACE-TUNNEL-WARP",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-BORROW-BORROWOBJECT",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELEND",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORROTATE"
    ],
    "trigger_logic": "近处物体离开画面边缘而远处出口保持稳定",
    "combined_effect": "近物的历史姿态从画面侧边进入隧道，在远处出口处以较小比例重现",
    "why_new": "入口与出口的比例由深度决定，时间窗口保留了对象过去的姿态",
    "preview_behavior": "移动端预览从近物穿隧的结果层反推触发：屏幕持续保留对象身份和最近历史，当“近处物体离开画面边缘而远处出口保持稳定”成立时，把“近物的历史姿态从画面侧边进入隧道，在远处出口处以较小比例重现”分成进入、保持、退场三段显示。若出现物体尺度估计不稳会产生跳缩，使用对象姿态历史平滑，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把近物穿隧拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“近处物体离开画面边缘而远处出口保持稳定”，再细化“近物的历史姿态从画面侧边进入隧道，在远处出口处以较小比例重现”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "物体尺度估计不稳会产生跳缩，使用对象姿态历史平滑"
    ],
    "target_scenarios": [
        "在长走廊中的纵深推进使用近物穿隧。镜头从未触发状态开始横向移动，人物或物体执行“近处物体离开画面边缘而远处出口保持稳定”后继续穿过画面，以“近物的历史姿态从画面侧边进入隧道，在远处出口处以较小比例重现”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-DEPTH-TIME-WINDOW-V3",
    "name_zh": "景深时间窗口·深度分屏",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-DEFORMATION-SPACE-TUNNEL-WARP",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-BORROW-BORROWOBJECT",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELEND",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE"
    ],
    "trigger_logic": "用户向下拖动时间窗口并同时锁定前景与背景对象",
    "combined_effect": "前景显示当前帧、背景显示借来的历史帧，中间以隧道边缘连接，两个对象仍按真实深度遮挡",
    "why_new": "分屏不是固定左右布局，而是由景深边界生成，时间差可以沿空间比较",
    "preview_behavior": "拍摄者先看到深度分屏所需的对象边界、方向箭头和时间门；“用户向下拖动时间窗口并同时锁定前景与背景对象”被连续确认后，预览按由近到远的层次展开“前景显示当前帧、背景显示借来的历史帧，中间以隧道边缘连接，两个对象仍按真实深度遮挡”。用户可以把某个深度层的过去借到当前画面，目标在景深隧道尽头出现，前景仍按实时状态继续，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验深度分屏的身份链与事件顺序，再按单目深度选择时间窗口的前后层，事件窗口锁定对象历史，隧道形变把目标深度展开为入口，前后景分屏保持比较重建组件关系。“前景显示当前帧、背景显示借来的历史帧，中间以隧道边缘连接，两个对象仍按真实深度遮挡”使用完整历史窗口重新渲染，而“用户向下拖动时间窗口并同时锁定前景与背景对象”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "前后景边界移动会抖动，使用事件窗口滞回"
    ],
    "target_scenarios": [
        "把深度分屏安排在桌面与背景分层的景深镜头：固定主体身份后执行“用户向下拖动时间窗口并同时锁定前景与背景对象”，拍摄者绕触发点改变观察角度，用“前景显示当前帧、背景显示借来的历史帧，中间以隧道边缘连接，两个对象仍按真实深度遮挡”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-DEPTH-TIME-WINDOW-V4",
    "name_zh": "景深时间窗口·出口回看",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-DEFORMATION-SPACE-TUNNEL-WARP",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-BORROW-BORROWOBJECT",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELEND",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH",
        "FX-WORLD-STYLE-SEASON-SEASONROTATE"
    ],
    "trigger_logic": "用户注视隧道出口并向镜头回头",
    "combined_effect": "出口显示对象刚才的姿态，回头动作让出口时间倒退一小段并重新对齐当前物体",
    "why_new": "视线确认和回头事件共同改变历史窗口，观看动作成为时间导航",
    "preview_behavior": "为预览出口回看，系统只更新与“用户注视隧道出口并向镜头回头”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“出口显示对象刚才的姿态，回头动作让出口时间倒退一小段并重新对齐当前物体”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "出口回看的后处理从失败点开始：针对“回头检测误触发会倒退错误对象，要求目标深度稳定”复核掩码、锚点或时间戳，通过后才将“出口显示对象刚才的姿态，回头动作让出口时间倒退一小段并重新对齐当前物体”提升到成片质量。触发逻辑“用户注视隧道出口并向镜头回头”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "回头检测误触发会倒退错误对象，要求目标深度稳定"
    ],
    "target_scenarios": [
        "城市墙角的转身一镜到底可用出口回看组织一段连续互动。参与者先保持关系稳定，再完成“用户注视隧道出口并向镜头回头”；镜头不切断，直到“出口显示对象刚才的姿态，回头动作让出口时间倒退一小段并重新对齐当前物体”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-DEPTH-TIME-WINDOW-V5",
    "name_zh": "景深时间窗口·窗口合拢",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH",
        "ATOM-TEMPORAL-STATE-EVENT-WINDOW",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-DEFORMATION-SPACE-TUNNEL-WARP",
        "ATOM-CLONING-ECHOES-SPATIAL-DUPLICATE"
    ],
    "component_effect_ids": [
        "FX-TIME-EDITING-BORROW-BORROWOBJECT",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELEND",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR"
    ],
    "trigger_logic": "对象回到原深度位置且事件窗口结束",
    "combined_effect": "隧道沿深度方向收缩，借位对象逐层回到原时间，最后只留下出口处一圈薄光",
    "why_new": "时间窗口结束和空间回位共同完成合拢，效果拥有可审计的生命周期",
    "preview_behavior": "窗口合拢的取景反馈以结束状态为目标：预览先保留真实动作，在“对象回到原深度位置且事件窗口结束”完成时快速呈现“隧道沿深度方向收缩，借位对象逐层回到原时间，最后只留下出口处一圈薄光”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留窗口合拢的完整生命周期。系统逆向检查“隧道沿深度方向收缩，借位对象逐层回到原时间，最后只留下出口处一圈薄光”是否回到稳定终态，再从“对象回到原深度位置且事件窗口结束”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "对象出框会无法回位，保存最后深度并淡出"
    ],
    "target_scenarios": [
        "以返回原锚点关闭空间层的收尾作为窗口合拢的结尾段落：让“对象回到原深度位置且事件窗口结束”发生在最后一个动作峰值，保持机位直到“隧道沿深度方向收缩，借位对象逐层回到原时间，最后只留下出口处一圈薄光”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "COMIC-POSE-LIGHT", "spatial_world", "漫画姿态速度光",
        (
            "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
            "ATOM-DEFORMATION-SPACE-COMIC-SPEED-LINES",
            "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
            "ATOM-INTERACTION-TRIGGERS-BODY-POSE",
        ),
        (
            "FX-WORLD-STYLE-COMIC-COMICMOVE",
            "FX-LIGHT-TRAILS-OPTICS-BODY-SILHOUETTE",
            "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        ),
        ("body_pose", "realtime_light_trail", "time"),
        "骨骼姿态提供动作方向，漫画速度线沿动作切线布局，星芒标记姿态峰值，快门切片保留动作阶段",
        "人物动作会被拆成带速度线和星芒节点的漫画姿态页，动作峰值短暂停留后继续向下一格推进",
        "预览只渲染骨骼关键段、少量速度线和一个峰值星芒，动作峰值时提高快门切片密度",
        "录制后重建姿态阶段、速度线透视和星芒遮挡，细化多肢体交叉及漫画层与真人层的边界",
        "跑步、跳跃或运动短片中把连续动作变成可读的漫画分镜",
        (
        {
    "recipe_id": "RECIPE-COMIC-POSE-LIGHT-V1",
    "name_zh": "漫画姿态速度光·冲刺分镜",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-DEFORMATION-SPACE-COMIC-SPEED-LINES",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE",
        "ATOM-GEOMETRY-TRACKING-MONOCULAR-DEPTH"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICMOVE",
        "FX-LIGHT-TRAILS-OPTICS-BODY-SILHOUETTE",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-SPATIAL-PORTALS-TUNNEL-TUNNELORBIT"
    ],
    "trigger_logic": "人物从静止突然向前冲刺并经过第一个速度峰值",
    "combined_effect": "静止、起跑和冲刺姿态排列成三格漫画层，速度线从脚后方向前景汇聚，峰值处爆出星芒",
    "why_new": "姿态阶段决定分镜、运动方向决定速度线、峰值决定星芒，三者共同描述动作",
    "preview_behavior": "预览只渲染骨骼关键段、少量速度线和一个峰值星芒，动作峰值时提高快门切片密度。针对冲刺分镜，取景器先在“人物从静止突然向前冲刺并经过第一个速度峰值”发生前标出候选轨迹，确认后才显示“静止、起跑和冲刺姿态排列成三格漫画层，速度线从脚后方向前景汇聚，峰值处爆出星芒”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建姿态阶段、速度线透视和星芒遮挡，细化多肢体交叉及漫画层与真人层的边界。录后以“人物从静止突然向前冲刺并经过第一个速度峰值”的首帧为时间锚，重新计算冲刺分镜涉及的遮挡和深度，使“静止、起跑和冲刺姿态排列成三格漫画层，速度线从脚后方向前景汇聚，峰值处爆出星芒”在原分辨率下保持连续；检测到脚步追踪丢失会让速度线反向，使用躯干方向校正时仅修补低置信度片段。",
    "risks": [
        "脚步追踪丢失会让速度线反向，使用躯干方向校正"
    ],
    "target_scenarios": [
        "门框前的人物穿越镜头适合拍摄冲刺分镜：先让主体完成“人物从静止突然向前冲刺并经过第一个速度峰值”，随后缓慢移动手机观察“静止、起跑和冲刺姿态排列成三格漫画层，速度线从脚后方向前景汇聚，峰值处爆出星芒”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-COMIC-POSE-LIGHT-V2",
    "name_zh": "漫画姿态速度光·跳跃定格",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-DEFORMATION-SPACE-COMIC-SPEED-LINES",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICMOVE",
        "FX-LIGHT-TRAILS-OPTICS-BODY-SILHOUETTE",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-SPATIAL-PORTALS-FLOOR-FLOORROTATE"
    ],
    "trigger_logic": "人物进入空中姿态并做出指定定格手势",
    "combined_effect": "身体轮廓变成一格粗线漫画剪影，手势位置出现星芒，恢复下落时剪影沿快门层碎开",
    "why_new": "定格手势是分镜确认，时间切片负责从定格过渡回连续动作",
    "preview_behavior": "移动端预览从跳跃定格的结果层反推触发：屏幕持续保留对象身份和最近历史，当“人物进入空中姿态并做出指定定格手势”成立时，把“身体轮廓变成一格粗线漫画剪影，手势位置出现星芒，恢复下落时剪影沿快门层碎开”分成进入、保持、退场三段显示。若出现手势误检会提前定格，要求姿态和停留同时满足，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把跳跃定格拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“人物进入空中姿态并做出指定定格手势”，再细化“身体轮廓变成一格粗线漫画剪影，手势位置出现星芒，恢复下落时剪影沿快门层碎开”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "手势误检会提前定格，要求姿态和停留同时满足"
    ],
    "target_scenarios": [
        "在长走廊中的纵深推进使用跳跃定格。镜头从未触发状态开始横向移动，人物或物体执行“人物进入空中姿态并做出指定定格手势”后继续穿过画面，以“身体轮廓变成一格粗线漫画剪影，手势位置出现星芒，恢复下落时剪影沿快门层碎开”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-COMIC-POSE-LIGHT-V3",
    "name_zh": "漫画姿态速度光·挥拳速度线",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-DEFORMATION-SPACE-COMIC-SPEED-LINES",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICMOVE",
        "FX-LIGHT-TRAILS-OPTICS-BODY-SILHOUETTE",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-SPATIAL-PORTALS-MIRROR-MIRRORGAZE"
    ],
    "trigger_logic": "手腕朝镜头方向快速运动且肩肘连接稳定",
    "combined_effect": "拳头周围出现向后拉伸的漫画速度线，肩肘关节以不同亮度组成一条发光动作骨架",
    "why_new": "速度线和骨架光绘共享手臂路径，漫画效果因此保留身体结构",
    "preview_behavior": "拍摄者先看到挥拳速度线所需的对象边界、方向箭头和时间门；“手腕朝镜头方向快速运动且肩肘连接稳定”被连续确认后，预览按由近到远的层次展开“拳头周围出现向后拉伸的漫画速度线，肩肘关节以不同亮度组成一条发光动作骨架”。人物动作会被拆成带速度线和星芒节点的漫画姿态页，动作峰值短暂停留后继续向下一格推进，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验挥拳速度线的身份链与事件顺序，再按骨骼姿态提供动作方向，漫画速度线沿动作切线布局，星芒标记姿态峰值，快门切片保留动作阶段重建组件关系。“拳头周围出现向后拉伸的漫画速度线，肩肘关节以不同亮度组成一条发光动作骨架”使用完整历史窗口重新渲染，而“手腕朝镜头方向快速运动且肩肘连接稳定”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "透视方向错估会让拳头拉伸过度，限制最大伸长"
    ],
    "target_scenarios": [
        "把挥拳速度线安排在桌面与背景分层的景深镜头：固定主体身份后执行“手腕朝镜头方向快速运动且肩肘连接稳定”，拍摄者绕触发点改变观察角度，用“拳头周围出现向后拉伸的漫画速度线，肩肘关节以不同亮度组成一条发光动作骨架”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-COMIC-POSE-LIGHT-V4",
    "name_zh": "漫画姿态速度光·转身星爆",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-DEFORMATION-SPACE-COMIC-SPEED-LINES",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICMOVE",
        "FX-LIGHT-TRAILS-OPTICS-BODY-SILHOUETTE",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDEPTH"
    ],
    "trigger_logic": "身体完成快速转身并在终点停住",
    "combined_effect": "转身前后姿态作为两页交错叠放，终点星芒沿肩线爆开，速度线在两页之间形成弧形翻页",
    "why_new": "时间切片表达前后页，姿态方向决定翻页弧线，星芒提供动作终点",
    "preview_behavior": "为预览转身星爆，系统只更新与“身体完成快速转身并在终点停住”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“转身前后姿态作为两页交错叠放，终点星芒沿肩线爆开，速度线在两页之间形成弧形翻页”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "转身星爆的后处理从失败点开始：针对“肩线遮挡会让翻页断裂，使用胸口参考补边”复核掩码、锚点或时间戳，通过后才将“转身前后姿态作为两页交错叠放，终点星芒沿肩线爆开，速度线在两页之间形成弧形翻页”提升到成片质量。触发逻辑“身体完成快速转身并在终点停住”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "肩线遮挡会让翻页断裂，使用胸口参考补边"
    ],
    "target_scenarios": [
        "城市墙角的转身一镜到底可用转身星爆组织一段连续互动。参与者先保持关系稳定，再完成“身体完成快速转身并在终点停住”；镜头不切断，直到“转身前后姿态作为两页交错叠放，终点星芒沿肩线爆开，速度线在两页之间形成弧形翻页”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-COMIC-POSE-LIGHT-V5",
    "name_zh": "漫画姿态速度光·多人追格",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-BODY-SKELETON",
        "ATOM-DEFORMATION-SPACE-COMIC-SPEED-LINES",
        "ATOM-LIGHT-OPTICS-DYNAMIC-STARBURST",
        "ATOM-INTERACTION-TRIGGERS-BODY-POSE",
        "ATOM-INTERACTION-TRIGGERS-PHONE-ROTATION"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICMOVE",
        "FX-LIGHT-TRAILS-OPTICS-BODY-SILHOUETTE",
        "FX-TIME-EDITING-SHUTTER-SHUTTERPOSE",
        "FX-WORLD-STYLE-SEASON-SEASONROTATE"
    ],
    "trigger_logic": "两人前后交替进入同一动作姿态",
    "combined_effect": "先到者留下漫画轮廓格，后到者沿速度线追上并让两格在峰值处合成双星芒",
    "why_new": "时间顺序和人体关系使同一动作成为追逐分镜，不是多人同时套滤镜",
    "preview_behavior": "多人追格的取景反馈以结束状态为目标：预览先保留真实动作，在“两人前后交替进入同一动作姿态”完成时快速呈现“先到者留下漫画轮廓格，后到者沿速度线追上并让两格在峰值处合成双星芒”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留多人追格的完整生命周期。系统逆向检查“先到者留下漫画轮廓格，后到者沿速度线追上并让两格在峰值处合成双星芒”是否回到稳定终态，再从“两人前后交替进入同一动作姿态”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "两人深度相近会错合，使用进入时间优先"
    ],
    "target_scenarios": [
        "以返回原锚点关闭空间层的收尾作为多人追格的结尾段落：让“两人前后交替进入同一动作姿态”发生在最后一个动作峰值，保持机位直到“先到者留下漫画轮廓格，后到者沿速度线追上并让两格在峰值处合成双星芒”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "MATERIAL-TOUCH-SOUND", "material_generation", "触摸玻璃声波",
        (
            "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
            "ATOM-MATERIAL-APPEARANCE-GLASS",
            "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
            "ATOM-DEFORMATION-SPACE-RIPPLE-DISPLACEMENT",
        ),
        (
            "FX-MATERIAL-MORPH-GLASS-GLASSTOUCH",
            "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
            "FX-MATERIAL-MORPH-GLASS-GLASSBEAT",
        ),
        ("touch_gesture", "sound", "material"),
        "触摸轨迹定义玻璃表面的敲击和划痕，声音音量控制波纹半径，玻璃材质与波纹位移共同形成可见声场",
        "指尖触碰画面会像敲击一块透明玻璃，声音越响波纹越深，波纹相遇时在玻璃表面折射出亮色",
        "预览只维护触摸点和少量波纹环，音量变化调整环厚度，避免每帧生成完整玻璃折射",
        "录制后细化触摸采样、玻璃高光、波纹位移和声音包络，处理波纹相遇与人物遮挡",
        "自拍、产品展示或音乐视频中把屏幕触摸变成一块会响应声音的玻璃表面",
        (
        {
    "recipe_id": "RECIPE-MATERIAL-TOUCH-SOUND-V1",
    "name_zh": "触摸玻璃声波·指尖敲窗",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-MATERIAL-APPEARANCE-GLASS",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-DEFORMATION-SPACE-RIPPLE-DISPLACEMENT",
        "ATOM-MATERIAL-APPEARANCE-LIQUID"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-GLASS-GLASSTOUCH",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-GLASS-GLASSBEAT",
        "FX-MATERIAL-MORPH-GLASS-GLASSBREAK"
    ],
    "trigger_logic": "用户在玻璃区域点按三次且每次点按伴随音量峰值",
    "combined_effect": "每次点按产生一圈玻璃波纹，音量峰值让波纹深度不同，三圈相遇时折射出细亮线",
    "why_new": "触摸提供空间位置，音量提供物理强度，玻璃折射把两者相遇变成可见结构",
    "preview_behavior": "预览只维护触摸点和少量波纹环，音量变化调整环厚度，避免每帧生成完整玻璃折射。针对指尖敲窗，取景器先在“用户在玻璃区域点按三次且每次点按伴随音量峰值”发生前标出候选轨迹，确认后才显示“每次点按产生一圈玻璃波纹，音量峰值让波纹深度不同，三圈相遇时折射出细亮线”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化触摸采样、玻璃高光、波纹位移和声音包络，处理波纹相遇与人物遮挡。录后以“用户在玻璃区域点按三次且每次点按伴随音量峰值”的首帧为时间锚，重新计算指尖敲窗涉及的遮挡和深度，使“每次点按产生一圈玻璃波纹，音量峰值让波纹深度不同，三圈相遇时折射出细亮线”在原分辨率下保持连续；检测到点按过密会造成波纹糊成一片，限制同时存在的波纹数时仅修补低置信度片段。",
    "risks": [
        "点按过密会造成波纹糊成一片，限制同时存在的波纹数"
    ],
    "target_scenarios": [
        "玻璃橱窗前的手势特写适合拍摄指尖敲窗：先让主体完成“用户在玻璃区域点按三次且每次点按伴随音量峰值”，随后缓慢移动手机观察“每次点按产生一圈玻璃波纹，音量峰值让波纹深度不同，三圈相遇时折射出细亮线”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-MATERIAL-TOUCH-SOUND-V2",
    "name_zh": "触摸玻璃声波·划痕声带",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-MATERIAL-APPEARANCE-GLASS",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-DEFORMATION-SPACE-RIPPLE-DISPLACEMENT",
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-GLASS-GLASSTOUCH",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-GLASS-GLASSBEAT",
        "FX-MATERIAL-MORPH-METAL-METALFLOW"
    ],
    "trigger_logic": "用户拖动指尖形成曲线且声音保持中等音量",
    "combined_effect": "指尖曲线成为玻璃划痕，声音沿划痕生成连续声带，抬手后声带从末端向起点消退",
    "why_new": "触摸路径和声音时间包络共同生成有方向的表面痕迹，不是静态纹理",
    "preview_behavior": "移动端预览从划痕声带的结果层反推触发：屏幕持续保留对象身份和最近历史，当“用户拖动指尖形成曲线且声音保持中等音量”成立时，把“指尖曲线成为玻璃划痕，声音沿划痕生成连续声带，抬手后声带从末端向起点消退”分成进入、保持、退场三段显示。若出现触摸采样断开会使划痕缺口，使用最近两点连接，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把划痕声带拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“用户拖动指尖形成曲线且声音保持中等音量”，再细化“指尖曲线成为玻璃划痕，声音沿划痕生成连续声带，抬手后声带从末端向起点消退”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "触摸采样断开会使划痕缺口，使用最近两点连接"
    ],
    "target_scenarios": [
        "在服装材质变化的半身跟拍使用划痕声带。镜头从未触发状态开始横向移动，人物或物体执行“用户拖动指尖形成曲线且声音保持中等音量”后继续穿过画面，以“指尖曲线成为玻璃划痕，声音沿划痕生成连续声带，抬手后声带从末端向起点消退”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-MATERIAL-TOUCH-SOUND-V3",
    "name_zh": "触摸玻璃声波·强拍裂纹",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-MATERIAL-APPEARANCE-GLASS",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-DEFORMATION-SPACE-RIPPLE-DISPLACEMENT",
        "ATOM-MATERIAL-APPEARANCE-HOLOGRAPHIC"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-GLASS-GLASSTOUCH",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-GLASS-GLASSBEAT",
        "FX-MATERIAL-MORPH-PAPER-PAPERTEAR"
    ],
    "trigger_logic": "闭合触摸线完成时检测到音乐强拍",
    "combined_effect": "闭合线瞬间裂成几块玻璃片，强拍把裂纹边缘点亮，下一拍玻璃片重新拼回原线",
    "why_new": "闭合手势决定裂纹拓扑，节拍决定破裂和重组时刻",
    "preview_behavior": "拍摄者先看到强拍裂纹所需的对象边界、方向箭头和时间门；“闭合触摸线完成时检测到音乐强拍”被连续确认后，预览按由近到远的层次展开“闭合线瞬间裂成几块玻璃片，强拍把裂纹边缘点亮，下一拍玻璃片重新拼回原线”。指尖触碰画面会像敲击一块透明玻璃，声音越响波纹越深，波纹相遇时在玻璃表面折射出亮色，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验强拍裂纹的身份链与事件顺序，再按触摸轨迹定义玻璃表面的敲击和划痕，声音音量控制波纹半径，玻璃材质与波纹位移共同形成可见声场重建组件关系。“闭合线瞬间裂成几块玻璃片，强拍把裂纹边缘点亮，下一拍玻璃片重新拼回原线”使用完整历史窗口重新渲染，而“闭合触摸线完成时检测到音乐强拍”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "闭合线自交会产生过多碎片，简化自交区域"
    ],
    "target_scenarios": [
        "把强拍裂纹安排在前景物体碎裂与复原的桌面镜头：固定主体身份后执行“闭合触摸线完成时检测到音乐强拍”，拍摄者绕触发点改变观察角度，用“闭合线瞬间裂成几块玻璃片，强拍把裂纹边缘点亮，下一拍玻璃片重新拼回原线”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-MATERIAL-TOUCH-SOUND-V4",
    "name_zh": "触摸玻璃声波·声压凹面",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-MATERIAL-APPEARANCE-GLASS",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-DEFORMATION-SPACE-RIPPLE-DISPLACEMENT",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-GLASS-GLASSTOUCH",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-GLASS-GLASSBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOROTATE"
    ],
    "trigger_logic": "音量持续升高且用户按住一个触摸点",
    "combined_effect": "触摸点成为玻璃凹面，音量越高凹面越深，周围背景被折射成向内弯曲的声压环",
    "why_new": "持续触摸提供固定中心，音量连续改变几何位移而非只改变亮度",
    "preview_behavior": "为预览声压凹面，系统只更新与“音量持续升高且用户按住一个触摸点”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“触摸点成为玻璃凹面，音量越高凹面越深，周围背景被折射成向内弯曲的声压环”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "声压凹面的后处理从失败点开始：针对“长按过久会遮挡主体，限制凹面半径”复核掩码、锚点或时间戳，通过后才将“触摸点成为玻璃凹面，音量越高凹面越深，周围背景被折射成向内弯曲的声压环”提升到成片质量。触发逻辑“音量持续升高且用户按住一个触摸点”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "长按过久会遮挡主体，限制凹面半径"
    ],
    "target_scenarios": [
        "人物转身带动风格切换的全身镜头可用声压凹面组织一段连续互动。参与者先保持关系稳定，再完成“音量持续升高且用户按住一个触摸点”；镜头不切断，直到“触摸点成为玻璃凹面，音量越高凹面越深，周围背景被折射成向内弯曲的声压环”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-MATERIAL-TOUCH-SOUND-V5",
    "name_zh": "触摸玻璃声波·静音回平",
    "component_atom_ids": [
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-MATERIAL-APPEARANCE-GLASS",
        "ATOM-INTERACTION-TRIGGERS-SOUND-VOLUME",
        "ATOM-DEFORMATION-SPACE-RIPPLE-DISPLACEMENT",
        "ATOM-MATERIAL-APPEARANCE-METAL"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-GLASS-GLASSTOUCH",
        "FX-AUDIO-LYRICS-MASK-MASKVOLUME",
        "FX-MATERIAL-MORPH-GLASS-GLASSBEAT",
        "FX-WORLD-STYLE-NEON-NEONMOVE"
    ],
    "trigger_logic": "声音降到静音且用户沿原路径反向擦过",
    "combined_effect": "玻璃波纹按反向擦拭逐段回平，残余高光收回触摸起点并消失",
    "why_new": "声音停止和反向手势共同完成几何复原，让用户能主动结束声场",
    "preview_behavior": "静音回平的取景反馈以结束状态为目标：预览先保留真实动作，在“声音降到静音且用户沿原路径反向擦过”完成时快速呈现“玻璃波纹按反向擦拭逐段回平，残余高光收回触摸起点并消失”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留静音回平的完整生命周期。系统逆向检查“玻璃波纹按反向擦拭逐段回平，残余高光收回触摸起点并消失”是否回到稳定终态，再从“声音降到静音且用户沿原路径反向擦过”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "反向路径不完整会留下凹面，使用历史路径补齐"
    ],
    "target_scenarios": [
        "以材质恢复原状后的定格结尾作为静音回平的结尾段落：让“声音降到静音且用户沿原路径反向擦过”发生在最后一个动作峰值，保持机位直到“玻璃波纹按反向擦拭逐段回平，残余高光收回触摸起点并消失”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "STYLE-BEAT-BODY", "material_generation", "身体风格节拍织物",
        (
            "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
            "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
            "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
            "ATOM-GENERATIVE-TRANSFORMATION-CLOTHING",
        ),
        (
            "FX-WORLD-STYLE-COMIC-COMICBEAT",
            "FX-MATERIAL-MORPH-HOLO-HOLOBEAT",
            "FX-MATERIAL-MORPH-HOLO-HOLOMOVE",
        ),
        ("body_pose", "sound", "generative_style"),
        "人体轮廓限定可变区域，视觉风格提供图形语言，节拍控制风格切页，服装变换把风格落在身体动作和衣料褶皱上",
        "人物在每个强拍切换一层可穿着的视觉风格，衣料高光和漫画线条跟随动作，而不是整张画面切滤镜",
        "预览只在人体轮廓内显示简化风格纹理，强拍时更新一小块服装和轮廓高光",
        "录制后重建人体掩码、服装褶皱和节拍风格层，细化风格切换边缘与人物遮挡",
        "舞蹈、时装或音乐短片中让服装在节拍上换成不同视觉材质",
        (
        {
    "recipe_id": "RECIPE-STYLE-BEAT-BODY-V1",
    "name_zh": "身体风格节拍织物·漫画衣摆",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-GENERATIVE-TRANSFORMATION-CLOTHING",
        "ATOM-MATERIAL-APPEARANCE-GLASS"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOMOVE",
        "FX-MATERIAL-MORPH-GLASS-GLASSBREAK"
    ],
    "trigger_logic": "强拍到来且人物完成甩衣动作",
    "combined_effect": "衣摆先变成漫画速度线，再在动作峰值处恢复为带全息边缘的织物，身体轮廓保持连续",
    "why_new": "节拍决定风格切换，衣摆动作决定切换形状，风格不再覆盖静止的人物",
    "preview_behavior": "预览只在人体轮廓内显示简化风格纹理，强拍时更新一小块服装和轮廓高光。针对漫画衣摆，取景器先在“强拍到来且人物完成甩衣动作”发生前标出候选轨迹，确认后才显示“衣摆先变成漫画速度线，再在动作峰值处恢复为带全息边缘的织物，身体轮廓保持连续”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建人体掩码、服装褶皱和节拍风格层，细化风格切换边缘与人物遮挡。录后以“强拍到来且人物完成甩衣动作”的首帧为时间锚，重新计算漫画衣摆涉及的遮挡和深度，使“衣摆先变成漫画速度线，再在动作峰值处恢复为带全息边缘的织物，身体轮廓保持连续”在原分辨率下保持连续；检测到衣摆分割失败会让线条泄露到背景，限制在人体掩码内时仅修补低置信度片段。",
    "risks": [
        "衣摆分割失败会让线条泄露到背景，限制在人体掩码内"
    ],
    "target_scenarios": [
        "玻璃橱窗前的手势特写适合拍摄漫画衣摆：先让主体完成“强拍到来且人物完成甩衣动作”，随后缓慢移动手机观察“衣摆先变成漫画速度线，再在动作峰值处恢复为带全息边缘的织物，身体轮廓保持连续”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-STYLE-BEAT-BODY-V2",
    "name_zh": "身体风格节拍织物·全息换装",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-GENERATIVE-TRANSFORMATION-CLOTHING",
        "ATOM-MATERIAL-APPEARANCE-LIQUID"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOMOVE",
        "FX-MATERIAL-MORPH-METAL-METALFLOW"
    ],
    "trigger_logic": "人物转身时连续经过两个强拍",
    "combined_effect": "每拍切换一套全息服装色层，转身产生的褶皱运动让新旧材质沿身体侧面交接",
    "why_new": "节拍选择材质层，动作褶皱决定交接位置，换装拥有可见的身体因果",
    "preview_behavior": "移动端预览从全息换装的结果层反推触发：屏幕持续保留对象身份和最近历史，当“人物转身时连续经过两个强拍”成立时，把“每拍切换一套全息服装色层，转身产生的褶皱运动让新旧材质沿身体侧面交接”分成进入、保持、退场三段显示。若出现转身过快会让服装纹理错位，使用躯干姿态对齐，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把全息换装拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“人物转身时连续经过两个强拍”，再细化“每拍切换一套全息服装色层，转身产生的褶皱运动让新旧材质沿身体侧面交接”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "转身过快会让服装纹理错位，使用躯干姿态对齐"
    ],
    "target_scenarios": [
        "在服装材质变化的半身跟拍使用全息换装。镜头从未触发状态开始横向移动，人物或物体执行“人物转身时连续经过两个强拍”后继续穿过画面，以“每拍切换一套全息服装色层，转身产生的褶皱运动让新旧材质沿身体侧面交接”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-STYLE-BEAT-BODY-V3",
    "name_zh": "身体风格节拍织物·线稿呼吸",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-GENERATIVE-TRANSFORMATION-CLOTHING",
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOMOVE",
        "FX-MATERIAL-MORPH-PAPER-PAPERTEAR"
    ],
    "trigger_logic": "人物在强拍间保持静止并在拍点轻微起伏",
    "combined_effect": "强拍时轮廓变成粗线稿，拍间线稿变薄并让织物高光随呼吸起伏",
    "why_new": "节拍和微动作分别控制线稿强度与材质高光，静止仍有节奏状态",
    "preview_behavior": "拍摄者先看到线稿呼吸所需的对象边界、方向箭头和时间门；“人物在强拍间保持静止并在拍点轻微起伏”被连续确认后，预览按由近到远的层次展开“强拍时轮廓变成粗线稿，拍间线稿变薄并让织物高光随呼吸起伏”。人物在每个强拍切换一层可穿着的视觉风格，衣料高光和漫画线条跟随动作，而不是整张画面切滤镜，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验线稿呼吸的身份链与事件顺序，再按人体轮廓限定可变区域，视觉风格提供图形语言，节拍控制风格切页，服装变换把风格落在身体动作和衣料褶皱上重建组件关系。“强拍时轮廓变成粗线稿，拍间线稿变薄并让织物高光随呼吸起伏”使用完整历史窗口重新渲染，而“人物在强拍间保持静止并在拍点轻微起伏”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "呼吸检测弱时线稿闪变，保持上一周期"
    ],
    "target_scenarios": [
        "把线稿呼吸安排在前景物体碎裂与复原的桌面镜头：固定主体身份后执行“人物在强拍间保持静止并在拍点轻微起伏”，拍摄者绕触发点改变观察角度，用“强拍时轮廓变成粗线稿，拍间线稿变薄并让织物高光随呼吸起伏”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-STYLE-BEAT-BODY-V4",
    "name_zh": "身体风格节拍织物·双色领舞",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-GENERATIVE-TRANSFORMATION-CLOTHING",
        "ATOM-MATERIAL-APPEARANCE-HOLOGRAPHIC"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOMOVE",
        "FX-MATERIAL-MORPH-HOLO-HOLOROTATE"
    ],
    "trigger_logic": "两人轮流在强拍上完成同一姿态",
    "combined_effect": "先完成姿态者获得一种全息材质，后完成者获得互补颜色，下一拍两种材质沿关系边交换",
    "why_new": "动作先后决定颜色归属，节拍让材质交换具有编排感",
    "preview_behavior": "为预览双色领舞，系统只更新与“两人轮流在强拍上完成同一姿态”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“先完成姿态者获得一种全息材质，后完成者获得互补颜色，下一拍两种材质沿关系边交换”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "双色领舞的后处理从失败点开始：针对“两人同时完成会颜色混合，使用进入顺序稳定窗口”复核掩码、锚点或时间戳，通过后才将“先完成姿态者获得一种全息材质，后完成者获得互补颜色，下一拍两种材质沿关系边交换”提升到成片质量。触发逻辑“两人轮流在强拍上完成同一姿态”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "两人同时完成会颜色混合，使用进入顺序稳定窗口"
    ],
    "target_scenarios": [
        "人物转身带动风格切换的全身镜头可用双色领舞组织一段连续互动。参与者先保持关系稳定，再完成“两人轮流在强拍上完成同一姿态”；镜头不切断，直到“先完成姿态者获得一种全息材质，后完成者获得互补颜色，下一拍两种材质沿关系边交换”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-STYLE-BEAT-BODY-V5",
    "name_zh": "身体风格节拍织物·散拍碎衣",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE",
        "ATOM-INTERACTION-TRIGGERS-AUDIO-BEAT",
        "ATOM-GENERATIVE-TRANSFORMATION-CLOTHING",
        "ATOM-MATERIAL-APPEARANCE-METAL"
    ],
    "component_effect_ids": [
        "FX-WORLD-STYLE-COMIC-COMICBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOBEAT",
        "FX-MATERIAL-MORPH-HOLO-HOLOMOVE",
        "FX-WORLD-STYLE-NEON-NEONMOVE"
    ],
    "trigger_logic": "音乐进入段落结尾且人物做出快速转身",
    "combined_effect": "服装材质在连续强拍上分成发光碎片，碎片沿转身方向飞散，最后一拍重新织回轮廓",
    "why_new": "材质碎裂、动作方向和段落节拍构成完整结尾动作",
    "preview_behavior": "散拍碎衣的取景反馈以结束状态为目标：预览先保留真实动作，在“音乐进入段落结尾且人物做出快速转身”完成时快速呈现“服装材质在连续强拍上分成发光碎片，碎片沿转身方向飞散，最后一拍重新织回轮廓”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留散拍碎衣的完整生命周期。系统逆向检查“服装材质在连续强拍上分成发光碎片，碎片沿转身方向飞散，最后一拍重新织回轮廓”是否回到稳定终态，再从“音乐进入段落结尾且人物做出快速转身”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "碎片过多会遮挡脸部，限制碎片只从服装区域生成"
    ],
    "target_scenarios": [
        "以材质恢复原状后的定格结尾作为散拍碎衣的结尾段落：让“音乐进入段落结尾且人物做出快速转身”发生在最后一个动作峰值，保持机位直到“服装材质在连续强拍上分成发光碎片，碎片沿转身方向飞散，最后一拍重新织回轮廓”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "MORPH-TIME-REVERSE", "material_generation", "材质反转时间碎片",
        (
            "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION",
            "ATOM-TEMPORAL-STATE-TIME-REVERSE",
            "ATOM-MATERIAL-APPEARANCE-LIQUID",
            "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        ),
        (
            "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
            "FX-TIME-EDITING-REVERSE-REVERSEMASK",
            "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWREVERSE",
        ),
        ("material", "time", "shadow"),
        "前景掩码限定材质对象，时间反转提供动作方向，碎片化负责拆分边界，液体材质让碎片在反向过程中重新流合",
        "前景对象先碎成带时间顺序的材质片，局部反转时碎片沿原运动反向流回，影子同步演示相反动作",
        "预览只处理前景对象的边缘和少量碎片，反转窗口内显示简化液体流线",
        "录制后重建对象掩码、碎片运动和影子反向帧，细化液体合流、遮挡与材质边缘",
        "物体变换、手部遮挡或转身片段中制造可控的碎裂回收效果",
        (
        {
    "recipe_id": "RECIPE-MORPH-TIME-REVERSE-V1",
    "name_zh": "材质反转时间碎片·杯子回凝",
    "component_atom_ids": [
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-MATERIAL-APPEARANCE-GLASS"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWREVERSE",
        "FX-MATERIAL-MORPH-GLASS-GLASSBREAK"
    ],
    "trigger_logic": "前景杯子被手掌遮住后快速移开",
    "combined_effect": "杯子边缘碎成几片并按遮挡前的运动反向回凝，影子同时做一个相反方向的收手动作",
    "why_new": "遮挡事件确定碎裂时刻，液体回凝和影子反向共同解释物体如何恢复",
    "preview_behavior": "预览只处理前景对象的边缘和少量碎片，反转窗口内显示简化液体流线。针对杯子回凝，取景器先在“前景杯子被手掌遮住后快速移开”发生前标出候选轨迹，确认后才显示“杯子边缘碎成几片并按遮挡前的运动反向回凝，影子同时做一个相反方向的收手动作”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建对象掩码、碎片运动和影子反向帧，细化液体合流、遮挡与材质边缘。录后以“前景杯子被手掌遮住后快速移开”的首帧为时间锚，重新计算杯子回凝涉及的遮挡和深度，使“杯子边缘碎成几片并按遮挡前的运动反向回凝，影子同时做一个相反方向的收手动作”在原分辨率下保持连续；检测到手掌掩码不完整会留下碎片，使用前景边界补洞时仅修补低置信度片段。",
    "risks": [
        "手掌掩码不完整会留下碎片，使用前景边界补洞"
    ],
    "target_scenarios": [
        "玻璃橱窗前的手势特写适合拍摄杯子回凝：先让主体完成“前景杯子被手掌遮住后快速移开”，随后缓慢移动手机观察“杯子边缘碎成几片并按遮挡前的运动反向回凝，影子同时做一个相反方向的收手动作”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-MORPH-TIME-REVERSE-V2",
    "name_zh": "材质反转时间碎片·花瓣倒流",
    "component_atom_ids": [
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-MATERIAL-APPEARANCE-HOLOGRAPHIC"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWREVERSE",
        "FX-MATERIAL-MORPH-METAL-METALFLOW"
    ],
    "trigger_logic": "前景物体向上抛出并在最高点选定反转窗口",
    "combined_effect": "物体碎片在最高点沿液体流线向下回收，影子先倒放抛出动作再贴回脚边",
    "why_new": "反转只从动作峰值开始，材质和影子的不同回放速度形成双层时间错觉",
    "preview_behavior": "移动端预览从花瓣倒流的结果层反推触发：屏幕持续保留对象身份和最近历史，当“前景物体向上抛出并在最高点选定反转窗口”成立时，把“物体碎片在最高点沿液体流线向下回收，影子先倒放抛出动作再贴回脚边”分成进入、保持、退场三段显示。若出现峰值选错会让碎片逆流过早，使用速度零点确认，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把花瓣倒流拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“前景物体向上抛出并在最高点选定反转窗口”，再细化“物体碎片在最高点沿液体流线向下回收，影子先倒放抛出动作再贴回脚边”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "峰值选错会让碎片逆流过早，使用速度零点确认"
    ],
    "target_scenarios": [
        "在服装材质变化的半身跟拍使用花瓣倒流。镜头从未触发状态开始横向移动，人物或物体执行“前景物体向上抛出并在最高点选定反转窗口”后继续穿过画面，以“物体碎片在最高点沿液体流线向下回收，影子先倒放抛出动作再贴回脚边”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-MORPH-TIME-REVERSE-V3",
    "name_zh": "材质反转时间碎片·手中复原",
    "component_atom_ids": [
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWREVERSE",
        "FX-MATERIAL-MORPH-PAPER-PAPERTEAR"
    ],
    "trigger_logic": "手部离开前景对象后向原位置反向移动",
    "combined_effect": "对象碎片沿手部反向轨迹回到掌心，液体边缘在掌心处凝固，影子回放对应的抓取动作",
    "why_new": "手部轨迹成为材质回收路径，影子提供动作反相证据，结果可被手势完成",
    "preview_behavior": "拍摄者先看到手中复原所需的对象边界、方向箭头和时间门；“手部离开前景对象后向原位置反向移动”被连续确认后，预览按由近到远的层次展开“对象碎片沿手部反向轨迹回到掌心，液体边缘在掌心处凝固，影子回放对应的抓取动作”。前景对象先碎成带时间顺序的材质片，局部反转时碎片沿原运动反向流回，影子同步演示相反动作，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验手中复原的身份链与事件顺序，再按前景掩码限定材质对象，时间反转提供动作方向，碎片化负责拆分边界，液体材质让碎片在反向过程中重新流合重建组件关系。“对象碎片沿手部反向轨迹回到掌心，液体边缘在掌心处凝固，影子回放对应的抓取动作”使用完整历史窗口重新渲染，而“手部离开前景对象后向原位置反向移动”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "手部轨迹断裂会让碎片停在半路，冻结最近可信路径"
    ],
    "target_scenarios": [
        "把手中复原安排在前景物体碎裂与复原的桌面镜头：固定主体身份后执行“手部离开前景对象后向原位置反向移动”，拍摄者绕触发点改变观察角度，用“对象碎片沿手部反向轨迹回到掌心，液体边缘在掌心处凝固，影子回放对应的抓取动作”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-MORPH-TIME-REVERSE-V4",
    "name_zh": "材质反转时间碎片·边缘倒擦",
    "component_atom_ids": [
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-MATERIAL-APPEARANCE-METAL"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWREVERSE",
        "FX-MATERIAL-MORPH-HOLO-HOLOROTATE"
    ],
    "trigger_logic": "用户沿前景对象边缘拖动时间反转区域",
    "combined_effect": "被拖过的边缘按反向顺序碎裂，未拖区域保持原材质，拖回起点时碎片重新流合",
    "why_new": "用户能以局部路径选择时间方向，材质边界直接显示编辑范围",
    "preview_behavior": "为预览边缘倒擦，系统只更新与“用户沿前景对象边缘拖动时间反转区域”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“被拖过的边缘按反向顺序碎裂，未拖区域保持原材质，拖回起点时碎片重新流合”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "边缘倒擦的后处理从失败点开始：针对“拖动过快会跳过碎片层，降低反转采样密度”复核掩码、锚点或时间戳，通过后才将“被拖过的边缘按反向顺序碎裂，未拖区域保持原材质，拖回起点时碎片重新流合”提升到成片质量。触发逻辑“用户沿前景对象边缘拖动时间反转区域”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "拖动过快会跳过碎片层，降低反转采样密度"
    ],
    "target_scenarios": [
        "人物转身带动风格切换的全身镜头可用边缘倒擦组织一段连续互动。参与者先保持关系稳定，再完成“用户沿前景对象边缘拖动时间反转区域”；镜头不切断，直到“被拖过的边缘按反向顺序碎裂，未拖区域保持原材质，拖回起点时碎片重新流合”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-MORPH-TIME-REVERSE-V5",
    "name_zh": "材质反转时间碎片·影材合流",
    "component_atom_ids": [
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION",
        "ATOM-TEMPORAL-STATE-TIME-REVERSE",
        "ATOM-MATERIAL-APPEARANCE-LIQUID",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-MATERIAL-APPEARANCE-FIRE"
    ],
    "component_effect_ids": [
        "FX-MATERIAL-MORPH-DISSOLVE-DISSOLVEREVERSE",
        "FX-TIME-EDITING-REVERSE-REVERSEMASK",
        "FX-VIRTUAL-LIGHT-SHADOW-DOUBLE-SHADOWREVERSE",
        "FX-WORLD-STYLE-NEON-NEONMOVE"
    ],
    "trigger_logic": "材质对象和其影子同时进入反向时间窗口",
    "combined_effect": "对象碎片向主体回流，影子碎片从墙地表面反向爬回脚下，两股流在接触点合成一层液态边缘",
    "why_new": "对象与影子的反向合流让材质变化具有空间对应，不是两个独立倒放效果",
    "preview_behavior": "影材合流的取景反馈以结束状态为目标：预览先保留真实动作，在“材质对象和其影子同时进入反向时间窗口”完成时快速呈现“对象碎片向主体回流，影子碎片从墙地表面反向爬回脚下，两股流在接触点合成一层液态边缘”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留影材合流的完整生命周期。系统逆向检查“对象碎片向主体回流，影子碎片从墙地表面反向爬回脚下，两股流在接触点合成一层液态边缘”是否回到稳定终态，再从“材质对象和其影子同时进入反向时间窗口”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "接触点估计错误会让两股流错开，使用脚底锚点对齐"
    ],
    "target_scenarios": [
        "以材质恢复原状后的定格结尾作为影材合流的结尾段落：让“材质对象和其影子同时进入反向时间窗口”发生在最后一个动作峰值，保持机位直到“对象碎片向主体回流，影子碎片从墙地表面反向爬回脚下，两股流在接触点合成一层液态边缘”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "BACKGROUND-PORTAL", "material_generation", "背景生成穿页",
        (
            "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
            "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-GENERATIVE-TRANSFORMATION-SCENE-LIGHTING",
        ),
        (
            "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
            "FX-WORLD-STYLE-UNDERWATER-WATERROTATE",
            "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        ),
        ("generative_world", "spatial_portal", "world_anchor"),
        "背景世界变换生成新环境，画面穿越提供人物通过的边界，世界锚点固定页角，场景光照保证前后页受光一致",
        "人物经过一个真实边界时，背景像翻页一样换成另一空间，页角固定在世界中，人物和动作连续穿过",
        "预览只生成边界另一侧的低分辨率背景，并用人物轮廓和页角保证穿越方向可读",
        "录制后重建背景生成、页角锚点和场景光照，细化人物穿页遮挡、接缝与光照连续性",
        "门框、墙角、人体擦镜或街景转身视频中做一段可执行的世界穿页",
        (
        {
    "recipe_id": "RECIPE-BACKGROUND-PORTAL-V1",
    "name_zh": "背景生成穿页·门框翻页",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GENERATIVE-TRANSFORMATION-SCENE-LIGHTING",
        "ATOM-MATERIAL-APPEARANCE-GLASS"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-UNDERWATER-WATERROTATE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-MATERIAL-MORPH-GLASS-GLASSBREAK"
    ],
    "trigger_logic": "人物沿门框移动并让肩部遮住一侧边界",
    "combined_effect": "肩部经过门框时背景翻到目标空间，门框页角仍固定在墙面，人物从旧光照自然走入新光照",
    "why_new": "人物遮挡定义翻页时刻，世界锚点定义页角，光照变换让新旧空间可连贯穿过",
    "preview_behavior": "预览只生成边界另一侧的低分辨率背景，并用人物轮廓和页角保证穿越方向可读。针对门框翻页，取景器先在“人物沿门框移动并让肩部遮住一侧边界”发生前标出候选轨迹，确认后才显示“肩部经过门框时背景翻到目标空间，门框页角仍固定在墙面，人物从旧光照自然走入新光照”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建背景生成、页角锚点和场景光照，细化人物穿页遮挡、接缝与光照连续性。录后以“人物沿门框移动并让肩部遮住一侧边界”的首帧为时间锚，重新计算门框翻页涉及的遮挡和深度，使“肩部经过门框时背景翻到目标空间，门框页角仍固定在墙面，人物从旧光照自然走入新光照”在原分辨率下保持连续；检测到门框检测不稳会造成整面墙翻页，使用直线和遮挡联合确认时仅修补低置信度片段。",
    "risks": [
        "门框检测不稳会造成整面墙翻页，使用直线和遮挡联合确认"
    ],
    "target_scenarios": [
        "玻璃橱窗前的手势特写适合拍摄门框翻页：先让主体完成“人物沿门框移动并让肩部遮住一侧边界”，随后缓慢移动手机观察“肩部经过门框时背景翻到目标空间，门框页角仍固定在墙面，人物从旧光照自然走入新光照”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-BACKGROUND-PORTAL-V2",
    "name_zh": "背景生成穿页·墙角穿越",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GENERATIVE-TRANSFORMATION-SCENE-LIGHTING",
        "ATOM-MATERIAL-APPEARANCE-LIQUID"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-UNDERWATER-WATERROTATE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-MATERIAL-MORPH-METAL-METALFLOW"
    ],
    "trigger_logic": "人物从墙角一侧转身到另一侧且前景轮廓稳定",
    "combined_effect": "墙角成为折页轴，转身过程中一侧背景先换成水下世界，完成转身后两侧合成新空间",
    "why_new": "身体转身阶段控制局部翻页比例，墙角锚点使生成背景遵循真实折页结构",
    "preview_behavior": "移动端预览从墙角穿越的结果层反推触发：屏幕持续保留对象身份和最近历史，当“人物从墙角一侧转身到另一侧且前景轮廓稳定”成立时，把“墙角成为折页轴，转身过程中一侧背景先换成水下世界，完成转身后两侧合成新空间”分成进入、保持、退场三段显示。若出现墙角深度估计错误会使页轴漂浮，吸附到稳定垂直边，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把墙角穿越拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“人物从墙角一侧转身到另一侧且前景轮廓稳定”，再细化“墙角成为折页轴，转身过程中一侧背景先换成水下世界，完成转身后两侧合成新空间”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "墙角深度估计错误会使页轴漂浮，吸附到稳定垂直边"
    ],
    "target_scenarios": [
        "在服装材质变化的半身跟拍使用墙角穿越。镜头从未触发状态开始横向移动，人物或物体执行“人物从墙角一侧转身到另一侧且前景轮廓稳定”后继续穿过画面，以“墙角成为折页轴，转身过程中一侧背景先换成水下世界，完成转身后两侧合成新空间”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-BACKGROUND-PORTAL-V3",
    "name_zh": "背景生成穿页·地面翻场",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GENERATIVE-TRANSFORMATION-SCENE-LIGHTING",
        "ATOM-MATERIAL-APPEARANCE-FRAGMENTATION"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-UNDERWATER-WATERROTATE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-MATERIAL-MORPH-PAPER-PAPERTEAR"
    ],
    "trigger_logic": "人物迈步经过地面纹理变化明显的位置",
    "combined_effect": "脚步落点触发地面像纸页向前翻起，页下逐步显露目标场景，人物脚底遮住翻页边缘",
    "why_new": "脚步是穿页触发器，地面锚点和生成背景共同决定空间从下方出现",
    "preview_behavior": "拍摄者先看到地面翻场所需的对象边界、方向箭头和时间门；“人物迈步经过地面纹理变化明显的位置”被连续确认后，预览按由近到远的层次展开“脚步落点触发地面像纸页向前翻起，页下逐步显露目标场景，人物脚底遮住翻页边缘”。人物经过一个真实边界时，背景像翻页一样换成另一空间，页角固定在世界中，人物和动作连续穿过，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验地面翻场的身份链与事件顺序，再按背景世界变换生成新环境，画面穿越提供人物通过的边界，世界锚点固定页角，场景光照保证前后页受光一致重建组件关系。“脚步落点触发地面像纸页向前翻起，页下逐步显露目标场景，人物脚底遮住翻页边缘”使用完整历史窗口重新渲染，而“人物迈步经过地面纹理变化明显的位置”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "地面纹理重复会误触发，要求步态事件与平面稳定"
    ],
    "target_scenarios": [
        "把地面翻场安排在前景物体碎裂与复原的桌面镜头：固定主体身份后执行“人物迈步经过地面纹理变化明显的位置”，拍摄者绕触发点改变观察角度，用“脚步落点触发地面像纸页向前翻起，页下逐步显露目标场景，人物脚底遮住翻页边缘”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-BACKGROUND-PORTAL-V4",
    "name_zh": "背景生成穿页·人体擦页",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GENERATIVE-TRANSFORMATION-SCENE-LIGHTING",
        "ATOM-MATERIAL-APPEARANCE-HOLOGRAPHIC"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-UNDERWATER-WATERROTATE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-MATERIAL-MORPH-HOLO-HOLOROTATE"
    ],
    "trigger_logic": "人物快速横穿镜头并完整遮住画面中部",
    "combined_effect": "人体轮廓作为移动页片，身后背景在其经过后变为新世界，边缘留下短暂纸张高光",
    "why_new": "前景人体和背景生成不是独立擦镜，人体运动速度决定世界切换的推进速度",
    "preview_behavior": "为预览人体擦页，系统只更新与“人物快速横穿镜头并完整遮住画面中部”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“人体轮廓作为移动页片，身后背景在其经过后变为新世界，边缘留下短暂纸张高光”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "人体擦页的后处理从失败点开始：针对“人体轮廓孔洞会露出旧背景，使用前景掩码内缩”复核掩码、锚点或时间戳，通过后才将“人体轮廓作为移动页片，身后背景在其经过后变为新世界，边缘留下短暂纸张高光”提升到成片质量。触发逻辑“人物快速横穿镜头并完整遮住画面中部”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "人体轮廓孔洞会露出旧背景，使用前景掩码内缩"
    ],
    "target_scenarios": [
        "人物转身带动风格切换的全身镜头可用人体擦页组织一段连续互动。参与者先保持关系稳定，再完成“人物快速横穿镜头并完整遮住画面中部”；镜头不切断，直到“人体轮廓作为移动页片，身后背景在其经过后变为新世界，边缘留下短暂纸张高光”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-BACKGROUND-PORTAL-V5",
    "name_zh": "背景生成穿页·回走复页",
    "component_atom_ids": [
        "ATOM-GENERATIVE-TRANSFORMATION-BACKGROUND-WORLD",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GENERATIVE-TRANSFORMATION-SCENE-LIGHTING",
        "ATOM-GENERATIVE-TRANSFORMATION-VISUAL-STYLE"
    ],
    "component_effect_ids": [
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-UNDERWATER-WATERROTATE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-WORLD-STYLE-NEON-NEONMOVE"
    ],
    "trigger_logic": "人物反向走回原边界且页角仍可追踪",
    "combined_effect": "新世界按人物反向路径折回旧世界，页角先合拢，最后人物影子回到原受光方向",
    "why_new": "回走动作改变生成世界的时间方向，场景光照回配使返回具有空间因果",
    "preview_behavior": "回走复页的取景反馈以结束状态为目标：预览先保留真实动作，在“人物反向走回原边界且页角仍可追踪”完成时快速呈现“新世界按人物反向路径折回旧世界，页角先合拢，最后人物影子回到原受光方向”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留回走复页的完整生命周期。系统逆向检查“新世界按人物反向路径折回旧世界，页角先合拢，最后人物影子回到原受光方向”是否回到稳定终态，再从“人物反向走回原边界且页角仍可追踪”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "回走路径不完整会留下生成接缝，沿锚点历史补齐"
    ],
    "target_scenarios": [
        "以材质恢复原状后的定格结尾作为回走复页的结尾段落：让“人物反向走回原边界且页角仍可追踪”发生在最后一个动作峰值，保持机位直到“新世界按人物反向路径折回旧世界，页角先合拢，最后人物影子回到原受光方向”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),

    _b(
        "SPLIT-HAND-WORLD", "effect_cinematography", "手指拉出的世界分屏",
        (
            "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
            "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        ),
        (
            "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDRAW",
            "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
            "FX-SPATIAL-PORTALS-PALM-PALMMOVE",
        ),
        ("touch_gesture", "world_anchor", "spatial_portal"),
        "手部二维路径绘制分屏边界，世界锚点把边界拉成立体切面，相机运动提供两侧不同的视差和内容锁定",
        "指尖划出的不是平面分割线，而是一道固定在场景中的立体切面，切面两侧显示不同时间或空间内容",
        "预览先显示触摸线和粗分屏面，镜头运动时只更新锚点法线和低分辨率两侧画面",
        "录制后重建手势边界、相机轨迹和世界切面，细化切面厚度、两侧遮挡及拉动动画",
        "旅行转场、商品展示或双场景对比中用手指拉开一条世界分屏",
        (
        {
    "recipe_id": "RECIPE-SPLIT-HAND-WORLD-V1",
    "name_zh": "手指拉出的世界分屏·水平拉页",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDRAW",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-SPATIAL-PORTALS-PALM-PALMMOVE",
        "FX-EFFECT-CINEMATOGRAPHY-ZOOM-ZOOMGAZE"
    ],
    "trigger_logic": "用户从左向右画线并在终点停留",
    "combined_effect": "画线变成固定在墙面上的立体分屏，左侧保留原场景，右侧展开另一空间并产生视差",
    "why_new": "触摸路径定义边界、世界锚点定义固定性，分屏因此能承受镜头移动",
    "preview_behavior": "预览先显示触摸线和粗分屏面，镜头运动时只更新锚点法线和低分辨率两侧画面。针对水平拉页，取景器先在“用户从左向右画线并在终点停留”发生前标出候选轨迹，确认后才显示“画线变成固定在墙面上的立体分屏，左侧保留原场景，右侧展开另一空间并产生视差”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建手势边界、相机轨迹和世界切面，细化切面厚度、两侧遮挡及拉动动画。录后以“用户从左向右画线并在终点停留”的首帧为时间锚，重新计算水平拉页涉及的遮挡和深度，使“画线变成固定在墙面上的立体分屏，左侧保留原场景，右侧展开另一空间并产生视差”在原分辨率下保持连续；检测到线段抖动会使切面锯齿，使用路径平滑保留端点时仅修补低置信度片段。",
    "risks": [
        "线段抖动会使切面锯齿，使用路径平滑保留端点"
    ],
    "target_scenarios": [
        "旅行街景中的手绘分屏镜头适合拍摄水平拉页：先让主体完成“用户从左向右画线并在终点停留”，随后缓慢移动手机观察“画线变成固定在墙面上的立体分屏，左侧保留原场景，右侧展开另一空间并产生视差”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-SPLIT-HAND-WORLD-V2",
    "name_zh": "手指拉出的世界分屏·竖向切雨",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDRAW",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-SPATIAL-PORTALS-PALM-PALMMOVE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH"
    ],
    "trigger_logic": "用户从地面向上拖动手指且相机轻微上仰",
    "combined_effect": "竖向切面沿真实地面延伸到天空，两侧雨幕方向不同，镜头上仰时切面仍锁在世界",
    "why_new": "手势方向与相机运动共同决定切面姿态，效果不是固定竖屏分栏",
    "preview_behavior": "移动端预览从竖向切雨的结果层反推触发：屏幕持续保留对象身份和最近历史，当“用户从地面向上拖动手指且相机轻微上仰”成立时，把“竖向切面沿真实地面延伸到天空，两侧雨幕方向不同，镜头上仰时切面仍锁在世界”分成进入、保持、退场三段显示。若出现相机运动过大导致锚点漂移，冻结最近可信切面，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把竖向切雨拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“用户从地面向上拖动手指且相机轻微上仰”，再细化“竖向切面沿真实地面延伸到天空，两侧雨幕方向不同，镜头上仰时切面仍锁在世界”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "相机运动过大导致锚点漂移，冻结最近可信切面"
    ],
    "target_scenarios": [
        "在人物视线拉焦的产品展示使用竖向切雨。镜头从未触发状态开始横向移动，人物或物体执行“用户从地面向上拖动手指且相机轻微上仰”后继续穿过画面，以“竖向切面沿真实地面延伸到天空，两侧雨幕方向不同，镜头上仰时切面仍锁在世界”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-SPLIT-HAND-WORLD-V3",
    "name_zh": "手指拉出的世界分屏·环形分屏",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDRAW",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-SPATIAL-PORTALS-PALM-PALMMOVE",
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSUREBEAT"
    ],
    "trigger_logic": "用户画出闭合椭圆并将掌窗向前推",
    "combined_effect": "椭圆成为有厚度的环形分屏，环内显示近景历史，环外保持实时空间",
    "why_new": "闭合手势产生内容包围关系，前推动作把屏幕分区变成可移动的世界环",
    "preview_behavior": "拍摄者先看到环形分屏所需的对象边界、方向箭头和时间门；“用户画出闭合椭圆并将掌窗向前推”被连续确认后，预览按由近到远的层次展开“椭圆成为有厚度的环形分屏，环内显示近景历史，环外保持实时空间”。指尖划出的不是平面分割线，而是一道固定在场景中的立体切面，切面两侧显示不同时间或空间内容，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验环形分屏的身份链与事件顺序，再按手部二维路径绘制分屏边界，世界锚点把边界拉成立体切面，相机运动提供两侧不同的视差和内容锁定重建组件关系。“椭圆成为有厚度的环形分屏，环内显示近景历史，环外保持实时空间”使用完整历史窗口重新渲染，而“用户画出闭合椭圆并将掌窗向前推”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "闭合不稳定会生成断环，连接首尾并降低厚度"
    ],
    "target_scenarios": [
        "把环形分屏安排在夜景旋转曝光的环绕机位：固定主体身份后执行“用户画出闭合椭圆并将掌窗向前推”，拍摄者绕触发点改变观察角度，用“椭圆成为有厚度的环形分屏，环内显示近景历史，环外保持实时空间”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-SPLIT-HAND-WORLD-V4",
    "name_zh": "手指拉出的世界分屏·斜切追拍",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDRAW",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-SPATIAL-PORTALS-PALM-PALMMOVE",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITCHASE"
    ],
    "trigger_logic": "用户沿移动对象运动方向斜划，镜头同时横移",
    "combined_effect": "斜切面追随对象一段距离，前侧显示对象当前帧，后侧显示它刚经过的路径",
    "why_new": "相机运动和对象世界锚点共同决定追拍分屏的速度，时间比较嵌入空间切面",
    "preview_behavior": "为预览斜切追拍，系统只更新与“用户沿移动对象运动方向斜划，镜头同时横移”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“斜切面追随对象一段距离，前侧显示对象当前帧，后侧显示它刚经过的路径”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "斜切追拍的后处理从失败点开始：针对“对象遮挡会使分屏断开，使用对象姿态预测短时延伸”复核掩码、锚点或时间戳，通过后才将“斜切面追随对象一段距离，前侧显示对象当前帧，后侧显示它刚经过的路径”提升到成片质量。触发逻辑“用户沿移动对象运动方向斜划，镜头同时横移”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "对象遮挡会使分屏断开，使用对象姿态预测短时延伸"
    ],
    "target_scenarios": [
        "舞蹈人物经过镜头的擦镜转场可用斜切追拍组织一段连续互动。参与者先保持关系稳定，再完成“用户沿移动对象运动方向斜划，镜头同时横移”；镜头不切断，直到“斜切面追随对象一段距离，前侧显示对象当前帧，后侧显示它刚经过的路径”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-SPLIT-HAND-WORLD-V5",
    "name_zh": "手指拉出的世界分屏·合屏收回",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-HAND-2D-TRAJECTORY",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW",
        "ATOM-SEGMENTATION-MASKS-OBJECT-INSTANCE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITDRAW",
        "FX-LIGHT-TRAILS-OPTICS-WORLD-ANCHOR",
        "FX-SPATIAL-PORTALS-PALM-PALMMOVE",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "用户反向沿分屏边界擦回起点",
    "combined_effect": "两侧内容沿擦拭方向逐段合拢，最后世界切面缩成一条发光锚线并消失",
    "why_new": "关闭路径由手指控制，分屏有可逆的空间生命周期而不是剪辑式硬切",
    "preview_behavior": "合屏收回的取景反馈以结束状态为目标：预览先保留真实动作，在“用户反向沿分屏边界擦回起点”完成时快速呈现“两侧内容沿擦拭方向逐段合拢，最后世界切面缩成一条发光锚线并消失”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留合屏收回的完整生命周期。系统逆向检查“两侧内容沿擦拭方向逐段合拢，最后世界切面缩成一条发光锚线并消失”是否回到稳定终态，再从“用户反向沿分屏边界擦回起点”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "擦拭中断会残留半屏，超时沿原路径收回"
    ],
    "target_scenarios": [
        "以切面或光轨合拢后的结束镜头作为合屏收回的结尾段落：让“用户反向沿分屏边界擦回起点”发生在最后一个动作峰值，保持机位直到“两侧内容沿擦拭方向逐段合拢，最后世界切面缩成一条发光锚线并消失”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "FOCUS-GAZE-CATCHLIGHT", "effect_cinematography", "凝视焦点眼神光穿刺",
        (
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
            "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
            "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        ),
        (
            "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
            "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-FOLLOW",
            "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        ),
        ("gaze", "expression", "light"),
        "视线向量选择焦点目标，虹膜关键点稳定眼神光，物体姿态保持焦点对象边缘，光核在焦点切换时完成转移",
        "目光所到之处成为焦点，焦点穿刺光环从瞳孔高光发出并在目标边缘收束，切换时留下短暂光核",
        "预览使用粗焦点目标和单层眼神光，视线停留确认后才渲染穿刺光环",
        "录制后细化焦点拉移、瞳孔高光、物体姿态和光核转移，修复快速视线切换的边缘",
        "访谈、产品展示或街景中用眼神完成可见的焦点拉移",
        (
        {
    "recipe_id": "RECIPE-FOCUS-GAZE-CATCHLIGHT-V1",
    "name_zh": "凝视焦点眼神光穿刺·镜头到物",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-FOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-EFFECT-CINEMATOGRAPHY-ZOOM-ZOOMGAZE"
    ],
    "trigger_logic": "用户先看镜头再把视线移到手中物体",
    "combined_effect": "眼神光从双眼向镜头收束，再沿视线穿刺到物体边缘，物体成为新的高光中心",
    "why_new": "镜头节点和物体节点有明确转移路径，焦点效果由视线行为而非点击驱动",
    "preview_behavior": "预览使用粗焦点目标和单层眼神光，视线停留确认后才渲染穿刺光环。针对镜头到物，取景器先在“用户先看镜头再把视线移到手中物体”发生前标出候选轨迹，确认后才显示“眼神光从双眼向镜头收束，再沿视线穿刺到物体边缘，物体成为新的高光中心”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后细化焦点拉移、瞳孔高光、物体姿态和光核转移，修复快速视线切换的边缘。录后以“用户先看镜头再把视线移到手中物体”的首帧为时间锚，重新计算镜头到物涉及的遮挡和深度，使“眼神光从双眼向镜头收束，再沿视线穿刺到物体边缘，物体成为新的高光中心”在原分辨率下保持连续；检测到手中物体姿态不稳会使光环漂移，保持最近可信姿态时仅修补低置信度片段。",
    "risks": [
        "手中物体姿态不稳会使光环漂移，保持最近可信姿态"
    ],
    "target_scenarios": [
        "旅行街景中的手绘分屏镜头适合拍摄镜头到物：先让主体完成“用户先看镜头再把视线移到手中物体”，随后缓慢移动手机观察“眼神光从双眼向镜头收束，再沿视线穿刺到物体边缘，物体成为新的高光中心”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-FOCUS-GAZE-CATCHLIGHT-V2",
    "name_zh": "凝视焦点眼神光穿刺·物到人",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-FOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH"
    ],
    "trigger_logic": "视线从物体快速回到人物脸部并停留",
    "combined_effect": "物体边缘光核先断开，沿视线方向回到虹膜高光，脸部轮廓出现一次短焦点脉冲",
    "why_new": "光核可以回到发射者，眼神光不只是终点而是焦点闭环的状态",
    "preview_behavior": "移动端预览从物到人的结果层反推触发：屏幕持续保留对象身份和最近历史，当“视线从物体快速回到人物脸部并停留”成立时，把“物体边缘光核先断开，沿视线方向回到虹膜高光，脸部轮廓出现一次短焦点脉冲”分成进入、保持、退场三段显示。若出现回看太快会漏掉回流，延长光核尾迹半拍，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把物到人拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“视线从物体快速回到人物脸部并停留”，再细化“物体边缘光核先断开，沿视线方向回到虹膜高光，脸部轮廓出现一次短焦点脉冲”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "回看太快会漏掉回流，延长光核尾迹半拍"
    ],
    "target_scenarios": [
        "在人物视线拉焦的产品展示使用物到人。镜头从未触发状态开始横向移动，人物或物体执行“视线从物体快速回到人物脸部并停留”后继续穿过画面，以“物体边缘光核先断开，沿视线方向回到虹膜高光，脸部轮廓出现一次短焦点脉冲”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-FOCUS-GAZE-CATCHLIGHT-V3",
    "name_zh": "凝视焦点眼神光穿刺·双目标穿刺",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-FOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSUREBEAT"
    ],
    "trigger_logic": "视线依次锁定近处和远处两个物体",
    "combined_effect": "近物环先收紧，随后一条带深度渐变的光线穿过近物到远物，两个边缘分别保留高光等级",
    "why_new": "物体姿态和深度关系让焦点切换具有穿透顺序，不是同时高亮两个对象",
    "preview_behavior": "拍摄者先看到双目标穿刺所需的对象边界、方向箭头和时间门；“视线依次锁定近处和远处两个物体”被连续确认后，预览按由近到远的层次展开“近物环先收紧，随后一条带深度渐变的光线穿过近物到远物，两个边缘分别保留高光等级”。目光所到之处成为焦点，焦点穿刺光环从瞳孔高光发出并在目标边缘收束，切换时留下短暂光核，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验双目标穿刺的身份链与事件顺序，再按视线向量选择焦点目标，虹膜关键点稳定眼神光，物体姿态保持焦点对象边缘，光核在焦点切换时完成转移重建组件关系。“近物环先收紧，随后一条带深度渐变的光线穿过近物到远物，两个边缘分别保留高光等级”使用完整历史窗口重新渲染，而“视线依次锁定近处和远处两个物体”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "深度排序错误会让光线穿过前景，按最近遮挡物截断"
    ],
    "target_scenarios": [
        "把双目标穿刺安排在夜景旋转曝光的环绕机位：固定主体身份后执行“视线依次锁定近处和远处两个物体”，拍摄者绕触发点改变观察角度，用“近物环先收紧，随后一条带深度渐变的光线穿过近物到远物，两个边缘分别保留高光等级”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-FOCUS-GAZE-CATCHLIGHT-V4",
    "name_zh": "凝视焦点眼神光穿刺·眨眼确认",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-FOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITCHASE"
    ],
    "trigger_logic": "视线停留在目标且眨眼一次",
    "combined_effect": "眨眼将目标光环从呼吸状态锁定为实线，下一次视线移开时实线沿目标轮廓消散",
    "why_new": "眨眼把注视变成确认动作，光环因此具有选择和取消的交互语义",
    "preview_behavior": "为预览眨眼确认，系统只更新与“视线停留在目标且眨眼一次”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“眨眼将目标光环从呼吸状态锁定为实线，下一次视线移开时实线沿目标轮廓消散”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "眨眼确认的后处理从失败点开始：针对“眨眼误检会锁定错误目标，使用停留门限二次确认”复核掩码、锚点或时间戳，通过后才将“眨眼将目标光环从呼吸状态锁定为实线，下一次视线移开时实线沿目标轮廓消散”提升到成片质量。触发逻辑“视线停留在目标且眨眼一次”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "眨眼误检会锁定错误目标，使用停留门限二次确认"
    ],
    "target_scenarios": [
        "舞蹈人物经过镜头的擦镜转场可用眨眼确认组织一段连续互动。参与者先保持关系稳定，再完成“视线停留在目标且眨眼一次”；镜头不切断，直到“眨眼将目标光环从呼吸状态锁定为实线，下一次视线移开时实线沿目标轮廓消散”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-FOCUS-GAZE-CATCHLIGHT-V5",
    "name_zh": "凝视焦点眼神光穿刺·对话穿焦",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
        "ATOM-GEOMETRY-TRACKING-IRIS-PUPIL-LANDMARKS",
        "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE",
        "ATOM-SEGMENTATION-MASKS-OBJECT-INSTANCE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSGAZE",
        "FX-FACE-GAZE-EXPRESSION-CATCHLIGHT-FOLLOW",
        "FX-FACE-GAZE-EXPRESSION-GLOW-GLOWTRANSFER",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "说话者视线从听者切到镜头旁并出现说话峰值",
    "combined_effect": "焦点环在听者边缘和镜头旁之间穿过，眼神光随声音峰值短暂变亮并回到听者",
    "why_new": "说话事件改变焦点转移强度，视线与声音共同决定对话镜头的视觉节奏",
    "preview_behavior": "对话穿焦的取景反馈以结束状态为目标：预览先保留真实动作，在“说话者视线从听者切到镜头旁并出现说话峰值”完成时快速呈现“焦点环在听者边缘和镜头旁之间穿过，眼神光随声音峰值短暂变亮并回到听者”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留对话穿焦的完整生命周期。系统逆向检查“焦点环在听者边缘和镜头旁之间穿过，眼神光随声音峰值短暂变亮并回到听者”是否回到稳定终态，再从“说话者视线从听者切到镜头旁并出现说话峰值”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "声音峰值可能来自背景，使用脸部附近声源置信度"
    ],
    "target_scenarios": [
        "以切面或光轨合拢后的结束镜头作为对话穿焦的结尾段落：让“说话者视线从听者切到镜头旁并出现说话峰值”发生在最后一个动作峰值，保持机位直到“焦点环在听者边缘和镜头旁之间穿过，眼神光随声音峰值短暂变亮并回到听者”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "EXPOSURE-MOTION-COLOR", "effect_cinematography", "旋转曝光色散轨迹",
        (
            "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
            "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
            "ATOM-LIGHT-OPTICS-CHROMATIC-ABERRATION",
            "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        ),
        (
            "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSURECOLOR",
            "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
            "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL",
        ),
        ("realtime_light_trail", "sound", "time"),
        "相机运动轨迹提供旋转曝光方向，光绘笔刷累积亮点路径，色散边缘按轨迹速度分色，节拍时钟切出停格节点",
        "镜头旋转留下带颜色分层的曝光轨迹，强拍把轨迹切成短暂停格片段，回到实时后色带继续流动",
        "预览使用短曝光历史和低分辨率色散，强拍时只冻结局部轨迹节点以保持帧率",
        "录制后重建相机运动、曝光历史、色散宽度与节拍停格，细化高光轨迹和场景边缘",
        "夜景旋转、灯光表演或城市移动镜头中制作具有节奏节点的彩色长曝光",
        (
        {
    "recipe_id": "RECIPE-EXPOSURE-MOTION-COLOR-V1",
    "name_zh": "旋转曝光色散轨迹·旋转彩带",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-LIGHT-OPTICS-CHROMATIC-ABERRATION",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSURECOLOR",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-ZOOM-ZOOMGAZE"
    ],
    "trigger_logic": "相机绕固定主体旋转并连续捕获点光源",
    "combined_effect": "点光源沿旋转方向拉出红绿蓝三层彩带，主体保持清晰，强拍处彩带出现一格停顿",
    "why_new": "相机运动决定带形，色散决定分层，节拍决定停顿，三种状态共同形成轨迹语言",
    "preview_behavior": "预览使用短曝光历史和低分辨率色散，强拍时只冻结局部轨迹节点以保持帧率。针对旋转彩带，取景器先在“相机绕固定主体旋转并连续捕获点光源”发生前标出候选轨迹，确认后才显示“点光源沿旋转方向拉出红绿蓝三层彩带，主体保持清晰，强拍处彩带出现一格停顿”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建相机运动、曝光历史、色散宽度与节拍停格，细化高光轨迹和场景边缘。录后以“相机绕固定主体旋转并连续捕获点光源”的首帧为时间锚，重新计算旋转彩带涉及的遮挡和深度，使“点光源沿旋转方向拉出红绿蓝三层彩带，主体保持清晰，强拍处彩带出现一格停顿”在原分辨率下保持连续；检测到快速旋转会使色带过宽，限制曝光历史长度时仅修补低置信度片段。",
    "risks": [
        "快速旋转会使色带过宽，限制曝光历史长度"
    ],
    "target_scenarios": [
        "旅行街景中的手绘分屏镜头适合拍摄旋转彩带：先让主体完成“相机绕固定主体旋转并连续捕获点光源”，随后缓慢移动手机观察“点光源沿旋转方向拉出红绿蓝三层彩带，主体保持清晰，强拍处彩带出现一格停顿”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-EXPOSURE-MOTION-COLOR-V2",
    "name_zh": "旋转曝光色散轨迹·强拍切片",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-LIGHT-OPTICS-CHROMATIC-ABERRATION",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSURECOLOR",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH"
    ],
    "trigger_logic": "相机横移经过多个点光源且强拍连续到来",
    "combined_effect": "每个强拍截取一片不同颜色的曝光轨迹，切片按相机移动方向排列成可读的光幕",
    "why_new": "节拍把连续运动切成有序曝光切片，颜色记录每片的时间阶段",
    "preview_behavior": "移动端预览从强拍切片的结果层反推触发：屏幕持续保留对象身份和最近历史，当“相机横移经过多个点光源且强拍连续到来”成立时，把“每个强拍截取一片不同颜色的曝光轨迹，切片按相机移动方向排列成可读的光幕”分成进入、保持、退场三段显示。若出现强拍过密会造成切片重叠，合并相邻切片，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把强拍切片拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“相机横移经过多个点光源且强拍连续到来”，再细化“每个强拍截取一片不同颜色的曝光轨迹，切片按相机移动方向排列成可读的光幕”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "强拍过密会造成切片重叠，合并相邻切片"
    ],
    "target_scenarios": [
        "在人物视线拉焦的产品展示使用强拍切片。镜头从未触发状态开始横向移动，人物或物体执行“相机横移经过多个点光源且强拍连续到来”后继续穿过画面，以“每个强拍截取一片不同颜色的曝光轨迹，切片按相机移动方向排列成可读的光幕”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-EXPOSURE-MOTION-COLOR-V3",
    "name_zh": "旋转曝光色散轨迹·回卷曝光",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-LIGHT-OPTICS-CHROMATIC-ABERRATION",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSURECOLOR",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSUREBEAT"
    ],
    "trigger_logic": "相机完成旋转后反向回扫同一路径",
    "combined_effect": "新轨迹沿原路径反向回卷，色散边缘从外向内收窄，旧轨迹在回扫结束时合并",
    "why_new": "相机反向运动改变曝光历史方向，回卷是由真实回扫动作触发",
    "preview_behavior": "拍摄者先看到回卷曝光所需的对象边界、方向箭头和时间门；“相机完成旋转后反向回扫同一路径”被连续确认后，预览按由近到远的层次展开“新轨迹沿原路径反向回卷，色散边缘从外向内收窄，旧轨迹在回扫结束时合并”。镜头旋转留下带颜色分层的曝光轨迹，强拍把轨迹切成短暂停格片段，回到实时后色带继续流动，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验回卷曝光的身份链与事件顺序，再按相机运动轨迹提供旋转曝光方向，光绘笔刷累积亮点路径，色散边缘按轨迹速度分色，节拍时钟切出停格节点重建组件关系。“新轨迹沿原路径反向回卷，色散边缘从外向内收窄，旧轨迹在回扫结束时合并”使用完整历史窗口重新渲染，而“相机完成旋转后反向回扫同一路径”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "回扫偏离原路径会出现断带，按最近路径匹配并淡出"
    ],
    "target_scenarios": [
        "把回卷曝光安排在夜景旋转曝光的环绕机位：固定主体身份后执行“相机完成旋转后反向回扫同一路径”，拍摄者绕触发点改变观察角度，用“新轨迹沿原路径反向回卷，色散边缘从外向内收窄，旧轨迹在回扫结束时合并”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-EXPOSURE-MOTION-COLOR-V4",
    "name_zh": "旋转曝光色散轨迹·光源脉冲",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-LIGHT-OPTICS-CHROMATIC-ABERRATION",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSURECOLOR",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITCHASE"
    ],
    "trigger_logic": "点光源速度出现峰值且节拍相位进入强拍",
    "combined_effect": "光源轨迹在速度峰值处形成星芒节点，节点颜色按速度分段并在强拍时短暂爆亮",
    "why_new": "速度峰值、光源位置与拍点共同决定节点，避免普通镜头光斑叠加",
    "preview_behavior": "为预览光源脉冲，系统只更新与“点光源速度出现峰值且节拍相位进入强拍”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“光源轨迹在速度峰值处形成星芒节点，节点颜色按速度分段并在强拍时短暂爆亮”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "光源脉冲的后处理从失败点开始：针对“星芒过亮会吞没色散，降低节点中心曝光”复核掩码、锚点或时间戳，通过后才将“光源轨迹在速度峰值处形成星芒节点，节点颜色按速度分段并在强拍时短暂爆亮”提升到成片质量。触发逻辑“点光源速度出现峰值且节拍相位进入强拍”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "星芒过亮会吞没色散，降低节点中心曝光"
    ],
    "target_scenarios": [
        "舞蹈人物经过镜头的擦镜转场可用光源脉冲组织一段连续互动。参与者先保持关系稳定，再完成“点光源速度出现峰值且节拍相位进入强拍”；镜头不切断，直到“光源轨迹在速度峰值处形成星芒节点，节点颜色按速度分段并在强拍时短暂爆亮”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-EXPOSURE-MOTION-COLOR-V5",
    "name_zh": "旋转曝光色散轨迹·边缘染色",
    "component_atom_ids": [
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION",
        "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        "ATOM-LIGHT-OPTICS-CHROMATIC-ABERRATION",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK",
        "ATOM-SEGMENTATION-MASKS-OBJECT-INSTANCE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSURECOLOR",
        "FX-LIGHT-TRAILS-OPTICS-SOURCE-MOVE",
        "FX-LIGHT-TRAILS-OPTICS-BEAT-STUTTERTRAIL",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "相机从暗处转向亮处且轨迹跨过建筑边缘",
    "combined_effect": "建筑边缘被曝光轨迹染成细色边，亮处轨迹继续流动，暗处只保留一条冷色回声",
    "why_new": "场景边缘参与色散合成，曝光轨迹因此会被空间结构分段",
    "preview_behavior": "边缘染色的取景反馈以结束状态为目标：预览先保留真实动作，在“相机从暗处转向亮处且轨迹跨过建筑边缘”完成时快速呈现“建筑边缘被曝光轨迹染成细色边，亮处轨迹继续流动，暗处只保留一条冷色回声”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留边缘染色的完整生命周期。系统逆向检查“建筑边缘被曝光轨迹染成细色边，亮处轨迹继续流动，暗处只保留一条冷色回声”是否回到稳定终态，再从“相机从暗处转向亮处且轨迹跨过建筑边缘”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "边缘检测误选纹理会产生杂色，限制长直边触发"
    ],
    "target_scenarios": [
        "以切面或光轨合拢后的结束镜头作为边缘染色的结尾段落：让“相机从暗处转向亮处且轨迹跨过建筑边缘”发生在最后一个动作峰值，保持机位直到“建筑边缘被曝光轨迹染成细色边，亮处轨迹继续流动，暗处只保留一条冷色回声”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
    _b(
        "WIPE-PERSON-PORTAL", "effect_cinematography", "人体擦镜空间门户",
        (
            "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
            "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
            "ATOM-SEGMENTATION-MASKS-FOREGROUND",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        ),
        (
            "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
            "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
            "FX-WORLD-STYLE-COMIC-COMICWIPE",
        ),
        ("spatial_portal", "body_pose", "world_anchor"),
        "人体轮廓作为移动擦镜面，前景掩码保护擦镜前后的主体层，画面穿越把边界变成门户，世界锚点固定接缝",
        "人物经过镜头时，身体轮廓像一道有厚度的擦镜门，门后世界随通过方向切换并在接缝处保留漫画边线",
        "预览只用人体轮廓和简化门后背景，经过镜头中心时才生成门户厚度和漫画边线",
        "录制后重建人体掩码、穿越边界和世界接缝，细化头发、手臂遮挡及新旧背景光照",
        "街拍、舞蹈转场或人物经过镜头时完成一个自然的空间换页",
        (
        {
    "recipe_id": "RECIPE-WIPE-PERSON-PORTAL-V1",
    "name_zh": "人体擦镜空间门户·肩部擦换",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-CAMERA-MOTION"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-COMIC-COMICWIPE",
        "FX-EFFECT-CINEMATOGRAPHY-ZOOM-ZOOMGAZE"
    ],
    "trigger_logic": "人物肩部从画面左侧进入并遮住镜头中心",
    "combined_effect": "肩部轮廓扫过的位置变成漫画边线，身后背景逐步切换成目标空间，肩部离开后接缝合拢",
    "why_new": "人体速度决定擦换推进，世界锚点保持接缝，漫画边线记录了擦镜轨迹",
    "preview_behavior": "预览只用人体轮廓和简化门后背景，经过镜头中心时才生成门户厚度和漫画边线。针对肩部擦换，取景器先在“人物肩部从画面左侧进入并遮住镜头中心”发生前标出候选轨迹，确认后才显示“肩部轮廓扫过的位置变成漫画边线，身后背景逐步切换成目标空间，肩部离开后接缝合拢”；触发区域以外保持原始画面，便于判断空间锚点是否稳定。",
    "post_behavior": "录制后重建人体掩码、穿越边界和世界接缝，细化头发、手臂遮挡及新旧背景光照。录后以“人物肩部从画面左侧进入并遮住镜头中心”的首帧为时间锚，重新计算肩部擦换涉及的遮挡和深度，使“肩部轮廓扫过的位置变成漫画边线，身后背景逐步切换成目标空间，肩部离开后接缝合拢”在原分辨率下保持连续；检测到肩部掩码孔洞会露出旧背景，使用轮廓内缩时仅修补低置信度片段。",
    "risks": [
        "肩部掩码孔洞会露出旧背景，使用轮廓内缩"
    ],
    "target_scenarios": [
        "旅行街景中的手绘分屏镜头适合拍摄肩部擦换：先让主体完成“人物肩部从画面左侧进入并遮住镜头中心”，随后缓慢移动手机观察“肩部轮廓扫过的位置变成漫画边线，身后背景逐步切换成目标空间，肩部离开后接缝合拢”与真实遮挡的关系，最后停在效果的空间终点。"
    ]
},
        {
    "recipe_id": "RECIPE-WIPE-PERSON-PORTAL-V2",
    "name_zh": "人体擦镜空间门户·转身开门",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-TEMPORAL-STATE-BEAT-PHASE-CLOCK"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-COMIC-COMICWIPE",
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPETOUCH"
    ],
    "trigger_logic": "人物在镜头前转身并让躯干完整覆盖中部",
    "combined_effect": "躯干轮廓成为门户门扇，转身方向决定门的开合，人物离开时从另一空间露出",
    "why_new": "转身姿态和门户开合共享身体法线，擦镜效果因此具有动作因果",
    "preview_behavior": "移动端预览从转身开门的结果层反推触发：屏幕持续保留对象身份和最近历史，当“人物在镜头前转身并让躯干完整覆盖中部”成立时，把“躯干轮廓成为门户门扇，转身方向决定门的开合，人物离开时从另一空间露出”分成进入、保持、退场三段显示。若出现转身过快会错估门扇方向，使用上一姿态短时预测，当前帧立即退回可信轮廓。",
    "post_behavior": "成片阶段把转身开门拆成触发、发展和回收三条可调时间线。系统沿对象轨迹重放“人物在镜头前转身并让躯干完整覆盖中部”，再细化“躯干轮廓成为门户门扇，转身方向决定门的开合，人物离开时从另一空间露出”的边缘、材质和粒子密度；原始动作帧始终保留用于逐段回退。",
    "risks": [
        "转身过快会错估门扇方向，使用上一姿态短时预测"
    ],
    "target_scenarios": [
        "在人物视线拉焦的产品展示使用转身开门。镜头从未触发状态开始横向移动，人物或物体执行“人物在镜头前转身并让躯干完整覆盖中部”后继续穿过画面，以“躯干轮廓成为门户门扇，转身方向决定门的开合，人物离开时从另一空间露出”完成一次清晰的中段转折。"
    ]
},
        {
    "recipe_id": "RECIPE-WIPE-PERSON-PORTAL-V3",
    "name_zh": "人体擦镜空间门户·手臂双擦",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-COMIC-COMICWIPE",
        "FX-EFFECT-CINEMATOGRAPHY-EXPOSURE-EXPOSUREBEAT"
    ],
    "trigger_logic": "人物先伸手遮住左侧再用另一只手遮住右侧",
    "combined_effect": "两条手臂分别擦出两道窄门，中间背景保持原样，第二道门完成后两门合并成一页",
    "why_new": "分段人体遮挡生成多道门户，动作顺序决定页面合并方式",
    "preview_behavior": "拍摄者先看到手臂双擦所需的对象边界、方向箭头和时间门；“人物先伸手遮住左侧再用另一只手遮住右侧”被连续确认后，预览按由近到远的层次展开“两条手臂分别擦出两道窄门，中间背景保持原样，第二道门完成后两门合并成一页”。人物经过镜头时，身体轮廓像一道有厚度的擦镜门，门后世界随通过方向切换并在接缝处保留漫画边线，因此镜头移动时仍能读出前后关系。",
    "post_behavior": "录制结束后先校验手臂双擦的身份链与事件顺序，再按人体轮廓作为移动擦镜面，前景掩码保护擦镜前后的主体层，画面穿越把边界变成门户，世界锚点固定接缝重建组件关系。“两条手臂分别擦出两道窄门，中间背景保持原样，第二道门完成后两门合并成一页”使用完整历史窗口重新渲染，而“人物先伸手遮住左侧再用另一只手遮住右侧”只决定作用区间，不改写区间外的原视频。",
    "risks": [
        "双臂交叉会交换门身份，按进入时间保持归属"
    ],
    "target_scenarios": [
        "把手臂双擦安排在夜景旋转曝光的环绕机位：固定主体身份后执行“人物先伸手遮住左侧再用另一只手遮住右侧”，拍摄者绕触发点改变观察角度，用“两条手臂分别擦出两道窄门，中间背景保持原样，第二道门完成后两门合并成一页”展示前后层、时间层或材质层的差异。"
    ]
},
        {
    "recipe_id": "RECIPE-WIPE-PERSON-PORTAL-V4",
    "name_zh": "人体擦镜空间门户·舞步换景",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-INTERACTION-TRIGGERS-TOUCH-DRAW"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-COMIC-COMICWIPE",
        "FX-EFFECT-CINEMATOGRAPHY-SPLIT-SPLITCHASE"
    ],
    "trigger_logic": "人物横向舞步连续经过三个位置",
    "combined_effect": "每一步擦过的区域切换为不同世界风格，三块背景沿人体轮廓留下短漫画边并按舞步顺序排列",
    "why_new": "人体运动轨迹成为多页世界索引，空间切换与舞步阶段一一对应",
    "preview_behavior": "为预览舞步换景，系统只更新与“人物横向舞步连续经过三个位置”相关的局部缓存，并在屏幕边缘显示触发置信度。动作越过门限后，“每一步擦过的区域切换为不同世界风格，三块背景沿人体轮廓留下短漫画边并按舞步顺序排列”从触发点向关联对象传播；一旦身份或遮挡失稳，传播停止而不是继续套用效果。",
    "post_behavior": "舞步换景的后处理从失败点开始：针对“背景生成过多会延迟，预览只保留最近两页”复核掩码、锚点或时间戳，通过后才将“每一步擦过的区域切换为不同世界风格，三块背景沿人体轮廓留下短漫画边并按舞步顺序排列”提升到成片质量。触发逻辑“人物横向舞步连续经过三个位置”和效果退场分别保存为可单独调整的元数据。",
    "risks": [
        "背景生成过多会延迟，预览只保留最近两页"
    ],
    "target_scenarios": [
        "舞蹈人物经过镜头的擦镜转场可用舞步换景组织一段连续互动。参与者先保持关系稳定，再完成“人物横向舞步连续经过三个位置”；镜头不切断，直到“每一步擦过的区域切换为不同世界风格，三块背景沿人体轮廓留下短漫画边并按舞步顺序排列”传播并回落到可读状态。"
    ]
},
        {
    "recipe_id": "RECIPE-WIPE-PERSON-PORTAL-V5",
    "name_zh": "人体擦镜空间门户·回穿复原",
    "component_atom_ids": [
        "ATOM-SEGMENTATION-MASKS-BODY-SILHOUETTE",
        "ATOM-DEFORMATION-SPACE-FRAME-TRAVERSAL",
        "ATOM-SEGMENTATION-MASKS-FOREGROUND",
        "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
        "ATOM-GEOMETRY-TRACKING-OBJECT-POSE"
    ],
    "component_effect_ids": [
        "FX-EFFECT-CINEMATOGRAPHY-WIPE-WIPEBODY",
        "FX-SPATIAL-PORTALS-PAGE-PAGEWALK",
        "FX-WORLD-STYLE-COMIC-COMICWIPE",
        "FX-EFFECT-CINEMATOGRAPHY-FOCUS-FOCUSPULSE"
    ],
    "trigger_logic": "人物反向沿原路线走回并再次覆盖镜头中心",
    "combined_effect": "旧背景沿人体轮廓反向擦回，门户边缘按原接缝闭合，最后恢复原场景的光照和纹理",
    "why_new": "返回路径控制世界复原方向，锚点和人体身份让换景具有可逆性",
    "preview_behavior": "回穿复原的取景反馈以结束状态为目标：预览先保留真实动作，在“人物反向沿原路线走回并再次覆盖镜头中心”完成时快速呈现“旧背景沿人体轮廓反向擦回，门户边缘按原接缝闭合，最后恢复原场景的光照和纹理”的收束形态，随后显示可回收的锚点、时间层或关系边，让用户知道如何主动结束效果。",
    "post_behavior": "最终输出保留回穿复原的完整生命周期。系统逆向检查“旧背景沿人体轮廓反向擦回，门户边缘按原接缝闭合，最后恢复原场景的光照和纹理”是否回到稳定终态，再从“人物反向沿原路线走回并再次覆盖镜头中心”处向前后扩展少量帧，补齐快速动作造成的断口；无法恢复的区域以原画面平滑替换。",
    "risks": [
        "回穿路线偏移会留下接缝，沿历史轨迹吸附"
    ],
    "target_scenarios": [
        "以切面或光轨合拢后的结束镜头作为回穿复原的结尾段落：让“人物反向沿原路线走回并再次覆盖镜头中心”发生在最后一个动作峰值，保持机位直到“旧背景沿人体轮廓反向擦回，门户边缘按原接缝闭合，最后恢复原场景的光照和纹理”完成回收、闭合或定格，留下可直接分享的视觉证据。"
    ]
},
        ),
    ),
)


_BLUEPRINT_BY_SLUG = {blueprint["slug"]: blueprint for blueprint in RECIPE_BLUEPRINTS}
_RECIPE_PREFIXES = tuple(
    sorted((f"RECIPE-{slug}-" for slug in _BLUEPRINT_BY_SLUG), key=len, reverse=True)
)
_VARIANT_PATTERN = re.compile(r"-V([1-5])$")

def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _source_ids() -> tuple[set[str], set[str]]:
    atoms = _read_jsonl(ATOM_INPUT)
    ideas = _read_jsonl(IDEA_INPUT)
    return (
        {atom["atom_id"] for atom in atoms},
        {idea["effect_id"] for idea in ideas},
    )


def blueprint_slug(recipe: Mapping[str, object]) -> str:
    recipe_id = str(recipe["recipe_id"])
    for prefix in _RECIPE_PREFIXES:
        if recipe_id.startswith(prefix) and _VARIANT_PATTERN.search(recipe_id):
            return prefix[len("RECIPE-") : -1]
    raise ValueError(f"unknown recipe blueprint in {recipe_id}")


def recipe_dimensions(recipe: Mapping[str, object]) -> tuple[str, ...]:
    component_ids = tuple(recipe["component_atom_ids"]) + tuple(recipe["component_effect_ids"])
    dimensions = []
    for dimension, markers in _DIMENSION_COMPONENT_MARKERS.items():
        if any(
            component_id == marker or marker in component_id
            for component_id in component_ids
            for marker in markers
        ):
            dimensions.append(dimension)
    return tuple(dimension for dimension in _DIMENSION_ORDER if dimension in dimensions)


_DIMENSION_COMPONENT_MARKERS = {
    "realtime_light_trail": ("LIGHT-TRAILS", "LIGHT-PAINT-BRUSH", "EXPOSURE"),
    "world_anchor": ("WORLD-SPACE-ANCHOR", "-WORLD-", "WORLD-ANCHOR"),
    "sound": ("AUDIO-BEAT", "SOUND-VOLUME", "LYRIC-TIMESTAMP", "AUDIO-LYRICS", "-VOICE", "-BEAT"),
    "spatial_portal": ("MIRROR-PORTAL", "FRAME-TRAVERSAL", "TUNNEL-WARP", "FX-SPATIAL-PORTALS", "-WIPE-"),
    "body_pose": ("BODY-SKELETON", "BODY-SILHOUETTE", "POSE-SLICES", "BODY-MOTION", "BODY-"),
    "time": ("ATOM-TEMPORAL-STATE", "ATOM-CLONING-ECHOES", "FX-TIME-EDITING", "FX-BODY-MOTION-CLONES", "-STUTTER"),
    "gaze": ("GAZE-VECTOR", "GAZE-FOCUS", "IRIS-PUPIL", "FACE-GAZE", "FOCUSGAZE"),
    "material": ("ATOM-MATERIAL-APPEARANCE", "FX-MATERIAL-MORPH"),
    "expression": ("ATOM-INTERACTION-TRIGGERS-BLINK", "ATOM-INTERACTION-TRIGGERS-EXPRESSION", "ATOM-INTERACTION-TRIGGERS-MOUTH", "CATCHLIGHT", "GLOW-"),
    "multi_person": ("MULTI-PERSON", "DUET", "STATUE", "ENERGY"),
    "color_layer": ("CHROMATIC-ABERRATION", "POSECOLOR", "EXPOSURECOLOR", "CATCHCOLOR", "-COLOR"),
    "touch_gesture": ("TOUCH-DRAW", "MULTI-PERSON-TOUCH", "-TOUCH", "-GESTURE", "HAND-GESTURE"),
    "shadow": ("SHADOW", "SHADOW-"),
    "action_inverse": ("TIME-REVERSE", "-REVERSE", "REVERSE-"),
    "particle": ("PARTICLES-ATMOSPHERE", "FX-PARTICLES"),
    "generative_world": ("BACKGROUND-WORLD", "FX-WORLD-STYLE"),
    "generative_style": ("VISUAL-STYLE", "HOLO", "FX-WORLD-STYLE"),
    "light": ("CATCHLIGHT", "RIM-LIGHT", "LUMINOUS-CORE", "VIRTUAL-SPOTLIGHT", "FX-VIRTUAL-LIGHT"),
}


def recipe_fingerprint(recipe: Mapping[str, object]) -> tuple[object, ...]:
    normalize = lambda value: " ".join(str(value).split()).casefold()
    return (
        tuple(sorted(recipe["component_atom_ids"])),
        tuple(sorted(recipe["component_effect_ids"])),
        normalize(recipe["trigger_logic"]),
        normalize(recipe["combined_effect"]),
        normalize(recipe["preview_behavior"]),
    )


def build_recipes() -> list[dict[str, object]]:
    return [
        copy.deepcopy(variant)
        for blueprint in RECIPE_BLUEPRINTS
        for variant in blueprint["variants"]
    ]


def _has_components(recipe: Mapping[str, object], *required: str) -> bool:
    components = set(recipe["component_atom_ids"]) | set(recipe["component_effect_ids"])
    return all(component_id in components for component_id in required)


def count_key_patterns(recipes: Iterable[Mapping[str, object]]) -> dict[str, int]:
    patterns = {
        "hand_anchor_light": (
            "ATOM-GEOMETRY-TRACKING-HAND-3D-TRAJECTORY",
            "ATOM-GEOMETRY-TRACKING-WORLD-SPACE-ANCHOR",
            "ATOM-LIGHT-OPTICS-LIGHT-PAINT-BRUSH",
        ),
        "gaze_catch_dialogue": (
            "ATOM-GEOMETRY-TRACKING-GAZE-VECTOR",
            "ATOM-LIGHT-OPTICS-CATCHLIGHT-RERENDER",
            "FX-FACE-GAZE-EXPRESSION-DIALOGUE-REDIRECT",
        ),
        "clone_pose_color": (
            "ATOM-CLONING-ECHOES-HUMAN-TIME-CLONE",
            "ATOM-CLONING-ECHOES-POSE-SLICES",
            "FX-BODY-MOTION-CLONES-POSE-POSECOLOR",
        ),
        "shadow_delay_reverse": (
            "ATOM-SEGMENTATION-MASKS-SHADOW",
            "ATOM-TEMPORAL-STATE-FRAME-DELAY",
            "ATOM-TEMPORAL-STATE-TIME-REVERSE",
            "FX-BODY-MOTION-CLONES-SHADOW-SHADOWREVERSE",
        ),
        "lyric_mouth_ring": (
            "ATOM-INTERACTION-TRIGGERS-LYRIC-TIMESTAMP",
            "ATOM-INTERACTION-TRIGGERS-MOUTH-SHAPE",
            "ATOM-PARTICLES-ATMOSPHERE-LYRIC-RING",
        ),
        "graph_touch_energy": (
            "ATOM-GEOMETRY-TRACKING-MULTI-PERSON-GRAPH",
            "ATOM-INTERACTION-TRIGGERS-MULTI-PERSON-TOUCH",
            "FX-MULTI-PERSON-INTERACTION-ENERGY-ENERGYTOUCH",
        ),
    }
    return {
        name: sum(_has_components(recipe, *required) for recipe in recipes)
        for name, required in patterns.items()
    }


KEY_PATTERN_COUNTS = count_key_patterns(build_recipes())


def validate_recipes(
    recipes: list[dict[str, object]],
    atom_ids: set[str],
    idea_ids: set[str],
) -> dict[str, object]:
    """Validate schema, references, explicit blueprint coverage, and uniqueness."""

    if not isinstance(recipes, list):
        raise ValueError("recipes must be a list")
    canonical = build_recipes()
    if recipes != canonical:
        raise ValueError("recipe variants must match canonical blueprint records")
    for index, recipe in enumerate(recipes):
        if not isinstance(recipe, Mapping):
            raise ValueError(f"recipe[{index}] must be a mapping")
        if set(recipe) != set(RECIPE_FIELDS):
            raise ValueError(f"recipe[{index}] fields must match schema fields exactly")
        try:
            schema.validate_recipe(recipe, atom_ids, idea_ids)
        except ValueError as exc:
            recipe_id = recipe.get("recipe_id", f"index {index}")
            raise ValueError(f"schema validation failed for {recipe_id}: {exc}") from exc
        all_components = list(recipe["component_atom_ids"]) + list(recipe["component_effect_ids"])
        if len(all_components) != len(set(all_components)):
            raise ValueError(f"duplicate component ID across lists: {recipe['recipe_id']}")
        blueprint_slug(recipe)

    for field in ("recipe_id", "name_zh"):
        duplicates = _find_duplicates(recipe[field] for recipe in recipes)
        if duplicates:
            raise ValueError(f"duplicate {field}: {', '.join(duplicates)}")

    blueprint_counts = Counter(blueprint_slug(recipe) for recipe in recipes)
    expected_slugs = tuple(blueprint["slug"] for blueprint in RECIPE_BLUEPRINTS)
    if tuple(dict.fromkeys(blueprint_slug(recipe) for recipe in recipes)) != expected_slugs:
        raise ValueError("recipes are not in stable blueprint order")
    if set(blueprint_counts) != set(expected_slugs):
        raise ValueError("recipe blueprint set is incomplete")
    if any(count != 5 for count in blueprint_counts.values()):
        raise ValueError("every recipe blueprint must have exactly five variants")

    fingerprints = [recipe_fingerprint(recipe) for recipe in recipes]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("recipe semantic fingerprints must be unique")

    family_counts = Counter(
        _BLUEPRINT_BY_SLUG[blueprint_slug(recipe)]["family"] for recipe in recipes
    )
    dimensions = Counter(
        dimension
        for recipe in recipes
        for dimension in recipe_dimensions(recipe)
    )
    return {
        "count": len(recipes),
        "family_counts": dict(family_counts),
        "blueprint_counts": dict(blueprint_counts),
        "fingerprint_count": len(fingerprints),
        "multidimensional_count": sum(
            len(set(recipe_dimensions(recipe)) & MULTIDIMENSION_AXES) >= 2
            for recipe in recipes
        ),
        "dimension_counts": dict(dimensions),
        "key_pattern_counts": count_key_patterns(recipes),
    }


def _find_duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def write_jsonl(recipes: list[dict[str, object]], path: Path = RECIPE_OUTPUT) -> None:
    atom_ids, idea_ids = _source_ids()
    validate_recipes(recipes, atom_ids, idea_ids)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output:
        for recipe in recipes:
            output.write(json.dumps(recipe, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")


def main(argv: list[str] | None = None, *, output: Path = RECIPE_OUTPUT) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=output)
    args = parser.parse_args(argv)
    recipes = build_recipes()
    atom_ids, idea_ids = _source_ids()
    report = validate_recipes(recipes, atom_ids, idea_ids)
    write_jsonl(recipes, args.output)
    print(f"wrote {report['count']} recipes to {args.output}")
    print(f"blueprints: {report['blueprint_counts']}")
    print(f"families: {report['family_counts']}")
    print(f"multidimensional: {report['multidimensional_count']}")


if __name__ == "__main__":
    main()
