# Drafted.ai — AI生成住宅平面图与CAD/PDF下载

> 合并自 `epc/drafted-ai-house-plans` 技能。免费AI住宅平面图生成器。

## 一句话定位
免费AI住宅平面图生成器：输入卧室数、浴室数、面积范围、风格偏好（8种Character × 7种Style）和特色需求（泳池/家庭影院/健身房等），AI直接生成外立面渲染图 + 平面户型图，支持一键免费下载PDF和CAD文件。

## 核心数据
- **平台**: https://www.drafted.ai
- **已生成方案**: 88,807+ 个（截至2026-05-08）
- **技术栈**: Next.js + App Router（React SSR）, Clerk（认证）, PostHog（分析）
- **定价**: 基础功能免费（浏览、下载），高级功能需注册

## 核心功能

### 1. 探索/浏览（无需注册）
筛选栏：Bedrooms（1-5+）、Bathrooms（1-4+）、Square Footage（滑块）
Character（8种氛围风格）：Natural、Rustic、Industrial、Classic、Earthy、Dark、Bright、Bold
Feature（特色设施）：Pool、Rec Room、Home Office、Bar、Theater、Gym、Custom Shape

### 2. 创建生成（Create — 需注册）
三步流程：Concepts（构思→房间列表）→ Finalize（定稿→用地面积/轮廓约束）→ Materialize（导出PDF/CAD）

## 对EPC建筑行业的应用价值

| 场景 | 用途 | 价值 |
|------|------|------|
| 客户沟通 | 快速生成户型方案给客户参考 | 比手绘/找参考快10倍 |
| 方案灵感 | 输入需求看方案找灵感 | 拓展设计思路 |
| 报建参考 | CAD导出作为项目前期概念参考 | 节省概念设计时间 |

### 与现有工具链的配合
| 工具 | 关系 | 配合方式 |
|------|------|---------|
| floorplan-diagnostics（户型诊断） | 互补 → Drafted生成方案 → 户型诊断分析 | 先出图再诊断 |
| baoyu-infographic | 下游 → 截图打包成信息图给客户 | 方案可视化包装 |
| PDF-tool | 下游 → 下载的PDF可后处理（水印/合并/编辑） | PDF后期加工 |

## 使用速查

### 浏览探索（零注册）
1. 打开 https://www.drafted.ai
2. 左侧边栏选：卧室数、浴室数、面积、Character风格、特色设施
3. 滚动浏览卡片
4. 点击方案 → 详情 → Free Download PDF/CAD

### 风格速查表
| 中文 | Character |
|------|-----------|
| 自然风 | Natural |
| 乡村风 | Rustic |
| 工业风 | Industrial |
| 经典风 | Classic |
| 大地色 | Earthy |
| 暗黑风 | Dark |
| 明亮风 | Bright |
| 大胆风 | Bold |

### 面积快速换算
1㎡ ≈ 10.76 sqft
100㎡ → 1,076 sqft, 150㎡ → 1,614 sqft, 200㎡ → 2,152 sqft

## 注意事项
1. 美式尺寸：平台使用平方英尺（sqft）
2. 美式风格：偏美式独栋住宅，适合自建房/别墅/民宿
3. AI质量：外立渲染效果好，平面图需人工审校
4. 无中国规范（日照间距/防火分区等）
5. 需科学上网
