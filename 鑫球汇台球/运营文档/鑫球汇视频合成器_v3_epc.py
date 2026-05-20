#!/usr/bin/env python3
"""
鑫球汇视频合成器 v3.0
女性友好 · 新手友好 · 助教陪练风格
用Pillow画图，本地FFmpeg拼接，不依赖drawtext滤镜
Re-synthesized with real snooker images + BGM
"""

import asyncio
import json
import os
import subprocess
import tempfile
import textwrap
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

# ============================================================
# ↓ 文案从这里改 ↓
# ============================================================

IMAGE_DIR = os.path.expanduser("~/Desktop/东盛建筑视频/素材图片")

VIDEO_TITLE = "14.29GW一季度风电EPC大爆发-东盛建筑"

# 7 scenes about 2026 Q1 wind power EPC market
SCENES = [
    {
        "text": "14.29GW！这是2026年一季度中国风电EPC市场的总装机量。你参与了吗？",
        "image": os.path.join(IMAGE_DIR, "scene_01.png"),
    },
    {
        "text": "海上风电EPC价格每千瓦605到7500元，差距十倍。市场分层越来越明显。",
        "image": os.path.join(IMAGE_DIR, "scene_02.png"),
    },
    {
        "text": "中国能建广东院、中建三局领跑榜单。国字头吃肉，民企还有机会吗？",
        "image": os.path.join(IMAGE_DIR, "scene_03.png"),
    },
    {
        "text": "有！设计施工一体化才是突破口。EPC模式的核心竞争力，就是把分包的蛋糕自己做。",
        "image": os.path.join(IMAGE_DIR, "scene_04.png"),
    },
    {
        "text": "风电EPC要求设计院懂施工、施工方懂设计。传统的设计施工两张皮，玩不转了。",
        "image": os.path.join(IMAGE_DIR, "scene_05.png"),
    },
    {
        "text": "东盛建筑设计，深耕EPC总承包领域，从勘察到设计到施工，一站式交付。",
        "image": os.path.join(IMAGE_DIR, "scene_06.png"),
    },
    {
        "text": "风电+EPC是未来五年的黄金赛道。关注东盛建筑，每天一个行业干货，帮你抓住风口。",
        "image": os.path.join(IMAGE_DIR, "scene_01.png"),
    },
]

TTS_VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓女声
MIN_DURATION = 3.0
WIDTH = 1080
HEIGHT = 1920
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")

# No BGM by default — download_bgm will check for files silently
BGM_PATH = None

# ============================================================
# 以上不用改
# ============================================================

# 字体路径
FONT_REGULAR = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Medium.ttc"


def get_color_scheme(index):
    """东盛建筑品牌色系：深蓝+金色+白"""
    schemes = [
        {"bg": (13, 27, 42), "accent": (201, 169, 78), "text": (255, 255, 255), "sub": (201, 169, 78)},   # 深蓝黑+金色
        {"bg": (20, 32, 48), "accent": (180, 155, 60), "text": (255, 255, 255), "sub": (200, 220, 255)},  # 深蓝+暗金
        {"bg": (10, 22, 36), "accent": (201, 169, 78), "text": (255, 255, 255), "sub": (255, 200, 100)},  # 更深蓝+金
        {"bg": (16, 30, 44), "accent": (190, 160, 70), "text": (255, 255, 255), "sub": (180, 210, 255)},  # 深蓝灰+金
        {"bg": (13, 27, 42), "accent": (201, 169, 78), "text": (255, 255, 255), "sub": (200, 220, 255)},  # 重复
        {"bg": (20, 32, 48), "accent": (180, 155, 60), "text": (255, 255, 255), "sub": (255, 200, 100)},
        {"bg": (10, 22, 36), "accent": (201, 169, 78), "text": (255, 255, 255), "sub": (180, 210, 255)},
        {"bg": (16, 30, 44), "accent": (190, 160, 70), "text": (255, 255, 255), "sub": (200, 220, 255)},
    ]
    return schemes[index % len(schemes)]


def draw_construction_pattern(draw, w, h, colors):
    """画建筑行业风格的装饰元素"""
    # 顶部金色细线
    draw.rectangle([0, 0, w, 5], fill=colors["accent"])
    # 底部金色细线
    draw.rectangle([0, h-4, w, h-4], fill=colors["accent"])

    # 左上角建筑方块装饰
    for i in range(3):
        x = 50 + i * 28
        y = 180 + i * 35
        draw.rectangle([x, y, x + 20, y + 20], outline=colors["accent"], width=2)

    # 右下角建筑方块装饰
    for i in range(3):
        x = w - 70 - i * 28
        y = h - 180 - i * 35
        draw.rectangle([x, y, x + 20, y + 20], outline=colors["accent"], width=2)


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
        except Exception as e:
            print(f"    ⚠ 图片加载失败: {e}，回退纯色背景")
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
    draw_construction_pattern(draw, w, h, colors)
    
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
    draw.text((w // 2, 80), "东盛建筑设计", fill=colors["accent"], font=font_sub, anchor="mt")
    # 副标题
    try:
        font_brand_sub = ImageFont.truetype(FONT_REGULAR, 24)
        draw.text((w // 2, 125), "设计·勘察·施工 EPC总承包", fill=(200, 200, 200), font=font_brand_sub, anchor="mt")
    except:
        pass

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


def download_bgm():
    """Check for available BGM file"""
    # BGM_PATH is None — skip BGM
    if BGM_PATH is None:
        print("  ℹ BGM未配置，跳过混音")
        return None
    
    if os.path.exists(BGM_PATH):
        print(f"  ✓ BGM已存在: {BGM_PATH}")
        return BGM_PATH
    
    # Also check alternative path
    alt_path = "/tmp/bgm_full.mp3"
    if os.path.exists(alt_path):
        print(f"  ✓ 使用备选BGM: {alt_path}")
        return alt_path
    
    alt_path2 = "/tmp/bgm_ambient.mp3"
    if os.path.exists(alt_path2):
        print(f"  ✓ 使用备选BGM: {alt_path2}")
        return alt_path2
    
    print(f"  ⚠ 未找到BGM文件")
    return None


def mix_bgm(video_path, bgm_path, output_path, volume=0.15):
    """Mix BGM at low volume under the TTS voice"""
    if not bgm_path or not os.path.exists(bgm_path):
        print(f"  ⚠ BGM不存在，复制无BGM视频作为最终版本")
        import shutil
        shutil.copy2(video_path, output_path)
        final_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  ✓ 最终视频: {output_path} ({final_mb:.1f}MB)")
        return output_path
    
    print(f"  🎵 混音BGM (音量{int(volume*100)}%)...")
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
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  ✓ 混音完成: {size_mb:.1f}MB")
        return output_path
    else:
        print(f"  ⚠ 混音失败: {r.stderr[:200]}")
        return video_path


async def main():
    print("=" * 55)
    print("  东盛建筑 视频合成器 v3.0 (EPC版)")
    print(f"  选题: {VIDEO_TITLE}")
    print(f"  配图: 东盛品牌素材")
    print("=" * 55)

    # Verify all images exist
    print("\n📸 检查图片素材...")
    all_ok = True
    for i, scene in enumerate(SCENES):
        img_path = scene.get("image")
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
            print(f"  ✓ 场景{i+1}: {os.path.basename(img_path)} ({img.size[0]}×{img.size[1]})")
        else:
            print(f"  ✗ 场景{i+1}: 图片缺失 - {img_path}")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️ 部分图片缺失，继续执行（将使用纯色背景）")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="dongsheng_v3_")

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
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#0D1B2A",
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
        print(f"\n✅ 视频合成成功！（无BGM版本）")
        print(f"   路径: {output_no_bgm}")
        print(f"   时长: {total_dur:.1f}s")
        print(f"   大小: {size_mb:.1f}MB")
        print(f"   分辨率: {WIDTH}x{HEIGHT} (竖屏)")
        print(f"   配音: {TTS_VOICE}")
        print(f"\n📁 文件在: {OUTPUT_DIR}/")
        
        # Download and mix BGM
        print(f"\n🎵 下载并混合背景音乐...")
        bgm_file = download_bgm()
        mix_bgm(output_no_bgm, bgm_file, output_path, volume=0.15)
        
        if os.path.exists(output_path):
            final_mb = os.path.getsize(output_path) / 1024 / 1024
            print(f"\n🎉 最终视频完成！")
            print(f"   路径: {output_path}")
            print(f"   大小: {final_mb:.1f}MB")
    else:
        print(f"\n✗ 拼接失败: {r.stderr[:300]}")


if __name__ == "__main__":
    asyncio.run(main())
