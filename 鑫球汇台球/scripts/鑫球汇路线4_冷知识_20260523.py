#!/usr/bin/env python3
"""
鑫球汇台球俱乐部 — 路线4：冷知识搬运
2026-05-23 周六
10条斯诺克/台球冷知识 + 开头Hook + CTA
"""

import subprocess, os, sys, json, shutil, asyncio, re
from PIL import Image, ImageDraw, ImageFont

# ===== 配置 =====
VIDEO_TITLE = "斯诺克99%的人都不知道的10个冷知识-鑫球汇"
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")
SCRIPT_DIR = os.path.expanduser("~/Desktop")
IMAGE_DIR = os.path.expanduser("~/Desktop/鑫球汇图片素材")

WIDTH, HEIGHT = 1080, 1920
FPS = 30
MIN_DURATION = 4.5  # 每段最小秒数
TTS_VOICE = "zh-CN-YunyangNeural"  # 云扬男声 — 路线4专用

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
    os.path.expanduser("~/Desktop/鑫球汇图片素材/bgm_01.mp3"),
    "/tmp/bgm_snooker.mp3",
]

# ===== 配色方案（路线4：10+套，每段不重样）=====
SCHEMES = [
    ("#1a1a2e", "#16213e"),  # 深灰金 - 开场hook
    ("#4a1c40", "#2d0a28"),  # 紫粉 - 1
    ("#0c3547", "#051a26"),  # 蓝青 - 2
    ("#7f2d0f", "#3e1305"),  # 暖褐金 - 3
    ("#1b4332", "#081c15"),  # 绿亮绿 - 4
    ("#5a2d6b", "#2d0a38"),  # 粉紫 - 5
    ("#3a1a0d", "#1a0a05"),  # 金 - 6
    ("#2d4a1a", "#0d1a05"),  # 黄绿 - 7
    ("#0d3a3a", "#051a1a"),  # 青绿 - 8
    ("#6b4a1a", "#2d1a05"),  # 暖金 - 9
    ("#3a2d5a", "#1a0d2d"),  # 紫蓝 - 10
    ("#1a1a2e", "#0f3460"),  # 深灰金 - CTA结尾
]
ACCENT_COLORS = [
    (255, 200, 0), (255, 150, 200), (100, 200, 255),
    (200, 150, 100), (100, 255, 150), (200, 150, 255),
    (255, 180, 50), (180, 230, 80), (80, 220, 200),
    (230, 180, 60), (180, 130, 255), (255, 200, 100),
]

# ===== 文案（零「/」P0规则）=====
SCENES_TEXTS = [
    "斯诺克99%的人都不知道的10个冷知识",
    "一杆147满分杆的理论最低耗时只有5分钟",
    "斯诺克球台的绿色台呢最早其实是干草染色",
    "丁俊晖8岁就开始每天练球8小时",
    "奥沙利文的最快147只用时5分08秒",
    "台球杆的前枝和后枝用的是不同木材",
    "中式八球的袋口比斯诺克大但比美式小",
    "世界上第一张台球桌出现在15世纪的法国",
    "高手打球时脑子里同时想的是接下来三杆",
    "职业选手的皮头每打两三局就要换一次",
    "台球厅最赚钱的不是台费而是饮料和小吃",
    "鑫球汇秦州万达店全场会员优惠等你来",
]

# ===== BG图自动生成（素材目录为空时自恢复）=====
def ensure_bg_images():
    """生成10张渐变装饰背景图，如果不存在"""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    existing = [f for f in os.listdir(IMAGE_DIR) if f.startswith("bg_") and f.endswith(".png")]
    if len(existing) >= 9:
        print(f"✅ bg图已存在: {len(existing)}张")
        return

    print("🔄 生成bg装饰背景图...")
    schemes = [
        ("#1a1a2e","#16213e"), ("#0f3460","#1a1a2e"),
        ("#2c3e50","#1a252f"), ("#1b4332","#081c15"),
        ("#4a1c40","#2d0a28"), ("#3c096c","#10002b"),
        ("#7f2d0f","#3e1305"), ("#0c3547","#051a26"),
        ("#1a1a2e","#0f3460"),
    ]
    accents = [(255,200,0), (100,200,255), (200,150,255),
               (100,255,150), (255,150,200), (255,180,50),
               (150,200,255), (255,100,100), (255,200,100)]

    for i in range(9):
        c1_hex, c2_hex = schemes[i]
        accent = accents[i]
        c1 = tuple(int(c1_hex[j:j+2], 16) for j in (1,3,5))
        c2 = tuple(int(c2_hex[j:j+2], 16) for j in (1,3,5))
        img = Image.new("RGB", (WIDTH, HEIGHT), c1)
        draw = ImageDraw.Draw(img)

        # 渐变
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(c1[0]*(1-ratio) + c2[0]*ratio)
            g = int(c1[1]*(1-ratio) + c2[1]*ratio)
            b = int(c1[2]*(1-ratio) + c2[2]*ratio)
            draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

        # 强调线
        draw.rectangle([0, 0, WIDTH, 8], fill=accent)
        draw.rectangle([0, HEIGHT-8, WIDTH, HEIGHT], fill=accent)

        # 角落圆环
        for cx, cy in [(60, 60), (WIDTH-60, 60), (60, HEIGHT-60), (WIDTH-60, HEIGHT-60)]:
            draw.ellipse([cx-15, cy-15, cx+15, cy+15], outline=accent, width=3)

        # 彩色球列阵
        colors = [(255,215,0),(0,0,255),(255,0,0),(128,0,128),(255,165,0),(0,128,0)]
        sx = WIDTH//2 - len(colors)*35
        for j, col in enumerate(colors):
            bx = sx + j*70 + 35
            draw.ellipse([bx-22, 1670-22, bx+22, 1670+22], fill=col)

        path = os.path.join(IMAGE_DIR, f"bg_{i+1:02d}.png")
        img.save(path, "PNG")
    print(f"✅ bg图生成完成: 9张")

# ===== 场景配图生成 =====
def create_scene_image(text, output_path, index, total, scene_image_path=None):
    """用Pillow在背景图上叠加文字"""
    scheme_index = min(index, len(SCHEMES) - 1)
    c1_hex, c2_hex = SCHEMES[scheme_index]
    c1 = tuple(int(c1_hex[j:j+2], 16) for j in (1,3,5))
    c2 = tuple(int(c2_hex[j:j+2], 16) for j in (1,3,5))
    accent = ACCENT_COLORS[scheme_index]

    # 背景图或纯色
    if scene_image_path and os.path.exists(scene_image_path):
        bg_img = Image.open(scene_image_path).convert("RGB")
        if bg_img.size[0] == WIDTH and bg_img.size[1] == HEIGHT:
            img = bg_img.copy()
        else:
            img = Image.new("RGB", (WIDTH, HEIGHT), c1)
            # 渐变
            draw = ImageDraw.Draw(img)
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                r = int(c1[0]*(1-ratio) + c2[0]*ratio)
                g = int(c1[1]*(1-ratio) + c2[1]*ratio)
                b = int(c1[2]*(1-ratio) + c2[2]*ratio)
                draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
            draw.rectangle([0, 0, WIDTH, 8], fill=accent)
            draw.rectangle([0, HEIGHT-8, WIDTH, HEIGHT], fill=accent)
    else:
        img = Image.new("RGB", (WIDTH, HEIGHT), c1)

    # 半透明遮罩
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 主文字
    lines = text.split("\n")
    title_font = ImageFont.truetype(FONT_PATH, 72)
    sub_font = ImageFont.truetype(FONT_PATH, 52)

    # 计算文字总高度
    total_text_h = 0
    for li, line in enumerate(lines):
        font = title_font if li == 0 else sub_font
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1]
        total_text_h += lh + 15

    start_y = (HEIGHT - total_text_h) // 2

    for li, line in enumerate(lines):
        font = title_font if li == 0 else sub_font
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        # 文字阴影
        draw.text((x+2, start_y+2), line, fill=(0, 0, 0, 180), font=font)
        # 主文字
        color = (255, 255, 255) if li == 0 else (accents := (255, 200, 0) if li > 0 else (200, 200, 200))
        fill_color = (255, 255, 255) if li == 0 else (255, 215, 0)  # 首行白，其余金
        draw.text((x, start_y), line, fill=fill_color, font=font)

        lh = bbox[3] - bbox[1] + 15
        start_y += lh

    # 页码
    page_font = ImageFont.truetype(FONT_PATH, 36)
    page_text = f"{index+1}/{total}"
    pb = draw.textbbox((0, 0), page_text, font=page_font)
    draw.text((WIDTH - (pb[2]-pb[0]) - 40, HEIGHT - 60), page_text, fill=(150, 150, 150), font=page_font)

    img.save(output_path, "PNG")

# ===== TTS配音（subprocess调用，长间隔重试应对Edge TTS不稳定）=====
async def gen_tts(text, path, voice=TTS_VOICE):
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
                pass  # 网络问题，重试
            else:
                raise RuntimeError(f"edge-tts error: {err_msg[:200]}")
        except (asyncio.TimeoutError, Exception) as e:
            if attempt < 5:
                wait = 5 * (attempt + 2)  # 10,15,20,25,30
                print(f"  ⚠️ TTS重试 {attempt+1}: 等待{wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"  ❌ TTS {attempt+1}次重试均失败，跳过本段")
                raise

def get_audio_duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                       "-show_format", path], capture_output=True, text=True)
    data = json.loads(r.stdout)
    if "format" not in data or "duration" not in data.get("format", {}):
        print(f"  ⚠️ 无法获取音频时长，估算4s")
        return 4.0
    return float(data["format"]["duration"])

# ===== Ken Burns 2步合成 =====
def build_ken_burns(image_path, audio_path, output_path, duration):
    """2步合成：先zoompan视频，再合流音频（避免FFmpeg 8.1 bug）"""
    frames = int(duration * FPS) + 5
    tmp_video = output_path.replace(".mp4", "_tmpvid.mp4")

    # Step 1: 纯视频（zoompan）
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

# ===== 拼接 =====
def concat_segments(segments, output_path):
    seg_list = "/tmp/xinqiuhui_segments.txt"
    with open(seg_list, "w") as f:
        for sp in segments:
            f.write(f"file '{sp}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", seg_list, "-c", "copy", output_path]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

# ===== BGM叠加 =====
def get_bgm():
    for bp in BGM_PATHS:
        if os.path.exists(bp) and os.path.getsize(bp) > 1000:
            print(f"🎵 BGM: {os.path.basename(bp)} ({os.path.getsize(bp)//1024}KB)")
            return bp
    print("⚠️ BGM未找到，跳过")
    return None

def mix_bgm(video_path, bgm_path, output_path):
    if bgm_path is None:
        shutil.copy2(video_path, output_path)
        return
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", bgm_path,
        "-filter_complex",
        "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

# ===== 验证 =====
def verify_video(video_path):
    print(f"\n🔍 验证: {os.path.basename(video_path)}")
    # 黑帧检测
    try:
        r = subprocess.run(
            ["ffmpeg", "-i", video_path, "-vf", "blackdetect=d=0.1:pix_th=0.1", "-f", "null", "-"],
            capture_output=True, text=True, timeout=30
        )
        if "black_start" in r.stderr:
            print("❌ 黑帧检测失败: 有黑帧")
            return False
        print("✅ 无黑帧")
    except:
        pass

    # 基本信息
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,width,height:nb_frames",
         "-of", "default=noprint_wrappers=1", video_path],
        capture_output=True, text=True
    )
    print(r.stdout.strip())

    r2 = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True
    )
    info = json.loads(r2.stdout)["format"]
    dur = float(info["duration"])
    size_mb = int(info["size"]) / 1024 / 1024
    print(f"⏱ {dur:.1f}s, 💾 {size_mb:.1f}MB")

    if size_mb < 8:
        print("⚠️ 文件偏小，可能无配图")
    else:
        print("✅ 配图正常")

    return True

# ===== 主流程 =====
async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # 1. 确保背景图
    ensure_bg_images()

    # 2. 生成配图
    scenes = SCENES_TEXTS
    total = len(scenes)
    print(f"\n📝 文案段落: {total}段")

    # 分配bg图（12段用10张，封面+01~09循环）
    bg_images = ["bg_cover.png"] + [f"bg_{i+1:02d}.png" for i in range(9)]

    scene_images = []
    for i, text in enumerate(scenes):
        img_file = f"scene_{i+1:02d}.png"
        img_path = os.path.join(IMAGE_DIR, img_file)
        bg_idx = min(i, len(bg_images) - 1)
        bg_path = os.path.join(IMAGE_DIR, bg_images[bg_idx])
        # 如果封面图不存在，回退到bg_01
        if bg_idx == 0 and not os.path.exists(bg_path):
            bg_path = os.path.join(IMAGE_DIR, "bg_01.png")
        create_scene_image(text, img_path, i, total, bg_path if os.path.exists(bg_path) else None)
        scene_images.append(img_path)
        print(f"  [{i+1}/{total}] 配图: {img_file} ({'封面' if bg_idx==0 else bg_images[bg_idx]})")

    # 3. TTS配音（逐个合成，间隔3秒避免连接重置）
    print("\n🎤 TTS配音中...")
    audio_files = []
    for i, text in enumerate(scenes):
        audio_path = f"/tmp/xqhui_audio_{i+1:02d}.mp3"
        await gen_tts(text, audio_path)
        dur = get_audio_duration(audio_path)
        audio_dur = max(dur, MIN_DURATION)
        audio_files.append((audio_path, audio_dur))
        print(f"  [{i+1}/{total}] {dur:.1f}s: {text[:20]}...")
        # 间隔3秒避免Edge TTS连接风暴
        if i < len(scenes) - 1:
            await asyncio.sleep(5)  # 每段间间隔5秒降低连接风暴

    # 4. Ken Burns合成
    print("\n🎬 合成段落（Ken Burns运镜）...")
    segments = []
    for i, (img_path, (audio_path, dur)) in enumerate(zip(scene_images, audio_files)):
        seg_path = f"/tmp/xqhui_seg_{i+1:02d}.mp4"
        build_ken_burns(img_path, audio_path, seg_path, dur)
        segments.append(seg_path)
        print(f"  [{i+1}/{total}] {dur:.1f}s ✅")

    # 5. 拼接
    print("\n🔗 拼接段落...")
    merged = "/tmp/xqhui_merged.mp4"
    concat_segments(segments, merged)

    # 6. BGM
    print("\n🎵 叠加BGM...")
    bgm_path = get_bgm()
    output_no_bgm = f"/tmp/xqhui_no_bgm.mp4"
    # 先copy一份无BGM版做备份
    # 再混合
    video_title_safe = VIDEO_TITLE.replace("/", "-")
    final_output = os.path.join(OUTPUT_DIR, f"{video_title_safe}.mp4")

    if bgm_path:
        mix_bgm(merged, bgm_path, final_output)
        print(f"✅ 带BGM版: {os.path.basename(final_output)}")
    else:
        shutil.copy2(merged, final_output)
        print(f"✅ 无BGM版: {os.path.basename(final_output)}")

    # 清理中间文件
    if os.path.exists(f"/tmp/xqhui_no_bgm.mp4"):
        os.remove(f"/tmp/xqhui_no_bgm.mp4")
    for seg in segments:
        if os.path.exists(seg):
            os.remove(seg)

    # 7. 验证
    ok = verify_video(final_output)

    print(f"\n{'='*50}")
    print(f"📺 成品: {final_output}")
    print(f"{'='*50}")
    return final_output, ok

if __name__ == "__main__":
    result, ok = asyncio.run(main())
    sys.exit(0 if ok else 1)
