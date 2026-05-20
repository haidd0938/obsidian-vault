---
name: tool-evaluation
description: "快速评估开源工具/项目的可用性：老板发来 GitHub 链接，快速判断能不能装、有什么用、有没有必要。产出三栏结论：能装吗？有什么用？有必要吗？"
triggers:
  - 老板发 GitHub 链接问"研究一下"
  - 老板发 X/Twitter 推文链接问"帮我搞一下" / "研究一下这个"
  - "这个我能装吗"
  - "有什么用/有必要吗"
  - 任何"帮我看看这个工具/项目"的请求
  - 老板连续发多条X推文链接说"融合到现有体系搞钱"
---

# 技术工具快速评估

老板经常发来 GitHub 项目让评估。回答结构要干脆：直接结论先行，然后分三块分析。

## 特殊场景1：X推文链接的在线服务评估

老板有时会发X推文链接（如免费解析站合集），要求评估并产出可用工具。流程：

1. **先确认推文可访问性** — 用浏览器打开或API尝试获取内容。如果X跳登录页，换headless方式或从上下文推测
2. **快速验证每个服务的可用性** — 对列表中的每个URL做HTTP健康检查（curl -sI / curl -sL），确认200状态码
3. **理解服务原理** — 检查页面源码，理解服务的工作方式（API调用、iframe嵌入、WASM等）
4. **评估对老板的价值** — 思考如何整合到老板现有体系（EPC业务、鑫球汇台球、信息套利）
5. **产出可用工具** — 如果服务有价值，直接搭成可用的HTML页面（快捷键：claude-design技能），而不是只给分析报告。老板喜欢"直接能用"的交付物
6. **附带变现方向分析** — 结合老板的副业场景（台球厅、公众号、短视频等），给出2-3个具体可行的变现方向，按投入产出排序

## 特殊场景2：批量X推文推荐GitHub项目的评估

老板有时会连发多条X推文链接，每条推荐一个GitHub项目（如"小红书起号神器"、"图片转3D工具"、"一人公司方法论"）。这是"好工具寻找"的批量模式。流程：

1. **并行抓取所有X推文** — 用browser_navigate逐个打开推文链接。注意X页面经常跳登录页导致内容为空，但browser_snapshot有时能读到部分内容。优先观察snapshot中的article元素（包含推文文本和链接）
2. **提取每个推文中的GitHub项目地址** — 在snapshot中找到链接元素（通常以`github.com/...`形式出现），注意：
   - 推文会截断长项目名（如显示`github.com/xpzouying/xiao...`但实际是`xiaohongshu-mcp`）
   - 推文自带的链接卡片可能会指向正确的GitHub页面 — 点击卡片区域（ref可能带onclick属性）可跳转到实际GitHub URL
3. **打开每个GitHub项目页面获取关键数据** — ⭐数、语言、描述、最近提交时间
4. **先判断推文是否夸大了星数** — 推文可能说"15.4k⭐"，但实际是另一个同名不同项目。**不能轻信推文里的⭐数**，必须到GitHub页面确认实际数据
5. **交叉验证项目身份** — 如果搜不到推文里提到的名字，尝试用中文关键词（如"一人公司 skill" "方糖 OPC"）搜索。实际项目可能藏在搜索结果后面
6. **批量输出：结论先行，再逐个分析，最后给融合方案** — 老板发多条的目的不是要逐个分析，而是要你**给结论和方案**。结构：
   - **一句话总览**：这几条里哪几个值得搞、哪个先搞
   - **逐个核心价值**：每条一句话概括核心能力
   - **融合优先级排序**：哪个先落地、哪个暂缓（说明理由）
   - **具体融合路径**：怎么接入现有体系（MCP注册/cron自动化/Skill化等）
7. **优先级判断**：
   - 🔥 立即搞：能直接做成MCP Server/Skill的，或接入成本<30分钟的
   - 🟢 可以搞：需要一点配置但价值明确的
   - 🔶 暂缓：Intel Mac不支持、生态不成熟、或重复现有能力的
   - ❌ 不搞：成本高收益低或受众错配的
8. **融合完成后要更新tool-evaluation的references** — 把评估结果、实际数据、集成方式写进对应reference文件
9. **对\"已经在运行\"的工具要检查实际状态** — 不只是看README，还要检查launchd/进程/cron等实际运行状态。有些工具可能早就装好了但没启用

## macOS 二进制工具安装工作流

老板发来的 GitHub 项目如果是**CLI 二进制工具**（Go/Rust 编译的单文件），安装流程有固定模式：

### 安装尝试顺序（按成功率排序）

1. **首选：brew install**（如果有 Homebrew formula）
2. **次选：npm install -g**（但注意 EACCES 权限问题，需要 sudo 或修改 npm 全局路径）
3. **直接下载 Release 二进制** — 最可靠方式：
   - 从 GitHub Releases 页面下载对应架构的二进制
   - Intel Mac 选 `*-x86_64` 或 `*-amd64`，不选 `*-arm64`
   - 下载到 `/tmp/` 再 `sudo mv` 到 `/usr/local/bin/`
   - 如果 curl 下载慢，用 Python `urlretrieve` 替代
4. **install.sh 一键脚本** — 安全但需要提前检查脚本内容
5. **go install** / **cargo install** — 最后手段，编译慢

### WeChat 相关工具的特殊步骤

微信相关 CLI（如 wx-cli）需要先给微信做 ad-hoc 签名：

```bash
# 基础签名
codesign --force --deep --sign - /Applications/WeChat.app

# 如果 WeChatAppEx.app 子组件报 Operation not permitted：
codesign --force --sign - "/Applications/WeChat.app/Contents/MacOS/WeChatAppEx.app"
codesign --force --deep --sign - /Applications/WeChat.app

# 完成后续微信重启
killall WeChat; open /Applications/WeChat.app
```

微信更新后需要重新签一次。签名失败不影响微信使用，只影响 wx-cli 读取数据。

### sudo 密码处理

如果安装需要 `sudo mv`，Hermes 的 terminal 工具不支持交互式密码输入。解决方案：
- 让老板在终端手动执行 `sudo mv /path/to/binary /usr/local/bin/xxx`
- 或提前配置 sudoers 免密码：`echo 'mac ALL=(ALL) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/mac`

## 评估清单

### 1. 平台兼容性（能不能装？）
检查项目核心依赖与老板环境是否匹配：

- **芯片架构**：他的 MacBook Pro 是 **Intel 芯片**（非 Apple Silicon）
  - 项目只支持 Apple Silicon 的 MLX / Core ML / Metal → ❌ 不能
  - 纯 CPU 可跑或通用 Python → ✅ 可以，但注意 CPU 推理速度
  - 需要 GPU / CUDA → ❌ 不能（Intel Mac 无 GPU 加速）
- **系统要求**：macOS 版本、Python 版本、额外依赖
- **安装方式**：brew / pip / npm / Docker — 越简单越好

### 2. 核心功能（有什么用？）
从 README 提取关键信息：
- 项目定位（一句话）
- 核心能力 vs 现有方案对比
- 对老板场景的直接价值（EPC 业务、AI 助理、台球俱乐部、信息套利）
- 关键指标：速度、精度、API 兼容性、工具链集成

### 3. 必要性判断（有必要吗？）
结合老板现有体系判断：
- 是否有**重复/替代**：他已有的 Ollama、Hermes、DeepSeek API 是否已覆盖
- **增量价值**：新工具带来什么现有方案没有的
- **成本**：安装配置成本 vs 收益
- 老板的偏好的风格风格**务实、成本敏感**、**稳定压倒一切**
- **检查项目是否已经安装/运行了** — 用 launchctl list / ps aux / 检查端口 等方式确认。不要假设 README 说的"支持"就代表已经装好了

### 4. 如果结论是"不推荐"
给出理由后，可以提一句"如果你之后换了 M 芯片 Mac，可以再考虑"作为收尾。

## 注意事项（Pitfalls）

- **不要只抄 README** — README 是项目方的宣传，要结合老板的实际场景做判断
- **项目目标受众 vs 老板身份的匹配度检查** — 很多 AI 项目面向游戏玩家、二次元爱好者、主播等特定人群。先确认项目定位（阅读README简介），再对照老板的实际身份（建筑EPC从业者、台球俱乐部经营者、技术爱好者），明显不匹配的直接在"有必要吗"栏点出受众错配，不要让老板花时间研究一款为完全不同人群设计的工具
- **Intel Mac 是硬限制** — 很多新 AI 工具只支持 Apple Silicon，直接判断不用试。但注意：即使项目 README 说支持 macOS，实际 Releases 页面可能只提供 Apple Silicon (arm64/aarch64) 的 DMG/pkg/binary。**要检查 Release 页面实际提供的构建产物架构**，不止看 README 的系统要求声明
- **老板优先用 API 方案** — 他目前的模式是 DeepSeek API 主力 + Ollama 本地备用。纯本地方案除非有显著优势，否则吸引力不大
- **回答要简洁** — 他有信息套利研究中说的"信息筛选直觉"，不喜欢冗长。三栏直接给结论，展开只在关键点上
- **要判断"是否值得安装尝试"** — 即使理论上能装，如果配置复杂且收益不大，直接说不推荐
- **评估语音/输入类工具时，先对焦老板现有的语音 AI 模式** — 老板已建立「发语音→贾维斯回语音」的闭环（Auto-TTS + Edge TTS），文字和语音同步规则已确定。语音工具（如 OpenLess、Whisper 本地方案）需要判断：它是补充这个闭环，还是试图替代它？老板的场景是"和 AI 说话"，不是"自己口述写 prompt 再粘贴"
- **检查工具的实际运行状态** — 已安装 ≠ 正在运行。要用 launchctl list, ps aux, curl 端口检查 等方式确认服务是活着的。注意 launchd 的 KeepAlive 机制可能导致服务反复启停，日志中有 "address already in use" 说明端口冲突
