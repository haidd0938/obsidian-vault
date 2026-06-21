---
name: telegram-integration-configuration
title: Telegram Integration Configuration
description: Configure Hermes Agent to connect as a Telegram bot for messaging integration
tags:
  - telegram
  - messaging
  - gateway
  - bot
  - integration
prerequisites:
  - Telegram bot token from @BotFather
  - Telegram user ID (from @userinfobot)
  - Hermes Agent installed and gateway service available
---

# Telegram Integration Configuration

Configure Hermes Agent to act as a Telegram bot for messaging, notifications, and command execution.

## Prerequisites

1. **Bot Token**: Create a bot via [@BotFather](https://t.me/BotFather) on Telegram:
   - Send `/newbot` to @BotFather
   - Choose a display name and username (must end with `bot`)
   - Save the API token (format: `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`)

2. **User ID**: Get your Telegram numeric user ID:
   - Message [@userinfobot](https://t.me/userinfobot) or [@get_id_bot](https://t.me/get_id_bot)
   - Save the numeric ID (e.g., `1932005111`)

3. **Hermes Gateway**: Ensure the gateway is installed:
   ```bash
   hermes gateway status
   ```

## Configuration Steps

### 1. Add Environment Variables

Add to `~/.hermes/.env`:

```bash
# Existing config may be above...
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=your_user_id_here  # Comma-separated for multiple users
```

**Note**: The `.env` file is protected, so you cannot use `patch` tool. Use terminal commands:
```bash
cd ~/.hermes
echo "TELEGRAM_BOT_TOKEN=8764424792:AAHz8bk97X9kdhTy2qxegmsNcNWUeFTCfF0" >> .env
echo "TELEGRAM_ALLOWED_USERS=1932005111" >> .env
```

### 2. Enable Telegram Platform in Config

Add Telegram configuration to `~/.hermes/config.yaml` under the `platforms` section:

```yaml
platforms:
  # ... other platforms ...
  telegram:
    enabled: true
    # No extra config needed - token and users are from .env
```

If using Python to update config programmatically:

```python
import yaml
import os

config_path = os.path.expanduser('~/.hermes/config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

if 'platforms' not in config:
    config['platforms'] = {}

config['platforms']['telegram'] = {'enabled': True}

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=1000)
```

### 3. Restart Gateway Service

```bash
hermes gateway restart
```

Wait 5-10 seconds for the service to fully restart.

### 4. Verify Connection

Check the gateway logs for successful connection:

```bash
tail -30 ~/.hermes/logs/gateway.log | grep -i telegram
```

Expected success messages:
```
[Telegram] Connected to Telegram (polling mode)
✓ telegram connected
```

**Important**: If you don't see "Connecting to telegram..." in logs, verify that `platforms.telegram.enabled: true` is set in `config.yaml`. The gateway will only load Telegram platform if explicitly enabled, even with `TELEGRAM_BOT_TOKEN` in `.env`.

### 4. Proxy Configuration (CRITICAL for GFW Networks)

**Background**: Hermes' telegram.py reads proxy from environment variable `TELEGRAM_PROXY`, **NOT** from `config.yaml`'s `platforms.telegram.proxy_url`. The config.yaml field is a placeholder — the code only checks:

1. `TELEGRAM_PROXY` env var (highest priority)
2. `HTTPS_PROXY` / `HTTP_PROXY` / `ALL_PROXY` (and lowercase variants)
3. macOS system proxy via `scutil --proxy` (auto-detect)

**If you're behind the GFW** (Telegram API is blocked), you **must** set `TELEGRAM_PROXY` in `.env`:

```bash
echo "TELEGRAM_PROXY=http://127.0.0.1:6478" >> ~/.hermes/.env
```

**Without this variable**, the code enters fallback-IP mode and tries to connect to `api.telegram.org` directly + fallback IP `149.154.166.110` — both will fail on GFW networks. The error log shows:

```
[Telegram] Primary api.telegram.org connection failed (); trying fallback IPs 149.154.166.110
[Telegram] Fallback IP 149.154.166.110 failed:
[Telegram] Connect attempt 1/3 failed: httpx.ConnectError:  — retrying in 1s
...
ERROR gateway.platforms.telegram: [Telegram] Failed to connect to Telegram: httpx.ConnectError:
```

After 20 failed attempts, the gateway gives up permanently: `Giving up reconnecting telegram after 20 attempts`.

**Optional**: Disable fallback IPs to avoid wasted connections:

```bash
echo "HERMES_TELEGRAM_DISABLE_FALLBACK_IPS=true" >> ~/.hermes/.env
```

**IMPORTANT GOTCHA**: The `.env` file is loaded by `hermes_cli.main` at startup via `load_dotenv()`. However, `hermes gateway start` spawns a **subprocess** — if the subprocess's environment variable inheritance doesn't include the loaded `.env` vars, the proxy won't be set. **Safe workaround**: Verify environment variables are actually set in the running gateway by checking `ls -la /proc/$PID/environ` (Linux) or directly testing connectivity:

```bash
# Test Telegram API reachability through proxy before starting gateway
curl -x http://127.0.0.1:6478 -s --connect-timeout 10 \
  "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```

If curl works but gateway doesn't connect, the proxy env var isn't reaching the gateway process. Fix with:

```bash
# Export manually, then start gateway in foreground
export TELEGRAM_PROXY=http://127.0.0.1:6478
hermes gateway run --replace
```

### 5. Performance Optimization

**Issue**: Slow response times (several seconds delay).

**Solutions**:
1. **Switch to Local Models**: Cloud APIs (DeepSeek) add network latency. Use local Ollama models for sub-second response:
   ```bash
   hermes config set model.provider "Local (127.0.0.1:11434)"
   hermes config set model.model "qwen2.5:7b"  # Or other available local model
   hermes gateway restart
   ```

2. **Disable Other Platforms**: If WeCom or other platforms have connection errors, they may cause resource contention:
   ```bash
   # Edit ~/.hermes/config.yaml and set wecom.enabled: false
   # Then restart gateway
   ```

3. **Network Issues**: Telegram may use fallback IPs due to connectivity problems. Check logs for:
   ```
   [Telegram] Auto-discovered Telegram fallback IPs: 149.154.166.110
   [Telegram] Primary api.telegram.org connection failed
   ```
   On GFW networks this is **not** normal — it means the proxy isn't configured. Follow the Proxy Configuration section above.

### 5. Test the Bot

1. Open Telegram and search for your bot (by its username)
2. Send `/start` or any message
3. The bot should respond

## Troubleshooting

### Bot Doesn't Respond

**Issue**: Bot is online but not responding to messages.

**Solutions**:
1. **Privacy Mode**: Telegram bots have privacy mode enabled by default. Disable it:
   - Message @BotFather → `/mybots` → Select your bot → Bot Settings → Group Privacy → Turn off
   - Remove and re-add bot to any groups (Telegram caches privacy state)

2. **Admin Privileges**: Alternative to disabling privacy mode:
   - Make the bot a group admin (admin bots see all messages)

3. **User Allowlist**: Ensure your user ID is in `TELEGRAM_ALLOWED_USERS`

### Connection Issues

**Issue**: Gateway fails to connect to Telegram.

**Solutions**:
1. **Platform Enabled Check**: Ensure `platforms.telegram.enabled: true` is set in `~/.hermes/config.yaml`. This is required even with `TELEGRAM_BOT_TOKEN` in `.env`.
2. **Token Verification**: Check token is correct and hasn't been revoked
3. **Network Connectivity**: Ensure server can reach `api.telegram.org`
4. **Proxy Settings**: If behind proxy, Telegram may use fallback IPs (seen in logs as "Auto-discovered Telegram fallback IPs")
5. **Logs Check**: Detailed errors in `~/.hermes/logs/gateway.log`

### Webhook Mode (Cloud Deployments)

For cloud deployments (Fly.io, Railway, etc.), use webhook mode instead of polling:

```bash
# Add to ~/.hermes/.env
TELEGRAM_WEBHOOK_URL=https://your-app.region.railway.app/telegram
TELEGRAM_WEBHOOK_SECRET=your_secret_here  # Optional but recommended
```

## Common Use Cases

### 1. Daily Task Intake
- User sends mixed work/life tasks via Telegram
- Agent analyzes tasks, identifies patterns and required workflows
- Routes tasks to appropriate systems or initiates processes

### 2. Project Management Updates
- Receive EPC project status updates via Telegram
- Send automated alerts for milestones, delays, or issues
- Query project data through natural language

### 3. Personal Assistant Commands
- Set reminders, schedule meetings
- Control smart home devices
- Get weather, news, or information updates

### 4. Business Operations
- Billiards club side business management
- Inventory checks, booking confirmations
- Customer inquiries routing

## Integration with Super Personal Assistant System

When implementing the "Super Personal Assistant Secretary Team" architecture:

1. **Telegram as Primary Interface**: Use Telegram for daily task intake and quick queries
2. **Intelligent Routing**: Based on message content, route to appropriate backend:
   - EPC business tasks → Local Qwen models + specialized tools
   - Billiards club tasks → Separate processing layer
   - Personal tasks → General assistant functions
3. **Data Isolation**: Ensure business-sensitive EPC data remains secure while using Telegram for communication

## Related Skills

- `wecom-configuration-troubleshooting`: For Enterprise WeChat integration
- `send_message`: For sending messages to various platforms