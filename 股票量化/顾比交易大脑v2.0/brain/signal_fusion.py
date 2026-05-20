#!/usr/bin/env python3
"""
顾比交易大脑 — 信号融合引擎
技术分析 + 基本面 + 情绪 → 综合置信度评分 → 买卖建议

这是整个系统的核心决策引擎。
从 Vibe-Trading 的 Sage-OS 决策系统借鉴思路：
  多维度定性+定量打分 → 加权融合 → 综合建议
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain.config import WEIGHTS


def normalize_score(value, min_val=0, max_val=10):
    """将分数归一化到 0-1 区间"""
    if value is None:
        return 0.5
    return max(0, min(1, (value - min_val) / (max_val - min_val)))


def fusion_decision(technical_result, fundamental_result, sentiment_result, cookie_jar_summary=None):
    """
    三引擎融合决策

    参数:
      technical_result: 技术分析结果 (from daily-review or technical-indicators)
      fundamental_result: 基本面分析结果
      sentiment_result: 情绪分析结果 (总体情绪)
      cookie_jar_summary: 当前持仓概要

    返回:
      每个标的的融合评分 + 综合建议
    """
    fusion_results = []

    # 先提取技术面中每个标的的分析
    stock_analyses = technical_result.get("stock_analyses", [])
    technical_overall = technical_result.get("market_overview", {})

    # 情绪得分
    sentiment_score = sentiment_result.get("combined_score", 0)  # -1 ~ 1

    for sa in stock_analyses:
        code = sa.get("code", "?")
        name = sa.get("name", code)

        if "error" in sa:
            fusion_results.append({
                "code": code,
                "name": name,
                "error": sa["error"],
                "overall_score": 0,
                "action": "跳过",
                "reason": "数据异常"
            })
            continue

        # 1. 技术分 (0-1)
        tech_signals = sa.get("analysis", {}).get("signals", {})
        tech_score_raw = tech_signals.get("signal_score", 0)  # -5 ~ 5
        tech_score = normalize_score(tech_score_raw + 5, 0, 10)  # 映射到0-1

        # 2. 基本面分 (0-1)
        fund_score_raw = 5  # 默认中性
        fund_signal = ""
        for f in fundamental_result:
            if f.get("code") == code:
                fund_score_raw = f.get("fundamentals_score", 5)
                fund_signal = f.get("fundamentals_signal", "")
                break
        fund_score = normalize_score(fund_score_raw)  # 0-10映射到0-1

        # 3. 情绪分 (-1~1) 映射到 0-1
        sent_score = normalize_score(sentiment_score + 1, 0, 2)

        # 4. 加权融合
        overall = (
            tech_score * WEIGHTS["technical"]
            + fund_score * WEIGHTS["fundamental"]
            + sent_score * WEIGHTS["sentiment"]
            + tech_score * WEIGHTS["momentum"]  # 动量复用技术分
        )

        # 5. 生成行动建议
        if overall >= 0.75:
            action = "强烈推荐买入 🚀"
            confidence = "高"
            reason_parts = []
            if tech_score >= 0.7: reason_parts.append("技术面强势")
            if fund_score >= 0.7: reason_parts.append("基本面优秀")
            if sentiment_score >= 0.3: reason_parts.append("市场情绪积极")
            reason = " + ".join(reason_parts) if reason_parts else "综合评分高"

        elif overall >= 0.6:
            action = "建议买入 📗"
            confidence = "中高"
            reason_parts = []
            if tech_score >= 0.6: reason_parts.append(f"技术分{tech_score:.0%}")
            if fund_score >= 0.6: reason_parts.append(f"基本面{fund_score:.0%}")
            reason = " / ".join(reason_parts) if reason_parts else "评分尚可"

        elif overall >= 0.45:
            action = "中性观察 👀"
            confidence = "中等"
            # 看哪个维度最弱
            if tech_score < 0.4:
                reason = "技术面偏弱，等待信号"
            elif fund_score < 0.4:
                reason = "估值偏高，谨慎"
            else:
                reason = "多空平衡，观望"

        elif overall >= 0.3:
            action = "建议减仓 📕"
            confidence = "中低"
            reason = f"综合评分偏低({overall:.0%})"
        else:
            action = "强烈建议回避/止损 ❌"
            confidence = "高"
            reason = f"风险信号(综合评分{overall:.0%})"

        fusion_results.append({
            "code": code,
            "name": name,
            "tech_score": round(tech_score, 3),
            "fund_score": round(fund_score, 3),
            "sentiment_score": round(sent_score, 3),
            "overall_score": round(overall, 3),
            "action": action,
            "confidence": confidence,
            "reason": reason,
        })

    # 按综合评分排序
    fusion_results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

    # 生成全局策略
    overall_market = technical_overall.get("market_trend", "震荡")
    sentiment_advice = sentiment_result.get("advice", "")

    # 统计推荐
    buy_count = sum(1 for r in fusion_results if "买入" in r.get("action", "") or "推荐" in r.get("action", ""))
    sell_count = sum(1 for r in fusion_results if "回避" in r.get("action", "") or "减仓" in r.get("action", ""))
    hold_count = sum(1 for r in fusion_results if "观察" in r.get("action", ""))
    error_count = sum(1 for r in fusion_results if "跳过" in r.get("action", ""))

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "market_condition": overall_market,
        "market_sentiment": sentiment_advice,
        "fusion_signals": fusion_results,
        "statistics": {
            "total": len(fusion_results),
            "buy_signals": buy_count,
            "sell_signals": sell_count,
            "hold_signals": hold_count,
            "errors": error_count,
        },
        "market_risk_level": "高" if sell_count > buy_count * 2 else ("低" if buy_count > sell_count * 2 else "中"),
    }


if __name__ == "__main__":
    print("🤖 信号融合引擎 (Signal Fusion Core)")
    print("=" * 45)
    print("被 brain/trading_brain.py 调用，不独立运行")
