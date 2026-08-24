# AI 工具付费/免费对照表（收藏）

> 来源：X/Twitter 帖子（2026-08 收藏）
> 状态：**短链未解析**（t.co 国内被墙，网络解析不出目标）。想看具体工具时逐个打开。
> 分类：12 类工具 × 付费版/免费版各一个链接

## 对照表

| # | 类别 | 付费版 | 免费版 |
|---|------|--------|--------|
| 1 | 研究工具 | http://t.co/pxPBeXMHSG | http://t.co/c6K9QBTzeU |
| 2 | 视频生成 | http://t.co/ctq9QQMeMk | http://t.co/4xbuaHfBQY |
| 3 | 设计工具 | http://t.co/FZGZAVHzA7 | http://t.co/cyWBnoZ2vf |
| 4 | 图像生成 | http://t.co/qpur1TNFSJ | http://t.co/90D7T7ZDzi |
| 5 | 代码助手 | http://t.co/3ymxjh4dYC | http://t.co/NdVY5N45xi |
| 6 | 演示文稿制作 | http://t.co/9LRu0ch43n | http://t.co/2CXrRESunN |
| 7 | 声音克隆 | http://t.co/7e5KI6tgA9 | http://t.co/HfUrgCAgHI |
| 8 | 视频编辑 | http://t.co/PZd4jM1f03 | http://t.co/UsPj2BwCu2 |
| 9 | AI 写作 | http://t.co/vn3RGNY0mG | http://t.co/qZLqZT4AFO |
| 10 | 自动化工具 | http://t.co/7fZjAHF61N | http://t.co/crz4WKz4pb |
| 11 | 网站建设 | http://t.co/WE1Xp4yqD3 | http://t.co/zDUiBTUumO |
| 12 | AI 会议记录 | http://t.co/yvCISLGgQA | http://t.co/51bxWxwglF |

## 解析方法（想看具体工具时）

t.co 短链国内直连不通，走代理解析：

```bash
# 解析单个（走 FlyingBird 代理）
curl -sL -x http://127.0.0.1:7892 -o /dev/null -m 20 -w "%{url_effective}\n" "http://t.co/短链码"
# 或浏览器（agent-browser）打开会自动跳转
```

## 备注

- 付费/免费各一个 = 同一类工具的"花钱版"和"免费替代"对比
- 老板偏好：免费优先、稳定优先，付费工具先看免费版够不够用
- 与现有工具重叠检查（部分可能已有替代）：
  - 图像生成 → SiliconFlow Z-Image（已有）
  - 声音克隆 → MiniMax T2A / IndexTTS2（已研究）
  - 视频生成 → MeiGen / Seedance（已研究）
  - 代码助手 → Codex / Claude Code（已配置）
  - 会议记录 → 讯飞听见（已推荐）
