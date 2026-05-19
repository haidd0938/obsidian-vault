---
tags: #AI生图 #AI视频 #工具收藏 #评估
created: 2026-05-19
rating: 🟢 强烈推荐
---

# Meigen AI — 生图/生视频平台深度评估

> 一句话：一次性付费，每张图¥0.1+，多模型聚合接入，MCP/OpenClaw双集成路径

## 基本信息

| 项目 | 内容 |
|------|------|
| 官网 | https://meigen.ai |
| 邀请链接 | https://meigen.ai/invite/NR4JUV2R |
| 开发商 | Meigen Creative L.L.C.（美国怀俄明州） |
| 邀请码 | NR4JUV2R（双方都有积分） |
| 价格模式 | **一次性购买积分（永久有效）**，无订阅 |
| 最低单价 | ¥0.1/张（Z Image Turbo / Flux 2 Klein） |
| 核心价值 | 多模型一站聚合 + 一次性付费 + 丝滑交互 |

## 支持模型

### 生图模型

| 模型 | 积分/张 | 速度 | 特点 |
|------|---------|------|------|
| **GPT Image 2.0** | 2-80（依分辨率） | ~45s | OpenAI 官方，文字渲染近乎完美 |
| **Nanobanana Pro** | 10 | ~46s | 高画质 |
| **Nanobanana 2** | 5 | ~38s | 性价比 |
| **Seedream 5.0 Lite** | 5 | ~35s | 字节跳动模型 |
| **Seedream 4.5** | 5 | ~17s | 最快之一 |
| **Midjourney V8.1** | 15/4张 | ~45s | 四张候选图 |
| **Flux 2 Klein** | 2 | ~18s | 最便宜草稿 |
| **Z Image Turbo** | 2 | ~12s | 最便宜+最快 |

### 生视频模型

| 模型 | 积分/秒 | 支持 | 特点 |
|------|---------|------|------|
| **Seedance 2.0** | 13-42/秒 | Fast & Pro | 支持参考视频 |
| **Happyhorse 1.0** | 2-3/秒 | 文生视频+图生视频 | 有音频 |
| **Veo 3.1**（待确认） | - | - | Google |

## 集成方案

### 路径1：OpenClaw Skill（✅ 已安装成功）
```bash
openclaw skills install creative-toolkit
```
- 安装在 ~/.openclaw/workspace/skills/creative-toolkit/
- 版本 v1.0.33
- 含 1,446 条精选 prompt 搜索
- 已确认：通过 `mcporter` 调用 search_gallery / enhance_prompt 等工具
- **免费工具无需API Key**

### 路径2：MCP Server（推荐给Hermes）
GitHub: https://github.com/jau123/MeiGen-AI-Design-MCP
- 1.2k ⭐
- 原生 MCP 协议，Hermes 可直接对接
- 配置方式：
  ```json
  // ~/.config/mcporter/config.json
  {
    "mcpServers": {
      "creative-toolkit": {
        "command": "npx",
        "args": ["-y", "meigen@1.3.1"]
      }
    }
  }
  ```
- 配置 API Token（从 meigen.ai 设置页获取）

### 路径3：Figma 插件
- 可在 Figma 社区安装

## 优缺点分析

### 优势 ✅
1. **一次性付费** — 积分永久有效，无订阅压力
2. **多模型聚合** — 8+ 生图 + 3+ 生视频模型一个接口
3. **交互流畅** — 老板亲测"不是那种磕磕绊绊的感觉"
4. **价格极低** — Z Image Turbo 2积分/张 ≈ ¥0.1+/张
5. **中文支持** — 全中文界面
6. **MCP生态原生** — 比 Midjourney 好集成得多
7. **Prompt 库巨赞** — 1,446 条精选带图带热度数据

### 劣势 ❌
1. **不是完全开源** — 只是前端聚合，底层调各厂商 API
2. **非中国公司** — 需要科学上网
3. **视频模型较贵** — Seedance 2.0 13-42积分/秒
4. **模型不是自己训练的** — 哪天某厂商改价/限制可能影响
5. **MCP 需要 API Token 才能生图** — 免费只能搜prompt

## 结论

> **🟢 强烈推荐** — 特别是对于需要：
> - 频繁生图/生视频的老板
> - 不想每月交订阅费
> - 想要一个接口调所有模型
> - 需要MCP/Hermes集成的自动化工作流

**适合场景：**
- 小红书封面生成（GPT Image 2 文字渲染完美）
- EPC施工现场用 Nanobanana 生成效果图
- 台球俱乐部活动海报（Midjourney V8.1）
- 出海接单的素材图

## 配套资源

### nanobanana-trending-prompts
- GitHub: https://github.com/jau123/nanobanana-trending-prompts
- ⭐ 555, Fork 73
- 1,446 条精选 prompt（含 GPT Image 2 + Nanobanana）
- 6大分类：摄影(533)、插画3D(370)、产品(239)、美食(156)、海报(146)、UI(52)
- 每条约有 268 ❤️、17,193 次浏览（社交验证）
- 数据结构：rank/id/prompt/author/likes/views/image/model/categories/score/date/source_url
- 评分机制：基于 likes/views 的热度排序
- 语言：绝大多数英文，3%含中文字符
- 更新频率：几乎每周更新，最近一次 2026-04-29
- 附赠：系统提示词优化器（中英文双语版）
- 许可证：CC BY 4.0
- 注意：当前不包含 Seedance 2（视频）的 prompt

### 实操建议
1. 先注册 meigen.ai（用邀请码 NR4JUV2R 拿积分）
2. 安装 OpenClaw Skill 测试免费搜索/增强功能
3. 配置 MCP Server 接入 Hermes
4. 从 prompt 仓库挑灵感 → enhance_prompt → generate_image
5. 需要生视频时用 Seedance 2.0
