"""Build a deterministic catalog of reusable mobile video-effect atoms."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path

try:
    from tools.video_effects import schema
except ModuleNotFoundError:  # Allow direct execution from the repository root.
    import schema  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT
METADATA = PROJECT / "daily" / "20260827_录像特效调研" / "metadata"
ATOM_OUTPUT = METADATA / "effect_atoms.jsonl"

ATOM_FIELDS = (
    "atom_id",
    "name_zh",
    "name_en",
    "family",
    "primitive_type",
    "visible_primitive",
    "required_signals",
    "temporal_state",
    "parameters",
    "failure_modes",
    "mobile_notes",
)

FAMILY_ORDER = (
    "segmentation_masks",
    "geometry_tracking",
    "temporal_state",
    "light_optics",
    "cloning_echoes",
    "deformation_space",
    "material_appearance",
    "particles_atmosphere",
    "generative_transformation",
    "interaction_triggers",
)

# Each row is independently reviewed: slug, Chinese name, English name, primitive
# type, visible change, specific signal, specific parameter, specific failure.
ATOM_SPECS = {
    "segmentation_masks": (
        ("FACE-REGION", "人脸区域掩码", "Face Region Mask", "semantic_mask", "画面中的人脸皮肤与五官区域形成可控制的连续遮罩边界", "face_landmarks", "face_edge_feather", "大角度侧脸会使耳侧边界缺失"),
        ("BODY-SILHOUETTE", "人体轮廓掩码", "Body Silhouette Mask", "semantic_mask", "画面中的整个人体轮廓被分离为可独立合成的前景区域", "body_keypoints", "body_mask_threshold", "肢体交叉时轮廓容易粘连"),
        ("HAIR-STRANDS", "头发细节掩码", "Hair Detail Mask", "detail_mask", "发丝与半透明碎发在背景前呈现可调边缘和覆盖范围", "hair_detail_map", "hair_matte_detail", "逆光细发可能被误判为背景"),
        ("CLOTHING-REGION", "服装区域掩码", "Clothing Region Mask", "semantic_mask", "上衣下装与配饰区域被标记为可单独换色或贴材质的范围", "clothing_labels", "garment_class_select", "服装与肤色接近时边界会漂移"),
        ("HAND-REGION", "手部区域掩码", "Hand Region Mask", "semantic_mask", "双手和手指在画面中形成可遮挡粒子或光效的精细区域", "hand_landmarks", "finger_edge_refine", "快速挥手会产生手指缺口"),
        ("FOREGROUND", "前景主体掩码", "Foreground Subject Mask", "foreground_mask", "距离镜头较近的主体被分成可独立移动和调色的前景层", "foreground_probability", "foreground_cutoff", "多层遮挡会混淆前景归属"),
        ("BACKGROUND", "背景区域掩码", "Background Region Mask", "background_mask", "主体之外的背景形成可替换或模糊的稳定可控区域", "background_probability", "background_fill_radius", "细杆和网格背景容易漏入主体"),
        ("SHADOW", "影子区域分割", "Shadow Region Segmentation", "appearance_mask", "地面或墙面上的可见影子被提取为可重绘亮度与形状的区域", "luminance_chroma", "shadow_softness", "深色物体可能被误识别为影子"),
        ("REFLECTION", "反射区域分割", "Reflection Region Segmentation", "appearance_mask", "镜面与水面中的反射内容被标记为可独立扭曲和调色的区域", "reflection_cues", "reflection_confidence", "弱反射会与真实背景混合"),
        ("SKY", "天空区域掩码", "Sky Region Mask", "semantic_mask", "地平线以上的天空与云层形成可替换且保留遮挡边缘的区域", "sky_semantics", "horizon_feather", "玻璃幕墙中的天空会造成重复区域"),
        ("SKIN", "皮肤区域掩码", "Skin Region Mask", "semantic_mask", "面部与肢体皮肤形成可局部调色并避开服装的连续区域", "skin_probability", "skin_tone_range", "暖色衣物可能侵入皮肤遮罩"),
        ("OBJECT-INSTANCE", "物体实例掩码", "Object Instance Mask", "instance_mask", "多个可见物体各自获得独立编号遮罩以控制合成前后关系", "instance_proposals", "instance_merge_threshold", "同类物体接触时实例编号可能合并"),
    ),
    "geometry_tracking": (
        ("HAND-2D-TRAJECTORY", "手部二维轨迹", "Hand 2D Trajectory", "point_trajectory", "手掌中心在屏幕平面形成连续可平滑的二维位置轨迹", "hand_2d_landmarks", "trajectory_smoothing", "手部出框会中断轨迹身份"),
        ("HAND-3D-TRAJECTORY", "手部三维轨迹", "Hand 3D Trajectory", "spatial_trajectory", "手掌在相机坐标中形成带前后深度变化的三维运动轨迹", "hand_depth", "depth_scale", "单目深度突变会造成前后跳跃"),
        ("BODY-SKELETON", "人体骨骼拓扑", "Human Body Skeleton", "pose_graph", "人体关节与骨段在画面上形成可驱动附着效果的骨骼拓扑", "pose_keypoints", "joint_confidence", "多人交叉时关节身份可能交换"),
        ("HEAD-POSE", "头部姿态向量", "Head Pose Vector", "orientation_track", "头部偏航俯仰和翻滚角控制画面元素的朝向与透视", "face_landmarks", "pose_angle_limit", "遮住下巴时俯仰估计不稳定"),
        ("GAZE-VECTOR", "视线方向向量", "Gaze Direction Vector", "direction_track", "双眼注视方向被表示为可控制光点或目标选择的视线向量", "eye_crops", "gaze_calibration", "镜片反光会偏移视线方向"),
        ("IRIS-PUPIL-LANDMARKS", "虹膜瞳孔关键点", "Iris and Pupil Landmarks", "landmark_track", "虹膜圆周与瞳孔中心形成可重绘眼神光和瞳孔变化的关键点", "eye_landmarks", "iris_radius_scale", "眨眼闭合时关键点会暂时消失"),
        ("MONOCULAR-DEPTH", "单目深度场", "Monocular Depth Field", "dense_geometry", "画面像素获得相对远近值以控制遮挡虚化和空间位移", "rgb_frame", "depth_contrast", "反射表面会产生错误深度层级"),
        ("SURFACE-NORMALS", "表面法线场", "Surface Normal Field", "dense_geometry", "可见表面的朝向被编码为法线以控制局部受光和材质反射", "depth_or_rgb", "normal_smoothing", "纹理弱区域的法线方向容易抖动"),
        ("WORLD-SPACE-ANCHOR", "世界空间锚点", "World Space Anchor", "world_anchor", "选定点在相机移动后仍固定于真实场景位置并保持可见对齐", "camera_pose", "anchor_persistence", "快速转身会使空间锚点丢失"),
        ("MULTI-PERSON-GRAPH", "多人关系图", "Multi-person Relation Graph", "relation_graph", "多个人体节点之间的距离朝向和接触关系形成可查询的关系图", "person_tracks", "relation_distance", "人员重叠会造成关系边误连"),
        ("CAMERA-MOTION", "相机运动轨迹", "Camera Motion Track", "camera_trajectory", "手机平移旋转和缩放趋势形成可抵消或放大画面运动的轨迹", "imu_samples", "motion_scale", "滚动快门会使视觉运动与陀螺仪不一致"),
        ("OBJECT-POSE", "物体六自由度姿态", "Object Six-DoF Pose", "object_pose", "刚体物体的位置与朝向持续控制贴附图形的透视和遮挡", "object_features", "pose_reprojection", "无纹理物体旋转时姿态会漂移"),
    ),
    "temporal_state": (
        ("TIME-DECAY", "时间衰减缓存", "Temporal Decay Buffer", "state_decay", "历史画面或属性按可调速率逐帧变淡并最终从当前画面消失", "history_buffer", "decay_rate", "衰减过慢会留下脏污式残留"),
        ("TRAJECTORY-ACCUMULATION", "轨迹积累缓存", "Trajectory Accumulation Buffer", "state_accumulation", "连续位置样本被累积成可控制长度和密度的可见轨迹", "tracked_positions", "history_length", "跟踪跳点会画出错误连线"),
        ("LOCAL-TIME-FREEZE", "局部时间冻结", "Local Time Freeze", "regional_time_control", "选定区域停留在指定帧而周围画面继续随时间正常变化", "region_mask", "freeze_frame_index", "遮挡变化会暴露冻结区域边界"),
        ("TIME-LOOP", "局部时间循环", "Local Time Loop", "cyclic_buffer", "指定区域在一段历史帧之间往复或循环播放可见动作", "loop_frame_buffer", "loop_duration", "循环首尾姿态差异会产生跳切"),
        ("TIME-REVERSE", "局部时间反转", "Local Time Reverse", "reverse_buffer", "选定对象的短时动作按相反帧序回放而背景保持当前时间", "object_track_history", "reverse_window", "对象离开区域后反转内容会断裂"),
        ("EVENT-WINDOW", "事件触发窗口", "Event Trigger Window", "event_window", "触发前后的一段帧被标记为可供特效渐入保持和渐出的时间窗口", "event_timestamp", "pre_roll_frames", "连续事件过近会导致窗口重叠"),
        ("MOTION-PHASE", "动作阶段状态", "Motion Phase State", "phase_state", "起势持续峰值和收势阶段被映射为可控制强度变化的离散状态", "motion_features", "phase_threshold", "慢动作可能被误判为持续阶段"),
        ("FRAME-DELAY", "帧延迟队列", "Frame Delay Queue", "delay_buffer", "画面区域按固定或可变帧差显示过去内容形成时间错位基础", "frame_stream", "delay_frames", "内存压力下历史帧可能被提前丢弃"),
        ("IDENTITY-MEMORY", "时序身份记忆", "Temporal Identity Memory", "identity_state", "被跟踪的人或物在短暂遮挡后恢复原有编号和关联属性", "track_embeddings", "reacquire_timeout", "相似外观对象会发生身份互换"),
        ("BEAT-PHASE-CLOCK", "节拍相位时钟", "Beat Phase Clock", "phase_clock", "音乐节拍之间的连续相位值控制周期性缩放闪烁或位移", "beat_timestamps", "phase_offset", "变速音乐会让相位逐渐偏移"),
        ("STATE-HYSTERESIS", "状态滞回门限", "State Hysteresis Gate", "state_gate", "触发量跨越不同进入退出阈值后才切换可见状态以减少闪烁", "control_signal", "enter_threshold", "阈值间距过大会造成响应迟钝"),
        ("MOTION-HISTORY", "运动历史体", "Motion History Volume", "spatiotemporal_volume", "多帧运动区域叠成带时间层次的体积记录供后续形变或着色控制", "motion_masks", "temporal_depth", "镜头抖动会污染整个运动历史"),
    ),
    "light_optics": (
        ("LIGHT-PAINT-BRUSH", "光绘笔刷", "Light Painting Brush", "emissive_stroke", "沿输入路径生成宽度亮度和颜色可控的发光笔刷线条", "brush_path", "stroke_width", "快速转折处线条容易出现尖角"),
        ("LUMINOUS-CORE", "发光核心", "Luminous Core", "emissive_region", "目标中心出现可调半径和亮度的发光核并向外柔和衰减", "target_center", "core_radius", "高亮背景会降低发光核可见度"),
        ("DYNAMIC-STARBURST", "动态星芒", "Dynamic Starburst", "diffraction_rays", "亮点周围生成随亮度和角度变化的多方向星芒射线", "highlight_points", "ray_count", "密集灯光会让星芒互相覆盖"),
        ("LENS-FLARE", "镜头光斑", "Lens Flare", "lens_artifact", "强光源与画面中心连线上出现可调鬼影光斑和光晕", "light_source_position", "ghost_spacing", "错误光源位置会使光斑失去光学关联"),
        ("VIRTUAL-RIM-LIGHT", "虚拟轮廓光", "Virtual Rim Light", "relighting", "主体背光边缘出现颜色强度与宽度可控的轮廓亮边", "subject_normals", "rim_width", "分割毛边会被轮廓光放大"),
        ("CATCHLIGHT-RERENDER", "眼神光重渲染", "Catchlight Re-rendering", "eye_relit", "瞳孔表面出现位置形状与亮度可控制的高光反射点", "iris_landmarks", "catchlight_size", "闭眼和侧脸时眼神光可能越界"),
        ("VIRTUAL-SPOTLIGHT", "虚拟追光", "Virtual Follow Spotlight", "tracked_light", "圆形或椭圆光区跟随目标移动并控制周围区域的相对明暗", "target_track", "spot_radius", "目标快速换向会让光区明显滞后"),
        ("SHADOW-RERENDER", "影子重渲染", "Shadow Re-rendering", "synthetic_shadow", "主体下方或侧面生成方向软硬和长度可调的可见投影影子", "ground_plane", "shadow_length", "缺少地面几何时影子会悬空"),
        ("VOLUMETRIC-LIGHT", "体积光束", "Volumetric Light Beam", "volume_light", "光源到场景之间形成带散射密度和锥角的可见体积光束", "depth_field", "scattering_density", "深度错误会使光束穿过前景"),
        ("CHROMATIC-ABERRATION", "色散边缘", "Chromatic Aberration Edge", "spectral_offset", "高对比边缘分离出方向和距离可控的红绿蓝色偏移", "image_edges", "channel_offset", "大偏移会使人物轮廓显得失焦"),
        ("BLOOM-GLOW", "高光泛光", "Highlight Bloom", "bloom_filter", "超过阈值的高亮区域向周围扩散成半径和强度可调的柔光", "luminance_map", "bloom_threshold", "过低阈值会让整幅画面发灰"),
        ("CAUSTIC-PROJECTION", "焦散投影", "Caustic Projection", "light_pattern", "表面出现流动的高亮焦散纹路并可控制尺度方向和速度", "surface_region", "caustic_scale", "纹理运动与表面透视不符会显得漂浮"),
    ),
    "cloning_echoes": (
        ("HUMAN-TIME-CLONE", "人体时间克隆", "Human Time Clone", "temporal_clone", "同一人物在不同历史时刻的完整轮廓同时出现在当前画面", "person_track_history", "clone_delay", "人物路径重叠时克隆边界会互相遮挡"),
        ("MOTION-AFTERIMAGE", "动作残影", "Motion Afterimage", "motion_echo", "移动肢体后方保留若干透明度递减的历史姿态残影", "pose_history", "afterimage_count", "低置信姿态会生成断裂残影"),
        ("SHADOW-DOUBLE", "影子分身", "Shadow Double", "shadow_clone", "主体旁出现保持影子外观但动作可延迟的独立轮廓分身", "shadow_mask", "shadow_delay", "真实阴影复杂时分身会混入环境暗区"),
        ("MIRROR-PERSONA", "镜像人格", "Mirror Persona", "mirrored_clone", "人物的镜像副本在对称位置呈现可独立延迟或变速的动作", "person_mask", "mirror_axis", "越过镜像轴时两个人像会粘连"),
        ("POSE-SLICES", "姿态切片", "Pose Time Slices", "pose_slice", "连续历史姿态被离散成多个空间偏移的可见人体切片", "skeleton_history", "slice_spacing", "动作幅度小时切片难以区分"),
        ("DELAYED-CLONE", "延迟分身", "Delayed Clone", "delayed_clone", "目标的完整副本按指定时间差重复当前动作并保持身份一致", "object_history", "delay_seconds", "长时间遮挡会使延迟副本缺帧"),
        ("SILHOUETTE-ECHO", "轮廓回声", "Silhouette Echo", "contour_echo", "主体边缘的历史轮廓按时间顺序扩散成多层透明线框", "contour_history", "echo_spacing", "背景边缘泄漏会产生杂乱线框"),
        ("SPATIAL-DUPLICATE", "空间复制体", "Spatial Duplicate", "spatial_clone", "选定目标在多个可控屏幕位置显示同步外观和同步动作副本", "target_crop", "duplicate_offsets", "副本跨越遮挡物时层级关系会错误"),
        ("FRAME-STUTTER", "帧停顿克隆", "Frame Stutter Clone", "stutter_clone", "若干冻结历史帧以分身形式依次排布并在更新时跳到新姿态", "sampled_frames", "stutter_interval", "采样间隔不均会造成节奏混乱"),
        ("PERSPECTIVE-CLONE", "透视分身", "Perspective Clone", "perspective_clone", "同一目标副本按虚拟深度缩放并沿透视方向分布在画面中", "vanishing_point", "depth_spacing", "错误消失点会让分身比例不自然"),
        ("EXPRESSION-ECHO", "表情回声", "Expression Echo", "facial_echo", "历史面部表情以局部透明副本叠在脸部周围并依次衰减", "expression_history", "expression_delay", "头部转动会使表情副本错位"),
        ("GESTURE-ECHO", "手势回声", "Gesture Echo", "gesture_echo", "手部历史姿态以多个局部副本沿运动方向依次显现", "hand_pose_history", "gesture_echo_count", "手指遮挡会让回声形状残缺"),
    ),
    "deformation_space": (
        ("LOCAL-LIQUIFY", "局部液化形变", "Local Liquify Warp", "image_warp", "笔刷覆盖区域的像素沿拖动方向连续流动并保持边缘可调", "touch_vector_field", "liquify_strength", "大形变会拉出重复纹理"),
        ("PERSPECTIVE-STRETCH", "透视拉伸", "Perspective Stretch", "projective_warp", "选定区域朝消失点方向拉长或压缩并呈现可控透视变化", "vanishing_direction", "stretch_ratio", "主体边界未锁定时背景会一起拉伸"),
        ("SPACE-FOLD", "空间折叠", "Spatial Fold", "piecewise_warp", "画面沿可控折线分成多个平面并产生折叠角度和遮挡变化", "fold_line", "fold_angle", "折线穿过人脸会造成不连续断面"),
        ("MIRROR-PORTAL", "镜面入口", "Mirror Portal", "portal_mapping", "指定镜面区域显示另一空间视角并保留边框透视和进入遮挡", "portal_mask", "portal_depth", "入口边缘跟踪漂移会暴露贴图错位"),
        ("FRAME-TRAVERSAL", "画面穿越", "Frame Traversal", "depth_transition", "主体跨过可控画面平面时在前后空间之间连续缩放和遮挡", "crossing_depth", "plane_position", "深度顺序错误会让主体突然跳层"),
        ("COMIC-SPEED-LINES", "漫画速度线", "Comic Speed Lines", "directional_lines", "运动方向周围生成长度密度和汇聚点可控的漫画速度线", "motion_direction", "line_density", "静止镜头噪声会触发杂乱速度线"),
        ("ELASTIC-WARP", "弹性形变", "Elastic Warp", "elastic_deformation", "目标区域受到位移后以可调弹性和阻尼回到原始轮廓", "deformation_handle", "elasticity", "边界约束过弱会拖动相邻背景"),
        ("DEPTH-PARALLAX", "深度视差位移", "Depth Parallax Shift", "depth_warp", "不同深度层按相机移动产生幅度不同的横向位移和遮挡变化", "depth_map", "parallax_scale", "深度断层会产生撕裂空洞"),
        ("TUNNEL-WARP", "隧道透视形变", "Tunnel Perspective Warp", "radial_warp", "画面围绕中心形成向内延伸的隧道尺度和径向透视变化", "tunnel_center", "tunnel_depth", "中心靠近边缘时形变分布会失衡"),
        ("RADIAL-TWIST", "径向扭转", "Radial Twist", "polar_warp", "中心周围像素按半径逐渐旋转形成角度和范围可控的扭转", "twist_center", "twist_angle", "强扭转会放大采样锯齿"),
        ("GRAVITY-BEND", "重力弯曲场", "Gravity Bend Field", "vector_field_warp", "画面元素朝一个可控引力中心弯曲位移并随距离改变强度", "gravity_center", "falloff_exponent", "引力中心穿过主体时轮廓会塌缩"),
        ("RIPPLE-DISPLACEMENT", "波纹位移", "Ripple Displacement", "wave_warp", "触发点向外传播同心波纹并周期性推移可见像素位置", "ripple_origin", "wave_amplitude", "高频波纹会产生明显走样"),
    ),
    "material_appearance": (
        ("METAL", "金属材质响应", "Metal Material Response", "material_transfer", "目标表面出现方向相关高光和金属反射色并保留原有形状", "surface_normals", "metallic_level", "法线错误会让高光方向跳变"),
        ("GLASS", "玻璃材质响应", "Glass Material Response", "material_transfer", "目标区域呈现可调透明度折射和边缘高光的玻璃外观", "background_sample", "refraction_strength", "缺少背后内容时折射会显得空洞"),
        ("LIQUID", "液体材质响应", "Liquid Material Response", "material_transfer", "目标表面出现流动反射和波动轮廓并可控制黏度与速度", "surface_motion", "viscosity", "快速运动会使液体纹理滑离目标"),
        ("FIRE", "火焰材质响应", "Fire Material Response", "material_transfer", "目标轮廓内外出现向上流动的火焰颜色亮度和边缘扰动", "object_mask", "flame_height", "细小区域会让火焰结构无法展开"),
        ("NEON", "霓虹材质响应", "Neon Material Response", "material_transfer", "目标边缘和内部线条呈现颜色可控的霓虹发光管外观", "edge_map", "neon_width", "复杂纹理会生成过密霓虹线条"),
        ("PIXEL", "像素材质响应", "Pixel Material Response", "material_transfer", "目标区域被量化为尺寸和调色板可控的可见像素块", "target_region", "pixel_size", "像素块过大会抹除主体识别特征"),
        ("PAPER", "纸张材质响应", "Paper Material Response", "material_transfer", "目标表面叠加纸纤维褶皱与漫反射并保持轮廓可控", "surface_uv", "paper_roughness", "纹理尺度不当会像贴图漂浮"),
        ("FABRIC", "织物材质响应", "Fabric Material Response", "material_transfer", "目标表面呈现经纬纹理柔软起伏和方向性反光的织物外观", "garment_normals", "weave_scale", "身体快速形变会拉伸织物纹理"),
        ("PIXEL-DISSOLVE", "像素溶解", "Pixel Dissolve", "material_transition", "目标从边缘或噪声阈值处逐块转为散开的像素单元", "dissolve_mask", "dissolve_progress", "阈值变化过快会像硬切消失"),
        ("FRAGMENTATION", "碎片化", "Surface Fragmentation", "material_transition", "目标表面分裂成尺寸方向和散开距离可控的可见碎片", "fragment_cells", "fragment_spread", "碎片过多会遮蔽主体动作"),
        ("CRYSTAL", "水晶材质响应", "Crystal Material Response", "material_transfer", "目标表面呈现多面折射高光和半透明晶体色彩变化", "facet_normals", "crystal_ior", "低分辨率区域会出现闪烁切面"),
        ("HOLOGRAPHIC", "全息材质响应", "Holographic Material Response", "material_transfer", "目标表面随观察角度出现彩虹色带扫描线和半透明闪烁", "view_direction", "hue_shift", "视角估计抖动会造成色带跳闪"),
    ),
    "particles_atmosphere": (
        ("SMOKE", "烟雾粒子", "Smoke Particles", "particle_field", "目标附近生成密度扩散方向和消散速度可控的半透明烟雾粒子", "emitter_region", "smoke_density", "前景深度错误会让烟雾穿过人物"),
        ("SPARKS", "火花粒子", "Spark Particles", "particle_field", "触发点喷射带亮度尾迹和寿命控制的高速火花粒子", "emitter_point", "spark_velocity", "过曝区域会吞没火花细节"),
        ("PETALS", "花瓣粒子", "Petal Particles", "particle_field", "画面空间飘落旋转速度和密度可调的花瓣形粒子", "scene_depth", "petal_density", "遮挡缺失会让花瓣贴在人物表面"),
        ("RAIN", "雨滴粒子", "Rain Particles", "particle_field", "画面中出现方向长度和速度可控的雨滴线并响应镜头运动", "camera_motion", "rain_intensity", "快门拖影会与生成雨线冲突"),
        ("SNOW", "雪片粒子", "Snow Particles", "particle_field", "不同深度层飘落大小旋转和速度可控的雪片粒子", "depth_layers", "snow_size", "背景高亮会降低雪片可见度"),
        ("TEXT", "文字粒子", "Text Particles", "glyph_particle_field", "字符作为粒子沿路径聚散旋转并保持文字内容和字号可控", "text_glyphs", "glyph_count", "字符过小会失去可读性"),
        ("MUSIC-SPECTRUM", "音乐频谱粒子", "Music Spectrum Particles", "audio_particle_field", "粒子高度颜色和扩散幅度随多个音频频段能量连续变化", "audio_spectrum", "band_gain", "噪声底会让低能量频段持续抖动"),
        ("LYRIC-RING", "歌词文字环", "Lyric Text Ring", "text_orbit", "当前歌词沿可控半径环绕目标排布并随时间旋转和更新", "lyric_segments", "ring_radius", "长歌词会在环上重叠难读"),
        ("DUST", "漂浮尘埃粒子", "Floating Dust Particles", "particle_field", "光照区域内出现缓慢漂浮且景深大小可控的细小尘埃粒子", "light_volume", "dust_density", "压缩噪声可能与尘埃混淆"),
        ("BUBBLES", "气泡粒子", "Bubble Particles", "particle_field", "透明气泡从发射区域上升并具有可调大小折射和破裂时机", "emitter_region", "bubble_buoyancy", "边缘折射过强会产生黑色轮廓"),
        ("CONFETTI", "彩纸粒子", "Confetti Particles", "particle_field", "多色纸片按重力旋转和空气阻力散落并可控制发射范围", "gravity_direction", "confetti_amount", "大量纸片会遮挡人脸和手势"),
        ("EMBERS", "余烬粒子", "Ember Particles", "particle_field", "细小发光余烬向上漂移并以可调温度颜色和寿命逐渐熄灭", "heat_direction", "ember_lifetime", "暗部降噪会抹除微小余烬"),
    ),
    "generative_transformation": (
        ("CLOTHING", "服装受控生成变换", "Controlled Clothing Transformation", "conditional_generation", "仅在服装掩码内按款式颜色和结构条件重绘可见服装外观", "clothing_mask", "garment_prompt_strength", "宽松衣摆运动时生成纹理可能跳变"),
        ("HAIRSTYLE", "发型受控生成变换", "Controlled Hairstyle Transformation", "conditional_generation", "头发区域按长度卷曲和颜色条件重绘并保持脸部身份不变", "hair_mask", "hairstyle_condition", "发丝遮脸时可能改写五官边界"),
        ("AGE", "年龄受控生成变换", "Controlled Age Transformation", "conditional_generation", "面部在年龄条件下改变皱纹轮廓和肤质同时保留身份特征", "face_identity", "target_age", "大年龄跨度会削弱人物身份一致性"),
        ("CHARACTER", "角色受控生成变换", "Controlled Character Transformation", "conditional_generation", "主体按角色条件重绘服饰面部细节和配色并保持动作姿态", "subject_pose", "character_condition", "快速姿态变化会导致角色细节闪烁"),
        ("WEATHER", "天气受控生成变换", "Controlled Weather Transformation", "conditional_generation", "背景环境按晴雨雾雪条件重绘光照天空和地面湿润外观", "scene_layout", "weather_condition", "天气变化可能错误覆盖前景人物"),
        ("BACKGROUND-WORLD", "背景世界受控生成变换", "Controlled Background World Transformation", "conditional_generation", "主体之外的区域按世界设定重绘建筑地貌和天空并保留遮挡", "background_mask", "world_condition", "镜头移动时新背景几何可能不连续"),
        ("VISUAL-STYLE", "风格受控生成变换", "Controlled Visual Style Transformation", "conditional_generation", "整幅画面按指定视觉风格重绘色彩线条和纹理并约束主体结构", "structure_guidance", "style_strength", "高风格强度会改变人物身份"),
        ("PROP", "道具受控生成变换", "Controlled Prop Transformation", "conditional_generation", "手持或场景物体按类别和外形条件重绘同时保持接触位置", "object_mask", "prop_condition", "手指遮挡会破坏道具握持关系"),
        ("MAKEUP", "妆容受控生成变换", "Controlled Makeup Transformation", "conditional_generation", "面部局部按妆容颜色和范围条件重绘并跟随五官运动", "face_regions", "makeup_intensity", "侧脸时妆容边界可能漂移"),
        ("SCENE-LIGHTING", "场景光照受控生成", "Controlled Scene Lighting Generation", "conditional_generation", "画面按光源方向色温和强度条件重绘受光与阴影关系", "scene_geometry", "lighting_condition", "几何估计错误会生成矛盾阴影"),
        ("SEASON", "季节受控生成变换", "Controlled Seasonal Transformation", "conditional_generation", "环境按季节条件重绘植被地表和色调并保持原有场景布局", "scene_semantics", "season_condition", "细小植被在视频中可能随机变化"),
    ),
    "interaction_triggers": (
        ("GAZE-FOCUS", "视线注视触发", "Gaze Focus Trigger", "signal_trigger", "视线在目标区域持续停留后输出可调置信度和持续时间的触发量", "gaze_vector", "dwell_duration", "眼镜反光会造成错误注视触发"),
        ("BLINK", "眨眼触发", "Blink Trigger", "signal_trigger", "眼睑完成闭合再张开时输出单次事件并区分左右眼", "eyelid_landmarks", "blink_threshold", "快速低头可能被误识别为眨眼"),
        ("EXPRESSION", "表情强度触发", "Expression Intensity Trigger", "signal_trigger", "微笑惊讶或皱眉达到可调强度时输出连续控制值或事件", "facial_action_units", "expression_threshold", "夸张说话会混入表情强度"),
        ("MOUTH-SHAPE", "嘴型触发", "Mouth Shape Trigger", "signal_trigger", "嘴唇开合圆扁和特定口型变化映射为可控制的连续信号", "lip_landmarks", "mouth_shape_class", "遮住嘴部时口型分类会失效"),
        ("HAND-GESTURE", "手势触发", "Hand Gesture Trigger", "signal_trigger", "指定手势进入保持和退出阶段时输出类别置信度与事件边沿", "hand_pose", "gesture_hold_time", "相似手势之间容易短暂跳类"),
        ("BODY-POSE", "姿态触发", "Body Pose Trigger", "signal_trigger", "人体关节关系达到指定姿态条件时输出强度和持续状态", "body_skeleton", "pose_similarity", "身体出框会降低姿态匹配可靠性"),
        ("SOUND-VOLUME", "声音音量触发", "Sound Volume Trigger", "audio_trigger", "麦克风响度跨越阈值时输出平滑包络值和进入退出事件", "audio_waveform", "volume_threshold", "环境突发噪声会造成误触发"),
        ("AUDIO-BEAT", "音频节拍触发", "Audio Beat Trigger", "audio_trigger", "检测到音乐节拍时输出时间戳强度和相邻节拍间隔", "audio_onsets", "beat_sensitivity", "弱拍和切分节奏可能被漏检"),
        ("LYRIC-TIMESTAMP", "歌词时间戳触发", "Lyric Timestamp Trigger", "metadata_trigger", "播放进度到达歌词片段时间戳时输出当前文本和片段区间", "timed_lyrics", "timestamp_offset", "音轨版本不一致会导致歌词错位"),
        ("SOURCE-DIRECTION", "声源方向触发", "Sound Source Direction Trigger", "audio_spatial_trigger", "估计声源方位跨入指定角区时输出方向角和稳定置信度", "microphone_channels", "direction_sector", "混响环境会让方向估计摇摆"),
        ("TOUCH-DRAW", "触摸画线输入", "Touch Drawing Input", "direct_control", "手指在屏幕上的采样点形成压力速度和宽度可控制的连续画线路径", "touch_samples", "path_resampling", "采样稀疏会让曲线出现折角"),
        ("PHONE-ROTATION", "手机旋转输入", "Phone Rotation Input", "sensor_control", "手机三轴旋转角速度映射为画面元素方向位移或强度控制量", "gyroscope", "rotation_gain", "传感器漂移会造成静止时缓慢移动"),
        ("MULTI-PERSON-TOUCH", "多人触碰触发", "Multi-person Touch Trigger", "relation_trigger", "两人手部或身体区域在画面中接近并接触时输出关系事件", "person_relation_graph", "contact_distance", "透视重叠但未真实接触会误触发"),
    ),
}

FAMILY_DEFAULTS = {
    "segmentation_masks": {
        "signal": "rgb_video_frames",
        "parameter": "mask_edge_feather",
        "failure": "快速运动会使遮罩边缘产生短暂抖动",
        "temporal": "short_window：使用相邻帧稳定遮罩身份与边界，不保存长期用户状态",
        "mobile": "端侧预览使用缩小分辨率遮罩并在合成前上采样，精细边缘留给录制后处理。",
    },
    "geometry_tracking": {
        "signal": "timestamped_rgb_frames",
        "parameter": "tracking_confidence",
        "failure": "低纹理或遮挡会降低几何跟踪连续性",
        "temporal": "long_state：跨帧维护轨迹身份，丢失后按超时规则重建",
        "mobile": "端侧保存稀疏几何量和置信度供预览使用，密集几何可按设备能力降采样。",
    },
    "temporal_state": {
        "signal": "monotonic_frame_timestamps",
        "parameter": "state_window_length",
        "failure": "时间戳不连续会使状态更新出现跳变",
        "temporal": "long_state：显式维护跨帧缓存或状态机，并按时间戳确定更新顺序",
        "mobile": "端侧使用有界环形缓存并允许降低历史分辨率，避免宣称未测的帧率或功耗。",
    },
    "light_optics": {
        "signal": "linear_rgb_or_hdr_estimate",
        "parameter": "effect_intensity",
        "failure": "曝光范围不足会压缩光学效果的层次",
        "temporal": "short_window：逐帧渲染并用短窗口平滑亮度位置，避免闪烁",
        "mobile": "端侧预览使用低分辨率光效缓冲与可分离模糊，录制后可提高采样质量。",
    },
    "cloning_echoes": {
        "signal": "tracked_subject_frames",
        "parameter": "clone_opacity",
        "failure": "主体遮挡关系错误会让克隆层级穿帮",
        "temporal": "long_state：保存带身份和时间戳的主体历史切片供延迟或复制",
        "mobile": "端侧压缩保存主体裁剪和遮罩，限制同时可见副本数量以控制内存。",
    },
    "deformation_space": {
        "signal": "source_image_grid",
        "parameter": "warp_extent",
        "failure": "采样坐标越界会产生空洞或拉丝边缘",
        "temporal": "short_window：形变参数逐帧更新并用短窗口约束连续位移",
        "mobile": "端侧预览采用规则网格或低分辨率位移场，录制后再细化边界采样。",
    },
    "material_appearance": {
        "signal": "target_surface_mask",
        "parameter": "material_blend",
        "failure": "遮罩与表面运动不同步会造成材质滑动",
        "temporal": "short_window：逐帧着色并在目标坐标中稳定纹理相位与高光",
        "mobile": "端侧使用简化材质参数和预计算纹理，复杂反射可在录制后细化。",
    },
    "particles_atmosphere": {
        "signal": "frame_timestamps",
        "parameter": "particle_lifetime",
        "failure": "粒子数量过高会造成画面拥挤和排序错误",
        "temporal": "long_state：维护粒子出生位置速度寿命和跨帧遮挡状态",
        "mobile": "端侧使用实例化粒子与固定容量池，按画面占比降低粒子更新密度。",
    },
    "generative_transformation": {
        "signal": "source_video_frames",
        "parameter": "structure_preservation",
        "failure": "逐帧独立生成会造成纹理和身份闪烁",
        "temporal": "long_state：保留身份结构与上一帧生成特征以约束跨帧一致性",
        "mobile": "端侧仅提供低分辨率或关键帧预览，完整受控生成可在录制后执行并保留回退原片。",
    },
    "interaction_triggers": {
        "signal": "monotonic_event_timestamps",
        "parameter": "trigger_cooldown",
        "failure": "信号在阈值附近抖动会造成重复触发",
        "temporal": "short_window：使用进入保持退出状态和冷却窗口生成稳定触发事件",
        "mobile": "端侧只记录触发值时间戳和置信度，预览效果可按能力选择轻量反馈。",
    },
}


def _atom(family: str, spec: tuple[str, ...]) -> dict[str, object]:
    slug, name_zh, name_en, primitive_type, visible, signal, parameter, failure = spec
    defaults = FAMILY_DEFAULTS[family]
    family_id = family.upper().replace("_", "-")
    return {
        "atom_id": f"ATOM-{family_id}-{slug}",
        "name_zh": name_zh,
        "name_en": name_en,
        "family": family,
        "primitive_type": primitive_type,
        "visible_primitive": visible,
        "required_signals": [defaults["signal"], signal],
        "temporal_state": [defaults["temporal"]],
        "parameters": [defaults["parameter"], parameter],
        "failure_modes": [defaults["failure"], failure],
        "mobile_notes": [defaults["mobile"]],
    }


def build_atoms() -> list[dict]:
    """Return atoms in stable family and definition order."""

    return [
        _atom(family, spec)
        for family in FAMILY_ORDER
        for spec in ATOM_SPECS[family]
    ]


def _find_duplicates(values: Iterable[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def validate_atoms(atoms: list[dict]) -> dict:
    """Validate atom schemas, exact fields, uniqueness, IDs, and family order."""

    if not isinstance(atoms, list):
        raise ValueError("atoms must be a list")

    expected_fields = set(ATOM_FIELDS)
    for index, atom in enumerate(atoms):
        if not isinstance(atom, Mapping):
            raise ValueError(f"atom[{index}] must be a mapping")
        if set(atom) != expected_fields:
            raise ValueError(f"atom[{index}] fields must match schema fields exactly")
        try:
            schema.validate_atom(atom)
        except ValueError as exc:
            atom_id = atom.get("atom_id", f"index {index}")
            raise ValueError(f"schema validation failed for {atom_id}: {exc}") from exc

        family = atom["family"]
        expected_prefix = f"ATOM-{family.upper().replace('_', '-')}-"
        if not atom["atom_id"].startswith(expected_prefix):
            raise ValueError(f"atom_id family prefix mismatch: {atom['atom_id']}")

    for field in ("atom_id", "name_zh", "name_en"):
        duplicates = _find_duplicates(atom[field] for atom in atoms)
        if duplicates:
            raise ValueError(f"duplicate {field}: {', '.join(duplicates)}")

    family_counts = Counter(atom["family"] for atom in atoms)
    unknown_families = sorted(set(family_counts) - set(FAMILY_ORDER))
    if unknown_families:
        raise ValueError(f"unknown families: {', '.join(unknown_families)}")
    observed_order = tuple(dict.fromkeys(atom["family"] for atom in atoms))
    expected_order = tuple(family for family in FAMILY_ORDER if family in family_counts)
    if observed_order != expected_order:
        raise ValueError("atom families are not in stable FAMILY_ORDER")

    return {
        "count": len(atoms),
        "family_counts": dict(family_counts),
    }


def write_jsonl(rows: list[dict], path: Path = ATOM_OUTPUT) -> None:
    """Write compact UTF-8 JSONL with deterministic separators and newlines."""

    validate_atoms(rows)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--atoms-only",
        action="store_true",
        help="Generate only effect atoms; this is also the current default behavior.",
    )
    parser.parse_args()

    atoms = build_atoms()
    report = validate_atoms(atoms)
    write_jsonl(atoms)
    print(f"wrote {report['count']} atoms to {ATOM_OUTPUT}")


if __name__ == "__main__":
    main()
