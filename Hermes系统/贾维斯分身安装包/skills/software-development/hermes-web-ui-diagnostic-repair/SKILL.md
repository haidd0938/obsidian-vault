---
name: hermes-web-ui-diagnostic-repair
title: Hermes Web UI Diagnostic and Repair
description: Diagnose and repair Hermes Web UI connectivity issues, focusing on API server configuration, gateway conflicts, and port connectivity
tags:
  - hermes
  - web-ui
  - gateway
  - api-server
  - troubleshooting
  - configuration
created: 2026-04-17
updated: 2026-04-17
version: 1.0
difficulty: intermediate
prerequisites:
  - Hermes Agent installed
  - Basic understanding of ports and services
  - Access to terminal and configuration files
---

# Hermes Web UI Diagnostic and Repair

This skill provides a systematic approach to diagnosing and fixing Hermes Web UI connectivity issues, particularly when the web interface fails to connect to the backend API server.

## When to Use This Skill

Use this skill when:
- Hermes Web UI (http://localhost:8648/#/chat) shows connection errors
- API server is not responding on port 8642
- Gateway service has configuration conflicts
- WebSocket connections fail in the browser console
- You see login screen but authentication fails

## Problem Symptoms

1. **Web UI loads but cannot connect** - Shows "Connecting..." or "Failed to connect" messages
2. **Login screen appears but login fails** - API server not responding
3. **Port 8642 not listening** - No service on default API server port
4. **Gateway service conflicts** - WeCom or other platforms causing connection failures

## Diagnostic Process

### Step 1: Check Service Status

```bash
# Check if gateway is running
hermes gateway status

# If not running, start it
hermes gateway start

# Check for error logs
tail -30 ~/.hermes/logs/gateway.log
tail -30 ~/.hermes/logs/gateway.error.log
```

### Step 2: Verify API Server Configuration

The API server must be explicitly enabled in `config.yaml`. Check the current configuration:

```bash
read_file ~/.hermes/config.yaml
```

Look for the `api_server` section under `platforms`:

```yaml
platforms:
  api_server:
    enabled: true  # Must be true
    # Other settings are optional
```

### Step 3: Check Port Connectivity

Verify API server is listening on port 8642:

```bash
# Check if port 8642 is in use
lsof -i :8642

# Or use netstat
netstat -an | grep 8642

# Test API endpoint
curl -v http://localhost:8642/health
```

### Step 4: Identify Configuration Conflicts

Common conflicts:
1. **WeCom connection failures** causing gateway to stall
2. **Multiple bot_id configurations** (config.yaml vs .env)
3. **Disabled platforms** preventing proper initialization

## Repair Procedures

### Procedure A: Fix API Server Configuration

If API server is not enabled or has issues:

1. **Enable API server in config.yaml**:
   ```bash
   patch ~/.hermes/config.yaml
   ```
   
   Find the platforms section and ensure:
   ```yaml
   platforms:
     api_server:
       enabled: true
     # Other platforms...
   ```

2. **Disable conflicting platforms temporarily**:
   ```yaml
   platforms:
     wecom:
       enabled: false  # Disable if causing connection errors
     weixin:
       enabled: false  # Disable personal WeChat integration
     telegram:
       enabled: true   # Keep if working
     api_server:
       enabled: true   # Enable for Web UI
   ```

### Procedure B: Clean Up Environment Variables

Environment variables in `.env` may conflict with config.yaml settings:

1. **Check current .env configuration**:
   ```bash
   read_file ~/.hermes/.env
   ```

2. **Add flags to disable problematic platforms**:
   Add these lines to `.env`:
   ```bash
   WECOM_ENABLED=false
   GATEWAY_ALLOW_ALL_USERS=true
   ```

3. **Apply environment changes**:
   ```bash
   echo "WECOM_ENABLED=false" >> ~/.hermes/.env
   echo "GATEWAY_ALLOW_ALL_USERS=true" >> ~/.hermes/.env
   ```

### Procedure C: Remove Problematic Configuration Blocks

When conflicting configurations cause persistent errors (e.g., invalid bot_id), remove the problematic block entirely:

1. **Remove WeCom configuration block** from config.yaml:
   - Delete or comment out the entire `wecom:` section
   - This resolves "invalid bot_id" errors that prevent gateway startup

2. **Restart services after changes**:
   ```bash
   hermes gateway stop
   hermes gateway start
   ```

### Procedure D: Verify Web UI Configuration

Check Web UI backend configuration:

1. **Find Web UI installation path**:
   ```bash
   which hermes-web-ui
   ```

2. **Check Web UI config**:
   ```bash
   find /usr/local -name "config.js" | xargs grep -l "8642" | head -1
   ```

3. **Expected configuration**:
   ```javascript
   // Should point to local API server
   upstream: 'http://127.0.0.1:8642'
   ```

## Complete Repair Workflow

Follow this complete workflow when Web UI is completely broken:

### Phase 1: Stop and Diagnose
```bash
# Stop gateway to prevent resource waste
hermes gateway stop

# Check logs for last errors
tail -50 ~/.hermes/logs/gateway.error.log

# Check current configuration
read_file ~/.hermes/config.yaml | grep -A 5 -B 5 "platforms:"
```

### Phase 2: Fix Configuration
1. **Disable problematic platforms** (WeCom, Weixin)
2. **Enable API server**
3. **Update .env with disable flags**
4. **Remove conflicting configuration blocks**

### Phase 3: Restart and Verify
```bash
# Start gateway
hermes gateway start

# Wait 5 seconds for initialization
sleep 5

# Check logs for success
tail -20 ~/.hermes/logs/gateway.log | grep -E "(api_server|listening|connected)"

# Test API endpoint
curl -s http://localhost:8642/health && echo "✓ API server responding"

# Check port
lsof -i :8642 | grep LISTEN && echo "✓ Port 8642 listening"
```

### Phase 4: Test Web UI
1. **Navigate to** http://localhost:8648/#/chat
2. **Login with access token** (from config.yaml or .env)
3. **Verify connection** - should show "Connected" status

## Verification Steps

### Success Indicators
1. ✓ Gateway logs show: `[Api_Server] API server listening on http://127.0.0.1:8642`
2. ✓ Port 8642 shows LISTEN state
3. ✓ curl http://localhost:8642/health returns 200 OK
4. ✓ Web UI login successful, shows "Connected" status
5. ✓ Browser console shows WebSocket connection established

### Common Error Messages and Fixes

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| "invalid bot_id" | WeCom configuration conflict | Remove wecom: block from config.yaml |
| "Failed to connect" | API server not enabled | Enable api_server in platforms |
| Port 8642 not listening | Gateway not running | Restart gateway with hermes gateway start |
| Login fails | Wrong access token | Use token from ~/.hermes/.env or config.yaml |
| WebSocket error | Network/proxy issue | Check browser console, disable proxy if needed |

## Key Learnings

1. **API server must be explicitly enabled** - it's not enabled by default
2. **WeCom conflicts block gateway startup** - "invalid bot_id" errors prevent API server from starting
3. **Configuration precedence**: Environment variables (.env) override config.yaml
4. **Clean configuration approach**: When conflicts persist, remove entire configuration blocks
5. **Verification sequence**: Check logs → check ports → test API → test Web UI

## Pitfalls to Avoid

1. **Not restarting gateway** after configuration changes
2. **Assuming API server is enabled by default** (it's not)
3. **Ignoring .env file conflicts** with config.yaml
4. **Not checking gateway.error.log** for detailed error messages
5. **Forgetting to test with curl** before trying Web UI

## Related Skills

- `wecom-configuration-troubleshooting`: For specific WeCom bot_id issues
- `telegram-integration-configuration`: For Telegram bot setup
- `macos-app-proxy-connectivity`: For network/proxy related issues
- `ekko-hermes-web-ui-setup`: For EKKOLearnAI community Web UI (port 8648, standalone Node.js)

## Important Distinction: Two Different Hermes Web UIs

There are **two separate** Hermes Web UIs. Do not confuse them:

| Aspect | Official Hermes Web Dashboard | EKKOLearnAI Community Web UI |
|--------|-------------------------------|-------------------------------|
| Port | 9119 | 8648 |
| Backend | FastAPI (Python, Hermes gateway API server) | Koa (Node.js, standalone) |
| API server port | 8642 (must be enabled in config.yaml) | N/A — connects to gateway proxy |
| Dependency | `api_server.enabled: true` in config.yaml, gateway running | `hermes` CLI on $PATH, Node.js >=22 |
| When it breaks | Config.yaml issues, gateway not running, api_server disabled | CLI not found, Node version, npm install failure |
| Startup command | `hermes gateway start` | `node bin/hermes-web-ui.mjs start` |
| Impact of config.yaml changes | Direct — controls API server, auth, platforms | Indirect — only via gateway proxy/CLI |
| Shutdown | `hermes gateway stop` | `node bin/hermes-web-ui.mjs stop` |

**Diagnosis tip:** If the user says `localhost:8648`, it's **always** the EKKOLearnAI community Web UI. Use the `ekko-hermes-web-ui-setup` skill. The repair skill (this one) is for the official dashboard on port 9119.

## Notes

- Web UI runs on port 8648 by default, API server on 8642
- Access token is typically in `.env` as `HERMES_ACCESS_TOKEN` or similar
- Gateway restart is required after most configuration changes
- Always verify each step before proceeding to the next