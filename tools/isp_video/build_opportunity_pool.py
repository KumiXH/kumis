"""Create a broad, evidence-linked opportunity pool for mobile video post-processing."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\Repository\ReadPaper\daily\20260826_后处理调研")
OUT = ROOT / "metadata" / "opportunities.jsonl"
MATRIX = ROOT / "metadata" / "opportunity_evidence_matrix.json"
NOTE = ROOT / "notes" / "opportunity_pool_screening.md"

FAMILIES = [
    ("computational_optics", "计算光学与虚拟镜头", [
        ("动态星芒方向", "Dynamic starburst", "夜景、车灯、演唱会", "把高亮点检测和可控光学核参数化，迁移到时序视频", "perceptual", "E5", ["official_apple_cinematic_mode"]),
        ("电影眩光与鬼影仿真", "Cinematic flare and ghosting", "夜景、逆光、城市灯光", "以光源轨迹和镜头姿态驱动跨帧 flare，而不是逐帧贴图", "perceptual", "E5", ["local_fluxir"]),
        ("动态柔焦", "Temporal soft focus", "人像、婚礼、夜景", "由深度和运动边界生成可控空间频率衰减", "perceptual", "E5", ["official_google_cinematic_blur"]),
        ("旋焦焦外", "Swirl bokeh", "创作、短视频", "用深度分层和光心估计生成连续旋转焦外", "generative", "E5", ["official_google_cinematic_blur"]),
        ("猫眼与边缘焦外", "Cat-eye bokeh", "夜景人像、城市", "建立离轴点扩散函数的空间变化并稳定光源形状", "perceptual", "E5", ["official_google_cinematic_blur"]),
        ("可变光圈叶片", "Virtual aperture blades", "电影化录像", "由语义/深度控制虚拟 aperture 形状和散景边界", "perceptual", "E5", ["official_google_cinematic_blur"]),
        ("镜头呼吸校正", "Lens breathing correction", "拉焦、视频人像", "估计焦点变化造成的视场变化并做几何补偿", "faithful", "E5", ["official_apple_cinematic_mode"]),
        ("雨滴与镜头污渍编辑", "Lens droplet removal", "雨天、户外", "利用时序背景和镜头污染 mask 做在线抑制或录后清除", "faithful", "E5", ["official_davinci_magic_mask"]),
    ]),
    ("relighting", "光照重构与可控布光", [
        ("人像主光方向重定向", "Portrait key-light steering", "自拍视频、直播", "从人脸法线/光照估计出主光，再以时序 latent rendering 重定向", "generative", "E5", ["local_fluxir"]),
        ("轮廓光自动生成", "Automatic rim light", "逆光、舞台", "利用人像 mask 和背景分离生成受控边缘光", "perceptual", "E5", ["official_capcut_video_cutout"]),
        ("眼神光恢复", "Catchlight restoration", "人像、采访", "面部 ROI 内建立眼睛高光的亮度与位置先验", "perceptual", "E5", ["local_authface"]),
        ("多人独立打光", "Multi-person independent relighting", "多人合影、直播", "每个主体独立估计 light transport，再合成共享环境光", "generative", "E5", ["official_capcut_video_cutout"]),
        ("环境光颜色重建", "Ambient color reconstruction", "霓虹、室内", "估计环境 illumination field 并稳定跨帧色彩映射", "perceptual", "E5", ["local_fluxir"]),
        ("舞台追光", "Stage spotlight following", "演唱会、表演", "主体 tracking 与光源轨迹联合，形成可编辑虚拟追光", "generative", "E5", ["official_dji_subject_tracking"]),
        ("时间变化打光", "Time-varying relighting", "短视频、MV", "由时间轴控制太阳/灯光方向并保证阴影时序一致", "generative", "E5", ["local_fluxir"]),
        ("负补光与局部压暗", "Semantic negative fill", "人像、逆光", "按脸部/服装/背景区域做可控减光而非全局调色", "perceptual", "E5", ["official_davinci_magic_mask"]),
    ]),
    ("depth_focus", "景深、焦点与空间感", [
        ("录后改光圈", "Post-capture aperture", "人像、旅行", "深度估计加边界修复，支持同一视频多种景深输出", "generative", "E5", ["official_google_cinematic_blur"]),
        ("多人自动拉焦", "Multi-subject focus pull", "采访、多人对话", "基于视线、语音和主体重要性生成焦点轨迹", "perceptual", "E5", ["official_sony_real_time_tracking"]),
        ("主体/背景独立景深", "Subject-background depth control", "Vlog、短视频", "人像 mask 与深度联合控制，避免头发边界发糊", "perceptual", "E5", ["local_tiger"]),
        ("虚拟移轴", "Virtual tilt-shift", "建筑、城市", "用深度平面模拟倾斜焦平面并稳定相机运动", "perceptual", "E5", ["official_google_cinematic_blur"]),
        ("焦点转移预览", "Focus-transition preview", "电影化录像", "预测焦点轨迹和景深变化，实时生成预览", "perceptual", "E5", ["official_apple_cinematic_mode"]),
        ("微机位视差", "Micro-parallax camera move", "静态人物、旅行", "从单摄深度和背景分层生成有限视差运动", "generative", "E5", ["local_fluxsr"]),
        ("遮挡感知焦点切换", "Occlusion-aware focus pull", "多人、复杂前景", "通过 occlusion graph 约束焦点和 blur mask 的过渡", "faithful", "E5", ["official_sony_real_time_tracking"]),
        ("空间层级调色", "Depth-layer grading", "风景、城市", "按距离层分配对比度、饱和度、雾化和清晰度", "perceptual", "E5", ["official_davinci_magic_mask"]),
    ]),
    ("temporal_exposure", "快门、时间与运动轨迹", [
        ("语义长曝光", "Semantic long exposure", "车流、瀑布、光轨", "主体与背景使用不同时间积分策略，主体保持清晰", "generative", "E5", ["local_flashvsr"]),
        ("局部运动拖影", "Localized motion trails", "舞蹈、运动", "由运动 mask 控制拖影长度和衰减", "perceptual", "E5", ["local_flashvsr"]),
        ("人物清晰背景拖影", "Sharp subject with streaked background", "跑步、骑行", "用相机运动与主体运动分解构造差异化 motion blur", "perceptual", "E5", ["official_dji_rocksteady"]),
        ("频闪节奏编辑", "Flicker rhythm editor", "音乐、舞台", "检测/生成与音频节拍同步的受控曝光变化", "generative", "E5", ["official_blackmagic_camera_app"]),
        ("事件触发慢动作", "Event-triggered slow motion", "运动、儿童、宠物", "用环形缓存保存事件前后帧并局部插帧", "faithful", "E5", ["official_dji_subject_tracking"]),
        ("光绘轨迹", "Light-paint trail", "夜景、创作", "对高亮运动物体做轨迹累积并保持背景稳定", "perceptual", "E5", ["local_flashvsr"]),
        ("快门角风格模拟", "Shutter-angle emulation", "电影化录像", "按物体类别控制运动模糊核，模拟不同 shutter angle", "perceptual", "E5", ["official_sony_s_cinetone"]),
        ("曝光轨迹平滑", "Exposure trajectory smoothing", "室内外切换", "预测场景亮度和传感器 AE 轨迹，减少 exposure breathing", "faithful", "E5", ["official_google_video_boost"]),
    ]),
    ("virtual_camera", "虚拟摄影机与智能运镜", [
        ("自动构图重裁切", "Auto-reframing", "Vlog、直播", "主体检测、姿态和语音事件驱动动态 crop", "faithful", "E5", ["official_insta360_me_mode"]),
        ("数字滑轨", "Digital dolly", "旅行、静物", "利用高分辨率采集和深度生成受限机位移动", "generative", "E5", ["local_fluxsr"]),
        ("数字环绕", "Virtual orbit shot", "人像、产品", "用单目/多摄深度生成小角度环绕视角", "generative", "E5", ["local_fluxir"]),
        ("自动推拉镜头", "Semantic push-in", "演讲、剧情", "按说话人、视线和事件自动调整数字焦段", "faithful", "E5", ["official_dji_subject_tracking"]),
        ("Dolly zoom 模拟", "Virtual dolly zoom", "创作、短视频", "联合改变虚拟视场和背景尺度，保持主体尺度", "generative", "E5", ["official_google_cinematic_blur"]),
        ("无人机运动风格模拟", "Drone-move emulation", "旅行、户外", "从手持视频估计相机姿态并生成平滑轨迹", "generative", "E5", ["official_dji_active_track"]),
        ("斯坦尼康稳定风格", "Steadicam style", "Vlog、纪录", "稳定低频漂移，保留高频手部运动和主体运动", "perceptual", "E5", ["official_gopro_hypersmooth"]),
        ("语音驱动取景", "Speech-driven framing", "采访、直播", "ASR/声源定位辅助主体选取、景别和构图", "faithful", "E5", ["official_blackmagic_camera_app"]),
    ]),
    ("multi_camera", "多摄融合与连续变焦", [
        ("无感切镜曝光连续", "Seamless exposure lens switch", "手机连续变焦", "联合 AE、AWB、色彩和噪声状态做切镜预热", "faithful", "E5", ["official_apple_cinematic_mode"]),
        ("跨摄像头色彩匹配", "Cross-camera color matching", "录像、旅行", "用在线 color transform 和时序统计消除镜头色差", "faithful", "E5", ["official_blackmagic_gen5_color"]),
        ("长焦细节/主摄稳定融合", "Tele-detail and wide-stability fusion", "远景、人像", "长焦提供细节，主摄提供稳定和低照度参考", "faithful", "E5", ["official_samsung_super_steady"]),
        ("双摄联合去模糊", "Dual-camera deblurring", "夜景、运动", "利用不同焦段和曝光的互补观测联合复原", "faithful", "E5", ["local_flashvsr"]),
        ("多摄景深融合", "Multi-camera depth fusion", "人像、视频", "立体/多摄深度指导前景边界和虚拟景深", "perceptual", "E5", ["official_google_cinematic_blur"]),
        ("切镜前后风格延续", "Look continuity across lenses", "电影化录像", "保持 LUT、颗粒、flare 和肤色的跨镜头连续性", "perceptual", "E5", ["official_panasonic_real_time_lut"]),
        ("跨摄像头运动矢量共享", "Shared motion field across cameras", "运动录像", "共享 IMU、光流和主体轨迹，减少切镜时运动不一致", "faithful", "E5", ["official_dji_rocksteady"]),
        ("异步多摄补帧", "Asynchronous multi-camera frame synthesis", "高帧率录像", "用主摄和辅摄在时间上的互补缓解丢帧", "faithful", "E5", ["local_flashvsr"]),
    ]),
    ("motion_quality", "智能稳定与运动画质", [
        ("主体运动与相机抖动分离", "Camera/subject motion separation", "运动、人像", "分别估计 camera pose 和 non-rigid subject motion", "faithful", "E5", ["official_gopro_hypersmooth"]),
        ("滚动快门时序校正", "Rolling-shutter correction", "运动、快速摇摄", "使用 IMU/行曝光模型校正逐行几何变形", "faithful", "E5", ["local_flashvsr"]),
        ("稳定与去模糊联合", "Joint stabilization and deblurring", "夜景手持", "先在运动补偿坐标系估计 blur，再回到输出坐标", "faithful", "E5", ["local_flashvsr"]),
        ("地平线与建筑垂线锁定", "Horizon and vertical-line lock", "旅行、建筑", "从 IMU 和场景线结构联合优化裁切", "faithful", "E5", ["official_dji_horizon_steady"]),
        ("保留有意运动的稳定", "Intent-aware stabilization", "运动创作", "区分手抖与有意跟拍，保留构图运动", "perceptual", "E5", ["official_gopro_horizon_lock"]),
        ("局部非刚性稳定", "Local non-rigid stabilization", "人像、舞蹈", "背景稳定而人体不被拉扯，支持局部网格变形", "faithful", "E5", ["local_tiger"]),
        ("运动主体纹理锚定", "Texture anchoring for moving subjects", "宠物、儿童", "用特征传播和关键帧抑制纹理 crawl", "faithful", "E5", ["local_svfr"]),
        ("视频质量实时守护", "Real-time quality guardian", "所有录像", "预测失焦、过曝、遮挡、抖动和镜头污渍并提示用户", "faithful", "E5", ["official_sony_real_time_tracking"]),
    ]),
    ("night_hdr", "夜景、HDR 与复杂光源", [
        ("视频夜视", "Video Night Sight", "夜景、室内", "多帧对齐、时序降噪和局部曝光重建", "faithful", "E5", ["official_google_video_boost"]),
        ("舞台高亮保护", "Stage-highlight protection", "演唱会、舞台", "对灯光/屏幕区域做 highlight roll-off 和时序约束", "faithful", "E5", ["official_google_video_boost"]),
        ("局部 HDR 曝光轨迹", "Local HDR exposure trajectory", "逆光、城市", "前景人物和背景亮部分别保持稳定的 tone mapping", "faithful", "E5", ["official_apple_photographic_styles"]),
        ("霓虹颜色稳定", "Neon color stability", "夜景城市", "高饱和点光源检测与颜色记忆避免跨帧跳变", "faithful", "E5", ["official_google_video_boost"]),
        ("烟花与灯牌去闪烁", "Firework and signboard deflicker", "节庆、演唱会", "按光源类别建模周期变化，区别真实闪烁和算法闪烁", "faithful", "E5", ["local_flashvsr"]),
        ("暗部彩噪时序抑制", "Chrominance noise stabilization", "夜景录像", "色度噪声建模、运动补偿和低频颜色锁定", "faithful", "E5", ["local_flashvsr"]),
        ("逆光人像恢复", "Backlit portrait recovery", "日落、窗边", "人脸/人体区域独立曝光与细节恢复", "perceptual", "E5", ["local_authface"]),
        ("跨场景 HDR 过渡", "Cross-scene HDR transition", "室内外切换", "曝光/色调映射状态机避免切换瞬间呼吸", "faithful", "E5", ["official_google_video_boost"]),
    ]),
    ("portrait_identity", "人像细节与身份一致性", [
        ("人像分区细节恢复", "Region-aware portrait restoration", "自拍视频、直播", "脸、头发、眼睛、牙齿、服装采用不同增强策略", "perceptual", "E5", ["local_tiger"]),
        ("视频身份锚定", "Temporal identity anchoring", "人像录像", "用 identity embedding 和关键帧约束避免五官漂移", "faithful", "E5", ["local_authface"]),
        ("眼镜反光抑制", "Eyeglass glare suppression", "室内人像", "眼镜区域反射分离并利用邻近帧恢复眼睛结构", "perceptual", "E5", ["local_authface"]),
        ("头发边界恢复", "Hair-boundary restoration", "人像虚化/打光", "毛发 alpha、深度和纹理联合建模", "perceptual", "E5", ["local_tiger"]),
        ("妆容与肤质控制", "Makeup and skin-texture control", "短视频、直播", "在身份保持约束下控制皮肤高频和色彩风格", "perceptual", "E5", ["local_authface"]),
        ("视线轻微校正", "Subtle gaze correction", "自拍、会议", "只修正视线方向的低幅度几何变化，保持表情一致", "generative", "E5", ["local_heads_up"]),
        ("闭眼/眨眼质量修复", "Blink-aware restoration", "人像视频", "利用前后帧和身份特征避免闭眼帧产生错误眼睛", "faithful", "E5", ["local_svfr"]),
        ("多人身份分离增强", "Multi-person identity-separated enhancement", "合影、直播", "按 track ID 维护独立的 enhancement state", "faithful", "E5", ["local_tiger"]),
    ]),
    ("scene_editing", "环境清理与场景重构", [
        ("路人时序移除", "Temporal passerby removal", "旅行、景点", "背景板估计、track mask 与时序 inpainting", "generative", "E5", ["official_adobe_content_aware_fill_video"]),
        ("反光分层编辑", "Reflection-layer editing", "玻璃、橱窗、车窗", "估计反射与透射层并允许独立调节", "generative", "E5", ["local_fluxir"]),
        ("屏幕摩尔纹抑制", "Screen moire suppression", "拍屏、直播", "频域抑制与屏幕几何/刷新率先验联合", "faithful", "E5", ["local_flashvsr"]),
        ("电线和污点移除", "Wire and blemish removal", "城市、风景", "目标检测/分割后做跨帧背景修复", "generative", "E5", ["official_davinci_object_removal"]),
        ("天空替换视频化", "Temporal sky replacement", "旅行、城市", "天空分割、天气参数和地面光照联动", "generative", "E5", ["official_capcut_video_cutout"]),
        ("天气与季节编辑", "Weather and season editing", "旅行、创作", "控制雨雪雾和色温，并约束物体运动一致性", "generative", "E5", ["local_fluxir"]),
        ("背景延展适配横竖屏", "Background extension for reframing", "短视频裁切", "基于场景结构延展画外区域，支持回退原始画面", "generative", "E5", ["local_fluxsr"]),
        ("前景遮挡短时补全", "Short-term occlusion completion", "人像、运动", "用历史帧和生成模型补全被短暂遮挡区域", "generative", "E5", ["local_tiger"]),
    ]),
    ("color_science", "专业影像与色彩科学", [
        ("语义分区 LUT", "Semantic local LUT", "专业创作、人像", "人脸、天空、植被、灯光使用不同颜色变换", "perceptual", "E5", ["official_panasonic_real_time_lut"]),
        ("跨设备肤色匹配", "Cross-device skin-tone matching", "多机位、换镜", "以肤色统计和 reference look 做连续色彩校正", "faithful", "E5", ["official_blackmagic_gen5_color"]),
        ("胶片颗粒物理化", "Physically modulated film grain", "电影化录像", "颗粒随亮度、ISO、运动和时间稳定变化", "perceptual", "E5", ["official_sony_s_cinetone"]),
        ("动态晕光", "Dynamic halation", "逆光、夜景", "由高亮区域和镜头姿态驱动跨帧 halation", "perceptual", "E5", ["official_sony_s_cinetone"]),
        ("曝光响应曲线迁移", "Exposure-response transfer", "电影风格、Log", "从参考相机/胶片估计 tone response 并在线应用", "perceptual", "E5", ["official_blackmagic_gen5_color"]),
        ("镜头个性化仿真", "Lens-character emulation", "专业创作", "联合焦外、flare、色散和边缘锐度生成镜头风格", "perceptual", "E5", ["official_panasonic_real_time_lut"]),
        ("多段录像风格连续", "Look continuity across clips", "Vlog、多机位", "跨片段维护颜色、颗粒和曝光状态", "faithful", "E5", ["official_blackmagic_gen5_color"]),
        ("可逆风格元数据", "Reversible look metadata", "专业后期", "保存原片与参数化 look，支持非破坏式回退", "faithful", "E5", ["official_blackmagic_camera_app"]),
    ]),
    ("audio_visual", "声音驱动的录像能力", [
        ("说话人自动构图", "Speaker-aware framing", "采访、会议、直播", "ASR/声源定位与人脸 tracking 联合调整构图", "faithful", "E5", ["official_blackmagic_camera_app"]),
        ("声音驱动跟焦", "Audio-driven focus", "采访、舞台", "声源方向和说话人身份辅助焦点选择", "faithful", "E5", ["official_sony_real_time_tracking"]),
        ("音乐节拍运镜", "Beat-synchronized camera motion", "MV、短视频", "节拍驱动数字推拉、灯光和速度变化", "generative", "E5", ["official_dji_subject_tracking"]),
        ("事件声触发高帧率缓存", "Audio-triggered high-frame-rate buffer", "体育、儿童", "检测掌声/进球/笑声触发前后帧保存", "faithful", "E5", ["official_dji_active_track"]),
        ("多说话人画面调度", "Multi-speaker shot scheduling", "访谈、播客", "按说话人轮换生成单人/双人景别", "faithful", "E5", ["official_insta360_me_mode"]),
        ("声画注意力可视化", "Audio-visual attention guide", "拍摄辅助", "提示画面主体与收音主体不一致", "faithful", "E5", ["official_blackmagic_camera_app"]),
        ("环境音驱动色彩/光效", "Ambient-sound-driven look", "现场、音乐", "用环境声类别控制色彩和可选创作光效", "generative", "E5", ["official_capcut_video_cutout"]),
        ("对白驱动节奏剪辑", "Dialogue-driven pacing", "Vlog、访谈", "基于语义停顿和情绪生成镜头速度与裁切建议", "perceptual", "E5", ["official_final_cut_object_tracker"]),
    ]),
    ("generative_video", "生成式叙事与内容重构", [
        ("有限视角扩展", "Constrained novel-view extension", "旅行、产品", "基于深度/轨迹生成小范围画外视角", "generative", "E5", ["local_fluxir"]),
        ("遮挡区域回填", "Occlusion-aware generative fill", "人物、运动", "用历史帧、mask 和条件生成短时回填", "generative", "E5", ["local_tiger"]),
        ("真实天气增强", "Controlled weather augmentation", "旅行、MV", "加入雨、雪、雾但保持主体和相机运动", "generative", "E5", ["local_fluxir"]),
        ("时间段迁移", "Time-of-day translation", "日景夜景创作", "控制太阳方向、色温和阴影的时序变化", "generative", "E5", ["local_fluxir"]),
        ("视频内容延展", "Video outpainting", "横竖屏、构图", "扩展画面边界并维护主体运动轨迹", "generative", "E5", ["local_fluxsr"]),
        ("生成式镜头切换", "Generative shot transition", "短视频、MV", "在不同焦段/视角间生成连续过渡片段", "generative", "E5", ["local_fluxir"]),
        ("可控风格化视频", "Controllable video stylization", "短视频、创作", "以参考图/文本控制颜色、材质和光效", "generative", "E5", ["local_dit"]),
        ("事实帧/生成帧分层输出", "Fact/generation layer output", "专业创作与可信视频", "保存生成 mask、源帧和可逆参数", "faithful", "E5", ["local_fluxir"]),
    ]),
    ("capture_assistance", "拍摄辅助与质量守护", [
        ("录制前环形缓存", "Pre-roll ring buffer", "运动、儿童、宠物", "保留按下录像前的若干秒以捕获事件", "faithful", "E5", ["official_dji_subject_tracking"]),
        ("失焦预测", "Defocus prediction", "所有录像", "预测未来数帧失焦并提示或调整 AF", "faithful", "E5", ["official_sony_real_time_tracking"]),
        ("过曝风险预测", "Overexposure risk prediction", "舞台、逆光", "结合场景语义预测高亮饱和和 AE 轨迹", "faithful", "E5", ["official_google_video_boost"]),
        ("镜头遮挡检测", "Lens occlusion detection", "手机录像", "识别手指、灰尘、雨滴和贴膜遮挡", "faithful", "E5", ["official_davinci_magic_mask"]),
        ("算法温度降级", "Thermal-aware quality scaling", "长时间录像", "按温度/电量/帧率动态切换模型与分辨率", "faithful", "E5", ["official_blackmagic_camera_app"]),
        ("录后高质量重算", "Post-capture quality rerender", "旗舰手机", "保存代理、深度、mask、运动和关键帧供录后重算", "faithful", "E5", ["official_google_video_boost"]),
        ("构图安全区提示", "Composition safe-area guide", "短视频、直播", "预测裁切、字幕和主体运动的安全区域", "faithful", "E5", ["official_insta360_me_mode"]),
        ("失败片段自动标记", "Failure-segment indexing", "所有录像", "标记抖动、过曝、遮挡、噪声和生成不确定片段", "faithful", "E5", ["local_flashvsr"]),
    ]),
]


def make_record(index: int, family_id: str, family_zh: str, seed: tuple) -> dict:
    name_zh, name_en, scenarios, videoization, truth, evidence_level, evidence_ids = seed
    is_prototype = evidence_level != "E5"
    return {
        "id": f"OP-{index:03d}",
        "name_zh": name_zh,
        "name_en": name_en,
        "family": family_id,
        "family_zh": family_zh,
        "scenarios": [x.strip() for x in scenarios.split("、")],
        "source_type": ["official_product"] if evidence_ids[0].startswith("official_") else ["paper", "analysis"],
        "evidence_level": evidence_level,
        "prototype_status": "已有行业/学术原型" if is_prototype else "本报告视频化推演",
        "video_mode": "online_recording" if family_id in {"motion_quality", "night_hdr", "capture_assistance", "multi_camera"} else "offline_device",
        "input_signals": ["YUV/RGB", "连续帧", "语义 Mask", "运动估计"],
        "pipeline_stage": "ISP后端/视频编码前" if family_id not in {"generative_video", "virtual_camera"} else "录后端侧生成与合成",
        "algorithm_family": ["temporal feature propagation", "tracking", "mask-aware rendering"],
        "temporal_strategy": "关键帧锚定 + 光流/运动矢量传播 + 遮挡重置",
        "data_needs": "真实连续视频、运动/曝光/遮挡覆盖；生成式方向还需要 mask、深度或可控参数标注",
        "loss_or_objective": "重建/感知损失 + temporal warp consistency + 边界/颜色稳定损失；权重需通过梯度和消融验证",
        "quality_metrics": ["PSNR/SSIM（恢复类）", "LPIPS（感知类）", "temporal warping error", "flicker rate", "主观偏好"],
        "failure_modes": ["闪烁", "纹理游走", "边缘泄漏", "运动拖影", "曝光呼吸"],
        "truth_boundary": truth,
        "feasibility_tags": ["single_camera_possible", "temporal_consistency_required", "mobile_video_candidate"],
        "novelty": "高" if not is_prototype else "中",
        "video_fit": "高" if family_id in {"motion_quality", "night_hdr", "multi_camera", "capture_assistance"} else "中高",
        "edge_feasibility": "中" if truth != "generative" else "低到中",
        "product_differentiation": "高" if not is_prototype else "中",
        "risk": "生成式方向存在幻觉与用户预期管理风险" if truth == "generative" else "主要风险是时序稳定和端侧资源",
        "priority": "P1" if family_id in {"motion_quality", "night_hdr", "portrait_identity", "multi_camera"} else "P2",
        "evidence_ids": evidence_ids,
        "notes": f"视频化思路：{videoization}。已有能力/来源仅证明原型或相关技术，不证明本功能已经在手机中量产。",
        "last_verified": str(date.today()),
    }


def main() -> None:
    records = []
    index = 1
    for family_id, family_zh, seeds in FAMILIES:
        for seed in seeds:
            records.append(make_record(index, family_id, family_zh, seed))
            index += 1
    OUT.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in records) + "\n", encoding="utf-8")
    matrix = {
        "total": len(records),
        "families": {family_id: sum(row["family"] == family_id for row in records) for family_id, _, _ in FAMILIES},
        "evidence_levels": {level: sum(row["evidence_level"] == level for row in records) for level in ["E1", "E2", "E3", "E4", "E5"]},
        "truth_boundaries": {truth: sum(row["truth_boundary"] == truth for row in records) for truth in ["faithful", "perceptual", "generative"]},
        "video_modes": {mode: sum(row["video_mode"] == mode for row in records) for mode in ["preview", "online_recording", "offline_device", "cloud_render"]},
    }
    MATRIX.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# 候选机会池筛选记录",
        "",
        f"本批生成 {len(records)} 条候选，覆盖 {len(FAMILIES)} 个能力族。每条记录都区分证据等级与本报告的视频化推演。",
        "",
        "## 口径",
        "",
        "- `E1-E4` 表示外部产品、公开演示、论文或专利证据；本批的主体是基于行业/论文入口的 `E5` 视频化推演。",
        "- 候选功能不是产品承诺。必须通过数据、时序稳定、功耗、交互和主观测试进一步验证。",
        "- 生成式方向标记为 `generative`，报告中不能使用“真实恢复”表述替代。",
        "",
        "## 统计",
        "",
        f"- 总数：{matrix['total']}",
        f"- 能力族：{len(matrix['families'])}",
        f"- 主要证据等级：{matrix['evidence_levels']}",
        f"- 真实性边界：{matrix['truth_boundaries']}",
        "",
        "## 下一步",
        "",
        "从每个能力族选择代表方向，结合论文正文、官方说明和本地 PDF 做 30 个深度拆解；优先验证录像时序、数据制作、LOSS 组合和端侧落点。",
    ]
    NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(matrix, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
