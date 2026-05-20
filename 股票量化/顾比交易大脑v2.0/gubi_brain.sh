#!/bin/bash
# ============================================================
# 顾比交易大脑 — 启动脚本
# 用法:
#   ./gubi_brain.sh           # 完整模式（彩色输出到终端）
#   ./gubi_brain.sh cron      # cron精简模式（纯文本输出到日志）
#   ./gubi_brain.sh deep 002594 比亚迪  # 深度分析单只股票
# ============================================================
set -e
cd "$(dirname "$0")"

MODE="${1:-full}"
shift 2>/dev/null || true

case "$MODE" in
    full)
        echo "🧠 顾比交易大脑 — 完整分析"
        echo "================================"
        python3 brain/trading_brain.py full
        ;;
    cron)
        python3 brain/trading_brain.py cron
        ;;
    deep)
        CODE="${1:-002594}"
        NAME="${2:-比亚迪}"
        echo "🔍 深度分析: $NAME($CODE)"
        python3 brain/trading_brain.py deep "$CODE" "$NAME"
        ;;
    *)
        echo "用法: $0 {full|cron|deep CODE NAME}"
        exit 1
        ;;
esac
