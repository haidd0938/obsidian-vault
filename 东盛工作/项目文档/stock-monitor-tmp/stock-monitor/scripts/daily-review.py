#!/usr/bin/env python3
"""
每日股票复盘报告生成脚本
功能：获取行情数据 → 计算趋势 → 生成完整复盘报告
"""

import sys
import json
import os
import subprocess
from datetime import datetime

# 默认监控列表
DEFAULT_WATCHLIST = [
    {"code": "159840", "name": "锂电池ETF", "type": "ETF"},
    {"code": "516020", "name": "化工ETF", "type": "ETF"},
    {"code": "512480", "name": "半导体ETF", "type": "ETF"},
    {"code": "002594", "name": "比亚迪", "type": "股票"},
    {"code": "603986", "name": "兆易创新", "type": "股票"},
]


def fetch_quotes(codes):
    """通过子进程调用 stock-quote.py 获取行情"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        [sys.executable, os.path.join(script_dir, "stock-quote.py")] + codes,
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"行情获取失败: {result.stderr}")
        return []
    return json.loads(result.stdout)


def get_market_index():
    """获取大盘指数"""
    indices = fetch_quotes(["sh000001", "sz399001", "sz399006"])
    result = []
    for idx in indices:
        if "error" in idx:
            continue
        result.append({
            "name": idx["name"],
            "price": idx["current_price"],
            "change_pct": idx["change_pct"],
            "change": idx["change"],
        })
    return result


def generate_full_report():
    """生成完整复盘报告"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d %H:%M")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
    
    lines = []
    lines.append(f"# 每日复盘 — {today}（{weekday_cn}）\n")
    
    # ===== 1. 大盘概况 =====
    lines.append("## 大盘概况\n")
    indices = get_market_index()
    if indices:
        lines.append("| 指数 | 收盘价 | 涨跌幅 |")
        lines.append("|:---:|:------:|:------:|")
        for idx in indices:
            sign = "+" if idx["change_pct"] > 0 else ""
            lines.append(f"| {idx['name']} | {idx['price']:.2f} | **{sign}{idx['change_pct']:.2f}%** |")
        lines.append("")
    
    # 大盘判断
    if indices:
        avg_change = sum(idx["change_pct"] for idx in indices) / len(indices)
        if avg_change > 1.5:
            lines.append("**大盘判断**：三大指数全线上涨，市场情绪明显回暖。\n")
        elif avg_change > 0.5:
            lines.append("**大盘判断**：市场整体上涨，走势稳健。\n")
        elif avg_change > -0.5:
            lines.append("**大盘判断**：市场窄幅震荡，方向不明。\n")
        elif avg_change > -1.5:
            lines.append("**大盘判断**：市场整体回调，谨慎观望。\n")
        else:
            lines.append("**大盘判断**：市场大幅下跌，注意风险。\n")
    
    # ===== 2. 持仓复盘 =====
    codes = [w["code"] for w in DEFAULT_WATCHLIST]
    results = fetch_quotes(codes)
    
    lines.append("## 持仓复盘\n")
    for r in results:
        if "error" in r:
            lines.append(f"### {r.get('code', '?')} ❌ 获取失败\n")
            lines.append(f"错误：{r['error']}\n")
            continue
        
        name = r["name"]
        code = r["code"]
        price = r["current_price"]
        change = r["change"]
        change_pct = r["change_pct"]
        
        # 涨跌图标和趋势描述
        if change_pct > 3:
            icon = "🔥"
            trend_desc = "大涨"
        elif change_pct > 0:
            icon = "📈"
            trend_desc = "上涨"
        elif change_pct < -3:
            icon = "💧"
            trend_desc = "大跌"
        elif change_pct < 0:
            icon = "📉"
            trend_desc = "下跌"
        else:
            icon = "➖"
            trend_desc = "平盘"
        
        lines.append(f"### {name}（{code}）{icon}\n")
        lines.append(f"| 指标 | 数据 |")
        lines.append(f"|:---:|:----:|")
        lines.append(f"| 今日收盘 | **{price}元** |")
        lines.append(f"| 今日涨幅 | **{change_pct:.2f}%**（{change}元）|")
        lines.append(f"| 今日最高 | {r['high']}元 |")
        lines.append(f"| 今日最低 | {r['low']}元 |")
        lines.append(f"| 振幅 | {r['amplitude']:.2f}% |")
        
        if r["volume"] > 0:
            lines.append(f"| 成交量 | {r['volume']/10000:.2f}万手 |")
        if r["amount"] > 10000:
            lines.append(f"| 成交额 | {r['amount']/100000000:.2f}亿元 |")
        if r["market_cap"] > 0:
            lines.append(f"| 总市值 | {r['market_cap']:.2f}亿元 |")
        if r["circulating_cap"] > 0:
            lines.append(f"| 流通市值 | {r['circulating_cap']:.2f}亿元 |")
        if r["pe_ratio"] > 0:
            lines.append(f"| 市盈率(动态) | {r['pe_ratio']:.2f}倍 |")
        
        # 趋势判断
        lines.append("")
        if change_pct > 3:
            lines.append(f"**趋势判断**：{name}今日大涨{change_pct:.2f}%，走势强劲，量价配合良好。\n")
        elif change_pct > 1:
            lines.append(f"**趋势判断**：{name}今日温和上涨{change_pct:.2f}%，趋势向好。\n")
        elif change_pct > 0:
            lines.append(f"**趋势判断**：{name}今日微涨{change_pct:.2f}%，走势平稳。\n")
        elif change_pct > -1:
            lines.append(f"**趋势判断**：{name}今日微跌{change_pct:.2f}%，窄幅震荡，属于正常调整。\n")
        elif change_pct > -3:
            lines.append(f"**趋势判断**：{name}今日回调{change_pct:.2f}%，短期承压，关注后续走势。\n")
        else:
            lines.append(f"**趋势判断**：{name}今日大跌{change_pct:.2f}%，注意风险控制。\n")
    
    # ===== 3. 趋势汇总 =====
    lines.append("## 趋势汇总\n")
    lines.append("| 标的 | 今日涨跌 | 趋势评级 |")
    lines.append("|:---:|:--------:|:--------:|")
    for r in results:
        if "error" in r:
            continue
        pct = r["change_pct"]
        if pct > 3: rating = "⭐⭐⭐ 强势"
        elif pct > 1: rating = "⭐⭐ 向好"
        elif pct > 0: rating = "⭐ 平稳"
        elif pct > -1: rating = "⭐ 微调"
        elif pct > -3: rating = "⭐⭐ 回调"
        else: rating = "⭐⭐⭐ 警惕"
        sign = "+" if pct > 0 else ""
        lines.append(f"| {r['name']}（{r['code']}）| {sign}{pct:.2f}% | {rating} |")
    lines.append("")
    
    # ===== 4. 操作建议 =====
    lines.append("## 操作建议\n")
    lines.append("> ⚠️ 以下建议仅供参考，不构成投资建议，请根据自身情况判断。\n")
    
    # 简单策略建议
    up_count = sum(1 for r in results if "error" not in r and r["change_pct"] > 1)
    down_count = sum(1 for r in results if "error" not in r and r["change_pct"] < -1)
    
    if up_count >= 3:
        lines.append("今日多数标的上涨，市场氛围较好。若后续维持强势，可考虑择机建仓。\n")
    elif down_count >= 3:
        lines.append("今日多数标的回调，建议观望为主，等待企稳信号。\n")
    else:
        lines.append("各标的分化明显，建议区别对待，强势标的可关注，弱势标的暂观望。\n")
    
    lines.append("---\n")
    lines.append(f"*报告生成时间：{today}*\n")
    
    return "\n".join(lines)


if __name__ == "__main__":
    report = generate_full_report()
    print(report)
    
    # 可选：保存到文件
    if "--save" in sys.argv:
        filename = f"复盘报告_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ 报告已保存: {filename}")
