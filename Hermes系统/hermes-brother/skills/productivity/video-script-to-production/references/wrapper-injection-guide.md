# Wrapper Injection Guide for 东盛热点视频合成器.py v3.5

## Script Architecture

The script at `~/Desktop/_东盛建筑/东盛热点视频合成器.py` has this layout:

```
# Config variables (lines 22-72)
VIDEO_TITLE = "stale title"
BRAND_NAME = "东盛建筑设计"
BRAND_SUBTITLE = "设计 · 勘察 · 施工 · EPC总承包"
SCENES_TEXTS = [7 elements]  # stale from last run
BGM_URL = "..."             # always 404

# === INJECTION POINT HERE (after BGM_URL line) ===

# Helper functions (lines 75+)
def draw_rounded_rect(...)
def wrap_text(...)
def draw_scene_N_images(...)
def generate_subtitles(...)

# Main async function
async def main():
    # Step 1: generate images (Pillow)
    # Step 2: generate TTS audio (edge_tts)
    # Step 3: composite video clips (FFmpeg Ken Burns)
    # Step 4: concat clips
    # Step 5: add BGM (fails silently)

if __name__ == "__main__":
    asyncio.run(main())
```

## Directory Layout (critical)

The original script lives under `~/Desktop/_东盛建筑/` but the OUTPUT_DIR in the script points to `~/Desktop/东盛建筑视频/`. These are two different directories. Always:
- `cd ~/Desktop/_东盛建筑` to run
- Check output in `~/Desktop/东盛建筑视频/`

## Injection Implementation

The script reads variables BEFORE any functions are defined, so inserting overrides after `BGM_URL` and before `draw_rounded_rect` ensures they shadow the originals.

## Session Example (2026-05-07)

**Topic:** 中央财政砸8-12亿！城市更新行动2026年重磅启动

**News source:** https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2026/art_d23871c95483416aa53e4bbecb43d1be.html

**SCENES_TEXTS:** (see SKILL.md Step 3 section for full text)

**Output:** `~/Desktop/东盛建筑视频/中央财政砸8-12亿！城市更新行动2026年重磅启动，建筑企业的新风口来了？_merged.mp4`
**Duration:** 116.8s, **Size:** 78.4MB, **Resolution:** 1080×1920

## Session Example (2026-05-08)

**Topic:** 中央财政2026年城市更新：每城最高12亿！不足15城入选，谁是赢家？

**News source:** Same policy doc — deeper dive into 15-city cap and competition details
Extracted from: https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2026/art_d23871c95483416aa53e4bbecb43d1be.html

**Script approach:** Shifted angle from "big money" to "15 slots, fierce competition" — highlighting the screening criteria (no new implicit debt, old-town district, safety record) to create urgency with EPC practitioners.

**SCENES_TEXTS:**
```python
[
    "重磅政策！财政部住建部联合发文：2026年中央财政继续大手笔支持城市更新行动！每城最高12亿补助，全国评选不超过15个城市。这钱怎么分？谁有机会？",
    "东部城市每城8亿，中部每城10亿，西部每城最高12亿。划重点：资金投向两个方向——重点样板片区建设和城市更新机制建设。不是撒胡椒面，是集中打造标杆！",
    "15个名额，全国地级市上百个，竞争激烈！而且硬性门槛明确：不能增加隐性债务，必须在老城区实施片区改造，2024年以来无重大安全事故。筛掉一批，再筛一批。",
    "城市更新工程有多复杂？给排水、供热、综合管廊、老旧小区改造、历史文化街区活化……涉及十几个专业。EPC总承包模式下，设计施工一体化统筹，一个团队管到底。这正是城市更新最适合的交付模式！",
    "2026年一季度，全国城市更新新开工项目超3000个，总投资额同比增长15%以上。EPC模式在市政更新类项目中的采用率已达63%。城市更新，已是建筑行业最大的增量市场。",
    "东盛建筑设计，十五年深耕建筑工程与城市更新领域。设计引领、勘察先行、施工管控、EPC总承包一站式闭环服务。中央财政政策来了，项目机会来了——我们准备好了，您呢？",
    "你的城市有机会拿到这8-12亿吗？评论区说说你们当地的城市更新项目进度。关注东盛建筑设计，每天一个行业深度解读。觉得有用点个赞，转给做工程的同行！",
]
```

**Output:** `~/Desktop/东盛建筑视频/中央财政2026年城市更新：每城最高12亿！不足15城入选，谁是赢家？_merged.mp4`
**Duration:** 124s, **Size:** 87MB, **Resolution:** 1080×1920
**Record file:** `~/Desktop/任务中心/02-EPC视频/2026-05-08-EPC视频记录.md`
