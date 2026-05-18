# The Agency (agency-agents) 深度评估

**链接**: https://github.com/msitarzewski/agency-agents  
**⭐ 99,768 stars | 🍴 16,559 forks | ⚡ Shell | 📄 MIT | 最后更新: 2026-04-12**

---

## 这是什么？— AI Agent 角色包/工作流模板库

不是一个工具或框架，而是一个**开源的角色/Agent定义集合**（144个专业Agent，横跨12个部门）。每个Agent是一个Markdown文件，包含：

- **角色身份与性格**（独特的说话风格、行为模式）
- **核心使命与工作流程**（step-by-step方法论）
- **技术交付物与代码示例**
- **成功指标与质量标准**

## 能装吗？— **不用装，这是"规则包"不是"软件"**

**安装方式**：把 `.md` 文件复制到 AI 工具的 agent 目录下就行（如 `~/.claude/agents/`、`~/.github/agents/`），本质是**提示词模板**，不是有依赖的可执行程序。

| 问题 | 答案 |
|------|------|
| 能装到 Hermes 上吗？ | ✅ 可以，但需要手工转换格式（Hermes 用的是 SKILL.md） |
| 能装到 OpenClaw 上吗？ | ✅ 官方自带 convert.sh 脚本适配 OpenClaw |
| 需要 GPU/特殊硬件吗？ | ❌ 不需要，纯文本模板 |
| Intel Mac 兼容？ | ✅ 完全兼容 |

## 有什么用？— **给 AI 打工人的"角色扮演指南"**

### 核心价值（对老板来说）

**🏗️ EPC业务直接可用的Agent：**

| Agent | 用途 |
|-------|------|
| Civil Engineer | 结构分析、多标准建筑规范（Eurocode/ACI/AISC） |
| Government Digital Presales Consultant | 政府数字化项目投标书、标书方案撰写 |
| Supply Chain Strategist | 供应链管理、采购策略 |
| Financial Analyst | 财务建模、项目预算分析 |
| Compliance Auditor | SOC 2/ISO 27001 合规审计 |
| Document Generator | PDF/PPTX/DOCX/XLSX 报告生成 |
| MCP Builder | MCP Server 构建（直接相关！） |

**🎯 副业/内容创作Agent：**

| Agent | 用途 |
|-------|------|
| 小红书 Specialist | 小红书写真、趋势内容 |
| 抖音 Strategist | 短视频平台运营 |
| Xiaohongshu Specialist | 小红书增长、美学叙事 |
| WeChat Official Account Manager | 公众号运营 |
| 知乎 Strategist | 知乎知识分享、lead generation |
| Reddit Community Builder | Reddit社区营销 |
| Baidu SEO Specialist | 百度搜索优化 |
| China E-Commerce Operator | 淘宝/拼多多运营 |
| Private Domain Operator | 微信私域运营 |

**🛠️ 和技术栈直接相关的Agent：**

| Agent | 用途 |
|-------|------|
| MCP Builder | 构建 MCP Server 扩展 AI 能力 |
| Voice AI Integration Engineer | 语音 AI 集成（STT/TTS） |
| Code Reviewer | PR审查、代码质量 |
| DevOps Automator | CI/CD 管道、自动化运维 |
| Backend Architect | API设计、数据库架构 |
| AI Engineer | ML模型部署、AI集成 |

### 与你的现有体系的互补性

| 现有能力 | The Agency 补充什么？ |
|---------|-------------------|
| Hermes Agent (通用助理) | 专业角色分工——让每个对话有"专家人设" |
| 小红书技能 | Xiaohongshu Specialist → 更精准的运营方法论 |
| stock-robot 技能 | Financial Analyst → 更专业的投资分析框架 |
| bidding-qualification-packaging 技能 | Government Digital Presales Consultant → 更强的政府采购方案撰写 |
| 出海接单方案 | 各领域专家Agent包装成服务，提高 Upwork 竞标成功率 |

## 有必要吗？— **🟢 可以搞，但不急**

### 值得干的理由

1. **99,768⭐** = 社区验证过的质量，144个Agent覆盖极广
2. **和 Hermes 生态互补**——Hermes 提供"助理框架"，The Agency 提供"各行业专家角色"
3. **EPC相关Agent** (Civil Engineer/Government Presales/Supply Chain) 对主业有直接价值
4. **副业场景Agent**（小红书/抖音/知乎/私域运营）对副业有帮助
5. **MCP Builder** 直接帮我们构建更多 MCP Server
6. **MIT许可证**，随便改

### 不急着搞的理由

1. **转换成本**——144个 .md 文件要适配 Hermes 的 SKILL.md 格式，手工转不现实
2. **质量参差**——99K stars 很多是"收藏即支持"，实际142个 open issues 说明不少 Agent 还是理论模板，未经过真实业务验证
3. **你的 Hermes 已有独家技能库**（stock-robot/video-script/EPC结算等），这些是真正跑在生产环境的，不是模板
4. **99.8K stars 但 "Language: Shell"**——说明这是集合项目，核心资产是 .md 不是代码，star 数含水量高

### 建议优先级

1. 🔥 **优先装 MCP Builder Agent** → 配合已有 MCP 生态直接出活
2. 🟢 **第二步装小红书/抖音/知乎/私域 Agent** → 优化副业内容策略
3. 🔶 **第三步装 Civil Engineer/Government Presales** → EPC业务方案润色
4. ⏸️ **其余按需取用**——不需要一次性装144个

## 怎么装？

最简单的方式——**只用你最需要的几个Agent**，手工复制内容到对应的 SKILL.md 或 项目文件：

```bash
# 克隆项目
git clone https://github.com/msitarzewski/agency-agents.git /tmp/agency-agents

# 挑选需要的Agent复制到Hermes skills
cp /tmp/agency-agents/specialized/specialized-mcp-builder.md ~/.hermes/skills/
```

或者用官方脚本装到 OpenClaw：
```bash
cd /tmp/agency-agents
./scripts/convert.sh --tool openclaw
./scripts/install.sh --tool openclaw
```
