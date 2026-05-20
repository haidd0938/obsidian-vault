# Telegram Bot Dumb-Down Diagnosis (TG 降智排查)

When the Telegram bot suddenly starts replying short (63-118 chars), switches to English, or loses memory.

## 6-Dimension Root Cause Framework

### Dimension 5 (NEW): System Prompt too short — model over-tooling
The SOUL.md + skills list forms 20K+ char system_prompt. With 29 tool definitions, models tend to call tools instead of answering directly. No instruction tells the model "simple Q&A -> answer directly, don't call tools."

### Dimension 4: Missed channel_prompts — system_prompt too long to append
If system_prompt is already 20K+ strings, channel_prompts appended at the end may be truncated. **Fix**: truncate SOUL.md or add commit_force_responses style instruction.

### Dimension 3: Model/provider switch — Chinese model → English model
Switch from deepseek-chat or qwen to claude/gpt/other English-based models. Model's built-in behavior overrides channel_prompts. **Fix**: hardcode language in system prompt, not just channel_prompt.

### Dimension 2: Session poisoning — bad messages stuck in context
Session files in `~/.hermes/sessions/` contain corrupted context from failed tool calls. **Fix**: `rm ~/.hermes/sessions/telegram_*.json` and restart gateway.

### Dimension 1: Provider config corruption
Check `hermes config show` for dirty state (provider switching left stale values).

## Quick Fixes (in order of probability)
1. Reset sessions: `rm ~/.hermes/sessions/telegram_*.json && hermes gateway restart`
2. Check logs: `tail -n 100 ~/.hermes/logs/gateway.log | grep -iE "token|switch|model|error"`
3. Verify provider: `hermes config show`
4. Re-export TELEGRAM env vars
5. Truncate SOUL.md if it's too long (>10K chars)
