---
name: macOS App Proxy Connectivity Troubleshooting
title: macOS App Proxy Connectivity Troubleshooting
description: Diagnose and fix proxy connectivity issues for apps on macOS, especially when apps don't automatically inherit system proxy settings.
tags:
  - macos
  - proxy
  - vpn
  - networking
  - troubleshooting
  - telegram
  - apps
version: 1.0
last_updated: 2026-04-16
---

# macOS App Proxy Connectivity Troubleshooting

Diagnose and fix applications on macOS that fail to connect through proxy/VPN, particularly when they don't automatically inherit system proxy settings. This skill focuses on the common scenario where apps like Telegram, Discord, or other network-dependent applications work without proxy but fail when system proxy is enabled.

## When to Use

Use this skill when:
- An app works fine without proxy/VPN but fails to connect when proxy is enabled
- The app doesn't automatically use macOS system proxy settings
- You've changed VPN/proxy software and apps stopped working
- Network-dependent apps show "Connecting..." indefinitely or time out

## Common Patterns

1. **App Store vs. Official Versions**: App Store versions often have stricter sandboxing and may not respect system proxy settings
2. **HTTP vs. SOCKS5**: Some apps work better with SOCKS5 proxies than HTTP proxies
3. **TUN Mode**: VPN software's TUN/global mode often solves proxy inheritance issues
4. **App-Specific Proxy Settings**: Many apps have internal proxy configuration options

## Diagnostic Flow

### Phase 1: Quick System Checks

```bash
# Check current network service proxy settings
networksetup -getsocksfirewallproxy Wi-Fi
networksetup -getwebproxy Wi-Fi
networksetup -getsecurewebproxy Wi-Fi

# Identify proxy service running
ps aux | grep -E '(clash|surge|v2ray|v2box|qv2ray|trojan|ssr|shadowsocks|proxy)' | grep -v grep

# Test proxy connectivity
curl -x http://127.0.0.1:6478 https://telegram.org -I --max-time 5
curl --socks5 127.0.0.1:6478 https://telegram.org -I --max-time 5
```

### Phase 2: Application-Specific Checks

```bash
# Check if app is running
ps aux | grep -i [appname] | grep -v grep

# Find app's configuration files
find ~/Library -name "*[appname]*" -type d 2>/dev/null
find ~/Library/Containers -name "*[appname]*" -type d 2>/dev/null

# Check app's plist preferences
find ~/Library/Containers -name "*.plist" 2>/dev/null | grep -i [appname]
```

### Phase 3: Network Path Verification

```bash
# Test direct connection (should fail if proxy is required)
curl https://telegram.org -I --max-time 5

# Test through proxy (should succeed)
curl -x http://127.0.0.1:6478 https://telegram.org -I --max-time 5

# Check listening proxy ports
lsof -i :6478
netstat -an | grep LISTEN | grep -E ':(6478|1080|1086|1087|7890)'
```

## Solution Strategies

### Strategy 1: App-Internal Proxy Configuration

For apps that support internal proxy settings (Telegram, Slack, Discord, etc.):

1. **Telegram**: Settings → Advanced → Connection Type → Use Proxy → Add Proxy
   - Type: HTTP or SOCKS5 (prefer SOCKS5 if available)
   - Server: `127.0.0.1`
   - Port: `6478` (or your proxy port)
   - Save and enable

2. **App-Specific Paths**:
   - Telegram: `Cmd + ,` → Advanced → Connection Type
   - Many apps: Settings → Network/Advanced → Proxy

### Strategy 2: Environment Variable Launch (Temporary)

Create a launch script for apps that ignore system settings:

```bash
#!/bin/bash
# Save as ~/launch-with-proxy.sh
env ALL_PROXY=http://127.0.0.1:6478 \
    HTTP_PROXY=http://127.0.0.1:6478 \
    HTTPS_PROXY=http://127.0.0.1:6478 \
    /Applications/Telegram.app/Contents/MacOS/Telegram &
```

Make executable and use to launch app: `chmod +x ~/launch-with-proxy.sh && ~/launch-with-proxy.sh`

### Strategy 3: VPN TUN/Global Mode (Recommended)

Enable TUN (virtual network interface) or global mode in your VPN software:

1. **Benefits**:
   - All traffic goes through VPN, no proxy inheritance issues
   - Works for ALL applications automatically
   - More reliable than per-app proxy configuration

2. **How to enable**:
   - Look for "TUN Mode", "Virtual Network Interface", or "Global Mode" in VPN app settings
   - May require app restart or system reboot

### Strategy 4: Proxy Rule Configuration

Check VPN software rules to ensure app domains are included:

```yaml
# Example Clash/V2Ray rule format
rules:
  - DOMAIN-SUFFIX,telegram.org,Proxy
  - DOMAIN-KEYWORD,telegram,Proxy
  - DOMAIN-SUFFIX,telegram.org,DIRECT  # If you want to bypass proxy
```

## Common Pitfalls

### Pitfall 1: Multiple Proxy Services Conflicting
- Check for multiple proxy services running simultaneously
- Disable unused proxy services
- Ensure only one proxy is managing system settings

### Pitfall 2: App Store Sandbox Restrictions
- App Store versions may have limited network access
- Solution: Download official version from app website
- Example: `https://telegram.org/dl/desktop/mac`

### Pitfall 3: IPv6 vs IPv4
- Some proxies only handle IPv4 traffic
- Disable IPv6 if having issues: `networksetup -setv6off Wi-Fi`

### Pitfall 4: Firewall/Antivirus Interference
- Temporarily disable firewall/antivirus to test
- Add app to firewall allowlist

## Verification Steps

After applying a solution:

1. **Test basic connectivity**:
   ```bash
   curl -x http://127.0.0.1:6478 https://telegram.org -I --max-time 5
   ```

2. **Test app-specific functionality**:
   - Telegram: Send message to @BotFather
   - Other apps: Perform core network operation

3. **Check app connection status**:
   - Look for "Proxy Connected" indicator
   - Network icon should show active connection

## Case Study: Telegram on macOS

### Problem
Telegram shows "Connecting..." indefinitely after switching VPN/proxy software.

### Diagnosis
1. System proxy set to `127.0.0.1:6478` ✅
2. Direct curl to telegram.org fails ❌
3. Curl through proxy succeeds ✅
4. Telegram is App Store version (sandboxed) ✅

### Solution Applied
Enabled TUN mode in VPN software → All traffic routed through VPN → Telegram connects successfully.

### Alternative Solutions
1. Telegram internal proxy settings (works but requires manual config)
2. Launch with env variables (works but temporary)
3. Download official Telegram version (more likely to respect system proxy)

## Resources

- macOS network troubleshooting: `man networksetup`
- Common proxy ports: `6478` (V2BOX), `7890` (Clash), `1080` (SOCKS5)
- Test URLs: `https://telegram.org`, `https://api.telegram.org`