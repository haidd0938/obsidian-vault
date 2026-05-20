# EPC建筑行业信息图流水线

> 合并自 `media/epc-baoyu-infographic` 技能。基于 baoyu-infographic 能力，专门为建筑EPC行业定制的信息图生成流程。

## 前置条件
```yaml
workspace: ~/Documents/obsidian-vault/epc/infographics/
layout: binary-comparison    # 默认布局
style: corporate-memphis     # 默认风格
ratio: "16:9 landscape"      # 默认比例
```

## 推荐布局×风格组合

### 常用布局
| 场景 | 推荐布局 |
|------|---------|
| EPC vs 传统模式对比 | binary-comparison |
| 项目管理流程 | timeline-vertical |
| 资质办理全流程 | step-by-step |
| 投标资料清单 | table-matrix |
| 年度业务总结 | bento-grid |
| 成本/收益对比 | feature-comparison |

### 推荐风格
| 场景 | 推荐风格 |
|------|---------|
| 正式投标/汇报 | corporate-memphis |
| 社交媒体传播 | pop-art |
| 技术性讲解 | flat-infographics |
| 培训教材 | flat-infographics |
| 内部管理 | minimal-lineart |

## 完整流程

### Step 1: 内容分析
分析原始素材，输出：主题、学习目标、受众、信息复杂度、关键数据点

### Step 2: 结构化为维度
每个维度包含：标题、内容要点、数据/数字、图标参考

### Step 3: 推荐布局×风格
根据内容和场景推荐组合，让用户确认。

### Step 4: 用户确认后生成prompt
传给 baoyu-infographic 技能的 prompt 模板。

### Step 5: 生成HTML信息图
使用 baoyu-infographic 或降级为手写HTML（用 claude-design 技能）。

### Step 6: 交付
保存在 `~/Documents/obsidian-vault/epc/infographics/`，文件名 `infographic-{主题}.html`

## EPC vs 传统施工模式参考

### 6大对比维度
1. **管理模式**：EPC单一责任主体 vs 传统多方交叉管理
2. **设计施工**：EPC一体化协同 vs 传统先后独立+频繁变更
3. **成本控制**：EPC固定总价+限额设计 vs 传统低价中标+签证满天飞
4. **工期效率**：EPC并行推进 vs 传统串行+界面摩擦
5. **质量控制**：EPC设计保施工可行 vs 传统设计不管施工落地
6. **招标方式**：EPC一次性招标 vs 传统多次招标

### 配色方案（corporate-memphis风格）
- EPC侧主色: #2A7C6F（深蓝绿）
- 传统侧主色: #E8853D（暖橙）
- 背景: #F7F5F0（米白基底）

## EPC行业术语
限额设计、固定总价、平行发包、设计施工一体化、EPC总承包
