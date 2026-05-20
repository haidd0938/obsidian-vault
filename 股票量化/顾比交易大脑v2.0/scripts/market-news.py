#!/usr/bin/env python3
"""
市场热点与新闻检索模块
功能：
1. 从新浪财经/同花顺/东方财富等免费源检索当日热点新闻
2. 提取板块轮动信息
3. 标记重大政策/行业事件

数据源：全免费，无需API Key
"""

import sys
import json
import urllib.request
import urllib.parse
import re
from datetime import datetime


def fetch_url(url, encoding='utf-8'):
    """通用URL获取"""
    try:
        req = urllib.request.Request(
            url, 
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/json,*/*",
                "Referer": "https://finance.sina.com.cn",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode(encoding, errors='replace')
        return data
    except Exception as e:
        return None


def fetch_sina_hot_news():
    """从新浪财经获取热门新闻"""
    urls = [
        ("https://feed.mix.sina.com.cn/api/roll/get", "新浪财经"),
        ("https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=15", "新浪财经"),
    ]
    
    news = []
    for url, source in urls:
        data = fetch_url(url)
        if data:
            try:
                parsed = json.loads(data)
                items = parsed.get("result", {}).get("data", [])
                for item in items[:10]:
                    title = item.get("title", "")
                    if title and len(title) > 5:
                        news.append({
                            "title": title,
                            "source": source,
                            "url": item.get("url", ""),
                            "time": item.get("ctime", ""),
                            "summary": item.get("intro", "")[:150],
                        })
            except json.JSONDecodeError:
                continue
    
    return news


def fetch_sina_news():
    """从新浪财经首页抓取热点"""
    data = fetch_url("https://finance.sina.com.cn/", encoding='gbk')
    if not data:
        return []
    
    news = []
    # 提取新闻标题
    patterns = [
        r'<a[^>]*href="(https://finance\.sina\.com\.cn[^"]*)"[^>]*title="([^"]*)"',
        r'<a[^>]*href="([^"]*)"[^>]*>(?:<[^>]*>)*([^<]{10,80})(?:<[^>]*>)*</a>',
    ]
    
    seen = set()
    for pat in patterns:
        for m in re.finditer(pat, data):
            url = m.group(1)
            title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if title and len(title) > 6 and title not in seen:
                if any(kw in title for kw in ['A股', '股票', '涨停', '跌停', '板块', '政策', '行情', 
                                               '涨', '跌', '基金', '投资', '市场', '资金']):
                    seen.add(title)
                    news.append({
                        "title": title,
                        "source": "新浪财经",
                        "url": url,
                        "summary": "",
                    })
    
    return news[:15]


def fetch_eastmoney_hot():
    """从东方财富获取热门板块"""
    data = fetch_url("https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=15&fs=m:90+t:3&fields=f12,f14,f3,f4,f104,f105")
    if not data:
        return {"hot_sectors": [], "hot_stocks": []}
    
    try:
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        sectors = []
        for item in items[:15]:
            sectors.append({
                "name": item.get("f14", ""),
                "code": item.get("f12", ""),
                "change_pct": item.get("f3", 0),
            })
        return {"hot_sectors": sectors}
    except:
        return {"hot_sectors": []}


def get_market_focus():
    """整合所有数据源，输出当日关注焦点"""
    sina_news = fetch_sina_hot_news() or fetch_sina_news()
    sectors = fetch_eastmoney_hot()
    
    # === 市场热点分类 ===
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "hot_news": [],
        "hot_sectors": sectors.get("hot_sectors", []),
        "suggested_focus": "",
    }
    
    # 热门新闻去重
    seen_titles = set()
    for news in sina_news:
        t = news["title"].strip()
        if t and len(t) > 6 and t not in seen_titles:
            seen_titles.add(t)
            result["hot_news"].append(news)
    
    result["hot_news"] = result["hot_news"][:10]
    
    # === 根据新闻内容智能生成关注建议 ===
    all_text = " ".join([n["title"] + " " + n.get("summary", "") for n in result["hot_news"]])
    
    focus_keywords = []
    # 检查是否包含特定关键词
    if any(kw in all_text for kw in ['新能源', '锂电池', '新能源汽车', '光伏', '风电']):
        focus_keywords.append("新能源")
    if any(kw in all_text for kw in ['半导体', '芯片', '集成电路', 'AI', '人工智能', '算力']):
        focus_keywords.append("科技/半导体/AI")
    if any(kw in all_text for kw in ['基建', '建筑', '建材', '房地产', '地产', '水利', '铁路']):
        focus_keywords.append("基建/建材")
    if any(kw in all_text for kw in ['化工', '材料', '有色', '钢铁', '煤炭']):
        focus_keywords.append("周期板块")
    if any(kw in all_text for kw in ['消费', '白酒', '食品', '旅游', '餐饮']):
        focus_keywords.append("消费")
    if any(kw in all_text for kw in ['医药', '医疗', '创新药', '中药']):
        focus_keywords.append("医药")
    if any(kw in all_text for kw in ['政策', '利好', '重大', '改革', '新规', '监管']):
        focus_keywords.append("政策面")
    
    if focus_keywords:
        result["suggested_focus"] = f"今日市场焦点板块：{'、'.join(focus_keywords)}。建议关注相关ETF和龙头股。"
    else:
        result["suggested_focus"] = "市场无明显板块性热点，建议关注大盘整体走势。"
    
    return result


if __name__ == "__main__":
    import time
    
    # 简单输出
    if "--simple" in sys.argv:
        result = get_market_focus()
        print(f"📰 市场热点（{result['timestamp']}）")
        print("=" * 50)
        for i, news in enumerate(result["hot_news"][:5], 1):
            print(f"{i}. {news['title']}")
        print()
        if result["hot_sectors"]:
            print("🏷️ 热门板块：")
            for s in sorted(result["hot_sectors"], key=lambda x: abs(x.get("change_pct", 0)), reverse=True)[:5]:
                sign = "+" if s["change_pct"] > 0 else ""
                print(f"   {s['name']}: {sign}{s['change_pct']:.2f}%")
        print()
        print(f"💡 {result['suggested_focus']}")
    else:
        result = get_market_focus()
        print(json.dumps(result, ensure_ascii=False, indent=2))
