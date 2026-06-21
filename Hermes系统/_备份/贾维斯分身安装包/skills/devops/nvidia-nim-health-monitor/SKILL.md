---
name: nvidia-nim-health-monitor
description: Monitor NVIDIA NIM API availability — manual switching only. Auto-switching is disabled because it caused model quality issues ("胡说八道") that disrupted the user's work.
---

# NVIDIA NIM Health Monitor

**IMPORTANT: Auto-switching is DISABLED.** The user explicitly chose manual switching because auto-switching caused severe quality degradation ("胡说八道") with NVIDIA models (`meta/llama-3.1-8b-instruct`).

The user's policy: "后面需要了，我再下命令" (only switch on explicit command).

## Trigger

Only when the user explicitly requests switching providers. Do NOT create or run auto-switch cron jobs.

## Manual Provider Switching

```bash
bash ~/.hermes/switch-provider.sh nvidia    # switch to NVIDIA NIM
bash ~/.hermes/switch-provider.sh deepseek  # switch to DeepSeek
bash ~/.hermes/switch-provider.sh status    # show current state
```

## Check NVIDIA Health (for status reports)

Use `/v1/models` endpoint (NOT `/v1`):

```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --max-time 15 \
  "https://integrate.api.nvidia.com/v1/models"
```

- HTTP 200 → NVIDIA is healthy
- Any other code or connection failure → NVIDIA is down

## Config File Location

`~/.hermes/config.yaml`

## Provider Details

| Provider | Base URL | Model | Max Context |
|----------|----------|-------|-------------|
| NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.1-8b-instruct` | 32768 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | 131072 |

## switch-provider.sh Implementation Details

The script at `~/.hermes/switch-provider.sh` handles config changes.

Key techniques:
- **sed delimiter**: Use `|` instead of `/` because model names contain slashes (e.g., `meta/llama-3.1-8b-instruct`)
- Must update **four fields**: `provider`, `default` (model name), `base_url`, `max_context`
- Use `head -1` when grepping because config has many `provider:`/`base_url:` entries

## History

- **April 25-26, 2026**: Auto-switch cron job (`*/30 * * * *`) was running, causing unexpected provider changes
- **April 27, 2026**: User explicitly disabled auto-switching after quality issues. Cron job `c51f9be97068` was removed.
- **Current policy**: Manual switching only, on user command.

## Pitfalls

- **Auto-switching is rejected**: The user experienced "胡说八道" (nonsense responses) when auto-switched to NVIDIA. Never re-enable auto-switching without explicit approval.
- **sed delimiter**: Always use `|` as sed delimiter when model names contain `/`
- **Four fields must switch**: `provider`, `default`, `base_url`, `max_context` — missing any one causes misconfiguration
- **`grep` matches multiple lines**: Config has many `provider:`/`base_url:` entries. Use `head -1` to get the top-level `model` section value
