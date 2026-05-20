---
name: opc-growth-xiaohongshu-fusion
description: 方糖OPC获客方法论 + 小红书MCP自动化融合Skill。用AI自动做内容、发笔记、引流私域、成交转化。适合EPC业务获客、台球俱乐部引流、个人副业小红书起号。
version: 1.2.0
updated: 2026-05-10
lessons:
  - "老板说『全权处理』时：先产出内容草案给老板过目，老板说OK再发布。不要直接发，除非老板明确说『你自己决定』"
  - "老板发多个X链接要求融合到现有体系时：逐个评估，排除不靠谱的（如Intel Mac跑不了的Modly），只融能落地的"
  - "老板说『不知道密码』的手机号账号：引导在App内重置密码，或启动二维码扫码登录"
  - "账号资料完善（头像/简介/背景图）小红书网页版MCP不支持，需用户在App端手动设置"
  - "变现导向内容要轮换方向，每天1条，不刷屏"
  - "publish_content调用urllib总返回502，必须用原生socket发送HTTP/1.0请求绕过"
  - "发布操作耗时30-60秒，搜索/评论操作15-30秒，超时必须设足够大"
tags: [小红书, 获客, 内容营销, 自动化, OPC]
---

# OPC Growth × 小红书自动化融合Skill

融合了方糖OPC Growth的获客方法论 + xiaohongshu-mcp的工具能力，实现从选题→创作→发布→引流→成交的自动化闭环。

## 触发场景

- 老板说"搞个小号发小红书"
- 老板说"你不是在吹牛吧"（意思是：研究一下X推文里的工具能不能真用）
- 老板连续发多条X推文链接说"融合到现有体系搞钱" → 逐个评估 → 找能落地的工具 → 融进Skill
- 老板说"你全权处理，我只看看内容" → 登录账号 → 每日出内容给老板审核 → 审核通过发布
- 老板发来账号说"不知道密码" → 让老板在App设置密码，或引导扫码登录
- EPC项目需要线上获客
- 台球俱乐部需要引流到店
- 想做一个副业小红书账号
- 老板在笔记本上问小红书的事但笔记本上的Jarvis不知道

## 工作流

### 阶段1：赛道定位（OPC Strategy方法）

用方糖的三维度评分：
- **需求刚性** (35%)：用户是否已经为这个问题花钱/花时间/承担损失
- **技术成熟度** (30%)：现有AI是否能稳定完成70%以上交付
- **变现清晰度** (35%)：30天内是否能找到决策人并收第一笔钱

总分≥80 → 进入7天验证，否则换赛道

### 阶段2：7天付费验证

| 天数 | 动作 | 产出 |
|------|------|------|
| Day 1-2 | web_search搜索赛道热点话题，确定10个选题 | 选题清单 |
| Day 3-4 | 用AI生成10条笔记内容（图文或视频） | 内容草稿 |
| Day 5-7 | 用xiaohongshu-mcp发布+监测互动数据 | 发布记录+数据复盘 |

### 阶段3：内容获取（小红书MCP）

实际注册的13个MCP工具（HTTP协议，端口18060）：

1. **内容发布**
   - `publish_content` — 发布图文笔记（参数：title, content, tags, images[], is_original, schedule_at, visibility）
   - `publish_with_video` — 发布视频笔记（参数：title, content, tags, video(本地路径), is_original）

2. **互动运营**
   - `search_feeds` — 搜索内容（参数：keyword, filters）
   - `get_feed_detail` — 获取笔记详情（参数：feed_id, xsec_token, load_all_comments）
   - `post_comment_to_feed` — 发表评论（参数：feed_id, content, xsec_token）
   - `reply_comment_in_feed` — 回复评论（参数：feed_id, comment_id, user_id, content）
   - `like_feed` — 点赞/取消点赞（参数：feed_id, xsec_token, unlike）
   - `favorite_feed` — 收藏/取消收藏（参数：feed_id, xsec_token, unfavorite）

3. **数据与账号**
   - `list_feeds` — 获取首页推荐列表
   - `check_login_status` — 检查登录状态
   - `get_login_qrcode` — 获取登录二维码(Base64图片)
   - `delete_cookies` — 删除cookies，重置登录
   - `user_profile` — 获取用户主页信息（参数：user_id, xsec_token）

⚠️ 调用工具前需先通过 initialize 请求获取 Mcp-Session-Id

### 阶段4：私域转化（OPC方式）

首单成交脚本：
1. 确认问题：最想解决的是什么
2. 量化损失：每周浪费多少时间/钱
3. 展示相似案例：先用小方案验证
4. 给三档报价：低价试点→标准交付→深度定制
5. 设置下一步：今天确认→明天给方案→付款进群

### 阶段5：标准化交付SOP

1. 交付时附使用说明，不只丢文件
2. 3-7天后问是否达成目标，主动修复
3. 14天后发额外洞察或优化建议
4. 30天后给续费/升级/转介绍方案

### 阶段6：复盘与优化

每7天复盘：
- 发布了多少条笔记
- 获赞/收藏/涨粉数据
- 私信咨询数量
- 转化成交金额
- 下一个7天计划

## Cron自动化任务示例

### 每日内容发布

```yaml
# 每天早上10点自动发布一条小红书笔记
cron:
  schedule: "0 10 * * *"
  prompt: "用xiaohongshu-mcp写一条关于[主题]的小红书图文笔记并发布"
  skills: [opc-growth-xiaohongshu-fusion]
```

### 每周数据复盘

```yaml
# 每周一早上9点复盘小红书数据
cron:
  schedule: "0 9 * * 1"
  prompt: "复盘最近7天的小红书账号运营数据，给出优化建议"
  skills: [opc-growth-xiaohongshu-fusion]
```

## 登录与账号管理

xiaohongshu-mcp 支持多种登录方式，需要根据账号类型选择：

### 方式1：QR码扫码登录（最推荐）
MCP服务自带 `xiaohongshu-login` 工具，会打开Chrome浏览器显示二维码：
```bash
# 启动二维码登录界面，用手机小红书App扫
/Users/mac/xiaohongshu-mcp/xiaohongshu-login-darwin-amd64

# 可选指定浏览器路径
/Users/mac/xiaohongshu-mcp/xiaohongshu-login-darwin-amd64 \
  -bin "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# 扫码成功后Cookie保存到data/目录
# 重启MCP服务使Cookie生效
launchctl kickstart gui/501/com.xiaohongshu.mcp
```
⚠️ 注意：`get_login_qrcode` MCP工具会尝试打开浏览器窗口，如果用headless/无界面环境会卡死。这种情况下用CLI的 `xiaohongshu-login` 工具代替。

### 方式2：密码找回（手机号注册忘记密码）
如果用户用手机号注册但忘了密码：
1. 告知用户：打开小红书App → 设置 → 账号与安全 → 重置密码
2. 用户设好密码后发过来
3. 用手机号+密码+MCP服务登录

### 方式3：全权委托模式（老板最常用）
老板说"你全权处理，我只看看内容"时的运营流程：
1. 老板把账号密码/验证码发过来
2. 我登录成功后开始产出内容
3. **内容发布前先在群里给老板过目** — 发草稿+发布计划
4. 老板说OK就发，说"懒得看你自己决定"就直接发
5. 每周一给数据复盘报告（涨粉/赞藏/私信咨询/转化）
6. 登录凭证安全处理：不存外部系统、不共享、用完即弃

### 日常内容生产流程（全权委托模式）
1. 每天或每周用web_search搜索AI工具/行业热点选题
2. 用AI生成图文笔记（标题+正文+图片）
3. 在群里发草稿：笔记标题+摘要+配图预览
4. 老板反馈 → 修改 → 发布 / 或老板说OK → 直接发布
5. 定期监测互动数据并汇报

### 已知坑
- HTTP MCP需先初始化session才能调用tools/list
- 首次使用需用login工具生成Cookie
- xiaohongshu-mcp是Intel Mac原生Go二进制，不是Docker
- 端口18060，launchd自拉起
- **🔥 urllib.request 发布返回502**: Python的 `urllib.request.urlopen()` 调用 `publish_content` 总返回502（服务端实际完成发布），需用原生socket建连发送HTTP/1.0请求替代。详见 [`references/cron-config.md`] 中"Python发布脚本（原生Socket版）"
- **`Accept`头要求**: MCP的Gin框架拒绝没有 `Accept: application/json` 或 `text/event-stream` 的请求
- **发布超时30-60秒**: `publish_content` 需要30-60秒完成（上传图片+小红书审核），`curl --max-time` 和 Python timeout 都必须设够大
- **搜索/评论操作也需15-30秒**: 使用浏览器自动化，非即时响应
- **XHS_PROXY代理**: launchd plist 中配置了 `XHS_PROXY=http://127.0.0.1:6478`（此端口有 `FEB` 等进程连接），MCP的渲染和请求通过此代理

## 成本控制（OPC原则）

| 阶段 | 月收入 | 月预算 | 建议 |
|------|--------|--------|------|
| 验证期 | <¥5000 | ¥0-500 | 用免费工具，不买付费账号 |
| 稳定期 | ¥5000-20000 | ¥500-2000 | 配AI会员+小红书投放 |
| 增长期 | >¥20000 | ¥2000+ | 多账号矩阵+自动化+精准投放 |

## 常用命令

```bash
# 查看小红书MCP是否在线
curl -s http://localhost:18060/mcp

# 触发内容创作+发布流程
# 在Hermes中说：帮我写一条关于[主题]的小红书笔记并发布
```

## 配套工具

| 工具 | 用途 |
|------|------|
| xiaohongshu-mcp (MCP Server) | 小红书自动化操作 |
| web_search | 热点话题检索、选题挖掘 |
| Obsidian Vault | 素材库和笔记管理 |
- 顾比交易大脑 | 股市方向的分析内容，可转化为小红书财经笔记

## 参考文件
- [setup-details.md](references/setup-details.md) — 实操记录、MCP调用方式、登录流程
- [cron-config.md](references/cron-config.md) — 每日发布cron配置、内容轮换方案、发布脚本模板
- [publish_note.py](scripts/publish_note.py) — 原生Socket发布脚本（解决urllib 502问题）
