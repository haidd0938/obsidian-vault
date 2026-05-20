# OpenClaw Configuration Reference

## `openclaw.json` Full Structure

```json
{
  "meta": { "lastTouchedVersion": "...", "lastTouchedAt": "..." },
  "auth": {
    "profiles": {
      "ollama:default": { "provider": "ollama", "mode": "api_key" },
      "nvidia:default": { "provider": "nvidia", "mode": "api_key" }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434",
        "apiKey": "***",
        "models": [
          { "id": "gemma4:26b", "name": "gemma4:26b", "contextWindow": 32768, "maxTokens": 8192 }
        ]
      },
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "***",
        "models": [
          { "id": "meta/llama-3.3-70b-instruct", "name": "meta/llama-3.3-70b-instruct", "contextWindow": 131072, "maxTokens": 8192 }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "provider/model-name",
        "fallbacks": ["provider/model2"]
      },
      "models": {
        "nvidia/meta/llama-3.3-70b-instruct": {},
        "ollama/gemma4:26b": {}
      },
      "workspace": "/Users/mac/.openclaw/workspace",
      "contextTokens": 28000,
      "thinkingDefault": "off"
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "plugins": true,
    "restart": true,
    "ownerDisplay": "raw"
  },
  "gateway": {
    "mode": "local",
    "auth": { "mode": "token", "token": "***" }
  },
  "plugins": {
    "allow": ["openclaw-web-search", "voice-call", "nvidia", "ollama"],
    "load": { "paths": ["..."] },
    "entries": { ... }
  }
}
```

## Model Reference Format

`provider/model-id` — e.g.:
- `ollama/qwen3:4b`
- `nvidia/meta/llama-3.3-70b-instruct`
- `nvidia/deepseek-ai/deepseek-v4-pro`
- `ollama/gemma4:26b`

## Fallback Configuration

The `fallbacks` field must be an array of model reference strings:

```json
"model": {
  "primary": "nvidia/meta/llama-3.3-70b-instruct",
  "fallbacks": ["ollama/qwen3:4b", "ollama/gemma4:26b"]
}
```

Without `fallbacks: [...]`, OpenClaw logs `fallbackConfigured: false` and will NOT attempt fallback — it exhausts retries on the primary model only.

## Gateway Logging

Gateway logs to stdout. Log includes:
- `config change detected; evaluating reload` — hot-reload triggered
- `agent model: <ref>` — resolved model after fallback
- `Model inference completed: ... outputTokens=X` — actual output
- `sendError=Error: No content` — model returned empty response
- `⚠️ API rate limit reached` — 429 from provider

## CLI Commands

OpenClaw controller CLI (`/usr/local/bin/openclaw`):
- `openclaw` — interactive TUI
- No `update`, `stop`, `start` as subcommands based on v2026.3.28
- Process management via launchd: `kill <PID>` → auto-restart
