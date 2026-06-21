---
name: provider-switch-fault-diagnosis
description: Diagnose and recover from provider/model switching failures in Hermes Agent — root cause analysis of "降智" (short/English replies, memory loss, tool errors)
tags:
  - hermes
  - provider
  - switch
  - fault-diagnosis
  - config
trigger: provider switch failure, 降智, 模型切换错误, 回复变短, 英文回复, 胡言乱语
---

# Provider Switch Fault Diagnosis

## Problem Symptoms
After switching provider/model in Hermes Agent, common failure modes:
1. **Short replies** (63-118 chars, single sentence)
2. **English replies** despite Chinese system prompt
3. **Memory loss** — agent forgets user identity, name, context
4. **Tool errors** — function call failures, "I'm not able to provide a response for the given function call"
5. **Context window errors** — `ValueError: Model X has a context window of Y, which is below the minimum 64,000 required`

## Root Cause Checklist (in order)

### 1. Check if switch-provider.sh script is outdated
The script may modify config fields that no longer exist in the current config.yaml format.

**Diagnosis:**
```bash
bash ~/.hermes/switch-provider.sh status
```
Or check manually:
```bash
head -7 ~/.hermes/config.yaml
```

**Two possible config formats:**

*Old format (no `model:` wrapper):*
```yaml
provider: deepseek
default: deepseek-chat
base_url: https://api.deepseek.com/v1
```

*Current format (under `model:` block):*
```yaml
model:
  provider: deepseek
  default: deepseek-chat
  max_context: 131072
  max_tokens: 4096
  base_url: https://api.deepseek.com/v1
```

If the script uses `sed -i '' "s/^  provider:.*/..."` but config has `model:` wrapper, **the script silently does nothing** — the grep finds no match, the file stays unchanged, user thinks they switched but they didn't.

**Fix:** Update switch-provider.sh to target the correct hierarchy.

For the current format (`model:` block), the sed commands should be:
```bash
# Change provider under model block
sed -i '' "/^model:$/,/^[a-z]/s/^  provider:.*/  provider: nvidia-nim/" "$CONFIG"
# Change default model under model block
sed -i '' "/^model:$/,/^[a-z]/s/^  default:.*/  default: meta/llama-3.3-70b-instruct/" "$CONFIG"
```

**Simpler approach** (used in the repaired script): since `provider:` and `default:` only appear once in the file (under the `model:` block), simple `sed -i '' "s/^  provider:.*/..."` works as long as there's no other occurrence in the file. Always verify with `bash switch-provider.sh status` after switching.

### 2. Check model context_length
Some models (especially 8B variants on NVIDIA) report context_length <64K, which Hermes rejects.

**Diagnosis:** Read `custom_providers` in config.yaml and check each model's `context_length`. Minimum is 64,000 tokens.

**Common offenders:**
- `meta/llama-3.1-8b-instruct`: 32,768 on NVIDIA (FAIL)
- `gemma4:e4b`: 3,078 (FAIL)
- `qwen2.5:7b`: 3,048 (FAIL)

### 3. Check channel_prompts
TG降智时，检查telegram.channel_prompts是否被覆盖或清除。

**Diagnosis:** Read `telegram.channel_prompts.default` in config.yaml. It should contain the full Chinese system prompt with memory rules.

### 4. Check model behavior on the provider side
Some models (e.g. meta/llama-3.3-70b-instruct on NVIDIA NIM) may return short/English responses unpredictably.

**Diagnosis:** Test with direct API call:
```bash
curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"meta/llama-3.3-70b-instruct","messages":[{"role":"user","content":"用中文回答，你是谁？"}],"max_tokens":100}' | jq .
```
If response is English or truncated, the model/provider combo is unstable.

## Recovery Plan

### Fastest Recovery — Full rollback from backup
```bash
# List available backups
ls -la ~/.hermes/config.yaml.save ~/.hermes/config.yaml.bak

# Restore from most recent save (this is the fastest and safest option)
cp ~/.hermes/config.yaml.save ~/.hermes/config.yaml

# Then fix the model section to use correct provider syntax
# (backup may use 'custom' provider format — update to 'deepseek' if needed)
```

### Targeted Fix — Manual repair
If full rollback is not desired, fix specific sections:

**Fix provider:**
```yaml
model:
  provider: deepseek  # or nvidia-nim
  default: deepseek-chat
```

**Remove problematic NVIDIA model config:**
Remove the 70B entry from `custom_providers` if it causes issues. Keep only stable models:
```yaml
- name: NVIDIA NIM
  base_url: https://integrate.api.nvidia.com/v1
  api_key: <key>
  model: meta/llama-3.1-8b-instruct
  models:
    meta/llama-3.1-8b-instruct:
      context_length: 32768
```

**Restore TG channel_prompts:**
Ensure `telegram.channel_prompts.default` contains the full Chinese-only system prompt with identity rules.

**Fix switch-provider.sh:**
Update the script to target the correct fields. The repaired script (`~/.hermes/switch-provider.sh`) uses:

```bash
# Change provider (targets "  provider:" under model block)
sed -i '' "s/^  provider:.*/  provider: nvidia-nim/" "$CONFIG"
sed -i '' "s/^  default:.*/  default: meta/llama-3.3-70b-instruct/" "$CONFIG"
```

**Critical: always verify after switching:**
```bash
bash ~/.hermes/switch-provider.sh status
```
Expected output should show the provider and model you intended to switch to. If it shows something else (e.g. still shows `custom` or wrong model), the `sed` didn't match — check the file format.

## Prevention
1. Always keep a `config.yaml.save` before any manual model switch
2. Test model with direct API curl before switching Hermes to it
3. After switching, send a test message (e.g. "我是谁？") to verify memory and language
4. Maintain the switch-provider.sh script in sync with config.yaml format changes
