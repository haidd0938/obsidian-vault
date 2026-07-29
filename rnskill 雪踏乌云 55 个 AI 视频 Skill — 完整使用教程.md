

> 作者：雪踏乌云 · [@Pluvio9yte](https://x.com/Pluvio9yte)  

> 仓库本地镜像：`~/references/rnskill/`  

> 许可证：CC BY-NC 4.0（非商业用途可自由使用/改编，需署名）

---

**一、这是什么**

55 个 `SKILL.md` 格式的 AI Agent 技能文件，覆盖**视频内容生产全链路**：

选题策划 → 内容创作 → 视频下载 → 配音 → 数字人 → 编辑 → 字幕 → 封面 → 动效 → 调度质检

每个 Skill 是一份 Markdown 文件，写清楚**一个环节该怎么做、什么能做什么不能做、质量标准在哪**。AI 读了这份文件，就知道怎么执行这个环节。

**核心创新**：Skill 之间可以链式串联。一条指令触发 8 个 Skill 自动串完，从链接到待制作队列。

---

**二、全部 55 个 Skill 速查**

**选题与策划（4 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ra-选题**|`skills/ra-选题/`|选题全生命周期：灵感→建卡→深化→推荐→立项分发|
|**ra-实操策划**|`skills/ra-实操策划/`|实操长片策划稿：测试题组、结构时间轴、口播稿、录屏清单|
|**ra-hook**|`skills/ra-hook/`|短视频钩子选型：7 种类型×3 大类，带前提/模板/常见错误|
|**ra-video-title**|`skills/ra-video-title/`|视频标题生成：主题锁定→对标拆解→8-12 候选+Top3 推荐|

**内容创作（5 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ra-video-wash-pipeline**|`skills/ra-video-wash-pipeline/`|⭐ **视频洗稿调度器**：自动串下载→逐字稿→洗稿→质量门→待制作队列|
|**ra-逐字稿提取skill**|`skills/ra-逐字稿提取skill/`|抖音/小红书视频逐字稿提取，去水印+Paraformer ASR|
|**ra-洗稿**|`skills/ra-洗稿/`|脚本洗稿核心，自动串人话→AI检测→钩子诊→共鸣→标题|
|**ra-人话**|`skills/ra-人话/`|⭐ **去 AI 味写作**：硬禁清单极其实用，零外部依赖|
|**ra-公众号提取**|`skills/ra-公众号提取/`|微信公众号全文提取，MicroMessenger UA 伪装，纯标准库|

**视频下载（2 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ra-video-download**|`skills/ra-video-download/`|抖音/YouTube/B站/Twitter/小红书下载，yt-dlp+TikHub|
|**xiaohu-video-download**|（外部工具）|额外支持音频下载/播放列表/字幕烧录|

**配音（1 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**tts-skill**|`skills/tts-skill/`|⭐ IndexTTS2 本地声音克隆，固定无损参考，禁止云端 fallback|

**数字人（1 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**heygen-digital-avatar**|`skills/heygen-digital-avatar/`|HeyGen Digital Twin 生成合成，有「先确认试听」硬门|

**视频编辑（4 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ra-local-talking-head-cut**|`skills/ra-local-talking-head-cut/`|本地口播粗剪：ASR→剪前校对→用户确认→语义删减→响度 QC|
|**video-use**|`skills/video-use/`|通用视频编辑：转写/剪辑/调色/动画/烧字幕|
|**ai-jian-koubo**|`skills/ai-jian-koubo/`|口播转录+AI 口误识别+网页审核+FCPXML 导出|
|**chengfeng-videocut-skills**|`skills/chengfeng-videocut-skills/`|乘风口播剪辑原版|

**字幕（2 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ra-audio-to-subtitles**|`skills/ra-audio-to-subtitles/`|火山 Doubao-ASR 词级时间戳+对齐/碎片/阅读速度质检|
|**skill-captions**|`skills/skill-captions/`|字幕外观渲染烧录：anchor-dark/anchor-light 样式，4K 原生|

**视觉与封面（6 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ian-xiaohei-illustrations**|`skills/ian-xiaohei-illustrations/`|小黑猫 IP 概念插画，DashScope wanx 生成|
|**skill-cover**|`skills/skill-cover/`|封面生成：注册风格/双比例资产/自动出图|
|**editorial-dot-cover**|`skills/editorial-dot-cover/`|点阵编辑风封面：暖灰纸底+超大中文标题+留白+点阵图标|
|**editorial-collage-motion**|`skills/editorial-collage-motion/`|半色调拼贴动效，FFmpeg/HyperFrames 渲染|
|**rn-cover-skill**|`skills/rn-cover-skill/`|编辑图解风封面：固定 5:2 暖白画布，左字右图|

**图文制作（1 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**xhs-article-to-images**|`skills/xhs-article-to-images/`|Markdown→小红书 3:4 图片组，5 套皮肤+3 个女性向主题|

**制作调度与质检（2 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**ra-video-production-director**|`skills/ra-video-production-director/`|⭐ **制作总导演**：读交接稿契约→调下游 Skill→状态管理→归档质检|
|**ra-复盘**|`skills/ra-复盘/`|数据取数→爆款分级(R/M)→归因→资产沉淀→选题卡回写|

**视频动效 HyperFrames（6 个）**

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**rn-motion-director**|`skills/rn-motion-director/`|动效导演：选题→视觉隐喻/运动语法/Anti-PPT 门|
|**rn-motion-replica**|`skills/rn-motion-replica/`|参考动效复刻→原创 HyperFrames 工程+QC|
|**rn-dark-saas-video**|`skills/rn-dark-saas-video/`|暗色 SaaS 产品视频：8 套场景蓝图|
|**rn-bw-text-opener**|`skills/rn-bw-text-opener/`|黑白打字机开场动画，3 种时长|
|**rn-replica-qc**|`skills/rn-replica-qc/`|复刻质检：五级保真度+三道全帧门|
|**rn-cover-skill**|（同上封面组）|无参考 SVG 封面自动生成|

**dbs 商业工具箱（22 个）**

来自 [@dontbesilent](https://x.com/dontbesilent) 的开源项目 dbskill。

视频生产中自动调用的（重点）：

|   |   |   |
|---|---|---|
|**Skill**|**目录**|**作用**|
|**dbs-ai-check**|`skills/dbs-ai-check/`|AI 写作特征扫描，检测文稿中的 AI 生成痕迹|
|**dbs-hook**|`skills/dbs-hook/`|视频开头诊断（与 ra-hook 配对：ra 选类型，dbs 诊断执行）|
|**dbs-resonate**|`skills/dbs-resonate/`|文稿共鸣诊断，传播心理学框架|
|**dbs-xhs-title**|`skills/dbs-xhs-title/`|小红书标题公式：75 个验证爆款公式|

独立使用的：

|   |   |
|---|---|
|**Skill**|**作用**|
|dbs-diagnosis|商业模式诊断：问诊+体检两种模式|
|dbs-benchmark|对标分析：五重过滤找可模仿的对标|
|dbs-goal|目标清晰化：维特根斯坦语言哲学审计模糊目标|
|dbs-content|内容创作诊断|
|dbs-spread|传播心理解码：5 个传播学理论|
|dbs-action|执行力诊断：阿德勒心理学框架|
|dbs-deconstruct|概念拆解到原子级别|
|dbs-slowisfast|慢就是快诊断|
|dbs-learning|交互式学习|
|dbs-chatroom|多角色模拟对话|
|dbs-decision|个人决策系统|
|dbs-content-system|内容结构化系统|
|dbs-report/save/restore|诊断存档和报告|

---

**三、在 Hermes 中安装 Skill**

**方法一：直接复制（推荐）**

# 单个安装  
cp -R ~/references/rnskill/skills/ra-人话 ~/.hermes/skills/ra-人话  
  
# 批量安装核心（洗稿链相关）  
for skill in ra-人话 ra-hook ra-video-title ra-洗稿 ra-选题 ra-video-wash-pipeline ra-video-production-director ra-逐字稿提取skill ra-video-download ra-audio-to-subtitles skill-captions tts-skill heygen-digital-avatar; do  
  cp -R ~/references/rnskill/skills/"$skill" ~/.hermes/skills/"$skill" 2>/dev/null || echo "跳过 $skill"  
done  
  
# 安装 dbs 质量门  
for skill in dbs-hook dbs-ai-check dbs-resonate dbs-xhs-title; do  
  cp -R ~/references/rnskill/skills/"$skill" ~/.hermes/skills/"$skill"  
done

**方法二：用 skill_manage 创建**

通过 Hermes 的 `skill_manage` 工具逐个创建（推荐边读边改）。

**安装后验证**

ls ~/.hermes/skills/ | head -20

Hermes 下次会话自动发现新的 Skill。

---

**四、Skill 链式串联 — 核心架构**

这是本套系统最大的价值。Skill 之间不是孤立的，而是通过 `SKILL.md` 中的引用自动串联。

**洗稿链（8 个 Skill 自动串）**

用户说："这个链接做成视频"  
                          ↓  
      ra-video-wash-pipeline（调度器）  
       ├── ra-video-download （拉视频）  
       ├── ra-逐字稿提取skill （转写）  
       └── ra-洗稿  
            ├── ra-人话         （去 AI 味）  
            ├── dbs-ai-check    （扫 AI 痕迹）  
            ├── dbs-hook        （诊开头）  
            ├── dbs-resonate    （查共鸣）  
            └── ra-video-title  （出标题候选）  
                          ↓  
              交接稿 → 待制作队列

**制作链（7 个 Skill 自动串）**

      ra-video-production-director（导演）  
       ├── tts-skill                （配音）  
       ├── heygen-digital-avatar    （数字人）  
       ├── ian-xiaohei-illustrations（插画）  
       ├── HyperFrames 渲染  
       ├── ra-audio-to-subtitles    （字幕时间戳）  
       ├── skill-captions           （烧字幕）  
       └── 质检 + 归档

**关键设计模式**

1. **交接稿契约** — Skill 之间通过 `交接稿.md` 传递结构化数据，frontmatter 是硬合同（比例/时长/声音/字幕风格），下游不能覆盖

2. **状态管理** — 项目文件夹从「待制作」→「制作中」→「已制作」，防止两台机器重复制作

3. **质量门** — dbs-* Skill 作为质量门嵌入流水线，发现问题不 dump 报告，直接改稿

4. **隐私墙** — 源视频的原文/标题/链接不出现在任何产物中

---

**五、案例实战：从链接到成片**

**场景：做一条抖音 AI 工具评测视频**

**用户输入：**

> "这个链接做成视频 https://v.douyin.com/xxxxx/"

**实际自动发生的事：**

#### Step 1: 选题登记

`ra-选题` 在 `00-选题池/` 建选题卡，记录来源链接。

#### Step 2: 洗稿链（8 个 Skill）

`ra-video-wash-pipeline`：

5. 查重台账检查该链接是否洗过

6. `ra-video-download` 下载源视频到 `.internal/`

7. `ra-逐字稿提取skill` 跑 Paraformer ASR 转写

8. `ra-洗稿` 改写脚本（内部串 5 道质量门）

9. 输出 `交接稿.md` 到 `待制作/` 队列

#### Step 3: 产出交接稿

01-内容生产/视频工作台/待制作/2026-07-27-ai工具测评/  
├── 交接稿.md    ← frontmatter 记录平台/时长/风格/配音需求

#### Step 4: 人工确认

用户做三件事（约 5 分钟）：

10. ✅ 确认校对稿

11. ✅ 确认试听音频

12. ✅ 挑封面

#### Step 5: 制作链（8 个 Skill）

用户说"直接出片"，`ra-video-production-director`：

13. 状态 `待制作`→`制作中`

14. tts-skill 用 IndexTTS2 本地声音克隆配音

15. heygen-digital-avatar 生成数字人（如需）

16. ian-xiaohei-illustrations 生成配图

17. HyperFrames 渲染

18. ra-audio-to-subtitles 跑字幕时间戳

19. skill-captions 烧字幕

20. 质检→归档→状态 `已完成`

---

**六、推荐学习路径**

按从易到难排列：

**第一阶段（纯写作，零外部依赖）**

21. **ra-人话** — 读完整个 SKILL.md，理解去 AI 味的硬禁清单，所有中文写作都能用

22. **ra-hook** — 7 种钩子类型+决策流程，写视频开头用

23. **ra-video-title** — 两段式标题生成方法论

24. **dbs-ai-check / dbs-hook / dbs-resonate** — 三道质量门，当质检器用

**第二阶段（选题与内容策略）**

25. **ra-选题** — 选题全生命周期管理，配合 Obsidian 或便签系统

26. **ra-洗稿** — 脚本改写方法论

27. **ra-实操策划** — 长视频策划模板

**第三阶段（视频流水线）**

28. **ra-video-wash-pipeline** — 洗稿调度器，理解链式串联模式

29. **ra-video-production-director** — 制作总导演，505 行的完整编排标准

30. **ra-复盘** — 发布后数据分析和资产沉淀

**第四阶段（具体工具）**

31. **ra-video-download** + **ra-逐字稿提取skill** — 下载和转写

32. **tts-skill** + **heygen-digital-avatar** — 配音+数字人

33. **ra-audio-to-subtitles** + **skill-captions** — 字幕

34. **rn-cover-skill** + **skill-cover** — 封面

---

**七、与 Hermes 已有能力的对比**

|   |   |   |
|---|---|---|
|**能力**|**rnskill**|**我们已有**|
|ra-人话 去AI味|⭐⭐⭐⭐⭐ 296行硬禁清单|humanizer skill 但规则不够具体|
|封面生成|多种风格(SVG+PNG)|rn-cover-skill 已装|
|视频动效|HyperFrames 6个 Skill|HyperFrames skill 已装|
|字幕|火山引擎ASR+样式渲染|bri-video-srt skill|
|小红书图文|Markdown→图片组|article-tools-workflow|
|洗稿链式调度|⭐ 差异化最强|无|
|制作导演模式|⭐ 差异化最强|无|
|dbs 商业诊断|22个诊断 Skill|无|

---

**八、外部依赖清单**

如果真要跑通全链路，需要准备：

|   |   |   |
|---|---|---|
|**依赖**|**用途**|**是否必须**|
|yt-dlp|视频下载|视频流水线必需|
|TikHub Token|抖音去水印|抖音源必需|
|Paraformer ASR|逐字稿转写|可选（可换火山引擎）|
|IndexTTS2|本地声音克隆|配音必需|
|HeyGen API|数字人生成|数字人必需|
|火山引擎 Doubao-ASR|字幕时间戳|字幕必需|
|HyperFrames|代码驱动动效|动效必需|
|FFmpeg|视频处理|必需|
|DashScope wanx|AI 生图|小黑猫插画必需|

---

**附：快速参考命令**

# 仓库本地路径  
cd ~/references/rnskill  
  
# 查看所有 Skill 目录  
ls -d skills/*/  
  
# 读一个 Skill 的内容  
cat skills/ra-人话/SKILL.md  
  
# 统计 Skill 数量  
ls -d skills/*/ | wc -l  
  
# 安装到 Hermes  
cp -R skills/ra-人话 ~/.hermes/skills/ra-人话  
  
# 打包特定 Skill 供分享  
cd skills/ra-人话 && zip -r ~/ra-人话.zip .