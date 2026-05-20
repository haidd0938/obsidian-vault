#!/usr/bin/env python3
"""
顾比交易大脑 — YOLO 安全交易模式
从 Vibe-Trading 借鉴的核心安全机制

YOLO = You Only Look Once
  - 安全模式(YOLO=ON)：系统只出建议，老板确认后才操作
  - 自动模式(YOLO=OFF)：系统可以自动执行交易（需老板手动开启）

自动下单接口预留，未来可对接：
  - 同花顺/iFind API
  - 券商API（华泰/中信/东方财富）
  - 模拟盘 (trade-log.py)
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain.cookie_jar import load_jar, save_jar, add_suggestion


def check_yolo():
    """检查当前 YOLO 模式状态"""
    data = load_jar()
    return data.get("yolo_mode", True)


def suggest_trade(decision_item, price=None):
    """
    生成一条买卖建议（YOLO 模式）
    只记录建议，不执行任何操作

    参数:
      decision_item: signal_fusion 输出的一个标的决策
      price: 当前价格（可选）
    """
    data = load_jar()
    yolo_mode = data.get("yolo_mode", True)

    suggestion = {
        "code": decision_item.get("code", "?"),
        "name": decision_item.get("name", "?"),
        "action": decision_item.get("action", "观察"),
        "reason": decision_item.get("reason", ""),
        "overall_score": decision_item.get("overall_score", 0),
        "confidence": decision_item.get("confidence", ""),
        "price": price,
        "yolo_mode": yolo_mode,
        "status": "pending_approval" if yolo_mode else "auto_execute",
    }

    # 记录到 Cookie Jar
    add_suggestion(suggestion)

    return suggestion


def get_pending_suggestions():
    """获取待确认的买卖建议"""
    data = load_jar()
    pending = [s for s in data.get("suggestions", [])
               if s.get("status") == "pending_approval"]
    return pending


def approve_suggestion(index=-1, code=None):
    """
    老板确认执行某条建议
    参数:
      index: 建议列表中的索引（从0开始，-1=最新一条）
      code: 按代码匹配
    返回: 模拟盘交易结果或执行计划
    """
    data = load_jar()
    suggestions = data.get("suggestions", [])

    # 找到目标建议
    target = None
    if index >= 0 and index < len(suggestions):
        target = suggestions[index]
    elif code:
        for s in reversed(suggestions):
            if s.get("code") == code and s.get("status") == "pending_approval":
                target = s
                break
    else:
        # 默认最新一条待确认的
        for s in reversed(suggestions):
            if s.get("status") == "pending_approval":
                target = s
                break

    if not target:
        return {"success": False, "error": "没有找到待确认的建议"}

    # 标记为已确认
    target["status"] = "approved"
    target["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_jar(data)

    return {
        "success": True,
        "message": f"✅ 已确认: {target['name']}({target['code']}) - {target['action']}",
        "suggestion": target,
        "next_step": "需要执行模拟盘操作吗？请用 trade-log 操作"
    }


def execute_auto(decision_list, stock_quotes=None):
    """
    自动执行模式（仅 YOLO=OFF 时可用）
    目前先输出"可执行的交易计划"，未来对接券商API后真正下单

    返回: 交易计划
    """
    if check_yolo():
        return {"error": "🛡️ YOLO安全模式已开启，请先关闭才可自动执行"}

    plan = []
    for d in decision_list:
        action = d.get("action", "")
        code = d.get("code", "")
        name = d.get("name", "")

        if "买入" in action or "推荐" in action:
            # 建议仓位比例 = 综合评分 * 30%
            suggested_pct = min(d.get("overall_score", 0.5) * 0.3, 0.3)
            plan.append({
                "code": code,
                "name": name,
                "action": "BUY",
                "suggested_pct": round(suggested_pct, 2),
                "reason": d.get("reason", ""),
            })
        elif "减仓" in action or "回避" in action:
            plan.append({
                "code": code,
                "name": name,
                "action": "SELL",
                "reason": d.get("reason", ""),
            })

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "yolo_mode": False,
        "trade_plan": plan,
        "note": "这是自动生成的交易计划，对接券商API后可自动执行"
    }


if __name__ == "__main__":
    import sys
    yolo = check_yolo()
    print(f"🛡️ YOLO 安全模式: {'开启 ✅ (只建议，不执行)' if yolo else '关闭 ⚠️ (可以自动执行)'}")

    if len(sys.argv) > 1 and sys.argv[1] == "pending":
        pending = get_pending_suggestions()
        if pending:
            print(f"\n📋 待确认的建议 ({len(pending)}条):")
            for s in pending:
                print(f"  {s['name']}({s['code']}): {s['action']} - {s['reason']}")
        else:
            print("\n✅ 没有待确认的建议")
