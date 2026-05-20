#!/usr/bin/env python3
"""
鑫球汇视频合成器 v3.0 - 路线1：科普干货
Friday May 8, 2026
"""
import asyncio
import json
import os
import subprocess
import tempfile
import textwrap
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

VIDEO_TITLE = "台球厅潜规则-老板不会告诉你的7个秘密"

# 图片素材目录
IMAGE_DIR = os.path.expanduser("~/Desktop/鑫球汇图片素材")

SCENES = [
    {
        "text": "为什么你一进门\\\\n台球厅老板就热情招呼你？\\\\n这些秘密他从来没说过",
        "img": "bg_01.png",
    },
    {
        "text": "第一：黄金时段一桌难求\\\\n其实大部分台是空的\\\\n老板故意说满了让你排队",
        "img": "bg_02.png",
    },
    {
        "text": "第二：台球厅最赚钱的\\\\n根本不是台费\\\\n是饮料和小吃，利润翻三倍",
        "img": "bg_03.png",
    },
    {
        "text": "第三：高手都是凌晨来打球\\\\n人少安静没人催\\\\n老板还愿意打折",
        "img": "bg_04.png",
    },
    {
        "text": "第四：台呢多久换一次？\\\\n好球厅三个月就换\\\\n差球厅三年不换你说呢",
        "img": "bg_05.png",
    },
    {
        "text": "第五：助教不只是陪练\\\\n真正的高手助教\\\\n能帮你的球技提升两个档次",
        "img": "bg_06.png",
    },
    {
        "text": "来鑫球汇看看真章\\\\n秦州万达B1层\\\\n美女助教等你来战🎱",
        "img": "bg_07.png",
    },
]

TTS_VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓女声 - 科普路线专用
MIN_DURATION = 3.5
WIDTH = 1080
HEIGHT = 1920
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")

BGM_PATH = "/tmp/bgm_snooker.mp3"

FONT_REGULAR = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Medium.ttc"


def get_scene_image(scene, index):
    """获取场景指定的配图"""
    img_name = scene.get("img")
    if img_name:
        path = os.path.join(IMAGE_DIR, img_name)
        if os.path.exists(path):
            return path
    # 回退到本地图片
    for prefix in ["search_", "pexels_", "素材_"]:
        for idx in range(1, 20):
            for ext in [".jpg", ".png"]:
                fname = f"{prefix}{idx:02d}{ext}"
                path = os.path.join(IMAGE_DIR, fname)
                if os.path.exists(path):
                    return path
    return None


def get_color_scheme(index):
    schemes = [
        {"bg": (20, 28, 48), "accent": (255, 185, 55), "text": (255, 255, 255), "sub": (180, 210, 255)},  # 深蓝+金
        {"bg": (40, 28, 28), "accent": (255, 165, 0), "text": (255, 255, 255), "sub": (255, 200, 150)},  # 深红+橙
        {"bg": (28, 40, 28), "accent": (100, 200, 80), "text": (255, 255, 255), "sub": (180, 255, 180)},  # 深绿+亮绿
        {"bg": (48, 28, 48), "accent": (255, 130, 200), "text": (255, 255, 255), "sub": (255, 200, 220)},  # 紫+粉
        {"bg": (20, 40, 55), "accent": (80, 200, 255), "text": (255, 255, 255), "sub": (180, 220, 255)},  # 深海+青
        {"bg": (55, 40, 20), "accent": (255, 180, 60), "text": (255, 255, 255), "sub": (255, 220, 180)},  # 暖褐+金
        {"bg": (20, 28, 48), "accent": (255, 185, 55), "text": (255, 255, 255), "sub": (180, 210, 255)},  # 重复收尾
    ]
    return schemes[index % len(schemes)]


def draw_billiard_pattern(draw, w, h, colors):
    cx, cy = w - 120, 120
    draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=(255, 255, 255), outline=None)
    try:
        font_small = ImageFont.truetype(FONT_REGULAR, 36)
        draw.text((cx - 10, cy - 20), "8", fill=(0, 0, 0), font=font_small)
    except Exception:
        pass
    draw.rectangle([0, h - 6, w, h], fill=colors["accent"])
    draw.rectangle([0, 0, w, 6], fill=colors["accent"])
    for x_pos, y_pos in [(80, h - 120), (80, 120)]:
        draw.ellipse([x_pos - 15, y_pos - 15, x_pos + 15, y_pos + 15], fill=colors["accent"])


def create_scene_image(text, output_path, index, total, scene_image_path=None):
    colors = get_color_scheme(index - 1)
    w, h = WIDTH, HEIGHT
    draw_bg = True

    if scene_image_path is not None and os.path.exists(scene_image_path):
        try:
            bg_img = Image.open(scene_image_path).convert("RGB")
            bg_w, bg_h = bg_img.size
            if bg_w == w and bg_h == h:
                img = bg_img.copy()
                draw_bg = False
            else:
                scale = max(w / bg_w, h / bg_h)
                new_w, new_h = int(bg_w * scale), int(bg_h * scale)
                bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                bg_img = bg_img.crop((left, top, left + w, top + h))
                img = bg_img
                draw_bg = True
        except Exception as e:
            print(f"    ⚠ 图片加载失败: {e}，回退纯色")
            img = Image.new("RGB", (w, h), colors["bg"])
            draw_bg = True
    else:
        img = Image.new("RGB", (w, h), colors["bg"])
        draw_bg = True

    draw = ImageDraw.Draw(img)
    if draw_bg:
        draw_billiard_pattern(draw, w, h, colors)

    # 半透明黑色遮罩
    overlay_mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(overlay_mask)
    mask_draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay_mask).convert("RGB")
    draw = ImageDraw.Draw(img)

    lines = []
    for paragraph in text.split("\\n"):
        wrapped = textwrap.fill(paragraph, width=16)
        for line in wrapped.split("\\n"):
            if line.strip():
                lines.append(line.strip())
    if not lines:
        lines = [text]

    try:
        font_main = ImageFont.truetype(FONT_REGULAR, 64)
        font_sub = ImageFont.truetype(FONT_REGULAR, 36)
        font_page = ImageFont.truetype(FONT_REGULAR, 28)
    except Exception:
        font_main = ImageFont.load_default()
        font_sub = font_main
        font_page = font_main

    line_height = 90
    total_text_h = len(lines) * line_height
    start_y = (h - total_text_h) // 2 - 60

    text_box_padding = 40
    text_box_y = start_y - text_box_padding
    text_box_h = total_text_h + text_box_padding * 2

    overlay2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw2 = ImageDraw.Draw(overlay2)
    overlay_draw2.rectangle([60, text_box_y, w - 60, text_box_y + text_box_h], fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img.convert("RGBA"), overlay2).convert("RGB")
    draw = ImageDraw.Draw(img)

    for i, line in enumerate(lines):
        y_pos = start_y + i * line_height
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            draw.text((w // 2 + dx, y_pos + dy), line, fill=(0, 0, 0), font=font_main, anchor="mt")
        draw.text((w // 2, y_pos), line, fill=colors["text"], font=font_main, anchor="mt")

    draw.text((60, h - 60), f"{index}/{total}", fill=(200, 200, 200), font=font_page)
    draw.text((w // 2, 80), "🎱 鑫球汇台球俱乐部", fill=colors["accent"], font=font_sub, anchor="mt")

    img.save(output_path, "PNG")
    return True


async def generate_tts(text, output_path, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", output_path],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def get_bgm():
    if os.path.exists(BGM_PATH):
        return BGM_PATH
    for alt in ["/tmp/bgm_ambient.mp3", "/tmp/bgm_generated.mp3"]:
        if os.path.exists(alt):
            return alt
    return None


def mix_bgm(video_path, bgm_path, output_path, volume=0.15):
    if not bgm_path or not os.path.exists(bgm_path):
        shutil.copy2(video_path, output_path)
        return output_path
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", bgm_path,
        "-filter_complex",
        f"[1:a]volume={volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first",
        "-c:v", "copy",
        output_path
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        return output_path
    else:
        shutil.copy2(video_path, output_path)
        return output_path


async def main():
    print("=" * 55)
    print("  🎱 鑫球汇视频合成器 v3.0")
    print(f"  路线: 科普干货 (周五)")
    print(f"  选题: {VIDEO_TITLE}")
    print("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="xinqiuhui_route1_")

    audio_files = []
    img_files = []
    durations = []

    n = len(SCENES)
    print(f"\n📝 共 {n} 段，生成配音和图片...\n")

    for i, scene in enumerate(SCENES):
        idx = i + 1
        short = scene["text"][:25].replace("\\n", " ")
        print(f"  [{idx}/{n}] {short}...")

        audio_path = os.path.join(temp_dir, f"audio_{idx:02d}.mp3")
        try:
            duration = await generate_tts(scene["text"], audio_path, TTS_VOICE)
            audio_files.append(audio_path)
            durations.append(duration)
            print(f"    ✓ 配音 {duration:.1f}s")
        except Exception as e:
            print(f"    ✗ 配音失败: {e}")
            return

        img_path = os.path.join(temp_dir, f"img_{idx:02d}.png")
        try:
            bg_path = get_scene_image(scene, i)
            create_scene_image(scene["text"], img_path, idx, n, scene_image_path=bg_path)
            img_files.append(img_path)
            print(f"    ✓ 图片已生成 (bg: {bg_path.split('/')[-1] if bg_path else '无配图'})")
        except Exception as e:
            print(f"    ✗ 图片生成失败: {e}")
            return

    print(f"\n🎬 逐段合成...")
    segment_files = []
    for i in range(n):
        dur = max(durations[i], MIN_DURATION)
        seg_path = os.path.join(temp_dir, f"seg_{i:02d}.mp4")
        segment_files.append(seg_path)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_files[i],
            "-i", audio_files[i],
            "-t", str(dur),
            "-c:v", "h264_videotoolbox",
            "-pix_fmt", "yuv420p",
            "-b:v", "6M",
            "-vf",
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#141C30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            seg_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ⚠ 硬件编码失败，回退软件编码...")
            cmd[7] = "libx264"
            cmd[9] = "5M"
            r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ✗ 第{i+1}段失败: {r.stderr[:200]}")
            return
        print(f"    ✓ 第{i+1}段 ({dur:.1f}s)")

    print(f"\n📎 拼接...")
    concat_file = os.path.join(temp_dir, "segments.txt")
    with open(concat_file, "w") as f:
        for sp in segment_files:
            f.write(f"file '{sp}'\n")

    safe_title = "".join(c for c in VIDEO_TITLE if c.isalnum() or c in " _-（）").strip()
    output_no_bgm = os.path.join(OUTPUT_DIR, f"{safe_title}_no_bgm.mp4")
    output_path = os.path.join(OUTPUT_DIR, f"{safe_title}.mp4")

    r = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_no_bgm
    ], capture_output=True, text=True)

    if r.returncode == 0:
        size_mb = os.path.getsize(output_no_bgm) / 1024 / 1024
        total_dur = sum(max(d, MIN_DURATION) for d in durations)
        print(f"\n✅ 合成成功！（无BGM）")
        print(f"   时长: {total_dur:.1f}s / 大小: {size_mb:.1f}MB")

        bgm_file = get_bgm()
        mix_bgm(output_no_bgm, bgm_file, output_path, volume=0.15)

        if os.path.exists(output_path):
            final_mb = os.path.getsize(output_path) / 1024 / 1024
            total_sec = sum(max(d, MIN_DURATION) for d in durations)
            print(f"\n🎉 最终视频完成！")
            print(f"   路径: {output_path}")
            print(f"   时长: {total_sec:.0f}s / {final_mb:.1f}MB")
            print(f"   配音: {TTS_VOICE}")
            print(f"   分辨率: {WIDTH}x{HEIGHT} 竖屏")
            return output_path, total_sec, final_mb
    else:
        print(f"\n✗ 拼接失败: {r.stderr[:300]}")
        return None, 0, 0


if __name__ == "__main__":
    result = asyncio.run(main())
    if result and result[0]:
        print(f"\n✅ 最终输出: {result[0]}")
