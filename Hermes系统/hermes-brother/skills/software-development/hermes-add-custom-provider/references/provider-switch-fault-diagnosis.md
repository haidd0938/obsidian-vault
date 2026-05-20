# Provider Switch Fault Diagnosis

When switching provider/model in Hermes, common failure modes:
1. **Short replies** (63-118 chars, single sentence)
2. **English replies** despite Chinese system prompt
3. **Memory loss** — agent forgets user context
4. **Tool errors** — function call failures
5. **Context window errors** — `ValueError: Model X has context window Y, below minimum 64,000`

## Root Cause Checklist

### 1. switch-provider.sh Script Mismatch
The script may target fields in the wrong config hierarchy.

**Two formats:**
- **Old** (no `model:` wrapper): `provider: deepseek` at root level
- **Current** (under `model:` block):
```yaml
model:
  provider: deepseek
  default: deepseek-chat
```

**Fix:** Ensure sed targets correct hierarchy.
```bash
# For current format (model block)
sed -i '' "/^model:/,/^[a-z]/s/^  provider:.*/  provider: nvidia-nim/" "$CONFIG"
sed -i '' "/^model:/,/^[a-z]/s/^  default:.*/  default: meta/llama-3.3-70b-instruct/" "$CONFIG"
```

Always verify with `bash switch-provider.sh status`.

### 2. Context Length Check
Check each model's `context_length` in `custom_providers`. Minimum is 64,000.
Common offenders:
- `meta/llama-3.1-8b-instruct`: 32,768 on NVIDIA (FAIL)
- `gemma4:e4b`: 3,078 (FAIL)
- `qwen2.5:7b`: 3,048 (FAIL)

### 3. TG Channel Prompts
检查 telegram.channel_prompts.default 是否被覆盖。应包含完整中文系统提示。

### 4. Test Model Directly
```bash
curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"meta/llama-3.3-70b-instruct","messages":[{"role":"user","content":"用中文回答，你是谁？"}],"max_tokens":100}' | jq .
```

## Recovery
1. Full rollback: `cp ~/.hermes/config.yaml.save ~/.hermes/config.yaml`
2. Targeted fix: fix provider/default fields, remove problematic models
3. Fix switch-provider.sh to target correct format
