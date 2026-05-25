# 系统 API 密钥清单

> ⚠️ 本文件仅用于记录各 API 服务商、状态和 Key 截尾，**完整 Key 在 `~/.hermes/config.yaml` 和 `~/.hermes/.env` 中**
> 更新日期: 2026-05-25

---

## 当前在用

### 1. DeepSeek (主力)
- **API Key**: `set in .env`
- **余额**: ¥8.48 (2026-05-24充值)
- **模型**: `deepseek-chat`, `deepseek-reasoner`
- **状态**: 正常 ✅
- **用途**: 日常对话主力

### 2. apikey.fun (第一备选)
- **API Key**: `sk-abdf85111a04fd9068e5ecd1c8284ede676019e4f5c5f8809ee15f040421654a`
- **余额**: ¥30 (用户告知)
- **模型**: GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5-codex, GPT-Image 系列等
- **base_url**: `https://slb.apikey.fun/v1` (负载均衡，最快最稳)
- **状态**: 需要时测试可用 ✅
- **注**: 偶尔间歇性 SSL 断连，重试即可恢复

### 3. NVIDIA NIM (第二备选)
- **API Key**: `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`
- **模型**: `meta/llama-3.1-8b-instruct`, `meta/llama-3.3-70b` 等
- **状态**: 免费额度，正常可用 ✅
- **注**: 每日有限次调用

### 4. Ollama 本地 (第三备选)
- **无需 Key**
- **模型**: `qwen2.5:7b`, `gemma4:e4b`, `qwen3:4b`
- **状态**: 免费，正常 ✅
- **注**: 本地模型，能力弱但稳定

---

## 已失效 / 废弃

### SiliconFlow (硅基流动)
- **API Key**: `sk-ila...wauo` (截尾)
- **原因**: Key 已失效，API 返回 "Api key is invalid"
- **之前余额**: ¥14.19 (5月4日)
- **建议**: 如需用，去 cloud.siliconflow.cn 重新生成 Key

### Hyperbolic
- **原因**: Key 免费配额用完，余额为0
- **之前曾用于**: 图像生成 (FLUX.1-schnell)

### apikey.fun 旧配置
- **旧 base_url**: `https://apikey.fun/v1` → 已改为 `https://slb.apikey.fun/v1`
- **旧 key (截断)**: `sk-abd...654a` → 已改为完整 Key

---

## Fallback 优先级

```
DeepSeek (主力)
  → apikey.fun (¥30余额，SLB负载均衡)
  → NVIDIA NIM (免费额度)
  → Ollama 本地 (免费，能力弱)
```

配置位置: `~/.hermes/config.yaml` → `fallback_providers`

---

## 平台地址

| 平台 | 网址 | 注册方式 |
|:----|:----|:--------|
| DeepSeek | platform.deepseek.com | 手机/邮箱 |
| apikey.fun | apikey.fun | 需要确认 |
| NVIDIA NIM | build.nvidia.com | 邮箱 |
| Ollama | ollama.com (本地) | 本地安装 |

---

## 更新记录

- 2026-05-25: 新建，汇总全部 API 状态，更新 apikey.fun base_url 为 slb 负载均衡地址
