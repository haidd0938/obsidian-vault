---
name: macos-system-diagnostics
description: Comprehensive macOS system diagnostics — hardware, software, network, storage, and developer environment. Collect system information using standard macOS commands and present in a structured format.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [macos, system, diagnostics, hardware, configuration]
    homepage: https://github.com/NousResearch/hermes-agent
    related_skills: []
---

# macOS System Diagnostics

This skill provides a comprehensive checklist for gathering macOS system configuration information. Use when the user asks to "check system configuration", "diagnose hardware", or "review system specs".

## When to Use

- User wants to know their macOS system specifications
- Need to diagnose hardware compatibility or performance issues
- Collect environment information for debugging or setup
- Check system health and resource utilization

## Prerequisites

- macOS system (tested on macOS 10.15+)
- Standard UNIX utilities (pre-installed)
- Administrator privileges for some commands (optional)

## Step-by-Step Guide

### 1. Basic System Information

```bash
# Kernel and OS version
uname -a
sw_vers

# Hardware model
system_profiler SPHardwareDataType 2>/dev/null | grep -E "Model Name|Model Identifier|Serial Number|Boot ROM Version|SMC Version" | head -10

# Uptime and load
uptime
```

### 2. CPU and Memory

```bash
# CPU model
sysctl -n machdep.cpu.brand_string

# Core count
sysctl -n hw.ncpu

# Total RAM (in bytes)
sysctl -n hw.memsize

# Convert to human-readable (GB)
echo "RAM: $(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024)) GB"

# Swap usage
sysctl vm.swapusage
```

### 3. Graphics

```bash
# Graphics card information
system_profiler SPDisplaysDataType 2>/dev/null | head -30

# Check for both integrated and discrete GPUs
system_profiler SPDisplaysDataType 2>/dev/null | grep -A5 -B5 "Intel\|Radeon\|NVIDIA"
```

### 4. Storage

```bash
# Root filesystem usage
df -h /

# Detailed disk information (if needed)
diskutil list
```

### 5. Network

```bash
# Local IP address (en0 is typically primary ethernet/Wi-Fi)
ifconfig en0 | grep "inet " | awk '{print $2}'

# Alternative: use scutil
scutil --get LocalHostName
scutil --get HostName

# Check external IP (may be blocked by privacy settings)
# curl -s ifconfig.me

# Network proxy configuration
networksetup -listallnetworkservices
networksetup -getwebproxy Wi-Fi 2>/dev/null || echo "No Wi-Fi proxy"
networksetup -getwebproxy Ethernet 2>/dev/null || echo "No Ethernet proxy"

# Test proxy connectivity
echo "Testing proxy connectivity:"
curl -x http://127.0.0.1:6478 -I https://baidu.com --max-time 5 2>/dev/null | head -1
```

### 6. Power and Battery

```bash
# Battery status (for laptops)
pmset -g batt
```

### 7. Developer Environment

```bash
# Current user
whoami

# Timezone
date +%Z

# Git
which git && git --version | head -1

# Python
which python3 && python3 --version

# Node.js
which node && node --version 2>/dev/null || echo "Node not installed"

# Docker
which docker && docker --version 2>/dev/null || echo "Docker not installed"

# Homebrew
which brew && brew --version 2>/dev/null | head -1
```

### 8. System Load and Processes

```bash
# Load averages (from uptime)
uptime | grep -o "load averages:.*"

# Top processes (optional)
top -l 1 -o cpu -n 5 | tail -6

# Check for common proxy ports
netstat -an | grep LISTEN | grep -E ':(6478|1080|1086|1087|7890|10808|10809|20171|20172)'
```

### 9. Application Proxy Issues (Specific Diagnostics)

Use these commands when applications (Telegram, browsers, etc.) report network connectivity issues despite system proxy being configured:

```bash
# 1. Check if system proxy is actually enabled
networksetup -getwebproxy Wi-Fi

# 2. Test proxy server connectivity
curl -v http://127.0.0.1:6478 2>&1 | head -20

# 3. Test external connectivity through proxy
curl -x http://127.0.0.1:6478 -I https://baidu.com --max-time 10

# 4. Test external connectivity without proxy (direct)
curl -I https://baidu.com --max-time 10

# 5. Check for running proxy applications
ps aux | grep -E '(clash|surge|v2ray|v2box|proxy)' | grep -v grep

# 6. Check environment variables for proxy settings
env | grep -i proxy

# 7. Check common proxy configuration files
ls -la ~/.config/*proxy* 2>/dev/null || true
ls -la /etc/*proxy* 2>/dev/null || true

# 8. Diagnose specific application issues (e.g., Telegram)
# a. Check if application is running
ps aux | grep -i telegram | grep -v grep

# b. Check application's network connections
lsof -i -P -n | grep telegram

# 9. Common macOS proxy patterns:
# - System proxy (127.0.0.1:6478) ≠ Application using it
# - Applications may need internal proxy configuration
# - Some apps bypass system proxy for specific domains
```

## Complete Diagnostic Script

For a quick one-liner that captures most information:

```bash
{
  echo "=== SYSTEM DIAGNOSTICS ==="
  echo "Date: $(date)"
  echo ""
  echo "--- Basic Info ---"
  uname -a
  sw_vers
  echo ""
  echo "--- Hardware ---"
  sysctl -n machdep.cpu.brand_string
  echo "Cores: $(sysctl -n hw.ncpu)"
  echo "RAM: $(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024)) GB"
  echo ""
  echo "--- Storage ---"
  df -h /
  echo ""
  echo "--- Network ---"
  ifconfig en0 | grep "inet " | awk '{print $2}' | xargs echo "Local IP:"
  echo ""
  echo "--- Developer Tools ---"
  which git >/dev/null && echo "Git: $(git --version | head -1)" || echo "Git: Not found"
  which python3 >/dev/null && echo "Python: $(python3 --version)" || echo "Python3: Not found"
  which node >/dev/null && echo "Node: $(node --version 2>/dev/null)" || echo "Node: Not found"
} | tee /tmp/system-diag-$(date +%Y%m%d).txt
```

## Output Formatting

When presenting results to the user, organize information into clear sections:

1. **System Overview** — OS version, kernel, uptime
2. **Hardware Configuration** — CPU, RAM, graphics, model
3. **Storage & Memory** — disk usage, swap
4. **Network** — IP addresses, hostname
5. **Power** — battery status (if applicable)
6. **Developer Environment** — installed tools and versions
7. **Performance** — load averages, running processes

## Pitfalls and Solutions

1. **Permission issues**: Some commands require sudo. Skip or note when permission denied.
2. **Network commands blocked**: External IP check may be blocked by privacy settings. Provide alternative or skip.
3. **Missing tools**: Use `which` checks before calling commands to avoid errors.
4. **Different macOS versions**: Commands like `system_profiler` output format may vary. Use `head`/`grep` to extract key info.
5. **Battery commands on desktops**: `pmset -g batt` returns "No battery" on desktops. Handle gracefully.

## Verification

After running diagnostics, verify that:
- All major hardware components are detected (CPU, RAM, graphics)
- Storage usage is reported correctly
- Network interfaces show valid IP addresses
- Developer tools report correct versions

## Related Skills

- `references/nodejs-upgrade-proxy-diagnostics.md` — Node.js upgrade + proxy troubleshooting (absorbed from `macos-upgrade-node-with-brew-fallback`)

## Updates

- 2026-04-15: Initial version with comprehensive macOS diagnostic commands.
