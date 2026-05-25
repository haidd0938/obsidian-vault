# md-to-pptx — Markdown 一键转 PPT

## 基本信息
- **管线位置**: ~/.hermes/skills/productivity/powerpoint/scripts/md_to_pptx/
- **依赖**: python-pptx 1.0.2（已安装）
- **可用主题**: 3 套

## 一句话说明
在 Obsidian 里写好 Markdown 笔记，一条命令转成可编辑的 .pptx 文件，省去做 PPT 的时间。

## 可用主题

| 主题名 | 封面色 | 适用场景 |
|--------|--------|----------|
| corporate-blue | 商务蓝渐变 | EPC汇报、路演、商业计划书 |
| forbidden-red | 朱红古建 | **老板最爱** — 投标、传统文化、祠堂、家族文化 |
| tech-dark | 深色科技风 | 技术分享、代码演示、开发者向 |

## 使用方式

### 方式一：跟我说（最省事）
直接说"贾维斯，帮我做一份 XX 项目的 ptt，朱红古建主题"
我给你写好 Markdown，转好 .pptx，放桌面你打开就行。

### 方式二：自己写笔记自己转
1. 在 Obsidian 写好笔记，用 `---` 分隔每张幻灯片
2. 可以用的语法：
   - 表格 → 自动出数据页
   - `# 标题` → 封面
   - `## 目录` + 列表 → 目录页
   - `> 引文` → 引文页
   - ```代码块``` → 代码展示页
   - 最后一张写"谢谢" → 自动结语页
3. 在终端运行：
```bash
cd ~/.hermes/skills/productivity/powerpoint/scripts
PYTHONPATH=. /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
  -m md_to_pptx 你的笔记.md 输出.pptx --theme forbidden-red
```

### 方式三：给大纲我出 Markdown
把你的结构写给我，我给一段可复用的 Markdown，你存到 Obsidian 里随时改。

## Markdown 语法映射

| 写这个... | 变成... | 效果 |
|-----------|---------|------|
| `# 标题` | 封面 | 深色渐变大标题 |
| `## 目录` + 列表 | 目录页 | 带编号的目录 |
| `## 标题` + 正文 | 内容页 | 标题+要点卡片 |
| 表格（有表头） | 数据页 | 表头深色背景 |
| `### A` 列表 + `### B` 列表 | 对比页 | 左右对比 |
| `` ``` `` 代码 | 代码页 | 深色背景代码 |
| `> 引文` | 引文页 | 左竖线引文 |
| 最后一张 | 结语页 | 居中大号字 |

## 验证方法
转出来后双击 .pptx 就能在 Keynote/WPS 里继续编辑。也可以检查内容：
```bash
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m markitdown 输出.pptx
```

## 对老板的价值
1. **投标 ppt** — forbidden-red 朱红古建，适合 EPC 汇报、祠堂文化、传统文化项目
2. **鑫球汇路演** — corporate-blue 商务风，改改直接用
3. **技术分享** — tech-dark 深色风，代码展示效果好
4. **省时间** — 不用从零排版，写好内容直接出

## 备注
- pptx 是真文件，发微信/邮件给别人都能打开编辑
- 暂不支持嵌入图片（后续可扩展）
- 封面可手动微调字号和间距
