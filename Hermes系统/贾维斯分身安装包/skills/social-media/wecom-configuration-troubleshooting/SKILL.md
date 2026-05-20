---
name: wecom-configuration-troubleshooting
title: WeCom Configuration Troubleshooting
description: Debug and troubleshoot WeCom (Enterprise WeChat) AI Bot integration with Hermes Agent
tags:
  - wecom
  - wechat-work
  - enterprise-wechat
  - configuration
  - troubleshooting
  - bot-id
  - websocket
created: 2026-04-16
updated: 2026-04-16
version: 1.0
difficulty: intermediate
prerequisites:
  - Hermes Agent installed
  - WeCom AI Bot credentials
  - Basic understanding of YAML configuration
---

# WeCom Configuration Troubleshooting

This skill documents the process of configuring and troubleshooting WeCom (Enterprise WeChat) AI Bot integration with Hermes Agent. It focuses on debugging the "invalid bot_id" error and finding the correct bot_id format.

## When to Use This Skill

Use this skill when:
- You're setting up WeCom integration with Hermes Agent
- You encounter "invalid bot_id" errors (error 93019)
- You need to debug WeCom WebSocket connection issues
- You're unsure about the correct bot_id format

## Problem Statement

When configuring WeCom integration, the gateway connection fails with error:
```
invalid bot_id, hint: [xxxxxxxxxxxx], from ip: 42.89.98.65, more info at https://open.work.weixin.qq.com/devtool/query?e=93019 (errcode=93019)
```

## Configuration Locations

WeCom can be configured in two places:

### 1. Environment Variables (Recommended)
```bash
WECOM_BOT_ID="your-bot-id"
WECOM_SECRET="your-secret"
WECOM_WEBSOCKET_URL="wss://openws.work.weixin.qq.com"  # Optional
WECOM_ALLOWED_USERS="user1,user2"  # Optional
```

### 2. Config.yaml (Override)
```yaml
platforms:
  wecom:
    enabled: true
    extra:
      bot_id: "your-bot-id"
      secret: "your-secret"
      websocket_url: "wss://openws.work.weixin.qq.com"
      dm_policy: "open"  # open | allowlist | disabled | pairing
      allow_from: ["user_id_1"]
      group_policy: "open"  # open | allowlist | disabled
      group_allow_from: ["group_id_1"]
```

## Common Issues and Solutions

### 1. Invalid bot_id Format

**Symptoms**: Error 93019 with "invalid bot_id" message

**Diagnosis**: The bot_id format provided doesn't match what WeCom AI Bot expects. Common user-provided parameters:
- Corp ID (e.g., `ww2c7bf7004641e5e8`)
- Agent ID (e.g., `1000022`)
- Secret (e.g., `6Nsi9BVXDb5huX0cGgK2B9Rdsrz2OWjtk5IzLEpvw-g`)

**Troubleshooting Steps**:

1. **Test Corp ID only**:
   ```bash
   bot_id: "ww2c7bf7004641e5e8"
   ```

2. **Test Agent ID only**:
   ```bash
   bot_id: "1000022"
   ```

3. **Test combined formats**:
   - `ww2c7bf7004641e5e8-1000022` (hyphen)
   - `ww2c7bf7004641e5e8_1000022` (underscore)
   - `ww2c7bf7004641e5e8:1000022` (colon)
   - `1000022:ww2c7bf7004641e5e8` (reverse)
   - `ww2c7bf7004641e5e8@1000022` (at symbol)
   - `1000022@ww2c7bf7004641e5e8` (reverse with @)

4. **Check config.yaml vs .env conflicts**:
   - config.yaml uses bot_id: "1000022" (Agent ID format)
   - .env uses WECOM_BOT_ID=ww2c7bf7004641e5e8 (Corp ID format)
   - This inconsistency causes "invalid bot_id" errors

5. **Alternative solution**: Remove WeCom configuration entirely if not essential, to allow other platforms (API server, Telegram) to function:
   ```bash
   # Remove wecom block from config.yaml
   patch ~/.hermes/config.yaml
   # Find and remove entire wecom: section
   ```

4. **Check if bot_id is a separate AI Bot ID**:
   - The bot_id might be a completely different value from the WeCom AI Bot platform
   - Check the WeCom AI Bot management console for the correct bot_id

5. **Verify secret correctness**:
   - Ensure the secret matches the bot_id
   - Secrets are typically 43-44 characters long

### 2. Configuration File Issues

**Symptoms**: Configuration changes don't take effect

**Diagnosis**: Multiple configuration sources causing conflicts

**Solutions**:

1. **Check precedence**: Environment variables override config.yaml
2. **Clear cache**: Restart the gateway after configuration changes
3. **Check file permissions**: Ensure config files are readable

### 3. WebSocket Connection Issues

**Symptoms**: Connection timeout or handshake failure

**Diagnosis**: Network or WebSocket URL issues

**Solutions**:

1. **Verify WebSocket URL**:
   ```yaml
   websocket_url: "wss://openws.work.weixin.qq.com"
   ```

2. **Test network connectivity**:
   ```bash
   curl -v wss://openws.work.weixin.qq.com
   ```

3. **Check firewall**: Ensure outbound connections to port 443 are allowed

## Diagnostic Commands

### 1. Test Gateway Connection
```bash
hermes gateway run
```

### 2. Check Configuration
```bash
# View current config
cat ~/.hermes/config.yaml | grep -A 10 "wecom:"

# Check environment variables
env | grep WECOM_
```

### 3. View Error Details
```bash
# Run gateway with verbose output
hermes gateway run 2>&1 | grep -i wecom
```

### 4. Check Source Code for Configuration Format
```bash
# View WeCom adapter source
cat ~/.hermes/hermes-agent/gateway/platforms/wecom.py | head -30

# Check configuration loading
cat ~/.hermes/hermes-agent/gateway/config.py | grep -A 10 -B 10 "WECOM_BOT_ID"
```

## Step-by-Step Debugging Process

1. **Read current configuration**:
   ```bash
   read_file ~/.hermes/config.yaml
   ```

2. **Check environment variables**:
   ```bash
   read_file ~/.hermes/.env
   ```

3. **Test connection with current config**:
   ```bash
   hermes gateway run 2>&1 | head -20
   ```

4. **Analyze error message**:
   - Note the error code (93019)
   - Note the hint code for WeCom tracking
   - Check the error URL for details

5. **Modify configuration**:
   ```bash
   patch ~/.hermes/config.yaml
   # OR update .env if accessible
   ```

6. **Iterate through bot_id formats**:
   - Start with simplest format
   - Progress through combinations
   - Document which formats fail

## Key Learnings

1. **Bot_id format is critical**: The bot_id is NOT simply Corp ID or Agent ID - it's a separate identifier from the WeCom AI Bot platform
2. **Configuration conflicts cause failures**: When config.yaml and .env have different bot_id formats (e.g., config.yaml uses Agent ID "1000022", .env uses Corp ID "ww2c7bf7004641e5e8"), the gateway fails with "invalid bot_id"
3. **Secret validation**: WeCom validates both bot_id and secret together
4. **Error codes**: Error 93019 specifically means "invalid bot_id"
5. **Configuration precedence**: Environment variables > config.yaml > defaults
6. **Debug approach**: Systematic trial of different bot_id formats is necessary
7. **Alternative solution**: If WeCom is not essential, removing the entire wecom configuration block allows other platforms (API server, Telegram) to function normally
8. **Web UI dependency**: WeCom connection failures can block API server startup, preventing Web UI from working

## Pitfalls to Avoid

1. **Assuming Corp ID = bot_id**: This is the most common mistake
2. **Not restarting gateway**: Configuration changes require restart
3. **Ignoring environment variables**: They override config.yaml settings
4. **Using wrong WebSocket URL**: Must be the official WeCom AI Bot URL

## Notes

- The WeCom AI Bot uses WebSocket connections, not traditional HTTP APIs
- Configuration requires both bot_id AND secret to be valid
- The error hint code (e.g., `[1776326444286792219624449]`) is for WeCom internal tracking
- Always restart the gateway after configuration changes

## References

1. WeCom AI Bot Documentation: https://work.weixin.qq.com/api/doc/90000/90135/90664
2. Error Code Lookup: https://open.work.weixin.qq.com/devtool/query?e=93019
3. Hermes Gateway Documentation: Internal source code at `~/.hermes/hermes-agent/gateway/platforms/wecom.py`