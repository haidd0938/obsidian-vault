---
name: hermes-web-ui-production-deployment
description: UMBRELLA — All Hermes Web UI operations. Covers production deployment via launchd, setup from source, diagnostic and repair, version downgrade to stable, NAS Docker deployment, the official built-in dashboard on port 9119, and the community Web UI.
category: software-development
---

# Hermes Web UI Production Deployment (hermes-web-ui)

Deploy the [EKKOLearnAI/hermes-web-ui](https://github.com/EKKOLearnAI/hermes-web-ui) project — a full-featured Vue 3 chat dashboard for Hermes Agent — as a persistent background service on macOS.

**Key differences from `hermes dashboard`:**
- hermes-web-ui runs on port **8648**, NOT 9119
- It's a separate open-source project (Vue 3 + Koa BFF), not the built-in Hermes dashboard
- Has chat interface, session management, usage analytics, platform config, cron management
- Built with `node dist/server/index.js`, not a Python/FastAPI backend

## Prerequisites

- Node.js >= 23.0.0 (hermes-web-ui >=0.4.7)
- Hermes Agent gateway running (port 8642) — the web UI proxies API calls to it
- Project either:
  - **Local install:** cloned at `~/hermes-web-ui/` with built `dist/`
  - **Global install:** installed via `npm install -g hermes-web-ui` (goes to `/usr/local/lib/node_modules/hermes-web-ui/`)

## Installation

### Option A — Local install (from source)

```bash
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git ~/hermes-web-ui
cd ~/hermes-web-ui
npm install
npm run build
```

Launch path: `/Users/mac/hermes-web-ui/dist/server/index.js`

### Option B — Global install (npm)

```bash
npm install -g hermes-web-ui@0.4.9
```

Launch path: `/usr/local/lib/node_modules/hermes-web-ui/dist/server/index.js`

> **IMPORTANT:** These are different directories! When updating via `npm install -g`, the launchd plist must point to the **global** path, not the local source directory.

## Steps

### 1. Check if the project is set up

```bash
ls ~/hermes-web-ui/dist/server/index.js   # needs to exist
ls ~/hermes-web-ui/dist/client/index.html  # needs to exist
```

If not, clone and build:
```bash
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git ~/hermes-web-ui
cd ~/hermes-web-ui
npm install
npm run build
```

### 2. Create the launchd plist

Create `/Users/mac/Library/LaunchAgents/com.hermes-webui.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hermes-webui</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>/Users/mac/hermes-web-ui/dist/server/index.js</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PORT</key>
        <string>8648</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
        <key>HOME</key>
        <string>/Users/mac</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>/Users/mac/hermes-web-ui</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/Users/mac/.hermes-web-ui/launchd-stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/mac/.hermes-web-ui/launchd-stderr.log</string>

    <key>ThrottleInterval</key>
    <integer>5</integer>
</dict>
</plist>
```

**IMPORTANT:** Check the node path with `which node` on the target machine. On Intel Macs it's usually `/usr/local/bin/node`, on Apple Silicon it's `/opt/homebrew/bin/node`.

### 3. Load the service

```bash
# Clean any stale PID file
rm -f ~/.hermes-web-ui/server.pid

# Kill any process on port 8648
lsof -ti:8648 | xargs kill -9 2>/dev/null

# Load into launchd
launchctl load ~/Library/LaunchAgents/com.hermes-webui.plist

# Wait and verify
sleep 3
curl -s -o /dev/null -w "%{http_code}" http://localhost:8648/
# Should return 200
```

### 4. Verify service status

```bash
launchctl list | grep hermes-webui
# Expected output: "PID\t0\tcom.hermes-webui"  (PID is the process ID, 0 = no error)
```

### 5. Open in browser

```bash
open http://localhost:8648/
```

## Managing the service

```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.hermes-webui.plist

# Restart (unload + load)
launchctl unload ~/Library/LaunchAgents/com.hermes-webui.plist && launchctl load ~/Library/LaunchAgents/com.hermes-webui.plist

# Check status
launchctl list | grep hermes-webui

# View logs
cat ~/.hermes-web-ui/launchd-stderr.log
cat ~/.hermes-web-ui/launchd-stdout.log
```

The service also has its own built-in CLI:
```bash
cd ~/hermes-web-ui && node bin/hermes-web-ui.mjs status
cd ~/hermes-web-ui && node bin/hermes-web-ui.mjs stop
cd ~/hermes-web-ui && node bin/hermes-web-ui.mjs start
cd ~/hermes-web-ui && node bin/hermes-web-ui.mjs restart
```

## Consolidated Sections

This umbrella skill subsumes six sibling skills as labeled subsections below. Sub-skill files have been archived for discoverability — the content lives here.

### Section A: Setup from Source (was `ekko-hermes-web-ui-setup`)
Install and launch the community Hermes Web UI at `http://localhost:8648`.

```bash
cd ~
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git
cd hermes-web-ui
npm install --ignore-engines
npm run build
node bin/hermes-web-ui.mjs start
```

**Proxy note:** If behind macOS HTTP Proxy 127.0.0.1:6478:
```bash
git config --global http.proxy http://127.0.0.1:6478
git config --global https.proxy http://127.0.0.1:6478
npm config set registry https://registry.npmmirror.com
# Clean up after:
git config --global --unset http.proxy && git config --global --unset https.proxy
npm config delete proxy && npm config delete https-proxy
```

**Auth token:** On first visit, the server prints the login URL with token. Find it: `cat ~/.hermes-web-ui/server.log | grep "token="`

**Shutdown:** `cd ~/hermes-web-ui && node bin/hermes-web-ui.mjs stop`

### Section B: Official Built-in Dashboard (was `hermes-web-ui-setup`)
Install the **official** Hermes Web Dashboard (FastAPI + Vite/React, port **9119**).

```bash
cd ~/.hermes
source hermes-agent/venv/bin/activate
pip install 'fastapi' 'uvicorn[standard]'
cd hermes-agent/web
npm install && npm run build
HERMES_WEB_DIST=$PWD/hermes-agent/hermes_cli/web_dist hermes dashboard --no-open
```

**Note:** This is a **different** project from the community Web UI on port 8648. Port 9119 is the FastAPI-based management dashboard (gateway status, sessions, logs, cron, skills, config).

### Section C: Diagnostic and Repair (was `hermes-web-ui-diagnostic-repair`)
Systematic troubleshooting when Web UI shows connection errors.

**Primary checklist:**
1. Is gateway running? `hermes gateway status` / `hermes gateway start`
2. Is API server enabled in config.yaml? Check `platforms.api_server.enabled: true`
3. Is port 8642 listening? `lsof -i :8642` / `curl -v http://localhost:8642/health`
4. Are there conflicting platforms (WeCom, Weixin)? Disable them in config.yaml
5. Check logs: `tail -30 ~/.hermes/logs/gateway.log`, `tail -30 ~/.hermes/logs/gateway.error.log`

**Common errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| "invalid bot_id" | WeCom config conflict | Remove wecom: block from config.yaml |
| "Failed to connect" | API server not enabled | Enable api_server in platforms |
| Port 8642 not listening | Gateway not running | `hermes gateway start` |
| Login fails | Wrong access token | Use token from ~/.hermes/.env or config.yaml |

**After config changes:** Always restart gateway: `hermes gateway stop && hermes gateway start`

### Section D: Version Downgrade (was `hermes-web-ui-downgrade-stable`)
Downgrade from latest to 0.4.7 when newer versions cause DeepSeek compatibility issues.

**Symptoms:** "Agent returned no output" / "missing field `tool_call_id`" errors in Web UI but not in CLI.

```bash
launchctl unload ~/Library/LaunchAgents/com.hermes-webui.plist 2>/dev/null
kill $(lsof -ti:8648) 2>/dev/null
npm uninstall -g hermes-web-ui
npm install -g hermes-web-ui@0.4.7
launchctl load ~/Library/LaunchAgents/com.hermes-webui.plist
sleep 3
curl -s -o /dev/null -w "%{http_code}" http://localhost:8648/
```

**Root cause:** 0.5.x changed session message serialization, incompatible with DeepSeek API's strict format validation. 0.4.7 is the last fully stable version for DeepSeek.

### Section E: NAS Docker Deployment (was `hermes-deploy-on-fnos-nas-docker`)
Deploy Hermes Agent + Web UI on 飞牛 NAS (fnOS) using Docker.

See `references/nas-docker-deployment.md` for the full docker-compose.yml and step-by-step guide.

**Key points:**
- NAS Docker images: `nousresearch/hermes-agent:latest`, `lingganwu/hermes-web-ui:latest`
- NAS Web UI port: 6060 (not 8648 like Mac)
- Use a **different** Telegram Bot Token for NAS vs Mac (create a new bot via BotFather)
- Same DeepSeek API key works from multiple IPs
- FN Connect remote access is unreliable — prefer local LAN or stable VPN

### Reference: Two Different Hermes Web UIs

| Aspect | Official Dashboard | Community Web UI |
|--------|-------------------|-----------------|
| Port | 9119 | 8648 |
| Backend | FastAPI (Python) | Koa (Node.js) |
| API server port | 8642 | N/A (connects via gateway proxy) |
| Startup | `hermes dashboard` | `node bin/hermes-web-ui.mjs start` |
| Service | Managed by gateway | Managed by launchd |

### Reference: launchd Service Template

The `scripts/` directory contains a reusable launchd plist template file.

---

## Node.js Compatibility Note

hersmes-web-ui >=0.4.7 requires **Node.js >= 23.0.0**. If your system runs Node v22:

- The server will start and listen on port 8648 (curl returns 200)
- BUT the frontend JavaScript detects the version and shows an error banner: "Node.js vX detected, please upgrade to v23 or above"
- The page appears blank/blocked to the user

**Solutions:**

1. **Rollback to 0.4.7** (or earlier) — quickest fix, all features work:
   ```bash
   npm install -g hermes-web-ui@0.4.7
   ```

2. **Upgrade Node.js** to v23+ — needed for 0.4.8+ versions:
   ```bash
   brew upgrade node   # may take 10+ minutes from source
   # Or download binary installer from https://nodejs.org/
   ```

Also note: starting from 0.4.7, token-based auth is **enabled by default**. The token is stored at `~/.hermes-web-ui/.token`. Access the UI via:
```
http://localhost:8648/#/?token=<token_from_file>
```

## Pitfalls

- The PLIST **must** use the correct Node.js path. Common locations:
  - Intel Mac: `/usr/local/bin/node`
  - Apple Silicon: `/opt/homebrew/bin/node`
  - Prebuilt binary install (v23+): `/usr/local/node23/bin/node`
  - Verify with `which node` and also check custom install locations.
  - **If the user upgraded Node via prebuilt binary (not brew), the old `/usr/local/bin/node` may be a different version or missing!** The launchd plist will silently fail with `spawn hermes ENOENT` errors because the wrong node path can't find global npm modules.
- `AUTH_TOKEN` is auto-generated to `~/.hermes-web-ui/.token` by the server. If auth is enabled, the URL includes `?token=...`. For local-only use, you can set `AUTH_DISABLED=1` but this is not recommended for security.
- If the service starts but `/health` returns non-200, check `launchd-stderr.log` for errors.
- crash recovery: launchd with `KeepAlive` + `ThrottleInterval 5` means it restarts automatically, but waits 5 seconds between attempts to prevent restart loops.
- If the user also has `hermes dashboard` (port 9119) or gateway `api_server` (port 8642), those are separate services on different ports — no conflict.
- **The PATH in plist must include the custom node bin directory** so that `hermes` CLI is found. Standard PATH `/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin` may not include `/usr/local/node23/bin`. Add it to the plist's EnvironmentVariables.
- **After reboot troubleshooting:** If Web UI doesn't load after reboot:
  1. Check `launchctl list | grep hermes-webui` — if exit code is non-zero, the process crashed
  2. Check `cat ~/.hermes-web-ui/launchd-stderr.log` for error messages
  3. Common error: `spawn hermes ENOENT` — PATH is wrong, missing node bin directory
  4. Common error: node binary not found — plist points to old node path
  5. Fix: update plist's ProgramArguments node path AND EnvironmentVariables PATH, then `launchctl unload && launchctl load`
