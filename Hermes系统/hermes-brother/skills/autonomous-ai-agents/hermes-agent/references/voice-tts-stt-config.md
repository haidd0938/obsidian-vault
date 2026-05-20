# Voice/TTS/STT Configuration Reference

> For the user "老板" (macOS, Asia/Shanghai, Telegram gateway).
> This user communicates primarily via voice on Telegram (driving, on the go).

## Communication Rules (as of 2026-05-08)

| User sends | AI replies with |
|------------|-----------------|
| Voice message | Voice (TTS) |
| Text message | Text |
| User explicitly specifies | Per instruction |

## TTS Configuration

**Fixed provider: Edge TTS** (`zh-CN-XiaoxiaoNeural`, Microsoft Xiaoxiao)
- Free, fast, natural Chinese female voice
- No API key needed
- Config: `hermes config set tts.provider edge`
- Edge TTS voice: configured in `~/.hermes/config.yaml` under `tts.edge.voice`

Other options evaluated and rejected:
- NVIDIA NIM: was default, user found inferior
- ElevenLabs: paid, not needed
- OpenAI TTS: paid
- NeuTTS local: too slow on Intel Mac

## STT (Speech-to-Text) Configuration

**Provider: local** (faster-whisper)
- Model: `base` (runs on Intel Mac, no GPU needed)
- Free, offline, no API key
- Config: `hermes config set stt.provider local`
- Prerequisite: `pip install faster-whisper` (already installed, v1.2.1)
- Previously was `nvidia-nim` — changed to `local` for reliability

## Troubleshooting

### Voice messages not being transcribed
1. Check STT config: `grep -A5 "stt:" ~/.hermes/config.yaml`
2. Verify faster-whisper installed: `python3 -c "import faster_whisper; print(faster_whisper.__version__)"`
3. Gateway restart needed after config change: `hermes gateway restart`
4. If still broken: switch to Groq Whisper (free tier, set `GROQ_API_KEY`)

### TTS not working
1. Check TTS config: `grep -A3 "tts:" ~/.hermes/config.yaml`
2. Test: `hermes text-to-speech "test"`
3. Edge TTS requires internet — if offline, TTS will fail silently
