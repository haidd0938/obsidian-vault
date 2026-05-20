# osascript Notes Cookbook

Proven commands for this Mac (macOS, user "mac", 2026-05-08).

## Create a note
```python
import subprocess, json

result = subprocess.run([
    'osascript', '-e',
    'tell application "Notes" to make new note in folder "Notes" with properties {name:"' + title + '", body:"' + body + '"}'
], capture_output=True, text=True, timeout=10)
# Returns: note id x-coredata://.../ICNote/pNNN
```

## List folder names
```bash
osascript -e 'tell application "Notes" to get name of every folder'
```
→ `Inbox, Notes, Notes, Notes, 个人, 工作, 知识与目标`

## Count total notes
```bash
osascript -e 'tell application "Notes" to get count of notes'
```
→ `43` (as of 2026-05-08)

## List notes in a specific folder
```bash
osascript -e 'tell application "Notes" to get name of every note whose container is folder "Notes"'
```

## KNOWN ISSUES
- `get name of every note` (unscoped) hangs → always scope by folder
- osascript calls to Reminders.app hang consistently on this machine → never use for reminders
- Body content returned in HTML format (`<div>...` wrapped)
