#!/usr/bin/env python3
"""
顾比交易大脑 — 多渠道推送模块
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
参考 daily_stock_analysis 的多渠道推送设计：
  企业微信 / 飞书 / Telegram 等

用法：
  python3 brain/notifier.py wechat     # 推送到企业微信
  python3 brain/notifier.py feishu     # 推送到飞书
  python3 brain/notifier.py test       # 测试配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import sys
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(BRAIN_DIR)
sys.path.insert(0, BRAIN_DIR)
sys.path.insert(0, ROBOT_DIR)

# ──────────── 推送配置 ────────────
# 在这里配置你的 Webhook URL
# 企业微信机器人: 群聊 → 添加群机器人 → 复制 Webhook URL
# 飞书机器人: 群设置 → 群机器人 → 添加 → Webhook

NOTIFIER_CONFIG = {
    # 企业微信机器人 Webhook URL（留空则不启用）
    "wechat_webhook": "",
    # 飞书机器人 Webhook URL（留空则不启用）
    "feishu_webhook": "",
    # 是否启用桌面通知（终端打印）
    "terminal_output": True,
}


def _fetch_url(url, data=None, timeout=10):
    """发送HTTP请求"""
    if data:
        data = data.encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "GubiTradingBrain/1.0",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


# ═══════════════ 企业微信 ═══════════════

def send_wechat(title, content, msg_type="markdown"):
    """
    发送企业微信群消息

    支持类型: markdown / text
    """
    webhook = NOTIFIER_CONFIG.get("wechat_webhook", "")
    if not webhook:
        return {"success": False, "error": "未配置企业微信Webhook"}

    try:
        if msg_type == "markdown":
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content[:4096],  # 企微限制4096字
                },
            }
        else:
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"{title}\n\n{content[:2048]}",
                },
            }

        result = _fetch_url(webhook, json.dumps(payload, ensure_ascii=False))
        if result:
            parsed = json.loads(result)
            if parsed.get("errcode") == 0:
                return {"success": True, "channel": "企业微信"}
            else:
                return {"success": False, "error": f"企微返回: {parsed.get('errmsg', '未知错误')}"}
        return {"success": False, "error": "请求失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════ 飞书 ═══════════════

def send_feishu(title, content):
    """
    发送飞书群消息（富文本格式）
    """
    webhook = NOTIFIER_CONFIG.get("feishu_webhook", "")
    if not webhook:
        return {"success": False, "error": "未配置飞书Webhook"}

    try:
        # 构建飞书富文本消息
        content_list = [[{"tag": "text", "text": f"📊 {title}"}]]
        content_list.append([{"tag": "text", "text": f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}])
        content_list.append([{"tag": "text", "text": "\n"}])

        # 将markdown文本分行处理
        for line in content.split("\n"):
            if not line.strip():
                content_list.append([{"tag": "text", "text": " "}])
            elif line.startswith("#"):
                content_list.append([
                    {"tag": "text", "text": line.replace("#", "").strip(), "style": ["bold"]},
                ])
            else:
                # 检测是否为关键信息
                if "✅" in line or "🟢" in line or "📗" in line:
                    content_list.append([{"tag": "text", "text": line}])
                elif "❌" in line or "🔴" in line or "📕" in line:
                    content_list.append([{"tag": "text", "text": line}])
                else:
                    content_list.append([{"tag": "text", "text": line}])

        # 飞书卡片有限制，裁剪到合理长度
        if len(content_list) > 50:
            content_list = content_list[:50]
            content_list.append([{"tag": "text", "text": "...（内容过长已截断）"}])

        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title[:128],
                        "content": content_list,
                    }
                }
            },
        }

        result = _fetch_url(webhook, json.dumps(payload, ensure_ascii=False))
        if result:
            parsed = json.loads(result)
            if parsed.get("code") == 0:
                return {"success": True, "channel": "飞书"}
            else:
                return {"success": False, "error": f"飞书返回: {parsed.get('msg', '未知错误')}"}
        return {"success": False, "error": "请求失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ═══════════════ 桌面通知 ═══════════════

def send_terminal(title, content):
    """终端输出（本地通知）"""
    if not NOTIFIER_CONFIG.get("terminal_output", True):
        return {"success": False, "error": "终端输出已禁用"}

    print("=" * 55)
    print(f"📬 {title}")
    print("=" * 55)
    print(content)
    print("=" * 55)
    return {"success": True, "channel": "终端"}


# ═══════════════ macOS 通知 ═══════════════

def send_macos_notification(title, message):
    """macOS 通知中心"""
    try:
        import subprocess
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, timeout=5
        )
        return {"success": True, "channel": "macOS通知"}
    except:
        return {"success": False, "error": "macOS通知发送失败"}


# ═══════════════ 统一推送入口 ═══════════════

def notify(title, content, channels=None):
    """
    统一推送入口

    参数:
      title: 标题
      content: 内容（支持markdown格式）
      channels: ["wechat", "feishu", "terminal", "macos"] 或 None（全部启用）

    返回:
      [{channel, success, error}, ...]
    """
    if channels is None:
        channels = ["terminal"]

    results = []

    for ch in channels:
        ch = ch.lower().strip()

        if ch == "wechat":
            result = send_wechat(title, content)
        elif ch == "feishu":
            result = send_feishu(title, content)
        elif ch == "terminal":
            result = send_terminal(title, content)
        elif ch == "macos":
            result = send_macos_notification(title, content[:200])
        else:
            result = {"success": False, "error": f"未知渠道: {ch}"}

        result["channel"] = ch
        results.append(result)

        if result.get("success"):
            print(f"✅ [{ch}] 推送成功")
        else:
            print(f"❌ [{ch}] 推送失败: {result.get('error', '?')}")

    return results


# ═══════════════ 自动生成简报 ═══════════════

def build_daily_brief(market_overview=None, decision_cards=None, sentiment=None):
    """
    生成每日简报文本（用于推送）

    从大盘复盘 + 决策评分卡 自动生成简洁的每日简报。
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"# 📊 顾比交易大脑 · 每日简报")
    lines.append(f"🕐 {timestamp}")
    lines.append("")

    # 大盘概况
    if market_overview:
        lines.append("## 📈 大盘概览")
        for idx in market_overview.get("indices", []):
            sign = "+" if idx.get("change_pct", 0) > 0 else ""
            lines.append(f"- {idx['name']}: {idx['price']:.2f} ({sign}{idx['change_pct']:.2f}%)")
        lines.append("")

    # 市场情绪
    if sentiment:
        lines.append(f"## 📰 市场情绪: {sentiment.get('overall_sentiment', '?')}")
        lines.append(f"- {sentiment.get('advice', '')}")
        lines.append("")

    # 决策评分卡重点摘要
    if decision_cards:
        lines.append("## 📋 决策评分")
        for card in decision_cards:
            if card.get("status") != "ok":
                continue
            name = card["name"]
            score = card["overall_score"]
            grade = card["grade"]
            risk = card.get("risk_level", "?")
            action = card.get("action", {}).get("suggestion", "?")
            lines.append(f"- **{name}**: {score}分[{grade}] | {risk} | {action[:40]}")

        lines.append("")

    lines.append("---")
    lines.append("🤖 由顾比交易大脑自动生成")

    return "\n".join(lines)


# ═══════════════ 主入口 ═══════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 brain/notifier.py test          # 测试通知配置")
        print("  python3 brain/notifier.py wechat        # 推送企业微信")
        print("  python3 brain/notifier.py feishu        # 推送飞书")
        print("  python3 brain/notifier.py brief         # 生成简报")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "test":
        print("🔍 推送配置检查")
        print("=" * 40)
        wc = NOTIFIER_CONFIG.get("wechat_webhook", "")
        fs = NOTIFIER_CONFIG.get("feishu_webhook", "")
        print(f"企业微信: {'✅ 已配置' if wc else '❌ 未配置（编辑notifier.py的NOTIFIER_CONFIG）'}")
        print(f"飞书:     {'✅ 已配置' if fs else '❌ 未配置（编辑notifier.py的NOTIFIER_CONFIG）'}")
        print(f"终端输出: {'✅ 已开启' if NOTIFIER_CONFIG.get('terminal_output', True) else '❌ 已关闭'}")

    elif cmd == "wechat":
        content = build_daily_brief()
        result = send_wechat("顾比交易大脑 · 每日简报", content)
        print(f"结果: {result}")

    elif cmd == "feishu":
        content = build_daily_brief()
        result = send_feishu("顾比交易大脑 · 每日简报", content)
        print(f"结果: {result}")

    elif cmd == "brief":
        content = build_daily_brief()
        print(content)
