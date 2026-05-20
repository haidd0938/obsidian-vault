#!/usr/bin/env python3
"""DeepSeek余额检查脚本 — 从.env读取API Key查余额
输出: HAS_OUTPUT=true/false + 余额信息
"""
import os, json, subprocess, datetime

STATUS_FILE = os.path.expanduser("~/.hermes/data/deepseek_balance_status.json")
ENV_FILE = os.path.expanduser("~/.hermes/.env")
TODAY = datetime.date.today().isoformat()

# 检查今天是否已有余额记录
if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE) as f:
        data = json.load(f)
    if data.get("date") == TODAY and data.get("balance") is not None:
        print(f"HAS_OUTPUT=true")
        print(f"BALANCE={data['balance']}")
        print(f"CURRENCY={data.get('currency','CNY')}")
        print(f"SOURCE=cached")
        exit(0)

# 从.env读API Key
api_key = ""
if os.path.exists(ENV_FILE):
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith("DEEPSEEK_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip("'\"")
                break

if not api_key:
    print("HAS_OUTPUT=false")
    print("ERROR=API Key not found in .env")
    exit(0)

# 查余额
result = subprocess.run(
    ["curl", "-s", "https://api.deepseek.com/user/balance",
     "-H", f"Authorization: Bearer {api_key}"],
    capture_output=True, text=True, timeout=15
)

if result.returncode != 0:
    print("HAS_OUTPUT=false")
    print("ERROR=curl failed")
    exit(0)

try:
    data = json.loads(result.stdout)
    if "is_available" in data and data["is_available"]:
        balance = data["balance_infos"][0]["total_balance"]
        currency = data["balance_infos"][0]["currency"]
        # 写入状态文件
        status = {
            "date": TODAY,
            "balance": balance,
            "currency": currency,
            "checked_at": datetime.datetime.now().isoformat()
        }
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f)
        print(f"HAS_OUTPUT=true")
        print(f"BALANCE={balance}")
        print(f"CURRENCY={currency}")
        print(f"SOURCE=api")
    else:
        print("HAS_OUTPUT=false")
        print("ERROR=API returned unavailable")
except Exception as e:
    print("HAS_OUTPUT=false")
    print(f"ERROR={e}")
