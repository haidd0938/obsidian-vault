# browse.sh - AI Agent 网站技能引擎

> 研究日期: 2026-05-26 | 来源: https://browse.sh/ | 出品方: Browserbase

## 概述

Browserbase 出品的开源 CLI 工具，专为 AI Agent 设计，让其能高效操控网站。`npm i -g browse` 即可安装。

## 核心能力

### 1. 预制网站技能库（Open Web Catalog）
- 收录几百个常用网站的 skill
- 每个 skill 封装了该网站的最佳 DOM 选择器和 XHR 请求接口
- 宣称可降低 50 倍 token 消耗
- 社区+官方共同维护

**示例场景：**
```bash
browse skills add alltrails.com
browse skills add recreation.gov
claude "帮我规划去犹他州的公路旅行，安排充电站和露营地"
```

### 2. 四合一 CLI
- **Web Skill** - 直接调用预制网站技能
- **Browser Automation** - 浏览器自动化操作
- **Debugging** - 调试工具
- **Cloud** - 云端浏览器会话

### 3. 官方合作伙伴
- Lovable（建项目）、Poke（消息推送）、Ramp（报销）
- Reducto（文档解析）、Link（支付凭证）、Agent Email（邮箱）

## 与 Hermes Agent 对比

| 维度 | browse.sh | Hermes |
|------|-----------|--------|
| 网站技能 | 开放目录，社区维护，几百个预制 | 通用 browser + Scrapling |
| Token 成本 | 极低（对每个站手写优化） | 较高（通用方案） |
| 浏览器基础设施 | 依赖 Browserbase 云端（付费） | 本地 |
| 灵活性 | 局限于已收录的网站 | 全通用适配 |

## 使用结论

**适用场景：** 需要 AI 自动操作特定网站（Amazon 比价、Airbnb 搜房源、12306 查票、Craigslist 搜信息等）

**我们的评估：** 目前 Hermes 已有的 browser + scrapling 组合够用。等出海接单业务需要做网站数据采集/自动化时再考虑安装。

## 链接
- 官网: https://browse.sh/
- GitHub: Browse.sh (Browserbase)
- 依赖: npm, Browserbase 账号（付费）