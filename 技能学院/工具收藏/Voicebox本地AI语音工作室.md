# Voicebox — 开源本地 AI 语音工作室

> jamiepine/voicebox | 25.9k⭐ | MIT | TypeScript(55%)+Python(34%)+Rust(9%) | 活跃开发
>
> 官网: https://voicebox.sh | 文档: https://docs.voicebox.sh

---

## 一句话

**ElevenLabs + WisprFlow 合体的开源替代。** 声音克隆+语音合成+听写输入+音频后期，全部本地运行。

---

## 技术架构

```
Tauri(Rust壳) → React前端 → FastAPI后端 → 推理引擎(MLX/CUDA/CPU)
                                              ↓
    MCP Server  ←  SQLite  ←  Whisper(STT)  ←  ↓
                                         + Qwen3-LLM(人设改写)
```

- **桌面壳:** Tauri (Rust) — 不是 Electron，性能好
- **前端:** React + TypeScript + Tailwind + Zustand
- **后端:** Python FastAPI
- **推理:** Apple Silicon → MLX (快4-5x) | Intel Mac → CPU | Windows/Linux → CUDA/ROCm
- **数据库:** SQLite

---

## 核心能力

### 7 套 TTS 引擎

| 引擎 | 语言 | 特点 |
|------|------|------|
| Qwen3-TTS (0.6B/1.7B) | 10 | 高质量克隆，自然语言指令（"说慢点""悄悄说"） |
| Qwen CustomVoice | 10 | 9个预设声音，不需要参考音频 |
| Chatterbox Multilingual | **23** | 覆盖最广（阿拉伯/丹麦/芬兰/希腊/希伯来/印地/马来/挪威/波兰/斯瓦希里/瑞典/土耳其等） |
| Chatterbox Turbo | English | 350M轻量模型，支持音效标签 `[laugh]` `[sigh]` `[gasp]` |
| LuxTTS | English | 轻量(~1GB VRAM)，48kHz输出，CPU上150倍实时 |
| TADA (1B/3B) | 10 | HumeAI 语音语言模型，700s+连贯音频 |
| Kokoro | 8 | 50个预设声音，82M超小型，CPU飞快 |

### 声音克隆
- 几秒音频 → 零样本克隆
- 50+ 预设声音（Kokoro + Qwen CustomVoice）
- 导入/导出声音配置
- 每条声音可配**人格设定**（人设→本地Qwen3 LLM改写→TTS）

### 8 种后期效果
变调/混响/延迟/合唱/压缩/增益/高通/低通
4个内置预设（机器人音/电台/回声室/低音炮）+ 自定义保存

### 多轨编辑器（Stories）
拖拽多角色对话/播客/有声书，支持音频裁剪和版本追踪

### 系统级听写
- 全局快捷键→说话→Whisper转录→自动粘贴到任何输入框
- macOS 无障碍注入，不污染剪贴板
- LLM可选去掉口头语（嗯、那个、就是）
- 浮窗显示录音/转写/朗读状态

### MCP Server — 对 Hermes 最有价值
内置 MCP Server，Claude Code / Cursor / Windsurf / **Hermes** 可通过 MCP 调用：

```
voicebox.speak()      → 让Agent用克隆声音说话
voicebox.transcribe() → 转写音频文件
voicebox.list_captures() → 查看录音记录
voicebox.list_profiles() → 列出声音配置
```

**一句话集成到 Hermes：**
`POST /speak` 或 MCP 工具，Hermes 就能用你的克隆声音回答。

### 完整 REST API
- `POST /generate` — 生成语音
- `POST /speak` — Agent 说话
- `POST /transcribe` — 转写
- `GET /profiles` — 列出声音

---

## 安装

| 平台 | 下载 |
|------|------|
| macOS Apple Silicon | [DMG下载](https://voicebox.sh/download/mac-arm) ~513MB |
| **macOS Intel** | [DMG下载](https://voicebox.sh/download/mac-intel) **~560MB** |
| Windows | [MSI下载](https://voicebox.sh/download/windows) ~517MB |
| Docker | `docker compose up` |

**Intel Mac 注意：** 没有 MLX 加速，跑 CPU 推理，TTS 生成会比较慢，但能用。

---

## 适用场景

### ✅ 对你有用
- **Hermes 声音输出** — 通过 MCP 集成，让 Hermes 用你的克隆声音说话
- **本地听写** — 全局热键说话→自动粘贴，不依赖任何在线STT
- **声音克隆** — 克隆自己的声音，输出中文TTS（Qwen3-TTS/Chaterbox支持中文）
- **EPC 项目汇报** — 生成本地朗读版报告（对有阅读障碍的场景有用）
- **台球俱乐部宣传** — 多角色配音生成广告音频

### ❌ 注意
- **Intel Mac 推理慢** — 这是硬伤，Apple Silicon 快4-5倍
- **包很大** — DMG 560MB + 首次运行还要下模型
- **快速迭代** — 3个月从 v0.1→v0.5，API可能还在变

---

## 结论

**值得装来试 MCP 集成。** 主要价值不是当 ElevenLabs 替代（Intel Mac 慢），而是把 Hermes 接上 Voicebox 的 MCP Server，让 AI 助理**能用你的声音说话**——这才是它对你最独特的价值。

下载: https://voicebox.sh/download/mac-intel (~560MB)
