# OpenClaw Configuration Full Reference

> 合并自 `hermes/openclaw-configuration` 技能。完整覆盖 OpenClaw 配置、Provider、Gateway管理、Web UI 兼容性、免费 API 替代方案。

## Overview
OpenClaw is an AI assistant framework (v2026.3.28 installed at `/usr/local/lib/node_modules/openclaw/`).

## Key Locations
| Item | Path |
|------|------|
| Main config | `~/.openclaw/openclaw.json` |
| Gateway binary | `/usr/local/lib/node_modules/openclaw/dist/index.js` |
| Gateway process | launchd-managed (auto-restarts on kill) |
| Port | 18789 (local) |
| Web UI | Built-in `control-ui` from Gateway's dist |
| Workspace | `~/.openclaw/workspace` |

## Gateway Management
```bash
kill <PID>                    # Stop (launchd auto-restarts)
curl http://localhost:18789/health  # Check health
```

**Pitfalls:**
- `openclaw stop/start` may NOT fully reload dist file changes — use `kill <PID>` and let launchd auto-restart
- Config changes may hot-reload automatically but sometimes need full restart

## Model Configuration

### Provider Config
```json
"models": {
  "mode": "merge",
  "providers": {
    "ollama": {
      "baseUrl": "http://127.0.0.1:11434",
      "apiKey": "***",
      "models": [ { "id": "gemma4:26b", "name": "...", "contextWindow": 32768, "maxTokens": 8192 } ]
    },
    "nvidia": {
      "baseUrl": "https://integrate.api.nvidia.com/v1",
      "apiKey": "***",
      "models": [ { "id": "meta/llama-3.3-70b-instruct", "name": "...", "contextWindow": 131072, "maxTokens": 8192 } ]
    }
  }
}
```

### Fallback Chain
```json
"agents": {
  "defaults": {
    "model": {
      "primary": "nvidia/meta/llama-3.3-70b-instruct",
      "fallbacks": ["ollama/qwen3:4b"]
    }
  }
}
```

**⚠️ Pitfalls:**
- `strategy: "auto-failover"` is **Hermes syntax** — does NOT work in OpenClaw
- Use `fallbacks: [...]` array instead
- Model reference format: `provider/model-name` (e.g., `ollama/gemma4:26b`)

## Free API Alternatives (when primary fails)

| Provider | Sign-up | Free Models | Limits | Compat |
|----------|---------|-------------|--------|:------:|
| **OpenRouter** 🥇 | Email only | Llama 3.3 70B, Gemma 4 31B, Qwen 3 | 20rpm, 50req/day | ✅ |
| **Groq** 🥈 | Email only | Llama 3.3 70B (1000req/day), Llama 4 Scout | 1000req/day | ✅ |
| **Cerebras** 🥉 | Email only | gpt-oss-120b, Llama 3.1 8B | 30rpm, 14400req/day | ✅ |

## Local Model Performance (Intel Mac, no GPU)
| Model | CPU Speed | Verdict |
|-------|-----------|---------|
| qwen3:4b (2.5GB) | ❌ Too slow | Fallback only |
| qwen2.5:7b (4.7GB) | ❌ Slower | Not recommended |
| gemma4:26b (~15GB) | ⚠️ Slow but functional | Best local option |

## NVIDIA Free Tier Limitations
- Llama 3.3 70B: ❌ 429 rate limit (very aggressive)
- DeepSeek V4 Pro: ❌ Returns 200 but empty content
- Do NOT rely on NVIDIA free tier as primary.

## Web UI Compatibility
- Gateway v2026.3.28 expects `session_id` (snake_case)
- After Web UI updates from "系统更新" button, full Gateway restart required
- `openclaw stop/start` may NOT be sufficient — use `kill <PID>` directly

## References
See `references/openclaw-gateway-reload.md` for dist file reload pitfalls.
