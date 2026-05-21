---
created: 2026-05-22T11:00:00+08:00
tags:
  - AI工具
  - 编码代理
  - DeepSeek
  - 终端工具
source: https://github.com/Hmbown/DeepSeek-TUI
status: 已安装
---

# DeepSeek-TUI 编码代理

> 终端编码代理，专为 DeepSeek V4 打造。与 Hermes Agent 互补使用。

## 基本信息

| 项目 | 内容 |
|------|------|
| ⭐ 仓库 | Hmbown/DeepSeek-TUI — 33k stars |
| 💻 语言 | Rust（编译二进制） |
| 📜 协议 | MIT |
| 📦 安装路径 | `/usr/local/bin/deepseek` + `/usr/local/bin/deepseek-tui` |
| 🔖 版本 | v0.8.40 |

## 安装记录

- **日期**：2026-05-22
- **方式**：从 GitHub Releases 下载 x86_64-macos 二进制
- **API 配置**：走本地 one-api（`http://127.0.0.1:3010/v1`）
  - 模型：`deepseek-v4-pro`（Auto 模式自动降级为 `deepseek-v4-flash`）
- **Skills 目录**：`~/.deepseek/skills/`
- **配置文件**：`~/.deepseek/config.toml`
- **钥匙串**：API Key 已保存到 macOS 钥匙串

## 核心功能

- **Auto 模式**：自动判断任务复杂度，简单问答走 Flash（省钱），复杂编码走 Pro + 深度思考
- **Prefix-cache 优化**：缓存命中时成本极低（$0.0036/1M，比 miss 便宜 100 倍）
- **原生 1M Token 上下文**：专为 DeepSeek V4 优化
- **实时成本追踪**：可切换人民币显示
- **三种模式**：Plan（只读）/ Agent（审批）/ YOLO（全自动执行）
- **天赋系统（Skills）**：兼容 Claude/Cursor/OpenCode 的 SKILL.md
- **多 Provider 支持**：OpenRouter / Ollama / OpenAI 兼容 API
- **MCP 支持**：兼容 Model Context Protocol
- **沙箱保护**：macOS Seatbelt 沙箱隔离

## 与 Hermes Agent 的分工

| 场景 | 用谁 |
|------|------|
| Telegram 聊天、股票监控、定时任务、日常管理 | **Hermes Agent** |
| 复杂编码、代码审查、项目开发 | **DeepSeek-TUI** |

## 使用方法

### 基本命令

```bash
# 1️⃣ 交互式 TUI 模式（推荐！最常用）
deepseek-tui

# 2️⃣ 快速问答（非交互，适合一次性的问题）
deepseek-tui exec -p "你的问题"

# 3️⃣ 命令行快速问答（和上面等效）
deepseek -p "写一个 Python 斐波那契生成器"

# 4️⃣ 审查当前 git diff（未提交代码）
deepseek-tui review

# 5️⃣ YOLO 模式（全自动执行，慎用！）
deepseek-tui -y "给项目加个 README.md"
```

### 模式选择

| 模式 | 命令 | 描述 |
|------|------|------|
| Plan | `deepseek-tui --plan` | 只读模式，只看代码不动手 |
| Agent | `deepseek-tui`（默认） | 每次操作前向你确认 |
| YOLO | `deepseek-tui -y` | 全自动，直接执行不确认 |

### 编码工作流示例

```bash
# 1. 进入项目目录
cd ~/my-project

# 2. 启动 TUI 会话
deepseek-tui

# 3. 在 TUI 中对话，例如：
#    "重构这个模块，提取公共逻辑"
#    "给这段代码加单元测试"
#    "review 当前分支的改动"

# 4. 快速完成小任务
deepseek -p "给这个 Python 脚本加 argparse 参数"
```

### 成本优化技巧

由于 DeepSeek V4 Pro 的 75% 折扣到 2026-05-31 到期，建议：

- **日常简单问题**：直接走 Hermes（调 DeepSeek API，和 TUI 同价）
- **编码任务**：用 DeepSeek-TUI 的 Auto 模式，自动选最经济的模型
- **长对话**：利用 prefix-cache 省钱，避免频繁开启新会话
- **费用跟踪**：在 one-api 日志查看详细消费记录

## 注意事项

- 所有外网请求走本地 one-api（`localhost:3010`），和 Hermes 共享出口
- 终端 TUI，不是 Web UI，需要开终端窗口使用
- 编码任务更适合它，日常对话/监控等用 Hermes
- 如果遇到沙箱限制，可关闭沙箱运行（不推荐）

## 相关链接

- [GitHub 仓库](https://github.com/Hmbown/DeepSeek-TUI)
- [官方文档](https://deepseek-tui.dev)
- [[OneAPI-完整配置文档]]
- [[Hermes Agent本机配置]]
