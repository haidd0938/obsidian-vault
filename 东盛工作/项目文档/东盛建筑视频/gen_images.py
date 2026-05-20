#!/usr/bin/env python3
"""Generate professional background images for architecture industry videos"""
from PIL import Image, ImageDraw, ImageFont
import os, textwrap

OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频/素材图片")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 1080, 1920
BG = (13, 27, 42)
GOLD = (201, 169, 78)
WHITE = (255, 255, 255)

def parse_color(c):
    c = c.replace("0x", "").replace("#", "")
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def make_scene(title, subtitle, accent_hex, num, total):
    accent = parse_color(accent_hex)
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Font
    fp = "/System/Library/Fonts/PingFang.ttc"
    if not os.path.exists(fp):
        fp = "/System/Library/Fonts/STHeiti Light.ttc"
    main_font = ImageFont.truetype(fp, 64)
    sub_font = ImageFont.truetype(fp, 28)
    brand_font = ImageFont.truetype(fp, 36)
    tiny_font = ImageFont.truetype(fp, 20)

    # Top gold line
    draw.rectangle([0, 0, W, 5], fill=GOLD)
    # Bottom gold line
    draw.rectangle([0, H-4, W, H-4], fill=GOLD)

    # Brand
    draw.text((60, 60), "东盛建筑", fill=GOLD, font=brand_font)
    draw.text((60, 110), "设计 · 勘察 · 施工  EPC总承包", fill=(180,180,180), font=sub_font)

    # Center decoration line
    cy = H // 2 - 140
    draw.rectangle([W//2-60, cy, W//2+60, cy+4], fill=GOLD)

    # Title (centered, wrapped)
    lines = textwrap.wrap(title, width=12)
    th = len(lines) * 80
    sy = H//2 - th//2 - 20
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=main_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw)//2, sy), line, fill=WHITE, font=main_font)
        sy += 80

    # Subtitle
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw = bbox[2] - bbox[0]
        draw.text(((W - sw)//2, H//2 + 80), subtitle, fill=GOLD, font=sub_font)

    # Page number
    pn = f"{num}/{total}"
    bbox = draw.textbbox((0, 0), pn, font=tiny_font)
    pw = bbox[2] - bbox[0]
    draw.text((W - pw - 60, H - 60), pn, fill=(150,150,150), font=tiny_font)

    # Bottom decoration
    draw.rectangle([W//2-40, H-80, W//2+40, H-78], fill=GOLD)

    path = os.path.join(OUTPUT_DIR, f"scene_{num:02d}.png")
    img.save(path, "PNG")
    return path

scenes = [
    ("EPC总承包的三个致命陷阱", "很多老板第一个工程就栽了", "0xc9a94e"),
    ("陷阱一：设计不控造价", "图纸定下来，造价就定死了", "0xe84c3d"),
    ("陷阱二：勘察不到位", "挖开才发现地基不行，工期翻倍", "0xe67e22"),
    ("陷阱三：设计施工两张皮", "分开管就等于白做EPC", "0xe74c3c"),
    ("东盛建筑一站式EPC交付", "从图纸到竣工，一个团队管到底", "0xc9a94e"),
    ("关注东盛建筑", "每天一个行业干货，帮你避坑省钱", "0xc9a94e"),
]

for i, (title, sub, color) in enumerate(scenes):
    p = make_scene(title, sub, color, i+1, len(scenes))
    sz = os.path.getsize(p) / 1024
    print(f"[{i+1}/6] OK ({sz:.0f}KB) {title}")

print("\nDone! All in: " + OUTPUT_DIR)
