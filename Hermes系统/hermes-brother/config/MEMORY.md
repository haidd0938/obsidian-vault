系统运维：OpenClaw kill Gateway加载新dist(launchd自拉起)。Web UI:18789。Drafted.ai技能已保存(skill drafted-ai-house-plans)：免费AI住宅平面图生成，88K+方案，PDF/CAD免费下载。EPC客户沟通/别墅/民宿场景。
§
小红书体系完整入库: 技能学院/生产力工具/小红书自动化运营, 创意设计/小红书封面设计, 研究分析/小红书变现路径设计。总纲已更新。
§
文件操作陷阱：终端 ls 显示的文件名可能含零宽空格(\u200b)导致 Finder 不显示。诊断用 Python repr()，修复用 os.rename() 去除不可见字符。桌面路径用绝对路径 /Users/mac/Desktop/（mac是用户名不是haidd）。Python write_file 和 terminal 操作可能路径行为不同，优先 terminal。
§
顾比交易大脑完整系统已建成(模拟盘+回测+7:30cron)。已模拟买入锂电池ETF+沪深300ETF。历史信号胜率43.8%,能源ETF最佳+8.77%。技能gubi-trading-brain已覆盖全部功能。
§
飞牛NAS Obsidian备份待配置。老板回家喊一声，用rsync+launchd配自动同步到飞牛NAS共享文件夹。NAS FN ID: haidd0938，远程穿透不稳，需局域网操作。
§
2026-05-08 - Apple Reminders已联通（remindctl已安装+Full access）。列表：提醒事项（5条待办）。可创建同步到iPhone的提醒。Apple Notes备忘录也已联通：memo 0.5.2用于查看/搜索笔记（memo notes / memo notes -s "关键词"），创建笔记用 osascript（subprocess.run + osascript via Python）。43条笔记，7个文件夹。
§
语音/文字同步规则：老板发语音→贾维斯回语音，老板发文字→贾维斯回文字。Auto-TTS已开启，开车时自动语音沟通。
§
Mac是Intel芯片(x86_64)，不是Apple Silicon(arm64)。下载macOS应用时要用x64版本，不能用darwin-arm64。
§
飞牛NAS备份已配置：rsync+launchd每小时整点自动备份Obsidian Vault到NAS。NAS IP 192.168.1.5:5666，SMB共享obsidian-backup通过Finder钥匙串自动挂载。备份脚本/Users/mac/scripts/backup-obsidian.sh，手动命令backup-obsidian。FNOS web API: fnos/fs/file/mkdir可直接创建文件夹绕过UI限制。
§
股票系统对比 (2026-05-08)：对比了HKUDS/Vibe-Trading(6k⭐)和ZhuLinsen/daily_stock_analysis。结论：不替换现有系统，但有4个改进方向——①大盘复盘模块 ②决策评分卡输出 ③缠论/波浪/一目均衡高级技术分析 ④多渠道推送。Vibe-Trading可作为MCP集成按需使用。完整对比在stock-robot技能references/vibe-trading-dsa-comparison-2026-05-08.md。
§
顾比交易大脑升级 v2.0 (2026-05-08)：新增 brain/market_overview.py(大盘复盘:指数+涨跌统计+板块+趋势)、brain/decision_engine.py(决策评分卡:0-100评分+A+/A/B+/B/C/D评级+买卖点位+风险警报+检查清单)、brain/advanced_tech.py(缠论:分型/笔/中枢/买卖点+艾略特波浪+一目均衡表)、brain/notifier.py(多渠道推送框架:企业微信/飞书/终端/macOS)。Cron已更新每日7:30顾比早报包含全部新模块。中优先级待升级：1) 配置企业微信/飞书Webhook推送 2) Vibe-Trading MCP集成 3) AI辅助决策模块 4) 交割单分析。
§
复合检查机制已上线(2026-05-09)：7个副业cron全部挂了检查脚本(~/.hermes/scripts/checkers/)。机制：到点先跑检查脚本，HAS_OUTPUT=true就跳过，false才执行。甘肃项目已改为用web_search替代失效的甘肃平台API。
§
2026-05-10 - 小红书MCP已接入Hermes：xiaohongshu-mcp(13.4k⭐, Go, Intel Mac原生) 端口18060，launchd自拉起，13个MCP工具。融合Skill已建: opc-growth-xiaohongshu-fusion。账号"AI副业研究所"(手机号注册)已登录，cron每日10点自动发AI工具测评。