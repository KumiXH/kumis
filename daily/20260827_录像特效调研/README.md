# 手机录像特效玩法库

本目录以用户可直接看到、操控和分享的录像特效为中心，不把普通防抖、去噪、HDR、超分和常规运镜当作主玩法。

## 当前规模

- 特效原子：120
- 完整玩法：300
- 组合配方：200
- 重点深拆：50

## 阅读入口

- `report/手机录像特效重点玩法图文洞察_20260827.docx`：50 个重点案例的 Word 图文研究手册。
- `report/手机录像特效重点玩法图文洞察_20260827.md`：与 Word 同源、可版本管理的图文报告。
- `matrix/手机录像特效玩法库_20260827.xlsx`：120 原子、300 玩法、200 配方、重点 50 和真实参考。
- `report/手机录像特效玩法全量库_20260827.md`：300 个完整玩法的全量检索入口。
- `metadata/priority_effects.jsonl`：50 个重点玩法的实现级拆解。
- `metadata/effect_recipes.jsonl`：200 个跨原子/跨玩法组合配方。
- `metadata/effect_stats.json`：实际统计，不用计划目标冒充完成数量。
- `figures/effect_storyboards/`：50 张显式标注“本项目概念分镜”的三帧视觉说明。
- `figures/real_references/`：14 张证据边界卡，不作为产品效果截图。
- `references/reference_manifest.jsonl`：真实参考能够证明与不能证明的内容。
- `notes/final_audit.md`：跨 JSONL、图片、Markdown、DOCX 和 XLSX 的最终审计。

## 使用边界

预览预算只给出代理分辨率、ROI、实例上限、缓存和降级方向；未经实机测量的时延、帧率、功耗和内存数字不作为结论。生成式玩法还需单独评估身份漂移、几何错误、时序闪烁和事实改写风险。
