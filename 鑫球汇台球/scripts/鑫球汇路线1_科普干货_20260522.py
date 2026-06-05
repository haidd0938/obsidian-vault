#!/usr/bin/env python3
"""鑫球汇路线1：科普干货 — 台球高手才懂的5个击球技巧
周五 (2026-05-22) cron生产
v3.1风格：Ken Burns运镜 + 封面字卡 + 8M码率
"""

import os, sys, subprocess, json, shutil, asyncio, re, glob

# === Auto-install deps ===
for pkg in ["Pillow", "edge-tts"]:
    try:
        __import__(pkg.replace("-", "_").replace(".", ""))
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

from PIL import Image, ImageDraw, ImageFont
import edge_tts

# ===================== CONFIG =====================
VIDEO_TITLE = "台球高手才懂的5个击球技巧-鑫球汇"
OUTPUT_DIR = os.path.expanduser("~/Desktop/鑫球汇视频")
IMAGE_DIR = os.path.expanduser("~/Desktop/鑫球汇图片素材")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920  # 竖屏
FPS = 30

# 字体路径
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_SM = 48   # 副标题/描述
FONT_MD = 64   # 正文
FONT_LG = 80   # 大标题
FONT_XL = 100  # 封面标题

# TTS声线 — 路线1: 晓晓女声（温柔讲解感）
TTS_VOICE = "zh-CN-XiaoxiaoNeural"

# ==================== SCENES ====================
# 路线1：科普干货（知识向）
# 结构: Hook(痛点提问) + 5个知识点 + CTA引流
# 文案零「/」检查（P0级）
SCENES = [
    {
        "text": "打台球这么多年\n为什么你的水平一直上不去？",
        "img": "bg_cover.png"
    },
    {
        "text": "第一：握杆姿势不对\n很多人握杆太紧\n导致出杆不直",
        "img": "bg_01.png"
    },
    {
        "text": "第二：瞄准靠感觉\n真正的瞄准不是用眼睛\n而是用身体去对准",
        "img": "bg_02.png"
    },
    {
        "text": "第三：发力太僵硬\n高手用的是柔和的发力\n让球杆自然穿透母球",
        "img": "bg_03.png"
    },
    {
        "text": "第四：不重视走位\n只看进袋不管母球停哪\n永远不会连续得分",
        "img": "bg_04.png"
    },
    {
        "text": "第五：不练基本功\n天天打花球 不练基础\n白球控制永远是硬伤",
        "img": "bg_05.png"
    },
    {
        "text": "这五个技巧你中了几条\n来鑫球汇练一练\n我们一起提升",
        "img": "bg_09.png"
    },
    {
        "text": "鑫球汇台球俱乐部\n秦州万达B1层\n团购有优惠 一卡打到爽",
        "img": "bg_cover.png"
    }
]

# ============ Pillow 场景配图生成 ============
FONT_CACHE = {}
def get_font(size):
    if size not in FONT_CACHE:
        FONT_CACHE[size] = ImageFont.truetype(FONT_PATH, size)
    return FONT_CACHE[size]

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_scene_image(scene_data, output_path):
    """生成配图（背景+装饰+半透明遮罩+文字）"""
    img_name = scene_data["img"]
    img_path = os.path.join(IMAGE_DIR, img_name)
    
    if os.path.exists(img_path):
        bg = Image.open(img_path).convert("RGB")
        # 如果尺寸不对则resize
        if bg.size != (W, H):
            bg = bg.resize((W, H), Image.LANCZOS)
        img = bg.copy()
    else:
        # fallback纯色
        img = Image.new("RGB", (W, H), (26, 26, 46))
    
    draw = ImageDraw.Draw(img)
    text = scene_data["text"]
    
    # 半透明黑色遮罩（保证文字在任何背景上都清晰）
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([0, 200, W, H-200], fill=(0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # 分割多行文本
    lines = text.split("\n")
    
    # 根据行数和内容确定字体大小
    # 如果是封面段(bg_cover.png)用大号字体
    is_cover = (img_name == "bg_cover.png" and lines[0].startswith("打台球"))
    is_cta = ("团购" in text or "鑫球汇台球俱乐部" in text)
    
    if is_cover:
        font_size = FONT_XL
    elif is_cta and len(text) < 20:
        font_size = FONT_LG
    elif len(lines) <= 2:
        font_size = FONT_LG
    else:
        font_size = FONT_MD
    
    font = get_font(font_size)
    
    # 计算总文字块高度
    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        total_h += (bbox[3] - bbox[1]) + 15
    
    # 从中心偏上开始画
    start_y = (H - total_h) // 2 - 50
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        x = (W - lw) // 2
        # 文字阴影
        draw.text((x+2, start_y+2), line, font=font, fill=(0, 0, 0, 160))
        draw.text((x, start_y), line, font=font, fill=(255, 255, 255))
        start_y += lh + 15
    
    # 底部品牌标识 + 页码
    if not is_cta:
        draw.text((30, H-80), "鑫球汇台球俱乐部", font=get_font(36), fill=(180, 180, 180))
    
    img.save(output_path, "PNG")

# ============ Edge TTS 配音 ============
async def gen_tts(text, output_path):
    """生成TTS配音，返回时长"""
    c = edge_tts.Communicate(text, TTS_VOICE, rate="-5%")
    await c.save(output_path)
    # 获取时长
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json",
                       "-show_format", output_path], capture_output=True, text=True)
    data = json.loads(r.stdout)
    return float(data["format"]["duration"])

# ============ Ken Burns 视频段合成 ============
def build_segment(image_path, audio_path, output_path, duration):
    """生成带Ken Burns缩放+平移效果的视频段
    
    两步法：先用zoompan生成无音频视频，再合流音频输入
    避免zoompan+音频输入的选项顺序冲突
    """
    frames = int(duration * FPS)
    tmp_video = output_path.replace(".mp4", "_tmpvid.mp4")
    
    # Step 1: 生成zoompan视频（无音频）
    cmd1 = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-filter_complex",
        f"[0:v]scale=1920:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z='if(eq(on,1),1.0,1.0+0.003*(on-1))':d={frames}:s=1080x1920"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'[v]",
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "medium",
        "-b:v", "8M",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-an",
        "-t", str(duration + 0.5),  # 给点余量
        tmp_video
    ]
    subprocess.run(cmd1, check=True, capture_output=True, text=True)
    
    # Step 2: 合流音频
    cmd2 = [
        "ffmpeg", "-y",
        "-i", tmp_video,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd2, check=True, capture_output=True, text=True)
    
    # 清理tmp
    if os.path.exists(tmp_video):
        os.remove(tmp_video)

# ============ BGM叠加 ============
# BGM路径检查（持久化路径优先）
BGM_PATHS = [
    os.path.expanduser("~/Desktop/鑫球汇图片素材/bgm_01.wav"),
    os.path.expanduser("~/Desktop/鑫球汇图片素材/bgm_02.wav"),
    "/tmp/bgm_snooker.mp3",
    "/tmp/bgm_ambient.mp3",
]

def get_bgm():
    for p in BGM_PATHS:
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    return None

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

# ============ 主流程 ============
async def main():
    print(f"=== 鑫球汇路线1 科普干货 ({VIDEO_TITLE}) ===")
    print(f"日期: 2026-05-22, 星期五")
    
    # Step 1: 生成场景配图
    print("\n[1/5] 生成场景配图...")
    os.makedirs(os.path.join(OUTPUT_DIR, "素材图片_20260522"), exist_ok=True)
    img_paths = []
    for i, scene in enumerate(SCENES):
        out = os.path.join(OUTPUT_DIR, f"素材图片_20260522", f"scene_{i+1:02d}.png")
        create_scene_image(scene, out)
        img_paths.append(out)
        print(f"  scene_{i+1:02d}.png ✅")
    
    # Step 2: 生成TTS配音
    print("\n[2/5] 生成TTS配音...")
    audio_dir = "/tmp/xinqiuhui_audio_20260522"
    os.makedirs(audio_dir, exist_ok=True)
    audio_paths = []
    durations = []
    total_dur = 0
    
    for i, scene in enumerate(SCENES):
        out = os.path.join(audio_dir, f"audio_{i+1:02d}.mp3")
        text = scene["text"].replace("\n", "，")
        dur = await gen_tts(text, out)
        audio_paths.append(out)
        durations.append(dur)
        total_dur += dur
        print(f"  audio_{i+1:02d}.mp3: {dur:.1f}s")
    
    print(f"  总配音时长: {total_dur:.1f}s")
    
    # Step 3: 合成段落
    print("\n[3/5] 合成各段视频（Ken Burns运镜）...")
    seg_dir = "/tmp/xinqiuhui_seg_20260522"
    os.makedirs(seg_dir, exist_ok=True)
    seg_paths = []
    
    for i in range(len(SCENES)):
        out = os.path.join(seg_dir, f"seg_{i+1:02d}.mp4")
        try:
            build_segment(img_paths[i], audio_paths[i], out, durations[i])
            seg_paths.append(out)
            sz = os.path.getsize(out)
            print(f"  seg_{i+1:02d}.mp4: {durations[i]:.1f}s, {sz/1024/1024:.1f}MB ✅")
        except subprocess.CalledProcessError as e:
            print(f"  seg_{i+1:02d} 失败: {e.stderr[-500:]}")
            raise
    
    # Step 4: 拼接
    print("\n[4/5] 拼接各段...")
    concat_path = "/tmp/xinqiuhui_merged_20260522.mp4"
    
    # 写segments.txt
    seg_list_path = "/tmp/xinqiuhui_segments_20260522.txt"
    with open(seg_list_path, "w") as f:
        for sp in seg_paths:
            f.write(f"file '{sp}'\n")
    
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", seg_list_path, "-c", "copy", concat_path
    ], check=True, capture_output=True, text=True)
    print(f"  拼接完成: {os.path.getsize(concat_path)/1024/1024:.1f}MB")
    
    # Step 5: BGM叠加
    print("\n[5/5] 叠加BGM...")
    output_no_bgm = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_no_bgm.mp4")
    output_final = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
    
    # 先复制一份无BGM版（作为备份）
    shutil.copy2(concat_path, output_no_bgm)
    
    bgm = get_bgm()
    if bgm:
        print(f"  找到BGM: {bgm}")
        mix_bgm(concat_path, bgm, output_final)
        print(f"  BGM叠加完成 ✅")
        # 清理无BGM中间文件
        if os.path.exists(output_no_bgm):
            os.remove(output_no_bgm)
            print(f"  已清理无BGM中间文件")
    else:
        print(f"  无BGM文件，交付纯配音版")
        shutil.copy2(concat_path, output_final)
    
    # 清理 /tmp 中间文件
    for d in [audio_dir, seg_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
    for f in [concat_path, seg_list_path]:
        if os.path.exists(f):
            os.remove(f)
    print(f"  已清理临时文件")
    
    # 最终验证
    print(f"\n=== 最终成品 ===")
    print(f"路径: {output_final}")
    sz = os.path.getsize(output_final)
    print(f"大小: {sz/1024/1024:.1f}MB")
    
    # 检查分辨率
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                       "-show_entries", "stream=width,height,codec_name",
                       "-of", "default=noprint_wrappers=1", output_final],
                      capture_output=True, text=True)
    print(f"编码: {r.stdout.strip()}")
    
    # 黑帧检测
    r = subprocess.run([
        "ffmpeg", "-i", output_final,
        "-vf", "blackdetect=d=0.1:pix_th=0.1",
        "-f", "null", "-"
    ], capture_output=True, text=True)
    if "black_start" in r.stderr:
        print("⚠️ 黑帧检测: 检测到黑帧!")
        print(r.stderr[-300:])
    else:
        print("黑帧检测: ✅ 无黑帧")
    
    print(f"\n✅ 生产完成!")
    return output_final

if __name__ == "__main__":
    result = asyncio.run(main())
