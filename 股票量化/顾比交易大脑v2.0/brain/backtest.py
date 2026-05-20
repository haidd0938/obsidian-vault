#!/usr/bin/env python3
"""
顾比交易大脑 — 历史回测引擎（Backtest Engine）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

用过去3-6个月的历史数据，模拟顾比大脑信号：
  - 验证技术指标信号的胜率
  - 测试买入/卖出信号的准确性
  - 评估三引擎融合策略的历史表现

策略规则：
  买入信号: 技术评分 > 0 + 价格在20日均线上方 → 买入
  卖出信号: 技术评分 < 0 + 价格在20日均线下方 → 卖出
  持仓等待: 技术评分 > -1 → 持有
  空仓等待: 技术评分 ≤ -1 → 空仓

用法：
  python3 brain/backtest.py <code>           # 回测单只标的
  python3 brain/backtest.py <code> --full    # 完整回测（含图表数据）
  python3 brain/backtest.py batch            # 批量回测整个监控池
  python3 brain/backtest.py report           # 生成批量回测报告
"""
import sys
import os
import json
import importlib.util
from datetime import datetime, timedelta

BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(BRAIN_DIR)
SCRIPT_DIR = os.path.join(ROBOT_DIR, "scripts")
sys.path.insert(0, ROBOT_DIR)
sys.path.insert(0, BRAIN_DIR)

from brain.config import WATCHLIST
from brain.data_layer import get_kline

# ========== 技术指标引擎加载 ==========

def load_technical_engine():
    """延迟加载技术指标引擎（importlib绕过连字符文件名）"""
    spec = importlib.util.spec_from_file_location(
        "technical_indicators",
        os.path.join(SCRIPT_DIR, "technical-indicators.py")
    )
    ti = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ti)
    return ti

# ========== 滑动窗口策略测试 ==========

def sliding_window_backtest(code, name, klines, window_size=40):
    """
    滑动窗口回测：用前window_size根K线判断第window_size+1根K线的涨跌
    
    返回：{signals, wins, losses, win_rate, ...}
    """
    ti = load_technical_engine()
    results = []
    
    def get_price(klines_row):
        """从K线行提取收盘价"""
        if isinstance(klines_row, dict):
            return float(klines_row.get("close", 0))
        elif isinstance(klines_row, (list, tuple)):
            return float(klines_row[2]) if len(klines_row) > 2 else 0
        return 0
    
    total_test = len(klines) - window_size - 1
    if total_test < 10:
        return {"error": f"数据不足，只能测试{max(0,total_test)}次"}
    
    correct_bull = 0  # 看多信号 → 次日上涨
    correct_bear = 0  # 看空信号 → 次日下跌
    total_bull = 0
    total_bear = 0
    false_bull = 0    # 看多但跌了
    false_bear = 0    # 看空但涨了
    
    # 模拟交易
    simulated_capital = 100000
    cash = simulated_capital
    position = None  # {code, shares, buy_price, buy_date}
    trades = []
    trade_pnls = []
    
    for i in range(window_size, len(klines) - 1):
        train = klines[i - window_size:i]
        test_kline = klines[i]
        next_kline = klines[i + 1]
        
        test_date = test_kline.get("date", "?") if isinstance(test_kline, dict) else str(test_kline[0] if test_kline else "?")
        test_price = get_price(test_kline)
        next_price = get_price(next_kline)
        
        if test_price <= 0 or next_price <= 0:
            continue
        
        try:
            analysis = ti.full_technical_analysis(train)
            signals = analysis.get("signals", {})
            score = signals.get("signal_score", 0)
            strength = signals.get("signal_strength", "中性")
            trend_direction = signals.get("trend_direction", "震荡")
        except:
            continue
        
        # 计算均线
        closes = [get_price(k) for k in train]
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else sum(closes) / len(closes)
        ma5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else sum(closes) / len(closes)
        
        # 策略判断
        predicted_direction = 0  # 0=观望, 1=看涨, -1=看跌
        signal_type = "观望"
        
        if score >= 2 and test_price > ma20:
            predicted_direction = 1
            signal_type = "看多(信号强+均线上方)"
            total_bull += 1
            if next_price > test_price:
                correct_bull += 1
                win = True
            else:
                false_bull += 1
                win = False
        
        elif score <= -2 and test_price < ma20:
            predicted_direction = -1
            signal_type = "看空(信号弱+均线下方)"
            total_bear += 1
            if next_price < test_price:
                correct_bear += 1
                win = True
            else:
                false_bear += 1
                win = False
        
        # 模拟交易
        actual_change = (next_price - test_price) / test_price * 100
        
        if predicted_direction == 1:
            # 看多信号：买入持有1天
            if position is None:
                shares = int(cash * 0.3 / test_price / 100) * 100
                if shares >= 100:
                    cost = shares * test_price
                    if cost <= cash:
                        position = {"code": code, "shares": shares, "buy_price": test_price, "buy_date": test_date}
                        cash -= cost
                        trades.append({
                            "date": test_date,
                            "type": "买入",
                            "price": test_price,
                            "shares": shares,
                            "reason": signal_type,
                            "score": score,
                        })
        elif predicted_direction == -1:
            # 看空信号：如果持有则卖出
            if position is not None and position["code"] == code:
                sell_value = position["shares"] * test_price
                pnl = sell_value - (position["shares"] * position["buy_price"])
                pnl_pct = round((test_price - position["buy_price"]) / position["buy_price"] * 100, 2)
                cash += sell_value
                trade_pnls.append(pnl)
                trades.append({
                    "date": test_date,
                    "type": "卖出",
                    "price": test_price,
                    "shares": position["shares"],
                    "reason": signal_type,
                    "pnl": round(pnl, 2),
                    "pnl_pct": pnl_pct,
                    "score": score,
                })
                position = None
        
        # 日内止盈：如果上涨超过3%且持有，卖出
        if position is not None and (next_price - position["buy_price"]) / position["buy_price"] > 0.03:
            sell_value = position["shares"] * next_price
            pnl = sell_value - (position["shares"] * position["buy_price"])
            cash += sell_value
            trade_pnls.append(pnl)
            trades.append({
                "date": test_kline.get("date", "?"),
                "type": "止盈",
                "price": next_price,
                "shares": position["shares"],
                "pnl": round(pnl, 2),
                "pnl_pct": round((next_price - position["buy_price"]) / position["buy_price"] * 100, 2),
            })
            position = None
        
        # 日内止损：如果下跌超过2%，卖出
        if position is not None and (next_price - position["buy_price"]) / position["buy_price"] < -0.02:
            sell_value = position["shares"] * next_price
            pnl = sell_value - (position["shares"] * position["buy_price"])
            cash += sell_value
            trade_pnls.append(pnl)
            trades.append({
                "date": test_date,
                "type": "止损",
                "price": next_price,
                "shares": position["shares"],
                "pnl": round(pnl, 2),
                "pnl_pct": round((next_price - position["buy_price"]) / position["buy_price"] * 100, 2),
            })
            position = None
    
    # 平掉最后持仓
    if position is not None:
        last_price = get_price(klines[-1])
        sell_value = position["shares"] * last_price
        pnl = sell_value - (position["shares"] * position["buy_price"])
        cash += sell_value
        trade_pnls.append(pnl)
        trades.append({
            "date": klines[-1].get("date", "?"),
            "type": "平仓",
            "price": last_price,
            "shares": position["shares"],
            "pnl": round(pnl, 2),
            "pnl_pct": round((last_price - position["buy_price"]) / position["buy_price"] * 100, 2),
        })
        position = None
    
    # 统计
    total_signals = total_bull + total_bear
    correct_signals = correct_bull + correct_bear
    win_rate = round(correct_signals / total_signals * 100, 1) if total_signals > 0 else 0
    bull_win_rate = round(correct_bull / total_bull * 100, 1) if total_bull > 0 else 0
    bear_win_rate = round(correct_bear / total_bear * 100, 1) if total_bear > 0 else 0
    
    # 交易收益
    total_pnl = sum(trade_pnls)
    total_pnl_pct = round(total_pnl / simulated_capital * 100, 2)
    trade_count = len([t for t in trades if t["type"] in ("卖出", "止盈", "止损", "平仓")])
    win_trades = sum(1 for p in trade_pnls if p > 0)
    lose_trades = sum(1 for p in trade_pnls if p < 0)
    trade_win_rate = round(win_trades / trade_count * 100, 1) if trade_count > 0 else 0
    final_asset = cash
    
    return {
        "code": code,
        "name": name,
            "period": f"{klines[0].get('date', '?')} ~ {klines[-1].get('date', '?')}" if len(klines) > 1 else "?",
        "sessions": len(klines),
        "total_signals": total_signals,
        "bull_signals": total_bull,
        "bear_signals": total_bear,
        "correct_bull": correct_bull,
        "correct_bear": correct_bear,
        "false_bull": false_bull,
        "false_bear": false_bear,
        "overall_win_rate": win_rate,
        "bull_win_rate": bull_win_rate,
        "bear_win_rate": bear_win_rate,
        "simulated_start": simulated_capital,
        "simulated_end": round(final_asset, 2),
        "simulated_pnl": round(total_pnl, 2),
        "simulated_pnl_pct": total_pnl_pct,
        "trade_count": trade_count,
        "win_trades": win_trades,
        "lose_trades": lose_trades,
        "trade_win_rate": trade_win_rate,
        "trades": trades[-20:],  # 最后20笔
    }


def run_single(code, name=""):
    """运行单只标的回测"""
    print(f"\n🔬 回测: {name}({code})")
    print("=" * 40)
    
    data = get_kline(code, 180)  # 约6个月
    if "error" in data:
        print(f"  ❌ {data['error']}")
        return None
    
    klines = data.get("klines", [])
    if len(klines) < 50:
        print(f"  ❌ K线不足({len(klines)})，需要至少50条")
        return None
    
    print(f"  📅 {klines[0].get('date','?')} ~ {klines[-1].get('date','?')} ({len(klines)}个交易日)")
    
    result = sliding_window_backtest(code, name, klines)
    if "error" in result:
        print(f"  ❌ {result['error']}")
        return result
    
    # 打印回测报告
    print(f"\n  📊 信号统计:")
    print(f"     总信号: {result['total_signals']}次 (看多{result['bull_signals']} / 看空{result['bear_signals']})")
    print(f"     看多正确: {result['correct_bull']}/{result['bull_signals']} ({result['bull_win_rate']}%)")
    print(f"     看空正确: {result['correct_bear']}/{result['bear_signals']} ({result['bear_win_rate']}%)")
    print(f"     综合胜率: {result['overall_win_rate']}%")
    print(f"\n  💰 模拟交易 (10万本金):")
    print(f"     {result['trade_count']}笔交易")
    print(f"     胜率: {result['win_trades']}胜/{result['lose_trades']}负 ({result['trade_win_rate']}%)")
    sym = "+" if result['simulated_pnl'] >= 0 else ""
    print(f"     最终资产: ¥{result['simulated_end']:,.0f} ({sym}{result['simulated_pnl_pct']}%)")
    
    # 最近交易
    if result['trades']:
        print(f"\n  📝 最近交易:")
        for t in result['trades'][-5:]:
            sym = "🟢" if t.get('pnl', 0) >= 0 else "🔴"
            pct = f" ({t['pnl_pct']}%)" if 'pnl_pct' in t else ""
            print(f"     {t['date']} {t['type']}: {t['shares']}股 @ {t['price']:.2f} {sym}¥{t.get('pnl', 0):.0f}{pct}")
    
    return result


def batch_backtest():
    """批量回测整个监控池"""
    print("🧪 顾比交易大脑 — 批量回测")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📋 监控池: {len(WATCHLIST)}只标的\n")
    
    all_results = []
    for w in WATCHLIST:
        code = w["code"]
        name = w["name"]
        
        data = get_kline(code, 180)
        if "error" in data or not data.get("klines"):
            print(f"  ❌ {name}({code}) — 数据获取失败")
            continue
        
        klines = data["klines"]
        if len(klines) < 50:
            print(f"  ❌ {name}({code}) — K线不足({len(klines)})")
            continue
        
        result = sliding_window_backtest(code, name, klines)
        if "error" in result:
            print(f"  ❌ {name}({code}) — {result['error']}")
            continue
        
        all_results.append(result)
        
        # 压缩输出
        sym = "+" if result['simulated_pnl'] >= 0 else ""
        print(f"  {'✅' if result['trade_win_rate'] >= 50 else '⚠️'} {name}({code}): "
              f"信号胜率{result['overall_win_rate']}% | "
              f"交易{result['trade_count']}笔胜{result['trade_win_rate']}% | "
              f"收益{sym}{result['simulated_pnl_pct']}%")
    
    # 汇总
    print("\n" + "=" * 50)
    print("📋 批量回测汇总")
    
    avg_win_rate = sum(r['overall_win_rate'] for r in all_results) / len(all_results)
    avg_trade_win = sum(r['trade_win_rate'] for r in all_results) / len(all_results)
    avg_pnl = sum(r['simulated_pnl_pct'] for r in all_results) / len(all_results)
    positive_count = sum(1 for r in all_results if r['simulated_pnl'] > 0)
    
    print(f"  覆盖: {len(all_results)}/{len(WATCHLIST)}只标的")
    print(f"  平均信号胜率: {avg_win_rate:.1f}%")
    print(f"  平均交易胜率: {avg_trade_win:.1f}%")
    print(f"  平均收益: {avg_pnl:+.2f}%")
    print(f"  正收益标的: {positive_count}/{len(all_results)} ({positive_count/len(all_results)*100:.0f}%)")
    print(f"\n  策略说明: 技术评分≥2+均线上方→看多 | 评分≤-2+均线下方→看空")
    print(f"  止盈3% | 止损2% | 单只仓位30%")
    
    # 保存结果
    output = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "total_stocks": len(WATCHLIST),
        "tested": len(all_results),
        "summary": {
            "avg_signal_win_rate": round(avg_win_rate, 1),
            "avg_trade_win_rate": round(avg_trade_win, 1),
            "avg_pnl_pct": round(avg_pnl, 2),
            "positive_stocks": positive_count,
        },
        "results": all_results,
    }
    report_path = os.path.join(BRAIN_DIR, "..", "data", "backtest_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  💾 报告已保存: {os.path.abspath(report_path)}")
    
    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "batch":
        batch_backtest()
    
    elif cmd == "report":
        path = os.path.join(BRAIN_DIR, "..", "data", "backtest_report.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            s = data["summary"]
            print("📋 顾比回测报告")
            print("=" * 45)
            print(f"📅 {data['timestamp']}")
            print(f"覆盖: {data['tested']}/{data['total_stocks']}只")
            print(f"信号胜率: {s['avg_signal_win_rate']}%")
            print(f"交易胜率: {s['avg_trade_win_rate']}%")
            print(f"平均收益: {s['avg_pnl_pct']:+.2f}%")
            print(f"正收益比: {s['positive_stocks']}/{data['tested']}")
        else:
            print("❌ 还没有回测报告，先跑 batch 命令")
    
    else:
        # 单只回测
        code = cmd
        name = ""
        for w in WATCHLIST:
            if w["code"] == code:
                name = w["name"]
                break
        
        if len(sys.argv) > 2 and sys.argv[2] == "--full":
            result = run_single(code, name)
            if result:
                print(f"\n完整回测数据JSON:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            run_single(code, name)
