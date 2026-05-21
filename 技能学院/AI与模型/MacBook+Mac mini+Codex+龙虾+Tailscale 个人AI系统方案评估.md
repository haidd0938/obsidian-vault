---
tags: [AI系统, 架构评估, 硬件方案, Tailscale]
来源: https://x.com/XChatScout/status/2056622783761899644
日期: 2026-05-19
状态: 已评估
---

# MacBook + Mac mini + Codex + 龙虾 + Tailscale 个人AI系统方案评估

## ⚡ 简介

来自 XChatScout 分享的一套个人AI系统搭建方案，核心思路是：**多设备分工协作，各尽其能组成有机整体**。

> 原帖：317👍 / 70🔄 / 50💬
> 标题：*个人专属超级AI系统搭建教程：MacBook + Mac mini + Codex + 龙虾 + Tailscale = 个人专属超级 AI 系统*

## 📋 方案架构

| 组件 | 角色 |
|------|------|
| **MacBook** | 日常使用的笔记本，作为客户端入口 |
| **Mac mini** | 专用 AI 服务器，7×24 运行 |
| **Codex** | OpenAI 编码代理（类似 Claude Code），处理编码任务 |
| **龙虾** | 可能是 Lobster 或某个中文昵称的本地 AI 工具/框架 |
| **Tailscale** | 组网方案，将 MacBook 和 Mac mini 连到一个虚拟局域网 |

## 💡 与现有方案（Hermes Agent）对比

| 维度 | 此方案 | 我的方案 |
|------|--------|---------|
| **AI 服务器** | Mac mini 专用机 | Intel MacBook（单机） |
| **编码代理** | Codex | Hermes Agent + Skill 体系 |
| **组网** | Tailscale（跨设备） | Hermes Gateway（本地） |
| **模型来源** | 未明确（可能是本地+API混合） | Ollama 本地 + DeepSeek API |
| **客户端** | MacBook | MacBook（与服务器同机） |

### ✅ 可借鉴的点

1. **Mac mini 作为专用 AI 服务器** — 如果未来有常驻 7×24 服务需求，M4 Mac mini 跑本地模型比 Intel MacBook 快 5-10 倍
2. **Tailscale 组网** — 如果未来有多设备协同需求，Tailscale 是最简单的方案
3. **多设备分工的架构思路** — 各司其职，服务器做服务器的事，客户端做客户端的事

### ❌ 对我价值有限的原因

1. **已经在用 DeepSeek API** — 云端大模型效果远超本地小模型，且成本极低
2. **Codex 不优于 Hermes Agent** — 能力在同一水平线
3. **Intel Mac 才是瓶颈** — 与其加一台 Mac mini 去组网，不如直接换一台 M 系列 Mac

### 🔑 核心结论

这个方案的价值在于**架构思路的启发**（多设备分工），但就我的实际场景而言：

> **目前 Hermes + DeepSeek API 的组合已经够用。** 最需要解决的不是加设备，而是把 Intel Mac 换成 M 系列。

### 🔗 相关链接

- [[Tailscale异地共享OpenWebUI实施方案]] — 此前对 Tailscale 的研究
- [[Hermes系统/Windows-Hermes安装指南]] — 现有 Hermes 部署方案

---

## 📝 后续可能用到的场景

- 如果要搞云上 AI 服务器（比如租一台云主机跑 Hermes），可以参考 Tailscale 组网
- 如果要给二弟（联想电脑）赋能，也可以用 Tailscale 打通
- 如果后面真要买 Mac mini，这个架构可以拿来做 baseline 参考
