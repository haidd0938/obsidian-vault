# wx-cli — WeChat 命令行工具

**项目：** [jackwener/wx-cli](https://github.com/jackwener/wx-cli) ⭐ ~1k / Rust
**最新版本：** v0.1.10 (2026-05)

## 核心能力

| 功能 | 命令 | 用途 |
|------|------|------|
| 会话列表 | `wx sessions` | 获取最近聊天 |
| 未读消息 | `wx unread --filter private,group` | 只显示真人/群消息 |
| 全文搜索 | `wx search "关键词"` | 全量聊天记录搜索 |
| 朋友圈 | `wx sns-feed` / `wx sns-search` | 查朋友圈/搜朋友圈 |
| 聊天导出 | `wx export "名称" --format markdown -o chat.md` | 导出为 Markdown/JSON |
| 收藏 | `wx favorites` | 查看微信收藏 |
| 群成员 | `wx members "群名"` | 获取群成员列表 |
| 数据统计 | `wx stats "某人"` | 聊天频率/活跃度 |

## 安装记录 (Intel Mac)

1. **前置：WeChat 签名** — 需要 ad-hoc 签名才能让 wx-cli 读取微信内存数据
2. **安装方式：** 下载 GitHub Release `wx-macos-x86_64` → `chmod +x` → `sudo mv /usr/local/bin/wx`
3. **npm 方式不可行** — `/usr/local/node23/lib/node_modules/` 目录权限 EACCES
4. **install.sh 跳过** — Hermes 安全扫描拦截 curl|bash，需手动审核

## 初始化

```bash
sudo wx init    # 需要微信正在运行，首次初始化需要 sudo 读取微信内存
```

## AI 集成

项目自带了 `CLAUDE.md` 和 `AGENTS.md`，设计上就是给 AI Agent 用的。集成到 Hermes 的方式：
- terminal 工具直接调用 `wx sessions` / `wx search` 等命令
- 输出 YAML 格式，对 AI token 友好
- 可做成 Skill 包装常用查询场景
