---
name: imessage
description: Send and receive iMessages/SMS via the imsg CLI on macOS.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [iMessage, SMS, messaging, macOS, Apple]
prerequisites:
  commands: [imsg]
---

# iMessage

Use `imsg` to read and send iMessage/SMS via macOS Messages.app.

## Prerequisites

- **macOS** with Messages.app signed in
- Install: `HOMEBREW_NO_AUTO_UPDATE=1 brew install steipete/tap/imsg`
- Post-install: `imsg` binary at `/usr/local/bin/imsg`
- Grant Full Disk Access for terminal (System Settings → Privacy & Security → Full Disk Access)
- Grant Automation permission for Messages.app when prompted

### ⚠️ Installation Pitfalls

1. **Homebrew auto-update timeout**: Always prepend `HOMEBREW_NO_AUTO_UPDATE=1` — the auto-update can hang for 60+ seconds on slow connections, causing command timeout. Without it, first install may fail silently despite `brew install` succeeding later.
2. **PATH**: imsg installs to `/usr/local/bin/imsg`. If `which imsg` returns nothing, use the full path or re-source shell config.
3. **Full Disk Access**: If you get `authorization denied (code: 23)` after installation, the terminal hasn't been granted Full Disk Access. Open System Settings → Privacy & Security → Full Disk Access → add your terminal app. The Messages database at `~/Library/Messages/chat.db` requires this.
4. **Verification**: After setup, check with `imsg chats --limit 5 --json` or `ls ~/Library/Messages/chat.db` to confirm access.

## When to Use

- User asks to send an iMessage or text message
- Reading iMessage conversation history
- Checking recent Messages.app chats
- Sending to phone numbers or Apple IDs

## When NOT to Use

- Telegram/Discord/Slack/WhatsApp messages → use the appropriate gateway channel
- Group chat management (adding/removing members) → not supported
- Bulk/mass messaging → always confirm with user first

## Quick Reference

### List Chats

```bash
imsg chats --limit 10 --json
```

### View History

```bash
# By chat ID
imsg history --chat-id 1 --limit 20 --json

# With attachments info
imsg history --chat-id 1 --limit 20 --attachments --json
```

### Send Messages

```bash
# Text only
imsg send --to "+14155551212" --text "Hello!"

# With attachment
imsg send --to "+14155551212" --text "Check this out" --file /path/to/image.jpg

# Force iMessage or SMS
imsg send --to "+14155551212" --text "Hi" --service imessage
imsg send --to "+14155551212" --text "Hi" --service sms
```

### Watch for New Messages

```bash
imsg watch --chat-id 1 --attachments
```

## Service Options

- `--service imessage` — Force iMessage (requires recipient has iMessage)
- `--service sms` — Force SMS (green bubble)
- `--service auto` — Let Messages.app decide (default)

## Rules

1. **Always confirm recipient and message content** before sending
2. **Never send to unknown numbers** without explicit user approval
3. **Verify file paths** exist before attaching
4. **Don't spam** — rate-limit yourself

## Example Workflow

User: "Text mom that I'll be late"

```bash
# 1. Find mom's chat
imsg chats --limit 20 --json | jq '.[] | select(.displayName | contains("Mom"))'

# 2. Confirm with user: "Found Mom at +1555123456. Send 'I'll be late' via iMessage?"

# 3. Send after confirmation
imsg send --to "+1555123456" --text "I'll be late"
```
