---
name: free-image-generation-api
category: mlops
description: 免费/低价AI图像生成API接入，适用于Intel Mac无GPU环境。支持SiliconFlow、Hyperbolic等平台。
---

# Free Image Generation API

## Overview

Intel Mac无GPU环境下，图像生成只能通过云端API完成。本技能管理免费/低价的图像生成API配置和使用。

## Primary Provider: SiliconFlow (硅基流动)

| Detail | Value |
|--------|-------|
| **Website** | https://siliconflow.cn |
| **API Base** | `https://api.siliconflow.cn/v1` |
| **Auth** | Bearer Token in Authorization header |
| **Account** | `haidongdong0938@gmail.com` (微信登录) |
| **Remaining Balance** | ¥14.19 (as of 2026-05-04) |

### Supported Image Models

| Model ID | Cost/Image | Quality | Notes |
|----------|-----------|---------|-------|
| `Qwen/Qwen-Image` | ¥0.05/张 (5分) | 中文理解好 | **推荐默认** |
| `black-forest-labs/FLUX.1-schnell` | ¥0.20/张 (2毛) | 最高质量 | 偶尔API禁用 |
| `black-forest-labs/FLUX.1-dev` | ¥0.25/张 | 高质量 | 相对稳定 |
| `Kwai-Kolors/Kolors` | ¥0.10/张 (1毛) | 快 | 风格偏写实 |
| `Tongyi-MAI/Z-Image-Turbo` | 免费额度 | 快 | — |

### Other Models Available

Also supports: LLMs (DeepSeek, Qwen), Embedding (BAAI/bge), STT (SenseVoiceSmall), TTS (CosyVoice), VLMs (Qwen-VL), Rerank (BAAI/bge-reranker).

## Secondary Provider: Hyperbolic

| Detail | Value |
|--------|-------|
| **API Key** | `sk_live_om-ieUW-QNEYt9wJVt0ogQIwkA8AGrajFBNTcTm01pabwf4DsrWYQJrqg16sBeuck` |
| **API Base** | `https://api.hyperbolic.xyz/v1` |
| **Status** | ❌ Free credits exhausted (402 error) |

## Usage

### Via Python

```python
import requests
API_KEY = "sk-..."
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
payload = {
    "model": "Qwen/Qwen-Image",
    "prompt": "your prompt",
    "n": 1,
    "size": "1024x1024"
}
resp = requests.post("https://api.siliconflow.cn/v1/images/generations",
                     headers=HEADERS, json=payload, timeout=120)
if resp.status_code == 200:
    img_url = resp.json()["images"][0]["url"]
    img_data = requests.get(img_url).content
    with open("output.png", "wb") as f:
        f.write(img_data)
```

### Via Hermes config.yaml

Configured as custom provider in config.yaml. Use `image_gen` tool in chat.

## Pitfalls

1. **Filename zero-width spaces**: When generating filenames programmatically, invisible Unicode chars (\\u200b, \\u200c) can leak in. Always verify with `python3 -c "print(repr(filename))"`. Fix with `os.rename()`.
2. **FLUX occasionally disabled**: If 403/404 on FLUX, fall back to `Qwen/Qwen-Image` or `Kwai-Kolors/Kolors`.
3. **Desktop path**: User home is `/Users/mac`, NOT `/Users/haidd`. Always use absolute path `/Users/mac/Desktop/`.
4. **Timeouts**: Image gen takes 15-60s. Set timeout >= 120s.
5. **Rate limits**: SiliconFlow has no strict rate limit, but Hyperbolic 429s on frequent calls.

## References

- Obsidian vault has skill cards for `信息套利方法论`, `热点追踪工具箱`, `免费图像生成API` under `技能学院/研究分析/`
- Config.yaml stores SiliconFlow API key under custom providers section
