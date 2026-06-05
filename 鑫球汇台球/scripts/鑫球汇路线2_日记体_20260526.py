#!/usr/bin/env python3
"""
鑫球汇台球俱乐部 - 路线2：日记体
辞职开台球厅第12天-女高中生放学就来练球-鑫球汇
周二 2026-05-26
"""

import os, sys, subprocess, json, asyncio, shutil, math

# ── 自动安装依赖 ──
try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont

try:
    import edge_tts
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
    import edge_tts

# ── 字体路径自动检测 ──
FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]
FONT_PATH = next((fp for fp in FONT_CANDIDATES if os.path.exists(fp)), None)
if not FONT_PATH:
    raise FileNotFoundError("No Chinese font found on system")
print(f"📝 字体: {os.path.basename(FONT_PATH)}")

# ── 目录设置 ──
BASE_DIR = os.path.expanduser("~/Desktop")
IMAGE_DIR = os.path.join(BASE_DIR, "鑫球汇图片素材")
OUTPUT_DIR = os.path.join(BASE_DIR, "鑫球汇视频")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 确保背景图存在 ──
def ensure_bg_images():
    """自恢复bg_01~09.png + bg_cover.png"""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    if os.path.exists(os.path.join(IMAGE_DIR, "bg_01.png")):
        return
    print("  🎨 生成装饰背景图...")
    schemes = [("#1a1a2e","#16213e"),("#0f3460","#1a1a2e"),
               ("#2c3e50","#1a252f"),("#1b4332","#081c15"),
               ("#4a1c40","#2d0a28"),("#3c096c","#10002b"),
               ("#7f2d0f","#3e1305"),("#0c3547","#051a26"),
               ("#1a1a2e","#0f3460")]
    accents = [(255,200,0),(100,200,255),(200,150,255),
               (100,255,150),(255,150,200),(255,180,50),
               (150,200,255),(255,100,100),(255,200,100)]
    for i in range(9):
        c1, c2 = schemes[i]; accent = accents[i]
        img = Image.new("RGB", (1080,1920), c1)
        draw = ImageDraw.Draw(img)
        for y in range(1920):
            ratio = y/1920
            r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
            r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
            r = int(r1*(1-ratio) + r2*ratio)
            g = int(g1*(1-ratio) + g2*ratio)
            b = int(b1*(1-ratio) + b2*ratio)
            draw.line([(0,y),(1080,y)], fill=(r,g,b))
        draw.rectangle([0,0,1080,8], fill=accent)
        draw.rectangle([0,1912,1080,1920], fill=accent)
        for cx,cy in [(60,60),(1020,60),(60,1860),(1020,1860)]:
            draw.ellipse([cx-15,cy-15,cx+15,cy+15], outline=accent, width=3)
        colors = [(255,215,0),(0,0,255),(255,0,0),(128,0,128),(255,165,0),(0,128,0)]
        sx = 1080//2 - len(colors)*35
        for j, col in enumerate(colors):
            bx = sx + j*70 + 35
            draw.ellipse([bx-22,1670-22,bx+22,1670+22], fill=col)
        img.save(os.path.join(IMAGE_DIR, f"bg_{i+1:02d}.png"), "PNG")
    # 封面
    cover = Image.new("RGB", (1080,1920), (13,27,42))
    draw = ImageDraw.Draw(cover)
    draw.rectangle([0,0,1080,10], fill=(201,169,78))
    draw.rectangle([0,1910,1080,1920], fill=(201,169,78))
    cx,cy = 540,760
    draw.ellipse([cx-80,cy-80,cx+80,cy+80], fill=(255,255,255), outline=(0,0,0), width=3)
    draw.ellipse([cx-38,cy-38,cx+38,cy+38], fill=(0,0,0))
    draw.ellipse([cx-90,cy-90,cx+90,cy+90], outline=(201,169,78), width=3)
    colors2 = [(255,215,0),(0,0,255),(255,0,0),(128,0,128),(255,165,0),(0,128,0),(255,20,147),(0,0,0)]
    sx2 = 1080//2 - len(colors2)*30
    for j, col in enumerate(colors2):
        bx = sx2 + j*60 + 30
        draw.ellipse([bx-18,1840-18,bx+18,1840+18], fill=col)
    cover.save(os.path.join(IMAGE_DIR, "bg_cover.png"), "PNG")
    print(f"  ✅ 生成 {sum(1 for f in ['bg_01.png','bg_02.png','bg_03.png','bg_04.png','bg_05.png','bg_06.png','bg_07.png','bg_08.png','bg_09.png','bg_cover.png'] if os.path.exists(os.path.join(IMAGE_DIR,f)))}/10 张背景图")

ensure_bg_images()

# ── BGM检查 ──
BGM_PATHS = [
    os.path.join(IMAGE_DIR, "bgm_01.wav"),
    os.path.join(IMAGE_DIR, "bgm_02.wav"),
    "/tmp/bgm_snooker.mp3",
]
def get_bgm():
    for p in BGM_PATHS:
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            print(f"  🎵 BGM: {os.path.basename(p)} ({os.path.getsize(p)//1024}KB)")
            return p
    print("  🎵 BGM: 无")
    return None

BGM_PATH = get_bgm()

# ── 视频参数 ──
FPS = 30
RES = (1080, 1920)

# ── 路线2：日记体 ──
# 主题：女高中生放学就来练球
VIDEO_TITLE = "辞职开台球厅第12天-女高中生放学就来练球-鑫球汇"

SCENES = [
    {
        "text": "辞职开台球厅第12天\n来了个每天放学必到的女高中生",
        "img": "bg_cover.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "每天下午五点半准时推门进来\n书包往角落一放就开始练球",
        "img": "bg_01.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "最开始我以为她只是放学来玩\n后来发现她练的是真基本功",
        "img": "bg_02.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "光一个直线球反复站同一个位置\n练定点入袋，一练就是一小时",
        "img": "bg_03.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "我问她为什么这么拼命\n她说想考体育特长生，台球是她的路",
        "img": "bg_04.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "她家条件不太好\n买不起专业球杆，用的是厅里的公用杆",
        "img": "bg_05.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "但她的准度已经超过很多成年业余选手了\n专注的样子让人动容",
        "img": "bg_06.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "我让她免费练，给她留了固定台位\n还送了她一根入门级小头杆",
        "img": "bg_07.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
    {
        "text": "她说将来打比赛了一定回来报答\n这就是开台球厅最暖心的时刻",
        "img": "bg_08.png",
        "voice": "zh-CN-XiaoxiaoNeural"
    },
]

# ⚠️ P0检查：文案零「/」
for i, s in enumerate(SCENES):
    assert "/" not in s["text"], f"SCENE[{i}] 包含 '/' 字符！"
print("✅ 文案零「/」检查通过")

# ── 场景图片生成 ──
def create_scene_image(scene, idx):
    """Pillow生成带文字的配图"""
    bg_name = scene["img"]
    bg_path = os.path.join(IMAGE_DIR, bg_name)

    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGB")
        # 如果是bg_cover.png，不做额外装饰（保留AI图干净）
        if bg_name == "bg_cover.png":
            pass
        else:
            # 半透明黑色遮罩确保文字可读
            overlay = Image.new("RGBA", img.size, (0,0,0,0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([0,0,img.width,img.height], fill=(0,0,0,100))
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    else:
        # 回退纯色背景
        print(f"  ⚠️ 图片不存在: {bg_path}, 回退纯色")
        img = Image.new("RGB", RES, (26,26,46))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0,0,1080,8], fill=(201,169,78))
        draw.rectangle([0,1912,1080,1920], fill=(201,169,78))

    draw = ImageDraw.Draw(img)

    # 左上角品牌名
    try:
        small_font = ImageFont.truetype(FONT_PATH, 28)
        draw.text((40, 40), "鑫球汇台球俱乐部", fill=(201,169,78), font=small_font)
    except:
        pass

    # 主文字（大号，居中）
    lines = scene["text"].split("\n")
    font_size = 56 if len(lines) <= 2 else 48
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except:
        font = ImageFont.load_default()

    # 每行文字居中
    line_height = font_size + 20
    total_h = len(lines) * line_height
    start_y = (1920 - total_h) // 2 - 100

    for i_line, line in enumerate(lines):
        # 金色高亮处理：如果是最后一段且包含团购，用金色
        is_coupon = idx >= len(SCENES) - 2 and "团购" in line
        is_cta = idx == len(SCENES) - 1

        if i_line == 0 and len(lines) > 1:
            # 标题行用稍大字体
            try:
                title_font = ImageFont.truetype(FONT_PATH, font_size + 8)
            except:
                title_font = font
            bbox = draw.textbbox((0,0), line, font=title_font)
            tw = bbox[2] - bbox[0]
            tx = (1080 - tw) // 2
            draw.text((tx, start_y + i_line * line_height), line, fill=(255,255,255), font=title_font)
        elif is_coupon or is_cta:
            bbox = draw.textbbox((0,0), line, font=font)
            tw = bbox[2] - bbox[0]
            tx = (1080 - tw) // 2
            draw.text((tx, start_y + i_line * line_height), line, fill=(255,215,0), font=font)
        else:
            bbox = draw.textbbox((0,0), line, font=font)
            tw = bbox[2] - bbox[0]
            tx = (1080 - tw) // 2
            draw.text((tx, start_y + i_line * line_height), line, fill=(255,255,255), font=font)

    # 页面左下角页码
    try:
        page_font = ImageFont.truetype(FONT_PATH, 24)
        draw.text((40, 1860), f"{idx+1}/{len(SCENES)}", fill=(180,180,180), font=page_font)
    except:
        pass

    out_path = os.path.join(IMAGE_DIR, f"scene_{idx+1:02d}.png")
    img.save(out_path, "PNG")
    return out_path

print("\n🎨 生成场景配图...")
scene_images = []
for idx, scene in enumerate(SCENES):
    path = create_scene_image(scene, idx)
    scene_images.append(path)
    print(f"  ✅ {idx+1}/{len(SCENES)}: {os.path.basename(path)}")

# ── Edge TTS 配音生成 ──
async def gen_tts(text, path, voice="zh-CN-XiaoxiaoNeural"):
    """Edge TTS配音，含网络重试"""
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
                # 获取时长
                r = await asyncio.create_subprocess_exec(
                    "ffprobe", "-v", "quiet", "-print_format", "json",
                    "-show_format", path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                out, _ = await r.communicate()
                data = json.loads(out.decode())
                dur = float(data["format"]["duration"])
                return dur
            err_msg = stderr.decode() if stderr else ""
            if "Connection reset" in err_msg or "Cannot connect" in err_msg:
                pass  # 网络问题，重试
            else:
                raise RuntimeError(f"edge-tts error: {err_msg[:200]}")
        except (asyncio.TimeoutError, Exception) as e:
            if attempt < 5:
                wait = 5 * (attempt + 2)  # 10,15,20,25,30
                print(f"  ⚠️ TTS重试 {attempt+1}: 等待{wait}s... (错误: {str(e)[:60]})")
                await asyncio.sleep(wait)
            else:
                raise
    raise RuntimeError(f"TTS failed after 6 attempts")

async def gen_all_tts():
    """并行生成所有配音"""
    print("\n🎤 生成配音...")
    audio_dir = os.path.join(OUTPUT_DIR, "audio_tmp")
    os.makedirs(audio_dir, exist_ok=True)

    tasks = []
    for idx, scene in enumerate(SCENES):
        text = scene["text"]
        voice = scene.get("voice", "zh-CN-XiaoxiaoNeural")
        out_path = os.path.join(audio_dir, f"audio_{idx+1:02d}.mp3")
        tasks.append(gen_tts(text, out_path, voice))

    # 顺序执行（每条之间加5秒间隔降低连接风暴）
    durations = []
    for idx, task in enumerate(tasks):
        try:
            dur = await task
            durations.append(dur)
            print(f"  ✅ {idx+1}/{len(tasks)}: {dur:.1f}s")
        except Exception as e:
            print(f"  ❌ {idx+1}/{len(tasks)}: {e}")
            raise
        if idx < len(tasks) - 1:
            await asyncio.sleep(5)  # 间隔防限流

    return durations

audio_durations = asyncio.run(gen_all_tts())
audio_dir = os.path.join(OUTPUT_DIR, "audio_tmp")
print(f"  📊 总时长: {sum(audio_durations):.1f}s")

# ── Ken Burns 视频段落合成 ──
def build_segment(image_path, audio_path, output_path, duration):
    """2步合成：先zoompan视频，再合流音频"""
    # Step 1: zoompan视频（无音频）
    tmp_video = output_path.replace(".mp4", "_tmpvid.mp4")
    frames = max(int(duration * FPS), 30)

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
    r1 = subprocess.run(cmd1, capture_output=True, text=True)
    if r1.returncode != 0:
        print(f"  ⚠️ Step 1 zoompan失败: {r1.stderr[:200]}")
        # 回退：静帧无zoompan
        cmd1_fallback = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-c:v", "libx264", "-preset", "medium", "-b:v", "8M",
            "-pix_fmt", "yuv420p", "-r", str(FPS), "-an",
            "-t", str(duration + 0.5), "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            tmp_video
        ]
        subprocess.run(cmd1_fallback, check=True, capture_output=True, text=True)

    # Step 2: 合流音频
    cmd2 = [
        "ffmpeg", "-y",
        "-i", tmp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", output_path
    ]
    subprocess.run(cmd2, check=True, capture_output=True, text=True)

    # 清理
    if os.path.exists(tmp_video):
        os.remove(tmp_video)

# ── 合成所有段落 ──
print("\n🎬 Ken Burns合成段落...")
segments_dir = os.path.join(OUTPUT_DIR, "segments_tmp")
os.makedirs(segments_dir, exist_ok=True)

segment_files = []
for idx, (scene, dur) in enumerate(zip(SCENES, audio_durations)):
    img_path = scene_images[idx]
    aud_path = os.path.join(audio_dir, f"audio_{idx+1:02d}.mp3")
    out_path = os.path.join(segments_dir, f"seg_{idx+1:02d}.mp4")
    build_segment(img_path, aud_path, out_path, dur)
    segment_files.append(out_path)
    print(f"  ✅ {idx+1}/{len(SCENES)}: {dur:.1f}s -> {os.path.basename(out_path)}")

# ── 拼接段落 ──
print("\n🔗 拼接段落...")
concat_file = os.path.join(OUTPUT_DIR, "segments.txt")
with open(concat_file, "w") as f:
    for sp in segment_files:
        f.write(f"file '{sp}'\n")

merged_video = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_no_bgm.mp4")
cmd_concat = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_file, "-c", "copy", merged_video
]
subprocess.run(cmd_concat, check=True, capture_output=True, text=True)

# ── 叠加BGM ──
if BGM_PATH:
    print(f"\n🎵 叠加BGM...")
    final_video = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
    cmd_bgm = [
        "ffmpeg", "-y",
        "-i", merged_video,
        "-i", BGM_PATH,
        "-filter_complex",
        "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        final_video
    ]
    subprocess.run(cmd_bgm, check=True, capture_output=True, text=True)
    # 清理_no_bgm中间文件
    if os.path.exists(merged_video):
        os.remove(merged_video)
        print("  🧹 已清理_no_bgm中间文件")
else:
    print("\n🎵 BGM: 无BGM，使用纯配音版")
    # 去掉_no_bgm后缀
    clean_name = merged_video.replace("_no_bgm.mp4", ".mp4")
    if clean_name != merged_video:
        shutil.move(merged_video, clean_name)
        final_video = clean_name
    else:
        final_video = merged_video
    print(f"   最终文件: {os.path.basename(final_video)}")

# ── 清理中间文件 ──
print("\n🧹 清理中间文件...")
if os.path.exists(concat_file):
    os.remove(concat_file)
if os.path.exists(audio_dir):
    shutil.rmtree(audio_dir)
if os.path.exists(segments_dir):
    shutil.rmtree(segments_dir)
print("  ✅ 清理完成")

# ── 验证 ──
print("\n🔍 验证输出...")

# 检查黑帧
r_black = subprocess.run(
    ["ffmpeg", "-i", final_video, "-vf", "blackdetect=d=0.1:pix_th=0.1", "-f", "null", "-"],
    capture_output=True, text=True
)
if "black_start" in r_black.stderr:
    print(f"  ❌ 检测到黑帧!")
    print(r_black.stderr[:200])
else:
    print("  ✅ 无黑帧")

# 检查分辨率
r_probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,nb_frames",
     "-of", "default=noprint_wrappers=1", final_video],
    capture_output=True, text=True
)
for line in r_probe.stdout.strip().split("\n"):
    print(f"  📊 {line}")

# 文件大小
fsize = os.path.getsize(final_video)
print(f"  💾 大小: {fsize/1024/1024:.1f}MB")

# 总时长
r_fmt = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", final_video],
    capture_output=True, text=True
)
fmt_data = json.loads(r_fmt.stdout)
total_dur = float(fmt_data["format"]["duration"])
print(f"  ⏱️  时长: {total_dur:.1f}s")

print(f"\n✅ 完成！输出: {final_video}")
print(f"   文件名: {VIDEO_TITLE}.mp4")
