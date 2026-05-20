# Provider Health Monitor

Covers checking health, balance, and availability of all configured Hermes providers.

## Quick Start — Check Current Provider & Balance

```bash
# 1. See what's active right now
head -5 ~/.hermes/config.yaml

# 2. Check DeepSeek balance
DS_KEY=$(grep -A2 'name: DeepSeek' ~/.hermes/config.yaml | grep api_key | head -1 | awk '{print $2}')
curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $DS_KEY"

# 3. Check NVIDIA health (use /v1/models NOT /v1)
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 15 \
  "https://integrate.api.nvidia.com/v1/models"
```

## Provider Details

| Provider | Base URL | Default Model |
|----------|----------|---------------|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.1-8b-instruct` |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.5-flash` |

## Policy: Manual Switch Only

**Auto-switching is DISABLED.** The user experienced quality degradation with auto-switching to NVIDIA models. Only switch on explicit command.

## Balancing Checking

**DeepSeek:** `curl -s https://api.deepseek.com/user/balance -H "Authorization: Bearer $KEY"`  
Expected: `{"is_available":true,"balance_infos":[{"currency":"RMB","total_balance":"XX.XX"}]}`

**Two distinct failure modes:**

| Symptom | Balance API | Chat API | Diagnosis |
|---------|-------------|----------|-----------|
| **Balance-only denial** | `401` balance endpoint | `200` chat works | Key is valid but may lack balance API scope — the account still has balance for inference. Check chat completion to confirm. |
| **True dead key** | `401` balance endpoint | `401` chat also fails | Key has been revoked, expired, or the account is frozen. **Different from balance-only denial.** Check `auth.json` `last_status` — if it says `"exhausted"` with 401 on actual completion calls, the key is fully dead. |

**How to distinguish them:**
```bash
# Quick test: try an actual chat completion
curl -s -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'
# 200 → balance-only denial (key works for inference)
# 401 → true dead key
```

**Also check `~/.hermes/auth.json`:** The credential pool tracks per-key status. Look for:
- `"last_status": "exhausted"` + `"last_error_code": 401` → the key has been tried and failed
- `"last_status": null` or `"last_status": "ok"` → recent failure may be transient

**When the key IS dead for everything (both balance + chat 401):**
- The balance cron job will report `authentication_error` every time it runs
- Alert via Telegram: this is a critical issue — no DeepSeek inference available
- User needs to generate a new key at https://platform.deepseek.com
- Update `~/.hermes/config.yaml` and `switch-provider.sh` with the new key
- This happened with key `be5c67...9319` (confirmed dead 2026-05-08 / 2026-05-09)

## Cron Job

A daily cron job `DeepSeek余额监控 - 低于5元提醒` runs at 09:00 and alerts via Telegram if balance < ¥5. Historical output at `~/Desktop/任务中心/03-DeepSeek余额/$(date +%Y-%m-%d)-余额检查.md`.

**Dead key handling:** When the key returns 401 (authentication_error), the cron job should:
1. Write the report file noting authentication failure (not just "unknown balance")
2. Send a Telegram alert — this is a critical failure, not a routine low-balance warning
3. Do NOT use `deliver=origin` (cron session has no origin) — write file + send via Telegram directly
4. Check `send_message` target: use `telegram:<chat_name>` (e.g. `telegram:Jarvis秘书团`), not bare `telegram` (which fails if no home channel is configured)

## Pitfalls
- sed delimiter: Always use `|` when model names contain `/`
- Four fields must be switched together: `provider`, `default`, `base_url`, `max_context`
- `grep` matches multiple lines — use `head -1` to get top-level matches
- Balance 401 doesn't mean chat is broken — test actual chat completion first
- **Telegram `send_message` requires explicit channel name** — bare `telegram` target fails with "No home channel set" if `TELEGRAM_HOME_CHANNEL` is not configured. Always use `telegram:ChannelName` format.
- **Consecutive days of the same error** — check for an existing report file from yesterday. If the same error persists, note it in the report so the user can see the pattern.
