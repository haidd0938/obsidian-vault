# Session Learnings — 2026-05-04

## v3.5 脚本已验证可用

`~/Desktop/东盛热点视频合成器.py` (v3.5, 476行) 已在 2026-05-04 成功运行：
- 生成7段场景配图（含建筑网格/警示横幅/柱状图/饼图/品牌展示/互动页）
- Edge TTS配音全部成功（YunjianNeural）
- Ken Burns动效+字幕叠加正常
- 最终输出：116秒, 78MB, 1080x1920 竖屏, H.264 VideoToolbox编码

## BGM下载失败：corporate-technology-8bit.mp3 不可用

本次BGM源 `https://raw.githubusercontent.com/nicedoc/free-bgm/main/corporate-technology-8bit.mp3` 返回404/超时。
尝试备选 `corporate-technology.mp3` 同样失败。
GitHub Raw上的 free-bgm 仓库现已不可用。

**结论：** 不要再依赖 GitHub Raw 的 free-bgm 仓库。如果用户没有本地BGM文件，告知用户自行提供。

## web_search 工具在 delegate_task 中可用

本次使用 `delegate_task` + `web_search`（通过toolsets=["web","search"]）成功检索了7组搜索关键词，共获取14条新闻结果。
耗时约26秒，远快于浏览器方案（2-6分钟）。
推荐优先使用 `delegate_task + web_search` 代替浏览器检索热点。

## 视频输出验证命令

```bash
ls -lh ~/Desktop/东盛建筑视频/住建部今日出手*.mp4
# 输出: 78M ... 住建部今日出手！EPC违规分包被严查，2026资质改革下谁被洗牌？.mp4
```

## 选题组合策略（本次成功）

将两个同日交叉的热点组合为一个视频：
- 热点A：住建部紧急叫停EPC违规分包（今日突发新闻）
- 热点B：2026资质改革落地（593→245类别，行业洗牌）
- 串联逻辑：违规分包的根因在于资质门槛太低 → 新资质改革提高门槛 → EPC模式是解决方案
- 效果：信息密度高、从业者共鸣强、自然带出品牌
