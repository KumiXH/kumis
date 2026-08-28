# 手机录像特效研究库最终审计

- 审计状态：`passed_with_rendering_limitation`
- 数据数量：原子 120，完整玩法 300，组合配方 200，重点案例 50，参考 14，概念分镜 50
- 重点案例参考覆盖：50/50
- Markdown：50 个重点 ID，64 个图片引用，缺图 0
- DOCX：2166 个段落，172 个表格，64 张嵌入图，媒体文件 64，显式小于 10 磅的文本 0
- XLSX：10 个工作表，公式单元格 89，ZIP 完整性通过

## 已验证

- 所有 JSONL 通过 schema 验证，ID 引用与数量一致
- 50 张概念分镜均存在、为 RGB，且显式标注“本项目概念分镜”
- 14 张参考卡均存在，参考清单明确写出能够证明与不能证明的内容
- Markdown 的 64 个图片路径全部有效
- DOCX ZIP、媒体关系、重点 ID、微软雅黑字体和最小字号规则通过
- XLSX 工作表名、明细行数、公式单元格和 ZIP 结构通过

## 未验证

- Word 逐页 PNG 视觉渲染状态：`not_run_renderer_unavailable`
- 原因：LibreOffice/soffice is not installed or on PATH. Microsoft Word is also unavailable on this host.
- 因当前主机没有 LibreOffice/soffice 或 Microsoft Word，未能检查 Word 页面级裁切、分页和图文重叠；已以结构、媒体、字体和源图联系表审计作为替代，但不能等同于完整视觉门禁
