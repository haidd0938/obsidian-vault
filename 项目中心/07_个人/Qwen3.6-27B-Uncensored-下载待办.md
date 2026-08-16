---
tags: [download-todo, ai-model, gguf, qwen]
date: 2026-08-16
status: 待下载
---

# 🤖 Qwen3.6-27B-Uncensored-HauhauCS-Aggressive（下载待办）

> 用户 2026-08-16 要求保留，**后期找空间下载**（未指定目标机器/时间）

## 模型信息

| 项 | 值 |
|----|-----|
| HuggingFace | https://huggingface.co/HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive |
| 作者 | HauhauCS |
| 最后更新 | 2026-04-24 |
| 下载量 | 347,147 |
| likes | 674 |
| 格式 | **GGUF**（llama.cpp 可直接跑，支持 CPU/Metal/CUDA） |
| 特性 | Uncensored + Aggressive 版本，含 mmproj 多模态投影（可看图） |

## 文件清单（总约 170GB 全量，按需选一个量化即可）

| 量化 | 大小 | 适用 |
|------|------|------|
| IQ2_M | 10.0 GB | 最低配（效果较差） |
| IQ3_M | 12.6 GB | 低配 |
| IQ3_XS | 12.0 GB | 低配 |
| Q2_K_P | 11.5 GB | 低配 |
| Q3_K_P | 14.3 GB | 中低配 |
| **Q4_K_P** | **17.5 GB** | ⭐ 推荐（平衡） |
| IQ4_XS | 15.1 GB | 中配 |
| Q5_K_P | 20.8 GB | 中高配 |
| Q6_K_P | 23.2 GB | 高配 |
| Q8_K_P | 32.0 GB | 最高质量 |
| mmproj-f16 | 0.9 GB | 多模态（可看图，按需） |

## 下载方式（到时用）

```bash
# 需要代理（国内直连 HF 不稳定）
# 单文件下载：
curl -L -x http://127.0.0.1:7892 \
  "https://huggingface.co/HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive/resolve/main/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-Q4_K_P.gguf" \
  -o Qwen3.6-27B-Q4_K_P.gguf

# 或用 huggingface-cli（更稳，支持断点续传）：
# pip install -U "huggingface_hub[cli]"
# huggingface-cli download HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive \
#   --include "*Q4_K_P.gguf" --local-dir ./qwen27b
```

## 运行参考（下载后）

- llama.cpp / Ollama 直接加载 GGUF
- 27B 量化后：Q4_K_P 17.5GB —— 需要至少 20GB+ 内存/显存（M 芯片 32GB 统一内存可跑）
- 老板 Intel Mac 16GB 内存跑不动 Q4（需 Q2/IQ2 且很慢）→ 目标空间建议：NAS / 云主机 / 以后 M 芯片 Mac

## 触发条件（什么时候下载）

- 用户说"下载那个模型" / "找个空间下 Qwen3.6"
- 用户提供目标机器/空间（NAS、云主机、新电脑）
