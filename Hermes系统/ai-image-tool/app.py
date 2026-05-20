#!/usr/bin/env python3
"""
AI 图像生成工具 - 极简 Web 界面
Intel MacBook Pro 轻量化方案 | 零成本 | 本地运行
"""
import os
import sys
import time
import torch
import gradio as gr
from diffusers import StableDiffusionPipeline

# ---------- 配置 ----------
MODEL_ID = "runwayml/stable-diffusion-v1-5"  # 通用风格，稳定
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/diffusers")
OUTPUT_DIR = os.path.expanduser("~/Desktop/ai-image-tool/outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- 加载模型 ----------
print("加载模型...")
pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_ID,
    cache_dir=CACHE_DIR,
    torch_dtype=torch.float32,
    safety_checker=None,
    requires_safety_checker=False,
)
# Intel Mac 无 GPU，用 CPU
device = "cpu"
pipe = pipe.to(device)
# 启用内存优化
pipe.enable_attention_slicing()
print("模型加载完成")

def generate(prompt, negative_prompt, steps, guidance, width, height):
    """生成图片"""
    start = time.time()
    try:
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            num_inference_steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
        ).images[0]

        elapsed = time.time() - start
        timestamp = int(start)
        filename = f"gen_{timestamp}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        image.save(filepath)

        status = f"生成完成！耗时 {elapsed:.1f} 秒 | 保存至: {filename}"
        return image, status
    except Exception as e:
        return None, f"生成失败: {str(e)}"


# ---------- 界面 ----------
with gr.Blocks(
    title="AI 图像生成",
    theme=gr.themes.Soft(),
    css="""
    .container { max-width: 900px; margin: auto; }
    .generate-btn { height: 80px; font-size: 20px !important; }
    """
) as demo:
    gr.Markdown(
        """
        # AI 图像生成 · 本地轻量化版
        > Intel Mac 免费运行 · 无需联网 · 零成本
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            prompt = gr.Textbox(
                label="提示词",
                placeholder="描述你想生成的画面...",
                lines=4,
            )
        with gr.Column(scale=1):
            neg = gr.Textbox(
                label="负面提示词（可选）",
                placeholder="low quality, blurry, ugly...",
                lines=2,
            )

    with gr.Row():
        with gr.Column(scale=1):
            steps = gr.Slider(minimum=10, maximum=50, value=25, step=1, label="采样步数")
        with gr.Column(scale=1):
            guidance = gr.Slider(minimum=1.0, maximum=20.0, value=7.5, step=0.5, label="引导尺度")
        with gr.Column(scale=1):
            width = gr.Dropdown(
                choices=[384, 512, 640, 768], value=512, label="宽度"
            )
        with gr.Column(scale=1):
            height = gr.Dropdown(
                choices=[384, 512, 640, 768], value=512, label="高度"
            )

    with gr.Row():
        btn = gr.Button("生成", variant="primary", scale=1, elem_classes="generate-btn")
        clear = gr.Button("清空", scale=0)

    output = gr.Image(label="生成结果", height=500)
    status = gr.Textbox(label="状态", interactive=False)

    btn.click(
        fn=generate,
        inputs=[prompt, neg, steps, guidance, width, height],
        outputs=[output, status],
    )
    clear.click(lambda: (None, "", "", 25, 7.5, 512, 512), outputs=[output, prompt, neg, steps, guidance, width, height])

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=8668,
        share=False,
        show_error=True,
    )
