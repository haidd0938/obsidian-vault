# Apple Reminders + Notes Setup Journey

**User:** 老板 (macOS, username: mac)
**Date:** 2026-05-08 (updated)

## Machine Profile

- **OS:** macOS (Intel MacBook Pro)
- **Username:** mac (not haidd)
- **Shell:** bash/zsh
- **Network:** Outside home (cellular/VPN) — Homebrew auto-update causes 2-3 min delays
- **Remote access:** Cannot trigger macOS permission dialogs when user is away

## Setup Record

### remindctl — ✅ SUCCESS (Fully Operational)

| Step | Status | Notes |
|------|--------|-------|
| `brew install steipete/tap/remindctl` | ✅ | Installed from `steipete/tap` v0.2.0 |
| `remindctl authorize` | ✅ Full access | User was at keyboard, clicked Allow in dialog |
| `remindctl today` | ✅ Works | Can list/create/complete reminders |

**User's reminder lists that exist:**
- inbox (0)
- 个人 (0)
- 今天 (0)
- 工作 (0)
- 提醒 (0)
- **提醒事项 (5)** ← primary, has existing reminders
- 日常采购 (0)

### memo (Apple Notes) — ❌ NOT INSTALLED

| Step | Status | Duration | Notes |
|------|--------|----------|-------|
| `brew tap antoniorodr/memo` | ✅ | ~15s | Tapped successfully (13 files, 19.7KB) |
| `brew install antoniorodr/memo/memo` | ❌ | Timed out at 180s | Download stalled on slow network; try again on home WiFi |

## What Worked / Didn't

| Approach | Verdict | Why |
|----------|---------|-----|
| `remindctl` | ✅✅ Primary | Installed, authorized, works. Use for all personal reminders. |
| `osascript` for Reminders | ❌ Avoid | Hangs >15s on this Mac — AppleScript bridge unreliable |
| `shortcuts` CLI | ⚠️ Limited | Can only trigger pre-existing shortcuts, can't create dynamic reminders |
| Hermes cron job | ⚠️ Fallback only | Use only for agent-system tasks, NOT personal reminders |
| brew install on slow network | ⚠️ Needs patience | Always set `timeout=180`, consider `HOMEBREW_NO_AUTO_UPDATE=1` |
| memo brew install | ❌ Failed | Home WiFi worked for tap but stalled on download. Try again. |

## User Preference

- **User wants Apple Reminders (syncs to iPhone) over Telegram-only cron reminders** — this is the primary channel
- cron job reminders → only for agent tasks (bot alerts, automated reports)
- User is comfortable with terminal commands but prefers Web UI / minimal friction
- User is often away from Mac (mobile) — schedule setup tasks for when they confirm they're at the keyboard
- User confirmed "到家喊贾维斯" is the signal — they want to do NAS backup setup in person
