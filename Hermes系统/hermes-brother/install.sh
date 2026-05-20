#!/bin/bash
# ============================================================
#  贾维斯二弟 — 一键安装脚本
#  用法: bash install.sh
# ============================================================

set -e

echo "=========================================="
echo "  🧠 贾维斯二弟 Hermes Agent 部署脚本"
echo "=========================================="

# --- 检测系统 ---
OS="$(uname)"
if [ "$OS" != "Darwin" ]; then
    echo "❌ 目前仅支持 macOS（检测到 $OS）"
    exit 1
fi

# --- 检查 Hermes 是否已安装 ---
if command -v hermes &> /dev/null; then
    echo "✅ Hermes Agent 已安装: $(hermes --version 2>/dev/null || echo '版本未知')"
else
    echo "❌ 未检测到 Hermes Agent"
    echo "   请先安装: curl -fsSL https://hermes-agent.sh/install | bash"
    echo "   或者手动安装后重新运行此脚本"
    exit 1
fi

# --- 检查 Homebrew ---
if ! command -v brew &> /dev/null; then
    echo "⚠️  Homebrew 未安装，安装依赖中..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# --- 安装依赖 ---
echo ""
echo "📦 安装系统依赖..."
brew install jq sqlcipher ffmpeg 2>/dev/null || true

# --- 备份现有配置 ---
if [ -f ~/.hermes/config.yaml ]; then
    BACKUP_DIR=~/.hermes/backup-$(date +%Y%m%d-%H%M%S)
    mkdir -p "$BACKUP_DIR"
    cp -r ~/.hermes/config.yaml ~/.hermes/SOUL.md ~/.hermes/memories/ "$BACKUP_DIR/" 2>/dev/null || true
    echo "📂 现有配置已备份到: $BACKUP_DIR"
fi

# --- 部署配置 ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo ""
echo "📋 部署核心配置..."

mkdir -p ~/.hermes/memories
mkdir -p ~/.hermes/cron
mkdir -p ~/.hermes/scripts/checkers
mkdir -p ~/.hermes/skills
mkdir -p ~/.hermes/data

# 复制核心配置
if [ -f "$SCRIPT_DIR/config/config.yaml" ]; then
    cp "$SCRIPT_DIR/config/config.yaml" ~/.hermes/config.yaml
    echo "  ✅ config.yaml"
fi

if [ -f "$SCRIPT_DIR/config/SOUL.md" ]; then
    cp "$SCRIPT_DIR/config/SOUL.md" ~/.hermes/SOUL.md
    echo "  ✅ SOUL.md (贾维斯的灵魂)"
fi

if [ -f "$SCRIPT_DIR/config/.env" ]; then
    cp "$SCRIPT_DIR/config/.env" ~/.hermes/.env
    echo "  ✅ .env (环境变量，需要填入API密钥)"
fi

# --- 部署技能 ---
if [ -d "$SCRIPT_DIR/skills" ]; then
    echo ""
    echo "🧩 部署技能..."
    for skill_dir in "$SCRIPT_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            mkdir -p ~/.hermes/skills/"$skill_name"
            cp -r "$skill_dir"/* ~/.hermes/skills/"$skill_name"/ 2>/dev/null || true
            echo "  ✅ 技能: $skill_name"
        fi
    done
fi

# --- 部署脚本 ---
if [ -d "$SCRIPT_DIR/scripts" ]; then
    echo ""
    echo "⚙️  部署检查脚本..."
    for script_file in "$SCRIPT_DIR/scripts"/checkers/*.py; do
        if [ -f "$script_file" ]; then
            cp "$script_file" ~/.hermes/scripts/checkers/
        fi
    done
    echo "  ✅ 检查脚本已部署"
fi

# --- 部署 launchd 自启动 ---
if [ -d "$SCRIPT_DIR/launchd" ]; then
    echo ""
    echo "🚀 配置自启动..."
    for plist in "$SCRIPT_DIR/launchd"/*.plist; do
        if [ -f "$plist" ]; then
            plist_name=$(basename "$plist")
            # 卸载旧版避免冲突
            launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/"$plist_name" 2>/dev/null || true
            cp "$plist" ~/Library/LaunchAgents/"$plist_name"
            launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/"$plist_name" 2>/dev/null || true
            echo "  ✅ 自启动: $plist_name"
        fi
    done
fi

# --- 创建 cron 任务（引导用户手动注册）---
echo ""
echo "⏰ Cron 任务清单（共10个）："
echo "----------------------------------------------"
echo "  1. 07:30 顾比交易大脑每日早报"
echo "  2. 08:00 每日EPC建筑行业热点视频"
echo "  3. 09:00 DeepSeek余额监控"
echo "  4. 09:00 每周一项目进度汇总"
echo "  5. 10:00 AI副业研究所小红书每日内容"
echo "  6. 10:30 鑫球汇台球每日视频（4路线轮换）"
echo "  7. 11:00 甘肃投资项目每日抓取"
echo "  8. 15:30 股票机器人每日收盘复盘"
echo "  9. 22:00 GitHub Trending副业监控"
echo " 10. 00:00 睡前提醒+每日汇总"
echo "----------------------------------------------"
echo "⚠️  首次运行请在 Hermes 中手动添加 cron 任务："
echo "   hermes cron create ... (参考 README.md)"
echo ""

# --- 完成 ---
echo "=========================================="
echo "  ✅ 贾维斯二弟部署完成！"
echo ""
echo "  接下来要做的事："
echo "  1. 编辑 ~/.hermes/.env 填入你的 API 密钥"
echo "  2. 编辑 ~/.hermes/config.yaml 确认 provider 配置"
echo "  3. 在终端运行: hermes 启动"
echo ""
echo "  详细说明见: README.md"
echo "=========================================="
