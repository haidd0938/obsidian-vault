# cups-web — 网页版打印管理工具

来源: GitHub https://github.com/hanxi/cups-web  
评估日期: 2026-05-25  
⭐: 869  
📝: 把家用 USB 打印机变成随时可访问的网络打印服务  
📋: MIT 许可证  
最新提交: 2026-05-20

## 能装吗

✅ 非常容易。Docker 一键部署或直接下载 macOS 二进制运行。Docker 镜像已预装 50+ 品牌打印机驱动。

## 核心功能

- 浏览器上传文件 → 自动转换（PDF/图片/Office/OFD/文本）→ 远程打印
- 支持多格式：PDF、JPG/PNG/GIF/HEIC、doc/docx/xls/xlsx/ppt/pptx、OFD、txt/md
- 多用户系统（admin/user 角色）+ 打印记录追踪
- 安全：Session 加密、CSRF 防护、bcrypt 密码
- 默认管理员 admin/admin，首次启动自动创建
- 数据保留策略：按天自动清理过期记录

## 技术栈

后端 Go 1.26 + SQLite，前端 Vue 3 + Vite 7 + Nuxt UI v4 + Tailwind CSS v4

## 使用场景

USB 打印机 → Web 可访问的网络打印服务

- 适合：桌面只有 USB 打印机的办公室/家庭/台球俱乐部前台
- 不适合：已经是网络打印机（网线/WiFi直连）的环境

## 结论

**暂不安装。** 办公室打印机已经是网线/WiFi 直连网络，Mac 自带 AirPrint 支持，不需要再套一层 cups-web。

未来搬到新办公室或者加 USB 打印机时再装。
