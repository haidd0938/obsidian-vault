---
name: reminder-setup
title: Setup Timed Reminders for Boss
description: Setup timed reminders for user in Asia/Shanghai timezone
tags: [reminder, cronjob, personal-assistant]
---

# Setup Timed Reminders for Boss

Setup reminders for user addressed as "老板" in Asia/Shanghai timezone.

## Decision: Apple Reminders vs Cron Job

**Apple Reminders** (preferred for personal reminders):
- Syncs to user's iPhone via iCloud
- Use when user says "提醒我XXX", "设个提醒", "提醒事项"
- Requires `remindctl` → check with `which remindctl`
- If not installed: `brew install steipete/tap/remindctl` (set timeout=180)
- If not authorized: `remindctl authorize` (user MUST be at keyboard)
- Create: `remindctl add --title "内容" --due "YYYY-MM-DD HH:mm" --list "提醒事项"`
- List existing: `remindctl list`
- Check today: `remindctl today`

**Cron Job** (for agent/system tasks only):
- Use when user means "让贾维斯到时提醒我" (agent alerts)
- Or for automated reports, system tasks
- Use the cronjob tool with deliver="local"

## Steps (for Apple Reminders)

1. Parse time like "明天早上9点"
2. Calculate exact time in Asia/Shanghai timezone
3. Check if remindctl is installed and authorized (`which remindctl && remindctl status`)
4. Verify the "提醒事项" list exists (`remindctl list`)
5. Create: `remindctl add --title "内容" --due "YYYY-MM-DD HH:mm" --list "提醒事项"`
6. Confirm with `remindctl today` or `remindctl week`

## Example Code

```python
import datetime
from zoneinfo import ZoneInfo

# Timezone
tz = ZoneInfo("Asia/Shanghai")
now = datetime.datetime.now(tz)

# For "明天早上9点"
if now.hour < 9:
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
else:
    target = (now + datetime.timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

iso_time = target.isoformat()  # "2026-04-17T09:00:00+08:00"
```

## ⚠️ 关键：Cron任务输出管理

**不要用 `deliver="origin"`** —— cron运行在独立会话中，没有来源可投递，结果永远到不了用户手里。

改为 `deliver="local"`，并在prompt中加入写入文件逻辑（结果保存到任务中心）：

```python
# ✅ 正确用法
cronjob(
    action="create",
    name="提醒任务",
    prompt="老板，提醒时间到了！记得把响应结果写入 ~/Desktop/任务中心/08-0点提醒/$(date +%Y-%m-%d)-晚安提醒.md",
    schedule=iso_time,
    deliver="local",      # ← 关键：不用origin
    repeat="once"
)
```

> 详见 `hermes/cron-task-output-management` 技能——完整覆盖cron任务结果落地+归档+Obsidian同步方案。