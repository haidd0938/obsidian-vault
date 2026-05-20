# 🧠 顾比交易大脑 v2.0

> 三引擎融合的智能交易决策系统 — **纯Python零依赖，零成本运行**
> 数据源：腾讯证券 + 东方财富 + 新浪财经（全部免费，无需API Key）
> 覆盖：A股 + ETF，自动监控15只标的

---

## 🚀 快速上手

### 环境要求
- Python 3.7+（macOS/Linux都行）
- **零依赖** — 纯Python标准库，不需要装任何第三方包

### 第一条命令

```bash
# 完整分析（大盘复盘+评分卡+高级技术分析+融合决策）
python3 brain/trading_brain.py full

# 快速扫描（只看结论）
python3 brain/trading_brain.py scan

# 深度分析单只股票
python3 brain/trading_brain.py deep 159840

# 系统仪表盘
python3 brain/trading_brain.py cockpit
```

看到输出就成功了。数据全部实时从腾讯证券API拉取。

### 其他常用命令

```bash
# 大盘复盘（独立运行）
python3 brain/market_overview.py

# 高级技术分析（缠论/波浪/一目均衡）
python3 brain/advanced_tech.py

# 每日模拟交易
python3 brain/paper_trader.py daily

# 美观日报
python3 brain/paper_trader.py report

# 批量回测
python3 brain/backtest.py batch

# 模拟账户状态
python3 brain/paper_account.py status

# 多渠道推送测试
python3 brain/notifier.py test
```

---

## 🧠 系统架构

```
stock-robot/
├── orchestrator.py           # 🔌 旧引擎主调度器（兼容老用法）
├── gubi_brain.sh             # 🚀 快捷命令（bash别名）
├── brain/                    # 🧠 顾比交易大脑（核心引擎）
│   ├── config.py              # 统一配置（权重/监控池/阈值）
│   ├── data_layer.py          # 数据层（行情+K线+板块+大盘）
│   ├── fundamental_analysis.py# 基本面引擎（PE/PB/ROE评分）
│   ├── sentiment_engine.py    # 情绪引擎（新闻/板块热度）
│   ├── signal_fusion.py       # 三引擎融合决策
│   ├── decision_engine.py     # 决策评分卡（0-100评分+评级+警报）
│   ├── market_overview.py     # 大盘复盘（指数+涨跌+板块+趋势）
│   ├── advanced_tech.py       # 高级技术分析（缠论/波浪/一目均衡）
│   ├── trading_brain.py       # 🧠 主调度器（集成全流程）
│   ├── paper_account.py       # 模拟资金账户
│   ├── paper_trader.py        # 每日模拟交易执行
│   ├── backtest.py            # 历史回测引擎
│   ├── yolo_trader.py         # YOLO安全执行模式
│   ├── cookie_jar.py          # 持仓管理
│   └── notifier.py            # 多渠道推送
├── scripts/                  # 🔧 旧引擎组件
│   ├── stock-quote.py         # 行情引擎（实时+历史K线）
│   ├── technical-indicators.py# 技术指标计算（MACD/KDJ/RSI/MA/BOLL）
│   ├── daily-review.py        # 每日复盘报告
│   ├── market-news.py         # 市场热点检索
│   └── trade-log.py           # 模拟交易日志
└── data/                     # 📁 数据文件
    ├── paper_account.json     # 模拟账户
    ├── trade_log.json         # 交易日志
    └── daily_reports/         # 每日报告存档
```

### 核心流程（full命令）

```
trading_brain.py full
  ① 大盘复盘     → market_overview.get_market_overview()
  ② 基本面分析   → fundamental_analysis.batch_analysis()
  ③ 情绪分析     → sentiment_engine.assess_market_sentiment()
  ④ 技术面分析   → technical-indicators.py（全部15只标的）
  ⑤ 高级技术分析 → advanced_tech.py（缠论+波浪+一目均衡）
  ⑥ 三引擎融合   → signal_fusion.fusion_decision()
  ⑦ 决策评分卡   → decision_engine.build_decision_card()
  ⑧ 结果输出     → 控制台打印 + JSON存档
```

---

## 📊 技术指标

| 指标 | 参数 | 信号含义 |
|------|------|---------|
| **MA** | 5/10/20/30/60日 | 多头排列=上涨，空头排列=下跌 |
| **MACD** | 12/26/9 | DIF>DEA多头，DIF<DEA空头 |
| **KDJ** | 9/3/3 | K>80超买，K<20超卖 |
| **RSI** | 6/12/24 | >70超买，<30超卖 |
| **BOLL** | 20/2σ | 上轨超买，下轨超卖 |
| **缠论** | 分型/笔/中枢 | 一买/二买/三买/一卖/二卖/三卖 |
| **波浪** | 5浪推动+3浪调整 | 当前位置+浪型预测 |
| **一目均衡** | 云层/基准线 | 云层突破/转换线信号 |

---

## ⚙️ 自定义配置

编辑 `brain/config.py` 可以改：

```python
# 监控池（想监控哪些股票/ETF）
WATCHLIST = {
    "159840": {"name": "锂电池ETF", "type": "ETF"},
    "516020": {"name": "化工ETF", "type": "ETF"},
    "512480": {"name": "半导体ETF", "type": "ETF"},
    "588000": {"name": "科创50ETF", "type": "ETF"},
    "510300": {"name": "沪深300ETF", "type": "ETF"},
    "159865": {"name": "基建ETF", "type": "ETF"},
    "159930": {"name": "能源ETF", "type": "ETF"},
    "002594": {"name": "比亚迪", "type": "stock"},
    "603986": {"name": "兆易创新", "type": "stock"},
    "601668": {"name": "中国建筑", "type": "stock"},
    "601390": {"name": "中国中铁", "type": "stock"},
    "600585": {"name": "海螺水泥", "type": "stock"},
    "AAPL":   {"name": "苹果", "type": "US"},
    "TSLA":   {"name": "特斯拉", "type": "US"},
    "COIN":   {"name": "Coinbase", "type": "US"},
}

# 融合权重
WEIGHTS = {
    "technical": 0.40,   # 技术面
    "fundamental": 0.25, # 基本面
    "sentiment": 0.20,   # 情绪面
    "trend": 0.15,       # 趋势动量
}

# YOLO安全模式（默认开启，只建议不执行）
YOLO_MODE = True
```

---

## 📈 模拟盘

系统内置了模拟交易功能，不用真金白银：

```bash
# 查看持仓
python3 brain/paper_account.py status

# 每日自动交易
python3 brain/paper_trader.py daily

# 查看交易历史
python3 scripts/trade-log.py history

# 重置账户（初始资金1万）
python3 brain/paper_account.py reset --amount 10000
```

### 模拟规则
- 初始资金：¥10,000
- 手续费：万2.5（最低¥5）
- 卖出印花税：千1
- 每次买卖上限：总资金的20%

---

## 📊 回测引擎

```bash
# 批量回测全部15只标的
python3 brain/backtest.py batch

# 单只回测
python3 brain/backtest.py 300750

# 查看回测报告
python3 brain/backtest.py report
```

---

## 🐛 常见问题

### 1. 行情获取失败
macOS Python 3.12 有SSL兼容性问题，会自动降级到 `curl` 模式。如果还是失败：
```bash
# 手动测试行情API
curl -sL "https://qt.gtimg.cn/q=sh000001" | iconv -f gbk -t utf-8
```

### 2. 缠论报错
需要至少**40根K线**才能稳定计算。刚开市的股票可能数据不够。

### 3. 所有指标都是None
数据不足，等积累更多K线数据。一般3个月以上的股票就没问题。

### 4. 大盘API超时
东方财富大盘API偶尔会超时，重试一次就行。代码里已经做了异常保护。

---

## 📝 代码规范

写这个系统的时候注意：

1. **文件名含"-"的无法import** — 用 `importlib` 或 `subprocess` 调用
2. **所有被调用的脚本**必须用 `if __name__ == "__main__":` 包裹CLI入口
3. **跨模块通信**用subprocess + stdout JSON，不要直接import
4. **三元表达式别套娃** — Python的 `a if b else c if d else e` 有坑，老老实实用 if/elif/else
5. **腾讯API字段索引不稳定** — 涨跌家数（fields[51/52/53]）在不同指数中索引不同，用try/except保护

---

## 💡 一句话总结

> **纯Python零依赖、零成本、纯规则驱动的A股+ETF量化交易分析系统。**
> 秒杀市面上那些要API Key、要付费、要装一堆包的"量化神器"。
> 打开终端、敲命令、出报告。
