---
name: ekko-hermes-web-ui-setup
description: Install and launch EKKOLearnAI/hermes-web-ui — a Vue 3 + Koa web dashboard for Hermes Agent on port 8648, with chat, jobs, channels, skills, memory, models, terminal, and usage analytics.
category: software-development
---

# EKKOLearnAI Hermes Web UI Setup

Install and launch the community Hermes Web UI at `http://localhost:8648`. This is a **different project** from the official Hermes Web Dashboard (port 9119) — it has a richer chat interface, session management, terminal, and is Vue 3 + Koa based.

## Steps

### 1. Clone the repo

```bash
cd ~
git clone https://github.com/EKKOLearnAI/hermes-web-ui.git
cd hermes-web-ui
```

**Proxy note:** If you're behind a proxy (e.g. macOS HTTP Proxy 127.0.0.1:6478), set git proxy first:
```bash
git config --global http.proxy http://127.0.0.1:6478
git config --global https.proxy http://127.0.0.1:6478
```

### 2. Install npm dependencies

```bash
# Switch npm registry to npmmirror (China mirror) for faster installs
npm config set registry https://registry.npmmirror.com

# Install with --ignore-engines because minimum Node requirement is >=23
# (current macOS Node is typically v22.x)
npm install --ignore-engines
```

**Known issue:** Node.js >=23 is required but Node v22 works fine with `--ignore-engines`. The UI will show a warning banner about Node version but functions normally.

**Proxy note:** If using proxy, don't forget to clean up npm proxy settings after install:
```bash
npm config delete proxy
npm config delete https-proxy
```

### 3. Build

The `npm install` step should auto-build the project. If it didn't:

```bash
npm run build
```

Build output goes to `dist/client/` (Vite frontend) and `dist/server/` (esbuild server bundle).

### 4. Start the server (quick test)

```bash
cd ~/hermes-web-ui
node bin/hermes-web-ui.mjs start
```

Server starts on `http://localhost:8648`. Default port is 8648. The CLI manages PID in `~/.hermes-web-ui/` and auto-generates an auth token.

### 5. Get the access token (if auth is enabled)

Check the server start log:
```bash
cat ~/.hermes-web-ui/server.log | grep "token="
```

Or from the process output — the token is in the URL:
```
http://localhost:8648/#/?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 6. Login

Open `http://localhost:8648` in browser, paste the access token, and click Login.

> **Note:** When running the server directly via Node (not the CLI wrapper), no auth token is generated — the server starts in a mode that works without authentication on localhost.

## Shutdown (CLI-managed)

```bash
cd ~/hermes-web-ui && node bin/hermes-web-ui.mjs stop
```

## Verification

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8648/
# Should return 200
```

---

## Persistence: launchd (macOS service — auto-start on boot + crash recovery)

For a **production-grade** setup that survives reboots and auto-recovers from crashes, install as a launchd service.

### Create the plist

Write `~/Library/LaunchAgents/com.hermes-webui.plist`:

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

> **Important:** Run the server directly via `dist/server/index.js` — not the CLI wrapper (`bin/hermes-web-ui.mjs`). The CLI wrapper manages its own PID file and doesn't daemonize cleanly under launchd. Running the server entry directly avoids auth token issues and is simpler.

### Load the service

```bash
launchctl load ~/Library/LaunchAgents/com.hermes-webui.plist
```

### Verify

```bash
launchctl list | grep hermes-webui
# Output: PID	0	com.hermes-webui  (exit code 0 = running)

curl -s -o /dev/null -w "%{http_code}" http://localhost:8648/
# Should return 200
```

### Management commands

| Action | Command |
|--------|---------|
| Stop | `launchctl unload ~/Library/LaunchAgents/com.hermes-webui.plist` |
| Start | `launchctl load ~/Library/LaunchAgents/com.hermes-webui.plist` |
| Restart | `launchctl unload ... && launchctl load ...` |
| Status | `launchctl list \| grep hermes-webui` |
| Logs | `tail -f ~/.hermes-web-ui/launchd-stdout.log` |
| Errors | `tail -f ~/.hermes-web-ui/launchd-stderr.log` |

### Cleanup before loading

If the server was previously started via the CLI wrapper, clean up stale state first:

```bash
kill $(cat ~/.hermes-web-ui/server.pid 2>/dev/null) 2>/dev/null
rm -f ~/.hermes-web-ui/server.pid
```

## Pitfalls

- **Node version:** Requires >=23 (v22 works with `--ignore-engines`). The UI shows a warning banner but functions normally.
- **Network issues:** GitHub clone and npm install may hang without proxy. Use `git config --global http.proxy` and `npm config set registry https://registry.npmmirror.com`.
- **npm install failure:** If it fails with ECONNRESET, it's likely a proxy issue. Set npm registry to npmmirror and clear proxy settings.
- **npm install using proxy:** If you have proxy env vars set, npm may still try to use them after `npm config delete proxy`. Set `registry` to npmmirror as the primary fix.
- **Token login:** The Web UI requires an access token on first visit. Check the server startup logs — it prints the login URL with the token embedded.
- **Clean up git proxy:** After cloning, remove global git proxy settings so other git operations aren't affected:
  ```bash
  git config --global --unset http.proxy
  git config --global --unset https.proxy
  ```
- **Restart:** If you need to restart, use `node bin/hermes-web-ui.mjs restart` rather than killing and starting manually.
- **No `hermes` CLI dependency at runtime:** Unlike the official dashboard, this UI runs as a standalone Node.js server and doesn't require `hermes` CLI commands during operation.
