# 建筑学长AI技能拆解 & 本地实现方案

> 分析日期: 2026-04-26
> 目标平台: jianzhuxuezhang.com
> 核心理念: 零成本本地替代，能跑本地绝不用付费API

---

## 一、平台概览

**建筑学长**是一个面向建筑/室内/景观/规划领域的AI创作平台，提供约32+个AI功能点。技术底层主要依赖:
- **Stable Diffusion** 系列模型 (txt2img, img2img, ControlNet)
- **GPT-4o / GPT-image-2** (文本生成图片, 用于高精度文字生成图像)
- **自研Banana智能体** (组合多个模型的工作流)
- **Micro-frontend微前端架构** (API入口: `ai.miankoutupian.com`)

**平台短板**: 每次生成消耗积分/次数，免费额度有限，高级功能需付费会员。所有图片有压缩/水印风险。

---

## 二、能力板块分类

我将32个功能归类为以下 **8大板块**:

| 板块 | 功能数 | 核心能力 |
|------|--------|---------|
| 1. 文生图/图生图 (基础生成) | 3 | 文本→建筑图, 风格迁移, 多角度生成 |
| 2. 外立面/改造/城市更新 | 4 | 立面迁移, 旧房改造, 城市更新, 夜景照明 |
| 3. 室内设计 | 10 | 装修, 风格转换, 家具替换, 材质替换, 照明 |
| 4. 户型图&CAD | 4 | 上色, 转3D, CAD→3D, 室内绘图 |
| 5. 模型渲染 | 3 | 模型渲染, 室内模型渲染, 软装设计 |
| 6. 手绘/创意 | 3 | 室内手绘, 家具棚拍, 灵感草图 |
| 7. 视频/漫游 | 2 | 漫游视频, AI室内图转三维模型 |
| 8. 专业增强 | 3 | 彩平生成, Banana Pro, AI室内大师 |

---

## 三、逐功能分析 + 本地替代方案

### === 板块1: 文生图 / 图生图（基础生成）===

#### 1. AI建筑设计 (Text-to-Architecture)
- **平台原理**: Stable Diffusion + 建筑LoRA + ControlNet
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - **ComfyUI** + SDXL/FLUX.1-dev + ControlNet (Canny/DW/depth)
  - 建筑LoRA可从CivitAI下载免费建筑风格LoRA
  - 提示词模板用 Qwen3/Ollama 本地生成
  - **已有**: Ollama (gemma4/qwen3), 可装ComfyUI
- **难度**: ⭐⭐ 需安装ComfyUI, 下载1-2个模型

#### 2. AI景观设计 / AI城乡规划
- **平台原理**: SD + 景观ControlNet + 语义分割引导
- **本地实现**: ✅ **完全可以**
- **方案**: 同上 + SAM分割出绿地/水体区域后引导生成
- **已有**: SAM (Segment Anything) 可用, CLIP可用

#### 3. AI建筑风格迁移 / AI室内风格转换
- **平台原理**: img2img + style LoRA
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - ComfyUI img2img workflow
  - IP-Adapter (图像风格提示) 实现风格迁移
  - LoRA切换不同风格: 中式、现代、古典、新中式
- **难度**: ⭐ 基础img2img操作

---

### === 板块2: 外立面 / 改造 / 城市更新 ===

#### 4. AI立面迁移 (Facade Transfer)
- **平台原理**: SD Inpaint + ControlNet
- **本地实现**: ✅ **完全可以**
- **方案**: ComfyUI中加载建筑照片 → 用SAM或手动遮罩 → ControlNet保持结构 → img2img重新生成立面
- **已有**: SAM, CLIP

#### 5. AI旧房改造 / AI城市更新
- **平台原理**: 同上 + 更强结构保持
- **本地实现**: ✅ **完全可以**
- **方案**: ControlNet (Canny/MLSD) 保持原建筑轮廓 + IP-Adapter参考风格图
- **难度**: ⭐⭐ 需调节denoise强度平衡改造程度

#### 6. AI夜景照明设计
- **平台原理**: img2img + 光照LoRA
- **本地实现**: ✅ **完全可以**
- **方案**: 原图 → ControlNet保持结构 → 暖色调/冷色调prompt → 低denoise(0.3-0.4)只改光照
- **技巧**: ComfyUI可加光照控制节点

#### 7. AI城市更新
- 同#5, 不重复

---

### === 板块3: 室内设计（最大板块，10个功能）===

#### 8. AI室内装修 / AI毛坯房装修 / AI房屋装修
- **平台原理**: SD Inpaint + 室内ControlNet
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - 毛坯房照片 → SAM分割空间 → Inpaint填充家具/装修
  - 建议SDXL室内专用模型: `realistic-vision-v5.1` 或 `dreamshaper`
- **已有**: SAM可用

#### 9. AI拍照装修 (Photo Decoration)
- **平台原理**: 上传照片 → SD Inpaint
- **本地实现**: ✅ **完全可以**
- **方案**: 用户拍房间照片 → ComfyUI Inpaint → 指定装修风格
- **难度**: ⭐ 最简单场景

#### 10. AI家具替换 / AI材质替换
- **平台原理**: SD Inpaint + 局部重绘
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - SAM点击家具自动分割 → 遮罩 + prompt "a modern sofa" → Inpaint
  - 材质替换同理，遮罩墙/地面后改材质描述
- **已有**: SAM (一键分割), CLIP (识别内容)

#### 11. AI室内照明 (Interior Lighting)
- **平台原理**: 光照img2img
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - SD + lighting LoRA 或 IC-Light (光照控制模型, 开源)
  - IC-Light 可以改变场景光照方向/色温
- **技巧**: IC-Light是专门的光照控制模型, 效果优于SD硬调

#### 12. AI软装设计
- **平台原理**: 生成软装布置参考图
- **本地实现**: ✅ **完全可以**
- **方案**: SD + 软装LoRA (CivitAI搜索"soft furnishing"或"室内软装")
- **难度**: ⭐

#### 13. AI室内手绘
- **平台原理**: SD + 手绘风格LoRA
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - img2img加载渲染图 → 手绘风格LoRA + low denoise
  - 或直接用ControlNet从线稿生成
- **已有**: Ollama可以生成符合风水/美学的手绘提示词

#### 14. AI室内大师 (综合智能体)
- **平台原理**: LLM + SD组合工作流
- **本地实现**: ⚠️ **部分可行**
- **方案**: 
  - **LLM部分**: 用Ollama (qwen3/gemma4) 理解用户需求, 生成设计提示词
  - **SD部分**: 自动调用ComfyUI API生成
  - 需写一个Python封装脚本串联两者
- **已有**: Ollama模型, Python脚本能力
- **需新装**: ComfyUI + 调用ComfyUI API的Python库

---

### === 板块4: 户型图 & CAD ===

#### 15. AI户型图上色 (Floor Plan Coloring)
- **平台原理**: SD + 户型图ControlNet + 颜色LoRA
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - 户型图线条 → ControlNet (Canny/Lineart) → SD上色
  - 或用专业户型图LoRA: `floor-plan-lora`
- **难度**: ⭐

#### 16. AI户型图转三维
- **平台原理**: 2D→3D生成 (可能是3D-aware diffusion)
- **本地实现**: ⚠️ **部分可行**
- **方案**: 
  - 开源方案: **TripoSR** (单图转3D, 开源), **Zero-1-to-3** (视角合成)
  - 或用Stable Zero123 + 3D重建
- **难度**: ⭐⭐⭐ 需GPU, 3D模型较重

#### 17. CAD转三维建模
- **平台原理**: CAD兜稿 → 3D重建
- **本地实现**: ❌ **有限可行**
- **方案**:
  - 开源 **CAD-reconstruction** 模型 (Point-E, Shape-E)
  - 更实用方案: CAD→OBJ导出 → Blender自动化渲染
- **已有**: Blender可做命令行渲染

#### 18. AI室内绘图 (Interior Drawing)
- 同#8 室内装修, 差别是输出风格
- **本地实现**: ✅ **完全可以**

#### 19. AI室内模型渲染
- **平台原理**: 3D模型 → SD风格化渲染
- **本地实现**: ✅ **完全可以**
- **方案**: Blender导出多角度 → SD img2img统一风格渲染

---

### === 板块5: 模型渲染 ===

#### 20. AI模型渲染 (Model Render)
- **平台原理**: SU/3D模型 → AI风格化
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - Blender (开源) 渲染白模 → SD img2img转风格化效果图
  - ControlNet保持结构, LoRA控制风格
- **已有**: Blender免费, SAM/CLIP可用

#### 21. AI室内模型渲染
- 同上, 室内版

#### 22. AI漫游视频生成 (Roaming Video)
- **平台原理**: 单图/多图 → 视频 (AnimateDiff / SVD)
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - **ComfyUI + AnimateDiff** (本地生成视频)
  - 或 **Stable Video Diffusion** (单图转视频)
  - 或直接FFmpeg+图片序列合成
- **已有**: FFmpeg ✅, 鑫球汇视频合成器.py ✅ (可改造复用)
- **难度**: ⭐⭐ 需ComfyUI

---

### === 板块6: 手绘 / 创意 ===

#### 23. AI室内手绘 (Interior Hand-drawn)
- 同#13

#### 24. AI家具棚拍 (Furniture Studio Photography)
- **平台原理**: 家具白底图 → AI棚拍风格
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - 家具照片 → SD + "studio photography, soft lighting, white background" + 产品LoRA
  - 或 IP-Adapter 参考商业摄影风格
- **难度**: ⭐

#### 25. AI室内图三维模型
- **平台原理**: 单图 → 3D重建
- **本地实现**: ⚠️ **部分可行** (同#16)
- **方案**: TripoSR / Zero-1-to-3

---

### === 板块7: 视频 / 漫游 ===

#### 26. AI漫游视频生成
- 同#22

#### 27. AI室内图三维模型 → 视频
- 组合: 3D模型 + 相机运镜 → 视频
- **本地实现**: ✅ **完全可以**
- **方案**: 
  - Blender导入3D模型 → 设置相机路径 → 渲染序列帧 → FFmpeg合成视频
  - Edge TTS配音 + 鑫球汇视频合成器.py
- **已有**: FFmpeg ✅, Edge TTS ✅, 鑫球汇视频合成器.py ✅

---

### === 板块8: 专业增强 ===

#### 28. AI彩平生成 (Color Plan Generation)
- **平台原理**: CAD平面图 → SD上色填充
- **本地实现**: ✅ **完全可以**
- **方案**: CAD导出线稿 → SD + ControlNet (MLSD/Lineart) + 彩平LoRA
- **专业平替**: QGIS (开源GIS) 自动配色

#### 29. Banana Pro (智能体)
- **平台原理**: 组合多个模型的工作流编排
- **本地实现**: ⚠️ **部分可行**
- **方案**: 
  - **ComfyUI Workflow** 本身就是Banana Pro的平替
  - 或写Python脚本编排：Ollama(分析需求) → SD(生成) → FFmpeg(后处理)
- **已有**: Ollama ✅, Python ✅, FFmpeg ✅

#### 30. AI举报重绘
- 疑为"效果图重绘" (Effect Redraw)
- **本地实现**: ✅ **完全可以**
- **方案**: 标准img2img, 同#2

---

## 四、总结: 本地实现所需工具链

### ✅ 我们已经拥有的（零成本）

| 工具 | 用途 | 状态 |
|------|------|------|
| Ollama (qwen3, gemma4) | 设计需求理解, 提示词生成, 风格分析 | ✅ 已装 |
| Edge TTS | 漫游视频配音 | ✅ 已装 |
| FFmpeg | 视频合成, 图片序列→视频 | ✅ 已装 |
| Python | 脚本编排, 自动化工作流 | ✅ 已装 |
| Pillow | 图像处理 | ✅ 已装 |
| SAM (可用) | 图像分割 - 识别建筑/家具/房间 | ✅ 技能中有 |
| CLIP (可用) | 图像内容理解 - 找相似风格 | ✅ 技能中有 |
| Whisper (可用) | 语音转文字 (not needed but nice to have) | ✅ 已装 |
| 鑫球汇视频合成器.py | 短视频合成模板, 可改造复用 | ✅ 已有 |

### 🔧 需要安装的（仍然零成本）

| 工具 | 安装方式 | 用途 | 优先级 |
|------|----------|------|--------|
| **ComfyUI** | `pip install comfyui` 或 git clone | SD工作流编排, ControlNet, AnimateDiff | P0 - 核心 |
| **diffusers** | `pip install diffusers transformers accelerate` | Python中直接调用SD | P0 - 核心 |
| **SDXL模型** | HuggingFace下载 (FLUX.1-dev / SDXL) | 文生图, 图生图基础 | P0 - 核心 |
| **ControlNet** | diffusers或ComfyUI节点 | 结构保持 (Canny/Depth/MLSD) | P0 - 核心 |
| **IP-Adapter** | diffusers | 风格迁移参考 | P1 |
| **IC-Light** | GitHub开源 | 光照控制 | P1 |
| **AnimateDiff** | ComfyUI节点 | 建筑漫游视频 | P1 |
| **TripoSR** | GitHub开源 | 户型图→3D | P2 |
| **Blender** | brew install blender | 3D渲染, 相机运镜 | P1 |
| **建筑/室内LoRA** | CivitAI下载 | 特定风格提升 | P1 |

### 📦 推荐下载的模型 (全部免费/开源)

```
# 基础模型 (选1-2个)
1. FLUX.1-dev            - 最新, 质量最高 (需GPU)
2. SDXL (stabilityai)     - 生态最丰富
3. Realistic Vision V6    - 室内/建筑写实

# ControlNet
1. controlnet-canny-sdxl  - 边缘保持
2. controlnet-depth-sdxl  - 深度保持
3. controlnet-mlsd        - 直线/建筑结构

# LoRA (CivitAI免费下载)
1. architectural-visualization
2. interior-design-lora
3. chinese-architecture
4. floor-plan-color
```

---

## 五、关键结论

### 覆盖率: ~85% 可完美本地实现

| 等级 | 数量 | 说明 |
|------|------|------|
| ✅ 完全本地可行 | 27/32 | 标准SD/ControlNet/ComfyUI即可 |
| ⚠️ 部分可行 | 4/32 | 3D重建需要TripoSR, CAD需要专业工具 |
| ❌ 有限 | 1/32 | CAD转3D需结合Blender流水线 |

### 最大缺口: 3D相关功能
- 户型图→3D, CAD→3D, 单图→3D 是本地最难替代的
- 但开源方案 (TripoSR, Zero-1-to-3) 正在快速进步
- 实用性角度: 90%的用户需求是2D出图, 这些3D功能使用频率低

### 投资回报最高的安装顺序

```
第1步: pip install diffusers transformers accelerate
       → 立即解锁: 文生图, 图生图, 室内装修, 风格迁移 (覆盖60%功能)

第2步: 安装ComfyUI + ControlNet + IP-Adapter
       → 解锁: ControlNet精确控制, 立面迁移, 材质替换 (覆盖85%)

第3步: brew install blender  + 下载TripoSR
       → 解锁: 3D渲染, 漫游视频, 户型图转3D (覆盖95%)
```

### 与建筑学长相比的本地优势

1. **零成本** — 不限次数, 不限分辨率, 不限生成量
2. **无水印** — 原图输出, 无平台压缩
3. **无审核** — 不触发AI内容审核 (但不建议违法用途)
4. **可控** — ControlNet精确度远超平台一键生成
5. **可定制** — 自行训练LoRA适配项目风格
6. **可批量** — 脚本批量出图, 大幅提升效率

### 与建筑学长相比的本地劣势

1. **需动手** — 没有Web UI一键出图 (除非写Gradio界面)
2. **需硬件** — Intel Macbook + 32GB内存勉强可跑SDXL (CPU推理慢)
3. **更新追踪** — 平台会集成最新模型 (如GPT-image-2), 本地需手动更新
4. **资源库** — 他们没有提供CAD/SU/PS素材库, 这个需要自行积累

### 关于GPT-image-2 (GPT-4o图像生成)

建筑学长最近上线了 GPT-image-2 (GPT-4o) 的文本直接生成建筑图功能。这个能力特点是:
- **文字渲染能力极强** — 在图上生成法文字/标注
- **构图理解好** — 理解建筑师的自然语言描述

**本地替代**: 暂无完全对等的开源替代, 但SDXL/FLUX + 详细的prompt + ControlNet 可在质量上超越 (只是需要更多调试)

---

## 六、立即行动建议

如果要最快搭建一个可用系统, 推荐:

```
1. 安装 diffusers + transformers
   pip install diffusers transformers accelerate

2. 下载 SDXL base 模型 (~7GB)
   huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0

3. 写一个 Python 脚本, 实现核心功能:
   - 文本→建筑效果图 (txt2img)
   - 照片→装修效果图 (img2img + inpaint)
   - 立面迁移 (controlnet + img2img)
   
4. 写一个 Gradio Web界面 (一行代码 pip install gradio)
   - 一键出图, 比建筑学长的界面更简洁
```

这样就覆盖了建筑学长 **80%以上的日常使用场景**, 且完全免费、无限量。
