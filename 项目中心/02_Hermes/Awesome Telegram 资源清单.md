# Awesome Telegram 资源清单

> 来源：[ebertti/awesome-telegram](https://github.com/ebertti/awesome-telegram) (5.1k stars)
> 整理日期：2026-05-28

官方交流群：[@awesometelegram](https://telegram.me/awesometelegram)

---

## 一、值得关注的 Bot

### 实用工具类
| Bot | 用途 |
|-----|------|
| @weatherman_bot | 天气查询 |
| @voicybot | 语音转文字 |
| @voice_translator_bot | 语音翻译 (speech-to-speech) |
| @pdfbot | PDF 文件处理 |
| @ResizerTool_bot | 图片裁剪 |
| @KillerBgBot | 去背景 (批量上传) |
| @IgGramBot | Instagram 视频/照片/Reels 下载 |
| @CyberCollectorBot | 抖音/TikTok/Instagram/YouTube/X 视频下载 |
| @QuickLinkGeneratorBot | 生成 Telegram 媒体直链 (含加密频道) |
| @RestrictedSaverRobot | 保存限制频道文件 (最大 4GB) |

### 效率与自动化
| Bot | 用途 |
|-----|------|
| @selfmailbot | 消息转发到邮箱 (GTD 适用) |
| @MiddlemanBot | HTTP 调用转 Telegram 消息 (开源) |
| @el_monitorro_bot | RSS/Atom/JSON feed 阅读器 (Rust, 开源) |
| @HyperTAG_bot | YouTube 视频生成标签和摘要 (开源) |
| @SignalDigest_Bot | AI 精选每日新闻摘要 (免费 3篇/天) |
| @AwakariBot | 实时搜索结果推送 (开源) |
| @blogwatcher_bot | RSS/blog 监控 |

### 群管理
| Bot | 用途 |
|-----|------|
| @comstatbot | 群聊数据统计可视化 |
| @joinhider_bot | 自动删除进群/退群消息 |
| @watchdog_robot | 自动删除链接/sticker/GIF/视频等 |
| @daysandbox_bot | 新成员 24h 内禁止发链接 |
| @nosticker_bot | 删除群内 sticker |
| @airnope_bot | 清除加密货币空投 spam (开源) |
| @xiaolangzaibot | AI 反垃圾 (支持 OpenAI/DeepSeek/Qwen, 开源) |
| @InviteMemberBot | 付费频道/群的会员管理 |
| @SUCH | 反馈和支持 bot 生成器 |
| @BanOnExit | 自动封禁进群又退群的用户 |

### 支付/财务
| Bot | 用途 |
|-----|------|
| @ExpenseBot | 日常开支管理 (开源) |
| @TyzenhausBot | 共享开支追踪 |
| @MoniPayBot | 无 Gas 稳定币打赏/订阅 (USDC/USDT) |
| @demo_aiogramshopbot | 开店 Bot (支持加密货币支付, 开源) |

### AI / LLM
| Bot | 用途 |
|-----|------|
| @Plasma_gpt_ai_bot | 接入 ChatGPT-4 + Midjourney, 免费 |
| @ximanager_bot | AI 版... bot |

### 其他实用工具
| Bot | 用途 |
|-----|------|
| @github_gist_bot | 文本上传 GitHub Gist |
| @Ya_Disk_Bot | 上传文件到 Yandex.Disk |
| @StickerShirtsBot | Sticker 转 T 恤 |
| @Unlock2Link_bot | 短链接 + 解锁挑战 (关注/订阅) |
| @QuickCloneBot | 文件分享 Bot (无需编码) |
| @QuickFilterBot | 群文件快速搜索过滤 |

---

## 二、Inline Bot (打字即用)

在聊天框输入 @bot名 + 关键词即可:

| Bot | 功能 |
|-----|------|
| @gif | 动图搜索 |
| @vid | YouTube 视频 |
| @imdb | IMDB 电影 |
| @wiki | Wikipedia 百科 |
| @bing | Bing 图片搜索 |
| @music | 经典音乐搜索 |
| @pic | Yandex 图片 |
| @bold | 排版 (粗体/斜体/等宽) |
| @vote | 投票生成器 |
| @like | 点赞按钮 |
| @foursquare | 分享地点 |
| @githubbot | GitHub 事件通知 |
| @memingbot | 表情包生成器 |
| @guggybot | 文字转 GIF |
| @HideItBot | 隐藏消息 |
| @HideThisBot | 针对/绕过特定人的隐藏消息 |
| @automemebot | 强大表情包生成器 |
| @myinstantsbot | 音效搜索 |
| @relevantxkcdbot | XKCD 漫画搜索 |
| @asciifacesbot | ASCII 表情 (¯\\_(ツ)_/¯) |

---

## 三、游戏 Bot

| Bot | 说明 |
|-----|------|
| @gamebot | 官方 HTML5 游戏 |
| @gamee | Gamee 平台游戏 |
| @unobot | UNO 卡牌 |
| @minegame_bot | 扫雷 (首个可视化交互游戏 bot) |
| @mytetrisbot | 俄罗斯方块 (含多人模式) |
| @TrueMafiaBot | 天黑请闭眼 (群组) |
| @andys_tic_tac_toe_bot | 井字棋 (开源) |

---

## 四、Bot 开发框架 (各种语言)

### Python (最推荐)
- **python-telegram-bot** — 最流行的 Python 封装
- **AIOGram** — 全异步框架 (推荐用于新项目)
- **pyTelegramBotAPI** — 简单易用
- **Telethon** — MTProto 协议客户端 (可做用户 Bot)
- **Pyrogram** — MTProto Python 客户端
- **Folds** — 优雅可扩展框架
- **Teledigest** — LLM 驱动的摘要/频道分析框架

### JavaScript/TypeScript/Node
- **Telegraf** — 最流行的 Node.js 框架
- **grammY** — TypeScript Telegram Bot 框架 (推荐)
- **GramIO** — 强类型框架
- **mtcute** — 现代 MTProto TypeScript 库

### 其他语言
- Go: `telegram-bot-api`, `telebot`
- Rust: `Frankenstein`, `grammers`
- PHP: `MadelineProto` (异步 MTProto), `Nutgram`
- C#: `WTelegramClient`
- Dart: `TeleDart`

---

## 五、工具

| 工具 | 说明 |
|------|------|
| **TGPy** | 在 Telegram 聊天里直接跑 Python 代码 |
| shell2telegram | 命令行输出发到 Telegram |
| telegram-send | 命令行发消息/文件到 Telegram |
| telegram-owl | Go 写的轻量级 CLI 发送工具 |
| telepipe | Bash 工具，管道输出自动发到 TG (自动切分) |
| BanOnExit | 自动封禁进群又退群的用户 |
| telegram-finder | 从手机号/邮箱/LinkedIn 查 TG 用户 |
| Telegram Media Downloader | 自托管 TG 媒体下载守护进程 |
| Untether | 自托管 Bot 桥接 AI 编程助手到 TG (含键盘/语音/文件传输) |
| Maltego Telegram | OSINT 数据采集 |
| botan.io | Bot 数据分析工具 |

---

## 六、渠道与群组

| 名称 | 说明 |
|------|------|
| @awesometelegram | 本清单官方群 |
| @telegram | 官方 Telegram 新闻 |
| @BotNews | Bot API 官方新闻 |
| @hacker_news_feed | Hacker News 热帖 |
| @thedevs | 开发者社区 |
| @codingatnight | 编程/技术每日文章 |
| @Code_Stars | GitHub 热门仓库实时推送 |
| @Opensource_Findings | 开源工具评价 |
| @CatOps | DevOps/SRE 新闻 |
| @Kubernative | K8s/云原生新闻 |
| @Raycast_New_Extensions | Raycast 新扩展推送 |

---

## 七、安全相关

### AI 安全 (英文/俄文)
- PWN AI — LLM 安全/MLSecOps
- LLM Security — Jailbreak/注入/防御
- AI Security Lab — Raft × ITMO 实验室 (攻防)
- AI Attacks — AI 攻击案例流
- AGI Security — 通用人工智能安全

### 网络安全
- @yazoul — 自动 CVE 公告/数据泄露/暗网情报

---

## 八、目录网站

| 网站 | 说明 |
|------|------|
| storebot.me | Telegram Bot 商店 |
| tgdev.io | Bot 列表 |
| groupfind.org | 群组/频道目录 |
| tdirectory.me | 搜索 TG 频道/群组/Bot |
| directorytg.com | 高级频道/App/游戏目录 |
| statiko.io | 公共频道分析平台 (检测编辑/删除) |

---

## 九、对我们有用的资源

结合我们现有的 Hermes Agent + Telegram 集成，以下值得重点研究:

1. **Untether** — 自托管 bot 桥接 AI 助手到 Telegram，已有键盘/语音转文字/文件传输功能，可对标
2. **Teledigest** — LLM 驱动的频道分析/summary 框架，可用于我们的公众号/频道日更
3. **TGPy** — 直接在 TG chat 里跑 Python，适合快速调试
4. **telegram-send / telegram-owl** — CLI 发送消息，cron job 通知可选
5. **python-telegram-bot / AIOGram** — Python 框架，开发自定义 Bot 用
6. **@el_monitorro_bot** (Rust RSS reader) — 可以接 feed，跟 blogwatcher 类似
7. **@HyperTAG_bot** — 视频/链接内容自动总结，适合频道运营
8. **AI 安全频道 (PWN AI/LLM Security)** — 追踪 AI 安全情报
9. **Code_Stars** 频道 — 发现 GitHub 热门项目
