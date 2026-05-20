# 生成台球主题背景图指南（替代不可靠的网上图片）

## 为什么需要这个

本指南记录了**一次完整的试错循环**：

- ❌ **Pixabay**: 403 Forbidden（Cloudflare保护）
- ❌ **Unsplash source.unsplash.com**: 域名解析失败/重定向
- ❌ **Pexels** `images.pexels.com/photos/{ID}/...`: 下载成功但同一ID在不同时间返回完全不同内容（隧道/足球/眼睛/台球桌随机切换）
- ✅ **Pillow绘制的抽象渐变+台球装饰背景**: 100%可靠，无版权问题，视觉统一

## 核心方案：Pillow绘制主题背景

```python
from PIL import Image, ImageDraw

w, h = 1080, 1920  # 竖屏
c1 = hex_to_rgb("#1a1a2e")  # 深蓝
c2 = hex_to_rgb("#16213e")

img = Image.new("RGB", (w, h), c1)
draw = ImageDraw.Draw(img)

# 渐变
for y in range(h):
    ratio = y / h
    r = int(c1[0] * (1-ratio) + c2[0] * ratio)
    g = int(c1[1] * (1-ratio) + c2[1] * ratio)
    b = int(c1[2] * (1-ratio) + c2[2] * ratio)
    draw.line([(0, y), (w, y)], fill=(r, g, b))
```

## 台球主题装饰元素

| 元素 | 实现 | 效果 |
|------|------|------|
| 顶部/底部强调线 | `draw.rectangle([0, 0, w, 10], fill=accent)` | 品牌分割线 |
| 角落装饰球 | `draw.ellipse([cx-20, cy-20, cx+20, cy+20], outline=accent, width=4)` | 四个角落圆环 |
| 半透明桌面 | `draw.rounded_rectangle([...], fill=(*accent, 20), outline=(*accent, 80))` | 台球桌轮廓（RGBA混合） |
| 彩色球列阵 | 6种颜色（黄/蓝/红/紫/橙/绿）的实心圆+高光 | 台球氛围核心 |
| 8号球（白底黑8） | 白色大圆+黑色圆形+白色数字"8" | 标志性元素 |
| 球杆（斜线） | `draw.line([(x1,y1), (x2,y2)], fill=(200,160,100), width=8)` | 对角线球杆 |

## 9段配色方案

```python
schemes = [
    ("#1a1a2e", "#16213e"),  # 深蓝黑 - 开场
    ("#0f3460", "#1a1a2e"),  # 深蓝 - 段落1
    ("#2c3e50", "#1a252f"),  # 墨蓝 - 段落2
    ("#1b4332", "#081c15"),  # 墨绿 - 段落3
    ("#4a1c40", "#2d0a28"),  # 紫红 - 段落4
    ("#3c096c", "#10002b"),  # 紫色 - 段落5
    ("#7f2d0f", "#3e1305"),  # 棕色 - 段落6
    ("#0c3547", "#051a26"),  # 深青 - 段落7
    ("#1a1a2e", "#0f3460"),  # 深蓝 - CTA
]
```

强调色对应（每个方案一组）：
```python
accent_colors = [(255,200,0), (100,200,255), (200,150,255), 
                 (100,255,150), (255,150,200), (255,180,50),
                 (150,200,255), (255,100,100), (255,200,100)]
```

## 集成到合成器脚本

**create_scene_image** 函数的修改：

1. 当背景图尺寸 == WIDTH×HEIGHT（1080×1920）时，直接使用不缩放、不裁剪
2. 此时 `draw_bg = False`，跳过背景装饰绘制（因为背景图自带装饰元素）
3. 仍需要叠加半透明遮罩（黑色alpha=100/255）确保文字可读
4. PNG文件18-19KB，比JPEG实景图（100-500KB）更小，渲染更快

```python
def create_scene_image(text, output_path, index, total, scene_image_path=None):
    w, h = WIDTH, HEIGHT  # 1080, 1920
    
    if scene_image_path and os.path.exists(scene_image_path):
        bg_img = Image.open(scene_image_path).convert("RGB")
        if bg_img.size[0] == w and bg_img.size[1] == h:
            img = bg_img.copy()
            draw_bg = False  # 背景图已有装饰，不重复画
        else:
            # 缩放+裁剪（兼容非标准尺寸图片）
            draw_bg = True
    else:
        img = Image.new("RGB", (w, h), colors["bg"])
        draw_bg = True
    
    # 如果回退了纯色背景，才画装饰
    if draw_bg:
        draw_billiard_pattern(draw, w, h, colors)
    
    # 遮罩（始终叠加，确保文字在任何背景上都清晰）
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
```

## 生产验证（2026-05-07）

✅ **已经用此方案生产了2个主题视频（潜规则+高效引流），每段9张背景图**
- 文件命名: `bg_01.png` ~ `bg_09.png`，储存在 `~/Desktop/鑫球汇图片素材/`
- 每个文件18-20KB，1080×1920，8-bit RGB PNG
- 生成耗时：约5秒（9张全部）
- 渲染耗时：无需额外渲染，v3.py直接读取使用

### 判断何时使用生成背景 vs 实景图片

| 用户反馈 | 行动 | 示例 |
|---------|------|------|
| "图片都不好看" | 全部切生成背景 | 潜规则v2→v3迭代 |
| "素材不匹配" | 尝试网络搜图；若失败则切生成 | 首版潜规则 |
| 没说图片问题 | 用搜索到的实景图片 | 首版冷知识 |

```bash
# 检查生成的PNG文件
file ~/Desktop/鑫球汇图片素材/bg_01.png
# → PNG image data, 1080 x 1920, 8-bit/color RGB, non-interlaced

sips -g pixelWidth -g pixelHeight ~/Desktop/鑫球汇图片素材/bg_01.png
# → pixelWidth: 1080, pixelHeight: 1920

# 从视频抽帧检查效果
ffmpeg -y -ss 00:00:03 -i "output.mp4" -vframes 1 -q:v 1 frame.jpg
open frame.jpg
```

## 注意事项

- 生成的PNG只有18-20KB（纯几何图形，无损压缩效率高）— 这是正常的
- vision_analyze可能会说"纯色背景"— 因为Gemini视觉模型对几何图案不敏感，实际视频中渐变+台球元素清晰可见
- 如果要在HTML/CSS渲染的信息图中使用类似设计，可以直接复用渐变颜色代码——色调方案和强调色完全兼容HTML渐变色
- 抽象装饰背景更适合**知识科普/冷知识类**视频；如果是产品展示/实地探店类，仍需实景图片
