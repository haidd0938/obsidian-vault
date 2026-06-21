#!/usr/bin/env python3
"""
东盛建筑设计短视频合成器 v1.0
专为抖音号「东盛建筑」打造
一键合成：文案 + 配音 + 实景配图 = 建筑行业干货短视频

使用方法：
  1. 修改下方 SCENES 列表中的文案
  2. python3 ~/Desktop/东盛建筑视频合成器.py

首次使用会自动创建 ~/Desktop/东盛建筑视频/ 目录
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

import edge_tts

# ============================================================
# ↓ 你只需要改这里 ↓
# ============================================================

# 视频标题（显示在文件名上）
VIDEO_TITLE = "EPC模式的三个致命陷阱"

# 品牌信息（显示在视频顶部）
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 EPC总承包"

# 配音文案（每段对应一个场景）
SCENES = [
    {
        "text": "EPC总承包，听着高大上，但很多老板第一个工程就栽了。",
        "image": "",  # 留空 = 品牌色背景 + 大字幕
    },
    {
        "text": "第一个陷阱：设计阶段不控造价，施工时才发现超预算。\nEPC的核心是设计牵头，设计定下来，造价就定死了。",
        "image": "",
    },
    {
        "text": "第二个陷阱：勘察不到位，施工挖开发现地基不行。\n地下情况没摸清，后面全是变更和索赔，工期直接翻倍。",
        "image": "",
    },
    {
        "text": "第三个陷阱：设计施工两张皮，各管各的。\nEPC的最大优势就是设计与施工一体化，分开管就等于白做。",
        "image": "",
    },
    {
        "text": "东盛建筑，专注EPC模式，设计+勘察+施工一站式交付。\n从图纸到竣工，一个团队管到底，不甩锅、不扯皮。",
        "image": "",
    },
    {
        "text": "关注东盛建筑，每天一个行业干货，帮你避坑省钱。",
        "image": "",
    },
]

# 配音设置
TTS_VOICE = "zh-CN-YunjianNeural"  # 云健（稳重男声，适合建筑行业）
# 其他可选：
# zh-CN-XiaoxiaoNeural (晓晓-女声)
# zh-CN-YunxiNeural (云希-搞笑男声)
# zh-CN-YunjianNeural (云健-稳重男声)

# 每段保底时长（秒，配音较短时用）
MIN_DURATION = 4.0

# 视频分辨率
WIDTH = 1080
HEIGHT = 1920  # 竖屏 9:16，抖音标准

# 输出目录
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")

# ============================================================
# 以上不用改
# ============================================================

# 品牌色系（深蓝 + 金色，专业沉稳）
BG_COLOR = "0x0d1b2a"       # 深蓝黑背景
ACCENT_COLOR = "0xc9a94e"    # 金色强调
TITLE_COLOR = "white"


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


def create_text_image(text, output_path, index, total):
    """生成带专业排版的品牌色背景图"""
    # 按换行分割段落
    paragraphs = text.split("\n")
    all_lines = []
    for para in paragraphs:
        # 每段内按字数换行
        lines = []
        while para:
            if len(para) <= 14:
                lines.append(para)
                break
            cut = 14
            for i in range(14, max(10, 0), -1):
                if i < len(para) and para[i] in "，。！？、；：,.!?;:":
                    cut = i + 1
                    break
            lines.append(para[:cut].strip())
            para = para[cut:].strip()
        all_lines.append(("", lines))  # 空tag表示普通段落
    
    # 生成纯色背景
    bg_path = output_path.replace(".png", "_bg.png")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={BG_COLOR}:s={WIDTH}x{HEIGHT}:d=1",
        "-frames:v", "1",
        bg_path
    ], capture_output=True, text=True)

    # 构建drawtext滤镜
    filters = []
    
    # 顶部品牌名
    filters.append(
        f"drawtext=text='{BRAND_NAME}'"
        f":fontfile='/System/Library/Fonts/PingFang.ttc'"
        f":fontsize=30"
        f":fontcolor={ACCENT_COLOR.replace('0x', '')}@0.8"
        f":x=(w-text_w)/2"
        f":y=60"
    )
    
    # 品牌副标题
    filters.append(
        f"drawtext=text='{BRAND_SUBTITLE}'"
        f":fontfile='/System/Library/Fonts/PingFang.ttc'"
        f":fontsize=20"
        f":fontcolor=white@0.5"
        f":x=(w-text_w)/2"
        f":y=100"
    )

    # 主文案（居中排列）
    # 先计算所有行总高度
    para_spacing = 20  # 段落间距
    line_height = 75
    total_lines = sum(len(lines) for _, lines in all_lines)
    total_height = total_lines * line_height + (len(all_lines) - 1) * para_spacing
    start_y = HEIGHT // 2 - total_height // 2

    current_y = start_y
    # 如果是最后一段（品牌宣传或关注引导），用金色强调
    is_last = (index == total)
    for tag, lines in all_lines:
        for j, line in enumerate(lines):
            color = "yellow" if is_last else "white"
            filters.append(
                f"drawtext=text='{line}'"
                f":fontfile='/System/Library/SystemFonts/PingFang.ttc'"
                f":fontsize=48"
                f":fontcolor={color}"
                f":x=(w-text_w)/2"
                f":y={current_y}"
                f":shadowx=2:shadowy=2:shadowcolor=black@0.5"
            )
            current_y += line_height
        current_y += para_spacing

    # 底部页码
    filters.append(
        f"drawtext=text='{index}/{total}'"
        f":fontfile='/System/Library/Fonts/PingFang.ttc'"
        f":fontsize=24"
        f":fontcolor=white@0.3"
        f":x=(w-text_w)/2"
        f":y=h-60"
    )

    filter_str = ",".join(filters)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", bg_path,
        "-vf", filter_str,
        output_path
    ], capture_output=True, text=True)

    if not os.path.exists(output_path):
        import shutil
        shutil.copy(bg_path, output_path)


async def main():
    print("=" * 55)
    print(f"  🏗️  {BRAND_NAME} 短视频合成器 v1.0")
    print("  文案 + 配音 + 图片 = 短视频")
    print("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="dongsheng_")

    audio_files = []
    image_files = []
    durations = []

    n = len(SCENES)
    print(f"\n📝 共 {n} 段，开始生成配音和画面...\n")

    for i, scene in enumerate(SCENES):
        idx = i + 1
        text_short = scene["text"].replace("\n", " ")[:20] + ("..." if len(scene["text"]) > 20 else "")
        print(f"  [{idx}/{n}] {text_short}")

        # 配音
        audio_path = os.path.join(temp_dir, f"audio_{idx:02d}.mp3")
        duration = await generate_tts(scene["text"], audio_path, TTS_VOICE)
        audio_files.append(audio_path)
        durations.append(duration)
        print(f"    ✓ 配音 {duration:.1f}s")

        # 画面
        img_path = os.path.join(temp_dir, f"img_{idx:02d}.png")
        create_text_image(scene["text"], img_path, idx, n)
        image_files.append(img_path)

    print(f"\n🎬 逐段合成中...")

    segment_files = []
    for i in range(n):
        dur = max(durations[i], MIN_DURATION)
        seg_path = os.path.join(temp_dir, f"seg_{i:02d}.mp4")
        segment_files.append(seg_path)

        r = subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_files[i],
            "-i", audio_files[i],
            "-t", str(dur),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf",
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#0d1b2a",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            seg_path
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ✗ 第{i+1}段失败: {r.stderr[:200]}")
            return
        print(f"    ✓ 第{i+1}段 ({dur:.1f}s)")

    # 拼接
    concat_file = os.path.join(temp_dir, "segments.txt")
    with open(concat_file, "w") as f:
        for sp in segment_files:
            f.write(f"file '{sp}'\n")

    output_path = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
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
        print(f"   配音声线: {TTS_VOICE}")
        print(f"   品牌: {BRAND_NAME} - {BRAND_SUBTITLE}")
    else:
        print(f"\n✗ 拼接失败: {r.stderr[:300]}")

    print(f"\n📁 视频文件在: {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
