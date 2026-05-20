---
name: reminder-setup
title: Setup Timed Reminders for Boss
description: Setup timed reminders for user in Asia/Shanghai timezone
tags: [reminder, cronjob, personal-assistant]
---

# Setup Timed Reminders for Boss

Setup reminders for user addressed as "老板" in Asia/Shanghai timezone.

## Steps

1. Parse time like "明天早上9点"
2. Calculate exact time in Asia/Shanghai timezone
3. Create cronjob with ISO timestamp
4. Deliver to current Telegram chat ("origin")

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

## Cronjob Creation

```python
# Use cronjob tool
cronjob(
    action="create",
    name="提醒任务",
    prompt="老板，提醒时间到了！",
    schedule=iso_time,
    deliver="origin",
    repeat="once"
)
```