---
name: fnos-nas-backup
description: Configure automated backups to 飞牛NAS (FNOS) via SMB + rsync + launchd on macOS. Covers web API interactions, SMB mounting, script creation, and cron scheduling.
triggers: 飞牛NAS, FNOS, NAS备份, 备份到NAS, obsidian backup, rsync launchd, smb backup, fnos api
---

# 飞牛NAS (FNOS) Backup — macOS Automated Backup

Configure periodic backups from macOS to 飞牛NAS via SMB, driven by rsync + launchd.

## Architecture

```
macOS  ←SMB→  FNOS NAS
  │                │
  │  rsync         │ obsidian-backup/
  │  --delete      │   ObsidianVault/
  │                │     (mirror of source)
  │ launchd        │
  │ (hourly cron)  │
```

## Discovery: Find the NAS on LAN

```bash
# Ping common home subnets
ping -c1 -W1 192.168.1.5  # try known IP
ping -c1 -W1 192.168.31.115  # try fallback subnet

# Scan subnet for open ports (5666 = FNOS web UI default)
for i in $(seq 1 254); do
  (echo >/dev/tcp/192.168.1.$i/5666) 2>/dev/null && echo "Found: 192.168.1.$i"
done

# Check ARP cache
arp -a | grep -i "fnos\|飞牛"

# mDNS discovery
dns-sd -B _http._tcp local | head -20
```

## Web UI: Headless File/Folder Creation via API

The FNOS web UI's "New Folder" button can be invisible or broken in certain views. **Use the REST API directly:**

```bash
# Login first (get session cookie)
curl -s -c /tmp/fnos_cookies.txt \
  -X POST "http://NAS_IP:5666/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS"}'

# Create folder (API endpoint: fnos/fs/file/mkdir)
curl -s -b /tmp/fnos_cookies.txt \
  -X POST "http://NAS_IP:5666/fnos/fs/file/mkdir" \
  -H "Content-Type: application/json" \
  -d '{"path":"/","name":"foldername"}'

# List folder contents
curl -s -b /tmp/fnos_cookies.txt \
  "http://NAS_IP:5666/fnos/fs/file/list?path=/" \
  | python3 -m json.tool
```

**Known web UI quirks:**
- "新建共享文件夹" button may not render in headless browser. Use API directly.
- Page navigation via `document.querySelector` may fail if elements are shadow DOM or lazy-loaded.
- Always fall back to direct API calls when UI interaction fails.

## Step 1: Create Shared Folder on NAS

Use the API above to create `obsidian-backup` (or your preferred name). Verify it appeared:

```bash
curl -s -b /tmp/fnos_cookies.txt \
  "http://NAS_IP:5666/fnos/fs/file/list?path=/" \
  | python3 -c "import sys,json; data=json.load(sys.stdin); print([f['name'] for f in data.get('data',{}).get('files',[])])"
```

## Step 2: SMB Mount on macOS

### One-time setup (user must do this):
1. In Finder: `⌘K` → `smb://NAS_IP` → select the shared folder
2. Login with NAS credentials, **check "Remember password in keychain"**
3. After mounting, the folder appears at `/Volumes/<foldername>/`

### Auto-mount in backup script (avoids sudo):
```bash
if [ ! -d "/Volumes/obsidian-backup" ]; then
    open "smb://192.168.1.5/obsidian-backup"
    sleep 5
fi
```

**Pitfall:** `mount_smbfs` requires sudo on modern macOS, which means terminal password prompt. Use `open smb://...` instead — macOS handles keychain-stored credentials transparently.

## Step 3: Backup Script

Template at `/Users/mac/scripts/backup-obsidian.sh`:

```bash
#!/bin/bash
SOURCE="/Users/mac/Documents/Obsidian Vault/"
DEST="/Volumes/obsidian-backup/ObsidianVault"
LOG="/Users/mac/scripts/backup-obsidian.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Mount if needed
if [ ! -d "/Volumes/obsidian-backup" ]; then
    open "smb://192.168.1.5/obsidian-backup"
    sleep 5
fi

if [ ! -d "/Volumes/obsidian-backup" ]; then
    echo "[$TIMESTAMP] ❌ Mount failed" >> "$LOG"
    exit 1
fi

echo "[$TIMESTAMP] 🚀 Starting backup..." >> "$LOG"
rsync -avz --delete \
    --exclude=".obsidian/workspace.json" \
    --exclude=".obsidian/workspace" \
    --exclude=".DS_Store" \
    --exclude="__pycache__/" \
    --exclude=".trash/" \
    "$SOURCE" "$DEST" >> "$LOG" 2>&1
echo "[$TIMESTAMP] ✅ Done" >> "$LOG"
```

## Step 4: launchd plist (Hourly Cron)

Location: `~/Library/LaunchAgents/com.obsidian.backup.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.obsidian.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/mac/scripts/backup-obsidian.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/mac/scripts/backup-obsidian.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/mac/scripts/backup-obsidian.log</string>
    <key>ThrottleInterval</key>
    <integer>3600</integer>
</dict>
</plist>
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.backup.plist
launchctl list | grep "com.obsidian"
```

## Step 5: Shell Alias (Manual Trigger)

```bash
alias backup-obsidian='bash /Users/mac/scripts/backup-obsidian.sh && echo "📋 Last 5 log lines:" && tail -5 /Users/mac/scripts/backup-obsidian.log'
```

Add to `~/.zshrc` and `source ~/.zshrc`.

## User Preferences (this specific environment)

- **NAS:** 飞牛NAS, hostname haidd0938, IP 192.168.1.5, web port 5666
- **Mac user:** `mac` (not `haidd`), Intel x86_64, macOS
- **Vault path:** `/Users/mac/Documents/Obsidian Vault/` (with space — always quote)
- **Credentials:** username `haidd`, password stored in macOS keychain via Finder SMB mount
- **Backup frequency:** every hour (at :00)
- **Launch agent label:** `com.obsidian.backup`

## Verification

```bash
# Check launchd status
launchctl list | grep com.obsidian.backup

# Read backup log
cat /Users/mac/scripts/backup-obsidian.log

# List backup destination
ls -la /Volumes/obsidian-backup/ObsidianVault/
```
