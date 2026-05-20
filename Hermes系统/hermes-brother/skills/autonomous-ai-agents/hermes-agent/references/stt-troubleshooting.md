# STT (语音转文字) 排错参考

## 该用户Mac上的配置 (2026-05-08)

- `faster-whisper` 已安装 (`pip install faster-whisper` → 自动依赖)
- STT provider 从 `nvidia-nim` 切换到 `local` 后正常工作
- 切换命令: `hermes config set stt.provider local`
- 切换后需要重启网关: `hermes gateway restart`

## 验证STT是否工作

1. 检查配置: `grep -A5 "stt:" ~/.hermes/config.yaml`
2. 检查faster-whisper: `python3 -c "import faster_whisper; print(faster_whisper.__version__)"`
3. 在Telegram上发一条语音消息 — 如果系统提示"can't listen"说明STT未生效

## 用户环境

- 系统: macOS (Intel MacBook Pro)
- local model: `base` (默认，够用且Intel Mac能跑)
- 网关: 走Telegram platform
