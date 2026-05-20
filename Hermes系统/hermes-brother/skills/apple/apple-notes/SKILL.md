---
name: apple-notes
description: "Manage Apple Notes via memo CLI or osascript fallback: create, search, edit."
version: 1.0.1
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [Notes, Apple, macOS, note-taking]
    related_skills: [obsidian]
prerequisites:
  commands: [memo]
---

# Apple Notes

Use `memo` (preferred) or osascript fallback to manage Apple Notes. Notes sync across all Apple devices via iCloud.

## Prerequisites

- **macOS** with Notes.app
- Install memo: `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
  - ⚠️ `brew tap` clones a GitHub repo; `brew install` downloads a binary. Both are slow on remote connections.
  - Speed up: `HOMEBREW_NO_AUTO_UPDATE=1 brew install antoniorodr/memo/memo` with `timeout=300`
  - ❌ Do NOT `pip install memo` — that installs `koaning/memo` (unrelated Python package)
  - If brew fetch stalls, the background process may still be downloading — check with `brew list --versions memo` on retry. On this Mac (2026-05-08), brew's background download queue continued after `timeout=180` killed the foreground task; a second attempt at `timeout=300` succeeded.
- Grant Automation access to Notes.app when prompted (System Settings → Privacy → Automation)

## Status on this Mac (2026-05-08)

**memo v0.5.2 installed** via `brew install antoniorodr/memo/memo` (took ~2 min total across two attempts).
- Install tip: use `HOMEBREW_NO_AUTO_UPDATE=1` + `timeout=300`. Even when brew's foreground `timeout` fires, the background download queue (`brew fetch` subprocess) may **continue running**. A second invocation can complete instantly because dependencies are already fetched.
- `memo notes` — works, lists 43 notes across 7 folders
- `memo notes -s "query"` — fuzzy search works
- `memo notes -f "Folder"` — filter by folder works
- `memo notes -v N` — view note content by list index works
- `memo notes -a` — INTERACTIVE ONLY. Opens vim. Cannot accept piped/heredoc input. For automated creation, use osascript fallback.
- `memo notes -nc` — bypass cache, force refresh

**When memo is available:** use for reading/searching only. For writing: use osascript fallback.

## When to Use

- User asks to create, view, or search Apple Notes
- Saving information to Notes.app for cross-device sync (iPhone/iPad/Mac)
- Organizing notes into folders
- Exporting notes

## When NOT to Use

- Obsidian vault management → use the `obsidian` skill
- Quick agent-only notes → use the `memory` tool instead
- Reminders/tasks → use the `apple-reminders` skill instead

## Primary Method: memo CLI

### View Notes

```bash
memo notes                        # List all notes (this machine: 43 notes)
memo notes -f "Folder Name"       # Filter by folder
memo notes -s "query"             # Fuzzy search notes
memo notes -v N                   # View note #N from the list
memo notes -nc                    # Bypass cache, fetch fresh data
```

### ⚠️ Create Notes — DO NOT use `memo notes -a`

The `-a` flag opens vim interactively. It **cannot accept piped/heredoc input**. It will fail silently (opens vim, gets no tty, exits with "Note creation cancelled").

Instead, for automated creation, use the **osascript fallback** (see below).

### Edit / Delete / Move / Export

```bash
memo notes -e                     # Interactive selection to edit
memo notes -d                     # Interactive selection to delete
memo notes -m                     # Move note to folder
memo notes -ex                    # Export to HTML/Markdown
```

## Fallback: osascript (for writing notes)

Memo is installed and works for reading/searching. But `memo notes -a` is interactive-only (opens vim). For **automated creation**, use osascript instead.

### Check if osascript works for Notes

```bash
# Test: list folders
osascript -e 'tell application "Notes" to get name of every folder'

# Test: count notes
osascript -e 'tell application "Notes" to get count of notes'
```

### Create a note

```python
# Python (recommended over raw osascript — handles timeout better)
import subprocess

result = subprocess.run([
    'osascript', '-e',
    'tell application "Notes" to make new note in folder "Notes" with properties {name:"标题", body:"内容"}'
], capture_output=True, text=True, timeout=10)
```

Or raw bash:
```bash
osascript -e 'tell application "Notes" to make new note in folder "Notes" with properties {name:"标题", body:"内容"}'
```

### Available folders (this user's Mac, 2026-05-08):
- `Inbox` (inbox)
- `Notes`
- `个人`
- `工作`
- `知识与目标`

### List recent notes

```bash
osascript -e 'tell application "Notes" to get name of every note whose container is folder "Notes"'
```

⚠️ Warning: querying ALL notes via `get name of every note` can hang/take >15 seconds. Always scope by folder.

### Body format

Notes body is HTML by default. When creating with osascript, body content is plain text. When reading back, it returns wrapped in `<div>` tags.

## Rules

1. First check if `memo` is available: `which memo`. If yes, use it.
2. If memo not installed: try `brew install` with `HOMEBREW_NO_AUTO_UPDATE=1` and `timeout=120`.
3. If brew fails: use osascript fallback via Python subprocess.
4. When using osascript: always scope queries to a specific folder to avoid hangs.
5. ❌ Do NOT `pip install memo` — wrong package.
