# macOS Node.js Upgrade Guide (Prebuilt Binaries + Brew Fallback)

> 合并自 `macos-upgrade-node-with-brew-fallback` 技能。当 `brew upgrade node` 从源码编译太慢（Intel Mac常见）或失败时，用官方预编译二进制包快速升级。

## When to Use
- `brew upgrade node` takes 30+ minutes on Intel Mac
- You need Node >= 23 for hermes-web-ui 0.4.8+

## Steps

### 1. Check current
```bash
node --version
which node
brew list --versions node
```

### 2. Stop Node-dependent services
```bash
launchctl unload ~/Library/LaunchAgents/com.hermes-webui.plist 2>/dev/null
kill $(lsof -ti:8648) 2>/dev/null
```

### 3. Download prebuilt binary
```bash
cd /tmp
curl -L -o node-v23.tar.xz \
  https://nodejs.org/dist/v23.11.0/node-v23.11.0-darwin-x64.tar.xz
tar xf node-v23.tar.xz
```

Find latest version at https://nodejs.org/en/download

### 4. Link binaries
```bash
ln -sf /tmp/node-v23.11.0-darwin-x64/bin/node /usr/local/bin/node
ln -sf /tmp/node-v23.11.0-darwin-x64/bin/npm /usr/local/bin/npm
ln -sf /tmp/node-v23.11.0-darwin-x64/bin/npx /usr/local/bin/npx
node --version && npm --version
```

### 5. Upgrade npm tools and restart
```bash
npm install -g hermes-web-ui@latest
launchctl load ~/Library/LaunchAgents/com.hermes-webui.plist
```

## Pitfalls
1. **Brew compiles from source** on Intel Mac → 30+ min. Skip to binary approach.
2. **Symlinks point to /tmp** — reboot destroys them. For production, move to persistent dir.
3. **npm installs globally to /tmp** — expected behavior, `npm list -g` still works.
4. **hermes-web-ui 0.5.2+** adds session auto-grouping by source (api_server, telegram, etc.).
5. **If grouping doesn't show**: `localStorage.removeItem('hermes_collapsed_groups')` in browser console.

## macOS App Proxy Connectivity

Quick check for apps behind proxy (Telegram, Discord):
```bash
scutil --proxy
curl -x http://127.0.0.1:PORT -s --connect-timeout 10 https://example.com
# Common fix: restart proxy app, then restart target app
```
