#!/usr/bin/env python3
"""检查甘肃投资项目今天是否已有产出"""
import os
from datetime import datetime

output_dir = os.path.expanduser("~/甘肃投资项目")
today = datetime.now().strftime("%Y-%m-%d")
today_dir = os.path.join(output_dir, today)

if os.path.isdir(today_dir):
    files = os.listdir(today_dir)
    if files:
        print("HAS_OUTPUT=true")
        print(f"产出文件: {files}")
    else:
        # 目录存在但为空
        print("HAS_OUTPUT=false")
        print("原因: 输出目录为空")
else:
    print("HAS_OUTPUT=false")
    print(f"原因: 没有今日产出目录 ({today_dir})")
