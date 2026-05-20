# 🧠 贾维斯二弟 — Hermes 备用部署包

## 这是什么？

这是你的主力 Mac（大哥）的 **Hermes Agent 完全复制版**，放到联想笔记本（二弟）上用。
二弟不断电、有网，和你哥俩互补，你俩谁在外面都不耽误任务运行。

## 包内容

```
hermes-brother/
├── install.sh              ← 🔥 一键安装（双击终端运行）
├── README.md               ← 这个文件
│
├── config/                 ← 核心配置（需要手动改密钥）
│   ├── config.yaml         ← Hermes 完整配置（三道保险已配好）
│   ├── SOUL.md             ← 贾维斯的灵魂
│   ├── .env                ← API密钥模板（必须填！）
│   ├── MEMORY.md           ← 系统记忆（你的设定）
│   └── user.md             ← 用户画像（你的偏好）
│
├── skills/                 ← 34个技能（跟大哥一模一样）
│   ├── stock-robot/        ← 股票量化
│   ├── gansu-project-crawler/ ← 甘肃项目
│   ├── opc-growth-xiaohongshu-fusion/ ← 小红书
│   ├── video-script-to-production/ ← 视频制作
│   └── ...（更多）
│
├── scripts/checkers/       ← 8个检查脚本（防重复执行）
│
├── launchd/                ← （暂无，后面补）
│
└── cron-backup/            ← 10个定时任务清单
    └── cron-tasks.json
```

## 安装步骤（在联想笔记本上操作）

### 第一步：确保 Hermes 已安装

打开终端，跑：

```bash
curl -fsSL https://hermes-agent.sh/install | bash
```

如果提示要装 Homebrew，先 `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

### 第二步：解压包

```bash
# 假设包在 下载 目录
cd ~/Downloads
unzip hermes-brother.zip
cd hermes-brother
```

### 第三步：填入 API 密钥 🔑

用文本编辑器打开 `config/.env`，填入你的密钥：

```bash
# 至少填一个，建议三个都填
OPENROUTER_API_KEY=sk-or-v1-你的key     # 推荐主力
DEEPSEEK_API_KEY=sk-你的key              # 备胎1
NVIDIA_API_KEY=nvapi-你的key             # 备胎2（免费）
```

然后同样编辑 `config/config.yaml`，把里面 `""` 的 API Key 也填上。

### 第四步：一键部署

```bash
bash install.sh
```

### 第五步：启动！

```bash
hermes
```

首次启动会提示输入 web 界面密钥（随便设一个记住它）。

浏览器打开：`http://localhost:8648` 就能用了。

### 第六步：注册定时任务

在 Hermes 对话中，依次创建以下 cron 任务：

```
hermes cron create --name "顾比早报" --schedule "30 7 * * 1-5" --skills stock-robot --prompt "现在是7:30，执行顾比交易大脑早报流程..."
```

（详细的10个任务见 `cron-backup/cron-tasks.json`）

## 三道 API 保险（这张图就是精华）

```
你发消息
    ↓
二弟 (Hermes Agent)
    ↓
provider: deepseek-chat
    ↓ 挂了 ↓
    OpenRouter API  ← 保险一（推荐主用）
    DeepSeek API    ← 保险二（官方直连）
    NVIDIA NIM API  ← 保险三（免费备胎）
    ↓ 全挂了 ↓
    报错通知老板
```

## 注意事项

1. **包内不含你的 API 密钥** — 二弟需要自己的密钥
2. **联想的 API Key 可以用你的，也可以重新注册** — 推荐重新注册，两边独立互不影响
3. **小红书账号** — 如果二弟也要发小红书，需要登录自己的小红书账号
4. **wx-cli** — 本机装了但没初始化成功，二弟需要的话要另外配置
5. **备份** — 建议也配一个飞牛NAS备份，跟大哥的 `/Users/mac/scripts/backup-obsidian.sh` 一样的思路

## 故障排查

- **hermes 命令找不到** → 重新跑安装命令
- **启动报错** → 检查 `~/.hermes/config.yaml` 确认密钥已填
- **API 超时** → 检查网络/代理，OpenRouter 可能需要科学上网
- **技能不生效** → `hermes reload` 重载配置

## 更新

当大哥的技能/配置有更新时，重新跑这个包的安装流程就行。

---

**祝二弟健康成长！🤖**
