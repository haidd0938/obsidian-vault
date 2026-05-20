# Tailscale 异地共享 Open WebUI 实施方案

> 2026-05-18 整理
> 目标：让异地的朋友通过 Tailscale 安全地使用你本地的 Open WebUI（localhost:3000）

---

## 一、什么是 Tailscale

Tailscale 是一个基于 WireGuard 的虚拟组网工具。你和朋友各装一个，就像在同一个局域网里一样，不用暴露公网端口。

**优点：**
- ✅ 端到端加密（任何人都无法偷看对话内容）
- ✅ 免费版最多 3 个用户、100 台设备（完全够用）
- ✅ 直连 P2P，速度取决于双方带宽
- ✅ 支持 Mac / Windows / Linux / iOS / Android
- ✅ 装好后一劳永逸

---

## 二、你的操作（Mac 端）

### 步骤 1：安装 Tailscale

```bash
brew install tailscale
```

如果没装 Homebrew，可以去官网下载：https://tailscale.com/download

### 步骤 2：启动并登录

```bash
tailscale up
```

会自动弹出浏览器窗口，选一个账号登录（推荐用你已有的 Google / Apple ID / GitHub），选哪个都行。

登录成功后在终端会看到：
```
Success.
```

### 步骤 3：查看你的虚拟 IP

```bash
tailscale ip -4
```

会输出类似：`100.83.42.151`

**记住这个 IP**，这就是你电脑在网络上的地址。

### 步骤 4：确认 Open WebUI 已监听所有接口

检查 Docker 是否已经允许外部访问：

```bash
docker inspect open-webui --format '{{range $p,$conf := .NetworkSettings.Ports}}{{if $conf}}{{(index $conf 0).HostIp}}:{{$p}} -> {{$conf}}{{end}}{{end}}'
```

如果输出是 `0.0.0.0:3000 -> ...`，就说明可以从外部访问了。

如果不行，重新运行容器允许外部访问（一般不需要）：

```bash
docker stop open-webui
docker rm open-webui
docker run -d -p 0.0.0.0:3000:8080 \
  --name open-webui \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_API_KEY=sk-placeholder \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8642/v1 \
  ghcr.io/open-webui/open-webui:main
```

### 步骤 5：启动后台服务（开机自动）

Tailscale 安装后默认开机自启，你不需要做额外设置。

### 步骤 6：添加朋友到共享网络

打开 Tailscale 管理后台：
https://login.tailscale.com/admin/machines

找到你的 Mac 电脑 → 点击右侧 `...` → **Share** → 输入你朋友的邮箱地址（就是他注册 Tailscale 用的邮箱）→ **发送邀请**

或者更简单的方法：让朋友安装 Tailscale 登录后，告诉他你的邮箱/用户名，让他在 Tailscale 客户端搜索并请求连接。

---

## 三、朋友的操作（Mac / Windows / 手机均可）

### 步骤 1：安装 Tailscale

| 设备 | 方式 |
|------|------|
| **Mac** | `brew install tailscale` 或下载 https://tailscale.com/download-mac |
| **Windows** | https://tailscale.com/download-win |
| **iPhone/Android** | App Store / 应用商店搜 "Tailscale" |
| **Linux** | `curl -fsSL https://tailscale.com/install.sh | sh` |

### 步骤 2：登录

```bash
tailscale up
```

弹浏览器 → 注册一个新账号（用邮箱、Google、Apple 都行，免费的）。

### 步骤 3：等你添加他

你把设备共享给他后，他会收到邮件通知，确认后就能连上了。

### 步骤 4：访问 Open WebUI

打开浏览器，输入你的虚拟 IP + 端口 3000：

```
http://100.83.42.151:3000
```

（把 `100.83.42.151` 替换成你的实际 IP）

### 步骤 5：注册账号

首次访问 Open WebUI 需要注册账号（邮箱密码随便填，本地账号）。之后就可以选择模型开始聊天了。

---

## 四、配置建议（Open WebUI 设置）

### 限制可用模型（防止朋友乱选贵模型）

登录 Open WebUI 后 → 左下角设置 ⚙️ → **管理员设置** → **模型** → 在"允许的模型"列表里只保留：

- `deepseek-chat`（DeepSeek V4 Flash，¥1/百万输入，最便宜）
- `deepseek-ai/DeepSeek-V4-Flash`（硅基流动的备胎，免费额度用）
- 其他随意

这样朋友就选不了高价模型（如 gpt-5.5），防止意外产生高额费用。

### 朋友多的话，可以设置每日限额

在 Open WebUI 设置 → 用户管理里可以给每个用户配置用量限制。

---

## 五、费用预期

朋友使用走的是你的 API 通道，费用如下：

| 模型 | 输入（¥/百万tokens） | 输出（¥/百万tokens） | 一次聊天大约 |
|------|---------------------|---------------------|------------|
| DeepSeek V4 Flash | 1 | 2 | ¥0.01~0.05 |
| 硅基流动 DeepSeek V4 Flash | 约 2-4 | 约 4-8 | ¥0.02~0.10 |

朋友一个月聊几百条，也就几块钱，不用担心。

---

## 六、故障排查

| 问题 | 解决办法 |
|------|---------|
| 朋友访问不了 `http://100.x.x.x:3000` | 确认你电脑的 Tailscale 正常运行：`tailscale status` 显示 online |
| 登录 Open WebUI 被拒 | 重新注册账号，或在 Docker 里清空用户数据：`docker exec open-webui rm /app/backend/data/data.db && docker restart open-webui` |
| 朋友看不到模型列表 | 确认 Open WebUI 的 API Base URL 是 `http://host.docker.internal:8642/v1`，且你的 Hermes Gateway 已重启 |
| 连接速度慢 | Tailscale 会自动尝试直连，如果走中继会慢。等几秒钟自动优化 |

---

## 七、一键完成检查清单

- [ ] 你装好了 Tailscale
- [ ] 你 `tailscale up` 登录成功
- [ ] 你记下了虚拟 IP（`tailscale ip -4`）
- [ ] Open WebUI Docker 端口绑定了 `0.0.0.0`
- [ ] 朋友也装好了 Tailscale 并登录
- [ ] 你在 Tailscale 后台把设备共享给朋友
- [ ] 朋友用 `http://你的IP:3000` 能打开登录页
- [ ] Open WebUI 里设置好了允许的模型列表
