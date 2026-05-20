---
name: floorplan-diagnostics
description: 户型图诊断专家 — 扔户型图，出专业装修诊断报告+信息图。使用 Gemini 视觉模型分析户型结构、动线、采光、功能分区，支持双模式输出：文字报告或信息图。
version: 2.0.0
author: 贾维斯
license: MIT
metadata:
  hermes:
    tags: [floorplan, diagnostics, interior-design, epc, renovation, vision, infographic]
    related_skills: [epc-business-analysis-from-filesystem, baoyu-infographic, claude-design]
---

# 户型图诊断专家 v2.0

融合虎小象「禅院宅居断事师」信息图结构，支持双模式输出。

## 触发条件

当用户发来户型图/平面图/建筑图纸时，自动使用此技能进行诊断分析。适用于：
- 装修前方案评估
- 户型优缺点分析
- 功能分区与动线优化
- 名宿/酒店/商业空间改造

用户可指定输出模式：
- `文字报告`（默认）：详细诊断报告
- `信息图`：输出一张高级竖版信息图（适合发微信/小红书/抖音）

## Provider 策略（重要）

此技能**推荐使用 Gemini** 获得最佳视觉分析效果。

### Provider 切换

```bash
# 方式1：手动切到 Gemini
# 修改 config.yaml 的 model 段：
#   provider: custom
#   default: gemini-2.5-flash
#   base_url: https://generativelanguage.googleapis.com/v1beta/openai/
#   max_context: 1048576

# 方式2：切回日常聊天
#   provider: deepseek
#   default: deepseek-chat
#   base_url: https://api.deepseek.com/v1
#   max_context: 131072
```

### Provider 配置位置

- Gemini: `~/.hermes/config.yaml` → custom_providers → name: Gemini
- base_url: `https://generativelanguage.googleapis.com/v1beta/openai/`
- 模型: `gemini-2.5-flash`（快速分析） / `gemini-2.5-pro`（深度分析）
- 上下文: 1M tokens

### 常见故障与恢复

1. **Gemini 429（额度耗尽）**
   - 症状：`ResourceExhausted` / `prepayment credits are depleted`
   - 原因：AI Studio 免费额度用完
   - 方案A：让用户去 https://aistudio.google.com 充值（最推荐，Gemini 2.5 Flash 极便宜）
   - 方案B：降级到 NVIDIA NIM 的 `meta/llama-3.2-11b-vision`（免费但有配额限制）
     - NVIDIA base_url: `https://integrate.api.nvidia.com/v1`
     - NVIDIA API Key: 见 config.yaml custom_providers

2. **NVIDIA NIM base_url 配置错误**
   - ⚠️ 2026-04-29 发现 config.yaml 中 NVIDIA NIM 的 base_url 曾被错误写成 `api.deepseek.com`
   - 正确值：`https://integrate.api.nvidia.com/v1`
   - 修复后已在 NVIDIA NIM 的 models 列表中加入 `meta/llama-3.2-11b-vision`（带 vision: true）

3. **Gemini base_url 配置错误**
   - ⚠️ 2026-04-29 发现 Gemini 的 base_url 初始配置时被错误写成 `api.deepseek.com`
   - 正确值：`https://generativelanguage.googleapis.com/v1beta/openai/`

4. **config.yaml 手工切换后必须保持一致性**
   - 切换 Provider 时，model 段的 `provider`, `default`, `base_url`, `max_context` 四个字段必须同时改
   - 不能只改 provider 不改 base_url（这是之前两个 Provider 配错的原因）

## 图片获取方式（关键）

### 用户通过 Telegram/WebUI 发图
- 图片可能存储在微信沙盒路径：
  `/Users/mac/Library/Containers/com.tencent.xinWeChat/Data/.../temp/InputTemp/*.png`
- **必须先拷贝到 `/tmp/` 才能被 vision_analyze 读取**（微信沙盒权限限制）
- 方法：
  ```bash
  cp "/Users/mac/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_o2m9jg7ele9r22_86c3/temp/InputTemp/最新图片.png" /tmp/floorplan.png
  ```
- 找图片技巧：
  - 微信 InputTemp 下按时间排序取最新的两个
  - `ls -lt ".../InputTemp/" | head -5`
  - 两个最新的一般是用户刚发的（一个可能是缩略图，一个是大图）

### 用户通过 CLI 提供路径
- 直接告诉 vision_analyze 路径即可
- 如果是 `.dwg` 格式（CAD），需要先提用户转成图片

## 工作流程

### Step 1: 找图并拷贝
先检查图片来源是否在微信沙盒，如是则拷贝到 `/tmp/` 再分析。

### Step 2: 确认输出模式
询问用户要 `文字报告` 还是 `信息图`（信息图模式更简洁直观）。
如果用户已明确说明（如说"出张图"），直接跳过此步。

### Step 3: Provider 准备
1. 当前 Provider 确认是否支持视觉
2. 如不支持（如 DeepSeek），切换到 Gemini 或 NVIDIA
3. 切换后检查 vision_analyze 工具实际调用是否成功
4. 如 Gemini 429 则降级到 NVIDIA vision 模型

### Step 4: 视觉分析

使用 `vision_analyze` 工具，问题模板（v2.0加强版，适配信息图结构）：

```
请详细分析这个户型平面图，严格按照以下9大维度诊断。每个维度都给出✅正常/⚠️注意/❌问题，并分析因果关联（A问题→B问题→C后果）：

[入户与玄关]
- 有无独立玄关？隐私性如何？
- 入户门位置是否合理？换鞋/放包空间够吗？

[动线与布局]
- 主要动线（家务/访客/居住）是否交叉？
- 空间利用率如何？有没有明显浪费区域？

[客餐厅]
- 客餐厅一体还是独立？空间是否通透？
- 餐桌位置是否合理？电视墙/沙发墙条件如何？

[卧室]
- 每间卧室的尺寸感、朝向、采光
- 衣柜位置是否合理？

[厨房]
- 布局类型（I型/L型/U型/双一字）？操作台面够吗？
- 冰箱/烟道/燃气位置是否合理？

[卫生间]
- 是否干湿分离？数量是否够用？
- 马桶/洗手台/淋浴区布局是否合理？

[采光与通风]
- 主要采光面朝向？窗户分布？
- 有无暗卫/暗厨？通风条件如何？

[收纳空间]
- 有没有独立的储物间/家政间？
- 全屋收纳潜力评估

[风水形势（非迷信版）]
- 门对门/门对窗/穿堂煞等形法问题
- 财位/卫生间位置/炉灶对门等实用考量
- 解释：不是迷信，是长期居住心理舒适度

额外要求：
- 总结出3-5条最核心的问题，标注优先级（🔴必须改/🟡建议改/🟢可改可不改）
- 对每个核心问题，建立因果链（因为A所以B，导致C）
- 给出改造优先级排序列表
- 每一条建议附带一句精炼的"一句诀"点评（类似"煞位在卫生间，不开运转运难"这类）
```

### Step 5: 输出诊断

#### 模式 A：文字报告（默认）

按原v1.0的详细报告结构输出（见下方模板）。

#### 模式 B：信息图

如果用户选择信息图模式，执行以下步骤：

### Step 5b: 信息图生成流程

#### 5b.1 整理结构化内容

将视觉分析结果整理成以下10个模块的结构化数据，用于信息图渲染：

**模块1 - 标题区**
- 标题："禅院宅居断事 · 户型诊断"
- 副标题：户型名称/面积/朝向

**模块2 - 户型概览（骨架）**
- 户型类型、面积、朝向、功能分区列表
- 一句话总评

**模块3-8 - 6大核心问题模块**
从9大维度中选出最突出的6个问题/亮点，每个模块包含：
- 问题标题
- ✅/⚠️/❌ 状态标
- 简短诊断（15字内）
- 因果链（因为A→导致B→后果C）
- 一句诀点评

**模块9 - 优先级排序**
- 🔴 必改项（2-3条）
- 🟡 建议改（2-3条）
- 🟢 可改可不改（1-2条）

**模块10 - 一句诀总结**
- 一针见血的金句收尾

#### 5b.2 渲染方式选择

**⚠️ 环境限制**：本环境（Intel MacBook，无GPU）不支持 `image_generate` / MJ / DALL·E。渲染方式取决于可用工具：

**方式A（推荐）：claude-design → 自包含HTML信息图**
当 `image_generate` 不可用时，使用此方式：
1. 将Step 5b.1的结构化内容组织为静态信息图HTML
2. 使用 `claude-design` 技能生成一个自包含的HTML文件（九宫格布局，dense-modules风格）
3. 视觉参数：
   - 画布：1080×1920px（9:16竖版）
   - 配色：Morandi 莫兰迪色系（#F5F0E6 米白背景, #7BA3A8 青绿标题, #D4956A 陶土高亮, #4A4540 深棕文字）
   - 粗糙纸纹质感，手绘封边元素
   - 字体：Noto Serif SC（标题）+ Noto Sans SC（正文）
4. 用模版文件 `templates/infographic.html` 作为参考结构

**方式B：baoyu-infographic → image_generate**
仅在 `image_generate` 可用时使用（本环境不支持）：
1. 将结构化内容传给 `baoyu-infographic` 技能
2. layout: `dense-modules`, style: `morandi-journal`, aspect: portrait
3. 语言: zh

#### 5b.3 验证与交付

1. 生成HTML后保存到 `~/Desktop/`，命名格式：`{项目名}-户型诊断信息图.html`
2. 用 `browser_navigate` 打开验证（file:// URL）
3. 用 `browser_vision` 截取完整页面截图确认布局正确
4. 最终将文件路径和截图一并展示给用户

---

## 文字报告模板（模式A）

```
═══════════════════════════════════════════
 🏠 户型诊断报告
═══════════════════════════════════════════

📐 一、骨架拆解 — 户型结构总览
├─ 户型类型：三室两厅 / 开间 / Loft / 异形...
├─ 建筑面积：约 XX㎡
├─ 功能分区：客餐厅 | 厨房 | 卧室X3 | 卫生间X2 | 阳台
├─ 结构特点：方正/狭长/异形/动静分区...
└─ 朝向分析：主采光面朝XX，通风条件...

🔍 二、微观体检 — 9大维度逐区诊断
├─ 🚪 入户与玄关：
│  ├─ ✅ 有独立玄关，隐私性好
│  └─ ⚠️ 玄关宽度不足1.2m，鞋柜难放
├─ 🌀 动线与布局：
│  ├─ ✅ 动静分区合理
│  └─ ⚠️ 餐桌位置遮挡通往卧室的动线
├─ 🛋️ 客餐厅：
│  ├─ ✅ 客餐厅一体，空间通透
│  └─ ⚠️ 缺乏独立电视墙
├─ 🛏️ 卧室：
│  └─ [诊断内容]
├─ 🍳 厨房：
│  └─ [诊断内容]
├─ 🚽 卫生间：
│  └─ [诊断内容]
├─ ☀️ 采光与通风：
│  └─ [诊断内容]
├─ 📦 收纳空间：
│  └─ [诊断内容]
└─ 🧭 风水形势：
   └─ [实用形法分析]

🔄 三、动线分析
├─ 家务动线：[描述]
├─ 访客动线：[描述]
├─ 居住动线：[描述]
└─ ⭐ 优化建议：[关键动线改造方案]

🔗 四、问题因果链
├─ 🔴 问题1：[核心问题]
│  └─ 因果：因为A → 导致B → 造成C
├─ 🟡 问题2：[核心问题]
│  └─ 因果：因为A → 导致B → 造成C
└─ 🟢 问题3：[可优化项]
   └─ 因果：[因果分析]

💡 五、改造建议（按优先级排序）
1. 🔴 必改：
   - [建议] ─ 一句诀点评
2. 🟡 建议改：
   - [建议] ─ 一句诀点评
3. 🟢 可改可不改：
   - [建议]

🎯 六、针对性建议
【针对成县名宿 / 常记呱呱 / 装修项目】
├─ 民宿运营角度：[结合商业用途的分析]
├─ 预算建议：[粗估改造费用区间]
└─ 施工注意：[EPC视角的施工要点]

═══════════════════════════════════════════
```
---

## 信息图渲染提示词模板（模式B用）

当需要生成信息图时，将视觉分析结果按下面格式组织，传给 baoyu-infographic 技能：

### 格式要求

```
标题：禅院宅居断事 · 户型诊断
副标题：[户型名称] | [面积] | [朝向]

【模块1：户型骨架】
类型：[类型]
面积：[约XX㎡]
朝向：[主采光面]
一句话总评：[一句话总结]

【模块2-7：六大门诊断】
每个模块格式：
🔴/🟡/🟢 维度名：[诊断标题]
核心问题：[一句话]
因果链：[因为A→导致B→造成C]
一句诀：「金句」

【模块8：优先级排序】
🔴 必改：
1. [问题] — [建议]
2. [问题] — [建议]
🟡 建议改：
1. [问题] — [建议]
2. [问题] — [建议]
🟢 可优化：
1. [问题] — [建议]

【模块9：一句诀】
[总结性金句]
```

### baoyu-infographic 参数

- layout: `dense-modules`
- style: `morandi-journal`（默认，奶油低饱和温暖风） 或 `technical-schematic`（工程蓝图风）
- aspect: portrait (9:16)
- language: zh

---

## 针对不同场景的诊断重点

### 成县名宿（民宿改造）
- 重点：客房数量最大化、私密性、公共区域利用率
- 关注：每个房间独立卫浴的可能性、景观面利用
- 运营：动线能否支持清洁/布草/早餐服务

### 常记呱呱（餐饮空间）
- 重点：厨房与用餐区比例、客流动线、消防要求
- 关注：排烟/排水/燃气管道条件、明档/暗厨选择
- 运营：翻台率、高峰期人流承载

### 住宅自住
- 重点：居住舒适度、收纳空间、家庭成长性
- 关注：儿童安全、老人友好、未来改造弹性

## 参考资源

本技能包含以下参考文件和模板（含从合并技能吸收的内容）：

- `references/huxiao-xiang-temple-technique.md` — 虎小象「禅院宅居断事师」提示词结构解析
- `references/drafted-ai-house-plans-guide.md` — Drafted.ai AI户型生成器使用指南（absorbed from `epc/drafted-ai-house-plans`）
- `references/epc-baoyu-infographic-flow.md` — EPC建筑行业信息图流水线（absorbed from `media/epc-baoyu-infographic`）
- `templates/infographic.html` — 户型诊断信息图HTML模板（纯文字模块，无户型图嵌入）
- `templates/floorplan-diagnosis-with-images.html` — 户型诊断信息图HTML模板（带实际户型图嵌入，A4竖版可打印）—— 这是首选用模板，用户要看到实际图纸

## 注意事项

1. **版权提醒**：户型图可能有开发商版权，分析结果仅供内部参考
2. **精度说明**：视觉分析基于图片像素，精确尺寸需参考原始CAD图纸
3. **规范确认**：实际施工前务必核实当地建筑规范（尤其是承重墙改造）
4. **多图分析**：如有多个方案/不同楼层户型图，可做横向对比分析
5. **与EPC项目结合**：可联动已有EPC项目档案，获取施工工艺和材料数据
6. **Provider 安全恢复**：用完 Gemini 后必须切回 DeepSeek，否则用户日常对话也走 Gemini
7. **信息图模式**：本环境 `image_generate` 不可用（Intel Mac无GPU，无MJ/DALL·E API）。只能用 `claude-design` → 自包含HTML方式输出信息图。详见 Step 5b.2 方式A
8. **信息图不适合极细节内容**：文字报告能容纳更多细节，信息图侧重核心要点可视化

## 限制

- Gemini API 免费额度有限（429 时需通知用户充值或降级 NVIDIA）
- ⚠️ NVIDIA `meta/llama-3.2-11b-vision` 的户型图分析效果**未经验证**
- 微信沙盒路径的图片必须手动拷贝到 `/tmp/` 才能用 vision_analyze
- 对非标准比例/旋转/模糊的户型图分析质量会下降
- 不能替代现场勘测和结构工程师的专业判断
- **信息图模式下 image_generate 工具可能无法在本地 MacBook Intel CPU 上运行**（需要GPU或API）
