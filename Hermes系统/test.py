#!/usr/bin/env python3
print("🎉 Python 测试成功！")
print("Python 版本：", __import__('sys').version)
import requests
try:
    r = requests.get("http://localhost:5678", timeout=2)
    print("✅ n8n 连接状态：", r.status_code)
except:
    print("ℹ️  n8n 未运行（正常）")
