---
tags: [开源项目, AI, 房地产, 房源搜索, 自动化]
created: 2026-06-22
source: https://x.com/github_daily/status/2067532792653869560
---

# AI Real Estate Assistant 🏠

> AI 驱动的房地产对话式搜索与数据分析平台

## ⚡ 简介

开源 AI 房地产助手，通过自然语言对话帮用户搜索匹配房源，内置房贷计算器、租买对比、投资回报分析等财务工具。支持地图查看房源分布和区域对比。多语言（含中文），Docker 一键部署。

## 📋 核心技术栈

- **后端：** Python 3.12+ / FastAPI
- **前端：** Next.js 16 / TypeScript 5.x
- **数据库/向量：** ChromaDB（语义+关键词混合搜索，MMR 重排序，相关性↑30-40%）
- **AI：** 6+ LLM 提供商（OpenAI、Anthropic、Google、Grok、DeepSeek、Ollama），自动 fallback
- **部署：** Docker / K8s 支持
- **Demo：** https://realestate-web-dz1y.onrender.com/

## 💡 核心功能

- 🗣️ **自然语言搜房** — "预算50万以内的两居室"即可匹配
- 🤖 **多模型 AI** — 多提供商智能路由
- 📊 **财务工具** — 房贷计算器、租vs买对比、投资回报分析、TCO
- 🗺️ **交互地图** — 房源聚类、区域对比
- 🌍 **9种语言** — 中文、英文、波兰语、俄语、德语、西班牙语、意大利语、葡萄牙语、土耳其语、乌克兰语

## 💡 参考价值（对鑫球汇）

这套项目的架构思路（FastAPI+Next.js+向量检索+财务分析）如果应用到鑫球汇的房源管理系统，可以实现：
- AI对话搜房替代传统筛选
- 房源自动匹配推荐
- 经营数据分析可视化

## 项目链接

- GitHub: https://github.com/AleksNeStu/ai-real-estate-assistant
- 许可证: MIT (1317 commits, 7000+ tests)
