"""Build a large, deterministic mobile-video post-processing idea universe."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


AXES = {
    "processing_stage": {
        "label": "处理阶段",
        "values": [
            ("preview", "实时预览", "用低分辨率分析和轻量代理模型提供取景反馈"),
            ("online_recording", "录制在线", "采用因果时序缓存，在编码前持续处理"),
            ("offline_device", "录后端侧", "利用完整前后文和设备空闲算力重新成片"),
            ("cloud_render", "云端高质量", "上传必要素材和元数据，执行高成本非因果重建"),
        ],
    },
    "truth_boundary": {
        "label": "真实性边界",
        "values": [
            ("faithful", "忠实恢复", "禁止新增不可观察事实，并保留恢复置信度"),
            ("perceptual", "感知增强", "允许受控调整观感，但保护身份、文字和事件事实"),
            ("generative", "生成式创作", "允许重构内容，同时保存原片、Mask、参数和生成标记"),
        ],
    },
    "input_mode": {
        "label": "输入信号",
        "values": [
            ("single_camera", "单摄", "仅依靠单摄连续帧、相机元数据和时序先验"),
            ("dual_camera", "双摄", "利用双焦段或双曝光视角提供互补细节和视差"),
            ("depth", "深度", "引入 ToF、LiDAR、双目或单目深度以约束遮挡和空间效果"),
            ("imu", "IMU", "使用陀螺仪、加速度计和 OIS 位姿约束相机运动"),
            ("audio", "音频", "使用声源方向、事件声音、对白或音乐节奏作为控制信号"),
            ("multi_device", "多设备", "多手机或相机共享时间码、位姿、声音和主体轨迹"),
        ],
    },
    "scene": {
        "label": "用户场景",
        "values": [
            ("portrait", "人像", "围绕身份、肤色、发丝、眼镜和人物光照设计"),
            ("pet", "宠物", "适应不可预测运动、毛发、低机位和短时精彩事件"),
            ("children", "儿童", "保护身份和自然表情，并结合环形缓存捕捉瞬间"),
            ("sports", "运动", "优先高速运动、稳定、轨迹、慢动作和精彩事件"),
            ("night", "夜景", "强化低照、动态范围、频闪、霓虹和复杂混合光处理"),
            ("concert", "演唱会", "保护舞台 LED、高光、远距离主体、音频节拍和遮挡"),
            ("travel", "旅行", "强化建筑、天气、路人、空间运镜和跨镜头连续性"),
            ("live", "直播", "强调低延迟、长时稳定、身份可信、温控和即时交互"),
        ],
    },
    "temporal_spec": {
        "label": "时间规格",
        "values": [
            ("30fps", "30 fps", "以常规实时录像预算设计完整功能"),
            ("60fps", "60 fps", "缩短窗口并复用运动信息以满足更高帧率"),
            ("high_fps", "高帧率慢动作", "面向 120/240 fps 使用短曝光和事件窗口"),
            ("long_recording", "长时间录像", "增加温控、状态压缩、漂移重置和断点续算"),
        ],
    },
    "processing_scope": {
        "label": "处理范围",
        "values": [
            ("full_frame", "全画面", "全分辨率统一处理并检查全局一致性"),
            ("roi", "ROI", "只对主体、脸、文字、光源或问题区域投入高质量算力"),
            ("keyframe", "关键帧", "关键帧运行高成本模型，中间帧采用传播和校正"),
            ("proxy", "低功耗代理", "录制时生成轻量版本，录后再恢复高质量母版"),
        ],
    },
    "delivery": {
        "label": "交付形态",
        "values": [
            ("instant_share", "即时分享", "快速导出可直接发布的紧凑成片"),
            ("master", "专业母版", "保留高位深、宽色域和可追溯处理参数"),
            ("editable_project", "可编辑工程", "封装原片、图层、Mask、轨迹、深度和控制参数"),
            ("edge_cloud", "端云协同", "端侧处理敏感和忠实部分，云端完成高成本重算"),
        ],
    },
}


PRIOR_IDEAS = [
    ("计算底片", "capture_system", "将原片、深度、Mask、运动、曝光和光照信息封装为可重算录像资产"),
    ("可重放 ISP", "capture_system", "录后重新选择降噪、HDR、锐化、色彩和人像处理链"),
    ("即时成片与高质量母版双轨录像", "capture_system", "拍摄时输出即时分享版，并在设备空闲后重算专业母版"),
    ("对象级可编辑视频", "capture_system", "把人物、天空、灯光、反射、文字和背景保存为独立时序图层"),
    ("置信度录像", "capture_system", "为恢复、补全和生成区域保存逐像素时空置信度"),
    ("对象级快门", "temporal_exposure", "人物、背景和高亮轨迹采用不同的等效快门角"),
    ("运动分层 HDR", "night_hdr", "静态区域积累动态范围，快速主体使用短曝光恢复"),
    ("时间焦点", "temporal_exposure", "目标动作保持清晰，动作发生前后逐渐进入时间模糊"),
    ("Event Sensor 融合录像", "sensor_fusion", "普通图像传感器提供颜色，事件流提供高速运动和亮度变化"),
    ("意图感知稳定", "motion_quality", "识别摇摄、跟拍、甩镜和升降，保留创作者主动运动"),
    ("运动模糊重新渲染", "motion_quality", "先恢复结构，再按真实相机和物体运动重新生成电影化模糊"),
    ("视频光源分解", "relighting", "分离环境光、主光、轮廓光、屏幕光、反射光和阴影"),
    ("真实光与虚拟光融合", "relighting", "虚拟光受深度、遮挡、材质和真实阴影约束"),
    ("PWM与LED防频闪录像", "night_hdr", "结合逐行曝光时间和频率估计校正灯牌与舞台频闪"),
    ("真实镜头个性学习", "computational_optics", "学习具体镜头的眩光、焦外、呼吸、暗角和色彩响应"),
    ("可控动态星芒系统", "computational_optics", "依据光源、光圈叶片、焦距和相机运动控制星芒"),
    ("玻璃反射分离录像", "material_editing", "将玻璃内外景和反射层分离后独立增强或抑制"),
    ("连续焦段计算镜头", "multi_camera", "跨超广角、主摄和长焦形成连续的曝光、纹理和透视模型"),
    ("多手机协同电影机", "multi_device", "共享时间码、颜色、位姿、主体轨迹、声音和导播策略"),
    ("身份可信的人像增强", "portrait_identity", "增强前后持续验证身份表征、肤色和面部几何"),
    ("隐私身份替换", "privacy", "对路人做可逆、可审计的匿名替换并保留原始保护层"),
    ("材质级视频编辑", "material_editing", "按皮肤、金属、玻璃、水面、天空和织物分别处理"),
    ("背景持久记忆", "scene_memory", "利用拍摄前已观察背景恢复后续短时遮挡"),
    ("声源方向驱动跟焦", "audio_visual", "以麦克风阵列定位说话人并驱动焦点轨迹"),
    ("多人对话自动导播", "audio_visual", "融合对白、视线、表情和构图自动选择人物与景别"),
    ("保护区生成式编辑", "trustworthy_generation", "脸、文字、商标和主体默认锁定，生成仅限用户授权区域"),
    ("视频世界状态记忆", "trustworthy_generation", "记录物体身份、位置、材质和关系，防止生成跨镜头漂移"),
    ("编码器运动矢量复用", "codec_system", "复用编码运动信息以降低光流、传播和稳定成本"),
    ("功耗感知模型路由", "edge_system", "根据温度、功耗和 NPU 负载动态选择模型和处理范围"),
    ("边录边建立场景三维缓存", "spatial_video", "拍摄时持续积累空间结构，为录后运镜和遮挡恢复服务"),
    ("演唱会计算摄影录像系统", "concert", "联合 LED 保护、远距主体恢复、音频事件、追光和星芒"),
    ("儿童与宠物精彩事件录像系统", "event_capture", "使用环形缓存、声音、表情和动作预测保存事件前后"),
    ("多手机协同体育导播", "sports_broadcast", "多设备自动选择机位、同步回放、轨迹和精彩事件"),
    ("面向创作者的计算底片母版系统", "capture_system", "从即时代理到可编辑工程和高质量母版形成完整工作流"),
]


FAMILY_ZH = {
    "capture_system": "计算底片与录像系统",
    "temporal_exposure": "曝光、快门与时间",
    "night_hdr": "夜景、HDR 与复杂光源",
    "sensor_fusion": "新型传感器与融合",
    "motion_quality": "运动画质与稳定",
    "relighting": "光照重构与虚拟布光",
    "computational_optics": "计算光学与虚拟镜头",
    "material_editing": "反射、透明与材质",
    "multi_camera": "多摄融合与连续变焦",
    "multi_device": "多设备协同",
    "portrait_identity": "人像细节与身份一致性",
    "privacy": "隐私、安全与真实性",
    "scene_memory": "场景记忆与环境重构",
    "audio_visual": "声音驱动与自动摄影",
    "trustworthy_generation": "可信生成式视频",
    "codec_system": "编解码与语义传输",
    "edge_system": "端侧计算与系统调度",
    "spatial_video": "空间视频与虚拟机位",
    "concert": "演唱会与舞台录像",
    "event_capture": "事件预测与精彩捕捉",
    "sports_broadcast": "体育录像与自动导播",
}


def cluster(
    key: str,
    family: str,
    title: str,
    targets: list[tuple[str, str]],
    mechanisms: list[tuple[str, str, str]],
    signals: list[str],
    scenarios: list[str],
    mobile_value: str,
    temporal_span: str = "short_to_long",
) -> dict:
    return {
        "key": key,
        "family": family,
        "title": title,
        "targets": targets,
        "mechanisms": mechanisms,
        "signals": signals,
        "scenarios": scenarios,
        "mobile_value": mobile_value,
        "temporal_span": temporal_span,
    }


CLUSTERS = [
    cluster("raw_asset", "capture_system", "可重算影像资产",
            [("曝光状态", "重新选择亮度与高光保护"), ("色彩状态", "重新选择白平衡、色调和色域"), ("细节状态", "重新选择降噪、锐化和纹理"), ("语义图层", "重新组合人物、天空、灯光和背景")],
            [("计算底片封装", "保存可逆中间数据", "perceptual"), ("多版本同步录制", "同步生成即时版和母版", "faithful"), ("录后 ISP 重放", "重新执行成像流水线", "faithful"), ("置信度伴随记录", "保存每项处理可信度", "faithful"), ("参数化工程导出", "输出可编辑项目", "perceptual"), ("端云分层重算", "设备与云端分配不同阶段", "perceptual")],
            ["RAW", "YUV", "ISP metadata", "semantic masks"], ["专业创作", "旅行", "直播"], "手机可在拍摄时获得完整相机元数据并调度 ISP/NPU/编码器"),
    cluster("object_exposure", "temporal_exposure", "对象级曝光与快门",
            [("人物主体", "人物清晰并保护肤色"), ("运动载具", "控制速度感和车灯轨迹"), ("天空水面", "分别控制云、水和反射时间积累"), ("舞台屏幕", "分别保护表演者与 LED 内容")],
            [("对象级快门", "不同对象采用不同等效快门角", "perceptual"), ("分层 HDR", "按运动状态分配曝光融合", "faithful"), ("曝光轨迹编程", "时间上设计曝光变化", "perceptual"), ("局部长曝光", "只对选定区域时间积分", "perceptual"), ("瞬态短曝光恢复", "高速片段自动切换短曝光", "faithful"), ("曝光呼吸消除", "跨帧约束局部亮度", "faithful")],
            ["RAW burst", "motion", "semantic masks", "row timestamps"], ["运动", "演唱会", "夜景", "旅行"], "手机能够联合 AE、逐行曝光、运动估计和语义分割"),
    cluster("temporal_canvas", "temporal_exposure", "可编辑时间画布",
            [("动作前后", "控制事件发生前后的时间表现"), ("局部区域", "让画面不同区域处于不同时间速度"), ("高亮轨迹", "控制灯光和反射的时间轨迹"), ("表情瞬间", "选择人物最佳表情和动作节点")],
            [("时间焦点", "主体时刻清晰、前后逐渐模糊", "perceptual"), ("局部时间冻结", "冻结选区并保持其他区域运动", "generative"), ("局部慢放", "对选区重建高帧率", "perceptual"), ("时间反转窗口", "局部动作短时反向播放", "generative"), ("语义时间积分", "按语义累积运动轨迹", "perceptual"), ("最佳时刻重组", "从缓存重组最佳状态", "generative")],
            ["high-fps buffer", "optical flow", "audio events", "semantic tracks"], ["儿童", "宠物", "运动", "舞蹈"], "手机持续环形缓存和多模态事件检测可在按键前后保留时间信息"),
    cluster("intent_stabilization", "motion_quality", "意图感知运动控制",
            [("跟拍人物", "主体稳定同时保留环境速度感"), ("摇摄甩镜", "保留创作者主动旋转与转场"), ("步行跑动", "抑制步态冲击并保留运动节奏"), ("骑行车载", "锁定地平线、道路和转弯倾斜")],
            [("意图分类稳定", "先识别运镜语法再滤波", "faithful"), ("主体背景解耦", "对相机和主体运动分别处理", "faithful"), ("未来轨迹预测", "预留裁切并规划稳定路径", "faithful"), ("运动模糊重渲染", "恢复后按目标轨迹重加模糊", "perceptual"), ("局部非刚性稳定", "对脸、身体和背景分别稳像", "faithful"), ("节奏化稳定", "随音乐或步频改变运动质感", "perceptual")],
            ["IMU", "OIS pose", "optical flow", "subject tracks"], ["Vlog", "运动", "骑行", "车载"], "手机 IMU、OIS、EIS 和语义跟踪可以形成统一的运动意图模型"),
    cluster("motion_recovery", "motion_quality", "运动细节与畸变恢复",
            [("高速人脸", "恢复高速运动中的身份与表情"), ("手部器械", "恢复手指、球拍、乐器和工具"), ("车辆文字", "恢复车身纹理、车牌和灯光"), ("建筑线条", "恢复滚动快门下的垂线和几何")],
            [("方向感知去模糊", "按局部运动核恢复", "faithful"), ("滚动快门联合校正", "逐行时间与运动联合优化", "faithful"), ("多帧细节锚定", "从清晰邻帧传播纹理", "faithful"), ("短长曝光融合", "短曝光保运动、长曝光保信噪比", "faithful"), ("结构优先生成", "只在低置信纹理区感知补全", "perceptual"), ("失真置信度保护", "无法恢复时降低锐化和生成", "faithful")],
            ["short/long exposure", "row timestamps", "motion vectors", "semantic ROI"], ["运动", "夜景", "车载", "演唱会"], "手机可联合曝光计划、PDAF、IMU 和编码运动矢量"),
    cluster("virtual_optics", "computational_optics", "可编程镜头特性",
            [("点光源", "控制星芒、鬼影和光晕"), ("人物高光", "控制柔焦、肤光和轮廓高光"), ("焦外区域", "控制光圈形状、猫眼和旋焦"), ("画面边缘", "控制暗角、像差和边缘焦外")],
            [("物理参数星芒", "按叶片数、角度和焦距渲染", "perceptual"), ("镜头个性迁移", "学习特定镜头响应", "perceptual"), ("光线路径眩光", "依据光源与姿态生成 flare", "perceptual"), ("动态柔焦", "按亮度与语义自适应扩散", "perceptual"), ("可变虚拟光圈", "连续改变焦外核", "generative"), ("光学缺陷可逆控制", "检测后允许修复或艺术化增强", "perceptual")],
            ["lens metadata", "highlight masks", "depth", "camera pose"], ["夜景", "人像", "演唱会", "专业创作"], "手机镜头参数、多摄深度和姿态可驱动时序一致的虚拟光学"),
    cluster("lens_surface", "computational_optics", "镜头表面与介质",
            [("雨滴水珠", "检测镜头或玻璃上的动态水滴"), ("雾气结露", "识别缓慢变化的低对比介质"), ("灰尘污点", "区分固定镜头污点和场景纹理"), ("透明保护壳", "处理壳体反射、划痕和炫光")],
            [("可逆抑制", "生成干净层并保留介质 Mask", "faithful"), ("艺术化增强", "控制水滴、雾气和光晕风格", "perceptual"), ("跨帧背景记忆", "利用未遮挡历史恢复背景", "faithful"), ("介质深度估计", "估计污渍所在光学平面", "faithful"), ("触摸清洁提示", "实时显示问题位置与严重度", "faithful"), ("物理折射重渲染", "按水滴形状修正或强化折射", "generative")],
            ["video", "focus sweep", "IMU", "background memory"], ["雨天", "户外", "车载", "运动"], "手机可用对焦变化、固定传感器坐标和运动差异区分介质与场景"),
    cluster("light_decomposition", "relighting", "视频光场与光源分解",
            [("单人人像", "分别控制主光、轮廓光和环境光"), ("多人场景", "为每个人提供独立但一致的照明"), ("商品材质", "控制金属、玻璃、织物和食物高光"), ("建筑空间", "控制窗光、灯带、屏幕和阴影层")],
            [("光源分层", "估计多个直接与间接光源", "faithful"), ("主光重定向", "改变主光方向与软硬", "generative"), ("虚拟轮廓光", "按深度和遮挡生成边缘光", "perceptual"), ("负补光", "局部压暗以强化主体", "perceptual"), ("眼神光控制", "稳定并编辑眼部高光", "perceptual"), ("阴影一致性审计", "检查人物、物体和地面阴影", "faithful")],
            ["RGB", "depth", "surface normals", "semantic masks"], ["人像", "直播", "商品", "室内"], "手机深度、分割和拍摄前短扫描有利于估计几何与环境光"),
    cluster("complex_lights", "night_hdr", "复杂人造光录像",
            [("LED 屏幕", "保护内容、文字、色彩和刷新纹理"), ("霓虹灯牌", "保持颜色、边缘和高光层次"), ("舞台灯束", "处理频闪、烟雾和移动追光"), ("车灯路灯", "抑制眩光同时保留夜景氛围")],
            [("频率自适应曝光", "检测 PWM 并选择安全曝光", "faithful"), ("逐行频闪校正", "按 row timestamp 修正条带", "faithful"), ("高光内容保护", "屏幕与人物分层 HDR", "faithful"), ("颜色锁定", "跨帧稳定饱和高亮颜色", "faithful"), ("光束空间重建", "利用雾与深度重建灯束", "perceptual"), ("虚实追光融合", "真实灯与虚拟追光联合控制", "generative")],
            ["RAW", "row timestamps", "flicker sensor", "audio beat"], ["演唱会", "夜景", "车载", "室内"], "手机可控制曝光时序，并从连续帧估计灯光频率和相位"),
    cluster("multi_camera_continuity", "multi_camera", "连续焦段与跨摄像头一致性",
            [("曝光色彩", "切镜时维持亮度、白平衡和肤色"), ("纹理噪声", "切镜时维持锐度、噪声和颗粒"), ("运动几何", "切镜时维持运动、视差和稳定轨迹"), ("景深焦点", "切镜时维持焦点距离和虚化风格")],
            [("目标镜头预热", "提前收敛 AE/AWB/AF 和去噪", "faithful"), ("重叠区域校准", "在公共视野估计颜色与细节变换", "faithful"), ("跨摄纹理借用", "主摄与长焦互补纹理", "faithful"), ("跨摄运动共享", "共享光流、IMU 和主体 track", "faithful"), ("连续虚拟焦段", "在物理镜头之间合成连续视角", "perceptual"), ("切镜风格延续", "保持 LUT、颗粒和镜头特性", "perceptual")],
            ["multi-camera", "AE/AWB/AF metadata", "IMU", "depth"], ["旅行", "人像", "演唱会", "运动"], "手机原生多摄可同步采集并共享 ISP 与姿态信息"),
    cluster("spatial_reframe", "spatial_video", "空间录像与录后运镜",
            [("人物周围", "在人物附近进行小幅环绕和推拉"), ("建筑空间", "生成受约束的横移、升降和透视调整"), ("桌面商品", "生成细微轨道运动和景深变化"), ("旅行风景", "进行横竖屏重构和有限画外延展")],
            [("三维缓存", "边录边积累深度和场景点", "faithful"), ("受约束虚拟滑轨", "只在已观测区域内重投影", "faithful"), ("小幅生成机位", "对新显露区域有限补全", "generative"), ("Dolly Zoom 重构", "用真实深度约束透视变化", "generative"), ("自动机位规划", "根据主体和遮挡规划轨迹", "perceptual"), ("生成边界可视化", "显示新增视野和可信度", "faithful")],
            ["multi-camera", "depth", "SLAM", "IMU"], ["旅行", "商品", "人像", "空间视频"], "手机可同时提供多摄、深度、SLAM 和高分辨率裁切余量"),
    cluster("portrait_regions", "portrait_identity", "人像区域可信增强",
            [("眼睛眼镜", "恢复眼部、镜片和眼神光"), ("皮肤五官", "恢复肤质、唇齿和微表情"), ("头发饰品", "恢复发丝、耳饰和边界"), ("服装手部", "恢复织物、手指和身体边缘")],
            [("区域专用恢复", "不同区域路由不同模型", "perceptual"), ("身份嵌入锚定", "持续检查身份和面部几何", "faithful"), ("时序纹理锁定", "减少皮肤和发丝纹理游走", "faithful"), ("反光分层处理", "分离镜片、眼睛和反射", "perceptual"), ("自然度自适应", "根据距离和运动限制增强强度", "perceptual"), ("群体公平审计", "检查肤色、年龄和性别偏差", "faithful")],
            ["face tracks", "landmarks", "parsing", "identity embedding"], ["人像", "直播", "采访", "夜景"], "手机的人脸跟踪、PDAF 和局部 NPU 能以 ROI 方式持续运行"),
    cluster("body_action", "portrait_identity", "人体动作与服装细节",
            [("手指手势", "保护精细动作、手语和器械交互"), ("舞蹈肢体", "保持姿态、衣摆和快速动作"), ("运动装备", "恢复球拍、球、车轮和滑雪板"), ("服装纹理", "稳定条纹、格纹、亮片和织物")],
            [("姿态引导恢复", "用骨架约束局部重建", "faithful"), ("部件运动分解", "手、衣物和身体分别估计运动", "faithful"), ("动作轨迹增强", "显示或艺术化关键动作路径", "perceptual"), ("边界时序锁定", "减少衣摆和手指闪烁", "faithful"), ("运动清晰窗口", "在动作峰值提高局部质量", "faithful"), ("姿态驱动构图", "根据动作趋势预测取景", "faithful")],
            ["body pose", "part masks", "high-fps buffer", "IMU"], ["舞蹈", "运动", "直播", "教育"], "手机可将人体姿态、环形缓存和局部处理结合"),
    cluster("reflection_material", "material_editing", "反射透明与材质分层",
            [("玻璃窗面", "分离内景、外景、反射和污渍"), ("水面湿地", "保护波纹、倒影和镜面高光"), ("金属珠宝", "控制锐利高光、颜色和反射环境"), ("半透明介质", "处理烟雾、纱帘、薄膜和透明容器")],
            [("层分解", "估计透射、反射和散射层", "faithful"), ("材质专用降噪", "按 BRDF 特征选择处理", "faithful"), ("高光重定向", "控制高光位置与强度", "perceptual"), ("环境反射替换", "改变反射环境并标记生成", "generative"), ("材质一致性传播", "锁定纹理和高光运动", "faithful"), ("交互式区域控制", "用户点选材质后独立调节", "perceptual")],
            ["polarization cues", "motion", "depth", "material masks"], ["车内", "商品", "旅行", "美食"], "手机运动、多摄视差和语义分割可帮助分离材质层"),
    cluster("scene_memory", "scene_memory", "场景持续记忆与清理",
            [("短时路人", "利用历史真实背景移除经过人物"), ("前景遮挡", "恢复被手、车辆或人群短时挡住的主体"), ("固定杂物", "识别电线、污点、垃圾和重复干扰物"), ("动态背景", "维护树叶、水面、人群和屏幕的状态")],
            [("真实历史回填", "只用已观察背景恢复", "faithful"), ("场景状态缓存", "维护物体身份和可见性", "faithful"), ("遮挡因果推理", "根据进入离开关系决定恢复", "faithful"), ("受约束生成补全", "无真实背景时有限生成", "generative"), ("用户确认式清理", "自动建议 Mask 并逐项授权", "perceptual"), ("事实保护审计", "锁定文字、人物和事件对象", "faithful")],
            ["long video memory", "object tracks", "depth", "semantic masks"], ["旅行", "街拍", "直播", "车载"], "手机在按下录制前可维护短期场景缓存并持续跟踪物体"),
    cluster("weather_atmosphere", "scene_memory", "天气与空气介质",
            [("天空云层", "控制云量、速度、曝光和颜色"), ("雨雪颗粒", "保护、去除或艺术化降水"), ("雾霾空气", "按深度控制能见度和空气透视"), ("地面环境", "联动湿地反射、阴影和色温")],
            [("物理分层恢复", "估计大气透射与环境光", "faithful"), ("局部天气编辑", "仅编辑授权空间区域", "generative"), ("天气光照联动", "同步天空、阴影、反射和人物光", "generative"), ("降水时序锁定", "保持雨雪速度和遮挡连续", "perceptual"), ("深度感知去雾", "避免远景被过度拉平", "faithful"), ("真实度标记", "导出天气生成 Mask 和参数", "faithful")],
            ["depth", "sky mask", "weather cues", "long-range flow"], ["旅行", "车载", "户外", "直播"], "手机可结合天气传感、定位、深度和场景语义进行约束"),
    cluster("semantic_color", "capture_system", "语义色彩与影调",
            [("人物肤色", "跨光源和镜头保持自然肤色"), ("天空植物", "分别控制蓝天、云层和绿色植被"), ("建筑室内", "保护材质、中性色和灯光氛围"), ("高光阴影", "控制高光 roll-off、黑位和局部对比")],
            [("语义分区 LUT", "不同区域使用协同色彩变换", "perceptual"), ("参考外观记忆", "学习用户长期喜欢的影调", "perceptual"), ("跨镜头色彩锁定", "多摄和多段视频保持连续", "faithful"), ("胶片响应模拟", "模拟颗粒、晕光和曲线", "perceptual"), ("可逆外观元数据", "保存非破坏调色参数", "faithful"), ("显示设备自适应", "按 HDR/SDR 屏幕生成不同母版", "faithful")],
            ["scene semantics", "color chart priors", "display profile", "camera metadata"], ["专业创作", "旅行", "人像", "直播"], "手机可统一相机、显示、编码和用户风格记忆"),
    cluster("audio_camera", "audio_visual", "声音驱动自动摄影",
            [("单一说话人", "让焦点和构图跟随当前讲话者"), ("多人对话", "自动选择人物、景别和反应镜头"), ("音乐表演", "按节拍、段落和乐器控制镜头"), ("突发事件", "用掌声、碰撞、欢呼或叫声触发缓存")],
            [("声源定位跟焦", "麦克风阵列与人脸轨迹关联", "faithful"), ("对白驱动导播", "根据对话轮次选择构图", "faithful"), ("节拍驱动运镜", "按音乐结构规划运动", "perceptual"), ("声音事件回溯", "从事件前缓存生成精彩片段", "faithful"), ("空间声音虚拟打光", "声源方向控制光效位置", "generative"), ("声画质量联合评分", "联合评估画面和音频精彩度", "faithful")],
            ["microphone array", "audio events", "face tracks", "camera controls"], ["采访", "演唱会", "儿童", "直播"], "手机同时具备麦克风阵列、人脸跟踪、电子变焦和环形缓存"),
    cluster("trusted_generation", "trustworthy_generation", "可信生成与事实保护",
            [("人物身份", "锁定脸、身体、服装和动作事实"), ("文字符号", "锁定招牌、字幕、车牌、文档和商标"), ("空间几何", "锁定建筑、透视、遮挡和物体关系"), ("事件内容", "锁定发生过的动作、参与者和时间顺序")],
            [("保护区生成", "只允许授权区域变化", "generative"), ("世界状态记忆", "跨帧维护对象属性与关系", "generative"), ("生成置信度地图", "输出时空可信度和不确定性", "faithful"), ("关键帧生成传播", "关键帧生成、中间帧受约束传播", "generative"), ("一致性审计", "检测身份、文字、几何和光照变化", "faithful"), ("可逆证据封装", "保存原片、Hash、Mask 和模型版本", "faithful")],
            ["protected masks", "identity", "OCR", "scene graph"], ["新闻", "旅行", "人像", "社交"], "手机端可以在素材离开设备前建立保护区和真实性元数据"),
    cluster("semantic_codec", "codec_system", "语义感知编解码",
            [("人脸手部", "在低码率下优先保护身份和动作"), ("文字屏幕", "优先保护可读性、色彩和刷新纹理"), ("高速主体", "优先保护运动边界和关键纹理"), ("静态背景", "允许更高压缩并保存重建提示")],
            [("语义码率分配", "按内容价值分配比特", "faithful"), ("运动矢量共享", "算法与编码器复用运动信息", "faithful"), ("特征伴随码流", "保存轻量恢复特征", "faithful"), ("可伸缩质量层", "即时版和母版共享码流", "faithful"), ("生成式背景编码", "背景以语义和参考帧重建", "generative"), ("真实性水印", "编码生成区域和处理历史", "faithful")],
            ["encoder vectors", "semantic ROI", "feature sidecar", "bitstream metadata"], ["直播", "长录像", "社交", "端云"], "手机同时控制拍摄算法与硬件编码器，便于共享分析结果"),
    cluster("power_scheduler", "edge_system", "功耗与热稳定录像",
            [("人像增强链", "长时间保持身份、肤色和自然度"), ("夜景恢复链", "在高算力和发热下保持画质稳定"), ("稳定运镜链", "持续复用运动与裁切状态"), ("生成编辑链", "把高风险高成本任务延迟到录后")],
            [("温度感知路由", "按热状态选择网络", "faithful"), ("ROI 动态缩放", "优先处理用户关注区域", "faithful"), ("关键帧大模型", "大模型低频运行并传播结果", "perceptual"), ("代理与母版双路径", "实时轻量、录后高质量", "perceptual"), ("异构流水线调度", "ISP/DSP/NPU/GPU/VPU 分工", "faithful"), ("无感质量降级", "降算力时保持色彩和锐度连续", "faithful")],
            ["thermal state", "NPU load", "ROI", "encoder state"], ["直播", "演唱会", "旅行", "长录像"], "手机系统能获得温度、功耗和异构计算负载并控制整条录像链"),
    cluster("event_sensor", "sensor_fusion", "高速事件与新型传感器",
            [("高速运动", "捕捉普通帧之间的快速边缘变化"), ("频闪光源", "测量 LED/PWM 的时间频率和相位"), ("极暗场景", "在低照中提供稀疏亮度变化信息"), ("相机抖动", "以高时间分辨率估计微小运动")],
            [("事件帧融合", "事件流与 RGB 帧联合重建", "faithful"), ("事件引导去模糊", "用事件约束运动核", "faithful"), ("事件引导插帧", "重建高速中间状态", "faithful"), ("事件防频闪", "依据相位调整逐行亮度", "faithful"), ("事件稳定", "高频运动辅助 EIS", "faithful"), ("事件轨迹艺术化", "将事件流变成可控视觉轨迹", "perceptual")],
            ["event stream", "RGB", "IMU", "row timestamps"], ["运动", "夜景", "演唱会", "车载"], "未来手机可将事件传感器作为低功耗高速辅助通道"),
    cluster("focus_phase", "sensor_fusion", "对焦与光学机构信息",
            [("人脸眼睛", "用 PDAF 和焦点状态判断真实清晰度"), ("高速主体", "预测主体进入焦平面的时刻"), ("多层场景", "维护前中后景的焦点关系"), ("跨镜头焦点", "切镜前后保持物理对焦连续")],
            [("PDAF 引导恢复", "用相位差约束去模糊和深度", "faithful"), ("失焦预测", "预测下一时刻焦点失败", "faithful"), ("焦点轨迹重放", "录后重新设计拉焦路径", "perceptual"), ("遮挡感知跟焦", "遮挡时维持目标身份", "faithful"), ("景深置信度", "显示虚化和深度不确定性", "faithful"), ("焦点与构图联动", "用叙事重点选择焦点和景别", "perceptual")],
            ["PDAF", "lens position", "depth", "subject tracks"], ["人像", "运动", "采访", "演唱会"], "手机可读取对焦位置、PDAF、镜头切换和主体跟踪状态"),
    cluster("privacy_safety", "privacy", "隐私与安全录像",
            [("路人人脸", "可逆匿名化并保护身份信息"), ("儿童敏感区域", "限制上传、生成和共享范围"), ("车牌文档", "自动识别并按规则保护文字"), ("家庭空间", "识别屏幕、照片和私人环境")],
            [("本地隐私 Mask", "敏感区域不离开设备", "faithful"), ("可逆匿名替换", "授权后可恢复原始内容", "generative"), ("分级导出", "不同接收者获得不同版本", "faithful"), ("隐私码率隔离", "敏感区域单独加密或删除", "faithful"), ("生成保护", "禁止模型修改或学习敏感对象", "faithful"), ("审计日志", "记录访问、编辑和导出历史", "faithful")],
            ["face/OCR detection", "secure enclave", "access policy", "metadata"], ["家庭", "儿童", "直播", "公共场所"], "手机安全硬件和本地识别可在编码前执行隐私规则"),
    cluster("concert_capture", "concert", "演唱会与舞台专用录像",
            [("远距离歌手", "恢复主体但避免生成错误面部"), ("舞台 LED", "保护屏幕内容、颜色和高光"), ("观众遮挡", "在举手机和人群遮挡中维持主体"), ("灯光烟雾", "保持光束、烟雾和舞台氛围")],
            [("音频人物关联", "用声音和视觉锁定表演者", "faithful"), ("高光分层 HDR", "人物、屏幕和灯光分别融合", "faithful"), ("远距身份保护恢复", "只恢复可证实结构", "perceptual"), ("遮挡轨迹记忆", "短时遮挡保持主体位置", "faithful"), ("虚拟追光", "按表演者轨迹增加可控灯光", "generative"), ("节拍星芒与光效", "按音乐结构控制镜头效果", "perceptual")],
            ["telephoto", "audio", "subject track", "flicker metadata"], ["演唱会", "舞台", "音乐节", "夜景"], "手机长焦、多麦克风和高动态录像可以组成舞台专用链路"),
    cluster("sports_capture", "sports_broadcast", "体育与动作自动摄影",
            [("球与器械", "跟踪高速小目标和轨迹"), ("运动员", "维持人物、号码、姿态和动作"), ("比赛区域", "理解边界、球门、篮筐和赛道"), ("观众反应", "同步捕捉欢呼和关键反应")],
            [("规则感知跟拍", "用项目规则预测事件", "faithful"), ("轨迹增强", "可视化球、车或运动员路径", "perceptual"), ("事件前缓存", "预测得分和精彩动作", "faithful"), ("自动慢动作", "对关键局部重建高帧率", "perceptual"), ("多机位导播", "多手机自动选择最佳视角", "faithful"), ("战术空间重构", "重建位置关系和运动线路", "generative")],
            ["high-fps", "audio events", "multi-device", "object tracks"], ["球类", "跑步", "骑行", "滑雪"], "手机可分布式部署在多个视角，并共享声音和轨迹"),
    cluster("children_pet", "event_capture", "儿童与宠物不可预测事件",
            [("第一次动作", "捕捉迈步、跳跃、接物等突发瞬间"), ("自然表情", "保留微笑、惊讶、眨眼和互动"), ("快速宠物", "处理毛发、低机位和突然变向"), ("亲子互动", "同时保护多人表情和动作关系")],
            [("行为预测缓存", "预测事件并保留按键前画面", "faithful"), ("声音触发", "叫声、笑声和碰撞触发高帧率", "faithful"), ("最佳状态合成", "从连续帧组合多人最佳表情", "generative"), ("毛发与人脸双路恢复", "分别增强宠物毛发和人物", "perceptual"), ("自动低机位构图", "根据宠物和儿童高度调整裁切", "faithful"), ("成长记忆匹配", "跨日期统一人物和宠物识别", "faithful")],
            ["ring buffer", "audio", "face/pet tracks", "high-fps"], ["儿童", "宠物", "家庭", "户外"], "手机随手拍、环形缓存和本地人物宠物识别适合捕捉不可重复事件"),
    cluster("vehicle_cabin", "material_editing", "车内与移动空间录像",
            [("车窗外景", "处理高速景物、反射和曝光"), ("车内人物", "保护逆光人脸和混合色温"), ("挡风玻璃", "处理雨滴、污渍、HUD 和眩光"), ("道路灯光", "控制夜间车灯、路灯和频闪")],
            [("内外景分层", "分离车窗透射和反射", "faithful"), ("运动 HDR", "车内人物与高速外景分别曝光", "faithful"), ("玻璃介质恢复", "去除雨滴雾气和局部污渍", "faithful"), ("道路稳定", "利用车辆运动约束地平线", "faithful"), ("HUD 保护", "锁定导航和显示文字", "faithful"), ("旅行氛围重构", "受控增强沿途天气和光效", "generative")],
            ["IMU", "GPS", "window masks", "row timestamps"], ["车载", "旅行", "夜景", "直播"], "手机可利用车辆运动、定位、多个摄像头和麦克风记录移动空间"),
    cluster("live_stream", "edge_system", "直播与长时在线录像",
            [("主播人像", "长时稳定身份、肤色、眼镜和背景"), ("多人连麦", "保持不同画面和设备的颜色与响度"), ("移动直播", "在网络、温度和运动变化中稳定质量"), ("商品展示", "保护文字、材质、颜色和细节")],
            [("热稳定增强", "根据温度平滑调整模型", "faithful"), ("网络感知质量", "码率变化时保护关键语义", "faithful"), ("区域增强控制", "主播可调脸、头发、眼镜和背景", "perceptual"), ("低延迟虚拟布光", "轻量深度与法线驱动打光", "perceptual"), ("事实保护生成背景", "锁定人物商品和文字", "generative"), ("直播故障回退", "出现漂移时自动回原始链路", "faithful")],
            ["thermal", "network", "face/product masks", "encoder state"], ["直播", "电商", "采访", "户外"], "手机可联合相机、编码、网络和温度状态做端到端调度"),
    cluster("commerce_product", "relighting", "商品与美食录像",
            [("珠宝金属", "控制小面积锐利高光和反射"), ("玻璃液体", "保护透明、折射、气泡和液面"), ("织物服装", "稳定纹理、颜色、褶皱和亮片"), ("食物表面", "控制油光、蒸汽、颜色和新鲜感")],
            [("材质识别增强", "按材质路由恢复和调色", "faithful"), ("虚拟棚拍布光", "生成主光、轮廓光和背景光", "generative"), ("真实颜色锁定", "用参考色和多帧保持色准", "faithful"), ("微距景深重构", "录后调整焦点和景深", "perceptual"), ("蒸汽液体时序保护", "避免降噪抹除动态细节", "faithful"), ("商品文字保护", "锁定包装、标签和品牌信息", "faithful")],
            ["macro camera", "material masks", "depth", "color reference"], ["电商", "美食", "直播", "广告"], "手机多摄、微距、深度和实时预览降低商品视频制作门槛"),
    cluster("travel_story", "scene_memory", "旅行与城市叙事",
            [("地标建筑", "保持几何、文字和人群关系"), ("自然风景", "控制天空、水面、雾和光照"), ("街道行进", "稳定步行、路人和沿途空间"), ("行程片段", "跨地点形成连贯色彩和叙事")],
            [("净景记忆", "利用真实历史帧移除短时路人", "faithful"), ("空间运镜", "从高分辨率和深度生成小幅机位", "perceptual"), ("天气联动编辑", "天空、地面和人物光照协同", "generative"), ("地标事实保护", "锁定建筑、文字和标志", "faithful"), ("自动旅行镜头组", "按地点和动作组织远中近景", "perceptual"), ("跨日外观连续", "统一不同地点设备和天气", "perceptual")],
            ["GPS", "depth", "scene memory", "OCR"], ["旅行", "城市", "户外", "Vlog"], "手机定位、多摄和持续携带特性适合建立个人旅行场景记忆"),
    cluster("interview_meeting", "audio_visual", "采访会议与演讲",
            [("双人采访", "自动选择说话人和反应镜头"), ("多人圆桌", "理解发言轮次和人物关系"), ("演讲者屏幕", "同时保护人物、PPT 和激光笔"), ("移动采访", "在行走、环境噪声和遮挡中保持构图")],
            [("说话人导播", "声音和人脸轨迹联合切换", "faithful"), ("语义拉焦", "按发言和视线规划焦点", "faithful"), ("屏幕人物双曝光", "分别保护屏幕与人脸", "faithful"), ("字幕安全构图", "预留字幕和竖屏裁切空间", "faithful"), ("自动 B-roll 建议", "识别内容并提示补充镜头", "perceptual"), ("跨机位连续", "多手机同步颜色和时间", "faithful")],
            ["microphone array", "face tracks", "screen detection", "multi-device"], ["采访", "会议", "演讲", "直播"], "手机麦克风、人脸、OCR 和多设备同步可支持轻量自动制作"),
    cluster("accessibility", "capture_system", "无障碍与辅助录像",
            [("手语手部", "优先保护手指、手势和面部表情"), ("低视力观看", "增强关键主体、轮廓和文字"), ("听力辅助", "结合说话人构图和实时字幕安全区"), ("认知辅助", "减少复杂背景并突出关键动作")],
            [("手语 ROI 编码", "优先分配手脸质量", "faithful"), ("语义对比增强", "提高关键对象可见性", "perceptual"), ("字幕人物联合构图", "避免字幕遮挡动作", "faithful"), ("声音事件可视化", "将方向和事件转成画面提示", "perceptual"), ("背景复杂度抑制", "受控弱化非关键区域", "perceptual"), ("个性化辅助配置", "按用户需求保存处理策略", "faithful")],
            ["hand pose", "speech", "OCR", "user profile"], ["教育", "会议", "家庭", "直播"], "手机是个人设备，可结合用户辅助需求和端侧隐私计算"),
    cluster("education_science", "capture_system", "教育实验与科学记录",
            [("白板文档", "保护文字、图表和笔迹过程"), ("实验现象", "记录快速、微弱或周期性变化"), ("显微天文", "多帧提升弱光和细节"), ("操作演示", "同时保护手部、工具和步骤")],
            [("过程分层记录", "保存关键步骤和状态变化", "faithful"), ("高动态文档保护", "人物与屏幕白板分别曝光", "faithful"), ("科学多帧积累", "按运动和噪声模型融合", "faithful"), ("事件时间标注", "自动识别反应或操作节点", "faithful"), ("局部细节放大", "对实验区域持续超分", "perceptual"), ("可复现元数据", "保存曝光、时间、传感器和处理历史", "faithful")],
            ["RAW", "OCR", "macro", "sensor metadata"], ["教育", "实验", "维修", "科普"], "手机便携且能同步记录视频、声音、时间和传感器元数据"),
    cluster("ar_overlay", "spatial_video", "AR 与现实融合录像",
            [("虚拟物体", "保持遮挡、光照和接触关系"), ("空间标注", "把箭头、文字和路径固定在真实位置"), ("人物特效", "让特效随身体、衣服和环境交互"), ("多人共享", "多个设备看到一致的虚实状态")],
            [("深度遮挡合成", "真实与虚拟对象正确遮挡", "faithful"), ("环境光匹配", "虚拟物体继承真实照明", "perceptual"), ("空间锚点稳定", "跨帧和跨设备保持位置", "faithful"), ("物理交互模拟", "接触、碰撞和阴影一致", "generative"), ("录后虚拟元素重排", "在空间工程中重新编辑", "generative"), ("虚实区域标记", "导出对象来源与生成信息", "faithful")],
            ["SLAM", "depth", "body tracking", "multi-device anchors"], ["AR", "社交", "教育", "游戏"], "手机拥有成熟 SLAM、深度、显示和多设备连接能力"),
    cluster("memory_narrative", "event_capture", "个人记忆与长期叙事",
            [("家庭人物", "跨日期保持人物身份和自然外观"), ("地点变化", "记录同一地点的季节和时间演化"), ("成长过程", "自动关联儿童、宠物和重要事件"), ("创作项目", "保持角色、道具、色彩和镜头连续")],
            [("长期身份索引", "本地关联人物和宠物", "faithful"), ("地点时间对齐", "重建相同视角的变化", "faithful"), ("自动镜头日记", "按事件组织短片而非只按日期", "perceptual"), ("连续性检查", "检测服装、物体和场景突变", "faithful"), ("记忆风格重映", "按用户选择统一历史外观", "perceptual"), ("隐私分层分享", "按人物授权生成不同版本", "faithful")],
            ["local identity index", "GPS", "scene retrieval", "timeline"], ["家庭", "旅行", "创作", "成长记录"], "手机长期随身且具有本地相册索引和安全存储"),
    cluster("collaborative_capture", "multi_device", "协同拍摄与群体录像",
            [("同一活动", "多个手机共同覆盖舞台、观众和环境"), ("体育比赛", "多视角覆盖运动员、球和比分区域"), ("旅行同行", "自动合并不同人的视角和声音"), ("采访制作", "主机位、侧机位和环境机位协同")],
            [("时间码同步", "通过音频、UWB 和网络对齐", "faithful"), ("共享主体轨迹", "跨设备维持同一人物和物体 ID", "faithful"), ("自动最佳机位", "按遮挡、清晰度和构图选择", "faithful"), ("跨设备色彩母版", "统一相机和曝光风格", "faithful"), ("空间声场合成", "合并多个麦克风视角", "perceptual"), ("协同三维重构", "利用多视角生成空间录像", "generative")],
            ["UWB", "network time", "multi-camera", "audio sync"], ["活动", "体育", "旅行", "采访"], "手机数量多、网络和 UWB 普及，适合临时组成分布式摄像系统"),
    cluster("social_creation", "trustworthy_generation", "社交创作与自动成片",
            [("单段素材", "从一段录像生成多节奏、多画幅版本"), ("多人合拍", "协调人物构图、表情和镜头分配"), ("产品内容", "生成不同平台的重点版本"), ("旅行活动", "自动组织远景、中景、特写和反应")],
            [("多画幅安全重构", "横竖方形分别规划构图", "faithful"), ("节奏化剪辑", "根据动作和音乐组织片段", "perceptual"), ("自动封面时刻", "选择清晰、表情好且信息完整的帧", "faithful"), ("镜头连接生成", "有限生成过渡并显式标记", "generative"), ("平台质量适配", "按码率和屏幕重新锐化调色", "perceptual"), ("事实一致摘要", "不改变事件顺序和参与者", "faithful")],
            ["audio", "semantic highlights", "safe crop", "platform profile"], ["社交", "旅行", "直播", "电商"], "手机掌握拍摄、相册、编辑和发布的完整闭环"),
    cluster("drone_action", "motion_quality", "无人机与运动相机玩法迁移",
            [("高速穿行", "处理快速视差、滚转和遮挡"), ("地平线轨迹", "在坡度和转弯中控制水平感"), ("主体跟随", "预测人物、车辆和宠物运动"), ("大范围风景", "规划路径、速度和视角变化")],
            [("轨迹平滑迁移", "将无人机路径语法用于手机", "perceptual"), ("地平线模式切换", "区分真实倾斜和意外抖动", "faithful"), ("主体路径预测", "为裁切和跟拍预留空间", "faithful"), ("速度感重构", "通过模糊和视差强化速度", "perceptual"), ("自动绕行镜头", "用深度生成有限环绕", "generative"), ("运动风险提示", "检测碰撞、遮挡和失焦风险", "faithful")],
            ["IMU", "depth", "subject prediction", "GPS"], ["运动", "旅行", "骑行", "宠物"], "手机可借鉴无人机和运动相机的轨迹规划与地平线算法"),
    cluster("cinema_language", "spatial_video", "电影镜头语言辅助",
            [("人物对话", "规划正反打、反应和景别变化"), ("动作场面", "规划跟拍、甩镜和慢动作节点"), ("空间建立", "生成建立镜头、过肩和细节关系"), ("情绪表达", "用焦距、光线、运动和色彩表达情绪")],
            [("运镜语法识别", "识别推拉摇移跟升降环绕", "faithful"), ("镜头意图建议", "根据场景推荐下一镜头", "perceptual"), ("连续性守护", "检查视线、方向和轴线", "faithful"), ("自动镜头组", "从长素材生成镜头组合", "perceptual"), ("受约束镜头补拍", "生成缺失的小幅过渡镜头", "generative"), ("摄影风格记忆", "学习个人构图和运动偏好", "perceptual")],
            ["scene graph", "body gaze", "camera pose", "editing history"], ["短片", "采访", "旅行", "家庭"], "手机可以把拍摄建议、自动控制和录后编辑置于同一系统"),
    cluster("quality_guard", "edge_system", "拍摄质量预测与自救",
            [("对焦曝光", "预测失焦、过曝和暗部不可恢复"), ("镜头介质", "检测遮挡、污渍、结露和手指"), ("时序稳定", "检测闪烁、纹理游走、漂移和跳变"), ("资源状态", "检测温度、存储、网络和电量风险")],
            [("录前风险预警", "在不可逆失败前提示", "faithful"), ("自动参数自救", "调整曝光、帧率、镜头或模型", "faithful"), ("失败片段标记", "为录后重算记录问题区间", "faithful"), ("替代镜头切换", "主镜头失败时无感切换", "faithful"), ("恢复可行性预测", "判断录后是否可修复", "faithful"), ("用户意图保护", "降级时优先保持核心效果", "faithful")],
            ["AF/AE state", "quality metrics", "thermal", "storage/network"], ["所有录像", "直播", "长录像", "重要事件"], "手机系统可以同时观察成像质量和资源状态并实时控制链路"),
    cluster("multi_spectral", "sensor_fusion", "多光谱与辅助成像",
            [("近红外人像", "在低照中提供结构但保护肤色"), ("热信息", "辅助夜间主体发现和温度可视化"), ("偏振信息", "分离反射、天空和材质高光"), ("环境传感", "结合光谱、天气和空间数据")],
            [("辅助通道融合", "只在低置信区域使用辅助信息", "faithful"), ("跨光谱颜色恢复", "从可见光约束真实颜色", "faithful"), ("反射偏振控制", "利用偏振差分抑制反光", "faithful"), ("热目标提示", "低照中提示人物动物和设备", "perceptual"), ("多模态分层录像", "保存可见光和辅助层", "faithful"), ("科学可视化模式", "将不可见信息转成标记效果", "perceptual")],
            ["RGB", "NIR", "thermal", "polarization"], ["夜景", "户外", "科研", "安全"], "未来手机可以通过辅助传感器或外设获得多模态成像"),
]


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "idea"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def make_legacy_ideas(rows: list[dict]) -> list[dict]:
    ideas = []
    for row in rows:
        ideas.append({
            "idea_id": f"LEGACY-{row['id']}",
            "legacy_id": row["id"],
            "name_zh": row["name_zh"],
            "family": row["family"],
            "family_zh": row["family_zh"],
            "idea_cluster": "legacy_112",
            "cluster_zh": "既有 112 条机会库",
            "source_layer": "legacy_112",
            "user_effect": row.get("notes", "保留既有录像后处理方向"),
            "core_mechanism": "; ".join(row.get("algorithm_family", [])),
            "mobile_unique_value": "继承已有机会库中的手机录像链路分析",
            "input_signals": row.get("input_signals", []),
            "scenarios": row.get("scenarios", []),
            "default_truth": row.get("truth_boundary", "perceptual"),
            "temporal_span": "short_to_long",
            "risks": row.get("failure_modes", []),
            "tags": ["legacy", row.get("video_mode", "offline_device"), row.get("priority", "P2")],
            "status": "idea_only_with_legacy_evidence_pointer",
        })
    return ideas


def make_prior_ideas() -> list[dict]:
    ideas = []
    for index, (name, family, description) in enumerate(PRIOR_IDEAS, 1):
        ideas.append({
            "idea_id": f"PRIOR-{index:03d}",
            "legacy_id": "",
            "name_zh": name,
            "family": family,
            "family_zh": FAMILY_ZH[family],
            "idea_cluster": "prior_brainstorm",
            "cluster_zh": "此前明确提出的重点方向",
            "source_layer": "prior_brainstorm",
            "user_effect": description,
            "core_mechanism": description,
            "mobile_unique_value": "保留前序讨论中的关键录像创意，作为后续组合和变体入口",
            "input_signals": ["video", "temporal metadata", "semantic analysis"],
            "scenarios": ["通用录像"],
            "default_truth": "perceptual",
            "temporal_span": "short_to_long",
            "risks": ["时序不一致", "端侧资源", "真实性边界"],
            "tags": ["prior_example", "must_keep"],
            "status": "idea_only",
        })
    return ideas


def make_native_ideas() -> list[dict]:
    ideas = []
    sequence = 1
    for item in CLUSTERS:
        for target_name, target_effect in item["targets"]:
            for mechanism_name, mechanism_effect, truth in item["mechanisms"]:
                name = f"{target_name}：{mechanism_name}录像"
                ideas.append({
                    "idea_id": f"NATIVE-{sequence:04d}",
                    "legacy_id": "",
                    "name_zh": name,
                    "family": item["family"],
                    "family_zh": FAMILY_ZH[item["family"]],
                    "idea_cluster": item["key"],
                    "cluster_zh": item["title"],
                    "source_layer": "new_native_idea",
                    "user_effect": f"围绕{target_name}，{target_effect}；通过{mechanism_name}实现{mechanism_effect}。",
                    "core_mechanism": f"{mechanism_name}：{mechanism_effect}。需要跨帧维护目标状态、遮挡关系和质量置信度。",
                    "mobile_unique_value": item["mobile_value"],
                    "input_signals": item["signals"],
                    "scenarios": item["scenarios"],
                    "default_truth": truth,
                    "temporal_span": item["temporal_span"],
                    "risks": ["时序闪烁", "遮挡错误", "用户控制复杂度", "端侧功耗"],
                    "tags": [item["key"], slug(target_name), slug(mechanism_name), "mobile_video"],
                    "status": "idea_only",
                })
                sequence += 1
    return ideas


def variant_note(axis: str, value_label: str, detail: str, idea: dict) -> str:
    return f"把“{idea['name_zh']}”设计为{value_label}版本：{detail}。基础用户效果保持不变，变化的是实现约束与交付方式。"


def make_variants(ideas: list[dict]) -> list[dict]:
    variants = []
    sequence = 1
    for idea in ideas:
        for axis, axis_info in AXES.items():
            for value, value_label, detail in axis_info["values"]:
                variants.append({
                    "variant_id": f"VAR-{sequence:06d}",
                    "base_idea_id": idea["idea_id"],
                    "base_name_zh": idea["name_zh"],
                    "family_zh": idea["family_zh"],
                    "idea_cluster": idea["idea_cluster"],
                    "variant_axis": axis,
                    "variant_axis_zh": axis_info["label"],
                    "variant_value": value,
                    "variant_value_zh": value_label,
                    "variant_name_zh": f"{idea['name_zh']} - {value_label}版",
                    "implementation_note": variant_note(axis, value_label, detail, idea),
                    "base_truth": idea["default_truth"],
                    "source_layer": idea["source_layer"],
                    "status": "idea_variant_only",
                })
                sequence += 1
    return variants


def validate(ideas: list[dict], variants: list[dict], legacy_count: int) -> dict:
    idea_ids = [row["idea_id"] for row in ideas]
    variant_ids = [row["variant_id"] for row in variants]
    required = ["动态星芒", "打光", "计算底片", "对象级快门", "多手机", "声音", "Event", "生成"]
    searchable = "\n".join(row["name_zh"] + " " + row["user_effect"] for row in ideas)
    axis_counts = Counter(row["variant_axis"] for row in variants)
    expected_per_axis = {axis: len(info["values"]) * len(ideas) for axis, info in AXES.items()}
    report = {
        "idea_ids_unique": len(idea_ids) == len(set(idea_ids)),
        "variant_ids_unique": len(variant_ids) == len(set(variant_ids)),
        "legacy_count": sum(row["source_layer"] == "legacy_112" for row in ideas),
        "legacy_expected": legacy_count,
        "legacy_complete": sum(row["source_layer"] == "legacy_112" for row in ideas) == legacy_count,
        "variant_references_valid": {row["base_idea_id"] for row in variants}.issubset(set(idea_ids)),
        "axis_counts_match": all(axis_counts[axis] == count for axis, count in expected_per_axis.items()),
        "required_direction_hits": {term: term.lower() in searchable.lower() for term in required},
    }
    if not all(value for key, value in report.items() if isinstance(value, bool)):
        raise ValueError(f"Idea universe validation failed: {report}")
    if not all(report["required_direction_hits"].values()):
        raise ValueError(f"Missing required directions: {report['required_direction_hits']}")
    return report


def build_stats(ideas: list[dict], variants: list[dict], validation: dict) -> dict:
    return {
        "status": "idea_only_not_product_or_paper_claim",
        "counts": {
            "core_ideas": len(ideas),
            "variants": len(variants),
            "legacy_ideas": sum(x["source_layer"] == "legacy_112" for x in ideas),
            "prior_brainstorm": sum(x["source_layer"] == "prior_brainstorm" for x in ideas),
            "new_native_ideas": sum(x["source_layer"] == "new_native_idea" for x in ideas),
            "variant_axes": len(AXES),
            "variant_values": sum(len(x["values"]) for x in AXES.values()),
        },
        "by_source_layer": Counter(x["source_layer"] for x in ideas),
        "by_family": Counter(x["family_zh"] for x in ideas),
        "by_cluster": Counter(x["cluster_zh"] for x in ideas),
        "by_truth": Counter(x["default_truth"] for x in ideas),
        "variants_by_axis": Counter(x["variant_axis_zh"] for x in variants),
        "validation": validation,
    }


def markdown_report(ideas: list[dict], variants: list[dict], stats: dict) -> str:
    lines = [
        "# 手机录像后处理 IDEA 全量宇宙",
        "",
        "日期：2026-08-27",
        "",
        "> 本文档是创意数据库，不是量产功能、论文结论或性能承诺。旧机会、此前讨论方向、新增创意和实现变体分别标记。",
        "",
        "## 1. 总览",
        "",
        f"- 基础 IDEA：{len(ideas):,} 条。",
        f"- 单轴实现变体：{len(variants):,} 条。",
        f"- 既有机会保留：{stats['counts']['legacy_ideas']:,} 条。",
        f"- 此前重点方向：{stats['counts']['prior_brainstorm']:,} 条。",
        f"- 新增原生创意：{stats['counts']['new_native_ideas']:,} 条。",
        f"- 变体轴：{stats['counts']['variant_axes']} 个，共 {stats['counts']['variant_values']} 个单轴取值。",
        "",
        "基础 IDEA 改变用户效果、处理对象、手机输入信号、录像链路或交互方式；变体只改变处理阶段、真实性、输入、场景、时间规格、处理范围或交付形态。",
        "",
        "## 2. 变体轴",
        "",
    ]
    for axis, info in AXES.items():
        labels = "、".join(value_label for _, value_label, _ in info["values"])
        lines.append(f"- **{info['label']}**（`{axis}`）：{labels}。")
    lines.extend(["", "## 3. 基础 IDEA 全量清单", ""])
    grouped: dict[str, list[dict]] = defaultdict(list)
    for idea in ideas:
        grouped[f"{idea['source_layer']}|{idea['cluster_zh']}"] .append(idea)
    current_layer = None
    layer_labels = {
        "legacy_112": "既有 112 条机会",
        "prior_brainstorm": "此前明确提出的重点方向",
        "new_native_idea": "新增原生录像创意",
    }
    for group_key, rows in grouped.items():
        layer, cluster_name = group_key.split("|", 1)
        if layer != current_layer:
            lines.extend([f"### {layer_labels[layer]}", ""])
            current_layer = layer
        lines.extend([f"#### {cluster_name}", ""])
        for row in rows:
            signals = " / ".join(row["input_signals"])
            scenes = " / ".join(row["scenarios"])
            lines.append(f"- **{row['idea_id']}｜{row['name_zh']}**：{row['user_effect']} 输入：{signals}；场景：{scenes}；默认边界：`{row['default_truth']}`。")
        lines.append("")
    lines.extend([
        "## 4. 变体全量文件",
        "",
        "全部单轴变体逐条写入 `metadata/idea_universe/idea_variants.jsonl`、Excel 的 `Variants` 工作表，以及独立的 Markdown 变体清单。",
        "",
        "## 5. 使用方式",
        "",
        "可以先按能力族或场景筛选基础 IDEA，再用变体轴选择实时/录后、忠实/生成、单摄/多传感器、帧率、处理范围和交付形态。需要更大规模时，可继续对两个或三个轴做组合，但不建议直接生成七轴笛卡尔积。",
        "",
    ])
    return "\n".join(lines)


def variants_markdown(variants: list[dict]) -> str:
    lines = [
        "# 手机录像后处理 IDEA 单轴变体全量清单",
        "",
        "日期：2026-08-27",
        "",
        "> 每条记录是某个基础 IDEA 的实现版本，不等同于新的基础发明。",
        "",
    ]
    current_base = None
    for row in variants:
        if row["base_idea_id"] != current_base:
            lines.extend([f"## {row['base_idea_id']}｜{row['base_name_zh']}", ""])
            current_base = row["base_idea_id"]
        lines.append(f"- **{row['variant_id']}｜{row['variant_axis_zh']}｜{row['variant_value_zh']}**：{row['implementation_note']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=r"D:\Repository\ReadPaper\daily\20260826_后处理调研")
    args = parser.parse_args()
    root = Path(args.root)
    legacy_rows = read_jsonl(root / "metadata" / "opportunities.jsonl")
    ideas = make_legacy_ideas(legacy_rows) + make_prior_ideas() + make_native_ideas()
    variants = make_variants(ideas)
    validation = validate(ideas, variants, len(legacy_rows))
    stats = build_stats(ideas, variants, validation)

    metadata_dir = root / "metadata" / "idea_universe"
    report_dir = root / "report"
    write_jsonl(metadata_dir / "core_ideas.jsonl", ideas)
    write_jsonl(metadata_dir / "idea_variants.jsonl", variants)
    (metadata_dir / "idea_universe_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "手机录像后处理_IDEA全量宇宙_20260827.md").write_text(
        markdown_report(ideas, variants, stats), encoding="utf-8"
    )
    (report_dir / "手机录像后处理_IDEA变体全量_20260827.md").write_text(
        variants_markdown(variants), encoding="utf-8"
    )
    print(json.dumps(stats["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
