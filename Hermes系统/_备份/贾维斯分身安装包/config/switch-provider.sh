#!/bin/bash
# ── 智能 Provider 切换脚本 ──────────────────
# 用法: ./switch-provider.sh [nvidia|deepseek|status]
# 不加参数则自动检测：NVIDIA 可用则用 NVIDIA，否则切 DeepSeek
# ─────────────────────────────────────────────

CONFIG="$HOME/.hermes/config.yaml"

# NVIDIA 配置参数
NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1"
NVIDIA_API_KEY="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"
NVIDIA_MODEL="meta/llama-3.1-8b-instruct"
NVIDIA_MAX_CONTEXT="32768"

# DeepSeek 配置参数
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-be5c67e4da59b68e413e66e217654f1f915185bd01eb41d0c4ab78da1d399319}"
DEEPSEEK_MODEL="deepseek-chat"
DEEPSEEK_MAX_CONTEXT="131072"

switch_to_nvidia() {
    echo "🟢 切换到 NVIDIA NIM（免费）..."

    sed -i '' "s/^  provider:.*/  provider: nvidia-nim/" "$CONFIG"
    sed -i '' 's|^  default:.*|  default: '"$NVIDIA_MODEL"'|' "$CONFIG"
    sed -i '' 's|^  base_url:.*|  base_url: '"$NVIDIA_BASE_URL"'|' "$CONFIG"
    sed -i '' "s/^  max_context:.*/  max_context: $NVIDIA_MAX_CONTEXT/" "$CONFIG"

    echo "✅ 已切换至 NVIDIA NIM - $NVIDIA_MODEL"
}

switch_to_deepseek() {
    echo "🔵 切换到 DeepSeek..."

    sed -i '' "s/^  provider:.*/  provider: deepseek/" "$CONFIG"
    sed -i '' "s/^  default:.*/  default: $DEEPSEEK_MODEL/" "$CONFIG"
    sed -i '' 's|^  base_url:.*|  base_url: '"$DEEPSEEK_BASE_URL"'|' "$CONFIG"
    sed -i '' "s/^  max_context:.*/  max_context: $DEEPSEEK_MAX_CONTEXT/" "$CONFIG"

    echo "✅ 已切换至 DeepSeek - $DEEPSEEK_MODEL"
}

check_nvidia() {
    local result
    result=$(curl -s -o /dev/null -w "%{http_code}" \
        "https://integrate.api.nvidia.com/v1/models" \
        -H "Authorization: Bearer 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" \
        --max-time 10 2>/dev/null)

    if [ "$result" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# ── 主逻辑 ──
case "${1:-auto}" in
    nvidia)
        switch_to_nvidia
        ;;
    deepseek)
        switch_to_deepseek
        ;;
    auto)
        echo "🔍 自动检测 Provider..."
        if check_nvidia; then
            switch_to_nvidia
        else
            echo "⚠️  NVIDIA NIM 不可用"
            switch_to_deepseek
        fi
        ;;
    status)
        current_provider=$(grep "^  provider:" "$CONFIG" | head -1 | awk '{print $2}')
        current_model=$(grep "^  default:" "$CONFIG" | head -1 | awk '{print $2}')
        echo "当前 Provider: $current_provider"
        echo "当前模型:     $current_model"
        if check_nvidia; then
            echo "NVIDIA NIM:   ✅ 可用"
        else
            echo "NVIDIA NIM:   ❌ 不可用"
        fi
        echo "DeepSeek余额: $(curl -s https://api.deepseek.com/user/balance -H \"Authorization: Bearer ${DEEPSEEK_API_KEY}\" | grep -o '\"total_balance\":[0-9.]*' | cut -d: -f2) 元"
        ;;
    *)
        echo "用法: $0 {nvidia|deepseek|auto|status}"
        exit 1
        ;;
esac
