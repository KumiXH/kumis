# 手机录像后处理 IDEA 图文图鉴视觉审计

日期：2026-08-27

## 1. 产物

- 总入口：`report/手机录像后处理_IDEA图文图鉴_20260827.md`
- 簇级页面：`report/idea_atlas_pages/`
- 母图：`figures/idea_atlas/contact_sheets/`
- 簇图：`figures/idea_atlas/panels/`
- 资产清单：`figures/idea_atlas/visual_manifest.json`

## 2. 覆盖情况

| 项目 | 数量 |
|---|---:|
| 基础 IDEA | 1,154 |
| 创意簇 | 44 |
| 簇级 Markdown 页面 | 44 |
| 簇级概念图 | 44 |
| 统一母图 | 8 |
| 已检查本地链接 | 260 |
| 缺失本地资产 | 0 |

每个基础 IDEA 都通过 `idea_id` 出现在且只出现在一个创意簇页面中。每个创意簇页面都有至少一张簇级图，并包含“看图理解、完整 IDEA、风险、相关来源和阅读建议”。

## 3. 图片来源边界

本图鉴的 8 张母图由统一的概念视觉提示生成，再裁切为 44 张簇级概念图。它们用于解释用户可能看到的效果和算法对象，不是论文原文截图、厂商真实产品截图或实测结果。

页面中的产品页、论文 PDF、官方 HTML 与本地缓存链接独立列出，并保留来源状态。能够核实的来源用于理解技术背景；来源不足的簇明确写出“暂未绑定具体论文或产品来源”。

## 4. 链接策略

- 外部来源优先使用已保存的官方产品页、论文页或项目页；
- 本地论文和 HTML 使用相对路径，支持在项目内直接打开；
- 页面层级变化后，使用 `tools/isp_video/verify_idea_atlas_markdown.py` 重新检查；
- 不把图片本身作为功能成熟度、真实性、帧率、功耗或量产状态的证据。

## 5. 最新验证结果

运行：

```text
python tools/isp_video/verify_idea_atlas_markdown.py
```

结果：

```json
{
  "core_ideas": 1154,
  "cluster_pages": 44,
  "panel_images": 44,
  "local_links_checked": 260,
  "missing_assets": 0
}
```

同时完成 Python 脚本编译检查和 `git diff --check`。检查过程中没有发现页面图片缺失、基础 IDEA 漏项或本地链接断链。
