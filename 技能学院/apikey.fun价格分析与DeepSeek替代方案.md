# APIKEY.FUN 价格分析 & DeepSeek V4 Flash替代方案

> 2026-05-17 整理
> 背景：DeepSeek折扣（V4 Pro 2.5折）至2026/05/31截止，评估备选方案

---

## 一、DeepSeek 官方当前定价

### deepseek-chat（= deepseek-v4-flash）← 主驱动
| 计费项 | 价格（￥/百万tokens） |
|-------|-------------------|
| 输入（缓存命中） | **0.02** |
| 输入（缓存未命中） | **1** |
| 输出 | **2** |
**这个价格从未变过，折扣结束后也不变。**

### deepseek-reasoner（= deepseek-v4-pro）← 2.5折到5月底
| 计费项 | 折后价 | 原价 |
|-------|-------|------|
| 输入（缓存命中） | 0.025 | 0.1 |
| 输入（缓存未命中） | 3 | 12 |
| 输出 | 6 | 24 |

---

## 二、APIKEY.FUN 实际情况
**apikey.fun不做DeepSeek中转。** 只提供三类产品：

### 1. Claude Code 分组（Claude全家桶）
| 模型 | 输入 | 输出 | 折扣 |
|-----|------|------|------|
| claude-opus-4-7 | ￥3.50 | ￥17.50 | 1折 |
| claude-sonnet-4-6 | ￥2.10 | ￥10.50 | 1折 |
| claude-haiku-4-5 | ￥0.70 | ￥3.50 | 1折 |

**官方价 ¥35 → apikey.fun ￥3.50，省90%**

### 2. Codex 分组（GPT/OpenAI全家桶）
| 模型 | 输入 | 输出 | 缓存读取 | 折扣 |
|-----|------|------|---------|------|
| **gpt-5.5** | ￥2.50 | ￥15.00 | ￥0.25 | 省93% |
| **gpt-5.4** | ￥1.25 | ￥7.50 | ￥0.13 | 省93% |
| **gpt-5.4-mini** | **￥0.38** | **￥2.25** | **￥0.04** | 省93% |
| gpt-5.2 | ￥0.88 | ￥7.00 | ￥0.09 | 省93% |
| gpt-5.3-codex | ￥0.88 | ￥7.00 | ￥0.09 | 省93% |

### 3. Gemini 分组 — 空（无可用模型）

---

## 三、能力对比：DeepSeek V4 Flash vs GPT-5.4-mini
数据来源：Artificial Analysis 基准测试

| 维度 | DeepSeek V4 Flash | GPT-5.4 mini (xhigh) |
|-----|------------------|---------------------|
| **智力指数** | **47分** | **49分** |
| 排名 | #10/85（推理模型） | #26/146（全模型） |
| **输出速度** | **93.9 tokens/s** | **161.5 tokens/s** ⚡更快 |
| 输入价格（官方） | $0.14/百万 | $0.75/百万 |
| 输出价格（官方） | $0.28/百万 | $4.50/百万 |
| 上下文 | 100万tokens | 40万tokens |
| 模型权重 | 开源(MIT) | 闭源 |

### apikey.fun Codex价 vs DeepSeek 官方价
| 场景 | DeepSeek V4 Flash | gpt-5.4-mini (apikey.fun) |
|-----|------------------|--------------------------|
| 输入 | ￥1.00/百万 | ￥0.38/百万 ✅更便宜 |
| 输出 | ￥2.00/百万 | ￥2.25/百万 ❌略贵 |

**结论：gpt-5.4-mini 能力略高于 V4 Flash（49 vs 47分），输入更便宜，可做备胎**

---

## 四、你的5个API通道总览

| # | 名称 | API地址 | 默认模型 | 余额 | 用途 |
|---|------|---------|---------|------|------|
| 1️⃣ | **DeepSeek官方** | 官方API | deepseek-chat (V4 Flash) | 按量计费 | **主驱动**，日常对话、工具调用 |
| 2️⃣ | **Ollama本地** | http://127.0.0.1:11434/v1 | qwen2.5:7b | 免费 | 本地离线备份，断网也能用 |
| 3️⃣ | **NVIDIA NIM** | integrate.api.nvidia.com/v1 | meta/llama-3.1-8b | 免费 | 云备份，Llama系列模型 |
| 4️⃣ | **apikey.fun** | https://apikey.fun/v1 | gpt-5.4-mini | **¥30** | 备用GPT，输入比DeepSeek便宜 |
| 5️⃣ | **硅基流动** | https://api.siliconflow.cn/v1 | deepseek-ai/DeepSeek-V4-Flash | **¥10.36** | DeepSeek备用，还有Qwen/Kimi/GLM |

### 5个通道的定位
1️⃣ **DeepSeek官方 → 主力**（日常都用这个）
2️⃣ **Ollama → 离线保底**（断网、debug测试）
3️⃣ **NVIDIA NIM → 免费Llama云备胎**
4️⃣ **apikey.fun → GPT备胎**（¥30，gpt-5.4-mini速度快）
5️⃣ **硅基流动 → DeepSeek冗余备胎**（¥10，还能用DeepSeek V4 Flash/Qwen/Kimi等开源模型）

---

## 五、推广返利计划

### apikey.fun 5%返利
- **邀请码：YJHRABT5EZ23**
- **邀请链接：https://apikey.fun/register?aff=YJHRABT5EZ23**
- 别人通过链接注册充值并消费，你拿 **5% 返到余额**
- 返利自动到账，永不过期
- 适合有开发者群/AI工具群/副业群的人推广

### 硅基流动 推荐官计划
- 硅基流动也有「推荐官计划」，邀请好友赢全平台通用代金券
- 需要登录后看具体规则

---

## 六、Hermes 配置状态

| 项目 | 状态 |
|------|------|
| DeepSeek官方 | ✅ 默认provider |
| Ollama本地 | ✅ custom_providers已配 |
| NVIDIA NIM | ✅ custom_providers已配 |
| apikey.fun | ✅ custom_providers已配（¥30余额） |
| 硅基流动 SiliconFlow | ✅ custom_providers已配（¥10.36余额） |
| **生效状态** | **⏳ 需重启Gateway**：`hermes gateway restart` |

### 配置方式
5个provider已全部写入 `~/.hermes/config.yaml` 的 `custom_providers` 段。

在Web UI（localhost:8648）→ 设置 → 模型选择，可随时切换使用哪个provider。

---

### 一句话
**马照跑。5路备胎，AI自由。**
