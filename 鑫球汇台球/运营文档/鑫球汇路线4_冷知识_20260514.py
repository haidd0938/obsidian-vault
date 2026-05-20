#!/usr/bin/env python3
"""
鑫球汇视频合成器 v3.0 - 冷知识路线4：台球高手才懂的10个冷知识
快节奏 · 云扬男声 · bg装饰背景
Route 4: 冷知识信息搬运 (Thursday 2026-05-14)
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

VIDEO_TITLE = "台球高手才懂的10个冷知识-鑫球汇"

# 图片素材目录
IMAGE_DIR = os.path.expanduser("~/Desktop/鑫球汇图片素材")

SCENES = [
    {
        "text": "打台球这么多年\\\\n这10个冷知识你知道几个？",
        "img": "bg_01.png",
    },
    {
        "text": "第一：斯诺克147满分杆\\\\n历史上只有200多次\\\\n比中彩票还难",
        "img": "bg_02.png",
    },
    {
        "text": "第二：台球桌的台呢\\\\n其实就是羊毛做的\\\\n一张桌子的呢料要三只羊的毛",
        "img": "bg_03.png",
    },
    {
        "text": "第三：亨得利退役前\\\\n练习时连续打了\\\\n26杆过百 恐怖如斯",
        "img": "bg_04.png",
    },
    {
        "text": "第四：中式八球的球桌\\\\n比斯诺克小一半\\\\n但袋口反而更窄 更难进",
        "img": "bg_05.png",
    },
    {
        "text": "第五：台球杆并不是越直越好\\\\n顶级手工杆都有\\\\n微妙的弧线",
        "img": "bg_06.png",
    },
    {
        "text": "第六：九球比赛时\\\\n选手开球力量可达\\\\n30公里每小时",
        "img": "bg_07.png",
    },
    {
        "text": "第七：丁俊晖8岁开始打球\\\\n15岁就拿亚洲冠军\\\\n天赋型选手",
        "img": "bg_08.png",
    },
    {
        "text": "第八：台球最远的一杆球\\\\n吉尼斯纪录是93米\\\\n在特制长桌上完成的",
        "img": "bg_09.png",
    },
    {
        "text": "第九：皮头的弧度差异\\\\n只有0.5毫米\\\\n但准度差一个量级",
        "img": "bg_01.png",
    },
    {
        "text": "第十：鑫球汇比赛级球桌\\\\n台呢每月更换一次\\\\n在这个城市找不出第二家",
        "img": "bg_02.png",
    },
    {
        "text": "关注鑫球汇\\\\n每天一个台球冷知识\\\\n📍秦州万达B1层\\\\n热线188-9398-9938🎱",
        "img": "bg_03.png",
    },
]

TTS_VOICE = "zh-CN-YunyangNeural"
MIN_DURATION = 3.5
WIDTH = 1080
HEIGHT = 1920
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")

BGM_PATH = "/tmp/bgm_snooker.mp3"

FONT_REGULAR = "/System/Library/Fonts/STHeiti Medium.ttc"


def get_scene_image(scene, index):
    img_name = scene.get("img")
    if img_name:
        path = os.path.join(IMAGE_DIR, img_name)
        if os.path.exists(path):
            return path
    fallback = os.path.join(IMAGE_DIR, f"search_{index+1:02d}.jpg")
    if os.path.exists(fallback):
        return fallback
    return None


def get_color_scheme(index):
    schemes = [
        {"bg": (28, 28, 40), "accent": (255, 165, 0), "text": (255, 255, 255), "sub": (255, 200, 100)},
        {"bg": (40, 20, 40), "accent": (255, 100, 200), "text": (255, 255, 255), "sub": (255, 180, 220)},
        {"bg": (20, 40, 50), "accent": (80, 200, 255), "text": (255, 255, 255), "sub": (180, 230, 255)},
        {"bg": (45, 30, 15), "accent": (255, 180, 60), "text": (255, 255, 255), "sub": (255, 210, 150)},
        {"bg": (15, 45, 20), "accent": (80, 255, 100), "text": (255, 255, 255), "sub": (150, 255, 170)},
        {"bg": (45, 20, 40), "accent": (255, 80, 200), "text": (255, 255, 255), "sub": (255, 150, 220)},
        {"bg": (40, 40, 15), "accent": (255, 215, 0), "text": (255, 255, 255), "sub": (255, 230, 100)},
        {"bg": (20, 40, 20), "accent": (180, 255, 50), "text": (255, 255, 255), "sub": (200, 255, 120)},
        {"bg": (28, 28, 40), "accent": (255, 165, 0), "text": (255, 255, 255), "sub": (255, 200, 100)},
        {"bg": (40, 20, 40), "accent": (255, 100, 200), "text": (255, 255, 255), "sub": (255, 180, 220)},
        {"bg": (20, 40, 50), "accent": (80, 200, 255), "text": (255, 255, 255), "sub": (180, 230, 255)},
        {"bg": (45, 30, 15), "accent": (255, 180, 60), "text": (255, 255, 255), "sub": (255, 210, 150)},
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
            print(f"    ⚠ 图片加载失败: {e}，回退纯色")
            img = Image.new("RGB", (w, h), colors["bg"])
    else:
        img = Image.new("RGB", (w, h), colors["bg"])

    draw = ImageDraw.Draw(img)

    # 半透明黑色遮罩
    overlay_mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mask_draw = ImageDraw.Draw(overlay_mask)
    mask_draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay_mask).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 台球装饰元素
    draw_billiard_pattern(draw, w, h, colors)

    lines = []
    for paragraph in text.split("\n"):
        wrapped = textwrap.fill(paragraph, width=16)
        for line in wrapped.split("\n"):
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
    if os.path.exists(BGM_PATH) and os.path.getsize(BGM_PATH) > 1000:
        return BGM_PATH
    for alt in ["/tmp/bgm_ambient.mp3", "/tmp/bgm_generated.mp3"]:
        if os.path.exists(alt) and os.path.getsize(alt) > 1000:
            return alt
    return None


def mix_bgm(video_path, bgm_path, output_path, volume=0.15):
    if not bgm_path or not os.path.exists(bgm_path):
        print("    ⚠ BGM文件不存在，跳过BGM叠加")
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
        print(f"    ⚠ BGM叠加失败: {r.stderr[:200]}，跳过BGM")
        shutil.copy2(video_path, output_path)
        return output_path


async def main():
    print("=" * 55)
    print("  🎱 鑫球汇视频合成器 v3.0 - 冷知识篇")
    print(f"  选题: {VIDEO_TITLE}")
    print("  路线: 冷知识信息搬运 (路线4)")
    print("  日期: 2026-05-14 (周四)")
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
        short = scene["text"][:25].replace("\n", " ") + ("..." if len(scene["text"]) > 25 else "")
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
            print(f"    bg: {bg_path.split('/')[-1] if bg_path else '无配图'}")
            create_scene_image(scene["text"], img_path, idx, n, scene_image_path=bg_path)
            img_files.append(img_path)
            print(f"    ✓ 图片已生成")
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
        print(f"\n✅ 合成成功！（无BGM）")
        print(f"   时长: {total_dur:.1f}s / 大小: {size_mb:.1f}MB")

        bgm_file = get_bgm()
        if bgm_file:
            print(f"\n🎵 叠加BGM...")
            mix_bgm(output_no_bgm, bgm_file, output_path, volume=0.15)
        else:
            print(f"\n⚠ BGM未找到，直接使用无BGM版本")
            shutil.copy2(output_no_bgm, output_path)

        if os.path.exists(output_path):
            final_mb = os.path.getsize(output_path) / 1024 / 1024
            total_sec = sum(max(d, MIN_DURATION) for d in durations)
            print(f"\n🎉 最终视频完成！")
            print(f"   路径: {output_path}")
            print(f"   时长: {total_sec:.0f}s / {final_mb:.1f}MB")
            print(f"   配音: {TTS_VOICE}")
    else:
        print(f"\n✗ 拼接失败: {r.stderr[:300]}")


if __name__ == "__main__":
    asyncio.run(main())
