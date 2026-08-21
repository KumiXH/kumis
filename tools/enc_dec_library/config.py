from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "daily" / "20260821_ENC_DEC"

CATEGORIES = {
    "01_history_and_tokenizers": ROOT / "papers" / "01_history_and_tokenizers",
    "02_image_vae": ROOT / "papers" / "02_image_vae",
    "03_video_vae": ROOT / "papers" / "03_video_vae",
    "04_dit_training": ROOT / "papers" / "04_dit_training",
    "05_flashvsr_case": ROOT / "papers" / "05_flashvsr_case",
}


def arxiv(key, title, arxiv_id, category, year, venue, role, priority="core"):
    return {
        "key": key,
        "title": title,
        "arxiv_id": arxiv_id,
        "category": category,
        "year": year,
        "venue": venue,
        "role": role,
        "priority": priority,
        "source_type": "paper",
        "source_url": f"https://arxiv.org/abs/{arxiv_id}",
        "pdf_url": f"https://export.arxiv.org/pdf/{arxiv_id}",
    }


PAPERS = [
    arxiv("vae", "Auto-Encoding Variational Bayes", "1312.6114", "01_history_and_tokenizers", 2014, "ICLR 2014", "continuous latent foundation"),
    arxiv("vqvae", "Neural Discrete Representation Learning", "1711.00937", "01_history_and_tokenizers", 2017, "NeurIPS 2017", "discrete tokenizer foundation"),
    arxiv("vqvae2", "Generating Diverse High-Fidelity Images with VQ-VAE-2", "1906.00446", "01_history_and_tokenizers", 2019, "NeurIPS 2019", "hierarchical discrete tokenizer", "supporting"),
    arxiv("vqgan", "Taming Transformers for High-Resolution Image Synthesis", "2012.09841", "01_history_and_tokenizers", 2021, "CVPR 2021", "perceptual adversarial tokenizer"),
    arxiv("ldm", "High-Resolution Image Synthesis with Latent Diffusion Models", "2112.10752", "01_history_and_tokenizers", 2022, "CVPR 2022", "latent diffusion autoencoder"),
    arxiv("dit", "Scalable Diffusion Models with Transformers", "2212.09748", "04_dit_training", 2023, "ICCV 2023", "frozen VAE latent DiT training"),
    arxiv("sdxl", "SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis", "2307.01952", "02_image_vae", 2023, "ICLR 2024", "production latent diffusion baseline"),
    arxiv("sd3", "Scaling Rectified Flow Transformers for High-Resolution Image Synthesis", "2403.03206", "02_image_vae", 2024, "ICML 2024", "16-channel image VAE and MMDiT"),
    arxiv("titok", "An Image is Worth 32 Tokens for Reconstruction and Generation", "2406.07550", "02_image_vae", 2024, "NeurIPS 2024", "one-dimensional image tokenizer"),
    arxiv("dcae", "Deep Compression Autoencoder for Efficient High-Resolution Diffusion Models", "2410.10733", "02_image_vae", 2025, "ICLR 2025", "high-compression continuous autoencoder"),
    arxiv("sana", "SANA: Efficient High-Resolution Image Synthesis with Linear Diffusion Transformers", "2410.10629", "02_image_vae", 2025, "ICLR 2025", "DC-AE in efficient DiT"),
    arxiv("videogpt", "VideoGPT: Video Generation using VQ-VAE and Transformers", "2104.10157", "03_video_vae", 2021, "arXiv 2021", "3D VQ-VAE video tokenizer", "supporting"),
    arxiv("magvit", "MAGVIT: Masked Generative Video Transformer", "2212.05199", "03_video_vae", 2023, "CVPR 2023", "unified image-video tokenizer"),
    arxiv("magvit2", "Language Model Beats Diffusion -- Tokenizer is Key to Visual Generation", "2310.05737", "03_video_vae", 2024, "ICLR 2024", "lookup-free causal video tokenizer"),
    arxiv("cvvae", "CV-VAE: A Compatible Video VAE for Latent Generative Video Models", "2405.20279", "03_video_vae", 2024, "arXiv 2024", "image-VAE-compatible video VAE"),
    arxiv("cogvideox", "CogVideoX: Text-to-Video Diffusion Models with An Expert Transformer", "2408.06072", "03_video_vae", 2025, "ICLR 2025", "causal 3D video VAE"),
    arxiv("wfvae", "WF-VAE: Enhancing Video VAE by Wavelet-Driven Energy Flow for Latent Video Diffusion Model", "2411.17459", "03_video_vae", 2025, "CVPR 2025", "wavelet video VAE"),
    arxiv("vidtok", "VidTok: A Versatile and Open-Source Video Tokenizer", "2412.13061", "03_video_vae", 2025, "CVPR 2025", "open video tokenizer training study"),
    arxiv("opensora", "Open-Sora: Democratizing Efficient Video Production for All", "2412.20404", "03_video_vae", 2025, "arXiv 2024", "open video generation system and VAE"),
    arxiv("hunyuanvideo", "HunyuanVideo: A Systematic Framework For Large Video Generative Models", "2412.03603", "03_video_vae", 2025, "CVPR 2025", "causal video VAE system"),
    arxiv("ltxvideo", "LTX-Video: Realtime Video Latent Diffusion", "2501.00103", "03_video_vae", 2025, "arXiv 2024", "high-compression video VAE"),
    arxiv("cosmos", "Cosmos World Foundation Model Platform for Physical AI", "2501.03575", "03_video_vae", 2025, "arXiv 2025", "continuous and discrete video tokenizers"),
    arxiv("wan", "Wan: Open and Advanced Large-Scale Video Generative Models", "2503.20314", "03_video_vae", 2025, "arXiv 2025", "Wan causal 3D VAE"),
    arxiv("flashvsr", "FlashVSR: Towards Real-Time Diffusion-Based Streaming Video Super-Resolution", "2510.12747", "05_flashvsr_case", 2026, "CVPR 2026", "LQ projection and conditional decoder case"),
]


PREFERRED_PDF_URLS = {
    "vqvae": "https://proceedings.neurips.cc/paper_files/paper/2017/file/7a98af17e63a0ac09ce2e96d03992fbc-Paper.pdf",
    "vqvae2": "https://proceedings.neurips.cc/paper_files/paper/2019/file/5f8e2fa1718d1bbcadf1cd9c7a54fb8c-Paper.pdf",
    "vqgan": "https://openaccess.thecvf.com/content/CVPR2021/papers/Esser_Taming_Transformers_for_High-Resolution_Image_Synthesis_CVPR_2021_paper.pdf",
    "ldm": "https://openaccess.thecvf.com/content/CVPR2022/papers/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.pdf",
    "dit": "https://openaccess.thecvf.com/content/ICCV2023/papers/Peebles_Scalable_Diffusion_Models_with_Transformers_ICCV_2023_paper.pdf",
    "magvit": "https://openaccess.thecvf.com/content/CVPR2023/papers/Yu_MAGVIT_Masked_Generative_Video_Transformer_CVPR_2023_paper.pdf",
    "wfvae": "https://openaccess.thecvf.com/content/CVPR2025/papers/Li_WF-VAE_Enhancing_Video_VAE_by_Wavelet-Driven_Energy_Flow_for_Latent_CVPR_2025_paper.pdf",
    "flashvsr": "https://openaccess.thecvf.com/content/CVPR2026/papers/Zhuang_FlashVSR_Towards_Real-time_Diffusion-Based_Streaming_Video_Super_Resolution_CVPR_2026_paper.pdf",
}


OFFICIAL_FILES = [
    {
        "group": "flux",
        "name": "model.py",
        "url": "https://raw.githubusercontent.com/black-forest-labs/flux/main/src/flux/model.py",
        "purpose": "FLUX DiT implementation",
    },
    {
        "group": "flux",
        "name": "modules/autoencoder.py",
        "url": "https://raw.githubusercontent.com/black-forest-labs/flux/main/src/flux/modules/autoencoder.py",
        "purpose": "FLUX image autoencoder implementation",
    },
    {
        "group": "flux",
        "name": "util.py",
        "url": "https://raw.githubusercontent.com/black-forest-labs/flux/main/src/flux/util.py",
        "purpose": "FLUX autoencoder configuration",
    },
    {
        "group": "sd3",
        "name": "sd3_impls.py",
        "url": "https://raw.githubusercontent.com/Stability-AI/sd3-ref/master/sd3_impls.py",
        "purpose": "SD3 VAE and latent preprocessing implementation",
    },
    {
        "group": "ldm",
        "name": "autoencoder.py",
        "url": "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/ldm/models/autoencoder.py",
        "purpose": "LDM autoencoder training implementation",
    },
    {
        "group": "ldm",
        "name": "vqperceptual.py",
        "url": "https://raw.githubusercontent.com/CompVis/latent-diffusion/main/ldm/modules/losses/vqperceptual.py",
        "purpose": "LDM reconstruction/perceptual/adversarial losses",
    },
    {
        "group": "dit",
        "name": "models.py",
        "url": "https://raw.githubusercontent.com/facebookresearch/DiT/main/models.py",
        "purpose": "DiT latent patch processing",
    },
    {
        "group": "flashvsr",
        "name": "TCDecoder.py",
        "url": "https://raw.githubusercontent.com/OpenImagingLab/FlashVSR/main/examples/WanVSR/utils/TCDecoder.py",
        "purpose": "Tiny Conditional Decoder",
    },
    {
        "group": "flashvsr",
        "name": "utils.py",
        "url": "https://raw.githubusercontent.com/OpenImagingLab/FlashVSR/main/examples/WanVSR/utils/utils.py",
        "purpose": "LQ projection module",
    },
    {
        "group": "flashvsr",
        "name": "infer_flashvsr_v1.1_tiny.py",
        "url": "https://raw.githubusercontent.com/OpenImagingLab/FlashVSR/main/examples/WanVSR/infer_flashvsr_v1.1_tiny.py",
        "purpose": "Tiny-decoder inference wiring",
    },
    {
        "group": "flashvsr",
        "name": "infer_flashvsr_v1.1_full.py",
        "url": "https://raw.githubusercontent.com/OpenImagingLab/FlashVSR/main/examples/WanVSR/infer_flashvsr_v1.1_full.py",
        "purpose": "Full Wan VAE decoder inference wiring",
    },
    {
        "group": "flashvsr",
        "name": "wan_video_vae.py",
        "url": "https://raw.githubusercontent.com/OpenImagingLab/FlashVSR/main/diffsynth/models/wan_video_vae.py",
        "purpose": "Wan video VAE implementation used by FlashVSR",
    },
    {
        "group": "flashvsr",
        "name": "README.md",
        "url": "https://raw.githubusercontent.com/OpenImagingLab/FlashVSR/main/README.md",
        "purpose": "Official model, weights, dataset and runtime claims",
    },
    {
        "group": "wan",
        "name": "wan/modules/vae.py",
        "url": "https://raw.githubusercontent.com/Wan-Video/Wan2.1/main/wan/modules/vae.py",
        "purpose": "Official Wan VAE implementation",
    },
    {
        "group": "cogvideox",
        "name": "sat/vae_modules/cp_enc_dec.py",
        "url": "https://raw.githubusercontent.com/THUDM/CogVideo/main/sat/vae_modules/cp_enc_dec.py",
        "purpose": "CogVideoX causal VAE implementation",
    },
    {
        "group": "hunyuanvideo",
        "name": "hyvideo/vae/autoencoder_kl_causal_3d.py",
        "url": "https://raw.githubusercontent.com/Tencent-Hunyuan/HunyuanVideo/main/hyvideo/vae/autoencoder_kl_causal_3d.py",
        "purpose": "HunyuanVideo causal VAE implementation",
    },
]


EXTRA_DIRS = [
    ROOT / "figures" / "paper_figures",
    ROOT / "figures" / "explanatory",
    ROOT / "figures" / "review_crops",
    ROOT / "source_code",
    ROOT / "metadata" / "raw",
    ROOT / "metadata" / "evidence",
    ROOT / "report",
    ROOT / "rendered_report",
    ROOT / "text",
]


def ensure_directories():
    for path in [*CATEGORIES.values(), *EXTRA_DIRS]:
        path.mkdir(parents=True, exist_ok=True)
