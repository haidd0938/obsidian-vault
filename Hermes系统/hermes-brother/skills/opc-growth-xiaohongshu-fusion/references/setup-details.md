# 小红书MCP实操记录（2026-05-10）

## 环境信息

- MCP服务：xiaohongshu-mcp v2.0.0 (Go, Intel Mac原生)
- 端口：18060
- 启动方式：launchd自拉起（com.xiaohongshu.mcp）
- 工作目录：/Users/mac/xiaohongshu-mcp/
- 二进制文件：xiaohongshu-mcp-darwin-amd64 (21MB)
- 登录工具：xiaohongshu-login-darwin-amd64 (15MB)
- 代理：XHS_PROXY=http://127.0.0.1:6478

## 账号信息（脱敏）

- 平台：小红书
- 账户名：AI副业研究所
- 注册方式：手机号注册
- 使用者偏好：全权委托运营，只看结果

## MCP协议调用方式

xiaohongshu-mcp 使用 StreamableHTTP 传输协议。

### 1. 初始化会话（获取Session ID）

```bash
curl -s -i -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}}' \
  http://localhost:18060/mcp
```

响应头中包含 `Mcp-Session-Id: XXXXX`，后续所有请求必须携带此Header。

### 2. 列出工具

```bash
SESSION_ID="获取到的Session ID"
curl -s -X POST -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  http://localhost:18060/mcp
```

### 3. 调用工具

```bash
curl -s -X POST -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"publish_content","arguments":{...}}}' \
  http://localhost:18060/mcp
```

## 登录流程（两次尝试经验）

### 尝试1：通过MCP工具 get_login_qrcode（失败）
- 调用后卡死（30秒超时无响应）
- 原因：需要打开浏览器窗口，且需要浏览器支持headless
- 日志显示下载了Chromium到 ~/.cache/rod/browser/

### 尝试2：CLI工具 xiaohongshu-login（成功 ✅）
- 直接运行登录工具会打开Chrome浏览器
- 浏览器弹出小红书登录页，显示二维码
- 用户用手机小红书App扫码
- 扫码后自动生成 cookies.json 保存到工作目录
- 登录成功后重启MCP服务使cookies生效

```bash
# 启动登录（会弹Chrome窗口）
/Users/mac/xiaohongshu-mcp/xiaohongshu-login-darwin-amd64

# 登录成功后重启MCP
launchctl unload /Users/mac/Library/LaunchAgents/com.xiaohongshu.mcp.plist
launchctl load /Users/mac/Library/LaunchAgents/com.xiaohongshu.mcp.plist
```

### 错误处理
- cookies.json 位置：必须在工作目录下（/Users/mac/xiaohongshu-mcp/cookies.json）
- Login工具默认把cookies写到 /Users/mac/cookies.json，需要手动cp
- MCP服务启动时不读cookies，调用check_login_status时才会读
- 如果cookies过期，需要重新登录

## 发布测试结果

- 第一条笔记标题：DeepSeek实测：一个提示词写出3篇爆款
- 标签：#AI工具 #DeepSeek #小红书运营 #AI写作 #副业
- 配图：用PIL本地生成的1000x1000封面图
- 状态：发布完成 ✅

## 注意事项

1. MCP每次调用可能耗时较长（搜索/发布都需要浏览器操作），超时设为60秒
2. 发布API支持本地图片路径和网络图片URL
3. 标题限制20个中文字或英文单词
4. 定时发布支持ISO8601格式
5. 每个session有生命周期，长时间不用会过期
6. 账号是手机号注册，老板不知道密码 → 引导在App内重置密码，或用扫码登录
