#!/usr/bin/env python3
"""
鑫球汇台球俱乐部 — 路线1：科普干货
2026-05-25 周一
7个台球高手都知道的击球技巧 + 开头Hook + CTA
"""
import subprocess, os, sys, json, shutil, asyncio, re
from PIL import Image, ImageDraw, ImageFont

# ===== 配置 =====
VIDEO_TITLE = "台球高手才知道的7个击球技巧-鑫球汇"
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")
SCRIPT_DIR = os.path.expanduser("~/Desktop")
IMAGE_DIR = os.path.expanduser("~/Desktop/鑫球汇图片素材")

WIDTH, HEIGHT = 1080, 1920
FPS = 30
MIN_DURATION = 5.0  # 每段最小秒数
TTS_VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓女声 — 路线1专用

# 字体自动检测
FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]
FONT_PATH = next((fp for fp in FONT_CANDIDATES if os.path.exists(fp)), None)
if not FONT_PATH:
    raise FileNotFoundError("No Chinese font found on system")
print(f"✅ 字体: {os.path.basename(FONT_PATH)}")

# BGM路径
BGM_PATHS = [
    os.path.expanduser("~/Desktop/鑫球汇图片素材/bgm_01.wav"),
    os.path.expanduser("~/Desktop/鑫球汇图片素材/bgm_02.wav"),
    "/tmp/bgm_snooker.mp3",
]

# ===== 配色方案（路线1：7套深色→渐变）=====
SCHEMES = [
    ("#0d1b2a", "#1b2838"),  # 深蓝金 - 开场hook
    ("#1a1a2e", "#16213e"),  # 深蓝金 - 1
    ("#3a1a0d", "#1a0a05"),  # 暖褐金 - 2
    ("#1b4332", "#081c15"),  # 深绿 - 3
    ("#4a1c40", "#2d0a28"),  # 紫粉 - 4
    ("#0c3547", "#051a26"),  # 深海青 - 5
    ("#2c3e50", "#1a252f"),  # 深灰蓝 - 6
    ("#0d1b2a", "#1b2838"),  # 深蓝金 - CTA结尾
]
ACCENT_COLORS = [
    (255, 200, 0), (100, 200, 255), (200, 150, 100),
    (100, 255, 150), (255, 150, 200), (255, 180, 50),
    (150, 200, 255), (255, 200, 100),
]

# ===== 文案（零「/」P0规则）=====
SCENES_TEXTS = [
    "台球高手才知道的7个击球技巧",
    "第一，击球前一定要先看目标球的入袋角度",
    "第二，站位时下巴要贴住球杆，保持三点一线",
    "第三，手架要稳，开掌支撑比握拳更准确",
    "第四，出杆要像钟摆一样，只用小臂带动手腕",
    "第五，母球加塞时，瞄点要向反方向偏移半个皮头",
    "第六，防守时把母球贴库，对手就没法进攻",
    "第七，心态比技术更重要，每一杆都当最后一杆打",
    "来鑫球汇，实战练出真功夫，秦州万达B1层等你",
]

# ===== 配图映射 =====
BG_IMAGES = [f"bg_{i:02d}.png" for i in range(1, 10)]  # bg_01~09


def ensure_bg_images():
    """如果bg图丢失则自动生成"""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    if os.path.exists(os.path.join(IMAGE_DIR, "bg_01.png")):
        print(f"  bg_01.png 已存在，跳过生成")
        return
    print(f"  ⚠️ bg图不存在，自动生成...")
    schemes = [("#1a1a2e","#16213e"), ("#0f3460","#1a1a2e"),
               ("#2c3e50","#1a252f"), ("#1b4332","#081c15"),
               ("#4a1c40","#2d0a28"), ("#3c096c","#10002b"),
               ("#7f2d0f","#3e1305"), ("#0c3547","#051a26"),
               ("#1a1a2e","#0f3460")]
    accents = [(255,200,0), (100,200,255), (200,150,255),
               (100,255,150), (255,150,200), (255,180,50),
               (150,200,255), (255,100,100), (255,200,100)]
    for i in range(9):
        c1, c2 = schemes[i]; accent = accents[i]
        img = Image.new("RGB", (1080,1920), c1)
        draw = ImageDraw.Draw(img)
        for y in range(1920):
            ratio = y/1920
            r = int(int(c1[0])*(1-ratio) + int(c2[0])*ratio)
            g = int(int(c1[1])*(1-ratio) + int(c2[1])*ratio)
            b = int(int(c1[2])*(1-ratio) + int(c2[2])*ratio)
            draw.line([(0,y), (1080,y)], fill=(r,g,b))
        draw.rectangle([0,0,1080,8], fill=accent)
        draw.rectangle([0,1912,1080,1920], fill=accent)
        for cx,cy in [(60,60),(1020,60),(60,1860),(1020,1860)]:
            draw.ellipse([cx-15,cy-15,cx+15,cy+15], outline=accent, width=3)
        colors = [(255,215,0),(0,0,255),(255,0,0),(128,0,128),(255,165,0),(0,128,0)]
        sx = 1080//2 - len(colors)*35
        for j, col in enumerate(colors):
            bx = sx + j*70 + 35
            draw.ellipse([bx-22, 1670-22, bx+22, 1670+22], fill=col)
        img.save(os.path.join(IMAGE_DIR, f"bg_{i+1:02d}.png"), "PNG")
    # 封面
    cover = Image.new("RGB", (1080,1920), (13,27,42))
    draw = ImageDraw.Draw(cover)
    draw.rectangle([0,0,1080,10], fill=(201,169,78))
    draw.rectangle([0,1910,1080,1920], fill=(201,169,78))
    cx, cy = 540, 760
    draw.ellipse([cx-80, cy-80, cx+80, cy+80], fill=(255,255,255), outline=(0,0,0), width=3)
    draw.ellipse([cx-38, cy-38, cx+38, cy+38], fill=(0,0,0))
    draw.ellipse([cx-90, cy-90, cx+90, cy+90], outline=(201,169,78), width=3)
    colors2 = [(255,215,0),(0,0,255),(255,0,0),(128,0,128),(255,165,0),(0,128,0),(255,20,147),(0,0,0)]
    sx2 = 1080//2 - len(colors2)*30
    for j, col in enumerate(colors2):
        bx = sx2 + j*60 + 30
        draw.ellipse([bx-18, 1840-18, bx+18, 1840+18], fill=col)
    cover.save(os.path.join(IMAGE_DIR, "bg_cover.png"), "PNG")
    print(f"  ✅ 已生成10张bg图")


def get_bgm():
    """获取BGM，优先本地持久化路径，防0字节陷阱"""
    for p in BGM_PATHS:
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    return None


async def gen_tts(text, path, voice=TTS_VOICE):
    """用edge-tts CLI生成配音，含重试机制"""
    for attempt in range(6):
        try:
            proc = await asyncio.create_subprocess_exec(
                "edge-tts", "--voice", voice, "--text", text,
                "--write-media", path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=45)
            if proc.returncode == 0:
                return
            err_msg = stderr.decode() if stderr else ""
            if "Connection reset" in err_msg or "Cannot connect" in err_msg:
                pass
            else:
                raise RuntimeError(f"edge-tts error: {err_msg[:200]}")
        except (asyncio.TimeoutError, Exception) as e:
            if attempt < 5:
                wait = 5 * (attempt + 2)
                print(f"  ⚠️ TTS重试 {attempt+1}: 等待{wait}s...")
                await asyncio.sleep(wait)
            else:
                raise


def get_audio_duration(path):
    """用ffprobe获取音频时长"""
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                       "-show_format", path], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def create_scene_image(text, bg_name, scheme_idx, is_cover=False, is_cta=False):
    """用Pillow在图片上叠加文字"""
    if bg_name and os.path.exists(os.path.join(IMAGE_DIR, bg_name)):
        img = Image.open(os.path.join(IMAGE_DIR, bg_name)).convert("RGB")
    else:
        # 纯色背景
        c1, c2 = SCHEMES[scheme_idx % len(SCHEMES)]
        img = Image.new("RGB", (WIDTH, HEIGHT), c1)
        draw = ImageDraw.Draw(img)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(int(c1[0])*(1-ratio) + int(c2[0])*ratio)
            g = int(int(c1[1])*(1-ratio) + int(c2[1])*ratio)
            b = int(int(c1[2])*(1-ratio) + int(c2[2])*ratio)
            draw.line([(0,y), (WIDTH,y)], fill=(r,g,b))

    draw = ImageDraw.Draw(img)

    # 半透明黑色遮罩
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    o_draw = ImageDraw.Draw(overlay)
    o_draw.rectangle([0, 100, WIDTH, HEIGHT-100], fill=(0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    if is_cta:
        # CTA段：金色促销文字
        accent = ACCENT_COLORS[scheme_idx % len(ACCENT_COLORS)]
        font_large = ImageFont.truetype(FONT_PATH, 56)
        font_small = ImageFont.truetype(FONT_PATH, 40)

        lines = text.split("\n") if "\n" in text else [text]
        total_h = len(lines) * 70
        start_y = (HEIGHT - total_h) // 2

        for li, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_large)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw)//2, start_y + li*70), line,
                      fill=accent, font=font_large)

        # 底部金色装饰条 + 品牌名
        draw.rectangle([WIDTH//2-120, HEIGHT-250, WIDTH//2+120, HEIGHT-246], fill=(255, 215, 0))

        # CTA超大金色
        bbox = draw.textbbox((0, 0), "📍 秦州万达B1层", font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw)//2, HEIGHT-220), "📍 秦州万达B1层",
                  fill=(255, 215, 0), font=font_small)
    else:
        # 普通段：白色大标题居中
        accent = ACCENT_COLORS[scheme_idx % len(ACCENT_COLORS)]
        font_main = ImageFont.truetype(FONT_PATH, 58)

        # 突出关键词
        lines = text.split("\n") if "\n" in text else [text]

        total_h = len(lines) * 75
        start_y = (HEIGHT - total_h) // 2 - 40

        for li, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_main)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw)//2, start_y + li*75), line,
                      fill=(255, 255, 255), font=font_main)

        # 顶部金色装饰线（品牌感）
        draw.rectangle([WIDTH//2-80, 150, WIDTH//2+80, 154], fill=accent)

        # 左上角品牌名
        font_brand = ImageFont.truetype(FONT_PATH, 28)
        draw.text((40, 40), "鑫球汇台球", fill=accent, font=font_brand)

        # 底部页码
        font_page = ImageFont.truetype(FONT_PATH, 24)
        page_text = f"{scheme_idx+1}/{len(SCENES_TEXTS)}"
        bbox = draw.textbbox((0, 0), page_text, font=font_page)
        draw.text((WIDTH-80, HEIGHT-60), page_text, fill=(180, 180, 180), font=font_page)

    return img


def build_ken_burns(image_path, audio_path, output_path, duration):
    """生成带Ken Burns缩放效果的视频段（2步合成，防FFmpeg 8.1 bug）"""
    frames = int(duration * FPS)
    tmp_video = output_path.replace(".mp4", "_tmpvid.mp4")

    # Step 1: 仅zoompan视频（无音频）
    cmd1 = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-filter_complex",
        f"[0:v]scale=1920:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z='if(eq(on,1),1.0,1.0+0.003*(on-1))':d={frames}:s=1080x1920"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium", "-b:v", "8M",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-an",
        "-t", str(duration + 0.5), tmp_video
    ]
    subprocess.run(cmd1, check=True, capture_output=True, text=True)

    # Step 2: 合流音频
    cmd2 = [
        "ffmpeg", "-y",
        "-i", tmp_video, "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_path
    ]
    subprocess.run(cmd2, check=True, capture_output=True, text=True)

    if os.path.exists(tmp_video):
        os.remove(tmp_video)


def mix_bgm(video_path, bgm_path, output_path):
    """叠加BGM，配音优先"""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", bgm_path,
        "-filter_complex",
        "[1:a]volume=0.15[bgm];"
        "[0:a][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"🎱 鑫球汇视频生产 | 路线1：科普干货")
    print(f"📅 2026-05-25 周一")
    print(f"📹 {VIDEO_TITLE}")
    print(f"🎤 {TTS_VOICE}")
    print(f"{'='*60}\n")

    # 1. 确保背景图存在
    ensure_bg_images()

    # 2. 准备配图
    print(f"\n{'='*40}")
    print(f"📷 准备配图（{len(SCENES_TEXTS)}段）")
    print(f"{'='*40}")
    scene_images = []
    for idx, text in enumerate(SCENES_TEXTS):
        is_cover = (idx == 0)
        is_cta = (idx == len(SCENES_TEXTS) - 1)

        if is_cover:
            bg_name = "bg_cover.png" if os.path.exists(os.path.join(IMAGE_DIR, "bg_cover.png")) else BG_IMAGES[idx % len(BG_IMAGES)]
        elif is_cta:
            bg_name = "bg_cover.png" if os.path.exists(os.path.join(IMAGE_DIR, "bg_cover.png")) else BG_IMAGES[idx % len(BG_IMAGES)]
        else:
            bg_name = BG_IMAGES[idx % len(BG_IMAGES)]

        img_path = os.path.join(OUTPUT_DIR, f"scene_{idx+1:02d}.png")
        img = create_scene_image(text, bg_name, idx, is_cover=is_cover, is_cta=is_cta)
        img.save(img_path, "PNG")
        scene_images.append(img_path)
        print(f"  [{idx+1}/{len(SCENES_TEXTS)}] bg: {bg_name}")

    # 3. 生成TTS配音
    print(f"\n{'='*40}")
    print(f"🎤 TTS配音生成（{len(SCENES_TEXTS)}段）")
    print(f"{'='*40}")
    audio_files = []
    durations = []
    for idx, text in enumerate(SCENES_TEXTS):
        audio_path = os.path.join(OUTPUT_DIR, f"audio_{idx+1:02d}.mp3")
        print(f"  [{idx+1}/{len(SCENES_TEXTS)}] 生成配音...", end=" ", flush=True)
        await gen_tts(text, audio_path)
        dur = get_audio_duration(audio_path)
        dur = max(dur, MIN_DURATION)
        durations.append(dur)
        audio_files.append(audio_path)
        print(f"{dur:.1f}s")

        # 段间等待，降低TTS连接风暴
        if idx < len(SCENES_TEXTS) - 1:
            await asyncio.sleep(3)

    print(f"  ✅ 全部配音生成完成")

    # 4. Ken Burns合成各段
    print(f"\n{'='*40}")
    print(f"🎬 Ken Burns合成（{len(SCENES_TEXTS)}段）")
    print(f"{'='*40}")
    segments = []
    for idx, (img_path, audio_path, dur) in enumerate(zip(scene_images, audio_files, durations)):
        seg_path = os.path.join(OUTPUT_DIR, f"seg_{idx+1:02d}.mp4")
        print(f"  [{idx+1}/{len(SCENES_TEXTS)}] {dur:.1f}s...", end=" ", flush=True)
        build_ken_burns(img_path, audio_path, seg_path, dur)
        segments.append(seg_path)
        print(f"✅")

    # 5. 拼接
    print(f"\n{'='*40}")
    print(f"🔗 拼接视频段")
    print(f"{'='*40}")
    segments_txt = os.path.join(OUTPUT_DIR, "segments.txt")
    with open(segments_txt, "w") as f:
        for sp in segments:
            f.write(f"file '{sp}'\n")

    merged_no_bgm = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_no_bgm.mp4")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", segments_txt, "-c", "copy", merged_no_bgm
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True, text=True)
    print(f"  ✅ 拼接完成: {os.path.basename(merged_no_bgm)}")

    # 6. BGM叠加
    print(f"\n{'='*40}")
    print(f"🎵 BGM处理")
    print(f"{'='*40}")
    bgm_path = get_bgm()
    final_video = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")

    if bgm_path:
        print(f"  🎵 找到BGM: {os.path.basename(bgm_path)} ({os.path.getsize(bgm_path)//1024}KB)")
        mix_bgm(merged_no_bgm, bgm_path, final_video)
        print(f"  ✅ BGM叠加完成")
        if os.path.exists(merged_no_bgm):
            os.remove(merged_no_bgm)
            print(f"  🗑️ 已清理_no_bgm中间文件")
    else:
        print(f"  ⚠️ 无BGM，交付纯配音版")
        clean_name = merged_no_bgm.replace("_no_bgm.mp4", ".mp4")
        if clean_name != merged_no_bgm:
            shutil.move(merged_no_bgm, clean_name)
            final_video = clean_name
        else:
            final_video = merged_no_bgm

    # 7. 验证
    print(f"\n{'='*40}")
    print(f"🔍 验证输出")
    print(f"{'='*40}")

    # 文件大小
    if os.path.exists(final_video):
        size_mb = os.path.getsize(final_video) / (1024 * 1024)
        print(f"  📦 文件大小: {size_mb:.1f}MB")

    # 视频信息
    r = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_name,width,height",
        "-of", "default=noprint_wrappers=1", final_video
    ], capture_output=True, text=True)
    print(f"  🎬 编码信息:")
    for line in r.stdout.strip().split("\n"):
        print(f"     {line}")

    duration_info = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1", final_video
    ], capture_output=True, text=True)
    for line in duration_info.stdout.strip().split("\n"):
        print(f"     {line}")

    # 黑帧检测
    black_r = subprocess.run([
        "ffmpeg", "-i", final_video,
        "-vf", "blackdetect=d=0.1:pix_th=0.1",
        "-f", "null", "-"
    ], capture_output=True, text=True, timeout=30)
    if "black_start" in black_r.stderr:
        print(f"  ❌ 黑帧检测异常!")
        lines = [l for l in black_r.stderr.split('\n') if 'black' in l]
        print(f"     {lines[:3]}")
    else:
        print(f"  ✅ 黑帧检测: 通过（无黑帧）")

    # 最终路径
    print(f"\n{'='*60}")
    print(f"✅ 生产完成！")
    print(f"📹 {os.path.basename(final_video)}")
    print(f"📂 {final_video}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
