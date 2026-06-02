https://work.yibiao.pro/login

**易标投标工具箱 / OpenBidKit_Yibiao**

这个比较猛——Electron + React + TypeScript 桌面板，有官网 [yibiao.pro](http://yibiao.pro/) 在线体验，AGPL-3.0 开源。

核心卖点：

- AI 写标书（技术标/商务标），亲测 20 万字用 DeepSeek V4 只要 0.8-1 元
- 支持 OpenAI like API 模式的任何模型（已适配 DeepSeek、龙猫、火山方舟，也支持 Ollama 本地模型）
- 企业知识库管理（沉淀历史案例）
- 标书查重 + 废标项检查
- 图文生成（Mermaid 图表转 Word）
- 后台任务可恢复（生成到一半切页面不丢进度）
- 完全本地桌面工作区，Windows/macOS 客户端

**对你来说**：这个比你现有的法务中心和 bidding-qualification-packaging 多了一个"整套桌面客户端"的体验。不过功能上有重叠：

- 你的法务中心已经做合同审查/风险提示
- 你的资格预审/报名资料也已经有一套流程

**结论：**

- ProposalLLM 可以忽略（太老太简陋）
- OpenBidKit 值得关注——它是一个完整的标书生成客户端，集成了知识库、查重、废标检查等功能。但它是独立桌面 App，不是 skill，不好直接集成到你现有一键流程里。可以当参考看它的标书生成思路和知识库管理设计，看有什么能吸收到你的系统中。

GitHub 链接指向的是 `https://github.com/yibiaoai/yibiao-simple` — 注意这是另外一个仓库 **yibiaoai/yibiao-simple**，不是 FB208/OpenBidKit_Yibiao。官网的"开源版"用的是旧的仓库。

这里面最快的应该是在你自己电脑上通过浏览器手动下载。我直接告诉你链接和下载方式：

**方式1：直接用浏览器下载（推荐）**

你的网络可能比我这边快。在浏览器打开这个 GitHub Releases 页面，直接点 x64 ZIP 下载：
`https://github.com/FB208/OpenBidKit_Yibiao/releases/tag/v2.5.2`

进去后往下翻，找 **Yibiao-2.5.2-mac-x64-package.zip**（201MB），点一下就开始下载了。下载完把 ZIP 解压到 `OpenBidKit_Yibiao-main` 文件夹放到 `/Users/mac/Downloads/` 即可。

**方式2：123云盘（13MB Mac客户端，但版本较旧）**
`https://www.123912.com/s/E4rbVv-4udAh?提取码:qtcA`

**方式3：直接用网页版（最快，不用下载）**
`https://work.yibiao.pro/` — 打开就能用，功能应该跟桌面版差不多。

你想用哪个方式？如果让我继续用 curl 下载的话，我可以开后台慢慢下，但估计要几十分钟。或者你自己手动下载 ZIP 更快。