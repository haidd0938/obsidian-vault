# Community Skill Manual Installation Guide

When `hermes skills install <name>` is unavailable or fails, install community skills manually.

## The Workaround

`hermes skills install` may not be implemented in the current Hermes version. The CLI returns `unknown command` for `install`, `inspect`, and `search` subcommands even though they appear in the docs.

## Manual Installation Steps

### 1. Find the skill on GitHub

Community skills live at: https://github.com/lobehub/hermes-agent-skills

Browse the `skills/` directory. Each skill is a subdirectory with a `hermes.json` config file.

### 2. Download and install

```bash
# Option A: git sparse checkout (recommended for single skill)
git clone --depth 1 --filter=blob:none --sparse https://github.com/lobehub/hermes-agent-skills.git /tmp/hermes-skills-tmp
cd /tmp/hermes-skills-tmp
git sparse-checkout set "skills/<skill-name>"
cp -r "skills/<skill-name>" ~/.hermes/skills/<skill-name>
rm -rf /tmp/hermes-skills-tmp

# Option B: download specific directory (if gh CLI available)
gh repo clone lobehub/hermes-agent-skills /tmp/hermes-skills-tmp -- --depth 1
cp -r /tmp/hermes-skills-tmp/skills/<skill-name> ~/.hermes/skills/<skill-name>
rm -rf /tmp/hermes-skills-tmp
```

### 3. Check the structure

A valid community skill contains:
- `hermes.json` — tool definitions with name/description/schema/handler
- `README.md` — usage docs
- `requirements.txt` — Python dependencies (install them manually)
- `.env.example` — required environment variables
- Source files (`.py` or `.js`) referenced by `hermes.json` handlers

### 4. Install dependencies

```bash
cd ~/.hermes/skills/<skill-name>
pip install -r requirements.txt  # if present
```

### 5. Set environment variables

Copy `.env.example` to `~/.hermes/.env` or create entries:
```bash
# Add to ~/.hermes/.env
echo "TWILIO_ACCOUNT_SID=your_sid" >> ~/.hermes/.env
```

### 6. Load the skill

Start a new Hermes session — skills in `~/.hermes/skills/` are auto-discovered at startup.

## Notes

- Manual installs don't get auto-updates — the user needs to re-copy when the upstream skill changes.
- Some community skills may have Python dependency conflicts — install in a venv if needed.
- The skill's tools appear alongside built-in tools once loaded. Verify with `hermes tools list` or just start using them.
