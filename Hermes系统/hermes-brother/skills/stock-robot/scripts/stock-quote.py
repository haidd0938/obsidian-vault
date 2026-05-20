#!/usr/bin/env python3
"""
股票行情数据引擎 — 升级版
功能：
1. 实时行情获取（腾讯证券API）
2. 历史日K线获取（腾讯复权K线API）
3. 批量多标的操作
4. 自动判断市场代码（sh/sz）

数据源：腾讯证券API（免费，无需API Key）
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# ========== 行情API配置 ==========
QUOTE_API = "https://qt.gtimg.cn/q={code}"
KLINE_API = "http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},day,{start_date},,{days},qfq"

# 腾讯K线字段索引
# 格式: [日期, 开盘, 收盘, 最高, 最低, 成交量]
# 注意：ETF用 "day"，股票用 "qfqday"


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
    except:
        pass
    return default


def safe_int(fields, idx, default=0):
    try:
        if len(fields) > idx and fields[idx]:
            return int(fields[idx])
    except:
        pass
    return default


def fetch_real_time(code):
    """获取单只股票/ETF的实时行情"""
    market_prefix, actual_code = get_market_prefix(code)
    url = QUOTE_API.format(code=f"{market_prefix}{actual_code}")
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('gbk')
    except Exception as e:
        return {"error": f"行情获取失败: {e}", "code": code}
    
    if '="' not in data:
        return {"error": "数据格式异常", "code": code, "raw": data[:200]}
    
    raw = data.split('="')[1].rstrip('";\n\r ')
    fields = raw.split('~')
    
    if len(fields) < 35:
        return {"error": f"数据字段不足({len(fields)})", "code": code, "raw": raw[:300]}
    
    name = fields[1] if len(fields) > 1 else code
    
    result = {"code": code, "name": name}
    result["current_price"] = safe_float(fields, 3, 0)
    result["yesterday_close"] = safe_float(fields, 4, 0)
    result["open_price"] = safe_float(fields, 5, 0)
    result["volume"] = safe_int(fields, 6, 0)
    result["high"] = safe_float(fields, 33, result["current_price"])
    result["low"] = safe_float(fields, 34, result["current_price"])
    
    yclose = result["yesterday_close"]
    if yclose > 0:
        result["change"] = round(result["current_price"] - yclose, 2)
        result["change_pct"] = round((result["change"] / yclose) * 100, 2)
    else:
        result["change"] = 0
        result["change_pct"] = 0
    
    amount_wan = safe_float(fields, 37, 0)
    result["amount"] = amount_wan * 10000
    
    result["market_cap"] = safe_float(fields, 45, 0)
    result["circulating_cap"] = safe_float(fields, 44, 0)
    result["pe_ratio"] = safe_float(fields, 39, 0)
    
    if yclose > 0:
        result["amplitude"] = round(((result["high"] - result["low"]) / yclose) * 100, 2)
    else:
        result["amplitude"] = 0
    
    # 涨跌停价格（用于判断是否涨停/跌停）
    if yclose > 0:
        if code.startswith('3') or code.startswith('68'):
            limit = 0.20  # 创业板/科创板 20%
        elif code.startswith('8') or code.startswith('4'):
            limit = 0.30  # 北交所 30%
        elif code.startswith('51') or code.startswith('56') or code.startswith('58'):
            limit = 0.10  # ETF 10%
        else:
            limit = 0.10  # 主板 10%
        result["limit_up"] = round(yclose * (1 + limit), 2)
        result["limit_down"] = round(yclose * (1 - limit), 2)
    
    # 获取当前时间（从API字段23获取更新时间）
    update_time = safe_float(fields, 23, 0)
    if update_time > 0:
        t = int(update_time)
        result["update_time"] = f"{t//100:02d}:{t%100:02d}"
    
    return result


def fetch_history_kline(code, days=60):
    """获取历史日K线数据（复权）"""
    market_prefix, actual_code = get_market_prefix(code)
    full_code = f"{market_prefix}{actual_code}"
    
    # 计算起始日期
    start_date = datetime.now() - timedelta(days=days + 10)  # 留余量
    start_str = start_date.strftime("%Y-%m-%d")
    
    url = KLINE_API.format(code=full_code, start_date=start_str, days=days)
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode('gbk')
    except Exception as e:
        return {"error": f"K线获取失败: {e}", "code": code}
    
    try:
        data = json.loads(text)
    except:
        return {"error": "K线数据JSON解析失败", "code": code, "raw": text[:300]}
    
    # 提取K线数据
    stock_data = None
    for v in data.get("data", {}).values():
        if isinstance(v, dict):
            stock_data = v.get("day") or v.get("qfqday")
            break
    
    if not stock_data or not isinstance(stock_data, list):
        return {"error": "K线数据为空", "code": code}
    
    # 格式化为统一结构
    klines = []
    for row in stock_data:
        if len(row) >= 6:
            klines.append({
                "date": row[0],
                "open": float(row[1]),
                "close": float(row[2]),
                "high": float(row[3]),
                "low": float(row[4]),
                "volume": int(float(row[5])),
            })
    
    return {
        "code": code,
        "klines": klines,
        "count": len(klines),
        "from_date": klines[0]["date"] if klines else None,
        "to_date": klines[-1]["date"] if klines else None,
    }


def fetch_batch(codes):
    """批量获取实时行情"""
    return [fetch_real_time(c) for c in codes]


def fetch_batch_kline(codes, days=60):
    """批量获取历史K线"""
    return [fetch_history_kline(c, days) for c in codes]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  实时行情: python3 stock-quote.py <代码1> [代码2...]")
        print("  历史K线:  python3 stock-quote.py --kline <代码> [天数=60]")
        print("示例:")
        print("  python3 stock-quote.py 159840 002594")
        print("  python3 stock-quote.py --kline 159840 120")
        sys.exit(1)
    
    mode = "realtime"
    if sys.argv[1] == "--kline":
        mode = "kline"
        args = sys.argv[2:]
        if not args:
            print("请指定代码")
            sys.exit(1)
        codes = args[:-1] if len(args) > 1 else args
        days = int(args[-1]) if len(args) > 1 and args[-1].isdigit() else 60
        if len(args) == 1:
            codes = [args[0]]
            days = 60
    else:
        codes = sys.argv[1:]
    
    if mode == "realtime":
        results = fetch_batch(codes)
    else:
        results = [fetch_history_kline(c, days) for c in codes]
    
    print(json.dumps(results, ensure_ascii=False, indent=2))
