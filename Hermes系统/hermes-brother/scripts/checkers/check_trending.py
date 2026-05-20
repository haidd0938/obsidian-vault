#!/usr/bin/env python3
"""检查今日GitHub Trending监控是否已产出"""
import os
from datetime import datetime

desktop = os.path.expanduser("~/Desktop")
today = datetime.now().strftime("%Y%m%d")

try:
    files = os.listdir(desktop)
    today_files = [f for f in files if "GitHub副业监控" in f and today in f]
    if today_files:
        print("HAS_OUTPUT=true")
        for f in today_files:
            print(f"产出: {f}")
    else:
        print("HAS_OUTPUT=false")
        print(f"桌面没有含 {today} 的GitHub监控文件")
except Exception as e:
    print("HAS_OUTPUT=false")
    print(f"检查出错: {e}")
