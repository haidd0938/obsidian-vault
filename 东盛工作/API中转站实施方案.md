# API 中转站实施方案（2026-05-27）

## 一、什么是 API 中转站

你在低价渠道进货（SiliconFlow / DeepSeek / OpenRouter 等），加价转售给需要 API 的开发者。
用 One API 做中间层统一管理渠道、令牌、配额、价格。

利润来源：信息差 + 聚合便利 + 技术服务

## 二、当前部署状态

One API v0.6.11-preview.7 已在 Docker 运行

- 管理后台: http://localhost:3001
- 对外入口: https://complications-rehab-postcard-durable.trycloudflare.com
- 管理员: root / oneAPI8836

已有渠道(7条):
1. DeepSeek主力 - deepseek-chat, deepseek-reasoner
2. [空] 
3. SiliconFlow - deepseek-ai/DeepSeek-V4-Flash ★主用
4. apikey.fun - gpt-5.4-mini 等
5. OpenRouter - deepseek-chat 等
6. Hyperbolic - deepseek-chat 等
7. NVIDIA NIM - llama 系列
8. 本地Ollama - qwen2.5:7b 等

已有令牌(3个):
- Hermes主力Token - 无限制配额，你自己用
- 分享令牌-朋友 - 给朋友测试用
- 测试令牌 - 开发测试

## 三、需要你手动完成的事

！！！重要: One API 渠道的 API Key 需要你手动更新！！！
原因：系统安全机制自动隐藏了密钥，我无法读取完整 Key。

操作步骤:
1. 打开 http://localhost:3001
2. 用 root / oneAPI8836 登录
3. 点「渠道」菜单
4. 找 SiliconFlow 那行，点「编辑」
5. 在「鉴权密钥」框里粘贴你的 SiliconFlow API Key
6. 点「提交」
7. 回到渠道列表，点 SiliconFlow 那行的「测试」按钮，确认显示「测试成功」

同样检查:
- DeepSeek主力 渠道 - 如果 DeepSeek 账号已注销，这个渠道失效
- 其他渠道 - 确保 Key 都有效

## 四、定价方案

免费尝鲜套餐 - ¥0
- 每天 100 万 token
- 限 deepseek-ai/DeepSeek-V4-Flash
- 吸引用户试用的钩子

开发者入门 - ¥29/月
- 每月 5000 万 token
- 访问 DeepSeek-V4-Flash / Qwen 系列
- 1个并发限制

标准套餐 - ¥99/月
- 每月 2 亿 token
- 全部模型可访问
- 5个并发限制

专业套餐 - ¥299/月
- 每月 8 亿 token
- 全部模型，优先队列
- 无并发限制

企业定制 - ¥999+/月
- 自定义配额
- 专属渠道
- 技术支持

成本分析（以 DeepSeek-V4-Flash 为例）:
- 进货价: SiliconFlow ¥1/1M token（输入）
- 售价: ¥3/1M token
- 毛利: ¥2/1M token (66%)
- 一个中度开发者: 约 500 万 token/月 → ¥10 毛利

盈亏平衡点: 3个付费用户 (月消耗合计约 6000 万 token)

月收入预期:
- 10个用户: ¥600-800 毛利
- 50个用户: ¥4000-5000 毛利
- 100个用户: ¥9000-12000 毛利

## 五、拉客方案

渠道1: Telegram AI 群（最直接）
- 加国内 AI 相关 TG 群
- 分享实测截图、对比价格表
- 提供免费试用 Token

渠道2: 知乎/掘金/CSDN
- 发技术文章「从零搭建自己的 API 中转站」
- 文章末尾放试用链接
- 引流文章已写好: 东盛工作/API中转站/引流文章.md

渠道3: 你自己的产品 Hermes
- 在 Hermes 教程页放你的中转站入口
- 自然流量转化

渠道4: 朋友推荐
- 分享令牌-朋友 已经配好
- 让他们试用后推广

## 六、利润核算脚本

脚本位置: ~/.hermes/scripts/profit-tracker.py

用法:
- python3 ~/.hermes/scripts/profit-tracker.py dashboard - 查看总看板
- python3 ~/.hermes/scripts/profit-tracker.py daily - 今日统计
- python3 ~/.hermes/scripts/profit-tracker.py monthly - 月度报表

功能:
- 从 One API 日志接口拉取数据
- 计算每个用户的消耗和利润
- 按天/月汇总

## 七、日常运维

启动/停止 One API:
```
docker start one-api
docker stop one-api
docker restart one-api
```

启动/停止隧道:
```
bash ~/.hermes/scripts/start-tunnel.sh
```

查看日志:
```
docker logs one-api --tail 100
docker logs cloudflared-tunnel --tail 50
```

隧道地址会变（免费版特点），每次重启隧道用:
```
docker logs cloudflared-tunnel 2>&1 | grep "trycloudflare.com"
```

## 八、需要你充值吗？

需要。但不是往 One API 充，是往你的上游渠道充值：

1. SiliconFlow - 登录 https://cloud.siliconflow.cn 充值
   - 你已有账号，有邀请链接可拿返佣
   - DeepSeek-V4-Flash 约 ¥0.5-1/1M token

2. DeepSeek - 登录 https://platform.deepseek.com
   - 但之前你说已注销账号，如果还想用需要重新注册

3. One API 本身不需要充值，它只是个中间层

建议先给 SiliconFlow 充 ¥50 试水，足够支撑 5000 万 token 了

## 九、落地页

地址: ~/.hermes/web-ui-api-landing/index.html

已经做好了暗黑风格定价页面。通过隧道可以直接访问。
如需要绑定自定义域名，需要 Cloudflare 账号创建命名隧道。

## 十、问题排查

Q: 用户说连不上
A: 先自己测 http://localhost:3001/v1/models ，再测隧道地址

Q: One API 管理后台打不开
A: docker ps 检查 one-api 容器是否在运行

Q: 渠道测试失败
A: 点「编辑」检查 API Key 和 Base URL 是否正确

Q: 隧道地址变了
A: 免费版 trycloudflare 每次重启都变地址。需要固定地址就注册 Cloudflare 账号做命名隧道
