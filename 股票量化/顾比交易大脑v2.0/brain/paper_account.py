#!/usr/bin/env python3
"""
顾比交易大脑 — 模拟资金账户系统（Paper Account）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

虚拟本金 10,000 元，记录每笔模拟买卖，自动算收益率、持仓盈亏。

核心功能：
  - 初始化账户（虚拟10,000元）
  - 模拟买入：记录买入价、数量、手续费（万2.5）
  - 模拟卖出：记录卖出价、损益、剩余仓位
  - 自动更新：每笔交易后自动计算收益率、持仓市值
  - YOLO 联动：同步顾比大脑建议 → 你确认 → 执行模拟交易

用法：
  python3 brain/paper_account.py status           # 查看账户状态
  python3 brain/paper_account.py buy <code> <股数> # 模拟买入
  python3 brain/paper_account.py sell <code> <股数> # 模拟卖出
  python3 brain/paper_account.py reset            # 重置账户
  python3 brain/paper_account.py pnl              # 损益报表
"""
import sys
import os
import json
from datetime import datetime

BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BRAIN_DIR))

from brain.cookie_jar import load_jar, save_jar
from brain.data_layer import get_quote

COMMISSION_RATE = 0.00025  # 万2.5手续费
MIN_COMMISSION = 5.0       # 最低手续费5元
STAMP_TAX = 0.001          # 印花税千分之一（卖出时）
ACCOUNT_PATH = os.path.join(os.path.dirname(BRAIN_DIR), "data", "paper_account.json")
INITIAL_CAPITAL = 10000.0

def load_account():
    """加载模拟账户"""
    if os.path.exists(ACCOUNT_PATH):
        with open(ACCOUNT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return _create_account()

def _create_account():
    """创建新的模拟账户"""
    account = {
        "initial_capital": INITIAL_CAPITAL,
        "cash": INITIAL_CAPITAL,
        "holdings": {},       # code -> {name, shares, avg_cost, buy_date, current_value}
        "orders": [],         # [order, ...] 交易记录
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_fees_paid": 0.0,
        "peak_capital": INITIAL_CAPITAL,
    }
    _save_account(account)
    return account

def _save_account(account):
    """保存模拟账户"""
    account["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(ACCOUNT_PATH), exist_ok=True)
    with open(ACCOUNT_PATH, "w", encoding="utf-8") as f:
        json.dump(account, f, ensure_ascii=False, indent=2)

def calc_commission(amount):
    """计算手续费（最低5元）"""
    fee = max(amount * COMMISSION_RATE, MIN_COMMISSION)
    return round(fee, 2)

def get_current_price(code):
    """获取当前价格"""
    quotes = get_quote([code])
    if quotes and len(quotes) > 0:
        return quotes[0].get("current_price", 0)
    return 0

def buy_stock(code, shares, name=None, price=None):
    """模拟买入"""
    account = load_account()

    if code in account["holdings"]:
        return {"success": False, "error": f"已在持仓中: {code}。请直接覆盖买入或作为加仓操作。若加仓，修改shares为总股数后使用--force"}

    # 获取价格
    if price is None:
        price = get_current_price(code)
    if price <= 0:
        return {"success": False, "error": f"无法获取 {code} 行情"}

    total_cost = price * shares
    commission = calc_commission(total_cost)
    total_needed = total_cost + commission

    if total_needed > account["cash"]:
        return {
            "success": False,
            "error": f"现金不足！需 {total_needed:.2f} 元，可用 {account['cash']:.2f} 元",
        }

    # 仓位限制：单只不超过30%总资产
    holding_name = name or f"未知({code})"
    max_position = account["initial_capital"] * 0.3
    if total_cost > max_position:
        return {
            "success": False,
            "error": f"仓位超限！单只最多 {max_position:.0f} 元（30%）",
        }

    # 执行买入
    account["cash"] -= total_needed
    account["holdings"][code] = {
        "name": holding_name,
        "shares": shares,
        "avg_cost": price,
        "total_cost": round(total_cost, 2),
        "buy_date": datetime.now().strftime("%Y-%m-%d"),
        "commission": commission,
    }
    account["total_fees_paid"] += commission

    order = {
        "type": "BUY",
        "code": code,
        "name": holding_name,
        "shares": shares,
        "price": price,
        "total": round(total_cost, 2),
        "commission": commission,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    account["orders"].append(order)

    # 更新峰值
    total_asset = account["cash"] + total_cost
    if total_asset > account["peak_capital"]:
        account["peak_capital"] = total_asset

    _save_account(account)

    return {
        "success": True,
        "message": f"✅ 模拟买入成功：{holding_name}({code}) {shares}股 @ {price:.2f} (手续费{commission:.2f})",
        "order": order,
        "cash_remaining": round(account["cash"], 2),
    }

def sell_stock(code, shares=None, price=None):
    """模拟卖出"""
    account = load_account()

    if code not in account["holdings"]:
        return {"success": False, "error": f"持仓中无 {code}"}

    holding = account["holdings"][code]
    sell_shares = shares if shares is not None else holding["shares"]
    if sell_shares > holding["shares"]:
        return {"success": False, "error": f"可卖股数不足！持仓 {holding['shares']}，试图卖 {sell_shares}"}

    # 获取价格
    if price is None:
        price = get_current_price(code)
    if price <= 0:
        return {"success": False, "error": f"无法获取 {code} 行情"}

    sell_value = price * sell_shares
    commission = calc_commission(sell_value)
    stamp_tax = sell_value * STAMP_TAX
    total_fee = round(commission + stamp_tax, 2)
    net_income = sell_value - total_fee

    # 计算损益
    cost_per_share = holding["avg_cost"]
    cost_of_sold = cost_per_share * sell_shares
    pnl = round(sell_value - cost_of_sold - total_fee, 2)
    pnl_pct = round((pnl / cost_of_sold) * 100, 2) if cost_of_sold > 0 else 0

    # 执行卖出
    account["cash"] += net_income
    account["total_fees_paid"] += total_fee

    if sell_shares >= holding["shares"]:
        del account["holdings"][code]
    else:
        holding["shares"] -= sell_shares
        holding["total_cost"] = round(holding["shares"] * cost_per_share, 2)

    order = {
        "type": "SELL",
        "code": code,
        "name": holding["name"],
        "shares": sell_shares,
        "price": price,
        "total": round(sell_value, 2),
        "commission": round(commission + stamp_tax, 2),
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    account["orders"].append(order)

    _save_account(account)

    return {
        "success": True,
        "message": f"✅ 模拟卖出成功：{holding['name']}({code}) {sell_shares}股 @ {price:.2f} (盈亏: {pnl_pct}%)",
        "order": order,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "cash_remaining": round(account["cash"], 2),
    }

def get_status():
    """获取账户状态报告"""
    account = load_account()
    cash = account["cash"]
    holdings = account["holdings"]
    orders = account["orders"]

    # 计算持仓市值
    total_market_value = 0
    holdings_detail = []
    for code, h in holdings.items():
        price = get_current_price(code)
        market_value = price * h["shares"]
        cost_value = h["avg_cost"] * h["shares"]
        pnl = market_value - cost_value
        pnl_pct = round((pnl / cost_value) * 100, 2) if cost_value > 0 else 0
        total_market_value += market_value
        holdings_detail.append({
            "code": code,
            "name": h["name"],
            "shares": h["shares"],
            "avg_cost": h["avg_cost"],
            "current_price": price,
            "market_value": round(market_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": pnl_pct,
        })

    total_asset = cash + total_market_value
    total_pnl = total_asset - account["initial_capital"]
    total_pnl_pct = round((total_pnl / account["initial_capital"]) * 100, 2)
    peak = account.get("peak_capital", account["initial_capital"])
    drawdown = round((1 - total_asset / peak) * 100, 2) if peak > 0 else 0

    # 已实现盈亏
    realized_pnl = sum(
        o.get("pnl", 0) for o in orders if o["type"] == "SELL"
    )

    return {
        "initial_capital": account["initial_capital"],
        "cash": round(cash, 2),
        "total_asset": round(total_asset, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": total_pnl_pct,
        "realized_pnl": round(realized_pnl, 2),
        "peak_capital": round(peak, 2),
        "drawdown": drawdown,
        "position_count": len(holdings),
        "holdings": holdings_detail,
        "total_orders": len(orders),
        "total_fees": round(account["total_fees_paid"], 2),
    }

def get_pnl_report():
    """生成损益报告"""
    account = load_account()
    status = get_status()

    lines = []
    lines.append("📊 顾比模拟账户 — 损益报表")
    lines.append("=" * 45)
    lines.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append(f"💰 初始本金:    ¥{status['initial_capital']:,.2f}")
    lines.append(f"📦 总资产:      ¥{status['total_asset']:,.2f}")
    lines.append(f"💵 现金余额:    ¥{status['cash']:,.2f}")
    lines.append(f"📈 持仓市值:    ¥{sum(h['market_value'] for h in status['holdings']):,.2f}")
    lines.append("")
    # 盈亏
    pnl = status["total_pnl"]
    pnl_str = f"+¥{pnl:,.2f}" if pnl >= 0 else f"-¥{abs(pnl):,.2f}"
    pct_str = f"+{status['total_pnl_pct']}%" if status['total_pnl_pct'] >= 0 else f"{status['total_pnl_pct']}%"
    lines.append(f"📊 总盈亏:      {pnl_str} ({pct_str})")
    lines.append(f"📊 已实现盈亏:  ¥{status['realized_pnl']:+,.2f}")
    lines.append(f"📊 回撤(DD):    {status['drawdown']}%")
    lines.append(f"📊 手续费总计:  ¥{status['total_fees']:,.2f}")
    lines.append("")

    # 持仓明细
    if status["holdings"]:
        lines.append("📦 当前持仓:")
        for h in status["holdings"]:
            pnl_sym = "📈" if h["pnl"] >= 0 else "📉"
            lines.append(f"  {h['name']}({h['code']}): {h['shares']}股 | "
                        f"成本{h['avg_cost']:.2f} → 现价{h['current_price']:.2f} | "
                        f"{pnl_sym} {h['pnl_pct']}%")
        lines.append("")
    else:
        lines.append("📦 当前持仓: 空仓")
        lines.append("")

    # 交易记录
    if account["orders"]:
        lines.append(f"📝 最近交易 ({min(5, len(account['orders']))}条):")
        for o in account["orders"][-5:]:
            sym = "🟢买入" if o["type"] == "BUY" else "🔴卖出"
            pnl_info = f" | 盈亏{o['pnl']:+.2f}" if o.get("pnl") else ""
            lines.append(f"  {sym} {o['name']}({o['code']}) {o['shares']}股 @ {o['price']:.2f}{pnl_info}")
        lines.append("")

    lines.append(f"⚡ 已同步: 顾比交易大脑融合信号 + YOLO安全模式")
    lines.append(f"💡 下一笔模拟操作？用 paper_account.py buy/sell")

    return "\n".join(lines)

def reset():
    """重置模拟账户"""
    account = _create_account()
    return {"success": True, "message": "🔄 模拟账户已重置，初始本金 ¥10,000"}


# ===== 从顾比大脑融合信号一键执行模拟买入 =====
def execute_from_signal(code, signal_result, force=False):
    """
    根据顾比大脑的融合信号，一键执行模拟买入。
    signal_result: fusion_decision 输出的一个标的决策字典
    force: 跳过确认（用于快速测试）
    
    建议仓位比例 = 综合得分 × 30% （单只不超过30%）
    """
    account = load_account()
    cash = account["cash"]
    score = signal_result.get("overall_score", 0)
    
    if score < 0.6 and not force:
        return {"success": False, "error": f"综合评分{score:.0%}过低(需≥60%)，暂不建议建仓"}
    
    # 建议仓位
    suggested_pct = min(score * 0.3, 0.3)  # 最大30%
    suggested_amount = cash * suggested_pct
    # 不超过单只上限
    max_single = account["initial_capital"] * 0.3
    suggested_amount = min(suggested_amount, max_single)
    
    # 按价格算股数（取整百）
    price = get_current_price(signal_result.get("code", ""))
    if price <= 0:
        return {"success": False, "error": "无法获取行情"}
    
    shares = int(suggested_amount / price / 100) * 100
    if shares < 100:
        return {"success": False, "error": f"资金不足买100股（需¥{price*100:.0f}）"}
    
    return buy_stock(
        code=signal_result["code"],
        shares=shares,
        name=signal_result.get("name", ""),
        price=price,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        s = get_status()
        print(f"💰 总资产: ¥{s['total_asset']:,.2f} | 现金: ¥{s['cash']:,.2f}")
        pnl_str = f"+{s['total_pnl_pct']}%" if s['total_pnl_pct'] >= 0 else f"{s['total_pnl_pct']}%"
        print(f"📊 总盈亏: ¥{s['total_pnl']:+,.2f} ({pnl_str}) | 回撤: {s['drawdown']}%")
        if s['holdings']:
            print(f"\n📦 持仓 ({s['position_count']}只):")
            for h in s['holdings']:
                sym = "📈" if h["pnl"] >= 0 else "📉"
                print(f"  {h['name']}({h['code']}): {h['shares']}股 | {sym} {h['pnl_pct']}%")
        else:
            print("\n📦 空仓")
        print(f"\n📝 交易次数: {s['total_orders']} | 手续费: ¥{s['total_fees']:,.2f}")

    elif cmd == "buy" and len(sys.argv) >= 4:
        code = sys.argv[2]
        shares = int(sys.argv[3])
        name = sys.argv[4] if len(sys.argv) > 4 else None
        result = buy_stock(code, shares, name)
        print(result.get("message", result.get("error", "")))

    elif cmd == "sell" and len(sys.argv) >= 3:
        code = sys.argv[2]
        shares = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
        result = sell_stock(code, shares)
        print(result.get("message", result.get("error", "")))

    elif cmd == "reset":
        r = reset()
        print(r["message"])

    elif cmd == "pnl":
        print(get_pnl_report())

    elif cmd == "status_full":
        print(get_pnl_report())

    else:
        print("用法:")
        print("  python3 brain/paper_account.py status             # 快捷状态")
        print("  python3 brain/paper_account.py pnl                # 完整损益报表")
        print("  python3 brain/paper_account.py buy <code> <股数> [名称]  # 模拟买入")
        print("  python3 brain/paper_account.py sell <code> [股数]       # 模拟卖出")
        print("  python3 brain/paper_account.py reset              # 重置")
