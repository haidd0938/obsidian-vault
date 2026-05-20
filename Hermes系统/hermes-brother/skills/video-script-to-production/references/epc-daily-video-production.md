# Daily EPC/Construction Hot-Topic Video Production

> 合并自 `creative/daily-epc-video-production` 技能。EPC建筑行业短视频的每日cron产线。
> 每天早8:00 cron自动运行，产出一条建筑/EPC热点短视频，用于"东盛建筑设计"品牌推广。
> 竖屏1080×1920，7段场景，约90-120秒，Pillow生成配图+Edge TTS配音+Ken Burns动效+字幕叠加。

## Triggers
- 每日定时 cron job
- 用户手动触发："做今天的视频"、"执行每日流程"

## ⚠️ 2026-05-09 更新：实际使用的脚本是 `run_today_video.py`

**实际 cron/手动使用的脚本已演变为 `~/Desktop/_东盛建筑/run_today_video.py`**（557行，v3.5增强版）。

旧的 `东盛建筑视频合成器_v3.py` 和 `东盛热点视频合成器.py` 可能仍存在于桌面上，但 **`run_today_video.py` 是当前活跃的产线脚本**。

### `run_today_video.py` 的关键特征

1. **内置"每日覆盖注入"机制**（非外部wrapper）— 脚本末尾附近有一段注释标记的区域：
   ```
   # === YYYY-MM-DD 每日覆盖注入 ===
   VIDEO_TITLE = '今日视频标题'
   BRAND_NAME = '东盛建筑设计'
   BRAND_SUBTITLE = '设计 · 勘察 · 施工 · EPC总承包'
   SCENES_TEXTS = ['第1段', ...]
   # === 结束覆盖 ===
   ```
   这个注入段会覆盖脚本顶部的默认值（默认值不会被执行）。修改时：
   - 复制一份脚本：`cp run_today_video.py run_today_video_YYYYMMDD.py`
   - 修改注入段的 `VIDEO_TITLE` 和 `SCENES_TEXTS`
   - 运行后可以删除临时副本

2. **字体使用**：`/System/Library/Fonts/STHeiti Medium.ttc`（非 PingFang）

3. **输出目录结构**：
   - 脚本位置：`~/Desktop/_东盛建筑/`
   - 视频输出：`~/Desktop/东盛建筑视频/`
   - 记录文件：`~/Desktop/任务中心/02-EPC视频/YYYY-MM-DD-EPC视频记录.md`

4. **BGM 下载**：尝试下载但通常失败（GitHub raw 403/超时），脚本会跳过 BGM 并输出无 BGM 版本

## 脚本位置（桌面上有多个，别搞混）

| 脚本 | 路径 | 特点 | 推荐度 |
|------|------|------|--------|
| `run_today_video.py` | `~/Desktop/_东盛建筑/` | **活跃产线**，557行，v3.5，内置覆盖注入机制 | ⭐ **当前首选** |
| v3.0（旧版） | `~/Desktop/_东盛建筑/东盛建筑视频合成器_v3.py` | 稳定，359行 | ❌ 已归档 |
| v3.5（新版） | `~/Desktop/_东盛建筑/东盛热点视频合成器.py` | 476行 | ❌ 已被run_today替代 |
| 每日临时副本 | `~/Desktop/_东盛建筑/run_today_video_YYYYMMDD.py` | 运行后删除 | 🗑️ 临时文件 |

**⚠️ 关键路径规则：** 桌面上有 `鑫球汇视频合成器v3.py` — 那是台球俱乐部的，完全不同，不要用。

验证方法：`ls -la ~/Desktop/_东盛建筑/run_today_video.py`

## Step 1: Hot Topic Research (热点检索)

### Primary Source: MOHURD (住建部官网)
使用 curl 直接抓取住建部官网。Google/Baidu/Bing 通常会因验证码或 JS 渲染返回空结果。
```bash
curl -s --max-time 15 "https://www.mohurd.gov.cn/" -o /tmp/mohurd.html
```

### Extract Article Titles
```python
import re, html
with open('/tmp/mohurd.html', 'r', encoding='utf-8') as f:
    content = f.read()
for m in re.finditer(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>', content):
    href = m.group(1)
    text = html.unescape(m.group(2)).strip()
    if text and len(text) > 5 and not href.startswith('#') and not href.startswith('javascript'):
        print(f'{text}\n  -> {href}')
```

### Fetch Article Detail Pages
For relative URLs, prepend `https://www.mohurd.gov.cn/`.
```bash
curl -s --max-time 15 "https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2026/art_xxx.html" -o /tmp/article.html
```

### Fallback (if no news found)
- 中央财政城市更新行动
- 绿色建筑与智能建造协同发展
- 数字住建/智能建造
- 资质改革趋势
- "好房子"与科技融合
- 联合体中标趋势

## Step 2: Topic Selection
1. 新闻热度 — 政策类 > 行业动态 > 地方实践
2. EPC相关性 — 城市更新、工程总承包、联合体模式最佳
3. 从业者共鸣 — 政策解读、市场机会、行业痛点
4. 信息差价值 — 新政策解读、数据趋势分析

### Title Pattern
```
[重磅/突发/政策名词] + [核心数据/金额] + [观点/追问]
```

## Step 3: Script (7 segments, ~90-120s)

| Seg | Scene | Purpose |
|-----|-------|---------|
| 1 | 0 | Hook — 热点新闻开场 |
| 2 | 1 | 政策分析 |
| 3 | 2 | 数据冲击 |
| 4 | 3 | EPC优势分析 |
| 5 | 4 | 趋势数据 |
| 6 | 5 | 品牌植入（东盛建筑设计） |
| 7 | ≥6 | 互动引导 CTA |

Per-segment: ~25-50 characters, 10-20 seconds each.
Language: 建筑行业从业者口吻，专业但口语化。

### Brand Integration (Scene 5)
Must include: **东盛建筑设计**, **设计·勘察·施工·EPC总承包**, 十五年深耕 + 一站式闭环服务

## Step 4: Override & Run Synthesis

**使用内置覆盖注入机制（推荐）**：

```bash
# 1. 复制一份脚本
cp ~/Desktop/_东盛建筑/run_today_video.py ~/Desktop/_东盛建筑/run_today_video_$(date +%Y%m%d).py

# 2. 用 sed 或 patch 修改注入段的 VIDEO_TITLE 和 SCENES_TEXTS
# 脚本末尾附近有：
#   # === YYYY-MM-DD 每日覆盖注入 ===
#   VIDEO_TITLE = '...'
#   SCENES_TEXTS = ['...', ...]
#   # === 结束覆盖 ===

# 3. 运行
cd ~/Desktop/_东盛建筑 && python3 run_today_video_$(date +%Y%m%d).py

# 4. 清理临时文件（可选）
rm ~/Desktop/_东盛建筑/run_today_video_$(date +%Y%m%d).py
```

**⚠️ 中文引号陷阱**：如果 SCENES_TEXTS 文案中包含中文双引号（如 `从"盖完就扔"转向`），Python 字符串会被截断报 `SyntaxError`。解决方案：
- 使用单引号包裹字符串：`'从"盖完就扔"转向'`
- 或者用 `re.sub(pattern, new_scenes, content, flags=re.DOTALL)` 替换整个列表块

**Old approach (wrapper injection, no longer needed):**

## Step 5: Output Verification
```bash
ls -la ~/Desktop/东盛建筑视频/*.mp4 | tail -5
```
Check: size > 0, 1080×1920, ~90-120s

### Handle BGM Failure
The script attempts BGM download — it will 404. Script handles silently. Output: `{VIDEO_TITLE}_merged.mp4`

## Step 6: Final Report & Record File
Write to `~/Desktop/任务中心/02-EPC视频/YYYY-MM-DD-EPC视频记录.md` containing:
- 日期, 选题来源与热点摘要, 脚本标题与完整文案
- 视频产出路径, 技术规格, 状态, 发布建议

Report to user: topic + file name + specs + posting advice.

If no news found → respond `[SILENT]`

## Cron超时问题

Cron 有600s超时限制。两种解决方案：
- **方案A（推荐）：** 用`delegate_task`派发子代理（`toolsets=["browser","terminal","file"]`）
- **方案B：** 提前patch好文案，cron只需运行`python3`（90-180s）

## Pitfalls
1. Baidu/Bing/Google blocked — skip, use MOHURD curl directly. If MOHURD also fails, try browsing archiposition.com (有方) directly — it returns clean HTML with current building industry news.
2. Chinese news sites (163, qq, sina) WAF blocked — do not attempt
3. BGM URL always 404 — fine, output file gets `_merged` suffix
4. Never edit original script — always use wrapper override
5. Never ask questions during cron runs
6. SCENES_TEXTS in original is stale — always override
7. h264_videotoolbox — macOS-specific encoder
8. MOHURD detail pages SSL EOF with Python urllib — use curl instead
9. The exact script name may vary — always check available files first
10. Directory split: script under `~/Desktop/_东盛建筑/`, output to `~/Desktop/东盛建筑视频/`

### ⚠️ 2026-05-10: Fallback approach when `daily-epc-video-production` skill is missing
If the cron job lists `daily-epc-video-production` as a required skill but it's not found (was deleted or renamed), create a self-contained video from scratch:

1. **Hot topic research**: If Baidu/Bing/Google all throw CAPTCHAs in the browser:
   - Use `curl` to `cn.bing.com/search?q=...` with proper User-Agent
   - Or navigate browser directly to `https://cn.bing.com/search?q=...` 
   - Or visit `https://www.archiposition.com/` (有方) for current architecture news (no CAPTCHA)
   - Or `https://www.archdaily.cn/cn` for global architecture news
   - The Bing search page rendered in the browser tool will show results even if curl gets redirected

2. **ffmpeg drawtext filter not available**: macOS Homebrew ffmpeg may not have `drawtext` compiled. Verify: `ffmpeg -filters 2>&1 | grep drawtext`. If empty:
   - Use Pillow (Python) to generate PNG frames instead
   
3. **Pillow frame → ffmpeg video pipeline** (no drawtext dependency):
   ```python
   from PIL import Image, ImageDraw, ImageFont
   font = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 30)  # PingFang may fail
   img = Image.new("RGB", (1080, 1920), (26, 26, 46))
   draw = ImageDraw.Draw(img)
   draw.text((x, y), "内容", fill=(255,255,255), font=font)
   img.save("scene.png")
   ```

4. **ffmpeg concat approach** (concat demuxer doesn't support `duration` sub-command):
   ```bash
   # Per segment: loop 1 frame for N seconds
   ffmpeg -y -loop 1 -i scene.png -c:v libx264 -t 8 -pix_fmt yuv420p -r 30 seg_01.mp4
   # Then concat with -c copy:
   echo "file 'seg_01.mp4'" > concat.txt
   echo "file 'seg_02.mp4'" >> concat.txt
   ffmpeg -y -f concat -safe 0 -i concat.txt -c copy final.mp4
   ```

5. **Font fallback chain**: On macOS, try in order:
   - `/System/Library/Fonts/PingFang.ttc` (preferred, may fail silently with wrong glyphs on some systems)
   - `/System/Library/Fonts/STHeiti Light.ttc` (reliable fallback)
   - `/System/Library/Fonts/AppleSDGothicNeo.ttc`

6. **Python Chinese double-quote trap**: If scene text contains Chinese double quotes inside Python `"..."` string (e.g., `"从"盖完就扔"转向"`), Python sees the Chinese `"` as a string terminator. Fix: use single quotes for the string: `'从"盖完就扔"转向'`, or use escaped unicode.
