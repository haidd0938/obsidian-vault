---
tags:
  - AI工具
  - AI-Agent
  - 评测
created: 2026-05-23
status: 已评
---

# OpenHuman — 开源桌面个人 AI Agent

> **一句话**: TinyHumans 团队开发的桌面 AI Agent，主打"认识你的 AI"——一键 OAuth 集成 118+ 服务 + 本地 Memory Tree + Obsidian 记忆库。
> **结论**: 代码开源 GPL-3.0，但核心功能走托管订阅（$20/月）。老板的 Hermes 系统已覆盖其能力，**不建议替换**。

---

## ⚡ 简介

- **全称**: [tinyhumansai/openhuman](https://github.com/tinyhumansai/openhuman)
- **Star**: 25.9k ⭐ (2026.05.23)
- **状态**: Early Beta，作者标识"Expect rough edges"
- **协议**: GNU GPL-3.0
- **架构**: Rust + Tauri（桌面端）
- **口号**: "Private, Simple and extremely powerful"

---

## 🧠 核心特性

### 1. Memory Tree（记忆树）
- 所有同步数据 → 标准化 ≤3k Token Markdown 块 → 评分/去重 → 分层存入 SQLite
- 同时生成 **Obsidian 兼容的 .md 文件库**
- 宣称支持 **10 亿 Token** 本地存储
- 灵感来自 Karpathy 的 [obsidian-wiki 工作流](https://x.com/karpathy/status/2039805659525644595)

### 2. Auto-Fetch（自动抓取）
- 每 20 分钟自动遍历所有活跃连接，拉取最新数据入记忆
- 无需写 Prompt，无需配置轮询

### 3. 118+ 第三方集成（Composio 层）
- Gmail、GitHub、Slack、Notion、Calendar、Drive、Linear、Jira 等
- 一键 OAuth，无需配 API Key
- OAuth 和集成工具调用走 TinyHumans 托管后端代理
- 也可自备 Composio API Key 直连模式

### 4. TokenJuice 压缩
- HTML→Markdown、URL 缩短、冗余去重
- 宣称降低成本/延迟 **最高 80%**

### 5. 模型路由
- 内置 router provider，自动按任务分配模型（reasoning/fast/vision/summarize/code）
- 默认走 OpenHuman 托管后端（一个订阅包所有模型）
- 可选 Ollama/LM Studio 本地模型

### 6. 桌面 Mascot
- 会说话、能感知环境的虚拟形象
- 口型同步、**可加入 Google Meet 会议**
- 后台持续思考

### 7. 内置工具
- 网页搜索、网页抓取、编程工具集（文件系统/Git/lint/test/grep）
- 浏览器/桌面控制、定时任务、子 Agent 协调
- 原生语音（STT + ElevenLabs TTS）

---

## 💰 商业模式（关键！）

| | 免费版 | 订阅版 |
|---|---|---|
| 模型调用 | ❌ 无 | ✅ 一条订阅包 200+ 模型 |
| 集成 OAuth | ❌ 托管的用不了 | ✅ 走 Composio 代理层 |
| Web Search | ❌ 无 | ✅ 托管代理 |
| Ollama 本地模式 | ✅ **有**（需自己配置） | ✅ |
| **月费** | **0 元** | 约 **$20/月**（未明确定价） |

> **实际体验**: App 免费下，但启动就要 Sign In，不走订阅基本用不了。
> Ollama 本地模式虽然可用，但文档说明"部分实时触发器和托管功能仍需后端"。

---

## 📋 与 Hermes Agent 对比

| 维度 | Hermes Agent | OpenHuman |
|---|---|---|
| **月费** | **0 元**（本地 Ollama + DeepSeek） | $20/月 |
| **Telegram Bot** | ✅ 24/7 | ❌ 仅有桌面端 |
| **小红书 MCP** | ✅ | ❌ |
| **股票监控** | ✅ 自有 cron | ❌ |
| **工程标书** | ✅ 定制 Skill | ❌ 通用 AI |
| **数据隐私** | ✅ 完全本地 | ⚠️ 核心功能走托管后端 |
| **UI 体验** | Web UI + TG | 桌面 Mascot（精致） |
| **稳定性** | ✅ 生产级 | ❌ Early Beta |
| **上手难度** | ⚠️ 终端配置 | ✅ GUI 开箱即用 |
| **集成数量** | 自配 | 118+ 一键 OAuth |

---

## 💡 值得学习的思路

OpenHuman 不适合替换，但有三个设计值得参考：

1. **Memory Tree 的自动构建** — 定期轮询集成 → 压缩 → 分层存储。我们的 TokenJuice Lite + Obsidian 思路接近，但 Auto-Fetch 的自动化程度更高
2. **TokenJuice 压缩策略** — 在数据进 LLM 前做 HTML→MD 转换、URL 缩短、去重。我们的文件交付工作流可以借鉴
3. **模型路由（hint 机制）** — 用 hint:reasoning/fast/vision 前缀自动选模型。Hermes 的 model routing 方向一致

---

## 🔗 链接

- GitHub: https://github.com/tinyhumansai/openhuman
- 官网: https://tinyhumans.ai/openhuman
- 文档: https://tinyhumans.gitbook.io/openhuman
- Discord: https://discord.tinyhumans.ai
- Reddit: https://www.reddit.com/r/tinyhumansai/
