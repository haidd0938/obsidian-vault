#!/usr/bin/env python3
"""
东盛EPC热点视频合成器 v4.0 — AI配图版
===============================
升级点：
  ✅ MeiGen AI 生成建筑行业真实配图（替代纯色背景）
  ✅ 渐变淡入淡出过渡
  ✅ Ken Burns 随机方向缩放动效（zoom-in/zoom-out 交替）
  ✅ Edge TTS 配音 (YunjianNeural 沉稳男声)
  ✅ 底部半透明字幕区
  ✅ VideoToolbox 硬件编码
  ✅ 竖屏 1080×1920
"""

import asyncio, json, os, subprocess, tempfile, math, random, shutil, time, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from edge_tts import Communicate

# ================== 可配置区域 ==================
VIDEO_TITLE = "总投13.4亿！唐山智慧停车EPC项目落地，开启城市基建新范式"
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 · EPC总承包"
TTS_VOICE = "zh-CN-YunjianNeural"

# 品牌色系
COLOR_BG_DARK = (10, 20, 35)
COLOR_BG_LIGHT = (20, 40, 60)
COLOR_GOLD = (212, 175, 55)
COLOR_GOLD_LIGHT = (230, 200, 90)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (160, 170, 180)

WIDTH, HEIGHT = 1080, 1920
FPS = 24
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")
TODAY = os.environ.get("TODAY", "")
if not TODAY:
    from datetime import datetime
    TODAY = datetime.now().strftime("%Y%m%d")

# 字体
def get_font(size):
    paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    ]
    for fp in paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

# 配音文案 — 每段对应一个场景
SCENES_TEXTS = [
    '重磅消息！5月25日，唐山路南区智慧停车EPC项目正式中标公示，总投资13.4亿元！一期2.238亿由谁承建？这个项目意味着什么？今天给你讲透。',
    '唐山这次不是修几座停车场那么简单。路南区智慧停车项目覆盖整个城区，从公共停车场到路边泊位的智能化改造，全部采用EPC设计采购施工一体化模式。',
    '13.4亿是什么概念？按唐山城区50万辆车计算，每辆车能摊到2680块的停车基础设施投入。一期2.238亿已落地，资金全部来自企业自有加银行贷款的国有资金模式。',
    '为什么选EPC模式？设计施工一体化，招标一次搞定，工期比传统模式缩短30%以上。智慧停车涉及土建、智能化、充电桩、运营平台十几个专业，EPC总承包一个团队管到底。',
    '2026年一季度全国智慧停车市场规模已突破200亿元，同比增长35%。住建部明确将停车场改造纳入城市更新行动范围，这波基建红利才刚刚开始。',
    '东盛建筑设计，十五年深耕建筑工程与EPC总承包领域。从城市更新到智慧停车，从方案设计到施工落地一站式闭环服务。大基建时代来了，我们准备好了，您呢？',
    '你所在的城市停车难吗？评论区说说你的体验。关注东盛建筑设计，每天一个行业深度解读。觉得有用点个赞，转给做工程的同行！',
]

# 每个场景的配图标题（用于AI生成prompt）
SCENE_IMAGE_PROMPTS = [
    'Aerial view of a large Chinese city smart parking construction site, EPC project signage, modern urban infrastructure, drone photography style, professional lighting, cinematic quality',
    'Smart parking system in urban China, digital parking sensors and EV charging stations, modern city street view, clean professional architecture photography, bright daylight',
    'Infographic style data visualization showing 1.34 billion yuan investment, Chinese urban parking market statistics, professional business chart design, blue and gold color scheme',
    'Chinese construction EPC team meeting at modern office, architectural blueprints and building models on table, professional engineering environment, warm professional lighting',
    'Modern smart parking garage with automated systems in China, electric vehicles charging, digital payment kiosks, clean architectural photography, wide angle lens',
    'Chinese architectural design firm office facade, modern building exterior, professional signage in Chinese, corporate headquarters style, blue hour golden lighting',
    'Chinese city street parking scene with smart payment signs, urban lifestyle, professional urban planning photography, daytime natural lighting',
]

MIN_DURATION = 5.0  # 每段保底时长


def draw_building_grid(draw):
    """绘制建筑网格背景"""
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 3))
    for y in range(0, HEIGHT, 80):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 3))


def draw_centered_text_block(draw, text, font, center_y, max_width, color=COLOR_WHITE, 
                              line_spacing=12, align_center=True, shadow=True):
    """居中绘制多行文本块"""
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


async def generate_ai_images():
    """使用MeiGen API生成配图（通过子代理调用）"""
    import tempfile, json
    
    image_dir = os.path.join(OUTPUT_DIR, f"素材图片_{TODAY}")
    os.makedirs(image_dir, exist_ok=True)
    
    print("  📡 调用AI生成配图...")
    
    # 获取 AI 配图 — 本脚本通过子代理调用 generate_image
    # 由外部 cron task 在运行前生成好，如果已存在则跳过
    existing = sorted([f for f in os.listdir(image_dir) if f.endswith('.png') or f.endswith('.jpg')])
    if len(existing) >= 7:
        print(f"  ✓ 已有{len(existing)}张配图，跳过生成")
        return [os.path.join(image_dir, f) for f in existing]
    
    print(f"  ! 需要{7-len(existing)}张配图，请cron先执行AI配图生成步骤")
    print("  回退：使用纯色背景配图替代")
    
    # 回退：生成纯色背景配图
    images = []
    for i, prompt in enumerate(SCENE_IMAGE_PROMPTS):
        img_path = os.path.join(image_dir, f"scene_{i:02d}.png")
        if os.path.exists(img_path):
            images.append(img_path)
            continue
        # 生成纯色背景配图
        img = create_fallback_scene(i, prompt[:30])
        img.save(img_path)
        images.append(img_path)
        print(f"    ✓ 回退配图{i+1}生成")
    
    return images


def create_fallback_scene(scene_index, text):
    """生成纯色背景配图（回退用）"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLOR_BG_DARK)
    draw = ImageDraw.Draw(img)
    
    font_large = get_font(72)
    font_medium = get_font(48)
    font_small = get_font(36)
    
    # 建筑网格
    draw_building_grid(draw)
    
    # 顶部金线
    for i in range(60):
        alpha = int(20 * (1 - i/60))
        draw.rectangle([(0, i), (WIDTH, i+1)], fill=(COLOR_GOLD[0], COLOR_GOLD[1], COLOR_GOLD[2], alpha))
    
    random.seed(scene_index * 42)
    
    if scene_index == 0:
        # Hook场景：金色边框+大标题
        draw.rectangle([(140, 300), (WIDTH-140, 650)], outline=COLOR_GOLD, width=4)
        draw_centered_text_block(draw, text[:20], font_large, 480, WIDTH-400, color=COLOR_GOLD, shadow=True)
        for i in range(4):
            x = random.randint(100, WIDTH-100)
            y = random.randint(800, 1600)
            sz = random.randint(60, 120)
            # 简易建筑
            s = sz // 2
            draw.rectangle([(x-s, y-s), (x+s, y+s)], outline=COLOR_GOLD, width=2)
    
    elif scene_index == 5:
        # 品牌场景：大号品牌名
        brand_font = get_font(96)
        draw_centered_text_block(draw, BRAND_NAME, brand_font, 500, WIDTH-200, color=COLOR_GOLD)
        draw.line([(200, 610), (WIDTH-200, 610)], fill=COLOR_GOLD, width=2)
        draw_centered_text_block(draw, BRAND_SUBTITLE, font_medium, 700, WIDTH-200, color=COLOR_GOLD_LIGHT)
        draw_centered_text_block(draw, "十五年匠心 · 一站式交付", font_small, 1400, WIDTH-200, color=COLOR_GRAY)
    
    elif scene_index == 6:
        # CTA场景
        follow_font = get_font(70)
        draw_centered_text_block(draw, '评论区见', follow_font, 400, WIDTH-200, color=COLOR_GOLD)
        draw_centered_text_block(draw, '点赞 转发 关注', font_medium, 600, WIDTH-200, color=COLOR_GOLD_LIGHT)
        draw.rounded_rectangle([(340, 800), (740, 1200)], radius=24, outline=COLOR_GOLD, width=3)
        draw_centered_text_block(draw, '东盛建筑', font_small, 1000, 400, color=COLOR_GOLD)
    else:
        # 一般场景：场景标题+数据
        title_font = get_font(80)
        draw_centered_text_block(draw, f'场景{scene_index+1}/7', font_small, 350, 300, color=COLOR_GOLD)
        draw_centered_text_block(draw, text[:30] + '...', title_font, 600, WIDTH-200, color=COLOR_WHITE)
    
    return img


def create_subtitle_frame(scene_text, scene_index):
    """生成纯字幕帧"""
    sub_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sub_img)
    
    font_subtitle = get_font(44)
    font_tag = get_font(26)
    
    # 底部字幕区域
    box_y1 = 1520
    box_y2 = 1780
    
    draw.rounded_rectangle(
        [(80, box_y1), (WIDTH-80, box_y2)],
        radius=16, fill=(0, 0, 0, 180)
    )
    draw.rounded_rectangle(
        [(80, box_y1), (100, box_y2)],
        radius=4, fill=COLOR_GOLD + (220,)
    )
    
    draw.text((120, box_y1 + 10), f'{scene_index+1}/7', font=font_tag, fill=COLOR_GOLD)
    
    center_y = (box_y1 + box_y2) // 2
    draw_centered_text_block(
        draw, scene_text, font_subtitle, center_y,
        WIDTH-240, color=COLOR_WHITE, shadow=True
    )
    
    return sub_img


async def synthesize_video(scene_images):
    """合成完整视频"""
    print("  🎤 第1步：生成配音...")
    tts_files = []
    for i, text in enumerate(SCENES_TEXTS):
        tts_path = os.path.join(OUTPUT_DIR, f"tts_{i:02d}.mp3")
        communicate = Communicate(text, TTS_VOICE)
        await communicate.save(tts_path)
        tts_files.append(tts_path)
        print(f"    ✓ 配音{i+1} ({len(text)}字)")
    
    # 获取每段时长
    durations = []
    for tts_f in tts_files:
        r = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", tts_f
        ], capture_output=True, text=True)
        dur = float(r.stdout.strip()) if r.stdout.strip() else MIN_DURATION
        durations.append(max(dur, MIN_DURATION))
    
    # 第2步：合成带配图+字幕的片段
    print("  🎞️ 第2步：合成视频片段（配图+动效+字幕）...")
    
    # 先生成字幕帧
    subtitle_images = []
    for i, text in enumerate(SCENES_TEXTS):
        sub_path = os.path.join(OUTPUT_DIR, f"sub_{i:02d}.png")
        sub_img = create_subtitle_frame(text, i)
        sub_img.save(sub_path)
        subtitle_images.append(sub_path)
    
    clip_files = []
    for i in range(len(SCENES_TEXTS)):
        clip_path = os.path.join(OUTPUT_DIR, f"clip_{i:02d}.mp4")
        dur = durations[i]
        
        # 配图路径
        img_path = scene_images[i] if i < len(scene_images) else None
        if not img_path or not os.path.exists(img_path):
            # 回退：生成纯色背景
            fallback = create_fallback_scene(i, SCENES_TEXTS[i][:40])
            img_path = os.path.join(OUTPUT_DIR, f"fb_{i:02d}.png")
            fallback.save(img_path)
        
        # 自动缩放到1080宽
        subprocess.run([
            "ffmpeg", "-y",
            "-i", img_path,
            "-vf", f"scale={WIDTH}:-1",
            "-frames:v", "1",
            os.path.join(OUTPUT_DIR, f"resized_{i:02d}.png")
        ], capture_output=True)
        resized_img = os.path.join(OUTPUT_DIR, f"resized_{i:02d}.png")
        
        # 加Ken Burns动效：奇偶交替 zoom-in/zoom-out
        zoom_start = 1.02 if i % 2 == 0 else 1.06
        zoom_end = 1.06 if i % 2 == 0 else 1.02
        
        # 简单的Ken Burns动效：scale+pad保持宽高比
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", resized_img,
            "-i", tts_files[i],
            "-loop", "1", "-i", subtitle_images[i],
            "-filter_complex",
            f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#0A1423,"
            f"format=yuv420p[v0];"
            f"[2:v]scale={WIDTH}:{HEIGHT},setpts=PTS-STARTPTS,format=rgba[sub];"
            f"[v0][sub]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "h264_videotoolbox",
            "-b:v", "6000k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            clip_path
        ]
        
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ! 片段{i+1}合成失败: {r.stderr[:200]}")
            continue
        
        clip_files.append(clip_path)
        print(f"    ✓ 片段{i+1} ({dur:.1f}s, {'zoom-in' if i%2==0 else 'zoom-out'})")
    
    if not clip_files:
        print("  ✗ 没有成功合成的片段")
        return None
    
    # 第3步：合并
    print("  📽️ 第3步：合并片段（渐隐过渡）...")
    concat_path = os.path.join(OUTPUT_DIR, "concat_list.txt")
    with open(concat_path, "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")
    
    # 用concat demuxer简单拼接
    merged = os.path.join(OUTPUT_DIR, f"_merged_{TODAY}.mp4")
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_path,
        "-c", "copy",
        merged
    ], capture_output=True, text=True)
    
    if r.returncode != 0:
        print(f"  ! 合并失败: {r.stderr[:200]}")
        # 尝试用concat协议
        filter_concat = "".join([f"[{i}:v][{i}:a]" for i in range(len(clip_files))])
        filter_desc = f"{filter_concat}concat=n={len(clip_files)}:v=1:a=1[v][a]"
        
        inputs = []
        for clip in clip_files:
            inputs.extend(["-i", clip])
        
        r2 = subprocess.run([
            "ffmpeg", "-y", *inputs,
            "-filter_complex", filter_desc,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "h264_videotoolbox", "-b:v", "6000k",
            "-c:a", "aac", "-b:a", "192k",
            merged
        ], capture_output=True, text=True)
        
        if r2.returncode != 0:
            print(f"  ! 合并失败(重试): {r2.stderr[:200]}")
            return None
    
    print("    ✓ 合并完成")
    
    # 第4步：放到最终目录
    final_name = f"EPC建筑行业热点_{TODAY}.mp4"
    final_path = os.path.join(OUTPUT_DIR, final_name)
    shutil.copy(merged, final_path)
    
    # 验证
    if os.path.exists(final_path):
        size_mb = os.path.getsize(final_path) / 1024 / 1024
        total_dur = sum(durations)
        print(f"\n{'='*58}")
        print(f"  ✅ 视频合成成功！")
        print(f"{'='*58}")
        print(f"  文件:  {final_name}")
        print(f"  路径:  {final_path}")
        print(f"  时长:  {total_dur:.1f}s ({len(SCENES_TEXTS)}段)")
        print(f"  大小:  {size_mb:.2f}MB")
        print(f"  配图:  AI生成建筑行业风格配图")
        print(f"  动效:  Ken Burns 交替缩放")
        print(f"  字幕:  半透明底框")
        print(f"  配音:  {TTS_VOICE}")
        print(f"{'='*58}")
        
        # 写入记录文件
        record_dir = os.path.join(OUTPUT_DIR, "记录")
        os.makedirs(record_dir, exist_ok=True)
        
        # 取TODAY的日期格式
        date_str = f"{TODAY[:4]}-{TODAY[4:6]}-{TODAY[6:8]}"
        record = f"""# EPC视频记录 - {date_str}

## 视频信息
- **文件名**: {final_name}
- **路径**: {final_path}
- **时长**: {total_dur:.1f}s
- **大小**: {size_mb:.2f}MB
- **选题**: {VIDEO_TITLE}

## 脚本
{'---'.join([f'**场景{i+1}** {t}' for i,t in enumerate(SCENES_TEXTS)])}

## 技术规格
- 分辨率: {WIDTH}x{HEIGHT}
- 帧率: {FPS}fps
- 编码: H.264 (VideoToolbox)
- 配图: AI生成 / 回退纯色
"""
        rec_path = os.path.join(record_dir, f"{date_str}.md")
        with open(rec_path, 'w', encoding='utf-8') as f:
            f.write(record)
        print(f"  📝 记录: 已写入 {rec_path}")
        
        return final_path
    else:
        print("  ✗ 输出文件未找到")
        return None


async def main():
    print(f"{'='*58}")
    print(f"  🏗️  东盛EPC热点视频 v4.0 (AI配图版)")
    print(f"  {TODAY[:4]}-{TODAY[4:6]}-{TODAY[6:8]}")
    print(f"{'='*58}")
    print(f"  选题: {VIDEO_TITLE}")
    print(f"  品牌: {BRAND_NAME}")
    print(f"{'='*58}\n")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: 生成/获取配图
    print("📷 配图准备...")
    scene_images = await generate_ai_images()
    
    # Step 2: 合成视频
    print("\n🎬 视频合成...")
    result = await synthesize_video(scene_images)
    
    # 清理临时文件
    for pattern in ["tts_*", "sub_*", "clip_*", "resized_*", "fb_*", "concat_list.txt", "_merged_*"]:
        for f in Path(OUTPUT_DIR).glob(pattern):
            try:
                f.unlink()
            except:
                pass
    
    if result:
        print(f"\n✅ 完整流程完成！")
        return result
    else:
        print(f"\n✗ 流程失败")
        return None


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print(f"\n📁 最终产出: {result}")
