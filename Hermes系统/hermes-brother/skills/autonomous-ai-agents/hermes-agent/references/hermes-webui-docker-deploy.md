# Hermes Web UI (Docker Compose 版) — 第三方部署方案

来源：公众号"艾算立方AIX³" (2026-04-10)
文章链接：https://mp.weixin.qq.com/s/XI0yZENIq0E2r_-EdoDzyg

> ⚠️ **这套系统和咱们当前跑的 Hermes Agent (CLI/Telegram版) 不是同一套。**
> 它使用的是 `hermes-agent/server:latest` 等镜像（非 `nousresearch/hermes-agent`），
> 架构是 Next.js Web 界面 + PostgreSQL + GitHub OAuth 登录 + Node.js 技能体系。

## 架构

| 组件 | 镜像 | 端口 |
|------|------|------|
| PostgreSQL | `postgres:15.2-alpine` | 5432 |
| Server (Web UI) | `hermes-agent/server:latest` | 3000 |
| Worker | `hermes-agent/worker:latest` | — |
| Beat (定时) | `hermes-agent/beat:latest` | — |

## 核心区别 vs 当前系统

| 维度 | 第三方 Web UI版 | 当前 CLI/Telegram版 |
|------|----------------|-------------------|
| 交互方式 | **Web管理界面** (localhost:3000) | Telegram / CLI |
| 登录认证 | **GitHub OAuth** (必须) | 无认证 |
| 技能开发 | **Node.js** (JS) | **Python** (SKILL.md) |
| 部署方式 | **Docker Compose** | pip install + 命令行 |
| 数据库 | PostgreSQL (必需) | SQLite (内置) |
| 多平台 | Web only | Telegram/Discord/Slack/WhatsApp等20+ |
| 技能市场 | 有 Web 界面管理 | CLI管理 |

## 部署步骤摘要

```yaml
# docker-compose.yml 核心配置
services:
  postgres:
    image: postgres:15.2-alpine
    environment:
      - POSTGRES_USER=hermes
      - POSTGRES_PASSWORD=hermes
      - POSTGRES_DB=hermes

  server:
    image: hermes-agent/server:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://hermes:hermes@postgres:5432/hermes
      - SECRET_KEY=your-super-secret-key-change-in-production-at-least-32-chars
      - NEXT_PUBLIC_BASE_URL=http://localhost:3000
      - GITHUB_CLIENT_ID=your-github-client-id
      - GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 前置条件
- Docker / Docker Compose
- **GitHub OAuth App**（必须，用于登录Web UI）
  - 注册地址: https://github.com/settings/developers
  - Callback URL: `http://localhost:3000/auth/github/callback`

### 启动命令
```bash
mkdir hermes-agent && cd hermes-agent
# 创建 docker-compose.yml (见上)
docker-compose up -d
# 访问 http://localhost:3000
```

### 域名 + HTTPS（生产环境）
```bash
# Nginx 反代 + Certbot SSL
sudo apt install nginx certbot python3-certbot-nginx
# 配置 Nginx → proxy_pass http://localhost:3000
sudo certbot --nginx -d your-domain.com
```

## 闲鱼自动化技能开发

文章后半部分演示了用这套系统开发闲鱼自动回复/智能议价技能：

- **技能类型**: Node.js 模块，继承 `Skill` 类
- **核心功能**: 自动回复、智能议价、商品监控
- **技能结构**: `config.json` + `main.js` + `manifest.json` + `schema.json`
- **部署方式**: Web UI 上传 → Skills → Add Skill

闲鱼自动化项目参考: `XianyuAutoAgent` (含 cookie 管理、签名生成、消息收发 API 封装)

## 何时推荐使用

- 老板**明确想要Web管理界面**，不想用 CLI/Telegram
- 有一台独立的服务器（NAS/云服务器）部署
- 愿意配置 GitHub OAuth
- 能接受 Node.js 技能体系（而非 Python）

## 当前不推荐的理由

- 与现有的 Hermes CLI/Telegram 版不互通
- 需要额外部署 PostgreSQL + Docker
- 需要 GitHub 账号配置 OAuth
- 技能用 Node.js 开发，与现有的 Python 技能体系不同
- 当前 Hermes CLI版已有 Web UI (`localhost:8648`)，虽然功能不同但基本可满足聊天需求
