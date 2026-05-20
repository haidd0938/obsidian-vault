# TTS Config Troubleshooting

> Common issues and fixes for Hermes TTS (Chinese voice for boss)

## Quick Reference: Voice Settings

| Setting | Correct Value for Boss | Notes |
|---------|----------------------|-------|
| `tts.provider` | `edge` | Free, works offline |
| `tts.edge.voice` | `zh-CN-XiaoxiaoNeural` | Chinese female voice |
| `stt.provider` | `local` | faster-whisper base model |

## Symptom: TTS returns English voice or fails

### 1. Voice reverted to English

**Root cause**: Some config operations (setup wizard, model change, hermes config set) reset `tts.edge.voice` back to the default `en-US-AriaNeural`.

**Fix**:
```bash
# Check current voice
hermes config show | grep voice

# Fix in config.yaml
# Edit ~/.hermes/config.yaml, find this section:
tts:
  provider: edge
  edge:
    voice: zh-CN-XiaoxiaoNeural  # Change from en-US-AriaNeural to this
```

Or patch directly:
```bash
# Using Python
cd ~/.hermes && python3 -c "
import yaml
with open('config.yaml') as f: c = yaml.safe_load(f)
c['tts']['edge']['voice'] = 'zh-CN-XiaoxiaoNeural'
with open('config.yaml', 'w') as f: yaml.dump(c, f, default_flow_style=False, sort_keys=False, width=1000)
"
hermes gateway restart
```

### 2. Edge TTS CLI works but `text_to_speech()` tool fails

**Root cause**: Usually a stale gateway process or config desync. The `text_to_speech()` tool reads config from its running process, not from disk.

**Fix**: Restart gateway → `/restart` or `hermes gateway restart`.

**Bypass** (when tool fails but CLI works):
```bash
edge-tts --text "你的文本" --voice zh-CN-XiaoxiaoNeural -o /tmp/tts.ogg
```
Then send via MEDIA: path.

### 3. TTS server error (429, 503, connection refused)

**Root cause**: Network issues (Edge TTS connects to Microsoft servers). Usually temporary.

**Fix**: Retry after 30 seconds. If persistent, switch to CLI bypass.

## Verification

After fixing, test with:
```bash
# CLI test
edge-tts --text "测试语音" --voice zh-CN-XiaoxiaoNeural --write-media /tmp/test.ogg

# Gateway test - send a voice to boss via Telegram
# The agent will use text_to_speech() tool automatically
```

## Common Pitfalls

- **Don't set `auto_tts: true` in `voice` section** — `auto_tts` under `voice:` controls CLI voice mode, not gateway TTS. Gateway uses the `tts:` section.
- **Gateway restart is required** after config changes — `tts.edge.voice` is read at startup.
- **Don't use ElevenLabs or OpenAI TTS** for Chinese — Edge TTS (Xiaoxiao) has the best free Chinese voice.
