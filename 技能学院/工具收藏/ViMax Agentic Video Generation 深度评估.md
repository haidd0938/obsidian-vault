# ViMax: Agentic Video Generation 深度评估

**链接**: https://github.com/HKUDS/ViMax  
**⭐ 4,718 stars | 🍴 845 forks | 🐍 Python | 📄 MIT | 最后更新: 2026-03-29**  
**🏫 香港大学数据科学实验室 (HKUDS)**

---

## 这是什么？— "一句话生成完整视频"的多Agent框架

ViMax 是由香港大学研究团队开发的**多智能体端到端视频生成框架**。输入一个创意/小说/剧本，自动完成：

1. 🧬 **长剧本生成** → RAG引擎从长篇内容自动切分为多场景剧本  
2. 🪄 **分镜设计** → 电影语言生成镜头级 storyboard  
3. 🔮 **多机位模拟** → 同一场景多机位拍摄+位置一致性  
4. 🧸 **智能参考图选择** → 自动选首帧参考图，确保角色/环境一致性  
5. ⚙️ **自动化图像生成** → 自动生成图像 prompts + 空间位置  
6. ✅ **一致性校验** → MLLM/VLM 并行生成+最优帧选择  
7. ⚡ **并行镜头生成** → 同机位镜头并行处理  

**四种模式**：创意→视频 (Idea2Video) | 小说→视频 (Novel2Video) | 剧本→视频 (Script2Video) | 照片客串 (AutoCameo)

## 能装吗？— **❌ 不能装（Intel Mac 硬限制）**

| 检查项 | 结果 |
|--------|------|
| 系统要求 | Linux/Windows (README明确写支持这俩) → **macOS未列在支持列表** |
| Python版本 | ≥3.12 ✅ |
| uv依赖管理 | 项目用 uv sync，环境管理可行 ✅ |
| **Google API依赖** | 需要 `google-genai` + Google API Key → 国内网络无法直接使用 ❌ |
| **视频生成引擎** | 需要 Veo (Google Veo) API / Nanobanana API → 国内不可用 ❌ |
| **图像生成引擎** | 需要 Google Imagen API → 国内不可用 ❌ |
| **PyTorch依赖** | `torch` 需要 CUDA 12.8 → Intel Mac 无 CUDA ❌ |
| 时间同步 | 2026-03-29最后更新，**近2个月无更新**，可能已停更 ⚠️ |
| Intel Mac 额外限制 | `scenedetect[opencv]` 和 `opencv-python` 依赖摄像头/加速框架，Intel Mac可能需要额外配置 |

**结论：Intel Mac + 国内网络 = ❌ 双重打击。**

## 有什么用？— **对 AI 视频创作者来说很震撼**

### 核心能力（看演示效果非常炸裂）

- **Idea2Video**: "猫和狗是好朋友，遇到一只新猫会怎样？" → 自动生成3场景动画视频
- **Script2Video**: 写篮球训练剧本 → 自动转分镜+生成长视频
- **Novel2Video**: 完整小说自动压缩为分集视频
- **AutoCameo**: 上传你的照片，作为客串角色融入视频

### 技术亮点

| 能力 | 评价 |
|------|------|
| **角色一致性** | ✅ 多Agent校验，角色外观跨场景保持一致 |
| **长视频能力** | ✅ 不是几秒片段的拼接，是真正分钟级长视频 |
| **音画同步** | ✅ 角色语音+音效自动同步 |
| **电影级分镜** | ✅ 用电影语言（不是简单提示词） |
| **多机位模拟** | ✅ 机位切换+空间位置一致性 |
| **并行生成** | ✅ 同机位镜头并行处理 |

### 和你的场景的关系

| 场景 | 价值 |
|------|------|
| EPC施工视频 | 🔴 不相关（不是做教育视频的） |
| 台球厅宣传视频 | 🟢 理论上有用——一句话生成台球厅宣传短剧 |
| 小红书视频 | 🟢 理论上有用——自动生成小红书爆款视频 |
| 出海接单 | 🟢 包装成"AI视频制作服务"接单 |
| 模型训练/部署 | 🔴 跟你的技术栈不搭（Google API 系 vs Hermes/Ollama系） |

## 有必要吗？— **❌ 目前没必要**

### 原因

| 维度 | 结论 |
|------|------|
| **硬件** | Intel Mac + 国内网络 = 装不了，跑不动 |
| **API依赖** | 全是 Google (Veo/Imagen/Gemini) API，国内直连基本没戏 |
| **不在 macOS 支持列表** | 官方只写了 Linux/Windows，macOS 未知 |
| **开发状态** | 近2个月未更新，学术项目，可能暂停了 |
| **实际生产力** | 演示视频很炸裂，但学术项目到生产可用还有距离 |
| **你的视频需求** | 现有 `video-script-to-production` skill 已覆盖短视频生成，质量够了 |

### 值得关注的方向

如果未来：
1. 换了 M 芯片 Mac + 能直连 Google API
2. 项目支持了 macOS
3. 视频质量从"演示级"进化到"可用级"

**那时可以重评。**

目前可以借鉴它的**多Agent分镜设计思路**改进自己的 `video-script-to-production` skill——特别是角色一致性校验和电影分镜语言的部分。

---

## 技术细节（供参考）

### 依赖栈
```
google-genai (Google AI SDK)
langchain + langchain-community + langchain-openai
openai (API兼容层)
faiss-cpu (RAG向量检索)
scenedetect[opencv] (场景检测)
moviepy (视频合成)
opencv-python
torch + torchaudio (CUDA后端)
```

### 运行成本（纯API调用，估计）
- **Chat Model**: OpenRouter / Google Gemini API（按 token 计费）
- **Image Gen**: Google Imagen / Nanobanana API（每张图约 $0.01-$0.05）
- **Video Gen**: Google Veo 2 API（每分钟视频约 $5-$20）
- **单次 30秒视频预估**: $3-$15

### 架构亮点
- 6层流水线：Input → Central Orchestration → Script Understanding → Scene Planning → Visual Asset → Synthesis
- MLLM做一致性校验（VLM选择最优帧）
- RAG做长文本剧本分割
- 同机位镜头并行生成（线性依赖的部分串行）
