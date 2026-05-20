# macOS App Proxy Connectivity Troubleshooting

Diagnose and fix applications on macOS that fail to connect through proxy/VPN but work without it.

## When to Use
- App works fine without proxy but fails when proxy is enabled
- App doesn't automatically use macOS system proxy settings
- You've changed VPN/proxy software and apps stopped working
- Network-dependent apps show "Connecting..." indefinitely

## Quick Diagnostic Steps
```bash
# 1. Check system proxy settings
scutil --proxy

# 2. Test basic connectivity
curl -s --connect-timeout 10 https://example.com

# 3. Test proxy connectivity
curl -x http://127.0.0.1:PORT -s --connect-timeout 10 https://example.com

# 4. Check DNS
scutil --dns
```

## Common Fixes
1. **Restart the app** after checking/changing proxy settings
2. **Restart the proxy/VPN client** (many proxy apps cache routing tables)
3. **Check macOS firewall** (System Settings > Network > Firewall)
4. **Disable HTTP/3** in some apps — QUIC bypasses system proxy
5. **Bypass proxy for local addresses**: ensure `*.local, 127.0.0.1` in proxy bypass list

## App-Specific Notes
- **Telegram Desktop**: uses its own proxy settings independent of system
- **Discord**: respects system proxy on macOS
- **Terminal apps** (curl/wget): use `HTTP_PROXY` / `HTTPS_PROXY` env vars
