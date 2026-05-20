---
name: xinqiuhui-7agent
description: 鑫球汇台球俱乐部7-Agent自动化系统 — 扫大众点评差评球房 → 运营诊断 → 出改善方案。Agent1 Scout侦察→Agent2 Diagnoser诊断→Agent3 Builder方案。后续扩展：Agent4 Filmer(案例视频)→Agent5 Pitcher(触达话术)→Agent6 Checker(质检验证)→Agent7 Mobile(推送触达)
---

# 鑫球汇 7-Agent 自动化系统

## 触发条件
老板说要"搞7-Agent"、"扫点评"、"差评球房"、"触达"等。

## 架构概览

```
┌──────────┐   ┌───────────┐   ┌──────────┐
│ Agent1   │ → │ Agent2    │ → │ Agent3   │ → 后续延伸
│ Scout    │   │ Diagnoser │   │ Builder  │
│ (侦察)   │   │ (诊断)    │   │ (方案)    │
└──────────┘   └───────────┘   └──────────┘
```

## 目录结构

全部脚本在 `~/.hermes/scripts/xinqiuhui-7agent/`

| 文件 | 用途 |
|------|------|
| `AGENT1_scout.py` | 侦察：差评数据采集（样例数据+百度地图API接口预留） |
| `AGENT2_diagnoser.py` | 诊断：问题归类+根因分析+改善建议 |
| `AGENT3_builder.py` | 方案：改善项清单+时间线+预算 |
| `agent_orchestrator.py` | 调度器：一键运行全流程 |

## 使用方法

### 一键运行（推荐）
```bash
# 全流程（Agent1~7，所有球房）
cd ~/.hermes/scripts/xinqiuhui-7agent && python3 agent_orchestrator.py --city "天水" --use-sample --run-all

# 快速演示模式（只处理前3家球房）
cd ~/.hermes/scripts/xinqiuhui-7agent && python3 agent_orchestrator.py --city "天水" --use-sample --run-all --limit 3
```

### 可选参数
- `--city "兰州"` — 指定目标城市
- `--use-sample` — 使用样例数据（演示模式，推荐）
- `--run-all` — 从Scout到Builder全流程
- `--step 1` — 只跑某一步（1=Scout, 2=Diagnoser, 3=Builder）

### 分步执行
```bash
# Step1: 侦察
python3 AGENT1_scout.py --city "天水"

# Step2: 诊断
python3 AGENT2_diagnoser.py --input /Users/mac/Desktop/鑫球汇7Agent/scout_天水.json

# Step3: 方案
python3 AGENT3_builder.py --input /Users/mac/Desktop/鑫球汇7Agent/scout_天水_诊断报告.md
```

## 产出物

全部输出到 `~/Desktop/鑫球汇7Agent/`

| 文件 | 格式 | 说明 |
|------|:---:|------|
| `scout_{城市}.json` | JSON | Scout侦察原始数据 |
| `scout_{城市}_诊断报告.md` | Markdown | 诊断报告（含问题排名+根因+建议） |
| `scout_{城市}_改善方案.md` | Markdown | 改善方案（含P0/P1/P2优先级+预算） |
| `{城市}_执行报告.md` | Markdown | 全流程执行摘要 |

## 样例数据说明

Scout内置了天水市3家球房的样例数据（模拟大众点评差评），包含：
- XX台球俱乐部（秦州店）— 评分3.2，差评3条
- XX台球吧（麦积店）— 评分3.5，差评2条
- XX桌球会所 — 评分2.8，差评4条（紧急优先级）

实际部署时需替换为真实数据源（百度地图POI + 大众点评爬虫 或 第三方聚合API）。

## 后续扩展计划

## 后续扩展计划

| Agent | 功能 | 状态 | 产出 |
|:---:|------|:---:|------|
| Agent4 Filmer 🎬 | 诊断报告→短视频脚本（P0优先拍） | ✅ **已完成** | `{城市}_视频脚本.md` |
| Agent5 Pitcher 🗣️ | 差评→触达话术（阴阳怪气友好版） | ✅ **已完成** | `{城市}_触达话术.md` |
| Agent6 Checker 🔍 | 质检验证视频脚本+话术质量 | ✅ **已完成** | `{城市}_质检报告.md` |
| Agent7 Mobile 📱 | 推送配置（渠道入口+配置建议） | ✅ **已完成** | `{城市}_推送配置.md` |

## 已完成扩展：Agent4~7 详情

Agent4~7 全部在 `~/.hermes/scripts/xinqiuhui-7agent/` 目录下：

| 文件 | 功能 |
|------|------|
| `agent4_filmer.py` | 读取Agent3改善方案 → 按P0优先级生成6段式TikTok/抖音短视频脚本（文案+配图描述+时长） |
| `agent5_pitcher.py` | 读取Scout原始差评数据 → 生成差异化触达话术（短信/微信/电话三种渠道） |
| `agent6_checker.py` | 读取Agent4+Agent5产出 → 质量检查+评分（脚本吸引力/逻辑性/可行性，话术亲和力/针对性/行动号召力） |
| `agent7_mobile.py` | 读取Agent6质检通过 → 输出推送配置方案（含渠道选择建议+调度时间+提醒内容） |

集成到Orchestrator（`agent_orchestrator.py`），支持：
- `--run-all` 跑Agent1~7全流程
- `--step 4` / `--step 5` / `--step 6` / `--step 7` 分步执行
- `--limit N` 限制处理的球房数量（快速演示模式）

**Agent4-7的输入输出链：**
```
Agent4(self, improvement_report_path) → {城市}_视频脚本.md
Agent5(self, raw_reviews_path) → {城市}_触达话术.md
Agent6(self, video_script_path, outreach_path) → {城市}_质检报告.md
Agent7(self, quality_report_path) → {城市}_推送配置.md
```

### Agent4 Filmer 视频脚本格式
每段脚本包含：场景编号 → 视觉描述 → 文案 → 配音建议 → 预计时长
按Agent3的P0/P1/P2优先级排序，P0任务优先出脚本

### Agent5 Pitcher 触达话术
每套话术包含：球房名称 → 差评摘要 → 触达话术（短信用/微信用/电话用三个版本） → 建议触达时机
用语风格：友好但直击痛点，不贬低对方，提供"免费诊断报告"作为价值钩子

### Agent6 Checker 质检标准
- 视频脚本：吸引力(0-5) + 逻辑性(0-5) + 可行性(0-5) + 满分15 → ≥12合格
- 触达话术：亲和力(0-5) + 针对性(0-5) + 行动号召力(0-5) + 满分15 → ≥12合格
- 质检报告含不合格项的具体修改建议

### Agent7 Mobile 推送配置（预留入口）
当前输出推送配置方案（含渠道选择、调度时间、提醒内容），实际推送待用户确认渠道后接入。

## ⚠️ 已知问题
- Scout目前使用样例数据演示，实际点评数据需接入爬虫或API
- Builder的`action_items`按固定的问题类型分配，未根据实际差评原文动态生成
- Diagnoser的根因分析基于规则判断，未使用LLM分析差评语义
- Agent7当前为配置输出模式，实际推送（微信/短信/电话）需用户确认具体服务端接口后接入

### 已修复Bug记录

1. **`--use-sample` 参数逻辑取反** — `agent_orchestrator.py` 中 `use_sample=True` 时加了 `--no-sample` 参数（第39行），导致样例模式与非样例模式完全互换。修复：改为 `if not use_sample: cmd.append("--no-sample")`。

2. **Builder 从 JSON 数据解析球房列表失败** — 当诊断报告文件先被 `json.load()` 尝试解析（预期JSON格式），但实际文件是Markdown时抛异常。修复：Agent4的读取逻辑改用 `with open()...read()` 原始字符串接受，外部调用时传文件路径而非解析后的对象。

3. **DeepSeek API Key 过期导致诊断重复失败** — 这是外部依赖问题，不影响本系统代码逻辑。
