# 易标投标工具箱 - 技术方案模块架构文档

> 基于 OpenBidKit_Yibiao v2.12.2 源码分析（后续升级中）
> 对比此前 v2.6.1 反编译分析版，v2.12 代码结构、类型系统、工作流引擎均有重大升级

---

## 一、架构全景

### 进程模型（不变）
```
Electron Main Process
  └── ipc/index.cjs (IPC handlers)
      ├── aiService ── AI API 调用
      ├── fileService ── 文件读写
      ├── pdfParseService ── 文档解析
      └── webSocketService ── 实时推送

Electron Renderer (React SPA)
  └── src/
      ├── app/           ← 新增：应用框架层
      ├── features/      ← 每个功能模块独立目录
      ├── shared/        ← 跨模块共享（AI / types / UI / prompts）
      ├── components/    ← 全局组件
      ├── App.tsx
      └── main.tsx
```

### 技术栈
- 渲染层: React 18 + Radix UI + Tailwind
- 图表: Mermaid
- 文档解析: PDF.js, DocX
- AI 层: Electron IPC → Node.js → OpenAI 协议 API
- 存储: better-sqlite3 (workspace database)
- 状态: React useState + IPC 序列化持久化

### 相比 v2.6.1 的关键架构变化

| 维度 | v2.6.1 | v2.12.2 |
|------|--------|---------|
| 目录结构 | 扁平组件 | feature-based (components/hooks/services/pages) |
| 类型系统 | 内联类型 | shared/types/ 拆分为 ai/outline/ipc/config/exportFormat 等 |
| 状态持久化 | 无缓存 | technicalPlanStorage.ts (IPC 桥接) |
| 目录生成模式 | 一次性+分步 | aligned + 审核循环 (两次生成) |
| 工作流种类 | technical-plan | technical-plan + existing-plan-expansion |
| 内容生成 | 单任务 | 多阶段背景任务 (planning→generating→auditing→illustrating) |
| 条文一致性 | 无 | consistency audit + agent repair |
| 原文覆盖审查 | 无 | original plan coverage audit |
| Agent 集成 | 无 | OpenCode binary 用于 agent 模式修复 |
| 导出模板 | 固定 | 可配置模板 (ExportFormatConfig) |
| AI 客户端 | hx.chat/requestJson | aiClient.chat/requestJson (IPC 桥接) |

---

## 二、AI 服务层

### 接口定义 (shared/ai/aiClient.ts)

```typescript
export const aiClient = {
  chat(request: ChatCompletionRequest): Promise<string>,
  requestJson<TResult>(request: JsonCompletionRequest): Promise<TResult>,
};
```

通过 `window.yibiao.ai.chat()` / `window.yibiao.ai.requestJson()` IPC 桥接到 Electron 主进程。

### 请求类型 (shared/types/ai.ts)

```typescript
interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatRequestOptions {
  temperature?: number;
  response_format?: { type: 'json_object' };
  timeout_ms?: number;
  timeout_message?: string;
  logTitle?: string;
  log_title?: string;
}

interface ChatCompletionRequest extends ChatRequestOptions {
  messages: ChatMessage[];
}

interface JsonCompletionRequest<TInput = unknown> extends ChatRequestOptions {
  messages: ChatMessage[];
  schemaName?: string;
  input?: TInput;
  max_retries?: number;
  progressLabel?: string;
  failureMessage?: string;
}
```

### 关于知识库引用

AI 请求中可携带 `knowledge_item_ids`，系统会自动将对应知识库条目作为 system message 注入。

---

## 三、技术方案模块 (technical-plan)

### 3.1 目录结构 (v2.12)

```
features/technical-plan/
├── types.ts              ← 完整类型定义
├── components/
│   └── BidSectionSelectorDialog.tsx  ← 招标段落选择对话框
├── hooks/
│   └── useTechnicalPlanWorkflow.ts   ← 工作流状态 Hook（含 hydration）
├── services/
│   ├── bidAnalysisWorkflow.ts        ← 招标分析提取项定义
│   ├── outlineWorkflow.ts            ← 目录生成流程（核心升级）
│   └── technicalPlanStorage.ts       ← 状态持久化（IPC 桥接）
└── pages/
    ├── TechnicalPlanHome.tsx         ← 入口
    ├── DocumentAnalysisPage.tsx      ← 文档分析
    ├── BidAnalysisPage.tsx           ← 招标分析页
    ├── OutlineEditPage.tsx           ← 目录编辑
    ├── GlobalFactsPage.tsx           ← 全局事实
    └── ContentEditPage.tsx           ← 正文编辑
```

**新增页面**: v2.6.1 仅有提取页+目录生成页+正文编辑页，v2.12 拆为 6 页。

### 3.2 工作流状态 (TechnicalPlanState)

```typescript
interface TechnicalPlanState {
  workflowKind: TechnicalPlanWorkflowKind;  // 'technical-plan' | 'existing-plan-expansion'
  step: TechnicalPlanStep;
  
  // 文档
  tenderFile: File | null;
  originalPlanFile: File | null;  // 仅在 existing-plan-expansion 模式使用
  projectOverview: string;
  techRequirements: string;
  
  // 招标分析
  bidAnalysisMode: BidAnalysisMode;  // 'key' | 'full' | 'custom'
  bidAnalysisSelectedTaskIds: string[];
  bidAnalysisTasks: Record<string, BidAnalysisTaskState>;
  bidAnalysisProgress: number;
  
  // 招标段落提取
  bidSectionMode: BidSectionMode;  // 'single' | 'multiple'
  bidSections: DetectedBidSection[];
  bidSectionExtractionStatus: BidSectionExtractionStatus;
  
  // 目录
  outlineMode: OutlineMode;  // 始终 'aligned'
  outlineExpansionMode: OutlineExpansionMode;  // 'original-only' | 'ai-complement'
  outlineData: OutlineData | null;
  referenceKnowledgeDocumentIds: string[];
  
  // 背景任务
  bidSectionExtractionTask?: BackgroundTaskState;
  bidAnalysisTask?: BackgroundTaskState;
  outlineGenerationTask?: BackgroundTaskState;
  globalFactsTask?: BackgroundTaskState;
  
  // 全局事实
  globalFacts: GlobalFactGroupState[];
  
  // 正文生成
  contentGenerationTask?: BackgroundTaskState;
  contentGenerationSections: Record<string, ContentGenerationSectionState>;
  contentGenerationPlans: Record<string, ContentGenerationPlanState | null>;
  contentGenerationRuntime?: ContentGenerationRuntimeState;
}
```

**关键变化**: 状态从分散变成了统一的状态树，通过 IPC 持久化 (`technicalPlanStorage`)。

### 3.3 招标分析 (Bid Analysis)

#### 提取项定义 (bidAnalysisWorkflow.ts)

与 v2.6.1 相同的 15 项，结构定义如下：

```typescript
interface BidAnalysisTaskDefinition {
  id: string;           // 唯一标识
  label: string;        // 中文显示名
  description: string;  // 功能描述
  required: boolean;    // 是否必选
  output: 'markdown' | 'json';   // 输出格式
  buildTaskPrompt: () => string; // 构建 AI 提示词
}
```

完整提取项列表（15 项，与 v2.6.1 一致）：

| ID | Label | Required | Output |
|----|-------|----------|--------|
| projectOverview | 项目概述 | ✅ | markdown |
| techRequirements | 技术评分要求 | ✅ | markdown |
| projectInfo | 项目信息 | ❌ | json |
| partAInfo | 甲方信息 | ❌ | json |
| agentInfo | 代理机构信息 | ❌ | json |
| keyInfo | 投标关键节点 | ❌ | json |
| marginInfo | 投标保证金 | ❌ | json |
| qualificationReview | 资格性审查 | ❌ | markdown |
| complianceCheck | 符合性检查 | ❌ | markdown |
| openBid | 开标要求 | ❌ | json |
| evaluationBid | 评标要求 | ❌ | json |
| businessScoring | 商务评分要求 | ❌ | markdown |
| discardedBids | 无效标与废标项 | ❌ | markdown |
| signingProcess | 合同授予与签订 | ❌ | json |
| terminationCondition | 合同解除和终止 | ❌ | json |

新增字段 (v2.12):
- `deliveryAndServiceRequirements` - 交货和服务要求（json，必选）
- `procurementList` - 采购清单（markdown，可选）
- `responseFileRequirements` - 响应文件要求（markdown，可选）

这些在 type 定义中可见，但 bidAnalysisWorkflow.ts 中的任务数组有13+项。

#### 任务状态

```typescript
interface BidAnalysisTaskState {
  id: string;
  label: string;
  status: BidAnalysisTaskStatus;  // 'idle' | 'running' | 'success' | 'error'
  content: string;
  error?: string;
}
```

### 3.4 目录生成 (核心升级)

#### 目录类型定义 (shared/types/outline.ts)

```typescript
interface OutlineItem {
  id: string;
  title: string;
  description: string;
  source_requirement_id?: string;     // ← 关联技术评分号
  source_requirement_title?: string;  // ← 关联评分项标题
  knowledge_item_ids?: string[];
  children?: OutlineItem[];
  content?: string;
}

type OutlineMode = 'aligned';
type OutlineExpansionMode = 'original-only' | 'ai-complement';

interface OutlineData {
  outline: OutlineItem[];
  project_name?: string;
  project_overview?: string;
}

interface TechnicalRequirementGroup {
  requirement_id: string;
  title: string;
  description: string;
  detail_points: string[];
}
```

**相比 v2.6.1 升级**:
1. source_requirement_id/title 字段 - 目录节点关联到具体评分项
2. TechnicalRequirementGroup 类型 - 技术评分大类显式定义
3. OutlineExpansionMode - 两种展开模式

#### 对齐生成流程 (outlineWorkflow.ts)

**新流程（两阶段生成+两轮审核）：**

```
Step 1: 提取技术评分大类
  extractRequirementGroups(options)
  → AI 分析招标文件的技术评分要求，分组为 TechnicalRequirementGroup[]
  → temperature=0.3

Step 2: 构建一级目录
  topLevelItems = buildTopLevelFromGroups(groups)
  → 每个评分大类的 title 直接作为一级目录标题
  → 自动关联 source_requirement_id

Step 3: 逐章生成二三级目录
  for each parentItem:
    generateAlignedChildren(options, parentItem, requirementGroup)
    → AI 根据评分细项需求生成子目录
    → temperature=0.7

Step 4: 编号
  renumberOutline(outline) → 1, 1.1, 1.1.1, 1.2, ...

Step 5: 首次审核
  reviewAlignedOutline(options, groups, outline)
  → AI 检查目录是否覆盖所有评分要点
  → 通过 → 返回目录
  → 不通过 → 收集修改建议

Step 6: 二次生成（审核失败时）
  extractRequirementGroups(options, suggestions)
  → 根据上次审核建议重新提取评分大类
  → 重新生成目录
  → 最终审核（passed 才返回，否则 throw 人类手动介入）
```

**对比 v2.6.1:**
- v2.6.1: 一次性生成或分步生成，无审核循环
- v2.12: 两级生成+两轮AI审核，自动修正。目录始终与评分要求"对齐"

#### 目录保存

```typescript
type SaveOutlineReason = 'sort' | 'edit' | 'delete' | 'add-root' | 'add-child' | 'replace';

interface SaveOutlineRequest {
  outlineData: OutlineData;
  reason: SaveOutlineReason;
  idMap?: Record<string, string>;      // 拖拽排序时的 ID 映射
  affectedNodeIds?: string[];          // 被影响的节点 ID
}
```

### 3.5 正文生成 (背景任务引擎)

#### 后台任务状态 (v2.12 新增)

```typescript
type BackgroundTaskType = 
  | 'bid-section-extraction' 
  | 'bid-analysis' 
  | 'outline-generation' 
  | 'global-facts-generation' 
  | 'content-generation';

type BackgroundTaskStatus = 'running' | 'pausing' | 'paused' | 'success' | 'error';
```

#### 内容生成阶段 (Phase) - 复杂状态机

```typescript
phase: 
  | 'planning'           // 编排阶段：规划每节内容结构、配图需求
  | 'restoring'          // 还原阶段（existing-plan-expansion 模式时存在）
  | 'generating'         // 正文生成阶段
  | 'outline-expanding'  // 目录展开阶段（展开模式下）
  | 'expanding'          // 展开阶段
  | 'original-auditing'  // 原文覆盖审查阶段
  | 'auditing'           // 条文一致性审查阶段
  | 'table-cleaning'     // 表格清理阶段
  | 'illustrating'       // 配图阶段（AI 图 + Mermaid）
  | 'done';              // 完成
```

#### 生成选项

```typescript
interface ContentGenerationOptions {
  useAiImages: boolean;
  maxAiImages: number;
  useMermaidImages: boolean;
  tableRequirement: ContentTableRequirement;  // 'none' | 'light' | 'moderate' | 'heavy'
  minimumWords: number;
  enableConsistencyAudit: boolean;            // ← 新增
  consistencyRepairMode: 'agent' | 'normal';   // ← 新增
  enableOriginalPlanCoverageAudit: boolean;    // ← 新增
  originalPlanCoverageRepairMode: 'agent' | 'normal';  // ← 新增
}
```

#### 内容生成计划 (Per-Node)

```typescript
interface ContentGenerationPlanData {
  writing_focus?: string;                    // 写作重点
  knowledge: { item_ids: string[] };         // 关联知识库
  facts: { titles: string[] };               // 关联全局事实
  table: { needed: boolean; purpose: string };
  mermaid: {
    needed: boolean;
    title: string;
    code: string;        // Mermaid 代码
    priority: number;
    reason: string;
  };
  image: {
    needed: boolean;
    style: 'engineering_diagram' | 'realistic_photo' | '';
    title: string;
    prompt: string;
    priority: number;
    reason: string;
  };
  original_material?: {                      // existing-plan-expansion 模式
    restored: boolean;
    optimized: boolean;
    source_ids: string[];
    source_titles: string[];
    source_hashes: string[];
    restored_chars: number;
    restored_at?: string;
    optimized_at?: string;
  };
}
```

**相比 v2.6.1:**
- v2.6.1: 直接生成，仅有并发数和配图开关
- v2.12: 先生成 plan（编排），再生成正文，包含完整的配图规划

### 3.6 工作流种类 (WorkflowKind)

#### Technical-Plan（全新生成）
```
文档分析 → 招标分析 → 目录生成 → 全局事实 → 正文生成 → 导出
```

#### Existing-Plan-Expansion（基于已有方案的扩写）
```
上传已有方案 → 文档分析 → 招标分析 → 解析还原旧方案目录结构
→ 目录扩展（original-only / ai-complement） → 正文扩写 → 导出
```

新增 `OutlineExpansionMode` 控制展开方式：
- `original-only`: 仅保留原文内容，不新增 AI 生成节
- `ai-complement`: AI 补充缺失评分项的章节

### 3.7 全局事实 (Global Facts)

```typescript
interface GlobalFactGroupState {
  id: string;
  title: string;
  content: string;
  updated_at?: string;
}
```

全局事实用于所有正文生成节点，常见内容：
- 公司简介
- 项目背景
- 通用承诺条款
- 无法分类但通用的段落

### 3.8 余项检查

#### 一致性审查 (Consistency Audit)
正文生成完成后，AI 检查所有章节之间的内容是否冲突：
- 同一个参数在不同章节说法是否一致
- 数字/日期是否矛盾
- 承诺的技术指标是否前后统一

`consistencyRepairMode`:
- `normal`: AI 直接出具修改建议
- `agent`: 通过 OpenCode Agent 自动调用文件修改接口修复

#### 原文覆盖审查 (Original Plan Coverage Audit)
对于 `existing-plan-expansion` 模式：
- 检查原方案的每条要求是否在扩写方案中得到覆盖
- `originalPlanCoverageRepairMode` 同上有 normal / agent 两种模式

---

## 四、页面路由

### 导航层级

```
App.tsx → AppShell → AppRouter
                    ├── TechnicalPlanHome       -> /technical-plan
                    ├── TechnicalPlanHome       -> /existing-plan-expansion
                    ├── BusinessBidPage         -> /business-bid
                    ├── KnowledgeBasePage       -> /document-knowledge-base
                    ├── DuplicateCheckPage      -> /duplicate-check
                    ├── RejectionCheckPage      -> /rejection-check
                    ├── ResourcesPage           -> /resources
                    ├── SettingsPage            -> /settings
                    └── ExportFormatPage        -> /export-format
```

使用 `SectionId` 类型管理路由，通过 `menuConfig.ts` 配置导航菜单。

### 技术方案子页面

```typescript
type TechnicalPlanStep = 
  | 'document-analysis'    // 文档分析（文件上传）
  | 'bid-analysis'         // 招标分析（提取项）
  | 'outline-generation'   // 目录生成
  | 'global-facts'         // 全局事实
  | 'content-edit'         // 正文编辑
  | 'expand';              // 扩写
```

---

## 五、IPC 通信协议（window.yibiao 桥）

### AI 接口

```typescript
window.yibiao.ai.chat(request: ChatCompletionRequest): Promise<string>;
window.yibiao.ai.requestJson<T>(request: JsonCompletionRequest): Promise<T>;
```

### 技术方案持久化

```typescript
window.yibiao.technicalPlan.loadState(): Promise<TechnicalPlanState | null>;
// 补存: 通过 patch 方式逐步保存，每次只传 partial state
```

### 文件操作

```typescript
window.yibiao.file.selectFile(options): Promise<FileSelectionResult>;
window.yibiao.file.getFileContent(filePath): Promise<string>;
```

### 配置

```typescript
window.yibiao.config.load(): Promise<ClientConfig>;
window.yibiao.config.save(config: ClientConfig): Promise<ConfigSaveResult>;
```

### 知识库

```typescript
window.yibiao.knowledgeBase.search(query): Promise<KnowledgeItem[]>;
window.yibiao.knowledgeBase.getIndex(): Promise<KnowledgeBaseIndex>;
```

### Agent 运行时 (v2.12 新增)

```typescript
window.yibiao.agent.run(payload: AgentRunPayload): Promise<AgentRunResult>;
window.yibiao.agent.getRuntimeStatus(): Promise<AgentRuntimeStatus>;
window.yibiao.agent.selfCheck(): Promise<AgentSelfCheckResult>;
```

---

## 六、导出系统

### 配置 (shared/types/exportFormat.ts)

```typescript
interface ExportFormatConfig {
  headingNumberingFormat: HeadingNumberingFormat;
  headingStyleConfig: HeadingStyleConfig;
  headingBorderConfig: HeadingBorderConfig;
  bodyTextStyleConfig: BodyTextStyleConfig;
  tableCellStyleConfig: TableCellStyleConfig;
  tableStyleConfig: TableStyleConfig;
  imageStyleConfig: ImageStyleConfig;
  listStyle: ListStyle;
  pageSetupConfig: PageSetupConfig;
}
```

支持自定义导出模板 (`ExportTemplateRecord`)，保存和管理多个导出样式组合。

### Word 导出事件

```typescript
interface WordExportProgressEvent {
  requestId?: string;
  phase: 'running' | 'success' | 'error' | 'canceled';
  progress: number;
  message: string;
  warnings?: string[];
}
```

---

## 七、状态持久化

### 工作流状态缓存

`technicalPlanStorage.ts` 通过 IPC 读写技术方案的工作流状态：

```typescript
technicalPlanStorage.load(): Promise<TechnicalPlanState | null>;
```

工作流 Hook `useTechnicalPlanWorkflow` 在 mount 时：
1. 尝试从 IPC 加载缓存状态
2. 加载成功则用缓存恢复工作流
3. 加载失败则使用初始状态
4. 设置 `hydrated = true` 表示初始化完成

### Workspace Database

应用使用 SQLite workspace database 管理完整会话，在 `WorkspaceDatabaseGate.tsx` 中处理数据库的：
- checking: 版本检查
- repairing: 修复
- backing-up: 备份
- upgrading: 迁移
- ready: 可用
- error: 错误

---

## 八、关键提示词协议 (v2.12)

### 目录生成提示词 (outlinePrompts.ts)

系统围绕"技术评分要求对齐"：

```
1. 提取技术评分大类: 
   - 分析招标文件的评分项
   - 按大类分组（如: 施工方案、质量保证、进度计划）
   - 输出 TechnicalRequirementGroup[]

2. 生成对齐目录:
   - 一级目录 = 技术评分大类的标题
   - 二三级目录 = 每个大类的评分细项展开
   - 关联 source_requirement_id

3. 审核提示词:
   - 检查所有评分项是否都被覆盖
   - 检查一级目录标题是否与评分大类一致
   - 输出审核结果 + 建议
```

### 目录扩展提示词 (OutlineExpansionMode)

```
original-only: 
  仅基于原文结构生成目录，不新增 AI 内容章节
  
ai-complement:
  识别原方案中未覆盖的评分要点
  补充必要的章节
  在补充的章节标注 "AI 补充完善"
```

### 条文一致性审查提示词

```
比较所有章节中对同一项的表述是否一致
检查项：
- 技术参数的数值
- 时间节点
- 承诺条款
- 单位/格式
```

---

## 九、Agent 运行时集成

v2.12 集成了 OpenCode Agent binary，用于：

1. **一致性修复 (agent mode)**: 当检测到条文冲突时，自动调用 Agent 修改文件内容
2. **原文覆盖修复 (agent mode)**: 当检测到原文要求未被覆盖时，自动补充

Agent 状态：
```typescript
interface AgentRuntimeStatus {
  phase: 'stopped' | 'starting' | 'idle' | 'running' | 'aborting' | 'unhealthy' | 'restarting' | 'closing';
  healthy: boolean;
  message: string;
  proxy: { active: number; queued: number; limit: number };
  opencode: { pid: number; base_url?: string; port?: number };
}
```

---

## 十、与 v2.6.1 的差异总结

| 模块 | v2.6.1 | v2.12.2 | 意义 |
|------|--------|---------|------|
| 代码结构 | 扁平 | feature-based 分层 | 可维护性提升，模块独立 |
| 类型系统 | 无独立定义 | shared/types/ 完整类型 | 开发友好，IDE 支持 |
| 工作流步数 | 3步 (提取→目录→正文) | 6步 + expand 模式 | 新增全局事实、审查环节 |
| 目录生成 | 一次性/分步 | 对齐+审核循环 | 质量大幅提升 |
| 正文生成 | 直接生成 | 编排→生成→审查→配图 | 完整 pipeline |
| 一致性检查 | 无 | ✅ consistency audit | 避免标书自相矛盾 |
| 原文覆盖检查 | 无 | ✅ coverage audit | 保证不遗漏要求 |
| 扩写模式 | 无 | existing-plan-expansion | 支持基于已有方案工作 |
| Agent 集成 | 无 | OpenCode binary | 自动化修复能力 |
| 导出模板 | 固定 | 可配置模板 | 个性化导出 |
| 配图 | 简单开关 | 详细规划 + prompt | 配图质量提升 |
| 编码 | .cjs + passthrough | .ts 全类型安全 | 减少运行时错误 |

---

## 十一、可扩展点

### 添加新提取项
```typescript
// 在 bidAnalysisWorkflow.ts 的 bidAnalysisTasks 数组中添加
{
  id: 'myNewItem',
  label: '新提取项',
  description: '描述...',
  required: false,
  output: 'markdown',
  buildTaskPrompt: () => `任务：...`,
}
```

### 在正文生成计划中添加新配图类型
在 `ContentGenerationPlanData` 的 image/mermaid 配置基础上，扩展 `illustration_type` 枚举。

### 添加新的生成后检查
在 `ContentGenerationOptions` 中添加新开关，在 `BackgroundTaskState.stats.content` 阶段中插入新 phase。

### 自定义导出模板
通过 `shared/types/exportFormat.ts` 的 `ExportFormatConfig` 接口扩展样式配置。

---

*文档版本: v2.0 | 基于 OpenBidKit_Yibiao v2.12.2 源码分析*
*生成日期: 2026-06-29*
*对应旧版: 易标投标工具箱-v2.6.1-技术方案模块-API开发文档.md（存档于 东盛工作/）*
