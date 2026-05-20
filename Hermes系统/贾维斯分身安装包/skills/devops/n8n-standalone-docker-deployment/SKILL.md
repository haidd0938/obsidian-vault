---
name: n8n-standalone-docker-deployment
description: Deploy n8n as standalone Docker service on macOS with one-click startup commands
tags: [docker, n8n, automation, macos, webhook]
category: devops
trigger: When user wants to deploy n8n for workflow automation and prefers simple startup commands
---

# n8n Standalone Docker Deployment for macOS

## When to use
- When the user wants to deploy n8n as a standalone service on macOS
- When the user prefers a one-click start button instead of complex terminal commands
- When integrating n8n with Hermes Agent for workflow automation
- When the user dislikes port/terminal interaction and prefers graphical/web interfaces

## Prerequisites
1. Docker Desktop installed and running on macOS
2. User has administrative privileges to create symlinks in `/usr/local/bin/`

## Configuration Steps

### 1. Create n8n directory structure
```bash
mkdir -p ~/n8n
cd ~/n8n
```

### 2. Create docker-compose.yml
Create `~/n8n/docker-compose.yml` with the following content:

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    environment:
      - N8N_BASIC_AUTH_ACTIVE=false
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - N8N_EDITOR_BASE_URL=http://localhost:5678
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
      - GENERIC_TIMEZONE=Asia/Shanghai
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/home/node/.n8n
    ports:
      - "5678:5678"
    networks:
      - n8n-network

networks:
  n8n-network:
    driver: bridge
```

### 3. Create start script
Create `~/n8n/start-n8n.sh` with executable permissions:

```bash
#!/bin/bash

# n8n启动脚本
# 用法: ./start-n8n.sh 或 n8n-start

set -e

echo "🔄 检查Docker服务状态..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker服务未运行，请先启动Docker Desktop"
    exit 1
fi

echo "✅ Docker服务正常"

# 检查是否已存在n8n容器
if docker ps --format '{{.Names}}' | grep -q '^n8n$'; then
    echo "✅ n8n容器已经在运行"
    echo "🌐 访问地址: http://localhost:5678"
    exit 0
fi

# 检查是否有停止的n8n容器
if docker ps -a --format '{{.Names}}' | grep -q '^n8n$'; then
    echo "🔄 启动已存在的n8n容器..."
    docker start n8n
else
    echo "🔄 创建并启动n8n容器..."
    cd "$(dirname "$0")"
    docker-compose up -d
fi

# 等待容器启动
echo "⏳ 等待n8n启动..."
sleep 5

# 检查容器状态
if docker ps --format '{{.Names}}' | grep -q '^n8n$'; then
    echo "✅ n8n启动成功"
    echo "🌐 访问地址: http://localhost:5678"
    echo "📂 数据目录: ~/n8n/data"
else
    echo "❌ n8n启动失败，请检查日志: docker logs n8n"
    exit 1
fi
```

Make it executable:
```bash
chmod +x ~/n8n/start-n8n.sh
```

### 4. Create stop script (optional)
Create `~/n8n/stop-n8n.sh`:

```bash
#!/bin/bash

# n8n停止脚本
# 用法: ./stop-n8n.sh 或 n8n-stop

set -e

echo "🔄 检查n8n容器状态..."
if docker ps --format '{{.Names}}' | grep -q '^n8n$'; then
    echo "🛑 停止n8n容器..."
    docker stop n8n
    echo "✅ n8n已停止"
else
    echo "ℹ️  n8n容器未在运行"
fi
```

```bash
chmod +x ~/n8n/stop-n8n.sh
```

### 5. Create symlinks for one-click commands
```bash
ln -sf ~/n8n/start-n8n.sh /usr/local/bin/n8n-start
ln -sf ~/n8n/stop-n8n.sh /usr/local/bin/n8n-stop
```

Note: If permission denied, use `sudo`:
```bash
sudo ln -sf ~/n8n/start-n8n.sh /usr/local/bin/n8n-start
sudo ln -sf ~/n8n/stop-n8n.sh /usr/local/bin/n8n-stop
```

## Usage

### Start n8n
```bash
n8n-start
```
or
```bash
cd ~/n8n && ./start-n8n.sh
```

### Stop n8n
```bash
n8n-stop
```

### Access n8n web interface
Open browser: **http://localhost:5678**

### Check n8n status
```bash
docker ps --filter "name=n8n"
```

### View logs
```bash
docker logs n8n
```

## Integration with Hermes Agent

### 1. Create webhook workflow in n8n
1. Access http://localhost:5678
2. Create new workflow
3. Add "Webhook" node
4. Configure webhook path (e.g., `/hermes-webhook`)
5. Add processing nodes (HTTP request, code, etc.)
6. Activate workflow

### 2. Get webhook URL
After activation, n8n displays webhook URL like:
```
http://localhost:5678/webhook/your-workflow-id
```

### 3. Call n8n from Hermes
Hermes can call n8n via:
1. **Terminal tool**: Execute `curl -X POST http://localhost:5678/webhook/your-workflow-id -d '{"message": "Hello from Hermes"}'`
2. **Custom skill**: Create a Hermes skill that encapsulates n8n API calls
3. **Webhook subscriptions skill**: Use the built-in `webhook-subscriptions` skill

### 4. Example: Weather query workflow
Create a n8n workflow that:
- Receives city name via webhook
- Calls weather API (like OpenWeatherMap)
- Returns formatted weather information
- Hermes skill sends request and presents results to user

## Pitfalls and Troubleshooting

### Docker not running
```
❌ Docker服务未运行，请先启动Docker Desktop
```
Solution: Start Docker Desktop application first.

### Permission denied when creating symlinks
```
ln: /usr/local/bin/n8n-start: Permission denied
```
Solution: Use `sudo` or check `/usr/local/bin/` ownership.

### Port 5678 already in use
```
Bind for 0.0.0.0:5678 failed: port is already allocated
```
Solution: Change port mapping in `docker-compose.yml` (e.g., "5680:5678").

### Container fails to start
Check logs:
```bash
docker logs n8n
```

### n8n not accessible after startup
Verify container is running:
```bash
docker ps | grep n8n
```
Test connectivity:
```bash
curl -I http://localhost:5678
```

## Verification

After deployment, verify:
1. `n8n-start` command works
2. n8n web interface accessible at http://localhost:5678
3. Container persists data in `~/n8n/data`
4. Hermes can successfully call n8n webhooks

## Related Skills
- `webhook-subscriptions`: Manage webhook subscriptions in Hermes
- `hermes-web-ui-diagnostic-repair`: Fix Hermes web interface issues
- `docker-compose` skills for other service deployments