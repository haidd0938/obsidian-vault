# Cron执行失败排查手册

> 用于视频产线cron（EPC 8:00 / 鑫球汇 10:30）没有产出时的系统化排查

## 快速排查流程

### 第1步：确认cron配置
```bash
hermes cron list | grep -E "(EPC|鑫球|视频)"
# 确认 schedule、last_run_at、next_run_at、last_status
```

### 第2步：检查cron session日志
```bash
# 今天有没有cron session文件
ls -lt ~/.hermes/sessions/ | grep "$(date +%Y%m%d)" | grep "cron_"

# 没有输出 → gateway可能挂了，cron scheduler没启动
# 有输出但缺了某个任务 → 那个任务被跳过了
```

### 第3步：检查gateway日志
```bash
# Cron ticker在走吗？
grep "Cron ticker" ~/.hermes/logs/gateway.log | tail -5

# 网络正常吗？（大量httpx.ConnectError = 网络波动）
grep -c "httpx.ConnectError" ~/.hermes/logs/gateway.log

# 看具体的cron调度记录
grep -i "scheduler\|cron" ~/.hermes/logs/agent.log | grep "$(date +%Y-%m-%d)" | head -20
```

### 第4步：检查任务中心产出
```bash
# EPC视频
ls -la ~/Desktop/任务中心/02-EPC视频/ | grep "$(date +%Y-%m-%d)"

# 鑫球汇视频
ls -la ~/Desktop/任务中心/04-鑫球汇视频/ | grep "$(date +%Y-%m-%d)"
```

### 第5步：检查cron jobs.json状态
```bash
python3 -c "
import json
with open('$HOME/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)
for j in jobs:
    if isinstance(j, dict):
        name = j.get('name','?')
        if '视频' in name or 'EPC' in name or '鑫球' in name:
            print(f'{name}: next={j.get(\"next_run_at\")} last={j.get(\"last_run_at\")} status={j.get(\"last_status\")}')
"
```

## 常见失败模式

| 症状 | 根因 | 修复 |
|------|------|------|
| next_run_at是今天但没session | 网络波动导致agent创建跳过 | 手动补跑 |
| next_run_at是今天但status=error | 执行时出错 | 查看gateway.log具体错误 |
| gateway.log有Cron ticker但无调度 | 调度器bug或session创建失败 | 重启gateway |
| 视频产线cron跑了但没产出文件 | prompt缺少写入步骤 | 修prompt加写入逻辑 |
| 鑫球汇cron周六没跑 | 检查排期 `* * * *` 是否含周末 | 确认schedule配置 |

## 补跑命令
```bash
# 手动触发补跑（用同一prompt和配置）
# 方法1：直接运行脚本
cd ~ && python3 ~/Desktop/东盛建筑视频合成器_v3.py

# 方法2：用cron edit --run-now
hermes cron edit <job_id> --deliver local --run-now

# 方法3：在会话中手动执行（当前会话）
# 先确认当前是哪个会话，然后执行prompt中的步骤
```
