#!/usr/bin/env python3
"""
顾比交易大脑 — 主入口
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
统一调度：技术面 → 基本面 → 情绪面 → 融合决策 → 报告输出

用法：
  python3 brain/trading_brain.py full       # 完整大脑运行（推荐）
  python3 brain/trading_brain.py scan       # 快速扫描
  python3 brain/trading_brain.py deep <code> # 深度分析
  python3 brain/trading_brain.py cron       # 定时报告模式
  python3 brain/trading_brain.py cockpit    # 大脑仪表盘

输出：融合信号报告 (技术+基本面+情绪 -> 综合置信度评分+买卖建议+YOLO模式)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import sys
import os
import json
from datetime import datetime

# 加载路径
ROBOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.join(ROBOT_DIR, "scripts")
BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROBOT_DIR, "data")
LOG_DIR = os.path.join(ROBOT_DIR, "logs")

sys.path.insert(0, ROBOT_DIR)
sys.path.insert(0, BRAIN_DIR)

from brain.config import WATCHLIST, LOG_DIR
from brain.data_layer import get_quote, get_kline, get_hot_sectors, get_market_indices
from brain.fundamental_analysis import batch_analysis
from brain.sentiment_engine import assess_market_sentiment
from brain.signal_fusion import fusion_decision
from brain.yolo_trader import suggest_trade, check_yolo
from brain.cookie_jar import get_summary as get_cookie_jar_summary
from brain.market_overview import build_market_overview, print_market_overview
from brain.decision_engine import build_decision_card, print_decision_cards


def run_full_report():
    """
    完整大脑运行流程：
    1. 大盘 + 热点
    2. 技术面分析（调用 stock-robot 的 technical-indicators）
    3. 基本面分析
    4. 情绪分析
    5. 三引擎融合决策
    6. YOLO 安全输出
    7. 生成结构化报告
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    print("🧠 顾比交易大脑 | 完整运行模式")
    print("=" * 55)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    yolo_mode = check_yolo()
    print(f"🛡️ YOLO: {'安全模式' if yolo_mode else '自动模式'}")
    print()

    # ===== 步骤1: 大盘 + 热点 =====
    print("🔍 [1/5] 获取大盘数据...")
    indices = get_market_indices()
    if indices:
        for idx in indices:
            sign = "+" if idx["change_pct"] > 0 else ""
            print(f"  📊 {idx['name']}: {idx['price']:.2f} ({sign}{idx['change_pct']:.2f}%)")
    print()

    # ===== 大盘复盘（新增） =====
    print("=" * 55)
    print("📊 大盘复盘")
    market_overview = build_market_overview()
    print(print_market_overview(market_overview))
    print()

    # ===== 步骤2: 基本面分析 =====
    print("🔍 [2/5] 基本面分析...")
    fundamental_results = batch_analysis(WATCHLIST)
    for f in fundamental_results:
        if "error" not in f:
            sig = f.get("fundamentals_signal", "")
            score = f.get("fundamentals_score", 0)
            print(f"  📗 {f['name']}({f['code']}): PE={f['valuation']['pe']:.1f} | ROE={f['valuation']['roe']:.1f}% | 评分={score:.1f} | {sig}")
    print()

    # ===== 步骤3: 情绪分析 =====
    print("🔍 [3/5] 市场情绪分析...")
    sentiment = assess_market_sentiment()
    print(f"  📰 {sentiment['overall_sentiment']} (综合分: {sentiment['combined_score']:+.2f})")
    print(f"  💡 {sentiment['advice']}")
    if sentiment.get("top_sectors"):
        top = sentiment["top_sectors"][:3]
        sector_strs = [f"{s['name']}({'+' if s['change_pct']>0 else ''}{s['change_pct']:.2f}%)" for s in top]
        print(f"  🏷️  热门板块: {' | '.join(sector_strs)}")
    print()

    # ===== 步骤4: 技术面分析 =====
    print("🔍 [4/5] 技术面分析（调用 stock-robot 引擎）...")
    # 导入 stock-robot 的技术指标引擎
    tech_dir = SCRIPT_DIR
    if tech_dir not in sys.path:
        sys.path.insert(0, tech_dir)

    technical_result = {}

    try:
        # 获取每个标的的 K 线 + 技术指标
        stock_analyses = []
        for w in WATCHLIST:
            code = w["code"]
            name = w["name"]
            kline_data = get_kline(code, 120)

            if "error" in kline_data:
                stock_analyses.append({"code": code, "name": name, "error": kline_data["error"]})
                continue

            klines = kline_data.get("klines", [])
            if len(klines) < 20:
                stock_analyses.append({"code": code, "name": name, "error": f"K线不足({len(klines)})"})
                continue

            # 调用技术指标引擎 (importlib绕开连字符文件名)
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "technical_indicators",
                    os.path.join(SCRIPT_DIR, "technical-indicators.py")
                )
                ti = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ti)
                analysis = ti.full_technical_analysis(klines)
                summary = ti.full_technical_summary(klines)
                signals_data = analysis.get("signals", {})
                signal_score = signals_data.get("signal_score", 0)
                trend = signals_data.get("signal_strength", "中性")

                stock_analyses.append({
                    "code": code,
                    "name": name,
                    "analysis": {
                        "signals": {
                            "signal_score": signal_score,
                            "signal": trend,
                        },
                        "summary": summary,
                    },
                })
                trend_icon = "📈" if "涨" in str(trend) or "多" in str(trend) else ("📉" if "跌" in str(trend) or "空" in str(trend) else "➖")
                print(f"  {trend_icon} {name}({code}): 评分={signal_score:+.1f} | {trend}")

            except ImportError as e:
                stock_analyses.append({"code": code, "name": name, "error": f"技术指标模块导入失败: {e}"})
            except Exception as e:
                stock_analyses.append({"code": code, "name": name, "error": str(e)})

        # 市场总览
        total_up = sum(1 for s in stock_analyses if
                       s.get("analysis", {}).get("signals", {}).get("signal_score", 0) > 0)
        total_down = sum(1 for s in stock_analyses if
                         s.get("analysis", {}).get("signals", {}).get("signal_score", 0) < 0)

        if indices:
            avg_change = sum(i["change_pct"] for i in indices) / len(indices)
            market_trend = "上涨 📈" if avg_change > 0.5 else ("下跌 📉" if avg_change < -0.5 else "震荡 ➖")
        else:
            market_trend = "震荡"
            avg_change = 0

        technical_result = {
            "stock_analyses": stock_analyses,
            "market_overview": {
                "market_trend": market_trend,
                "avg_change_pct": round(avg_change, 2),
                "bullish_ratio": round(total_up / max(len(stock_analyses), 1), 2),
                "bearish_ratio": round(total_down / max(len(stock_analyses), 1), 2),
            },
        }
    except Exception as e:
        print(f"  ❌ 技术分析失败: {e}")
        technical_result = {"stock_analyses": [], "market_overview": {"market_trend": "未知"}}

    print()

    # ===== 步骤5: 融合决策 =====
    print("🔍 [5/5] 三引擎融合决策...")
    fusion = fusion_decision(technical_result, fundamental_results, sentiment)

    print(f"  📊 市场状态: {fusion['market_condition']}")
    print(f"  🎯 买入信号: {fusion['statistics']['buy_signals']} | 卖出: {fusion['statistics']['sell_signals']} | 观望: {fusion['statistics']['hold_signals']}")
    print(f"  ⚠️  风险等级: {fusion['market_risk_level']}")
    print()

    # ===== 决策评分卡（新增） =====
    print("📋 决策评分卡")
    # 收集kline_data用于价格区间计算
    kline_data = {}
    for w in WATCHLIST:
        kd = get_kline(w["code"], 30)
        if "error" not in kd:
            kline_data[w["code"]] = kd
    decision_cards = build_decision_card(
        technical_result.get("stock_analyses", []),
        fundamental_results,
        sentiment,
        kline_data
    )
    print(print_decision_cards(decision_cards))
    print()

    # ===== 输出最终建议 =====
    print("=" * 55)
    print("📋 最终融合建议")
    print("=" * 55)

    buy_signals = [s for s in fusion["fusion_signals"] if "买入" in s.get("action", "") or "推荐" in s.get("action", "")]
    sell_signals = [s for s in fusion["fusion_signals"] if "回避" in s.get("action", "") or "减仓" in s.get("action", "")]
    hold_signals = [s for s in fusion["fusion_signals"] if "观察" in s.get("action", "")]
    error_signals = [s for s in fusion["fusion_signals"] if "跳过" in s.get("action", "")]

    if buy_signals:
        print("\n🚀 买入信号:")
        for s in buy_signals:
            print(f"  {s['name']}({s['code']}): 综合{s['overall_score']:.0%} | {s['reason']}")

    if hold_signals:
        print("\n👀 观望:")
        for s in hold_signals[:3]:
            print(f"  {s['name']}({s['code']}): 综合{s['overall_score']:.0%} | {s['reason']}")

    if sell_signals:
        print("\n📕 卖出/回避信号:")
        for s in sell_signals:
            print(f"  {s['name']}({s['code']}): 综合{s['overall_score']:.0%} | {s['reason']}")

    print()
    print(f"💡 {sentiment['advice']}")
    print(f"🛡️ YOLO: {'安全模式 - 以上为建议，确认后执行' if yolo_mode else '自动模式 - 系统可自动执行'}")

    # 保存完整报告
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "type": "full",
        "yolo_mode": yolo_mode,
        "market_indices": indices,
        "market_overview": market_overview,
        "decision_cards": decision_cards,
        "sentiment": sentiment,
        "fundamentals": [f for f in fundamental_results if "error" not in f],
        "fusion": fusion,
        "generated_by": "顾比交易大脑",
    }
    save_report(report)

    return report


def run_scan():
    """快速扫描模式"""
    print("⚡ 顾比交易大脑 | 快速扫描")
    print("=" * 40)

    # 大盘概览
    indices = get_market_indices()
    if indices:
        print("📊 大盘：")
        for idx in indices:
            sign = "+" if idx["change_pct"] > 0 else ""
            print(f"  {idx['name']}: {idx['price']:.2f} ({sign}{idx['change_pct']:.2f}%)")

    # 情绪
    sentiment = assess_market_sentiment()
    print(f"\n📰 {sentiment['overall_sentiment']}")

    # 基本面速览
    print("\n📗 估值速览:")
    fund_results = batch_analysis(WATCHLIST)
    for f in sorted(fund_results, key=lambda x: x.get("fundamentals_score", 0), reverse=True)[:5]:
        if "error" not in f:
            print(f"  {f['name']}({f['code']}): PE={f['valuation']['pe']:.1f} | ROE={f['valuation']['roe']:.1f}% | 评分={f['fundamentals_score']:.1f}")

    # Cookie Jar 状态
    jar = get_cookie_jar_summary()
    if jar["position_count"] > 0:
        print(f"\n📦 持仓: {jar['position_count']}只 | YOLO: {'✅' if jar['yolo_mode'] else '⚠️'}")

    print()
    print(f"💡 {sentiment.get('advice', '')}")


def run_deep(code):
    """深度分析单一标的"""
    print(f"🔬 顾比交易大脑 | 深度分析: {code}")
    print("=" * 45)

    # 找到标的名称
    name = code
    for w in WATCHLIST:
        if w["code"] == code:
            name = w["name"]
            break

    # 1. 行情
    print("\n📈 实时行情:")
    quotes = get_quote([code])
    if quotes and quotes[0].get("current_price", 0) > 0:
        q = quotes[0]
        print(f"  {q.get('name', name)}({code}): {q['current_price']:.2f} | {q['change_pct']:+.2f}%")
        print(f"  高: {q['high']:.2f} | 低: {q['low']:.2f} | 换手: {q['turnover_rate']:.2f}%")
        print(f"  PE: {q['pe_ratio']:.2f} | 市值: {q['market_cap']:.2f}亿")

    # 2. 基本面
    print("\n📗 基本面分析:")
    from brain.fundamental_analysis import full_fundamental_analysis
    fund = full_fundamental_analysis(code, name)
    if "error" not in fund:
        v = fund["valuation"]
        print(f"  PE={v['pe']:.1f} | PB={v['pb']:.2f} | ROE={v['roe']:.1f}%")
        print(f"  股息率: {v['dividend_yield']:.2f}% | EPS: {v['eps']:.2f}")
        print(f"  52周区间: {v['52week_low']:.2f} ~ {v['52week_high']:.2f}")
        print(f"  基本面评分: {fund['fundamentals_score']:.1f} | {fund['fundamentals_signal']}")
        print("\n  各维度:")
        for dim, info in fund["scores"].items():
            if isinstance(info, dict):
                print(f"    {dim}: {info.get('score', '?')}分 - {info.get('note', '')}")
    else:
        print(f"  ❌ {fund.get('error', '获取失败')}")

    # 3. 技术面
    print("\n📐 技术面分析:")
    kline_data = get_kline(code, 120)
    if "error" not in kline_data:
        klines = kline_data.get("klines", [])
        print(f"  K线: {len(klines)}条")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "technical_indicators",
                os.path.join(SCRIPT_DIR, "technical-indicators.py")
            )
            ti = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ti)
            analysis = ti.full_technical_analysis(klines)
            print(f"\n  {ti.full_technical_summary(klines)}")
            signals = analysis.get("signals", {})
            print(f"  信号评分: {signals.get('signal_score', 'N/A')} | {signals.get('signal_strength', 'N/A')}")
        except Exception as e:
            print(f"  ❌ 技术分析失败: {e}")
    else:
        print(f"  ❌ {kline_data.get('error', 'K线获取失败')}")


def run_cron():
    """Cron模式 - 输出精简摘要"""
    os.makedirs(LOG_DIR, exist_ok=True)

    result = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    result.append(f"🧠 {timestamp}")

    # 大盘
    indices = get_market_indices()
    if indices:
        idx_strs = []
        for idx in indices[:3]:
            sign = "+" if idx["change_pct"] > 0 else ""
            idx_strs.append(f"{idx['name']}{sign}{idx['change_pct']:.2f}%")
        result.append(f"📊 {' '.join(idx_strs)}")

    # 情绪
    sentiment = assess_market_sentiment()
    result.append(f"📰 {sentiment['overall_sentiment']}")

    # 基本面+融合
    fund_results = batch_analysis(WATCHLIST)
    buy_count = sum(1 for f in fund_results if "error" not in f and f.get("fundamentals_score", 0) >= 6.5)
    sell_count = sum(1 for f in fund_results if "error" not in f and f.get("fundamentals_score", 0) < 4)
    result.append(f"📗 看多{buy_count} | 看空{sell_count}")

    # Cookie Jar
    jar = get_cookie_jar_summary()
    if jar["position_count"] > 0:
        result.append(f"📦 {jar['position_count']}只持仓")

    output = " | ".join(result)
    print(output)

    # 存档
    with open(os.path.join(LOG_DIR, "brain_daily.log"), "a", encoding="utf-8") as f:
        f.write(output + "\n")

    return output


def run_cockpit():
    """大脑仪表盘"""
    print("🧠 顾比交易大脑仪表盘")
    print("=" * 45)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # YOLO状态
    yolo = check_yolo()
    print(f"🛡️ YOLO模式: {'开启 ✅ (只建议不执行)' if yolo else '关闭 ⚠️ (自动执行)'}")

    # Cookie Jar
    jar = get_cookie_jar_summary()
    print(f"📦 Cookie Jar:")
    print(f"   持仓: {jar['position_count']}只")
    print(f"   观察: {jar['watchlist_count']}只")
    print(f"   建议记录: {jar['suggestion_count']}条")

    # 大盘
    indices = get_market_indices()
    if indices:
        print(f"\n📊 大盘:")
        for idx in indices[:5]:
            sign = "+" if idx["change_pct"] > 0 else ""
            print(f"   {idx['name']}: {idx['price']:.2f} ({sign}{idx['change_pct']:.2f}%)")

    # 系统信息
    from brain.config import WEIGHTS
    print(f"\n⚙️  系统信息:")
    print(f"   监控标的: {len(WATCHLIST)}只")
    print(f"   权重配置: 技术{WEIGHTS['technical']:.0%} 基本面{WEIGHTS['fundamental']:.0%} 情绪{WEIGHTS['sentiment']:.0%} 动量{WEIGHTS['momentum']:.0%}")
    print(f"   信号范围: A股 + ETF")
    print(f"   数据源: 腾讯行情(免费) | 东方财富(免费) | 新浪财经(免费)")


def save_report(report):
    """保存完整报告"""
    try:
        fname = f"brain_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        path = os.path.join(LOG_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    except:
        pass


# ===== 主入口 =====
if __name__ == "__main__":
    # 加载配置
    from brain.config import WEIGHTS

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "full":
        run_full_report()
    elif cmd == "scan":
        run_scan()
    elif cmd == "deep" and len(sys.argv) > 2:
        run_deep(sys.argv[2])
    elif cmd == "cron":
        run_cron()
    elif cmd == "cockpit":
        run_cockpit()
    else:
        print(f"未知命令: {cmd}")
        print("可用命令: full, scan, deep <code>, cron, cockpit")
