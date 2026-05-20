# Free AI API Providers for OpenClaw

Compiled 2026-05-05. Source: https://github.com/cheahjs/free-llm-api-resources (⭐20k)

## OpenRouter 🥇

**Base URL:** `https://openrouter.ai/api/v1` (OpenAI-compatible)
**Sign-up:** Email only, no credit card, no phone
**Limits:** 20 requests/min, 50 requests/day (up to 1000/day with $10 lifetime topup)
**Free models include:**
- `meta-llama/llama-3.3-70b-instruct:free` — 70B parameter
- `google/gemma-4-31b-it:free` — 31B Gemma 4
- `google/gemma-4-26b-a4b-it:free` — 26B MOE Gemma 4
- `qwen/qwen3-coder:free` — Qwen 3 Coder
- `qwen/qwen3-next-80b-a3b-instruct:free` — 80B MOE Qwen
- `openai/gpt-oss-120b:free` — 120B open model
- `nousresearch/hermes-3-llama-3.1-405b:free` — 405B Hermes

**OpenClaw provider config:**
```json
"openrouter": {
  "baseUrl": "https://openrouter.ai/api/v1",
  "apiKey": "<your-api-key>",
  "models": [
    { "id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B Free", "contextWindow": 131072, "maxTokens": 8192 },
    { "id": "google/gemma-4-31b-it:free", "name": "Gemma 4 31B Free", "contextWindow": 32768, "maxTokens": 8192 },
    { "id": "openai/gpt-oss-120b:free", "name": "GPT OSS 120B Free", "contextWindow": 131072, "maxTokens": 8192 }
  ]
}
```

## Groq 🥈

**Base URL:** `https://api.groq.com/openai/v1` (OpenAI-compatible)
**Sign-up:** Email only, no credit card
**Limits (free tier):**
| Model | Requests/day | Tokens/min |
|-------|:---:|:---:|
| Llama 3.3 70B | 1,000 | 12,000 |
| Llama 4 Scout | 1,000 | 30,000 |
| Llama 3.1 8B | 14,400 | 6,000 |
| Qwen 3 32B | 1,000 | 6,000 |
| GPT-OSS 120B | 1,000 | 8,000 |

**Use case:** Best for high-frequency needs — 1000 Llama 70B requests/day is generous
**Speed:** Extremely fast (dedicated LPU hardware)

## Cerebras 🥉

**Base URL:** `https://cloud.cerebras.ai` (OpenAI-compatible)
**Sign-up:** Email only, no credit card
**Limits:** 30 requests/min, 14,400 requests/day, 1M tokens/day, 60K tokens/min
**Models:** `gpt-oss-120b`, `Llama 3.1 8B`
**Use case:** Highest raw request limit — almost unlimited for light use

## Cloudflare Workers AI

**Base URL:** `https://api.cloudflare.com/client/v4/accounts/<acct>/ai/v1` (OpenAI-compatible)
**Sign-up:** Cloudflare account (free tier)
**Limits:** 10,000 neurons/day (~10,000 LLM inferences)
**Models:** Llama 3.3 70B (FP8), Gemma 4 26B, Qwen 3 Coder 30B, Llama 4 Scout
**⚠️ Gotcha:** Requires Workers AI binding, not trivial to configure for OpenAI-compatible use

## GitHub Models

**Base URL:** `https://models.inference.ai.azure.com` (OpenAI-compatible)
**Sign-up:** GitHub account
**Limits:** Dependent on Copilot subscription
- **Free:** Very restrictive (~5 req/day)
- **Pro/Pro+:** Higher limits
**Models:** Llama 3.3 70B, DeepSeek R1/V3, GPT-4.1, Qwen, Grok 3, Mistral, Phi-4

## Google AI Studio (Gemini) — DEPLETED

**Base URL:** `https://generativelanguage.googleapis.com/v1beta/openai/` (OpenAI-compatible)
**Status:** User's key depleted (429: "prepayment credits are depleted")
**Free tier when active:** Gemini 2.5 Flash (20req/day), Gemini 3 Flash (20req/day)
**⚠️ Gotcha:** Credits run out after sustained use; needs billing setup to replenish

## Providers with Trial Credits

| Provider | Credits | Note |
|----------|:-------:|------|
| Fireworks | $1 | Various open models |
| Hyperbolic | $1 | DeepSeek V3, Llama 3.3 |
| SambaNova | $5/3mo | Llama 3.3, DeepSeek V3.1 |
| Baseten | $30 | Any model (pay by compute) |
| Nebius | $1 | Various open models |
| Mistral (free tier) | 1B tokens/month | Needs phone verification, all Mistral models |

## Recommendation for OpenClaw

If current primary (local Ollama) is too slow:
1. **Best bet**: Register OpenRouter → get API key → add as `openrouter` provider in config
2. **Fastest fix**: Register Groq → Llama 3.3 70B with 1000req/day limit
3. **Most free queries**: Cerebras → 14,400 requests/day on gpt-oss-120b
