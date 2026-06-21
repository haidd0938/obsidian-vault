2026-04-01 - 身份确认 > 关键设定: 名字：贾维斯
§
2026-04-01 - 身份确认 > 关键设定: 用户称呼：老板
§
2026-04-26 - Provider: DeepSeek(deepseek-chat)优先，NVIDIA(免费)备选。switch-provider.sh已修复，快捷:nvidia/deepseek/status。config.yaml.save是4月25日23:30干净备份(恢复用)。
§
2026-04-19 - 系统配置偏好：用户偏好简单的一键启动命令，已为其创建n8n启动脚本（~/n8n/start-n8n.sh）和快捷命令（n8n-start）。关注Hermes与n8n可视化工作流的集成，这是构建超级个人助理系统的关键部分。n8n运行在localhost:5678端口，数据存储在~/n8n/data目录。
§
2026-04-27 - 四个项目并行: 1) 成县名宿(设计施工) 2) 常记呱呱(设计施工勘查) 3) 古浪宁氏钙材料(厂区+办公楼) 4) 宁氏尊词装饰工程。超级个人助理实施方案已认可
§
Telegram集成需求：用户Telegram网络问题已通过TUN模式解决，现在需要设置Telegram Bot集成。用户希望使用Telegram作为主要的即时通讯渠道。
§
2026-04-26 - TG修复：在config.yaml的platforms.telegram下加了extra.channel_prompts（中文强制指令），清理了旧TG session和sessions.json索引，重启了gateway。TG连接正常，polling模式。
§
2026-04-19 - n8n配置完成：已为用户创建n8n Docker配置和启动脚本。配置包括：1) docker-compose.yml文件在~/n8n目录；2) 启动脚本start-n8n.sh，可通过./start-n8n.sh或n8n-start启动；3) n8n运行在localhost:5678端口；4) 数据持久化存储在~/n8n/data目录。用户可轻松启动n8n服务用于与Hermes集成。
§
2026-04-20 - NVIDIA NIM API密钥重新确认：用户再次申请NVIDIA NIM免费API密钥，与现有配置完全相同。测试确认API密钥有效，可访问132个模型，包括已配置的meta/llama-3.1-8b-instruct模型。密钥有效期至2026年10月18日，免费额度每分钟40次调用。Hermes配置已使用此密钥，默认模型为NVIDIA NIM免费模型以避免DeepSeek高成本。已配置环境变量代理设置以解决Telegram连接问题。
§
2026-04-26 - 语音模式配置完成：Hermes 语音模式已配好。STT=本地faster-whisper(base,免费), TTS=Edge TTS(zh-CN-XiaoxiaoNeural,免费)。方案：Telegram发语音→STT转文字→处理→TTS语音回复，适合开车场景。config.yaml已改TTS语音为中文。Gateway已重启运行。
§
短视频合成器: ~/Desktop/鑫球汇视频合成器.py (Python+Edge TTS+FFmpeg零成本方案)。改SCENES列表换文案，运行自动出竖屏1080x1920视频到~/Desktop/鑫球汇视频/。Edge TTS推荐声线: YunxiNeural(搞笑男声), XiaoxiaoNeural(晓晓女声)。
§
Vision已配：NVIDIA NIM上meta/llama-3.2-11b-vision-instruct做辅助视觉模型，免费。
§
MacBook Pro是Intel芯片，无MPS/GPU加速。跑SD/FLUX等图像生成模型只能靠CPU推理，速度很慢。涉及AI图像生成的任务应优先考虑免费API方案而非本地模型推理。
§
2026-04-26 - NVIDIA NIM API只有LLM和多模态视觉模型（meta/llama-3.2-11b-vision等），没有Stable Diffusion/FLUX等图像生成模型。图像生成需要Fal AI（注册送$5，SDXL $0.012/张）、Hyperbolic（首充$1送$10）、OpenRouter（SDXL $0.006/张）等第三方服务。
§
2026-04-27 - Provider自动切换已永久禁用：用户因NVIDIA自动切换导致"胡说八道"问题，已删除auto-switch cron job。只能按用户命令手动切换。