# Windows 10 家庭小弟Hermes安装指南

## 前置条件检查
1. **Python 3.10+**：已安装 ✓
2. **Ollama**：已安装 ✓
3. **Git（可选）**：用于克隆仓库
4. **网络**：能与笔记本互通（同一局域网）

## 方案选择（根据技术难度）

### 方案A：直接安装（推荐先试）
在Windows上直接通过pip安装Hermes，可能遇到路径问题但通常可运行。

### 方案B：WSL 2（最稳定）
在Windows上安装WSL 2（Windows Subsystem for Linux），然后在Linux环境中安装Hermes，完全兼容。

### 方案C：主从架构（最简化）
家里电脑只运行Ollama模型服务，笔记本上的Hermes远程调用，家里电脑不安装完整Hermes。

---

## 方案A：直接安装步骤

### 1. 创建虚拟环境（避免污染系统Python）
```powershell
# 打开PowerShell（管理员权限）
# 创建项目目录
cd ~
mkdir hermes-home
cd hermes-home

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
# 如果PowerShell提示执行策略限制，先运行：
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 安装Hermes
```powershell
pip install hermes-ai
```

### 3. 复制配置文件（从笔记本传输）
将笔记本上的以下文件复制到家里电脑的 `~/.hermes/` 目录：
- `config.yaml`
- `.env`
- `skills/` 目录（可选）

**传输方法**：
- U盘拷贝
- 局域网共享（`\\笔记本IP\共享文件夹`）
- 微信/QQ文件传输

### 4. 修改配置（适应Windows环境）
编辑 `~/.hermes/config.yaml`：
```yaml
# 修改Ollama连接地址（如果笔记本和家里电脑Ollama独立运行）
# 方案1：家里电脑用自己的Ollama（localhost）
providers:
  ollama:
    base_url: "http://localhost:11434"

# 方案2：家里电脑连接笔记本的Ollama（远程调用）
# 假设笔记本IP是 192.168.0.190
providers:
  ollama:
    base_url: "http://192.168.0.190:11434"
```

### 5. 启动Hermes Web UI（使用不同端口）
```powershell
# 在虚拟环境中
hermes web --port 8658
```

### 6. 验证安装
浏览器访问：`http://localhost:8658/#/chat`

---

## 方案B：WSL 2安装（推荐长期使用）

### 1. 启用WSL 2
```powershell
# PowerShell（管理员）
wsl --install
# 安装Ubuntu发行版
wsl --install -d Ubuntu
```

### 2. 在WSL中安装Hermes
```bash
# 在Ubuntu终端中
sudo apt update
sudo apt install python3-pip

pip install hermes-ai
```

### 3. 配置（同方案A）
```bash
mkdir -p ~/.hermes
# 复制配置文件...
```

### 4. 启动
```bash
hermes web --port 8658
```

### 5. 从Windows访问
浏览器访问：`http://localhost:8658/#/chat`

---

## 方案C：简化主从架构（快速启动）

### 家里电脑只运行Ollama服务
```powershell
# 确保Ollama服务已启动并可远程访问
ollama serve
# 修改Ollama配置（允许远程连接）
# 编辑 ~/.ollama/config.json（如不存在则创建）
{
  "host": "0.0.0.0:11434"
}
```

### 笔记本远程调用
修改笔记本上的Hermes配置：
```yaml
# ~/.hermes/config.yaml
providers:
  ollama:
    base_url: "http://家里电脑IP:11434"
```

### 家里电脑运行简单任务接收器（可选）
创建 `task_receiver.py`：
```python
from flask import Flask, request
import subprocess
import json

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data['prompt']
    
    # 调用本地Ollama
    cmd = [
        "curl", "-s", "http://localhost:11434/api/generate",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False
        })
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout) if result.returncode == 0 else {"error": "生成失败"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 问题排查

### 1. `hermes` 命令找不到
- 确保虚拟环境已激活
- 检查Python Scripts目录是否在PATH中：`echo %PATH%`

### 2. 端口冲突
- 修改端口：`hermes web --port 8668`
- 查看占用：`netstat -ano | findstr :8658`

### 3. Ollama连接失败
- 确认Ollama服务运行：`ollama list`
- 防火墙允许端口11434
- 测试连接：`curl http://localhost:11434/api/tags`

### 4. Web UI无法访问
- 检查Hermes是否启动成功
- 尝试 `http://127.0.0.1:8658/#/chat`
- 查看日志：`hermes web --port 8658 --verbose`

---

## 今晚快速启动建议

1. **先尝试方案A**（直接安装），30分钟内看结果。
2. **如果失败，切换到方案C**（简化架构），至少能让笔记本远程调用家里电脑的Ollama。
3. **明天考虑方案B**（WSL 2），一劳永逸解决兼容性问题。

---

## 下一步协作

1. **等你回家后**：
   - 告诉我家里电脑的IP地址（在cmd中运行 `ipconfig`）
   - 告诉我你想尝试哪个方案（A/B/C）

2. **我会提供**：
   - 定制化的安装脚本
   - 配置好的技能文件
   - 测试命令

3. **目标**：
   - 今晚完成家里电脑的Hermes/Ollama部署
   - 实现笔记本向家里电脑派发第一个任务
   - 开始公众号矩阵的内容生成试运行