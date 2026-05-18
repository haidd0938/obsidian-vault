---
tags: [技能, AI]
---

# llama.cpp 本地推理
**技能名：** llama-cpp

## ⚡ 简介
本地运行 GGUF 格式的大模型。你的 Mac 上已经装了 Ollama，有 qwen2.5:7b 和 gemma4 等模型。

## 📋 使用方法
跟我说：
- "帮我跑一下 qwen2.5，写个XXX"
- "用本地的 gemma4 分析这段内容"
- "我想试试这个新模型，帮我找个 GGUF"
- "在本地跑个大模型试试"

> ⚠️ 你的 Mac 是 Intel 芯片，没有 GPU 加速，7B 模型可以跑但速度一般

## 💡 案例
> **你说：** "贾维斯，帮我用 ollama 跑一下 qwen2.5，总结这段话"
> **我：** 调用 ollama run qwen2.5:7b 做总结
