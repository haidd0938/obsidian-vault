#!/usr/bin/env python3
"""
GitHub Trending Monitor — 每日扫描 GitHub Trending（通过 ossinsight API），
筛选与副业相关的项目，输出结构化报告。
"""

import json
import re
import urllib.request
import urllib.error
from datetime import datetime

# ── 副业相关关键词 ──
CATEGORIES = {
    "critical": [
        # 建筑/EPC
        r"\b(bim|building|construction|architecture|structural|engineering|epc|civil|cad|cae|revit|autocad|floor.?plan)\b",
        r"\b(project.?management|construction.?tech|architect)\b",
        # 台球
        r"\b(billiard|billiards|pool|snooker|cue.?sport)\b",
        # 信息套利/副业变现
        r"\b(arbitrage|resell|reselling|flipping|side.?hustle|passive.?income|make.?money|monetize)\b",
        r"\b(dropshipping|print.?on.?demand|affiliate|ecommerce|shopify|magento|woocommerce)\b",
        # 内容出海/TikTok
        r"\b(tiktok|short.?video|video.?editing|video.?generation|video.?automation)\b",
        r"\b(cross.?border|crossborder|export|overseas|global.?market)\b",
        # AI工具变现
        r"\b(ai.?tool|ai.?wrapper|ai.?app|gpt.?wrapper|llm.?app)\b",
        r"\b(saas|indie.?hacker|startup.?template)\b",
    ],
    "important": [
        r"\b(no.?code|low.?code|automation|workflow|pipeline|agent.?framework)\b",
        r"\b(scraper|crawler|data.?mining|data.?extraction|web.?scrape)\b",
        r"\b(text.?to.?video|text.?to.?image|image.?gen|video.?gen|ai.?video|ai.?image)\b",
        r"\b(seo|keyword|content.?gen|blog|writing|copywriting)\b",
        r"\b(social.?media|scheduler|post|publish|analytics|dashboard)\b",
        r"\b(knowledge.?base|wiki|second.?brain|obsidian|notion|markdown.?note)\b",
        r"\b(stock|trading|quant|finance|portfolio|backtest|market.?data)\b",
        r"\b(mcp|model.?context.?protocol|api.?gateway|api.?proxy)\b",
        r"\b(n8n|make\.com|zapier|integromat)\b",
    ],
    "nice": [
        r"\b(docker|kubernetes|devops|deploy|ci.?cd)\b",
        r"\b(python|fastapi|flask|django|node|react|next|nuxt)\b",
        r"\b(database|sql|postgres|redis|sqlite)\b",
        r"\b(monitoring|visualization|chart|grafana)\b",
        r"\b(macOS|mac.?app|homebrew|brew)\b",
    ]
}

BLACKLIST = [
    r"\b(game|gaming|minecraft|roblox|unity|unreal|godot)\b",
    r"\b(porn|xxx|adult|nsfw)\b",
    r"\b(crypto|bitcoin|nft|blockchain|defi|web3)\b",
    r"\b(leetcode|algorithm|interview|coding.?challenge)\b",
    r"\b(os.?dev|kernel|driver|filesystem|compiler)\b",
    r"\b(language.?model|llm.?train|fine.?tune|grpo|rlhf|dpo|training.?llm)\b",
]

STAR_THRESHOLD = {"daily": 50, "weekly": 200}
MAX_RESULTS = 20
API_URL = "https://api.ossinsight.io/v1/trends/repos?since=%s&limit=50"


def fetch_trending(since="daily"):
    """Fetch trending repos from ossinsight API"""
    url = API_URL % since
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e), "repos": []}

    repos = data.get("data", {}).get("rows", [])
    parsed = []
    for r in repos:
        stars_total = int(r.get("stars", 0) or 0)
        total_score = float(r.get("total_score", 0) or 0)
        parsed.append({
            "name": r.get("repo_name", ""),
            "url": f"https://github.com/{r.get('repo_name', '')}",
            "description": (r.get("description") or "")[:300],
            "language": r.get("primary_language") or "",
            "total_stars": stars_total,
            "total_score": total_score,
        })
    return {"repos": parsed}


def match_relevance(repo):
    """Score relevance. Returns (score, matched_labels)"""
    text = f"{repo['name']} {repo['description']}"
    text_lower = text.lower()

    for p in BLACKLIST:
        if re.search(p, text_lower):
            return 0, ["🚫 blacklisted"]

    matched = []
    score = 0
    level_map = {"critical": ("🎯", 30), "important": ("💡", 10), "nice": ("🔧", 3)}

    for level, patterns in CATEGORIES.items():
        emoji, weight = level_map[level]
        for pat in patterns:
            if re.search(pat, text_lower):
                matched.append(f"{emoji} {level}")
                score += weight

    return score, matched


def build_report(repos, since_label):
    """Build formatted markdown report"""
    if not repos:
        return "📭 暂无数据"

    scored = []
    threshold = STAR_THRESHOLD.get(since_label.replace("榜", ""), 50)

    for repo in repos:
        score, matches = match_relevance(repo)
        if score == 0:
            continue
        if repo["total_score"] < threshold:
            continue
        scored.append((score, repo, matches))

    scored.sort(key=lambda x: (x[0], x[2][0] if x[2] else ""), reverse=True)
    scored = scored[:MAX_RESULTS]

    if not scored:
        return "📭 今日 Trending 中无副业相关项目"

    lines = [f"📡 **副业相关项目 ({since_label})** — 共 {len(scored)} 个\n"]

    for idx, (score, repo, matches) in enumerate(scored, 1):
        name = repo["name"]
        url = repo["url"]
        desc = repo["description"][:200]
        stars = repo["total_stars"]
        lang = repo["language"]

        if idx <= 3:
            prefix = "🔥"
        elif score >= 30:
            prefix = "⭐"
        else:
            prefix = "📌"

        lines.append(f"{prefix} **{idx}. [{name}]({url})**")
        if lang:
            lines.append(f"   🗂 {lang} | ⭐{stars:,}")
        else:
            lines.append(f"   ⭐{stars:,}")
        if desc:
            lines.append(f"   > {desc}")
        unique_matches = list(dict.fromkeys(matches))
        lines.append(f"   {' '.join(unique_matches[:3])}")
        lines.append("")

    return "\n".join(lines)


def main():
    results = {}
    for mode, label in [("daily", "今日榜"), ("weekly", "本周榜")]:
        data = fetch_trending(mode)
        if "error" in data:
            results[mode] = f"⚠️ 抓取失败：{data['error']}"
        else:
            results[mode] = build_report(data["repos"], label)

    daily = results.get("daily", "⚠️ 无数据")
    weekly = results.get("weekly", "⚠️ 无数据")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"📊 **GitHub Trending 副业监控** | {now}\n")
    print("=" * 50)
    print()
    print(daily)
    print()
    print("-" * 40)
    print()
    print(weekly)
    print()
    print("—" * 25)
    print("🤖 明天继续为你盯盘 · 数据来源: ossinsight.io")


if __name__ == "__main__":
    main()
