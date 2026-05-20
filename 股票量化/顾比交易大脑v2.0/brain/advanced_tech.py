#!/usr/bin/env python3
"""
顾比交易大脑 — 缠论/波浪/高级技术分析模块
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
参考 Vibe-Trading 的开源实现思路，实现缠论核心算法：
  分型识别 → 笔划分 → 中枢判定 → 买卖点识别
以及艾略特波浪理论的基础实现。

独立模块，可被 technical-indicators.py 或 决策引擎调用。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import sys
import os
import math
from datetime import datetime


# ======================================================================
#  缠论 (Chan Theory) 核心算法
# ======================================================================

def find_fractals(klines, period=5):
    """
    识别分型（顶分型 / 底分型）

    顶分型条件：中间K线最高点是3根中最高，左右两边更低
    底分型条件：中间K线最低点是3根中最低，左右两边更高

    参数:
      klines: K线列表 [{"high": h, "low": l, "close": c, "date": d}, ...]
      period: 分型检查周期 (默认5，意味着看左右各2根)

    返回:
      fractals: [{type, index, high, low, date, strength}, ...]
    """
    fractals = []
    n = len(klines)

    half = period // 2  # 左右各看几步

    for i in range(half, n - half):
        current = klines[i]
        c_high = current["high"]
        c_low = current["low"]

        # 检查顶分型：中间最高
        is_top = True
        for j in range(1, half + 1):
            if klines[i - j]["high"] >= c_high or klines[i + j]["high"] >= c_high:
                is_top = False
                break

        # 检查底分型：中间最低
        is_bottom = True
        for j in range(1, half + 1):
            if klines[i - j]["low"] <= c_low or klines[i + j]["low"] <= c_low:
                is_bottom = False
                break

        if is_top:
            # 强度：左右高点与中间高点的差距之和
            left_avg = sum(klines[i - j]["high"] for j in range(1, half + 1)) / half
            right_avg = sum(klines[i + j]["high"] for j in range(1, half + 1)) / half
            strength = round((c_high - left_avg) + (c_high - right_avg), 2)

            fractals.append({
                "type": "顶分型",
                "index": i,
                "high": c_high,
                "low": c_low,
                "date": current.get("date", ""),
                "strength": strength,
            })

        if is_bottom:
            # 强度：中间低点与左右低点的差距
            left_avg = sum(klines[i - j]["low"] for j in range(1, half + 1)) / half
            right_avg = sum(klines[i + j]["low"] for j in range(1, half + 1)) / half
            strength = round((left_avg - c_low) + (right_avg - c_low), 2)

            fractals.append({
                "type": "底分型",
                "index": i,
                "high": c_high,
                "low": c_low,
                "date": current.get("date", ""),
                "strength": strength,
            })

    return fractals


def identify_bi_segments(fractals):
    """
    将分型连接为笔（Bi）
    顶分型和底分型交替连接形成笔。

    规则：
    1. 从底分型开始 → 顶分型 → 底分型 → ...
    2. 顶分型必须高于前一个底分型
    3. 底分型必须低于前一个顶分型

    返回:
      bi_segments: [{type, start_idx, end_idx, start_price, end_price, length}, ...]
    """
    if len(fractals) < 2:
        return []

    # 按index排序
    sorted_f = sorted(fractals, key=lambda x: x["index"])

    # 决定从哪开始：找第一个顶或底
    segments = []
    i = 0

    # 找第一个有效对
    while i < len(sorted_f) - 1:
        current = sorted_f[i]
        next_f = sorted_f[i + 1]
        gap = next_f["index"] - current["index"]

        # 必须有一定距离才构成笔（至少3根K线）
        if gap < 3:
            i += 1
            continue

        # 顶分型必须在底分型之上
        if current["type"] == "底分型" and next_f["type"] == "顶分型":
            if next_f["high"] > current["low"]:
                segments.append({
                    "type": "上升笔",
                    "start_idx": current["index"],
                    "end_idx": next_f["index"],
                    "start_price": current["low"],
                    "end_price": next_f["high"],
                    "start_date": current.get("date", ""),
                    "end_date": next_f.get("date", ""),
                    "length": next_f["high"] - current["low"],
                    "strength": round(
                        (next_f.get("strength", 0) + current.get("strength", 0)) / 2, 2
                    ),
                })
                segments[-1]["price_change_pct"] = round(
                    segments[-1]["length"] / current["low"] * 100, 2
                )
                i += 1
                break

        if current["type"] == "顶分型" and next_f["type"] == "底分型":
            if current["high"] > next_f["low"]:
                segments.append({
                    "type": "下降笔",
                    "start_idx": current["index"],
                    "end_idx": next_f["index"],
                    "start_price": current["high"],
                    "end_price": next_f["low"],
                    "start_date": current.get("date", ""),
                    "end_date": next_f.get("date", ""),
                    "length": current["high"] - next_f["low"],
                    "strength": round(
                        (current.get("strength", 0) + next_f.get("strength", 0)) / 2, 2
                    ),
                })
                segments[-1]["price_change_pct"] = round(
                    -segments[-1]["length"] / current["high"] * 100, 2
                )
                i += 1
                break

        i += 1

    # 继续连接
    while i < len(sorted_f) - 1:
        current = sorted_f[i]
        next_f = sorted_f[i + 1]
        gap = next_f["index"] - current["index"]

        if gap < 3:
            i += 1
            continue

        last_type = segments[-1]["type"] if segments else None

        if last_type == "上升笔" and current["type"] == "顶分型" and next_f["type"] == "底分型":
            if current["high"] > next_f["low"]:
                segments.append({
                    "type": "下降笔",
                    "start_idx": current["index"],
                    "end_idx": next_f["index"],
                    "start_price": current["high"],
                    "end_price": next_f["low"],
                    "start_date": current.get("date", ""),
                    "end_date": next_f.get("date", ""),
                    "length": current["high"] - next_f["low"],
                    "strength": round(
                        (current.get("strength", 0) + next_f.get("strength", 0)) / 2, 2
                    ),
                })
                segments[-1]["price_change_pct"] = round(
                    -segments[-1]["length"] / current["high"] * 100, 2
                )

        elif last_type == "下降笔" and current["type"] == "底分型" and next_f["type"] == "顶分型":
            if next_f["high"] > current["low"]:
                segments.append({
                    "type": "上升笔",
                    "start_idx": current["index"],
                    "end_idx": next_f["index"],
                    "start_price": current["low"],
                    "end_price": next_f["high"],
                    "start_date": current.get("date", ""),
                    "end_date": next_f.get("date", ""),
                    "length": next_f["high"] - current["low"],
                    "strength": round(
                        (current.get("strength", 0) + next_f.get("strength", 0)) / 2, 2
                    ),
                })
                segments[-1]["price_change_pct"] = round(
                    segments[-1]["length"] / current["low"] * 100, 2
                )

        i += 1

    return segments


def find_trading_zones(bi_segments):
    """
    识别缠论中枢（Trading Zone / 走势中枢）

    中枢定义：至少3笔重叠区域
    第1笔的高点、第2笔的低点、第3笔的高点... 重叠部分

    返回:
      zones: [{start_idx, end_idx, zone_high, zone_low, midpoint, type}, ...]
    """
    zones = []
    if len(bi_segments) < 3:
        return zones

    # 至少需要3笔才能形成中枢
    for i in range(len(bi_segments) - 2):
        b1 = bi_segments[i]
        b2 = bi_segments[i + 1]
        b3 = bi_segments[i + 2]

        # 计算三笔重叠区域
        highs = [b1["start_price"] if b1["type"] == "上升笔" else b1["end_price"],
                 b1["end_price"] if b1["type"] == "上升笔" else b1["start_price"],
                 b2["start_price"] if b2["type"] == "上升笔" else b2["end_price"],
                 b2["end_price"] if b2["type"] == "上升笔" else b2["start_price"],
                 b3["start_price"] if b3["type"] == "上升笔" else b3["end_price"],
                 b3["end_price"] if b3["type"] == "上升笔" else b3["start_price"]]

        if len(highs) >= 6:
            h_min = min(highs[0], highs[2], highs[4])  # 最低的"高"
            h_max = max(highs[1], highs[3], highs[5])  # 最高的"低"
            # 所有的低点
            lows = highs[1::2]
            l_max = max(lows)

            zone_high = h_min  # 中枢上沿
            zone_low = l_max  # 中枢下沿

            if zone_high > zone_low:  # 有效的重叠区域
                zones.append({
                    "zone_high": round(zone_high, 2),
                    "zone_low": round(zone_low, 2),
                    "midpoint": round((zone_high + zone_low) / 2, 2),
                    "start_idx": b1["start_idx"],
                    "end_idx": b3["end_idx"],
                    "start_date": b1.get("start_date", ""),
                    "end_date": b3.get("end_date", ""),
                    "width": round(zone_high - zone_low, 2),
                    "type": "中枢",
                })

    # 合并重叠的中枢
    merged = []
    for zone in zones:
        if not merged:
            merged.append(zone)
        else:
            last = merged[-1]
            # 如果区间重叠或接近，合并
            if min(zone["zone_high"], last["zone_high"]) > max(zone["zone_low"], last["zone_low"]):
                last["zone_high"] = max(zone["zone_high"], last["zone_high"])
                last["zone_low"] = min(zone["zone_low"], last["zone_low"])
                last["midpoint"] = round((last["zone_high"] + last["zone_low"]) / 2, 2)
                last["width"] = round(last["zone_high"] - last["zone_low"], 2)
            else:
                merged.append(zone)

    return merged


def find_buy_sell_points(klines, zones, bi_segments):
    """
    识别缠论一/二/三类买卖点

    一类买点：下跌趋势中，第一个中枢下方出现底分型
    二类买点：突破第一个中枢后回踩不破
    三类买点：突破中枢后回踩不破中枢上沿

    卖点同理反向。
    """
    if not klines or len(klines) < 30:
        return {"buy_points": [], "sell_points": []}

    current_price = klines[-1]["close"]
    buy_points = []
    sell_points = []

    # 当前价格相对于中枢的位置
    for zone in zones:
        if not zone:
            continue
        z_high = zone["zone_high"]
        z_low = zone["zone_low"]

        # 一类买点：价格突破中枢下沿后反弹
        if current_price > z_low * 0.97 and current_price < z_low * 1.03:
            buy_points.append({
                "type": "第一类买点",
                "price_zone": f"{z_low:.2f}附近",
                "confidence": "中等",
                "note": "中枢下沿附近企稳，关注反弹力度",
            })

        # 二类买点：价格在中枢上方回踩中枢上沿
        if current_price > z_high and current_price < z_high * 1.05:
            buy_points.append({
                "type": "第二类买点",
                "price_zone": f"{z_high:.2f}附近",
                "confidence": "较高",
                "note": "突破中枢后回踩确认，可建仓",
            })

        # 三类买点：价格远高于中枢，回踩不破中枢上沿
        if current_price > z_high * 1.05 and current_price > z_high * 0.98:
            buy_points.append({
                "type": "第三类买点",
                "price_zone": f"{z_high:.2f}-{current_price:.2f}",
                "confidence": "高",
                "note": "强势突破中枢，趋势确立",
            })

        # 一类卖点：价格跌破中枢上沿后回踩不破
        if current_price < z_low * 1.03 and current_price > z_low * 0.97:
            sell_points.append({
                "type": "第一类卖点",
                "price_zone": f"{z_low:.2f}附近",
                "confidence": "较高",
                "note": "跌破中枢下沿，可能走弱",
            })

    if not buy_points:
        buy_points.append({
            "type": "无明确买点",
            "price_zone": "-",
            "confidence": "-",
            "note": "不在中枢买卖点区域，关注后续走势",
        })

    if not sell_points:
        sell_points.append({
            "type": "无明确卖点",
            "price_zone": "-",
            "confidence": "-",
            "note": "当前不在缠论卖点区域",
        })

    return {"buy_points": buy_points, "sell_points": sell_points}


# ======================================================================
#  艾略特波浪理论 (Elliott Wave) 基础
# ======================================================================

def elliott_wave_analysis(klines):
    """
    艾略特波浪基础分析

    主要识别：
    1. 当前处于推动浪（1/3/5浪）还是调整浪（2/4浪）
    2. 通过RSI背离判断浪型位置

    简化实现：通过短期/中期趋势的关系推断波浪位置
    """
    if len(klines) < 30:
        return {"wave_position": "数据不足", "confidence": "低"}

    closes = [k["close"] for k in klines[-50:]]
    highs = [k["high"] for k in klines[-50:]]
    lows = [k["low"] for k in klines[-50:]]

    # 找局部高点和低点
    n = len(closes)
    peaks = []
    troughs = []

    for i in range(5, n - 5):
        if closes[i] == max(closes[i - 5:i + 6]):
            peaks.append({"index": i, "price": closes[i], "date": klines[-(n - i)].get("date", "") if i < n else ""})
        if closes[i] == min(closes[i - 5:i + 6]):
            troughs.append({"index": i, "price": closes[i], "date": klines[-(n - i)].get("date", "") if i < n else ""})

    if len(peaks) < 2 or len(troughs) < 2:
        return {"wave_position": "无法识别", "confidence": "低"}

    latest = closes[-1]
    peak0 = peaks[-1]["price"] if peaks else latest
    trough0 = troughs[-1]["price"] if troughs else latest
    peak1 = peaks[-2]["price"] if len(peaks) >= 2 else peak0
    trough1 = troughs[-2]["price"] if len(troughs) >= 2 else trough0

    # 简单的波浪位置判断
    if latest > peak0 and peak0 > peak1:
        # 创新高 → 可能是推动浪
        wave_prob = "第3浪或第5浪"
    elif latest > trough0 and latest < peak0:
        # 反弹中 → 可能是第4浪调整
        wave_prob = "第4浪调整"
    elif latest < trough0 and trough0 < trough1:
        # 创新低 → 可能是C浪下跌
        wave_prob = "C浪下跌"
    elif latest > trough0 and latest < peak0 * 0.618 + trough0 * 0.382:
        # 在黄金分割位附近
        wave_prob = "回调浪（黄金分割位附近）"
    elif latest > peak0 - (peak0 - trough0) * 0.618:
        wave_prob = "回调接近0.618，可能是第2浪或第4浪"
    else:
        wave_prob = "趋势待确认"

    # 参考Rsi背离（简化）
    rsi_val = _simple_rsi(closes, 14)
    rsi_divergence = ""
    if rsi_val is not None:
        if rsi_val > 70 and latest <= peak0:
            rsi_divergence = "RSI顶背离，警惕反转"
        elif rsi_val < 30 and latest >= trough0:
            rsi_divergence = "RSI底背离，可能反弹"

    return {
        "wave_position": wave_prob,
        "peaks": len(peaks),
        "troughs": len(troughs),
        "last_peak": round(peak0, 2),
        "last_trough": round(trough0, 2),
        "rsi": round(rsi_val, 1) if rsi_val else None,
        "rsi_divergence": rsi_divergence,
        "confidence": "中" if len(peaks) >= 3 else "低",
    }


def _simple_rsi(closes, period=14):
    """简化的RSI计算，用于波浪分析"""
    if len(closes) <= period:
        return None

    gains = 0
    losses = 0
    for i in range(-period, -1):
        diff = closes[i + 1] - closes[i]
        if diff > 0:
            gains += diff
        else:
            losses -= diff

    avg_gain = gains / period
    avg_loss = losses / period

    for i in range(0, min(period, len(closes) - period)):
        diff = closes[-len(closes) + period + i] - closes[-len(closes) + period + i - 1]
        if diff > 0:
            avg_gain = (avg_gain * (period - 1) + diff) / period
            avg_loss = (avg_loss * (period - 1)) / period
        else:
            avg_loss = (avg_loss * (period - 1) - diff) / period
            avg_gain = (avg_gain * (period - 1)) / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ======================================================================
#  一目均衡表 (Ichimoku Cloud) 基础
# ======================================================================

def ichimoku_cloud(klines):
    """
    一目均衡表（Ichimoku Cloud）分析

    5条线：
    1. 转换线(Tenkan-sen)：(9日高+9日低)/2
    2. 基准线(Kijun-sen)：(26日高+26日低)/2
    3. 先行线A(Senkou A)：(转换+基准)/2，向前移26日
    4. 先行线B(Senkou B)：(52日高+52日低)/2，向前移26日
    5. 延迟线(Chikou)：当日收盘价向后移26日
    """
    if len(klines) < 60:
        return {}

    highs = [k["high"] for k in klines]
    lows = [k["low"] for k in klines]
    closes = [k["close"] for k in klines]

    n = len(klines)

    # 转换线 (9日)
    h9 = max(highs[-9:]) if n >= 9 else max(highs)
    l9 = min(lows[-9:]) if n >= 9 else min(lows)
    tenkan = (h9 + l9) / 2

    # 基准线 (26日)
    h26 = max(highs[-26:]) if n >= 26 else max(highs)
    l26 = min(lows[-26:]) if n >= 26 else min(lows)
    kijun = (h26 + l26) / 2

    # 先行线 (52日)
    h52 = max(highs[-52:]) if n >= 52 else max(highs)
    l52 = min(lows[-52:]) if n >= 52 else min(lows)
    senkou_b = (h52 + l52) / 2

    # 先行线A
    senkou_a = (tenkan + kijun) / 2

    current_price = closes[-1]

    # 云层判断
    cloud_top = max(senkou_a, senkou_b)
    cloud_bottom = min(senkou_a, senkou_b)
    in_cloud = current_price >= cloud_bottom and current_price <= cloud_top
    above_cloud = current_price > cloud_top
    below_cloud = current_price < cloud_bottom

    # 信号判断
    signals = []
    if above_cloud and tenkan > kijun:
        signals.append("☀️ 云层上方+转换>基准 → 强势多头")
    elif above_cloud:
        signals.append("🌤️ 云层上方 → 多头趋势")
    elif in_cloud:
        signals.append("☁️ 在云层内 → 趋势待确认")
    elif below_cloud and tenkan < kijun:
        signals.append("🌧️ 云层下方+转换<基准 → 弱势空头")
    else:
        signals.append("🌥️ 云层下方 → 空头趋势")

    return {
        "tenkan": round(tenkan, 2),
        "kijun": round(kijun, 2),
        "senkou_a": round(senkou_a, 2),
        "senkou_b": round(senkou_b, 2),
        "cloud_top": round(cloud_top, 2),
        "cloud_bottom": round(cloud_bottom, 2),
        "relative_position": "云层上方" if above_cloud else ("云层内" if in_cloud else "云层下方"),
        "signals": signals,
    }


# ======================================================================
#  整合分析入口
# ======================================================================

def advanced_technical_analysis(klines):
    """
    高级技术分析入口：缠论+波浪+一目均衡

    参数:
      klines: K线列表

    返回:
      {
        "chan_theory": {...},       # 缠论结果
        "elliott_wave": {...},      # 波浪结果
        "ichimoku": {...},          # 一目均衡
        "summary": "..."            # 文字总结
      }
    """
    if not klines or len(klines) < 30:
        return {"error": "K线数据不足（需至少30条）"}

    # 1. 缠论分析
    fractals = find_fractals(klines, period=5)
    bi_segments = identify_bi_segments(fractals)
    zones = find_trading_zones(bi_segments)
    buy_sell = find_buy_sell_points(klines, zones, bi_segments)

    chan_result = {
        "fractal_count": len(fractals),
        "top_fractals": sum(1 for f in fractals if f["type"] == "顶分型"),
        "bottom_fractals": sum(1 for f in fractals if f["type"] == "底分型"),
        "bi_count": len(bi_segments),
        "up_bi": sum(1 for b in bi_segments if b["type"] == "上升笔"),
        "down_bi": sum(1 for b in bi_segments if b["type"] == "下降笔"),
        "zone_count": len(zones),
        "zones": zones[-3:] if zones else [],
        # 最近的笔方向
        "last_bi_type": bi_segments[-1]["type"] if bi_segments else "无",
        "buy_sell_points": buy_sell,
    }

    # 2. 波浪分析
    wave_result = elliott_wave_analysis(klines)

    # 3. 一目均衡
    ichi_result = ichimoku_cloud(klines) if len(klines) >= 60 else {}

    # 4. 综合总结
    summary_parts = []

    # 缠论总结
    if bi_segments:
        last_bi = bi_segments[-1]
        change = last_bi.get("price_change_pct", 0)
        up_down = "上涨" if change > 0 else "下跌"
        summary_parts.append(
            f"缠论: 最近一笔为{last_bi['type']}(幅度{up_down}{abs(change):.1f}%)"
        )
    if zones:
        z = zones[-1]
        summary_parts.append(f"中枢区间[{z['zone_low']:.2f}~{z['zone_high']:.2f}]")
        buy_pts = buy_sell["buy_points"]
        if buy_pts and "无明确" not in buy_pts[0]["type"]:
            summary_parts.append(f"买点: {buy_pts[0]['type']}@{buy_pts[0]['price_zone']}")

    # 波浪总结
    summary_parts.append(f"波浪: {wave_result.get('wave_position', '未知')}")
    if wave_result.get("rsi_divergence"):
        summary_parts.append(wave_result["rsi_divergence"])

    # 一目均衡总结
    if ichi_result and ichi_result.get("signals"):
        summary_parts.append(f"一目: {ichi_result['signals'][0]}")

    summary = " | ".join(summary_parts) if summary_parts else "高级分析数据不足"

    return {
        "chan_theory": chan_result,
        "elliott_wave": wave_result,
        "ichimoku": ichi_result,
        "summary": summary,
    }


def print_advanced_analysis(result):
    """输出高级分析结果"""
    if "error" in result:
        return f"❌ {result['error']}"

    lines = []
    lines.append("━━━ 高级技术分析 ━━━")

    # 缠论
    chan = result.get("chan_theory", {})
    if chan:
        lines.append(f"【缠论】")
        lines.append(f"  分型: {chan.get('top_fractals', 0)}顶/ {chan.get('bottom_fractals', 0)}底 | "
                     f"笔: {chan.get('up_bi', 0)}升/ {chan.get('down_bi', 0)}降 | "
                     f"中枢: {chan.get('zone_count', 0)}个")
        if chan.get("zones"):
            for z in chan["zones"]:
                lines.append(f"  中枢: [{z['zone_low']:.2f} - {z['zone_high']:.2f}] 中点{z['midpoint']:.2f}")
        bp = chan.get("buy_sell_points", {})
        if bp.get("buy_points"):
            for b in bp["buy_points"][:2]:
                lines.append(f"  🟢 {b['type']}: {b.get('price_zone', '')} - {b.get('note', '')}")
        if bp.get("sell_points"):
            for s in bp["sell_points"][:2]:
                lines.append(f"  🔴 {s['type']}: {s.get('price_zone', '')} - {s.get('note', '')}")

    # 波浪
    wave = result.get("elliott_wave", {})
    if wave:
        lines.append(f"【波浪理论】")
        lines.append(f"  位置: {wave.get('wave_position', '?')}")
        if wave.get("rsi_divergence"):
            lines.append(f"  ⚡ {wave['rsi_divergence']}")

    # 一目均衡
    ichi = result.get("ichimoku", {})
    if ichi:
        lines.append(f"【一目均衡表】")
        lines.append(f"  位置: {ichi.get('relative_position', '?')}")
        if ichi.get("signals"):
            for s in ichi["signals"][:1]:
                lines.append(f"  {s}")

    # 综合总结
    summary = result.get("summary", "")
    if summary:
        lines.append(f"【综合】{summary}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("""
┌───────────────────────────────────────┐
│ 📐 高级技术分析引擎                      │
│   缠论 + 艾略特波浪 + 一目均衡表          │
└───────────────────────────────────────┘

被 technical-indicators.py 或 决策引擎调用，不独立运行。

依赖: K线数据 (至少30条，推荐60条以上)
使用方法:
  from brain.advanced_tech import advanced_technical_analysis
  result = advanced_technical_analysis(klines)
  print(result["summary"])
""")
