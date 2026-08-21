import json
from pathlib import Path

from PIL import Image

from tools.enc_dec_library.config import ROOT


CROPS = {
    "vqgan_architecture": ("vqgan_page_3.png", (0.04, 0.02, 0.97, 0.55)),
    "ldm_perceptual_compression": ("ldm_page_2.png", (0.04, 0.02, 0.98, 0.61)),
    "dit_architecture": ("dit_page_3.png", (0.03, 0.02, 0.98, 0.66)),
    "sd3_mmdit_architecture": ("sd3_architecture_page_5.png", (0.03, 0.02, 0.98, 0.83)),
    "sd3_autoencoder_table": ("sd3_autoencoder_page_7.png", (0.03, 0.02, 0.98, 0.66)),
    "magvit_pipeline": ("magvit_page_3.png", (0.03, 0.02, 0.98, 0.64)),
    "wfvae_architecture": ("wfvae_architecture_page_3.png", (0.03, 0.02, 0.98, 0.62)),
    "wfvae_reconstruction": ("wfvae_results_page_6.png", (0.03, 0.02, 0.98, 0.72)),
    "flashvsr_training_pipeline": ("flashvsr_training_page_4.png", (0.03, 0.01, 0.98, 0.48)),
    "flashvsr_tcdecoder_pipeline": ("flashvsr_tcdecoder_page_5.png", (0.45, 0.31, 0.98, 0.65)),
    "flashvsr_local_attention": ("flashvsr_tcdecoder_page_5.png", (0.03, 0.01, 0.98, 0.34)),
    "flashvsr_qualitative_results": ("flashvsr_results_page_7.png", (0.02, 0.01, 0.99, 0.60)),
}


def main():
    source_dir = ROOT / "figures" / "paper_figures"
    output_dir = ROOT / "figures" / "paper_figures" / "crops"
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, (source_name, box) in CROPS.items():
        source = source_dir / source_name
        destination = output_dir / f"{name}.png"
        with Image.open(source) as image:
            width, height = image.size
            left, top, right, bottom = box
            crop_box = (
                int(width * left), int(height * top), int(width * right), int(height * bottom)
            )
            cropped = image.crop(crop_box)
            cropped.save(destination, optimize=True)
        records.append({
            "name": name,
            "source": str(source),
            "crop_fraction": box,
            "local_path": str(destination),
            "width": cropped.width,
            "height": cropped.height,
        })
    (ROOT / "metadata" / "paper_crop_manifest.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(records, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
