---
name: hermes-add-custom-provider
description: Add custom API providers to Hermes Agent configuration, supporting OpenAI-compatible endpoints like NVIDIA NIM, local models, and other third-party services.
version: 1.0.0
author: Hermes Agent + Community
license: MIT
metadata:
  hermes:
    tags: [hermes, configuration, api, providers, custom]
    homepage: https://hermes-agent.nousresearch.com/docs/user-guide/configuration
    related_skills: [hermes-agent]
---

# Hermes Custom API Provider Setup

Add custom API providers to Hermes Agent configuration. This skill guides you through adding OpenAI-compatible endpoints (like NVIDIA NIM, local models, Ollama, or other third-party services) to the Hermes configuration file.

## When to Use

Use this skill when:
- Adding a new OpenAI-compatible API endpoint to Hermes
- Configuring NVIDIA NIM API, local Ollama instances, or other custom providers
- Need to verify API connectivity and test the configuration
- Want to update persistent memory with provider information

## Prerequisites

1. Hermes Agent installed and configured
2. API credentials for the target service (API key, base URL)
3. Knowledge of the provider's model name(s) and context length(s)

## Configuration Structure

Hermes uses `~/.hermes/config.yaml` with a `custom_providers` section. Each provider entry has:

```yaml
custom_providers:
  - name: Provider Name
    base_url: https://api.example.com/v1
    api_key: your-api-key-here
    model: default-model-name
    models:
      model-name-1:
        context_length: 32768
      model-name-2:
        context_length: 64000
```

## Step-by-Step Guide

### 1. Read Current Configuration

```python
read_file(path="~/.hermes/config.yaml")
```

Examine the existing `custom_providers` section to understand the format and avoid duplication.

### 2. Identify Insertion Point

Find where `custom_providers:` ends (typically before `timeout:` or other root-level keys). You'll insert the new provider as another item in the list.

### 3. Prepare Provider Configuration

Gather the following information:
- **Provider Name**: Human-readable name (e.g., "NVIDIA NIM", "Local Ollama")
- **Base URL**: API endpoint (e.g., `https://integrate.api.nvidia.com/v1`)
- **API Key**: Authentication token
- **Default Model**: The model to use by default
- **Models Dictionary**: Supported models with their context lengths

### 4. Add Provider to Config

Use the `patch` tool to insert the new provider:

```python
patch(
  mode="replace",
  path="~/.hermes/config.yaml",
  old_string="existing-text-to-find",
  new_string="existing-text-to-find\nnew-provider-config"
)
```

**Example for NVIDIA NIM API:**

```yaml
old_string: "      deepseek-reasoner:\n        context_length: 64000\ntimeout: 300"
new_string: "      deepseek-reasoner:\n        context_length: 64000\n  - name: NVIDIA NIM\n    base_url: https://integrate.api.nvidia.com/v1\n    api_key: nvapi-your-api-key-here\n    model: minimaxai/minimax-m2.7\n    models:\n      minimaxai/minimax-m2.7:\n        context_length: 32768\ntimeout: 300"
```

**Example for Local Ollama:**

```yaml
old_string: "existing-provider-entry\ntimeout: 300"
new_string: "existing-provider-entry\n  - name: Local Ollama\n    base_url: http://localhost:11434/v1\n    api_key: ollama\n    model: llama3.2:3b\n    models:\n      llama3.2:3b:\n        context_length: 32768\ntimeout: 300"
```

### 5. Verify Configuration

Read the updated config to confirm the provider was added correctly:

```python
read_file(path="~/.hermes/config.yaml", offset=line_number, limit=20)
```

### 5a. Update Existing Provider Configuration

If updating an existing provider (e.g., new API key, changed default model), locate the provider entry and modify it:

**Example: Update NVIDIA NIM API Key and Default Model**

```yaml
# Original configuration
- name: NVIDIA NIM
  base_url: https://integrate.api.nvidia.com/v1
  api_key: nvapi-old-key-here
  model: minimaxai/minimax-m2.7
  models:
    minimaxai/minimax-m2.7:
      context_length: 32768

# Updated configuration
- name: NVIDIA NIM
  base_url: https://integrate.api.nvidia.com/v1
  api_key: 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
  model: meta/llama-3.1-8b-instruct
  models:
    meta/llama-3.1-8b-instruct:
      context_length: 32768
    minimaxai/minimax-m2.7:
      context_length: 32768
```

**Steps to update**:
1. Read the config file to find the exact provider entry
2. Use `patch` to replace the old configuration with the new one
3. Include all necessary fields (name, base_url, api_key, model, models)
4. Consider adding multiple models under `models:` for flexibility

### 5b. Verify and Confirm Existing Provider Configuration

When a user provides new credentials for an already-configured provider, verify whether the configuration is already up-to-date before making changes:

**Scenario**: User provides a new API key that may be identical to the existing one.

**Steps**:
1. **Read the configuration file** to examine the existing provider entry:
   ```python
   read_file(path="~/.hermes/config.yaml", offset=line_number, limit=20)
   ```
   Focus on the custom_providers section containing the provider in question.

2. **Compare API keys**: Check if the provided key matches the configured key.
   - If keys are identical: Configuration is already up-to-date
   - If keys differ: Update is needed

3. **Configuration verification**: For NVIDIA NIM API specifically:
   - Confirm base URL: `https://integrate.api.nvidia.com/v1`
   - Check default model stability: Prefer `meta/llama-3.1-8b-instruct` over `minimaxai/minimax-m2.7` for reliability
   - Verify multiple models are defined under `models:` for fallback options

4. **Memory management**: When updating memory entries about provider configuration:
   - Check memory usage before adding new entries (`memory` tool shows current usage)
   - Remove duplicate or outdated entries to free space
   - Update existing entries with new information rather than creating duplicates

**Example workflow for key verification**:
```python
# Read config to check current NVIDIA NIM configuration
config = read_file(path="~/.hermes/config.yaml", offset=200, limit=50)

# Extract current API key from config (looking for the NVIDIA NIM entry)
# If new_key == existing_key: configuration is current
# If different: update configuration using patch()

# Update memory if needed (check current usage first)
memory_info = memory(action="list", target="memory")  # Check current usage
# If near limit, remove less critical entries before adding new ones
```

**Important**: Always check configuration before making changes to avoid unnecessary updates or duplication.

### 5c. Cost Optimization: Switching Default Models to Free Providers

When cost control is a priority (e.g., user wants to avoid expensive API fees), switch the default model from paid providers to free alternatives:

**Steps to change default model in config.yaml:**

1. **Read the model configuration section:**
```python
read_file(path="~/.hermes/config.yaml", offset=1, limit=20)
```

2. **Identify the default model setting:** Look for `default:` under the `model:` section.

3. **Update to a free provider model:**
```python
patch(
  mode="replace",
  path="~/.hermes/config.yaml",
  old_string="  default: deepseek-reasoner",
  new_string="  default: meta/llama-3.1-8b-instruct"
)
```

**Example scenario:** Switching from DeepSeek (paid) to NVIDIA NIM (free):
- Original: `default: deepseek-reasoner`
- Updated: `default: meta/llama-3.1-8b-instruct`

**Important considerations:**
- Verify the new default model exists in the configured providers
- Test model stability and performance after switching
- Update memory to record the cost optimization decision

### 5d. Environment Variable Management for Third-Party APIs

For services that use environment variables (like Tavily, Fal.ai), add API keys to `~/.hermes/.env`:

**Steps to add API keys:**

1. **Read current .env file:**
```python
read_file(path="~/.hermes/.env")
```

2. **Check if key already exists:**
```python
# In execute_code or manual check
if 'TAVILY_API_KEY' not in env_content:
    # Add the key
```

3. **Add new API keys (preserve existing content):**
```python
# Using execute_code for safe updates
from hermes_tools import read_file, write_file

env_content = read_file('~/.hermes/.env')['content']
if 'TAVILY_API_KEY' not in env_content:
    if env_content and not env_content.endswith('\n'):
        env_content += '\n'
    env_content += 'TAVILY_API_KEY=tvly-dev-xxx\n'
    write_file('~/.hermes/.env', env_content)
```

4. **Configure corresponding backends:**
```bash
# For Tavily search backend
hermes config set web.backend tavily
```

**Common environment variables:**
- `TAVILY_API_KEY`: Tavily search API (1000 free queries/month)
- `FAL_KEY`: Fal.ai image generation API (free tier available)
- `OPENAI_API_KEY`: For OpenAI-based services

**Security notes:**
- `.env` files store credentials in plain text
- Ensure proper file permissions (`chmod 600 ~/.hermes/.env`)
- Consider using Hermes' built-in credential management if available

**Important: Protected environment files**
Some Hermes installations protect `.env` files from direct writes by tools. If you encounter "Write denied" errors when trying to update `.env`:

1. **Check if file is protected**: Attempt to read the file first
2. **Use terminal with user confirmation**: Ask user to manually add keys or approve terminal commands
3. **Alternative storage**: Consider storing keys in config.yaml (less secure but more accessible)
4. **User action required**: For protected files, user may need to manually edit the file

**Example workflow for protected .env:**
```python
# First, check if we can read the file
env_content = read_file(path="~/.hermes/.env")["content"]

# Check if key already exists
if "TAVILY_API_KEY" not in env_content:
    # Ask user to add manually or approve terminal command
    print("TAVILY_API_KEY not found in .env file.")
    print("Please add manually or approve terminal command to add it.")
    
    # Option: Ask user to run command
    print("Run this command to add:")
    print('echo "TAVILY_API_KEY=tvly-dev-xxx" >> ~/.hermes/.env')
```

### 6. Test API Connectivity

Use `curl` to verify the API endpoint is accessible:

```bash
curl -s -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "minimaxai/minimax-m2.7",
    "messages": [{"role": "user", "content": "Hello, test"}],
    "max_tokens": 10
  }'
```

A successful response indicates the API is working:
```json
{"id":"chatcmpl-...","object":"chat.completion",...}
```

### 6a. Comprehensive API Testing Script

For thorough testing, create a Python script to validate API functionality:

**`test_nim.py` Example:**
```python
#!/usr/bin/env python3
"""
Test NVIDIA NIM API key validity and functionality
"""

import requests
import json

API_KEY = "nvapi-your-api-key-here"
BASE_URL = "https://integrate.api.nvidia.com/v1"

def test_api_key():
    """Test API key and list available models"""
    url = f"{BASE_URL}/models"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API key valid! {len(data.get('data', []))} models available")
        
        # Check if configured model is available
        configured_model = "meta/llama-3.1-8b-instruct"
        available = any(m.get('id') == configured_model for m in data.get('data', []))
        print(f"Model '{configured_model}' available: {'✅' if available else '❌'}")
        
        return True
    else:
        print(f"❌ API request failed: {response.status_code}")
        return False

def test_chat_completion():
    """Test chat completion functionality"""
    url = f"{BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta/llama-3.1-8b-instruct",
        "messages": [{"role": "user", "content": "Hello, say something short."}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        reply = data['choices'][0]['message']['content']
        print(f"✅ Chat completion successful! Reply: {reply}")
        return True
    else:
        print(f"❌ Chat request failed: {response.status_code}")
        return False

if __name__ == "__main__":
    print("Testing NVIDIA NIM API...")
    
    tests = [
        ("API key validation", test_api_key),
        ("Chat completion test", test_chat_completion),
    ]
    
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} - Passed")
            else:
                print(f"❌ {test_name} - Failed")
        except Exception as e:
            print(f"❌ {test_name} - Exception: {e}")
```

**Usage:**
```bash
# Run from Hermes virtual environment
cd ~/.hermes/hermes-agent && source venv/bin/activate && python ~/test_nim.py
```

### 6b. Duplicate Key Verification

When a user provides new API credentials for an already-configured provider:

1. **Compare with existing configuration** before making changes
2. **Skip update** if keys are identical to avoid unnecessary config changes
3. **Notify user** that configuration is already up-to-date

**Verification steps:**
```python
# Read current NVIDIA NIM configuration
config = read_file(path="~/.hermes/config.yaml", offset=200, limit=50)

# Extract current API key from config
# Compare with new key provided by user
# If identical: configuration already current, no update needed
# If different: update configuration using patch()
```

### 6c. STT (Speech-to-Text) Configuration Testing

For Hermes built-in STT system verification:

**Test faster-whisper installation:**
```bash
# From Hermes virtual environment
cd ~/.hermes/hermes-agent && source venv/bin/activate && python -c "import faster_whisper; print(f'faster_whisper version: {faster_whisper.__version__}')"
```

**Verify STT configuration:**
```python
#!/usr/bin/env python3
"""
Simple Hermes STT configuration test
"""
import os
import sys

hermes_path = os.path.expanduser("~/.hermes/hermes-agent")
sys.path.insert(0, hermes_path)

try:
    from tools.transcription_tools import transcribe_audio, is_stt_enabled, _load_stt_config
    
    config = _load_stt_config()
    print(f"STT Config: {config}")
    print(f"STT Enabled: {is_stt_enabled(config)}")
    
    # Test faster-whisper import
    import faster_whisper
    print(f"faster_whisper version: {faster_whisper.__version__}")
    
    print("✅ STT system configuration complete")
except Exception as e:
    print(f"❌ STT configuration error: {e}")
```

### 7. Verify Hermes Provider Recognition

After adding a custom provider, test if Hermes recognizes it:

```bash
# Option 1: Try the chat command (may not work for custom providers)
hermes chat --help | grep "provider"

# Option 2: Use interactive model selection
hermes model

# Option 3: Check if provider appears in available choices
# Note: Some Hermes versions only show built-in providers in --help
```

**Important Discovery**: Custom providers added via `custom_providers` may not appear in the `--provider` argument list. Instead, you need to use `hermes model` (interactive terminal selection) to switch to custom providers. The provider identifier format is typically `provider-name/model-name` (e.g., `nvidia-nim/minimaxai/minimax-m2.7`).

### 8. Test Model Stability (Recommended)

For NVIDIA NIM API and similar services, test multiple models to find the most stable:

```bash
# Test meta/llama-3.1-8b-instruct (often more stable)
curl -s -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 5
  }' | jq -r '.choices[0].message.content // "ERROR"'

# Explore available models
curl -s -H "Authorization: Bearer your-api-key" \
  https://integrate.api.nvidia.com/v1/models | jq '.data[].id' | head -10
```

**Stability Findings**:
- `meta/llama-3.1-8b-instruct`: Generally stable, fast response (1-3 seconds)
- `minimaxai/minimax-m2.7`: May timeout or be unstable in some cases
- `deepseek-ai/deepseek-v3.2`: Often times out (>30 seconds)
- Test and choose the most reliable model for your use case

### 7. Update Memory with Smart Management

Add provider information to persistent memory with efficient space management:

```python
# Check current memory usage before adding
memory_info = memory(action="list", target="memory")  # Shows current entries and usage

# Example memory entry for NVIDIA NIM
memory_entry = "2026-04-20 - NVIDIA NIM API密钥重新确认：用户再次申请NVIDIA NIM免费API密钥，与现有配置完全相同。测试确认API密钥有效，可访问132个模型，包括已配置的meta/llama-3.1-8b-instruct模型。密钥有效期至2026年10月18日，免费额度每分钟40次调用。Hermes配置已使用此密钥，默认模型为NVIDIA NIM免费模型以避免DeepSeek高成本。"

# Strategy 1: Add if space available
try:
    memory(action="add", target="memory", content=memory_entry)
except Exception as e:
    if "exceed the limit" in str(e):
        # Strategy 2: Replace less critical entries
        # Look for older or less relevant entries to replace
        memory(
            action="replace",
            target="memory",
            old_text="older-entry-to-replace",
            content=memory_entry
        )
```

**Memory Management Best Practices:**

1. **Check before adding**: Always check memory usage before attempting to add new entries
2. **Use replace over add**: When near limit (e.g., >95% usage), prefer replacing existing entries
3. **Prioritize user preferences**: Keep entries about user corrections, preferences, and important configurations
4. **Consolidate similar entries**: Combine related information into single entries to save space
5. **Remove outdated entries**: Clean up old configuration details that are no longer relevant
6. **Use descriptive timestamps**: Include dates in entries for easier management and sorting

**Common memory update patterns:**

```python
# Update existing entry about NVIDIA NIM
memory(
    action="replace",
    target="memory",
    old_text="2026-04-19 - NVIDIA NIM API密钥最终确认",
    content="2026-04-20 - NVIDIA NIM API密钥重新确认：用户再次申请NVIDIA NIM免费API密钥，与现有配置完全相同。测试确认API密钥有效，可访问132个模型，包括已配置的meta/llama-3.1-8b-instruct模型。密钥有效期至2026年10月18日，免费额度每分钟40次调用。Hermes配置已使用此密钥，默认模型为NVIDIA NIM免费模型以避免DeepSeek高成本。"
)

# Add new entry (with space check)
try:
    memory(action="add", target="memory", content="New entry...")
except Exception as e:
    if "exceed the limit" in str(e):
        # Handle memory full scenario
        print("Memory full, need to remove or replace entries")
        # Option: Replace least important entry
        memory(action="replace", target="memory", old_text="Old entry", content="New entry...")
```

## Common Provider Examples

### NVIDIA NIM API
- **Name**: NVIDIA NIM
- **Base URL**: `https://integrate.api.nvidia.com/v1`
- **API Key Format**: `nvapi-...`
- **Model**: `minimaxai/minimax-m2.7`
- **Context Length**: 32768
- **Rate Limits**: 40 calls per minute (free tier)

### Local Ollama
- **Name**: Local (127.0.0.1:11434)
- **Base URL**: `http://127.0.0.1:11434/v1`
- **API Key**: `ollama` (literal string)
- **Model**: Varies (e.g., `qwen2.5:7b`, `gemma4:e4b`)
- **Context Length**: Varies by model

### DeepSeek API
- **Name**: DeepSeek
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key**: `sk-...` or `be5...`
- **Model**: `deepseek-reasoner` or `deepseek-chat`
- **Context Length**: 64000

### Generic OpenAI-Compatible
- **Name**: Your Service Name
- **Base URL**: `https://your-api.com/v1`
- **API Key**: As provided
- **Model**: As specified by provider
- **Context Length**: Check provider documentation

## Advanced: System Integration Verification

After configuring multiple components (API providers, STT, messaging platforms), perform comprehensive system verification:

### 7a. Verify Service Status and Dependencies

**Check Hermes gateway status:**
```bash
# Check if Hermes gateway is running
ps aux | grep "hermes gateway\|python.*gateway" | grep -v grep

# Check running services
ps aux | grep -i "hermes\|python" | grep -v grep | head -10
```

**Test messaging platform connections:**
```python
# For Telegram integration, check if bot is accessible
# From memory or config, verify Telegram token and allowed users
read_file(path="~/.hermes/.env")  # Check TELEGRAM_BOT_TOKEN
read_file(path="~/.hermes/config.yaml", offset=250, limit=10)  # Check telegram enabled
```

### 7b. End-to-End Configuration Audit

Create a configuration audit script to verify all system components:

```python
#!/usr/bin/env python3
"""
Hermes Configuration Audit - Verify all system components
"""
import os
import subprocess
import yaml
import sys

def check_config_file():
    """Verify config.yaml structure and key settings"""
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    checks = []
    
    # Check default model (should be free provider)
    default_model = config.get('model', {}).get('default', '')
    if 'meta/llama-3.1-8b-instruct' in default_model or 'mistral' in default_model:
        checks.append(("✅ Default model", f"Configured to free model: {default_model}"))
    else:
        checks.append(("⚠️ Default model", f"Consider switching to free model (current: {default_model})"))
    
    # Check STT configuration
    stt_enabled = config.get('stt', {}).get('enabled', False)
    if stt_enabled:
        checks.append(("✅ STT enabled", "Speech-to-text is configured"))
    else:
        checks.append(("❌ STT disabled", "Consider enabling for voice support"))
    
    # Check providers
    providers = config.get('custom_providers', [])
    for provider in providers:
        name = provider.get('name', 'Unknown')
        checks.append((f"✅ Provider", f"{name} configured"))
    
    return checks

def check_service_status():
    """Check if essential services are running"""
    checks = []
    
    # Check Hermes gateway
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'hermes gateway' in result.stdout or 'python.*gateway' in result.stdout:
        checks.append(("✅ Hermes gateway", "Running"))
    else:
        checks.append(("❌ Hermes gateway", "Not running (use: hermes gateway run)"))
    
    # Check n8n if configured
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'n8n' in result.stdout:
        checks.append(("✅ n8n service", "Running"))
    else:
        checks.append(("ℹ️ n8n service", "Not running (use: n8n-start to start)"))
    
    return checks

def main():
    """Run all checks and display results"""
    print("=" * 60)
    print("Hermes Configuration Audit")
    print("=" * 60)
    
    all_checks = []
    
    print("\n1. Configuration File Checks:")
    print("-" * 40)
    config_checks = check_config_file()
    all_checks.extend(config_checks)
    for status, message in config_checks:
        print(f"  {status}: {message}")
    
    print("\n2. Service Status Checks:")
    print("-" * 40)
    service_checks = check_service_status()
    all_checks.extend(service_checks)
    for status, message in service_checks:
        print(f"  {status}: {message}")
    
    print(f"\n" + "=" * 60)
    print(f"Summary: {len([c for c in all_checks if '✅' in c[0]])} passed, "
          f"{len([c for c in all_checks if '❌' in c[0]])} failed")
    
    # Return overall status
    failures = len([c for c in all_checks if '❌' in c[0]])
    return failures == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### 7c. Cost Optimization Strategy

**Free-tier prioritization workflow:**

1. **Identify free components:**
   - NVIDIA NIM API (40 calls/min free)
   - Tavily search (1000 queries/month free)
   - Fal.ai image generation (free tier)
   - Local faster-whisper STT (completely free)
   - Edge TTS (Microsoft free service)

2. **Configure fallback order:**
   ```python
   # Example configuration priority:
   # 1. NVIDIA NIM (free)
   # 2. Local Ollama (free, if available)
   # 3. DeepSeek (paid, use only when necessary)
   # 4. OpenAI (paid, use only when necessary)
   ```

3. **Automatic model selection based on task:**
   - Simple tasks: Use `meta/llama-3.1-8b-instruct` (NVIDIA NIM)
   - Complex reasoning: Use `mistralai/mistral-7b-instruct-v0.3` (NVIDIA NIM)
   - Critical tasks: Use paid providers only when free models fail

4. **Monitor and log usage:**
   ```bash
   # Check Hermes dashboard for cost tracking
   hermes-dashboard  # If installed
   
   # Monitor NVIDIA NIM usage via API response headers
   # X-Ratelimit-Limit, X-Ratelimit-Remaining headers
   ```

## Critical: Provider Not Reporting Context Length

Some API providers (especially NVIDIA NIM, Ollama, and some open-source model runtimes) do not report `context_length` in their model metadata. This causes Hermes to default to a conservative value (e.g., 32,768 tokens) which may trigger this launch-blocking error:

```
ValueError: Model <name> has a context window of 32,768 tokens,
which is below the minimum 64,000 required by Hermes Agent.
Choose a model with at least 64K context, or set model.context_length
in config.yaml to override.
```

### Root Cause
- NVIDIA NIM's `/v1/models` endpoint returns models without a `max_context_length` field
- Hermes Agent requires minimum 64K context to operate (handles tool calls, long system prompts, memory injection)
- The error happens at session startup — the Agent refuses to start, not during inference
- **The model itself may actually support 128K+ context** — it's just the metadata that's missing

### Fix: Override `model.context_length` in config.yaml

Set the actual context length for your model. Known values for NVIDIA NIM models:

| Model | Actual Context | Set This |
|-------|---------------|----------|
| meta/llama-3.1-8b-instruct | 128K | `max_context: 128000` |
| meta/llama-3.3-70b-instruct | 131K | `max_context: 131072` |
| meta/llama-3.2-11b-vision-instruct | 128K | `max_context: 128000` |
| meta/llama-4-maverick-17b-128e-instruct | 1M | `max_context: 1048576` |
| gemma-3-27b-it | 128K | `max_context: 131072` |
| google/gemma-4-31b-it | 256K | `max_context: 262144` |

**How to fix:**
```yaml
# ~/.hermes/config.yaml — edit this section
model:
  provider: nvidia-nim
  default: meta/llama-3.3-70b-instruct
  max_context: 131072    # <-- ADD THIS to override the default
  max_tokens: 4096
```

The file is at `~/.hermes/config.yaml`. In the `model:` section, either:
1. Add `max_context: <value>` (inferred value when provider doesn't report it)
2. Set it to the model's actual context length (check model card/docs)

**Verify the fix:**
```bash
hermes doctor        # Should pass the context check
```

### This Error Happens on Gateway, Not CLI

The context window error only blocks **Gateway sessions** (Telegram, Discord, etc.). CLI sessions (`hermes` or `hermes chat -q`) may work fine because they don't perform the same startup validation. Always test on the messaging platform after fixing.

After editing config.yaml, restart the Gateway:
```bash
# Graceful restart (starts new process with --replace)
pkill -f "hermes_cli.main gateway" && sleep 2

# Or if using a startup script
~/hermes/start-gateway-with-proxy.sh

# Verify in logs
grep "Connected to Telegram\|Connected to Discord" ~/.hermes/logs/agent.log | tail -3
```

### Provider-Specific: NVIDIA NIM + Free Tier Models

For NVIDIA NIM free tier specifically, good replacements for `meta/llama-3.1-8b-instruct` that have larger context:

1. **meta/llama-3.3-70b-instruct** (131K context, stronger reasoning, still free)
2. **google/gemma-3-27b-it** (128K context, fast, free)
3. **google/gemma-4-31b-it** (256K context, latest, free)

These are all available on the same NVIDIA NIM endpoint (`https://integrate.api.nvidia.com/v1`) with the same API key, no additional cost.

## Verification Steps

1. **Config Syntax**: Ensure YAML indentation is correct (2 spaces per level)
2. **API Key Security**: API keys are stored in plaintext in config.yaml; consider using `.env` variables if needed
3. **Model Availability**: Verify the specified model exists on the provider
4. **Rate Limits**: Note any usage limits to avoid unexpected failures
5. **Service Integration**: Verify all components work together (API + STT + messaging)
6. **Cost Efficiency**: Ensure free-tier components are prioritized over paid alternatives

## Troubleshooting

### "Invalid provider" errors
- Check `base_url` format (must end with `/v1` for OpenAI compatibility)
- Verify API key format and permissions
- Ensure the provider is accessible from your network (no firewall blocking)

### Configuration not taking effect
- Hermes may need a restart to pick up config changes
- Use `/reset` in chat session to start fresh
- Check for YAML syntax errors with a linter

### API connection failures
- Test with `curl` first to isolate the issue
- Check network connectivity and proxy settings
- Verify API endpoint documentation for exact requirements

## Best Practices

1. **Selective Usage**: Configure smart model routing in Hermes to use providers based on task type and cost
2. **Memory Updates**: Always add provider details to memory for cross-session reference
3. **Testing First**: Use curl or simple test queries before full integration
4. **Rate Limit Awareness**: Note free tier limits and implement retry logic if needed
5. **Backup Config**: Consider backing up config.yaml before making changes

## Related Commands

- `hermes model` - Interactive provider selection
- `hermes config edit` - Manual configuration editing
- `hermes doctor` - Configuration validation
- `/model [name]` - Change model within a session

## Key Learnings from Experience

### From Implementation Experience

**Configuration Management:**
1. **Verify before updating**: Always check current configuration before making changes, especially when users provide "new" credentials that may be identical to existing ones
2. **Test thoroughly**: Create comprehensive test scripts for API connectivity, STT functionality, and system integration
3. **Memory efficiency**: Manage memory space proactively by replacing outdated entries instead of always adding new ones

**Cost Optimization:**
1. **Prioritize free tiers**: Configure Hermes to use free providers (NVIDIA NIM, Tavily, Edge TTS, faster-whisper) by default
2. **Automatic fallback**: Set up smart model routing that uses paid providers only when free options fail
3. **Monitor usage**: Track API call counts and costs, especially when users report unexpected expenses

**System Integration:**
1. **Comprehensive auditing**: Regularly audit all system components (providers, STT, messaging platforms, services)
2. **Service verification**: Check running processes and connectivity for all integrated services
3. **User preferences**: Respect user preferences (e.g., graphical interfaces over CLI, simple startup commands)

**Common Pitfalls and Solutions:**
- **Duplicate API keys**: Users may provide the same key multiple times; verify against existing config
- **Memory limits**: Memory has fixed capacity (2200 chars); use replace() instead of add() when near limit
- **Protected files**: `.env` files may be write-protected; work with user to add keys manually
- **Model stability**: Some free models may be unstable; test and select reliable alternatives

## See Also

- [Hermes Configuration Documentation](https://hermes-agent.nousresearch.com/docs/user-guide/configuration)
- [Hermes Providers Guide](https://hermes-agent.nousresearch.com/docs/integrations/providers)
- [NVIDIA NIM API Documentation](https://build.nvidia.com/nim/api-docs)
- [ResearchWang's Hermes Advanced Configuration Guide](https://x.com/ResearchWang/status/2045812932538438001) - Chinese guide for advanced Hermes tool configuration