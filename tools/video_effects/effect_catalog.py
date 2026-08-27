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

# A motif describes the object and its spatial meaning. The reviewed behavior
# table below explicitly decides which temporal responses belong to each motif.
IDEA_FAMILY_SPECS = {
    "light_trails_optics": {
        "title_zh": "光轨光学",
        "title_en": "Light Trails Optics",
        "motifs": (
            ("FINGER", "指尖实时光绘轨迹", "Finger Screen Light Painting", "屏幕触摸路径与指尖", "手绘签名或涂鸦录像", "用户在屏幕按下并拖动指尖", "笔刷宽度", ("LIGHT-PAINT-BRUSH", "TOUCH-DRAW"), "screen_touch_path", "touch_samples", "手指离开屏幕会中断连续笔画"),
            ("BODY", "人体肢体光绘", "Body Limb Light Painting", "人体关节与四肢运动路径", "舞蹈、体操或运动录像", "全身进入画面并开始动作", "骨骼光线粗细", ("LIGHT-PAINT-BRUSH", "BODY-SKELETON"), "body_motion_path", "pose_keypoints", "肢体交叉会让关节轨迹错连"),
            ("SOURCE", "手持灯棒移动光轨", "Handheld Moving Light Trail", "手持灯棒或移动点光源", "夜景灯棒与车灯录像", "锁定手持灯棒或移动光源", "光源阈值", ("LIGHT-PAINT-BRUSH", "LUMINOUS-CORE"), "moving_light_path", "highlight_points", "多个光源交汇会交换跟踪身份"),
            ("WORLD", "世界空间锚定书写", "World-anchored Light Writing", "场景平面上的发光文字", "绕拍光字或空间签名", "对准场景平面书写并移动镜头", "锚点稳定度", ("LIGHT-PAINT-BRUSH", "WORLD-SPACE-ANCHOR"), "world_anchored_text", "camera_pose", "锚点丢失会让文字随镜头漂移"),
            ("BEAT", "节拍星芒变色光轨", "Beat-color Pulsing Trail", "随音乐变化的历史光轨", "卡点舞蹈或音乐录像", "检测音乐强拍并启用光轨", "色相范围", ("LIGHT-PAINT-BRUSH", "BEAT-PHASE-CLOCK"), "beat_driven_trail", "beat_timestamps", "变速音乐会让颜色相位偏移"),
        ),
    },
    "body_motion_clones": {
        "title_zh": "身体运动分身",
        "title_en": "Body Motion Clones",
        "motifs": (
            ("TIME", "时间分身", "Time Clone", "同一人物全身轮廓", "舞蹈或走位镜头", "点选人物作为分身源", "clone_delay", ("HUMAN-TIME-CLONE",), "full_body", "person_track_history", "遮挡会让历史分身缺帧"),
            ("SHADOW", "影子分身", "Shadow Double", "人物投在地面的影子", "侧光人像或街舞", "点按地面影子", "shadow_delay", ("SHADOW-DOUBLE",), "ground_plane", "shadow_mask", "真实影子与副本可能混合"),
            ("POSE", "走位剪影队列", "Pose Silhouette Queue", "连续走位的身体剪影", "走廊或空旷舞台", "检测到连续跨步姿态", "slice_spacing", ("POSE-SLICES",), "motion_path", "skeleton_history", "小幅动作时剪影难分离"),
            ("GESTURE", "手势时间排队", "Queued Gesture Echo", "挥手与手臂的局部分身", "近景手势舞", "手掌完成指定挥动", "gesture_echo_count", ("GESTURE-ECHO",), "hand_region", "hand_pose_history", "手指交叉会产生重叠"),
            ("MIRROR", "双向镜像人格", "Bidirectional Mirror Persona", "人物左右两侧的镜像身体", "对称构图人像", "用户在屏幕上划出镜像轴", "mirror_axis", ("MIRROR-PERSONA",), "symmetry_plane", "person_mask", "越过中轴时副本会粘连"),
        ),
    },
    "face_gaze_expression": {
        "title_zh": "面部视线表情",
        "title_en": "Face Gaze Expression",
        "motifs": (
            ("CAMERA", "摄像头对视矫正·视线矫正", "Camera Eye-contact Correction", "自拍者双眼、瞳孔与镜头方向", "自拍视频、口播或远程访谈", "依次注视屏幕校准点和摄像头", "矫正强度", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS"), "two_eye_regions", "eye_crops", "大角度侧脸会限制可自然矫正范围"),
            ("DIALOGUE", "多人对话对视重定向", "Dialogue Gaze Redirection", "对话双方的眼球、虹膜和目标人物", "双人访谈或多人对话", "检测当前说话者并选择对视对象", "重定向幅度", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS", "MULTI-PERSON-GRAPH"), "multiple_face_regions", "person_tracks", "人员交叉会导致对视目标身份交换"),
            ("GLOW", "视线点亮目标", "Gaze-lit Object", "被凝视的物体实例", "产品展示或空间互动", "视线在目标上停留达到门限", "发光半径", ("GAZE-VECTOR", "GAZE-FOCUS"), "gaze_selected_object", "object_track", "相邻物体过近会造成注视目标跳转"),
            ("CATCHLIGHT", "眼神光跟随", "Following Catchlight", "双眼虹膜上的虚拟高光", "近景人像与自拍视频", "转头时保持视线可见并跟踪虹膜", "眼神光大小", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS", "CATCHLIGHT-RERENDER"), "iris_regions", "iris_landmarks", "眨眼闭合时高光锚点会暂时消失"),
            ("SELECT", "凝视选择特效", "Gaze Effect Selection", "画面中的候选物体与特效入口", "免手触控录像", "凝视候选目标并等待选中反馈", "选择停留时间", ("GAZE-VECTOR", "GAZE-FOCUS", "OBJECT-INSTANCE"), "gaze_ui_and_objects", "gaze_vector", "视线漂移会在候选目标间来回切换"),
        ),
    },
    "time_editing": {
        "title_zh": "时间编辑",
        "title_en": "Time Editing",
        "motifs": (
            ("FREEZE", "局部时间冻结", "Local Time Freeze", "人物手部或一块场景区域", "街头动作或舞台表演", "长按要冻结的区域", "freeze_frame_index", ("LOCAL-TIME-FREEZE",), "local_region", "region_mask", "遮挡变化会暴露冻结边界"),
            ("LOOP", "局部时间循环", "Local Time Loop", "人物发梢或水面小区域", "舞蹈、风吹头发或流水", "画圈框选循环区域", "loop_duration", ("TIME-LOOP",), "selected_region", "loop_frame_buffer", "首尾姿态差异会跳切"),
            ("REVERSE", "局部时间倒放", "Local Time Reverse", "飞起的纸片或挥动手臂", "动作短片或魔术", "向后拖动目标轨迹", "reverse_window", ("TIME-REVERSE",), "tracked_object", "object_track_history", "对象离开区域后内容会断裂"),
            ("SHUTTER", "动作快门切片", "Motion Shutter Slices", "快速转身的人体轮廓", "运动舞蹈或跑步", "手机快速旋转一次", "slice_count", ("FRAME-DELAY",), "motion_path", "frame_stream", "镜头本身移动会污染切片"),
            ("BORROW", "时间借位窗口", "Borrowed Time Window", "前景人物与背景事件", "街拍或多人即兴", "检测手势事件并按住快门", "borrow_offset", ("EVENT-WINDOW",), "foreground_background", "event_timestamp", "事件过近会造成窗口重叠"),
        ),
    },
    "spatial_portals": {
        "title_zh": "空间入口",
        "title_en": "Spatial Portals",
        "motifs": (
            ("MIRROR", "镜面穿越", "Mirror Traversal", "镜面、橱窗或水面反射", "街边镜面与室内拍摄", "点选一块镜面区域", "portal_depth", ("MIRROR-PORTAL", "REFLECTION"), "reflective_surface", "reflection_cues", "弱反射会与真实背景混合"),
            ("PALM", "掌中窗口", "Palm Window", "手掌之间的悬浮窗口", "旅行或朋友合拍", "双手围出矩形框", "window_scale", ("FRAME-TRAVERSAL",), "hand_bounded", "hand_2d_landmarks", "手指交叉会打断窗口"),
            ("FLOOR", "地面折叠门", "Floor Fold Door", "地面纹理与远处场景", "低机位走路镜头", "脚尖指向地面并停留", "fold_angle", ("SPACE-FOLD",), "ground_plane", "depth_map", "地面深度错误会让门悬空"),
            ("TUNNEL", "景深隧道", "Depth Tunnel", "主体背后的空间纵深", "快速推进或拉远", "双指向内捏合", "tunnel_depth", ("TUNNEL-WARP",), "vanishing_axis", "crossing_depth", "消失点偏移会破坏透视"),
            ("PAGE", "房间翻页", "Room Page Turn", "墙面、门框和房间边界", "室内转身或探店", "沿门框横向划动", "page_curl", ("SPACE-FOLD",), "architectural_plane", "camera_pose", "建筑边缘会产生折断"),
        ),
    },
    "virtual_light_shadow": {
        "title_zh": "虚拟光影",
        "title_en": "Virtual Light Shadow",
        "motifs": (
            ("DOUBLE", "影子分身", "Shadow Double", "地面或墙上的人物影子", "侧光街拍", "点选真实影子", "shadow_delay", ("SHADOW-RERENDER", "SHADOW-DOUBLE"), "shadow_plane", "shadow_mask", "深色背景会吞掉影子轮廓"),
            ("SUNSET", "虚拟日落边光", "Virtual Sunset Rim", "人物头发和肩部边缘", "户外人像", "滑动虚拟太阳位置", "rim_temperature", ("VIRTUAL-RIM-LIGHT",), "subject_contour", "subject_normals", "发丝分割误差会放大亮边"),
            ("FOLLOW", "移动追光圈", "Moving Follow Spot", "移动人物脚下或脸部光区", "舞台走位或夜间街拍", "点按目标并开始移动", "spot_radius", ("VIRTUAL-SPOTLIGHT",), "tracked_subject", "target_track", "快速换向会让光区滞后"),
            ("LONG", "影子变长", "Lengthening Shadow", "主体侧后方投射的长影", "日常走路或舞蹈", "手机向侧面倾斜", "shadow_length", ("SHADOW-RERENDER",), "ground_plane", "ground_plane", "缺少地面几何时影子悬空"),
            ("SCREEN", "人物投影幕", "Subject Projection Screen", "墙面上放大的主体轮廓", "室内墙面或演出场景", "框选一面墙", "projection_scale", ("SHADOW-RERENDER",), "wall_plane", "depth_field", "墙面斜视会使投影变形"),
        ),
    },
    "material_morph": {
        "title_zh": "材质变形",
        "title_en": "Material Morph",
        "motifs": (
            ("DISSOLVE", "材质溶解", "Material Dissolve", "人物服装或手持物", "变装、舞蹈或产品展示", "长按目标表面", "dissolve_progress", ("PIXEL-DISSOLVE",), "object_surface", "dissolve_mask", "阈值过快会像硬切消失"),
            ("GLASS", "玻璃呼吸", "Breathing Glass", "人物轮廓或透明道具", "橱窗、室内人像", "手指在目标上画一圈", "refraction_strength", ("GLASS",), "target_surface", "background_sample", "背后内容不足会显得空洞"),
            ("METAL", "液态金属", "Liquid Metal", "服饰、饰品或手臂", "未来感近景", "手机旋转到高光方向", "metallic_flow", ("METAL",), "subject_region", "surface_normals", "法线跳变会令高光断裂"),
            ("PAPER", "纸片裂变", "Paper Fragmentation", "人物和背景中的海报", "街头或舞台转场", "双指向外拉开", "fragment_spread", ("PAPER",), "planar_region", "surface_uv", "碎片过多会遮挡脸部"),
            ("HOLO", "全息织物", "Holographic Fabric", "衣服与头发边缘", "音乐短片或舞蹈", "节拍命中服装区域", "hue_shift", ("FABRIC", "HOLOGRAPHIC"), "garment_region", "garment_normals", "视角估计抖动会造成色带跳闪"),
        ),
    },
    "particles_weather": {
        "title_zh": "粒子天气",
        "title_en": "Particles Weather",
        "motifs": (
            ("LYRIC", "歌词环绕", "Lyric Orbit", "人物头部与肩部空间", "唱歌或口播", "选择一段歌词并点选人物", "ring_radius", ("LYRIC-RING", "TEXT"), "subject_orbit", "lyric_segments", "长歌词会在环上重叠"),
            ("RAIN", "节拍雨幕", "Beat Rain Curtain", "人物前后景空间", "夜景舞蹈或街拍", "点按节拍雨幕按钮", "rain_intensity", ("RAIN",), "depth_layers", "camera_motion", "雨线可能与真实雨冲突"),
            ("PETAL", "花瓣旋涡", "Petal Vortex", "手掌或人物周围", "春日人像", "手掌画圆", "vortex_strength", ("PETALS",), "hand_centered_volume", "hand_2d_landmarks", "手掌出框会让发射点跳动"),
            ("SNOW", "雪夜呼吸", "Breathing Snow Night", "前景脸部与远景街道", "冬日自拍视频", "对镜头吹气", "snow_size", ("SNOW",), "layered_atmosphere", "mouth_shape_class", "雪片会遮住眼睛"),
            ("DUST", "尘埃聚焦", "Dust Focus", "一束光与被注视的物体", "室内窗边或展品", "注视目标两秒", "dust_density", ("DUST",), "light_volume", "gaze_vector", "压缩噪声会混淆尘埃"),
        ),
    },
    "world_style": {
        "title_zh": "世界风格",
        "title_en": "World Style",
        "motifs": (
            ("SEASON", "季节翻转", "Season Flip", "背景天空、植物与地面", "旅行街拍", "向上滑动季节轮盘", "season_condition", ("SEASON",), "background_world", "scene_semantics", "细小植被会随机变化"),
            ("COMIC", "漫画街景", "Comic Street World", "建筑边缘与人物轮廓", "城市走路镜头", "双击画面风格按钮", "ink_density", ("VISUAL-STYLE",), "full_scene", "structure_guidance", "高风格强度会改写身份"),
            ("UNDERWATER", "水下城市", "Underwater City", "背景建筑和空气层", "城市夜景或水族馆", "手机向下倾斜", "caustic_motion", ("BACKGROUND-WORLD",), "background_region", "scene_layout", "前景人物可能被错误覆盖"),
            ("NEON", "霓虹世界", "Neon World", "街道灯牌和主体边缘", "夜间城市或音乐短片", "点亮一块霓虹招牌", "neon_palette", ("VISUAL-STYLE",), "scene_lighting", "scene_geometry", "新光照与真实阴影矛盾"),
            ("PAPER", "手绘舞台", "Hand-drawn Stage", "背景墙面与服装纹理", "室内表演或口播", "手指画出舞台边框", "brush_texture", ("VISUAL-STYLE",), "scene_and_clothing", "structure_guidance", "纹理会随镜头移动闪烁"),
        ),
    },
    "audio_lyrics": {
        "title_zh": "音频歌词",
        "title_en": "Audio Lyrics",
        "motifs": (
            ("ORBIT", "歌词环绕", "Lyric Orbit", "演唱者头部和肩部", "唱歌短视频", "选择带时间戳的歌词", "ring_radius", ("LYRIC-TIMESTAMP", "LYRIC-RING"), "subject_orbit", "timed_lyrics", "音轨版本可能错位"),
            ("RIBBON", "声源彩带", "Sound-source Ribbons", "说话者周围的空间方向", "多人对话或采访", "点选声源方向模式", "ribbon_width", ("SOURCE-DIRECTION",), "spatial_audio_field", "microphone_channels", "混响会令方向摇摆"),
            ("MASK", "人声光谱面罩", "Vocal Spectrum Mask", "人物脸部和嘴部周围", "唱歌或说唱", "长按人脸区域", "band_gain", ("MUSIC-SPECTRUM",), "face_region", "audio_spectrum", "低能量频段会持续抖动"),
            ("SUBTITLE", "低音地震字幕", "Bassquake Captions", "地面与悬浮字幕", "低音强的音乐片段", "选择低音频段", "quake_amount", ("TEXT",), "ground_and_text", "beat_timestamps", "低频噪声会误触发"),
            ("DUET", "多人接唱球", "Duet Sing-along Orbs", "两到三位演唱者之间", "合唱或接唱", "识别每位声源", "handoff_distance", ("MULTI-PERSON-GRAPH",), "between_people", "person_tracks", "声源重叠会交换颜色"),
        ),
    },
    "effect_cinematography": {
        "title_zh": "特效摄影",
        "title_en": "Effect Cinematography",
        "motifs": (
            ("ZOOM", "节拍变焦", "Beat Zoom", "人物眼睛或场景中心", "音乐卡点人像", "点按焦点对象", "zoom_ratio", ("TUNNEL-WARP",), "focus_center", "highlight_points", "快速变焦会放大采样锯齿"),
            ("WIPE", "遮罩擦镜", "Mask Wipe", "人物、门框或手掌边缘", "转场自拍", "手掌遮住镜头一次", "wipe_feather", ("FRAME-TRAVERSAL",), "foreground_boundary", "body_keypoints", "遮挡会让擦镜边界破碎"),
            ("EXPOSURE", "长曝光旋转", "Long-exposure Spin", "夜景点光源与主体边缘", "夜景旋转镜头", "手机旋转达到指定角速度", "exposure_length", ("RADIAL-TWIST", "LIGHT-PAINT-BRUSH"), "full_frame_motion", "imu_samples", "旋转过快会形成空洞"),
            ("SPLIT", "分屏追拍", "Split Chase", "同一人物的左右运动路径", "跑步或走廊追拍", "两指拉出分屏线", "split_gap", ("SPACE-FOLD",), "split_screen", "camera_trajectory", "分屏线会穿过主体关节"),
            ("FOCUS", "焦点穿刺", "Focus Pierce", "前景物体与远处人物", "前后景推拉", "点按前景和远景各一次", "focus_depth", ("DEPTH-PARALLAX",), "depth_layers", "depth_map", "深度层错误会造成焦点跳跃"),
        ),
    },
    "multi_person_interaction": {
        "title_zh": "多人互动",
        "title_en": "Multi-person Interaction",
        "motifs": (
            ("ENERGY", "多人能量传递", "Multi-person Energy Transfer", "两人手掌之间的空间", "双人合拍或舞蹈", "两人抬手互相靠近", "transfer_speed", ("MULTI-PERSON-GRAPH",), "between_hands", "person_tracks", "手部遮挡会中断能量链"),
            ("MIRROR", "双人镜像接力", "Two-person Mirror Relay", "两个人物的对称身体动作", "双人舞或挑战视频", "两人同时进入镜像姿态", "relay_delay", ("MULTI-PERSON-GRAPH", "BODY-SKELETON"), "two_person_plane", "pose_keypoints", "人员交换位置会错配身份"),
            ("STATUE", "三人合成雕像", "Three-person Living Statue", "三个人体轮廓与接触边界", "朋友合照或舞台定格", "三人形成闭合队形", "merge_smoothness", ("MULTI-PERSON-GRAPH", "BODY-SKELETON"), "group_silhouette", "person_tracks", "肢体交叉会粘连轮廓"),
            ("SHOULDER", "碰肩爆裂", "Shoulder Contact Burst", "两人肩膀接触点", "街拍擦肩或舞蹈", "肩部距离进入接触范围", "burst_radius", ("MULTI-PERSON-GRAPH",), "contact_zone", "person_relation_graph", "透视重叠可能误判接触"),
            ("RING", "队形环形光", "Formation Light Ring", "多人围成的中心与身体外缘", "团体舞或聚会", "三人以上进入环形队形", "ring_thickness", ("MULTI-PERSON-GRAPH",), "group_center", "person_tracks", "人员出框会使环形中心漂移"),
        ),
    },
}


# Each motif owns five reviewed behaviors. A behavior row contains:
# slug, Chinese name, English name, trigger, control, visible result, atom deps.
# The generator traverses only these explicit rows; it never forms a Cartesian
# product between unrelated motif and behavior pools.
IDEA_COMPATIBLE_BEHAVIORS = {
    "light_trails_optics": {
        "FINGER": (
            ("DRAW", "屏幕拖绘", "Screen Drawing", "用户在屏幕连续拖动形成笔画", "采样密度", "触摸路径被渲染为连续光轨，抬手后按设定时长衰减", ("TOUCH-DRAW",)),
            ("FADE", "指尖渐隐", "Finger Trail Fade", "完成一段触摸笔画并抬手", "渐隐时长", "最后一个触摸点开始向笔画起点逐段熄灭光轨", ("TIME-DECAY",)),
            ("REVERSE", "指尖倒擦", "Finger Reverse Erase", "向左拖动录后时间游标", "倒擦速度", "屏幕光轨按原触摸采样的相反顺序逐段回收", ("TIME-REVERSE",)),
            ("PRESSURE", "速度变宽", "Speed-sensitive Width", "指尖拖动速度跨过快慢阈值", "笔刷宽度响应", "慢画段变粗而快速段变细，整条触摸光轨宽度连续变化", ("TRAJECTORY-ACCUMULATION",)),
            ("SCREENBEAT", "指绘节拍闪色", "Finger Beat Flash", "触摸绘制期间检测到音乐强拍", "闪色幅度", "已画触摸光轨在强拍瞬间闪色，未触摸区域保持原画面", ("AUDIO-BEAT",)),
        ),
        "BODY": (
            ("MOTION", "肢体动作累积", "Body Motion Accumulation", "人体动作覆盖全身并持续超过半秒", "历史姿态数", "手腕、脚踝和躯干关节分别拉出光绘线，组合成完整动作轮廓", ("BODY-SKELETON",)),
            ("JOINT", "关节分色", "Joint Color Coding", "检测到手腕、脚踝和头部同时运动", "关节配色", "不同关节沿各自轨迹绘出不同颜色并保持人体拓扑", ("MOTION-HISTORY",)),
            ("POSEFREEZE", "姿态定格光字", "Pose Freeze Glyph", "人体进入指定姿态并保持", "定格保持时间", "关节光轨在姿态峰值冻结成完整人体光字，恢复动作后逐渐消散", ("BODY-POSE", "LOCAL-TIME-FREEZE")),
            ("BODYBEAT", "舞步节拍光绘", "Dance Beat Painting", "身体动作峰值与音乐强拍重合", "节拍增益", "每次强拍只累积当前肢体段，连续节拍拼成分段人体光绘", ("AUDIO-BEAT", "MOTION-PHASE")),
            ("SILHOUETTE", "轮廓扫光", "Silhouette Sweep", "全身轮廓连续移动穿过画面", "轮廓光宽度", "身体外轮廓沿运动方向留下闭合光绘，内部关节保持可见", ("BODY-SILHOUETTE",)),
        ),
        "SOURCE": (
            ("MOVE", "移动光源拖尾", "Moving-source Trail", "灯棒或移动光源位移超过跟踪阈值", "拖尾长度", "移动光源前端保持明亮核心，身后形成连续且逐渐变细的光轨拖尾", ("LUMINOUS-CORE",)),
            ("STAR", "灯棒星芒节点", "Light-stick Star Nodes", "灯棒运动速度降到局部最低点", "星芒射线数", "拖尾转折点绽放星芒节点，移动段仍保持连续光线", ("DYNAMIC-STARBURST",)),
            ("FLARE", "光源镜头鬼影", "Source Flare Ghosts", "移动光源靠近画面边缘或中心轴", "鬼影间距", "光轨前端沿光源到画面中心的轴线生成可见镜头鬼影", ("LENS-FLARE",)),
            ("SOURCEREVERSE", "灯棒轨迹回卷", "Source Trail Rewind", "灯棒停止后向反方向挥动", "回卷窗口", "旧光轨沿真实运动路径倒序收回到灯棒亮点", ("TIME-REVERSE",)),
            ("SOURCEORBIT", "环绕光源立体轨迹", "Orbiting Source Trail", "镜头围绕手持灯棒连续移动", "深度分层", "灯棒轨迹按主体前后关系分层，绕过身体形成立体光环", ("MONOCULAR-DEPTH", "CAMERA-MOTION")),
        ),
        "WORLD": (
            ("ANCHOR", "镜头移动固字", "Camera-stable Writing", "完成书写后移动镜头绕看文字", "文字缩放", "发光文字固定在原场景位置，镜头平移旋转后仍保持透视和遮挡", ("WORLD-SPACE-ANCHOR",)),
            ("OCCLUDE", "空间文字遮挡", "Anchored Text Occlusion", "人物从锚定光字前方经过", "遮挡羽化", "人物经过时遮住光字，离开后原位置文字完整显现", ("MONOCULAR-DEPTH", "FOREGROUND")),
            ("PARALLAX", "空间字视差", "Writing Parallax", "手机横向移动观察锚定文字", "视差幅度", "光字各笔画按虚拟深度产生不同视差但仍固定于场景", ("DEPTH-PARALLAX",)),
            ("ROTATEWORD", "绕字旋转", "Orbit Written Word", "手机围绕锚定文字旋转超过设定角度", "透视响应", "发光文字随观察角度更新厚度和透视，不跟随屏幕漂移", ("PHONE-ROTATION",)),
            ("WORLDFADE", "远离渐隐光字", "Distance-faded Writing", "镜头远离空间锚点超过距离阈值", "距离衰减", "锚定文字随真实观察距离缩小并渐隐，靠近后在原位恢复", ("CAMERA-MOTION", "TIME-DECAY")),
        ),
        "BEAT": (
            ("PULSE", "强拍变色脉冲", "Strong-beat Color Pulse", "音乐节拍进入强拍区间时触发", "脉冲强度", "整条历史光轨在强拍瞬间变色并向外脉冲，拍间平滑回落", ("BEAT-PHASE-CLOCK", "DYNAMIC-STARBURST")),
            ("COLOR", "频段分色光轨", "Band-colored Trail", "低中高频段能量主导关系发生变化", "色相范围", "光轨按当前主导频段切换颜色并保持拍间连续过渡", ("MUSIC-SPECTRUM",)),
            ("STUTTERTRAIL", "节拍停格轨迹", "Beat Stutter Trail", "连续两个强拍之间进入停格窗口", "停格间隔", "光轨在每拍冻结一段位置，下一拍跳到新段形成节奏切片", ("FRAME-STUTTER", "AUDIO-BEAT")),
            ("DECAYBEAT", "拍间呼吸衰减", "Inter-beat Breathing Decay", "节拍相位从峰值进入回落阶段", "拍间衰减", "光轨在强拍扩张、拍间收窄并按相位渐暗", ("TIME-DECAY", "BEAT-PHASE-CLOCK")),
            ("BURST", "强拍星芒喷发", "Beat Starburst Burst", "副歌首个强拍或重拍出现", "星芒长度", "光轨拐点同时爆发星芒射线，随后回落为原有轨迹", ("DYNAMIC-STARBURST", "AUDIO-BEAT")),
        ),
    },
    "body_motion_clones": {
        "TIME": (
            ("DELAY", "延迟跟随", "Delayed Follow", "人物速度超过设定阈值", "延迟秒数", "完整时间分身沿主身旧路径延迟跟随并逐步淡出", ("DELAYED-CLONE",)),
            ("REVERSE", "逆动作分身", "Reverse Clone", "主身完成一段动作后向后挥手", "反向窗口", "时间分身在主身旁倒序回放刚完成的动作", ("TIME-REVERSE",)),
            ("TIMESTUTTER", "时间分身停格", "Time-clone Stutter", "音乐连续强拍到达", "停格间隔", "每拍采样一个完整人物分身并固定在对应历史位置", ("FRAME-STUTTER", "AUDIO-BEAT")),
            ("TIMEMERGE", "分身回收", "Clone Rejoin", "主身回到最早分身附近", "回收半径", "历史时间分身按时间顺序融合回当前主身", ("IDENTITY-MEMORY",)),
            ("TIMEPATH", "路径分身队列", "Path Clone Queue", "人物连续走过可见路径", "队列间距", "时间分身沿真实走位路径等距排列并保持动作时序", ("MOTION-HISTORY",)),
        ),
        "SHADOW": (
            ("SHADOWDELAY", "影子延迟分身", "Delayed Shadow Double", "主体开始移动而真实影子可见", "影子延迟", "影子分身落后主体动作并在停下后追到脚下", ("SHADOW-DOUBLE",)),
            ("SHADOWREVERSE", "影子逆动作", "Reverse Shadow", "主体完成动作并踏回原地", "反向时长", "影子分身倒序表演上一段动作，主体保持当前时间", ("TIME-REVERSE", "SHADOW")),
            ("SHADOWSPLIT", "影子多重裂变", "Shadow Split", "主体姿态达到动作峰值", "影子数量", "一个真实影子裂成多层延迟剪影并向不同方向展开", ("SILHOUETTE-ECHO",)),
            ("SHADOWTOUCH", "踩影回收", "Step-on Shadow Merge", "主体脚步进入影子分身区域", "接触阈值", "脚踩到影子分身时该分身从接触点收缩回主体", ("BODY-POSE", "STATE-HYSTERESIS")),
            ("SHADOWBEAT", "节拍影子舞", "Beat Shadow Dance", "主体动作峰值命中强拍", "节拍延迟", "影子分身按下一拍重复主体上一拍动作", ("AUDIO-BEAT", "MOTION-PHASE")),
        ),
        "POSE": (
            ("POSEQUEUE", "姿态切片队列", "Pose Slice Queue", "检测到连续跨步姿态", "切片间距", "连续全身姿态沿走位方向排成可见剪影队列", ("POSE-SLICES",)),
            ("POSECOLOR", "姿态阶段分色", "Pose Phase Colors", "动作进入起势、峰值和收势阶段", "阶段配色", "不同动作阶段的姿态切片显示不同颜色并保持顺序", ("MOTION-PHASE",)),
            ("POSEFREEZE", "峰值姿态雕塑", "Peak Pose Statue", "全身动作达到速度峰值后短暂停顿", "雕塑保持时长", "峰值姿态冻结成实体感分身，主身继续下一动作", ("LOCAL-TIME-FREEZE",)),
            ("POSEDEPTH", "纵深姿态阶梯", "Depth Pose Steps", "人物朝镜头前后移动", "纵深间距", "姿态切片按真实深度缩放，形成向远处延伸的动作阶梯", ("PERSPECTIVE-CLONE", "MONOCULAR-DEPTH")),
            ("POSEERASE", "动作擦除队列", "Pose Queue Erase", "主身沿原路径反向返回", "擦除距离", "主身经过哪个历史姿态，哪个姿态切片就被依次擦除", ("TRAJECTORY-ACCUMULATION",)),
        ),
        "GESTURE": (
            ("GESTUREECHO", "手势回声", "Gesture Echo", "手掌完成指定挥动", "回声数量", "手部历史姿态沿挥动方向依次显现并衰减", ("GESTURE-ECHO",)),
            ("GESTURELOOP", "手势循环分身", "Gesture Loop Clone", "用户画圈后保持手掌在画面内", "循环时长", "局部手势分身循环播放最近一段挥手动作", ("TIME-LOOP", "HAND-REGION")),
            ("GESTUREBEAT", "手势节拍接力", "Beat Gesture Relay", "指定手势命中音乐强拍", "接力间隔", "每个强拍生成一个手势分身并沿手臂方向接力出现", ("AUDIO-BEAT", "HAND-GESTURE")),
            ("GESTUREMIRROR", "手势镜像双生", "Mirrored Gesture Twin", "手掌越过屏幕中轴", "镜像轴", "手势分身在中轴另一侧同步出现并保留短延迟", ("MIRROR-PERSONA", "HAND-2D-TRAJECTORY")),
            ("GESTUREBURST", "手势分身爆发", "Gesture Clone Burst", "握拳转为张掌", "爆发半径", "多个手势分身从掌心向外展开后逐个消散", ("HAND-GESTURE", "SPATIAL-DUPLICATE")),
        ),
        "MIRROR": (
            ("MIRRORDELAY", "镜像人格延迟", "Delayed Mirror Persona", "人物越过镜像轴后继续动作", "镜像延迟", "镜像人格以固定时间差重复主身动作", ("MIRROR-PERSONA", "FRAME-DELAY")),
            ("MIRRORBREAK", "镜像人格脱离", "Mirror Persona Breakaway", "主身触碰镜像轴", "脱离距离", "镜像副本从对称位置脱离并沿独立路径移动", ("SPATIAL-DUPLICATE",)),
            ("MIRRORMERGE", "镜像合身", "Mirror Merge", "主身与镜像副本在中轴相遇", "融合宽度", "两个人格在中轴叠合后变回单一主体", ("STATE-HYSTERESIS", "IDENTITY-MEMORY")),
            ("MIRRORBEAT", "镜像节拍对舞", "Mirror Beat Duet", "主身动作峰值命中强拍", "对舞相位", "镜像人格在下一拍回应主身上一拍动作", ("AUDIO-BEAT", "MOTION-PHASE")),
            ("MIRRORDEPTH", "纵深镜像队列", "Depth Mirror Queue", "手机向镜像轴方向推进", "透视间距", "镜像人格沿虚拟纵深复制成递减大小的动作队列", ("PERSPECTIVE-CLONE", "CAMERA-MOTION")),
        ),
    },
    "face_gaze_expression": {
        "CAMERA": (
            ("CALIBRATE", "瞳孔镜头校准", "Pupil-to-camera Calibration", "完成三个校准点注视后直视屏幕内容", "瞳孔平滑度", "瞳孔与虹膜被轻量重定向到镜头方向，眼睑、头姿和身份保持不变", ("IRIS-PUPIL-LANDMARKS",)),
            ("CAMERAHOLD", "镜头对视保持", "Camera Contact Hold", "视线短暂移开后在容差时间内返回", "保持容差", "短时读稿时瞳孔朝向保持镜头附近，超过容差后恢复真实视线", ("IDENTITY-MEMORY", "GAZE-VECTOR")),
            ("CAMERABLINK", "眨眼暂停矫正", "Blink-safe Correction", "检测到眼睑开始闭合", "暂停阈值", "眨眼期间冻结眼球重定向，睁眼后从真实虹膜位置平滑恢复", ("BLINK", "IRIS-PUPIL-LANDMARKS")),
            ("CAMERALIMIT", "侧脸矫正限幅", "Profile Correction Limit", "头部偏航超过自然矫正角度", "最大矫正角", "侧脸时逐步减弱瞳孔重定向，避免眼球转向不自然", ("HEAD-POSE", "GAZE-VECTOR")),
            ("CAMERAPREVIEW", "镜头对视预览", "Eye-contact Preview", "用户按住预览对比按钮", "预览混合度", "取景器并排显示真实视线与镜头对视矫正结果", ("GAZE-VECTOR", "IRIS-PUPIL-LANDMARKS")),
        ),
        "DIALOGUE": (
            ("REDIRECT", "对话对象重定向", "Dialogue-target Redirection", "当前说话者切换或对话对象转头", "对视目标", "双方眼球与虹膜朝向被重定向到对方眼睛，形成连续虚拟对视", ("MULTI-PERSON-GRAPH", "IRIS-PUPIL-LANDMARKS")),
            ("SPEAKERSWAP", "说话者视线交接", "Speaker Gaze Handoff", "声源从一位人物切换到另一位", "交接时长", "上一说话者移开视线，新说话者的眼球平滑转向对话对象", ("SOURCE-DIRECTION", "MULTI-PERSON-GRAPH")),
            ("DIALOGUEHOLD", "对视短停保持", "Conversation Contact Hold", "一方短暂低头读稿后抬头", "保持窗口", "低头期间保存对视目标，抬头后虹膜回到同一人物而非镜头", ("IDENTITY-MEMORY", "HEAD-POSE")),
            ("TRIAD", "三人轮转对视", "Three-person Gaze Rotation", "三位人物按发言顺序切换", "轮转顺序", "每位人物的眼球只重定向到当前说话者，发言切换时依次轮转", ("MULTI-PERSON-GRAPH", "SOURCE-DIRECTION")),
            ("DIALOGUEBREAK", "对视自然断开", "Natural Gaze Break", "说话停顿超过设定时间", "断开延迟", "停顿时逐渐减弱虚拟对视并恢复真实瞳孔方向", ("SOUND-VOLUME", "TIME-DECAY")),
        ),
        "GLOW": (
            ("DWELL", "停留点亮", "Dwell-to-glow", "视线停留在同一目标超过设定时长", "停留时长", "被注视目标从边缘向中心发光，移开视线后平滑熄灭", ("GAZE-FOCUS", "LUMINOUS-CORE")),
            ("GLOWPULSE", "凝视脉冲发光", "Gaze Pulse Glow", "凝视目标达到第二级停留时长", "脉冲半径", "目标发光核心向外扩散一次光环并继续保持选中", ("GAZE-FOCUS", "BLOOM-GLOW")),
            ("GLOWTRAIL", "视线扫光路径", "Gaze Sweep Trail", "视线连续扫过多个物体实例", "扫光衰减", "物体按被注视顺序依次点亮并留下短时可见路径", ("OBJECT-INSTANCE", "TRAJECTORY-ACCUMULATION")),
            ("GLOWBLINK", "眨眼锁定发光", "Blink-lock Glow", "目标已发光后完成一次眨眼", "锁定时长", "眨眼把当前发光对象锁定，视线移开后仍保持亮度", ("BLINK", "STATE-HYSTERESIS")),
            ("GLOWTRANSFER", "视线移交光核", "Gaze Glow Transfer", "视线从旧目标稳定移动到新目标", "移交速度", "发光核心沿两物体间的视线路径从旧目标移动到新目标", ("GAZE-VECTOR", "OBJECT-INSTANCE")),
        ),
        "CATCHLIGHT": (
            ("FOLLOW", "虹膜高光跟随", "Iris Catchlight Follow", "人物转头或视线横向移动", "跟随惯性", "眼神光贴着虹膜表面连续滑动并保持反射形状", ("IRIS-PUPIL-LANDMARKS", "CATCHLIGHT-RERENDER")),
            ("CATCHBLINK", "眨眼高光消隐", "Blink Catchlight Fade", "眼睑进入闭合阶段", "消隐速度", "眼神光随眼睑闭合缩小消失，睁眼后从虹膜位置恢复", ("BLINK", "IRIS-PUPIL-LANDMARKS")),
            ("CATCHDOUBLE", "双眼同源高光", "Paired Catchlights", "左右眼同时可见且头姿稳定", "光源一致度", "双眼高光保持同一虚拟光源方向和形状比例", ("HEAD-POSE", "CATCHLIGHT-RERENDER")),
            ("CATCHBEAT", "节拍眼神光", "Beat Catchlight", "音乐强拍到达且双眼可见", "闪耀强度", "眼神光在强拍瞬间扩大闪耀，拍间恢复原大小", ("AUDIO-BEAT", "CATCHLIGHT-RERENDER")),
            ("CATCHCOLOR", "视线方向变色高光", "Direction-colored Catchlight", "视线从左侧目标移向右侧目标", "高光色相", "眼神光随视线方向连续变色并保持虹膜贴附", ("GAZE-VECTOR", "CATCHLIGHT-RERENDER")),
        ),
        "SELECT": (
            ("CONFIRM", "眨眼确认选择", "Blink-confirm Selection", "候选目标出现选中环后完成一次眨眼", "确认反馈", "凝视对象先出现选中环，眨眼后明确选中并展开特效", ("GAZE-FOCUS", "OBJECT-INSTANCE")),
            ("SELECTDWELL", "凝视倒计时选择", "Dwell Countdown Select", "视线在候选对象停留进入倒计时", "选择停留时间", "对象周围进度环随凝视填满，填满后自动选中", ("GAZE-FOCUS", "STATE-HYSTERESIS")),
            ("SELECTCANCEL", "移开视线取消", "Look-away Cancel", "进度环未填满前视线移开", "取消衰减", "未完成的选中环反向消退且不会触发对象特效", ("GAZE-VECTOR", "TIME-DECAY")),
            ("SELECTCYCLE", "扫视轮换候选", "Gaze Candidate Cycle", "视线依次进入多个候选区域", "候选间隔", "候选对象按凝视顺序高亮，旧候选自动降级为轮廓提示", ("OBJECT-INSTANCE", "GAZE-FOCUS")),
            ("SELECTMENU", "凝视展开特效盘", "Gaze Effect Menu", "对象选中后继续凝视其上方入口", "菜单半径", "选中对象周围展开径向特效选项，视线停留即可预览", ("GAZE-VECTOR", "OBJECT-INSTANCE")),
        ),
    },
    "time_editing": {
        "FREEZE": (
            ("FREEZEHAND", "手势冻结区域", "Gesture Region Freeze", "手掌张开后握拳指向区域", "冻结边缘", "指向区域停在当前帧，周围画面继续实时播放", ("HAND-GESTURE", "LOCAL-TIME-FREEZE")),
            ("FREEZETOUCH", "触摸擦出冻结", "Touch-painted Freeze", "手指在目标区域涂抹", "冻结笔刷", "触摸覆盖区域逐步冻结成同一帧并保留柔和边缘", ("TOUCH-DRAW", "LOCAL-TIME-FREEZE")),
            ("FREEZEVOICE", "喊声解冻", "Voice Unfreeze", "冻结后人声音量超过阈值", "解冻加速度", "声音越强冻结区域越快追上当前时间", ("SOUND-VOLUME", "LOCAL-TIME-FREEZE")),
            ("FREEZESLIDER", "冻结选帧", "Freeze Frame Select", "拖动时间游标选择历史帧", "历史帧位置", "局部区域稳定显示用户选择的历史姿态", ("FRAME-DELAY", "LOCAL-TIME-FREEZE")),
            ("FREEZEBEAT", "节拍冻结释放", "Beat Freeze Release", "音乐强拍到达冻结区域", "释放拍数", "区域在强拍冻结并在设定拍数后恢复实时", ("AUDIO-BEAT", "LOCAL-TIME-FREEZE")),
        ),
        "LOOP": (
            ("LOOPSELECT", "圈选局部循环", "Selected Local Loop", "用户画圈框选发梢或水面", "循环时长", "选中区域在历史帧之间连续循环，外部保持当前时间", ("TIME-LOOP", "TOUCH-DRAW")),
            ("LOOPPINGPONG", "局部往返循环", "Ping-pong Local Loop", "循环区域首尾姿态差异较大", "往返速度", "区域在历史帧中正放后倒放，避免首尾硬跳", ("TIME-LOOP", "TIME-REVERSE")),
            ("LOOPBEAT", "节拍长度循环", "Beat-length Loop", "连续节拍建立稳定拍长", "循环拍数", "局部动作按一拍或两拍长度重复并对齐音乐", ("AUDIO-BEAT", "TIME-LOOP")),
            ("LOOPFADE", "循环边缘呼吸", "Loop Edge Breathing", "循环播放进入首尾过渡区", "边缘混合", "循环区域边缘在首尾阶段渐隐渐现以隐藏跳变", ("TIME-DECAY", "TIME-LOOP")),
            ("LOOPMOVE", "跟随对象循环", "Tracked Object Loop", "循环对象在画面中继续移动", "跟随范围", "循环内容跟随对象位置移动而不留在原屏幕区域", ("OBJECT-POSE", "TIME-LOOP")),
        ),
        "REVERSE": (
            ("REVERSEDRAG", "拖动局部倒放", "Drag-to-reverse", "向后拖动目标轨迹", "倒放窗口", "目标沿刚才的运动轨迹倒序回到起点", ("TIME-REVERSE", "OBJECT-POSE")),
            ("REVERSETHROW", "抛物回收", "Thrown-object Return", "抛出物体达到运动顶点", "回收速度", "飞出的物体倒放回手中而背景继续向前", ("MOTION-PHASE", "TIME-REVERSE")),
            ("REVERSEBEAT", "强拍动作倒放", "Beat Action Reverse", "动作峰值命中强拍", "倒放拍数", "选中动作在下一拍倒序回放并于拍点结束", ("AUDIO-BEAT", "TIME-REVERSE")),
            ("REVERSEMASK", "遮罩内倒放", "Masked Reverse", "用户点选一个物体实例", "遮罩羽化", "只有该物体区域倒放，周围对象保持当前运动", ("OBJECT-INSTANCE", "TIME-REVERSE")),
            ("REVERSELOOP", "倒放循环", "Reverse Loop", "倒放片段回到起点", "循环次数", "目标在正放与倒放间循环形成往返动作", ("TIME-LOOP", "TIME-REVERSE")),
        ),
        "SHUTTER": (
            ("SHUTTERROTATE", "旋转快门切片", "Rotating Shutter Slices", "手机快速旋转一次", "切片数量", "人体轮廓按手机角度分成扇形历史姿态", ("PHONE-ROTATION", "FRAME-DELAY")),
            ("SHUTTERPOSE", "动作阶段快门", "Motion-phase Shutter", "人体进入动作峰值", "阶段间隔", "起势峰值收势分别冻结为可见姿态切片", ("MOTION-PHASE", "FRAME-DELAY")),
            ("SHUTTERBEAT", "节拍快门队列", "Beat Shutter Queue", "音乐连续强拍到达", "拍点采样", "每个强拍采样一帧人体轮廓并沿运动方向排列", ("AUDIO-BEAT", "FRAME-DELAY")),
            ("SHUTTERDEPTH", "纵深快门切片", "Depth Shutter Slices", "人物朝镜头前后移动", "深度间距", "历史姿态按真实深度缩放并保持前后遮挡", ("MONOCULAR-DEPTH", "FRAME-DELAY")),
            ("SHUTTERERASE", "经过擦除切片", "Pass-through Slice Erase", "当前人物经过历史姿态位置", "擦除半径", "主身穿过哪个快门切片，哪个切片就被擦除", ("BODY-SKELETON", "STATE-HYSTERESIS")),
        ),
        "BORROW": (
            ("BORROWHAND", "手势借位窗口", "Gesture Borrowed Time", "检测手势事件并按住快门", "借位偏移", "前景人物显示稍早动作，背景保持当前事件", ("HAND-GESTURE", "EVENT-WINDOW")),
            ("BORROWBEAT", "节拍前后借位", "Beat Pre-post Offset", "强拍前后建立事件窗口", "前滚帧数", "人物动作提前进入强拍而环境仍按真实时间播放", ("AUDIO-BEAT", "EVENT-WINDOW")),
            ("BORROWPERSON", "双人时间错位", "Two-person Time Offset", "两人进入同一事件区域", "人物时间差", "两个人物分别显示不同历史时刻并保持同场互动", ("MULTI-PERSON-GRAPH", "FRAME-DELAY")),
            ("BORROWOBJECT", "物体时间借位", "Object Time Offset", "点选运动物体并选择历史偏移", "物体时间差", "物体显示历史位置而持有者保持当前动作", ("OBJECT-INSTANCE", "FRAME-DELAY")),
            ("BORROWRESET", "接触同步时间", "Contact Time Sync", "错位对象与人物发生接触", "同步速度", "接触发生时历史时间层逐步追上当前画面", ("MULTI-PERSON-TOUCH", "STATE-HYSTERESIS")),
        ),
    },
    "spatial_portals": {
        "MIRROR": (
            ("MIRRORSTEP", "迈步穿镜", "Step Through Mirror", "脚步跨过镜面入口平面", "入口厚度", "人物先被镜面边框遮挡再完整进入另一空间", ("BODY-SKELETON", "MIRROR-PORTAL")),
            ("MIRRORHAND", "手掌探镜", "Hand Through Mirror", "手掌进入镜面边界", "穿入深度", "手先穿过镜面并在另一侧出现，身体仍留在原空间", ("HAND-3D-TRAJECTORY", "MIRROR-PORTAL")),
            ("MIRRORROTATE", "转身换镜世界", "Rotate Mirror World", "手机绕镜面旋转到指定角度", "换景角度", "镜内世界随观察角度连续切换，镜外环境保持原样", ("PHONE-ROTATION", "MIRROR-PORTAL")),
            ("MIRRORTOUCH", "拉开镜面入口", "Pull-open Mirror", "触摸镜面边缘并向外拖", "开口宽度", "镜面从窄缝拉成有厚度的入口并保留手指遮挡", ("TOUCH-DRAW", "MIRROR-PORTAL")),
            ("MIRRORGAZE", "注视显露镜后", "Gaze-reveal Mirror", "视线停留在镜面中心", "显露速度", "镜面被注视时逐渐透明并显露另一空间", ("GAZE-FOCUS", "MIRROR-PORTAL")),
        ),
        "PALM": (
            ("PALMOPEN", "双手开窗", "Two-hand Portal Open", "双手围出矩形并向外拉", "窗口大小", "掌间窗口随手距扩大并露出另一场景", ("HAND-2D-TRAJECTORY", "FRAME-TRAVERSAL")),
            ("PALMMOVE", "掌窗跟随", "Palm Portal Follow", "双手保持框形并移动", "跟随平滑", "窗口固定在双手之间移动并正确遮挡手指", ("HAND-3D-TRAJECTORY", "FRAME-TRAVERSAL")),
            ("PALMTHROW", "抛出空间窗", "Throw Palm Portal", "双手合拢后向前抛出", "抛出距离", "掌中窗口飞到场景平面并变成世界锚定入口", ("HAND-GESTURE", "WORLD-SPACE-ANCHOR")),
            ("PALMBEAT", "节拍掌窗脉冲", "Beat Palm Portal", "双手框住窗口时音乐强拍到达", "脉冲尺度", "窗口边框在强拍扩张并短暂显露更大视野", ("AUDIO-BEAT", "FRAME-TRAVERSAL")),
            ("PALMCLOSE", "合掌关窗", "Palm Portal Close", "双手从分开移动到接触", "关闭速度", "窗口随手距缩小并在合掌时完全闭合", ("MULTI-PERSON-TOUCH", "FRAME-TRAVERSAL")),
        ),
        "FLOOR": (
            ("FLOORSTEP", "脚步开地门", "Step-open Floor Door", "脚尖指向地面并踏下", "折叠角度", "地面沿脚尖方向折开成通往另一空间的门", ("BODY-POSE", "SPACE-FOLD")),
            ("FLOORDROP", "物体落入地门", "Drop Through Floor", "物体进入地门区域并向下运动", "落入深度", "物体被地门边缘遮挡后掉入另一空间", ("OBJECT-POSE", "FRAME-TRAVERSAL")),
            ("FLOORWALK", "地门随步延伸", "Walking Floor Portal", "人物连续沿地面行走", "延伸长度", "折叠入口沿脚步方向向前延伸并在身后闭合", ("BODY-SKELETON", "WORLD-SPACE-ANCHOR")),
            ("FLOORBEAT", "节拍地面折叠", "Beat Floor Fold", "强拍到达且地面入口可见", "折叠幅度", "地面门按节拍开合并短暂露出下层世界", ("AUDIO-BEAT", "SPACE-FOLD")),
            ("FLOORROTATE", "旋转地门方向", "Rotate Floor Door", "手机绕竖轴旋转", "门朝向", "地门在世界空间内转向新的行走方向而不随屏幕漂移", ("PHONE-ROTATION", "WORLD-SPACE-ANCHOR")),
        ),
        "TUNNEL": (
            ("TUNNELPINCH", "捏合景深隧道", "Pinch Depth Tunnel", "双指向内捏合", "隧道深度", "背景围绕消失点向内延伸成连续景深隧道", ("TOUCH-DRAW", "TUNNEL-WARP")),
            ("TUNNELPUSH", "推进穿隧道", "Push Through Tunnel", "手机沿相机前向快速推进", "推进速度", "隧道层级向镜头两侧掠过并保持中心目标可见", ("CAMERA-MOTION", "TUNNEL-WARP")),
            ("TUNNELBEAT", "节拍隧道缩放", "Beat Tunnel Pulse", "音乐强拍到达", "缩放幅度", "隧道在强拍向内冲刺，拍间回到基础深度", ("AUDIO-BEAT", "TUNNEL-WARP")),
            ("TUNNELORBIT", "旋转隧道", "Rotating Tunnel", "手机横滚角持续变化", "扭转角", "隧道壁随手机旋转扭转，中心路径保持稳定", ("PHONE-ROTATION", "RADIAL-TWIST")),
            ("TUNNELEND", "凝视隧道出口", "Gaze Tunnel Exit", "视线停留在隧道出口", "出口显露", "出口被注视时逐渐放大并露出目标世界", ("GAZE-FOCUS", "FRAME-TRAVERSAL")),
        ),
        "PAGE": (
            ("PAGEWIPE", "门框翻页", "Doorframe Page Turn", "沿门框横向划动", "翻页弧度", "房间沿门框像纸页一样翻开露出另一室内场景", ("TOUCH-DRAW", "SPACE-FOLD")),
            ("PAGEWALK", "穿过翻页房间", "Walk Through Page", "人物跨过已翻开的房间边界", "边界厚度", "人物保持连续遮挡穿入翻页后的空间", ("BODY-SKELETON", "FRAME-TRAVERSAL")),
            ("PAGEROTATE", "转身翻房间", "Turn-to-page Room", "手机转身超过九十度", "触发角度", "新朝向的房间像下一页一样覆盖旧房间", ("PHONE-ROTATION", "SPACE-FOLD")),
            ("PAGEBEAT", "节拍房间翻页", "Beat Room Page", "音乐强拍到达", "每拍页数", "每个强拍翻过一层房间风格且保持门框位置", ("AUDIO-BEAT", "SPACE-FOLD")),
            ("PAGECLOSE", "回划合页", "Reverse Page Close", "沿原门框反向划动", "合页速度", "翻开的房间按原折叠路径闭合回当前空间", ("TIME-REVERSE", "SPACE-FOLD")),
        ),
    },
    "virtual_light_shadow": {
        "DOUBLE": (
            ("SHADOWCLOCK", "影子延迟分身", "Delayed Shadow Double", "主体开始移动或停下", "影子延迟", "影子分身沿旧姿态延迟跟随并追回主体脚下", ("SHADOW-DOUBLE",)),
            ("SHADOWBEAT", "节拍影子闪切", "Beat Shadow Flash", "主体动作峰值命中强拍", "闪切宽度", "影子分身在强拍翻到主体另一侧并爆亮轮廓", ("AUDIO-BEAT", "SHADOW-RERENDER")),
            ("SHADOWTOUCH", "拖动影子分身", "Drag Shadow Double", "触摸影子并拖向新位置", "拖动距离", "影子分身脱离脚下沿触摸路径移动，主体保持原位", ("TOUCH-DRAW", "SHADOW-DOUBLE")),
            ("SHADOWREVERSE", "影子动作倒放", "Reverse Shadow Motion", "主体停下后向后挥手", "倒放窗口", "影子分身倒序回放主体刚完成的动作", ("TIME-REVERSE", "SHADOW-DOUBLE")),
            ("SHADOWMERGE", "踩影合身", "Step-on Shadow Merge", "主体脚部进入影子分身区域", "融合半径", "影子从接触点收缩并重新贴回主体脚下", ("BODY-POSE", "STATE-HYSTERESIS")),
        ),
        "SUNSET": (
            ("SUNSETDRAG", "拖动日落光位", "Drag Sunset Light", "拖动虚拟太阳跨过人物", "光源方位", "头发与肩部轮廓光从一侧连续移动到另一侧", ("TOUCH-DRAW", "VIRTUAL-RIM-LIGHT")),
            ("SUNSETTEMP", "日落色温过渡", "Sunset Temperature Shift", "滑动日落时间控制条", "轮廓光色温", "轮廓光从暖黄过渡到红紫并保持受光方向", ("SCENE-LIGHTING", "VIRTUAL-RIM-LIGHT")),
            ("SUNSETMOVE", "行走日落边光", "Walking Sunset Rim", "人物在逆光方向行走", "边光宽度", "轮廓光跟随身体边缘移动且不覆盖正面皮肤", ("BODY-SILHOUETTE", "VIRTUAL-RIM-LIGHT")),
            ("SUNSETBEAT", "节拍日落闪耀", "Beat Sunset Rim", "音乐强拍到达", "闪耀强度", "暖色轮廓光在强拍扩张并拍间回落", ("AUDIO-BEAT", "VIRTUAL-RIM-LIGHT")),
            ("SUNSETFADE", "转身边光消隐", "Turn-away Rim Fade", "人物从背光转向正面光", "消隐角度", "轮廓光随头姿和身体朝向减弱直至消失", ("HEAD-POSE", "VIRTUAL-RIM-LIGHT")),
        ),
        "FOLLOW": (
            ("SPOTFOLLOW", "人物移动追光", "Moving Follow Spot", "点按人物后开始移动", "追光半径", "椭圆追光稳定跟随人物脚下或脸部", ("VIRTUAL-SPOTLIGHT", "BODY-SKELETON")),
            ("SPOTSWAP", "多人追光切换", "Multi-person Spotlight Swap", "新人物开始说话或动作", "切换时长", "追光从当前人物平滑移交到下一人物", ("MULTI-PERSON-GRAPH", "VIRTUAL-SPOTLIGHT")),
            ("SPOTBEAT", "节拍追光脉冲", "Beat Spotlight Pulse", "音乐强拍到达", "光圈脉冲", "追光圈在强拍扩大并提高亮度，拍间回落", ("AUDIO-BEAT", "VIRTUAL-SPOTLIGHT")),
            ("SPOTGESTURE", "手势移动追光", "Gesture-directed Spot", "人物手势指向新位置", "移动速度", "追光沿手指方向移动并在目标位置停留", ("HAND-GESTURE", "VIRTUAL-SPOTLIGHT")),
            ("SPOTFREEZE", "停步锁定追光", "Stop-lock Spotlight", "人物停止移动超过阈值", "锁定时长", "追光锁在停止位置，人物再次移动后重新跟随", ("MOTION-PHASE", "VIRTUAL-SPOTLIGHT")),
        ),
        "LONG": (
            ("LONGTILT", "倾斜拉长影子", "Tilt-lengthened Shadow", "手机向侧面倾斜", "影子长度", "主体影子沿地面方向连续拉长或缩短", ("PHONE-ROTATION", "SHADOW-RERENDER")),
            ("LONGWALK", "步伐延展长影", "Walking Long Shadow", "人物连续向前行走", "延展增益", "每一步让长影产生一段波动并保持脚底接触", ("BODY-SKELETON", "SHADOW-RERENDER")),
            ("LONGBEAT", "节拍影长脉冲", "Beat Shadow Length", "音乐强拍到达", "影长脉冲", "长影在强拍向外伸展并拍间收回", ("AUDIO-BEAT", "SHADOW-RERENDER")),
            ("LONGROTATE", "旋转影子方向", "Rotating Shadow Direction", "手机绕主体旋转", "影子方位", "长影围绕脚底连续改变方向且贴合地面", ("CAMERA-MOTION", "MONOCULAR-DEPTH")),
            ("LONGSPLIT", "长影分叉", "Forked Long Shadow", "人物张开双臂形成宽姿态", "分叉角度", "一个长影沿肢体方向分叉成多条可见剪影", ("BODY-POSE", "SHADOW-RERENDER")),
        ),
        "SCREEN": (
            ("SCREENCAST", "墙面人物投影", "Wall Subject Projection", "框选墙面并点选人物", "投影大小", "人物轮廓按墙面透视投射并随动作更新", ("BODY-SILHOUETTE", "SHADOW-RERENDER")),
            ("SCREENDELAY", "墙面延迟投影", "Delayed Wall Projection", "人物开始动作", "投影延迟", "墙面投影比真人慢固定时间重复动作", ("FRAME-DELAY", "SHADOW-RERENDER")),
            ("SCREENBEAT", "节拍投影放大", "Beat Projection Scale", "音乐强拍到达", "放大比例", "墙面人物投影在强拍瞬间放大并拍间恢复", ("AUDIO-BEAT", "SHADOW-RERENDER")),
            ("SCREENCOLOR", "彩色投影分层", "Layered Color Projection", "人物动作方向改变", "投影配色", "墙面出现多层不同颜色的短延迟轮廓投影", ("MOTION-AFTERIMAGE", "SHADOW-RERENDER")),
            ("SCREENLIGHT", "光束投影幕", "Beam Projection Screen", "手机摆动虚拟光束扫过墙面", "光束锥角", "体积光束扫到墙面时显露人物投影，离开后熄灭", ("VOLUMETRIC-LIGHT", "PHONE-ROTATION")),
        ),
    },
}

IDEA_COMPATIBLE_BEHAVIORS.update({
    "material_morph": {
        "DISSOLVE": (
            ("DISSOLVEEDGE", "边缘材质溶解", "Edge Material Dissolve", "目标轮廓运动速度超过阈值", "溶解推进速度", "材质从轮廓向内部逐块溶解并释放像素碎屑", ("PIXEL-DISSOLVE",)),
            ("DISSOLVETOUCH", "触摸材质溶解", "Touch Material Dissolve", "手指扫过目标表面", "溶解笔刷", "触摸经过处沿路径变成像素尘并露出背后内容", ("TOUCH-DRAW", "PIXEL-DISSOLVE")),
            ("DISSOLVEBEAT", "节拍材质溶解", "Beat Material Dissolve", "音乐强拍连续到达", "每拍溶解量", "目标材质在每个强拍推进一层溶解进度", ("AUDIO-BEAT", "PIXEL-DISSOLVE")),
            ("DISSOLVEREVERSE", "碎片反向凝结", "Reverse Material Condense", "录后向左拖动时间游标", "凝结速度", "散开碎片按出生顺序回到目标并闭合表面", ("TIME-REVERSE", "FRAGMENTATION")),
            ("DISSOLVEVOICE", "声压材质融解", "Voice-driven Dissolve", "人声音量持续超过阈值", "声压增益", "声音越响材质溶解越快，停声后冻结当前进度", ("SOUND-VOLUME", "PIXEL-DISSOLVE")),
        ),
        "GLASS": (
            ("GLASSBREATH", "玻璃呼吸", "Breathing Glass", "目标表面完成一轮扩张收缩动作", "折射呼吸幅度", "玻璃折射随表面呼吸起伏并保持轮廓透明", ("GLASS", "ELASTIC-WARP")),
            ("GLASSTOUCH", "指尖玻璃波纹", "Touch Glass Ripple", "触摸玻璃区域", "波纹幅度", "触点向外传播折射波纹并推移背后画面", ("RIPPLE-DISPLACEMENT", "GLASS")),
            ("GLASSBREAK", "玻璃裂片展开", "Glass Fragment Spread", "握拳转为张掌", "裂片间距", "玻璃表面分裂成透明碎片向外展开但保留目标轮廓", ("HAND-GESTURE", "FRAGMENTATION")),
            ("GLASSBEAT", "节拍玻璃闪光", "Beat Glass Flash", "音乐强拍到达", "边缘高光", "玻璃边缘在强拍闪亮并短暂增强折射", ("AUDIO-BEAT", "GLASS")),
            ("GLASSROTATE", "旋转玻璃色散", "Rotating Glass Dispersion", "手机绕目标旋转", "色散距离", "玻璃边缘随观察角度产生连续彩色色散", ("PHONE-ROTATION", "CHROMATIC-ABERRATION")),
        ),
        "METAL": (
            ("METALFLOW", "液态金属流动", "Liquid Metal Flow", "目标表面持续弯曲或移动", "金属流速", "金属高光沿表面运动方向流动并保持形状", ("METAL", "LIQUID")),
            ("METALROTATE", "旋转金属高光", "Rotating Metal Highlight", "手机绕目标旋转", "金属反射强度", "方向性高光随观察角度绕目标表面移动", ("PHONE-ROTATION", "METAL")),
            ("METALBEAT", "节拍金属脉冲", "Beat Metal Pulse", "音乐强拍到达", "粗糙度脉冲", "金属表面在强拍从粗糙变镜面再平滑回落", ("AUDIO-BEAT", "METAL")),
            ("METALTOUCH", "触摸金属化", "Touch Metallize", "手指扫过目标区域", "金属化笔刷", "触摸路径将原表面逐段转为金属并留下移动高光", ("TOUCH-DRAW", "METAL")),
            ("METALMELT", "声压金属融化", "Voice Metal Melt", "人声音量持续上升", "融化黏度", "硬质金属随音量变成流体并在停声后重新凝固", ("SOUND-VOLUME", "LIQUID")),
        ),
        "PAPER": (
            ("PAPERTEAR", "纸片裂变", "Paper Tear", "双指向外拉开海报区域", "裂片大小", "纸面沿手势方向撕裂成带纤维边缘的碎片", ("TOUCH-DRAW", "FRAGMENTATION")),
            ("PAPERFOLD", "纸面折叠", "Paper Fold", "沿纸面划出折线", "折叠角度", "海报沿划线折叠并显示纸张厚度和遮挡", ("SPACE-FOLD", "PAPER")),
            ("PAPERBEAT", "节拍纸屑爆发", "Beat Paper Burst", "音乐强拍到达", "纸屑数量", "纸面在强拍喷出碎片，拍间碎片缓慢落下", ("AUDIO-BEAT", "FRAGMENTATION")),
            ("PAPERREVERSE", "碎纸复原", "Reverse Paper Restore", "向左拖动时间游标", "复原速度", "散落纸片倒序飞回并重新拼成完整纸面", ("TIME-REVERSE", "FRAGMENTATION")),
            ("PAPERWIND", "转动吹散纸片", "Rotation-blown Paper", "手机快速横向旋转", "吹散方向", "纸片沿手机旋转方向被吹开并逐渐离开画面", ("PHONE-ROTATION", "PAPER")),
        ),
        "HOLO": (
            ("HOLOBEAT", "节拍全息织物", "Beat Holographic Fabric", "音乐强拍命中服装区域", "色相脉冲", "织物彩虹色带在强拍扩张并拍间回落", ("AUDIO-BEAT", "HOLOGRAPHIC")),
            ("HOLOMOVE", "动作全息流光", "Motion Holographic Flow", "服装随身体快速形变", "流光速度", "全息色带沿织物拉伸方向流动且不滑离服装", ("BODY-SKELETON", "FABRIC")),
            ("HOLOROTATE", "视角全息变色", "View Holographic Shift", "手机绕人物旋转", "色相范围", "织物随观察角度连续变色并保持经纬纹理", ("PHONE-ROTATION", "HOLOGRAPHIC")),
            ("HOLOTOUCH", "触摸全息染色", "Touch Holographic Paint", "手指在服装区域绘制", "染色笔刷", "触摸路径留下全息彩带并贴合衣物褶皱", ("TOUCH-DRAW", "CLOTHING-REGION")),
            ("HOLOFADE", "停步全息消隐", "Stillness Hologram Fade", "人物停止动作超过阈值", "消隐时长", "动作停止后全息色带逐步变透明，再次运动时恢复", ("MOTION-PHASE", "TIME-DECAY")),
        ),
    },
    "particles_weather": {
        "LYRIC": (
            ("LYRICORBIT", "歌词环绕旋转", "Lyric Orbit Rotation", "歌词时间戳进入当前句", "环绕速度", "当前歌词沿人物头肩空间环绕并在背后被遮挡", ("LYRIC-TIMESTAMP", "LYRIC-RING")),
            ("LYRICBEAT", "歌词节拍弹跳", "Lyric Beat Bounce", "当前歌词播放且强拍到达", "弹跳高度", "环绕歌词字符在强拍向外跳起再回到文字环", ("AUDIO-BEAT", "LYRIC-RING")),
            ("LYRICVOICE", "音量歌词扩环", "Volume Lyric Ring", "演唱音量持续变化", "音量响应", "声音越响歌词环半径越大，停声后缓慢收缩", ("SOUND-VOLUME", "LYRIC-RING")),
            ("LYRICGAZE", "注视歌词聚焦", "Gaze-focused Lyrics", "视线停留在某个歌词词组", "聚焦字号", "被注视词组放大高亮，其余字符继续环绕", ("GAZE-FOCUS", "TEXT")),
            ("LYRICTOUCH", "拖拽歌词轨道", "Drag Lyric Orbit", "触摸并拖动歌词环", "歌词时间偏移", "歌词环移动到人物另一侧并保持当前时间顺序", ("TOUCH-DRAW", "LYRIC-RING")),
        ),
        "RAIN": (
            ("RAINBEAT", "节拍雨幕", "Beat Rain Curtain", "音乐强拍到达", "雨量脉冲", "雨幕在强拍加密并在拍间恢复基础雨量", ("AUDIO-BEAT", "RAIN")),
            ("RAINTILT", "倾斜风雨", "Tilted Wind Rain", "手机横滚角发生变化", "雨线方向", "雨线随手机倾斜改变方向并响应镜头运动", ("PHONE-ROTATION", "RAIN")),
            ("RAINDEPTH", "前后景雨层", "Layered Depth Rain", "人物在画面中移动", "雨层数量", "雨滴分布在人物前后并保持正确遮挡", ("MONOCULAR-DEPTH", "RAIN")),
            ("RAINTOUCH", "指尖避雨区", "Touch Rain Shelter", "在画面上圈选保护区域", "避雨半径", "雨滴绕开圈选区域形成清晰的无雨窗口", ("TOUCH-DRAW", "RAIN")),
            ("RAINVOICE", "声音雨量", "Voice Rain Intensity", "环境声或人声音量超过阈值", "雨量响应", "声音越响雨线越密越长，停声后逐渐减弱", ("SOUND-VOLUME", "RAIN")),
        ),
        "PETAL": (
            ("PETALGESTURE", "手势花瓣旋涡", "Gesture Petal Vortex", "手掌画圆", "旋涡强度", "花瓣从掌心发射并沿手势方向形成旋涡", ("HAND-GESTURE", "PETALS")),
            ("PETALOPEN", "张掌花瓣爆发", "Open-palm Petal Burst", "握拳转为张掌", "爆发数量", "花瓣从掌心向外爆发后缓慢飘落", ("HAND-GESTURE", "PETALS")),
            ("PETALFOLLOW", "花瓣跟手", "Hand-follow Petals", "手掌在画面中连续移动", "跟随惯性", "花瓣发射点跟随手掌并留下弯曲粒子流", ("HAND-2D-TRAJECTORY", "PETALS")),
            ("PETALBEAT", "节拍花瓣环", "Beat Petal Ring", "手掌可见且强拍到达", "花瓣环半径", "花瓣在强拍围绕手掌扩成一圈并拍间散开", ("AUDIO-BEAT", "PETALS")),
            ("PETALBLOW", "吹散花瓣", "Blown Petals", "人物对镜头吹气", "吹散速度", "花瓣沿嘴部朝向被吹散并逐渐离开前景", ("MOUTH-SHAPE", "PETALS")),
        ),
        "SNOW": (
            ("SNOWBREATH", "呼吸雪夜", "Breath-driven Snow", "人物对镜头吹气", "雪片大小", "嘴前雪片随气息向外扩散并在远处缓慢下落", ("MOUTH-SHAPE", "SNOW")),
            ("SNOWDEPTH", "景深雪层", "Depth Snow Layers", "人物前后移动", "雪层深度", "不同大小雪片分布在人物前后并保持遮挡", ("MONOCULAR-DEPTH", "SNOW")),
            ("SNOWBEAT", "节拍雪闪", "Beat Snow Sparkle", "音乐强拍到达", "闪耀比例", "部分雪片在强拍闪亮并留下短暂光点", ("AUDIO-BEAT", "SNOW")),
            ("SNOWTOUCH", "触摸融雪", "Touch Snow Melt", "手指划过雪层", "融雪笔刷", "触摸路径内雪片快速融化消失并逐渐重新落入", ("TOUCH-DRAW", "SNOW")),
            ("SNOWTILT", "倾斜飘雪", "Tilted Snowfall", "手机左右倾斜", "飘雪方向", "雪片随手机倾斜改变横向漂移并保持重力下落", ("PHONE-ROTATION", "SNOW")),
        ),
        "DUST": (
            ("DUSTGAZE", "凝视尘埃聚焦", "Gaze Dust Focus", "视线停留在光照目标", "尘埃密度", "被注视区域的光束中聚集可见尘埃，移开后散开", ("GAZE-FOCUS", "DUST")),
            ("DUSTLIGHT", "光束尘埃", "Beam-lit Dust", "虚拟光束扫过空间", "光束尘量", "只有光束覆盖区域内的尘埃被照亮并显示景深", ("VOLUMETRIC-LIGHT", "DUST")),
            ("DUSTTOUCH", "指尖聚尘", "Touch Dust Gather", "触摸并拖动画面中的尘埃", "吸附半径", "尘埃沿触摸路径聚集成可见流线", ("TOUCH-DRAW", "DUST")),
            ("DUSTVOICE", "声波扬尘", "Voice Dust Wave", "声音音量突然上升", "扬尘幅度", "尘埃从目标表面被声波扬起并逐渐落回", ("SOUND-VOLUME", "DUST")),
            ("DUSTBEAT", "节拍尘埃闪烁", "Beat Dust Flicker", "音乐强拍到达", "闪烁强度", "尘埃在强拍短暂发亮并按深度顺序消隐", ("AUDIO-BEAT", "DUST")),
        ),
    },
    "world_style": {
        "SEASON": (
            ("SEASONWIPE", "擦换季节", "Season Wipe", "手指横向划过背景", "擦换宽度", "划线一侧逐步变为目标季节，人物保持原样", ("TOUCH-DRAW", "SEASON")),
            ("SEASONROTATE", "转身换季", "Turn-to-season", "手机绕竖轴旋转", "换季角度", "新朝向逐渐显露另一季节且接缝固定在世界空间", ("PHONE-ROTATION", "SEASON")),
            ("SEASONBEAT", "节拍季节推进", "Beat Season Step", "音乐连续强拍到达", "每拍季节步长", "背景在强拍依次从春夏秋冬推进并保持布局", ("AUDIO-BEAT", "SEASON")),
            ("SEASONGAZE", "凝视局部换季", "Gaze Local Season", "视线停留在一片植物或地面", "换季半径", "被注视区域先变季节，移开后向外扩散到背景", ("GAZE-FOCUS", "SEASON")),
            ("SEASONVOICE", "人声季节脉冲", "Voice Season Pulse", "人声音节连续出现", "色调脉冲", "每个音节推动背景植被与色调向目标季节变化", ("SOUND-VOLUME", "SEASON")),
        ),
        "COMIC": (
            ("COMICWIPE", "漫画街景擦换", "Comic Street Wipe", "手指从街景边缘划过", "线稿密度", "划过区域变为漫画线稿，人物轮廓保持一致", ("TOUCH-DRAW", "VISUAL-STYLE")),
            ("COMICBEAT", "节拍漫画分镜", "Beat Comic Panels", "音乐强拍到达", "分镜数量", "街景在强拍切成漫画分镜并保留连续人物动作", ("AUDIO-BEAT", "VISUAL-STYLE")),
            ("COMICGAZE", "凝视漫画化", "Gaze Comic Focus", "视线停留在建筑或人物", "漫画化半径", "被注视对象先变成高对比线稿，背景保持真实", ("GAZE-FOCUS", "VISUAL-STYLE")),
            ("COMICMOVE", "运动速度线世界", "Motion-line Comic World", "相机或人物快速移动", "速度线密度", "漫画街景沿运动方向出现汇聚速度线", ("CAMERA-MOTION", "COMIC-SPEED-LINES")),
            ("COMICVOICE", "口播漫画气泡", "Voice Comic Bubbles", "人物说话音量超过阈值", "气泡大小", "漫画世界在说话者旁生成随音量变化的对话气泡", ("SOUND-VOLUME", "TEXT")),
        ),
        "UNDERWATER": (
            ("WATERROTATE", "俯身进入水下城", "Tilt Into Underwater City", "手机向下倾斜", "水面高度", "背景从上到下变为水下城市并保留人物前景", ("PHONE-ROTATION", "BACKGROUND-WORLD")),
            ("WATERCAUSTIC", "水下焦散世界", "Underwater Caustic World", "虚拟水面光进入场景", "焦散速度", "建筑和地面出现随深度变化的流动焦散", ("CAUSTIC-PROJECTION", "SCENE-LIGHTING")),
            ("WATERBUBBLE", "水下气泡路径", "Underwater Bubble Path", "人物或镜头向前移动", "气泡密度", "气泡沿运动路径上升并在人物前后分层", ("BUBBLES", "MONOCULAR-DEPTH")),
            ("WATERVOICE", "声音水波世界", "Voice Ripple World", "人声持续出现", "水波幅度", "声音在水下背景中生成可见传播波纹", ("SOUND-VOLUME", "RIPPLE-DISPLACEMENT")),
            ("WATERBEAT", "节拍水下闪光", "Beat Underwater Flash", "音乐强拍到达", "水光脉冲", "水下城市焦散和气泡在强拍同步闪亮", ("AUDIO-BEAT", "SCENE-LIGHTING")),
        ),
        "NEON": (
            ("NEONLIGHT", "点亮霓虹世界", "Light Neon World", "点选一块真实灯牌", "霓虹配色", "灯牌颜色沿建筑边缘扩散成整片霓虹世界", ("LUMINOUS-CORE", "SCENE-LIGHTING")),
            ("NEONBEAT", "节拍霓虹脉冲", "Beat Neon Pulse", "音乐强拍到达", "霓虹脉冲", "街道霓虹线在强拍同步扩张发亮", ("AUDIO-BEAT", "VISUAL-STYLE")),
            ("NEONGAZE", "凝视霓虹点亮", "Gaze Neon Activation", "视线停留在建筑边缘", "点亮半径", "被注视建筑先出现霓虹轮廓再扩散到邻近结构", ("GAZE-FOCUS", "VISUAL-STYLE")),
            ("NEONMOVE", "移动霓虹拖影", "Moving Neon Echo", "镜头沿街道移动", "拖影长度", "霓虹灯牌沿相机运动方向留下彩色拖影", ("CAMERA-MOTION", "MOTION-AFTERIMAGE")),
            ("NEONVOICE", "人声霓虹频谱", "Voice Neon Spectrum", "人声频段能量变化", "频段增益", "街景霓虹颜色和高度随声音频谱变化", ("MUSIC-SPECTRUM", "SCENE-LIGHTING")),
        ),
        "PAPER": (
            ("PAPERDRAW", "手绘舞台展开", "Drawn Stage Reveal", "手指画出舞台边框", "笔触纹理", "边框内背景和服装逐步变成手绘纸张风格", ("TOUCH-DRAW", "VISUAL-STYLE")),
            ("PAPERBEAT", "节拍手绘翻页", "Beat Drawn Page", "音乐强拍到达", "翻页幅度", "手绘舞台在强拍翻到下一套纸张纹理", ("AUDIO-BEAT", "SPACE-FOLD")),
            ("PAPERPOSE", "姿态手绘定格", "Pose Drawn Freeze", "人物达到动作峰值", "定格描边", "人物峰值姿态变成纸上手绘剪影，背景继续运动", ("BODY-POSE", "VISUAL-STYLE")),
            ("PAPERCLOTH", "手绘服装跟随", "Drawn Clothing Follow", "服装随人物动作形变", "纹理稳定度", "手绘纹理贴合服装褶皱并保持跨帧一致", ("CLOTHING-REGION", "CLOTHING")),
            ("PAPERVOICE", "口播笔触脉冲", "Voice Brush Pulse", "人物说话音节出现", "笔触粗细", "每个音节让背景笔触变粗并产生短波纹", ("SOUND-VOLUME", "VISUAL-STYLE")),
        ),
    },
    "audio_lyrics": {
        "ORBIT": (
            ("ORBITTIME", "歌词逐字环绕", "Timed Lyric Orbit", "播放到歌词字词时间戳", "字距", "当前字词沿人物周围依次亮起并形成完整歌词环", ("LYRIC-TIMESTAMP", "LYRIC-RING")),
            ("ORBITBEAT", "节拍歌词环", "Beat Lyric Ring", "歌词播放期间强拍到达", "环弹跳", "歌词环在强拍扩大弹跳并拍间恢复", ("AUDIO-BEAT", "LYRIC-RING")),
            ("ORBITVOLUME", "音量歌词环", "Volume Lyric Ring", "演唱音量变化", "音量响应", "声音越响歌词环越厚越亮", ("SOUND-VOLUME", "LYRIC-RING")),
            ("ORBITGAZE", "凝视歌词词组", "Gaze Lyric Phrase", "视线停留在当前歌词词组", "词组放大", "被注视词组放大高亮，其余字符继续环绕", ("GAZE-FOCUS", "TEXT")),
            ("ORBITTOUCH", "拖动歌词环", "Drag Lyric Ring", "触摸并拖动歌词环", "歌词偏移", "歌词环移动到人物另一侧并保持时间同步", ("TOUCH-DRAW", "LYRIC-RING")),
        ),
        "RIBBON": (
            ("RIBBONDIRECTION", "声源方向彩带", "Directional Sound Ribbon", "声源进入指定方向角", "彩带宽度", "彩带从当前说话者方位生长并指向声音传播方向", ("SOURCE-DIRECTION",)),
            ("RIBBONVOLUME", "音量彩带厚度", "Volume Ribbon Width", "说话音量持续变化", "音量增益", "彩带随音量变粗变亮，停声后逐渐收窄", ("SOUND-VOLUME",)),
            ("RIBBONHANDOFF", "声源彩带移交", "Speaker Ribbon Handoff", "声源从一人切换到另一人", "移交时长", "彩带沿两人空间路径移动到新说话者", ("SOURCE-DIRECTION", "MULTI-PERSON-GRAPH")),
            ("RIBBONBEAT", "节拍声带波纹", "Beat Sound Ribbon", "音乐强拍到达", "波纹幅度", "声源彩带在强拍产生沿路径传播的波纹", ("AUDIO-BEAT", "RIPPLE-DISPLACEMENT")),
            ("RIBBONTOUCH", "拖拽声源彩带", "Drag Sound Ribbon", "触摸彩带并拖动控制点", "弯曲程度", "彩带路径随触摸弯曲但起点仍绑定说话者", ("TOUCH-DRAW", "SOURCE-DIRECTION")),
        ),
        "MASK": (
            ("MASKVOLUME", "音量光谱面罩", "Volume Spectrum Mask", "人物发声超过音量阈值", "频段增益", "脸部周围的频谱条随声音频段和音量变化", ("SOUND-VOLUME", "MUSIC-SPECTRUM")),
            ("MASKMOUTH", "嘴型频谱开合", "Mouth Spectrum Gate", "嘴型开合变化", "开合增益", "频谱面罩随嘴巴开合展开和收缩", ("MOUTH-SHAPE", "MUSIC-SPECTRUM")),
            ("MASKBEAT", "节拍光谱闪色", "Beat Spectrum Flash", "音乐强拍到达", "闪色强度", "面罩频谱在强拍统一闪色并保持脸部可见", ("AUDIO-BEAT", "MUSIC-SPECTRUM")),
            ("MASKGAZE", "视线选择频段", "Gaze Band Select", "视线停留在一个频段控件", "选中增益", "被凝视频段在面罩中放大突出", ("GAZE-FOCUS", "MUSIC-SPECTRUM")),
            ("MASKFADE", "停声面罩消隐", "Silence Mask Fade", "音量降到静音门限", "消隐时长", "光谱面罩从高频到低频依次熄灭", ("SOUND-VOLUME", "TIME-DECAY")),
        ),
        "SUBTITLE": (
            ("SUBBASS", "低音地震字幕", "Bassquake Captions", "低频强拍到达", "震动幅度", "地面字幕随低音上下震动并留下短残影", ("AUDIO-BEAT", "TEXT")),
            ("SUBTIME", "歌词时间字幕", "Timed Lyric Captions", "播放到歌词句时间戳", "字幕偏移", "当前歌词字幕按时间进入并在句末消散", ("LYRIC-TIMESTAMP", "TEXT")),
            ("SUBVOLUME", "音量字幕缩放", "Volume Caption Scale", "人声音量变化", "字号响应", "字幕随音量放大缩小并保持基线位置", ("SOUND-VOLUME", "TEXT")),
            ("SUBDIRECTION", "声源侧字幕", "Source-side Captions", "声源方向切换", "侧边距离", "字幕移动到当前说话者一侧并保留阅读方向", ("SOURCE-DIRECTION", "TEXT")),
            ("SUBTOUCH", "拖动字幕时间", "Caption Time Scrub", "拖动屏幕字幕片段", "时间偏移", "字幕移动到新位置并调整对应歌词时间", ("TOUCH-DRAW", "LYRIC-TIMESTAMP")),
        ),
        "DUET": (
            ("DUETHANDOFF", "多人接唱球", "Duet Sing-along Orb", "声源从一位演唱者切换到另一位", "传球弧线", "发光球沿两人空间路径飞向新声源", ("SOURCE-DIRECTION", "MULTI-PERSON-GRAPH")),
            ("DUETVOLUME", "合唱球大小", "Duet Orb Volume", "当前演唱者音量变化", "光球大小", "光球随当前声源音量缩放并保持人物绑定", ("SOUND-VOLUME", "MULTI-PERSON-GRAPH")),
            ("DUETBEAT", "节拍接唱传球", "Beat Duet Pass", "换唱时强拍到达", "传球速度", "光球在强拍瞬间完成说唱者间的传递", ("AUDIO-BEAT", "MULTI-PERSON-GRAPH")),
            ("DUETTOUCH", "触碰合唱连线", "Touch Duet Link", "两位演唱者手部接触", "连线亮度", "接触点生成连接双方的歌词光线", ("MULTI-PERSON-TOUCH", "TEXT")),
            ("DUETLYRIC", "对唱歌词分边", "Split Duet Lyrics", "歌词时间戳切换演唱角色", "左右间距", "不同演唱者歌词分别环绕对应人物并在接唱时换边", ("LYRIC-TIMESTAMP", "MULTI-PERSON-GRAPH")),
        ),
    },
    "effect_cinematography": {
        "ZOOM": (
            ("ZOOMBEAT", "节拍变焦", "Beat Zoom", "音乐强拍到达", "变焦比例", "画面向选中焦点快速推进并在拍间回弹", ("AUDIO-BEAT", "TUNNEL-WARP")),
            ("ZOOMPUNCH", "手势冲击变焦", "Gesture Punch Zoom", "击掌或握拳动作完成", "冲击幅度", "焦点对象快速放大并产生一次光学冲击环", ("HAND-GESTURE", "TUNNEL-WARP")),
            ("ZOOMGAZE", "凝视目标变焦", "Gaze Target Zoom", "视线停留在对象上", "凝视变焦速度", "取景器平滑向被注视对象推进", ("GAZE-FOCUS", "TUNNEL-WARP")),
            ("ZOOMREVERSE", "倒放回弹变焦", "Reverse Zoom Return", "向左拖动时间游标", "回弹时长", "上一段推进变焦按原路径倒序退回", ("TIME-REVERSE", "TUNNEL-WARP")),
            ("ZOOMSTAR", "星芒冲焦", "Starburst Punch-in", "焦点高光达到阈值", "星芒射线", "变焦推进时焦点同步绽放星芒并保持中心稳定", ("DYNAMIC-STARBURST", "TUNNEL-WARP")),
        ),
        "WIPE": (
            ("WIPEHAND", "手掌遮罩擦镜", "Hand Mask Wipe", "手掌完整遮住镜头后移开", "擦镜羽化", "手掌边缘揭开下一画面并保持人物轮廓", ("HAND-REGION", "FRAME-TRAVERSAL")),
            ("WIPEBODY", "人体经过擦镜", "Body Pass Wipe", "人物横向穿过画面", "过渡宽度", "人体轮廓后方逐步显露下一场景", ("BODY-SILHOUETTE", "FRAME-TRAVERSAL")),
            ("WIPEDOOR", "门框空间擦镜", "Doorframe Wipe", "镜头穿过门框", "边框厚度", "门框边缘作为转场线揭开下一镜头", ("WORLD-SPACE-ANCHOR", "FRAME-TRAVERSAL")),
            ("WIPETOUCH", "手指绘制擦镜", "Drawn Mask Wipe", "手指在屏幕画出擦镜路径", "笔刷大小", "触摸路径内显露下一画面并逐步扩张", ("TOUCH-DRAW", "FRAME-TRAVERSAL")),
            ("WIPEBEAT", "节拍遮罩闪切", "Beat Mask Wipe", "遮罩覆盖时强拍到达", "闪切速度", "强拍瞬间完成遮罩内外画面交换", ("AUDIO-BEAT", "FRAME-TRAVERSAL")),
        ),
        "EXPOSURE": (
            ("EXPOSUREROTATE", "长曝光旋转", "Long-exposure Spin", "手机旋转达到角速度阈值", "曝光长度", "夜景点光源围绕中心拉成旋转光轨", ("PHONE-ROTATION", "LIGHT-PAINT-BRUSH")),
            ("EXPOSUREHOLD", "停顿锁定曝光", "Pause-locked Exposure", "旋转后手机短暂停稳", "锁定时长", "旋转光轨固定在停顿姿态并停止继续拉伸", ("STATE-HYSTERESIS", "TRAJECTORY-ACCUMULATION")),
            ("EXPOSUREBEAT", "节拍曝光切片", "Beat Exposure Slices", "旋转期间强拍到达", "每拍采样", "每个强拍固定一层旋转光轨形成扇形切片", ("AUDIO-BEAT", "FRAME-DELAY")),
            ("EXPOSURECOLOR", "旋转色散曝光", "Chromatic Spin Exposure", "旋转速度持续上升", "色散距离", "旋转光轨按角速度分离出彩色边缘", ("CHROMATIC-ABERRATION", "CAMERA-MOTION")),
            ("EXPOSUREREVERSE", "曝光轨迹回卷", "Exposure Rewind", "手机反向旋转", "回卷窗口", "已有旋转光轨沿相反角度逐段收回", ("TIME-REVERSE", "PHONE-ROTATION")),
        ),
        "SPLIT": (
            ("SPLITDRAW", "手指拉出分屏", "Draw Split Screen", "两指拉出分屏线", "分屏间距", "同一人物左右运动路径显示在两个同步分区", ("TOUCH-DRAW", "SPACE-FOLD")),
            ("SPLITCHASE", "左右追拍分屏", "Split Chase", "人物横向跑过画面", "追拍延迟", "左右分屏分别显示当前与稍早的跑动位置", ("BODY-SKELETON", "FRAME-DELAY")),
            ("SPLITBEAT", "节拍分屏交换", "Beat Split Swap", "音乐强拍到达", "交换方向", "左右分屏在强拍交换位置并保持动作连续", ("AUDIO-BEAT", "SPACE-FOLD")),
            ("SPLITDEPTH", "前后景分屏", "Depth Split Screen", "点选前景和远景对象", "深度分界", "前后景分别进入两个分屏并保持遮挡", ("MONOCULAR-DEPTH", "OBJECT-INSTANCE")),
            ("SPLITMERGE", "合拢分屏", "Merge Split Screen", "两指向内合拢", "融合羽化", "两个分屏沿边界合并回单一画面", ("TOUCH-DRAW", "STATE-HYSTERESIS")),
        ),
        "FOCUS": (
            ("FOCUSTOUCH", "手指拉焦", "Finger Rack Focus", "依次点按前景和远景目标", "焦点过渡速度", "清晰区域从前景连续移动到远景目标", ("TOUCH-DRAW", "MONOCULAR-DEPTH")),
            ("FOCUSGAZE", "凝视拉焦", "Gaze Rack Focus", "视线停留在不同深度对象", "凝视焦点延迟", "焦平面平滑移动到被注视对象", ("GAZE-FOCUS", "MONOCULAR-DEPTH")),
            ("FOCUSBEAT", "节拍焦点跳转", "Beat Focus Jump", "多个目标已选择且强拍到达", "跳焦顺序", "焦点在每个强拍切换到下一个深度对象", ("AUDIO-BEAT", "OBJECT-INSTANCE")),
            ("FOCUSMOVE", "跟随移动焦点", "Moving Focus Follow", "选中对象连续移动", "跟焦平滑", "焦平面跟随对象深度变化并保持边缘清晰", ("OBJECT-POSE", "MONOCULAR-DEPTH")),
            ("FOCUSPULSE", "焦点穿刺光环", "Focus Pierce Ring", "焦点锁定完成", "穿刺光环", "目标清晰时出现一次沿深度扩散的光环", ("VIRTUAL-SPOTLIGHT", "MONOCULAR-DEPTH")),
        ),
    },
    "multi_person_interaction": {
        "ENERGY": (
            ("ENERGYTOUCH", "接触能量传递", "Contact Energy Transfer", "两人手掌首次接触", "传递速度", "能量从接触点沿双方手臂传播", ("MULTI-PERSON-TOUCH", "HAND-3D-TRAJECTORY")),
            ("ENERGYTHROW", "隔空能量抛接", "Thrown Energy Pass", "一人抛手势后另一人接手势", "飞行弧线", "能量球沿两人手掌之间的空间路径飞行", ("HAND-GESTURE", "MULTI-PERSON-GRAPH")),
            ("ENERGYBEAT", "节拍能量接力", "Beat Energy Relay", "领舞动作峰值命中强拍", "接力顺序", "能量在每个强拍传给下一位人物", ("AUDIO-BEAT", "MULTI-PERSON-GRAPH")),
            ("ENERGYVOICE", "声源能量传球", "Voice Energy Pass", "声源从一人切换到另一人", "传球速度", "发光能量球移动到新说话者身旁", ("SOURCE-DIRECTION", "MULTI-PERSON-GRAPH")),
            ("ENERGYRETURN", "双向能量回流", "Bidirectional Energy Return", "接收者做出反向推掌", "回流速度", "能量沿原路径反向回到发起者", ("TIME-REVERSE", "HAND-3D-TRAJECTORY")),
        ),
        "MIRROR": (
            ("MIRRORPOSE", "双人镜像接力", "Two-person Mirror Relay", "两人同时进入镜像姿态", "接力延迟", "一人动作沿对称轴传给另一人并延迟重复", ("BODY-SKELETON", "MULTI-PERSON-GRAPH")),
            ("MIRRORBEAT", "节拍镜像对舞", "Beat Mirror Duet", "双方动作峰值轮流命中强拍", "对舞相位", "两人在相邻强拍交替复制对方姿态", ("AUDIO-BEAT", "MULTI-PERSON-GRAPH")),
            ("MIRRORTOUCH", "触碰交换镜像", "Touch Swap Mirror", "双方手掌在中轴接触", "交换时长", "接触后两人的镜像角色和配色互换", ("MULTI-PERSON-TOUCH", "STATE-HYSTERESIS")),
            ("MIRRORBREAK", "同步失败裂变", "Mirror Sync Break", "两人姿态相似度下降到阈值", "裂变距离", "镜像轮廓从同步状态分裂成各自动作轨迹", ("BODY-POSE", "MOTION-AFTERIMAGE")),
            ("MIRRORMERGE", "同步合成双影", "Mirror Sync Merge", "两人恢复相同姿态并靠近中轴", "融合宽度", "两人轮廓在中轴融合成单一对称光影", ("BODY-POSE", "STATE-HYSTERESIS")),
        ),
        "STATUE": (
            ("STATUEPOSE", "三人合成雕像", "Three-person Living Statue", "三人形成闭合队形并停住", "融合平滑", "三个人体轮廓合成一座连续活体雕像", ("BODY-POSE", "MULTI-PERSON-GRAPH")),
            ("STATUEFREEZE", "队形时间冻结", "Formation Time Freeze", "闭合队形保持超过阈值", "冻结时长", "三人冻结成雕像，背景和其他人物继续运动", ("LOCAL-TIME-FREEZE", "MULTI-PERSON-GRAPH")),
            ("STATUEBREAK", "雕像分体", "Statue Breakapart", "任一人物离开闭合队形", "分体速度", "合成雕像沿每个人轮廓分开并恢复独立动作", ("BODY-SILHOUETTE", "STATE-HYSTERESIS")),
            ("STATUEBEAT", "节拍雕像换姿", "Beat Statue Pose", "音乐强拍到达", "换姿拍数", "雕像在每个强拍切换到新的群体姿态", ("AUDIO-BEAT", "BODY-POSE")),
            ("STATUEROTATE", "绕拍活体雕像", "Orbit Living Statue", "手机围绕队形旋转", "视差强度", "合成雕像保持世界位置并随视角显示层次", ("CAMERA-MOTION", "MONOCULAR-DEPTH")),
        ),
        "SHOULDER": (
            ("SHOULDERBURST", "碰肩爆裂", "Shoulder Contact Burst", "两人肩部进入接触范围", "爆裂半径", "接触点喷发光粒并沿双方轮廓扩散", ("MULTI-PERSON-TOUCH", "SPARKS")),
            ("SHOULDERBEAT", "节拍碰肩闪光", "Beat Shoulder Flash", "碰肩瞬间命中强拍", "闪光强度", "接触点在强拍爆亮并产生一圈冲击波", ("AUDIO-BEAT", "LUMINOUS-CORE")),
            ("SHOULDERSWAP", "擦肩颜色交换", "Shoulder Color Swap", "两人擦肩后分开", "交换时长", "双方轮廓光颜色在接触后互换", ("MULTI-PERSON-TOUCH", "VIRTUAL-RIM-LIGHT")),
            ("SHOULDERTRAIL", "擦肩双向轨迹", "Shoulder Crossing Trails", "两人沿相反方向擦肩", "轨迹长度", "接触点向双方离开方向拉出两条能量轨迹", ("MULTI-PERSON-GRAPH", "TRAJECTORY-ACCUMULATION")),
            ("SHOULDERFREEZE", "碰肩定格", "Shoulder Contact Freeze", "肩部接触保持超过阈值", "定格时间", "接触瞬间两人局部冻结并在分开后恢复", ("LOCAL-TIME-FREEZE", "MULTI-PERSON-TOUCH")),
        ),
        "RING": (
            ("RINGFORMATION", "队形环形光", "Formation Light Ring", "三人以上进入环形队形", "光环厚度", "光环固定在队形中心并连接每个人外缘", ("MULTI-PERSON-GRAPH", "WORLD-SPACE-ANCHOR")),
            ("RINGBREATH", "队形呼吸光环", "Formation Breathing Ring", "多人动作相位趋于一致", "呼吸幅度", "同步程度越高中心光环越亮并向外呼吸", ("BODY-POSE", "MULTI-PERSON-GRAPH")),
            ("RINGBEAT", "节拍队形环", "Beat Formation Ring", "全员动作峰值命中强拍", "环脉冲", "光环在强拍扩张并沿人物顺序依次点亮", ("AUDIO-BEAT", "MULTI-PERSON-GRAPH")),
            ("RINGROTATE", "旋转队形环", "Rotating Formation Ring", "人物沿环形队形移动", "旋转速度", "光环纹理跟随队形旋转而中心保持稳定", ("BODY-SKELETON", "WORLD-SPACE-ANCHOR")),
            ("RINGBREAK", "离队断环", "Formation Ring Break", "任一人物离开环形队形", "断裂衰减", "光环在离队位置断开并向两侧逐渐熄灭", ("MULTI-PERSON-GRAPH", "TIME-DECAY")),
        ),
    },
})


IDEA_PAIRINGS = {
    family: tuple(
        (motif_slug, behavior[0])
        for motif_slug, behaviors in motif_map.items()
        for behavior in behaviors
    )
    for family, motif_map in IDEA_COMPATIBLE_BEHAVIORS.items()
}

BEHAVIOR_ATOM_DEPENDENCIES = {
    family: {
        behavior[0]: behavior[6]
        for behaviors in motif_map.values()
        for behavior in behaviors
    }
    for family, motif_map in IDEA_COMPATIBLE_BEHAVIORS.items()
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


def _validate_idea_pairing_specs(atom_ids: set[str]) -> None:
    if tuple(IDEA_COMPATIBLE_BEHAVIORS) != IDEA_FAMILY_ORDER:
        raise ValueError("compatible behavior families must follow IDEA_FAMILY_ORDER")
    if tuple(IDEA_PAIRINGS) != IDEA_FAMILY_ORDER:
        raise ValueError("idea pairing families must follow IDEA_FAMILY_ORDER")
    if tuple(BEHAVIOR_ATOM_DEPENDENCIES) != IDEA_FAMILY_ORDER:
        raise ValueError("behavior dependency families must follow IDEA_FAMILY_ORDER")

    for family in IDEA_FAMILY_ORDER:
        motif_rows = IDEA_FAMILY_SPECS[family]["motifs"]
        motif_slugs = tuple(motif[0] for motif in motif_rows)
        compatible = IDEA_COMPATIBLE_BEHAVIORS[family]
        if tuple(compatible) != motif_slugs:
            raise ValueError(f"{family} compatible motif order does not match motifs")

        expected_pairings = []
        behavior_slugs = []
        expected_dependencies = {}
        for motif in motif_rows:
            motif_slug = motif[0]
            _resolve_atom_ids(atom_ids, motif[7])
            behaviors = compatible[motif_slug]
            if len(behaviors) != 5:
                raise ValueError(f"{family}/{motif_slug} must have five behaviors")
            for behavior in behaviors:
                if len(behavior) != 7:
                    raise ValueError(
                        f"{family}/{motif_slug} behavior rows must have seven fields"
                    )
                behavior_slug = behavior[0]
                behavior_atom_slugs = behavior[6]
                if not behavior_atom_slugs:
                    raise ValueError(
                        f"{family}/{behavior_slug} must declare behavior atom dependencies"
                    )
                _resolve_atom_ids(atom_ids, behavior_atom_slugs)
                expected_pairings.append((motif_slug, behavior_slug))
                behavior_slugs.append(behavior_slug)
                expected_dependencies[behavior_slug] = behavior_atom_slugs

        if len(behavior_slugs) != len(set(behavior_slugs)):
            raise ValueError(f"{family} behavior slugs must be unique")
        if tuple(expected_pairings) != IDEA_PAIRINGS[family]:
            raise ValueError(f"{family} pairings must match compatible behavior rows")
        if expected_dependencies != BEHAVIOR_ATOM_DEPENDENCIES[family]:
            raise ValueError(f"{family} behavior atom dependencies are inconsistent")


def _idea_from_specs(
    family: str,
    motif: tuple[str, ...],
    behavior: tuple[str, ...],
    atoms_by_id: Mapping[str, Mapping[str, object]],
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
        motif_atom_slugs,
        spatial_scope,
        motif_signal,
        motif_failure,
    ) = motif
    (
        behavior_slug,
        behavior_zh,
        behavior_en,
        behavior_trigger,
        behavior_control,
        visible_behavior,
        behavior_atom_slugs,
    ) = behavior
    resolved_atom_ids = _stable_unique(
        _resolve_atom_ids(
            set(atoms_by_id),
            (*motif_atom_slugs, *behavior_atom_slugs),
        )
    )
    atom_signals = _stable_unique(
        signal
        for atom_id in resolved_atom_ids
        for signal in atoms_by_id[atom_id]["required_signals"]
    )
    atom_modules = "、".join(
        str(atoms_by_id[atom_id]["name_zh"])
        for atom_id in resolved_atom_ids
    )
    family_title_zh = IDEA_FAMILY_SPECS[family]["title_zh"]
    family_title_en = IDEA_FAMILY_SPECS[family]["title_en"]
    visible_effect = f"{motif_zh}触发{behavior_zh}时，{visible_behavior}；{target_object}始终可见且与画面空间保持对应"
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
        "preview_pipeline": f"低分辨率预览明确调用{atom_modules}，按其原子信号驱动{behavior_zh}并合成可见结果。",
        "post_pipeline": f"录制后沿用{atom_modules}重建{motif_zh}，细化{spatial_scope}边缘、遮挡和{behavior_control}曲线。",
        "required_signals": _stable_unique([*atom_signals, motif_signal]),
        "atom_ids": resolved_atom_ids,
        "temporal_window": "触发前 12 帧至可见结果稳定后 24 帧",
        "continuity_challenges": [motif_failure, f"{behavior_zh}期间对象身份、遮挡和参数响应必须连续"],
        "edge_difficulty": "high" if ordinal % 3 else "research",
        "execution_targets": ["mobile_preview", "mobile_post"],
        "generation_level": "perceptual_effect",
        "risks": [motif_failure, f"{behavior_trigger}不稳定时可能造成{visible_behavior}的时序跳变"],
        "novelty": f"把{motif_zh}的对象语义与{behavior_zh}的时序行为绑定，触发和参数共同改变可见结果，而不是只更换场景。",
        "shareability": f"短视频中能直接看见{visible_effect}，适合一键录制、回看和分享。",
        "product_value": f"作为手机录像中的{family_title_zh}创作玩法，提供{motif_parameter}与{behavior_control}两个可理解的调节入口。",
        "reference_ids": [],
        "combinable_effect_ids": [],
        "status": "idea_only",
    }


def build_ideas() -> list[dict[str, object]]:
    """Return 300 ideas by traversing only reviewed motif-behavior pairings."""

    atoms = build_atoms()
    atoms_by_id = {atom["atom_id"]: atom for atom in atoms}
    _validate_idea_pairing_specs(set(atoms_by_id))
    ideas = []
    ordinal = 0
    for family in IDEA_FAMILY_ORDER:
        family_spec = IDEA_FAMILY_SPECS[family]
        motifs = {motif[0]: motif for motif in family_spec["motifs"]}
        compatible_behaviors = IDEA_COMPATIBLE_BEHAVIORS[family]
        for motif_slug, behavior_slug in IDEA_PAIRINGS[family]:
            behavior = next(
                behavior
                for behavior in compatible_behaviors[motif_slug]
                if behavior[0] == behavior_slug
            )
            ideas.append(
                _idea_from_specs(
                    family,
                    motifs[motif_slug],
                    behavior,
                    atoms_by_id,
                    ordinal,
                )
            )
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
