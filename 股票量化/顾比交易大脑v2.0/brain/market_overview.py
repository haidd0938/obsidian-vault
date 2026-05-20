#!/usr/bin/env python3
"""
顾比交易大脑 — 大盘复盘模块
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
参考 daily_stock_analysis 的大盘复盘设计：
  指数概况 + 涨跌统计 + 板块强弱 + 市场状态综合判断

数据源：全部免费（腾讯行情 + 东方财富）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import sys
import os
import json
from datetime import datetime

BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(BRAIN_DIR)
sys.path.insert(0, BRAIN_DIR)
sys.path.insert(0, ROBOT_DIR)

from brain.data_layer import get_market_indices, get_hot_sectors, fetch_url, get_quote, to_float


def get_sector_summary():
    """
    获取板块涨跌分布统计
    从东方财富获取行业板块 + 概念板块两个维度的数据
    """
    sectors_data = {"industry": [], "concept": []}

    # 行业板块 top20
    urls = {
        "industry": "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=25&fs=m:90+t:3&fields=f12,f14,f3,f4,f104,f105,f62,f184,f66",
        "concept": "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=25&fs=m:90+t:2&fields=f12,f14,f3,f4,f104,f105,f62,f184,f66",
    }

    for sector_type, url in urls.items():
        data = fetch_url(url, encoding='utf-8')
        if not data:
            continue

        try:
            data = data.strip()
            parsed = json.loads(data)
            items = parsed.get("data", {}).get("diff", [])
            sectors = []
            for item in items[:20]:
                change = to_float(item.get("f3", 0))
                sectors.append({
                    "name": item.get("f14", ""),
                    "code": item.get("f12", ""),
                    "change_pct": round(change, 2),
                    "turnover": to_float(item.get("f4", 0)),
                    "rise_count": to_float(item.get("f104", 0)),
                    "fall_count": to_float(item.get("f105", 0)),
                })

            # 按涨跌幅排序
            sectors.sort(key=lambda x: x["change_pct"], reverse=True)
            sectors_data[sector_type] = sectors

        except:
            continue

    return sectors_data


def get_market_breadth():
    """
    获取市场三大指数涨跌家数统计
    从腾讯行情获取上证/深证/创业板的涨跌家数
    """
    breadth = {}

    # 腾讯行情接口可以获取大盘涨跌家数
    # sh000001 = 上证指数，在 fields[51]=上涨家数, fields[52]=平盘, fields[53]=下跌
    url = "https://qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000688"
    data = fetch_url(url, encoding='gbk')
    if not data:
        return breadth

    index_names = {"sh000001": "上证指数", "sz399001": "深证成指", "sz399006": "创业板指", "sh000688": "科创50"}

    for line in data.split(';\n'):
        if '="' not in line:
            continue
        try:
            raw = line.split('=\"')[1].rstrip('\";\n\r ')
            fields = raw.split('~')
            code = fields[2].split('_')[0] if len(fields) > 2 else ""

            if code in index_names:
                name = index_names[code]
                # fields[49]=代码, fields[50]=名称, fields[51]=上涨, fields[53]=下跌, fields[52]=平
                advancers = int(to_float(fields[51])) if len(fields) > 51 else 0
                decliners = int(to_float(fields[53])) if len(fields) > 53 else 0
                unchanged = int(to_float(fields[52])) if len(fields) > 52 else 0
                total = advancers + decliners + unchanged

                breadth[code] = {
                    "name": name,
                    "advancers": advancers,
                    "decliners": decliners,
                    "unchanged": unchanged,
                    "total": total,
                    "ratio": round(advancers / max(decliners, 1), 2) if decliners > 0 else advancers,
                }
        except:
            continue

    return breadth


def get_index_kline_summary(code="sh000001", days=20):
    """
    获取大盘指数的短期K线趋势判断
    """
    prefix, actual = ("sh", code[2:]) if code.startswith("sh") else ("sz", code[2:])
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={prefix}{actual},day,,,{days},qfq"
    data = fetch_url(url, encoding='utf-8')

    if not data:
        return {}

    try:
        parsed = json.loads(data)
        stock_data = parsed.get("data", {}).get(f"{prefix}{actual}", {})
        days_data = stock_data.get("qfqday") or stock_data.get("day") or stock_data.get("qt", [])

        if isinstance(days_data, dict):
            days_data = days_data.get("day", [])

        if not days_data or len(days_data) < 5:
            return {}

        closes = [float(k[2]) for k in days_data if len(k) >= 3]

        if len(closes) < 10:
            return {}

        # 判断短期趋势
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / min(10, len(closes))
        ma20 = sum(closes[-20:]) / min(20, len(closes)) if len(closes) >= 20 else ma10

        current = closes[-1]
        prev = closes[-2] if len(closes) >= 2 else current

        # 5日均线方向
        ma5_trend = "flat"
        if len(closes) >= 6:
            prev_ma5 = sum(closes[-6:-1]) / 5
            ma5_trend = "up" if ma5 > prev_ma5 else "down"

        # 判断关键均线位置
        above_ma5 = current > ma5
        above_ma20 = current > ma20

        return {
            "current": round(current, 2),
            "change_pct": round((current - prev) / prev * 100, 2),
            "ma5": round(ma5, 2),
            "ma10": round(ma10, 2),
            "ma20": round(ma20, 2),
            "above_ma5": above_ma5,
            "above_ma20": above_ma20,
            "ma5_trend": ma5_trend,
            "trend": "上涨" if (above_ma5 and ma5_trend == "up") else "下跌" if (not above_ma5 and ma5_trend == "down") else "震荡",
        }
    except:
        return {}


def build_market_overview():
    """
    构建完整大盘复盘：
    1. 指数概览
    2. 涨跌家数统计
    3. 板块强弱
    4. 综合市场状态判断
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 1. 指数概览
    indices = get_market_indices()

    # 2. 涨跌家数
    breadth = get_market_breadth()

    # 3. 板块强弱
    sectors = get_sector_summary()

    # 4. 上证指数趋势
    sh_trend = get_index_kline_summary("sh000001", 30)

    # 5. 综合状态判断
    total_advancers = sum(b.get("advancers", 0) for b in breadth.values())
    total_decliners = sum(b.get("decliners", 0) for b in breadth.values())
    market_status = "中性"
    if total_advancers > total_decliners * 1.5:
        market_status = "偏多"
    elif total_decliners > total_advancers * 1.5:
        market_status = "偏空"

    # 板块维度：涨幅榜 vs 跌幅榜
    top_gainers = sectors["industry"][:5] if sectors["industry"] else []
    top_losers = sectors["industry"][-5:] if len(sectors["industry"]) >= 5 else []

    avg_sector_change = 0
    if sectors["industry"]:
        avg_sector_change = sum(s["change_pct"] for s in sectors["industry"]) / len(sectors["industry"])

    return {
        "timestamp": timestamp,
        "indices": indices,
        "breadth": list(breadth.values()),
        "sh_trend": sh_trend,
        "sectors": {
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "avg_sector_change": round(avg_sector_change, 2),
        },
        "market_status": market_status,
        "advancers_total": total_advancers,
        "decliners_total": total_decliners,
        "adv_decl_ratio": round(total_advancers / max(total_decliners, 1), 2),
    }


def print_market_overview(overview=None):
    """输出美观的大盘复盘文本"""
    if overview is None:
        overview = build_market_overview()

    lines = []
    lines.append("=" * 55)
    lines.append(f"📊 大盘复盘 | {overview['timestamp']}")
    lines.append("=" * 55)
    lines.append("")

    # 指数概览
    lines.append("📈 指数概览")
    for idx in overview.get("indices", []):
        sign = "+" if idx.get("change_pct", 0) > 0 else ""
        lines.append(f"  {idx['name']:　<6} {idx['price']:>8.2f}  ({sign}{idx['change_pct']:.2f}%)  "
                     f"成交{idx.get('amount', 0)/10000:.0f}亿")
    lines.append("")

    # 上证趋势
    trend = overview.get("sh_trend", {})
    if trend:
        ma5_status = "📈" if trend.get("above_ma5") else "📉"
        ma20_status = "✅" if trend.get("above_ma20") else "⚠️"
        lines.append(f"📐 上证趋势: {trend.get('trend', '?')} | "
                     f"现价{trend['current']} | "
                     f"MA5{trend['ma5']} {ma5_status} | "
                     f"MA20{trend['ma20']} {ma20_status}")

    # 涨跌家数
    if overview.get("breadth"):
        lines.append(f"\n🔢 涨跌家数")
        for b in overview["breadth"]:
            if b.get("total", 0) > 0:
                total = b["total"]
                adv = b["advancers"]
                dec = b["decliners"]
                lines.append(f"  {b['name']}: 涨{adv} 跌{dec} 平{b['unchanged']}  "
                             f"涨跌比{adv}:{dec}")
        adv_total = overview.get("advancers_total", 0)
        dec_total = overview.get("decliners_total", 0)
        ratio = overview.get("adv_decl_ratio", 0)
        if adv_total > 0 or dec_total > 0:
            status_icon = "🟢" if ratio >= 1.5 else ("🔴" if ratio <= 0.67 else "🟡")
            lines.append(f"  汇总: 涨{adv_total} / 跌{dec_total} | "
                         f"涨跌比{ratio:.2f} {status_icon}")
    lines.append("")

    # 板块强弱
    gainers = overview.get("sectors", {}).get("top_gainers", [])
    losers = overview.get("sectors", {}).get("top_losers", [])
    if gainers:
        lines.append("🏆 领涨板块 (Top 5)")
        for s in gainers:
            sign = "+" if s["change_pct"] > 0 else ""
            lines.append(f"  🟢 {s['name']}: {sign}{s['change_pct']:.2f}%")
    if losers:
        lines.append("📉 领跌板块 (Bottom 5)")
        for s in losers:
            sign = "" if s["change_pct"] > 0 else ""
            lines.append(f"  🔴 {s['name']}: {s['change_pct']:.2f}%")

    avg = overview.get("sectors", {}).get("avg_sector_change", 0)
    lines.append(f"  板块平均: {avg:+.2f}%")
    lines.append("")

    # 综合判断
    status = overview.get("market_status", "中性")
    status_icons = {"偏多": "🟢", "中性": "🟡", "偏空": "🔴"}
    lines.append(f"🎯 市场状态: {status_icons.get(status, '🟡')} {status}")
    lines.append("=" * 55)

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if "--json" in sys.argv:
        overview = build_market_overview()
        print(json.dumps(overview, ensure_ascii=False, indent=2))
    else:
        result = print_market_overview()
        print(result)
