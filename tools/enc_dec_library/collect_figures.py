import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image

from tools.enc_dec_library.config import ROOT


USER_AGENT = "ReadPaper-EncoderDecoder-Study/1.0 (academic research)"
POPLER = Path(r"C:\Users\xh932\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")


AR5IV_ASSETS = [
    ("titok_framework", "2406.07550", "framework_vertical.png"),
    ("titok_reconstruction", "2406.07550", "recon_vis_ditstyle.png"),
    ("dcae_architecture", "2410.10733", "dc_ae_detailed_arch.png"),
    ("dcae_compression_results", "2410.10733", "figure1_results.png"),
    ("magvit2_architecture", "2310.05737", "model_arch.png"),
    ("magvit2_reconstruction", "2310.05737", "reconstruction.png"),
    ("cogvideox_3dvae", "2408.06072", "images/3dvae_combined.jpg"),
    ("cogvideox_framepack", "2408.06072", "images/CogVideoX-framepacking-2.jpg"),
    ("cogvideox_caption_pipeline", "2408.06072", "images/pipeline.jpg"),
    ("vidtok_overview", "2412.13061", "overview.png"),
    ("vidtok_fps_ablation", "2412.13061", "imgs/results/fps8_fps3.png"),
    ("opensora_3dvae", "2412.20404", "sora13-vae.svg"),
    ("opensora_data_pipeline", "2412.20404", "open-sora-report-datapipeline.png"),
    ("ltx_denoising", "2501.00103", "assets/figures/denoising.png"),
    ("ltx_vae_encoder", "2501.00103", "assets/figures/vae_encoder.png"),
    ("ltx_vae_decoder", "2501.00103", "assets/figures/vae_decoder.png"),
    ("ltx_reconstruction_gan", "2501.00103", "assets/figures/compare_gan_results.png"),
    ("cosmos_tokenizer_architecture", "2501.03575", "fig_network_architecture.png"),
    ("cosmos_diffusion_decoder", "2501.03575", "diffusion_decoder_v2.png"),
    ("wan_vae_architecture", "2503.20314", "vae.png"),
    ("wan_vae_reconstruction", "2503.20314", "vae_visual.png"),
]


PDF_PAGES = [
    ("vqgan", ROOT / "papers/01_history_and_tokenizers/vqgan_2012.09841.pdf", 3),
    ("ldm", ROOT / "papers/01_history_and_tokenizers/ldm_2112.10752.pdf", 2),
    ("dit", ROOT / "papers/04_dit_training/dit_2212.09748.pdf", 3),
    ("sd3_architecture", ROOT / "papers/02_image_vae/sd3_2403.03206.pdf", 5),
    ("sd3_autoencoder", ROOT / "papers/02_image_vae/sd3_2403.03206.pdf", 7),
    ("magvit", ROOT / "papers/03_video_vae/magvit_2212.05199.pdf", 3),
    ("wfvae_architecture", ROOT / "papers/03_video_vae/wfvae_2411.17459.pdf", 3),
    ("wfvae_results", ROOT / "papers/03_video_vae/wfvae_2411.17459.pdf", 6),
    ("flashvsr_training", ROOT / "papers/05_flashvsr_case/flashvsr_2510.12747.pdf", 4),
    ("flashvsr_tcdecoder", ROOT / "papers/05_flashvsr_case/flashvsr_2510.12747.pdf", 5),
    ("flashvsr_results", ROOT / "papers/05_flashvsr_case/flashvsr_2510.12747.pdf", 7),
]


def download(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    incoming = destination.with_suffix(destination.suffix + ".part")
    if incoming.exists():
        incoming.unlink()
    subprocess.run(
        [
            r"C:\Windows\System32\curl.exe", "-L", "--fail", "--silent", "--show-error",
            "--connect-timeout", "10", "--max-time", "35", "--retry", "1",
            "-A", USER_AGENT, "-o", str(incoming), url,
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=45,
    )
    incoming.replace(destination)


def collect_ar5iv():
    output = ROOT / "figures" / "paper_figures"
    records = []
    for name, identifier, relative in AR5IV_ASSETS:
        suffix = Path(relative).suffix.lower()
        destination = output / f"{name}{suffix}"
        url = f"https://ar5iv.labs.arxiv.org/html/{identifier}/assets/{relative}"
        try:
            if not destination.exists() or destination.stat().st_size < 1000:
                download(url, destination)
            valid = destination.exists() and destination.stat().st_size > 1000
            error = ""
        except Exception as exc:
            valid = False
            error = str(exc)
        records.append({
            "name": name,
            "arxiv_id": identifier,
            "asset": relative,
            "local_path": str(destination),
            "valid": valid,
            "size": destination.stat().st_size if destination.exists() else 0,
            "error": error,
        })
        print(f"asset {name}: {valid}", flush=True)
    return records


def render_pdf_pages():
    output = ROOT / "figures" / "paper_figures"
    records = []
    for name, pdf, page in PDF_PAGES:
        destination = output / f"{name}_page_{page}.png"
        try:
            if not destination.exists() or destination.stat().st_size < 1000:
                subprocess.run(
                    [
                        str(POPLER), "-f", str(page), "-l", str(page), "-r", "170",
                        "-png", "-singlefile", str(pdf), str(destination.with_suffix("")),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            with Image.open(destination) as image:
                width, height = image.size
            valid = width > 500 and height > 500
            error = ""
        except Exception as exc:
            width = height = 0
            valid = False
            error = str(exc)
        records.append({
            "name": name,
            "paper": str(pdf),
            "page": page,
            "local_path": str(destination),
            "valid": valid,
            "width": width,
            "height": height,
            "error": error,
        })
        print(f"pdf page {name}: {valid}", flush=True)
    return records


def main():
    records = collect_ar5iv() + render_pdf_pages()
    (ROOT / "metadata" / "figure_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"figures_valid={sum(row['valid'] for row in records)}/{len(records)}")


if __name__ == "__main__":
    main()
