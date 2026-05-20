# Skills Hub 使用指南

> 来源: https://hermes-agent.nousresearch.com/docs/skills
> 本地镜像: /Users/mac/Documents/hermes-skills-hub-reference.md
> 保存时间: 2026-05-06

## 概况

| 指标 | 数量 |
|------|------|
| 总技能数 | **673** |
| Built-in (内置) | **89** |
| Optional (可选) | **63** |
| Community (社区) | **521** |
| Categories (分类) | **17** |
| Registries | 4 (Built-in, Optional, Anthropic, LobeHub) |

## 用户偏好

老板要求：**有需求直接检索安装**。这意味着：
1. 用户提到某个功能/需求时，优先去 Skills Hub 搜索是否有现成技能可用
2. 不要只依赖本地已有的技能列表
3. 找到后通过 `hermes skills install <名称>` 安装

## 搜索方法

### 方法 1: Web 搜索（推荐，因为Hub页面是动态加载的）
搜索页面上显示的所有技能名和描述。关键词搜索技能名称或描述文字。

### 方法 2: CLI 搜索
```bash
hermes skills search <query>
hermes skills browse
```

### 方法 3: 本地镜像参考
直接查看 `/Users/mac/Documents/hermes-skills-hub-reference.md`（仅含 Built-in 技能）

## 安装命令

### 官方/内置技能
```bash
hermes skills install <name>
```

ID 可以是 Hub 标识符，也可以是直接的 SKILL.md URL。如果 frontmatter 没有 name 字段，需要 `--name` 覆盖。

### 社区技能 (LobeHub 手动安装)
当 `hermes skills install` 找不到或报错时，可以手动安装社区技能包：

```bash
# 1. 从 LobeHub 获取技能包
npx @lobehub/agents-market --get <pkg-name> -o ~/.hermes/skills/<pkg-name>/

# 2. 或者直接从 GitHub 下载
git clone https://github.com/lobehub/agents-market ~/temp/agents
cp -r ~/temp/agents/agents/<pkg-name> ~/.hermes/skills/<pkg-name>/

# 3. 检查包内容结构（应包含 README.md 和 hermes.json 配置）
ls ~/.hermes/skills/<pkg-name>/

# 4. 检查 .env 配置需求
# 社区技能包常需要环境变量，从 hermes.json 中查找 requires_env 字段
cat ~/.hermes/skills/<pkg-name>/hermes.json

# 5. 重启生效
hermes gateway restart  # 如果是 gateway 模式
/restart                 # CLI 会话中
```

**注意:** 社区包格式为 lobehub 格式（`hermes.json` 配置工具），系统识别需 `community_skills_enabled: true`（已在 config.yaml 中启用）。

## 已安装的社区技能

### telephony (2026-05-07 安装)
- **来源:** LobeHub 社区技能包
- **功能:** Twilio 电话/短信 + Bland.ai/Vapi AI 外呼
- **包路径:** `~/.hermes/skills/telephony/`
- **包含 5 个工具:**
  - `twilio_send_sms` — 发短信/MMS
  - `twilio_make_call` — 拨打电话
  - `bland_ai_call` — Bland.ai AI 外呼
  - `vapi_ai_assistant_call` — Vapi AI 电话助手
  - `twilio_webhook_handler` — 来电/短信 webhook
- **状态:** 已安装但未激活（需配置环境变量 + 购买 Twilio 号码）
- **所需环境变量:**
  - `TWILIO_ACCOUNT_SID` — Twilio 账户 SID
  - `TWILIO_AUTH_TOKEN` — Twilio 认证 Token
  - `TWILIO_PHONE_NUMBER` — 已购买的 Twilio 号码
  - `BLAND_AI_API_KEY` — (可选) Bland.ai API Key
  - `VAPI_API_KEY` — (可选) Vapi API Key
- **Twilio 号码购买:** 美国普通号码 $1/月，支持语音+SMS
- **Twilio 官网:** https://twilio.com → Start for free ($15试用金)

## 常用场景分类索引

### 建筑行业 (老板主业 - EPC)
- floorplan-diagnostics: 户型图诊断（已装）
- daily-epc-video-production: 住建部热点→视频（已装）
- video-script-to-production: 短视频工作流（已装）
- gansu-project-crawler: 甘肃项目抓取（已装）

### 台球俱乐部 (副业)
- video-script-to-production (含鑫球汇变体)

### 创意/设计
- baoyu-infographic: 信息图（已装）
- claude-design: HTML 设计（已装）
- popular-web-designs: 设计参考（已装）

### 研究/内容
- blogwatcher: 博客/RSS 监控
- gif-search: 表情搜索
- heartmula: AI 音乐生成
- songwriting-and-ai-music: 歌曲创作

### 生产力
- google-workspace: Gmail/Calendar/Drive/Docs
- maps: 地理编码/POI/路线
- airtable: 数据库
- obisidian: 笔记管理（已装）

### 股票/量化
- gubi-trading-brain: 顾比交易系统（已装）
- stock-robot: 量化助手（已装）

## 注意事项
- 社区技能 (LobeHub 505个) 需要联网安装
- 安装前可用 `hermes skills inspect <id>` 预览
- 安装后若技能未显示，`hermes skills config` 检查平台启用状态
