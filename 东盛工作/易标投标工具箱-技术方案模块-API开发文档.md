# 易标投标工具箱 - 技术方案模块接口开发文档

> 基于 v2.6.1 反编译分析，React SPA + Electron IPC 架构

---

## 一、整体架构

### 技术栈
- **渲染层**: React 18 + Radix UI (Popper, Tooltip, Dialog, FocusScope)
- **图表**: Mermaid (流程图/甘特图) + Cytoscape (关系图/思维导图)
- **文件解析**: PDF.js (pdfParseService) + DocX/fastre
- **AI 层**: Electron IPC → Node.js → AI API（支持 OpenAI 协议）
- **存储**: better-sqlite3 (本地 SQLite)

### 进程模型
```
┌─────────────────────────────────────┐
│            Electron Main             │
│  ┌───────────────────────────────┐   │
│  │ ipc/index.cjs (IPC handlers)   │   │
│  │   ├── aiService.cjs           │   │
│  │   ├── bidAnalysisTaskService   │   │
│  │   ├── fileService.cjs         │   │
│  │   ├── pdfParseService.cjs     │   │
│  │   └── webSocketService.cjs    │   │
│  └───────────────────────────────┘   │
│                                   │
│        Electron Renderer             │
│  ┌───────────────────────────────┐   │
│  │  React SPA (dist/assets/)     │   │
│  │  ├── 技术方案模块 (核心)       │   │
│  │  ├── 标书查重                  │   │
│  │  ├── 废标项检查                │   │
│  │  ├── 错别字检查                │   │
│  │  ├── 逻辑谬误检查              │   │
│  │  ├── 素材库/模板库/案例库      │   │
│  │  └── 知识库                    │   │
│  └───────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 关键路径
- `dist/assets/` — 编译后的 React SPA（minified 868KB JS + CSS）
- `electron/services/` — Node.js 后台服务（IPC handlers）
- `electron/ipc/index.cjs` — IPC 路由注册

---

## 二、AI 服务层 (aiService.cjs)

### 接口

#### `hx.chat()` — 通用文本对话
```
请求: {messages, temperature?, logTitle?}
返回: string (AI 回复文本)
```
请求体遵循标准 OpenAI Chat API 格式：
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.1
}
```

#### `hx.requestJson()` — 结构化输出
```
请求: {messages, temperature?, logTitle?}
返回: Object (自动解析 JSON)
```
AI 服务内部处理 `response_format: {type: "json_object"}`。

---

## 三、核心模块：技术方案生成

### 3.1 提取项定义 (qb 数组)

每个提取项结构：
```typescript
interface ExtractionItem {
  id: string;            // 唯一标识
  label: string;         // 中文显示名
  description: string;   // 功能描述
  required: boolean;     // 是否必选
  output: 'markdown' | 'json';  // 输出格式
  buildTaskPrompt: () => string; // 生成 AI 提示词
}
```

#### 完整提取项列表

| ID | Label | Required | Output | 用途 |
|----|-------|----------|--------|------|
| `projectOverview` | 项目概述 | ✅ | markdown | 项目基本信息、背景、规模、时间 |
| `techRequirements` | 技术评分要求 | ✅ | markdown | 技术评分项、权重、标准 |
| `projectInfo` | 项目信息 | ❌ | json | 名称、编号、类型、预算、地址 |
| `partAInfo` | 甲方信息 | ❌ | json | 招标人公司、地址、联系人 |
| `agentInfo` | 代理机构信息 | ❌ | json | 代理机构联系方式、账户 |
| `keyInfo` | 投标关键节点 | ❌ | json | 公告日期、获取方式、截止时间 |
| `marginInfo` | 投标保证金 | ❌ | json | 金额、方式、截止、退还条件 |
| `qualificationReview` | 资格性审查 | ❌ | markdown | 投标人资格条件 |
| `complianceCheck` | 符合性检查 | ❌ | markdown | 文件完整性、有效性 |
| `openBid` | 开标要求 | ❌ | json | 时间地点、无效标认定 |
| `evaluationBid` | 评标要求 | ❌ | json | 委员会、评分构成、方法 |
| **`businessScoring`** | 商务评分要求 | ❌ | markdown | **商务评分因素** |
| `discardedBids` | 无效标与废标项 | ❌ | markdown | 废标风险项 |
| `signingProcess` | 合同授予与签订 | ❌ | json | 中标公示、保证金、合同 |
| `terminationCondition` | 合同解除和终止 | ❌ | json | 违约解除、争议解决 |

获取完整列表（含 required 筛选）：
```typescript
function oc(mode: 'full' | 'key'): ExtractionItem[]
// mode='key' 仅返回 required=true 的项
```

### 3.2 提取页 UI (b8 组件)

```
┌─────────────────────────────────────────┐
│  提取项选择 (下拉选择 S)                  │
│  ┌─────────────────────────────────┐    │
│  │  ◉ 项目概述 (待生成)            │    │
│  │  ◉ 技术评分要求 (已生成)        │    │
│  │  ○ 商务评分要求 (待生成)        │    │
│  │  ○ 甲方信息 (未选择)            │    │
│  │  ...                            │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │  [结果预览区] Markdown/JSON    │    │
│  └─────────────────────────────────┘    │
│          [开始提取] [全部提取]          │
└─────────────────────────────────────────┘
```

状态机: `idle | running | success | error | partial | planning`

### 3.3 目录生成流程

**系统提示 (system prompt)** 固定为：
```
你是一个专业的标书编写专家。根据提供的项目概述和技术评分要求，生成投标文件中技术标部分的目录结构。
```

**生成模式**（通过 Vb 函数调度）：

#### 模式 A: 一次性完整生成 (Vb → Yb)
```
输入: {overview, requirements, oldOutline?, suggestions?}
流程: AI → 生成完整→三级目录 outline
验证: mx() < 3 级 → throw
```

#### 模式 B: 分步生成 (Vb → Gb)
```
步骤1: KS() → 只生成一级目录
步骤2: WS() → 逐一对每个一级目录生成二三级
验证: 每步独立校验
```

#### 回退策略 (Vb)
```typescript
async function Vb(data, mode): [outline, 'full' | 'fallback'] {
  if (mode === 'full') return [await Yb(data), 'full'];
  if (mode === 'fallback') return [await Gb(data), 'fallback'];
  try {
    return [await Yb(data), 'full'];  // 先试一次性
  } catch {
    return [await Gb(data), 'fallback']; // 失败切分步
  }
}
```

#### 目录结构
```typescript
interface OutlineNode {
  id: string;        // 自动编号: "1.2.3"
  title: string;     // 章节标题
  description: string; // 章节描述
  children?: OutlineNode[]; // 子目录
}
```

目录的编号通过递归函数 `gx(node, prefix)` 自动生成：
```
1. 施工组织设计
   1.1 总体施工方案
   1.2 施工进度计划
2. 质量保证措施
   2.1 质量管理体系
   2.2 质量控制流程
3. 安全文明施工
   ...
```

#### 审核函数 ($S)
单独调用 AI 审核目录是否覆盖评分要点：
```typescript
function $S({overview, requirements, outlineJson}): 
  {passed: boolean, suggestions?: string}
```

### 3.4 正文生成

正文生成依赖目录结构（outline），每个叶节点最终生成 Markdown 内容。

**生成状态常量**：
```javascript
const Jl = {
  idle: "待生成",
  running: "生成中", 
  success: "已生成",
  error: "失败",
  partial: "部分生成",
  planning: "编排中"
};
```

**生成参数**：
- 并发数 (concurrency) — 可配置
- 最低字数 (minWords) — 通过 AI prompt 控制
- AI 图片开关 — 配置项 `use_ai_images`
- Mermaid 图表开关 — 配置项 `use_mermaid_images`

### 3.5 正文编排与配图

**正文编辑器** 支持：
- Markdown 源码编辑
- 格式化工具栏（加粗/列表/标题等）
- 配图插入（AI 生图或本地图片）
- 引用素材库中的模板段落

**生成触发**：
- 目录节点展开时自动触发
- 支持手动重新生成单节内容
- 支持整体全量生成

### 3.6 Word 导出

通过 `fileService.cjs` 调用 docx 库导出。
- 输出格式: .docx
- 按目录结构分章节
- 包含 AI 生成的全部正文内容
- 配图嵌入文档

---

## 四、辅助模块

### 4.1 标书查重
对已生成的章节内容进行文本相似度分析，避免同一份标书中出现重复表述。

### 4.2 废标项检查
```
🔴 高风险: 签字盖章、保证金、资质条件
🟡 中风险: 文件完整性、密封要求
🟢 低风险: 格式规范
```

### 4.3 错别字检查
AI 驱动的拼写/语法检查，返回修正建议。

### 4.4 逻辑谬误检查
```
检查项:
  - 矛盾: "采用A方案，但技术要求中禁止A"
  - 逻辑跳跃: 前提→结论之间缺少推理
  - 循环论证: 论据依赖论题本身
```

### 4.5 素材库/模板库/案例库
- 素材库: 可复用的段落、表格、图表
- 模板库: 预置的标书模板（多行业）
- 案例库: 历史成功案例

### 4.6 知识库
用户自定义知识库，用于补充 AI prompt 的 context。

---

## 五、配置项 (electron 侧)

通过 `window.yibiao?.config.load() / .save()` 读写：

```typescript
interface AppConfig {
  // AI 模型
  "ai_model": {
    "provider": string,
    "model": string,
    "api_key": string,
    "base_url": string
  },
  // 生图模型
  "image_model": {
    "provider": string,
    "api_key": string,
    "model": string,
    "status": "untested" | "available" | "unavailable"
  },
  // 文档解析
  "file_parser": {
    "provider": string
  },
  // 功能开关
  "use_mermaid_images": boolean,
  "use_ai_images": boolean
}
```

配置保存方法：
```javascript
window.yibiao?.config.save(newConfig)    // Promise<{success}>
window.yibiao?.config.load()              // Promise<config>
```

---

## 六、Analytics（可忽略）

`Zm("event_name", "page_name", extraData)` POST 到 `https://analytics.agnet.top/track`
- projectName: "yibiao-client"
- 含 version, platform, client_id

---

## 七、模块页面路由

应用为 SPA，无传统路由。页面切换通过 React 状态驱动：

```typescript
const [$5] = useState("documents")  // 顶层 tab
// states: "documents" | 提取 | 生成 | ...
```

各模块入口：
- 首页 → state="documents", tab="tender"
- 技术方案 → 提取页 (b8 组件) → 目录生成 → 正文生成 → 编排配图 → Word导出
- 废标检查 → tab="rejection"
- 错别字检查 → tab="analysis"
- 逻辑谬误检查 → 同上 tab
- 素材库 → 独立 section
- 设置 → config 管理页

---

## 八、关键提示词协议

### 目录生成 system prompt
```
你是一个专业的标书编写专家。根据提供的项目概述和技术评分要求，
生成投标文件中技术标部分的目录结构。

规则:
1. 章节名称要专业、准确，符合投标文件规范
2. ...
```

### 正文生成 system prompt（推断）
每个正文生成请求会带入：
- 项目概述
- 技术评分要求  
- 当前章节的目录名称和描述
- 最低字数要求

### 提取 prompt（通用前缀）
```
你是专业的招标文件分析助手。
请严格基于用户提供的招标文件原文完成提取和总结。

通用要求：
1. 保持信息全面、准确，尽量使用原文内容，不要自行编造
2. 如果原文没有提及，明确写"没有提及"或"原文未提及"
3. 只输出最终结果，不输出过程、提示语或客套话
4. 始终使用简体中文
```

---

## 九、商务标使用技术方案模块的工作机制

**核心原理**: 技术方案模块的提取项中包含 `businessScoring`（商务评分要求），该选项会提取招标文件中的商务评分因素，供用户编写商务方案。

商务标内容生成的工作流：
```
1. user 勾选 businessScoring 提取项
2. AI 从招标文件提取商务评分因素
3. user 在目录中手动插入商务标章节
4. 正文生成时 AI 同时处理技术和商务内容
5. Word 导出两份合一
```

**局限**:
- 无独立的商务标工作台界面
- 报价汇总表等需要手动编辑
- 无保证金/资质附件管理

---

## 十、可扩展点（用于独立开发）

### 如果你要做独立功能：

**IPC 扩展路径**:
```javascript
// electron/ipc/index.cjs 中注册新 channel
ipcMain.handle('my-custom-action', async (event, args) => {
  // 调用 aiService 或业务逻辑
})
```

**React 组件扩展**:
```javascript
// dist/ 是编译产物，需修改源代码重新 build
// 或通过 Electron 的 BrowserView / preload script 注入
```

**AI 服务扩展**:
```javascript
// electron/services/aiService.cjs
// 当前使用 OpenAI 协议格式
// 可复用 hx.chat() / hx.requestJson() 接口
```

---

*文档版本: v1.0 | 基于 易标投标工具箱 v2.6.1 反编译分析*
*生成日期: 2026-06-05*
