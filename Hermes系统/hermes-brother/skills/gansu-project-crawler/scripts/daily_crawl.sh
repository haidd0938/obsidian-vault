#!/bin/bash
"""
甘肃省投资项目备案 — 每日自动抓取脚本
=======================================
用法：
  手动执行： ./daily_crawl.sh
  添加到 crontab： 0 8 * * * /path/to/daily_crawl.sh

这个脚本会：
1. 读取 company_config.ini 获取配置
2. 执行 crawl_projects.py 抓取昨天的项目（因为备案通常第二天才显示）
3. 将结果保存到 output/ 目录
4. 如果有匹配项目，输出摘要到 stdout（方便 cron 邮件通知）
"""

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 配置
CRAWL_SCRIPT="$SCRIPT_DIR/crawl_projects.py"
CONFIG_FILE="$PROJECT_DIR/references/company_config.ini"
OUTPUT_DIR="$PROJECT_DIR/output"

# 读取配置（使用简单解析，不依赖外部工具）
if [ -f "$CONFIG_FILE" ]; then
    KEYWORDS=$(grep -A100 '^keywords' "$CONFIG_FILE" | grep -v '^\[' | grep -v '^$' | tr '\n' ',' | sed 's/,,*/,/g' | xargs)
    REGIONS=$(grep '^preferred_regions' "$CONFIG_FILE" | cut -d= -f2 | xargs)
    if [ -z "$REGIONS" ]; then
        REGIONS="天水,陇南"
    fi
else
    KEYWORDS="建筑设计,工程设计,房建,规划,勘察,监理"
    REGIONS="天水,陇南"
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 日期
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)

echo "========================================"
echo "📋 甘肃省投资项目备案 — 每日抓取"
echo "日期：$TODAY"
echo "查询日：$YESTERDAY"
echo "========================================"
echo ""

# 执行抓取（先查昨天，因为备案有延迟）
echo "🔍 正在抓取 $YESTERDAY 的项目..."
python3 "$CRAWL_SCRIPT" \
    --date "$YESTERDAY" \
    --keywords "$KEYWORDS" \
    --regions "$REGIONS" \
    --pages 3 \
    --output both 2>&1 | tee "$OUTPUT_DIR/${YESTERDAY}_report.txt"

# 也查一下今天（如果有数据的话）
echo ""
echo "🔍 正在抓取 $TODAY 的项目..."
python3 "$CRAWL_SCRIPT" \
    --date "$TODAY" \
    --keywords "$KEYWORDS" \
    --regions "$REGIONS" \
    --pages 3 \
    --output json 2>"$OUTPUT_DIR/${TODAY}_data.json" || true

echo ""
echo "✅ 完成！报告已保存到: $OUTPUT_DIR/"
