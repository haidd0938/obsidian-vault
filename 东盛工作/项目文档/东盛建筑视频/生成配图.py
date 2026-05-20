#!/usr/bin/env python3
"""用 Pillow 生成专业建筑行业短视频背景配图"""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频/素材图片")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920

# 品牌色
BG = (13, 27, 42)       # 深蓝黑 #0d1b2a
GOLD = (201, 169, 78)   # 金色 #c9a94e
WHITE = (255, 255, 255)
LIGHT_GOLD = (201, 169, 78, 180)

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def make_scene_image(title, subtitle, accent_color_hex="0xc9a94e", scene_num=1, total=6):
    accent = hex_to_rgb(accent_color_hex)
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # 尝试加载字体，逐级降级
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    font_main = None
    font_sub = None
    font_brand = None
    font_num = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font_main = ImageFont.truetype(fp, 64)
                font_sub = ImageFont.truetype(fp, 28)
                font_brand = ImageFont.truetype(fp, 36)
                font_num = ImageFont.truetype(fp, 20)
                break
            except:
                continue

    # 顶部金色细线
    draw.rectangle([0, 0, W, 5], fill=GOLD)
    # 底部金色细线（淡）
    draw.rectangle([0, H-4, W, H-4], fill=(GOLD[0], GOLD[1], GOLD[2], 80))

    # 品牌名（左上）
    if font_brand:
        draw.text((60, 60), "东盛建筑", fill=GOLD, font=font_brand)
    # 副标题
    if font_sub:
        draw.text((60, 110), "设计 · 勘察 · 施工  EPC总承包", fill=(200, 200, 200, 150), font=font_sub)

    # 居中金色装饰横线
    center_line_y = H // 2 - 120
    draw.rectangle([W//2-60, center_line_y, W//2+60, center_line_y+4], fill=GOLD)

    # 主标题（居中）
    if font_main:
        # 自动换行
        lines = textwrap.wrap(title, width=14)
        total_h = len(lines) * 80
        start_y = H//2 - total_h//2 - 20
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_main)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2, start_y), line, fill=WHITE, font=font_main)
            start_y += 80

    # 副说明
    if font_sub and subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
        sw = bbox[2] - bbox[0]
        draw.text(((W - sw) // 2, H//2 + 80), subtitle, fill=(GOLD), font=font_sub)

    # 页码
    if font_num:
        page_text = f"{scene_num} / {total}"
        bbox = draw.textbbox((0, 0), page_text, font=font_num)
        pw = bbox[2] - bbox[0]
        draw.text((W - pw - 60, H - 60), page_text, fill=(150, 150, 150), font=font_num)

    # 底部装饰金色短线
    draw.rectangle([W//2-40, H-80, W//2+40, H-78], fill=GOLD)

    path = os.path.join(OUTPUT_DIR, f"scene_{scene_num:02d}.png")
    img.save(path, "PNG")
    return path

# ===== 6个场景 =====
scenes = [
    ("EPC总承包的三个致命陷阱", "很多老板第一个工程就栽了", "0xc9a94e"),
    ("陷阱一：设计不控造价", "图纸定下来，造价就定死了", "0xe84c3d"),
    ("陷阱二：勘察不到位", "挖开才发现地基不行，工期翻倍", "0xe67e22"),
    ("陷阱三：设计施工两张皮", "分开管就等于白做EPC", "0xe74c3c"),
    ("东盛建筑一站式EPC交付", "从图纸到竣工，一个团队管到底", "0xc9a94e"),
    ("关注东盛建筑", "每天一个行业干货，帮你避坑省钱", "0xc9a94e"),
]

for i, (title, sub, color) in enumerate(scenes):
    path = make_scene_image(title, sub, color, i+1, len(scenes))
    size = os.path.getsize(path) / 1024
    print(f"[{i+1}/6] ✓ {path} ({size:.0f}KB)")

print(f"\n全部生成完毕！目录: {OUTPUT_DIR}/")
