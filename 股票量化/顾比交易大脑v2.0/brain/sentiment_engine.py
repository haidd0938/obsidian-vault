#!/usr/bin/env python3
"""
顾比交易大脑 — 情绪分析引擎
从 Vibe-Trading 借鉴的新闻情绪分析能力

功能：
  1. 新闻/热点情绪分析
  2. 板块轮动情绪
  3. 市场整体情绪指数

数据源：新浪财经 + 东方财富（免费）
"""
import sys
import os
import json
import urllib.request
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fetch_url(url, encoding='utf-8', timeout=15):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/json,*/*",
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode(encoding, errors='replace')
    except:
        return None


# ========== 情绪关键词词典 ==========

BULLISH_KEYWORDS = [
    '大涨', '涨停', '飙升', '爆发', '利好', '反弹', '回暖', '突破',
    '创新高', '资金流入', '主力买入', '北向资金', '加仓', '强烈推荐',
    '买入评级', '长牛', '牛市', '行情启动', '龙头', '领涨', '触底回升',
    '政策利好', '超预期', '景气', '高增长',
]

BEARISH_KEYWORDS = [
    '大跌', '跌停', '暴跌', '崩盘', '利空', '回调', '下挫', '破位',
    '创新低', '资金流出', '主力卖出', '减仓', '减持', '熊市',
    '风险提示', '调整', '亏损', '预警', '恐慌', '抛售', '清仓',
    '政策收紧', '不及预期', '衰退', '下滑',
]


def analyze_news_sentiment(news_list):
    """
    分析新闻列表的情绪倾向
    返回: {score: -1~1, bullish_count, bearish_count, neutral_count, sentiment}
    """
    bullish_count = 0
    bearish_count = 0

    for news in news_list:
        title = news.get("title", "")
        summary = news.get("summary", "")
        text = (title + " " + summary).lower()

        bull_hits = sum(1 for kw in BULLISH_KEYWORDS if kw in text)
        bear_hits = sum(1 for kw in BEARISH_KEYWORDS if kw in text)

        if bull_hits > bear_hits:
            bullish_count += 1
        elif bear_hits > bull_hits:
            bearish_count += 1

    total = max(len(news_list), 1)
    net = bullish_count - bearish_count
    score = net / total  # -1 ~ 1

    if score > 0.3:
        sentiment = "积极 😊"
    elif score > -0.3:
        sentiment = "中性 😐"
    else:
        sentiment = "消极 😟"

    return {
        "score": round(score, 2),
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": len(news_list) - bullish_count - bearish_count,
        "total_news": len(news_list),
        "sentiment": sentiment,
    }


def fetch_market_news():
    """获取市场新闻（复用 market-news.py 逻辑）"""
    # 新浪财经新闻
    news = []
    data = fetch_url(
        "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=20",
        encoding='utf-8'
    )
    if data:
        try:
            parsed = json.loads(data)
            items = parsed.get("result", {}).get("data", [])
            for item in items[:15]:
                title = item.get("title", "")
                if title and len(title) > 5:
                    news.append({
                        "title": title,
                        "source": "新浪财经",
                        "summary": item.get("intro", "")[:200],
                    })
        except:
            pass

    return news


def fetch_hot_sectors():
    """获取热门板块数据"""
    data = fetch_url(
        "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&fs=m:90+t:3&fields=f12,f14,f3,f4,f104,f105",
        encoding='utf-8'
    )
    if not data:
        return []

    try:
        # 处理可能的 padding
        data = data.strip()
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        sectors = []
        for item in items[:15]:
            sectors.append({
                "name": item.get("f14", ""),
                "code": item.get("f12", ""),
                "change_pct": item.get("f3", 0),
            })
        return sectors
    except:
        return []


def assess_market_sentiment():
    """
    综合评估市场情绪
    返回完整情绪报告
    """
    # 1. 新闻情绪
    news = fetch_market_news()
    news_sentiment = analyze_news_sentiment(news)

    # 2. 板块情绪
    sectors = fetch_hot_sectors()
    sector_bullish = sum(1 for s in sectors if s.get("change_pct", 0) > 0)
    sector_bearish = sum(1 for s in sectors if s.get("change_pct", 0) < 0)
    total_sectors = max(len(sectors), 1)
    sector_score = round((sector_bullish - sector_bearish) / total_sectors, 2)

    # 3. 综合情绪指数
    combined = round(news_sentiment["score"] * 0.5 + sector_score * 0.5, 2)

    if combined > 0.3:
        overall = "市场情绪积极 📈"
        advice = "市场整体偏乐观，适合关注突破机会"
    elif combined > -0.3:
        overall = "市场情绪中性 ➖"
        advice = "市场方向不明，建议控制仓位，等待信号"
    else:
        overall = "市场情绪谨慎 📉"
        advice = "市场偏弱，建议多看少动，降低风险敞口"

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "overall_sentiment": overall,
        "combined_score": combined,
        "news_sentiment": news_sentiment,
        "sector_sentiment": {
            "score": sector_score,
            "bullish_count": sector_bullish,
            "bearish_count": sector_bearish,
            "total_sectors": len(sectors),
        },
        "top_sectors": sorted(sectors, key=lambda x: abs(x.get("change_pct", 0)), reverse=True)[:5],
        "advice": advice,
        "hot_news": news[:5],
    }


if __name__ == "__main__":
    if "--simple" in sys.argv:
        s = assess_market_sentiment()
        print(f"📊 市场情绪: {s['overall_sentiment']} (综合评分: {s['combined_score']:+.2f})")
        print(f"📰 新闻情绪: {s['news_sentiment']['sentiment']} ({s['news_sentiment']['score']:+.2f})")
        print(f"🏷️ 板块情绪: 上涨{s['sector_sentiment']['bullish_count']} / 下跌{s['sector_sentiment']['bearish_count']}")
        print(f"💡 {s['advice']}")
        if s['top_sectors']:
            print("\n热门板块:")
            for sec in s['top_sectors']:
                sign = "+" if sec['change_pct'] > 0 else ""
                print(f"  {sec['name']}: {sign}{sec['change_pct']:.2f}%")
    else:
        result = assess_market_sentiment()
        print(json.dumps(result, ensure_ascii=False, indent=2))
