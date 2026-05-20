# Twitter/X 推文数据提取实战

> 工具评估场景：快速获取目标项目的Twitter推文数据（文本、互动数、图片URL、用户资料），无需登录/API Key。

## 核心方法：从HTML的 `__INITIAL_STATE__` 提取推文JSON

X.com的JavaScript在页面中嵌入完整的推文数据，可以直接从HTML中提取。

### 步骤

```bash
# 1. 用系统代理+浏览器UA下载推文页面
curl -sS --proxy http://127.0.0.1:6478 \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36' \
  -L 'https://x.com/{username}/status/{tweet_id}' -o ~/twitter_page.html
```

```python
import json, re

with open('~/twitter_page.html', 'r') as f:
    html = f.read()

match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
data = json.loads(match.group(1))

tweet_id = '2051490323072004458'  # 替换为目标推文ID
tweet = data['entities']['tweets']['entities'][tweet_id]

# 推文内容
print(tweet['full_text'])

# 互动数据
print(f"❤️ {tweet['favorite_count']}  🔁 {tweet['retweet_count']}  💬 {tweet['reply_count']}  🔖 {tweet['bookmark_count']}")

# 创建时间
print(tweet['created_at'])

# 图片
for m in tweet['entities']['media']:
    print(f"📷 {m['media_url_https']}")
```

### 用户信息

```python
user_data = data['entities']['users']['entities'][tweet['user']]
print(f"@{user_data['screen_name']} — {user_data['name']}")
print(f"👥 {user_data['followers_count']}  ✅蓝V={user_data['is_blue_verified']}")
print(f"📝 {user_data['description']}")
```

### 图片下载

```bash
# 基本URL
curl -sS --proxy http://127.0.0.1:6478 'https://pbs.twimg.com/media/{media_key}.jpg' -o image.jpg

# 大图（加:orig后缀）
curl -sS --proxy http://127.0.0.1:6478 'https://pbs.twimg.com/media/{media_key}.jpg:orig' -o image_original.jpg
```

## 可获取的完整数据字段

**推文数据 (tweet):**
- `full_text` / `text` — 推文全文
- `created_at` — ISO 8601时间戳
- `reply_count`, `favorite_count`, `retweet_count`, `bookmark_count`, `quote_count` — 互动数据
- `lang` — 语言代码
- `entities.media` — 媒体列表（图片URL、尺寸、类型）
- `entities.hashtags` — 标签
- `entities.urls` — 链接
- `entities.user_mentions` — @提及
- `user` — 用户ID

**用户数据 (user):**
- `name` — 显示名
- `screen_name` — 用户名(handle)
- `followers_count`, `friends_count`, `statuses_count`, `listed_count` — 统计
- `favourites_count`, `media_count` — 更多统计
- `description` — 个人简介
- `profile_image_url_https` — 头像
- `profile_banner_url` — 横幅
- `is_blue_verified` — X Premium认证
- `location` — 位置
- `created_at` — 创建时间
- `protected` — 是否保护账户
- `verified` — 传统认证（基本已废弃用新认证代替）

## 替代方法对比

| 方法 | 需代理 | 推文全文 | 互动数据 | 图片URL | 可靠性 |
|------|--------|----------|----------|---------|--------|
| `__INITIAL_STATE__` | ✅ 必需 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ⭐⭐⭐⭐⭐ |
| oembed API | ❌ 不需要 | ⚠️ 截断 | ❌ 无 | ⚠️ 短链 | ⭐⭐⭐ |
| Syndication API | ✅ 需要 | ✅ 有 | ❌ 无 | ⚠️ 需额外请求 | ⭐⭐ |
| Nitter | ✅ 需要 | ✅ 有 | ✅ 有 | ✅ 有 | ⭐（已基本不可用） |

## 已知坑点

1. **国内网络**：`pbs.twimg.com` 和 `x.com` 被屏蔽，必须用系统代理 `127.0.0.1:6478`
2. **图片alt文本**：大部分推文图片没有alt文本，无法通过API获取图文内容
3. **视觉模型读中文**：当前视觉模型对中文信息图查字识别率极低，不要依赖（已测试5+次失败）
4. **Tesseract OCR中文**：对艺术字体+地图底图叠加效果极差
5. **推文删除/保护**：被删除或设为隐私的推文无法获取
6. **X页面重定向**：页面可能重定向到登录页（`Something went wrong`），但`__INITIAL_STATE__`仍可直接从HTML文本中提取（不依赖JavaScript执行）
