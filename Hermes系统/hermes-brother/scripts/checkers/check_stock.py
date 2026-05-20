#!/usr/bin/env python3
"""检查今日股票复盘是否已产出"""
import os
from datetime import datetime

robot_dir = os.path.expanduser("~/stock-robot/data")
today = datetime.now().strftime("%Y-%m-%d")

if os.path.isdir(robot_dir):
    files = []
    for root, dirs, filenames in os.walk(robot_dir):
        for f in filenames:
            if today in f and ("复盘" in f or "summary" in f.lower()):
                files.append(os.path.join(root, f))
    if files:
        print("HAS_OUTPUT=true")
        for f in files[:5]:
            print(f"产出: {f}")
    else:
        print("HAS_OUTPUT=false")
        print(f"stock-robot/data 下没有今日复盘文件")
else:
    print("HAS_OUTPUT=false")
    print(f"目录不存在: {robot_dir}")
