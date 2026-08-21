import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.enc_dec_library.config import ROOT


STYLE = """
<style>
  text { font-family: 'Microsoft YaHei', 'Noto Sans CJK SC', Arial, sans-serif; fill: #17212B; }
  .title { font-size: 32px; font-weight: 700; }
  .subtitle { font-size: 17px; fill: #4B5B66; }
  .year { font-size: 19px; font-weight: 700; fill: #B31B34; }
  .label { font-size: 16px; font-weight: 700; }
  .body { font-size: 14px; }
  .shape { font-size: 13px; fill: #394B56; }
  .small { font-size: 12px; fill: #52636E; }
  .node { rx: 7; ry: 7; stroke-width: 2; }
  .conv { fill: #D8EBF7; stroke: #1479AD; }
  .conditionBox { fill: #DFF3E9; stroke: #07845F; }
  .latent { fill: #EEE6F7; stroke: #8052A5; }
  .attention { fill: #FBE6C4; stroke: #DC8500; }
  .operation { fill: #EDF0F2; stroke: #687984; }
  .main { fill: none; stroke: #263238; stroke-width: 2.2; marker-end: url(#arrow); }
  .condition { fill: none; stroke: #07845F; stroke-width: 2.2; marker-end: url(#arrowGreen); }
  .residual { fill: none; stroke: #8052A5; stroke-width: 2; stroke-dasharray: 8 6; marker-end: url(#arrowPurple); }
  .axis { stroke: #AAB5BC; stroke-width: 3; }
</style>
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#263238"/></marker>
  <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#07845F"/></marker>
  <marker id="arrowPurple" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#8052A5"/></marker>
</defs>
"""


def svg_document(width, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#FFFFFF"/>
{STYLE}
{body}
</svg>'''


def multiline(x, y, lines, css="body", anchor="start", line_height=20):
    tspans = "".join(
        f'<tspan x="{x}" dy="{0 if i == 0 else line_height}">{line}</tspan>'
        for i, line in enumerate(lines)
    )
    return f'<text x="{x}" y="{y}" class="{css}" text-anchor="{anchor}">{tspans}</text>'


def timeline():
    events = [
        (2014, ["VAE"], ["连续概率潜空间", "ELBO: 重建 + KL"]),
        (2017, ["VQ-VAE"], ["离散码本", "重建 + codebook", "+ commitment"]),
        (2021, ["VQGAN"], ["感知/对抗式 tokenizer", "LPIPS + GAN 改善纹理"]),
        (2022, ["LDM"], ["冻结 f8 图像 VAE", "扩散进入低维 latent"]),
        (2023, ["DiT / MAGVIT"], ["Transformer latent 建模", "图像与视频路线分化"]),
        (2024, ["SD3 / TiTok", "MAGVIT-v2"], ["16ch、1D token、因果量化", "token 形状成为主变量"]),
        (2025, ["DC-AE / Video VAE"], ["CogVideoX / LTX", "Cosmos / Wan；高压缩与缓存"]),
        (2026, ["FlashVSR"], ["条件投影 + decoder-only", "LQ_proj_in / TCDecoder"]),
    ]
    width, height = 1500, 720
    x0, x1, y = 105, 1390, 365
    body = [
        '<text x="80" y="66" class="title">DiT 编解码器技术演进 / Encoder-Decoder Evolution</text>',
        '<text x="80" y="100" class="subtitle">从概率潜空间到高压缩因果视频 tokenizer，再到面向复原的条件投影与 decoder-only 适配</text>',
        '<text x="80" y="126" class="shape">[pixels / frames] -> [continuous or discrete latent] -> [DiT tokens] -> [pixels / frames]</text>',
        '<g id="main-flow" data-flow="top-to-bottom">',
        f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" class="axis"/>',
    ]
    step = (x1 - x0) / (len(events) - 1)
    for i, (year, model_lines, detail_lines) in enumerate(events):
        x = x0 + i * step
        top = i % 2 == 0
        box_y = 145 if top else 425
        box_h = 150
        body.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#B31B34"/>')
        body.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{box_y + (box_h if top else 0)}" stroke="#B7C1C8" stroke-width="2"/>')
        body.append(f'<rect x="{x-78}" y="{box_y}" width="156" height="{box_h}" class="node operation"/>')
        body.append(f'<text x="{x}" y="{box_y+30}" class="year" text-anchor="middle">{year}</text>')
        body.append(multiline(x, box_y+57, model_lines, "label", "middle", 19))
        detail_y = box_y + 92 + max(0, len(model_lines) - 1) * 13
        body.append(multiline(x, detail_y, detail_lines, "small", "middle", 18))
    body.append('</g>')
    return svg_document(width, height, "\n".join(body))


def tensor_flow():
    width, height = 1500, 900
    body = [
        '<text x="70" y="60" class="title">主流 DiT 编解码器张量流 / Tensor Flow</text>',
        '<text x="70" y="94" class="subtitle">图像与视频使用同一训练边界：先训练 tokenizer，再冻结 latent 接口训练 DiT；复原模型可额外注入观测条件。</text>',
        '<g id="main-flow" data-flow="top-to-bottom">',
        '<rect x="95" y="145" width="360" height="90" class="node conditionBox"/>',
        '<text x="275" y="178" class="label" text-anchor="middle">图像 Image</text>',
        '<text x="275" y="207" class="shape" text-anchor="middle">x: [B,3,H,W] = [B,3,1024,1024]</text>',
        '<rect x="95" y="290" width="360" height="105" class="node conv"/>',
        '<text x="275" y="326" class="label" text-anchor="middle">2D Encoder / Tokenizer</text>',
        '<text x="275" y="352" class="shape" text-anchor="middle">f8, C=4/16; or discrete K tokens</text>',
        '<text x="275" y="376" class="small" text-anchor="middle">SD-VAE / SD3 / FLUX / TiTok / DC-AE</text>',
        '<rect x="95" y="455" width="360" height="100" class="node latent"/>',
        '<text x="275" y="490" class="label" text-anchor="middle">Image latent</text>',
        '<text x="275" y="518" class="shape" text-anchor="middle">[B,C,H/8,W/8] -> patchify -> [B,N,D]</text>',
        '<rect x="95" y="620" width="360" height="105" class="node attention"/>',
        '<text x="275" y="657" class="label" text-anchor="middle">Image DiT / MM-DiT</text>',
        '<text x="275" y="684" class="shape" text-anchor="middle">denoise / flow-match latent tokens</text>',
        '<rect x="95" y="780" width="360" height="80" class="node conv"/>',
        '<text x="275" y="815" class="label" text-anchor="middle">Frozen Decoder -> RGB</text>',
        '<text x="275" y="841" class="shape" text-anchor="middle">[B,C,H/8,W/8] -> [B,3,H,W]</text>',
        '<path d="M275 235 L275 290" class="main"/>',
        '<path d="M275 395 L275 455" class="main"/>',
        '<path d="M275 555 L275 620" class="main"/>',
        '<path d="M275 725 L275 780" class="main"/>',
        '<rect x="650" y="145" width="400" height="90" class="node conditionBox"/>',
        '<text x="850" y="178" class="label" text-anchor="middle">视频 Video</text>',
        '<text x="850" y="207" class="shape" text-anchor="middle">v: [B,3,T,H,W] = [B,3,81,720,1280]</text>',
        '<rect x="650" y="290" width="400" height="105" class="node conv"/>',
        '<text x="850" y="326" class="label" text-anchor="middle">Causal 3D Encoder / Tokenizer</text>',
        '<text x="850" y="352" class="shape" text-anchor="middle">temporal x4/8, spatial x8/32; first-frame policy</text>',
        '<text x="850" y="376" class="small" text-anchor="middle">CogVideoX / WF-VAE / LTX / Cosmos / Wan</text>',
        '<rect x="650" y="455" width="400" height="100" class="node latent"/>',
        '<text x="850" y="490" class="label" text-anchor="middle">Video latent</text>',
        '<text x="850" y="518" class="shape" text-anchor="middle">[B,C,T/f_t,H/f_s,W/f_s] -> 3D patch tokens</text>',
        '<rect x="650" y="620" width="400" height="105" class="node attention"/>',
        '<text x="850" y="657" class="label" text-anchor="middle">Video DiT / Flow Transformer</text>',
        '<text x="850" y="684" class="shape" text-anchor="middle">causal/full attention, text and image conditions</text>',
        '<rect x="650" y="780" width="400" height="80" class="node conv"/>',
        '<text x="850" y="815" class="label" text-anchor="middle">Causal Decoder -> Video</text>',
        '<text x="850" y="841" class="shape" text-anchor="middle">stream/cache or chunked decode</text>',
        '<path d="M850 235 L850 290" class="main"/>',
        '<path d="M850 395 L850 455" class="main"/>',
        '<path d="M850 555 L850 620" class="main"/>',
        '<path d="M850 725 L850 780" class="main"/>',
        '</g>',
        '<rect x="1135" y="260" width="295" height="145" class="node conditionBox"/>',
        '<text x="1282" y="298" class="label" text-anchor="middle">复原观测条件</text>',
        '<text x="1282" y="324" class="small" text-anchor="middle">Restoration observation</text>',
        '<text x="1282" y="353" class="body" text-anchor="middle">LQ RGB / mask / metadata</text>',
        '<text x="1282" y="379" class="shape" text-anchor="middle">project -> latent-aligned feature</text>',
        '<path d="M1135 335 L1050 520" class="condition" data-route="right"/>',
        '<rect x="1135" y="610" width="295" height="145" class="node operation"/>',
        '<text x="1282" y="648" class="label" text-anchor="middle">训练边界</text>',
        '<text x="1282" y="675" class="body" text-anchor="middle">1. Tokenizer/VAE 预训练</text>',
        '<text x="1282" y="701" class="body" text-anchor="middle">2. 冻结 latent 训练 DiT</text>',
        '<text x="1282" y="727" class="body" text-anchor="middle">3. 任务适配 / decoder 替换</text>',
    ]
    return svg_document(width, height, "\n".join(body))


def flashvsr():
    width, height = 1500, 980
    body = [
        '<text x="70" y="58" class="title">FlashVSR 三类编解码模块关系 / Module Boundary</text>',
        '<text x="70" y="91" class="subtitle">LQ_proj_in 是条件投影，Wan Encoder/Decoder 是完整 VAE，TCDecoder 是 decoder-only 加速器。</text>',
        '<g id="main-flow" data-flow="top-to-bottom">',
        '<rect x="110" y="150" width="300" height="82" class="node conditionBox"/>',
        '<text x="260" y="181" class="label" text-anchor="middle">LR Video</text>',
        '<text x="260" y="207" class="shape" text-anchor="middle">[B,3,T,H,W]</text>',
        '<rect x="110" y="295" width="300" height="122" class="node conditionBox"/>',
        '<text x="260" y="329" class="label" text-anchor="middle">M1: LQ_proj_in</text>',
        '<text x="260" y="355" class="body" text-anchor="middle">Pixel rearrange + causal Conv3d</text>',
        '<text x="260" y="381" class="shape" text-anchor="middle">RGB observation -> DiT feature</text>',
        '<text x="260" y="403" class="small" text-anchor="middle">trainable in SR adaptation</text>',
        '<rect x="540" y="295" width="360" height="122" class="node latent"/>',
        '<text x="720" y="329" class="label" text-anchor="middle">Wan latent / Noise latent</text>',
        '<text x="720" y="355" class="shape" text-anchor="middle">[B,16,T/4,H/8,W/8]</text>',
        '<text x="720" y="381" class="body" text-anchor="middle">LQ feature is added/aligned here</text>',
        '<rect x="540" y="492" width="360" height="130" class="node attention"/>',
        '<text x="720" y="528" class="label" text-anchor="middle">Sparse-Causal Wan DiT</text>',
        '<text x="720" y="555" class="body" text-anchor="middle">Stage 1 FM -> Stage 2 sparse causal</text>',
        '<text x="720" y="582" class="body" text-anchor="middle">Stage 3 DMD one-step + reconstruction</text>',
        '<text x="720" y="606" class="small" text-anchor="middle">LoRA rank 384</text>',
        '<rect x="540" y="700" width="360" height="92" class="node latent"/>',
        '<text x="720" y="734" class="label" text-anchor="middle">Predicted HR latent</text>',
        '<text x="720" y="761" class="shape" text-anchor="middle">same Wan latent contract</text>',
        '<path d="M260 232 L260 295" class="main"/>',
        '<path d="M410 356 L540 356" class="condition" data-route="right"/>',
        '<path d="M720 417 L720 492" class="main"/>',
        '<path d="M720 622 L720 700" class="main"/>',
        '</g>',
        '<rect x="1030" y="145" width="350" height="120" class="node conv"/>',
        '<text x="1205" y="180" class="label" text-anchor="middle">Wan Encoder</text>',
        '<text x="1205" y="208" class="body" text-anchor="middle">完整 causal 3D VAE encoder</text>',
        '<text x="1205" y="234" class="small" text-anchor="middle">训练/教师路径；非 LQ_proj_in</text>',
        '<path d="M1030 205 L900 345" class="residual" data-route="left"/>',
        '<rect x="1010" y="440" width="390" height="135" class="node conv"/>',
        '<text x="1205" y="476" class="label" text-anchor="middle">M2: WanDecoder (Full)</text>',
        '<text x="1205" y="503" class="body" text-anchor="middle">完整 causal 3D VAE decoder</text>',
        '<text x="1205" y="529" class="body" text-anchor="middle">高质量教师与 Ours-Full 推理路径</text>',
        '<text x="1205" y="553" class="small" text-anchor="middle">论文分析约占 70% 推理时间</text>',
        '<rect x="1010" y="665" width="390" height="150" class="node conditionBox"/>',
        '<text x="1205" y="701" class="label" text-anchor="middle">M3: TCDecoder (Tiny)</text>',
        '<text x="1205" y="728" class="body" text-anchor="middle">latent + LR conditional decoder</text>',
        '<text x="1205" y="754" class="body" text-anchor="middle">PixelShuffle3d(4,8,8)</text>',
        '<text x="1205" y="780" class="small" text-anchor="middle">nearly 7x decoder speedup</text>',
        '<path d="M900 746 L1010 510" class="main"/>',
        '<path d="M900 746 L1010 740" class="main"/>',
        '<path d="M410 191 C980 190 920 735 1010 735" class="condition" data-route="right"/>',
        '<rect x="1010" y="865" width="390" height="80" class="node operation"/>',
        '<text x="1205" y="895" class="label" text-anchor="middle">TCDecoder training</text>',
        '<text x="1205" y="922" class="shape" text-anchor="middle">MSE + LPIPS to GT and WanDecoder output</text>',
        '<path d="M1205 815 L1205 865" class="main"/>',
        '<rect x="500" y="855" width="400" height="90" class="node conditionBox"/>',
        '<text x="700" y="889" class="label" text-anchor="middle">HR Video output</text>',
        '<text x="700" y="917" class="shape" text-anchor="middle">Full path or Tiny path, same pixel target</text>',
        '<path d="M1010 520 C920 520 940 895 900 900" class="main"/>',
        '<path d="M1010 740 C930 740 950 900 900 900" class="main"/>',
    ]
    return svg_document(width, height, "\n".join(body))


def main():
    output = ROOT / "figures" / "explanatory"
    output.mkdir(parents=True, exist_ok=True)
    diagrams = {
        "encoder_decoder_timeline.svg": timeline(),
        "image_video_tensor_flow.svg": tensor_flow(),
        "flashvsr_module_boundary.svg": flashvsr(),
    }
    for name, content in diagrams.items():
        (output / name).write_text(content, encoding="utf-8")
    print(json.dumps({"created": [str(output / name) for name in diagrams]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
