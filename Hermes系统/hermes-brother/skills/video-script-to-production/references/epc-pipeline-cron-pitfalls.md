# EPC视频产线 Cron 故障排查记录

## 典型故障：Cron超时（TimeoutError）

```
TimeoutError: Cron job '每日EPC建筑行业热点视频' idle for 1755s (limit 600s)
— last activity: waiting for provider response (streaming)
```

### 排查步骤

1. **检查cron输出日志**
   ```bash
   ls -la ~/.hermes/cron/output/{job_id}/
   ```
   日志文件是 `YYYY-MM-DD_HH-MM-SS.md` 格式，内容包含完整的prompt和执行过程。

2. **检查脚本路径是否正确**
   - Deskop上存在多个相似脚本，路径写错是常见陷阱
   - 桌面上三个易混淆文件：
     - `~/Desktop/东盛建筑视频合成器_v3.py` — ✅ EPC建筑用（v3.0，359行）
     - `~/Desktop/东盛热点视频合成器.py` — ✅ EPC建筑用（v3.5，476行，增强版）
     - `~/Desktop/鑫球汇视频合成器v3.py` — ❌ 台球俱乐部用，完全不同
   - **不要凭名字"猜测"哪个更新** — 看cron prompt里写了哪个就用哪个

3. **检查合成器脚本是否被修改过**
   - `VIDEO_TITLE` 和 `SCENES_TEXTS` 是否已经更新为当天内容
   - 如果脚本里还是旧的文案，cron运行时需要大模型花很多时间理解+思考，容易超时

4. **BGM下载失败不是致命错误**
   - BGM源（raw.githubusercontent.com上的free-bgm）经常返回404
   - 脚本已内置跳过逻辑，不影响视频输出
   - 最终视频仍然有配音，只是没有背景音乐

### 💀 头号故障：cron prompt里脚本路径写错

**这是最隐蔽、最耗时的故障模式。** 桌面上有多条视频产线的脚本，路径极易搞混。

**实际案例（2026-05-01）：** Cron prompt 里写的是 `~/Desktop/鑫球汇视频合成器v3.py`（台球俱乐部的脚本），但老板要求的是一早产出EPC建筑视频。导致cron运行时：
- 执行的台球脚本 → 产出完全不相关的内容
- 然后又因为文案内容与预期不符，主agent反复思考/调整，最终超时600s被杀死

**修复：** 确认cron prompt里 `RUN` 步骤的脚本路径是 **东盛建筑** 的正确路径：
```
# ✅ 正确（EPC建筑用）
python3 ~/Desktop/东盛建筑视频合成器_v3.py

# ❌ 错误（台球俱乐部用，跟建筑完全不搭边）
python3 ~/Desktop/鑫球汇视频合成器v3.py
```

**预防：每次修改cron prompt时，RUN步骤的脚本路径必须跟视频产线一致。** 如果觉得需要核对，先用 `ls -la ~/Desktop/*合成器*` 确认文件名再写。

### 根本原因分析

| 原因 | 表现 | 修复 |
|------|------|------|
| **cron prompt脚本路径写错** | cron执行了错误产线的脚本，产出不相关内容，然后卡死 | 检查cron prompt的RUN步骤路径；用`ls -la ~/Desktop/*合成器*`确认 |
| 中文字符串引号导致SyntaxError | `SyntaxError: invalid syntax`，报错指向文案行 | 用`re.sub(pattern, new_scenes, content, flags=re.DOTALL)`替换整个`SCENES_TEXTS`块，而非修改单行 |
| 脚本文案未更新 | 大模型需要大量token来改写，流式IO慢 | 提前patch好文案再跑cron |
| **Provider响应慢 / 流式输出卡住** | 卡在"waiting for provider response (streaming)"，cron 600s超时被杀 | 用`delegate_task`子代理独立运行，子代理有独立的超时限制；或者手动跑（更快） |
| BGM下载失败（404） | `! BGM下载失败 (HTTP 404)` | 脚本自动跳过，不会影响配音输出。通知用户如需BGM可手动添加 |
| 热点检索耗时过长 | 浏览器搜索+分析占6分钟+，逼近cron 600s限制 | 用delegate_task + toolsets=["browser","web"]并行搜索；控制在4分钟内完成检索 |

### 修复后验证

```bash
# 检查有没有新视频产出
ls -la ~/Desktop/东盛建筑视频/ | grep -i "2026-05"

# 检查视频时长和分辨率
ffprobe -v quiet -print_format json -show_format ~/Desktop/东盛建筑视频/文件名.mp4 | python3 -c "import sys,json; d=json.load(sys.stdin)['format']; print(f'{d[\"duration\"]}s, {d[\"size\"]} bytes, {d[\"bit_rate\"]} bps')"
```

### 预防措施

- cron prompt中脚本路径写好后不要再改
- 每次换话题时，先patch好文案再让cron跑
- 如果cron连续两次超时，直接手动跑（不用等cron下一次触发）
