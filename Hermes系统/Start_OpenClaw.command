#!/bin/bash
# OpenClaw Gateway 启动脚本

# 1. 进入工作目录
cd "/Users/mac/.openclaw/workspace"

# 2. 打印启动日志到终端（方便你看到是否成功）
echo "正在启动 OpenClaw Gateway..."
echo "当前目录: $(pwd)"

# 3. 执行启动命令 (请确保该命令在你的 PATH 中，或者使用绝对路径)
openclaw gateway start

# 4. 保持窗口开启，这样你可以看到运行结果，不会一闪而过
echo "--------------------------------"
echo "启动指令已发出。如果需要停止，请在终端按下 Ctrl+C。"
echo "按回车键关闭此窗口。"
read
