#!/usr/bin/env python3
"""
东盛建筑设计短视频合成器 v2.0
Pillow生成配图 + Edge TTS配音 + 免费BGM = 竖屏短视频
不需要drawtext滤镜，解决黑屏问题
"""
import asyncio, json, os, subprocess, tempfile
from pathlib import Path
import edge_tts

# ====== 可配置区域 ======
VIDEO_TITLE = "EPC模式的三个致命陷阱"
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 EPC总承包"
TTS_VOICE = "zh-CN-YunjianNeural"
MIN_DURATION = 5.0
WIDTH, HEIGHT = 1080, 1920
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")
IMAGE_DIR = os.path.expanduser("~/Desktop/东盛建筑视频/素材图片")

# 配音文案（与配图对应）
SCENES_TEXTS = [
    "EPC总承包，听着高大上，但很多老板第一个工程就栽了。",
    "第一个陷阱：设计阶段不控造价，施工时才发现超预算。EPC的核心是设计牵头，设计定下来，造价就定死了。",
    "第二个陷阱：勘察不到位，施工挖开发现地基不行。地下情况没摸清，后面全是变更和索赔，工期直接翻倍。",
    "第三个陷阱：设计施工两张皮，各管各的。EPC的最大优势就是设计与施工一体化，分开管就等于白做。",
    "东盛建筑，专注EPC模式，设计、勘察、施工一站式交付。从图纸到竣工，一个团队管到底，不甩锅、不扯皮。",
    "关注东盛建筑，每天一个行业干货，帮你避坑省钱。",
]

# BGM设置
BGM_URL = "https://raw.githubusercontent.com/nicedoc/free-bgm/main/corporate-technology-8bit.mp3"
# 备用：无BGM URL时用内置生成的纯音乐


async def generate_tts(text, path):
    c = edge_tts.Communicate(text, TTS_VOICE)
    await c.save(path)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
                       capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


async def main():
    print("=" * 55)
    print(f"  东盛建筑短视频合成器 v2.0")
    print("  配图 + 配音 + BGM = 竖屏短视频")
    print("=" * 55)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="ds_video_")
    n = len(SCENES_TEXTS)

    # Step 1: 检查配图
    print("\n检查配图...")
    images = []
    for i in range(n):
        p = os.path.join(IMAGE_DIR, f"scene_{i+1:02d}.png")
        if not os.path.exists(p):
            print(f"  ! 缺少配图: {p}，先用纯色代替")
            from PIL import Image
            img = Image.new('RGB', (WIDTH, HEIGHT), (13, 27, 42))
            p = os.path.join(tmp, f"fallback_{i:02d}.png")
            img.save(p)
        images.append(p)
        print(f"  [{i+1}/{n}] ✓ {Path(p).name}")

    # Step 2: 生成配音
    print("\n生成配音...")
    audios = []
    durations = []
    for i, text in enumerate(SCENES_TEXTS):
        ap = os.path.join(tmp, f"audio_{i:02d}.mp3")
        d = await generate_tts(text, ap)
        audios.append(ap)
        durations.append(d)
        short = text.replace("\n", " ")[:25]
        print(f"  [{i+1}/{n}] {short}... ({d:.1f}s)")

    # Step 3: 下载BGM
    print("\n下载背景音乐...")
    bgm_path = os.path.join(tmp, "bgm.mp3")
    try:
        r = subprocess.run(["curl", "-sL", "-o", bgm_path, "-w", "%{http_code}", BGM_URL],
                          capture_output=True, text=True, timeout=15)
        bgm_size = os.path.getsize(bgm_path) if os.path.exists(bgm_path) else 0
        if r.stdout.strip() == "200" and bgm_size > 1000:
            print(f"  ✓ BGM已下载 ({bgm_size/1024:.0f}KB)")
        else:
            raise Exception(f"HTTP {r.stdout.strip()}")
    except Exception as e:
        print(f"  ! BGM下载失败 ({e})，跳过背景音乐")
        bgm_path = None

    # Step 4: 逐段合成
    print("\n逐段合成...")
    segments = []
    for i in range(n):
        dur = max(durations[i], MIN_DURATION)
        seg = os.path.join(tmp, f"seg_{i:02d}.mp4")

        # 图片循环展示，配音同步
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", images[i],
            "-i", audios[i],
            "-t", str(dur),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=#0d1b2a",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            seg,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ✗ 第{i+1}段失败: {r.stderr[:200]}")
            return
        segments.append(seg)
        print(f"  [{i+1}/{n}] {dur:.1f}s ✓")

    # Step 5: 拼接所有段落
    print("\n拼接视频段落...")
    concat_file = os.path.join(tmp, "segments.txt")
    with open(concat_file, "w") as f:
        for sp in segments:
            f.write(f"file '{sp}'\n")

    merged = os.path.join(tmp, "merged.mp4")
    r = subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        merged,
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ✗ 拼接失败: {r.stderr[:200]}")
        return
    print(f"  ✓ 拼接完成")

    # Step 6: 加BGM
    if bgm_path and os.path.exists(bgm_path):
        print("\n叠加背景音乐...")
        output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        total_dur = sum(max(d, MIN_DURATION) for d in durations)

        r = subprocess.run([
            "ffmpeg", "-y",
            "-i", merged,
            "-i", bgm_path,
            "-filter_complex",
            f"[1:a]volume=0.25,aloop=loop=-1:size=1,atrim=duration={total_dur}[bgm];"
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
            print(f"  ✗ BGM叠加失败: {r.stderr[:200]}")
            # fallback: 输出无BGM版本
            output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}_无BGM.mp4")
            import shutil
            shutil.copy(merged, output)
        else:
            print(f"  ✓ BGM叠加完成")
    else:
        output = os.path.join(OUTPUT_DIR, f"{VIDEO_TITLE}.mp4")
        import shutil
        shutil.copy(merged, output)

    # 完成
    if os.path.exists(output):
        size_mb = os.path.getsize(output) / 1024 / 1024
        total_dur = sum(max(d, MIN_DURATION) for d in durations)
        print(f"\n✅ 视频合成成功！")
        print(f"   路径: {output}")
        print(f"   时长: {total_dur:.1f}s")
        print(f"   大小: {size_mb:.1f}MB")
        print(f"   分辨率: {WIDTH}x{HEIGHT} (竖屏)")
        print(f"   配音: {TTS_VOICE}")
        print(f"   画面: 6张建筑行业配图")
    else:
        print(f"\n✗ 合成失败")

    print(f"\n📁 {OUTPUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
