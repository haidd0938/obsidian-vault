# GenCAD — 照片→参数化CAD生成

> 评估日期：2026-05-18
> 项目地址：https://gencad.github.io | https://github.com/ferdous-alam/GenCAD
> ArXiv: https://arxiv.org/abs/2409.16294
> 类型：MIT CSAIL 学术研究项目（CVPR 2025）

## 一句话

MIT这波是**赛道级的正确方向**——之前的"图片转3D"全是mesh/点云玩具，工业上用不了。GenCAD输出的**参数化CAD命令序列**保留建模历史，可以在SolidWorks/NX里继续编辑，这是本质区别。

## 它是做什么的？

GenCAD = 单张照片 → 可编辑的3D CAD模型（带建模历史）

### 核心创新

- **CADSequence**: 把CAD建模过程表示为token序列（每一步拉伸/切割/倒角 = 一个token）
- **对比学习 + 潜扩散模型**: 从照片中提取几何特征，映射到CAD命令空间
- 输出是**参数化的CAD命令序列** → 可以直接喂进CAD软件继续改

### 当前能力

- ✅ 能生成：机械零件、椅子、桌子、简单物体
- ❌ 不能：建筑结构、复杂曲面、多部件装配体
- ❌ 不能：从照片到施工图/工程量清单

## 在你的环境能装吗？❌

| 关卡 | 状态 | 说明 |
|------|------|------|
| Intel Mac（无GPU） | ❌ | Docker能起但CPU推理数小时 |
| 需NVIDIA CUDA | ❌ | Intel Mac没有 |
| 需Linux/Windows | ❌ | macOS非官方支持 |
| 10个月没更新 | ⚠️ | 最后提交2025-07-14，7 commits后停更 |
| 无LICENSE文件 | ⚠️ | 项目页写"100% open-source"但没有LICENSE文件 |
| 依赖pythonocc-core | ❌ | conda包，Mac上容易翻车 |
| HuggingFace模型 | ⚠️ | 可能需要科学上网下载 |

**结论：现在装不了，也没必要装。**

## 为什么值得关注？

之前所有的AI 3D生成（Meshy、Tripo、Zero-1-to-3、DreamFusion）全部输出mesh或点云——对工厂产线和设计师来说**没法编辑**，就是个"好看但没用"的玩意儿。

GenCAD是**第一次**输出参数化CAD命令序列，保留了"建模历史"（construction history）。这意味着：
- 设计师可以打开生成的STEP文件继续改
- 可以调整尺寸、重新约束
- 可以集成到现有CAD工作流

**这才是工业级AI建模的正确方向。**

## EPC 适用性评估

**当前：★☆☆☆☆（几乎为零）**

只能生成汽车零件、椅子级别的简单几何体。离建筑结构、框架、梁柱系统差太远。不能出施工图、工程量清单、BOM表。

**长期潜力：★★★☆☆**

如果这条路跑通：
- 现场拍照片 → 自动生成建筑物的粗略参数化模型
- 施工过程中拍照 → 自动建"as-built"模型（竣工模型）
- 配合大模型 → 从照片到结构分析模型

**现在能借鉴的（0成本）：**

框架底层用了对比学习（x-clip）+ 潜扩散 + transformer，可以改进我们的 `video-script-to-production` skill 中的视觉一致性校验逻辑。

## 技术栈（供参考）

```
环境管理器: conda + environment.yml
Python: 3.10
核心依赖: torch, torchvision, transformers, opencv-python
CAD内核: pythonocc-core 7.9.0（OpenCASCADE的Python接口）
3D工具: trimesh, plyfile
视觉: x-clip, einops, scikit-learn
序列化: h5py
```

## 社区数据

- GitHub Stars: 2.3k
- Forks: 260
- Issues: 26
- PRs: 3
- 最新提交: 2025-07-14（10个月前）
- 总计提交数: 7

## 推荐行动

1. **保持关注** — 这条技术路线（参数化CAD序列生成）在未来6-12个月内大概率会出更成熟的产品
2. **不要安装** — Intel Mac + 无CUDA + 10个月没更新 = 浪费时间
3. **长期留意** — 如果配了GPU服务器或者换M芯片Mac，可以用来跑开源权重试试
4. **Upwork卖点储备** — 了解这个方向可以作为"AI+CAD/建筑行业"的知识储备，接海外单时展示行业视野
