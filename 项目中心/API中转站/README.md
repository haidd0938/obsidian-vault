# API中转站 实操全方案

## 当前状态（2026-05-27）

### 已完成的

- [x] One API Docker 运行中，端口 3001
- [x] 7个渠道已配置（SiliconFlow / DeepSeek / OpenRouter / apikey.fun / Hyperbolic / NVIDIA / Ollama）
- [x] 3个已有 Token（Hermes主力 / 分享令牌-朋友 / 测试令牌）
- [x] 利润核算脚本：`~/.hermes/scripts/profit-tracker.py`
- [x] 落地页 HTML：`~/.hermes/web-ui-api-landing/index.html`
- [x] 引流文章：`~/东盛工作/API中转站/引流文章.md`

### 已上线

- [x] One API 管理后台密码已改为：**oneAPI8836**
- [x] 操作教程已保存：`项目中心/API中转站/实施操作教程.md`
- [x] Tunnel 启动脚本：`~/.hermes/scripts/start-tunnel.sh`

### Cloudflare Tunnel（需你自己执行）

执行一次：

```bash
bash ~/.hermes/scripts/start-tunnel.sh
```

看到 `https://xxx.trycloudflare.com` 就是公网地址。

**2. 创建用户账号**

在 One API 后台创建 5 个定价层级的用户：

| 层级 | 用户名 | 初始额度 |
|------|--------|---------|
| 免费尝鲜 | trial | 50元 |
| 入门版 29元 | basic | 29元 |
| 标准版 99元 | standard | 99元 |
| 专业版 299元 | pro | 299元 |
| 企业版 999元 | enterprise | 999元 |

**3. 设置价格倍率**

在 One API 运营设置里设置模型价格倍率：
- DeepSeek-V4-Flash -> 倍率 3.0（进货1元 -> 零售3元）
- DeepSeek-V3.2 -> 倍率 4.0（进货0.5元 -> 零售2元）
- DeepSeek-V4-Pro -> 倍率 2.5（进货4元 -> 零售10元）
- Qwen3.5-235B -> 倍率 3.0（进货2元 -> 零售6元）

---

## 利润核算系统

脚本位置：`~/.hermes/scripts/profit-tracker.py`

用法：
```bash
python3 ~/.hermes/scripts/profit-tracker.py          # 7天看板
python3 ~/.hermes/scripts/profit-tracker.py --daily   # 日报
python3 ~/.hermes/scripts/profit-tracker.py --model-costs  # 月度分析
```

输出内容：
- 整体概况（调用数、Token数、成本、收入、毛利、毛利率）
- 按模型分析（每个模型的利润贡献）
- 按渠道分析（各个进货渠道的成本）
- 用户消费排行

建议每天跑一次。

---

## 定价逻辑

进货价（SiliconFlow） -> One API -> 零售价
    DeepSeek-V4-Flash: 1元/百万 -> 倍率3.0 -> 3元/百万
    DeepSeek-V3.2: 0.5元/百万 -> 倍率4.0 -> 2元/百万
    DeepSeek-V4-Pro: 4元/百万 -> 倍率2.5 -> 10元/百万
    Qwen3.5-235B: 2元/百万 -> 倍率3.0 -> 6元/百万

毛利率约60%-75%。

---

## 用户如何接入？

用户用 OpenAI SDK，改一行代码：

```python
from openai import OpenAI
client = OpenAI(
    api_key="sk-xxx",
    base_url="https://你的域名/v1"
)
```

兼容所有 OpenAI SDK 工具：Cursor、Continue.dev、Open WebUI、NextChat、LobeChat 等。

---

## 拉客渠道

| 渠道 | 方式 | 优先级 |
|------|------|--------|
| Telegram AI 群 | 分享引流文章+直接推广 | 高 |
| 知乎 | 发技术教程帖引流 | 中 |
| GitHub 开源项目 | README 提到支持自建 API | 中 |
| Upwork/Fiverr | 接 Hermes 部署单时附送1个月 | 低 |
| 邀请返佣 | SiliconFlow 邀请链接 | 持续 |

---

## 预期收益

| 用户数 | 月毛利 |
|--------|--------|
| 10个 | 6000元 |
| 20个 | 12000元 |
| 50个 | 30000元 |
| 100个 | 60000元 |

启动成本：100元（SiliconFlow 预充值）
