---
name: scrapling
description: 🕷️ Scrapling 自适应网页抓取框架 — 反爬绕过(Cloudflare Turnstile)、Stealth浏览器、Spider爬虫框架、自适应解析。适用于大众点评/美团/竞品网站/招标信息等数据采集场景。替代 requests+BS4/Scrapy 组合的一站式方案。
version: "1.0.0"
metadata:
  homepage: "https://scrapling.readthedocs.io"
  github: "https://github.com/D4Vinci/Scrapling"
  requires:
    bins: [python3]
    pip: [scrapling]
---

# Scrapling 技能笔记

## 最佳路线图（按成本+速度优先级排序）

### 🥇 方案A：纯HTTP请求（零成本，最快）
**适用场景**：静态页面、简单网站、博客文章、API数据
**特征**：无浏览器，纯网络请求，速度最快，内存占用最小
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')
page.css('h1::text').get()
```
**CLI一行命令**：
```bash
scrapling extract get 'https://example.com' content.md
# 有CSS选择器提取特定内容
scrapling extract get 'https://example.com' content.txt -s 'article.main'
```

### 🥈 方案B：FetcherSession（低成本，快）
**适用场景**：需要Cookie维持会话、需要分页、需要伪装TLS指纹
**特征**：可复用Session，TLS指纹模仿浏览器，HTTP/3支持
```python
from scrapling.fetchers import FetcherSession
with FetcherSession(impersonate='chrome', http3=True) as s:
    p1 = s.get('https://example.com/page1', stealthy_headers=True)
    p2 = s.get('https://example.com/page2', stealthy_headers=True)
```

### 🥉 方案C：DynamicFetcher（中成本，慢3档）
**适用场景**：JS动态渲染页面（React/Vue等SPA）、需要等待网络空闲
**特征**：完整浏览器引擎，可执行JS，可阻塞广告/外部资源省流量
```python
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch('https://spa-site.com', headless=True, network_idle=True)
```
**CLI**：
```bash
scrapling extract fetch 'https://spa-site.com' content.md --network-idle
```

### 🛡️ 方案D：StealthyFetcher（高成本，慢3档）
**适用场景**：Cloudflare防护站、反爬严格的站（大众点评、美团）、有Turnstile验证
**特征**：最强反爬绕过，内置CF Turnstile自动解，WebRTC阻断，DNS防泄露
```python
from scrapling.fetchers import StealthyFetcher
StealthyFetcher.adaptive = True  # 开启自适应模式
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare', solve_cloudflare=True)
```
**CLI**：
```bash
scrapling extract stealthy-fetch 'https://protected-site.com' content.md --solve-cloudflare
```

### 🕸️ 方案E：Spider爬虫框架（大规模场景）
**适用场景**：整站爬取、多页面分页、需要并发/暂停恢复
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "myspider"
    start_urls = ["https://example.com/"]
    concurrent_requests = 10
    download_delay = 1.0
    
    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {"title": item.css('h2::text').get()}
        next_p = response.css('.next a')
        if next_p: yield response.follow(next_p[0].attrib['href'])

# 支持暂停恢复
result = MySpider(crawldir="./crawl_data").start()
result.items.to_json("output.json")
```

## 进阶技术

### 自适应解析（对付网站改版）
```python
from scrapling.fetchers import StealthyFetcher
StealthyFetcher.adaptive = True
# 第一次抓取用 auto_save=True 保存元素特征
page = StealthyFetcher.fetch('https://example.com')
products = page.css('.product', auto_save=True)
# 网站改版后，用 adaptive=True 自动重新定位
products = page.css('.product', adaptive=True)
```

### 代理轮换（反爬升级）
```python
from scrapling.fetchers import FetcherSession
from scrapling.fetchers.proxy import ProxyRotator

rotator = ProxyRotator([
    'http://proxy1:8080',
    'http://proxy2:8080',
    'http://proxy3:8080',
], strategy='cyclic')  # 或 'random'

with FetcherSession(impersonate='chrome', proxy_rotator=rotator) as s:
    pages = [s.get(url) for url in urls]  # 自动轮换代理
```

### DNS泄露防护
```python
with StealthySession(headless=True, dns_over_https=True) as session:
    page = session.fetch('https://example.com')
```

### 开发模式（省网络请求，免费）
```python
class MySpider(Spider):
    name = "myspider"
    development_mode = True  # 第一次抓取后缓存到本地，后续复用
    ...
```

## 新网站抓取正确决策树

```
目标网站 → 先试 Fetcher.get()
  ├─ 成功拿到数据 → ✅ 用方案A（零成本，最快）
  ├─ 被拦截/返回空 → 试 FetcherSession(impersonate='chrome'...)
  │   ├─ 成功 → ✅ 用方案B（低成本）
  │   ├─ 需要JS渲染 → 试 DynamicFetcher (headless, network_idle)
  │   │   ├─ 成功 → ✅ 用方案C（中成本）
  │   │   └─ 有Cloudflare → 试 StealthyFetcher (solve_cloudflare)
  │   │       ├─ 成功 → ✅ 用方案D（高成本但能过）
  │   │       └─ 失败 → 需要代理+Stealthy组合
  │   └─ 需要大量页面 → 用 Spider 框架（方案E）
  └─ 稳定后 → 开启 adaptive=True，防改版
```

## 会话管理（省钱关键）

| 场景 | 推荐 | 理由 |
|------|------|------|
| 单次抓取 | `Fetcher.get()` | 一次性请求，用完即弃 |
| 短时多次（<5页） | `FetcherSession` | 复用连接，省建立成本 |
| 长时批量（>5页） | `FetcherSession` + Session | 保持Cookie，避免重复验证 |
| 需要反爬 | `StealthySession` | 浏览器保持打开，只开一次 |
| 并发大批量 | `AsyncStealthySession(max_pages=4)` | 浏览器连接池，平衡速度和资源 |

## 已安装组件

```
核心: scrapling 0.4.7 (已安装)
扩展: pip install "scrapling[all]"  → 含 fetchers + shell + ai
浏览器: scrapling install --force  → 安装Playwright Chromium
```

当前环境：Intel Mac (无GPU)，macOS。Playwright浏览器可以跑但Chromium会稍慢。
当前仅安装了核心包（`scrapling`），fetchers/浏览器 依赖**按需安装**：
```bash
python3 -m pip install "scrapling[fetchers]"  # 需要时才装
python3 -m scrapling install  # 下载浏览器
```

## MCP 服务器（AI辅助抓取）

支持用AI（Claude等）指挥抓取：
```bash
# 启动MCP服务器
python3 -m scrapling.ai.mcp
```

MCP工具清单：
- `scrapling_get` — HTTP GET请求 + 解析
- `scrapling_post` — HTTP POST请求 + 解析
- `scrapling_fetch` — 浏览器渲染 + 抓取
- `scrapling_stealthy_fetch` — 反爬绕过 + 抓取
- `scrapling_extract` — CSS选择器提取
- `scrapling_session` — 管理持久化会话

## 最佳实践 & 省钱省时策略

1. **从小到大升级**：永远先试最轻量的方案（Fetcher.get），失败再升级
2. **CLI `--ai-targeted`**：AI消费场景用此参数，自动清理页面噪音+广告拦截，省token
3. **CSS选择器收窄**：`-s 'div.content'` 限制输出范围，省token省传输
4. **开发模式**：Spider开发时 `development_mode=True`，不重复请求目标服务器
5. **缓存**：Scrapling有内部缓存机制，重复URL自动用缓存
6. **代理免费方案**：先用无代理试，被Block再加。免费代理推荐列表：[free-proxy-list]
7. **并发控制**：Spider里设 `concurrent_requests=5`，不要全量，避免被封IP
8. **输出格式选择**：`.md` 最省token；`.txt` 纯文本次之；`.html` 最费

## 安装（按需）

核心包（当前已装）：
```bash
python3 -m pip install scrapling
```

完整功能（有反爬/浏览器需求时再装）：
```bash
python3 -m pip install "scrapling[all]"
python3 -m scrapling install --force  # 下载浏览器
```

## 典型场景速查

| 你的场景 | 推荐方案 | 理由 |
|----------|----------|------|
| 抓GitHub Trending | Fetcher.get() | 静态API内容 |
| 抓招标信息/项目备案 | FetcherSession | 需Cookie维持登录，轻量 |
| 大众点评差评球房 | StealthyFetcher | 反爬严格+Cloudflare |
| 公众号文章 | Fetcher.get() → DynamicFetcher | 先试HTTP，不行再开浏览器 |
| EPC行业资讯网站 | Fetcher.get() | 一般新闻站，无动态加载 |
| 短视频平台统计 | DynamicFetcher | SPA页面需要JS渲染 |
| 竞品大规模监控 | Spider框架 | 并发+暂停恢复+代理轮换 |
