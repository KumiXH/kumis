# DiT 编解码器研究资料库

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
