# 手机录像特效玩法库 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立以可见特效、实时交互和跨帧演化为中心的手机录像特效库，包含特效原子、完整玩法、组合配方、重点深度案例、真实参考、Excel 和图文 Word。

**Architecture:** 内容源与生成器分离：策划目录维护可审计的特效原子、玩法模板、组合规则和重点案例，Python 构建器确定性生成 JSONL、统计、Markdown 和 Word，Node 构建器生成 Excel。验证器把“可见变化、交互触发、原子引用、风险边界和非工程型方向”作为硬门槛；真实参考独立登记来源类型和实现边界，不反向限制原创 IDEA 数量。

**Tech Stack:** Python 3.12、标准库 `json/pathlib/hashlib/collections/unittest`、Pillow、python-docx、PyMuPDF、Node.js、ExcelJS 或项目现有 artifact_tool 运行时、LibreOffice/Word 渲染。

---

## 文件结构

### 工具代码

- `tools/video_effects/__init__.py`：包入口。
- `tools/video_effects/schema.py`：原子、玩法、配方、重点案例和参考来源的字段与校验。
- `tools/video_effects/effect_catalog.py`：12 个特效族、特效原子和完整玩法策划数据。
- `tools/video_effects/recipe_catalog.py`：组合语法和经人工策划的组合配方。
- `tools/video_effects/priority_catalog.py`：50 个重点玩法的深度分析数据。
- `tools/video_effects/build_library.py`：生成 JSONL、统计、README 和全量 Markdown。
- `tools/video_effects/build_references.py`：登记、缓存和核验真实参考。
- `tools/video_effects/extract_reference_visuals.py`：从本地页面、PDF、图片或视频中提取可追溯视觉素材。
- `tools/video_effects/build_workbook.mjs`：生成 Excel。
- `tools/video_effects/build_report_docx.py`：生成重点玩法图文 Word。
- `tools/video_effects/verify_library.py`：执行数据、引用、Excel、Markdown 和 Word 验证。
- `tools/video_effects/render_report_qa.py`：渲染 Word 代表页面。
- `tools/video_effects/test_video_effects.py`：全部 Python 回归测试。

### 研究产物

- `daily/20260827_录像特效调研/README.md`
- `daily/20260827_录像特效调研/metadata/effect_atoms.jsonl`
- `daily/20260827_录像特效调研/metadata/effect_ideas.jsonl`
- `daily/20260827_录像特效调研/metadata/effect_recipes.jsonl`
- `daily/20260827_录像特效调研/metadata/priority_effects.jsonl`
- `daily/20260827_录像特效调研/metadata/effect_stats.json`
- `daily/20260827_录像特效调研/references/reference_manifest.jsonl`
- `daily/20260827_录像特效调研/references/official_products/`
- `daily/20260827_录像特效调研/references/software_effects/`
- `daily/20260827_录像特效调研/references/film_mv_ads/`
- `daily/20260827_录像特效调研/references/papers_projects/`
- `daily/20260827_录像特效调研/figures/real_references/`
- `daily/20260827_录像特效调研/figures/effect_storyboards/`
- `daily/20260827_录像特效调研/report/手机录像特效玩法全量库_20260827.md`
- `daily/20260827_录像特效调研/report/手机录像特效重点玩法图文洞察_20260827.md`
- `daily/20260827_录像特效调研/report/手机录像特效重点玩法图文洞察_20260827.docx`
- `daily/20260827_录像特效调研/report/rendered/`
- `daily/20260827_录像特效调研/matrix/手机录像特效玩法库_20260827.xlsx`
- `daily/20260827_录像特效调研/notes/final_audit.md`

## Task 1: 建立特效数据 schema 与硬门槛

**Files:**
- Create: `tools/video_effects/__init__.py`
- Create: `tools/video_effects/schema.py`
- Create: `tools/video_effects/test_video_effects.py`

- [ ] **Step 1: 写入 schema 失败测试**

测试至少包含：

```python
class SchemaTests(unittest.TestCase):
    def test_effect_atom_requires_visible_primitive(self) -> None:
        atom = make_valid_atom()
        atom["visible_primitive"] = ""
        with self.assertRaisesRegex(ValueError, "visible_primitive"):
            validate_atom(atom)

    def test_effect_idea_requires_trigger_or_control(self) -> None:
        idea = make_valid_idea()
        idea["trigger_signals"] = []
        idea["user_controls"] = []
        with self.assertRaisesRegex(ValueError, "trigger"):
            validate_idea(idea)

    def test_effect_idea_rejects_engineering_only_feature(self) -> None:
        idea = make_valid_idea()
        idea["name_zh"] = "普通视频防抖"
        idea["visible_effect"] = "让视频更稳定"
        with self.assertRaisesRegex(ValueError, "engineering-only"):
            validate_idea(idea)

    def test_recipe_requires_novel_combined_effect(self) -> None:
        recipe = make_valid_recipe()
        recipe["combined_effect"] = "光轨加粒子"
        with self.assertRaisesRegex(ValueError, "combined_effect"):
            validate_recipe(recipe)
```

- [ ] **Step 2: 运行测试并确认失败**

```powershell
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tools.video_effects.test_video_effects.SchemaTests -v
```

Expected: `ModuleNotFoundError` 或 schema 函数不存在。

- [ ] **Step 3: 实现五类记录校验器**

`schema.py` 提供：

```python
validate_atom(record: Mapping[str, object]) -> None
validate_idea(record: Mapping[str, object], atom_ids: set[str] | None = None) -> None
validate_recipe(record: Mapping[str, object], atom_ids: set[str], idea_ids: set[str]) -> None
validate_priority(record: Mapping[str, object], idea_ids: set[str]) -> None
validate_reference(record: Mapping[str, object]) -> None
```

原子必填字段：

```text
atom_id, name_zh, name_en, family, primitive_type, visible_primitive,
required_signals, temporal_state, parameters, failure_modes, mobile_notes
```

玩法必填字段：

```text
effect_id, name_zh, name_en, family, visible_effect, scenarios,
target_objects, spatial_scope, trigger_signals, interaction,
user_controls, preview_pipeline, post_pipeline, required_signals,
atom_ids, temporal_window, continuity_challenges, edge_difficulty,
execution_targets, generation_level, risks, novelty, shareability,
product_value, reference_ids, combinable_effect_ids, status
```

配方必填字段：

```text
recipe_id, name_zh, component_atom_ids, component_effect_ids,
trigger_logic, combined_effect, why_new, preview_behavior,
post_behavior, risks, target_scenarios
```

重点案例必填字段：

```text
priority_id, effect_id, problem, experience_story, interaction_timeline,
module_pipeline, tensor_or_signal_flow, preview_budget,
recorded_metadata, post_refinement, adjustable_parameters,
failure_and_fallback, mobile_product_form, references
```

硬门槛：玩法必须有非空 `visible_effect`，且 `trigger_signals` 或 `user_controls` 至少一项非空；必须引用原子；禁止工程型黑名单标题作为主玩法；所有列表字段必须是真正的非空字符串列表；ID 前缀和引用有效。

- [ ] **Step 4: 运行 schema 测试**

Expected: 所有 SchemaTests 通过。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/__init__.py tools/video_effects/schema.py tools/video_effects/test_video_effects.py
git commit -m "test: define mobile video effects schemas"
```

## Task 2: 建立约 120 个特效原子

**Files:**
- Create: `tools/video_effects/effect_catalog.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/metadata/effect_atoms.jsonl`

- [ ] **Step 1: 写入原子覆盖测试**

测试要求：

```python
class AtomCatalogTests(unittest.TestCase):
    def test_atom_count_and_ids(self) -> None:
        atoms = build_atoms()
        self.assertGreaterEqual(len(atoms), 110)
        self.assertLessEqual(len(atoms), 140)
        self.assertEqual(len(atoms), len({row["atom_id"] for row in atoms}))

    def test_required_atom_families_exist(self) -> None:
        names = "\n".join(row["name_zh"] for row in build_atoms())
        for term in ["轨迹", "视线", "眨眼", "残影", "时间冻结", "轮廓光", "影子", "材质", "粒子", "节拍", "空间锚点"]:
            self.assertIn(term, names)
```

- [ ] **Step 2: 运行测试并确认失败**

Expected: `build_atoms` 不存在。

- [ ] **Step 3: 实现 10 类可复用原子**

`effect_catalog.py` 使用明确策划条目生成 110-140 个原子，覆盖分割、几何、时间、光效、复制、形变、材质、粒子、生成和触发。每个原子的 `visible_primitive` 必须解释它在画面里改变什么，不能只写模型名称。

关键原子至少包括：手部 2D/3D 轨迹、世界空间锚点、时间衰减、光绘笔刷、视线向量、瞳孔重定向、眼神光重渲染、眨眼事件、表情强度、人体时间克隆、局部时间冻结、影子分层、虚拟轮廓光、体积光、材质替换、像素溶解、音频节拍、歌词时间戳和多人关系图。

- [ ] **Step 4: 生成并验证原子 JSONL**

```powershell
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/video_effects/effect_catalog.py --atoms-only
```

Expected: 数量在 110-140；ID 唯一；重复运行 SHA-256 相同。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/effect_catalog.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/metadata/effect_atoms.jsonl
git commit -m "research: add reusable mobile video effect atoms"
```

## Task 3: 生成约 300 个完整特效玩法

**Files:**
- Modify: `tools/video_effects/effect_catalog.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/metadata/effect_ideas.jsonl`

- [ ] **Step 1: 写入完整玩法质量测试**

测试必须验证：

- 数量在 260-340；
- 12 个特效族都有内容，每族至少 12 条；
- ID 和中英文名称唯一；
- 每条通过 schema 并引用有效原子；
- 每条有一句话可见效果；
- 每条有触发或控制；
- 不含“普通防抖、普通去噪、普通 HDR、普通超分、普通自动构图、常规多摄切换”；
- 不能仅改变场景或对象而保持 `visible_effect`、触发和参数完全相同；
- 实时光绘轨迹、视线矫正、时间分身、局部时间冻结、节拍星芒、影子分身、镜面穿越、材质溶解、歌词环绕和多人能量传递必须存在。

增加针对重复的测试：

```python
fingerprint = (
    normalize(row["visible_effect"]),
    tuple(sorted(row["trigger_signals"])),
    tuple(sorted(row["user_controls"])),
    tuple(sorted(row["atom_ids"])),
)
self.assertEqual(len(fingerprints), len(set(fingerprints)))
```

- [ ] **Step 2: 运行测试并确认失败**

Expected: 完整玩法尚未实现。

- [ ] **Step 3: 实现 12 族策划数据与确定性构建**

每条玩法由策划过的“对象 + 时序行为 + 触发 + 可见结果 + 参数”组成。可以使用受控模板减少重复代码，但每个模板实例必须改变用户效果或交互逻辑，不能只更换场景名。

12 族固定为：

```text
light_trails_optics, body_motion_clones, face_gaze_expression,
time_editing, spatial_portals, virtual_light_shadow,
material_morph, particles_weather, world_style,
audio_lyrics, effect_cinematography, multi_person_interaction
```

实时光绘至少覆盖手指绘制、人体动作轨迹、移动光源轨迹、世界空间书写和节拍变色；视线至少覆盖摄像头对视矫正、多人对话对视、视线触发对象发光、眼神光跟随和凝视选择特效。

- [ ] **Step 4: 生成并抽样审查**

```powershell
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/video_effects/effect_catalog.py
rg -n "光绘|视线|眨眼|分身|冻结|星芒|影子|镜面|溶解|歌词|能量传递" daily/20260827_录像特效调研/metadata/effect_ideas.jsonl
```

Expected: 每个重点词有多个独立玩法；没有防抖类条目混入。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/effect_catalog.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/metadata/effect_ideas.jsonl
git commit -m "research: build mobile video effect idea catalog"
```

## Task 4: 建立约 200 个组合配方

**Files:**
- Create: `tools/video_effects/recipe_catalog.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/metadata/effect_recipes.jsonl`

- [ ] **Step 1: 写入组合质量测试**

测试要求：

- 数量在 160-240；
- 每条引用至少两个不同组件；
- 所有原子和玩法引用存在；
- `combined_effect` 与 `why_new` 均为非空完整描述；
- 配方名称和指纹唯一；
- 禁止用字符串拼接自动生成 `combined_effect`；
- 至少 40 条配方含实时光轨、视线、表情、时间、影子、声音或多人关系中的两个维度。

- [ ] **Step 2: 运行测试并确认失败**

Expected: 配方模块不存在。

- [ ] **Step 3: 实现组合语法和策划配方**

允许使用组合语法辅助构建，但 `combined_effect`、`why_new`、`trigger_logic` 和风险必须来自策划记录。典型组合：

```text
手部轨迹 + 空间锚点 + 发光衰减 + 节拍调色
视线矫正 + 眼神光 + 对话对象识别
时间克隆 + 姿态差分 + 颜色分层
影子分割 + 时间延迟 + 动作反相
歌词时间戳 + 口型位置 + 空间文字环
多人关系图 + 触碰事件 + 能量粒子传递
```

- [ ] **Step 4: 生成 JSONL 并验证确定性**

Expected: 数量在目标范围，重复运行哈希一致。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/recipe_catalog.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/metadata/effect_recipes.jsonl
git commit -m "research: add composable video effect recipes"
```

## Task 5: 深度拆解 50 个重点玩法

**Files:**
- Create: `tools/video_effects/priority_catalog.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/metadata/priority_effects.jsonl`

- [ ] **Step 1: 写入重点案例完整性测试**

测试要求准确 50 条，全部引用现有玩法，并完整包含：用户故事、交互时间线、模块流水线、信号流、预览预算、录制元数据、录后重算、可调参数、失败回退和产品形态。

首两条固定为：

1. 实时光绘轨迹；
2. 视线矫正与虚拟对视。

测试必须确认这两条的 `interaction_timeline`、`module_pipeline`、`preview_budget`、`recorded_metadata` 和 `failure_and_fallback` 均为多项列表，不是单句占位。

- [ ] **Step 2: 运行测试并确认失败**

Expected: 重点目录不存在。

- [ ] **Step 3: 实现 50 条深度记录**

每条至少包含 5 个交互时间节点、5 个模块步骤、4 类录制元数据、6 个可调参数和 4 个失败回退。预览预算只描述分辨率代理、处理频率、ROI 和降级顺序，不虚构未测量的毫秒、功耗或 FPS 数字。

实时光绘重点说明：手部/人体/光源轨迹、2D 与世界空间模式、遮挡、轨迹寿命、发光和粒子渲染、录后重绘。

视线矫正重点说明：双眼关键点、虹膜/瞳孔、头姿、目标注视点、眨眼保护、眼镜遮挡、眼神光联动、置信度回退和身份保护。

- [ ] **Step 4: 运行测试并生成 JSONL**

Expected: 50/50 记录通过，前两条信息密度满足测试。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/priority_catalog.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/metadata/priority_effects.jsonl
git commit -m "research: detail priority mobile video effects"
```

## Task 6: 构建统一库、统计和全量 Markdown

**Files:**
- Create: `tools/video_effects/build_library.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/metadata/effect_stats.json`
- Create: `daily/20260827_录像特效调研/README.md`
- Create: `daily/20260827_录像特效调研/report/手机录像特效玩法全量库_20260827.md`

- [ ] **Step 1: 写入交叉引用和报告测试**

测试所有 ID 唯一、原子/玩法/配方/重点引用有效，统计数字与 JSONL 行数一致；全量 Markdown 包含 12 族、全部玩法 ID、可见效果、交互、实时/录后、风险和组合入口。

- [ ] **Step 2: 运行测试并确认失败**

Expected: 构建器不存在。

- [ ] **Step 3: 实现一键构建器**

```powershell
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/video_effects/build_library.py
```

构建器重新生成全部 JSONL、统计、README 和全量 Markdown；使用 UTF-8、稳定排序和 `ensure_ascii=False`；重复运行不得产生 diff。

- [ ] **Step 4: 执行全量回归与确定性检查**

Expected: 所有 Python 测试通过；连续两次构建 `git diff` 不变化。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/build_library.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/metadata daily/20260827_录像特效调研/README.md daily/20260827_录像特效调研/report/手机录像特效玩法全量库_20260827.md
git commit -m "docs: build full mobile video effects library"
```

## Task 7: 调研和登记真实视觉参考

**Files:**
- Create: `tools/video_effects/build_references.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/references/reference_manifest.jsonl`
- Create: `daily/20260827_录像特效调研/references/official_products/`
- Create: `daily/20260827_录像特效调研/references/software_effects/`
- Create: `daily/20260827_录像特效调研/references/film_mv_ads/`
- Create: `daily/20260827_录像特效调研/references/papers_projects/`

- [ ] **Step 1: 写入参考来源边界测试**

每条参考必须包含：`reference_id`、标题、来源类型、产品/作品/论文、发布者、年份、原始来源、获取状态、本地文件、对应 effect IDs、实际展示、不能证明、实现边界、SHA-256。

实现边界枚举：

```text
mobile_realtime, mobile_offline, desktop_realtime, desktop_offline,
film_postproduction, research_prototype, visual_inspiration
```

测试禁止 `film_postproduction` 或 `visual_inspiration` 被标记为手机实时量产。

- [ ] **Step 2: 运行测试并确认失败**

Expected: 参考构建器不存在。

- [ ] **Step 3: 建立检索种子和低并发采集**

重点检索：

- 光绘、长曝光轨迹、AR 轨迹、动作拖尾；
- eye contact correction、gaze redirection、NVIDIA Broadcast Eye Contact、FaceTime eye contact；
- TikTok、CapCut、Snap、Meta、Apple Clips 等官方特效；
- After Effects、DaVinci Resolve、Final Cut、Unreal Engine、Unity VFX Graph 官方效果；
- 时间切片、分身、影子、材质、粒子、歌词和多人交互相关论文/项目页；
- 电影、MV 和广告中的代表效果，只登记可核实作品和效果，不下载未经允许的大体积成片。

网络采集间隔至少 2 秒，优先官方页面和本地已有材料；失败记录原因，不绕过访问限制。

- [ ] **Step 4: 人工核验并生成 manifest**

每个重点玩法至少有一个真实参考或明确标成暂无直接参考；同一参考可以关联多个高度相关玩法，但必须逐条写明它展示和不能证明的内容。

- [ ] **Step 5: 精确提交**

```powershell
git add -- tools/video_effects/build_references.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/references
git commit -m "research: add verifiable video effect references"
```

## Task 8: 提取参考图片与效果分镜

**Files:**
- Create: `tools/video_effects/extract_reference_visuals.py`
- Modify: `tools/video_effects/test_video_effects.py`
- Create: `daily/20260827_录像特效调研/figures/real_references/`
- Create: `daily/20260827_录像特效调研/figures/effect_storyboards/`

- [ ] **Step 1: 写入资产定位和完整性测试**

PDF 图必须有页码/图号，视频帧必须有时间戳，网页图片必须有页面区域或原始媒体定位；所有正式图片非空、尺寸大于 320x180、图像方差高于空白阈值。

- [ ] **Step 2: 实现提取与联系表工具**

支持本地 HTML 图片、PDF 页面/裁切、视频帧和已有图片；保留原图，衍生裁切单独保存。对无真实效果图的原创重点玩法，可用三帧文本分镜说明交互和时序，但必须标记为“本项目分镜”，不能伪装真实产品截图。

- [ ] **Step 3: 生成视觉资产并人工检查**

每个重点玩法优先配置：真实参考、局部放大或三帧时序分镜中的至少一种。联系表用于检查图片是否真正表现对应特效。

- [ ] **Step 4: 精确提交**

```powershell
git add -- tools/video_effects/extract_reference_visuals.py tools/video_effects/test_video_effects.py daily/20260827_录像特效调研/figures
git commit -m "research: add mobile video effect visuals"
```

## Task 9: 生成 Excel 特效数据库

**Files:**
- Create: `tools/video_effects/build_workbook.mjs`
- Create: `daily/20260827_录像特效调研/matrix/手机录像特效玩法库_20260827.xlsx`

- [ ] **Step 1: 实现工作簿结构**

工作表：

```text
总览, 特效原子, 完整玩法, 组合配方, 重点50,
真实参考, 按特效族, 按触发方式, 按生成程度, 字段字典
```

完整玩法表优先展示：名称、可见效果、交互、参数、实时流程、录后流程、原子、难度、生成程度、风险和参考。冻结标题行、开启筛选、微软雅黑、文本换行、列宽适合阅读。

- [ ] **Step 2: 生成并验证工作簿**

使用项目可用的表格运行时；验证 ZIP 完整、工作表数量和名称、每张表行数、公式错误和代表性单元格内容。渲染总览、完整玩法和重点50的代表区域。

- [ ] **Step 3: 精确提交**

```powershell
git add -- tools/video_effects/build_workbook.mjs daily/20260827_录像特效调研/matrix
git commit -m "docs: add mobile video effects workbook"
```

## Task 10: 生成重点玩法 Markdown 与 Word

**Files:**
- Create: `tools/video_effects/build_report_docx.py`
- Create: `daily/20260827_录像特效调研/report/手机录像特效重点玩法图文洞察_20260827.md`
- Create: `daily/20260827_录像特效调研/report/手机录像特效重点玩法图文洞察_20260827.docx`

- [ ] **Step 1: 先生成重点 Markdown**

每个重点玩法固定包含：效果说明、用户故事、交互时间线、真实参考/分镜、模块流程、信号流、实时预览、录制元数据、录后重算、可调参数、失败回退、端侧产品形态、风险和组合方向。

实时光绘与视线矫正作为前两章，篇幅和信息密度不得低于其他案例，并分别增加参数表与失败场景表。

- [ ] **Step 2: 实现 Word 构建器**

沿用项目现有 Word 工具的微软雅黑、A4、页眉页脚、内部书签和固定表格宽度。正文最小 10 pt；减少装饰模块；图片、图注、来源和实现边界紧邻；每个重点案例控制在相邻 2-4 页。

- [ ] **Step 3: 运行结构验证**

Word 必须包含 50 个 priority ID、全部案例标题、至少与有视觉资产案例数相同的图片关系、无损 ZIP、无重复或缺失案例。

- [ ] **Step 4: 精确提交**

```powershell
git add -- tools/video_effects/build_report_docx.py daily/20260827_录像特效调研/report/手机录像特效重点玩法图文洞察_20260827.md daily/20260827_录像特效调研/report/手机录像特效重点玩法图文洞察_20260827.docx
git commit -m "docs: add illustrated mobile video effects report"
```

## Task 11: 最终验证与视觉 QA

**Files:**
- Create: `tools/video_effects/verify_library.py`
- Create: `tools/video_effects/render_report_qa.py`
- Create: `daily/20260827_录像特效调研/report/rendered/`
- Create: `daily/20260827_录像特效调研/notes/final_audit.md`

- [ ] **Step 1: 实现一键验证器**

检查：JSONL 可解析、schema 通过、ID 与引用有效、数量目标、无工程型黑名单、无重复指纹、参考边界、图片定位、Excel 工作表和行数、Markdown ID、Word ZIP/媒体/标题计数。

- [ ] **Step 2: 运行全部测试和构建**

```powershell
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tools.video_effects.test_video_effects -v
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/video_effects/build_library.py
& 'C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/video_effects/verify_library.py
```

Expected: 零 invalid record、零 missing reference、零 duplicate fingerprint、零 engineering-only idea、零 missing image path。

- [ ] **Step 3: 渲染 Word 代表页面**

渲染封面、目录、实时光绘、视线矫正、每个特效族首个案例、横图/竖图密集页面和最后一页。检查图片清晰、无拉伸、文字不溢出、图注不孤立、来源边界可读。

- [ ] **Step 4: 写最终审计**

`final_audit.md` 报告实际原子数、玩法数、配方数、重点数、参考数、图片数、来源类型、手机实时/离线/桌面/影视/研究分布，以及没有真实参考的重点玩法。

- [ ] **Step 5: 最终精确提交**

```powershell
git add -- tools/video_effects/verify_library.py tools/video_effects/render_report_qa.py daily/20260827_录像特效调研/report/rendered daily/20260827_录像特效调研/notes/final_audit.md daily/20260827_录像特效调研/report daily/20260827_录像特效调研/matrix
git commit -m "test: verify mobile video effects research library"
```

## Task 12: 交付核验

**Files:**
- Verify only: Tasks 1-11 outputs

- [ ] **Step 1: 获取真实统计和提交证据**

读取 `effect_stats.json` 和 `final_audit.md`，运行 `git log -12 --oneline`、`git status --short`，记录最终提交和工作区状态。

- [ ] **Step 2: 抽样核验用户最关心方向**

从 JSONL、Excel、Markdown 和 Word 四层分别确认：实时光绘轨迹、视线矫正、残影分身、局部时间冻结、虚拟光影、材质溶解、粒子跟随、歌词环绕、多人互动和特效型运镜均可检索，且内容一致。

- [ ] **Step 3: 报告交付路径和边界**

最终回复提供 Word、Excel、全量 Markdown、JSONL、真实参考 manifest 和审计文件绝对路径；只报告实际测得数量，不使用计划目标冒充完成数量，并说明没有真实参考或仅属影视灵感的方向。
