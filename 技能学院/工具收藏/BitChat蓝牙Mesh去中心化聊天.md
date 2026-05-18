---
tags: [工具收藏, 通信, 去中心化, 离线]
rating: ⭐⭐⭐ (装备用，不当主力)
date: 2026-05-16
---

# BitChat — 蓝牙 Mesh 去中心化聊天

## 一句话
**离线也能聊的 IRC** — 蓝牙 Mesh 短距 + Nostr 远距，无服务器、无账号、无手机号。

## 基本信息

| 字段 | 值 |
|------|-----|
| GitHub | permissionlesstech/bitchat |
| ⭐ | 25,862 |
| 语言 | Swift (iOS/macOS 原生) |
| 许可证 | Unlicense（公有领域） |
| 安装 | **App Store 直接装** — 搜 "BitChat Mesh" |
| App Store | https://apps.apple.com/us/app/bitchat-mesh/id6748219622 |
| 大小 | 约 17.1MB |
| 最后更新 | 2026-05-10（活跃维护） |

## 架构

```
用户A ──Bluetooth LE Mesh──→ 用户B（短距，最多7跳中继）
   │                              │
   └────Nostr 协议(290+中继)──────┘（远距，走互联网）
```

- **短距**：Bluetooth LE Mesh，Noise Protocol E2EE
- **远距**：Nostr 协议，geohash 位置频道
- **路由**：蓝牙优先 → Nostr 兜底 → 队列等待

## 频道等级

| 级别 | 精度 | 范围 |
|------|------|------|
| block | 7位geohash | 街区级 |
| neighborhood | 6位 | 社区级 |
| city | 5位 | 城市级 |
| province | 4位 | 省级 |
| region | 2位 | 国家/大区域 |

## 适用场景

**✅ 装它**
- 上海断网/地震时替代 Telegram
- EPC 工地现场离线通信（工友间不需要 Wi-Fi）
- 台球俱乐部店内内部沟通
- 不依赖任何中央服务器，无封号风险

**❌ 别当主力**
- 日常聊天还是 Telegram 更好用
- 没有机器人 API
- 只有 Apple 设备

## 结论

装好放那，17MB 不占地方。断网时它能救命 —— 蓝牙 mesh 范围内，你和附近所有人都能聊。
