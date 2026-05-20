#!/usr/bin/env python3
"""
小红书MCP笔记发布脚本（原生Socket版）
避免urllib.request返回502 Bad Gateway的问题

用法:
  python3 publish_note.py <session_id> <title> "<content>" [tag1,tag2,...]

环境变量备用:
  SESSION_ID, TITLE, CONTENT, TAGS
"""

import json, socket, sys, os, re

SESSION_ID = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SESSION_ID", "")
TITLE = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("TITLE", "AI副业笔记")
CONTENT = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("CONTENT", "")
TAGS_STR = sys.argv[4] if len(sys.argv) > 4 else os.environ.get("TAGS", "AI副业,AI工具,搞钱")

if not SESSION_ID:
    import urllib.request
    req = urllib.request.Request(
        "http://localhost:18060/mcp",
        data=json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize",
            "params":{"protocolVersion":"2025-06-18","capabilities":{},
                      "clientInfo":{"name":"hermes","version":"1.0"}}}).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as resp:
        h = str(resp.headers)
        m = re.search(r"Mcp-Session-Id:\s*(\S+)", h)
        SESSION_ID = m.group(1).strip() if m else ""
    print(f"Session: {SESSION_ID}")

if not CONTENT:
    print("CONTENT is empty."); sys.exit(1)

TAGS = [t.strip() for t in TAGS_STR.split(",")]
payload = {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{
    "name":"publish_content","arguments":{
        "title":TITLE,"content":CONTENT,"tags":TAGS,
        "images":["/Users/mac/xiaohongshu-mcp/data/default_cover.png"],
        "is_original":True,"visibility":"公开可见"}}}
body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
print(f"Publishing: {TITLE} ({len(CONTENT)} chars)")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(240)
sock.connect(("127.0.0.1", 18060))
req = (f"POST /mcp HTTP/1.0\r\nHost: localhost:18060\r\n"
       f"Accept: application/json, text/event-stream\r\n"
       f"Content-Type: application/json\r\n"
       f"Mcp-Session-Id: {SESSION_ID}\r\n"
       f"Content-Length: {len(body)}\r\n\r\n").encode() + body
sock.sendall(req)
resp = b""
while True:
    try:
        d = sock.recv(65536)
        if not d: break
        resp += d
    except socket.timeout: break
sock.close()

h_end = resp.find(b"\r\n\r\n")
raw = resp[h_end+4:] if h_end >= 0 else resp
try:
    r = json.loads(raw)
    t = r.get("result",{}).get("content",[{}])[0].get("text","")
    if "发布成功" in t or "发布完成" in t:
        print(f"\nSUCCESS: {t[:100]}")
    else:
        print(f"\nResult: {t[:200]}")
except Exception as e:
    print(f"Parse error: {e}\nRaw: {raw[:500]}")
