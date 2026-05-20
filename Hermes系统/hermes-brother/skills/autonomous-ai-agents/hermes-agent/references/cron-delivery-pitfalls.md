# Cron Task Delivery Pitfalls

> Issues and solutions for Hermes cron job delivery when the agent runs in non-interactive (scheduled) mode.

## Context

Cron jobs (managed via `hermes cron` or the `cronjob` tool) execute as **independent, non-interactive sessions**. They do NOT have a persistent "origin" chat or platform session to deliver results back to.

## The Problem

### `deliver=origin` Fails in Cron

When `deliver=origin`, the cron job attempts to send results back to the session that created it. But **cron runs in a new isolated session** — there is no "origin" to send to.

**Error symptom:**
```
"no delivery target resolved for deliver=origin"
```

**Affected scenarios:**
- Tasks created via Web UI (`api_server` platform) then set to cron
- Tasks created via Telegram/CLI but the original session is gone by cron time
- Any cron job with `deliver=origin` and no `wrap_response` infrastructure

### `deliver=local` Saves But Doesn't Notify

`deliver=local` saves the result locally but **does not push it anywhere the user can see** (no Telegram message, no web UI notification).

## Solution: Write Results to File + deliver=local

### Pattern

1. Change `deliver` from `origin` to `local`
2. In the cron prompt, add instructions to write results to a task center folder
3. Create a numbered subdirectory per task (`01-任务名/`, `02-任务名/`)
4. Add a nightly aggregation cron (23:00) that reads all day's result files

### Organization: Task Center Structure

```
📂 ~/Desktop/任务中心/          ← Finder-accessible root
├── 📄 README.md                ← Task overview table
├── 📂 01-顾比早报/              ← 7:30 stock report
├── 📂 02-EPC视频/               ← 8:00 architecture video
├── 📂 03-DeepSeek余额/          ← 9:00 API balance check
├── 📂 04-鑫球汇视频/             ← 10:30 billiard video
├── 📂 05-甘肃项目/              ← 11:00 project crawler
├── 📂 06-股票复盘/              ← 15:30 market close review
├── 📂 07-GitHub监控/            ← 22:00 trending monitor
├── 📂 08-0点提醒/               ← 0:00 bedtime reminder
├── 📂 汇总报告/                 ← 23:00 daily aggregation
└── 📂 toolsets/任务模板/         ← Standard templates
```

**Obsidian sync:** `ln -sfn ~/Desktop/任务中心 ~/Documents/Obsidian\ Vault/任务中心`

### Prompt Template (per-task)

Each cron job's prompt should include a file-write instruction specific to its subdirectory:

```
【产出文件要求】
执行完毕后，将完整结果（Markdown格式）写入：
/Users/mac/Desktop/任务中心/01-顾比早报/$(date +%Y-%m-%d)-早报.md

内容包括：
- 执行状态
- 核心数据/结果
- 建议/操作项
```

### Prompt Writing Rules for Cron

1. **Be explicit about the output file path** — cron sessions have no UI to show results to. The only way the user sees output is via files.
2. **Include a date in the filename** — `$(date +%Y-%m-%d)-任务名.md` so daily runs don't overwrite each other.
3. **Specify the content structure** — the cron session is autonomous; it needs to know what format you expect.
4. **Label sections clearly** — the result file may be read by the user directly or by the 23:00 aggregation task.

### Aggregation Pattern

Create a 23:00 cron job that:
1. Reads all today's result files from the task center directories
2. Aggregates them into one summary
3. Writes combined report to `~/Desktop/任务中心/汇总报告/$(date +%Y-%m-%d)-每日汇总.md`
4. Reads each subdirectory by date pattern: `cat 任务中心/01-顾比早报/$(date +%Y-%m-%d)*.md`

## Cron Config Settings

```yaml
cron:
  wrap_response: true        # Already enabled — wraps cron output
  max_parallel_jobs: null    # No parallel limit
```

`wrap_response: true` is ON by default. Even with it on, `origin` delivery fails in isolated cron sessions.

## User Workflow

After fix: user asks "今天任务情况" and the agent reads the desktop files and reports back.
Or user checks Finder for `~/Desktop/每日任务汇总-*.md` files directly.

## Affected Tasks Pattern

Look for tasks with:
- `deliver: origin` 
- Created from `api_server` (Web UI) source
- Scheduled via cron (non-interactive execution)

Fix checklist:
- [ ] Change `deliver` to `local`
- [ ] Update prompt to include file write step
- [ ] Verify next run completes without delivery errors
- [ ] Show user how to retrieve results
