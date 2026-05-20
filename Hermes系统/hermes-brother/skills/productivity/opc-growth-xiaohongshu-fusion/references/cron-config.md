# 小红书账号每日自动发布 Cron 配置

## 实际运行配置（2026-05-10起）

### Cron任务：AI副业研究所-每日变现内容

- **job_id**: 37dfdd747ac4
- **schedule**: `0 10 * * *`（每天早上10点）
- **skill**: opc-growth-xiaohongshu-fusion
- **enabled_toolsets**: [web, terminal, file, skills]

### 内容轮换方向（每周7天）

| 周几 | 方向 | 示例标题 |
|------|------|----------|
| 周一 | AI工具实测 | "用XX工具3分钟做一张商品图" |
| 周二 | 搞钱案例 | "我靠XX一个月多赚了3000" |
| 周三 | 避坑指南 | "做AI副业千万别踩的5个坑" |
| 周四 | 工具对比 | "5个免费AI写文案工具横评" |
| 周五 | 变现教程 | "用小红书+AI自动发笔记赚佣金" |
| 周六 | 数据干货 | "AI工具号怎么做才能火" |
| 周日 | 复盘总结 | "这一周我用AI赚了多少钱" |

### 笔记格式规范

- **标题**: 数字+痛点+结果，20字内
- **正文**: 口语化、带emoji、引导互动，400-500字
- **结尾**: 必须引导私域或评论互动（如"想学留言'教程'"）
- **标签**: 5个，包含 #AI副业 #AI工具 #搞钱
- **配图**: 用 /Users/mac/xiaohongshu-mcp/data/default_cover.png 或新生成的封面图
- **原创声明**: is_original=true

### 发布脚本模板

```bash
# 获取session ID
SID=$(curl -s -i -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}}' \
  http://localhost:18060/mcp | grep "Mcp-Session-Id" | awk '{print $2}' | tr -d '\r')

# 发布笔记
curl -s --max-time 60 -X POST -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SID" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
      "name":"publish_content",
      "arguments":{
        "title":"标题（20字内）",
        "content":"正文内容",
        "tags":["标签1","标签2","标签3"],
        "images":["/Users/mac/xiaohongshu-mcp/data/default_cover.png"],
        "is_original":true
      }
    }
  }' http://localhost:18060/mcp
```

### 已知陷阱与排查

1. **Session过期**: 长时间不用需要重新 initialize 获取新 Session ID
2. **笔记审核**: 新发笔记有几分钟审核期，审核通过前 get_feed_detail 会返回"笔记不可访问"
3. **xsec_token**: 从搜索结果拿到 xsecToken 后，获取详情时必须在参数中传入，否则报错
4. **get_login_qrcode 卡死**: MCP工具方式会打开浏览器，Headless环境用CLI的 login 工具代替
5. **Cookie持久化**: login工具默认写cookies到 /Users/mac/cookies.json，需手动cp到MCP工作目录
6. **🔥 urllib.request 发布失败 (502 Bad Gateway)**: Python的 `urllib.request.urlopen()` 调用 `publish_content` 时总返回502，但服务端实际正常完成发布。原因是urllib的response流式读取与MCP的Gin框架在长耗时(30-60s)请求上的交互问题。
   - **解决方案**: 用**原生socket建连**发送HTTP/1.0请求，不要用urllib/requests库。见下方"Python发布脚本（原生Socket版）"
   - `curl` 配合 `--max-time 120` 和 `-H "Accept: application/json"` 也能工作
7. **`Accept`头必须包含 `application/json`**: MCP的Gin框架拒绝没有 `Accept: application/json` 或 `text/event-stream` 的请求（返回400 Bad Request）
8. **`--max-time` / 超时必须设够大**: 发布操作耗时30-60秒，搜索/评论加载操作也需15-30秒。短超时会导致502

### Python发布脚本（原生Socket版）

当 `curl` 或 `urllib.request` 返回502而MCP日志显示正常时，用以下脚本绕过：

```python
#!/usr/bin/env python3
import json, socket

# 1. 先初始化获取session
# 或者手动从之前的 initialize 响应中拿到 Mcp-Session-Id
SESSION_ID = "YOUR_SESSION_ID"

# 2. 构造 payload
payload = {
    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
    "params": {
        "name": "publish_content",
        "arguments": {
            "title": "你的标题",
            "content": "正文",
            "tags": ["标签1", "标签2"],
            "images": ["/Users/mac/xiaohongshu-mcp/data/default_cover.png"],
            "is_original": True,
            "visibility": "公开可见"
        }
    }
}
body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

# 3. 原生socket发送HTTP/1.0请求（绕过urllib的502问题）
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(240)
sock.connect(("127.0.0.1", 18060))

request = (
    f"POST /mcp HTTP/1.0\r\n"
    f"Host: localhost:18060\r\n"
    f"Accept: application/json, text/event-stream\r\n"
    f"Content-Type: application/json\r\n"
    f"Mcp-Session-Id: {SESSION_ID}\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"\r\n"
).encode() + body

sock.sendall(request)
response = b""
while True:
    try:
        data = sock.recv(65536)
        if not data: break
        response += data
    except socket.timeout:
        break
sock.close()

# 4. 解析响应
header_end = response.find(b"\r\n\r\n")
raw_body = response[header_end+4:] if header_end >= 0 else response
result = json.loads(raw_body)
print(f"Publish result: {result}")
```
