# 中国政府网站爬虫 — Cookie 认证模式

## 场景

许多中国政府网站（投资项目审批、招标公告、资质查询等）需要**登录后才能访问数据**，没有公开的匿名 API。典型的 Vue.js + Java 后端架构，数据通过 AJAX 接口返回但需要 Session/Cookie 认证。

## 判断网站是否需要登录

1. **curl 首页** → 返回 HTML 但内容是"登录"注册表单/Vue.js 框架
2. **curl API 接口** → 返回 302 跳转到登录页，或返回空的错误数据
3. **浏览器 F12 → Network** → 接口返回 200 但 `code != 0` 或 `data` 为空
4. **页面有验证码**（captcha）→ 通常说明需要先登录

## 认证流程

### 1. 首次获取 Cookie

用户手动操作（一次性的）：

1. 用 Chrome 打开目标网站并登录
2. F12 → **Application** → **Cookies** → 选择目标域名
3. 双击任一 Cookie 值区域 → `Ctrl+A` 全选 → `Ctrl+C` 复制
4. 保存到 `references/cookies.txt`（一行文本）

典型格式：
```
JSESSIONID=3239363033373936323936303337; route=xxxxx; ...
```

### 2. 脚本中加载 Cookie

```python
import os
import requests

COOKIE_FILE = os.path.join(SKILL_DIR, "references", "cookies.txt")

def load_cookies():
    if not os.path.exists(COOKIE_FILE):
        return None
    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return content if content else None

def get_session():
    session = requests.Session()
    cookie_str = load_cookies()
    if cookie_str:
        session.headers.update({"Cookie": cookie_str})
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": BASE_URL + "/",
    })
    return session
```

### 3. 发现真实 API 路径

很多网站使用 JS 动态加载数据，API 路径藏在 JS 文件里：

```bash
# 1. 查看首页 JS，找 path/baseUrl 变量
curl -s "https://example.gov.cn/js/common.js" | grep "path\s*="
# → var path = "/tzxmspweb";  # API 前缀

# 2. 尝试拼接 API 路径
# 首页用 path+/api/xxx 调接口
# 用 curl 尝试不同路径找能返回数据的
for api in "/api/unifiedLogin/getWebFlag" "/api/mobile/checkProjectCodeState" "/api/indexInfo/indexCount"; do
    curl -s -o /dev/null -w "%{http_code}" "https://example.gov.cn${path_prefix}${api}"
done
```

### 4. 多 API 路径备选方案

一个真实案例中，同一网站有多个可能的查询接口，依次尝试：

```python
API_PATHS = [
    "/api/project/queryPublicList",
    "/api/project/search",
    "/project/list",
]
for api_path in API_PATHS:
    try:
        resp = session.get(f"{BASE_URL}{API_PREFIX}{api_path}", params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data and ("data" in data or "list" in data or "rows" in data):
                items = data.get("data", data.get("list", data.get("rows", [])))
                if items:
                    return items
    except:
        continue
```

## 典型构架识别

| 特征 | 推测架构 |
|------|---------|
| Vue.js + Java Session + JSP | 传统政务网站（Tomcat） |
| 首页有 `path=/xxxspweb` | 有 API 路径前缀 |
| 表单含 `captcha`  | 需要登录才能访问数据 |
| `nginx` 服务器头 | 前置 nginx 反代 |
| JSESSIONID Cookie | Java 后端，Session 会话 |
| 接口返回 JSON 含 `{status, data, message}` | 常见统一返回格式 |

## Cookie 维护

- **JSESSIONID 通常 30 分钟无操作过期** → 长时间爬取需定期刷新
- **部分网站 Cookie 有效期 24 小时~7 天** → 过期后重新获取
- **多账号** → 分别保存 Cookie 文件，脚本中按需加载
- **自动化续期** → 可配置 Playwright/Selenium 自动登录 + 验证码识别（较复杂，一般手动续期即可）

## 常见陷阱

1. ⚠️ **网站有 WAF / 反爬** → 部分政务网站用安全狗/云锁等，频繁请求会被 ban IP
2. ⚠️ **API 返回 500 但误以为是接口不存在** → 500 可能是缺少必要参数（如 pageSize 不能太大）
3. ⚠️ **Cookie 换行符问题** → cookies.txt 必须是单行，不能有无意中的换行
4. ⚠️ **Cookie 中带特殊字符** → 直接粘贴，不需要 URL 编码
5. ⚠️ **网站分内外网** → 内网 IP 访问可能跳到不同页面，确保与浏览器相同网络环境

## 典型案例

### 甘肃省投资项目在线审批监管平台
- 网址：https://tzxm.fzgg.gansu.gov.cn/
- API 前缀：`/tzxmspweb`
- 架构：Vue.js + Java + nginx + Tomcat
- 需要：登录后获取 JSESSIONID
- Cookie 格式：`JSESSIONID=xxx; route=xxx`
- 输出目录：`~/甘肃投资项目/YYYY-MM-DD/`
