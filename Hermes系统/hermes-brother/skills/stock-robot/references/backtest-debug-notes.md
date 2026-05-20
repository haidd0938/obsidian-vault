# 回测调试记录

> 2026-05-05 会话中发现的坑和修复记录
> 环境：macOS Intel MacBook + Python 3 + Tencent/K-line API

## 1. 信号全为0的诊断

**症状**：回测 `sliding_window_backtest` 全部信号为0，胜率0%
**根因**：窗口太小（20根K线），`full_technical_analysis` 需要更多数据

**诊断流程**：
```python
# step1: 打印信号分布
signal_scores = [a.get('signal_score',0) for a in analysis_list]
print(f"非零信号: {sum(1 for s in signal_scores if s != 0)}")

# step2: 对比不同窗口大小
result1 = ta.full_technical_analysis(klines[:20])  # ❌ 信号=0
result2 = ta.full_technical_analysis(klines[:40])  # ✅ 信号=2.0
```

**结论**：回测时 window_size 应设为 ≥40，不是20。回测的"训练窗口"和"预测窗口"需要分开理解。

## 2. K线数据是dict不是list

**症状**：`TypeError: list indices must be integers or slices, not str` 或 IndexError

**根因**：腾讯API返回的K线项是 dict 结构：
```python
# ✅ 正确访问方式
kline.get('date', '?')
kline.get('close', 0)
kline.get('open', 0)
kline.get('high', 0)
kline.get('low', 0)
kline.get('volume', 0)

# ❌ 错误方式（来自旧版代码或list假设）
kline[0], kline[2], kline[-1][2]
```

**常见出问题的位置**：
- 止损/止盈检查时的 `test_kline[0]` → `.get("date")`
- 平仓时的 `klines[-1][2]` → `.get("close")`
- 日期范围打印：`klines[0][0]` → `.get("date")`

## 3. full_technical_analysis 返回值结构

```python
result = ta.full_technical_analysis(klines_list)
# result 是 dict
result.get('signals', {})           # 信号字典
result['signals'].get('signal_strength', '中性')   # 信号强度文本
result.get('signal_score', 0)        # 数值评分（关键字段！）
result.get('all_signals_count', 0)   # 子信号个数
```

**注意**：`signal_score` 是 key 在 dict 顶层，不是嵌套在 `signals` 里。评分范围 -4 ~ 4。

## 4. ETF 标的的特殊处理

所有ETF标的（如 159840, 516020）在 `get_quote()` 中：
- `current_price` 可能返回 0
- 需要 fallback 到 `avg_cost` 字段
- 基本面评分为 0（PE=0, ROE=0）
- K线数据正常获取不受影响

## 5. backtest.py 关键逻辑

```
初始化: 账户10万 + 阈值 buy_threshold=2, sell_threshold=-2
        止盈 3%, 止损 2%, 每笔 30% 仓位

滑动窗口:
  - train = klines[i-window_size:i]  # 40天训练
  - test = klines[i]                  # 第41天验证
  - train → full_technical_analysis → signal_score
  - if signal ≥ 2 AND close > MA20 → 买入
  - if signal ≤ -2 AND close < MA20 → 卖出

回测输出:
  - 信号胜率（信号方向 vs 实际走势）
  - 交易胜率（实际交易盈亏比）
  - 历史收益曲线
  - 最大回撤
```
