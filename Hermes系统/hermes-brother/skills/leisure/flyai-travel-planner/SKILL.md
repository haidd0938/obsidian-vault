---
name: flyai-travel-planner
description: AI旅行规划 — 飞猪FlyAI搜索技能 + 路线图生成提示词。搜机票/酒店/火车/景点门票，搭配ChatGPT生成徒步/自驾路线图。
category: leisure
version: 1.0
created: 2026-05-08
---

# ✈️ FlyAI 旅行规划技能

飞猪开源AI旅行规划能力 + 免费路线图生成，用于AI代理一站式旅行规划。

## 概述

| 项目 | 链接 | 说明 |
|------|------|------|
| **FlyAI Skill** | https://github.com/alibaba-flyai/flyai-skill | 飞猪开源AI Agent Skill，624⭐，MIT |
| **徒步路线图提示词** | https://x.com/Saccc_c/status/2049419422385799281 | 生成徒步旅行路线图 |
| **自驾游路线图提示词** | https://x.com/TanLuAI/status/2049719336743600358 | 生成自驾游旅行路线图 |

## FlyAI 核心功能

### 安装

```bash
# OpenClaw — 通过clawhub (推荐)
clawhub install flyai

# 或 via npx
npx skills add alibaba-flyai/flyai-skill

# Claude Code
cp -r /path/to/flyai-skill/skills/flyai ~/.claude/skills/flyai
```

### CLI 安装（Hermes 场景）

```bash
npm i -g @fly-ai/flyai-cli
```

### 验证

```bash
flyai keyword-search --query "things to do in Tokyo"
```

### 可选配置

```bash
flyai config set FLYAI_API_KEY "your-key"
```

## 8 个搜索命令

| 命令 | 用途 | 必填参数 |
|------|------|----------|
| `keyword-search` | 全品类自然语言搜索 | `--query` |
| `ai-search` | **语义搜索** — 理解复杂意图，精准推荐 | `--query` |
| `search-flight` | 结构化航班搜索 | `--origin` |
| `search-train` | 结构化火车票搜索 | `--origin` |
| `search-hotel` | 结构化酒店搜索 | `--dest-name` |
| `search-poi` | 景点/POI搜索 | `--city-name` |
| `search-marriott-hotel` | 万豪酒店搜索 | `--dest-name` |
| `search-marriott-package` | 万豪套餐搜索 | `--keyword` |

### 常用示例

**AI智慧搜索（最推荐）** — 一句话规划行程：
```bash
flyai ai-search --query "从广州到杭州3天游，住西湖附近，最省钱版"
```

**查航班**：
```bash
flyai search-flight --origin "北京" --destination "上海" --dep-date 2026-05-20 --sort-type 3
```

**查高铁**：
```bash
flyai search-train --origin "上海" --destination "杭州" --dep-date 2026-05-20 --journey-type 1
```

**查酒店**：
```bash
flyai search-hotel --dest-name "杭州" --poi-name "西湖" --check-in-date 2026-05-20 --check-out-date 2026-05-22
```

**查景点**：
```bash
flyai search-poi --city-name "桂林" --category "自然风光" --poi-level 5
```

## 路线图生成提示词

### 徒步路线图 (@Saccc_c)
用 ChatGPT + 提示词生成漂亮徒步路线图。原始推文：https://x.com/Saccc_c/status/2049419422385799281

### 自驾游路线图 (@TanLuAI)
用 ChatGPT + 提示词生成自驾游路线图。原始推文：https://x.com/TanLuAI/status/2049719336743600358

> 💡 **使用方式**：在ChatGPT中粘贴对应提示词，输入你的目的地和天数，AI自动生成可视化路线图。

## Hermes 集成方式

当老板需要规划旅行时：

1. **方案一** — 用 FlyAI CLI 查实时数据（机票/酒店/门票价格）
   ```bash
   flyai ai-search --query "用户的需求描述"
   ```

2. **方案二** — 用 ChatGPT + 提示词生成路线图
   - 徒步/自驾需求 → 提供对应提示词
   - 让老板在 ChatGPT 里运行

## 覆盖的旅行场景

| 类别 | 包含 |
|------|------|
| 🚗 交通 | 机票、火车票、机场接送、租车、包车 |
| 🏨 住宿 | 酒店、民宿、客栈、机酒套餐 |
| 🎯 体验 | 景点门票、一日游、跟团游、定制游 |
| 🎪 活动 | 演唱会、体育赛事、演出、动漫展 |
| 📄 服务 | 签证、旅行保险、SIM卡、WiFi租赁 |
| 🚢 行程 | 邮轮、周末游、蜜月、家庭游、研学游 |

## 注意事项

- 需要 Node.js 环境（CLI 依赖 npm）
- 搜索结果含直接预订链接
- 不需要 API Key 即可使用，可选配置增强版
- 数据源为飞猪（阿里巴巴旗下），国内旅行数据最全
- 路线图提示词需在 ChatGPT 中运行，非 CLI 工具
