---
name: stock-monitor
description: 股票/ETF行情监控与每日复盘分析。支持实时行情获取、每日收盘复盘、趋势分析、操作建议。使用腾讯证券API（免费，无需API Key）。当用户需要：监控股票行情、每日复盘、趋势分析、投资决策参考时使用。
---

# 股票监控分析技能包

A股股票和ETF行情监控与每日复盘分析工具。

## 功能

1. **实时行情获取** — 获取任意A股股票/ETF/大盘指数实时数据
2. **每日收盘复盘** — 自动生成完整的复盘报告（含大盘、持仓、趋势、建议）
3. **趋势分析** — 基于涨跌幅和成交量判断趋势强弱
4. **可配置监控列表** — 修改 `scripts/daily-review.py` 中的 `DEFAULT_WATCHLIST` 即可

## 快速使用

### 获取单只行情

```bash
python3 scripts/stock-quote.py 002594
```

### 批量获取

```bash
python3 scripts/stock-quote.py 159840 516020 512480 002594 603986
```

### 获取大盘指数

```bash
python3 scripts/stock-quote.py sh000001 sz399001 sz399006
```

### 生成完整复盘报告

```bash
python3 scripts/daily-review.py
```

### 保存复盘报告到文件

```bash
python3 scripts/daily-review.py --save
```

## 脚本说明

### stock-quote.py

核心行情获取脚本，使用腾讯证券API（免费，无需API Key）。

**支持的代码格式：**
- A股股票：`002594`（比亚迪）、`603986`（兆易创新）
- ETF：`159840`（锂电池ETF）、`516020`（化工ETF）、`512480`（半导体ETF）
- 大盘指数：`sh000001`（上证）、`sz399001`（深证）、`sz399006`（创业板）

**输出格式：** JSON，包含以下字段：
- `code` / `name` / `current_price` / `yesterday_close` / `open_price`
- `high` / `low` / `change` / `change_pct`
- `volume`（手）/ `amount`（元）
- `market_cap`（亿）/ `circulating_cap`（亿）
- `pe_ratio` / `amplitude`

### daily-review.py

每日复盘报告生成脚本，自动完成：
1. 获取大盘指数（上证、深证、创业板）
2. 获取监控列表中所有标的行情
3. 生成趋势分析和评级
4. 输出操作建议

## 配置监控列表

编辑 `scripts/daily-review.py` 中的 `DEFAULT_WATCHLIST`：

```python
DEFAULT_WATCHLIST = [
    {"code": "159840", "name": "锂电池ETF", "type": "ETF"},
    {"code": "516020", "name": "化工ETF", "type": "ETF"},
    {"code": "512480", "name": "半导体ETF", "type": "ETF"},
    {"code": "002594", "name": "比亚迪", "type": "股票"},
    {"code": "603986", "name": "兆易创新", "type": "股票"},
]
```

## 依赖

- Python 3（内置 `urllib`、`json`，无需额外安装）
- 网络连接（访问 `qt.gtimg.cn`）

## 注意事项

- 腾讯证券API数据为实时行情，但可能有短暂延迟
- 非交易时段获取的是最近一个交易日的收盘数据
- 所有数据仅供参考，不构成投资建议
