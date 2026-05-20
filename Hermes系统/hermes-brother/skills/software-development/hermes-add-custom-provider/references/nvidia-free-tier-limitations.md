# NVIDIA Free Tier API Limitations

## Environment
- API base: `https://integrate.api.nvidia.com/v1` (OpenAI-compatible)
- Auth: bearer token (`nvapi-...`)
- Client: OpenClaw Gateway with `openai-completions` provider type
- User's free NVIDIA account (no payment method added)

## Tested Models & Results

### meta/llama-3.3-70b-instruct
- **Result**: FAIL — 429 Too Many Requests
- **Log entry**: `⚠️ API rate limit reached. Please try again later. / 429 status code (no body)`
- **Behavior**: OpenClaw retried ~20+ times over ~2 minutes before exhausting fallback chain
- **Fallback chain result**: `fallbackConfigured: false` → `chain_exhausted`

### deepseek-ai/deepseek-v4-pro
- **Result**: FAIL — Empty content
- **Log entry**: `Model inference completed: model=nvidia/deepseek-ai/deepseek-v4-pro / inputTokens=7 outputTokens=0 / taskDuration=1222ms / sendError=Error: No content`
- **HTTP status**: 200 (OK) — but response body had no usable content
- **Tokens**: 7 input, 0 output

## Observed Patterns

1. **429 errors** are silent (no body) — hard to distinguish from successful responses
2. **Empty content** returns HTTP 200 but `choices[0].message.content` is empty/null
3. **No rate-limit headers** visible in Gateway logs for debugging
4. Free tier appears to have very low quota (possibly per-minute or per-hour limits)

## Recommendation

Do NOT rely on NVIDIA free tier for primary model inference. Use it only for:
- Occasional one-off queries
- Models with very light traffic
- After verifying the specific model is not rate-limited

## 2026-05-05 Session Test Results

Two high-profile models tested on NVIDIA free tier both failed:
| Model | Failure Mode |
|-------|-------------|
| `meta/llama-3.3-70b-instruct` | 429 after ~20 retries (rate limit) |
| `deepseek-ai/deepseek-v4-pro` | 200 OK but zero output tokens |

The `fallbacks: [...]` field in `openclaw.json` is critical but was missing — OpenClaw defaulted to `fallbackConfigured: false` and exhausted retries without ever trying the local fallback. After adding `"fallbacks": ["ollama/qwen3:4b"]` to `agents.defaults.model`, the chain works correctly.

Fallback models (`ollama/gemma4:26b`, `ollama/qwen3:4b`) on Intel Mac CPU are too slow for interactive use — user explicitly complained "本地太慢了". Cloud API alternatives should be preferred.
