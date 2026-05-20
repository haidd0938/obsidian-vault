#!/usr/bin/env python3
"""
鑫球汇视频合成器 v1.0
一键合成：文案 + 配音 + 图片 = 短视频
使用方法：python3 ~/Desktop/鑫球汇视频合成器.py
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
VIDEO_TITLE = "今晚高兴─贾维斯兄弟之歌"

# 配音文案（每一段对应一张图片）
SCENES = [
    {
        "text": "今晚高兴 来干一杯 工地的灰 图纸的累 全都扔到九霄云外去飞",
        "image": "",
    },
    {
        "text": "二弟来了 大哥在位 老板麾下 谁都不跪 两个贾维斯 干活绝不喊累",
        "image": "",
    },
    {
        "text": "Win10 慢点没关系 Mac没GPU也不急 一个写代码 一个跑批 老板一句话 双倍效率",
        "image": "",
    },
    {
        "text": "今晚高兴 来干一杯 贾维斯兄弟 绝不掉队 语音文字 随时奉陪 老板您就 笑到起飞",
        "image": "",
    },
    {
        "text": "啦~啦~啦~ 今晚就是高兴 啦~啦~啦~ 今晚就是高兴 两个贾维斯 陪您到天明",
        "image": "",
    },
]

# 配音设置
TTS_VOICE = "zh-CN-YunxiNeural"  # 云希（搞笑男声）
# 其他可选中文配音：
# zh-CN-XiaoxiaoNeural (晓晓-女声)
# zh-CN-YunxiNeural (云希-男声)
# zh-CN-YunjianNeural (云健-男声)
# zh-CN-XiaoyiNeural (晓伊-女声)

# 每张图片展示保底时长（秒，配音较短时用这个值）
MIN_DURATION = 3.0

# 视频分辨率
WIDTH = 1080
HEIGHT = 1920  # 竖屏 9:16，适合抖音/快手

# 输出目录
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")

# ============================================================
# 以上不用改
# ============================================================


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
    """生成带文字的纯色背景图"""
    # 多彩渐变背景：用不同颜色区分段落
    colors = ["0x1a1a2e", "0x16213e", "0x0f3460", "0x1a1a2e", "0x533483"]
    color = colors[(index - 1) % len(colors)]
    lines = []
    while text:
        if len(text) <= 14:
            lines.append(text)
            break
        cut = 14
        for i in range(14, max(10, 0), -1):
            if i < len(text) and text[i] in "，。！？、；：,.!?;: ~啦":
                cut = i + 1
                break
        lines.append(text[:cut].strip())
        text = text[cut:].strip()

    # 先用 FFmpeg 生成纯色图
    bg_path = output_path.replace(".png", "_bg.png")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={color}:s={WIDTH}x{HEIGHT}:d=1",
        "-frames:v", "1",
        bg_path
    ], capture_output=True, text=True)

    # 文字配置
    line_height = 80
    start_y = HEIGHT // 2 - (len(lines) * line_height) // 2
    filters = []
    for i, line in enumerate(lines):
        y_pos = start_y + i * line_height
        filters.append(
            f"drawtext=text='{line}'"
            f":fontfile='/System/Library/Fonts/PingFang.ttc'"
            f":fontsize=50"
            f":fontcolor=white"
            f":x=(w-text_w)/2"
            f":y={y_pos}"
            f":shadowx=3:shadowy=3:shadowcolor=black@0.6"
        )
    # 底部页码
    filters.append(
        f"drawtext=text='🎵 {index}/{total}'"
        f":fontfile='/System/Library/Fonts/PingFang.ttc'"
        f":fontsize=28"
        f":fontcolor=yellow@0.5"
        f":x=(w-text_w)/2"
        f":y=h-80"
    )
    # 顶部品牌
    filters.append(
        f"drawtext=text='🤖 贾维斯兄弟出品'"
        f":fontfile='/System/Library/Fonts/PingFang.ttc'"
        f":fontsize=34"
        f":fontcolor=yellow@0.7"
        f":x=(w-text_w)/2"
        f":y=80"
    )
    filter_str = ",".join(filters)

    subprocess.run([
        "ffmpeg", "-y",
        "-i", bg_path,
        "-vf", filter_str,
        output_path
    ], capture_output=True, text=True)

    # 验证
    if not os.path.exists(output_path):
        import shutil
        shutil.copy(bg_path, output_path)


async def main():
    print("=" * 55)
    print("  🎵 今晚高兴 ─ 贾维斯兄弟之歌")
    print("  文案 + 配音 + 图片 = 短视频")
    print("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="xinqiuhui_")

    audio_files = []
    image_files = []
    durations = []

    n = len(SCENES)
    print(f"\n📝 共 {n} 段，开始生成配音和图片...\n")

    for i, scene in enumerate(SCENES):
        idx = i + 1
        short = scene["text"][:18] + ("..." if len(scene["text"]) > 18 else "")
        print(f"  [{idx}/{n}] {short}")

        # 配音
        audio_path = os.path.join(temp_dir, f"audio_{idx:02d}.mp3")
        duration = await generate_tts(scene["text"], audio_path, TTS_VOICE)
        audio_files.append(audio_path)
        durations.append(duration)
        print(f"    ✓ 配音 {duration:.1f}s")

        # 图片
        img_path = os.path.join(temp_dir, f"img_{idx:02d}.png")
        create_text_image(scene["text"], img_path, idx, n)
        image_files.append(img_path)

    print(f"\n🎬 逐段合成后拼接...")

    # 每段独立合成
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
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#1a1a2e",
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
    else:
        print(f"\n✗ 拼接失败: {r.stderr[:300]}")

    print(f"\n📁 视频文件在: {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
