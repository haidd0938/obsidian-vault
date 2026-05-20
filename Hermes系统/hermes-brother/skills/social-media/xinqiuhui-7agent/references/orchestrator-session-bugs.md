# 7-Agent Orchestrator 调试记录 (2026-05-07)

## 本session发现的Bug

### 1. `--use-sample` 参数逻辑取反
**文件：** `agent_orchestrator.py` 第39行
**症状：** `--use-sample` 模式跑出的数据却是真实的球房名（天水果房的真实名称），`--no-sample` 反而用了虚构数据。
**根因：**
```python
# 错误代码（原版）：
if use_sample:
    cmd.append("--no-sample")  # 逻辑反了！
    
# 修复后：
if not use_sample:
    cmd.append("--no-sample")
```
**注意：** 测试时如果用 `--use-sample` 跑出3家天水果房的数据，说明代码尚未修复。

### 2. Agent4 Filmer 从JSON解析失败
**文件：** `agent4_filmer.py`
**症状：** `json.load()` 尝试解析Markdown格式的诊断报告时抛出异常。
**根因：** orchestrator调用Agent4时传入了 `improvement_report_path`（文件路径），但文件内容是Markdown，不是JSON。
**修复：** Agent4改用 `content = with open(path, 'r') as f: content = f.read()` 读取原始文本，不做JSON解析。

### 3. Agent5 Pitcher 同样的JSON解析问题
**文件：** `agent5_pitcher.py`
**症状/修复：** 同Agent4，改用原始文本读取。

## Agent4~7 数据流

```
Scout JSON → Diagnoser → 诊断报告.md → Builder → 改善方案.json+md
                                                    │
                                       ┌────────────┼────────────┐
                                       ▼            ▼            ▼
                                   Filmer       Pitcher      Checker
                                    (agent4)    (agent5)     (agent6)
                                       │            │            │
                                       ▼            ▼            ▼
                                  视频脚本.md    触达话术.md    质检报告
                                                                │
                                                                ▼
                                                            Mobile
                                                            (agent7)
                                                                │
                                                                ▼
                                                           推送配置.md
```

## 运行命令速查

```bash
# 全流程正向运行（样例数据，所有球房）
cd ~/.hermes/scripts/xinqiuhui-7agent
python3 agent_orchestrator.py --city "天水" --use-sample --run-all

# 限3家快速测试
python3 agent_orchestrator.py --city "天水" --use-sample --run-all --limit 3

# 分步：只跑Agent4
python3 agent_orchestrator.py --city "天水" --use-sample --step 4

# 分步：只跑Agent6+7（依赖前面的产出物存在）
python3 agent_orchestrator.py --city "天水" --use-sample --step 6
python3 agent_orchestrator.py --city "天水" --use-sample --step 7
```
