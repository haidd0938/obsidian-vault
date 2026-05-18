---
tags: [技能, AI]
---

# vLLM 推理服务
**技能名：** serving-llms-vllm

## ⚡ 简介
vLLM：高性能 LLM 推理引擎，支持 PagedAttention、Continuous Batching，提供 OpenAI 兼容 API。

## 📋 使用方法
跟我说：
- "帮我用 vLLM 部署一个模型"
- "启动 vLLM 服务器，跑XXX模型"

## 💡 案例
> **你说：** "帮我在本机用 vLLM 部署 Qwen2.5-7B"
> **我：** vLLM serve Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4 --host 0.0.0.0 --port 8000
