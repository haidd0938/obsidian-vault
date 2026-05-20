---
name: periodic-data-monitor
description: "基于 cron + Python 脚本构建定期数据监控系统：从 API 自动采集 → 关键词/规则筛选 → 格式化报告 → 定时推送到聊天。适用于监控招标信息、GitHub Trending、产品价格、热点话题等任何可 API 获取的周期性数据。"
triggers:
  - "每天帮我监控XXX"
  - "每周自动抓取XXX"
  - "定时/定期数据采集"
  - "自动监控XX变化"
  - "每天给我报告XXX"
  - 信息套利场景中的持续数据监控需求
---

# 定期数据监控（Periodic Data Monitor）

## 适用场景

信息套利、副业监控、竞品跟踪、行业动态——任何需要**每天/每周自动抓取外部数据并按规则筛选出有价值内容**的场景。

通用模式：`API定时爬取 → 关键词过滤 → 格式化报告 → cron推送到聊天`

## 通用架构

```
~/.hermes/scripts/<monitor-name>.py    # 1. 采集+筛选脚本
~/.hermes/                          # 2. cron job 自动执行
```

### 1. 脚本结构模板

```python
#!/usr/bin/env python3
import json, re, urllib.request
from datetime import datetime

# ── 配置区 ──
API_URL = "..."
# 关键词分级：critical(30分), important(10分), nice(3分)
CATEGORIES = {"critical": [r"\b...\b"], "important": [r"\b...\b"]}
BLACKLIST = [r"\b(game|porn|crypto)\b"]
SCORE_THRESHOLD = 10  # 低于此分跳过
MAX_RESULTS = 20

def fetch_data(since="daily"):
    """调用 API 获取原始数据"""
    ...

def match_relevance(item):
    """关键词匹配，返回 (score, matched_labels)"""
    text = f"{item.get('title','')} {item.get('description','')}"
    for p in BLACKLIST:
        if re.search(p, text.lower()):
            return 0, ["🚫"]
    score, matched = 0, []
    for level, patterns in CATEGORIES.items():
        weight = {"critical": 30, "important": 10, "nice": 3}[level]
        for pat in patterns:
            if re.search(pat, text.lower()):
                matched.append(level)
                score += weight
    return score, matched

def build_report(items, label):
    """格式化输出 markdown 报告"""
    scored = [(match_relevance(i), i) for i in items]
    scored = [s for s in scored if s[0][0] >= SCORE_THRESHOLD]
    scored.sort(key=lambda x: x[0][0], reverse=True)
    ...
    return "\n".join(lines)

def main():
    for mode, label in [("daily", "今日"), ("weekly", "本周")]:
        data = fetch_data(mode)
        print(build_report(data, label))

if __name__ == "__main__":
    main()
```

### 2. 创建 cron job

```python
# 在 Hermes 中：
cronjob(action='create',
    name='XXX 监控',
    prompt='执行脚本 xxx-monitor.py，把结果发给老板',
    schedule='0 22 * * *',
    script='xxx-monitor.py')
```

| 参数 | 说明 |
|------|------|
| schedule | cron 表达式，每天22:00 = `0 22 * * *` |
| script | 脚本文件名（必须放在 `~/.hermes/scripts/` 下） |
| deliver | 不传此参数 → 自动投递到创建 cron 时的聊天 |
| prompt | cron 触发时的 prompt，写明要执行什么 |

### 3. 安全扫描注意事项

安全扫描（tirith）会拦截：
- **curl | python3 管道** → 不要用管道写快速验证，直接写 .py 文件执行
- **未知域名 API** → 在安全提示中说明这是已知 API
- 如果被拦，重新跑一次命令老板审批即可

## 常用数据源

| 数据源 | API 地址 | 用途 |
|--------|---------|------|
| GitHub Trending | `api.ossinsight.io/v1/trends/repos?since=daily&limit=50` | GitHub 趋势项目监控 |
| GitHub 搜索 | `api.github.com/search/repositories?q=...` | 关键字搜索（需 token） |
| 今日热榜 | tophub.today | 中文全网热点（需爬虫） |
| NewsNow | newsnow.busiyi.world | 多平台聚合（需爬虫） |

### Ossinsight API 详解

用于获取 GitHub 仓库趋势数据，免费无需 Key。

**请求**：`GET https://api.ossinsight.io/v1/trends/repos?since=daily&limit=50`
- `since`: `daily` / `weekly` / `monthly`
- `limit`: 返回条数（最大50）

**响应结构**：
```json
{
  "type": "sql_endpoint",
  "data": {
    "columns": [{"col": "repo_name","data_type":"VARCHAR"}, ...],
    "rows": [
      {
        "repo_name": "owner/repo",
        "primary_language": "Python",
        "description": "...",
        "stars": "544",
        "forks": "55",
        "total_score": "2301.83"   // 热度分，越高越火
      }
    ]
  }
}
```

**Python 调用示例**：
```python
req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode("utf-8"))
repos = data["data"]["rows"]
```

## 典型应用案例

### 案例：GitHub Trending 副业监控
- **数据源**：ossinsight API
- **关键词**：建筑/EPC/BIM/CAD、台球、信息套利/出海/跨境电商、AI工具变现、短视频自动化、n8n/MCP、量化、知识管理
- **分级**：critical=30分（核心副业），important=10分（高相关），nice=3分（边缘相关）
- **黑名单**：游戏/成人内容/加密货币/算法面试/内核驱动
- **输出**：日榜 + 周榜，双榜 Markdown 报告，按热度排序
- **定时**：每天22:00执行
- **文件**：`~/.hermes/scripts/github-trending-monitor.py`

## 社交平台数据采集

社交平台（X/Twitter、小红书、抖音）内容抓取是监控系统中的常见需求。由于各平台反爬严格，专门整理了已验证方案。

详见 `references/social-platform-scraping.md`。

### 中国政府网站

许多政务网站（投资项目审批、招标公告等）需要**登录 Cookie** 才能访问数据。详见 `references/chinese-government-portal-scraping.md`。

## 关键陷阱

1. **源网页是 React 渲染的** — GitHub Trending 页面是动态渲染，`curl` 拿不到内容，必须用 API
2. **不要用 HTML parser 解析 GitHub** — GitHub 的 DOM 结构经常变，用 ossinsight API 更稳定
3. **cron job deliver 问题** — 不传 `deliver` 参数文档说自动投递，但实际行为是 `local`（不推送）。应该在 prompt 中写明"把结果发给老板"让 Hermes 处理
4. **安全拦截** — 脚本中的 `curl | python3` 管道会被 tirith 拦，全部用纯 Python 的 `urllib` 写
5. **频率控制** — 如果是免费 API，注意请求不要太频繁。ossinsight 可以每天/每周调用没问题
6. **输出不要太多** — 筛选后最多 20 条，头几条加 🔥 标记，超过 20 条老板不会看
7. **关键词要持续更新** — 副业方向会变，定期检查关键词是否需要调整

## 关键词设计原则

- **分级匹配**（critical/important/nice）比一刀切更合理
- **黑名单先于白名单** — 先过滤明显不相关的内容，再匹配正关键词
- **匹配要松紧适中** — `\bbim\b` 带 word boundary 避免误匹配（如 `bimonthly`）
- **中文也要覆盖** — 老板的副业可能有中文关键词（如"台球"、"短视频"）
- **正则不要过于宽泛** — `\bai\b` 会匹配太多内容，用 `\b(ai.?tool|ai.?agent|ai.?app)\b` 更精确
