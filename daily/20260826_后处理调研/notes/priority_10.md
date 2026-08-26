# 十个组合创新概念

组合创新不是现有产品清单，而是把已核验的产品/论文能力重新组织成手机录像预研方向。

## PC-01 夜景电影人像录像 (Night Cinematic Portrait Video)
- 组成：DD-02, DD-03, DD-08, DD-09
- 用户故事：用户在夜景城市或演唱会拍人像时，一次录像同时获得稳定肤色、可调主光、可调景深和高光保护。
- 交互：拍摄前选择自然/电影两档；录后可调整主光方向、光圈和人像恢复强度。
- 系统链路：RAW/YUV + AE/IMU -> 人像/深度/高光分析 -> 夜景恢复 -> 人像身份锚定 -> relight/defocus -> 色彩管理 -> 编码。
- MVP：单人半身、1080p30，在线夜景恢复和粗景深，录后完成打光和边界细化。
- 数据：真实夜景人像、多曝光、双摄深度、不同肤色与运动；使用可控 HDR 灯光合成补足标签。
- 指标：identity cosine、肤色偏差、flicker、高光裁切率、发丝边界和用户偏好。
- 风险：人脸身份或肤色改变、景深边界、夜景纹理幻觉。
- 真实性边界：perceptual/generative，必须保留原片和编辑 mask。

## PC-02 语义光轨运动录像 (Semantic Light-Trail Action Video)
- 组成：DD-01, DD-04, DD-07, DD-18
- 用户故事：用户拍跑步、骑行、舞蹈或车流时，主体保持清晰，背景/灯光形成可控拖影，并自动抓取精彩慢动作。
- 交互：选择主体、拖影长度和节奏；系统自动保存事件前后片段。
- 系统链路：视频/IMU/音频 -> 主体与运动分解 -> 稳定 -> 时间积分/光轨 -> 局部插帧 -> 编码。
- MVP：固定机位车流和单人跑步，支持两档拖影及 2x 局部慢放。
- 数据：短曝光序列、真实运动视频、IMU、音频事件、运动 mask。
- 指标：主体清晰度、轨迹连续性、ghosting、慢动作伪影、触发准确率。
- 风险：运动分解失败，生成轨迹不物理，事件误触发。
- 真实性边界：主体恢复偏 faithful，轨迹效果属于 generative。

## PC-03 智能采访摄影师 (AI Interview Camera Operator)
- 组成：DD-12, DD-19, DD-21, DD-25
- 用户故事：手机在双人/多人采访中自动识别说话人，平滑构图和拉焦，同时保持稳定和跨镜头肤色一致。
- 交互：用户选择保守/积极运镜，随时点选人物锁定或关闭自动切换。
- 系统链路：多麦克风 + face tracks + depth/IMU -> 说话人关联 -> focus/framing policy -> 稳定/切镜 -> look continuity。
- MVP：双人采访、wide/medium 两种景别、自动拉焦和手动锁定。
- 数据：多人对话、声源位置、face track、焦点和专业剪辑决策标注。
- 指标：speaker-face matching、错误切换、焦点命中、画面跳变和用户控制满意度。
- 风险：混响/抢话、自动策略打扰创作者、隐私。
- 真实性边界：faithful，不修改内容事实。

## PC-04 空间电影运镜 (Spatial Cinematic Reframing)
- 组成：DD-05, DD-13, DD-17, DD-27
- 用户故事：用户用普通手持视频录完后，生成小幅滑轨、推拉、横竖屏重构和景深变化。
- 交互：选择预设轨迹，界面显示原始区域与生成画外区域。
- 系统链路：高分辨率视频/深度/IMU -> scene layers -> 轨迹规划 -> warping -> constrained outpainting -> 景深/色彩。
- MVP：静态背景、单人、10% 画外延展和水平滑轨。
- 数据：多视角视频、宽幅裁切、深度、相机轨迹和动态遮挡。
- 指标：几何一致性、生成区域 temporal error、身份保持、用户可信度。
- 风险：画外幻觉、几何撕裂、文字与人物身份变化。
- 真实性边界：generative，必须输出生成区域和原片。

## PC-05 演唱会录像增强套件 (Concert Video Enhancement Suite)
- 组成：DD-01, DD-08, DD-16, DD-30
- 用户故事：演唱会录像保持舞台高光和暗部细节，并可录后增加跟随歌手的虚拟追光和受控星芒。
- 交互：实时显示高光保护，录后调追光目标、颜色、星芒和强度。
- 系统链路：夜景/HDR restoration -> performer tracking -> spotlight relighting -> starburst/flare -> audio-synced look。
- MVP：单个歌手、一个虚拟追光、两档星芒和高光保护。
- 数据：演唱会/舞台、LED 屏、强高光、远距离人物、观众遮挡和音乐节拍。
- 指标：高光 clipping、人物 track、光效 flicker、色彩稳定和主观电影感。
- 风险：真实舞台灯和虚拟灯冲突、远距离人脸误恢复、光效遮挡表演。
- 真实性边界：夜景增强 faithful，虚拟追光和星芒 perceptual/generative。

## PC-06 旅行净景与天气编辑 (Clean Travel Scene and Weather Editing)
- 组成：DD-10, DD-15, DD-24, DD-13
- 用户故事：旅行录像可清除短时路人、电线、镜头污渍，替换天空并适配横竖屏。
- 交互：系统自动给出问题 mask，用户逐项勾选清理；所有编辑可回退。
- 系统链路：质量检测 -> mask/track -> 背景 memory -> temporal inpainting -> sky/light coupling -> outpainting。
- MVP：固定机位景点，移除 1-2 个路人，预置天空，10% 边界延展。
- 数据：旅行景点、动态人群、天空/天气、雨滴和背景板。
- 指标：边界、temporal warping、背景重复、用户接受度和事实标注清晰度。
- 风险：生成改变真实场景、背景幻觉、透明/树枝边界。
- 真实性边界：generative，逐项保存 mask 和编辑参数。

## PC-07 连续变焦电影色彩 (Continuous-Zoom Cinematic Color)
- 组成：DD-06, DD-11, DD-20, DD-25
- 用户故事：用户在广角到长焦连续录像时，不再看到曝光、色彩、噪声和肤色跳变，并获得统一电影风格。
- 交互：用户选择 look；系统自动切镜与细节融合，可关闭长焦增强。
- 系统链路：multi-camera warm-up -> alignment/fusion -> color/noise transform -> semantic LUT -> encoder。
- MVP：主摄+长焦、日景/室内、人像和建筑，三档变焦切换。
- 数据：同步多摄、color chart、人像、不同焦段/曝光/运动和 lens metadata。
- 指标：switch transient、肤色 delta、锐度跳变、ghosting、稳定和温度。
- 风险：视差、同步、不同动态范围和高成本。
- 真实性边界：faithful/perceptual，不生成新内容。

## PC-08 身份可信的人像直播增强 (Identity-Safe Live Portrait Enhancement)
- 组成：DD-09, DD-22, DD-23, DD-28
- 用户故事：直播或长时间自拍视频中，改善逆光、眼镜反光、皮肤和头发细节，但不改变身份，并随温度自动降级。
- 交互：区域化强度控制和身份保护开关；温控降级时只降低细节、不改变肤色。
- 系统链路：face track/parsing -> local HDR -> region restoration -> identity check -> thermal scheduler -> encoder。
- MVP：单人 1080p30，脸/头发/眼镜三分区，两档温控。
- 数据：多肤色、多年龄、眼镜、逆光、长时间直播和设备 profiling。
- 指标：identity cosine、肤色、区域 flicker、FPS/温度、用户对自然度评价。
- 风险：外貌改变、群体偏差、温控导致画质跳变。
- 真实性边界：perceptual，禁止生成性脸型/年龄改变。

## PC-09 低功耗专业录像代理 (Low-Power Professional Video Proxy)
- 组成：DD-14, DD-28, DD-07, DD-11
- 用户故事：长时间录像时实时输出稳定可看的代理视频，同时保存少量中间信息，停止后再生成高质量母版。
- 交互：显示实时版和高质量重算进度；用户可选择立即导出代理或等待母版。
- 系统链路：online lightweight stabilization/look -> proxy encoder + metadata store -> offline restoration/look rerender。
- MVP：1080p 10分钟，实时轻量稳定/LUT，录后 30 秒片段高质量重算。
- 数据：不同热状态、存储和负载下的 profiling；同一场景 proxy/HQ 配对。
- 指标：实时 FPS、温度、存储、重算时长、母版质量和中断恢复。
- 风险：存储/后台耗电、用户等待、重算失败。
- 真实性边界：faithful/perceptual，保留原始代理和参数。

## PC-10 可信生成式手机录像编辑 (Trustworthy Generative Mobile Video Editing)
- 组成：DD-13, DD-24, DD-27, DD-14
- 用户故事：用户可做天空、天气、画外延展和局部背景编辑，同时系统明确展示哪些区域是生成的。
- 交互：编辑区域默认受限；脸、文字和主体默认保护；导出可携带生成区域 metadata。
- 系统链路：protected/editable masks -> keyframe generation -> temporal propagation -> consistency audit -> export original/mask/edit。
- MVP：天空和背景边界两类编辑，片段不超过 5 秒，禁止修改脸和文字。
- 数据：局部编辑三元组、真实视频、mask/depth/flow、文字和身份保护样本。
- 指标：保护区误差、生成区时序、身份/文字保存、用户是否理解生成边界。
- 风险：事实改变、隐私、版权、错误身份和不可逆导出。
- 真实性边界：generative，必须保留原片、hash、mask 和编辑参数。
