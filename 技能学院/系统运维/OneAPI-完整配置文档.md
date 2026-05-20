# One API 中转站 — 完整配置与使用文档

> 搭建时间：2026-05-16
> 部署方式：Docker on macOS (Intel)
> 版本：v0.6.11-preview.7

---

## 一、服务信息

| 项目 | 内容 |
|------|------|
| **管理后台** | [http://localhost:3010](http://localhost:3010) |
| **API端点** | `http://localhost:3010/v1` |
| **管理员账号** | `root` |
| **管理员密码** | `oneapi2026` |
| **数据目录** | `~/one-api/data/` (SQLite数据库) |

---

## 二、已配置渠道

### 渠道1：DeepSeek主力 ✅ 已验证通过

| 项目 | 内容 |
|------|------|
| 类型 | OpenAI 兼容 |
| 模型 | `deepseek-chat` (即DeepSeek-V3) |
|  | `deepseek-reasoner` (即DeepSeek-R1) |
| Base URL | `https://api.deepseek.com` |
| 状态 | ✅ 正常 |

> **注意**：API Key 敏感信息，不要在文档中明文存储。后台页面可查看/修改。

### 渠道2：本地Ollama ✅ 已验证通过

| 项目 | 内容 |
|------|------|
| 类型 | Ollama (type=22) |
| 模型 | `qwen2.5:7b`, `qwen3:4b`, `gemma4:e4b` |
| Base URL | `http://host.docker.internal:11434` |
| API Key | `ollama` |
| 状态 | ✅ 正常 |

> Docker容器通过 `host.docker.internal` 访问宿主机上的Ollama服务。

---

## 三、令牌（API Keys）

### 令牌1：测试令牌（自己用）

| 项目 | 内容 |
|------|------|
| 名称 | 测试令牌 |
| 额度 | 100,000,000 (约等于¥100) |
| 过期 | 永不过期 |
| **完整Key** | `1bst6MD2YCxk6pUGC67267E54f864a98859e551a072f36C3` |
| Key前12位 | `1bst6MD2YCxk` |

### 令牌2：分享令牌（给朋友）

| 项目 | 内容 |
|------|------|
| 名称 | 分享令牌-朋友 |
| 额度 | 5,000,000 (约等于¥5) |
| 过期 | 永不过期 |
| **完整Key** | `wCSJU4KD0yDoPDYGCdE51fEe162f450289369723Ac576d93` |
| Key前12位 | `wCSJU4KD0yDo` |

---

## 四、调用方式

### 命令行测试

```bash
# DeepSeek
curl http://localhost:3010/v1/chat/completions \
  -H "Authorization: Bearer 你的令牌" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"你好"}],"stream":false}'

# Ollama 本地模型
curl http://localhost:3010/v1/chat/completions \
  -H "Authorization: Bearer 你的令牌" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:7b","messages":[{"role":"user","content":"你好"}],"stream":false}'
```

### 在第三方工具中使用

任何支持 OpenAI API 的工具（如 ChatGPT-Next-Web, LobeChat, OpenClaw, Cursor 等），只需修改：

```
API端点: http://localhost:3010/v1
API Key:  你的令牌（如上所示）
```

> ⚠️ 注意：如果从其他设备访问，需要将 `localhost` 替换为这台Mac的局域网IP（如 `http://192.168.x.x:3010/v1`）

### 在Hermes Agent中使用

可以在 config.yaml 中添加自定义provider指向 one-api：

```yaml
custom_providers:
  - name: One API 中转
    base_url: http://localhost:3010/v1
    api_key: 1bst6MD2YCxk6pUGC67267E54f864a98859e551a072f36C3
    model: deepseek-chat
    models:
      deepseek-chat:
        context_length: 65536
      deepseek-reasoner:
        context_length: 65536
      qwen2.5:7b:
        context_length: 32768
```

---

## 五、管理后台操作

### 常用操作

1. **查看调用日志** — 侧边栏 → 日志
2. **创建新令牌** — 侧边栏 → 令牌 → 添加新的令牌
3. **查看用量统计** — 侧边栏 → 日志 → 按令牌/用户筛选
4. **修改渠道配置** — 侧边栏 → 渠道 → 点击对应渠道的详情/编辑
5. **添加新渠道**（如OpenAI、Claude等）— 侧边栏 → 渠道 → 添加新的渠道

### 额度说明

- 额度单位是 **系统内部积分**（显示为数字）
- 1次普通对话（deepseek-chat）约消耗 500-2000 额度
- 分享令牌设置了 5,000,000 额度，约等于 ¥5 的用量
- 不够了可以在后台修改额度数值

---

## 六、One API 运维命令

```bash
# 启动
docker start one-api

# 停止
docker stop one-api

# 重启
docker restart one-api

# 查看日志
docker logs one-api --tail 50

# 更新（先备份数据）
cp -r ~/one-api/data ~/one-api/data.bak
docker pull ghcr.io/songquanpeng/one-api:latest
docker stop one-api && docker rm one-api
docker run -d --name one-api -p 3010:3000 -v ~/one-api/data:/data ghcr.io/songquanpeng/one-api:latest
```

---

## 七、后续扩展建议

| 扩展方向 | 操作 |
|---------|------|
| 接入OpenAI | 添加渠道 → OpenAI类型 → 填入你的OpenAI Key |
| 接入Claude | 添加渠道 → Anthropic类型 → 填入Claude Key |
| 开放外网访问 | 用frp/ngrok内网穿透，或部署到香港云服务器 |
| 增加用户注册 | 后台设置 → 开启用户注册（注意安全） |
| 对接计费 | 接入支付宝/微信支付（需开发） |

---

## 八、当前状态总览

```
        用户/客户端
             │
             ▼
    ┌────────────────┐
    │  One API       │ ← 管理后台 http://localhost:3010
    │  (Docker:3010) │
    └───────┬────────┘
            │
    ┌───────┴────────┬───────────┐
    ▼                ▼           ▼
DeepSeek API     Ollama       [未来: OpenAI/Claude]
(云端)           (本地)
```

