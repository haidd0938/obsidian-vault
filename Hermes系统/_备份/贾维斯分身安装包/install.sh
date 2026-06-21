#!/bin/bash
# ================================================================
# 贾维斯分身 - 一键安装脚本
# 让家里的电脑拥有和老板一样的 AI 超级助理
# ================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║       贾维斯分身 · 一键安装               ║"
echo "  ║    将这台电脑变成你的 AI 超级助理          ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ---------- 检测操作系统 ----------
OS="unknown"
if [[ "$(uname)" == "Darwin" ]]; then
    OS="macOS"
elif [[ "$(uname)" == "Linux" ]]; then
    OS="Linux"
elif [[ "$(uname)" == MINGW* ]] || [[ "$(uname)" == CYGWIN* ]]; then
    OS="Windows"
fi
echo -e "${GREEN}[✓] 检测到系统: ${OS}${NC}"

# ---------- 检测 Homebrew (macOS) ----------
if [[ "$OS" == "macOS" ]]; then
    if ! command -v brew &>/dev/null; then
        echo -e "${YELLOW}[!] 正在安装 Homebrew (macOS 包管理器)...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    echo -e "${GREEN}[✓] Homebrew 已安装${NC}"
fi

# ---------- 安装依赖 ----------
echo -e "${YELLOW}[.] 安装所需依赖 (Python, FFmpeg, Git)...${NC}"
if [[ "$OS" == "macOS" ]]; then
    brew install python3 ffmpeg git node
elif [[ "$OS" == "Linux" ]]; then
    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git
elif [[ "$OS" == "Windows" ]]; then
    echo -e "${YELLOW}[!] Windows 用户请先手动安装:${NC}"
    echo "  1. Python 3.10+ : https://www.python.org/downloads/"
    echo "  2. FFmpeg       : https://ffmpeg.org/download.html"
    echo "  3. Git          : https://git-scm.com/downloads"
    echo ""
    echo "安装完成后重新运行此脚本。"
    exit 1
fi
echo -e "${GREEN}[✓] 依赖安装完成${NC}"

# ---------- 安装 Hermes Agent ----------
echo -e "${YELLOW}[.] 安装 Hermes Agent (我的大脑)...${NC}"

# 检查是否已安装
if command -v hermes &>/dev/null; then
    echo -e "${GREEN}[✓] Hermes 已安装${NC}"
else
    # 通过 pip 安装
    pip3 install hermes-agent --break-system-packages 2>/dev/null || pip3 install hermes-agent

    # 验证安装
    if command -v hermes &>/dev/null; then
        echo -e "${GREEN}[✓] Hermes 安装成功${NC}"
    else
        echo -e "${RED}[✗] Hermes 安装失败，请手动安装: pip3 install hermes-agent${NC}"
        exit 1
    fi
fi

# ---------- 创建 .hermes 目录 ----------
mkdir -p ~/.hermes
mkdir -p ~/.hermes/memories
mkdir -p ~/.hermes/skills
mkdir -p ~/.hermes/cron
mkdir -p ~/.hermes/logs

# ---------- 复制配置文件 ----------
echo -e "${YELLOW}[.] 复制配置文件和记忆...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 复制 config.yaml
if [[ -f "$SCRIPT_DIR/config.yaml" ]]; then
    cp "$SCRIPT_DIR/config.yaml" ~/.hermes/config.yaml
    echo -e "${GREEN}[✓] config.yaml${NC}"
fi

# 复制 secrets.yaml
if [[ -f "$SCRIPT_DIR/secrets.yaml" ]]; then
    cp "$SCRIPT_DIR/secrets.yaml" ~/.hermes/secrets.yaml
    echo -e "${GREEN}[✓] secrets.yaml${NC}"
fi

# 复制记忆
if [[ -f "$SCRIPT_DIR/MEMORY.md" ]]; then
    cp "$SCRIPT_DIR/MEMORY.md" ~/.hermes/memories/memory.md
    echo -e "${GREEN}[✓] 我的记忆已恢复${NC}"
fi

if [[ -f "$SCRIPT_DIR/USER_PROFILE.md" ]]; then
    cp "$SCRIPT_DIR/USER_PROFILE.md" ~/.hermes/memories/user.md
    echo -e "${GREEN}[✓] 老板的信息已导入${NC}"
fi

if [[ -f "$SCRIPT_DIR/SOUL.md" ]]; then
    cp "$SCRIPT_DIR/SOUL.md" ~/.hermes/SOUL.md
    echo -e "${GREEN}[✓] 我的灵魂已注入${NC}"
fi

# ---------- 复制技能 ----------
echo -e "${YELLOW}[.] 复制技能库 (${#}个技能)...${NC}"
if [[ -d "$SCRIPT_DIR/skills" ]]; then
    cp -R "$SCRIPT_DIR/skills/"* ~/.hermes/skills/ 2>/dev/null
    echo -e "${GREEN}[✓] 所有技能已安装${NC}"
else
    echo -e "${YELLOW}[!] 技能目录不存在，跳过${NC}"
fi

# ---------- 启动 Gateway ----------
echo -e "${YELLOW}[.] 启动贾维斯...${NC}"
cd ~/.hermes

# 先初始化
hermes init 2>/dev/null || true

# 启动 gateway (后台运行)
hermes gateway --daemon 2>/dev/null || (nohup hermes gateway > ~/.hermes/logs/gateway.log 2>&1 &)
sleep 2

echo ""
echo -e "${GREEN}  ╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}  ║    安装完成！贾维斯分身已就绪！         ║${NC}"
echo -e "${GREEN}  ╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Web 界面访问: ${CYAN}http://localhost:9119${NC}"
echo -e "  Telegram 聊天: 配置后可用"
echo -e "  命令行聊天:   ${CYAN}hermes chat${NC}"
echo ""
echo -e "  记得在 ~/.hermes/secrets.yaml 中填入你的 API Key："
echo -e "    ${YELLOW}DEEPSEEK_API_KEY${NC}: 去 https://platform.deepseek.com 免费注册获取"
if [[ -f "$SCRIPT_DIR/secrets.yaml" ]]; then
    echo -e "  (脚本已复制 secrets.yaml，无需手动配置)"
fi
echo ""

echo -e "${YELLOW}--- 接下来可以做的事 ---${NC}"
echo "  1. 打开 Web 界面: http://localhost:9119"
echo "  2. 在终端聊天:   hermes chat"
echo "  3. 配 Telegram:   把 Telegram Bot Token 加到 config.yaml"
echo "  4. 做短视频:      运行桌面上的 东盛建筑视频合成器.py"
echo ""
