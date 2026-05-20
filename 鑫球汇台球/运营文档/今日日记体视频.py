#!/usr/bin/env python3
"""
鑫球汇视频合成器 v3.0 - 路线2：日记体
辞职开台球厅第8天 · 晓晓女声 · 暖色调
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

VIDEO_TITLE = "辞职开台球厅第8天-大叔组团来踢馆-鑫球汇"

IMAGE_DIR = os.path.expanduser("~/Desktop/鑫球汇图片素材")

SCENES = [
    {
        "text": "辞职开台球厅第8天\\\\n今天来了几个大叔\\\\n气势汹汹说要踢馆🎱",
        "img": "bg_01.png",
    },
    {
        "text": "一进门就喊：\\\\n老板来桌！\\\\n今天要打遍全场！💪",
        "img": "bg_02.png",
    },
    {
        "text": "我看他们装备挺专业\\\\n自带球杆和巧粉\\\\n一看就是老手",
        "img": "bg_03.png",
    },
    {
        "text": "开了张斯诺克台\\\\n大叔上来就是一杆清\\\\n打得真漂亮🎯",
        "img": "bg_04.png",
    },
    {
        "text": "本想上去切磋两局\\\\n看这架势还是算了\\\\n先看会儿再说😅",
        "img": "bg_05.png",
    },
    {
        "text": "大叔打了三小时\\\\n走的时候说：\\\\n小伙子这台子不错！",
        "img": "bg_06.png",
    },
    {
        "text": "还说下周带球友来\\\\n组个局打比赛\\\\n这波稳了🔥",
        "img": "bg_07.png",
    },
    {
        "text": "开店最开心的就是\\\\n遇到真正懂球的顾客\\\\n聊两句就能学到东西",
        "img": "bg_08.png",
    },
    {
        "text": "鑫球汇台球俱乐部\\\\n在天水秦州万达\\\\n欢迎各路高手来切磋！🎱",
        "img": "bg_09.png",
    },
]

TTS_VOICE = "zh-CN-XiaoxiaoNeural"
MIN_DURATION = 3.5
WIDTH = 1080
HEIGHT = 1920
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")

BGM_PATH = "/tmp/bgm_snooker.mp3"

# 持久化BGM路径
BGM_PERSISTENT = os.path.expanduser("~/Desktop/_鑫球汇/bgm_snooker.mp3")

FONT_REGULAR = "/System/Library/Fonts/STHeiti Medium.ttc"


def get_color_scheme(index):
    # 日记体：暖色调方案（深蓝金→深红→深绿→深紫→蓝青→暖褐金→深红→深绿→深蓝金）
    schemes = [
        {"bg": (28, 28, 40), "accent": (201, 169, 78), "text": (255, 255, 255), "sub": (255, 200, 100)},
        {"bg": (40, 20, 20), "accent": (220, 80, 60), "text": (255, 255, 255), "sub": (255, 150, 120)},
        {"bg": (20, 40, 25), "accent": (60, 200, 80), "text": (255, 255, 255), "sub": (140, 230, 150)},
        {"bg": (35, 20, 40), "accent": (180, 80, 220), "text": (255, 255, 255), "sub": (210, 150, 240)},
        {"bg": (20, 35, 45), "accent": (60, 180, 220), "text": (255, 255, 255), "sub": (140, 210, 240)},
        {"bg": (45, 30, 15), "accent": (220, 160, 60), "text": (255, 255, 255), "sub": (240, 200, 140)},
        {"bg": (40, 20, 20), "accent": (220, 80, 60), "text": (255, 255, 255), "sub": (255, 150, 120)},
        {"bg": (20, 40, 25), "accent": (60, 200, 80), "text": (255, 255, 255), "sub": (140, 230, 150)},
        {"bg": (28, 28, 40), "accent": (201, 169, 78), "text": (255, 255, 255), "sub": (255, 200, 100)},
    ]
    return schemes[index % len(schemes)]


def get_scene_image(scene, index):
    img_name = scene.get("img")
    if img_name:
        path = os.path.join(IMAGE_DIR, img_name)
        if os.path.exists(path):
            return path
    return None


def create_scene_image(text, output_path, index, total, scene_image_path=None):
    colors = get_color_scheme(index - 1)
    w, h = WIDTH, HEIGHT

    if scene_image_path is not None and os.path.exists(scene_image_path):
        try:
            bg_img = Image.open(scene_image_path).convert("RGB")
            bg_w, bg_h = bg_img.size
            if bg_w == w and bg_h == h:
                img = bg_img.copy()
            else:
                scale = max(w / bg_w, h / bg_h)
                new_w, new_h = int(bg_w * scale), int(bg_h * scale)
                bg_img = bg_img.resize((new_w, new_h), Image.LANCZOS)
                left = (new_w - w) // 2
                top = (new_h - h) // 2
                bg_img = bg_img.crop((left, top, left + w, top + h))
                img = bg_img
        except Exception as e:
            print(f"    ⚠ 图片加载失败: {e}")
            img = Image.new("RGB", (w, h), colors["bg"])
    else:
        img = Image.new("RGB", (w, h), colors["bg"])

    draw = ImageDraw.Draw(img)

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

    overlay2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay_draw2 = ImageDraw.Draw(overlay2)
    text_box_y = start_y - 40
    text_box_h = total_text_h + 80
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
    # 优先级：持久化路径 → /tmp/ → None
    if os.path.exists(BGM_PERSISTENT):
        return BGM_PERSISTENT
    if os.path.exists(BGM_PATH):
        return BGM_PATH
    for alt in ["/tmp/bgm_ambient.mp3", "/tmp/bgm_generated.mp3"]:
        if os.path.exists(alt):
            return alt
    return None


def mix_bgm(video_path, bgm_path, output_path, volume=0.15):
    if not bgm_path or not os.path.exists(bgm_path):
        import shutil
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
    import shutil
    shutil.copy2(video_path, output_path)
    return output_path


async def main():
    print("=" * 55)
    print("  🎱 鑫球汇视频合成器 v3.0 - 日记体路线")
    print(f"  选题: {VIDEO_TITLE}")
    print("=" * 55)

    print(f"\n  📸 加载配图...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="xinqiuhui_v3_")

    audio_files = []
    img_files = []
    durations = []

    n = len(SCENES)
    print(f"\n📝 共 {n} 段，生成配音和图片...\n")

    for i, scene in enumerate(SCENES):
        idx = i + 1
        short = scene["text"][:25].replace("\\n", " ") + ("..." if len(scene["text"]) > 25 else "")
        print(f"  [{idx}/{n}] {short}")

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
            bg_name = bg_path.split("/")[-1] if bg_path else "无配图"
            print(f"    ✓ 图片已生成 ({bg_name})")
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
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#1C1C28",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            seg_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
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
        print(f"\\n✅ 合成成功！（无BGM）")
        print(f"   时长: {total_dur:.1f}s / 大小: {size_mb:.1f}MB")

        bgm_file = get_bgm()
        if bgm_file:
            print(f"   找到BGM: {bgm_file}")
        else:
            print(f"   未找到BGM，跳过混音")

        bgm_volume = 0.15
        mix_bgm(output_no_bgm, bgm_file, output_path, volume=bgm_volume)

        if os.path.exists(output_path):
            final_mb = os.path.getsize(output_path) / 1024 / 1024
            total_sec = sum(max(d, MIN_DURATION) for d in durations)
            print(f"\\n🎉 最终视频完成！")
            print(f"   路径: {output_path}")
            print(f"   时长: {total_sec:.0f}s / {final_mb:.1f}MB")
            print(f"   配音: {TTS_VOICE}")
    else:
        print(f"\\n✗ 拼接失败: {r.stderr[:300]}")


if __name__ == "__main__":
    asyncio.run(main())
