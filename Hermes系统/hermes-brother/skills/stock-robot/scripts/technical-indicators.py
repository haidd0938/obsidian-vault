#!/usr/bin/env python3
"""
技术指标计算引擎 — 纯Python实现
功能：
1. MA (移动平均线) — 5/10/20/30/60日均线
2. MACD (指数平滑异同移动平均线) — DIF/DEA/柱状图
3. KDJ (随机指标) — K/D/J 三线
4. RSI (相对强弱指标) — RSI6/RSI12/RSI24
5. BOLL (布林带) — 中轨/上轨/下轨
6. 综合信号生成 — 多指标叠加信号

全部使用 Python 标准库，零依赖。
"""

import json
import math


# ========== 工具函数 ==========

def ema(data, period):
    """指数移动平均线"""
    if not data or len(data) < period:
        return [None] * len(data)
    
    result = []
    multiplier = 2 / (period + 1)
    
    # 初始值：简单平均
    sma = sum(data[:period]) / period
    result.extend([None] * (period - 1))
    result.append(sma)
    
    for i in range(period, len(data)):
        ema_val = (data[i] - result[-1]) * multiplier + result[-1]
        result.append(ema_val)
    
    return result


def sma(data, period):
    """简单移动平均线"""
    if not data or len(data) < period:
        return [None] * len(data)
    
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(data[i - period + 1:i + 1]) / period)
    
    return result


def hhv(data, period):
    """N周期内最高值"""
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(max(data[i - period + 1:i + 1]))
    return result


def llv(data, period):
    """N周期内最低值"""
    result = []
    for i in range(len(data)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(min(data[i - period + 1:i + 1]))
    return result


# ========== 核心指标 ==========

def calc_ma(klines, periods=[5, 10, 20, 30, 60]):
    """计算多条移动平均线"""
    closes = [k["close"] for k in klines]
    result = {"dates": [k["date"] for k in klines]}
    
    for p in periods:
        ma_values = sma(closes, p)
        result[f"MA{p}"] = [round(v, 3) if v else None for v in ma_values]
    
    return result


def calc_macd(klines, fast=12, slow=26, signal=9):
    """
    MACD计算
    返回: {dates, DIF, DEA, MACD柱}
    """
    closes = [k["close"] for k in klines]
    n = len(closes)
    
    # 计算快慢EMA
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    
    # DIF = 快EMA - 慢EMA
    dif = []
    for i in range(n):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            dif.append(round(ema_fast[i] - ema_slow[i], 4))
        else:
            dif.append(None)
    
    # DEA = DIF的信号线(EMA)
    dea_raw = ema([d if d is not None else 0 for d in dif], signal)
    dea = [round(v, 4) if v is not None else None for v in dea_raw]
    
    # MACD柱 = 2 × (DIF - DEA)
    histogram = []
    for i in range(n):
        if dif[i] is not None and dea[i] is not None:
            histogram.append(round(2 * (dif[i] - dea[i]), 4))
        else:
            histogram.append(None)
    
    return {
        "dates": [k["date"] for k in klines],
        "DIF": dif,
        "DEA": dea,
        "MACD": histogram,
    }


def calc_kdj(klines, n=9, k_period=3, d_period=3):
    """
    KDJ计算
    返回: {dates, K, D, J}
    """
    highs = [k["high"] for k in klines]
    lows = [k["low"] for k in klines]
    closes = [k["close"] for k in klines]
    n_data = len(closes)
    
    highest = hhv(highs, n)
    lowest = llv(lows, n)
    
    # RSV计算
    rsv = []
    for i in range(n_data):
        if highest[i] is not None and lowest[i] is not None and highest[i] != lowest[i]:
            rsv_val = (closes[i] - lowest[i]) / (highest[i] - lowest[i]) * 100
            rsv.append(rsv_val)
        else:
            rsv.append(None)
    
    # K/D/J
    k_vals = [None] * n_data
    d_vals = [None] * n_data
    j_vals = [None] * n_data
    
    # 初始化K/D=50
    first_rsv = None
    for i in range(n_data):
        if rsv[i] is not None:
            first_rsv = i
            k_vals[i] = 50
            d_vals[i] = 50
            break
    
    if first_rsv is not None:
        for i in range(first_rsv, n_data):
            if rsv[i] is not None:
                if i == first_rsv:
                    k_vals[i] = 50
                    d_vals[i] = 50
                else:
                    k_vals[i] = (2/3) * k_vals[i-1] + (1/3) * rsv[i]
                    d_vals[i] = (2/3) * d_vals[i-1] + (1/3) * k_vals[i]
                j_vals[i] = 3 * k_vals[i] - 2 * d_vals[i]
    
    return {
        "dates": [k["date"] for k in klines],
        "K": [round(v, 2) if v is not None else None for v in k_vals],
        "D": [round(v, 2) if v is not None else None for v in d_vals],
        "J": [round(v, 2) if v is not None else None for v in j_vals],
    }


def calc_rsi(klines, periods=[6, 12, 24]):
    """
    RSI计算
    返回: {dates, RSI6, RSI12, RSI24}
    """
    closes = [k["close"] for k in klines]
    n = len(closes)
    
    # 计算涨跌
    gains = [0] * n
    losses = [0] * n
    for i in range(1, n):
        diff = closes[i] - closes[i-1]
        if diff > 0:
            gains[i] = diff
            losses[i] = 0
        else:
            gains[i] = 0
            losses[i] = abs(diff)
    
    result = {"dates": [k["date"] for k in klines]}
    
    for period in periods:
        rsi_vals = [None] * min(period + 1, n)
        
        # 初始平滑
        if n > period:
            avg_gain = sum(gains[1:period + 1]) / period
            avg_loss = sum(losses[1:period + 1]) / period
            
            if avg_loss == 0:
                rsi_vals.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi_vals.append(100 - 100 / (1 + rs))
            
            # 后续平滑
            for i in range(period + 2, n):
                avg_gain = ((avg_gain * (period - 1)) + gains[i-1]) / period
                avg_loss = ((avg_loss * (period - 1)) + losses[i-1]) / period
                if avg_loss == 0:
                    rsi_vals.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi_vals.append(100 - 100 / (1 + rs))
        else:
            rsi_vals.extend([None] * (n - len(rsi_vals)))
        
        result[f"RSI{period}"] = [round(v, 1) if v is not None else None for v in rsi_vals]
    
    return result


def calc_boll(klines, period=20, multiplier=2):
    """
    布林带计算
    返回: {dates, MID, UPPER, LOWER}
    """
    closes = [k["close"] for k in klines]
    n = len(closes)
    
    mid = sma(closes, period)
    
    upper = []
    lower = []
    
    for i in range(n):
        if mid[i] is None:
            upper.append(None)
            lower.append(None)
        elif i < period - 1:
            upper.append(None)
            lower.append(None)
        else:
            # 计算标准差
            segment = closes[i - period + 1:i + 1]
            std = math.sqrt(sum((x - mid[i]) ** 2 for x in segment) / period)
            upper.append(round(mid[i] + multiplier * std, 3))
            lower.append(round(mid[i] - multiplier * std, 3))
    
    return {
        "dates": [k["date"] for k in klines],
        "MID": [round(v, 3) if v is not None else None for v in mid],
        "UPPER": upper,
        "LOWER": lower,
    }


# ========== 信号生成 ==========

def generate_signals(klines, ma_data, macd_data, kdj_data, rsi_data, boll_data):
    """
    多指标综合信号生成
    返回: {latest_signals: {...}, signal_strength: '强烈看多'|'看多'|'中性'|'看空'|'强烈看空'}
    """
    if not klines:
        return {"signal_strength": "无数据", "signals": []}
    
    last = klines[-1]
    close = last["close"]
    signals = []
    
    # 获取最新值
    def last_val(data_list):
        vals = [v for v in data_list if v is not None]
        return vals[-1] if vals else None
    
    last_ma5 = last_val(ma_data["MA5"]) if "MA5" in ma_data else None
    last_ma10 = last_val(ma_data["MA10"]) if "MA10" in ma_data else None
    last_ma20 = last_val(ma_data["MA20"]) if "MA20" in ma_data else None
    last_ma60 = last_val(ma_data["MA60"]) if "MA60" in ma_data else None
    
    last_dif = last_val(macd_data["DIF"])
    last_dea = last_val(macd_data["DEA"])
    last_macd = last_val(macd_data["MACD"])
    
    last_k = last_val(kdj_data["K"])
    last_d = last_val(kdj_data["D"])
    last_j = last_val(kdj_data["J"])
    
    last_rsi6 = last_val(rsi_data["RSI6"])
    last_rsi12 = last_val(rsi_data["RSI12"])
    last_rsi24 = last_val(rsi_data["RSI24"])
    
    boll_mid = last_val(boll_data["MID"])
    boll_upper = last_val(boll_data["UPPER"])
    boll_lower = last_val(boll_data["LOWER"])
    
    # --- 均线信号 ---
    if last_ma5 and last_ma10:
        if last_ma5 > last_ma10:
            signals.append({"indicator": "MA", "signal": "看多", 
                          "detail": f"MA5({last_ma5:.2f})上穿MA10({last_ma10:.2f})"})
        else:
            signals.append({"indicator": "MA", "signal": "看空",
                          "detail": f"MA5({last_ma5:.2f})下穿MA10({last_ma10:.2f})"})
    
    # --- MACD信号 ---
    if last_dif is not None and last_dea is not None and last_macd is not None:
        if last_macd > 0 and last_dif > last_dea:
            signals.append({"indicator": "MACD", "signal": "看多",
                          "detail": f"DIF({last_dif:.4f})>DEA({last_dea:.4f}), 红柱"})
        elif last_macd < 0 and last_dif < last_dea:
            signals.append({"indicator": "MACD", "signal": "看空",
                          "detail": f"DIF({last_dif:.4f})<DEA({last_dea:.4f}), 绿柱"})
        elif last_macd < 0 and last_dif > last_dea:
            signals.append({"indicator": "MACD", "signal": "弱看多",
                          "detail": f"DIF上穿DEA但仍在零轴下方"})
        else:
            signals.append({"indicator": "MACD", "signal": "弱看空",
                          "detail": f"DIF下穿DEA但仍在零轴上方"})
    
    # --- KDJ信号 ---
    if last_k is not None and last_d is not None and last_j is not None:
        if last_k > 80 and last_d > 70:
            signals.append({"indicator": "KDJ", "signal": "超买",
                          "detail": f"K({last_k:.1f})>80, D({last_d:.1f})>70, 注意回调风险"})
        elif last_k < 20 and last_d < 30:
            signals.append({"indicator": "KDJ", "signal": "超卖",
                          "detail": f"K({last_k:.1f})<20, D({last_d:.1f})<30, 可能反弹"})
        elif last_k > last_d:
            signals.append({"indicator": "KDJ", "signal": "看多",
                          "detail": f"K({last_k:.1f})上穿D({last_d:.1f})"})
        else:
            signals.append({"indicator": "KDJ", "signal": "看空",
                          "detail": f"K({last_k:.1f})下穿D({last_d:.1f})"})
    
    # --- RSI信号 ---
    if last_rsi6 is not None:
        if last_rsi6 > 70:
            signals.append({"indicator": "RSI", "signal": "超买",
                          "detail": f"RSI6({last_rsi6:.0f})>70, 超买区"})
        elif last_rsi6 < 30:
            signals.append({"indicator": "RSI", "signal": "超卖",
                          "detail": f"RSI6({last_rsi6:.0f})<30, 超卖区"})
        elif last_rsi6 > 50:
            signals.append({"indicator": "RSI", "signal": "偏多",
                          "detail": f"RSI6({last_rsi6:.0f})>50, 偏强"})
        else:
            signals.append({"indicator": "RSI", "signal": "偏空",
                          "detail": f"RSI6({last_rsi6:.0f})<50, 偏弱"})
    
    # --- 布林带信号 ---
    if boll_upper and boll_lower and boll_mid:
        if close >= boll_upper:
            signals.append({"indicator": "BOLL", "signal": "超买",
                          "detail": f"收盘价({close:.2f})触及上轨({boll_upper:.2f})"})
        elif close <= boll_lower:
            signals.append({"indicator": "BOLL", "signal": "超卖",
                          "detail": f"收盘价({close:.2f})触及下轨({boll_lower:.2f})"})
        elif close > boll_mid:
            signals.append({"indicator": "BOLL", "signal": "偏多",
                          "detail": f"收盘价({close:.2f})在中轨({boll_mid:.2f})上方"})
        else:
            signals.append({"indicator": "BOLL", "signal": "偏空",
                          "detail": f"收盘价({close:.2f})在中轨({boll_mid:.2f})下方"})
    
    # --- 综合判断 ---
    score = 0
    for s in signals:
        if s["signal"] in ("看多", "强烈看多"):
            score += 1
        elif s["signal"] in ("偏多", "弱看多"):
            score += 0.5
        elif s["signal"] in ("看空", "强烈看空"):
            score -= 1
        elif s["signal"] in ("偏空", "弱看空"):
            score -= 0.5
        # 超买=看空信号, 超卖=看多信号
        if s["signal"] == "超买":
            score -= 1
        elif s["signal"] == "超卖":
            score += 1
    
    if score >= 3:
        strength = "强烈看多 ★★★★★"
    elif score >= 1.5:
        strength = "看多 ★★★☆"
    elif score >= -0.5:
        strength = "中性 ★★☆"
    elif score >= -2:
        strength = "看空 ★☆"
    else:
        strength = "强烈看空 ☆"
    
    return {
        "latest_price": close,
        "signal_score": score,
        "signal_strength": strength,
        "signal_count": len(signals),
        "signals": signals,
    }


# ========== 全量技术分析 ==========

def full_technical_analysis(klines):
    """对一组K线进行完整技术分析"""
    if not klines or len(klines) < 26:
        return {"error": f"K线数据不足，当前{len(klines)}条，至少需要26条"}
    
    ma = calc_ma(klines)
    macd = calc_macd(klines)
    kdj = calc_kdj(klines)
    rsi = calc_rsi(klines)
    boll = calc_boll(klines)
    signals = generate_signals(klines, ma, macd, kdj, rsi, boll)
    
    # 提取最新值
    def last_val(data_dict, key):
        vals = [v for v in data_dict.get(key, []) if v is not None]
        return vals[-1] if vals else None
    
    # 均线排列状态
    ma_status = {}
    for p in [5, 10, 20, 30, 60]:
        v = last_val(ma, f"MA{p}")
        if v:
            ma_status[f"MA{p}"] = round(v, 2)
    
    # 排序判断多头/空头排列
    ma_vals = [(k, v) for k, v in ma_status.items()]
    sorted_ma = sorted(ma_vals, key=lambda x: x[1], reverse=True)
    is_bullish = all(sorted_ma[i][1] >= sorted_ma[i+1][1] for i in range(len(sorted_ma)-1)) if len(sorted_ma) >= 3 else None
    
    return {
        "code": klines[0].get("code", klines[-1].get("code", "?")),
        "last_close": klines[-1]["close"],
        "last_date": klines[-1]["date"],
        "data_points": len(klines),
        "price_range": {
            "high_60d": round(max(k["high"] for k in klines[-60:]), 2) if len(klines) >= 60 else round(max(k["high"] for k in klines), 2),
            "low_60d": round(min(k["low"] for k in klines[-60:]), 2) if len(klines) >= 60 else round(min(k["low"] for k in klines), 2),
        },
        "ma": ma_status,
        "ma_arrangement": "多头排列" if is_bullish else ("空头排列" if is_bullish is False else "交叉"),
        "macd": {
            "DIF": round(last_val(macd, "DIF"), 4) if last_val(macd, "DIF") else None,
            "DEA": round(last_val(macd, "DEA"), 4) if last_val(macd, "DEA") else None,
            "MACD": round(last_val(macd, "MACD"), 4) if last_val(macd, "MACD") else None,
        },
        "kdj": {
            "K": round(last_val(kdj, "K"), 1) if last_val(kdj, "K") else None,
            "D": round(last_val(kdj, "D"), 1) if last_val(kdj, "D") else None,
            "J": round(last_val(kdj, "J"), 1) if last_val(kdj, "J") else None,
        },
        "rsi": {
            "RSI6": round(last_val(rsi, "RSI6"), 1) if last_val(rsi, "RSI6") else None,
            "RSI12": round(last_val(rsi, "RSI12"), 1) if last_val(rsi, "RSI12") else None,
            "RSI24": round(last_val(rsi, "RSI24"), 1) if last_val(rsi, "RSI24") else None,
        },
        "boll": {
            "MID": last_val(boll, "MID"),
            "UPPER": last_val(boll, "UPPER"),
            "LOWER": last_val(boll, "LOWER"),
        },
        "signals": signals,
    }


def full_technical_summary(klines):
    """
    返回简化的纯文本技术摘要
    用于每日复盘报告
    """
    analysis = full_technical_analysis(klines)
    if "error" in analysis:
        return analysis["error"]
    
    lines = []
    lines.append(f"📊 技术面分析")
    lines.append(f"━━━━━━━━━━━━━━━")
    lines.append(f"价格区间(60日): {analysis['price_range']['low_60d']} ~ {analysis['price_range']['high_60d']}")
    
    # 均线
    ma_str = " | ".join([f"{k}={v:.2f}" for k, v in sorted(analysis['ma'].items())])
    lines.append(f"均线排列: {analysis['ma_arrangement']}")
    lines.append(f"均线值: {ma_str}")
    
    # MACD
    m = analysis['macd']
    macd_str = f"DIF={m['DIF']} | DEA={m['DEA']} | MACD柱={m['MACD']}"
    macd_trend = "📗 多头" if m['MACD'] and m['MACD'] > 0 else "📕 空头"
    lines.append(f"MACD: {macd_str} → {macd_trend}")
    
    # KDJ
    k = analysis['kdj']
    kdj_str = f"K={k['K']} | D={k['D']} | J={k['J']}"
    kdj_status = ""
    if k['K'] and k['K'] > 80: kdj_status = "⚠️ 超买区"
    elif k['K'] and k['K'] < 20: kdj_status = "💡 超卖区"
    lines.append(f"KDJ: {kdj_str} {kdj_status}")
    
    # RSI
    r = analysis['rsi']
    rsi_str = f"RSI6={r['RSI6']} | RSI12={r['RSI12']} | RSI24={r['RSI24']}"
    rsi_status = ""
    if r['RSI6'] and r['RSI6'] > 70: rsi_status = "⚠️ 超买"
    elif r['RSI6'] and r['RSI6'] < 30: rsi_status = "💡 超卖"
    lines.append(f"RSI: {rsi_str} {rsi_status}")
    
    # 布林带
    b = analysis['boll']
    boll_str = f"中轨={b['MID']} | 上轨={b['UPPER']} | 下轨={b['LOWER']}"
    lines.append(f"布林带: {boll_str}")
    
    # 综合信号
    s = analysis['signals']
    lines.append(f"\n综合评级: {s['signal_strength']} (评分={s['signal_score']})")
    lines.append(f"\n详细信号:")
    for sig in s['signals']:
        icon = "🟢" if sig['signal'] in ("看多", "强烈看多", "偏多") else \
               "🔴" if sig['signal'] in ("看空", "强烈看空", "偏空") else \
               "🟡" if sig['signal'] in ("超买", "超卖") else "⚪"
        lines.append(f"  {icon} [{sig['indicator']}] {sig['signal']}: {sig['detail']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 用模拟数据测试
        import random
        test_klines = []
        price = 10.0
        for i in range(100):
            price *= (1 + random.uniform(-0.03, 0.03))
            test_klines.append({
                "date": f"2026-{i//30+1:02d}-{i%30+1:02d}",
                "open": round(price * 0.998, 2),
                "close": round(price, 2),
                "high": round(price * 1.02, 2),
                "low": round(price * 0.99, 2),
                "volume": random.randint(100000, 1000000),
            })
        
        result = full_technical_analysis(test_klines)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n" + "="*60)
        print(full_technical_summary(test_klines))
    else:
        print("technical-indicators.py - 技术指标计算引擎")
        print("用法: 被 stock-quote.py 和 daily-review.py 调用")
        print("测试: python3 technical-indicators.py --test")
