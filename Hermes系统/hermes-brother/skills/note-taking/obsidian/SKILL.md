---
name: obsidian
description: Read, search, and create notes in the Obsidian vault.
---

# Obsidian Vault

**Location:** Set via `OBSIDIAN_VAULT_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/Documents/Obsidian Vault`.

**⚠️ Tip: NEVER use relative paths with `write_file` for Obsidian — they silently fail. Always use the full absolute vault path.**

Note: Vault paths may contain spaces - always quote them.

## Get the correct vault path

Find the actual vault path if unsure:

```bash
# Read Obsidian config for vault path
cat ~/Library/Application\ Support/obsidian/obsidian.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(v['path']) for v in d['vaults'].values()]"
```

## Read a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
cat "$VAULT/Note Name.md"
```

## List notes

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# All notes
find "$VAULT" -name "*.md" -type f

# In a specific folder
ls "$VAULT/Subfolder/"
```

## Search

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"

# By filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# By content
grep -rli "keyword" "$VAULT" --include="*.md"
```

## Find the correct vault path

**Do NOT assume the path.** Verify it first:

```bash
cat ~/Library/Application\ Support/obsidian/obsidian.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(v['path']) for v in d['vaults'].values()]"
```

The vault path may differ from `~/Documents/Obsidian Vault/` — the Obsidian config is the source of truth. For this user (`mac`), the vault is at `/Users/mac/Documents/Obsidian Vault/`.

## Create a note

**ALWAYS use the absolute vault path.** Relative paths with `write_file` silently create files outside the vault (the tool reports success but the file doesn't appear in Obsidian).

```bash
VAULT="/Users/mac/Documents/Obsidian Vault"
write_file "$VAULT/Folder/Note Name.md" "Content here."
```

### Create notes in subdirectories

To organize notes in folders (e.g. `技能学院/AI与模型/`), ensure the directory exists first:

```bash
VAULT="/Users/mac/Documents/Obsidian Vault"
mkdir -p "$VAULT/技能学院/AI与模型"
write_file "$VAULT/技能学院/AI与模型/some-note.md" "# Title\n\nContent"
```

### ⚠️ CRITICAL PITFALL: Verify written files

`write_file` can report success even when the file was written to the wrong path. **Always verify** the file actually landed where expected:

```bash
VAULT="/Users/mac/Documents/Obsidian Vault"
# After writing, immediately check existence:
ls -la "$VAULT/skill学院/Folder/skill-name.md"
# Or search for it:
find "$VAULT" -name "skill-name.md" -type f
```

If the file is missing, you probably used a relative path or wrong base path — retry with the full absolute path confirmed from the Obsidian config.

**🕳️ Common failure mode:** Using `search_files` (tool) to verify — it can return false results. Always use `ls -la` or `find` via terminal for confirmation. In the May 2026 "82笔记" incident, files were reported as written but never actually appeared because `search_files` couldn't find them across the full vault, leading to a false sense of success. The correct approach: `ls -1 "$VAULT/TargetFolder/" | wc -l` to count files, then spot-check 2-3 by reading them.

### Creating notes at scale (batch generation)

For generating many notes in one go (e.g., creating a project catalog from a local directory):

```python
from hermes_tools import write_file

VAULT = "/Users/mac/Documents/Obsidian Vault"

# 1. Define notes as a list of (filename, content) tuples
notes = [
    ("Folder/Project Alpha.md", "# Project Alpha\n\nContent here..."),
    ("Folder/Project Beta.md", "# Project Beta\n\nContent here..."),
]

# 2. Loop + write_file
success = 0
for fname, content in notes:
    path = f"{VAULT}/{fname}"
    write_file(path=path, content=content)
    success += 1

# 3. VERIFY by counting files (NOT search_files tool!)
#    Use terminal + ls:
#    ls -1 "$VAULT/Folder/" | wc -l
```

**⚠️ Pitfall:** `write_file` reports success per-call in the tool output. Don't trust that alone. After the loop, run `ls -1 "$VAULT/Folder/" | wc -l` to confirm the right count. If count is wrong, the path was wrong — retry with the absolute vault path.

### Project index from filesystem (catalog pattern)

When asked to catalog local projects into Obsidian notes:

1. **List the source directory** — `ls -1 /path/to/projects/` to get all folders
2. **Gather metadata per folder** — file count via `find "$dir" -type f | wc -l`, sample filenames via `ls -1 "$dir" | head -5`
3. **Generate notes** — one `.md` per project with YAML frontmatter (status, type, category) + local path link + file count + empty sections for progress and todos
4. **Place in a single folder** like `项目中心/` — do NOT scatter across subdirs unless the vault already has a clear hierarchy
5. **Verify with `ls -1 | wc -l`** — never trust `search_files` for batch verification

**Relevant references:**
- `references/project-catalog-example.md` — example of the generated note format and the `execute_code` loop pattern used.
- `references/memory-archive-pattern.md` — how to dump memory to Obsidian before cleaning, with the 2,200-char cleanup workflow.

### 技能卡片格式 (简介+使用方法+案例) — STANDARD FORMAT

**Every skill card MUST use this exact 3-pillar format.** The user explicitly approved this format (said "这次的很不错"). Do not deviate.

```markdown
---

## ⚡ 简介
一句话说清楚这个技能干嘛

## 📋 使用方法
怎么调用、常用命令、注意事项

## 💡 案例
> **你说：** "实际场景中你会怎么跟我说"
> **我：** 我会怎么回应
```

This format is consistent across all ~113 skill cards in the vault. When adding new cards:
- Always include all 3 sections: ⚡简介 + 📋使用方法 + 💡案例
- Case studies should be real scenario dialog format
- Link to related skills using `[[技能学院/Category/Skill Name]]`

### Managing the vault at scale (113+ files)

For large batch operations (writing many files in one session):
1. **Batch by category** — write related cards together to minimize context switching
2. **Verify a sample** — after each batch, check 1-2 files actually exist with `ls -la`
3. **Update the 总纲笔记** — the master index (`📚 总纲笔记.md`) must be updated to link to new cards
4. **Memory is limited (2,200 chars)** — don't store vault content details in memory. Store only the vault path and format conventions.

## Append to a note

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-$HOME/Documents/Obsidian Vault}"
echo "
New content here." >> "$VAULT/Existing Note.md"
```

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
