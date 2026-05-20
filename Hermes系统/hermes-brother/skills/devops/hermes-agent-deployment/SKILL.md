---
name: hermes-agent-deployment
description: UMBRELLA — Clone, backup, and deploy a full Hermes Agent setup across machines. Covers packaging config, memories, skills, scripts, cron jobs, launchd plists, and auth files for headless/backup agents. Use when the user wants to replicate their Hermes setup to another machine, create a backup agent ("二弟"), or restore from a snapshot.
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, deployment, clone, backup, multi-machine, ops]
    related_skills: [hermes-agent, fnos-nas-backup]
---

# Hermes Agent Deployment

Clone, backup, and deploy a full Hermes Agent setup across machines. This covers the complete "贾维斯二弟" scenario — taking everything from one machine and making it work on another.

## What to Package

A full Hermes deployment includes these components:

```
hermes-deploy-v1/
├── install.sh                   ← One-click setup script
├── README.md                    ← Machine-specific instructions
│
├── hermes-env/                  ← Config + secrets (NEVER ship with real keys!)
│   ├── config.yaml              ← Full Hermes config
│   ├── .env                     ← API keys (blank template — fill on target)
│   ├── SOUL.md                  ← Agent identity
│   ├── auth.json                ← Credential pools (blank template)
│   └── memories/
│       ├── MEMORY.md            ← System notes
│       └── USER.md              ← User profile
│
├── skills/                      ← Full skill tree (find via ~/.hermes/skills/)
│   └── ...
│
├── scripts/                     ← Custom scripts + checkers
│   ├── checkers/
│   └── ...
│
├── launchd/                     ← macOS launchd plists for auto-start
│   ├── ai.hermes.gateway.plist
│   ├── com.hermes-webui.plist
│   ├── com.xiaohongshu.mcp.plist
│   └── ...
│
└── cron-jobs.json               ← Cron job definitions (restored via CLI or API)
```

## How to Package (Source Machine)

### 1. Create the deployment archive

```bash
# Create temp staging directory
mkdir -p /tmp/hermes-deploy/hermes-env/memories
mkdir -p /tmp/hermes-deploy/skills
mkdir -p /tmp/hermes-deploy/scripts/checkers
mkdir -p /tmp/hermes-deploy/launchd

# Copy config (strip secrets to templates for safety)
cp ~/.hermes/config.yaml /tmp/hermes-deploy/hermes-env/
cp ~/.hermes/SOUL.md /tmp/hermes-deploy/hermes-env/
cp ~/.hermes/memories/MEMORY.md /tmp/hermes-deploy/hermes-env/memories/
cp ~/.hermes/memories/USER.md /tmp/hermes-deploy/hermes-env/memories/

# Copy .env (blank out keys — user fills on target)
grep -v '=' ~/.hermes/.env > /tmp/hermes-deploy/hermes-env/.env.template

# Copy skills
cp -r ~/.hermes/skills/* /tmp/hermes-deploy/skills/ 2>/dev/null

# Copy scripts + checkers
cp -r ~/.hermes/scripts/* /tmp/hermes-deploy/scripts/ 2>/dev/null
cp -r ~/.hermes/scripts/checkers/* /tmp/hermes-deploy/scripts/checkers/ 2>/dev/null

# Copy launchd plists
cp ~/Library/LaunchAgents/*.hermes*.plist /tmp/hermes-deploy/launchd/ 2>/dev/null
cp ~/Library/LaunchAgents/com.hermes*.plist /tmp/hermes-deploy/launchd/ 2>/dev/null
cp ~/Library/LaunchAgents/com.xiaohongshu*.plist /tmp/hermes-deploy/launchd/ 2>/dev/null

# Export cron jobs (via hermes CLI)
hermes cron list --json > /tmp/hermes-deploy/cron-jobs.json 2>/dev/null || echo "{}" > /tmp/hermes-deploy/cron-jobs.json

# Create final tarball
cd /tmp && tar -czf ~/Desktop/hermes-deploy-v1.tar.gz hermes-deploy/
```

### 2. Write the install.sh script

The install script handles target-machine setup:

```bash
#!/bin/bash
# install.sh — Hermes Agent "二弟" Deployment Installer
set -e

HERMES_HOME="$HOME/.hermes"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📦 贾维斯二弟 — Hermes Agent Deployment Installer"
echo ""

# Step 1: Stop Hermes if running
echo "⏹️  Stopping Hermes..."
hermes gateway stop 2>/dev/null || true
launchctl bootout gui/$(id -u)/ai.hermes.gateway 2>/dev/null || true

# Step 2: Backup existing config if any
if [ -d "$HERMES_HOME" ]; then
    BACKUP="$HOME/.hermes.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📋 Backing up existing config to $BACKUP"
    mv "$HERMES_HOME" "$BACKUP"
fi

# Step 3: Install Hermes if not present
if ! command -v hermes &>/dev/null; then
    echo "🔧 Installing Hermes Agent..."
    curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
fi

# Step 4: Copy config, memories, SOUL
echo "📄 Copying configuration..."
mkdir -p "$HERMES_HOME"
cp -r "$SCRIPT_DIR/hermes-env/"* "$HERMES_HOME/"
mkdir -p "$HERMES_HOME/skills"
cp -r "$SCRIPT_DIR/skills/"* "$HERMES_HOME/skills/"
mkdir -p "$HERMES_HOME/scripts"
cp -r "$SCRIPT_DIR/scripts/"* "$HERMES_HOME/scripts/"

# Step 5: Install launchd plists
echo "🚀 Installing launchd services..."
mkdir -p "$HOME/Library/LaunchAgents"
for plist in "$SCRIPT_DIR/launchd/"*.plist; do
    cp "$plist" "$HOME/Library/LaunchAgents/"
done

# Step 6: Load services
echo "🔌 Loading launchd services..."
for plist in "$SCRIPT_DIR/launchd/"*.plist; do
    name=$(basename "$plist")
    launchctl bootstrap gui/$(id -u) "$HOME/Library/LaunchAgents/$name" 2>/dev/null || true
done

# Step 7: Restore cron jobs (manual step — requires API keys configured first)
echo ""
echo "⚠️  IMPORTANT: Before cron jobs will work, you must:"
echo "   1. Edit ~/.hermes/.env — paste your API keys"
echo "   2. Edit ~/.hermes/config.yaml — verify providers"
echo "   3. Run: hermes gateway start"
echo ""
echo "   To restore cron jobs after keys are configured:"
echo "   hermes cron create ...  # One by one (see cron-jobs.json)"

echo ""
echo "✅ 二弟部署完成！"
```

### 3. Ship to target machine

Options (in order of preference):
- **U盘/external drive**: `cp ~/Desktop/hermes-deploy-v1.tar.gz /Volumes/USB/`
- **NAS shared folder**: Copy to your NAS, then pull from target machine
- **AirDrop**: Finder → AirDrop to target Mac
- **网盘/微信**: Last resort for large files

## How to Deploy (Target Machine)

### Prerequisites

Target machine must have:
- macOS (Intel or Apple Silicon)
- Internet connection
- `brew` installed (for dependencies like sqlcipher)
- **Hermes Agent installed** (if not, install.sh will do it)

### Steps

```bash
# 1. Copy the tarball to target machine, then:
tar -xzf hermes-deploy-v1.tar.gz
cd hermes-deploy-v1

# 2. Edit API keys first!
cp hermes-env/.env.template hermes-env/.env
nano hermes-env/.env
# → Paste your DeepSeek, NVIDIA, Gemini, etc. API keys

# 3. Run the installer
bash install.sh

# 4. Verify
hermes doctor
hermes gateway status
hermes cron list
```

## ⚠️ Critical Pitfalls

### Never ship real API keys in the archive
- Use `.env.template` with placeholders like `DEEPSEEK_API_KEY=your_key_here`
- The user fills these in on the target machine
- **Exception**: If both machines share the same keys AND the transfer channel is secure (USB only, never network), you can include them — but still document what keys need to exist.

### Machine-specific differences to handle:
| Difference | What to fix |
|------------|-------------|
| **macOS version** | Launchd plists may need different paths. Check `whoami` differs. |
| **Intel vs Apple Silicon** | Binary paths differ (/usr/local/bin vs /opt/homebrew/bin). Update plists. |
| **OpenClaw** | May not be installed on target. Skip those plists or install OpenClaw first. |
| **Python packages** | `pip3 list` may differ. Install missing packages on demand. |
| **File paths** | Config references `/Users/mac/stock-robot` — update if username differs. |
| **Hostname** | Cron workdirs reference machine-specific paths. Update or use relative paths. |
| **MCP servers** | xiaohongshu-mcp needs to be installed separately on target (brew/go/launchd). |

### Cron jobs don't survive the migration
- Cron job definitions live in `state.db` which is NOT portable between machines
- They must be recreated via `hermes cron create` using the exported JSON
- Document each cron job's schedule + prompt in the README

### Hermes profile export/import
- `hermes profile export NAME` exists but only exports 1 profile's config + skills + memories
- It does NOT include: scripts, launchd plists, cron jobs, auth.json
- For full deployment, use the manual packaging approach above

## Verification Checklist

After deployment, verify:

```bash
hermes doctor                    # Config + deps OK
hermes config show               # Model/provider correct
hermes gateway status            # Platforms connected
hermes cron list                 # All jobs restored
hermes skills list               # All skills present
hermes memory status             # Memory loaded
cat ~/.hermes/memories/MEMORY.md # Memory file intact
cat ~/.hermes/memories/USER.md   # User profile intact
```

## Related Skills & References

- `hermes-agent` — General Hermes configuration, profiles, spawning
- `fnos-nas-backup` — Backing up config to FNOS NAS (alternative deployment channel)
- `references/offline-compute-cluster-plan.md` — Cron offloading to PC cluster (complementary strategy to full deployment)
