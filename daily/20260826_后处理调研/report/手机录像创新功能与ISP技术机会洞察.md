# 手机录像创新功能与 ISP 后处理技术机会洞察

> 研究日期：2026-08-26  | 研究目录：`daily/20260826_后处理调研`
> 研究对象：手机录像、ISP 后处理、计算摄影、相机玩法、端侧视频算法和生成式视频编辑

## 摘要

本报告面向 ISP 视频和手机影像预研，采用“产品创意池 + 技术可实现性评估 + 证据图谱”的组织方式。研究不把录像能力局限为传统降噪、锐化和防抖，而是将专业相机、电影机、运动相机、无人机、短视频 App、后期软件、学术论文和公开专利中的能力，重新映射到手机录像链路。

本阶段建立 112 条机会记录，覆盖 14 个技术能力族；完成 30 张技术深度卡和 10 个组合创新概念；来源清单包含 45 条产品/论文/本地资料，筛出 11 篇核心论文、8 个数据集，并保留 OpenAlex 初筛论文元数据 381 条。机会记录不是产品承诺，其中主体为 E5（本报告推演），外部证据与视频化推演在表格中分栏。

## 1. 研究口径与证据边界

### 1.1 录像优先

拍照能力只有在进一步说明连续帧、运动、曝光、遮挡、功耗和交互之后，才进入录像机会图谱。实时预览、录制在线处理、录后设备处理和云端重处理分别标注，不把照片功能直接改名为视频功能。

### 1.2 证据等级

- **E1 已量产**：官方产品页、说明书或支持文档明确描述。
- **E2 公开演示/有限发布**：官方白皮书、SDK、Demo 或发布材料。
- **E3 学术原型**：论文、补充材料、开源代码或实验报告。
- **E4 专利储备**：公开专利文本，仅证明提出过方案。
- **E5 本报告推演**：基于已有证据提出的录像化创新，不能当作行业事实。

### 1.3 真实性边界

- **Faithful enhancement 忠实增强**：尽量恢复真实内容，例如夜景降噪、去模糊、滚动快门校正和跨摄色彩连续。
- **Perceptual enhancement 感知增强**：允许改变质感和风格，例如胶片颗粒、虚拟镜头、局部 LUT 和受控人像增强。
- **Generative creation 生成式创作**：允许补全、替换或重构，但必须保存原片、生成 mask、编辑参数和可回退版本。

## 2. 技术机会总览

本阶段把机会拆为 14 个能力族，每个能力族先形成 8 条候选记录。

| 能力族 | 候选数 | 录像落点 |
|---|---:|---|
| 计算光学与虚拟镜头 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 光照重构与可控布光 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 景深、焦点与空间感 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 快门、时间与运动轨迹 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 虚拟摄影机与智能运镜 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 多摄融合与连续变焦 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 智能稳定与运动画质 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 夜景、HDR 与复杂光源 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 人像细节与身份一致性 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 环境清理与场景重构 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 专业影像与色彩科学 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 声音驱动的录像能力 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 生成式叙事与内容重构 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |
| 拍摄辅助与质量守护 | 8 | 实时预览、在线录像或录后处理，详见 Opportunity_Map |

### 2.1 三个最值得持续投入的主线

1. **视频真实性增强主线**：夜景 HDR、运动复原、滚动快门、跨摄连续、局部人像增强。这些方向产品价值稳定，难点是时序和系统协同，适合作为 ISP/NPU 联合优化对象。
2. **电影化计算摄影主线**：动态星芒、虚拟景深、虚拟镜头、语义 LUT、虚拟运镜。它们更容易形成用户可感知差异，但需要把效果参数化，不能依赖逐帧贴图。
3. **可信生成式录像主线**：天空/天气/画外延展/局部背景编辑。它们创新性最高，但必须把“生成了什么”纳入产品交互和文件元数据。

## 3. 从相机与软件玩法迁移到手机录像

### 3.1 手机原生影像已经验证的能力

Apple Cinematic mode 证明了焦点转移和视频景深可以成为手机原生体验；Google Pixel Cinematic Blur 和 Video Boost 分别代表视频景深和云端高质量视频处理；Samsung Super Steady 代表手机级稳定；DJI、GoPro、Insta360 则把稳定、地平线锁定、主体跟踪和自动构图推到运动影像产品中。Blackmagic Camera、DaVinci Resolve、After Effects 和 CapCut 说明，移动拍摄和后期编辑之间正在形成连续工作流。

### 3.2 迁移的关键不是功能名称，而是时序状态

相机和后期软件中很多功能在手机录像化时都需要新增状态：对象 track ID、关键帧、光源 ID、曝光轨迹、镜头状态、深度层、生成 mask、置信度和回退信息。没有这些状态，模型容易出现 flicker、texture crawl、identity drift、mask leakage 和 exposure breathing。

## 4. 端到端录像后处理系统框架

```text
Sensor / RAW / Multi-camera / Depth / IMU / Audio
                    |
        Front-end ISP and synchronization
                    |
     Detection: subject / light / motion / depth / quality
                    |
       Temporal memory: track / keyframe / flow / state
                    |
 Restoration / relighting / rendering / generative editing
                    |
    Temporal consistency + confidence + rollback metadata
                    |
        Color management / encoder / preview / export
```

### 4.1 实时与录后不是二选一

建议采用分级链路：实时预览只做低分辨率分析、粗粒度效果和质量提示；录像在线处理使用因果模型和有限参考帧；录后处理保留 proxy、关键帧、深度、mask、IMU 和曝光状态，再使用双向模型或生成式模型重算。FlashVSR、视频 VAE 和 DiT/FLUX 资料说明，latent 表征、特征传播和蒸馏可以把复杂模型压缩到更接近视频应用的推理形态，但具体手机 FPS、内存和功耗仍必须在目标 SoC 上实测。

## 5. 核心论文与数据集路线

### 5.1 核心论文

下表不是全量综述，而是本阶段用于支撑视频后处理功能设计的核心入口。`Paper_Discovery_381` 中的宽搜结果只作为发现池，不能替代论文正文核验。

| 论文 | 年份/会议 | 方向 | 对手机录像的价值 |
|---|---|---|---|
| VRT: A Video Restoration Transformer | 2024 / IEEE Transactions on Image Processing | motion_quality | Transformer-based video restoration and temporal alignment are directly relevant to mobile video enhancement. |
| Robust High-Resolution Video Matting with Temporal Guidance | 2022 / WACV | scene_editing | Temporal matting supports hair, foreground editing, relighting, background replacement, and video segmentation. |
| Real-Time High-Resolution Background Matting | 2021 / CVPR | scene_editing | Shows a practical path for real-time foreground extraction with auxiliary input, useful for mobile video effects. |
| MODNet: Real-Time Trimap-Free Portrait Matting via Objective Decomposition | 2022 / AAAI | portrait_identity | Portrait matting without a trimap is a core primitive for phone video relighting, blur, and background effects. |
| Variable Aperture Bokeh Rendering via Customized Focal Plane Guidance | 2024 / arXiv | depth_focus | Directly informs virtual aperture and bokeh controls that can be extended from images to temporally consistent video. |
| VFHQ: A High-Quality Video Face Super-Resolution Dataset | 2022 / arXiv | portrait_identity | High-quality facial video data and identity continuity are directly useful for phone portrait video restoration. |
| CelebV-HQ: A Large-Scale Video Facial Attributes Dataset | 2022 / arXiv | portrait_identity | Facial attributes and video identity coverage support region-aware portrait enhancement and identity loss design. |
| HDTF: High-Definition Talking-Face Dataset | 2020 / arXiv | audio_visual | Talking-face video supports speaker-aware framing, focus, portrait restoration, and audio-visual research. |
| High-Resolution Image Synthesis with Latent Diffusion Models | 2022 / CVPR | generative_video | Latent compression and diffusion conditioning are foundations for efficient image/video editing and restoration. |
| MAGVIT: Masked Generative Video Transformer | 2022 / CVPR | generative_video | Video tokenizer and temporal latent modeling are key to efficient video editing and restoration. |
| FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | 2025 / arXiv | motion_quality | One-step video SR and targeted flow distillation provide a direct route for low-latency video restoration research. |

推荐先读 `VRT` 和 `FlashVSR` 理解视频复原、特征传播和低步数推理；再读实时背景抠图、视频抠图与 `MODNet` 理解人像/环境 mask 的时序问题；随后读可变光圈散景、人像视频数据和视频 VAE/DiT，建立电影化效果与生成式编辑的基础。

### 5.2 数据集与数据制作入口

| 数据集 | 用途 | 访问/许可边界 |
|---|---|---|
| Flickr-Faces-HQ (FFHQ) | 高质量人脸静态训练源；可用于身份/细节预训练和退化合成 | 研究与单图许可需逐图核查 |
| CelebA | 人脸属性、身份和编辑控制数据 | 非商业研究条款 |
| VGGFace2 | 身份保持与人脸验证 | 需遵循官方研究使用条件 |
| VFHQ | 高质量视频人脸超分/复原 | 需核查项目下载与再分发条件 |
| CelebV-HQ | 高质量人脸视频与属性 | 需核查项目条款 |
| HDTF | 高清说话人视频、音画联合 | 原视频版权仍需遵循来源方 |
| VFRxBenchmark | 真实视频人脸复原评测 | 旧项目链接返回 404，优先以论文核验 |
| NTIRE 2025 Real-World Face Restoration | 真实人脸复原竞赛数据与评测 | 挑战赛条款 |

数据集不能简单混合使用。静态人脸数据适合身份和细节预训练，视频人脸数据适合时序与身份稳定，真实退化/挑战数据适合建立评测集。对夜景、光效、多摄、IMU、曝光和镜头切换，本项目仍需要自行采集手机连续视频，并保留 sensor/ISP metadata。

### 5.3 专利检索状态

当前仅登记 2 条待核验专利检索主题，尚未获得可稳定引用的公开专利号和正文，因此不将其写成 E4 已核验事实。后续应按申请人、公开日、权利要求和法律状态逐条补齐。

## 6. 30 个技术深度方向

### DD-01 动态星芒与镜头眩光视频化 / Temporal starburst and lens-flare rendering
- **能力族 / 模式 / 边界**：computational_optics / online_recording / perceptual
- **来源**：Cinematic mode | Apple | E1; Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3
- **研究问题**：逐帧叠加星芒/flare 会出现亮度跳变、光源形状游走和镜头运动不一致。
- **技术方案**：先检测高亮光源，再用光源轨迹、相机姿态和参数化 PSF 生成 flare；将光源 ID、中心、强度和遮挡状态写入 temporal state。
- **输入信号**：YUV/RGB + 连续帧 + IMU/电子防抖运动 + 高亮点 mask；可选深度。
- **模型链路**：轻量高亮检测器 + 光源 tracking + 参数化渲染器；生成式版本可用 latent adapter，但不应作为第一版在线链路。
- **训练数据**：真实夜景/舞台视频；合成多种光圈、鬼影和星芒参数；加入不同曝光、镜头污渍和 rolling-shutter 扰动。
- **LOSS / objective**：L = L_render_recon + 0.2 L_temporal_warp + 0.1 L_highlight_shape + 0.05 L_flicker；权重为起始假设，必须做梯度与消融。
- **时序策略**：光源 track + EMA 强度 + 关键帧重新估计；遮挡或镜头切换时重置。
- **端侧落点**：预览低分辨率分析，录制时只对光源 ROI 渲染；4K 录后再做高质量 flare。
- **风险**：把真实光学缺陷变成错误内容；flare 过强会遮挡主体；不同镜头的光学风格难以统一。
- **MVP**：先实现 1-3 个高亮点、2 种星芒形状、固定参数化鬼影，并验证 30fps 预览稳定性。

### DD-02 人像主光与轮廓光重定向 / Portrait key-light and rim-light steering
- **能力族 / 模式 / 边界**：relighting / offline_device / generative
- **来源**：Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3; AuthFace | ReadPaper local PortraitSR library | E3; Video background removal | CapCut | E2
- **研究问题**：拍摄时光线不可控；静态 relighting 迁移到录像会产生脸部颜色和阴影闪烁。
- **技术方案**：以 face/body parsing、法线或 3D face proxy 估计可解释的 light field，再使用条件生成器重建局部光照；只在 mask 内生成，背景使用保守颜色匹配。
- **输入信号**：连续 RGB/YUV + face/body mask + landmark + 可选深度/IMU。
- **模型链路**：轻量 intrinsic decomposition + temporal U-Net/DiT adapter；高质量录后可接 FLUX/扩散教师模型蒸馏。
- **训练数据**：HDR 人像、多光源人像、真实手机视频；用光照可控 3D 人脸和渲染数据补充主光方向、颜色、强度标签。
- **LOSS / objective**：重建 L1/Charbonnier + ROI perceptual + identity cosine + temporal warp + boundary alpha + illumination smoothness；身份损失只作用于脸部高层 embedding。
- **时序策略**：关键帧估计 light code，帧间用光流/track 传播；表情或大姿态变化触发局部重估。
- **端侧落点**：实时预览只给低频亮度变化；录后做细节和阴影生成。必须保留原片和 relight mask。
- **风险**：改变肤色、五官或身份；头发和眼镜边界泄漏；不同人的皮肤反射模型差异大。
- **MVP**：只做正面单人、主光左右移动、三档强度，先验证肤色稳定和身份相似度。

### DD-03 录后改光圈与时序景深 / Post-capture aperture and temporal depth-of-field
- **能力族 / 模式 / 边界**：depth_focus / offline_device / perceptual
- **来源**：Cinematic Blur | Google | E1; FluxSR | ReadPaper local Flux library | E3; TIGER: A Training Framework for Video Face Restoration | ReadPaper local PortraitSR library | E3
- **研究问题**：视频虚化比单帧更容易出现头发抖动、边缘漏背景和深度跳变。
- **技术方案**：用时序 depth + segmentation + motion boundary refinement 生成 blur field；对前景边界采用多层 alpha 和不确定性融合。
- **输入信号**：连续 RGB + depth/dual-camera disparity + person/scene mask + optical flow。
- **模型链路**：轻量深度网络 + recurrent refinement + differentiable defocus renderer。
- **训练数据**：真实双摄/多摄视频、带深度相机数据、电影镜头数据；合成不同 aperture、focus distance 和运动模糊。
- **LOSS / objective**：深度 L1 + alpha boundary + perceptual + temporal consistency + blur-kernel regularization；对发丝设置高权重边界采样。
- **时序策略**：深度低频状态保持，运动边界局部更新；长遮挡后回到关键帧重估。
- **端侧落点**：预览只显示粗粒度虚化；录后 1080p/4K 做高质量 alpha refinement。
- **风险**：深度错层导致人脸/头发被切断；生成 blur 改变真实空间关系；低照度深度不可靠。
- **MVP**：单人半身、背景相对静止、三档 aperture；用 flicker rate 和 hair-boundary IoU 做核心指标。

### DD-04 语义长曝光与主体保持清晰 / Semantic long exposure with sharp subjects
- **能力族 / 模式 / 边界**：temporal_exposure / offline_device / generative
- **来源**：FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3; WF-VAE: Wavelet Flow VAE for Video Compression | ReadPaper local ENC_DEC library | E3
- **研究问题**：传统长曝光视频会同时拖糊主体；简单帧叠加不能处理遮挡与非刚性运动。
- **技术方案**：分离 camera motion、background motion、subject motion，对不同区域使用不同时间积分；用视频 latent/warp 保留主体纹理。
- **输入信号**：连续帧 + optical flow + IMU + subject mask + optional depth。
- **模型链路**：motion decomposition + feature propagation + semantic compositor；录后可使用视频扩散/flow model 做局部补全。
- **训练数据**：真实短曝光序列合成长曝光目标；真实车流、瀑布、舞蹈和光轨视频；加入遮挡与曝光变化。
- **LOSS / objective**：区域重建 + motion-streak prior + temporal warp + subject identity/edge loss + background smoothness。
- **时序策略**：以参考帧作为主体锚点，背景轨迹可累计；主体出入画面时切换 track state。
- **端侧落点**：不建议实时全画面；在线只保存 ring buffer 和运动场，录后生成。
- **风险**：背景运动和主体运动分离失败；生成轨迹不符合真实物理；大幅运动造成 ghosting。
- **MVP**：固定机位车流和单人挥手两个场景，分别测主体清晰度、拖影连续性和用户偏好。

### DD-05 高分辨率采集驱动的数字滑轨 / High-resolution capture for digital dolly
- **能力族 / 模式 / 边界**：virtual_camera / offline_device / generative
- **来源**：FluxSR | ReadPaper local Flux library | E3; Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3; Scalable Diffusion Models with Transformers | ReadPaper local Flux library | E3
- **研究问题**：手机数字运镜受裁切、视角变化和画外区域限制；单纯缩放没有真实视差。
- **技术方案**：以高分辨率采集、深度/语义层和相机轨迹估计生成有限视差；超出可见区域部分使用内容延展，并标记生成区域。
- **输入信号**：高分辨率视频 + depth/多摄 + IMU + semantic layers。
- **模型链路**：depth-aware image warping + hole filling + optional neural rendering/FLUX adapter。
- **训练数据**：多摄/多视角视频、室内外静态场景和缓慢运动视频；合成相机轨迹、孔洞和视差变化。
- **LOSS / objective**：多视角 photometric + depth consistency + perceptual + hole-boundary + trajectory smoothness。
- **时序策略**：相机轨迹全局平滑，场景层局部跟踪；每次大幅改变机位时以 keyframe 重新生成。
- **端侧落点**：实时只预览 crop/warp；录后做高质量 outpainting。
- **风险**：画外区域幻觉；平面假设导致几何撕裂；人物和细节容易身份漂移。
- **MVP**：室内产品和单人静态场景，限制轨迹为水平滑轨和轻微 push-in。

### DD-06 无感切镜与跨摄像头颜色连续 / Seamless lens switching with color continuity
- **能力族 / 模式 / 边界**：multi_camera / online_recording / faithful
- **来源**：Cinematic mode | Apple | E1; Gen 5 Color Science | Blackmagic Design | E1; Super Steady | Samsung | E1
- **研究问题**：手机多摄切换时曝光、AWB、噪声、锐度、视场和运动状态会突然变化。
- **技术方案**：提前 warm-up 辅摄状态，建立每颗镜头的 color/noise/sharpness transform，并共享 IMU、AF、AE 和 temporal feature state。
- **输入信号**：多摄 RAW/YUV + IMU + AE/AWB/AF state + lens metadata。
- **模型链路**：跨摄像头对齐 + online color transform + feature/state handoff；不依赖生成模型。
- **训练数据**：同步多摄视频，覆盖不同光照和焦段；采集镜头 response、噪声和畸变标定数据。
- **LOSS / objective**：跨摄颜色差异 + tone continuity + temporal flow + edge sharpness consistency + switch transient penalty。
- **时序策略**：切换前 N 帧并行估计，切换后共享参考帧；镜头状态机控制 reset。
- **端侧落点**：ISP/视频管线前端优先落地，适合 30/60fps 实时。
- **风险**：不同传感器动态范围差异无法完全补偿；切换时视差和 AF 状态仍可能突变。
- **MVP**：主摄/长焦两路，固定三档变焦切换；指标为 switch transient、肤色差和用户可见跳变率。

### DD-07 相机运动与主体运动解耦稳定 / Camera-motion and subject-motion disentangled stabilization
- **能力族 / 模式 / 边界**：motion_quality / online_recording / faithful
- **来源**：HyperSmooth stabilization | GoPro | E1; RockSteady stabilization | DJI | E1; FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3
- **研究问题**：全局 EIS 会把主体运动当成相机抖动，导致人体形变、背景冻结或运动意图消失。
- **技术方案**：联合 IMU、global camera pose、optical flow 和 semantic tracks，分离刚性相机运动与非刚性主体运动。
- **输入信号**：YUV/RGB + IMU + EIS gyro + subject masks + optical flow。
- **模型链路**：causal motion decomposition network + mesh/flow warper。
- **训练数据**：真实运动视频与 IMU、合成抖动轨迹、人体/车辆运动数据；加入 rolling shutter 和遮挡。
- **LOSS / objective**：camera reprojection + non-rigid flow smoothness + subject shape preservation + horizon/line stability + temporal consistency。
- **时序策略**：低频相机轨迹使用长窗口，主体轨迹使用短窗口；快速转身或遮挡时局部 reset。
- **端侧落点**：可放在 EIS 后端/编码前，先低分辨率估计高分辨率 warp。
- **风险**：场景多主体和透明物体难以分解；运动语义判断错误会造成不自然稳定。
- **MVP**：跑步、骑行、手持走路三场景，比较普通 EIS 与 intent-aware EIS 的主观自然度。

### DD-08 视频夜视与高光保护联合 / Video night enhancement with highlight protection
- **能力族 / 模式 / 边界**：night_hdr / online_recording / faithful
- **来源**：Video Boost | Google | E1; FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3; WF-VAE: Wavelet Flow VAE for Video Compression | ReadPaper local ENC_DEC library | E3
- **研究问题**：夜景视频同时面临暗部噪声、运动模糊、霓虹高光和曝光呼吸，单帧增强会放大闪烁。
- **技术方案**：联合多帧对齐、曝光状态、语义高光 mask 和时序降噪；暗部/高光使用不同的 restoration policy。
- **输入信号**：RAW/YUV 多帧 + AE metadata + motion + highlight mask + optional multi-exposure。
- **模型链路**：causal VRT-like transformer / recurrent restoration；高质量模式可用 latent diffusion teacher 蒸馏。
- **训练数据**：真实夜景视频、短曝光到长曝光配对、合成 sensor noise/ISO/色偏/高光裁切；保留真实 motion。
- **LOSS / objective**：Charbonnier + perceptual + temporal warp + chroma noise + highlight roll-off + exposure trajectory loss。
- **时序策略**：低频颜色与亮度状态记忆，高频细节使用短时参考；高光区禁止跨帧平均过度。
- **端侧落点**：预览 720p/1080p 轻量模式；录后旗舰模式用更长参考队列。
- **风险**：夜景生成纹理不真实；灯牌/车灯被错误抹除；高 ISO 真实细节不可恢复。
- **MVP**：城市夜景、室内移动、逆光人像三组，重点看 flicker、highlight clipping 和肤色。

### DD-09 视频人像分区恢复与身份锚定 / Region-aware portrait restoration with identity anchoring
- **能力族 / 模式 / 边界**：portrait_identity / online_recording / perceptual
- **来源**：TIGER: A Training Framework for Video Face Restoration | ReadPaper local PortraitSR library | E3; SVFR | ReadPaper local PortraitSR library | E3; AuthFace | ReadPaper local PortraitSR library | E3
- **研究问题**：统一人像美化会把脸、头发、眼睛、牙齿和衣服用同一策略处理，导致身份漂移和局部过度锐化。
- **技术方案**：使用 face parsing/landmarks/track ID 建立区域化处理；以 identity embedding 锚定五官结构，用 temporal ROI features 保持连续。
- **输入信号**：YUV/RGB + face/body parsing + landmarks + track ID + optional reference frame。
- **模型链路**：ROI transformer/recurrent restoration + identity branch + mask-conditioned decoder。
- **训练数据**：真实人像视频、VFH​​Q/CelebV-HQ/FFHQ 类静态数据、合成压缩/模糊/噪声/遮挡；加入不同年龄、肤色、妆容。
- **LOSS / objective**：区域重建 + ROI perceptual + ArcFace/identity cosine + temporal feature consistency + mask boundary + skin-color stability。
- **时序策略**：每个 track 维护 identity prototype；关键帧更新 prototype，普通帧只更新局部特征。
- **端侧落点**：脸部 ROI 低分辨率分析、高分辨率局部增强；多人时按重要性预算。
- **风险**：身份 loss 过强会压制真实表情；过度生成会改变年龄/五官；mask 错误会伤及头发和背景。
- **MVP**：单人近景、30fps、脸部五分区，先验证身份余弦、纹理稳定和用户偏好。

### DD-10 视频路人和电线时序移除 / Temporal passerby and wire removal
- **能力族 / 模式 / 边界**：scene_editing / offline_device / generative
- **来源**：Content-Aware Fill for video | Adobe | E1; Object removal | Blackmagic Design | E1; Magic Mask | Blackmagic Design | E1
- **研究问题**：视频移除不是单帧 inpainting：需要处理动态背景、遮挡关系、镜头运动和新出现区域。
- **技术方案**：对象 tracking -> 背景板/时空 memory -> motion-compensated fill -> boundary refinement；输出移除 mask 和可回退原片。
- **输入信号**：连续视频 + object mask + camera motion + depth/scene segmentation。
- **模型链路**：video inpainting transformer；高质量模式可使用扩散/DiT 的局部条件编辑。
- **训练数据**：DAVIS/YouTube-VOS 类视频 mask、真实路人/电线采集、合成对象插入和镜头运动；对背景动态单独采样。
- **LOSS / objective**：known-region reconstruction + hole perceptual + temporal warp + boundary gradient + object-removal consistency。
- **时序策略**：用稳定背景 memory 作为参考，背景变化时更新；长时间遮挡需要生成式重建并降低置信度。
- **端侧落点**：适合录后端侧；实时只做检测、预览 mask 和短时移除。
- **风险**：背景板不真实、重复纹理、人物边界残留；生成区域可能改变事实。
- **MVP**：固定机位路人移除和电线移除，约束对象不超过 2 个，输出可回退的编辑工程。

### DD-11 语义分区 LUT 与动态胶片质感 / Semantic local LUT and dynamic film look
- **能力族 / 模式 / 边界**：color_science / online_recording / perceptual
- **来源**：Real Time LUT | Panasonic | E1; Gen 5 Color Science | Blackmagic Design | E1; S-Cinetone | Sony | E1
- **研究问题**：全局 LUT 会同时改变肤色、天空、霓虹和阴影；颗粒和晕光逐帧生成会闪烁。
- **技术方案**：按语义区域使用局部 color transform；颗粒、halation、tone curve 与亮度、ISO、运动状态绑定并用状态滤波稳定。
- **输入信号**：YUV/Log + scene segmentation + exposure/ISO metadata + motion state。
- **模型链路**：轻量 semantic segmentation + 3D LUT/MLP color transform + procedural grain/halation renderer。
- **训练数据**：多相机、多光照、参考电影片段；采集颜色 chart、肤色和不同 ISO 的颗粒统计。
- **LOSS / objective**：色彩重建 + skin-tone deviation + look perceptual + temporal color stability + grain spectrum matching。
- **时序策略**：LUT 参数低通，区域 mask 采用 tracking；镜头切换时使用颜色状态 handoff。
- **端侧落点**：适合实时录像，核心工作放在 ISP/GPU；高质量纹理可录后叠加。
- **风险**：语义分割错会导致局部颜色断层；风格与真实颜色边界模糊；不同屏幕显示不一致。
- **MVP**：肤色/天空/高亮三类区域 + 两种 film look，比较全局 LUT 与语义 LUT 的用户偏好。

### DD-12 说话人驱动构图、跟焦和变焦 / Speaker-driven framing, focus, and zoom
- **能力族 / 模式 / 边界**：audio_visual / online_recording / faithful
- **来源**：Blackmagic Camera app | Blackmagic Design | E1; Real-time tracking and subject recognition | Sony | E1; Me Mode | Insta360 | E2
- **研究问题**：采访/直播中相机不知道谁在说话，单纯人脸 tracking 会在多人之间错误切换。
- **技术方案**：音频 DOA/ASR/说话人 diarization 与 face track 对齐，再用 shot policy 控制景别、焦点和数字 crop。
- **输入信号**：多麦克风音频 + face tracks + body pose + camera metadata。
- **模型链路**：低延迟 audio-visual association + policy/state machine；避免直接使用大模型在线决策。
- **训练数据**：多说话人采访、播客、会议和嘈杂环境；标注说话人-脸对应、镜头选择和用户偏好。
- **LOSS / objective**：speaker-face matching + focus/framing classification + trajectory smoothness + shot-switch penalty。
- **时序策略**：说话人状态需有 hysteresis；至少持续若干帧才切换镜头，停顿时保留上一状态。
- **端侧落点**：DSP 运行声源特征，NPU 运行脸部 track，策略在 CPU/轻量 runtime；可 30fps 在线。
- **风险**：多人抢话、遮挡和混响会造成错配；自动运镜可能让用户失去控制。
- **MVP**：双人采访，只有 wide/medium 两种景别和一个焦点策略，加入手动锁定优先级。

### DD-13 有限视角扩展与视频画外补全 / Constrained novel-view extension and video outpainting
- **能力族 / 模式 / 边界**：generative_video / offline_device / generative
- **来源**：Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3; FluxSR | ReadPaper local Flux library | E3; Scalable Diffusion Models with Transformers | ReadPaper local Flux library | E3; MAGVIT: Masked Generative Video Transformer | ReadPaper local ENC_DEC library | E3
- **研究问题**：横竖屏裁切、数字运镜和镜头延展需要画外内容，但逐帧生成会出现结构和纹理漂移。
- **技术方案**：使用 depth/scene layout/trajectory 约束时空 outpainting；以关键帧生成画外结构，再用视频 latent/feature propagation 传播。
- **输入信号**：视频 + camera trajectory + depth/segmentation + text/reference optional。
- **模型链路**：video VAE/DiT latent editor + spatial adapter + temporal attention；端侧只考虑短片段录后。
- **训练数据**：多视角/宽幅视频裁切任务、合成画外区域、动态对象和遮挡；使用区域 mask 作为 supervision。
- **LOSS / objective**：known-region identity + generated-region perceptual + temporal consistency + layout/depth consistency + boundary blend。
- **时序策略**：只对新增区域生成；原视频区域尽量 copy/warp，关键帧负责结构锚定。
- **端侧落点**：优先云端或旗舰录后；手机端可限制输出边界和长度。
- **风险**：画外事实不可验证；人物、文字、建筑结构容易幻觉；用户可能误以为是原始录像。
- **MVP**：横转竖/竖转横 + 10% 边界延展，仅静态背景和短片段，保留生成 mask。

### DD-14 录制代理与录后高质量重算 / Proxy capture with post-capture quality rerender
- **能力族 / 模式 / 边界**：capture_assistance / offline_device / faithful
- **来源**：Video Boost | Google | E1; FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3; WF-VAE: Wavelet Flow VAE for Video Compression | ReadPaper local ENC_DEC library | E3
- **研究问题**：高质量算法无法在所有手机、温度和录像时长下实时运行，但只保存压缩视频又失去后处理所需信息。
- **技术方案**：录像时保存轻量 proxy、关键帧、深度/mask/IMU/曝光状态和压缩 latent；停止录像后按设备预算重算。
- **输入信号**：原始/高质量 proxy + metadata + motion/depth/mask + optional encoded latent。
- **模型链路**：在线轻量模型 + 录后 VRT/flow/diffusion/FLUX adapter；可按温度动态选择。
- **训练数据**：从同一段真实视频产生不同 proxy 和高质量目标；覆盖中断、掉帧、温度降级和存储受限。
- **LOSS / objective**：proxy-to-GT restoration + metadata consistency + temporal quality + rate/storage regularization。
- **时序策略**：完整时序状态保存在片段级 manifest；录后允许双向模型，在线只需因果状态。
- **端侧落点**：最适合把前沿模型带入手机，但需要存储、后台任务和用户等待交互。
- **风险**：存储成本、后台耗电、任务中断和用户对最终结果等待时间的接受度。
- **MVP**：1080p/10秒片段，保存低码率 proxy + motion/mask metadata，比较录后重算与实时输出。

### DD-15 镜头污渍、雨滴与玻璃反射抑制 / Lens contamination and reflection suppression
- **能力族 / 模式 / 边界**：computational_optics / online_recording / faithful
- **来源**：Magic Mask | Blackmagic Design | E1; Roto Brush and object selection | Adobe | E1; Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3
- **研究问题**：镜头雨滴、污渍和玻璃反射会在视频中产生固定/移动遮挡，单帧修复容易产生背景复制和闪烁。
- **技术方案**：识别 contamination type，利用相机运动、背景记忆和 reflection/transmission separation 做保守抑制；低置信度区域保持原片。
- **输入信号**：连续帧 + lens contamination mask + camera motion + depth/scene segmentation。
- **模型链路**：污染检测 + background memory + video inpainting/reflectance separation。
- **训练数据**：真实雨滴/玻璃拍摄、可控喷雾和污渍数据、合成反射/透射层；保留透明和半透明边界。
- **LOSS / objective**：mask-aware reconstruction + temporal warp + transparency consistency + background edge loss。
- **时序策略**：固定污渍用长期背景参考，移动雨滴用短期 track；镜头移动时更新 reference。
- **端侧落点**：检测可实时，强修复适合录后；保留“原片/抑制版”双输出。
- **风险**：真实高光被误判为污渍；透明物体的真实性难以恢复；背景运动时生成失败。
- **MVP**：固定镜头污渍和车窗反射两个场景，输出置信度和回退开关。

### DD-16 多人独立打光与共享环境光 / Independent multi-person relighting with shared environment light
- **能力族 / 模式 / 边界**：relighting / offline_device / generative
- **来源**：Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3; AuthFace | ReadPaper local PortraitSR library | E3; Video background removal | CapCut | E2
- **研究问题**：多人画面中每个人的肤色、朝向和遮挡不同，统一打光会产生不自然的阴影与颜色。
- **技术方案**：按 track ID 估计每人局部 light code，同时共享一个环境光低频场；遮挡关系决定前后景合成顺序。
- **输入信号**：multi-person tracks + parsing masks + pose/normal proxy + scene segmentation。
- **模型链路**：multi-ROI relighting network + shared environment latent + compositing module。
- **训练数据**：多人 HDR 人像、真实补光视频、3D human relighting 数据；合成不同人数和遮挡关系。
- **LOSS / objective**：person ROI reconstruction + identity + inter-person color consistency + occlusion boundary + temporal track consistency。
- **时序策略**：每个 track 独立维护 light state，环境光使用全局低频状态；新人出现时 warm-up。
- **端侧落点**：多人数量和 ROI 面积决定预算；实时预览只做两人以内，录后支持更多人。
- **风险**：身份/肤色不一致、人物边界互相污染、生成阴影不符合场景。
- **MVP**：双人正面站立，单一环境光、左右主光两档，先测色彩一致和边界。

### DD-17 语义分层虚拟移轴 / Semantic layered virtual tilt-shift
- **能力族 / 模式 / 边界**：depth_focus / offline_device / perceptual
- **来源**：Cinematic Blur | Google | E1; FluxSR | ReadPaper local Flux library | E3
- **研究问题**：移轴效果需要倾斜焦平面，普通手机没有足够光学自由度，视频中还需处理相机运动和多层深度。
- **技术方案**：从深度/语义层估计虚拟焦平面，按距离对不同层做 blur、色彩和饱和度处理，保留主体层锐度。
- **输入信号**：video + depth/scene parsing + motion field。
- **模型链路**：depth-layer renderer + temporal refinement；生成式模型只补复杂边界。
- **训练数据**：城市/建筑/风景视频、真实 tilt-shift 镜头参考、深度标注和合成焦平面。
- **LOSS / objective**：depth-layer consistency + edge/alpha + perceptual style + temporal stability。
- **时序策略**：焦平面参数由用户控制，低频稳定；深度层局部更新。
- **端侧落点**：实时预览可采用 2-3 层近似；录后增加细分层。
- **风险**：深度错误导致局部错焦；创意效果可能显得廉价；动态物体边界复杂。
- **MVP**：建筑/静态街景，固定焦平面方向和两种强度。

### DD-18 事件触发慢动作与局部插帧 / Event-triggered slow motion with local frame interpolation
- **能力族 / 模式 / 边界**：temporal_exposure / online_recording / faithful
- **来源**：Subject tracking | DJI | E1; FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3
- **研究问题**：全程高帧率耗电且存储大，但真正有价值的动作只占很短片段。
- **技术方案**：用音频、运动和语义事件触发 ring buffer，录制前后保留短片段；仅对主体 ROI 或事件窗口插帧。
- **输入信号**：低帧率视频 + ring buffer + IMU + audio + subject tracks。
- **模型链路**：轻量 event detector + local frame interpolation/flow model。
- **训练数据**：体育、儿童、宠物、舞台动作；标注事件边界和用户认为值得慢放的片段。
- **LOSS / objective**：interpolation reconstruction + flow consistency + occlusion handling + event boundary smoothness。
- **时序策略**：事件触发必须有 hysteresis 和 pre-roll/post-roll，避免重复触发。
- **端侧落点**：检测放 DSP/NPU，插帧在录后或片段停止后做。
- **风险**：错过事件或错误触发；快速遮挡时插帧伪影；用户不理解为什么保存了额外片段。
- **MVP**：声音/动作触发两个事件类别，固定 3 秒 ring buffer 和 2x 插帧。

### DD-19 说话人语义自动拉焦 / Speaker-aware semantic focus pull
- **能力族 / 模式 / 边界**：virtual_camera / online_recording / faithful
- **来源**：Cinematic mode | Apple | E1; Real-time tracking and subject recognition | Sony | E1
- **研究问题**：自动拉焦通常只根据最近/最大的人脸，无法理解对话中的说话人和视线。
- **技术方案**：将声源、人脸 track、视线、人物重要性组合成 focus policy，并使用 hysteresis 控制切换。
- **输入信号**：audio DOA + face/pose/eye gaze + depth + AF state。
- **模型链路**：audio-visual association + low-latency policy network + focus trajectory smoother。
- **训练数据**：双人/多人对话，标注焦点选择、切换时机和用户偏好；加入遮挡、转头和抢话。
- **LOSS / objective**：speaker association + focus target classification + transition smoothness + wrong-switch penalty。
- **时序策略**：最短 dwell time、切换冷却和关键帧 confidence；失去声源时回到视觉目标。
- **端侧落点**：声源特征由 DSP，脸部/深度由 NPU；适合在线预览和录像。
- **风险**：混响或多人抢话造成错误焦点；过于智能的切换会打扰摄影师控制。
- **MVP**：双人采访，支持自动/半自动两种模式和手动锁定。

### DD-20 双摄联合去模糊与细节补偿 / Dual-camera deblurring and detail compensation
- **能力族 / 模式 / 边界**：multi_camera / offline_device / faithful
- **来源**：FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3; Super Steady | Samsung | E1
- **研究问题**：主摄在低照度有噪声和运动模糊，长焦有细节但更不稳定，单路去模糊容易 hallucinate。
- **技术方案**：将两路摄像头按时空和视场对齐，利用长焦细节作为受控 reference，主摄作为稳定/曝光底图。
- **输入信号**：同步多摄 RAW/YUV + calibration + IMU + flow + exposure metadata。
- **模型链路**：cross-view alignment + confidence-aware feature fusion + restoration decoder。
- **训练数据**：同步双摄运动视频、真实模糊/噪声、不同焦段标定；训练时随机失配和曝光差。
- **LOSS / objective**：cross-view photometric + reconstruction + confidence calibration + temporal consistency + edge detail。
- **时序策略**：参考摄像头选择随运动/亮度变化，切换时共享 feature state。
- **端侧落点**：适合 1080p 在线或 4K 录后；高分辨率融合应限制 ROI。
- **风险**：视差/同步误差、不同 lens response 和遮挡导致 ghosting。
- **MVP**：主摄+长焦固定焦段，静态/缓慢运动夜景，比较单摄和双摄细节与伪影。

### DD-21 滚动快门与电子防抖联合校正 / Joint rolling-shutter and EIS correction
- **能力族 / 模式 / 边界**：motion_quality / online_recording / faithful
- **来源**：FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3; Horizon Lock | GoPro | E1
- **研究问题**：快速摇摄时逐行曝光造成倾斜/弯曲，EIS 再裁切会放大几何不一致。
- **技术方案**：显式使用 row-time model、IMU 和 flow，把滚动快门校正放进稳定优化，而不是后置单独处理。
- **输入信号**：RAW/YUV + row exposure timing + IMU + lens calibration + flow。
- **模型链路**：row-wise warp + camera pose estimator + causal stabilization controller。
- **训练数据**：真实高速旋转视频、IMU 对齐数据、合成 row-time distortion；加入不同读出速度。
- **LOSS / objective**：geometric reprojection + line straightness + horizon stability + temporal warp + crop penalty。
- **时序策略**：姿态使用高频 IMU，纹理 flow 使用短窗口；异常 IMU 时降级到普通 EIS。
- **端侧落点**：更适合 ISP/DSP 前置校正，几何模型比生成模型更适合端侧。
- **风险**：光流和 IMU 不一致时会变形；大滚快门畸变可能无法从单帧恢复。
- **MVP**：快速水平摇摄和骑行两类，测直线弯曲、裁切和稳定自然度。

### DD-22 逆光人像局部 HDR 与身份保持 / Backlit portrait local HDR with identity preservation
- **能力族 / 模式 / 边界**：night_hdr / online_recording / perceptual
- **来源**：AuthFace | ReadPaper local PortraitSR library | E3; TIGER: A Training Framework for Video Face Restoration | ReadPaper local PortraitSR library | E3; Video Boost | Google | E1
- **研究问题**：全局 HDR 会让逆光人脸灰、背景过曝或视频帧间呼吸；人脸增强又可能改变身份。
- **技术方案**：以人脸/人体 ROI 独立做 tone mapping 和 detail restoration，使用身份 embedding 与肤色稳定约束，背景保留真实高光滚降。
- **输入信号**：multi-frame YUV/RAW + face/body mask + exposure metadata + motion。
- **模型链路**：local tone mapping + portrait restoration branch + temporal fusion。
- **训练数据**：逆光人像视频、多曝光配对、不同肤色和光源；合成高光裁切、噪声和压缩。
- **LOSS / objective**：ROI reconstruction + identity + skin-tone + temporal color + highlight roll-off + boundary consistency。
- **时序策略**：肤色/低频亮度使用 track state；表情细节使用短期参考。
- **端侧落点**：适合在线 1080p，4K 只处理 face ROI；高质量模式录后重算。
- **风险**：肤色过度美化、背景与人物光照不匹配、逆光高光不可恢复。
- **MVP**：窗边和日落两场景，单人半身，测肤色偏差、identity cosine、flicker。

### DD-23 眼镜反光和眼神光联合处理 / Eyeglass glare suppression and catchlight control
- **能力族 / 模式 / 边界**：portrait_identity / offline_device / perceptual
- **来源**：AuthFace | ReadPaper local PortraitSR library | E3; SVFR | ReadPaper local PortraitSR library | E3
- **研究问题**：眼镜反光遮挡瞳孔时，直接修复容易生成错误眼睛；眼神光逐帧变化也会产生不自然跳闪。
- **技术方案**：检测镜片/眼睛层，先抑制反光再以身份和前后帧补偿瞳孔结构；眼神光使用显式可控参数。
- **输入信号**：face landmarks + eye/eyeglass mask + consecutive frames + optional reference frame。
- **模型链路**：eye ROI restoration + reflection separation + identity-conditioned decoder。
- **训练数据**：戴眼镜人像视频、可控反光拍摄、不同镜片和姿态；人工标注眼睛/镜片/高光。
- **LOSS / objective**：eye reconstruction + identity + reflection sparsity + temporal consistency + iris boundary。
- **时序策略**：眼睛 track 单独维护 reference；眨眼期间冻结或降低生成强度。
- **端侧落点**：只在眼睛 ROI 录后处理，避免全脸模型成本。
- **风险**：幻觉眼睛、瞳孔方向错误、反光真实语义被删除。
- **MVP**：固定眼镜类型、正面人像，支持开关和强度滑杆。

### DD-24 天空替换与地面光照联动 / Temporal sky replacement with ground-light coupling
- **能力族 / 模式 / 边界**：scene_editing / offline_device / generative
- **来源**：Video background removal | CapCut | E2; Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3
- **研究问题**：单独替换天空会使地面、人物边缘和环境色温不匹配，视频中天空还会抖动或穿帮。
- **技术方案**：天空 segmentation + camera motion + replacement sky trajectory + ground illumination adjustment；保持原始主体区域可回退。
- **输入信号**：video + sky mask + scene depth/segmentation + IMU + optional text/reference sky。
- **模型链路**：sky tracker + compositing + low-frequency relighting; generative model only for sky synthesis/outpainting。
- **训练数据**：多天气天空视频、真实地面光照和人物边界；合成天光方向、雾和动态云。
- **LOSS / objective**：sky reconstruction + boundary alpha + color/illumination consistency + temporal motion + semantic preservation。
- **时序策略**：天空作为全局层稳定，地面光照低频调整；云运动由用户速度或原始相机运动驱动。
- **端侧落点**：实时预览只做替换，地面联动录后完成。
- **风险**：发丝/树枝穿帮、地面颜色不自然、生成天空改变事件真实性。
- **MVP**：静态城市/旅行，预置 3 种天空，输出 sky mask 和可回退工程。

### DD-25 跨镜头肤色与胶片质感连续 / Cross-lens skin tone and film-look continuity
- **能力族 / 模式 / 边界**：color_science / online_recording / perceptual
- **来源**：Gen 5 Color Science | Blackmagic Design | E1; Real Time LUT | Panasonic | E1; S-Cinetone | Sony | E1
- **研究问题**：多摄切镜不仅有曝光差，肤色和颗粒风格也会跳变。
- **技术方案**：维护全局 look state，以脸部/肤色和灰阶区域作为 anchor，分别校正不同摄像头的 color response。
- **输入信号**：multi-camera YUV/Log + face/skin mask + exposure/ISO + lens metadata。
- **模型链路**：camera-specific color transform + stateful look controller + semantic LUT。
- **训练数据**：多摄同步拍摄 color chart、人像和不同光线；跨镜头 reference look 标定。
- **LOSS / objective**：skin-tone deviation + cross-lens color + temporal look smoothness + grain spectrum。
- **时序策略**：切换前进行 look state warm-up，切换时连续插值，不重置颗粒相位。
- **端侧落点**：适合 ISP/GPU 实时；颗粒和 halation 可采用低成本 procedural 版本。
- **风险**：过度肤色校正、不同肤色公平性、Log/Rec709 状态混用。
- **MVP**：主摄/超广/长焦三镜头，单人移动，比较普通切镜与 look continuity。

### DD-26 音频触发精彩瞬间与局部慢放 / Audio-triggered highlight capture and local slow motion
- **能力族 / 模式 / 边界**：audio_visual / online_recording / faithful
- **来源**：ActiveTrack subject tracking | DJI | E2; Blackmagic Camera app | Blackmagic Design | E1
- **研究问题**：用户常常错过进球、掌声、笑声或儿童动作的关键前后瞬间。
- **技术方案**：音频事件检测与视觉运动强度联合触发 ring buffer，保存事件窗口并给出局部慢放候选。
- **输入信号**：microphone array + video proxy + IMU + motion/subject detector。
- **模型链路**：tiny audio event classifier + vision motion scorer + rule/policy layer。
- **训练数据**：真实生活和运动声音、不同噪声场景、事件边界标注；用用户选择作为 ranking supervision。
- **LOSS / objective**：event classification + temporal boundary + highlight ranking + false-trigger penalty。
- **时序策略**：pre-roll/post-roll、触发冷却和事件合并；避免连续掌声生成多个片段。
- **端侧落点**：DSP + low-res NPU，适合持续运行；后续局部插帧可异步。
- **风险**：噪声误触发、私密音频处理、存储和用户隐私。
- **MVP**：掌声、笑声、撞击声三类事件，保存前后 2 秒。

### DD-27 视频扩散的局部事实保护编辑 / Localized video diffusion editing with fact-region protection
- **能力族 / 模式 / 边界**：generative_video / cloud_render / generative
- **来源**：Scalable Diffusion Models with Transformers | ReadPaper local Flux library | E3; MAGVIT: Masked Generative Video Transformer | ReadPaper local ENC_DEC library | E3; Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3
- **研究问题**：全视频扩散编辑会重绘原始区域，导致人物、文字和动作改变。
- **技术方案**：构建 protected region / editable region mask，原视频区域采用 latent inpainting constraints，只有指定区域允许生成。
- **输入信号**：video + edit mask + text/reference condition + optical flow/depth。
- **模型链路**：video latent diffusion/DiT + mask adapter + temporal attention；手机只负责上传/预览和 mask。
- **训练数据**：视频局部编辑数据、mask/文本/参考图三元组、区域冻结训练；加入文字、人脸和动作保护。
- **LOSS / objective**：protected-region reconstruction + editable-region diffusion objective + temporal consistency + identity/text preservation。
- **时序策略**：关键帧生成后通过 feature propagation 扩散，保护区尽量 copy/warp。
- **端侧落点**：云端或高端录后；必须输出生成 mask、原始视频 hash 和编辑参数。
- **风险**：生成区域边界、文字和人脸身份；云端隐私与版权问题。
- **MVP**：只做天空/背景色/雨雪等低风险区域，禁改脸和文字。

### DD-28 温度感知的算法质量伸缩 / Thermal-aware quality scaling for video algorithms
- **能力族 / 模式 / 边界**：capture_assistance / online_recording / faithful
- **来源**：FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3; WF-VAE: Wavelet Flow VAE for Video Compression | ReadPaper local ENC_DEC library | E3; Video Boost | Google | E1
- **研究问题**：手机录像的模型质量不能只按峰值算力设计，温度、电量、后台负载会导致中途掉帧和突然降质。
- **技术方案**：建立 quality ladder：模型宽度、参考帧数、ROI 范围、分辨率和后处理队列随热状态连续降级。
- **输入信号**：temperature/battery/SoC load + video mode + scene complexity + model latency telemetry。
- **模型链路**：多级模型或 early-exit/adapter；调度器在 CPU 上运行，模型在 NPU/GPU。
- **训练数据**：不同设备、温度、负载和片段长度的 profiling 数据；建立质量-延迟-功耗曲线。
- **LOSS / objective**：任务质量 + temporal stability + latency/power regularizer；训练权重不代替真实设备 profiling。
- **时序策略**：降级/升级使用 hysteresis，不能每帧切换；关键帧保持相同质量等级。
- **端侧落点**：直接面向端侧部署，必须联动编码器、内存和后台任务。
- **风险**：用户感知到中途画质跳变；不同 SoC 的 profile 不可直接迁移。
- **MVP**：两档温控和三档模型，录制 10 分钟观察 FPS、温度和质量变化。

### DD-29 动态污渍/雨滴检测与可逆抑制 / Dynamic contamination detection with reversible suppression
- **能力族 / 模式 / 边界**：computational_optics / online_recording / faithful
- **来源**：Magic Mask | Blackmagic Design | E1; FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation | ReadPaper local ENC_DEC library | E3
- **研究问题**：手机录像中雨滴或手指遮挡会在几秒内改变，静态 lens mask 不够。
- **技术方案**：检测透明/半透明污染并输出 mask/confidence；低置信度只做提示，避免强生成抹掉真实内容。
- **输入信号**：连续帧 + local contrast/flow + lens metadata + scene motion。
- **模型链路**：轻量 contamination detector + mask tracker + conservative temporal filter。
- **训练数据**：真实雨滴、指纹、灰尘、贴膜和逆光高光；hard negative 包含水面反光和灯光。
- **LOSS / objective**：mask BCE/Dice + temporal mask consistency + false-positive penalty + transparency regression。
- **时序策略**：污染 mask 有长寿命状态，真实场景高光短寿命；使用双时间常数。
- **端侧落点**：可实时运行，强修复单独触发。
- **风险**：误判真实高光或前景；检测器误报影响用户信任。
- **MVP**：只做提示和局部降低锐化，不直接生成清除。

### DD-30 舞台追光与人物 track 联动 / Stage spotlight following with subject tracks
- **能力族 / 模式 / 边界**：relighting / offline_device / generative
- **来源**：Subject tracking | DJI | E1; Acquire and then Adapt / FluxIR | ReadPaper local Flux library | E3
- **研究问题**：舞台录像中人物和灯光快速运动，手工加追光成本高，逐帧生成又容易跟丢。
- **技术方案**：用 person track、舞台区域和音乐节拍控制虚拟 spotlight；追光只影响可选光照层，不修改人物身份。
- **输入信号**：person tracks + stage segmentation + audio beat + background brightness map。
- **模型链路**：tracking + parametric spotlight renderer + optional relighting adapter。
- **训练数据**：舞台/演唱会视频、光源轨迹和人群遮挡；合成不同 spotlight 半径和颜色。
- **LOSS / objective**：track consistency + light falloff + boundary/occlusion + temporal intensity + perceptual style。
- **时序策略**：追光位置由 track 预测，强度/颜色低通；人物出场/退场使用 fade in/out。
- **端侧落点**：预览可做简单光斑，录后做人物受光和阴影。
- **风险**：舞台真实灯光与虚拟灯叠加不协调；多人场景光斑竞争。
- **MVP**：单人舞台、一个追光、三种颜色和强度，测跟随丢失率。

## 7. 10 个组合创新概念

组合创新不是现有产品清单，而是将已经存在的产品/论文能力重新组织为手机录像预研方向。

### PC-01 夜景电影人像录像 / Night Cinematic Portrait Video
- **组成**：DD-02, DD-03, DD-08, DD-09
- **用户故事**：用户在夜景城市或演唱会拍人像时，一次录像同时获得稳定肤色、可调主光、可调景深和高光保护。
- **交互**：拍摄前选择自然/电影两档；录后可调整主光方向、光圈和人像恢复强度。
- **系统链路**：RAW/YUV + AE/IMU -> 人像/深度/高光分析 -> 夜景恢复 -> 人像身份锚定 -> relight/defocus -> 色彩管理 -> 编码。
- **MVP**：单人半身、1080p30，在线夜景恢复和粗景深，录后完成打光和边界细化。
- **数据**：真实夜景人像、多曝光、双摄深度、不同肤色与运动；使用可控 HDR 灯光合成补足标签。
- **指标**：identity cosine、肤色偏差、flicker、高光裁切率、发丝边界和用户偏好。
- **风险**：人脸身份或肤色改变、景深边界、夜景纹理幻觉。
- **真实性边界**：perceptual/generative，必须保留原片和编辑 mask。

### PC-02 语义光轨运动录像 / Semantic Light-Trail Action Video
- **组成**：DD-01, DD-04, DD-07, DD-18
- **用户故事**：用户拍跑步、骑行、舞蹈或车流时，主体保持清晰，背景/灯光形成可控拖影，并自动抓取精彩慢动作。
- **交互**：选择主体、拖影长度和节奏；系统自动保存事件前后片段。
- **系统链路**：视频/IMU/音频 -> 主体与运动分解 -> 稳定 -> 时间积分/光轨 -> 局部插帧 -> 编码。
- **MVP**：固定机位车流和单人跑步，支持两档拖影及 2x 局部慢放。
- **数据**：短曝光序列、真实运动视频、IMU、音频事件、运动 mask。
- **指标**：主体清晰度、轨迹连续性、ghosting、慢动作伪影、触发准确率。
- **风险**：运动分解失败，生成轨迹不物理，事件误触发。
- **真实性边界**：主体恢复偏 faithful，轨迹效果属于 generative。

### PC-03 智能采访摄影师 / AI Interview Camera Operator
- **组成**：DD-12, DD-19, DD-21, DD-25
- **用户故事**：手机在双人/多人采访中自动识别说话人，平滑构图和拉焦，同时保持稳定和跨镜头肤色一致。
- **交互**：用户选择保守/积极运镜，随时点选人物锁定或关闭自动切换。
- **系统链路**：多麦克风 + face tracks + depth/IMU -> 说话人关联 -> focus/framing policy -> 稳定/切镜 -> look continuity。
- **MVP**：双人采访、wide/medium 两种景别、自动拉焦和手动锁定。
- **数据**：多人对话、声源位置、face track、焦点和专业剪辑决策标注。
- **指标**：speaker-face matching、错误切换、焦点命中、画面跳变和用户控制满意度。
- **风险**：混响/抢话、自动策略打扰创作者、隐私。
- **真实性边界**：faithful，不修改内容事实。

### PC-04 空间电影运镜 / Spatial Cinematic Reframing
- **组成**：DD-05, DD-13, DD-17, DD-27
- **用户故事**：用户用普通手持视频录完后，生成小幅滑轨、推拉、横竖屏重构和景深变化。
- **交互**：选择预设轨迹，界面显示原始区域与生成画外区域。
- **系统链路**：高分辨率视频/深度/IMU -> scene layers -> 轨迹规划 -> warping -> constrained outpainting -> 景深/色彩。
- **MVP**：静态背景、单人、10% 画外延展和水平滑轨。
- **数据**：多视角视频、宽幅裁切、深度、相机轨迹和动态遮挡。
- **指标**：几何一致性、生成区域 temporal error、身份保持、用户可信度。
- **风险**：画外幻觉、几何撕裂、文字与人物身份变化。
- **真实性边界**：generative，必须输出生成区域和原片。

### PC-05 演唱会录像增强套件 / Concert Video Enhancement Suite
- **组成**：DD-01, DD-08, DD-16, DD-30
- **用户故事**：演唱会录像保持舞台高光和暗部细节，并可录后增加跟随歌手的虚拟追光和受控星芒。
- **交互**：实时显示高光保护，录后调追光目标、颜色、星芒和强度。
- **系统链路**：夜景/HDR restoration -> performer tracking -> spotlight relighting -> starburst/flare -> audio-synced look。
- **MVP**：单个歌手、一个虚拟追光、两档星芒和高光保护。
- **数据**：演唱会/舞台、LED 屏、强高光、远距离人物、观众遮挡和音乐节拍。
- **指标**：高光 clipping、人物 track、光效 flicker、色彩稳定和主观电影感。
- **风险**：真实舞台灯和虚拟灯冲突、远距离人脸误恢复、光效遮挡表演。
- **真实性边界**：夜景增强 faithful，虚拟追光和星芒 perceptual/generative。

### PC-06 旅行净景与天气编辑 / Clean Travel Scene and Weather Editing
- **组成**：DD-10, DD-15, DD-24, DD-13
- **用户故事**：旅行录像可清除短时路人、电线、镜头污渍，替换天空并适配横竖屏。
- **交互**：系统自动给出问题 mask，用户逐项勾选清理；所有编辑可回退。
- **系统链路**：质量检测 -> mask/track -> 背景 memory -> temporal inpainting -> sky/light coupling -> outpainting。
- **MVP**：固定机位景点，移除 1-2 个路人，预置天空，10% 边界延展。
- **数据**：旅行景点、动态人群、天空/天气、雨滴和背景板。
- **指标**：边界、temporal warping、背景重复、用户接受度和事实标注清晰度。
- **风险**：生成改变真实场景、背景幻觉、透明/树枝边界。
- **真实性边界**：generative，逐项保存 mask 和编辑参数。

### PC-07 连续变焦电影色彩 / Continuous-Zoom Cinematic Color
- **组成**：DD-06, DD-11, DD-20, DD-25
- **用户故事**：用户在广角到长焦连续录像时，不再看到曝光、色彩、噪声和肤色跳变，并获得统一电影风格。
- **交互**：用户选择 look；系统自动切镜与细节融合，可关闭长焦增强。
- **系统链路**：multi-camera warm-up -> alignment/fusion -> color/noise transform -> semantic LUT -> encoder。
- **MVP**：主摄+长焦、日景/室内、人像和建筑，三档变焦切换。
- **数据**：同步多摄、color chart、人像、不同焦段/曝光/运动和 lens metadata。
- **指标**：switch transient、肤色 delta、锐度跳变、ghosting、稳定和温度。
- **风险**：视差、同步、不同动态范围和高成本。
- **真实性边界**：faithful/perceptual，不生成新内容。

### PC-08 身份可信的人像直播增强 / Identity-Safe Live Portrait Enhancement
- **组成**：DD-09, DD-22, DD-23, DD-28
- **用户故事**：直播或长时间自拍视频中，改善逆光、眼镜反光、皮肤和头发细节，但不改变身份，并随温度自动降级。
- **交互**：区域化强度控制和身份保护开关；温控降级时只降低细节、不改变肤色。
- **系统链路**：face track/parsing -> local HDR -> region restoration -> identity check -> thermal scheduler -> encoder。
- **MVP**：单人 1080p30，脸/头发/眼镜三分区，两档温控。
- **数据**：多肤色、多年龄、眼镜、逆光、长时间直播和设备 profiling。
- **指标**：identity cosine、肤色、区域 flicker、FPS/温度、用户对自然度评价。
- **风险**：外貌改变、群体偏差、温控导致画质跳变。
- **真实性边界**：perceptual，禁止生成性脸型/年龄改变。

### PC-09 低功耗专业录像代理 / Low-Power Professional Video Proxy
- **组成**：DD-14, DD-28, DD-07, DD-11
- **用户故事**：长时间录像时实时输出稳定可看的代理视频，同时保存少量中间信息，停止后再生成高质量母版。
- **交互**：显示实时版和高质量重算进度；用户可选择立即导出代理或等待母版。
- **系统链路**：online lightweight stabilization/look -> proxy encoder + metadata store -> offline restoration/look rerender。
- **MVP**：1080p 10分钟，实时轻量稳定/LUT，录后 30 秒片段高质量重算。
- **数据**：不同热状态、存储和负载下的 profiling；同一场景 proxy/HQ 配对。
- **指标**：实时 FPS、温度、存储、重算时长、母版质量和中断恢复。
- **风险**：存储/后台耗电、用户等待、重算失败。
- **真实性边界**：faithful/perceptual，保留原始代理和参数。

### PC-10 可信生成式手机录像编辑 / Trustworthy Generative Mobile Video Editing
- **组成**：DD-13, DD-24, DD-27, DD-14
- **用户故事**：用户可做天空、天气、画外延展和局部背景编辑，同时系统明确展示哪些区域是生成的。
- **交互**：编辑区域默认受限；脸、文字和主体默认保护；导出可携带生成区域 metadata。
- **系统链路**：protected/editable masks -> keyframe generation -> temporal propagation -> consistency audit -> export original/mask/edit。
- **MVP**：天空和背景边界两类编辑，片段不超过 5 秒，禁止修改脸和文字。
- **数据**：局部编辑三元组、真实视频、mask/depth/flow、文字和身份保护样本。
- **指标**：保护区误差、生成区时序、身份/文字保存、用户是否理解生成边界。
- **风险**：事实改变、隐私、版权、错误身份和不可逆导出。
- **真实性边界**：generative，必须保留原片、hash、mask 和编辑参数。

## 8. 训练数据与 LOSS 设计原则

### 8.1 数据制作

1. **真实连续视频优先**：训练时必须保留真实运动、曝光变化、压缩、滚动快门和镜头切换，不要只把独立图片随机拼成视频。
2. **退化链路可解释**：将 sensor noise、ISO、motion blur、compression、downsampling、color shift、lens flare 和遮挡按场景组合，记录每个退化参数。
3. **多源监督并存**：恢复类使用 GT/LQ 配对；人像使用 parsing、landmark、identity embedding；视频编辑使用 mask/depth/flow；生成式方案使用 protected/editable region。
4. **难例要单独建集**：夜景高光、玻璃反射、眼镜、发丝、多人遮挡、快速运动和镜头切换不能只混在随机训练集中，必须有独立评测集。

### 8.2 LOSS 组合

建议按功能而不是按网络结构组织损失：

```text
L_total = L_reconstruction
        + lambda_p L_perceptual
        + lambda_t L_temporal_warp
        + lambda_i L_identity_or_semantic
        + lambda_b L_boundary_or_mask
        + lambda_c L_color_or_exposure
        + lambda_g L_generation_control
        + lambda_e L_edge_latency_power
```

损失权重只能作为起始假设。实际工程中要检查每个 loss 的梯度量级、不同区域的有效像素数、ROI 面积归一化和 ablation 结果。对于人像身份，identity loss 应当约束结构稳定而不是把所有帧强行拉向同一个表情；对于生成式编辑，protected-region loss 应优先于视觉风格损失。

## 9. 端侧可实现性与系统建议

- **ISP 前端**适合做 RAW/YUV 预处理、曝光/颜色状态、镜头切换和低延迟几何校正。
- **DSP**适合持续运行 IMU、音频事件、轻量质量检测和环形缓存。
- **NPU/GPU**适合人像 ROI、光流、深度、视频复原和局部渲染。
- **VPU/编码器前**适合将中间状态与 proxy 视频配套保存。
- **录后任务**适合双向时序模型、FLUX/扩散教师蒸馏、局部生成和高质量超分。

建议所有复杂功能提供至少三档：preview、online recording、offline rerender。温度感知调度器必须使用 hysteresis，避免模型在相邻帧之间频繁升降级。

## 10. 主要研究空白

1. **生成式视频效果的长期身份和结构稳定**：单帧效果已经很多，但手机真实长视频的 track、遮挡和镜头切换仍缺少统一方案。
2. **光照效果的物理可解释控制**：动态打光、星芒、halation 和 flare 需要参数化、可回退、可跨镜头连续。
3. **多摄与生成模型协同**：多摄提供深度和真实细节，生成模型提供补全，但两者的置信度和视差融合还不成熟。
4. **端侧质量-功耗-时序联合优化**：论文常报告画质或速度的一面，真实手机需要同时优化热、存储、后台任务、编码和用户等待。
5. **可信生成式录像文件标准**：生成区域、源帧 hash、编辑参数和可回退版本应进入产品级元数据，而不只是 UI 提示。

## 11. 建议的后续研究顺序

第一阶段建议先做无生成或弱生成的高价值方向：跨摄连续、夜景 HDR、滚动快门与 EIS 联合、视频人像身份锚定、语义 LUT 和数字变焦 ROI 超分。第二阶段再做动态光学、录后景深、语义长曝光和旅行净景。第三阶段进入有限视角扩展、天空/天气编辑和可信视频扩散。每个阶段都保留原片、代理、mask、深度、运动和评测日志，形成可持续的数据闭环。

## 附录：本地资料与交付物

- Excel：`matrix/手机录像创新功能机会库.xlsx`
- 全量机会：`metadata/opportunities.jsonl`
- 30 张技术卡：`metadata/deep_dive_30.jsonl`
- 10 个组合概念：`metadata/priority_10.jsonl`
- 官方与本地来源：`sources/source_manifest.json`
- OpenAlex 原始查询：`sources/papers/openalex_raw/`

报告中凡是“建议”“可以”“应当”的句子均属于研究判断或预研假设；产品、论文和专利事实以来源清单和证据等级为准。
