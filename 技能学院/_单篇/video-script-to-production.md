# 🎬 短视频全自动产线

> 从创意到成品，一键发TG

**产线流程**:
1. 创意/脚本写作
2. Pillow画图（不依赖drawtext）
3. Edge TTS配音
4. FFmpeg合成视频
5. 自动发Telegram

**定时任务**: 每天7:00 cron → v3.0合成器 → 发TG

**变体**:
- EPC建筑行业版
- 鑫球汇台球俱乐部版

**技术栈**: Python + Pillow + Edge TTS + FFmpeg
