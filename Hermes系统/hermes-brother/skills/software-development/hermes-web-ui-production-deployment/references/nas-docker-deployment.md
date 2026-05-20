# NAS Docker Deployment (飞牛 fnOS)

Deploy Hermes Agent + Web UI on 飞牛 NAS using Docker. Useful as a backup instance when MacBook is offline.

## Prerequisites
- 飞牛 NAS running fnOS with Docker app
- Docker images: `nousresearch/hermes-agent:latest`, `lingganwu/hermes-web-ui:latest`

## docker-compose.yml

```yaml
version: '3.8'
services:
  hermes-agent:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-agent
    restart: unless-stopped
    ports:
      - "8642:8642"
    volumes:
      - ./hermes-home:/root/.hermes
      - ./projects:/root/projects
    environment:
      - DEEPSEEK_API_KEY=your_ds_key
      - TELEGRAM_BOT_TOKEN=your_tg_token
      - TZ=Asia/Shanghai

  hermes-webui:
    image: lingganwu/hermes-web-ui:latest
    container_name: hermes-webui
    restart: unless-stopped
    ports:
      - "6060:6060"
    volumes:
      - ./hermes-home:/root/.hermes
    environment:
      - UPSTREAM=http://hermes-agent:8642
      - PORT=6060
      - TZ=Asia/Shanghai
    depends_on:
      - hermes-agent
```

## Setup Steps
1. Open Docker app on NAS → Compose/Stack section
2. Paste YAML, replace API keys with real values
3. Deploy and wait for containers to start
4. Access agent container shell, run: `hermes gateway setup` then `hermes gateway start`
5. Access Web UI at http://[NAS_IP]:6060

## Key Notes
- Use different Telegram Bot Token for NAS vs Mac (create new bot via BotFather)
- Same DeepSeek API key works from multiple IPs
- Web UI on NAS uses port 6060, not 8648
- FN Connect remote access is unreliable — prefer local LAN
- Container restart policy `unless-stopped` ensures auto-start on NAS reboot
