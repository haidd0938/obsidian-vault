#!/usr/bin/env python3
"""快速验证技术指标"""
import json, sys, os, subprocess

# 获取K线
result = subprocess.run(
    [sys.executable, os.path.join(os.path.dirname(__file__), "stock-quote.py"), "--kline", "159840", "120"],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
klines = data[0]["klines"]
print(f"锂电池ETF: {len(klines)}条K线, {klines[-1]['date']}收盘{klines[-1]['close']}")

# 技术分析
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location("tech", os.path.join(os.path.dirname(__file__), "technical-indicators.py"))
tech = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tech)

analysis = tech.full_technical_analysis(klines)
print(f"\n=== 技术面综合评级 ===")
print(f"价格: {analysis['last_close']} ({analysis['last_date']})")
print(f"60日区间: {analysis['price_range']['low_60d']} ~ {analysis['price_range']['high_60d']}")
print(f"均线排列: {analysis['ma_arrangement']}")
for k,v in sorted(analysis['ma'].items()):
    print(f"  {k}={v}")
m = analysis['macd']
print(f"MACD: DIF={m['DIF']} DEA={m['DEA']} 柱={m['MACD']}")
k = analysis['kdj']
print(f"KDJ: K={k['K']} D={k['D']} J={k['J']}")
r = analysis['rsi']
print(f"RSI: RSI6={r['RSI6']} RSI12={r['RSI12']} RSI24={r['RSI24']}")
s = analysis['signals']
print(f"\n信号评分: {s['signal_score']}")
print(f"综合评级: {s['signal_strength']}")
print(f"\n详细信号:")
for sig in s['signals']:
    print(f"  [{sig['indicator']}] {sig['signal']}: {sig['detail']}")

print(f"\n{tech.full_technical_summary(klines)}")

# 测试模拟交易
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
trade_log_spec = importlib.util.spec_from_file_location("trade_log", os.path.join(os.path.dirname(os.path.abspath(__file__)), "trade-log.py"))
trade_log = importlib.util.module_from_spec(trade_log_spec)
trade_log_spec.loader.exec_module(trade_log)
print(f"\n=== 模拟交易测试 ===")
# 重置
trade_log.cmd_reset(10000)
# 买入
r1 = trade_log.cmd_buy("159840", "锂电池ETF", 3000, 0.96)
print(f"买入: {r1}")
r2 = trade_log.cmd_buy("002594", "比亚迪", 3000, 102.0)
print(f"买入: {r2}")
# 查持仓
summary = trade_log.cmd_summary()
print(f"\n持仓: {summary['position_count']}只, 总资产: {summary['total_assets']:.2f}, 收益: {summary['total_return']:.2f}%")
# 卖出
r3 = trade_log.cmd_sell("159840", "half", 0.99)
print(f"卖出半仓: {r3}")
summary = trade_log.cmd_summary()
print(f"持仓: {summary['position_count']}只, 总资产: {summary['total_assets']:.2f}, 收益: {summary['total_return']:.2f}%")
