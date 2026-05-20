# 免费图片素材获取指南（短视频用）

## 为什么需要图片素材

纯色背景+文字的短视频视觉效果单调，完播率低。加上实景图片能大幅提升观感。

## 推荐图库（免费可商用）

### ⭐ Wikimedia Commons（最可靠，无验证）
- **URL:** commons.wikimedia.org
- **无需API Key，无Cloudflare/机器人检测**（浏览器和curl都能直接访问）
- **全部 CC 协议**（免费可商用）
- **搜索方法（两步）：**
  1. 搜索图片文件：`action=query&list=search&srsearch={keyword}&srnamespace=6&srlimit=20&format=json`
  2. 获取下载URL：`action=query&titles=File:{exact_title}&prop=imageinfo&iiprop=url&format=json`
  - 下载URL在返回JSON的 `imageinfo[0].url` 字段
- **搜索技巧：**
  - 中英文关键词都要试（图片标题可能是英文，用中文搜不到）
  - 用 `srnamespace=6` 限制只返回文件（File: 开头的）
- **坑点：**
  - 429限速（curl太快会返回429），需sleep 5秒再重试
  - 404 URL（图片被重命名/删除），需重新搜索
  - 图片品质参差不齐（部分照片年代久远如1920年）
  - 维基返回的url带 `?utm_source=...` 参数，直接curl使用即可
- **下载命令：**
  ```bash
  curl -sL --connect-timeout 10 --max-time 30 -o /tmp/snooker_1.jpg "https://upload.wikimedia.org/wikipedia/commons/8/89/Snooker_on_a_snooker_table.jpg"
  ```

### Pexels（推荐）
- **URL:** pexels.com
- **无需API Key，CDN直链可下载**
- 图片ID直链格式：`https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg?auto=compress&cs=tinysrgb&w={width}&h={height}`
- 注意：Pexels网站有Cloudflare防护，但CDN直链可直接curl下载
- 图片ID可以通过 `web_search site:pexels.com {keyword}` 找到

### Pixabay
- **URL:** pixabay.com
- 需要API Key（免费注册）
- API: `https://pixabay.com/api/?key={API_KEY}&q={keyword}&orientation=vertical&per_page=20`

### Unsplash
- **URL:** unsplash.com
- 需要API Key（免费注册）
- API: `https://api.unsplash.com/search/photos?query={keyword}&client_id={ACCESS_KEY}`

## 下载脚本模板

```python
import urllib.request
import os

# Pexels直链下载（无需API Key）
PEXELS_IDS = [399187, 46871, 260386]  # 图片ID列表

os.makedirs("~/Desktop/鑫球汇图片素材/", exist_ok=True)

for i, pid in enumerate(PEXELS_IDS, 1):
    url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=800&h=1000"
    path = os.path.expanduser(f"~/Desktop/鑫球汇图片素材/素材_{i:02d}.jpg")
    urllib.request.urlretrieve(url, path)
    print(f"✅ 下载完成: 素材_{i:02d}.jpg")
```

## 图片分配策略

7段短视频推荐图片分配：

| 段落内容 | 推荐图片类型 | 示例 |
|---------|-------------|------|
| 热点新闻/赛事 | 比赛场景/人物特写 | 斯诺克比赛、选手击球 |
| 品牌引流入店 | 店铺环境/门头 | 台球厅全景、装修环境 |
| 场景/位置描述 | 空间大景 | 店内环境、吧台、休息区 |
| 人物/服务展示 | 人物互动 | 美女打球、顾客打球 |
| 产品/服务说明 | 细节特写 | 台球特写、球杆细节 |
| 社交/聚会场景 | 多人互动 | 朋友聚会、PK局 |
| CTA/联系方式 | 品牌形象 | 品牌Logo、门头、夜间灯光 |

## 已知坑点

1. **Pexels Cloudflare 绕过** — 网站有Cloudflare防护不能直接爬，
   但CDN直链 `images.pexels.com/photos/{ID}/...` 可直接 `curl` 或 `urllib` 下载
2. **图片比例适配** — 下载的图不一定是9:16竖屏，脚本里需做 `max(w/bg_w, h/bg_h)` 缩放+居中裁剪
3. **网络超时** — 国外CDN在中国访问可能慢，设 `timeout=10` + try/except 兜底
4. **图片版权** — Pexels图片免费可商用，但涉及人脸的可能有肖像权问题，商业视频慎用人脸特写
