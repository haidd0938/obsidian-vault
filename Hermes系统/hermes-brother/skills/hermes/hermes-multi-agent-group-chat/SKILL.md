---
name: hermes-multi-agent-group-chat
description: 创建多个Hermes Agent Profile，绑定不同的Telegram Bot Token，加入同一个TG群组，实现多Agent群聊协作（写代码→审阅、规划→执行等流水线）
version: 1.0
author: Hermes Agent
tags: [hermes, profiles, telegram, multi-agent, group-chat, collaborative]
---

# Hermes 多Agent群聊

## 原理

这不是一个内置的"群聊聊天室"功能，而是利用 **Hermes Profiles（多实例）** + **Telegram群组@提及机制** 的组合玩法：

1. 每个 Profile 是一个完全独立的 Hermes Agent 实例（独立配置、独立API密钥、独立记忆/人格/技能）
2. 每个 Profile 绑定一个独立的 Telegram Bot
3. 多个 Bot 加入同一个 Telegram 群组
4. 用户在群里 `@BotA`  @BotB` 进行路由
5. Bot之间也能互相`@`进行协作（如写完代码@审阅Bot）

## 前置条件

- Hermes Agent 已安装并正常运行
- 有可以创建 Telegram Bot 的账号
- Telegram Gateway 已经配置好并能正常工作

## 操作步骤

### 1. 创建 Profiles

每个 Profile 对应一个独立 Agent：

```bash
# 基于当前配置克隆（复制config.yaml、.env、SOUL.md）
hermes profile create coder --clone
hermes profile create reviewer --clone

# 或从头创建（空白配置）
hermes profile create assistant
```

### 2. 配置每个 Profile

```bash
# 配置 coder profile
coder setup                   # 配置API密钥、模型等
# 编辑其人格文件
vim ~/.hermes/profiles/coder/SOUL.md

# 配置 reviewer profile
reviewer setup
vim ~/.hermes/profiles/reviewer/SOUL.md
```

关键配置项：
- **SOUL.md** — 定义Agent人格/角色（直接影响行为风格）
- `.env` — 各Profile可以用不同的API Key或Provider
- `config.yaml` — 可以设置不同的模型（coder用claude写代码，reviewer用gpt-4o审阅）

### 3. 为每个 Profile 绑定不同的 Telegram Bot Token

在 Telegram 中通过 [@BotFather](https://t.me/BotFather) 创建多个 Bot，获得各自的 Token。

为每个 Profile 配置不同的 Bot Token：

```bash
# 编辑 coder 的 Gateway 配置
vim ~/.hermes/profiles/coder/.env
# 添加: TELEGRAM_BOT_TOKEN=xxx:BotA_Token

# 编辑 reviewer 的 Gateway 配置
vim ~/.hermes/profiles/reviewer/.env
# 添加: TELEGRAM_BOT_TOKEN=xxx:BotB_Token
```

### 4. 启动 Gateway

分别启动每个 Profile 的 Gateway 服务：

```bash
# 前台启动
coder gateway run
reviewer gateway run

# 或作为后台服务安装
coder gateway install
reviewer gateway install
coder gateway start
reviewer gateway start
```

### 5. 将 Bot 加入同一群组

- 在 Telegram 中创建一个群组
- 将所有 Bot（通过 @BotFather 创建的）加入该群组
- 给 Bot 管理员权限确保能读消息

### 6. 使用

```
用户在群里发消息：
  @coderBot  帮我写一个Python斐波那契函数
  @reviewerBot 帮我审阅一下上面的代码

Bot之间协作：
  @coderBot 写完代码后自动 @reviewerBot 触发审阅
```

## 进阶玩法

### 不同Model各司其职

可以为不同 Profile 设置不同模型以优化成本和效果：

```yaml
# coder/config.yaml
model:
  provider: anthropic
  default: claude-sonnet-4-20250514

# reviewer/config.yaml
model:
  provider: openrouter
  default: openai/gpt-4o
```

### 技能隔离

不同 Profile 加载不同的 Skill 集：

```bash
# coder 加载编码相关技能
hermes -p coder -s plan,test-driven-development,writing-plans chat

# reviewer 加载代码审查技能
hermes -p reviewer -s requesting-code-review chat
```

### 多角色编排

不止两种角色，可以创建更多：

| Profile | 角色 | 用途 |
|---------|------|------|
| `planner` | 架构师 | 设计方案、写计划 |
| `coder` | 开发者 | 写代码实现 |
| `reviewer` | 审阅者 | Code Review |
| `tester` | 测试员 | 写测试、跑测试 |
| `writer` | 文档撰写 | 写README/文档 |

### Honcho 记忆隔离

启用 Honcho 后，每个 Profile 有自己的独立记忆空间：

```yaml
memory:
  memory_enabled: true
  provider: honcho
```

## 注意事项

- **Token 去重保护**：Hermes 会在启动 Gateway 时检测 Token 冲突（同一 Token 不能给两个Profile用），报错信息清晰
- **资源开销**：每个 Profile 的 Gateway 是一个独立进程，多个 Gateway 同时运行会消耗更多内存
- **群组 @mention 策略**：单个 Hermes Agent 在群组中默认需要被 @ 才会回复（防止所有Bot抢答）
- **群组会话隔离**：每个用户在同一群组中拥有独立会话，避免上下文混淆
- **Profile 命令行快捷键**：`hermes profile create coder` 后自动生成 `coder chat`、`coder setup` 等命令

## 排错

| 问题 | 原因 | 解决 |
|------|------|------|
| Gateway 启动报 Token 冲突 | 两个 Profile 用了同一 Token | `hermes profile list` 检查 → 改.env |
| Bot 在群里不回复 | 没被 @ 提及 | 确认群组 @mention 策略配置正确 |
| Profile 无法启动 | 配置不完整 | `coder doctor --fix` |
| 想换模型但只影响一个 Profile | 改错了 Profile 的配置 | 确认改的是 `~/.hermes/profiles/<name>/config.yaml` |
