#!/usr/bin/env python3
"""
🤖 独立股票机器人 — 主控调度器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
功能：
  1. 全量运行：大盘 + 热点 + 技术面 + 模拟盘 = 完整报告
  2. 快速扫描：仅关键标的概览
  3. 单一标的深度分析
  4. 模拟盘操作
  5. 定时任务助手（生成cron-ready报告）
  
用法：
  python3 orchestrator.py full        # 完整复盘（推荐）
  python3 orchestrator.py scan        # 快速扫描
  python3 orchestrator.py deep <code> # 深度分析某一只
  python3 orchestrator.py cron        # cron模式（只输出摘要到stdout）
  python3 orchestrator.py news        # 只看新闻热点
  python3 orchestrator.py status      # 模拟盘状况

数据目录：~/stock-robot/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os
import json
import subprocess
from datetime import datetime

ROBOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.join(ROBOT_DIR, "scripts")
DATA_DIR = os.path.join(ROBOT_DIR, "data")
LOG_DIR = os.path.join(ROBOT_DIR, "logs")


def run_script(script_name, args=None, json_output=True):
    """运行scripts目录下的脚本"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        return {"error": f"脚本不存在: {script_name}"}
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return {"error": f"执行失败: {result.stderr[:500]}"}
        if json_output and result.stdout.strip():
            return json.loads(result.stdout)
        return result.stdout
    except json.JSONDecodeError:
        return {"error": f"输出不是JSON", "raw": result.stdout[:500]}
    except subprocess.TimeoutExpired:
        return {"error": "执行超时"}
    except Exception as e:
        return {"error": str(e)}


def cmd_full():
    """完整复盘运行"""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("🤖 股票机器人 | 完整复盘模式")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # 1. 大盘
    print("🔍 [1/5] 获取大盘数据...")
    indices = run_script("stock-quote.py", ["sh000001", "sz399001", "sz399006", "sh000688"])
    
    # 2. 新闻热点
    print("🔍 [2/5] 检索市场热点...")
    news = run_script("market-news.py", [], json_output=False)
    
    # 3. 运行复盘
    print("🔍 [3/5] 全量技术分析...")
    report_result = run_script("daily-review.py", ["--no-save"], json_output=False)
    
    # 4. 模拟盘状态
    print("🔍 [4/5] 检查模拟盘...")
    trade_status = run_script("trade-log.py", ["--summary"])
    
    # 5. 生成统一输出
    print("🔍 [5/5] 生成最终报告...")
    
    # 输出报告
    if isinstance(report_result, str):
        print("\n" + report_result)
    else:
        print("❌ 报告生成失败")
    
    # 输出模拟盘摘要
    print()
    if isinstance(trade_status, dict) and "error" not in trade_status:
        print("## 📋 模拟盘状态")
        print(f"总资产: {trade_status['total_assets']:.2f}元 | 收益: {trade_status['total_return']:.2f}% | 持仓: {trade_status['position_count']}只")
        print()
    
    print("=" * 50)
    print("✅ 报告完成")


def cmd_scan():
    """快速扫描模式"""
    print("⚡ 快速扫描模式")
    print("=" * 30)
    
    # 大盘概览
    indices = run_script("stock-quote.py", ["sh000001", "sz399001", "sz399006"])
    if isinstance(indices, list):
        print("\n📊 大盘：")
        for idx in indices:
            if "error" not in idx:
                sign = "+" if idx["change_pct"] > 0 else ""
                print(f"  {idx['name']}: {idx['current_price']:.2f} ({sign}{idx['change_pct']:.2f}%)")
    
    # 新闻热点摘要
    news_out = run_script("market-news.py", ["--simple"], json_output=False)
    if isinstance(news_out, str):
        print(f"\n{news_out}")
    
    # 模拟盘状态
    trade = run_script("trade-log.py", ["--summary"])
    if isinstance(trade, dict) and "error" not in trade:
        print(f"\n💰 模拟盘: {trade['total_assets']:.0f}元 ({trade['total_return']:+.2f}%) | {trade['position_count']}只持仓")


def cmd_deep(code):
    """深度分析单一标的"""
    print(f"🔬 深度分析: {code}")
    print("=" * 40)
    
    # 获取实时行情
    quote = run_script("stock-quote.py", [code])
    if isinstance(quote, list) and len(quote) > 0:
        q = quote[0]
        if "error" not in q:
            print(f"\n📈 {q['name']}({q['code']})")
            print(f"现价: {q['current_price']:.2f}元 | 涨跌: {q['change_pct']:+.2f}%")
            print(f"最高: {q['high']:.2f} | 最低: {q['low']:.2f} | 振幅: {q['amplitude']:.2f}%")
            print(f"成交额: {q['amount']/100000000:.2f}亿 | 换手: {q.get('volume', 0)/10000:.2f}万手")
            if q.get('pe_ratio', 0) > 0:
                print(f"市盈率: {q['pe_ratio']:.2f} | 市值: {q['market_cap']:.2f}亿")
    
    # 技术面分析
    kline = run_script("stock-quote.py", ["--kline", code, "120"])
    if isinstance(kline, list):
        kline = kline[0]
    klines = kline.get("klines", []) if isinstance(kline, dict) else []
    
    if klines and len(klines) >= 30:
        # 导入技术指标引擎
        sys.path.insert(0, SCRIPT_DIR)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "tech", os.path.join(SCRIPT_DIR, "technical-indicators.py")
        )
        tech = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tech)
        
        print("\n📐 技术面分析：")
        print(tech.full_technical_summary(klines))
    else:
        print(f"\n❌ K线数据不足({len(klines)}条，至少需要30条)")


def cmd_cron():
    """Cron模式 - 输出精简摘要用于定时任务"""
    # 大盘
    indices = run_script("stock-quote.py", ["sh000001", "sz399001", "sz399006"])
    
    # 模拟盘
    trade = run_script("trade-log.py", ["--summary"])
    
    # 构建一行摘要
    parts = [f"[{datetime.now().strftime('%m/%d %H:%M')}]"]
    
    if isinstance(indices, list):
        idx_strs = []
        for idx in indices:
            if "error" not in idx:
                s = "+" if idx["change_pct"] > 0 else ""
                short_name = idx["name"].replace("上证指数", "上证").replace("深证成指", "深证").replace("创业板指", "创业板")
                idx_strs.append(f"{short_name}{s}{idx['change_pct']:.2f}%")
        parts.append("大盘:" + " ".join(idx_strs))
    
    if isinstance(trade, dict) and "error" not in trade:
        parts.append(f"模拟盘:{trade['total_return']:+.2f}%")
    
    print(" | ".join(parts))
    
    # 也保存到日志
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "daily_summary.log"), "a", encoding="utf-8") as f:
        f.write(" | ".join(parts) + "\n")


def cmd_news():
    """只看热点新闻"""
    from market_news import get_market_focus
    result = get_market_focus()
    print(f"📰 市场热点（{result['timestamp']}）")
    print("=" * 50)
    for i, news in enumerate(result["hot_news"][:5], 1):
        print(f"{i}. {news['title']}")
    print()
    if result["hot_sectors"]:
        print("🏷️ 热门板块：")
        top_sectors = sorted(result["hot_sectors"], key=lambda x: abs(x.get("change_pct", 0)), reverse=True)[:5]
        for s in top_sectors:
            sign = "+" if s["change_pct"] > 0 else ""
            print(f"   {s['name']}: {sign}{s['change_pct']:.2f}%")
    print()
    print(f"💡 {result['suggested_focus']}")


def cmd_status():
    """模拟盘状态"""
    result = run_script("trade-log.py", ["--summary"])
    if isinstance(result, dict) and "error" not in result:
        print("📊 模拟盘概览")
        print("=" * 45)
        print(f"初始资金: {result['initial_capital']:.2f}元")
        print(f"总资产:   {result['total_assets']:.2f}元")
        print(f"可用资金: {result['available_cash']:.2f}元")
        print(f"持仓市值: {result['position_value']:.2f}元")
        print(f"总收益:   {'+' if result['total_return'] >= 0 else ''}{result['total_return']:.2f}%")
        print(f"总盈亏:   {'+' if result['total_profit'] >= 0 else ''}{result['total_profit']:.2f}元")
        print(f"交易次数: {result['trade_count']}笔 | 持仓 {result['position_count']}只")
        print()
        if result["positions"]:
            print("📋 持仓明细:")
            for p in result["positions"]:
                sign = "+" if p["profit_pct"] >= 0 else ""
                print(f"  {p['name']}({p['code']}): {p['shares']}股 | 均价{p['avg_cost']:.2f} | 现价{p['current_price']:.2f} | {sign}{p['profit_pct']:.2f}%")
        else:
            print("📋 空仓")
    else:
        print("❌ 获取模拟盘数据失败")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "full":
        cmd_full()
    elif cmd == "scan":
        cmd_scan()
    elif cmd == "deep" and len(sys.argv) > 2:
        cmd_deep(sys.argv[2])
    elif cmd == "cron":
        cmd_cron()
    elif cmd == "news":
        cmd_news()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"未知命令: {cmd}")
        print("可用命令: full, scan, deep <code>, cron, news, status")
