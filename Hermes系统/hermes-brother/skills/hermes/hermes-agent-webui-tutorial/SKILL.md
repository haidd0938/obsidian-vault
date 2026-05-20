---
name: hermes-agent-webui-tutorial
category: hermes
description: 艾算立方AIX³公众号文章 — Hermes Agent 手把手安装教程（Docker版，带Web管理界面3000端口+GitHub OAuth登录），以及闲鱼自动接单技能开发示例。
---

# Hermes Agent WebUI版安装教程（艾算立方AIX³）

来源：公众号「艾算立方AIX³」2026年4月10日
原文：https://mp.weixin.qq.com/s/XI0yZENIq0E2r_-EdoDzyg

## 架构（Docker Compose 4件套）

- **PostgreSQL** `postgres:15.2-alpine` — 数据库
- **Server** `hermes-agent/server:latest` — Web管理界面（端口3000）
- **Worker** `hermes-agent/worker:latest` — 任务执行
- **Beat** `hermes-agent/beat:latest` — 定时调度

## 与当前Hermes系统的区别

| 项目 | 文章这套 | 咱们现在这套 |
|------|---------|------------|
| 镜像来源 | `hermes-agent/*` (老版/分支) | `nousresearch/hermes-agent` |
| 交互方式 | **Web界面** localhost:3000 | Telegram / API |
| 登录方式 | GitHub OAuth | 无 |
| 技能开发语言 | Node.js (JS) | Python + SKILL.md |
| 部署方式 | Docker Compose | pip install + CLI |

## 部署步骤

### 1. 准备工作
- GitHub账户（用于登录管理界面）
- 安装Docker + Docker Compose
- 服务器或本地机器（推荐Linux/macOS）

### 2. Docker Compose配置
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15.2-alpine
    container_name: hermes-postgres
    environment:
      - POSTGRES_USER=hermes
      - POSTGRES_PASSWORD=hermes
      - POSTGRES_DB=hermes
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hermes -d hermes"]
      interval: 5s
      timeout: 5s
      retries: 5

  server:
    image: hermes-agent/server:latest
    container_name: hermes-server
    environment:
      - DATABASE_URL=postgresql://hermes:hermes@postgres:5432/hermes
      - SECRET_KEY=your-super-secret-key-change-in-production-at-least-32-chars
      - NEXT_PUBLIC_BASE_URL=http://localhost:3000
      - GITHUB_CLIENT_ID=your-github-client-id
      - GITHUB_CLIENT_SECRET=your-github-client-secret
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - server_logs:/app/logs/
      - server_data:/app/data/

  worker:
    image: hermes-agent/worker:latest
    container_name: hermes-worker
    environment:
      - DATABASE_URL=postgresql://hermes:hermes@postgres:5432/hermes
      - SECRET_KEY=your-super-secret-key-change-in-production-at-least-32-chars
    depends_on:
      postgres:
        condition: service_healthy
      server:
        condition: service_started
    volumes:
      - server_data:/app/data/:ro
      - worker_logs:/app/logs/

  beat:
    image: hermes-agent/beat:latest
    container_name: hermes-beat
    environment:
      - DATABASE_URL=postgresql://hermes:hermes@postgres:5432/hermes
      - SECRET_KEY=your-super-secret-key-change-in-production-at-least-32-chars
    depends_on:
      postgres:
        condition: service_healthy
      server:
        condition: service_started

volumes:
  postgres_data:
  server_logs:
  server_data:
  worker_logs:

networks:
  default:
    name: hermes-network
```

### 3. GitHub OAuth配置
1. 访问 https://github.com/settings/developers
2. 点击 "New OAuth App"
3. Application name: Hermes Agent
4. Homepage URL: http://localhost:3000
5. Authorization callback URL: http://localhost:3000/auth/github/callback
6. 复制 Client ID 和 Client Secret 到 docker-compose.yml

### 4. 启动
```bash
mkdir hermes-agent && cd hermes-agent
# 创建docker-compose.yml后
docker-compose up -d
# 访问 http://localhost:3000
```

### 5. Nginx + SSL（生产环境）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 闲鱼接单技能（文章中的示例）

文章演示了开发一个 XianyuAutoAgent 技能，实现：
- 自动回复买家消息
- 智能议价策略
- 商品监控与搜索

技能结构：
```
my-skill/
├── config.json          # 技能配置
├── package.json         # 依赖管理
├── main.js              # 主入口
├── manifest.json        # 技能元数据
├── resources/
├── tests/
└── schema.json          # 任务参数定义
```

## 注意事项
- 这套系统是**独立版本**，与咱们现在的Telegram版Hermes不互通
- 如需部署需要干净的Docker环境
- 需要GitHub OAuth才能登录
