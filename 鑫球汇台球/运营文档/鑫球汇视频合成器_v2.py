#!/usr/bin/env python3
"""
鑫球汇视频合成器 v2.0
女性友好 · 新手友好 · 助教陪练风格
用Pillow画图，本地FFmpeg拼接，不依赖drawtext滤镜
"""

import asyncio
import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

# ============================================================
# ↓ 文案从这里改 ↓
# ============================================================

VIDEO_TITLE = "吴宜泽杀入世锦赛决赛-鑫球汇邀你看球"

SCENES = [
    {
        "text": "吴宜泽17比16绝杀艾伦！中国00后杀入斯诺克世锦赛决赛",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_07.jpg"),
    },
    {
        "text": "五一假期来鑫球汇，大屏看决赛直播，为中国加油",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_01.jpg"),
    },
    {
        "text": "秦州万达B1层，轻奢装修氛围感拉满，身临其境般体验",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_04.jpg"),
    },
    {
        "text": "美女助教全程陪打，边看球边打球，快乐加倍",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_06.jpg"),
    },
    {
        "text": "0基础也不用怕，小姐姐手把手教你，女性友好",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_03.jpg"),
    },
    {
        "text": "约上朋友来PK一局，感受斯诺克的极致魅力",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_05.jpg"),
    },
    {
        "text": "📍秦州万达B1层·鑫球汇 约球热线188-9398-9938",
        "image": os.path.expanduser("~/Desktop/鑫球汇图片素材/素材_02.jpg"),
    },
]

TTS_VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓女声，适合年轻化台球风格
MIN_DURATION = 3.0
WIDTH = 1080
HEIGHT = 1920
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")
# 增加配乐配置
BGM_URL = None  # 暂时不加BGM，简化流程先出片
BGM_FILE = None

# ============================================================
# 以上不用改
# ============================================================

# 字体路径
FONT_REGULAR = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Medium.ttc"

def get_color_scheme(index):
    """鑫球汇品牌色系：活力橙+深灰+金色"""
    schemes = [
        {"bg": (28, 28, 40), "accent": (255, 165, 0), "text": (255, 255, 255), "sub": (255, 200, 100)},  # 深灰+橙色
        {"bg": (38, 28, 20), "accent": (255, 140, 0), "text": (255, 255, 255), "sub": (255, 200, 150)},  # 暖褐+橙
        {"bg": (20, 28, 38), "accent": (255, 165, 0), "text": (255, 255, 255), "sub": (200, 220, 255)},  # 深蓝+橙
        {"bg": (40, 28, 28), "accent": (255, 185, 50), "text": (255, 255, 255), "sub": (255, 210, 180)},  # 深红+金
        {"bg": (28, 38, 28), "accent": (255, 175, 0), "text": (255, 255, 255), "sub": (180, 255, 180)},  # 深绿+橙
        {"bg": (28, 28, 40), "accent": (255, 160, 30), "text": (255, 255, 255), "sub": (255, 200, 100)},  # 重复首尾
        {"bg": (38, 28, 20), "accent": (255, 140, 0), "text": (255, 255, 255), "sub": (255, 210, 160)},
        {"bg": (20, 28, 38), "accent": (255, 180, 0), "text": (255, 255, 255), "sub": (200, 220, 255)},
    ]
    return schemes[index % len(schemes)]


def draw_billiard_pattern(draw, w, h, colors):
    """画台球风格的装饰元素"""
    cx, cy = w - 120, 120
    # 画台球（圆形）
    draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=(255, 255, 255), outline=None)
    # 台球上的数字
    try:
        font_small = ImageFont.truetype(FONT_REGULAR, 36)
        draw.text((cx - 10, cy - 20), "8", fill=(0, 0, 0), font=font_small)
    except Exception:
        pass

    # 底部装饰线条
    draw.rectangle([0, h - 6, w, h], fill=colors["accent"])
    draw.rectangle([0, 0, w, 6], fill=colors["accent"])

    # 角落里画小球杆装饰
    for x_pos, y_pos in [(80, h - 120), (80, 120)]:
        draw.ellipse([x_pos - 15, y_pos - 15, x_pos + 15, y_pos + 15],
                     fill=colors["accent"])


def create_scene_image(text, output_path, index, total, scene_image_path=None):
    """用Pillow生成一帧画面"""
    colors = get_color_scheme(index - 1)
    w, h = WIDTH, HEIGHT

    # 创建渐变背景
    img = Image.new("RGB", (w, h), colors["bg"])
    draw = ImageDraw.Draw(img)

    # 如果配置了图片素材，用图片做背景
    if scene_image_path is not None and os.path.exists(scene_image_path):
        try:
            bg_img = Image.open(scene_image_path).convert("RGB")
            # 裁剪或缩放填满 1080x1920
            bg_w, bg_h = bg_img.size
            scale = max(w / bg_w, h / bg_h)
            new_w, new_h = int(bg_w * scale), int(bg_h * scale)
            bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
            # 居中裁剪
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            bg_img = bg_img.crop((left, top, left + w, top + h))
            img = bg_img
        except Exception:
            pass  # 图片加载失败，回退纯色背景
    else:
        # 纯色背景（渐变）
        for r in range(max(w, h), 0, -200):
            alpha = max(0, min(255, 60 - r // 10))
            if alpha <= 0:
                break
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.ellipse(
                [w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r],
                fill=(colors["accent"][0], colors["accent"][1], colors["accent"][2], alpha)
            )
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    
    draw = ImageDraw.Draw(img)
    
    # 绘制装饰元素
    draw_billiard_pattern(draw, w, h, colors)
    
    # 半透明黑色遮罩（让文字更清晰）
    overlay_mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(overlay_mask)
    mask_draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 100))  # 半透明
    img = Image.alpha_composite(img.convert("RGBA"), overlay_mask).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 排版文案
    lines = []
    for paragraph in text.split("\n"):
        wrapped = textwrap.fill(paragraph, width=16)
        for line in wrapped.split("\n"):
            if line.strip():
                lines.append(line.strip())

    if not lines:
        lines = [text]

    # 主文案——大号字体居中
    try:
        font_main = ImageFont.truetype(FONT_REGULAR, 64)
        font_sub = ImageFont.truetype(FONT_REGULAR, 36)
        font_page = ImageFont.truetype(FONT_REGULAR, 28)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = font_main
        font_page = font_main

    # 计算文案总高度
    line_height = 90
    total_text_h = len(lines) * line_height
    start_y = (h - total_text_h) // 2 - 60  # 稍微上移给底部留空间

    # 画文案背景条（半透明）
    text_box_padding = 40
    text_box_y = start_y - text_box_padding
    text_box_h = total_text_h + text_box_padding * 2
    draw.rectangle(
        [60, text_box_y, w - 60, text_box_y + text_box_h],
        fill=(0, 0, 0, 100) if hasattr(draw, 'fill') else None,
        outline=None
    )
    # 用半透明叠加
    overlay2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw2 = ImageDraw.Draw(overlay2)
    overlay_draw2.rectangle(
        [60, text_box_y, w - 60, text_box_y + text_box_h],
        fill=(0, 0, 0, 140)
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay2).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 写文案
    for i, line in enumerate(lines):
        y_pos = start_y + i * line_height
        # 描边效果（画4次偏移再画主字）
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw.text((w // 2 + dx, y_pos + dy), line, fill=(0, 0, 0), font=font_main, anchor="mt")
        draw.text((w // 2, y_pos), line, fill=colors["text"], font=font_main, anchor="mt")

    # 页码（底部）
    draw.text((60, h - 60), f"{index}/{total}", fill=(200, 200, 200), font=font_page)

    # 顶部品牌
    draw.text((w // 2, 80), "🎱 鑫球汇台球俱乐部", fill=colors["accent"], font=font_sub, anchor="mt")

    # 保存
    img.save(output_path, "PNG")
    return True


async def generate_tts(text, output_path, voice):
    """生成配音，返回音频时长（秒）"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", output_path],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


async def main():
    print("=" * 55)
    print("  🎱 鑫球汇台球俱乐部 视频合成器 v2.0")
    print(f"  选题: {VIDEO_TITLE}")
    print("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="xinqiuhui_v2_")

    audio_files = []
    image_files = []
    durations = []

    n = len(SCENES)
    print(f"\n📝 共 {n} 段，开始生成配音和图片...\n")

    for i, scene in enumerate(SCENES):
        idx = i + 1
        short = scene["text"][:20] + ("..." if len(scene["text"]) > 20 else "")
        print(f"  [{idx}/{n}] {short}")

        # 1. 配音
        audio_path = os.path.join(temp_dir, f"audio_{idx:02d}.mp3")
        try:
            duration = await generate_tts(scene["text"], audio_path, TTS_VOICE)
            audio_files.append(audio_path)
            durations.append(duration)
            print(f"    ✓ 配音 {duration:.1f}s")
        except Exception as e:
            print(f"    ✗ 配音失败: {e}")
            return

        # 2. 图片
        img_path = os.path.join(temp_dir, f"img_{idx:02d}.png")
        try:
            create_scene_image(scene["text"], img_path, idx, n, scene_image_path=scene.get("image"))
            image_files.append(img_path)
            print(f"    ✓ 图片已生成")
        except Exception as e:
            print(f"    ✗ 图片生成失败: {e}")
            return

    print(f"\n🎬 逐段合成视频...")

    segment_files = []
    for i in range(n):
        dur = max(durations[i], MIN_DURATION)
        seg_path = os.path.join(temp_dir, f"seg_{i:02d}.mp4")
        segment_files.append(seg_path)

        # 用videotoolbox硬件编码加速
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_files[i],
            "-i", audio_files[i],
            "-t", str(dur),
            "-c:v", "h264_videotoolbox",
            "-pix_fmt", "yuv420p",
            "-b:v", "6M",
            "-vf",
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#1C1C28",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            seg_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)

        if r.returncode != 0:
            # 如果videotoolbox不可用，回退到libx264
            print(f"    ⚠ 硬件编码失败，回退到软件编码...")
            cmd[7] = "libx264"
            cmd[9] = "5M"
            r = subprocess.run(cmd, capture_output=True, text=True)

        if r.returncode != 0:
            print(f"    ✗ 第{i+1}段合成失败")
            print(f"    错误: {r.stderr[:300]}")
            return

        print(f"    ✓ 第{i+1}段 ({dur:.1f}s)")

    # 拼接所有段落
    print(f"\n📎 拼接最终视频...")
    concat_file = os.path.join(temp_dir, "segments.txt")
    with open(concat_file, "w") as f:
        for sp in segment_files:
            f.write(f"file '{sp}'\n")

    # 清理文件名中的特殊字符
    safe_title = "".join(c for c in VIDEO_TITLE if c.isalnum() or c in " _-（）").strip()
    output_path = os.path.join(OUTPUT_DIR, f"{safe_title}.mp4")

    r = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path
    ], capture_output=True, text=True)

    if r.returncode == 0:
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        total_dur = sum(max(d, MIN_DURATION) for d in durations)
        print(f"\n✅ 视频合成成功！")
        print(f"   路径: {output_path}")
        print(f"   时长: {total_dur:.1f}s")
        print(f"   大小: {size_mb:.1f}MB")
        print(f"   分辨率: {WIDTH}x{HEIGHT} (竖屏)")
        print(f"   配音: {TTS_VOICE}")
        print(f"\n📁 文件在: {OUTPUT_DIR}/")
    else:
        print(f"\n✗ 拼接失败: {r.stderr[:300]}")


if __name__ == "__main__":
    asyncio.run(main())
