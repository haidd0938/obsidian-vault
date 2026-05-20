#!/usr/bin/env python3
"""
东盛建筑短视频合成器 v3.5 — 2026-05-15
热点：中汽工程中标SEW天津EPC + 建筑行业信用报告
"""
import asyncio, json, os, subprocess, tempfile, math, random, shutil, urllib.request
import edge_tts
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ===================== 配置 =====================
VIDEO_TITLE = "中汽工程中标SEW天津第五工厂EPC项目-建筑行业2026年5月热点"
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 · EPC总承包"
TTS_VOICE = "zh-CN-YunjianNeural"

COLOR_BG_DARK = (10, 20, 35)
COLOR_BG_LIGHT = (20, 40, 60)
COLOR_GOLD = (212, 175, 55)
COLOR_GOLD_LIGHT = (230, 200, 90)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (160, 170, 180)
COLOR_DARK_GRAY = (60, 70, 85)

WIDTH, HEIGHT = 1080, 1920
FPS = 24
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
MIN_DURATION = 5.0

# ===================== 今日热点脚本（7段） =====================
TODAY_DATE = "20260515"

SCENES_TEXTS = [
    # 第1段：重磅热点——中汽工程中标SEW天津EPC
    "重磅消息！就在5月12日，国机汽车旗下中汽工程成功中标SEW天津第五工厂EPC总承包项目。总用地7.6万平方米、总建筑面积6.1万平方米——涵盖设计、采购、施工全流程！",

    # 第2段：项目详情——重型设备生产基地
    "项目位于天津经济技术开发区，建设内容涵盖办公楼、联合厂房、动力站房及配套设施。建成后将作为SEW集团重型设备生产基地，填补其在重型减速机领域的产能空白。EPC全产业链优势充分体现！",

    # 第3段：行业背景——建筑行业进入深度调整期
    "但行业大环境不容乐观！联合资信最新报告显示：2025年中国建筑业总产值近十年来首次年度负增长，基建与地产投资双双下行。行业正从扩张期进入深度调整阶段。",

    # 第4段：转机信号——对外工程承包逆势增长
    "不过别慌！报告同时指出：对外工程承包表现亮眼，成为对冲国内下滑的重要增长极。政策围绕'扩大有效投资+化债清欠'推进，新基建与高端制造领域依然存在韧性。下行中也有结构性机会。",

    # 第5段：合规警示——ST岭南EPC违法转包被查
    "另一个值得警惕的信号：ST岭南2.32亿EPC项目因涉嫌违法转包，被万安县住建局立案调查。七年旧账被翻出，股价一度触及跌停。EPC不是拿了项目再转手！合规红线不容触碰。",

    # 第6段：东盛建筑设计——专业EPC服务
    "东盛建筑设计，十五年深耕建筑工程与EPC总承包领域。从中汽工程这样的高端制造项目到城市更新、市政基础设施——设计引领、勘察先行、施工管控、一站式交付。行业在变，我们的专业不变。",

    # 第7段：引导互动
    "你们公司今年接到EPC项目了吗？行业下行期，你觉得EPC模式是出路还是风险？评论区说说你的看法。关注东盛建筑设计，每天一个行业深度解读。觉得有用点个赞，转给做工程的同行看看！",
]


# ===================== 配图生成 =====================

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        if font.getlength(paragraph) <= max_width:
            lines.append(paragraph)
            continue
        chars = list(paragraph)
        current = ""
        for ch in chars:
            test = current + ch
            if font.getlength(test) > max_width:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
    return lines

def draw_centered_text_block(draw, text, font, center_y, max_width, color=COLOR_WHITE, 
                              line_spacing=12, align_center=True, shadow=True):
    lines = wrap_text(text, font, max_width)
    if not lines:
        return 0
    line_h = font.getbbox('中')[3] - font.getbbox('中')[1] + line_spacing
    total_h = len(lines) * line_h
    start_y = center_y - total_h // 2
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        fw = bbox[2] - bbox[0]
        x = (WIDTH - fw) // 2 if align_center else 100
        y = start_y + i * line_h
        if shadow:
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 128))
        draw.text((x, y), line, font=font, fill=color)
    return total_h

def draw_building_grid(draw):
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 4))
    for y in range(0, HEIGHT, 80):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 4))

def draw_building_shape(draw, cx, cy, size=80, color=COLOR_GOLD_LIGHT):
    s = size // 2
    draw.rectangle([(cx-s, cy-s), (cx+s, cy+s)], outline=color, width=3)
    ws = s // 3
    for row in range(3):
        for col in range(3):
            wx = cx - s + col * (s*2//3) + ws//2
            wy = cy - s + row * (s*2//3) + ws//2
            draw.rectangle([(wx, wy), (wx+ws//2, wy+ws//2)], outline=color, width=1)
    draw.polygon([(cx-s-5, cy-s), (cx, cy-s-40), (cx+s+5, cy-s)], outline=COLOR_GOLD, width=2)

def create_scene_image(scene_index, scene_text):
    img = Image.new('RGBA', (WIDTH, HEIGHT), COLOR_BG_DARK + (255,))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype(FONT_PATH, 72)
        font_medium = ImageFont.truetype(FONT_PATH, 48)
        font_small = ImageFont.truetype(FONT_PATH, 36)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_small = font_large
    
    # 通用装饰
    for i in range(60):
        alpha = int(20 * (1 - i/60))
        draw.rectangle([(0, i), (WIDTH, i+1)], fill=(COLOR_GOLD[0], COLOR_GOLD[1], COLOR_GOLD[2], alpha))
    
    draw_building_grid(draw)
    random.seed(scene_index * 42)
    
    if scene_index == 0:
        # 第1段：重磅中标——工厂EPC公告风格
        draw.rectangle([(140, 200), (WIDTH-140, 700)], outline=COLOR_GOLD, width=4)
        draw.rectangle([(150, 210), (WIDTH-150, 690)], fill=None, outline=COLOR_GOLD, width=1)
        title_font = ImageFont.truetype(FONT_PATH, 70)
        draw_centered_text_block(draw, "🏭 重磅中标", title_font, 400, WIDTH-400, color=COLOR_GOLD)
        sub_font = ImageFont.truetype(FONT_PATH, 42)
        draw_centered_text_block(draw, "SEW天津第五工厂", sub_font, 550, WIDTH-300, color=COLOR_GOLD_LIGHT)
        draw_centered_text_block(draw, "EPC总承包项目", sub_font, 630, WIDTH-300, color=COLOR_GOLD_LIGHT)
        # 建筑
        for i in range(4):
            x = random.randint(120, WIDTH-120)
            y = random.randint(850, 1400)
            draw_building_shape(draw, x, y, random.randint(50, 90), COLOR_GOLD)
    
    elif scene_index == 1:
        # 第2段：项目详情——工厂示意
        # 工厂建筑
        factory_y = 350
        draw.rectangle([(200, factory_y), (WIDTH-200, factory_y+400)], fill=COLOR_BG_LIGHT + (150,), outline=COLOR_GOLD, width=3)
        # 厂房细节
        for col in range(4):
            cx = 280 + col * 180
            cy = factory_y + 100
            draw.rectangle([(cx, cy), (cx+80, cy+200)], outline=COLOR_GOLD_LIGHT, width=2)
            draw.rectangle([(cx+15, cy+20), (cx+65, cy+70)], fill=(180, 200, 220, 60))
        # 烟囱
        draw.rectangle([(750, factory_y-150), (790, factory_y)], fill=COLOR_DARK_GRAY)
        # 标签
        tag_font = ImageFont.truetype(FONT_PATH, 40)
        draw_centered_text_block(draw, "7.6万㎡ 总用地", tag_font, 1000, WIDTH-200, color=COLOR_GOLD_LIGHT)
        draw_centered_text_block(draw, "6.1万㎡ 建筑面积", tag_font, 1100, WIDTH-200, color=COLOR_GRAY)
        draw_centered_text_block(draw, "天津经济技术开发区", tag_font, 1200, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index == 2:
        # 第3段：行业调整——下行趋势图表
        draw.rectangle([(200, 250), (WIDTH-200, 650)], fill=(60, 30, 30, 100), outline=(200, 50, 50), width=3)
        warn_font = ImageFont.truetype(FONT_PATH, 56)
        draw_centered_text_block(draw, "⚠️ 近十年首次负增长", warn_font, 380, WIDTH-300, color=(255, 80, 80))
        detail_font = ImageFont.truetype(FONT_PATH, 38)
        draw_centered_text_block(draw, "建筑业总产值年度负增长", detail_font, 520, WIDTH-300, color=COLOR_GRAY)
        
        # 向下箭头
        ax, ay = WIDTH//2, 800
        draw.line([(ax, ay), (ax, ay+200)], fill=COLOR_GOLD, width=4)
        draw.polygon([(ax, ay+220), (ax-20, ay+190), (ax+20, ay+190)], fill=COLOR_GOLD)
        
        # 下行数据点
        for i in range(5):
            bx = 200 + i * 180
            by = 1200 - i * 60
            draw.ellipse([(bx-8, by-8), (bx+8, by+8)], fill=COLOR_GOLD)
        draw_centered_text_block(draw, "基建·地产双下行", detail_font, 1350, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index == 3:
        # 第4段：转机——海外工程逆势增长
        # 上升箭头 + 地球符号
        draw.ellipse([(240, 250), (WIDTH-240, 700)], outline=COLOR_GOLD, width=3)
        globe_font = ImageFont.truetype(FONT_PATH, 100)
        draw_centered_text_block(draw, "🌍", globe_font, 450, 200, color=COLOR_GOLD)
        
        # 增长箭头
        ax, ay = 350, 900
        draw.line([(ax, ay), (ax+400, ay-200)], fill=(80, 200, 80), width=6)
        draw.polygon([(ax+410, ay-210), (ax+385, ay-180), (ax+435, ay-200)], fill=(80, 200, 80))
        
        green_font = ImageFont.truetype(FONT_PATH, 48)
        draw_centered_text_block(draw, "对外工程承包", green_font, 1100, WIDTH-200, color=(80, 200, 80))
        draw_centered_text_block(draw, "逆势增长", green_font, 1200, WIDTH-200, color=COLOR_GOLD_LIGHT)
        
        detail_font = ImageFont.truetype(FONT_PATH, 36)
        draw_centered_text_block(draw, "新基建·高端制造 结构性机会", detail_font, 1400, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index == 4:
        # 第5段：合规警示——违法转包
        # 警示框
        draw.rectangle([(150, 200), (WIDTH-150, 600)], fill=(180, 20, 20, 60), outline=(255, 40, 40), width=4)
        warn_big = ImageFont.truetype(FONT_PATH, 64)
        draw_centered_text_block(draw, "🚫 违法转包", warn_big, 350, WIDTH-300, color=(255, 60, 60))
        
        detail_font = ImageFont.truetype(FONT_PATH, 40)
        draw_centered_text_block(draw, "ST岭南2.32亿EPC项目", detail_font, 520, WIDTH-300, color=COLOR_WHITE)
        draw_centered_text_block(draw, "被立案调查", detail_font, 590, WIDTH-300, color=(255, 80, 80))
        
        # 金额标注
        money_font = ImageFont.truetype(FONT_PATH, 44)
        draw_centered_text_block(draw, "2.32亿", money_font, 780, WIDTH-200, color=COLOR_GOLD)
        draw_centered_text_block(draw, "七年旧账被翻出 股价跌停", detail_font, 900, WIDTH-200, color=COLOR_GRAY)
        
        # 破碎线条
        for _ in range(6):
            x1 = random.randint(150, WIDTH-150)
            y1 = random.randint(1000, 1600)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-80, 80)
            draw.line([(x1, y1), (x2, y2)], fill=(255, 50, 50, 50), width=3)
    
    elif scene_index == 5:
        # 第6段：东盛品牌
        brand_font = ImageFont.truetype(FONT_PATH, 96)
        draw_centered_text_block(draw, BRAND_NAME, brand_font, 500, WIDTH-200, color=COLOR_GOLD)
        draw.line([(200, 610), (WIDTH-200, 610)], fill=COLOR_GOLD, width=2)
        draw_centered_text_block(draw, BRAND_SUBTITLE, font_medium, 700, WIDTH-200, color=COLOR_GOLD_LIGHT)
        for i in range(3):
            bx = 200 + i * 350
            draw_building_shape(draw, bx, 1100, 80 + i*10, COLOR_GOLD)
        draw_centered_text_block(draw, "十五年匠心 · 一站式交付", font_small, 1400, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index >= 6:
        # 第7段：互动引导
        follow_font = ImageFont.truetype(FONT_PATH, 70)
        draw_centered_text_block(draw, "💬 评论区见", follow_font, 400, WIDTH-200, color=COLOR_GOLD)
        draw_centered_text_block(draw, "点赞 👍 转发 🔄 关注 ❤️", font_medium, 600, WIDTH-200, color=COLOR_GOLD_LIGHT)
        draw.rounded_rectangle([(340, 800), (740, 1200)], radius=24, outline=COLOR_GOLD, width=3)
        qr_font = ImageFont.truetype(FONT_PATH, 36)
        draw_centered_text_block(draw, "东盛建筑", qr_font, 1000, 400, color=COLOR_GOLD)
        for i in range(6):
            x = random.randint(100, WIDTH-100)
            y = random.randint(1300, 1800)
            draw.text((x, y), "👍", font=font_small, fill=COLOR_GOLD)
    
    return img


def create_subtitle_only_frame(scene_text, scene_index):
    subtitle_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(subtitle_img)
    
    try:
        font_subtitle = ImageFont.truetype(FONT_PATH, 48)
        tag_font = ImageFont.truetype(FONT_PATH, 28)
    except:
        font_subtitle = ImageFont.load_default()
        tag_font = font_subtitle
    
    subtitle_box_y1 = 1520
    subtitle_box_y2 = 1800
    
    draw.rounded_rectangle(
        [(80, subtitle_box_y1), (WIDTH-80, subtitle_box_y2)],
        radius=16, fill=(0, 0, 0, 180)
    )
    draw.rounded_rectangle(
        [(80, subtitle_box_y1), (100, subtitle_box_y2)],
        radius=4, fill=COLOR_GOLD + (220,)
    )
    draw.text((120, subtitle_box_y1 + 12), f"场景 {scene_index+1}/7", font=tag_font, fill=COLOR_GOLD)
    
    subtitle_center_y = (subtitle_box_y1 + subtitle_box_y2) // 2
    draw_centered_text_block(
        draw, scene_text, font_subtitle, subtitle_center_y, 
        WIDTH-240, color=COLOR_WHITE, shadow=True
    )
    
    return subtitle_img


async def main():
    print(f"{'='*58}")
    print(f"🎬  东盛建筑短视频合成器 v3.5 — {TODAY_DATE}")
    print(f"{'='*58}")
    print(f"   选题: {VIDEO_TITLE}")
    print(f"   品牌: {BRAND_NAME}")
    print(f"   场景: {len(SCENES_TEXTS)}段")
    print(f"{'='*58}\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # ========== 1. 配图 ==========
    print("📷 第1步：生成配图...")
    scene_images = []
    for i, text in enumerate(SCENES_TEXTS):
        img_path = os.path.join(OUTPUT_DIR, f"scene_{TODAY_DATE}_{i:02d}.png")
        img = create_scene_image(i, text)
        img.save(img_path)
        scene_images.append(img_path)
        print(f"  ✓ 场景{i+1}配图生成")
    
    subtitle_images = []
    for i, text in enumerate(SCENES_TEXTS):
        sub_path = os.path.join(OUTPUT_DIR, f"subtitle_{TODAY_DATE}_{i:02d}.png")
        sub_img = create_subtitle_only_frame(text, i)
        sub_img.save(sub_path)
        subtitle_images.append(sub_path)
        print(f"  ✓ 场景{i+1}字幕图生成")
    
    # ========== 2. TTS ==========
    print("\n🎤 第2步：生成配音...")
    tts_files = []
    for i, text in enumerate(SCENES_TEXTS):
        tts_path = os.path.join(OUTPUT_DIR, f"tts_{TODAY_DATE}_{i:02d}.mp3")
        communicate = edge_tts.Communicate(text, TTS_VOICE)
        await communicate.save(tts_path)
        tts_files.append(tts_path)
        print(f"  ✓ 场景{i+1}配音生成 ({len(text)}字)")
    
    durations = []
    for tts_f in tts_files:
        r = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", tts_f
        ], capture_output=True, text=True)
        dur = float(r.stdout.strip()) if r.stdout.strip() else MIN_DURATION
        durations.append(max(dur, MIN_DURATION))
    
    # ========== 3. 合成 ==========
    print("\n🎞️ 第3步：合成视频片段 (Ken Burns + 字幕)...")
    clip_files = []
    for i in range(len(SCENES_TEXTS)):
        clip_path = os.path.join(OUTPUT_DIR, f"clip_{TODAY_DATE}_{i:02d}.mp4")
        dur = durations[i]
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", scene_images[i],
            "-i", tts_files[i],
            "-loop", "1", "-i", subtitle_images[i],
            "-filter_complex",
            f"[0:v]format=rgba,scale=iw*1.05:ih*1.05:flags=lanczos,"
            f"zoompan=z=1+0.008*on:d={int(FPS*dur)}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p[v0];"
            f"[2:v]format=rgba,scale={WIDTH}:{HEIGHT},setpts=PTS-STARTPTS[sub];"
            f"[v0][sub]overlay=0:0:format=auto,format=yuv420p[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "h264_videotoolbox",
            "-b:v", "6000k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-movflags", "+faststart",
            clip_path
        ]
        
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ! 片段{i+1}合成失败: {r.stderr[:200]}")
            continue
        clip_files.append(clip_path)
        print(f"  ✓ 片段{i+1}合成 ({dur:.1f}s)")
    
    # ========== 4. 合并 ==========
    print("\n📽️ 第4步：合并所有片段...")
    concat_path = os.path.join(OUTPUT_DIR, f"concat_list_{TODAY_DATE}.txt")
    with open(concat_path, "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")
    
    merged = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_merged.mp4")
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_path,
        "-c", "copy",
        merged
    ], capture_output=True, text=True)
    
    if r.returncode != 0:
        print(f"  ! 合并失败: {r.stderr[:200]}")
        return
    print("  ✓ 合并完成")
    
    # ========== 5. BGM ==========
    print("\n🎵 第5步：叠加BGM...")
    bgm_path = None
    bgm_local = os.path.join(OUTPUT_DIR, "bgm.mp3")
    
    try:
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/nicedoc/free-bgm/main/corporate-technology-8bit.mp3", 
            bgm_local
        )
        bgm_path = bgm_local
        print("  ✓ BGM下载完成")
    except:
        for p in [os.path.expanduser("~/Desktop/bgm.mp3"), "/usr/local/share/bgm.mp3"]:
            if os.path.exists(p):
                bgm_path = p
                print(f"  ✓ 使用本地BGM: {p}")
                break
    
    if bgm_path:
        final_output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        r = subprocess.run([
            "ffmpeg", "-y",
            "-i", merged,
            "-i", bgm_path,
            "-filter_complex",
            "[1:a]volume=0.12[a_bgm];"
            "[0:a][a_bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            final_output,
        ], capture_output=True, text=True)
        
        if r.returncode != 0:
            print(f"  ! BGM叠加失败: {r.stderr[:100]}")
            final_output = merged
        else:
            print("  ✓ BGM叠加完成")
    else:
        final_output = merged
    
    # 复制到桌面
    desktop_path = os.path.expanduser(f"~/Desktop/EPC建筑行业热点_{TODAY_DATE}.mp4")
    shutil.copy2(final_output, desktop_path)
    
    # 完成
    if os.path.exists(final_output):
        size_mb = os.path.getsize(final_output) / 1024 / 1024
        total_dur = sum(durations)
        print(f"\n{'='*58}")
        print(f"✅  视频合成成功！")
        print(f"{'='*58}")
        print(f"   输出:   {final_output}")
        print(f"   桌面:   {desktop_path}")
        print(f"   时长:   {total_dur:.1f}s ({len(SCENES_TEXTS)}段)")
        print(f"   大小:   {size_mb:.1f}MB")
        print(f"   分辨率: {WIDTH}x{HEIGHT} (竖屏)")
        print(f"   配音:   {TTS_VOICE}")
        print(f"{'='*58}")

if __name__ == "__main__":
    asyncio.run(main())
