# OpenClaw (v2026.3.28) Configuration Guide

> Reference for working with OpenClaw's JSON config, provider setup, and failover.  
> OpenClaw is installed at `/usr/local/lib/node_modules/openclaw/` and config lives in `~/.openclaw/`.

## Config Files

| Path | Purpose |
|------|---------|
| `~/.openclaw/openclaw.json` | Main config — models, providers, agents, plugins, gateway |
| `~/.openclaw/agents/main/agent/models.json` | Per-agent model/provider overrides |
| `~/.openclaw/logs/gateway.log` | Gateway runtime logs |
| `~/.openclaw/logs/gateway.err.log` | Gateway error logs |
| `~/.openclaw/devices/paired.json` | Paired devices |
| `~/.openclaw/plugins/installs.json` | Plugin manifest |

## Model Configuration Pattern

### Provider Registration

Providers go under `models.providers`:

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "nvapi-xxxxx",
        "models": [
          {
            "id": "deepseek-ai/deepseek-v4-pro",
            "name": "deepseek-ai/deepseek-v4-pro",
            "contextWindow": 131072,
            "maxTokens": 8192
          }
        ]
      },
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434",
        "apiKey": "***",
        "models": [
          {
            "id": "qwen3:4b",
            "name": "qwen3:4b",
            "contextWindow": 32768,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

### Agent Model Selection + Fallback

In `agents.defaults.model`:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "nvidia/deepseek-ai/deepseek-v4-pro",
        "fallbacks": ["ollama/qwen3:4b"]
      }
    }
  }
}
```

**Key detail:** The `primary` field must use `provider/model-id` format. The `fallbacks` array is checked by OpenClaw's `resolveAgentModelFallbackValues()` function (source: `dist/model-input-DmUH8dul.js`). Without a `fallbacks` array, `fallbackConfigured` is `false` and the model fallback chain is empty — it will retry the primary model indefinitely on errors.

Model ref format: `nvidia/deepseek-ai/deepseek-v4-pro` → reads as provider `nvidia`, model ID `deepseek-ai/deepseek-v4-pro`.

### Per-Agent Model Overrides

`~/.openclaw/agents/main/agent/models.json` mirrors the provider list from `openclaw.json` but with an `"api"` field for defaults:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "...",
      "apiKey": "***",
      "models": [...],
      "api": "ollama"
    },
    "nvidia": {
      "baseUrl": "...",
      "apiKey": "nvapi-xxxxx",
      "models": [...]
    }
  }
}
```

`ollama` has `"api": "ollama"` explicitly. NVIDIA doesn't need it because the base URL implies OpenAI-compatible format.

## NVIDIA NIM Provider

### API Details

- **Base URL:** `https://integrate.api.nvidia.com/v1`
- **API format:** OpenAI-compatible (pass `model` field, use `/v1/chat/completions`)
- **Auth:** Bearer token via `apiKey` field
- **Gateway treats it as** `openai-completions` provider type (no `api` field = auto-detect OpenAI compat)

### Rate Limiting

NVIDIA free tier is **aggressive on rate limits**. Common models hit 429 quickly:
- `meta/llama-3.3-70b-instruct` — very limited, 429 within a few requests
- `deepseek-ai/deepseek-v4-pro` — more available, but still limited
- `nvidia/llama-3.3-nemotron-super-49b-v1` — NVIDIA-hosted, better quotas

429 errors show as: `"API rate limit reached. Please try again later."` with HTTP 429.

### Listing Available Models

```bash
curl -s "https://integrate.api.nvidia.com/v1/models" \
  -H "Authorization: Bearer $NVIDIA_API_KEY"
```

## Gateway Management

### Process Model

Gateway runs as a **launchd service** via `ai.openclaw.gateway` plist.  
It's auto-managed — killing the process causes launchd to restart it immediately.

Key commands:
```bash
# View process
ps aux | grep openclaw

# Kill to force restart (launchd auto-restarts)
kill <PID>

# Check health
curl http://localhost:18789/health
# → {"ok":true,"status":"live"}

# Check logs
tail -100 ~/.openclaw/logs/gateway.log
```

### Hot Reload

OpenClaw detects config file changes and hot-reloads within seconds. Log lines like:
```
[reload] config change detected; evaluating reload (agents.defaults.model.primary, agents.defaults.model.fallbacks)
[reload] config hot reload applied (agents.defaults.model.primary, agents.defaults.model.fallbacks)
```

Hot reload **does** pick up model/agent changes. It **does not** always pick up dist file changes (Web UI JS files).

### Full Restart When Needed

For Web UI dist changes or module upgrades, kill the process:
```bash
kill $(pgrep -f "openclaw.*gateway")
# launchd auto-restarts
```

### Runtime Node Version

Gateway uses Homebrew's `node@22` (`/usr/local/opt/node@22/bin/node`, v22.22.2), **not** the system default Node (which may be v23+).

## Web UI Version Mismatch

### Symptoms

- `invalid chat.send params: at root: unexpected property 'sessionId'`
- `invalid models.list params: at root: unexpected property 'view'`

### Root Cause

Web UI dist files (under `~/.openclaw/web/dist/assets/`) and Gateway framework files (under `/usr/local/lib/node_modules/openclaw/dist/`) are mismatched versions. The API protocol between Web UI and Gateway uses different parameter conventions.

**Gateway Schema (v2026.3.28):**
```javascript
const ChatSendParamsSchema = Type.Object({
    sessionKey: ChatSendSessionKeyString,
    sessionId: Type.Optional(NonEmptyString),  // accepts camelCase
    message: Type.String(),
    ...
}, { additionalProperties: false });
```

The Gateway *does* accept `sessionId` (camelCase). The `additionalProperties: false` means any **unexpected** extra field triggers the error. If the schema has `sessionId` but the Web UI sends a different set with extra fields, it fails.

### Fix Approach

1. **Kill Gateway process** — forces launchd to restart with fresh dist files
2. **If still failing**, patch the dist files:
   - Change `sessionId` → `session_id` in the JS sending params  
   - OR add `delete params.sessionId` before validation in `chat-CGlveWq2.js`

But the **reliable** fix is:
1. Ensure Web UI and Gateway are on matching versions
2. Kill + restart Gateway (not `stop/start` — use `kill`)

## Fallback Chain Behavior

OpenClaw's fallback logic (source: `model-fallback-BjdpR22p.js`, `failover-policy.ts`):

1. Try primary model
2. On error: check if error is recoverable (rate_limit, overloaded, timeout, billing, etc.)
3. If recoverable → try next in `fallbacks` array
4. If no more fallbacks → `chain_exhausted`, give up
5. Logs show: `fallbackConfigured: false` when no `fallbacks` array present

Fallback reasons that trigger failover:
- `rate_limit` (429)
- `overloaded` (503)
- `timeout` (request timeout)
- `billing` (insufficient credits)
- `empty_response`, `unknown`, `unclassified`

Fallback reasons that do NOT trigger failover:
- `model_not_found`, `format`, `auth`, `auth_permanent`, `session_expired`
