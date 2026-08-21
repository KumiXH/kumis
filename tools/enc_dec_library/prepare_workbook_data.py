import csv
import json
from pathlib import Path

from tools.enc_dec_library.config import ROOT


SHEETS = [
    (
        "来源索引",
        "source_manifest.csv",
        [
            ("key", "Key"),
            ("title", "标题"),
            ("arxiv_id", "arXiv ID"),
            ("category", "类别"),
            ("year", "年份"),
            ("venue", "发表/来源"),
            ("role", "作用"),
            ("priority", "优先级"),
            ("source_type", "来源类型"),
            ("evidence_status", "证据状态"),
            ("local_path", "本地文件"),
            ("valid", "有效"),
            ("page_count", "页数"),
            ("sha256", "SHA-256"),
            ("retrieved_at", "检索时间"),
            ("repository_commit", "仓库 Commit"),
            ("source_url", "来源 URL"),
            ("pdf_url", "PDF URL"),
        ],
    ),
    (
        "架构比较",
        "architecture_matrix.csv",
        [
            ("model", "模型"),
            ("family", "类别"),
            ("year", "年份"),
            ("encoder", "编码器"),
            ("bottleneck", "瓶颈"),
            ("decoder", "解码器"),
            ("compression", "压缩倍率"),
            ("latent_channels_or_tokens", "潜变量通道 / Token"),
            ("causal", "因果性"),
            ("dit_role", "DiT 中的作用"),
            ("evidence_status", "证据状态"),
            ("evidence_anchor", "证据锚点"),
            ("notes", "备注"),
        ],
    ),
    (
        "训练损失",
        "training_matrix.csv",
        [
            ("model", "模型"),
            ("training_regime", "训练范式"),
            ("trainable_parts", "可训练部分"),
            ("frozen_parts", "冻结部分"),
            ("losses", "损失组合"),
            ("staging", "分阶段策略"),
            ("optimizer_schedule", "优化器 / 调度"),
            ("evidence_status", "证据状态"),
            ("evidence_anchor", "证据锚点"),
            ("caveat", "限制与注意事项"),
        ],
    ),
    (
        "数据输入",
        "dataset_matrix.csv",
        [
            ("model", "模型"),
            ("data_sources", "数据来源"),
            ("cleaning_filtering", "清洗与过滤"),
            ("sampling", "采样策略"),
            ("input_tensor", "输入张量"),
            ("target_tensor", "目标张量"),
            ("pair_construction", "配对构造"),
            ("evidence_status", "证据状态"),
            ("evidence_anchor", "证据锚点"),
            ("notes", "备注"),
        ],
    ),
    (
        "FlashVSR 模块",
        "flashvsr_modules.csv",
        [
            ("module", "模块"),
            ("category", "类别"),
            ("input", "输入"),
            ("operations", "主要运算"),
            ("output", "输出"),
            ("trained_when", "训练阶段"),
            ("inference_role", "推理角色"),
            ("loss_supervision", "监督 / 损失"),
            ("evidence", "证据锚点"),
            ("common_misread", "常见误读"),
        ],
    ),
    (
        "术语表",
        "terminology.csv",
        [
            ("term_en", "English Term"),
            ("term_zh", "中文术语"),
            ("definition", "定义"),
            ("pitfall", "常见误区"),
        ],
    ),
]


def coerce(value):
    text = (value or "").strip()
    if text == "":
        return ""
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    if text.isdigit() and len(text) < 8:
        return int(text)
    return text


def main():
    metadata = ROOT / "metadata"
    payload = {"generated_from": str(metadata), "sheets": []}
    for sheet_name, file_name, columns in SHEETS:
        with (metadata / file_name).open("r", encoding="utf-8-sig", newline="") as stream:
            records = list(csv.DictReader(stream))
        headers = ["序号", *[label for _, label in columns]]
        rows = []
        for index, record in enumerate(records, start=1):
            rows.append([index, *[coerce(record.get(key, "")) for key, _ in columns]])
        payload["sheets"].append({
            "name": sheet_name,
            "source_file": file_name,
            "headers": headers,
            "rows": rows,
        })

    destination = metadata / "workbook_data.json"
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
