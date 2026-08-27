"""Build deterministic catalogs of reusable mobile video-effect atoms and ideas."""

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
IDEA_OUTPUT = METADATA / "effect_ideas.jsonl"

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

IDEA_FIELDS = (
    "effect_id",
    "name_zh",
    "name_en",
    "family",
    "visible_effect",
    "scenarios",
    "target_objects",
    "spatial_scope",
    "trigger_signals",
    "interaction",
    "user_controls",
    "preview_pipeline",
    "post_pipeline",
    "required_signals",
    "atom_ids",
    "temporal_window",
    "continuity_challenges",
    "edge_difficulty",
    "execution_targets",
    "generation_level",
    "risks",
    "novelty",
    "shareability",
    "product_value",
    "reference_ids",
    "combinable_effect_ids",
    "status",
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

IDEA_FAMILY_ORDER = (
    "light_trails_optics",
    "body_motion_clones",
    "face_gaze_expression",
    "time_editing",
    "spatial_portals",
    "virtual_light_shadow",
    "material_morph",
    "particles_weather",
    "world_style",
    "audio_lyrics",
    "effect_cinematography",
    "multi_person_interaction",
)

# A motif describes the object and its spatial meaning. A behavior describes
# the temporal response and control surface. Their Cartesian product keeps all
# 25 rows in each family materially different while remaining auditable.
IDEA_FAMILY_SPECS = {
    "light_trails_optics": {
        "title_zh": "光轨光学",
        "title_en": "Light Trails Optics",
        "motifs": (
            ("FINGER", "指尖实时光绘轨迹", "Finger Screen Light Painting", "屏幕触摸路径与指尖", "手绘签名或涂鸦录像", "用户在屏幕按下并拖动指尖", "笔刷宽度", ("LIGHT-PAINT-BRUSH", "TOUCH-DRAW"), "screen_touch_path", "touch_samples", "手指离开屏幕会中断连续笔画"),
            ("BODY", "人体肢体光绘", "Body Limb Light Painting", "人体关节与四肢运动路径", "舞蹈、体操或运动录像", "全身进入画面并开始动作", "骨骼光线粗细", ("LIGHT-PAINT-BRUSH", "BODY-SKELETON"), "body_motion_path", "pose_keypoints", "肢体交叉会让关节轨迹错连"),
            ("SOURCE", "手持灯棒移动光轨", "Handheld Moving Light Trail", "手持灯棒或移动点光源", "夜景灯棒与车灯录像", "锁定手持灯棒或移动光源", "光源阈值", ("LIGHT-PAINT-BRUSH", "LUMINOUS-CORE"), "moving_light_path", "highlight_points", "多个光源交汇会交换跟踪身份"),
            ("WORLD", "世界空间锚定书写", "World-anchored Light Writing", "场景平面上的发光文字", "绕拍光字或空间签名", "对准场景平面书写并移动镜头", "锚点稳定度", ("LIGHT-PAINT-BRUSH", "WORLD-SPACE-ANCHOR"), "world_anchored_text", "camera_pose", "锚点丢失会让文字随镜头漂移"),
            ("BEAT", "节拍星芒变色光轨", "Beat-color Pulsing Trail", "随音乐变化的历史光轨", "卡点舞蹈或音乐录像", "检测音乐强拍并启用光轨", "色相范围", ("LIGHT-PAINT-BRUSH", "BEAT-PHASE-CLOCK", "DYNAMIC-STARBURST"), "beat_driven_trail", "beat_timestamps", "变速音乐会让颜色相位偏移"),
        ),
        "behaviors": (
            ("DRAW", "屏幕拖绘", "Screen Drawing", "触摸路径逐点累积并按速度改变光轨密度", "用户在屏幕连续拖动形成笔画", "采样密度", "触摸路径被渲染为连续光轨，抬手后按设定时长衰减", "最近 64 个触摸采样点", "touch_samples", "采样稀疏会让曲线出现折角", "perceptual_effect", "光轨起止点必须与触摸事件完全对应"),
            ("MOTION", "肢体动作累积", "Body Motion Accumulation", "关节轨迹按历史姿态顺序累积成全身光绘", "人体动作覆盖全身并持续超过半秒", "历史姿态数", "手腕、脚踝和躯干关节分别拉出光绘线，组合成完整动作轮廓", "最近 36 帧人体姿态", "skeleton_history", "低置信关节会生成断裂光线", "perceptual_effect", "不同关节的光线需保持人体拓扑关系"),
            ("MOVE", "移动光源拖尾", "Moving-source Trail", "锁定光源后沿其真实运动路径生成亮度递减拖尾", "灯棒或移动光源位移超过跟踪阈值", "拖尾长度", "移动光源前端保持明亮核心，身后形成连续且逐渐变细的光轨拖尾", "最近 40 帧光源位置", "light_source_position", "高光过曝会令拖尾粘连", "perceptual_effect", "拖尾方向必须与光源运动方向一致"),
            ("ANCHOR", "镜头移动固字", "Camera-stable Writing", "书写完成后将光字固定到世界锚点并更新透视", "完成书写后移动镜头绕看文字", "文字缩放", "发光文字固定在原场景位置，镜头平移旋转后仍保持透视和遮挡", "从书写开始到录制结束", "camera_pose", "快速转身会令空间锚点短暂丢失", "perceptual_effect", "文字必须固定于世界空间而不是屏幕坐标"),
            ("PULSE", "强拍变色脉冲", "Strong-beat Color Pulse", "每个强拍推进光轨色相并产生一次宽度和亮度脉冲", "音乐节拍进入强拍区间时触发", "脉冲强度", "整条历史光轨在强拍瞬间变色并向外脉冲，拍间平滑回落", "最近 4 个节拍", "audio_onsets", "连续强拍会造成颜色过快跳变", "perceptual_effect", "色相变化与脉冲峰值必须同步到同一节拍"),
        ),
    },
    "body_motion_clones": {
        "title_zh": "身体运动分身",
        "title_en": "Body Motion Clones",
        "motifs": (
            ("TIME", "时间分身", "Time Clone", "同一人物全身轮廓", "舞蹈或走位镜头", "点选人物作为分身源", "clone_delay", ("HUMAN-TIME-CLONE", "DELAYED-CLONE"), "full_body", "person_track_history", "遮挡会让历史分身缺帧"),
            ("SHADOW", "影子分身", "Shadow Double", "人物投在地面的影子", "侧光人像或街舞", "点按地面影子", "shadow_delay", ("SHADOW-DOUBLE", "SILHOUETTE-ECHO"), "ground_plane", "shadow_mask", "真实影子与副本可能混合"),
            ("POSE", "走位剪影队列", "Pose Silhouette Queue", "连续走位的身体剪影", "走廊或空旷舞台", "检测到连续跨步姿态", "slice_spacing", ("POSE-SLICES", "MOTION-AFTERIMAGE"), "motion_path", "skeleton_history", "小幅动作时剪影难分离"),
            ("GESTURE", "手势时间排队", "Queued Gesture Echo", "挥手与手臂的局部分身", "近景手势舞", "手掌完成指定挥动", "gesture_echo_count", ("GESTURE-ECHO", "FRAME-STUTTER"), "hand_region", "hand_pose_history", "手指交叉会产生重叠"),
            ("MIRROR", "双向镜像人格", "Bidirectional Mirror Persona", "人物左右两侧的镜像身体", "对称构图人像", "用户在屏幕上划出镜像轴", "mirror_axis", ("MIRROR-PERSONA", "PERSPECTIVE-CLONE"), "symmetry_plane", "person_mask", "越过中轴时副本会粘连"),
        ),
        "behaviors": (
            ("DELAY", "延迟跟随", "Delayed Follow", "副本落后主身并按延迟逐步淡出", "人物速度超过设定阈值时触发", "延迟秒数", "主身前进时身后出现保持身份的完整动作分身", "最近 2.5 秒", "pose_keypoints", "跟踪丢失会中断队列", "perceptual_effect", "不同延迟副本要保持独立层级"),
            ("REVERSE", "逆动作回卷", "Reverse Motion Rollback", "副本播放主身刚刚完成的动作反向片段", "用户向后挥手或双击屏幕", "反向窗口", "人物身旁的分身像倒带一样收回上一个姿态", "触发前后各 18 帧", "object_track_history", "离开画面后反向内容断裂", "perceptual_effect", "反向回放不能改写当前主身动作"),
            ("STUTTER", "节奏停格", "Rhythmic Stutter", "副本在节拍间隔冻结成离散姿态", "音乐节拍连续出现两次以上", "停格间隔", "身体被切成一串按节奏跳变的动作雕塑", "最近 1.5 秒", "beat_timestamps", "切分节奏会造成姿态拥挤", "perceptual_effect", "停格姿态仍须保持人体轮廓完整"),
            ("MERGE", "相遇合身", "Meeting Merge", "两个历史分身接近时融合回主身", "分身间距小于设定距离", "融合半径", "多个延迟身体在相遇点叠合成一次发光回收", "最近 3 秒", "person_tracks", "遮挡关系会改变融合顺序", "generative_rewrite", "融合只改变副本，不替换原始人物"),
            ("SPIRAL", "螺旋走位", "Spiral Walkout", "副本沿螺旋路径排列并逐层缩小", "用户围绕人物旋转手机", "螺旋间距", "历史姿态从人物身后盘旋展开成可见运动螺旋", "最近 40 帧", "camera_trajectory", "镜头旋转与人物运动会相互污染", "perceptual_effect", "缩小副本仍需保留脸部和手势辨识度"),
        ),
    },
    "face_gaze_expression": {
        "title_zh": "面部视线表情",
        "title_en": "Face Gaze Expression",
        "motifs": (
            ("CAMERA", "摄像头对视矫正·视线矫正", "Camera Eye-contact Correction", "自拍者双眼、瞳孔与镜头方向", "自拍视频、口播或远程访谈", "依次注视屏幕校准点和摄像头", "矫正强度", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS"), "two_eye_regions", "eye_crops", "大角度侧脸会限制可自然矫正范围"),
            ("DIALOGUE", "多人对话对视重定向", "Dialogue Gaze Redirection", "对话双方的眼球、虹膜和目标人物", "双人访谈或多人对话", "检测当前说话者并选择对视对象", "重定向幅度", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS", "MULTI-PERSON-GRAPH"), "multiple_face_regions", "person_tracks", "人员交叉会导致对视目标身份交换"),
            ("GLOW", "视线点亮目标", "Gaze-lit Object", "被凝视的物体实例", "产品展示或空间互动", "视线在目标上停留达到门限", "发光半径", ("GAZE-VECTOR", "GAZE-FOCUS", "LUMINOUS-CORE"), "gaze_selected_object", "object_track", "相邻物体过近会造成注视目标跳转"),
            ("CATCHLIGHT", "眼神光跟随", "Following Catchlight", "双眼虹膜上的虚拟高光", "近景人像与自拍视频", "转头时保持视线可见并跟踪虹膜", "眼神光大小", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS", "CATCHLIGHT-RERENDER"), "iris_regions", "iris_landmarks", "眨眼闭合时高光锚点会暂时消失"),
            ("SELECT", "凝视选择特效", "Gaze Effect Selection", "画面中的候选物体与特效入口", "免手触控录像", "凝视候选目标并等待选中反馈", "选择停留时间", ("GAZE-VECTOR", "GAZE-FOCUS", "OBJECT-INSTANCE"), "gaze_ui_and_objects", "gaze_vector", "视线漂移会在候选目标间来回切换"),
        ),
        "behaviors": (
            ("CALIBRATE", "瞳孔镜头校准", "Pupil-to-camera Calibration", "校准后逐帧重定向眼球和瞳孔朝向摄像头", "完成三个校准点注视后直视屏幕内容", "瞳孔平滑度", "瞳孔与虹膜被轻量重定向到镜头方向，眼睑、头姿和人物身份保持不变", "最近 16 帧", "gaze_vector", "眨眼会短暂冻结重定向参数", "faithful_edit", "眼球重定向必须限制在自然转动范围"),
            ("REDIRECT", "对话对象重定向", "Dialogue-target Redirection", "说话人变化时把双方眼球和虹膜平滑重定向到对方脸部", "当前说话者切换或对话对象转头", "对视目标", "双方眼球与虹膜朝向被重定向到对方眼睛，形成连续虚拟对视而不改变头部姿态", "最近 24 帧", "person_relation_graph", "快速抢话会让对视目标频繁切换", "faithful_edit", "多人对话中每双眼睛必须绑定正确目标身份"),
            ("DWELL", "停留点亮", "Dwell-to-glow", "注视停留时间控制目标发光进入、保持和退出", "视线停留在同一目标超过设定时长", "停留时长", "被注视目标从边缘向中心发光，视线移开后按停留时长平滑熄灭", "注视前后各 20 帧", "dwell_duration", "凝视边界抖动会导致亮度闪烁", "perceptual_effect", "仅当前选中物体实例可以发光"),
            ("FOLLOW", "虹膜高光跟随", "Iris Catchlight Follow", "眼神光依据虹膜位置、头姿和视线方向连续滑动", "人物转头或视线横向移动", "跟随惯性", "眼神光贴着虹膜表面跟随移动并保持可见反射形状，闭眼时自然消失", "最近 12 帧", "head_pose", "侧脸时高光可能靠近眼白边界", "perceptual_effect", "左右眼高光必须保持一致的虚拟光源方向"),
            ("CONFIRM", "眨眼确认选择", "Blink-confirm Selection", "凝视完成预选后用一次眨眼确认特效对象", "候选目标出现选中环后完成一次眨眼", "确认反馈", "凝视对象先出现选中环，眨眼后该对象被明确选中并展开对应可见特效", "凝视 0.8 秒加一次眨眼", "eyelid_landmarks", "无意识眨眼可能提前确认", "perceptual_effect", "确认反馈必须与被选物体保持空间绑定"),
        ),
    },
    "time_editing": {
        "title_zh": "时间编辑",
        "title_en": "Time Editing",
        "motifs": (
            ("FREEZE", "局部时间冻结", "Local Time Freeze", "人物手部或一块场景区域", "街头动作或舞台表演", "长按要冻结的区域", "freeze_frame_index", ("LOCAL-TIME-FREEZE", "EVENT-WINDOW"), "local_region", "region_mask", "遮挡变化会暴露冻结边界"),
            ("LOOP", "局部时间循环", "Local Time Loop", "人物发梢或水面小区域", "舞蹈、风吹头发或流水", "画圈框选循环区域", "loop_duration", ("TIME-LOOP", "TIME-DECAY"), "selected_region", "loop_frame_buffer", "首尾姿态差异会跳切"),
            ("REVERSE", "局部时间倒放", "Local Time Reverse", "飞起的纸片或挥动手臂", "动作短片或魔术", "向后拖动目标轨迹", "reverse_window", ("TIME-REVERSE", "FRAME-DELAY"), "tracked_object", "object_track_history", "对象离开区域后内容会断裂"),
            ("SHUTTER", "动作快门切片", "Motion Shutter Slices", "快速转身的人体轮廓", "运动舞蹈或跑步", "手机快速旋转一次", "slice_count", ("FRAME-DELAY", "MOTION-PHASE"), "motion_path", "frame_stream", "镜头本身移动会污染切片"),
            ("BORROW", "时间借位窗口", "Borrowed Time Window", "前景人物与背景事件", "街拍或多人即兴", "检测手势事件并按住快门", "borrow_offset", ("EVENT-WINDOW", "STATE-HYSTERESIS"), "foreground_background", "event_timestamp", "事件过近会造成窗口重叠"),
        ),
        "behaviors": (
            ("HAND", "手势启动", "Gesture Start", "手势进入时渐入，保持时稳定，退出时还原", "手掌张开后握拳触发", "进入和退出阈值", "区域按动作边沿切换时间状态，周围画面保持连续播放", "进入前 8 帧至退出后 12 帧", "hand_pose", "手指遮挡会使边沿抖动", "faithful_edit", "时间边界要随区域边缘同步移动"),
            ("BEAT", "节拍切换", "Beat Switching", "每个节拍选择冻结、循环或倒放中的一个时间状态", "连续节拍强度超过门限", "节拍映射模式", "局部动作在音乐节拍处冻结又恢复，形成可见时间编舞", "最近 4 个节拍", "beat_timestamps", "变速音乐会导致相位漂移", "perceptual_effect", "切换不能破坏局部区域的运动因果"),
            ("TOUCH", "触摸擦除", "Touch Erase", "用户手指划过哪里，哪里就恢复实时帧", "触摸路径进入时间效果区域", "擦除笔刷半径", "冻结或倒放区域被手指擦出流动的当前时间窗口", "触摸前后 16 帧", "touch_samples", "快速划线会留下孔洞", "perceptual_effect", "擦除边界要有可见柔和过渡"),
            ("VOICE", "喊声解冻", "Voice Unfreeze", "声音包络上升时区域从停格向实时加速回放", "人声音量跨过上升阈值", "解冻加速度", "人物喊声越强，冻结区域越快追上当前帧", "最近 1.2 秒", "audio_waveform", "环境噪声会误解冻", "perceptual_effect", "音量映射要避免一次跳到实时画面"),
            ("SLIDER", "游标选帧", "Frame Scrub Select", "游标停留的历史帧成为局部稳定画面", "用户拖动时间游标并松手", "历史帧位置", "局部区域停在用户选中的精确姿态，背景继续移动", "可选最近 5 秒", "touch_samples", "游标跳跃会产生姿态跳变", "faithful_edit", "选帧结果必须可重复回看和微调"),
        ),
    },
    "spatial_portals": {
        "title_zh": "空间入口",
        "title_en": "Spatial Portals",
        "motifs": (
            ("MIRROR", "镜面穿越", "Mirror Traversal", "镜面、橱窗或水面反射", "街边镜面与室内拍摄", "点选一块镜面区域", "portal_depth", ("MIRROR-PORTAL", "REFLECTION"), "reflective_surface", "reflection_cues", "弱反射会与真实背景混合"),
            ("PALM", "掌中窗口", "Palm Window", "手掌之间的悬浮窗口", "旅行或朋友合拍", "双手围出矩形框", "window_scale", ("FRAME-TRAVERSAL", "WORLD-SPACE-ANCHOR"), "hand_bounded", "hand_2d_landmarks", "手指交叉会打断窗口"),
            ("FLOOR", "地面折叠门", "Floor Fold Door", "地面纹理与远处场景", "低机位走路镜头", "脚尖指向地面并停留", "fold_angle", ("SPACE-FOLD", "DEPTH-PARALLAX"), "ground_plane", "depth_map", "地面深度错误会让门悬空"),
            ("TUNNEL", "景深隧道", "Depth Tunnel", "主体背后的空间纵深", "快速推进或拉远", "双指向内捏合", "tunnel_depth", ("TUNNEL-WARP", "FRAME-TRAVERSAL"), "vanishing_axis", "crossing_depth", "消失点偏移会破坏透视"),
            ("PAGE", "房间翻页", "Room Page Turn", "墙面、门框和房间边界", "室内转身或探店", "沿门框横向划动", "page_curl", ("SPACE-FOLD", "MIRROR-PORTAL"), "architectural_plane", "camera_pose", "建筑边缘会产生折断"),
        ),
        "behaviors": (
            ("STEP", "迈步触发", "Step Trigger", "主体跨过入口平面时先遮挡再完整进入另一视角", "脚步跨过设定空间线", "入口厚度", "人物穿过镜面或窗口后，前后景遮挡关系连续交换", "跨越前后 24 帧", "body_keypoints", "腿部遮挡会使穿越断裂", "perceptual_effect", "穿越过程要让入口成为真实可见边界"),
            ("ROTATE", "旋转换景", "Rotation Scene Swap", "手机旋转超过角度时入口内世界随视角翻转", "手机绕竖轴旋转到指定角度", "旋转阈值", "入口内场景随手机转向完成连续换景，入口外保持原景", "最近 32 帧", "gyroscope", "滚动快门会造成入口边缘抖动", "generative_rewrite", "新旧空间的颜色与遮挡需要在轴线上对齐"),
            ("TOUCH", "指尖拉开", "Fingertip Pull Open", "手指拖动入口边缘时空间像布帘一样拉开", "触摸入口边缘并向外拖", "开口宽度", "入口由窄缝被拉成有厚度的可见空间洞口", "触摸后 1.5 秒", "touch_samples", "拖动过快会导致纹理拉丝", "perceptual_effect", "拉开形变需保留手指遮挡关系"),
            ("BEAT", "节拍折叠", "Beat Fold", "入口在节拍处折入、展开并短暂露出另一层画面", "音乐节拍命中入口动画", "折叠频率", "空间平面按节拍像纸片一样折叠，展开时露出后景", "最近 3 个节拍", "audio_onsets", "弱拍会令折叠不完整", "perceptual_effect", "折叠角度和入口透视要同时稳定"),
            ("GAZE", "注视穿门", "Gaze Through Door", "人物注视入口时入口逐渐变透明，移开视线后恢复", "视线停留在入口中心", "透明度响应", "入口被注视时露出其后的空间，视线移开则闭合", "注视前后各 20 帧", "gaze_vector", "视线漂移会造成透明度闪烁", "perceptual_effect", "透明变化必须限制在入口区域内"),
        ),
    },
    "virtual_light_shadow": {
        "title_zh": "虚拟光影",
        "title_en": "Virtual Light Shadow",
        "motifs": (
            ("DOUBLE", "影子分身", "Shadow Double", "地面或墙上的人物影子", "侧光街拍", "点选真实影子", "shadow_delay", ("SHADOW-RERENDER", "VIRTUAL-RIM-LIGHT"), "shadow_plane", "shadow_mask", "深色背景会吞掉影子轮廓"),
            ("SUNSET", "虚拟日落边光", "Virtual Sunset Rim", "人物头发和肩部边缘", "户外人像", "滑动虚拟太阳位置", "rim_temperature", ("VIRTUAL-RIM-LIGHT", "VIRTUAL-SPOTLIGHT"), "subject_contour", "subject_normals", "发丝分割误差会放大亮边"),
            ("FOLLOW", "移动追光圈", "Moving Follow Spot", "移动人物脚下或脸部光区", "舞台走位或夜间街拍", "点按目标并开始移动", "spot_radius", ("VIRTUAL-SPOTLIGHT", "SHADOW-RERENDER"), "tracked_subject", "target_track", "快速换向会让光区滞后"),
            ("LONG", "影子变长", "Lengthening Shadow", "主体侧后方投射的长影", "日常走路或舞蹈", "手机向侧面倾斜", "shadow_length", ("SHADOW-RERENDER", "MONOCULAR-DEPTH"), "ground_plane", "ground_plane", "缺少地面几何时影子悬空"),
            ("SCREEN", "人物投影幕", "Subject Projection Screen", "墙面上放大的主体轮廓", "室内墙面或演出场景", "框选一面墙", "projection_scale", ("SHADOW-RERENDER", "VOLUMETRIC-LIGHT"), "wall_plane", "depth_field", "墙面斜视会使投影变形"),
        ),
        "behaviors": (
            ("CLOCK", "时钟延迟", "Clock Delay", "影子比主体慢半拍移动并在停止时追上", "主体开始移动或停下时触发", "shadow_delay", "影子分身沿旧姿态延迟跟随，最后回到主体脚下", "最近 2 秒", "pose_history", "停顿太短会看不出延迟", "perceptual_effect", "影子动作必须服从地面接触点"),
            ("BEAT", "节拍闪切", "Beat Flash Cut", "光圈与影子在节拍瞬间互换明暗方向", "音频节拍强度跨过门限", "闪切宽度", "节拍处轮廓光爆亮，影子同步翻转成另一侧可见剪影", "最近 2 个节拍", "audio_onsets", "密集节拍会使画面频闪", "perceptual_effect", "明暗切换需限制峰值避免遮盖主体"),
            ("TOUCH", "指尖改光位", "Touch Light Relocation", "用户拖动光源时轮廓光和影子同步绕主体移动", "触摸并拖动虚拟光源", "光源方位", "光从左侧拖到右侧，人物亮边和地面影子连续换位", "触摸路径最近 1 秒", "touch_samples", "拖动越界会让影子出画", "faithful_edit", "光影方向必须由同一光源状态驱动"),
            ("ROTATE", "手机摆动光束", "Phone-sway Beam", "手机左右摆动时体积光束扫过人物与墙面", "手机横滚角速度超过门限", "光束锥角", "可见光束随手机摆动穿过空间，影子被光束边缘切开", "最近 18 帧", "gyroscope", "传感器漂移会令光束缓慢漂移", "perceptual_effect", "光束与主体深度遮挡不能互相穿透"),
            ("BLINK", "眨眼熄灯", "Blink Blackout", "眨眼闭合时轮廓光熄灭，睁眼后从影子边缘重新点亮", "检测完整眨眼事件", "熄灯时长", "一次眨眼让人物短暂只剩可见影子，睁眼时亮边逐圈恢复", "事件前后 14 帧", "eyelid_landmarks", "闭眼关键点消失会延长熄灯", "perceptual_effect", "熄灯期间仍需保留人物可辨识轮廓"),
        ),
    },
    "material_morph": {
        "title_zh": "材质变形",
        "title_en": "Material Morph",
        "motifs": (
            ("DISSOLVE", "材质溶解", "Material Dissolve", "人物服装或手持物", "变装、舞蹈或产品展示", "长按目标表面", "dissolve_progress", ("PIXEL-DISSOLVE", "FRAGMENTATION"), "object_surface", "dissolve_mask", "阈值过快会像硬切消失"),
            ("GLASS", "玻璃呼吸", "Breathing Glass", "人物轮廓或透明道具", "橱窗、室内人像", "手指在目标上画一圈", "refraction_strength", ("GLASS", "HOLOGRAPHIC"), "target_surface", "background_sample", "背后内容不足会显得空洞"),
            ("METAL", "液态金属", "Liquid Metal", "服饰、饰品或手臂", "未来感近景", "手机旋转到高光方向", "metallic_flow", ("METAL", "LIQUID"), "subject_region", "surface_normals", "法线跳变会令高光断裂"),
            ("PAPER", "纸片裂变", "Paper Fragmentation", "人物和背景中的海报", "街头或舞台转场", "双指向外拉开", "fragment_spread", ("PAPER", "FRAGMENTATION"), "planar_region", "surface_uv", "碎片过多会遮挡脸部"),
            ("HOLO", "全息织物", "Holographic Fabric", "衣服与头发边缘", "音乐短片或舞蹈", "节拍命中服装区域", "hue_shift", ("FABRIC", "HOLOGRAPHIC"), "garment_region", "garment_normals", "视角估计抖动会造成色带跳闪"),
        ),
        "behaviors": (
            ("EDGE", "边缘推进", "Edge Advance", "材质变化从轮廓向内部逐层推进", "目标轮廓运动速度超过门限", "推进速度", "目标先出现新材质边缘，再完整覆盖内部并留下微小碎屑", "最近 1.2 秒", "edge_map", "快速运动会留下原材质缺口", "generative_rewrite", "材质边界必须随形变保持贴合"),
            ("BEAT", "节拍脉冲", "Beat Pulse", "材质在节拍处完成一次亮度、粗糙度和颜色脉冲", "音乐节拍强度超过阈值", "脉冲幅度", "每个节拍让表面先鼓起高光再回落到新的材质状态", "最近 4 个节拍", "audio_onsets", "弱拍会造成不完整变形", "perceptual_effect", "连续脉冲不能产生随机纹理跳变"),
            ("TOUCH", "触摸溶解", "Touch Dissolve", "手指扫过区域时材质沿触摸路径逐块溶解", "触摸路径进入目标遮罩", "笔刷大小", "指尖经过处变成可见像素尘并在后方露出新材质", "触摸前后 20 帧", "touch_samples", "采样稀疏会出现锯齿轨迹", "perceptual_effect", "触摸路径与碎片出生位置必须一致"),
            ("VOICE", "声压融化", "Voice Melt", "人声越响，表面越快从硬质融成流体", "声音包络持续上升", "声压增益", "人物说话时材质随音量变软、流动并在停声后凝固", "最近 1 秒", "audio_waveform", "环境回声会延迟凝固", "perceptual_effect", "融化幅度要保持在目标遮罩内"),
            ("GHOST", "反向凝结", "Reverse Condensation", "倒放时间游标时散开的材质碎片反向回到原物体", "录后向左拖动时间游标", "凝结速度", "碎片按出生顺序回收，表面高光最后重新闭合", "最近 3 秒", "touch_samples", "游标跳跃会留下漂浮碎片", "faithful_edit", "回收顺序要与溶解过程相反且可预测"),
        ),
    },
    "particles_weather": {
        "title_zh": "粒子天气",
        "title_en": "Particles Weather",
        "motifs": (
            ("LYRIC", "歌词环绕", "Lyric Orbit", "人物头部与肩部空间", "唱歌或口播", "选择一段歌词并点选人物", "ring_radius", ("LYRIC-RING", "TEXT"), "subject_orbit", "lyric_segments", "长歌词会在环上重叠"),
            ("RAIN", "节拍雨幕", "Beat Rain Curtain", "人物前后景空间", "夜景舞蹈或街拍", "点按节拍雨幕按钮", "rain_intensity", ("RAIN", "MUSIC-SPECTRUM"), "depth_layers", "camera_motion", "雨线可能与真实雨冲突"),
            ("PETAL", "花瓣旋涡", "Petal Vortex", "手掌或人物周围", "春日人像", "手掌画圆", "vortex_strength", ("PETALS", "DUST"), "hand_centered_volume", "hand_2d_landmarks", "手掌出框会让发射点跳动"),
            ("SNOW", "雪夜呼吸", "Breathing Snow Night", "前景脸部与远景街道", "冬日自拍视频", "对镜头吹气", "snow_size", ("SNOW", "BUBBLES"), "layered_atmosphere", "mouth_shape_class", "雪片会遮住眼睛"),
            ("DUST", "尘埃聚焦", "Dust Focus", "一束光与被注视的物体", "室内窗边或展品", "注视目标两秒", "dust_density", ("DUST", "SPARKS"), "light_volume", "gaze_vector", "压缩噪声会混淆尘埃"),
        ),
        "behaviors": (
            ("ORBIT", "环绕旋转", "Orbit Rotation", "粒子沿目标圆周旋转并按距离衰减", "目标移动超过小幅位移门限", "旋转速度", "粒子围绕对象形成有深度的环并在背后被遮挡", "最近 48 帧", "target_track", "遮挡丢失会让环穿过对象", "perceptual_effect", "环的中心与目标锚点需要持续一致"),
            ("BEAT", "节拍爆发", "Beat Burst", "节拍进入时粒子密度瞬间上升，随后散落消退", "检测到强拍或副歌起点", "爆发数量", "粒子在节拍瞬间从对象边缘喷出并留下短暂亮点", "最近 1.5 秒", "audio_onsets", "连续强拍会造成粒子堆积", "perceptual_effect", "爆发与衰减要让每一拍可分辨"),
            ("GESTURE", "手势引流", "Gesture Stream", "手指方向改变粒子流向和弯曲程度", "手掌完成指定引导手势", "流向偏转", "粒子从手指尖流出，跟随手势弯折后形成可见彩带", "最近 36 帧", "hand_pose", "手势分类短暂跳变会扭流", "perceptual_effect", "发射方向与手指朝向保持可见对应"),
            ("WEATHER", "天气渐变", "Weather Gradient", "粒子天气由稀到密经历进入、维持、消散", "用户上下滑动天气强度条", "天气密度", "晴空逐步变为雨、雪或尘雾，粒子深度层同步改变", "最近 3 秒", "touch_samples", "强度快速变化会造成密度跳变", "generative_rewrite", "天气只作用于选定空间，不覆盖主体五官"),
            ("VOICE", "音量漂浮", "Volume Float", "声音包络控制粒子的上升速度和透明度", "人声或环境声超过音量阈值", "音量响应曲线", "声音越响，粒子越快上升并在顶端发亮破裂", "最近 2 秒", "audio_waveform", "噪声会造成持续漂浮", "perceptual_effect", "响应曲线要避免细小噪声持续触发"),
        ),
    },
    "world_style": {
        "title_zh": "世界风格",
        "title_en": "World Style",
        "motifs": (
            ("SEASON", "季节翻转", "Season Flip", "背景天空、植物与地面", "旅行街拍", "向上滑动季节轮盘", "season_condition", ("SEASON", "WEATHER"), "background_world", "scene_semantics", "细小植被会随机变化"),
            ("COMIC", "漫画街景", "Comic Street World", "建筑边缘与人物轮廓", "城市走路镜头", "双击画面风格按钮", "ink_density", ("VISUAL-STYLE", "BACKGROUND-WORLD"), "full_scene", "structure_guidance", "高风格强度会改写身份"),
            ("UNDERWATER", "水下城市", "Underwater City", "背景建筑和空气层", "城市夜景或水族馆", "手机向下倾斜", "caustic_motion", ("BACKGROUND-WORLD", "WEATHER"), "background_region", "scene_layout", "前景人物可能被错误覆盖"),
            ("NEON", "霓虹世界", "Neon World", "街道灯牌和主体边缘", "夜间城市或音乐短片", "点亮一块霓虹招牌", "neon_palette", ("VISUAL-STYLE", "SCENE-LIGHTING"), "scene_lighting", "scene_geometry", "新光照与真实阴影矛盾"),
            ("PAPER", "手绘舞台", "Hand-drawn Stage", "背景墙面与服装纹理", "室内表演或口播", "手指画出舞台边框", "brush_texture", ("VISUAL-STYLE", "CLOTHING"), "scene_and_clothing", "structure_guidance", "纹理会随镜头移动闪烁"),
        ),
        "behaviors": (
            ("WIPE", "横向擦换", "Horizontal Wipe", "风格世界沿用户划线方向逐步覆盖背景", "手指从画面边缘横向划过", "擦换宽度", "旧世界和新世界以一条跟随手指的可见边界交替出现", "触摸前后 1.8 秒", "touch_samples", "复杂前景边界会漏色", "generative_rewrite", "擦换边界要穿过场景但避开人物主体"),
            ("BEAT", "节拍换景", "Beat World Switch", "每个强拍推进一个风格层级并保留主体结构", "副歌强拍连续命中", "风格层级", "街景在节拍处从真实转线稿、霓虹再转水下，主体动作不断", "最近 4 个节拍", "audio_onsets", "节拍密集时风格会来不及稳定", "generative_rewrite", "跨风格切换必须保留同一空间布局"),
            ("ROTATE", "转身换季", "Turn-to-season", "相机转向不同角度时背景季节连续变化", "手机绕竖轴旋转超过阈值", "旋转换季角度", "镜头左侧仍是原季节，右侧随转身显露新季节并形成渐变边界", "最近 40 帧", "gyroscope", "滚动快门会产生季节接缝", "generative_rewrite", "接缝必须固定在世界空间而不是屏幕空间"),
            ("GAZE", "注视聚焦风格", "Gaze Style Focus", "被注视区域进入高风格强度，余下场景保持较低强度", "视线在物体上停留超过 0.6 秒", "注视风格半径", "视线扫到哪里，哪里就变成高对比线稿或霓虹，移开后缓慢恢复", "最近 2 秒", "gaze_vector", "注视漂移会令风格光斑跳动", "generative_rewrite", "风格半径需与深度和遮挡一致"),
            ("VOICE", "人声世界脉冲", "Voice World Pulse", "说话音节推动背景纹理和天空颜色脉冲", "人声包络出现连续音节", "脉冲强度", "每个音节让背景产生可见波纹、色调或云层移动，人物保持稳定", "最近 1.2 秒", "audio_waveform", "混响会令脉冲拖尾", "generative_rewrite", "背景变化要与人声节奏可感知对应"),
        ),
    },
    "audio_lyrics": {
        "title_zh": "音频歌词",
        "title_en": "Audio Lyrics",
        "motifs": (
            ("ORBIT", "歌词环绕", "Lyric Orbit", "演唱者头部和肩部", "唱歌短视频", "选择带时间戳的歌词", "ring_radius", ("LYRIC-TIMESTAMP", "GAZE-FOCUS"), "subject_orbit", "timed_lyrics", "音轨版本可能错位"),
            ("RIBBON", "声源彩带", "Sound-source Ribbons", "说话者周围的空间方向", "多人对话或采访", "点选声源方向模式", "ribbon_width", ("SOURCE-DIRECTION", "SOUND-VOLUME"), "spatial_audio_field", "microphone_channels", "混响会令方向摇摆"),
            ("MASK", "人声光谱面罩", "Vocal Spectrum Mask", "人物脸部和嘴部周围", "唱歌或说唱", "长按人脸区域", "band_gain", ("SOUND-VOLUME", "AUDIO-BEAT"), "face_region", "audio_spectrum", "低能量频段会持续抖动"),
            ("SUBTITLE", "低音地震字幕", "Bassquake Captions", "地面与悬浮字幕", "低音强的音乐片段", "选择低音频段", "quake_amount", ("AUDIO-BEAT", "LYRIC-TIMESTAMP"), "ground_and_text", "beat_timestamps", "低频噪声会误触发"),
            ("DUET", "多人接唱球", "Duet Sing-along Orbs", "两到三位演唱者之间", "合唱或接唱", "识别每位声源", "handoff_distance", ("SOURCE-DIRECTION", "MULTI-PERSON-TOUCH"), "between_people", "person_tracks", "声源重叠会交换颜色"),
        ),
        "behaviors": (
            ("TIME", "歌词逐字", "Word Timing", "歌词字符按时间戳进入、保持、消散", "播放进度到达歌词字词时间戳", "字距与入场速度", "当前歌词沿目标轮廓逐字亮起，上一句化成淡色轨迹", "当前句前后 0.5 秒", "timed_lyrics", "音轨错位会令字词提前", "perceptual_effect", "文字入场必须与歌词内容和时间顺序一致"),
            ("BEAT", "节拍弹跳", "Beat Bounce", "文字或音符在节拍处缩放弹跳并留下残影", "节拍强度跨过进入阈值", "弹跳高度", "歌词字符在每个强拍向外跳起，再回落到环绕路径", "最近 3 个节拍", "audio_onsets", "切分节奏会造成密集跳动", "perceptual_effect", "弹跳不能遮住当前演唱者的脸"),
            ("DIRECTION", "声源换边", "Source-side Handoff", "彩带和歌词从当前说话者一侧移向下一声源", "声源方向跨入另一角区", "换边时长", "说话者切换时文字沿空间方向传递到另一人物周围", "相邻声源事件间", "direction_sector", "混响会造成颜色来回切换", "perceptual_effect", "传递路径要体现两个声源的空间关系"),
            ("VOLUME", "音量成环", "Volume Ring", "音量包络控制环的厚度、亮度和半径", "声音持续超过音量门限", "音量响应曲线", "声音越响，歌词环越厚越亮，停声后按衰减曲线回落", "最近 2 秒", "audio_waveform", "环境噪声会抬高环底噪", "perceptual_effect", "环参数变化需与文字内容分离控制"),
            ("TOUCH", "歌词拖拽", "Lyric Scrub", "拖动歌词时对应历史音节和粒子回到目标位置", "用户拖动屏幕上的歌词片段", "歌词时间偏移", "歌词被拖到人物另一侧，音节轨迹按新位置重新排列", "可预览最近 8 秒", "touch_samples", "拖动过快会跳过字词", "faithful_edit", "拖拽结果要保持原歌词时间戳可回看"),
        ),
    },
    "effect_cinematography": {
        "title_zh": "特效摄影",
        "title_en": "Effect Cinematography",
        "motifs": (
            ("ZOOM", "节拍变焦", "Beat Zoom", "人物眼睛或场景中心", "音乐卡点人像", "点按焦点对象", "zoom_ratio", ("TUNNEL-WARP", "DYNAMIC-STARBURST"), "focus_center", "highlight_points", "快速变焦会放大采样锯齿"),
            ("WIPE", "遮罩擦镜", "Mask Wipe", "人物、门框或手掌边缘", "转场自拍", "手掌遮住镜头一次", "wipe_feather", ("FRAME-TRAVERSAL", "BODY-SILHOUETTE"), "foreground_boundary", "body_keypoints", "遮挡会让擦镜边界破碎"),
            ("EXPOSURE", "长曝光旋转", "Long-exposure Spin", "夜景点光源与主体边缘", "夜景旋转镜头", "手机旋转达到指定角速度", "exposure_length", ("RADIAL-TWIST", "LIGHT-PAINT-BRUSH"), "full_frame_motion", "imu_samples", "旋转过快会形成空洞"),
            ("SPLIT", "分屏追拍", "Split Chase", "同一人物的左右运动路径", "跑步或走廊追拍", "两指拉出分屏线", "split_gap", ("SPACE-FOLD", "PERSPECTIVE-CLONE"), "split_screen", "camera_trajectory", "分屏线会穿过主体关节"),
            ("FOCUS", "焦点穿刺", "Focus Pierce", "前景物体与远处人物", "前后景推拉", "点按前景和远景各一次", "focus_depth", ("DEPTH-PARALLAX", "VIRTUAL-SPOTLIGHT"), "depth_layers", "depth_map", "深度层错误会造成焦点跳跃"),
        ),
        "behaviors": (
            ("PUNCH", "镜头冲击", "Camera Punch", "触发瞬间画面向焦点方向推进并带光学冲击环", "手掌击掌或快速点按屏幕", "冲击幅度", "焦点对象在 8 帧内快速放大，边缘出现一次可见冲击波", "事件前后 16 帧", "hand_pose", "快速动作会重复触发", "perceptual_effect", "冲击结束要回到连续运动而非硬切"),
            ("BEAT", "节拍摇镜", "Beat Whip-pan", "每个节拍产生方向明确的短摇镜并保留主体", "音乐节拍命中并有相机运动", "摇镜方向", "节拍处画面沿运动方向甩出彩色边缘，下一拍回收清晰", "最近 2 个节拍", "audio_onsets", "弱拍可能没有足够运动", "perceptual_effect", "甩动方向要与相机轨迹一致"),
            ("TOUCH", "手指拉焦", "Finger Rack Focus", "手指拖动焦点从前景转到远景", "用户依次点按两个深度目标", "焦点过渡速度", "前景逐渐虚化、远景清晰并出现被选目标的高光轮廓", "最近 1 秒", "touch_samples", "深度噪声会令焦平面跳变", "perceptual_effect", "焦点过渡必须保持主体边缘完整"),
            ("ROTATE", "旋转快门", "Rotating Shutter", "手机旋转时画面按角度分片累积成扇形快门", "手机横滚角连续变化", "扇形数量", "每次旋转留下与角度对应的半透明画面扇片，停止时回收", "最近 36 帧", "gyroscope", "滚动快门和扇片会产生重影", "perceptual_effect", "扇片中心固定且不遮盖关键脸部"),
            ("BLINK", "眨眼蒙太奇", "Blink Montage", "每次眨眼切换一个短历史镜头角度或构图", "检测完整眨眼事件", "镜头片段数", "闭眼时旧镜头收缩，睁眼时新镜头从同一视线方向展开", "事件前后 12 帧", "eyelid_landmarks", "眨眼漏检会破坏节奏", "perceptual_effect", "切换保持人物身份和动作连续"),
        ),
    },
    "multi_person_interaction": {
        "title_zh": "多人互动",
        "title_en": "Multi-person Interaction",
        "motifs": (
            ("ENERGY", "多人能量传递", "Multi-person Energy Transfer", "两人手掌之间的空间", "双人合拍或舞蹈", "两人抬手互相靠近", "transfer_speed", ("MULTI-PERSON-GRAPH", "HAND-3D-TRAJECTORY"), "between_hands", "person_tracks", "手部遮挡会中断能量链"),
            ("MIRROR", "双人镜像接力", "Two-person Mirror Relay", "两个人物的对称身体动作", "双人舞或挑战视频", "两人同时进入镜像姿态", "relay_delay", ("MULTI-PERSON-GRAPH", "BODY-SKELETON"), "two_person_plane", "pose_keypoints", "人员交换位置会错配身份"),
            ("STATUE", "三人合成雕像", "Three-person Living Statue", "三个人体轮廓与接触边界", "朋友合照或舞台定格", "三人形成闭合队形", "merge_smoothness", ("MULTI-PERSON-GRAPH", "BODY-SKELETON"), "group_silhouette", "person_tracks", "肢体交叉会粘连轮廓"),
            ("SHOULDER", "碰肩爆裂", "Shoulder Contact Burst", "两人肩膀接触点", "街拍擦肩或舞蹈", "肩部距离进入接触范围", "burst_radius", ("MULTI-PERSON-GRAPH", "HAND-3D-TRAJECTORY"), "contact_zone", "person_relation_graph", "透视重叠可能误判接触"),
            ("RING", "队形环形光", "Formation Light Ring", "多人围成的中心与身体外缘", "团体舞或聚会", "三人以上进入环形队形", "ring_thickness", ("MULTI-PERSON-GRAPH", "WORLD-SPACE-ANCHOR"), "group_center", "person_tracks", "人员出框会使环形中心漂移"),
        ),
        "behaviors": (
            ("TOUCH", "接触启动", "Contact Start", "接触点亮起并沿关系图向下一位扩散", "两人的手或身体首次接触", "扩散速度", "能量从第一个接触点传到另一人的手臂，再回到两人之间", "接触前后 1.5 秒", "contact_distance", "遮挡会使扩散链断开", "perceptual_effect", "能量路径必须遵循真实接触关系"),
            ("BEAT", "节拍接力", "Beat Relay", "每个节拍把高光和粒子从当前领舞者传给下一人", "领舞者节拍动作达到峰值", "接力顺序", "人物按节拍轮流亮起，光带沿多人关系边连接", "最近 4 个节拍", "audio_onsets", "多人同时峰值会产生竞争", "perceptual_effect", "接力顺序和画面中的空间位置要一致"),
            ("GAZE", "视线连线", "Gaze Link", "两人的视线交点生成发光连接线", "双方互相注视超过停留时间", "连接线弯曲度", "视线交点被一条可弯曲的光线固定，转头时线条断开并消散", "最近 2 秒", "gaze_vector", "侧脸会令交点不稳定", "perceptual_effect", "连接线不能穿过第三个人的前景轮廓"),
            ("FORMATION", "队形呼吸", "Formation Breath", "多人队形中心随同步动作缩放并向外呼吸粒子", "两人以上动作相位相近", "呼吸幅度", "队形越整齐，中心光环越明亮并在收势时聚回每个人", "最近 1.2 秒", "pose_keypoints", "不同身高会扰乱相位", "perceptual_effect", "中心计算应对出框和遮挡稳定"),
            ("VOICE", "声源传球", "Voice Pass", "说话声形成发光球从一位人物飞向下一位", "声源方向从一人切换到另一人", "传球弧线", "每次轮到一人说话，光球沿两人空间路径飞行并停在新声源旁", "相邻发言事件间", "direction_sector", "混响会交换声源", "perceptual_effect", "光球路径需体现真实人物距离"),
        ),
    },
}


def _resolve_atom_ids(atom_ids: set[str], slugs: tuple[str, ...]) -> list[str]:
    """Resolve reviewed atom suffixes without duplicating the full IDs in specs."""

    resolved = []
    for slug in slugs:
        matches = sorted(atom_id for atom_id in atom_ids if atom_id.endswith(f"-{slug}"))
        if len(matches) != 1:
            raise ValueError(f"atom slug {slug!r} must resolve to exactly one atom: {matches}")
        resolved.append(matches[0])
    return resolved


def _stable_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _idea_from_specs(
    family: str,
    motif: tuple[str, ...],
    behavior: tuple[str, ...],
    atom_ids: set[str],
    ordinal: int,
) -> dict[str, object]:
    (
        motif_slug,
        motif_zh,
        motif_en,
        target_object,
        scenario,
        motif_trigger,
        motif_parameter,
        atom_slugs,
        spatial_scope,
        motif_signal,
        motif_failure,
    ) = motif
    (
        behavior_slug,
        behavior_zh,
        behavior_en,
        temporal_behavior,
        behavior_trigger,
        behavior_control,
        visible_behavior,
        temporal_window,
        behavior_signal,
        behavior_failure,
        generation_level,
        continuity_challenge,
    ) = behavior
    family_title_zh = IDEA_FAMILY_SPECS[family]["title_zh"]
    family_title_en = IDEA_FAMILY_SPECS[family]["title_en"]
    visible_effect = f"{motif_zh}对象{temporal_behavior}时，{visible_behavior}；{target_object}始终可见且与画面空间保持对应"
    effect_id = (
        f"FX-{family.upper().replace('_', '-')}-{motif_slug}-{behavior_slug}"
    )
    return {
        "effect_id": effect_id,
        "name_zh": f"{motif_zh}{behavior_zh}·{family_title_zh}",
        "name_en": f"{motif_en} {behavior_en} - {family_title_en}",
        "family": family,
        "visible_effect": visible_effect,
        "scenarios": [scenario],
        "target_objects": [target_object],
        "spatial_scope": [spatial_scope, "screen_composite"],
        "trigger_signals": [motif_trigger, behavior_trigger],
        "interaction": f"{motif_trigger}后，{behavior_trigger}；用户通过{behavior_control}调整{motif_parameter}。",
        "user_controls": [motif_parameter, behavior_control, "效果强度"],
        "preview_pipeline": f"低分辨率{motif_signal}与{behavior_signal}进入{temporal_behavior}预览，使用有界历史缓存和主体遮罩合成。",
        "post_pipeline": f"录制后按时间戳重建{motif_zh}，细化{spatial_scope}边缘、遮挡和{behavior_control}曲线。",
        "required_signals": _stable_unique([motif_signal, behavior_signal, "monotonic_event_timestamps"]),
        "atom_ids": _resolve_atom_ids(atom_ids, atom_slugs),
        "temporal_window": temporal_window,
        "continuity_challenges": [motif_failure, continuity_challenge],
        "edge_difficulty": "high" if ordinal % 3 else "research",
        "execution_targets": ["mobile_preview", "mobile_post"],
        "generation_level": generation_level,
        "risks": [motif_failure, behavior_failure],
        "novelty": f"把{motif_zh}的对象语义与{behavior_zh}的时序行为绑定，触发和参数共同改变可见结果，而不是只更换场景。",
        "shareability": f"短视频中能直接看见{visible_effect}，适合一键录制、回看和分享。",
        "product_value": f"作为手机录像中的{family_title_zh}创作玩法，提供{motif_parameter}与{behavior_control}两个可理解的调节入口。",
        "reference_ids": [],
        "combinable_effect_ids": [],
        "status": "idea_only",
    }


def build_ideas() -> list[dict[str, object]]:
    """Return 300 complete ideas in stable family, motif, and behavior order."""

    atoms = build_atoms()
    atom_ids = {atom["atom_id"] for atom in atoms}
    ideas = []
    ordinal = 0
    for family in IDEA_FAMILY_ORDER:
        family_spec = IDEA_FAMILY_SPECS[family]
        for motif in family_spec["motifs"]:
            for behavior in family_spec["behaviors"]:
                ideas.append(_idea_from_specs(family, motif, behavior, atom_ids, ordinal))
                ordinal += 1
    return ideas


def _idea_fingerprint(idea: Mapping[str, object]) -> tuple[object, ...]:
    normalize = lambda value: " ".join(str(value).split()).casefold()
    return (
        normalize(idea["visible_effect"]),
        tuple(sorted(idea["trigger_signals"])),
        tuple(sorted(idea["user_controls"])),
        tuple(sorted(idea["atom_ids"])),
    )


def validate_ideas(ideas: list[dict[str, object]], atom_ids: set[str]) -> dict[str, object]:
    """Validate complete idea records, family distribution, and semantic uniqueness."""

    if not isinstance(ideas, list):
        raise ValueError("ideas must be a list")
    expected_fields = set(IDEA_FIELDS)
    for index, idea in enumerate(ideas):
        if not isinstance(idea, Mapping):
            raise ValueError(f"idea[{index}] must be a mapping")
        if set(idea) != expected_fields:
            raise ValueError(f"idea[{index}] fields must match schema fields exactly")
        try:
            schema.validate_idea(idea, atom_ids)
        except ValueError as exc:
            effect_id = idea.get("effect_id", f"index {index}")
            raise ValueError(f"schema validation failed for {effect_id}: {exc}") from exc

    for field in ("effect_id", "name_zh", "name_en"):
        duplicates = _find_duplicates(idea[field] for idea in ideas)
        if duplicates:
            raise ValueError(f"duplicate {field}: {', '.join(duplicates)}")

    family_counts = Counter(idea["family"] for idea in ideas)
    unknown_families = sorted(set(family_counts) - set(IDEA_FAMILY_ORDER))
    if unknown_families:
        raise ValueError(f"unknown idea families: {', '.join(unknown_families)}")
    observed_order = tuple(dict.fromkeys(idea["family"] for idea in ideas))
    if observed_order != IDEA_FAMILY_ORDER:
        raise ValueError("idea families are not in stable IDEA_FAMILY_ORDER")

    fingerprints = [_idea_fingerprint(idea) for idea in ideas]
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("idea semantic fingerprints must be unique")

    return {
        "count": len(ideas),
        "family_counts": dict(family_counts),
        "fingerprint_count": len(fingerprints),
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


def write_ideas_jsonl(rows: list[dict], path: Path = IDEA_OUTPUT) -> None:
    """Write complete idea records as compact deterministic UTF-8 JSONL."""

    atom_ids = {atom["atom_id"] for atom in build_atoms()}
    validate_ideas(rows, atom_ids)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            output.write("\n")


def main(
    argv: list[str] | None = None,
    *,
    atom_output: Path = ATOM_OUTPUT,
    idea_output: Path = IDEA_OUTPUT,
) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--atoms-only",
        action="store_true",
        help="Generate only effect atoms; the default also generates complete ideas.",
    )
    args = parser.parse_args(argv)

    atoms = build_atoms()
    atom_report = validate_atoms(atoms)
    write_jsonl(atoms, atom_output)
    if args.atoms_only:
        print(f"wrote {atom_report['count']} atoms to {atom_output}")
        return

    ideas = build_ideas()
    idea_report = validate_ideas(ideas, {atom["atom_id"] for atom in atoms})
    write_ideas_jsonl(ideas, idea_output)
    print(f"wrote {atom_report['count']} atoms to {atom_output}")
    print(f"wrote {idea_report['count']} ideas to {idea_output}")


if __name__ == "__main__":
    main()
