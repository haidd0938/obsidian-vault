#!/usr/bin/env python3
"""
每日智能复盘报告生成器 — 升级版
集成：大盘概况 + 技术指标分析（MACD/KDJ/RSI/均线/布林带）+ 综合评级 + 操作建议
"""

import sys
import json
import os
import subprocess
from datetime import datetime

# 加入父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ========== 配置区：修改这里定制你的观察池 ==========
DEFAULT_WATCHLIST = [
    # ETF (老板关注的)
    {"code": "159840", "name": "锂电池ETF", "type": "ETF", "category": "新能源"},
    {"code": "516020", "name": "化工ETF", "type": "ETF", "category": "化工"},
    {"code": "512480", "name": "半导体ETF", "type": "ETF", "category": "半导体"},
    {"code": "588000", "name": "科创50ETF", "type": "ETF", "category": "科技"},
    {"code": "510300", "name": "沪深300ETF", "type": "ETF", "category": "大盘"},
    # A股 (老板关注的)
    {"code": "002594", "name": "比亚迪", "type": "股票", "category": "新能源车"},
    {"code": "603986", "name": "兆易创新", "type": "股票", "category": "半导体"},
    # 行业基建/建筑相关
    {"code": "601668", "name": "中国建筑", "type": "股票", "category": "基建"},
    {"code": "601390", "name": "中国中铁", "type": "股票", "category": "基建"},
    {"code": "600585", "name": "海螺水泥", "type": "股票", "category": "建材"},
]

# 追加建筑/EPC相关的ETF
EXTRA_WATCH = [
    {"code": "159930", "name": "能源ETF", "type": "ETF", "category": "能源"},
    {"code": "159865", "name": "基建ETF", "type": "ETF", "category": "基建"},
]


def run_script(script_name, args=None):
    """运行同目录下的其他脚本"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {"error": f"{script_name} 执行失败: {result.stderr[:500]}"}
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"{script_name} 输出不是JSON"}
    except Exception as e:
        return {"error": f"{script_name} 异常: {e}"}


def get_market_overview():
    """获取大盘概况"""
    result = run_script("stock-quote.py", ["sh000001", "sz399001", "sz399006", "sh000688"])
    if isinstance(result, dict) and "error" in result:
        return result
    
    indices = []
    if isinstance(result, list):
        for idx in result:
            if "error" not in idx:
                indices.append({
                    "code": idx["code"],
                    "name": idx["name"],
                    "price": idx["current_price"],
                    "change_pct": idx["change_pct"],
                    "change": idx["change"],
                    "volume": idx.get("volume", 0),
                    "amount": idx.get("amount", 0),
                })
    return indices


def analyze_stock(code, name):
    """对单个标的做全量技术分析"""
    # 获取K线
    kline_data = run_script("stock-quote.py", ["--kline", code, "120"])
    if isinstance(kline_data, dict) and "error" in kline_data:
        return {"error": kline_data["error"], "code": code, "name": name}
    
    if isinstance(kline_data, list):
        kline_data = kline_data[0]
    
    klines = kline_data.get("klines", [])
    if not klines or len(klines) < 30:
        return {"error": f"K线数据不足({len(klines)}条)", "code": code, "name": name}
    
    # 标记code到每个K线
    for k in klines:
        k["code"] = code
    
    # 导入技术指标引擎
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "tech", os.path.join(os.path.dirname(os.path.abspath(__file__)), "technical-indicators.py")
    )
    tech = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tech)
    
    analysis = tech.full_technical_analysis(klines)
    summary = tech.full_technical_summary(klines)
    
    # 获取实时行情
    quote_data = run_script("stock-quote.py", [code])
    quote = quote_data[0] if isinstance(quote_data, list) else {}
    
    return {
        "code": code,
        "name": name,
        "analysis": analysis,
        "summary": summary,
        "quote": {k: v for k, v in quote.items() if not isinstance(v, dict) and not isinstance(v, list)},
    }


def generate_report(market_indices, stock_analyses, trade_summary=None):
    """生成完整的复盘报告"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d %H:%M")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]
    is_trading_time = now.weekday() < 5 and 9 <= now.hour < 16
    
    lines = []
    
    # ===== 头部 =====
    lines.append(f"# 📊 每日智能复盘报告")
    lines.append(f"**{today}（{weekday_cn}）**")
    lines.append(f"📌 状态: {'📈 盘中实时' if is_trading_time else '📊 收盘数据'}")
    lines.append(f"🤖 独立股票机器人 — 自动生成")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # ===== 1. 大盘概况 =====
    lines.append("## 一、大盘概况")
    lines.append("")
    if isinstance(market_indices, list) and len(market_indices) > 0:
        lines.append("| 指数 | 收盘价 | 涨跌幅 | 涨跌额 |")
        lines.append("|:---:|:------:|:------:|:-----:|")
        for idx in market_indices:
            sign = "+" if idx["change_pct"] > 0 else ""
            emoji = "🟢" if idx["change_pct"] > 0 else ("🔴" if idx["change_pct"] < 0 else "⚪")
            lines.append(f"| {emoji} {idx['name']} | {idx['price']:.2f} | **{sign}{idx['change_pct']:.2f}%** | {sign}{idx['change']:.2f} |")
        lines.append("")
        
        # 大盘综合判断
        avg_change = sum(i["change_pct"] for i in market_indices) / len(market_indices)
        if avg_change > 1.5:
            lines.append("**大盘判断**：🔥 三大指数全线大涨，市场情绪明显回暖，赚钱效应强。")
        elif avg_change > 0.5:
            lines.append("**大盘判断**：📈 市场整体上涨，走势稳健，个股活跃度较高。")
        elif avg_change > -0.5:
            lines.append("**大盘判断**：➖ 市场窄幅震荡，方向不明，题材分化明显。")
        elif avg_change > -1.5:
            lines.append("**大盘判断**：📉 市场整体回调，短期承压，建议控制仓位。")
        else:
            lines.append("**大盘判断**：🚨 市场大幅下跌，注意系统性风险，谨慎观望。")
        lines.append("")
    else:
        lines.append("❌ 大盘数据获取失败")
        lines.append("")
    
    # ===== 1.5 市场热点 =====
    lines.append("## 二、市场热点与新闻")
    lines.append("")
    # 尝试检索热点（如果market-news.py存在且可用）
    news_result = run_script("market-news.py", [])
    if isinstance(news_result, dict) and "hot_news" in news_result:
        lines.append("### 今日市场热点")
        lines.append("")
        for i, news in enumerate(news_result["hot_news"][:5], 1):
            lines.append(f"{i}. **{news['title']}**")
            if news.get("summary"):
                lines.append(f"   > {news['summary']}")
        lines.append("")
        if news_result.get("suggested_focus"):
            lines.append(f"**建议关注**：{news_result['suggested_focus']}")
            lines.append("")
    else:
        lines.append("*（热点检索模块未运行或不可用）*")
        lines.append("")
    
    # ===== 2. 标的技术面分析 =====
    lines.append("## 三、标的技术面分析")
    lines.append("")
    
    # 按信号强度排序
    sorted_analyses = sorted(stock_analyses, 
        key=lambda x: x.get("analysis", {}).get("signals", {}).get("signal_score", 0) if "error" not in x else -999,
        reverse=True)
    
    for sa in sorted_analyses:
        if "error" in sa:
            lines.append(f"### ❌ {sa.get('name', sa['code'])} — 数据异常")
            lines.append(f"原因：{sa['error']}")
            lines.append("")
            continue
        
        analysis = sa.get("analysis", {})
        signals = analysis.get("signals", {})
        quote = sa.get("quote", {})
        name = sa["name"]
        code = sa["code"]
        
        # 涨跌标识
        change_pct = quote.get("change_pct", analysis.get("last_close", 0))
        emoji = "🔥" if signals.get("signal_score", 0) >= 3 else \
                "📗" if signals.get("signal_score", 0) > 0 else \
                "📘" if signals.get("signal_score", 0) > -2 else "📕"
        
        price = quote.get("current_price", analysis.get("last_close", 0))
        price_str = f"{price:.2f}" if isinstance(price, (int, float)) else str(price)
        
        lines.append(f"### {emoji} {name}（{code}）— 现价 {price_str}元")
        lines.append("")
        
        # 实时行情概要
        if quote and "change_pct" in quote:
            cp = quote["change_pct"]
            sign = "+" if cp > 0 else ""
            lines.append(f"**今日涨跌**：{sign}{cp:.2f}% | **综合评级**：**{signals.get('signal_strength', '未评级')}**")
        else:
            lines.append(f"**综合评级**：**{signals.get('signal_strength', '未评级')}**")
        lines.append("")
        
        # 技术指标摘要
        ma_data = analysis.get("ma", {})
        macd_data = analysis.get("macd", {})
        kdj_data = analysis.get("kdj", {})
        rsi_data = analysis.get("rsi", {})
        boll_data = analysis.get("boll", {})
        
        if ma_data:
            ma_text = " | ".join([f"{k}={v}" for k, v in sorted(ma_data.items())])
            lines.append(f"📐 均线：{ma_text}")
            lines.append(f"   排列：{analysis.get('ma_arrangement', 'N/A')}")
        if macd_data:
            lines.append(f"📊 MACD：DIF={macd_data.get('DIF')} | DEA={macd_data.get('DEA')} | 柱={macd_data.get('MACD')}")
        if kdj_data:
            kdj_str = f"K={kdj_data.get('K')} | D={kdj_data.get('D')} | J={kdj_data.get('J')}"
            kdj_warn = "⚠️超买" if (kdj_data.get('K') or 0) > 80 else ("💡超卖" if (kdj_data.get('K') or 0) < 20 else "")
            lines.append(f"📈 KDJ：{kdj_str} {kdj_warn}")
        if rsi_data:
            rsi_str = f"RSI6={rsi_data.get('RSI6')} | RSI12={rsi_data.get('RSI12')} | RSI24={rsi_data.get('RSI24')}"
            lines.append(f"📉 RSI：{rsi_str}")
        if boll_data:
            lines.append(f"📦 布林带：中轨={boll_data.get('MID')} | 上轨={boll_data.get('UPPER')} | 下轨={boll_data.get('LOWER')}")
        
        # 详细信号
        lines.append("")
        lines.append("**信号明细**：")
        for sig in signals.get("signals", []):
            icon = "🟢" if sig["signal"] in ("看多", "强烈看多", "偏多") else \
                   "🔴" if sig["signal"] in ("看空", "强烈看空", "偏空") else "🟡"
            lines.append(f"  {icon} [{sig['indicator']}] {sig['signal']}: {sig['detail']}")
        
        # 60日价格区间
        pr = analysis.get("price_range", {})
        if pr:
            lines.append(f"  📍 60日区间：{pr.get('low_60d')} ~ {pr.get('high_60d')}")
        
        lines.append("")
    
    # ===== 3. 综合策略建议 =====
    lines.append("## 四、综合策略建议")
    lines.append("")
    
    # 统计多空
    bullish_count = sum(1 for sa in stock_analyses 
        if "error" not in sa and sa.get("analysis", {}).get("signals", {}).get("signal_score", 0) >= 1.5)
    bearish_count = sum(1 for sa in stock_analyses 
        if "error" not in sa and sa.get("analysis", {}).get("signals", {}).get("signal_score", 0) <= -1.5)
    neutral_count = len(stock_analyses) - bullish_count - bearish_count - sum(1 for sa in stock_analyses if "error" in sa)
    
    lines.append(f"**多空力量**：看多 {bullish_count} | 中性 {neutral_count} | 看空 {bearish_count}")
    lines.append("")
    
    # 大盘关联建议
    if isinstance(market_indices, list) and len(market_indices) > 0:
        avg_change = sum(i["change_pct"] for i in market_indices) / len(market_indices)
        if avg_change > 1:
            lines.append("✅ **建议**：大盘强势，技术面偏多的标的可考虑建仓或加仓。")
        elif avg_change > -0.5:
            if bullish_count > bearish_count:
                lines.append("✅ **建议**：大盘震荡但个股机会存在，精选技术面强势标的。")
            else:
                lines.append("⚠️ **建议**：大盘震荡且多数标的偏弱，建议观望为主。")
        else:
            lines.append("🚨 **建议**：大盘回调明显，多看少动，等待企稳信号。")
    lines.append("")
    
    # ===== 4. 模拟交易日志 =====
    if trade_summary:
        lines.append("## 五、模拟交易记录")
        lines.append("")
        lines.append(f"**累计收益**：{trade_summary.get('total_return', 0):.2f}%")
        lines.append(f"**当前持仓**：{trade_summary.get('position_count', 0)} 只")
        lines.append(f"**交易次数**：{trade_summary.get('trade_count', 0)} 笔")
        lines.append("")
    
    # ===== 尾部 =====
    lines.append("---")
    lines.append(f"*🤖 股票机器人自动生成 · {today}*")
    lines.append("*⚠️ 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*")
    
    return "\n".join(lines)


def run(save=True, watchlist=None):
    """主入口"""
    if watchlist is None:
        watchlist = DEFAULT_WATCHLIST + EXTRA_WATCH
    
    print("🔍 获取大盘数据...", file=sys.stderr)
    indices = get_market_overview()
    
    print(f"🔍 分析 {len(watchlist)} 个标的...", file=sys.stderr)
    analyses = []
    for i, w in enumerate(watchlist):
        print(f"   [{i+1}/{len(watchlist)}] {w['name']}（{w['code']}）...", file=sys.stderr)
        result = analyze_stock(w["code"], w["name"])
        analyses.append(result)
    
    # 尝试获取模拟交易摘要
    trade_summary = None
    trade_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trade-log.py")
    if os.path.exists(trade_script):
        try:
            result = subprocess.run(
                [sys.executable, trade_script, "--summary"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                trade_summary = json.loads(result.stdout)
        except:
            pass
    
    report = generate_report(indices, analyses, trade_summary)
    
    if save:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        filename = f"复盘报告_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = os.path.join(log_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ 报告已保存: {filepath}", file=sys.stderr)
    
    print(report)


if __name__ == "__main__":
    watchlist = DEFAULT_WATCHLIST + EXTRA_WATCH
    save = "--no-save" not in sys.argv
    if "--watch" in sys.argv:
        idx = sys.argv.index("--watch")
        custom_codes = sys.argv[idx+1:]
        watchlist = [{"code": c, "name": c, "type": "自定义"} for c in custom_codes]
    
    run(save=save, watchlist=watchlist)
