#!/usr/bin/env python3
"""
甘肃省投资项目在线审批监管平台 — 项目备案抓取脚本
================================================
数据源：https://tzxm.fzgg.gansu.gov.cn/
用途：每天抓取新备案项目，按地区和资质匹配度筛选

使用方法：
  # 默认模式：抓取今天的数据
  python3 crawl_projects.py

  # 指定日期
  python3 crawl_projects.py --date 2026-05-06

  # 指定查询关键词（匹配公司资质用）
  python3 crawl_projects.py --keywords "建筑设计,工程设计,规划,勘察,监理"

  # 指定优先地区
  python3 crawl_projects.py --regions "天水,陇南"

  # 输出为JSON（供其他程序处理）
  python3 crawl_projects.py --output json

  # 完整示例
  python3 crawl_projects.py --date 2026-05-06 --keywords "建筑设计,工程设计,房建,规划,勘察,监理" --regions "天水,陇南,定西" --output text

依赖：pip install requests beautifulsoup4 lxml
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from configparser import ConfigParser

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，请运行: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    pass  # BeautifulSoup 只用于 Cookie 模式备用

# ============================================================
# 配置区
# ============================================================

# 甘肃省投资项目在线审批监管平台
BASE_URL = "https://tzxm.fzgg.gansu.gov.cn"
API_PREFIX = "/tzxmspweb"

# 公开API —— 无需登录即可访问
# 2026年4月实测：POST 此接口返回15条备案项目记录（示例数据，日期至2025年12月止）
PUBLIC_API_URL = f"{BASE_URL}{API_PREFIX}/api/project/queryProjectPublicList"

# 脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(SKILL_DIR, "references", "company_config.ini")

# 读取配置文件
config = ConfigParser()
config.read(CONFIG_FILE, encoding="utf-8")

# 从公司资质参考文件中读取资质关键词
COMPANY_KEYWORDS = [
    kw.strip() for kw in config.get("company", "keywords", fallback="").split(",")
    if kw.strip()
] or [
    "建筑设计", "建筑工程", "房屋建筑", "房建", "住宅", "公共建筑",
    "工业厂房", "厂房", "钢结构",
    "风景园林", "园林", "景观", "绿化", "公园",
    "市政给水", "市政排水", "给水", "排水", "供热", "热力",
    "公路", "桥梁", "隧道", "水利",
    "消防", "智能化", "弱电",
    "岩土", "勘察", "测量", "测绘",
    "检测", "鉴定", "安全性", "节能",
    "监理",
    "咨询", "可研", "造价", "全过程",
    "施工总承包", "施工",
    "老旧小区改造", "棚户区改造", "安置房", "保障房",
    "改造", "提升", "加固", "扩建",
]

# 优先关注的地区
PREFERRED_REGIONS = [
    r.strip() for r in config.get("company", "preferred_regions", fallback="").split(",")
    if r.strip()
] or ["天水", "陇南", "定西"]

# 输出目录
OUTPUT_DIR = config.get("company", "output_dir", fallback=str(os.path.join(os.path.expanduser("~"), "甘肃投资项目")))

# ============================================================
# Cookie 管理
# ============================================================

COOKIE_FILE = os.path.join(SKILL_DIR, "references", "cookies.txt")


def load_cookies():
    """从cookies.txt文件加载Cookie（跳过注释行）"""
    if not os.path.exists(COOKIE_FILE):
        return None
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # 跳过注释行，只取有效Cookie行
        valid_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                valid_lines.append(stripped)
        if valid_lines:
            content = " ".join(valid_lines)
            print(f"📄 已加载Cookie文件: {COOKIE_FILE}")
            return content
        else:
            print("⚠️  Cookie文件为空或只有注释，未配置有效Cookie")
            return None
    except Exception as e:
        print(f"⚠️  读取Cookie文件失败: {e}")
        return None


def get_session():
    """创建带Cookie的requests Session"""
    session = requests.Session()
    cookie_str = load_cookies()
    if cookie_str:
        # 设置Cookie头
        session.headers.update({"Cookie": cookie_str})

    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": BASE_URL + "/",
        "Content-Type": "application/json;charset=UTF-8",
    })
    return session


# ============================================================
# 核心逻辑
# ============================================================


def search_projects(session, keyword="", page=1, page_size=20, date_from="", date_to=""):
    """
    搜索项目备案信息。
    需要登录Cookie才能获取数据。
    """
    projects = []

    # 尝试方法1：通过列表页API获取
    api_paths = [
        "/api/project/queryPublicList",
        "/api/project/search",
        "/project/list",
    ]

    for api_path in api_paths:
        try:
            url = f"{BASE_URL}{API_PREFIX}{api_path}"
            params = {
                "keyword": keyword,
                "page": page,
                "pageSize": page_size,
                "startTime": date_from,
                "endTime": date_to,
            }
            resp = session.get(url, params=params, timeout=15)
            print(f"    API: {api_path} -> HTTP {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if data and ("data" in data or "list" in data or "rows" in data):
                        items = data.get("data", data.get("list", data.get("rows", [])))
                        if isinstance(items, list) and len(items) > 0:
                            total_pages = data.get("totalPages", data.get("pages", 1))
                            print(f"    ✅ 通过 {api_path} 获取到 {len(items)} 条数据")
                            return items, total_pages
                except (json.JSONDecodeError, ValueError):
                    pass
        except requests.RequestException as e:
            print(f"    ⚠️  API {api_path} 请求失败: {e}")
            continue

    # 尝试方法2：抓取公示公告页面
    try:
        urls_to_try = [
            f"{BASE_URL}{API_PREFIX}/gsgg/index.html",
            f"{BASE_URL}{API_PREFIX}/notice/index.html",
        ]
        for url in urls_to_try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                rows = soup.select("table tr")
                if len(rows) > 1:
                    for row in rows[1:]:
                        cols = row.find_all("td")
                        if len(cols) >= 4:
                            project = {
                                "name": cols[0].get_text(strip=True),
                                "code": cols[1].get_text(strip=True) if len(cols) > 1 else "",
                                "region": cols[2].get_text(strip=True) if len(cols) > 2 else "",
                                "date": cols[3].get_text(strip=True) if len(cols) > 3 else "",
                                "status": cols[4].get_text(strip=True) if len(cols) > 4 else "",
                                "url": cols[0].find("a")["href"] if cols[0].find("a") else "",
                            }
                            projects.append(project)
                    if projects:
                        print(f"    ✅ 通过页面解析获取到 {len(projects)} 条数据")
                        return projects, 1
    except Exception as e:
        print(f"    ⚠️  页面解析失败: {e}")

    return projects, 0


def match_project(project, keywords=None, regions=None):
    """匹配项目与公司资质和地区。返回匹配结果字典。"""
    if keywords is None:
        keywords = COMPANY_KEYWORDS
    if regions is None:
        regions = PREFERRED_REGIONS

    name = project.get("name", "")
    content = project.get("content", "")
    region = project.get("region", "")
    location = project.get("location", "")

    text_to_match = f"{name} {content} {region} {location}"

    # 匹配资质关键词
    matched_keywords = []
    for kw in keywords:
        if kw in text_to_match:
            matched_keywords.append(kw)

    # 判断地区优先级
    region_priority = 0
    for i, pref_region in enumerate(regions):
        if pref_region in region or pref_region in location:
            region_priority = max(region_priority, 2 - i)
            break

    match_score = len(matched_keywords) * 10 + region_priority * 20

    return {
        "matched": len(matched_keywords) > 0 or region_priority > 0,
        "matched_keywords": matched_keywords,
        "region_priority": region_priority,
        "match_score": match_score,
        "region": region or location,
    }


def format_project(project, match_result):
    """格式化单个项目为可读文本"""
    name = project.get("name", "未知项目")
    code = project.get("code", "")
    region = project.get("region", project.get("location", ""))
    date = project.get("date", project.get("approvalDate", ""))
    status = project.get("status", "准予许可")
    investment = project.get("investment", project.get("totalInvestment", ""))
    content = project.get("content", "")
    unit = project.get("unit", project.get("applicant", ""))

    lines = []
    lines.append(f"项目名称：{name}")
    if code:
        lines.append(f"项目代码：{code}")
    if region:
        lines.append(f"建设地点：{region}")
    if unit:
        lines.append(f"建设单位：{unit}")
    if investment:
        lines.append(f"投资金额：{investment}")
    if date:
        lines.append(f"日期：{date}")
    if status:
        lines.append(f"状态：{status}")
    if content:
        lines.append(f"建设内容：{content[:200]}")
    if match_result["matched_keywords"]:
        lines.append(f"匹配资质：{'、'.join(match_result['matched_keywords'])}")
    lines.append(f"匹配度：{'⭐' * (match_result['match_score'] // 10)}")
    return "\n".join(lines)


def save_report(date_str, all_projects, matched_projects, keywords, regions, output_dir):
    """保存抓取报告到文件"""
    os.makedirs(output_dir, exist_ok=True)
    today_cn = datetime.now().strftime("%Y年%m月%d日")
    date_dir = os.path.join(output_dir, date_str)
    os.makedirs(date_dir, exist_ok=True)

    # 保存完整报告
    report_path = os.path.join(date_dir, f"项目列表-{date_str}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 甘肃投资项目备案 — {date_str}\n\n")
        f.write(f"抓取时间：{today_cn}\n")
        f.write(f"共获取 {len(all_projects)} 个项目\n\n")

        if matched_projects:
            f.write("## 🔥 高价值匹配项目\n\n")
            for i, (p, m) in enumerate(matched_projects, 1):
                f.write(f"### #{i} {p.get('name', '未知')}\n\n")
                f.write(format_project(p, m) + "\n\n")
                f.write("---\n\n")

        f.write("## 📊 全部项目\n\n")
        for i, p in enumerate(all_projects, 1):
            f.write(f"{i}. {p.get('name', '未知')}")
            if p.get("region"):
                f.write(f" — {p.get('region')}")
            if p.get("date"):
                f.write(f" ({p.get('date')})")
            f.write("\n")

        f.write(f"\n\n---\n")
        f.write(f"关键词：{', '.join(keywords)}\n")
        f.write(f"优先地区：{', '.join(regions)}\n")

    # 保存高价值项目单独文件
    if matched_projects:
        highlight_path = os.path.join(date_dir, f"高价值项目-{date_str}.md")
        with open(highlight_path, "w", encoding="utf-8") as f:
            f.write(f"# 🔥 高价值项目 — {date_str}\n\n")
            for i, (p, m) in enumerate(matched_projects, 1):
                f.write(f"## #{i} {p.get('name', '未知')}\n\n")
                f.write(format_project(p, m) + "\n\n")
                f.write("---\n\n")

    return report_path


def main():
    parser = argparse.ArgumentParser(
        description="甘肃省投资项目备案抓取工具"
    )
    parser.add_argument(
        "--date",
        help="查询日期，格式 YYYY-MM-DD，默认今天",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "--keywords",
        help="公司资质关键词，逗号分隔",
        default=",".join(COMPANY_KEYWORDS),
    )
    parser.add_argument(
        "--regions",
        help="优先地区，逗号分隔",
        default=",".join(PREFERRED_REGIONS),
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="抓取页数，默认3页",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json", "both"],
        default="text",
        help="输出格式",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        default=True,
        help="保存报告到文件",
    )

    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",")]
    regions = [r.strip() for r in args.regions.split(",")]
    date_str = args.date

    print(f"🔍 正在查询 {date_str} 的项目备案...")
    print(f"   资质关键词: {', '.join(keywords)}")
    print(f"   优先地区: {', '.join(regions)}")
    print()

    # 获取带Cookie的Session
    session = get_session()

    all_projects = []
    total_pages = 0

    # 逐页抓取
    for page in range(1, args.pages + 1):
        print(f"   抓取第 {page} 页...")
        projects, total_pages = search_projects(
            session,
            keyword="",
            page=page,
            page_size=20,
            date_from=date_str,
            date_to=date_str,
        )
        if projects:
            print(f"   ✅ 找到 {len(projects)} 条")
            all_projects.extend(projects)
        else:
            print(f"   ⚠️  无数据")
        if page >= total_pages > 0:
            break
        if projects:
            time.sleep(1)

    if not all_projects:
        print("\n⚠️  未获取到数据。可能原因：")
        print("  1. 网站需要登录才能访问（最常见）")
        print("  2. 当天没有新备案项目")
        print("  3. 网络连接问题")
        print("  4. 网站改版，需要更新抓取逻辑")
        print()
        print("💡 解决办法：")
        print("  1. 用浏览器打开 https://tzxm.fzgg.gansu.gov.cn/ 并登录")
        print("  2. 按 F12 → Application/存储 → Cookies，找到 JSESSIONID")
        print("  3. 把它保存到:")
        print(f"     {COOKIE_FILE}")
        print("     格式示例: JSESSIONID=xxxxxxxx;")
        print("  4. 重新运行本脚本")
        sys.exit(0)

    # 匹配项目
    matched_projects = []
    for p in all_projects:
        match_result = match_project(p, keywords, regions)
        if match_result["matched"]:
            matched_projects.append((p, match_result))

    matched_projects.sort(key=lambda x: x[1]["match_score"], reverse=True)

    # 保存报告
    if args.save:
        output_dir = os.path.expanduser(OUTPUT_DIR)
        report_path = save_report(date_str, all_projects, matched_projects, keywords, regions, output_dir)
        print(f"\n📁 报告已保存: {report_path}")

    # 输出结果
    if args.output in ("text", "both"):
        today = datetime.now().strftime("%Y年%m月%d日")
        print(f"\n{'='*60}")
        print(f"📋 项目备案抓取结果 — {today}")
        print(f"{'='*60}")
        print(f"共获取 {len(all_projects)} 个项目，匹配 {len(matched_projects)} 个")
        print()

        if matched_projects:
            region_groups = {}
            for p, m in matched_projects:
                r = m.get("region", "其他")
                if r not in region_groups:
                    region_groups[r] = []
                region_groups[r].append((p, m))

            for region, items in region_groups.items():
                priority = "⭐ 优先地区" if any(
                    r in region for r in regions
                ) else "📍 其他地区"
                print(f"\n--- {priority}：{region} ({len(items)}个项目) ---")
                print()

                for i, (p, m) in enumerate(items, 1):
                    print(f"#{i}")
                    print(format_project(p, m))
                    print()
        else:
            print("⚠️  本次未匹配到符合条件的项目")
            print()

        print(f"{'='*60}")
        print(f"📊 统计")
        print(f"{'='*60}")
        print(f"总项目数: {len(all_projects)}")
        print(f"匹配项目: {len(matched_projects)}")
        print(f"匹配率: {len(matched_projects)/len(all_projects)*100:.1f}%")
        print()

    if args.output in ("json", "both"):
        output_data = {
            "date": date_str,
            "total": len(all_projects),
            "matched": len(matched_projects),
            "keywords": keywords,
            "regions": regions,
            "projects": [
                {
                    "name": p.get("name", ""),
                    "code": p.get("code", ""),
                    "region": p.get("region", p.get("location", "")),
                    "date": p.get("date", p.get("approvalDate", "")),
                    "status": p.get("status", ""),
                    "investment": p.get("investment", p.get("totalInvestment", "")),
                    "unit": p.get("unit", p.get("applicant", "")),
                    "content": p.get("content", ""),
                    "match_keywords": m["matched_keywords"],
                    "match_score": m["match_score"],
                    "region_priority": m["region_priority"],
                }
                for p, m in matched_projects
            ],
        }
        if args.output == "json":
            print(json.dumps(output_data, ensure_ascii=False, indent=2))
        else:
            print("\n--- JSON 数据 ---\n")
            print(json.dumps(output_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
