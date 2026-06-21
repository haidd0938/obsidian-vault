---
name: telegram-bot-dumb-down-diagnosis
title: Telegram Bot Dumb-Down Diagnosis (TG 降智排查)
description: 当 Telegram bot 突然回复变短、改用英文回复、或记忆丢失时的系统化根因排查方法
tags:
  - telegram
  - troubleshooting
  - model-switching
  - channel-prompts
  - session
created: 2026-04-26
version: 1.1
difficulty: advanced
prerequisites:
  - Hermes Agent configured with Telegram
  - Access to ~/.hermes/ directory
  - Access to session files and logs
---

# Telegram Bot Dumb-Down Diagnosis

## When to Use

Use this skill when:
- Telegram bot suddenly starts replying in very short messages (63-118 chars vs normal 300+ chars)
- Bot switches to English responses despite being configured for Chinese (中文)
- Memory appears lost — bot doesn't remember user details
- Bot outputs "I'm not able to provide a response for the given function call" (or similar English fallback)
- This happens AFTER switching to a different model/provider

## Root Cause Taxonomy — The "6-Dimension" Framework

TG 降智通常由以下 **5个维度** 中的一个或多个同时出问题导致：

### Dimension 5 (NEW!): System Prompt 太短/缺少强制指令 — 模型过度工具化

**意外发现**：即使 channel_prompts 配置正确，模型在 TG 上仍可能过度依赖工具调用。

**现象**：用户问纯知识性问题（如"苗族了解吗？"），模型不直接回答，而是：
1. 先调 `search_files("苗族")` — 试图在 memory 目录搜索
2. 失败后调 `clarify` — 反问用户"你问的XX是什么意思？"
3. clarify 在 TG 不可用 → 模型输出英文错误

**根因**：
- SOUL.md + skills 列表构成的 system_prompt 长达 20K+ 字符
- 模型被 29 个工具定义包围，倾向于用工具"完成"任务而非直接回答
- channel_prompts（目标追加到 ephemeral system prompt）可能并未实际被模型读到
- 没有任何指令告诉模型"简单问答直接回答，不要调工具"

**快速验证**：在 session json 文件中搜索 system_prompt 末尾，确认是否有强制中文/行为指令：

```bash
cd ~/.hermes/sessions
python3 -c "
import json
with open('session_2026*.json') as f:  # 最新session
    data = json.load(f)
sp = data.get('system_prompt','')
print(f'Total: {len(sp)} chars')
for kw in ['你必须', '中文回复', '不要调用工具']:
    print(f'{kw}: {\"✓\" if kw in sp else \"✗\"}')
"
```

**根本解决路径（推荐）**：不要试图修复 channel_prompts，直接使用 `agent.system_prompt` ​——这是在本次 70B 降智排查中总结出的最终方案，绕过整个 channel_prompts 注入链路。

使用第4点（直接回答问题不要调工具）是关键——70B 模型看到 29 个工具定义后倾向于为每个问题都调用工具，必须显式禁止。

**兜底方案**（如果不想改 agent.system_prompt）：

在 `config.yaml` 的 `agent.system_prompt` 字段中配置强制指令。这个字段通过 `_load_ephemeral_system_prompt()` 被加载，**一定会**拼接到 system_prompt 末尾（见 gateway/run.py 第 9686-9687 行），可靠性高于 channel_prompts：

```yaml
agent:
  system_prompt: |
    你是一个中文AI助手。
    必须遵守以下规则：
    1. 任何时候都必须用中文（简体）回复。绝不能用英文。
    2. 工具调用出错时，用中文向用户解释并提供解决方案。
    3. 绝对禁止输出「I'm not able to provide...」这种英文。
    4. 能用自身知识直接回答的问题（常识、知识、文化、历史等），直接回答，不要调用工具。
    5. 记住用户叫「老板」，你叫「贾维斯」。
  max_turns: 90
```

**为何 channel_prompts 可能不够可靠**：
- `resolve_channel_prompt()` 从 `platforms.telegram.extra.channel_prompts` 读取，结果通过 `event.channel_prompt` 传递给 `run_agent`
- 但 `combined_ephemeral = context_prompt + channel_prompt + ephemeral_system_prompt`
- 如果 `context_prompt` 太长（20K+），或 `channel_prompt` 被放到最后被截断，模型可能读不到
- `agent.system_prompt` 直接在 AIAgent 构造时传入，位置更稳定

### Dimension 6 (NEW!): Tool Error Cascade — 多个工具连续报错导致模型退化

**实际案例**：TG 对话中出现以下连续报错链：
1. 用户要求"发到群里" → 模型调用 `send_message` 
2. `send_message` 报错：`No home channel set for telegram`（未配置 TELEGRAM_HOME_CHANNEL）
3. 模型转而调用 `clarify` 来问用户频道ID
4. `clarify` 报错：`Clarify tool is not available in this execution context`（TG 上不可用）
5. 模型再调 `text_to_speech` 尝试用语音回复
6. TTS 也可能报错（Edge TTS 间歇性 `No audio was received`）
7. 最终模型输出英文或极短回复

**根因**：
- 单个工具报错不会导致降智，但**连续 3-4 个工具报错**会击穿模型的容错能力
- 模型在工具调用-报错-再尝试-再报错的循环中消耗了推理能力和 token
- 有些工具（如 `clarify`）在某些平台（TG）上完全不可用，但模型不知道
- 最终模型走 fallback 路径：输出英文的系统默认错误提示

**排查重点**：
在 jsonl 文件中找**连续的工具调用链**，特别是 `send_message` → `clarify` → TTS 这种模式：

```bash
cd ~/.hermes/sessions
python3 -c "
import json
with open('20260426_133102_fee3b946.jsonl') as f:
    tool_calls_in_row = 0
    for line in f:
        d = json.loads(line)
        if d.get('role') == 'assistant':
            tc = d.get('tool_calls', [])
            if tc:
                tool_calls_in_row += 1
                print(f'#{tool_calls_in_row}: {tc[0][\"function\"][\"name\"]}()')
            else:
                tool_calls_in_row = 0
"
```

如果看到连续 3+ 工具调用且后面跟着英文/短回复 → 确认是 error cascade。

**修复**：
- 配置 `TELEGRAM_HOME_CHANNEL` 让 `send_message` 能正常工作
- 在 channel_prompts 中明确告知模型：
  - "在 TG 上不要使用 clarify 工具（因为它不可用）"
  - "工具调用失败后，直接用中文向用户解释情况" 
- 或者使用 `agent.system_prompt` 注入兜底指令（见 Fix F）

### Dimension 1: Channel Prompts 配置层级错误 (配置文件结构层面)

**这是最容易踩的坑：config.yaml 中有两个不同位置的 `telegram:` 配置段！**

```yaml
# ❌ 位置A: 顶层 telegram (第~245行) — gateway 不读这里！
telegram:
  channel_prompts:
    default: "你必须用中文回复..."

# ✅ 位置B: platforms.telegram.extra (第~350行) — gateway 实际读这里！
platforms:
  telegram:
    enabled: true
    proxy_url: http://127.0.0.1:6478
    extra:                      # ← 需要手动添加 extra 字段
      channel_prompts:
        default: "你必须用中文回复..."
```

**根因**：`gateway/platforms/base.py` 的 `resolve_channel_prompt()` 函数从 `self.config.extra.get("channel_prompts")` 读取。
- 如果 `channel_prompts` 写在顶层 `telegram:` 下面的 `channel_prompts:`
- 而 `platforms.telegram:` 下面没有 `extra.channel_prompts`
- 则 gateway 读到的永远是个空字典 `{}`
- **channel_prompts 完全没有生效，模型从未收到过"必须用中文"的指令**

**快速验证**：查看 config.yaml 中 `platforms.telegram` 下面是否有 `extra.channel_prompts`：

```bash
grep -A 10 '^  telegram:' ~/.hermes/config.yaml | grep -A 5 'extra:'
```

**⚠️ 常见陷阱：`extra:` 整个章节缺失**
即使知道 channel_prompts 要放在 `platforms.telegram` 下，新手容易写成：
```yaml
platforms:
  telegram:
    enabled: true
    channel_prompts:          # ❌ 错误！直接写在 platforms.telegram 下
      default: "..."
```
缺少 `extra:` 层级。正确的完整结构是：
```yaml
platforms:
  telegram:
    enabled: true
    proxy_url: http://127.0.0.1:6478
    extra:                    # ✅ 必须有这一层
      channel_prompts:
        default: "你必须用中文回复..."
```

**修复**：在 `platforms.telegram:` 下添加 `extra.channel_prompts`（而非修改顶层 `telegram:` 下的配置），同时清理顶层废弃的 `telegram.channel_prompts` 避免混淆。

### Dimension 2: 模型幻觉 Optional 参数值 (工具 schema 层面)

**70B+ 模型会"自作聪明"为 optional 参数虚构值！**

当工具 schema 中有 optional 参数时，强模型倾向于主动填值，即使 description 明确写着"DO NOT specify"。

**案例**：TTS 工具的 `output_path` 参数
- schema 中 `output_path` 是 optional（`"required": ["text"]`，没有 output_path）
- description 写着"DO NOT specify this — the system handles it automatically"
- 但 70B 模型仍然填了 `output_path="/home/user/voice-memos/message.mp3"`（Linux 路径）
- 在 macOS 上 → 崩溃（Errno 45 Operation not supported）
- 模型拿到工具报错 → 输出英文 "I'm not able to provide a response for the given function call"

**核心规律**：模型越强（70B+），越容易主动填充 optional 参数。修改 description 无效——需要从 schema 中**彻底删除**该参数。

**排查方法**：检查工具报错堆栈中的参数值
1. 找 session jsonl 中的 tool call 记录
2. 看模型传了哪些参数值（特别关注路径、URL、文件名）
3. 如果路径在代码库中无硬编码定义 → 模型幻觉
4. 确认该参数在 schema 中是 optional 的

**修复方法**：
1. 从 schema `properties` 中删除该参数定义
2. handler 中硬编码传 `None` 给底层函数
3. 重启 gateway 生效

### Dimension 3: Session 污染 (运行时数据层面)
- 旧的 TG session 文件中记录了大量工具报错历史（如 vision/TTS 错误）
- 新对话启动时，session 历史被注入作为上下文
- 模型看到之前的工具报错 → 倾向输出更谨慎/简短的回复（防御性行为）
- **关键指标**：用终端 python 解析 session jsonl/json 文件，看历史消息中的 tool error 模式
- **特殊陷阱**：gateway 重启后会**自动复用旧的 session ID**（session_20260426_105155*.json 会从旧 jsonl 重建），阻断后用 `rm session_*.json *.jsonl` 清理

### Dimension 4: Provider Config 不一致 (配置层面)
- `model.default`（主模型）和 `custom_providers` 中的同名 provider 配置可能不一致
- 例如：主模型设为 `meta/llama-3.3-70b-instruct`（context_length 131072），但 custom_providers 中 NVIDIA NIM 仍指向 `meta/llama-3.1-8b-instruct`（context_length 32768）
- Hermes 在路由时可能使用 custom_providers 中的旧配置，导致：
  - context_length 被误判（某些模型如 8B 的 context_length < 64K，Hermes 拒绝使用 agent 能力）
  - TG 发图片时调用 vision 工具失败 → 模型回退英文

## Diagnostic Steps

### Step 0: Gather Core Metrics

```bash
# 1. 查看最新的 TG session 文件 — 核心证据源
cd ~/.hermes/sessions
ls -lt session_20260426_*.json | head -5

# 2. 检查 TG 对话的 jsonl 文件 (TG 对话的详细记录)
ls -lt 20260426_*.jsonl | head -5

# 3. 查看 agent.log 中的 TG 对话
grep -a 'TG\\|telegram\\|text_to_speech\\|vision' logs/agent.log | tail -20

# 4. 检查 system_prompt 是否包含强制指令
# 这是快速发现"模型过度工具化"问题的关键步骤
python3 -c "
import json, glob
files = sorted(glob.glob('session_2026*.json'), reverse=True)
if files:
    with open(files[0]) as f:
        data = json.load(f)
    sp = data.get('system_prompt','')
    print(f'System prompt: {len(sp)} chars, {len(data.get(\"tools\",[]))} tools defined')
    for kw in ['你必须', '中文回复', '不要调用工具', 'directly answer']:
        print(f'  {kw}: {\"✓\" if kw in sp else \"✗\"}')
    # 检查模型行为模式 — 是否调用了不必要的工具
    msgs = data.get('messages',[])
    for m in msgs:
        tc = m.get('tool_calls',[])
        if tc:
            print(f'  TOOL CALL: {tc[0][\"function\"][\"name\"]} → args: {str(tc[0][\"function\"][\"arguments\"])[:100]}')
"
```

### Step 0b: 直接测试模型本身 (排除模型问题)

不要假设模型有问题。先直接 API 测试：

```bash
curl -s -X POST "https://integrate.api.nvidia.com/v1/chat/completions" \
  -H "Authorization: Bearer $NVIDIA_NIM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.3-70b-instruct",
    "messages": [{"role": "user", "content": "苗族了解吗？用中文回答。"}],
    "max_tokens": 2048
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'][:300])"
```

如果 curl 测试中文回复正常 → **模型没问题，是 Hermes 配置/系统提示问题**。

### Step 1: 确认模型本身是否正常

不要假设模型有问题。先直接 API 测试：

```bash
# 用 curl 直接调用模型 API 测试中文回复
curl -s -X POST "https://integrate.api.nvidia.com/v1/chat/completions" \
  -H "Authorization: Bearer $NVIDIA_NIM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta/llama-3.3-70b-instruct",
    "messages": [{"role": "user", "content": "用中文回答：你是谁？"}],
    "max_tokens": 4096
  }' | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

如果 curl 测试中文回复正常，说明模型本身 OK。

### Step 2: 分析 TG 对话 Session — 找工具报错

```bash
cd ~/.hermes/sessions

# 方法 A: 看最新 session 中的 tool error 和英文回复
python3 << 'PYEOF'
import json

# 选最新的 session 文件
import glob
files = sorted(glob.glob("session_2024*.json"), reverse=True)
if not files:
    files = sorted(glob.glob("session_2026*.json"), reverse=True)

for fname in files[:1]:
    with open(fname) as f:
        data = json.load(f)
    msgs = data.get('messages',[])
    
    # 找 tool errors
    for i,m in enumerate(msgs):
        role = m.get('role','')
        content = str(m.get('content',''))
        tool_calls = m.get('tool_calls', [])
        
        if role == 'tool' and ('error' in content.lower()):
            print(f"--- TOOL ERROR MSG {i} ---")
            print(f"Content: {content[:300]}")
            print()
        
        # 找英文回复（assistant 回复且内容短）
        if role == 'assistant' and len(content) > 0 and len(content) < 150:
            # 检查是否包含中文字符
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in content)
            if not has_chinese:
                # 找它前面的 user 消息
                for j in range(i-1, max(i-5, -1), -1):
                    if msgs[j].get('role') == 'user':
                        user_msg = str(msgs[j].get('content',''))[:100]
                        break
                print(f"--- ENGLISH REPLY MSG {i} ---")
                print(f"User: {user_msg}")
                print(f"Reply: {content[:200]}")
                print()
PYEOF

# 方法 B: 查看 TG jsonl 对话记录
python3 << 'PYEOF'
import json
with open('20260426_105155_8e2a53f7.jsonl') as f:
    for line in f:
        if 'text_to_speech' in line or 'vision' in line or 'Error' in line:
            print(line[:400])
            print()
PYEOF
```

### Step 3: 检查 config.yaml 配置一致性

关注这三个配置点的关系：

```bash
# 1. 主模型配置
hermes config get model.default
hermes config get model.model

# 2. TG channel_prompts
read_file ~/.hermes/config.yaml | grep -A 10 "telegram:\n  channel_prompts"

# 3. custom_providers 中同名 provider 的配置
read_file ~/.hermes/config.yaml | grep -A 10 -E "^- name: NVIDIA|^- name: DeepSeek"
```

### Step 5 (NEW!): 使用 jsonl 文件快速扫描工具报错链（比 session.json 更直观）

TG 对话的详细记录在 `.jsonl` 文件中，比 session.json 更适合找工具调用模式：

```bash
cd ~/.hermes/sessions
ls -lt 20260426_*.jsonl | head -3   # 找到最新的 jsonl

# 快速扫描工具调用链（看连续调用了哪些工具）
python3 -c "
import json, sys
# 替换为你最新的 jsonl 文件名
with open('20260426_133102_fee3b946.jsonl') as f:
    for i, line in enumerate(f):
        if not line.strip(): continue
        d = json.loads(line)
        role = d.get('role','')
        content = d.get('content','')
        tc = d.get('tool_calls', [])
        
        if role == 'tool' and 'error' in str(content).lower():
            print(f'[LINE {i+1}] TOOL ERROR: {str(content)[:150]}')
        elif tc:
            print(f'[LINE {i+1}] TOOL CALL: {tc[0][\"function\"][\"name\"]} → {str(tc[0][\"function\"][\"arguments\"])[:100]}')
        elif role == 'assistant' and content.strip():
            # 检查英文回复
            has_zh = any(chr(0x4e00) <= c <= chr(0x9fff) for c in content)
            if not has_zh and len(content) < 200:
                print(f'[LINE {i+1}] ENGLISH REPLY: {content[:150]}')
"
```

jsonl 的好处：每行一个完整事件，不需要解析嵌套结构，扫描效率高。

Hermes 对 agent 模式有最低 context_length 要求（通常 64K）。某些模型（如 8B 模型）的 context_length 低于此阈值 → Hermes 在 TG 上不启用 agent 能力。

如果 context_length < 64K 且模型没有上报 context_length，Hermes 会默认一个较低值。

## Fix Strategies

### Fix A: 更新 Provider Config 一致性

确保 `custom_providers` 与 `model.default` 指向相同模型和 context_length：

```yaml
# 错误的配置 — custom_providers 仍指向旧模型
custom_providers:
- name: NVIDIA NIM
  model: meta/llama-3.1-8b-instruct  # ❌ 旧模型
  models:
    meta/llama-3.1-8b-instruct:
      context_length: 32768           # ❌ 低于 64K 阈值

# 正确的配置 — 同步更新
custom_providers:
- name: NVIDIA NIM
  model: meta/llama-3.3-70b-instruct  # ✅ 新模型
  models:
    meta/llama-3.3-70b-instruct:
      context_length: 131072           # ✅ 超过 64K 阈值
```

同时设置 model 级别 context_length：

```yaml
model:
  default: nvidia-nim
  provider: nvidia-nim
  model: meta/llama-3.3-70b-instruct
  max_context: 131072   # 手动设置，避免 context_length 检测问题
  max_tokens: 4096
```

### Fix B: 将 Channel Prompts 放在正确的配置位置

**关键修复**：channel_prompts 必须放在 `platforms.telegram.extra.channel_prompts` 下，而不是顶层 `telegram.channel_prompts`：

```yaml
# 正确的配置位置
platforms:
  telegram:
    enabled: true
    proxy_url: http://127.0.0.1:6478
    extra:
      channel_prompts:
        default: |
          你是一个中文AI助手，名叫贾维斯。必须严格遵守以下规则：
          
          1. 任何时候都必须用中文（简体）回复。绝不能用英文。
          2. 如果工具调用出错（比如图片分析失败、语音合成失败、天气查询失败等），
             你必须用中文向用户解释原因并提出解决方案。
          3. 绝对禁止输出「I'm not able to provide...」这种英文。
          4. 直接用中文回应问题，不说废话。
          5. 记住用户叫「老板」，你叫「贾维斯」。
```

注意清理顶层废弃的「telegram:」配置段，避免今后误改。

### Fix C: 从工具 schema 中彻底删除模型会幻觉的参数

当工具报错堆栈显示某参数值为模型生成的**不合理值**（如 Linux 路径出现在 macOS 上），且非代码硬编码 — 这属于**模型幻觉参数值**。70B+ 模型看到 optional 参数就"自作聪明"往里填值。

**修改 description 无效！必须从 schema 定义中彻底删除该参数：**

```python
# ❌ 修复前 — 模型看到 output_path 就想填值
"properties": {
    "text": { "type": "string" },
    "output_path": {  # ← 就是这个字段惹的祸
        "type": "string",
        "description": "DO NOT specify this..."
    }
},
"required": ["text"]

# ✅ 修复后 — 模型根本没机会传 output_path
"properties": {
    "text": { "type": "string" }
    # output_path 完全删除了
},
"required": ["text"]
```

配套操作：handler 中硬编码传 None：

```python
handler=lambda args, **kw: text_to_speech_tool(
    text=args.get("text", ""),
    output_path=None)  # 不给模型传参的机会，硬编码 None
```

**何时用这个方法**：
- 工具报错中出现不合理的路径、URL、文件名（如 macOS 上的 `/home/user` 路径）
- 代码中搜索不到该路径的硬编码定义
- 模型生成的参数值明显是幻觉/编造
- 该参数是 optional 的（不必须）

### Fix D: 清理旧 Session + 重启 Gateway

旧 session 中的错误历史会污染新对话：

```bash
# 1. 备份有问题的 session
cd ~/.hermes/sessions
mkdir -p ../old_sessions_backup

# 2. 找到并备份 TG session 和 jsonl 文件
cp session_20260426_1*.json ../old_sessions_backup/ 2>/dev/null
cp 20260426_1*.jsonl ../old_sessions_backup/ 2>/dev/null

# 3. 删除有问题的 session 文件和 jsonl 文件
rm -f session_20260426_1*.json 20260426_1*.jsonl

# 4. **关键：清理 sessions.json 索引** — gateway 重启后通过索引重建同名 session
# ⚠️ sessions.json 是 key-value 结构（非列表），需要按 key 删除
python3 << 'PYEOF'
import json
with open('sessions.json') as f:
    data = json.load(f)
# sessions.json 结构: {"agent:main:telegram:dm:1932005111": {...}, ...}
# 找出含有旧 session_id 的条目
keys_to_remove = []
for key, value in data.items():
    sid = value.get('session_id', '')
    if '20260426_133102' in sid or '20260426_132506' in sid:  # 替换为目标 session ID
        keys_to_remove.append(key)

for key in keys_to_remove:
    del data[key]
    print(f"Deleted: {key}")

with open('sessions.json', 'w') as f:
    json.dump(data, f, indent=2)
print(f"Done. Removed {len(keys_to_remove)} entries, remaining: {len(data)}")
PYEOF
```

5. 重启 gateway 让新配置生效
```bash
# macOS launchd
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
sleep 3
```

6. 验证清理结果
```bash
# 确认 session 文件已清理
ls session_*.json 2>/dev/null || echo "✅ No session files (clean)"
ls *.jsonl 2>/dev/null || echo "✅ No jsonl files (clean)"

# 确认 sessions.json 为空或只有非 TG 条目
python3 -c "
import json
with open('sessions.json') as f:
    data = json.load(f)
print(f'Total entries: {len(data)}')
for k, v in data.items():
    print(f'  {k}: {v.get(\"platform\",\"?\")} / {v.get(\"session_id\",\"?\")}')
"

# 确认 gateway 正在运行
ps aux | grep 'hermes.*gateway' | grep -v grep

# 检查 TG 连接状态（重启后的日志）
grep -a 'telegram.*connected\|Channel directory built' ../logs/gateway.log 2>/dev/null | tail -3
```

7. 新消息到来后，验证 session 重建正常（有新 session 文件生成，且 jsonl 中没有旧错误历史）。
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
sleep 1
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
sleep 3
```

5. 验证重启后"Channel directory built"显示 0 targets — 正常！说明会话索引已清空，需要用户发新消息才会重建。

### Fix F (NEW!): 使用 agent.system_prompt 作为兜底的强制指令注入

**场景**：当 channel_prompts 配置正确但模型仍然不听话（英文回复、过度工具化），说明指令没有被模型读到。

**原理**：`agent.system_prompt` 通过 `_load_ephemeral_system_prompt()` → `combined_ephemeral` → `AIAgent(ephemeral_system_prompt=...)` 传递，比 channel_prompts 更可靠。

**配置**：

```yaml
agent:
  system_prompt: |
    你是一个中文AI助手，名叫贾维斯。必须严格遵守以下规则：
    1. 任何时候都必须用中文（简体）回复。绝不能用英文。
    2. 如果工具调用出错，你必须用中文向用户解释原因并提出解决方案。
    3. 绝对禁止输出「I'm not able to provide a response for the given function call」这种英文。
    4. 能用自身知识直接回答的问题（如常识、知识、文化、历史等），直接回答，不要调用任何工具。
    5. 记住用户叫「老板」，你叫「贾维斯」。
  max_turns: 90
```

**注意**：第4点是本次排查中发现的最关键的补充 — 70B 模型在 TG 上看到 29 个工具列表，倾向于为每个问题调用工具，而不是直接回答。需要显式禁止。

**最佳实践**：同时配置 `channel_prompts`（在 `platforms.telegram.extra` 下）和 `agent.system_prompt`。前者是 TG 专有，后者是全局兜底。

macOS launchd 进程如果不设置 HOME 环境变量，Python 的 `Path("~").expanduser()` 可能展开到错误路径：

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>HOME</key>
    <string>/Users/mac</string>  <!-- 必须显式设置 -->
    <key>PATH</key>
    <string>...</string>
</dict>
```

## Verification

1. **模型端验证**：直接 API curl 确认模型本身中文回复正常
2. **配置生效验证**：检查新生成的 session json 文件末尾的 system_prompt，确认 channel_prompt 被正确追加：
   ```bash
   cd ~/.hermes/sessions
   python3 -c "
   import json, glob
   files = sorted(glob.glob('session_2026*.json'), reverse=True)
   with open(files[0]) as f:
       data = json.load(f)
   sp = data.get('system_prompt','')
   # 看最后 500 字符确认 channel_prompt 被注入
   print('=== System Prompt 末尾 500 字符 ===')
   print(sp[-500:])
   print()
   for kw in ['你必须用中文', '中文回复', '不要调用工具', '贾维斯']:
       print(f'  {kw}: {\"✅\" if kw in sp else \"❌\"}')
   "
   ```
   如果末尾没有 channel_prompt 的强制指令 → channel_prompts 配置位置错了或未生效。
3. **TG 对话验证**：在 TG 上发文字消息 + 发图片，确认：
   - 回复用中文
   - 回复长度正常（>200 chars）
   - 记忆正常（记得老板/贾维斯的关系）
4. **Session 验证**：新生成的 session 文件中没有 tool error → 英文回复链

### Dimension 7 (NEW!): Config Reset After Restoring Backup — 备份恢复导致 channel_prompts 丢失

**实际案例**：用户切换模型后发现回复异常，恢复 `config.yaml.save` 备份。但备份文件中的 `platforms.telegram.extra.channel_prompts` 是**空的**（备份时还未配置过），导致所有中文指令丢失。

**触发链条**：
```
恢复 config.yaml.save 备份
    → platforms.telegram 缺失 extra.channel_prompts（空字典 {}）
    → gateway 读到空 channel_prompts
    → 模型从未收到"必须用中文回复"指令
    → 70B 模型看到 29 个工具 → 过度工具化 → 工具报错 → 回退英文
```

**排查方法**：恢复备份后，立即检查 `platforms.telegram` 下是否有 `extra.channel_prompts`：
```bash
grep -A 25 '^  telegram:' ~/.hermes/config.yaml | head -25
```
重点看 extra: 这一级是否存在，且下面有 channel_prompts。

**预防措施**：在 memory 中记录备份的关键特征：
```
config.yaml.save 是 4月25日23:30 备份，不含 extra.channel_prompts
```
恢复备份后必须重新添加 channel_prompts（或从最新 config.yaml 中复制该段）。

## Pitfalls

1. **不要只测试文字消息** — 发图测试 vision 工具链，发语音测试 TTS 工具链
2. **session 污染可能来自更早的记录** — 如果删除后问题复现，检查 session 保留策略（`sessions.retention_days`）
3. **channel_prompts 的生效范围** — 只对正常对话流生效，工具报错时模型走独立 fallback 路径
4. **重启顺序重要** — 先改配置 → 清 session → 再重启 gateway；顺序颠倒会导致新 session 又记录错误
5. **模型 context_length 上报问题** — NVIDIA NIM 上的某些模型（如 8B）不上报 context_length，Hermes 默认值可能过低；手动设置 `model.max_context` 绕过
6. **⚠️ 两个 telelgram: 配置段的致命陷阱** — config.yaml 中顶层约 245 行和 platforms.telegram 约 350 行都有 telegram 相关配置。改错位置 = 改了等于没改。修改前先明确 gateway 代码读的是哪个层级。
7. **description 防不住 70B+ 模型的参数幻觉** — 模型越强越"主动"。看到 optional 参数就会填，不读 description。唯一的修复是删掉该参数。
9. **channel_prompts 不是唯一方案** — 如果配置正确但依旧无效，直接在 `agent.system_prompt` 中写死指令。这不是绕过，而是必要的多重保障。gateway 代码中 `_load_ephemeral_system_prompt()` 的可靠性高于 `resolve_channel_prompt()`。
10. **模型过度工具化是新维度** — 70B+ 模型看到工具列表会倾向于使用它们，即使问题不需要。必须在 system_prompt 中明确告诉它"直接回答"。

## Related Skills

- `telegram-integration-configuration`: Basic TG bot setup
- `systematic-debugging`: General debugging methodology
