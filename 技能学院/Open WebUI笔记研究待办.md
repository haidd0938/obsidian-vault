# Open WebUI 笔记研究（待办）

**来源**: Hermes Agent 对话 2026-05-18
**状态**: 🕐 搁置，后续再研究

## 发现

Open WebUI v0.9.5 **没有原生 Obsidian 同步功能**。
- 侧栏"笔记"(Notes)是 Open WebUI 内部 SQLite 笔记系统
- 跟本地 Obsidian Vault (`~/Documents/Obsidian Vault/`) 无关
- 管理面板设置了所有标签（外部连接、扩展功能、文档等），均无 Obsidian 集成选项

## 待方案

后续可选：
- **A**: 脚本定期把 Obsidian 笔记导入 Open WebUI 知识库
- **B**: 用 Obsidian Web Clipper 浏览器剪藏插件
- **C**: 写个 Hermes Agent cron 桥接两边

## 相关引用

https://x.com/XChatScout/status/2055973360870506665?s=20
