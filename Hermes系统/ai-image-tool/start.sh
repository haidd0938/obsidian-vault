#!/bin/bash
# 一键启动 AI 图像生成工具
export SSL_CERT_FILE=/etc/ssl/cert.pem
export REQUESTS_CA_BUNDLE=/etc/ssl/cert.pem
export http_proxy=http://127.0.0.1:6478
export https_proxy=http://127.0.0.1:6478
export HTTP_PROXY=http://127.0.0.1:6478
export HTTPS_PROXY=http://127.0.0.1:6478
source ~/venvs/ai-image/bin/activate
python3 ~/Desktop/ai-image-tool/app.py "$@"
