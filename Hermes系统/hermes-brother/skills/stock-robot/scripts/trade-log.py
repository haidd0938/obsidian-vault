#!/usr/bin/env python3
"""
模拟交易日志系统
功能：
1. 模拟买入/卖出操作
2. 自动计算收益率
3. 持仓管理
4. 交易历史查询
5. 绩效统计

文件存储：~/stock-robot/data/trade_log.json
"""

import sys
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TRADE_FILE = os.path.join(DATA_DIR, "trade_log.json")

# 默认资金（模拟盘）
INITIAL_CAPITAL = 10000.0  # 老板说1万起步，就先模拟1万


def load_data():
    """加载交易数据"""
    if os.path.exists(TRADE_FILE):
        with open(TRADE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "initial_capital": INITIAL_CAPITAL,
        "available_cash": INITIAL_CAPITAL,
        "positions": {},      # code -> {"shares": N, "avg_cost": X}
        "trades": [],          # 交易记录列表
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def save_data(data):
    """保存交易数据"""
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TRADE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def get_current_price(code):
    """从行情API获取当前价格"""
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, script_dir)
    import importlib.util
    spec = importlib.util.spec_from_file_location("sq", os.path.join(script_dir, "stock-quote.py"))
    sq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sq)
    return sq.fetch_real_time(code)


def cmd_buy(code, name, amount, price=None):
    """
    模拟买入
    code: 股票代码
    name: 股票名称
    amount: 买入金额（元）
    price: 买入价格（不指定则用市价）
    """
    data = load_data()
    
    # 获取价格
    if price is None:
        quote = get_current_price(code)
        if "error" in quote:
            return {"success": False, "error": f"获取价格失败: {quote['error']}"}
        price = quote["current_price"]
    
    shares = int(amount / price / 100) * 100  # 按手（100股）取整
    if shares <= 0:
        return {"success": False, "error": f"金额不足买入1手(100股)，当前价{price:.2f}元，至少需要{price*100:.2f}元"}
    
    cost = shares * price
    if cost > data["available_cash"]:
        return {"success": False, "error": f"余额不足！可用{data['available_cash']:.2f}元，需要{cost:.2f}元"}
    
    # 执行买入
    data["available_cash"] -= cost
    
    if code in data["positions"]:
        # 加仓：加权平均成本
        old_pos = data["positions"][code]
        total_shares = old_pos["shares"] + shares
        total_cost = old_pos["shares"] * old_pos["avg_cost"] + cost
        old_pos["shares"] = total_shares
        old_pos["avg_cost"] = round(total_cost / total_shares, 3)
    else:
        data["positions"][code] = {
            "name": name,
            "shares": shares,
            "avg_cost": price,
        }
    
    trade = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "BUY",
        "code": code,
        "name": name,
        "price": round(price, 2),
        "shares": shares,
        "amount": round(cost, 2),
        "available_cash_after": round(data["available_cash"], 2),
    }
    data["trades"].append(trade)
    save_data(data)
    
    return {
        "success": True,
        "action": "买入",
        "code": code,
        "name": name,
        "price": round(price, 2),
        "shares": shares,
        "amount": round(cost, 2),
        "remaining_cash": round(data["available_cash"], 2),
    }


def cmd_sell(code, shares_or_ratio="all", price=None):
    """
    模拟卖出
    code: 股票代码
    shares_or_ratio: 股数 或 "all"（全仓）或 "half"（半仓）
    price: 卖出价格（不指定则用市价）
    """
    data = load_data()
    
    if code not in data["positions"]:
        return {"success": False, "error": f"未持有{code}"}
    
    pos = data["positions"][code]
    
    # 计算卖出股数
    if shares_or_ratio == "all":
        sell_shares = pos["shares"]
    elif shares_or_ratio == "half":
        sell_shares = (pos["shares"] // 200) * 100  # 半仓取整到手
        if sell_shares <= 0:
            sell_shares = pos["shares"]
    else:
        sell_shares = int(shares_or_ratio)
    
    if sell_shares <= 0 or sell_shares > pos["shares"]:
        return {"success": False, "error": f"无效的卖出数量。持仓：{pos['shares']}股"}
    
    # 获取价格
    if price is None:
        quote = get_current_price(code)
        if "error" in quote:
            return {"success": False, "error": f"获取价格失败: {quote['error']}"}
        price = quote["current_price"]
    
    proceeds = sell_shares * price
    cost_basis = sell_shares * pos["avg_cost"]
    profit = proceeds - cost_basis
    profit_pct = (profit / cost_basis) * 100 if cost_basis > 0 else 0
    
    # 更新持仓
    data["available_cash"] += proceeds
    pos["shares"] -= sell_shares
    if pos["shares"] <= 0:
        del data["positions"][code]
    
    trade = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": "SELL",
        "code": code,
        "name": pos["name"],
        "price": round(price, 2),
        "shares": sell_shares,
        "amount": round(proceeds, 2),
        "profit": round(profit, 2),
        "profit_pct": round(profit_pct, 2),
        "available_cash_after": round(data["available_cash"], 2),
    }
    data["trades"].append(trade)
    save_data(data)
    
    return {
        "success": True,
        "action": "卖出",
        "code": code,
        "name": pos["name"],
        "price": round(price, 2),
        "shares": sell_shares,
        "amount": round(proceeds, 2),
        "profit": round(profit, 2),
        "profit_pct": round(profit_pct, 2),
        "remaining_cash": round(data["available_cash"], 2),
        "remaining_position": data["positions"].get(code, {}).get("shares", 0),
    }


def cmd_summary():
    """输出持仓和绩效摘要（JSON）"""
    data = load_data()
    
    total_pos_value = 0
    position_details = []
    
    for code, pos in data["positions"].items():
        quote = get_current_price(code)
        if "error" not in quote:
            current_price = quote["current_price"]
            market_value = pos["shares"] * current_price
            cost_total = pos["shares"] * pos["avg_cost"]
            profit = market_value - cost_total
            profit_pct = (profit / cost_total) * 100 if cost_total > 0 else 0
        else:
            current_price = pos["avg_cost"]
            market_value = pos["shares"] * current_price
            profit = 0
            profit_pct = 0
        
        total_pos_value += market_value
        position_details.append({
            "code": code,
            "name": pos["name"],
            "shares": pos["shares"],
            "avg_cost": round(pos["avg_cost"], 2),
            "current_price": round(current_price, 2),
            "market_value": round(market_value, 2),
            "profit": round(profit, 2),
            "profit_pct": round(profit_pct, 2),
        })
    
    total_assets = data["available_cash"] + total_pos_value
    total_return = ((total_assets - data["initial_capital"]) / data["initial_capital"]) * 100
    
    return {
        "initial_capital": data["initial_capital"],
        "available_cash": round(data["available_cash"], 2),
        "position_value": round(total_pos_value, 2),
        "total_assets": round(total_assets, 2),
        "total_return": round(total_return, 2),
        "total_profit": round(total_assets - data["initial_capital"], 2),
        "position_count": len(data["positions"]),
        "trade_count": len(data["trades"]),
        "positions": position_details,
        "last_trades": data["trades"][-5:] if data["trades"] else [],
    }


def cmd_history(code=None):
    """查询交易历史"""
    data = load_data()
    trades = data["trades"]
    if code:
        trades = [t for t in trades if t["code"] == code]
    return trades


def cmd_reset(initial_capital=None):
    """重置模拟盘"""
    cap = initial_capital if initial_capital else INITIAL_CAPITAL
    data = {
        "initial_capital": cap,
        "available_cash": cap,
        "positions": {},
        "trades": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    save_data(data)
    return {"success": True, "message": f"模拟盘已重置，初始资金{cap:.2f}元"}


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  买入: python3 trade-log.py buy <代码> [金额] [价格]")
        print("  卖出: python3 trade-log.py sell <代码> [数量/all/half] [价格]")
        print("  持仓: python3 trade-log.py summary")
        print("  历史: python3 trade-log.py history [代码]")
        print("  重置: python3 trade-log.py reset [初始资金]")
        print()
        print("示例:")
        print("  python3 trade-log.py buy 159840 2000        # 买入2000元锂电池ETF")
        print("  python3 trade-log.py buy 002594 5000 105.5 # 指定价格买入比亚迪")
        print("  python3 trade-log.py sell 159840 all       # 清仓锂电池ETF")
        print("  python3 trade-log.py sell 002594 half      # 半仓卖出比亚迪")
        print("  python3 trade-log.py summary               # 查看持仓")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "buy":
        if len(sys.argv) < 3:
            print("请指定代码")
            sys.exit(1)
        code = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else code
        amount = float(sys.argv[4]) if len(sys.argv) > 4 else 2000
        price = float(sys.argv[5]) if len(sys.argv) > 5 else None
        result = cmd_buy(code, name, amount, price)
        if result["success"]:
            print(f"✅ 买入成功: {result['name']}({result['code']}) {result['shares']}股 @ {result['price']}元")
            print(f"   成交额: {result['amount']:.2f}元 | 剩余资金: {result['remaining_cash']:.2f}元")
        else:
            print(f"❌ 买入失败: {result['error']}")
    
    elif cmd == "sell":
        if len(sys.argv) < 3:
            print("请指定代码")
            sys.exit(1)
        code = sys.argv[2]
        ratio = sys.argv[3] if len(sys.argv) > 3 else "all"
        price = float(sys.argv[4]) if len(sys.argv) > 4 else None
        result = cmd_sell(code, ratio, price)
        if result["success"]:
            profit_str = f"盈利{result['profit']:.2f}元({result['profit_pct']:.2f}%)" if result.get("profit", 0) > 0 else f"亏损{abs(result.get('profit', 0)):.2f}元({result.get('profit_pct', 0):.2f}%)"
            print(f"✅ 卖出成功: {result['name']}({result['code']}) {result['shares']}股 @ {result['price']}元")
            print(f"   成交额: {result['amount']:.2f}元 | 损益: {profit_str}")
            print(f"   剩余持仓: {result['remaining_position']}股 | 剩余资金: {result['remaining_cash']:.2f}元")
        else:
            print(f"❌ 卖出失败: {result['error']}")
    
    elif cmd in ("summary", "pos", "status", "--summary"):
        result = cmd_summary()
        print(f"📊 模拟盘概览")
        print(f"=" * 45)
        print(f"初始资金: {result['initial_capital']:.2f}元")
        print(f"总资产:   {result['total_assets']:.2f}元")
        print(f"可用资金: {result['available_cash']:.2f}元")
        print(f"持仓市值: {result['position_value']:.2f}元")
        print(f"总收益:   {'+' if result['total_return'] >= 0 else ''}{result['total_return']:.2f}%")
        print(f"交易次数: {result['trade_count']}笔 | 持仓 {result['position_count']}只")
        print()
        if result["positions"]:
            print("📋 当前持仓:")
            for p in result["positions"]:
                sign = "+" if p["profit_pct"] >= 0 else ""
                print(f"  {p['name']}({p['code']}): {p['shares']}股 | 均价{p['avg_cost']:.2f} | 现价{p['current_price']:.2f} | 市值{p['market_value']:.2f} | {sign}{p['profit_pct']:.2f}%")
        else:
            print("📋 当前持仓: 空仓")
    
    elif cmd == "history":
        code = sys.argv[2] if len(sys.argv) > 2 else None
        trades = cmd_history(code)
        print(f"📜 交易历史 ({len(trades)}笔)")
        print(f"=" * 60)
        for t in trades[-20:]:
            icon = "🟢买入" if t["action"] == "BUY" else "🔴卖出"
            profit_str = f" | {'+' if t.get('profit', 0) > 0 else ''}{t.get('profit_pct', 0):.2f}%" if t.get("profit") else ""
            print(f"  {t['time']} {icon} {t['name']}({t['code']}) {t['shares']}股 @ {t['price']:.2f}元 {profit_str}")
    
    elif cmd == "reset":
        cap = float(sys.argv[2]) if len(sys.argv) > 2 else 10000
        result = cmd_reset(cap)
        print(f"🔄 {result['message']}")
    
    elif cmd == "--json":
        # JSON模式输出（给复盘脚本用）
        result = cmd_summary()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
