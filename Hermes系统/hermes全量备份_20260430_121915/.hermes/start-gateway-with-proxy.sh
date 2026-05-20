#!/bin/bash
# Start Hermes Gateway with TELEGRAM_PROXY explicitly set
# This bypasses the .env inheritance issue

cd /Users/mac/.hermes

# Source .env explicitly
set -a
source .env
set +a

# Override with explicit proxy
export TELEGRAM_PROXY=http://127.0.0.1:6478
export HERMES_TELEGRAM_DISABLE_FALLBACK_IPS=true
export TELEGRAM_TIMEOUT=30

# Kill any existing gateway
pkill -f "hermes_cli.main gateway" 2>/dev/null || true
sleep 2

# Start gateway
exec python3 -m hermes_cli.main gateway run --replace
