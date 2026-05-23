#!/usr/bin/env python3
"""
每日EPC建筑热点视频合成器 — 2026年5月21日
主题：城市更新"十五五"规划审议通过
"""

import os, sys, subprocess, json, asyncio, math, shutil, textwrap
from PIL import Image, ImageDraw, ImageFont

# ======= 配置 =======
OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TODAY = "20260521"
DATE_STR = "2026年5月21日"

# 品牌信息
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 · EPC总承包"
BRAND_SLOGAN = "十五年深耕建筑行业 · 一站式EPC工程总承包服务"

# ======= 视频标题和文案 =======
VIDEO_TITLE = "城市更新十五五规划审议通过_EPC总承包迎来新机遇"

SCENES_TEXTS = [
    # 1. Hook - 热点开场
    '重磅消息！5月15日国务院常务会议审议通过了《城市更新十五五规划》，'
    '这意味着未来五年，城市更新将进入全面提速阶段！',

    # 2. 政策解读
    '规划明确，我国城市发展正从大规模增量扩张转向存量提质增效，'
    '城市更新被摆在突出位置。改造城镇危旧房约50万套，改造老旧小区约11.5万个。',

    # 3. 数据冲击
    '未来五年，建设改造燃气管网20万公里、排水管网17.5万公里、'
    '供水管网17.5万公里、污水管网10万公里，地下管网总改造量超77万公里！',

    # 4. EPC优势分析
    '大规模的城市更新项目，对工程总承包能力提出了更高要求。'
    'EPC模式凭借设计施工一体化优势，能够有效缩短工期、控制成本、保证质量。',

    # 5. 绿色趋势
    '今年一季度，绿色建材营收突破610亿元，同比增长12%。'
    '城市更新项目的绿色低碳转型，正在为建筑行业创造全新的市场空间。',

    # 6. 品牌植入 - 东盛建筑设计
    '从城市体检到老旧小区改造，从管网更新到危房治理，'
    '东盛建筑设计，十五年深耕建筑行业，以设计勘察施工EPC总承包一站式服务，'
    '助力城市更新高质量发展。',

    # 7. CTA - 互动引导
    '城市更新十五五已经启动，你准备好了吗？'
    '关注东盛建筑设计，获取更多EPC工程干货，我们下期见！',
]

# ======= 字体设置 =======
def get_font(size):
    """获取中文字体，尝试多个备选路径"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()

# ======= 颜色方案 =======
DARK_BG = (13, 27, 42)
MEDIUM_BG = (20, 40, 60)
GOLD = (201, 169, 78)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
OVERLAY_ALPHA = 100  # 半透明遮罩alpha值

def create_scene_image(scene_index, title, subtitle, brand_text=None):
    """创建单张场景配图（Pillow渲染，不使用drawtext）"""
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), DARK_BG)
    draw = ImageDraw.Draw(img)

    # 顶部装饰线
    draw.rectangle([0, 0, W, 6], fill=GOLD)

    # 左上角品牌标识
    small_font = get_font(32)
    draw.text((40, 30), BRAND_NAME, fill=GOLD, font=small_font)
    draw.text((40, 72), DATE_STR, fill=LIGHT_GRAY, font=get_font(24))

    # 场景编号 - 右下角
    page_font = get_font(28)
    page_text = f"{scene_index + 1}/{len(SCENES_TEXTS)}"
    bbox = draw.textbbox((0, 0), page_text, font=page_font)
    draw.text((W - bbox[2] - 40, H - 60), page_text, fill=GOLD, font=page_font)

    # 主标题区域 - 居中偏上
    title_font = get_font(68)
    title_color = WHITE

    # 主标题换行处理
    lines = textwrap.wrap(title, width=16)
    total_h = len(lines) * 90
    start_y = H // 2 - total_h // 2 - 100

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, start_y + i * 90), line, fill=title_color, font=title_font)

    # 金色装饰横线
    line_y = start_y + len(lines) * 90 + 40
    draw.rectangle([W//2 - 80, line_y, W//2 + 80, line_y + 3], fill=GOLD)

    # 副标题
    if subtitle:
        sub_font = get_font(36)
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, line_y + 50), subtitle, fill=GOLD, font=sub_font)

    # 底部品牌信息
    if brand_text:
        brand_font = get_font(28)
        bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, H - 120), brand_text, fill=LIGHT_GRAY, font=brand_font)

    # 底部装饰线
    draw.rectangle([0, H - 6, W, H], fill=GOLD)

    return img

# ======= 场景配图定义 =======
SCENE_CONFIGS = [
    {
        'title': '重磅！',
        'subtitle': '城市更新十五五规划审议通过',
        'brand': BRAND_SUBTITLE
    },
    {
        'title': '50万套危旧房改造',
        'subtitle': '11.5万个老旧小区更新',
        'brand': '从增量扩张转向存量提质增效'
    },
    {
        'title': '77万公里地下管网',
        'subtitle': '燃气、排水、供水、供热全面改造',
        'brand': '五年建设改造总里程超77万公里'
    },
    {
        'title': 'EPC总承包新机遇',
        'subtitle': '设计施工一体化优势凸显',
        'brand': '缩短工期 控制成本 保证质量'
    },
    {
        'title': '绿色建材营收610亿',
        'subtitle': '同比增长12% 低碳转型加速',
        'brand': '绿色建材助力城市更新'
    },
    {
        'title': '东盛建筑设计',
        'subtitle': '十五年深耕 · 一站式EPC服务',
        'brand': '设计 · 勘察 · 施工 · EPC总承包'
    },
    {
        'title': '城市更新已启动',
        'subtitle': '你准备好了吗？',
        'brand': '关注东盛建筑设计 获取更多干货'
    },
]

# ======= 依赖检查 =======
def check_deps():
    """检查所需依赖是否安装"""
    deps = {}
    try:
        import edge_tts
        deps["edge_tts"] = True
    except:
        deps["edge_tts"] = False
    try:
        from PIL import Image
        deps["pillow"] = True
    except:
        deps["pillow"] = False
    return deps

# ======= 生成配图 =======
def generate_all_images():
    """生成所有场景配图"""
    print("📸 生成场景配图...")
    img_dir = os.path.join(OUTPUT_DIR, f"素材图片_{TODAY}")
    os.makedirs(img_dir, exist_ok=True)

    paths = []
    for i, config in enumerate(SCENE_CONFIGS):
        title = config["title"]
        subtitle = config.get("subtitle", "")
        brand = config.get("brand", BRAND_SUBTITLE)
        img = create_scene_image(i, title, subtitle, brand)
        path = os.path.join(img_dir, f"scene_{i+1:02d}.png")
        img.save(path, "PNG")
        paths.append(path)
        print(f"  ✅ 第{i+1}张配图: {path}")

    return paths

# ======= 生成配音 =======
async def generate_audio_segments():
    """使用Edge TTS生成每段配音"""
    print("🎤 生成配音音频...")
    audio_dir = os.path.join(OUTPUT_DIR, f"音频_{TODAY}")
    os.makedirs(audio_dir, exist_ok=True)

    import edge_tts

    voice = "zh-CN-YunjianNeural"  # 稳重男声，适合建筑行业
    paths = []
    durations = []

    for i, text in enumerate(SCENES_TEXTS):
        path = os.path.join(audio_dir, f"audio_{i+1:02d}.mp3")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)
        paths.append(path)
        # 获取时长
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
            capture_output=True, text=True, timeout=10
        )
        try:
            duration = float(json.loads(result.stdout)["format"]["duration"])
        except:
            duration = 8.0  # 默认8秒
        durations.append(duration)
        print(f"  ✅ 第{i+1}段配音 ({duration:.1f}s): {os.path.basename(path)}")

    return paths, durations

# ======= 合成视频段落 =======
def synthesize_segments(image_paths, audio_paths, durations):
    """将图片和音频合成为视频段落"""
    print("🎬 合成视频段落...")
    seg_dir = os.path.join(OUTPUT_DIR, f"段落_{TODAY}")
    os.makedirs(seg_dir, exist_ok=True)

    seg_paths = []
    for i in range(len(image_paths)):
        output = os.path.join(seg_dir, f"seg_{i+1:02d}.mp4")
        duration = durations[i]

        # 确保至少5秒，最多18秒
        duration = max(5.0, min(18.0, duration))

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_paths[i],
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            "-b:v", "4M",
            "-preset", "medium",
            output
        ]
        subprocess.run(cmd, capture_output=True, timeout=60)
        seg_paths.append(output)
        print(f"  ✅ 第{i+1}段视频 ({duration:.1f}s)")

    return seg_paths

# ======= 合成配音到段落 =======
def add_audio_to_segments(seg_paths, audio_paths, durations):
    """将配音合成到视频段落"""
    print("🔊 合成配音到段落...")
    voiced_dir = os.path.join(OUTPUT_DIR, f"配音段落_{TODAY}")
    os.makedirs(voiced_dir, exist_ok=True)

    voiced_paths = []
    for i in range(len(seg_paths)):
        output = os.path.join(voiced_dir, f"voiced_{i+1:02d}.mp4")
        duration = durations[i]
        duration = max(5.0, min(18.0, duration))

        cmd = [
            "ffmpeg", "-y",
            "-i", seg_paths[i],
            "-i", audio_paths[i],
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration),
            "-shortest",
            output
        ]
        subprocess.run(cmd, capture_output=True, timeout=60)
        voiced_paths.append(output)
        print(f"  ✅ 第{i+1}段配音合成")

    return voiced_paths

# ======= 拼接所有段落 =======
def concat_segments(voiced_paths):
    """拼接所有段落为一个完整视频"""
    print("🔗 拼接所有段落...")
    concat_file = os.path.join(OUTPUT_DIR, f"concat_{TODAY}.txt")
    with open(concat_file, "w") as f:
        for path in voiced_paths:
            f.write(f"file '{path}'\n")

    output = os.path.join(OUTPUT_DIR, f"EPC建筑行业热点_{TODAY}.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output
    ]
    subprocess.run(cmd, capture_output=True, timeout=120)
    print(f"  ✅ 拼接完成: {output}")
    return output

# ======= 清理临时文件 =======
def cleanup():
    """清理临时目录和文件"""
    print("🧹 清理临时文件...")
    for d in [f"段落_{TODAY}", f"音频_{TODAY}", f"配音段落_{TODAY}"]:
        path = os.path.join(OUTPUT_DIR, d)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"  ✅ 已清理: {d}")

    concat_file = os.path.join(OUTPUT_DIR, f"concat_{TODAY}.txt")
    if os.path.exists(concat_file):
        os.remove(concat_file)

# ======= 验证输出 =======
def verify_output(path):
    """验证最终视频文件"""
    print("\n🔍 验证输出...")
    if not os.path.exists(path):
        print(f"  ❌ 文件不存在: {path}")
        return False

    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"  📊 文件大小: {size_mb:.1f} MB")

    # 检查编码信息
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path],
        capture_output=True, text=True, timeout=10
    )
    try:
        info = json.loads(result.stdout)
        fmt = info["format"]
        duration = float(fmt["duration"])
        print(f"  📊 时长: {duration:.1f}s")

        for stream in info.get("streams", []):
            if stream["codec_type"] == "video":
                print(f"  📊 分辨率: {stream['width']}x{stream['height']}")
                print(f"  📊 视频编码: {stream['codec_name']}")
            elif stream["codec_type"] == "audio":
                print(f"  📊 音频编码: {stream['codec_name']}")

        print(f"  ✅ 验证通过!")
        return True
    except Exception as e:
        print(f"  ❌ 验证失败: {e}")
        return False

# ======= 生成记录文件 =======
def write_record_file(video_path):
    """写入EPC视频记录文件"""
    record_dir = os.path.expanduser("~/Desktop/任务中心/02-EPC视频")
    os.makedirs(record_dir, exist_ok=True)

    content = f"""# EPC视频产出记录 - {DATE_STR}

## 基本信息
- **日期**: {DATE_STR}
- **选题**: 城市更新"十五五"规划审议通过
- **来源**: 住建部官网 / 人民日报海外版 2026.05.18

## 热点摘要
5月15日国务院常务会议审议通过《城市更新"十五五"规划》。
改造城镇危旧房约50万套，老旧小区约11.5万个。
建设改造各类地下管网总计约77万公里。
一季度绿色建材营收突破610亿元，同比增长12%。

## 视频信息
- **标题**: {VIDEO_TITLE}
- **文件**: {video_path}
- **脚本篇幅**: 7段 / 约90-120秒
- **主题**: EPC总承包迎城市更新新机遇

## 完整文案
"""
    for i, text in enumerate(SCENES_TEXTS):
        content += f"\n**第{i+1}段**: {text}\n"

    content += f"""
## 发布建议
- 适合平台: 抖音 / 视频号 / 小红书
- 推荐发布时间: 上午9:00-11:00
- 话题标签: #城市更新 #EPC总承包 #东盛建筑设计 #绿色建筑
"""
    record_path = os.path.join(record_dir, f"{DATE_STR}-EPC视频记录.md")
    with open(record_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ 记录文件: {record_path}")
    return record_path

# ======= 主流程 =======
async def main():
    print("=" * 60)
    print(f"  EPC建筑热点视频合成 - {DATE_STR}")
    print('  选题: 城市更新十五五规划审议通过')
    print("=" * 60)

    # 1. 检查依赖
    print("\n📋 检查依赖...")
    deps = check_deps()
    for dep, ok in deps.items():
        print(f"  {'✅' if ok else '❌'} {dep}")
    if not deps["edge_tts"]:
        print("  ⏳ 安装 edge-tts...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
    if not deps["pillow"]:
        print("  ⏳ 安装 Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])

    # 2. 生成配图
    image_paths = generate_all_images()

    # 3. 生成配音
    audio_paths, durations = await generate_audio_segments()

    # 4. 合成视频段落（无配音）
    seg_paths = synthesize_segments(image_paths, audio_paths, durations)

    # 5. 添加配音
    voiced_paths = add_audio_to_segments(seg_paths, audio_paths, durations)

    # 6. 拼接
    final_path = concat_segments(voiced_paths)

    # 7. 验证
    verify_output(final_path)

    # 8. 生成记录
    write_record_file(final_path)

    # 9. 清理
    cleanup()

    print("\n" + "=" * 60)
    print(f"  🎉 视频制作完成!")
    print(f"  📁 {final_path}")
    print("=" * 60)

    return final_path

if __name__ == "__main__":
    asyncio.run(main())
