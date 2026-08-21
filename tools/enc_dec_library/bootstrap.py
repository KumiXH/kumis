import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.enc_dec_library.config import OFFICIAL_FILES, PAPERS, ROOT, ensure_directories


README = """# DiT 编解码器研究资料库

本目录研究 DiT 与 latent diffusion 中的图像/视频编码器、解码器和视觉 tokenizer。

研究主线：

1. AutoEncoder、VAE、VQ-VAE、VQGAN 与 latent diffusion 的历史演进。
2. Stable Diffusion、SDXL、SD3、FLUX、TiTok、DC-AE 等图像架构。
3. MAGVIT、CogVideoX、Open-Sora、HunyuanVideo、LTX-Video、Cosmos、Wan 等视频架构。
4. Tokenizer/VAE 预训练、冻结 VAE 的 DiT 训练及恢复任务适配。
5. 图像、视频和 LQ-HQ 超分数据的制作、输入格式与张量流。
6. FlashVSR 中 LQ_proj_in、TCDecoder 和 Wan VAE Decoder 的代码级案例。

证据标签：

- `paper-verified`：原论文正文或附录明确给出。
- `code-verified`：官方仓库源码或配置明确给出。
- `model-card-verified`：官方模型卡明确给出。
- `analysis`：基于证据形成的工程解释，不冒充论文原始结论。
- `undisclosed`：公开材料未披露，不能根据其他模型代填。
"""


SCOPE = """# 研究范围与纳入标准

## 纳入

- 对 DiT、latent diffusion 或现代视觉生成模型的 latent 表征有直接影响的权威论文。
- 有原始论文、官方技术报告、官方模型卡或官方源码可核验的架构。
- 能回答架构、压缩倍率、训练目标、数据输入或任务适配至少一项关键问题的资料。

## 排除或降级

- 只做第三方复述、没有原始证据的博客。
- 名称相近但没有实际参与编码、解码或条件输入的模块。
- 未公开训练数据和损失的商业模型，不推断其未披露配方。

## 关键边界

`LQ_proj_in` 是低质量 RGB 条件投影，不是完整编码器；`TCDecoder` 是 decoder-only 的轻量因果条件解码器；`WanDecoder` 是 Wan 3D causal VAE 的完整解码路径。三者在报告中分别建模。
"""


def main():
    ensure_directories()
    (ROOT / "README.md").write_text(README, encoding="utf-8")
    (ROOT / "metadata" / "research_scope.md").write_text(SCOPE, encoding="utf-8")

    records = []
    for paper in PAPERS:
        records.append({**paper, "evidence_status": "pending", "local_path": ""})
    for source in OFFICIAL_FILES:
        records.append({
            "key": f"code_{source['group']}_{Path(source['name']).stem}",
            "title": source["purpose"],
            "arxiv_id": "",
            "category": "source_code",
            "year": "",
            "venue": "official repository",
            "role": source["purpose"],
            "priority": "core",
            "source_type": "official_code",
            "source_url": source["url"],
            "pdf_url": "",
            "evidence_status": "pending",
            "local_path": "",
        })
    metadata = ROOT / "metadata"
    (metadata / "source_manifest.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    with (metadata / "source_manifest.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"root={ROOT}")
    print(f"papers={len(PAPERS)} code_files={len(OFFICIAL_FILES)}")


if __name__ == "__main__":
    main()
