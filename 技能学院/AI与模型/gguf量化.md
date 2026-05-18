---
tags: [技能, AI]
---

# GGUF 量化
**技能名：** gguf-quantization

## ⚡ 简介
将模型量化为 GGUF 格式，用于 llama.cpp 本地推理。支持 Q2_K 到 Q8_0 各级量化。

## 📋 使用方法
跟我说：
- "帮我把这个模型量化成 Q4_K_M"
- "这个 safetensors 转成 GGUF"

## 💡 案例
> **你说：** "帮我把这个模型量化一下，在本地跑"
> **我：** 下载模型 → 用 llama.cpp 的 convert.py 转 GGUF → 量化到 Q4_K_M
