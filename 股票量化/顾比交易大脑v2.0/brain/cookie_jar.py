#!/usr/bin/env python3
"""
顾比交易大脑 — Cookie Jar 持仓管理系统
从 Vibe-Trading 借鉴的核心概念：
  - 你的私人持仓池（不在监控列表里的你也可以加入）
  - 仓位管理：单只不超过30%，最多5只
  - 买卖建议记录
  - YOLO 确认机制
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain.config import COOKIE_JAR_PATH, MAX_POSITIONS, MAX_SINGLE_POSITION_PCT


def load_jar():
    """加载 Cookie Jar 持仓池"""
    if os.path.exists(COOKIE_JAR_PATH):
        with open(COOKIE_JAR_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # 初始化空的 Cookie Jar
    return {
        "positions": {},       # code -> {name, shares, avg_cost, add_date, notes}
        "watchlist": [],       # [code, ...] 只看不买的
        "suggestions": [],     # [suggestion, ...] 历史建议记录
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "yolo_mode": True,     # 默认安全模式：只建议，不执行
    }


def save_jar(data):
    """保存 Cookie Jar"""
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    os.makedirs(os.path.dirname(COOKIE_JAR_PATH), exist_ok=True)
    with open(COOKIE_JAR_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def add_position(code, name, shares, avg_cost, notes=""):
    """添加仓位到 Cookie Jar（记录你的实际持仓）"""
    data = load_jar()
    if code in data["positions"]:
        # 更新：加权平均成本
        old = data["positions"][code]
        total_shares = old["shares"] + shares
        total_cost = old["shares"] * old["avg_cost"] + shares * avg_cost
        old["shares"] = total_shares
        old["avg_cost"] = round(total_cost / total_shares, 3)
        old["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        if notes:
            old["notes"] = notes
    else:
        data["positions"][code] = {
            "name": name,
            "shares": shares,
            "avg_cost": avg_cost,
            "add_date": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    return save_jar(data)


def remove_position(code, shares="all"):
    """从 Cookie Jar 移除仓位（减仓/清仓）"""
    data = load_jar()
    if code not in data["positions"]:
        return {"success": False, "error": f"{code} 不在 Cookie Jar 中"}

    pos = data["positions"][code]
    if shares == "all":
        removed = pos["shares"]
        del data["positions"][code]
    else:
        removed = min(int(shares), pos["shares"])
        pos["shares"] -= removed
        if pos["shares"] <= 0:
            del data["positions"][code]
    save_jar(data)
    return {"success": True, "code": code, "removed_shares": removed}


def add_to_watchlist(code):
    """加入观察列表（只看不买）"""
    data = load_jar()
    if code not in data["watchlist"]:
        data["watchlist"].append(code)
    return save_jar(data)


def add_suggestion(suggestion):
    """记录一次买卖建议"""
    data = load_jar()
    suggestion["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["suggestions"].append(suggestion)
    # 只保留最近50条
    if len(data["suggestions"]) > 50:
        data["suggestions"] = data["suggestions"][-50:]
    return save_jar(data)


def set_yolo_mode(enabled=True):
    """切换 YOLO 安全模式"""
    data = load_jar()
    data["yolo_mode"] = enabled
    save_jar(data)
    return {"yolo_mode": enabled, "message": "🛡️ YOLO安全模式已开启：只建议，不执行" if enabled
             else "⚠️ YOLO安全模式已关闭：系统将可以自动执行交易"}


def get_summary():
    """获取 Cookie Jar 概览"""
    data = load_jar()
    pos_list = []
    for code, pos in data["positions"].items():
        pos_list.append({
            "code": code,
            "name": pos["name"],
            "shares": pos["shares"],
            "avg_cost": pos["avg_cost"],
            "add_date": pos.get("add_date", ""),
        })
    return {
        "position_count": len(data["positions"]),
        "positions": pos_list,
        "watchlist_count": len(data["watchlist"]),
        "suggestion_count": len(data["suggestions"]),
        "yolo_mode": data.get("yolo_mode", True),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("🤖 顾比 Cookie Jar 管理系统")
        print("=" * 40)
        s = get_summary()
        print(f"📦 持仓: {s['position_count']}只")
        print(f"👀 观察: {s['watchlist_count']}只")
        print(f"📝 建议: {s['suggestion_count']}条")
        print(f"🛡️ YOLO: {'开启' if s['yolo_mode'] else '关闭'}")
        if s['positions']:
            print("\n持仓明细:")
            for p in s['positions']:
                print(f"  {p['name']}({p['code']}): {p['shares']}股 @ {p['avg_cost']:.2f}")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 5:
        add_position(sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]),
                     sys.argv[6] if len(sys.argv) > 6 else "")
        print(f"✅ 已加入持仓: {sys.argv[3]}({sys.argv[2]})")
    elif cmd == "remove" and len(sys.argv) >= 3:
        r = remove_position(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "all")
        if r["success"]:
            print(f"✅ 已移除持仓: {sys.argv[2]}")
    elif cmd == "yolo":
        enabled = sys.argv[2].lower() in ("on", "true", "1") if len(sys.argv) > 2 else True
        r = set_yolo_mode(enabled)
        print(r["message"])
    else:
        print("用法:")
        print("  python3 brain/cookie_jar.py add <代码> <名称> <股数> <均价> [备注]")
        print("  python3 brain/cookie_jar.py remove <代码> [all/股数]")
        print("  python3 brain/cookie_jar.py yolo [on/off]")
