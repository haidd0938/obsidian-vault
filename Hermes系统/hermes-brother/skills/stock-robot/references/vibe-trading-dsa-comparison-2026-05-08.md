# Vibe-Trading & daily_stock_analysis 竞品对比（2026-05-08）

> 研究日期：2026-05-08 | 用途：为 stock-robot + 顾比交易大脑寻找改进方向
> 项目链接：
> - https://github.com/HKUDS/Vibe-Trading (6k⭐, MIT)
> - https://github.com/ZhuLinsen/daily_stock_analysis (热门, MIT)

---

## 一、HKUDS/Vibe-Trading

### 定位
AI驱动的多Agent金融工作台，将自然语言转化为可执行的交易策略、研究洞察、组合分析。

### 核心数据
- 74个金融专业Skills（8大类）
- 29个Agent Swarm团队预设
- 27个工具
- 6个数据源，自动回退
- 13家LLM提供商（含Ollama本地）
- 7个市场回测引擎
- Python 3.11+ / FastAPI / React 19

### 关键技术栈
```
pip install vibe-trading-ai
# 三个命令：vibe-trading（CLI）、vibe-trading serve（Web UI）、vibe-trading-mcp（MCP Server）
```

### 亮点功能（值得借鉴）

| 功能 | 说明 | 借鉴难度 |
|------|------|---------|
| **缠论策略** | 分型/笔/中枢/买卖点完整参考文档 | 低 — 可直接引用开源文档实现 |
| **艾略特波浪** | 浪间关系+波浪结构+Fibonacci关系 | 低 |
| **一目均衡表** | 五线计算+信号系统 | 低 |
| **SMC/谐波形态** | 结构突破/订单块/XABCD形态 | 低 |
| **回测统计验证** | 蒙特卡洛/Bootstrap/Walk-Forward | 高 — 依赖LLM |
| **交割单分析** | 上传券商交割单→行为偏差诊断+影子账户回测 | 高 — 需要LLM+Tushare |
| **多平台导出** | TradingView Pine Script/通达信/MT5 | 中 |
| **因子研究** | IC/IR/分位回测/MVO/风险平价 | 中-高 |

### 安装方式（若需集成）
```bash
pip install vibe-trading-ai
cd ~/stock-robot && vibe-trading-mcp  # 作为MCP Server运行
```
需要配置LLM API Key（推荐deepseek性价比最高）。

---

## 二、ZhuLinsen/daily_stock_analysis

### 定位
AI驱动的A股/港股/美股自选股智能分析系统，每日自动分析并多渠道推送「决策仪表盘」。

### 核心数据
- 支持A股/港股/美股+ETF
- 7+数据源（TickFlow/AkShare/Tushare/Pytdx/YFinance等）
- 7+新闻搜索源（SerpAPI/博查/Brave/MiniMax等）
- 6+通知渠道（企微/飞书/TG/Discord/Slack/邮件）
- 11种内置策略
- Web UI双主题工作台
- GitHub Actions/Docker/本地cron/桌面客户端

### 亮点功能（最接近我们）

| 功能 | 说明 | 是否值得加 |
|------|------|-----------|
| **决策仪表盘** | 一句话结论+评分(0-100)+买卖点+风险警报+操作检查清单 | ✅ 高 |
| **大盘复盘** | 每日指数表现/涨跌统计/板块强弱 | ✅ 高 |
| **多渠道推送** | 企微/飞书/TG/Discord/Slack/邮件 | ✅ 中 |
| **AI回测验证** | 事后验证方向准确率 | ❌ 依赖LLM |
| **Agent策略对话** | 多轮策略问答 | ❌ 依赖LLM |
| **智能导入** | 图片/CSV/剪贴板/拼音补全 | ❌ 太重 |

### 决策仪表盘输出格式（模仿模板）
```
🎯 2026-xx-xx 决策仪表盘
共分析N只股票 | 🟢买入:X 🟡观望:Y 🔴卖出:Z

⚪ 股票名(代码): 观望 | 评分 65 | 看多
📰 舆情情绪: ...
🚨 风险警报: 
  · 风险点1
  · 风险点2
✨ 利好催化:
  · 利好1
📢 最新动态: ...
```

---

## 三、三方对比矩阵

| 维度 | 我们（stock-robot） | Vibe-Trading | daily_stock_analysis |
|------|-------------------|-------------|---------------------|
| **运行成本** | ¥0 | LLM API费 | LLM API费 |
| **代码量** | 小（~10个脚本） | 大（agent/src/完整架构） | 大（src/ + api/ + 前端） |
| **安装复杂度** | 零依赖 | pip install + API Key | pip + API Key + 通知配置 |
| **市场覆盖** | A股+ETF | 全球（A/港/美/加密/期货/外汇） | A股+港股+美股 |
| **数据源** | 腾讯证券 | 6源自动回退 | 7+源 |
| **AI驱动** | ❌ 纯规则 | ✅ Agent驱动 | ✅ LLM驱动 |
| **Web UI** | ❌ | ✅ React | ✅ React |
| **推送** | 本地文件 | 无（自身是Agent接口） | ✅ 多渠道 |
| **回测** | 简单信号回测 | 7引擎+复合+统计验证 | AI回测验证 |
| **高级技术面** | MACD/KDJ/RSI/MA/BOLL | 缠论/波浪/一目均衡/SMC/谐波 | 缠论/波浪/均线金叉/情绪周期 |
| **稳定性** | ✅ 稳定 | 持续迭代中 | 持续迭代中 |
| **适合场景** | 每日早报+模拟盘 | 复杂策略研究 | 自选股AI分析+推送 |

---

## 四、最终评估

### 结论：不建议替换，建议借鉴

**理由：**
1. 现有系统零成本、零依赖、稳定运行，已满足核心需求（每日早报+模拟盘+回测）
2. Vibe-Trading 和 daily_stock_analysis 都在快速迭代中，生产稳定性不如现有系统
3. 老板偏好：成本敏感、稳定压倒一切

**借鉴优先级：**
1. **大盘复盘模块** — 最直接，1-2个脚本即可
2. **决策评分卡输出** — 改进signal_fusion.py输出格式
3. **缠论/波浪/一目均衡** — Vibe-Trading有完整的开源参考文档
4. **多渠道推送** — 企业微信/飞书推送早报
5. **Vibe-Trading MCP集成** — 按需启用，不默认开启
