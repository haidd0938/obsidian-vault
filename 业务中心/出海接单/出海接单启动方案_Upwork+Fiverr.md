# 出海接单启动方案：Upwork + Fiverr

> 创建时间：2026-05-17
> 卖点：Hermes Agent 部署 / MCP 集成 / Ollama 运维 / AI 工作流自动化

---

## 总体思路

```
Week 1 搭建 Profile → Week 2 投递 Proposal → Week 3 出首单 → 之后稳定复利
```

**先Upwork后Fiverr。** Upwork是竞标制，主动出击，单价比Fiverr高一个量级。Fiverr是一口价等人上门，被动收入，两不冲突。

---

# 第一部分：Upwork Profile

## 注册 & 创建 Profile

1. **去 upwork.com 注册账号** — 选"Freelancer（自由职业者）"类型
2. 从 `https://www.upwork.com/nx/create-profile/title` 开始填

---

## Professional Title（职业标题）

> 直接影响搜索排名，买家第一眼看到

```
AI Agent & Automation Specialist — Hermes Agent, MCP, Ollama, AI Workflow
```

## Category（分类）

| 层级 | 选择 |
|------|------|
| Category（大类） | Web, Mobile & Software Dev |
| Subcategory（子类） | AI & ML（最重要） |

## Skills（技能标签）

一个个搜索添加，**最少10个**才能下一步：

### 必加10个：
1. AI Agent Development
2. Automation
3. Large Language Model (LLM) Integration
4. Ollama
5. Python
6. Telegram Bot Development
7. Linux Server Administration
8. API Integration
9. Docker
10. OpenAI API

### 再加这些（加分项）：
11. MCP (Model Context Protocol)
12. AI Workflow Automation
13. Hermes Agent
14. Webhook & Cron Job Configuration
15. Git
16. TypeScript
17. Node.js

## Overview（Profile简介——买家看到的第一个段落）

粘贴以下全文：

> **I build and deploy private AI assistants that work for you — not for OpenAI's server.**
>
> Instead of paying $20-200/month for ChatGPT Pro or dealing with API limits, I set up **your own AI agent** that runs on your hardware (Mac, Linux server, VPS, or cloud). Fully private. Fully customizable. No recurring subscription fees — just the model API costs you choose.
>
> **What I build:**
>
> 🔹 **Hermes Agent** — an autonomous AI agent by Nous Research with persistent memory, 70+ built-in tools, and a learning loop that gets smarter over time. Install it with one command, then talk to it from Telegram, Discord, WhatsApp, iMessage, Slack, or Web UI.
>
> 🔹 **MCP Server Integration** — connect your AI agent to your real tools: Gmail, Google Calendar, Notion, GitHub, databases, internal APIs, you name it. Your agent reads and writes to your systems, not just a chat window.
>
> 🔹 **Ollama Local LLM** — run models entirely offline on your own hardware. No data leaves your machine. Perfect for sensitive environments, compliance requirements, or anyone who wants zero dependency on third-party APIs.
>
> 🔹 **Automation Workflows** — cron jobs, webhook triggers, scheduled data monitoring, auto-reporting. Your agent works while you sleep and delivers results to your Telegram/Slack in the morning.
>
> **Why work with me:**
>
> I don't just copy-paste from tutorials. I've built and operated a full Hermes Agent system end-to-end — from bare-metal installation to multi-platform messaging to custom MCP servers. You get someone who understands the architecture, not someone who follows a README.
>
> **What you need to provide:** a Mac, Linux server, or VPS (I'll guide you through the minimal requirements).
>
> **Starting at $150 | Delivered in 24-48 hours**

## Rate（时薪）

- **初期（前5单积累评价）**：$30-40/h
- **之后提价**：$50-75/h

注意：Upwork平台抽成20%，到手为报价的80%
- 前$500收入抽20%
- $500-$10,000抽10%
- 超$10,000以后抽5%

## Portfolio（作品集）

> 至少放1个作品，强烈建议放表格+录屏

**作品1标题：** Private AI Assistant with Telegram + MCP

**说明文字：**
> Full Hermes Agent deployment with Telegram messaging gateway, MCP integration for Gmail and Notion, and daily cron reports. The agent remembers past conversations, runs code, browses the web, and checks emails on command.

**需要准备的材料：**
- [ ] Hermes Web UI 截图一张（localhost:8648）
- [ ] 30秒录屏：对着Web UI说"帮我看看今天的日程"之类

## Education / Employment

- 不强制填，空着也行
- 如果有相关工作经验就简单写一条

## Languages

- Chinese: Native
- English: 能写就行，填 Conversational 或 Intermediate

## Location

- China

---

# 第二部分：Fiverr Gig

## 注册

1. 去 fiverr.com 注册账号
2. 选"Become a Seller（成为卖家）"

## Gig 标题

```
I will deploy your private AI assistant with Hermes Agent in 24 hours
```

## Gig 描述（完整全文）

> **Stop paying monthly fees for AI you don't own.**
>
> I'll deploy **Hermes Agent** — the open-source autonomous AI agent by Nous Research — on your server or Mac. In 24 hours, you'll have your own personal AI that talks to **Telegram, Discord, iMessage, Slack, or Web UI**.
>
> **What your AI can do:**
> ✅ Long-term memory — remembers everything you tell it, session to session
> ✅ Browse the web and fetch real-time information
> ✅ Run code, read/write files, execute shell commands
> ✅ Integrate with your tools via MCP (Gmail, Notion, GitHub, calendars, databases)
> ✅ Automate daily reports, data monitoring, webhook-triggered tasks
> ✅ Fully private — runs on your hardware, your data never leaves
>
> **What you get:**
> - Full Hermes Agent installation and configuration
> - One messaging platform connected (Telegram, Web, or Discord — pick one)
> - Basic memory and tool setup
> - Handoff documentation so you can maintain it yourself
> - 7-day support for any setup issues
>
> **What I need from you:**
> - A Mac, Linux server, or any VPS with internet access
> - An API key from OpenAI, Anthropic, or DeepSeek (I'll help you pick the right one for your needs)
> - 30 minutes of your time for handoff
>
> **Why me?**
> I've deployed Hermes Agent from scratch — config, memory, MCP, cron, multi-platform messaging, troubleshooting. I know where things break and how to fix them. You're not getting a theoretical setup; you're getting a system that actually works.

## 定价包（3档）

| 套餐 | 价格 | 内容 |
|------|------|------|
| **Basic** | $100 | 单平台（Telegram或Web），基础记忆+工具，24h交付 |
| **Standard** | $180 | 2个MCP集成，双平台接入 |
| **Premium** | $300 | 完整方案：多平台+4个MCP+自定义cron+自动化 |

## Gig Extras（附加服务）

| 附加项 | 价格 |
|--------|------|
| Additional MCP integration（每多一个工具） | $50 |
| Additional messaging platform（多加一个平台） | $40 |
| Custom cron job / daily report setup | $30 |
| Telegram bot custom commands | $30 |
| Priority support（48h响应） | $20 |

## Gig FAQ

| 问题 | 回答 |
|------|------|
| Do I need a powerful computer? | No. A basic VPS ($5-10/month) or any Mac/Linux machine works. The heavy lifting is done by the LLM API, not your hardware. |
| Can I use free/cheap models? | Yes. I can configure DeepSeek or local Ollama models to keep costs minimal. |
| Does this replace ChatGPT? | Yes and more. Your AI agent has memory, tools, and automation — things ChatGPT doesn't do. |
| What if something breaks after setup? | I provide 7 days of support for all setup-related issues. |

---

# 第三部分：Upwork Proposal 投递策略

## 搜索关键词

在Upwork上搜这些关键词的职位：
- "AI automation developer"
- "LLM integration"
- "private AI assistant"
- "ChatGPT alternative self-hosted"
- "Ollama setup"
- "MCP server"
- "AI agent deployment"

## Proposal 模板

**投递时直接复制修改：**

> Hi [name],
>
> I read your post — you need a private AI assistant that talks to your tools. I do exactly this.
>
> I've built and deployed Hermes Agent (an open-source AI assistant framework) with MCP server integration. In plain English: I can set up an AI that reads your emails, checks your calendar, and runs on your own hardware — no monthly fees, no privacy concerns.
>
> Here's what I can deliver:
> • Full Hermes Agent deployment with memory and tools
> • MCP integration for your existing tools (Gmail, Notion, GitHub, etc.)
> • Telegram/Web/iMessage access
> • Fully documented handoff so you can maintain it yourself
>
> Starting at $150, delivered in 48 hours.
>
> Let me know if you want to see a demo.
>
> Best,
> [你的名字]

**关键规则：**
- 每天投3-5个Proposal
- 3段以内，别写长
- 第一句让人知道你在说什么
- 第二句证明你会做
- 第三句给价格+时间

---

# 第四部分：需要提前准备的材料

- [ ] Upwork账号注册完成
- [ ] Fiverr账号注册完成
- [ ] Hermes Web UI 截图（放在Portfolio/作品集）
- [ ] 30秒演示录屏（可选，有更好）
- [ ] 定价策略熟悉

---

# 第五部分：时间线预期

| 阶段 | 时间 | 行动 |
|------|------|------|
| 搭建期 | Day 1 | 注册Upwork + 填Profile（~30min） |
| 搭建期 | Day 1-2 | 注册Fiverr + 创建Gig（~20min） |
| 投递期 | Day 1-14 | 每天投3-5个Upwork Proposal（~15min/天） |
| 首单 | Week 1-2 | 通常投20-30个Proposal出首单 |
| 稳定期 | Month 2+ | 积累5单好评后提价，月收入$500-2000+ |

---

# 第六部分：成功率分析

| 路径 | 启动成本 | 出单周期 | 月收入预期 | 风险 |
|------|---------|---------|-----------|------|
| **Upwork（优先）** | 1h Profile + 每天30min投递 | 1-2周 | $500-2000/月 | 前期投递期可能没反馈 |
| **Fiverr（同步）** | 1h搭Gig | 被动等单，1-3周 | $200-800/月 | 卷，靠评价积累 |

---

*文件保存于：2026-05-17*
*找贾维斯讲解操作即可开始执行*
