#!/usr/bin/env python3
"""
东盛建筑设计短视频合成器 v3.0 — 高画质版
无drawtext依赖版（Python直接渲染字幕+Ken Burns用FFmpeg实现）

特性：
  ✅ Pillow生成精美配图 + 渲染字幕（白字黑底）
  ✅ Edge TTS专业配音（YunjianNeural沉稳男声）
  ✅ Ken Burns慢缩放动效
  ✅ 专业BGM叠加
  ✅ 竖屏1080×1920
"""
import asyncio, json, os, subprocess, tempfile, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts

# ===================== 可配置区域 =====================
VIDEO_TITLE = "20万亿城市更新来袭-EPC建筑企业如何抓住红利-2026"
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 · EPC总承包"
TTS_VOICE = "zh-CN-YunjianNeural"
MIN_DURATION = 5.0
WIDTH, HEIGHT = 1080, 1920
FPS = 24
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"

# 品牌色系
COLOR_BG = (13, 27, 42)       # 深蓝黑
COLOR_ACCENT = (212, 175, 55) # 金色
COLOR_WHITE = (255, 255, 255)

# 配音文案
SCENES_TEXTS = [
    "重磅！财政部、住建部联合发文，20万亿城市更新市场全面启动。EPC总承包企业，你们的时代来了！",
    "过去做城市更新，设计院出完图纸、施工队进场，扯皮推诿、造价失控——这种老模式每年浪费上百亿。",
    "新政策明确要求：城市更新项目优先采用EPC总承包模式。设计施工一体化，没这个能力的企业该慌了。",
    "数据显示，全国2026年城市更新投资规模将突破5万亿，连片改造取代单点改造，大标段整合是趋势。",
    "智能建造+BIM正向设计+装配式施工，EPC铁三角正在重新定义城市更新的交付标准。",
    "东盛建筑设计，深耕EPC总承包领域：设计引领、勘察先行、施工管控，一站式交付让城市更新不走弯路。",
    "关注东盛建筑，读懂EPC新风口。觉得有用点个赞，转发给身边做工程的同行——好信息一起分享！",
]

BGM_URL = "https://raw.githubusercontent.com/nicedoc/free-bgm/main/corporate-technology-8bit.mp3"


# ===================== 配图 + 字幕 统一生成 =====================

def split_text(text, max_chars=14):
    """按字数拆分文本行"""
    lines = []
    for i in range(0, len(text), max_chars):
        lines.append(text[i:i+max_chars])
    return lines


def draw_centered_text(draw, text, font, center_y, max_width, color=COLOR_WHITE):
    """居中绘制多行文字"""
    lines = []
    for line in text.split('\n'):
        if font.getlength(line) > max_width:
            chars_per_line = max(1, int(max_width / font.getlength('中')))
            for i in range(0, len(line), chars_per_line):
                lines.append(line[i:i+chars_per_line])
        else:
            lines.append(line)
    if not lines:
        return
    line_height = font.getbbox('中')[3] - font.getbbox('中')[1] + 12
    total_h = len(lines) * line_height
    start_y = center_y - total_h // 2
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        fw = bbox[2] - bbox[0]
        x = (WIDTH - fw) // 2
        y = start_y + i * line_height
        # 阴影
        draw.text((x+3, y+3), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=color)


def create_frame_with_subtitle(scene_text, scene_num, is_title=False, subtitle_text=None):
    """生成一帧完整画面（含配图背景+底部字幕）"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), COLOR_BG + (255,))
    draw = ImageDraw.Draw(img)
    
    # ---- 背景：网格线 ----
    for x in range(0, WIDTH, 120):
        draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 6))
    for y in range(0, HEIGHT, 120):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 6))
    
    # ---- 几何装饰 ----
    for _ in range(4):
        x = random.randint(60, WIDTH-60)
        y_ = random.randint(150, HEIGHT-150)
        size = random.randint(40, 100)
        draw.rectangle(
            [(x-size//2, y_-size//2), (x+size//2, y_+size//2)],
            outline=COLOR_ACCENT + (25,), width=2
        )
    
    # ---- 底部金色条 ----
    draw.rectangle([(0, HEIGHT-6), (WIDTH, HEIGHT)], fill=COLOR_ACCENT)
    # 侧边金线
    draw.rectangle([(45, 180), (49, HEIGHT-200)], fill=COLOR_ACCENT)
    
    # ---- 场景编号 ----
    if not is_title:
        num_font = ImageFont.truetype(FONT_PATH, 18)
        draw.text((65, 40), f"0{scene_num}/07", font=num_font, fill=(100, 100, 100))
    
    # ---- 主文案 ----
    if is_title:
        title_font = ImageFont.truetype(FONT_PATH, 72)
        draw_centered_text(draw, scene_text, title_font, HEIGHT//2 - 100, WIDTH-140, color=COLOR_ACCENT)
        sub_font = ImageFont.truetype(FONT_PATH, 32)
        draw_centered_text(draw, BRAND_NAME + "\n" + BRAND_SUBTITLE, sub_font, HEIGHT//2 + 80, WIDTH-140)
    else:
        main_font = ImageFont.truetype(FONT_PATH, 48)
        draw_centered_text(draw, scene_text, main_font, HEIGHT//2 - 80, WIDTH-140)
    
    # ---- 品牌标识 ----
    brand_font = ImageFont.truetype(FONT_PATH, 20)
    draw_centered_text(draw, BRAND_NAME + " | " + BRAND_SUBTITLE, brand_font, HEIGHT - 130, WIDTH-140, color=COLOR_ACCENT)
    
    # ---- 标签 ----
    tag_font = ImageFont.truetype(FONT_PATH, 18)
    tags = ["#城市更新", "#EPC总承包", "#20万亿", "#东盛建筑"]
    x_start = WIDTH//2 - 180
    for i, tag in enumerate(tags):
        draw.text((x_start + i*120, HEIGHT - 85), tag, font=tag_font, fill=(80, 80, 80))
    
    # ---- 底部字幕（如果有）----
    if subtitle_text:
        subtitle_font = ImageFont.truetype(FONT_PATH, 36)
        lines = split_text(subtitle_text, 14)
        line_h = 50
        total_h = len(lines) * line_h
        start_y = HEIGHT - 170 - total_h
        
        for i, line in enumerate(lines):
            bbox = subtitle_font.getbbox(line)
            fw = bbox[2] - bbox[0]
            fh = bbox[3] - bbox[1]
            x = (WIDTH - fw) // 2
            y = start_y + i * line_h
            
            # 黑色半透明背景框
            padding = 16
            draw.rectangle(
                [(x-padding, y-4), (x+fw+padding, y+fh+6)],
                fill=(0, 0, 0, 160)
            )
            draw.text((x, y), line, font=subtitle_font, fill=(255, 255, 255))
    
    return img


def create_scene_image(text, scene_num, output_path, is_title=False):
    """生成场景配图（无字幕）"""
    img = create_frame_with_subtitle(text, scene_num, is_title=is_title, subtitle_text=None)
    img.save(output_path, quality=92)
    return output_path


def create_subtitle_sequence(text, output_dir, prefix, num_frames, fps=24, scene_num=None):
    """为每一帧生成带字幕的画面（用于Ken Burns动效后的叠加）"""
    pass  # 改用另一种方案：把字幕直接渲染到图片上，FFmpeg只做缩放


# ===================== 配音生成 =====================

async def generate_tts(text, path):
    c = edge_tts.Communicate(text, TTS_VOICE, rate="-5%")
    await c.save(path)
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True
    )
    return float(json.loads(r.stdout)["format"]["duration"])


# ===================== 主流程 =====================

async def main():
    print("=" * 58)
    print("  东盛建筑短视频合成器 v3.0 — 高画质版")
    print("  Python直接渲染字幕 + Ken Burns缩放 + BGM")
    print("=" * 58)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="ds_v3_")
    n = len(SCENES_TEXTS)
    
    # ---------- Step 1: 生成配图 + Step 4提前 ----------
    # 方案：为每段生成一张高清配图（不含字幕），字幕直接画在图片上
    # FFmpeg只负责：图片输入 → zoompan缩放 → 输出视频段
    
    print("\n🎨 生成配图（含字幕）...")
    high_res_images = []
    for i, text in enumerate(SCENES_TEXTS):
        p = os.path.join(tmp, f"scene_{i+1:02d}_hq.png")
        # 生成带字幕的高清图
        img = create_frame_with_subtitle(text, i+1, is_title=(i==0), subtitle_text=text)
        img.save(p, quality=95)
        high_res_images.append(p)
        print(f"  [{i+1}/{n}] ✓")
    
    # ---------- Step 2: 生成配音 ----------
    print("\n🎤 生成配音...")
    audios = []
    durations = []
    for i, text in enumerate(SCENES_TEXTS):
        ap = os.path.join(tmp, f"audio_{i:02d}.mp3")
        d = await generate_tts(text, ap)
        audios.append(ap)
        durations.append(d)
        short = text.replace("\n", " ")[:25]
        print(f"  [{i+1}/{n}] {short}... ({d:.1f}s)")
    
    # ---------- Step 3: 下载BGM ----------
    print("\n🎵 下载背景音乐...")
    bgm_path = os.path.join(tmp, "bgm.mp3")
    try:
        r = subprocess.run(
            ["curl", "-sL", "-o", bgm_path, "-w", "%{http_code}", BGM_URL],
            capture_output=True, text=True, timeout=20
        )
        bgm_size = os.path.getsize(bgm_path) if os.path.exists(bgm_path) else 0
        if bgm_size > 1000 and r.stdout.strip().startswith("2"):
            print(f"  ✓ BGM下载成功 ({bgm_size/1024:.0f}KB)")
        else:
            raise Exception(f"HTTP {r.stdout.strip()}")
    except Exception as e:
        print(f"  ! BGM下载失败 ({e})，跳过BGM")
        bgm_path = None
    
    # ---------- Step 4: 逐段合成（Ken Burns缩放） ----------
    print("\n🎬 逐段合成（Ken Burns动效）...")
    segments = []
    
    for i in range(n):
        dur = max(durations[i], MIN_DURATION)
        seg = os.path.join(tmp, f"seg_{i:02d}.mp4")
        img_path = high_res_images[i]
        
        # 字幕已经渲染在图片上了
        # Ken Burns: 偶数段zoom in，奇数段zoom out
        d_frames = int(FPS * dur)
        if d_frames < 1:
            d_frames = 1
        
        if i % 2 == 0:
            # zoom in 1.0 -> 1.04
            vf = f"scale=iw*1.05:-2,zoompan=z='min(zoom+0.001,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        else:
            # zoom out 1.04 -> 1.0, with slight right pan
            vf = f"scale=iw*1.05:-2,zoompan=z='max(zoom-0.001,1.0)':x='iw/2-(iw/zoom/2)+40':y='ih/2-(ih/zoom/2)':d={d_frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-i", audios[i],
            "-t", str(dur),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-vf", vf,
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            seg,
        ]
        
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ✗ 第{i+1}段失败 (exit {r.returncode})")
            print(f"    {r.stderr[:200]}")
            return
        segments.append(seg)
        print(f"  [{i+1}/{n}] {dur:.1f}s ✓")
    
    # ---------- Step 5: 拼接 ----------
    print("\n🔗 拼接...")
    concat_file = os.path.join(tmp, "segments.txt")
    with open(concat_file, "w") as f:
        for sp in segments:
            f.write(f"file '{sp}'\n")
    
    merged = os.path.join(tmp, "merged.mp4")
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", merged],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"  ✗ 拼接失败: {r.stderr[:200]}")
        return
    print(f"  ✓ 拼接完成")
    
    # ---------- Step 6: 加BGM ----------
    if bgm_path and os.path.exists(bgm_path):
        print("\n🎵 叠加BGM...")
        output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        total_dur = sum(max(d, MIN_DURATION) for d in durations)
        
        r = subprocess.run([
            "ffmpeg", "-y",
            "-i", merged,
            "-i", bgm_path,
            "-filter_complex",
            f"[1:a]volume=0.20,aloop=loop=-1:size=1,atrim=duration={total_dur}[bgm];"
            f"[0:a][bgm]amix=inputs=2:duration=first[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output,
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ✗ BGM失败: {r.stderr[:200]}")
            import shutil
            output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_无BGM.mp4")
            shutil.copy(merged, output)
        else:
            print(f"  ✓ BGM叠加完成")
    else:
        output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        import shutil
        shutil.copy(merged, output)
    
    # ---------- 完成 ----------
    if os.path.exists(output):
        size_mb = os.path.getsize(output) / 1024 / 1024
        total_dur = sum(max(d, MIN_DURATION) for d in durations)
        print(f"\n{'='*58}")
        print(f"✅  视频合成成功！")
        print(f"{'='*58}")
        print(f"   路径:   {output}")
        print(f"   时长:   {total_dur:.1f}s ({n}段)")
        print(f"   大小:   {size_mb:.1f}MB")
        print(f"   分辨率: {WIDTH}x{HEIGHT} (竖屏)")
        print(f"   配音:   {TTS_VOICE}")
        print(f"   动效:   Ken Burns 慢缩放")
        print(f"   字幕:   Python渲染（白字黑底框）")
        print(f"   画质:   CRF 18")
        print(f"{'='*58}")
        print(f"\n📁 {OUTPUT_DIR}/")
    else:
        print(f"\n✗ 合成失败")


if __name__ == "__main__":
    asyncio.run(main())
