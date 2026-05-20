---
name: stock-robot
description: 🤖 独立股票量化助手 — 不依赖任何外部API密钥，纯免费数据源。集成技术指标分析(MACD/KDJ/RSI/MA/BOLL)、市场热点检索、每日智能复盘报告、模拟交易日志系统。完全独立于Hermes主环境运行。
---

# 🤖 股票量化机器人 — Stock Robot

> **完全独立运行的股票分析系统**  
> 路径：`~/stock-robot/`  
> 数据源：腾讯证券API（免费） + 新浪财经/东方财富（免费）  
> 零依赖：纯Python标准库，无需安装任何第三方包

## 🚀 快速启动

```bash
# ===== 基础版（旧引擎）=====
cd ~/stock-robot && python3 orchestrator.py full      # 完整复盘
cd ~/stock-robot && python3 orchestrator.py scan      # 快速扫描
cd ~/stock-robot && python3 orchestrator.py deep 159840 # 深度分析
cd ~/stock-robot && python3 orchestrator.py news      # 热点新闻
cd ~/stock-robot && python3 orchestrator.py status    # 模拟盘状态

# ===== 顾比交易大脑 v2.0（新引擎，推荐使用）=====
cd ~/stock-robot && python3 brain/trading_brain.py full    # 完整分析（大盘复盘+评分卡+高级分析+融合决策）
cd ~/stock-robot && python3 brain/trading_brain.py cockpit # 系统仪表盘
cd ~/stock-robot && python3 brain/market_overview.py       # 大盘复盘（独立运行）
cd ~/stock-robot && python3 brain/advanced_tech.py         # 高级技术分析（缠论/波浪/一目均衡）
cd ~/stock-robot && python3 brain/paper_trader.py daily    # 每日模拟交易
cd ~/stock-robot && python3 brain/paper_trader.py report   # 美观日报
cd ~/stock-robot && python3 brain/backtest.py batch        # 批量回测
cd ~/stock-robot && python3 brain/notifier.py test         # 多渠道推送测试
```

## 📂 系统结构

```
~/stock-robot/
├── orchestrator.py          # 主控调度器（旧引擎入口）
├── scripts/
│   ├── stock-quote.py        # 行情引擎（实时+历史K线）
│   ├── technical-indicators.py  # 技术指标计算（MACD/KDJ/RSI/MA/BOLL）
│   ├── daily-review.py       # 每日复盘报告生成器
│   ├── market-news.py        # 市场热点检索
│   ├── trade-log.py          # 模拟交易日志系统
│   └── test_system.py        # 系统集成测试（临时，可删除）
├── brain/                    # 🧠 顾比交易大脑（v2.0新引擎）
│   ├── config.py              # 统一配置（权重/监控池/阈值/YOLO）
│   ├── data_layer.py          # 数据层（行情+K线+板块+大盘）
│   ├── fundamental_analysis.py # 基本面引擎（PE/PB/ROE评分）
│   ├── sentiment_engine.py    # 情绪引擎（新闻/板块热度）
│   ├── signal_fusion.py       # 三引擎融合（旧融合逻辑）
│   ├── decision_engine.py     # 📋 决策评分卡（v2.0新增：0-100评分+评级+警报+检查清单）
│   ├── market_overview.py     # 📊 大盘复盘（v2.0新增：指数+涨跌统计+板块+趋势）
│   ├── advanced_tech.py       # 📐 高级技术分析（v2.0新增：缠论/波浪/一目均衡）
│   ├── notifier.py            # 📱 多渠道推送（v2.0新增：企微/飞书/终端/macOS）
│   ├── yolo_trader.py         # YOLO安全执行模式
│   ├── cookie_jar.py          # Cookie Jar持仓管理
│   ├── trading_brain.py       # 🧠 主调度器（集成大盘复盘+评分卡+高级分析+融合决策）
│   ├── paper_account.py       # 💰 模拟资金账户
│   ├── paper_trader.py        # 🔄 每日模拟交易执行器
│   └── backtest.py            # 📊 历史回测引擎
├── data/
│   ├── trade_log.json         # 模拟盘数据
│   ├── paper_account.json     # 顾比模拟账户
│   └── cookie_jar.json        # Cookie Jar持仓
└── logs/
    ├── 复盘报告_*.md           # 基础版复盘报告存档
    └── brain_reports/         # 顾比大脑报告存档
```

## 📊 技术指标说明

| 指标 | 参数 | 信号含义 |
|:---|:---|:---|
| **MA** | 5/10/20/30/60日 | 多头排列(短期>长期)=上涨趋势，空头排列=下跌趋势 |
| **MACD** | 12/26/9 | DIF>DEA红柱=多头，DIF<DEA绿柱=空头 |
| **KDJ** | 9/3/3 | K>80超买，K<20超卖，K上穿D=买入信号 |
| **RSI** | 6/12/24 | RSI6>70超买，RSI6<30超卖，>50偏多 |
| **BOLL** | 20/2σ | 触及上轨=超买，触及下轨=超卖，中轨支撑/压力 |

## 💰 模拟盘操作

```bash
# 查看模拟盘状态
cd ~/stock-robot/scripts && python3 trade-log.py summary

# 买入（以当前市价）
python3 trade-log.py buy 159840 锂电池ETF 3000

# 买入（指定价格）
python3 trade-log.py buy 002594 比亚迪 5000 105.5

# 卖出全部
python3 trade-log.py sell 159840 all

# 卖出半仓
python3 trade-log.py sell 002594 half

# 交易历史
python3 trade-log.py history

# 重置模拟盘
python3 trade-log.py reset 10000
```

## ⏰ 定时任务

每日收盘后自动复盘（15:30 交易日下午）：
```bash
# 在 Hermes 中设置
cronjob action=create schedule="30 15 * * 1-5" prompt="运行股票机器人完整复盘" skills=["stock-robot"]
```

## 📝 自定义监控列表

编辑 `~/stock-robot/scripts/daily-review.py` 中的 `DEFAULT_WATCHLIST` 和 `EXTRA_WATCH`。

或者编辑 `~/stock-robot/brain/config.py` 中的 `WATCHLIST`（12只标的，含ETF和个股）。

## 📋 升级路线（基于竞品对比）

2026-05-08 对比了两个开源项目（HKUDS/Vibe-Trading 6k⭐、ZhuLinsen/daily_stock_analysis）后的改进方向。

### ✅ 已完成的升级（2026-05-08）
| 功能 | 模块 | 说明 |
|------|------|------|
| **大盘复盘模块** | `brain/market_overview.py` | 指数概览+涨跌统计+板块强弱+趋势判断 — `python3 brain/market_overview.py` |
| **决策评分卡系统** | `brain/decision_engine.py` | 综合评分(0-100)+评级(A+/A/B+/B/C/D)+买卖点位+风险警报+检查清单 |
| **缠论/波浪/一目均衡** | `brain/advanced_tech.py` | 缠论(分型/笔/中枢/买卖点)、艾略特波浪、一目均衡表(云层/信号) |
| **多渠道推送框架** | `brain/notifier.py` | 企业微信/飞书/终端/macOS通知统一推送 — `python3 brain/notifier.py test` |
| **集成至主流程** | `brain/trading_brain.py` | `full`命令自动包含大盘复盘→评分卡→高级分析→融合决策全流程 |
| **Cron早报已更新** | 每日7:30 | 早报包含大盘复盘+评分卡+高级技术分析+模拟盘+操作建议 |

### 🔄 中优先级（按需启用，已记录）
| 功能 | 来源 | 说明 |
|------|------|------|
| **多渠道推送配置** | daily_stock_analysis | 编辑`notifier.py`的`NOTIFIER_CONFIG`填写Webhook地址后即可启用 |
| **Vibe-Trading MCP集成** | Vibe-Trading | `pip install vibe-trading-ai && vibe-trading-mcp`，需要LLM API Key |
| **AI辅助决策** | 两个项目 | 可选模块，用DeepSeek对信号做二次确认（控制成本） |
| **交割单分析** | Vibe-Trading | 上传券商交割单→行为偏差诊断+影子账户回测 |

### 不推荐做的
- ❌ 直接替换现有系统 — 零成本纯规则系统适合日常使用
- ❌ 全AI驱动分析 — 持续API调用成本，不如纯规则稳定
- ❌ 跨市场/加密货币 — 老板只关注A股+ETF

详见 `references/vibe-trading-dsa-comparison-2026-05-08.md`。

## 🔍 竞品速览（2026-05-08）

| 项目 | Stars | 核心差异 | 成本 |
|------|-------|---------|------|
| **我们系统** | — | 纯Python零依赖，纯规则驱动，无需API Key | **¥0** |
| **Vibe-Trading** | 6k | AI多Agent金融工作台，全球市场，74技能，29Swarm | LLM API费 |
| **daily_stock_analysis** | ⭐热门 | AI决策仪表盘+A股智能分析，多渠道推送，Web UI | LLM API费 |

## 🛠️ 技术发现 & 避坑指南

### 1. 腾讯证券API数据规则
- **实时行情**: `https://qt.gtimg.cn/q={market_prefix}{code}`，返回 `~` 分隔字段，编码 gbk
- **历史日K线**: `http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,{start_date},,{days},qfq`
  - ⚠️ ETF数据存在 `data.stock.day` 字段，股票数据存在 `data.stock.qfqday` 字段 — 必须做兼容检测
  - 最多返回约 320 条K线（约365天），请求更多也只会返回这些
  - 返回格式: `[日期, 开盘, 收盘, 最高, 最低, 成交量]`
- 大盘指数代码: `sh000001`(上证), `sz399001`(深证), `sz399006`(创业板), `sh000688`(科创50)
- 市场前缀规则: 6/9/51/56/58开头→`sh`，3/0/2开头→`sz`

### 2. Python 3.12 SSL 兼容性问题
- **问题**: macOS Python 3.12 的 `urllib.request.urlopen()` 访问 `https://qt.gtimg.cn` 会报 `SSLEOFError: EOF occurred in violation of protocol`
- **症状**: `stock-quote.py` 和 `orchestrator.py` 都返回行情获取失败
- **临时解决方案**: 使用 `curl -sL` 替代 `urllib` 获取数据（curl正常工作）
  ```python
  import subprocess
  def curl_get(url, timeout=15):
      r = subprocess.run(['curl', '-sL', '--connect-timeout', str(timeout), '-m', str(timeout+5), url],
                         capture_output=True, timeout=timeout+10)
      return r.stdout if r.returncode == 0 and r.stdout else None
  # 实时行情：raw.decode('gbk') → 解析 ~ 分隔字段
  # K线：json.loads(raw) → data[code]['qfqday'] or data[code]['day']
  ```
- **注意**: HTTP的K线API有`302重定向`，`curl`需加`-L`参数跟随跳转
- **建议**: 在macOS上考虑配置SSL上下文或升级到可信任的CA证书

### 3. 模块间调用的路径陷阱
- **问题**: 文件名含 `-`（如 `trade-log.py`、`stock-quote.py`）无法直接 import
- **解决方案**: 使用 `importlib.util.spec_from_file_location()` 动态加载模块
  ```python
  import importlib.util
  spec = importlib.util.spec_from_file_location("module_name", "path/to/script.py")
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  result = mod.function_name(args)
  ```
- **更可靠的方式**: `subprocess.run` 调用脚本，走 stdout JSON 通信
- 确保每个可被调用的脚本都用 `if __name__ == "__main__":` 包裹 CLI 代码

### 3. 安全限制下的测试策略
- Hermes 禁止 `python3 -c "..."` 和 pipe 到解释器模式
- **必须写独立 .py 测试文件**，然后 `python3 test_xxx.py` 执行
- stderr 中有安全告警时不会影响 stdout，但会误导查看

### 4. 跨模块数据传递规范
- 所有通过 `subprocess` 调用的脚本必须输出纯 JSON 到 stdout
- `--json` 或 `--summary` 参数用于区分人读和机读模式
- stderr 保留给人类可读的日志/进度输出

### 5. 技术指标计算细节（纯Python实现）
- **EMA**: 初始值用 SMA(period)，后续 `new_ema = price * k + prev_ema * (1-k)`，k=2/(period+1)
- **MACD**: DIF(快慢差)→ DEA(对DIF再做EMA)→ 柱=2×(DIF-DEA)
- **KDJ**: RSV先算 → K=RSV的3日平滑 → D=K的3日平滑 → J=3K-2D
- **RSI**: 初始平均涨跌幅法，后续递推 `avg_gain = (avg_gain*(p-1)+gain)/p`
- **BOLL**: 标准差直接用 `math.sqrt(sum((x-m)**2 for x in seg)/n)`
- 所有指标不足周期时返回 `None` 填充，不会抛出异常

---

## Section: 顾比交易大脑 — Gubi Trading Brain

> **三引擎融合的智能交易决策系统** — 构建于 stock-robot 之上。
> 路径：`~/stock-robot/brain/`
> 数据源：腾讯证券API + 东方财富 + 新浪财经（全部免费）
> 覆盖：A股 + ETF，12只监控标的

### Quick Start
```bash
cd ~/stock-robot
./gubi_brain.sh full            # 完整分析报告
./gubi_brain.sh scan            # 快速扫描
./gubi_brain.sh deep 002594     # 深度分析单只
./gubi_brain.sh cron            # 精简摘要
python3 brain/trading_brain.py full       # 🆕 完整分析（推荐）—大盘复盘+评分卡+高级分析+融合决策
python3 brain/trading_brain.py cockpit    # 仪表盘
python3 brain/trading_brain.py deep 159840 # 深度分析
python3 brain/market_overview.py          # 🆕 大盘复盘（独立运行）
python3 brain/decision_engine.py          # 🆕 决策评分卡信息
python3 brain/advanced_tech.py            # 🆕 高级技术分析（缠论/波浪/一目均衡）
python3 brain/paper_trader.py daily       # 每日模拟交易
python3 brain/paper_trader.py report      # 美观日报
python3 brain/backtest.py batch           # 批量回测
python3 brain/backtest.py 300750          # 单只回测
python3 brain/paper_account.py status     # 账户状态
python3 brain/notifier.py test            # 🆕 多渠道推送测试
```

### System Architecture
```
~/stock-robot/brain/
├── config.py                  # 统一配置（权重/监控池/阈值/YOLO）
├── data_layer.py              # 数据层（行情+K线+板块+大盘）
├── fundamental_analysis.py    # 基本面引擎（PE/PB/ROE评分）
├── sentiment_engine.py        # 情绪引擎（新闻/板块热度）
├── signal_fusion.py           # 三引擎融合（旧融合逻辑）
├── decision_engine.py         # 📋 决策评分卡（v2.0）—0-100评分+评级+警报+检查清单
├── market_overview.py         # 📊 大盘复盘（v2.0）—指数+涨跌统计+板块强弱+趋势
├── advanced_tech.py           # 📐 高级技术分析（v2.0）—缠论/波浪/一目均衡表
├── notifier.py                # 📱 多渠道推送（v2.0）—企微/飞书/终端/macOS
├── yolo_trader.py             # YOLO安全执行模式
├── cookie_jar.py              # Cookie Jar持仓管理
├── trading_brain.py           # 🧠 主调度器（集成大盘复盘+评分卡+高级分析+融合决策）
├── paper_account.py           # 💰 模拟资金账户
├── paper_trader.py            # 🔄 每日模拟交易执行器
└── backtest.py                # 📊 历史回测引擎
```

### Pipeline (full command flow)
```
trading_brain.py full
  1. 📊 大盘复盘     — market_overview.build_market_overview()
  2. 📗 基本面分析   — fundamental_analysis.batch_analysis()
  3. 📰 情绪分析     — sentiment_engine.assess_market_sentiment()
  4. 📐 技术面分析   — scripts/technical-indicators.py (via importlib)
  5. 📐 高级技术分析 — advanced_tech.advanced_technical_analysis() — 缠论+波浪+一目均衡
  6. 🧠 三引擎融合   — signal_fusion.fusion_decision()
  7. 📋 决策评分卡   — decision_engine.build_decision_card() — 评分+评级+警报+清单
  8. 📱 推送（可选） — notifier.notify()
```

### Signal Weights (config.py)
| Dimension | Default Weight |
|-----------|---------------|
| Technical Analysis | 40% |
| Fundamentals | 25% |
| Sentiment | 20% |
| Trend Momentum | 15% |

### YOLO Safety Mode
Default ON — only produces suggestions, never executes trades. Disable by setting `YOLO_MODE = False` in config.py.

### Watchlist (15 items)
ETF: 锂电池ETF(159840), 化工ETF(516020), 半导体ETF(512480), 科创50ETF(588000), 沪深300ETF(510300), 基建ETF(159865), 能源ETF(159930)
Stocks: 比亚迪(002594), 兆易创新(603986), 中国建筑(601668), 中国中铁(601390), 海螺水泥(600585)
US: AAPL, TSLA, COIN

### Paper Account
- Virtual capital ¥10,000
- Fee: 万2.5 (min ¥5), sell stamp 千1
- API: `load_account()` / `buy_stock()` / `sell_stock()` / `reset_account()`
- Data: `~/stock-robot/data/paper_account.json`

### Backtest Results (Feb-May 2026)
- Avg signal accuracy 43.8% | Trade accuracy 38.2% | Avg return +0.15%
- Best: Energy ETF (+8.77%), STAR 50 ETF (+3.34%), CSI 300 ETF (+2.23%)
- Worst: China Railway (-4.02%), Infrastructure ETF (-3.27%)
- ETF outperforms individual stocks overall

### Cron Jobs

**顾比早报** (Job ID `632bb5e34484` — daily 7:30, trading days Mon-Fri):
```bash
cd ~/stock-robot && python3 brain/trading_brain.py full
cd ~/stock-robot && python3 brain/paper_trader.py report
cd ~/stock-robot && python3 brain/market_overview.py
```
Results write to `~/Desktop/任务中心/01-顾比早报/$(date +%Y-%m-%d)-顾比早报.md`
Content includes: 大盘复盘 + 决策评分卡 + 高级技术分析(缠论/波浪/一目均衡) + 模拟盘日报

**基础版每日复盘** (Job ID `48281b395d0d` — 15:30, trading days Mon-Fri):
```bash
cd ~/stock-robot/scripts && python3 orchestrator.py full
```

### Known Pitfalls
- K-line data is dict format (not list), use `.get("close", 0)` access
- `full_technical_analysis` needs at least 40 K-lines for stable signals
- ETF `current_price` may default to 0, fallback to avg_cost
- All paths managed in `config.py`, never hardcode
- **Ternary syntax gotcha**: `a if cond else b if cond2 else c` is NOT valid Python — must use nested `a if cond else (b if cond2 else c)`. Write multi-branch logic as explicit if/elif/else blocks.
- **腾讯大盘涨跌家数字段不稳定**: 腾讯行情API的fields[51]/fields[52]/fields[53]（涨/平/跌家数）在不同指数中索引可能不同，解析时需要try/except保护
- **New module import chain**: `trading_brain.py full` imports from all brain modules — if any single module fails (e.g. network timeout), wrap it in try/except to avoid crashing the whole pipeline
- **大盘API超时**: `push2.eastmoney.com` 有时会超时，market_overview.py 的 `get_sector_summary` 和 `get_market_breadth` 都需要异常保护
