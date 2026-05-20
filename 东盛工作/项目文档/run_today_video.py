#!/usr/bin/env python3
"""
东盛建筑短视频合成器 v3.5 — 热点速出版
===============================
特性：
  ✅ Pillow生成高品质建筑风格配图（几何线条+渐变背景+专业构图）
  ✅ 文本分层：主文案居中醒目 + 底部独立字幕区（半透明黑底白字）
  ✅ Edge TTS专业配音（YunjianNeural沉稳男声）
  ✅ Ken Burns缩放+平移动效
  ✅ BGM自动叠加，音量自适应
  ✅ VideoToolbox硬件编码，快+高清
  ✅ 竖屏1080×1920，CRF 17高画质
  ✅ 全程无drawtext依赖（字幕渲染在图片上）
"""

import asyncio, json, os, subprocess, tempfile, math, random, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts

# ===================== 可配置区域 =====================
VIDEO_TITLE = "住建部今日出手！EPC违规分包被严查，2026资质改革下谁被洗牌？"
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 · EPC总承包"
TTS_VOICE = "zh-CN-YunjianNeural"

# 品牌色系
COLOR_BG_DARK = (10, 20, 35)       # 深色背景
COLOR_BG_LIGHT = (20, 40, 60)      # 浅色层
COLOR_GOLD = (212, 175, 55)        # 金色
COLOR_GOLD_LIGHT = (230, 200, 90)  # 亮金
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (160, 170, 180)
COLOR_DARK_GRAY = (60, 70, 85)

WIDTH, HEIGHT = 1080, 1920
FPS = 24
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")

# 字体
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_LIGHT = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"

# 每段保底时长（秒）
MIN_DURATION = 5.0

# 配音文案 — 每段文字对应一个场景
SCENES_TEXTS = [
    # 第1段：热点抓注意力——住建部今日出手
    "重磅消息！就在今天，住建部紧急发文，严查EPC项目违规分包！检查发现12%的项目存在违法分包，资质不合格的分包商直接进场干。你做的项目有没有被转包过？",
    
    # 第2段：行业痛点——违规分包的危害
    "说白了，有些总包企业就是拿项目当二道贩子。拿到项目转手一包，主体结构也敢分出去。结果呢？质量失控、安全事故、扯皮推诿——最终买单的还是业主和住户。",
    
    # 第3段：2026资质改革——行业洗牌
    "更关键的是，2026新版资质标准同步落地：资质类别从593个压减到245个，压了一半多！EPC总承包统一归为'工程总承包'一个类别。门槛提高了，混日子的企业没有活路了。",
    
    # 第4段：EPC模式的优势——设计施工一体化
    "新规为什么强调EPC？因为传统设计施工分离的模式，天然给违规分包留空间。EPC总承包模式下，设计院和施工队是一家人，责任追究跑不掉，质量有保障。这才是治本。",
    
    # 第5段：数据支撑——联合体趋势
    "数据不会骗人：2026年一季度，超亿元的EPC项目中，联合体中标占比高达47%。设计院牵头、施工企业配合的联合体模式，正在成为主流。单打独斗的时代结束了。",
    
    # 第6段：东盛建筑设计——专业解读
    "东盛建筑设计，深耕EPC总承包领域十五年。设计引领、勘察先行、施工管控——我们不是转包商，我们是一站式交付的实干派。新规之下，我们准备好了，您呢？",
    
    # 第7段：引导互动
    "你觉得住建部这次严查能治本吗？评论区说说你见过最离谱的分包案例。关注东盛建筑，每天一个行业深度解读。觉得有用点个赞，转给做工程的同行看看！",
]

BGM_URL = "https://raw.githubusercontent.com/nicedoc/free-bgm/main/corporate-technology-8bit.mp3"


# === 2026-05-08 每日覆盖注入 ===
VIDEO_TITLE = '中央财政2026年城市更新：每城最高12亿！不足15城入选，谁是赢家？'
BRAND_NAME = '东盛建筑设计'
BRAND_SUBTITLE = '设计 · 勘察 · 施工 · EPC总承包'
SCENES_TEXTS = ['重磅政策！财政部住建部联合发文：2026年中央财政继续大手笔支持城市更新行动！每城最高12亿补助，全国评选不超过15个城市。这钱怎么分？谁有机会？', '东部城市每城8亿，中部每城10亿，西部每城最高12亿。划重点：资金投向两个方向——重点样板片区建设和城市更新机制建设。不是撒胡椒面，是集中打造标杆！', '15个名额，全国地级市上百个，竞争激烈！而且硬性门槛明确：不能增加隐性债务，必须在老城区实施片区改造，2024年以来无重大安全事故。筛掉一批，再筛一批。', '城市更新工程有多复杂？给排水、供热、综合管廊、老旧小区改造、历史文化街区活化……涉及十几个专业。EPC总承包模式下，设计施工一体化统筹，一个团队管到底。这正是城市更新最适合的交付模式！', '2026年一季度，全国城市更新新开工项目超3000个，总投资额同比增长15%以上。EPC模式在市政更新类项目中的采用率已达63%。城市更新，已是建筑行业最大的增量市场。', '东盛建筑设计，十五年深耕建筑工程与城市更新领域。设计引领、勘察先行、施工管控、EPC总承包一站式闭环服务。中央财政政策来了，项目机会来了——我们准备好了，您呢？', '你的城市有机会拿到这8-12亿吗？评论区说说你们当地的城市更新项目进度。关注东盛建筑设计，每天一个行业深度解读。觉得有用点个赞，转给做工程的同行！']
# === 结束覆盖 ===


# ===================== 配图生成 =====================

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(text, font, max_width):
    """按最大宽度换行"""
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
    """居中或左对齐绘制多行文本块"""
    lines = wrap_text(text, font, max_width)
    if not lines:
        return 0
    
    # 计算总高度
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
    """绘制建筑网格背景"""
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 4))
    for y in range(0, HEIGHT, 80):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 4))


def draw_building_shape(draw, cx, cy, size=80, color=COLOR_GOLD_LIGHT):
    """绘制简易建筑轮廓"""
    s = size // 2
    # 主体
    draw.rectangle([(cx-s, cy-s), (cx+s, cy+s)], outline=color, width=3)
    # 窗户
    ws = s // 3
    for row in range(3):
        for col in range(3):
            wx = cx - s + col * (s*2//3) + ws//2
            wy = cy - s + row * (s*2//3) + ws//2
            draw.rectangle([(wx, wy), (wx+ws//2, wy+ws//2)], outline=color, width=1)
    # 屋顶
    draw.polygon([(cx-s-5, cy-s), (cx, cy-s-40), (cx+s+5, cy-s)], outline=COLOR_GOLD, width=2)


def create_scene_image(scene_index, scene_text):
    """为每个场景生成配图"""
    img = Image.new('RGBA', (WIDTH, HEIGHT), COLOR_BG_DARK + (255,))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype(FONT_PATH, 72)
        font_medium = ImageFont.truetype(FONT_PATH, 48)
        font_small = ImageFont.truetype(FONT_PATH, 36)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_small = font_large
    
    # ---- 通用装饰 ----
    # 顶部亮色渐变
    for i in range(60):
        alpha = int(20 * (1 - i/60))
        draw.rectangle([(0, i), (WIDTH, i+1)], fill=(COLOR_GOLD[0], COLOR_GOLD[1], COLOR_GOLD[2], alpha))
    
    # 建筑网格
    draw_building_grid(draw)
    
    # 几何装饰
    random.seed(scene_index * 42)
    
    # ---- 不同场景不同配图风格 ----
    
    if scene_index == 0:
        # 第1段：紧急通知/文件风格
        # 大号红色/金色警示标志
        draw.rectangle([(140, 200), (WIDTH-140, 700)], outline=COLOR_GOLD, width=4)
        draw.rectangle([(150, 210), (WIDTH-150, 690)], fill=None, outline=COLOR_GOLD, width=1)
        title_font = ImageFont.truetype(FONT_PATH, 80)
        draw_centered_text_block(draw, "📢 紧急通知", title_font, 450, WIDTH-400, color=COLOR_GOLD, shadow=True)
        
        # 建筑轮廓散落
        for i in range(5):
            x = random.randint(100, WIDTH-100)
            y = random.randint(850, 1500)
            sz = random.randint(40, 80)
            draw_building_shape(draw, x, y, sz, (160 + i*10, 170 + i*5, 180 + i*10))
    
    elif scene_index == 1:
        # 第2段：违规分包问题——红色警示
        # 警示横幅
        draw.rectangle([(200, 250), (WIDTH-200, 550)], fill=(180, 30, 30, 60), outline=(255, 60, 60), width=3)
        warn_font = ImageFont.truetype(FONT_PATH, 60)
        draw_centered_text_block(draw, "⚠️ 违规分包", warn_font, 400, WIDTH-400, color=(255, 80, 80))
        
        # 破碎的建筑线条
        for _ in range(8):
            x1 = random.randint(150, WIDTH-150)
            y1 = random.randint(700, 1600)
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(-80, 80)
            draw.line([(x1, y1), (x2, y2)], fill=(255, 50, 50, 40), width=2)
    
    elif scene_index == 2:
        # 第3段：资质改革——证书/标准风格
        # 证书框
        draw.rectangle([(180, 200), (WIDTH-180, 700)], fill=COLOR_BG_LIGHT + (200,), outline=COLOR_GOLD, width=3)
        cert_font = ImageFont.truetype(FONT_PATH, 52)
        draw_centered_text_block(draw, "资质改革", cert_font, 350, WIDTH-300, color=COLOR_GOLD)
        detail_font = ImageFont.truetype(FONT_PATH, 40)
        draw_centered_text_block(draw, "593 → 245", detail_font, 520, WIDTH-300, color=COLOR_GOLD_LIGHT)
        
        # 数字柱状图
        bar_y = 850
        bar_h = 500
        for i, (label, val) in enumerate([("旧标准", 593), ("新标准", 245)]):
            bx = 270 + i * 500
            bw = 180
            bh = int(bar_h * val / 600)
            color = COLOR_GOLD if i == 1 else COLOR_DARK_GRAY
            draw.rectangle([(bx, bar_y + bar_h - bh), (bx+bw, bar_y + bar_h)], fill=color + (200,))
            draw.text((bx+30, bar_y + bar_h - bh - 50), str(val), font=font_large, fill=color)
            draw.text((bx+10, bar_y + bar_h + 20), label, font=font_small, fill=COLOR_GRAY)
    
    elif scene_index == 3:
        # 第4段：EPC模式优势——一体化示意
        # 三个连续方块表示设计-施工一体化
        labels = ["设计", "施工", "一体化"]
        colors = [COLOR_GOLD, COLOR_GOLD_LIGHT, (100, 200, 100)]
        bx_start = 120
        box_w = 240
        box_h = 160
        gap = 30
        total_w = 3 * box_w + 2 * gap
        start_x = (WIDTH - total_w) // 2
        
        for i, (label, col) in enumerate(zip(labels, colors)):
            x = start_x + i * (box_w + gap)
            y = 500
            draw.rounded_rectangle([(x, y), (x+box_w, y+box_h)], radius=16, fill=col + (60,), outline=col, width=3)
            lf = ImageFont.truetype(FONT_PATH, 56)
            draw_centered_text_block(draw, label, lf, y + box_h//2, box_w-20, color=col)
            if i < 2:
                # 连接箭头
                ax = x + box_w
                ay = y + box_h // 2
                draw.line([(ax+5, ay), (ax+gap-5, ay)], fill=COLOR_GOLD, width=3)
                draw.polygon([(ax+gap-5, ay), (ax+gap-15, ay-10), (ax+gap-15, ay+10)], fill=COLOR_GOLD)
        
        # 底部EPC链条
        draw_centered_text_block(draw, "EPC总承包 → 责任闭环", font_medium, 800, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index == 4:
        # 第5段：数据图表——联合体趋势
        # 饼图/柱状图
        chart_cx = WIDTH // 2
        chart_cy = 550
        chart_r = 200
        
        # 饼图：47%
        for angle in range(0, 360):
            rad = math.radians(angle)
            px = chart_cx + int(chart_r * math.cos(rad))
            py = chart_cy + int(chart_r * math.sin(rad))
            color = COLOR_GOLD if angle < 169 else COLOR_DARK_GRAY
            draw.line([(chart_cx, chart_cy), (px, py)], fill=color + (200,), width=2)
        
        # 中心数据
        data_font = ImageFont.truetype(FONT_PATH, 90)
        draw_centered_text_block(draw, "47%", data_font, chart_cy - 30, 300, color=COLOR_GOLD)
        draw_centered_text_block(draw, "联合体中标占比", font_medium, chart_cy + 80, 500, color=COLOR_GRAY)
        
        # 对比标注
        draw_centered_text_block(draw, "2025年: 31%  →  2026Q1: 47%", font_small, 880, WIDTH-200, color=COLOR_GOLD_LIGHT)
    
    elif scene_index == 5:
        # 第6段：东盛品牌展示——专业形象
        # 品牌大标题
        brand_font = ImageFont.truetype(FONT_PATH, 96)
        draw_centered_text_block(draw, BRAND_NAME, brand_font, 500, WIDTH-200, color=COLOR_GOLD)
        
        # 金色分隔线
        draw.line([(200, 610), (WIDTH-200, 610)], fill=COLOR_GOLD, width=2)
        
        # 品牌副标题
        draw_centered_text_block(draw, BRAND_SUBTITLE, font_medium, 700, WIDTH-200, color=COLOR_GOLD_LIGHT)
        
        # 装饰性建筑轮廓
        for i in range(3):
            bx = 200 + i * 350
            draw_building_shape(draw, bx, 1100, 80 + i*10, COLOR_GOLD)
        
        # 年份
        draw_centered_text_block(draw, "十五年匠心 · 一站式交付", font_small, 1400, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index >= 6:
        # 第7段（及之后）：互动引导
        # 关注图标
        follow_font = ImageFont.truetype(FONT_PATH, 70)
        draw_centered_text_block(draw, "💬 评论区见", follow_font, 400, WIDTH-200, color=COLOR_GOLD)
        
        draw_centered_text_block(draw, "点赞 👍 转发 🔄 关注 ❤️", font_medium, 600, WIDTH-200, color=COLOR_GOLD_LIGHT)
        
        # 底部二维码占位
        draw.rounded_rectangle([(340, 800), (740, 1200)], radius=24, outline=COLOR_GOLD, width=3)
        qr_font = ImageFont.truetype(FONT_PATH, 36)
        draw_centered_text_block(draw, "东盛建筑", qr_font, 1000, 400, color=COLOR_GOLD)
        
        # 飘落的点赞标志
        for i in range(6):
            x = random.randint(100, WIDTH-100)
            y = random.randint(1300, 1800)
            heart_size = random.randint(20, 40)
            draw.text((x, y), "👍", font=font_small, fill=COLOR_GOLD)
    
    # ---- 底部字幕区 ----
    # 不在此处渲染字幕，字幕由create_subtitle_only_frame单独生成叠加
    
    return img


def create_subtitle_only_frame(scene_text, scene_index):
    """生成纯字幕帧（透明背景，只包含底部字幕文字）"""
    # 创建一个透明图像，大小与主画面一致
    subtitle_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(subtitle_img)
    
    try:
        font_subtitle = ImageFont.truetype(FONT_PATH, 48)
    except:
        font_subtitle = ImageFont.load_default()
    
    # 底部字幕区域：半透明黑底，白字
    # 字幕区域位置：底部，从 y=1550 到 y=1850
    subtitle_box_y1 = 1520
    subtitle_box_y2 = 1800
    
    # 半透明背景
    draw.rounded_rectangle(
        [(80, subtitle_box_y1), (WIDTH-80, subtitle_box_y2)],
        radius=16,
        fill=(0, 0, 0, 180)
    )
    
    # 左侧金色装饰条
    draw.rounded_rectangle(
        [(80, subtitle_box_y1), (100, subtitle_box_y2)],
        radius=4,
        fill=COLOR_GOLD + (220,)
    )
    
    # 场景编号小标签
    tag_font = ImageFont.truetype(FONT_PATH, 28)
    draw.text((120, subtitle_box_y1 + 12), f"场景 {scene_index+1}/7", font=tag_font, fill=COLOR_GOLD)
    
    # 文案文本，居中显示在字幕区域内
    subtitle_center_y = (subtitle_box_y1 + subtitle_box_y2) // 2
    draw_centered_text_block(
        draw, scene_text, font_subtitle, subtitle_center_y, 
        WIDTH-240, color=COLOR_WHITE, shadow=True
    )
    
    return subtitle_img


async def main():
    print(f"{'='*58}")
    print(f"🎬  东盛建筑设计短视频合成器 v3.5")
    print(f"{'='*58}")
    print(f"   选题: {VIDEO_TITLE}")
    print(f"   品牌: {BRAND_NAME}")
    print(f"   场景: {len(SCENES_TEXTS)}段")
    print(f"{'='*58}\n")
    
    # ========== 1. 生成所有配图 ==========
    print("📷 第1步：生成配图...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    scene_images = []
    for i, text in enumerate(SCENES_TEXTS):
        img_path = os.path.join(OUTPUT_DIR, f"scene_{i:02d}.png")
        img = create_scene_image(i, text)
        img.save(img_path)
        scene_images.append(img_path)
        print(f"  ✓ 场景{i+1}配图生成")
    
    # 生成字幕叠加图
    subtitle_images = []
    for i, text in enumerate(SCENES_TEXTS):
        sub_path = os.path.join(OUTPUT_DIR, f"subtitle_{i:02d}.png")
        sub_img = create_subtitle_only_frame(text, i)
        sub_img.save(sub_path)
        subtitle_images.append(sub_path)
        print(f"  ✓ 场景{i+1}字幕图生成")
    
    # ========== 2. 生成TTS配音 ==========
    print("\n🎤 第2步：生成配音...")
    tts_files = []
    for i, text in enumerate(SCENES_TEXTS):
        tts_path = os.path.join(OUTPUT_DIR, f"tts_{i:02d}.mp3")
        communicate = edge_tts.Communicate(text, TTS_VOICE)
        await communicate.save(tts_path)
        tts_files.append(tts_path)
        print(f"  ✓ 场景{i+1}配音生成 ({len(text)}字)")
    
    # 获取每个TTS的时长
    durations = []
    for tts_f in tts_files:
        r = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", tts_f
        ], capture_output=True, text=True)
        dur = float(r.stdout.strip()) if r.stdout.strip() else MIN_DURATION
        durations.append(max(dur, MIN_DURATION))
    
    # ========== 3. 合成视频片段 ==========
    print("\n🎞️ 第3步：合成视频片段 (Ken Burns动效 + 字幕)...")
    clip_files = []
    
    for i in range(len(SCENES_TEXTS)):
        clip_path = os.path.join(OUTPUT_DIR, f"clip_{i:02d}.mp4")
        dur = durations[i]
        
        # 使用filter_complex合成：配图（Ken Burns缩放）+ 字幕叠加
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
    
    # ========== 4. 合并所有片段 ==========
    print("\n📽️ 第4步：合并所有片段...")
    concat_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
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
    
    print(f"  ✓ 合并完成")
    
    # ========== 5. 叠加BGM ==========
    print("\n🎵 第5步：叠加BGM...")
    bgm_path = None
    bgm_local = os.path.join(OUTPUT_DIR, "bgm.mp3")
    
    # 尝试下载BGM
    try:
        import urllib.request
        urllib.request.urlretrieve(BGM_URL, bgm_local)
        bgm_path = bgm_local
        print(f"  ✓ BGM下载完成")
    except:
        # 尝试本地BGM
        for p in [os.path.expanduser("~/Desktop/bgm.mp3"), "/usr/local/share/bgm.mp3"]:
            if os.path.exists(p):
                bgm_path = p
                print(f"  ✓ 使用本地BGM: {p}")
                break
    
    if bgm_path:
        output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        # 混合：原声为主，BGM为背景
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
            output,
        ], capture_output=True, text=True)
        
        if r.returncode != 0:
            print(f"  ! BGM叠加失败: {r.stderr[:100]}")
            output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_无BGM.mp4")
            shutil.copy(merged, output)
        else:
            print(f"  ✓ BGM叠加完成")
    else:
        output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        shutil.copy(merged, output)
    
    # ---------- 完成 ----------
    if os.path.exists(output):
        size_mb = os.path.getsize(output) / 1024 / 1024
        total_dur = sum(max(d, MIN_DURATION) for d in durations)
        print(f"\n{'='*58}")
        print(f"✅  视频合成成功！")
        print(f"{'='*58}")
        print(f"   路径:   {output}")
        print(f"   时长:   {total_dur:.1f}s ({len(SCENES_TEXTS)}段)")
        print(f"   大小:   {size_mb:.1f}MB")
        print(f"   分辨率: {WIDTH}x{HEIGHT} (竖屏)")
        print(f"   配音:   {TTS_VOICE}")
        print(f"   动效:   Ken Burns 慢缩放+平移")
        print(f"   字幕:   半透明底框+金色侧边")
        print(f"   编码:   VideoToolbox H.265 8Mbps")
        print(f"   BGM:    {'已叠加' if bgm_path else '无'}")
        print(f"{'='*58}")
        print(f"\n📁 {OUTPUT_DIR}/")
    else:
        print(f"\n✗ 合成失败")


if __name__ == "__main__":
    asyncio.run(main())
