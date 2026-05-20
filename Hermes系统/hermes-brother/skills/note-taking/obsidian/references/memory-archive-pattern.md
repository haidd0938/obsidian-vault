# Memory Archive Pattern — Obsidian as Memory Backup

## Problem
Hermes Agent's persistent memory (`memory` tool) has a 2,200-character limit. When it fills up (~95%), new facts can't be stored. The user needs to free space but wants a retrievable record of what was in memory.

## Solution: Archive to Obsidian Before Cleaning

### Step 1: Dump all memory entries
Use the `memory` tool with `action=add` + a placeholder to force a full dump of all entries (the response includes the full list):

```
memory(action='add', target='memory', content='=== PLACEHOLDER ===')
```

The response contains an `entries` array with every stored memory string.

### Step 2: Create an Obsidian archive note
Write a comprehensive `.md` file to the vault:

```
路径: /Users/mac/Documents/Obsidian Vault/🧠 记忆归档_YYYY-MM-DD.md
```

**Archive note structure:**
- YAML frontmatter: `created`, `updated`, `type: archive`, `description`
- Sectioned by category: 系统环境, Hermes配置, 技能与工具, 自动化任务, 项目相关
- Tables for structured data (accounts, paths, credentials)
- Footer with entry count

### Step 3: Remove stale entries from memory
Use `memory(action='remove', target='memory', old_text='<unique substring>')` for each entry being cleaned.

**Remove old_text parameter:** The `old_text` is the `content` of the entry to match against, NOT a key name. Provide a short unique substring from the entry text.

**Which entries to keep vs. remove:**
| Keep | Remove |
|------|--------|
| System/env facts (vault path, username, file quirks) | Dated achievements (specific dates, completed workflows) |
| Active project credentials (API keys, paths) | Already-documented skills |
| Active workflow references (cron jobs, automation) | One-time fixes and workarounds |
| User preferences (format, style) | Session-specific task outcomes |

**Aim for ~30% memory usage after cleanup** (was 95%, cleaned to ~650 chars = 29%).

### Step 4: Verify archive
```
ls -la "/Users/mac/Documents/Obsidian Vault/🧠 记忆归档_YYYY-MM-DD.md"
```

## MCP Consideration
User asked if MCP could serve as memory storage. **Answer: Not worth it.**
- Existing MCP memory servers (e.g., `@anthropic/memory-server`) are the same local-JSON-file approach under the hood
- Building a custom MCP server for this purpose is disproportionate overhead
- Obsidian archive + session_search gives the same retrievability with zero infrastructure

## Pitfalls
1. **memory remove uses `old_text`, NOT `content`** — the parameter name is `old_text`, not `content`. Common mistake.
2. **Remove one entry at a time** — each `remove` call handles one entry. No batch remove.
3. **Memory entries may overlap in text** — ensure `old_text` uniquely identifies the target entry by including enough context.
4. **Placeholder entry must be removed** — after dumping, don't forget to remove the `=== PLACEHOLDER ===` entry.
5. **Archive note doesn't auto-sync** — the Obsidian note is a static snapshot. New memory entries added after cleanup are not reflected in the archive. That's intentional — the archive is a historical record, not a live backup.

## Example Flow (from 2026-05-08 session)
```
Memory at: 16 entries, 95% full (2,098/2,200 chars)
→ Dumped all entries via placeholder trick
→ Wrote archive to 项目中心/🧠 记忆归档_2026-05-08.md
→ Removed 11 dated entries (Web UI versions, API key notes, feature completion dates)
→ Kept 5 stable entries (system env, vault path, file pitfalls, gubi brain)
→ Result: 5 entries, 29% full (648 chars)
```
