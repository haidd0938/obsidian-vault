---
name: apple-reminders
description: "Apple Reminders via remindctl: add, list, complete."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Reminders, tasks, todo, macOS, Apple]
prerequisites:
  commands: [remindctl]
---

# Apple Reminders

Use `remindctl` to manage Apple Reminders directly from the terminal. Tasks sync across all Apple devices via iCloud.

## Prerequisites

- **macOS** with Reminders.app
- Install: `brew install steipete/tap/remindctl`
- Grant Reminders permission when prompted
- Check: `remindctl status` / Request: `remindctl authorize`

## When to Use

- User mentions "reminder" or "Reminders app"
- Creating personal to-dos with due dates that sync to iOS
- Managing Apple Reminders lists
- User wants tasks to appear on their iPhone/iPad

## When NOT to Use

- Scheduling agent alerts → use the cronjob tool instead
- Calendar events → use Apple Calendar or Google Calendar
- Project task management → use GitHub Issues, Notion, etc.
- If user says "remind me" but means an agent alert → clarify first

## Fallbacks (when remindctl is unavailable)

`brew install steipete/tap/remindctl` can time out on slow networks. If `remindctl` is not installed or brew fails:

### Fallback 1: macOS Shortcuts CLI

The `shortcuts` command (built-in on macOS) can trigger pre-existing shortcuts, but cannot create ad-hoc reminders natively:

```bash
# List available shortcuts
shortcuts list

# Run a shortcut by name (only if one exists for reminders)
shortcuts run "Create Reminder"
```

Limitations: `shortcuts` CLI cannot dynamically set reminder titles/dates — it only triggers a pre-built shortcut. For this user (mac), no reminder-centric shortcut exists.

### Fallback 2: AppleScript (osascript)

Can theoretically create reminders, but **often hangs** (timeout >15s on some macOS setups including this user's machine):

```bash
osascript -e 'tell application "Reminders" to make new reminder with properties {name:"Test", due date: (current date) + 60}'
```

⚠️ **This approach is unreliable.** On this user's Mac, `osascript` calls to Reminders consistently time out (>15s). Do NOT use as primary approach.

### Fallback 3: Hermes Cron Job (recommended alternative)

When Apple Reminders integration fails, use `cronjob` tool to create a scheduled Telegram message instead. This is **more reliable** and won't hang:

```bash
# Create a cron job that sends a Telegram reminder at 9 PM
cronjob(action='create', name='提醒标题', schedule='0 21 * * *', 
        prompt='提醒内容')
```

**Comparison:**

| Method | Reliability | Syncs to iPhone | Setup needed |
|--------|-------------|-----------------|--------------|
| remindctl | ✅ High | ✅ Yes | brew install |
| Shortcuts | ⚠️ Limited | ✅ Yes | Pre-built shortcut |
| osascript | ❌ Hangs | ✅ Yes | None |
| Cron job | ✅✅ High | ❌ Telegram only | None |

**Decision tree when user asks for a reminder:**  
1. `which remindctl` → if found, use it (Apple Reminders → syncs to iPhone)  
2. `remindctl status` → check if "Full access" is confirmed. If "Not determined", user must be at keyboard to click Allow dialog  
3. Create with: `remindctl add --title "内容" --due "YYYY-MM-DD HH:mm" --list "提醒事项"`  
4. List the user's reminder lists first with `remindctl list` if you're unsure which list to use  
5. If remindctl not installed or not accessible → use cronjob (Telegram fallback)

This user's setup (as of 2026-05-08): remindctl IS installed (v0.2.0) with Full access. The "提醒事项" list exists and is the primary list (5 reminders visible). cron-based reminders should only be used for agent tasks, not personal reminders — this user wants personal reminders to sync to iPhone via Apple Reminders.

**User voice/text rule:** When user sends voice → reply with voice (TTS). When user sends text → reply with text. Embedded here because reminders often trigger voice replies.

## Quick Reference

### Manage Lists

```bash
remindctl list               # List all lists
remindctl list Work          # Show specific list
remindctl list Projects --create    # Create list
remindctl list Work --delete        # Delete list
```

### Create Reminders

```bash
remindctl add "Buy milk"
remindctl add --title "Call mom" --list Personal --due tomorrow
remindctl add --title "Meeting prep" --due "2026-02-15 09:00"
```

### Complete / Delete

```bash
remindctl complete 1 2 3          # Complete by ID
remindctl delete 4A83 --force     # Delete by ID
```

### Output Formats

```bash
remindctl today --json       # JSON for scripting
remindctl today --plain      # TSV format
remindctl today --quiet      # Counts only
```

## Date Formats

Accepted by `--due` and date filters:
- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## Rules

1. When user says "remind me", clarify: Apple Reminders (syncs to phone) vs agent cronjob alert
2. Always confirm reminder content and due date before creating
3. Use `--json` for programmatic parsing
4. **After creating a reminder, show the user their upcoming list** — run `remindctl today` or `remindctl week` to confirm it landed correctly. This builds trust and lets the user verify the reminder is there.

## Troubleshooting

### `brew install` times out
- **Cause**: Slow network (common when user is mobile/outside home). brew pulls from GitHub which can be slow over cellular or VPN. Homebrew auto-update adds significant delay.
- **Solution**: Try again on a faster network (home WiFi). If auto-update is the bottleneck, skip it:
  ```bash
  HOMEBREW_NO_AUTO_UPDATE=1 brew install steipete/tap/remindctl
  ```
- Keep `timeout=180` in terminal tool calls — with auto-update it can take 2-3 minutes.
- **This user's Mac (2026-05-08)**: `HOMEBREW_NO_AUTO_UPDATE=1 brew install steipete/tap/remindctl` succeeded at a remote network in ~2s with no auto-update. The formula itself is tiny (4 files, 1.6MB). The bottleneck is brew's auto-update, not the download. Always set `HOMEBREW_NO_AUTO_UPDATE=1` proactively.

### `remindctl authorize` hangs
- **Cause**: Triggers a macOS permission dialog. If user is not at the keyboard, the command blocks indefinitely waiting for them to click "Allow".
- **Solution**: Only run `remindctl authorize` when user confirms they are at their Mac. Otherwise, tell them to run it manually and click Allow in the system dialog (System Settings > Privacy & Security > Reminders).

### `osascript` hangs on Reminders
- **Cause**: `System Events` process can detect Reminders.app exists but AppleScript bridge to Event Kit is unreliable on some macOS versions.
- **Diagnosis**: `osascript -e 'tell application "System Events" to exists (processes where name is "Reminders")'` — if this returns "true" but creating reminders hangs, the Reminders.app AppleScript dictionary is non-responsive.
- **No known fix**: This is a macOS limitation. Use cronjob as alternative.
