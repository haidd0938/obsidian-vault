
---

## ⚡ 简介
**Osiris** 是一个开源的全球实时情报仪表盘（1.9k⭐），把航班追踪、CCTV摄像头、地震监测、冲突区监控、新闻情报等整合到一个 WebGL 地图界面。本地部署在 `http://localhost:8649`，大部分功能不依赖API Key。

## 📋 数据层总览

| 分类 | 数据点 | 来源 |
|------|--------|------|
| **AVIATION 航空** | 商业航班/私人飞机/军机/公务机 | OpenSky Network |
| **MARITIME & SPACE 海事太空** | 39个全球港口/太空站 | 静态军事情报 + N2YO |
| **SURVEILLANCE 监控** | 2,000+ CCTV摄像头/新闻/SIGINT | TfL, WSDOT, NYCDOT等 |
| **NATURAL HAZARDS 自然灾害** | 地震(24h M2.5+)/山火/恶劣天气 | USGS / NASA FIRMS / EONET |
| **THREATS & INFRA 威胁基建** | 核设施/冲突事件/GPS干扰 | 静态OSINT情报 |
| **DISPLAY 显示** | 昼夜循环 | WebGL渲染 |
| **MARKETS & INTEL 市场情报** | 股指/军工/能源/商品/加密货币 | 实时行情API |
| **CONFLICT ZONE 冲突区** | 13个活跃冲突/紧张区域 | 静态OSINT情报 |

## 📋 使用方法

### 1. 开启/关闭数据层
左边栏 **DATA LAYERS**：
- 点分类名（如 `AVIATION`）展开子选项
- 点 `Enable all` 全开 / `Disable all` 全关
- 单独开关每个子层（点文字或旁边的开关点）
- 层名后面的数字 = 当前实体数（如 `Earthquakes (24h) 29`）

### 2. 查看地图上的实体
- 缩放至城市/街道级别（滚动滚轮）
- 点击实体的 **绿色/黄色/红色图标** 弹出信息面板
- 飞机图标 → 航班号、高度、速度、航线
- 地震红点 → 震级、深度、位置
- CCTV绿色摄像机 → 实时画面（部分地区）
- 新闻蓝色点 → 点击会打开新闻流播放器

### 3. RECON工具箱
左下角 **RECON** 按钮 → 弹出OSINT工具面板：
- **IP Lookup** — IP归属地、ASN、威胁评分
- **WHOIS** — 域名注册信息
- **DNS Lookup** — A/AAAA/MX/NS/TXT/CNAME记录
- **Port Scanner** — TCP端口扫描+服务识别
- **SSL/TLS Inspector** — 证书链分析
- **CVE Vulnerability** — NVD漏洞数据库查询
- **BGP Route** — 路由信息
- **Network Sweep** — 批量IP段扫描

### 4. SIGINT情报 + 新闻
- **SIGINT FEED**（右下角）— 20个情报类RSS，自动刷新
- **Live News Feeds**（路边新闻点）— 25+全球广播公司新闻流
- 每条新闻按严重度标注：LOW / MEDIUM / HIGH

### 5. 区域预设
中间栏 **REGION PRESETS**：
- 🌍 GLOBAL / 🇪🇺 EUROPE / 🌏 EAST ASIA / 🌎 AMERICAS
- 🔥 MIDDLE EAST / ⚔️ UKRAINE / 🌍 AFRICA / 🌏 S.E. ASIA
- ❄️ ARCTIC / 🇮🇳 INDIA / 🇦🇺 AUSTRALIA / ⚠️ SUDAN

### 6. 市场行情面板
右侧 **MARKETS & INTEL** 面板：
- INDICES 股指 / DEFENSE 军工股 / ENERGY 能源
- COMMODITIES 商品 / CRYPTO 加密货币

### 7. 地图模式切换
- **2D MAP** — 暗色地图
- **SATELLITE** — 卫星影像

## ⌨️ 快捷键

| 按键 | 功能 |
|------|------|
| `F` | 全屏切换 |
| `S` | 分享当前视图 |
| `L` | 开关图层面板 |
| `M` | 开关市场面板 |
| `I` | 开关情报面板 |
| `R` | 重置为全球视角 |
| `?` | 显示快捷键帮助 |
| `ESC` | 关闭所有面板/弹窗 |

> 注意：Osiris的快捷键通过 `KeyboardShortcuts.tsx` 组件管理，在输入框/文本框内不触发

## 🚀 启动与维护

### 启动
```bash
cd ~/Projects/osiris
npm run dev  # 开发模式（默认3000端口）
```
**本地访问：** http://localhost:8649（用 `PORT=8649` 或其他端口配置）

### 常见问题
- **端口3000被占用**：Docker常占3000端口，换端口启动或用 `lsof -i :3000` 查占用进程
- **国内网络**：npm install用淘宝镜像 `npm config set registry https://registry.npmmirror.com`
- **大多数功能无需API Key**，可选配置：`OPENSKY_USERNAME/PASSWORD`（航班数据增强）、`N2YO_API_KEY`（卫星追踪）

### 技术栈
- Next.js 16 + TypeScript 5 + Turbopack
- MapLibre GL JS（WebGL渲染，60fps）
- Framer Motion 动画
- Lucide React 图标

## 🔗 相关资源
- GitHub仓库：https://github.com/simplifaisoul/osiris
- Demo：https://osirisai.live
- Discord：https://discord.gg/umBykEpb98
- 本地目录：`~/Projects/osiris/`

## 💡 案例

> **你说：** "我想看看今天全球有哪些地震"
> **我：** 打开左边NATURAL HAZARDS → Earthquakes (24h) 已默认开启，地图上红色圆点就是震中，点击可以看震级和深度

> **你说：** "查一下这个IP的归属地"
> **我：** 左下角 RECON → IP Lookup → 输入IP → 即可看到国家、ASN、运营商信息

> **你说：** "中东那边现在什么情况"
> **我：** 点区域预设 🔥 MIDDLE EAST → 地图飞过去 → 开启冲突区(GPS Jamming/Global Incidents) + SIGINT新闻流，实时监控
