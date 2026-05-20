#!/usr/bin/env python3
"""
顾比交易大脑 — 每日模拟盘操作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

适配 paper_account.py 的函数式API（无PaperAccount类）

用法：
  python3 brain/paper_trader.py daily    # 每日模拟交易
  python3 brain/paper_trader.py report   # 生成美观日报
"""
import sys
import os
import json
from datetime import datetime

BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(BRAIN_DIR)
SCRIPT_DIR = os.path.join(ROBOT_DIR, "scripts")
sys.path.insert(0, ROBOT_DIR)
sys.path.insert(0, BRAIN_DIR)

from brain.config import WATCHLIST
from brain.data_layer import get_kline, get_quote
import brain.paper_account as pa
import importlib.util


def load_technical():
    spec = importlib.util.spec_from_file_location("ti", os.path.join(SCRIPT_DIR, "technical-indicators.py"))
    ti = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ti)
    return ti


def get_account_view():
    """获取当前账户的展示层数据"""
    acc = pa.load_account()
    cash = acc["cash"]
    holdings = acc["holdings"]
    
    # 计算持仓市值
    total_market_value = 0
    positions_view = []
    for code, h in holdings.items():
        quote = get_quote([code])
        current_price = quote[0].get("current_price", 0) if quote else 0
        if current_price == 0:
            current_price = h["avg_cost"]
        market_value = h["shares"] * current_price
        pnl = market_value - (h["shares"] * h["avg_cost"])
        pnl_pct = round((current_price - h["avg_cost"]) / h["avg_cost"] * 100, 2) if h["avg_cost"] > 0 else 0
        total_market_value += market_value
        positions_view.append({
            "code": code,
            "name": h.get("name", code),
            "shares": h["shares"],
            "avg_cost": h["avg_cost"],
            "current_price": current_price,
            "market_value": round(market_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": pnl_pct,
        })
    
    total_asset = cash + total_market_value
    total_pnl = total_asset - pa.INITIAL_CAPITAL
    total_pnl_pct = round(total_pnl / pa.INITIAL_CAPITAL * 100, 2)
    
    return {
        "total_asset": round(total_asset, 2),
        "cash": round(cash, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": total_pnl_pct,
        "positions": positions_view,
        "trade_count": len(acc["orders"]),
        "total_commission": round(acc["total_fees_paid"], 2),
    }


def daily_trade():
    """每日模拟交易主流程"""
    account_view = get_account_view()
    
    print(f"📊 顾比交易大脑 — 每日模拟交易")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    sym = "+" if account_view["total_pnl"] >= 0 else ""
    print(f"💰 总资产: ¥{account_view['total_asset']:,.2f} | 现金: ¥{account_view['cash']:,.2f}")
    print(f"📈 盈亏: ¥{account_view['total_pnl']:+,.2f} ({sym}{account_view['total_pnl_pct']}%)")
    print(f"📦 持仓: {len(account_view['positions'])}只")
    print("=" * 50)
    
    # 分析所有标的
    ti = load_technical()
    signals = []
    
    for w in WATCHLIST:
        code = w["code"]
        name = w["name"]
        
        data = get_kline(code, 60)
        klines = data.get("klines", [])
        if len(klines) < 40:
            continue
        
        try:
            analysis = ti.full_technical_analysis(klines)
            sig = analysis.get("signals", {})
            score = sig.get("signal_score", 0)
            strength = sig.get("signal_strength", "中性")
            
            closes = [k.get("close", 0) for k in klines]
            ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else 0
            price = klines[-1].get("close", 0)
            v20_avg = sum(closes[-20:]) / 20 if len(closes) >= 20 else 0
            
            if score >= 2 and price > ma20:
                action = "买入"
            elif score <= -2 and price < ma20:
                action = "卖出"
            elif score >= 1:
                action = "关注"
            elif score <= -1:
                action = "回避"
            else:
                action = "观望"
            
            signals.append({
                "code": code, "name": name, "price": price,
                "score": score, "strength": strength, "ma20": ma20,
                "diff_ma20": round((price - ma20) / ma20 * 100, 1),
                "action": action,
            })
        except Exception as e:
            print(f"  ❌ {name}({code}): {e}")
    
    buy_sigs = [s for s in signals if s["action"] == "买入"]
    sell_sigs = [s for s in signals if s["action"] == "卖出"]
    
    print(f"\n🔵 买入信号: {len(buy_sigs)}只")
    print(f"🔴 卖出信号: {len(sell_sigs)}只")
    print(f"🟡 关注/观望: {len(signals) - len(buy_sigs) - len(sell_sigs)}只")
    
    # 执行卖出
    held_codes = set(pa.load_account()["holdings"].keys())
    for s in sell_sigs:
        if s["code"] in held_codes:
            acc = pa.load_account()
            h = acc["holdings"][s["code"]]
            result = pa.sell_stock(s["code"], h["shares"], price=s["price"])
            if result.get("success"):
                pnl = result.get("pnl", 0)
                sym = "✅" if pnl >= 0 else "🔴"
                print(f"  {sym} 卖出 {s['name']}({s['code']}): {h['shares']}股 @ {s['price']:.2f} | 盈亏¥{pnl:+,.2f}")
            else:
                print(f"  ❌ 卖出 {s['name']}({s['code']})失败: {result.get('error', '?')}")
        else:
            print(f"  ⏭️  {s['name']}({s['code']}): 信号卖出但未持仓")
    
    # 执行买入（按score排序）
    buy_sigs.sort(key=lambda x: x["score"], reverse=True)
    acc_data = pa.load_account()
    cash = acc_data["cash"]
    
    for s in buy_sigs:
        if cash < 500:
            print(f"  ⏭️  现金不足¥{cash:.0f}, 停止买入")
            break
        
        # 最大单只30%仓位
        total = cash + sum(
            h["shares"] * h["avg_cost"]
            for h in acc_data["holdings"].values()
        )
        max_position = total * 0.30
        
        available = min(cash, max_position)
        if available < 500:
            continue
        
        shares = int(available / s["price"] / 100) * 100
        if shares < 100:
            continue
        
        cost = shares * s["price"]
        if cost <= cash:
            result = pa.buy_stock(s["code"], shares, name=s["name"], price=s["price"])
            if result.get("success"):
                cash -= cost
                print(f"  🟢 买入 {s['name']}({s['code']}): {shares}股 @ {s['price']:.2f} = ¥{cost:,.0f}")
    
    # 展示持仓
    account_view = get_account_view()
    print(f"\n📦 当前持仓 ({len(account_view['positions'])}只):")
    if account_view["positions"]:
        for p in account_view["positions"]:
            match = [s for s in signals if s["code"] == p["code"]]
            sig_str = match[0]["strength"] if match else "?"
            sym = "🟢" if p["pnl"] >= 0 else "🔴"
            print(f"  {sym} {p['name']}({p['code']}): {p['shares']}股 | "
                  f"成本{p['avg_cost']:.2f}→现价{p['current_price']:.2f} | "
                  f"盈亏¥{p['pnl']:+,.0f}({p['pnl_pct']:+.1f}%) | 信号:{sig_str}")
    else:
        print(f"  (空仓)")
    
    # 保存日报
    report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "account": account_view,
        "buy_signals": [{"code": s["code"], "name": s["name"], "price": s["price"],
                         "score": s["score"], "strength": s["strength"]} for s in buy_sigs],
        "sell_signals": [{"code": s["code"], "name": s["name"], "price": s["price"],
                          "score": s["score"], "strength": s["strength"]} for s in sell_sigs],
    }
    report_dir = os.path.join(os.path.dirname(pa.ACCOUNT_PATH), "daily_reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"{datetime.now().strftime('%Y%m%d')}.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 日报已保存: {report_file}")
    return report


def generate_report():
    """生成美观的日报文本"""
    report_dir = os.path.join(os.path.dirname(pa.ACCOUNT_PATH), "daily_reports")
    today_file = os.path.join(report_dir, f"{datetime.now().strftime('%Y%m%d')}.json")
    
    if os.path.exists(today_file):
        with open(today_file, "r") as f:
            report = json.load(f)
    else:
        report = None
    
    acc = get_account_view()
    
    lines = []
    lines.append("=" * 50)
    lines.append(f"💰 顾比交易大脑 | 模拟盘日报")
    lines.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 50)
    lines.append("")
    
    sym = "+" if acc["total_pnl"] >= 0 else ""
    lines.append(f"📊 账户总资产: ¥{acc['total_asset']:,.2f}")
    lines.append(f"    现金余额: ¥{acc['cash']:,.2f}")
    lines.append(f"    累计盈亏: ¥{acc['total_pnl']:+,.2f} ({sym}{acc['total_pnl_pct']}%)")
    lines.append(f"    交易次数: {acc['trade_count']} | 手续费: ¥{acc['total_commission']:.2f}")
    lines.append("")
    
    lines.append(f"📦 持仓 ({len(acc['positions'])}只)")
    if acc["positions"]:
        lines.append(f"{'代码':<10} {'名称':<12} {'数量':>6} {'成本':>8} {'现价':>8} {'盈亏':>10} {'占比':>6}")
        lines.append("-" * 60)
        for p in acc["positions"]:
            total_pos_cost = p["shares"] * p["avg_cost"]
            weight = total_pos_cost / acc["total_asset"] * 100 if acc["total_asset"] > 0 else 0
            p_sym = "+" if p["pnl"] >= 0 else ""
            lines.append(f"{p['code']:<10} {p['name']:<12} {p['shares']:>6} "
                         f"{p['avg_cost']:>8.2f} {p['current_price']:>8.2f} "
                         f"{p_sym}¥{p['pnl']:>+8.0f} {weight:>5.1f}%")
    else:
        lines.append("  (空仓)")
    lines.append("")
    
    if report:
        lines.append("🔵 买入信号")
        for s in report.get("buy_signals", []):
            lines.append(f"  + {s['name']}({s['code']}) 评分{s['score']:+.0f} {s['strength']} @ {s['price']:.2f}")
        
        lines.append("\n🔴 卖出信号")
        for s in report.get("sell_signals", []):
            lines.append(f"  - {s['name']}({s['code']}) 评分{s['score']:+.0f} {s['strength']} @ {s['price']:.2f}")
        lines.append("")
    
    lines.append("=" * 50)
    lines.append("💡 操作建议:")
    if report and report.get("sell_signals"):
        lines.append("  卖出: " + ", ".join(s["name"] for s in report["sell_signals"][:3]))
    if report and report.get("buy_signals"):
        lines.append("  买入: " + ", ".join(s["name"] for s in report["buy_signals"][:3]))
    if (not report or (not report.get("buy_signals") and not report.get("sell_signals"))):
        lines.append("  当前无强信号，建议观望")
    
    result = "\n".join(lines)
    print(result)
    
    # 也保存成文本
    report_path = os.path.join(os.path.dirname(pa.ACCOUNT_PATH), "daily_reports", f"daily_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 brain/paper_trader.py {daily|report}")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "daily":
        daily_trade()
    elif cmd == "report":
        generate_report()
    else:
        print(f"未知命令: {cmd}")
