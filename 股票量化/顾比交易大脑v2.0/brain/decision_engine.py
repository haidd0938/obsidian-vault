#!/usr/bin/env python3
"""
顾比交易大脑 — 决策评分系统（决策仪表盘格式）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
参考 daily_stock_analysis 的决策仪表盘设计：
  综合评分(0-100) + 买卖点位 + 风险警报 + 检查清单

将原有 signal_fusion.py 的输出升级为"评分卡"格式。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import sys
import os
import json
from datetime import datetime

BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
ROBOT_DIR = os.path.dirname(BRAIN_DIR)
sys.path.insert(0, BRAIN_DIR)
sys.path.insert(0, ROBOT_DIR)

from brain.config import WATCHLIST


def build_decision_card(tech_analysis, fund_analysis, sentiment, kline_data=None):
    """
    为每个标的生成决策评分卡

    评分卡维度 (每项满分100):
    ─────────────────────────────────
    技术面 (权重40%) → MACD/KDJ/RSI/BOLL/MA形态综合
    基本面 (权重25%) → PE/PB/ROE估值评分
    情绪面 (权重20%) → 市场热点/板块热度
    趋势结构 (权重15%) → 均线排列/价格位置

    每项输出:
      ✅ 评分 (0-100)
      ✅ 买卖点建议 (价格区间)
      ✅ 风险警报 (红色/黄色/绿色)
      ✅ 检查清单 (可执行事项)
      ✅ 支撑位/压力位
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cards = []

    for item in tech_analysis:
        code = item.get("code", "")
        name = item.get("name", code)
        t_sig = item.get("analysis", {}).get("signals", {})
        t_summary = item.get("analysis", {}).get("summary", "")

        if "error" in item:
            cards.append({
                "code": code,
                "name": name,
                "status": "error",
                "score": 0,
                "grade": "D",
                "message": item["error"],
            })
            continue

        # 1️⃣ 技术面评分 (0-100)
        signal_score = t_sig.get("signal_score", 0)  # -5 ~ 5
        tech_score = min(100, max(0, int((signal_score + 5) / 10 * 100)))

        # 技术面子维度诊断
        tech_detail = _diagnose_technical(t_summary)

        # 2️⃣ 基本面评分 (0-100)
        fund_score = 50  # 默认中性
        fund_detail = {}
        for f in fund_analysis:
            if f.get("code") == code:
                fund_raw = f.get("fundamentals_score", 5)  # 0-10
                fund_score = min(100, max(0, int(fund_raw * 10)))
                fund_detail = f.get("scores", {})
                break

        # 3️⃣ 情绪评分 (0-100)
        combined = sentiment.get("combined_score", 0)  # -1 ~ 1
        sent_score = min(100, max(0, int((combined + 1) / 2 * 100)))

        # 4️⃣ 趋势结构评分 (0-100)
        trend_score = _score_trend_structure(item, kline_data)

        # 加权总分
        overall = int(
            tech_score * 0.40
            + fund_score * 0.25
            + sent_score * 0.20
            + trend_score * 0.15
        )

        # 评级
        grade, color = _grade_score(overall)

        # 买卖点位
        entry_zone, exit_zone = _calc_price_zones(item, kline_data)

        # 风险警报
        alerts = _generate_alerts(tech_score, fund_score, sent_score, trend_score, item)

        # 检查清单
        checklist = _generate_checklist(tech_score, fund_score, sent_score, trend_score)

        # 支撑 / 压力位
        supports, resistances = _calc_support_resistance(item, kline_data)

        cards.append({
            "code": code,
            "name": name,
            "timestamp": timestamp,
            "status": "ok",
            # 综合评分
            "overall_score": overall,
            "grade": grade,
            "color": color,
            # 各维度详情
            "dimensions": {
                "technical": {"score": tech_score, "detail": tech_detail},
                "fundamental": {"score": fund_score, "detail": fund_detail},
                "sentiment": {"score": sent_score, "detail": {"source": sentiment.get("overall_sentiment", "中性")}},
                "trend_structure": {"score": trend_score, "detail": {"trend": item.get("analysis", {}).get("signals", {}).get("signal_strength", "中性")}},
            },
            # 操作建议
            "action": {
                "signal": t_sig.get("signal_strength", "中性"),
                "entry_zone": entry_zone,
                "exit_zone": exit_zone,
                "suggestion": _gen_action_suggestion(overall),
            },
            # 风险
            "risk_alerts": alerts,
            "risk_level": _risk_level(alerts),
            # 检查清单
            "checklist": checklist,
            # 技术参考
            "support_levels": supports,
            "resistance_levels": resistances,
        })

    return cards


def _diagnose_technical(summary_text):
    """分析技术面各子维度"""
    result = {}
    if not summary_text:
        return result

    summary_lower = str(summary_text).lower()

    # MACD方向
    if "macd" in summary_lower:
        if "金叉" in summary_text or "多头" in summary_text:
            result["macd"] = "金叉 ✅"
        elif "死叉" in summary_text or "空头" in summary_text:
            result["macd"] = "死叉 ❌"
        elif "零轴" in summary_text:
            result["macd"] = "零轴附近 ⚠️"
        else:
            result["macd"] = "观察"

    # KDJ
    if "k" in summary_lower or "kdj" in summary_lower:
        if "超卖" in summary_text:
            result["kdj"] = "超卖 (反弹机会) ⚡"
        elif "超买" in summary_text:
            result["kdj"] = "超买 (回调风险) ⚠️"
        else:
            result["kdj"] = "中性区间"
    else:
        # 从句子中提取
        result["kdj"] = "中性"

    # 均线形态
    if "多头排列" in summary_text:
        result["ma"] = "多头排列 📈"
    elif "空头排列" in summary_text:
        result["ma"] = "空头排列 📉"
    elif "交叉" in summary_text:
        result["ma"] = "均线交叉中"
    else:
        result["ma"] = "中性"

    return result


def _score_trend_structure(item, kline_data=None):
    """评估趋势结构分数"""
    signals = item.get("analysis", {}).get("signals", {})
    signal_score = signals.get("signal_score", 0)
    strength = signals.get("signal_strength", "")

    # 从signal_score映射到趋势结构分数
    if signal_score >= 3:
        return 80
    elif signal_score >= 1:
        return 60
    elif signal_score >= -1:
        return 50
    elif signal_score >= -3:
        return 30
    else:
        return 15


def _grade_score(score):
    """根据总分评级"""
    if score >= 80:
        return "A+", "#00cc66"
    elif score >= 70:
        return "A", "#22aa44"
    elif score >= 60:
        return "B+", "#668822"
    elif score >= 50:
        return "B", "#aa8800"
    elif score >= 40:
        return "C+", "#dd6600"
    elif score >= 30:
        return "C", "#ee4400"
    else:
        return "D", "#cc0000"


def _calc_price_zones(item, kline_data=None):
    """计算买卖价格区间"""
    entry_zone = {"reason": "待更多数据确定", "low": None, "high": None}
    exit_zone = {"reason": "待更多数据确定", "low": None, "high": None}

    if kline_data and kline_data.get(item.get("code", "")):
        klines = kline_data[item["code"]].get("klines", [])
        if len(klines) >= 20:
            closes = [k.get("close", 0) for k in klines[-20:]]
            highs = [k.get("high", 0) for k in klines[-20:]]
            lows = [k.get("low", 0) for k in klines[-20:]]
            ma20 = sum(closes) / 20
            recent_high = max(highs)
            recent_low = min(lows)

            entry_zone = {
                "reason": f"MA20附近({ma20:.2f})为参考买入区间",
                "low": round(recent_low, 2),
                "high": round(ma20 * 1.02, 2),
            }
            exit_zone = {
                "reason": f"近期高点({recent_high:.2f})附近为参考卖出区间",
                "low": round(recent_high * 0.98, 2),
                "high": round(recent_high, 2),
            }

    return entry_zone, exit_zone


def _calc_support_resistance(item, kline_data=None):
    """计算支撑位和压力位"""
    supports = []
    resistances = []

    if kline_data and kline_data.get(item.get("code", "")):
        klines = kline_data[item["code"]].get("klines", [])
        if len(klines) >= 30:
            closes = [k.get("close", 0) for k in klines[-30:]]
            highs = [k.get("high", 0) for k in klines[-30:]]
            lows = [k.get("low", 0) for k in klines[-30:]]
            ma10 = sum(closes[-10:]) / 10
            ma20 = sum(closes[-20:]) / 20
            ma30 = sum(closes) / 30

            supports = [
                f"MA20({ma20:.2f})",
                f"近期低点({min(lows):.2f})",
                f"MA30({ma30:.2f})",
            ]
            resistances = [
                f"MA10({ma10:.2f})",
                f"近期高点({max(highs):.2f})",
            ]

    return supports, resistances


def _generate_alerts(tech, fund, sent, trend, item):
    """生成风险警报列表"""
    alerts = []

    # 技术面风险
    if tech < 30:
        alerts.append({"type": "danger", "message": "技术面极度弱势，反弹减仓机会"})
    elif tech < 50:
        alerts.append({"type": "warning", "message": "技术面偏弱，等待企稳信号"})

    # 基本面风险
    if fund < 30:
        alerts.append({"type": "danger", "message": "基本面评分低，注意估值压力"})
    elif fund < 50:
        alerts.append({"type": "warning", "message": "估值偏高，注意性价比"})

    # 情绪面
    if sent < 30:
        alerts.append({"type": "danger", "message": "市场情绪消极，短期承压"})

    # 趋势结构
    signal = item.get("analysis", {}).get("signals", {}).get("signal_strength", "")
    if "空" in signal or "跌" in signal:
        alerts.append({"type": "warning", "message": "下行趋势中，不宜抄底"})

    if not alerts:
        alerts.append({"type": "safe", "message": "无明显风险信号"})

    return alerts


def _risk_level(alerts):
    """计算整体风险等级"""
    if any(a["type"] == "danger" for a in alerts):
        return "高风险 🔴"
    if any(a["type"] == "warning" for a in alerts):
        return "中等风险 🟡"
    return "低风险 🟢"


def _generate_checklist(tech, fund, sent, trend):
    """生成操作检查清单"""
    checklist = []

    if tech >= 60:
        checklist.append("✅ 技术面确认强势，可考虑建仓")
    elif tech >= 40:
        checklist.append("⬜ 等待技术面信号确认")
    else:
        checklist.append("❌ 技术面不宜入场")

    if fund >= 60:
        checklist.append("✅ 估值合理")
    elif fund >= 40:
        checklist.append("⬜ 估值偏高，控制仓位")
    else:
        checklist.append("❌ 估值过高，远离")

    if sent >= 60:
        checklist.append("✅ 情绪面支持做多")
    elif sent >= 40:
        checklist.append("⬜ 情绪中性，观望为主")
    else:
        checklist.append("⚠️ 情绪偏空，注意风险")

    if trend >= 60:
        checklist.append("✅ 趋势结构良好")
    elif trend >= 40:
        checklist.append("⬜ 趋势待确认")
    else:
        checklist.append("❌ 趋势向下")

    return checklist


def _gen_action_suggestion(score):
    """生成总体操作建议"""
    if score >= 80:
        return "🚀 强烈推荐买入 — 多个维度共振，积极建仓"
    elif score >= 70:
        return "📗 建议买入 — 各项指标向好，分批建仓"
    elif score >= 60:
        return "📘 增持 — 趋势向好，有回调可加仓"
    elif score >= 50:
        return "👀 中性观望 — 信号不明确，等待方向"
    elif score >= 40:
        return "📕 谨慎 — 部分维度偏弱，减少操作"
    elif score >= 30:
        return "🔴 建议减仓 — 风险信号增多"
    else:
        return "❌ 强烈建议回避 — 全维度风险"


def print_decision_cards(cards):
    """输出美观的决策评分卡"""
    lines = []
    lines.append("=" * 55)
    lines.append(f"📋 顾比决策仪表盘 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 55)
    lines.append("")

    ok_cards = [c for c in cards if c.get("status") == "ok"]
    error_cards = [c for c in cards if c.get("status") != "ok"]

    for card in ok_cards:
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        grade_color = card.get("color", "#888")
        grade = card.get("grade", "?")
        score = card.get("overall_score", 0)
        lines.append(f"🏷️  {card['name']}({card['code']})")
        lines.append(f"   评分: {score}/100  |  评级: [{grade}]  |  风险: {card.get('risk_level', '?')}")

        dims = card.get("dimensions", {})
        lines.append(f"   技术面: {dims.get('technical', {}).get('score', '?')}分 | "
                     f"基本面: {dims.get('fundamental', {}).get('score', '?')}分 | "
                     f"情绪面: {dims.get('sentiment', {}).get('score', '?')}分 | "
                     f"趋势: {dims.get('trend_structure', {}).get('score', '?')}分")

        action = card.get("action", {})
        lines.append(f"   💡 {action.get('suggestion', '?')}")

        # 支撑/压力
        supports = card.get("support_levels", [])
        resistances = card.get("resistance_levels", [])
        if supports or resistances:
            lines.append(f"   🔽 支撑位: {'  '.join(supports[:3])}")
        if resistances:
            lines.append(f"   🔼 压力位: {'  '.join(resistances[:3])}")

        # 风险警报
        alerts = card.get("risk_alerts", [])
        if alerts:
            for a in alerts:
                icon = {"danger": "🔴", "warning": "⚠️", "safe": "✅"}.get(a.get("type", ""), "•")
                lines.append(f"   {icon} {a['message']}")

        # 检查清单
        checklist = card.get("checklist", [])
        if checklist:
            lines.append(f"   📋 检查清单:")
            for item in checklist:
                lines.append(f"     {item}")

        lines.append("")

    if error_cards:
        lines.append("❌ 数据异常标的:")
        for c in error_cards:
            lines.append(f"   {c['name']}({c['code']}): {c.get('message', '?')}")
        lines.append("")

    # 汇总统计
    if ok_cards:
        a_count = sum(1 for c in ok_cards if c.get("grade", "") in ("A+", "A", "B+"))
        b_count = sum(1 for c in ok_cards if c.get("grade", "") in ("B", "C+"))
        c_count = sum(1 for c in ok_cards if c.get("grade", "") in ("C", "D"))
        avg_score = sum(c.get("overall_score", 0) for c in ok_cards) / len(ok_cards)
        lines.append(f"📊 汇总: {len(ok_cards)}只分析 | "
                     f"A区{a_count} | B区{b_count} | C区{c_count} | "
                     f"平均分{avg_score:.0f}")

    lines.append("=" * 55)
    return "\n".join(lines)


if __name__ == "__main__":
    print("📋 顾比决策评分系统 (Decision Card System)")
    print("被 trading_brain.py 调用，不独立运行")
    print()
    print("参考 daily_stock_analysis 的决策仪表盘设计，将现有信号")
    print("升级为: 综合评分(0-100) + 买卖点位 + 风险警报 + 检查清单")
