#!/usr/bin/env python3
"""
顾比交易大脑 — 基本面分析引擎
从 Vibe-Trading 借鉴的财报/估值分析能力

数据源：
  1. 腾讯证券API — PE、市值等基本估值指标
  2. 基于公开财务数据的简易基本面评分
  3. 行业对比分析

全部免费，无需API Key。
"""
import sys
import os
import json
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain.config import PE_THRESHOLDS


def fetch_url(url, encoding="utf-8", timeout=15):
    """安全的 URL 请求"""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode(encoding, errors="replace")
    except Exception as e:
        return None


def get_market_prefix(code):
    """判断市场代码前缀"""
    if code.startswith('sh') or code.startswith('sz'):
        return code[:2], code[2:]
    if code.startswith('6') or code.startswith('9') or code.startswith('51') or \
       code.startswith('56') or code.startswith('58'):
        return 'sh', code
    return 'sz', code


def safe_float(fields, idx, default=0.0):
    try:
        if len(fields) > idx and fields[idx]:
            return float(fields[idx])
    except: pass
    return default


def fetch_valuation(code):
    """从腾讯证券获取估值相关数据"""
    market_prefix, actual_code = get_market_prefix(code)
    url = f"https://qt.gtimg.cn/q={market_prefix}{actual_code}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("gbk")
    except Exception as e:
        return {"error": str(e), "code": code}

    if '="' not in data:
        return {"error": "数据格式异常", "code": code}

    raw = data.split('="')[1].rstrip('";\n\r ')
    fields = raw.split('~')
    if len(fields) < 50:
        return {"error": f"字段不足({len(fields)})", "code": code}

    valuation = {
        "code": code,
        "name": fields[1] if len(fields) > 1 else code,
        "pe_ratio": safe_float(fields, 39, 0),               # 动态市盈率
        "pb_ratio": safe_float(fields, 46, 0),                # 市净率
        "market_cap": safe_float(fields, 45, 0),              # 总市值(亿)
        "circulating_cap": safe_float(fields, 44, 0),         # 流通市值(亿)
        "roe": safe_float(fields, 53, 0),                     # 净资产收益率(%)
        "eps": safe_float(fields, 55, 0),                     # 每股收益
        "revenue": safe_float(fields, 58, 0),                 # 营业收入(亿)
        "profit": safe_float(fields, 60, 0),                  # 净利润(亿)
        "dividend": safe_float(fields, 62, 0),                # 股息率(%, 索引62)
        "total_shares": safe_float(fields, 66, 0),            # 总股本(亿)
        "current_price": safe_float(fields, 3, 0),
        "high_52week": safe_float(fields, 67, 0),             # 52周最高(索引67)
        "low_52week": safe_float(fields, 68, 0),              # 52周最低(索引68)
        "change_pct": safe_float(fields, 32, 0),
    }

    # 修复52周数据：如果拿到的是0或异常值，尝试其他索引
    if valuation["high_52week"] <= 0 and len(fields) > 49:
        try:
            v = safe_float(fields, 49, 0)
            if 0 < v < 10000:
                valuation["high_52week"] = v
        except: pass
    if valuation["low_52week"] <= 0 and len(fields) > 50:
        try:
            v = safe_float(fields, 50, 0)
            if 0 < v < 10000:
                valuation["low_52week"] = v
        except: pass
    return valuation


def score_pe(pe_ratio):
    """市盈率评分 (0-10)"""
    if pe_ratio <= 0:
        return 5, "亏损/无数据"
    if pe_ratio < 10:
        return 9, "明显低估"
    if pe_ratio < 20:
        return 7, "合理偏低"
    if pe_ratio < 30:
        return 5, "合理偏高"
    if pe_ratio < 50:
        return 3, "高估"
    return 1, "严重高估"


def score_pb(pb_ratio):
    """市净率评分 (0-10)"""
    if pb_ratio <= 0:
        return 5, "无数据"
    if pb_ratio < 1:
        return 9, "破净/低估"
    if pb_ratio < 2:
        return 7, "合理偏低"
    if pb_ratio < 4:
        return 5, "合理"
    if pb_ratio < 8:
        return 3, "偏高"
    return 1, "严重高估"


def score_roe(roe):
    """ROE评分 (0-10)"""
    if roe <= 0:
        return 3, "亏损或低ROE"
    if roe < 5:
        return 4, "较低"
    if roe < 10:
        return 6, "一般"
    if roe < 15:
        return 7, "良好"
    if roe < 25:
        return 9, "优秀"
    return 10, "卓越"


def score_market_cap_position(v):
    """市值位置评分：从52周区间看当前位置"""
    if v["high_52week"] - v["low_52week"] <= 0 or v["current_price"] <= 0:
        return 5, "无数据"
    position = (v["current_price"] - v["low_52week"]) / (v["high_52week"] - v["low_52week"])
    if position < 0.2:
        return 9, "接近52周低点"
    if position < 0.35:
        return 7, "低位区域"
    if position < 0.65:
        return 5, "中间区域"
    if position < 0.85:
        return 3, "高位区域"
    return 1, "接近52周高点"


def score_dividend(div):
    """股息率评分"""
    if div <= 0:
        return 3, "不分红"
    if div < 1:
        return 4, "偏低"
    if div < 2:
        return 6, "一般"
    if div < 4:
        return 8, "不错"
    return 10, "高股息"


def full_fundamental_analysis(code, name=""):
    """
    完整基本面分析
    返回: {code, name, valuation, scores, fundamentals_score, signal}
    """
    val = fetch_valuation(code)

    if "error" in val:
        return {"code": code, "name": name or code, "error": val["error"]}

    # 各维度评分
    pe_score, pe_note = score_pe(val["pe_ratio"])
    pb_score, pb_note = score_pb(val["pb_ratio"])
    roe_score, roe_note = score_roe(val["roe"])
    pos_score, pos_note = score_market_cap_position(val)
    div_score, div_note = score_dividend(val["dividend"])

    # 加权综合评分 (0-10)
    weights = {
        "pe": 0.25,
        "pb": 0.15,
        "roe": 0.30,
        "position": 0.20,
        "dividend": 0.10,
    }
    total_score = (
        pe_score * weights["pe"]
        + pb_score * weights["pb"]
        + roe_score * weights["roe"]
        + pos_score * weights["position"]
        + div_score * weights["dividend"]
    )

    # 信号生成
    if total_score >= 8:
        signal = "强烈看多 ★★★★★"
    elif total_score >= 6.5:
        signal = "看多 ★★★★"
    elif total_score >= 5:
        signal = "中性 ★★★"
    elif total_score >= 3.5:
        signal = "看空 ★★"
    else:
        signal = "强烈看空 ★"

    return {
        "code": code,
        "name": name or val.get("name", code),
        "valuation": {
            "pe": val["pe_ratio"],
            "pb": val["pb_ratio"],
            "roe": val["roe"],
            "eps": val["eps"],
            "market_cap": val["market_cap"],
            "dividend_yield": val["dividend"],
            "52week_low": val["low_52week"],
            "52week_high": val["high_52week"],
            "current_price": val["current_price"],
        },
        "scores": {
            "pe": {"score": pe_score, "note": pe_note, "value": val["pe_ratio"]},
            "pb": {"score": pb_score, "note": pb_note, "value": val["pb_ratio"]},
            "roe": {"score": roe_score, "note": roe_note, "value": val["roe"]},
            "price_position": {"score": pos_score, "note": pos_note},
            "dividend": {"score": div_score, "note": div_note, "value": val["dividend"]},
        },
        "fundamentals_score": round(total_score, 2),
        "fundamentals_signal": signal,
    }


def batch_analysis(watchlist):
    """批量基本面分析"""
    results = []
    for w in watchlist:
        result = full_fundamental_analysis(w["code"], w["name"])
        results.append(result)
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else code
        result = full_fundamental_analysis(code, name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("用法: python3 brain/fundamental_analysis.py <代码> [名称]")
