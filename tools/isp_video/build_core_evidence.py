"""Build curated core paper, dataset, and patent evidence records."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:\Repository\ReadPaper\daily\20260826_后处理调研")
PAPER_OUT = ROOT / "sources" / "papers" / "core_paper_records.jsonl"
DATASET_OUT = ROOT / "sources" / "datasets" / "dataset_records.jsonl"
PATENT_OUT = ROOT / "sources" / "patents" / "patent_records.jsonl"
STAMP = datetime.now(timezone.utc).isoformat()

CORE_PAPERS = [
    {
        "canonical_id": "doi:10.1109/TIP.2024.3372454", "title": "VRT: A Video Restoration Transformer", "year": 2024, "venue": "IEEE Transactions on Image Processing", "authors": "Chu et al.", "doi": "https://doi.org/10.1109/tip.2024.3372454", "url": "https://arxiv.org/abs/2201.12288", "local_path": "", "family": "motion_quality", "why_relevant": "Transformer-based video restoration and temporal alignment are directly relevant to mobile video enhancement.", "verification_status": "metadata_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "doi:10.1109/WACV51458.2022.00319", "title": "Robust High-Resolution Video Matting with Temporal Guidance", "year": 2022, "venue": "WACV", "authors": "Lin et al.", "doi": "https://doi.org/10.1109/wacv51458.2022.00319", "url": "https://arxiv.org/abs/2108.11515", "local_path": "", "family": "scene_editing", "why_relevant": "Temporal matting supports hair, foreground editing, relighting, background replacement, and video segmentation.", "verification_status": "metadata_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "doi:10.1109/CVPR46437.2021.00865", "title": "Real-Time High-Resolution Background Matting", "year": 2021, "venue": "CVPR", "authors": "Lin et al.", "doi": "https://doi.org/10.1109/cvpr46437.2021.00865", "url": "https://arxiv.org/abs/2012.07810", "local_path": "", "family": "scene_editing", "why_relevant": "Shows a practical path for real-time foreground extraction with auxiliary input, useful for mobile video effects.", "verification_status": "metadata_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "doi:10.1609/AAAI.V36I1.19999", "title": "MODNet: Real-Time Trimap-Free Portrait Matting via Objective Decomposition", "year": 2022, "venue": "AAAI", "authors": "Ke et al.", "doi": "https://doi.org/10.1609/aaai.v36i1.19999", "url": "https://ojs.aaai.org/index.php/AAAI/article/view/19999", "local_path": "", "family": "portrait_identity", "why_relevant": "Portrait matting without a trimap is a core primitive for phone video relighting, blur, and background effects.", "verification_status": "metadata_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2410.14400", "title": "Variable Aperture Bokeh Rendering via Customized Focal Plane Guidance", "year": 2024, "venue": "arXiv", "authors": "OpenAlex indexed authors", "doi": "https://doi.org/10.48550/arxiv.2410.14400", "url": "https://arxiv.org/abs/2410.14400", "local_path": "", "family": "depth_focus", "why_relevant": "Directly informs virtual aperture and bokeh controls that can be extended from images to temporally consistent video.", "verification_status": "metadata_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2205.03409", "title": "VFHQ: A High-Quality Video Face Super-Resolution Dataset", "year": 2022, "venue": "arXiv", "authors": "Xie et al.", "doi": "https://doi.org/10.48550/arxiv.2205.03409", "url": "https://arxiv.org/abs/2205.03409", "local_path": "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/vfhq.html", "family": "portrait_identity", "why_relevant": "High-quality facial video data and identity continuity are directly useful for phone portrait video restoration.", "verification_status": "local_project_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2207.12393", "title": "CelebV-HQ: A Large-Scale Video Facial Attributes Dataset", "year": 2022, "venue": "arXiv", "authors": "Zhu et al.", "doi": "https://doi.org/10.48550/arxiv.2207.12393", "url": "https://arxiv.org/abs/2207.12393", "local_path": "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/celebvhq.html", "family": "portrait_identity", "why_relevant": "Facial attributes and video identity coverage support region-aware portrait enhancement and identity loss design.", "verification_status": "local_project_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2012.09919", "title": "HDTF: High-Definition Talking-Face Dataset", "year": 2020, "venue": "arXiv", "authors": "Zhang et al.", "doi": "https://doi.org/10.48550/arxiv.2012.09919", "url": "https://arxiv.org/abs/2012.09919", "local_path": "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/hdtf.html", "family": "audio_visual", "why_relevant": "Talking-face video supports speaker-aware framing, focus, portrait restoration, and audio-visual research.", "verification_status": "local_project_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2112.10752", "title": "High-Resolution Image Synthesis with Latent Diffusion Models", "year": 2022, "venue": "CVPR", "authors": "Rombach et al.", "doi": "https://doi.org/10.48550/arxiv.2112.10752", "url": "https://arxiv.org/abs/2112.10752", "local_path": "D:/Repository/ReadPaper/daily/20260821_ENC_DEC/papers/01_history_and_tokenizers/ldm_2112.10752.pdf", "family": "generative_video", "why_relevant": "Latent compression and diffusion conditioning are foundations for efficient image/video editing and restoration.", "verification_status": "local_project_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2212.05199", "title": "MAGVIT: Masked Generative Video Transformer", "year": 2022, "venue": "CVPR", "authors": "Yu et al.", "doi": "https://doi.org/10.48550/arxiv.2212.05199", "url": "https://arxiv.org/abs/2212.05199", "local_path": "D:/Repository/ReadPaper/daily/20260821_ENC_DEC/papers/03_video_vae/magvit_2212.05199.pdf", "family": "generative_video", "why_relevant": "Video tokenizer and temporal latent modeling are key to efficient video editing and restoration.", "verification_status": "local_project_verified", "evidence_level": "E3",
    },
    {
        "canonical_id": "arxiv:2510.12747", "title": "FlashVSR: Near Real-Time One-Step Video Super-Resolution with Targeted Flow Distillation", "year": 2025, "venue": "arXiv", "authors": "Local ReadPaper record", "doi": "https://doi.org/10.48550/arxiv.2510.12747", "url": "https://arxiv.org/abs/2510.12747", "local_path": "D:/Repository/ReadPaper/daily/20260821_ENC_DEC/papers/05_flashvsr_case/flashvsr_2510.12747.pdf", "family": "motion_quality", "why_relevant": "One-step video SR and targeted flow distillation provide a direct route for low-latency video restoration research.", "verification_status": "local_project_verified", "evidence_level": "E3",
    },
]

DATASETS = [
    ("ffhq", "Flickr-Faces-HQ (FFHQ)", "高质量人脸静态训练源；可用于身份/细节预训练和退化合成", "https://github.com/NVlabs/ffhq-dataset", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/ffhq.html", "研究与单图许可需逐图核查", "archived_or_pending"),
    ("celeba", "CelebA", "人脸属性、身份和编辑控制数据", "https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/celeba.html", "非商业研究条款", "archived"),
    ("vggface2", "VGGFace2", "身份保持与人脸验证", "https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/vggface2.html", "需遵循官方研究使用条件", "archived"),
    ("vfhq", "VFHQ", "高质量视频人脸超分/复原", "https://liangbinxie.github.io/projects/vfhq/", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/vfhq.html", "需核查项目下载与再分发条件", "archived"),
    ("celebvhq", "CelebV-HQ", "高质量人脸视频与属性", "https://celebv-hq.github.io/", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/celebvhq.html", "需核查项目条款", "archived"),
    ("hdtf", "HDTF", "高清说话人视频、音画联合", "https://github.com/MRzzm/HDTF", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/hdtf.html", "原视频版权仍需遵循来源方", "archived"),
    ("vfrx", "VFRxBenchmark", "真实视频人脸复原评测", "https://arxiv.org/abs/2404.19500", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/fos_vfrx.html", "旧项目链接返回 404，优先以论文核验", "paper_only_or_stale_link"),
    ("ntire2025_face", "NTIRE 2025 Real-World Face Restoration", "真实人脸复原竞赛数据与评测", "https://github.com/zhengchen1999/NTIRE2025_RealWorld_Face_Restoration", "D:/Repository/ReadPaper/daily/PortraitSR/datasets/official_docs/ntire2025_face.html", "挑战赛条款", "archived"),
]

PATENTS = [
    {
        "patent_id": "PATENT_PENDING_001", "title": "手机视频中基于语义区域的光照/镜头效果后处理", "assignee": "待公开专利号核验", "status": "pending", "family": "relighting/computational_optics", "abstract": "本项目将动态打光、镜头效果和区域 mask 组合为候选专利检索主题；当前不把检索主题作为专利事实。", "url": "", "local_path": "", "verification_status": "unverified", "evidence_level": "E4",
    },
    {
        "patent_id": "PATENT_PENDING_002", "title": "多摄连续变焦与视频色彩/曝光状态切换", "assignee": "待公开专利号核验", "status": "pending", "family": "multi_camera/color_science", "abstract": "候选专利检索主题，等待稳定公开号码、文本和申请人信息后入库。", "url": "", "local_path": "", "verification_status": "unverified", "evidence_level": "E4",
    },
]


def main() -> None:
    PAPER_OUT.write_text("\n".join(json.dumps({**x, "retrieved_at": STAMP}, ensure_ascii=False) for x in CORE_PAPERS) + "\n", encoding="utf-8")
    DATASET_OUT.write_text("\n".join(json.dumps({"dataset_id": k, "name": n, "task": t, "official_url": u, "local_doc": l, "license_or_access": a, "verification_status": s, "retrieved_at": STAMP}, ensure_ascii=False) for k, n, t, u, l, a, s in DATASETS) + "\n", encoding="utf-8")
    PATENT_OUT.write_text("\n".join(json.dumps({**x, "retrieved_at": STAMP}, ensure_ascii=False) for x in PATENTS) + "\n", encoding="utf-8")
    print(f"core papers={len(CORE_PAPERS)} datasets={len(DATASETS)} patents={len(PATENTS)}")


if __name__ == "__main__":
    main()
