# GitHub Trending 副业监控 — 实现实录

## 概述
每天22:00扫描 GitHub Trending 上星标涨得快的项目，筛选与老板副业相关的，输出报告。

## 数据源：ossinsight.io API
- URL: `https://api.ossinsight.io/v1/trends/repos?since=daily&limit=50`
- 免费、无需 Key
- 返回 `repo_name`, `description`, `stars`, `total_score`（热度分）, `primary_language`

## 关键词分类

### 🎯 Critical（30分）— 核心副业方向
- 建筑/EPC: `bim|building|construction|architecture|structural|engineering|epc|civil|cad|cae|revit|autocad`
- 台球: `billiard|billiards|pool|snooker`
- 信息套利/副业: `arbitrage|resell|side.?hustle|passive.?income|monetize`
- 出海/TikTok: `tiktok|short.?video|cross.?border|crossborder|export|overseas`
- AI工具变现: `ai.?tool|ai.?wrapper|ai.?app|gpt.?wrapper|llm.?app|saas|indie.?hacker`
- 短视频自动化: `video.?editing|video.?generation|video.?automation`
- 跨境电商: `dropshipping|print.?on.?demand|affiliate|ecommerce`

### 💡 Important（10分）— 高相关
- AI自动化: `no.?code|low.?code|automation|workflow|agent.?framework`
- MCP/API生态: `mcp|model.?context.?protocol|api.?gateway`
- n8n: `n8n|make\.com|zapier`
- 量化/股票: `stock|trading|quant|finance|portfolio|backtest`
- 知识管理: `knowledge.?base|obsidian|notion|second.?brain`
- 社交媒体工具: `social.?media|scheduler|analytics`

### 🔧 Nice（3分）— 边缘相关
- 通用技术栈: `python|fastapi|react|next|docker|devops`
- 数据/可视化: `database|sql|monitoring|visualization|chart`

### 🚫 黑名单
- 游戏: `game|gaming|minecraft|roblox|unity`
- 成人: `porn|xxx|adult|nsfw`
- 加密货币: `crypto|bitcoin|nft|blockchain|defi`
- 算法面试: `leetcode|algorithm|interview`

## 脚本位置
`~/.hermes/scripts/github-trending-monitor.py`

## Cron Job
```json
{
  "name": "GitHub Trending 副业监控",
  "schedule": "0 22 * * *",
  "script": "github-trending-monitor.py",
  "prompt": "执行脚本 github-trending-monitor.py，把执行结果发给老板。"
}
```

## 运行截图（2026-05-04 测试）
成功输出日榜20条+周榜20条，共40条。日榜按相关度排序，top hits 包括：
- 🔥 Pixelle-Video（AI短视频引擎，直接命中视频自动化）
- 🔥 text-to-cad（文字转CAD，直接命中建筑方向）
- 🔥 tonhowtf/omniget（多平台视频下载器，信息套利素材工具）
- 💡 n8n-mcp（用Claude构建n8n工作流）
- 💡 daily_stock_analysis（LLM驱动的股票分析器，零成本）
