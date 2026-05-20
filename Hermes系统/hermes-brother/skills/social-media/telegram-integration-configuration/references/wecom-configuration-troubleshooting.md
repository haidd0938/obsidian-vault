# WeCom (Enterprise WeChat) Configuration and Troubleshooting

## Problem: "invalid bot_id" error (93019)

When configuring WeCom, the gateway connection fails:
```
invalid bot_id, hint: [xxxxxxxxxxxx], from ip: 42.89.98.65, more info at https://open.work.weixin.qq.com/devtool/query?e=93019 (errcode=93019)
```

## Configuration

Two places — environment variables recommended:

### Environment Variables
```bash
WECOM_BOT_ID="your-bot-id"
WECOM_SECRET="your-wecom-secret"
WECOM_WEBSOCKET_URL="wss://openws.work.weixin.qq.com"  # Optional
```

### Or config.yaml
```yaml
platforms:
  wecom:
    enabled: true
    bot_id: "your-bot-id"
    secret: "your-wecom-secret"
    websocket_url: "wss://openws.work.weixin.qq.com"
```

## bot_id Format Rules
- **DO NOT include `bot` prefix** — just the numeric ID
- Example: if WeCom bot page shows `bot1234567` or `bot:1234567`, use `1234567`
- The format changes depending on WeCom version: try `1234567` first

## Debug Steps
1. `hermes gateway restart`
2. Check logs: `tail -n 30 ~/.hermes/logs/gateway.log | grep -i wecom`
3. If `93019 invalid bot_id`, strip any `bot` prefix
4. Verify secret is correct
5. Try switching between config.yaml and .env

## Architecture Note
WeCom uses WebSocket connection (`wss://openws.work.weixin.qq.com`). This is different from Telegram's polling or webhook mode.
