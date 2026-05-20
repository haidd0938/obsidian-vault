#!/usr/bin/env python3
"""
东盛建筑热点视频 — 2026年5月6日运行脚本
选题：2026中央财政城市更新行动 每城最高12亿补贴

工作原理：修改原脚本中的 SCENES_TEXTS 和 VIDEO_TITLE，
然后执行原脚本的主逻辑。
"""
import os, sys, importlib.util

OUTPUT_DIR = os.path.expanduser("~/Desktop/东盛建筑视频/")
SCRIPT_PATH = os.path.expanduser("~/Desktop/东盛热点视频合成器.py")

# ====== 配置覆盖 ======

VIDEO_TITLE = "2026中央财政城市更新大放水-每城最高12亿-EPC企业如何抓住红利"

SCENES_TEXTS = [
    # 第1段：抓注意力——热点新闻轰炸
    "重磅消息！财政部和住建部联合发文，2026年中央财政继续砸钱支持城市更新，每城最高补贴12个亿！5月8号前就要申报，你准备好了吗？",

    # 第2段：政策分析——谁有钱谁有机会
    "这次全国只选不超过15个城市，东部每城补贴8亿，中部10亿，西部12亿。集中力量办大事，专门支持老城区更新改造，这波红利你抓不抓得住？",

    # 第3段：数据冲击——城市更新市场规模
    "全国城市更新市场规模早超万亿级，十四五收官之年，从供水供热到老旧小区改造，全是真金白银的项目。谁抢得快谁吃肉！",

    # 第4段：EPC模式的天然优势——设计施工一体化
    "为什么城市更新项目尤其适合EPC总承包？老城区改造涉及设计、施工、审批、居民协调，条块分割根本玩不转。EPC模式设计施工一体化，责权清晰、效率翻倍。",

    # 第5段：趋势数据——联合体中标占比飙升
    "城市更新联合体中标占比从2025年31%飙升到2026年一季度的47%。项目太综合了，设计院加施工单位加运营方组队投标，这才是新常态。",

    # 第6段：自然带出品牌——东盛建筑设计
    "东盛建筑设计深耕行业十五年，集设计、勘察、施工、EPC总承包于一体。从方案到交付一站式闭环服务，城市更新风口上，选对伙伴才能少走弯路。",

    # 第7段：互动引导
    "你们公司有没有参与城市更新项目？评论区说说你们那儿的补贴标准！点赞关注东盛建筑，每天解读行业新政，不错过任何赚钱机会！"
]

# ====== 动态修改原脚本的全局变量并执行 ======
# Read original script
with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# Inject our overrides right before the main() call
# The original script has: if __name__ == "__main__":  asyncio.run(main())
# We'll inject our config values right after the imports and then skip original execution

# Build override code
override = f"""
# ===== OVERRIDE by prepare_today_video.py (2026-05-06) =====
VIDEO_TITLE = {repr(VIDEO_TITLE)}
SCENES_TEXTS = {repr(SCENES_TEXTS)}
# ===== END OVERRIDE =====
"""

# Find the __name__ guard and insert our overrides before it
guard_pos = code.find('if __name__ == "__main__":')
if guard_pos > 0:
    modified_code = code[:guard_pos] + override + code[guard_pos:]
else:
    modified_code = override + code

# Write a clean runnable script
RUN_PATH = os.path.expanduser("~/Desktop/run_today_video.py")
with open(RUN_PATH, 'w', encoding='utf-8') as f:
    f.write(modified_code)

print(f"✅ 运行脚本已生成: {RUN_PATH}")
print(f"📹 选题: {VIDEO_TITLE}")
print(f"📝 场景数: {len(SCENES_TEXTS)}")
print(f"📁 输出目录: {OUTPUT_DIR}")
print()
print("开始运行视频合成...")
