#!/usr/bin/env python3
"""
股票行情数据获取脚本
从腾讯证券API获取A股实时行情数据
支持：股票、ETF、大盘指数

腾讯API字段索引说明（~分隔）：
0: 版本号
1: 名称
2: 代码
3: 当前价格
4: 昨收
5: 开盘
6: 成交量(手)
7: 买一量
8: 卖一量
...
33: 最高
34: 最低
37: 成交额(元) - 股票
39: 市盈率
44: 流通市值(亿)
45: 总市值(亿)
"""

import sys
import json
import urllib.request


def fetch_stock_quote(code):
    """获取单只股票/ETF的实时行情"""
    # 判断是否为指数（带前缀的如 sh000001）
    if code.startswith('sh') or code.startswith('sz'):
        # 大盘指数，直接使用
        market_prefix = code[:2]
        actual_code = code[2:]
    else:
        # 确定市场代码
        if code.startswith('6') or code.startswith('9') or code.startswith('51') or code.startswith('56') or code.startswith('58'):
            market_prefix = 'sh'
        else:
            market_prefix = 'sz'
        actual_code = code
    
    url = f"https://qt.gtimg.cn/q={market_prefix}{actual_code}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('gbk')
    except Exception as e:
        return {"error": f"获取失败: {e}", "code": code}
    
    # 解析腾讯API格式
    if '="' not in data:
        return {"error": "数据格式异常", "code": code, "raw": data[:200]}
    
    raw = data.split('="')[1].rstrip('";\n\r ')
    fields = raw.split('~')
    
    if len(fields) < 35:
        return {"error": f"数据字段不足({len(fields)})", "code": code, "raw": raw[:300]}
    
    name = fields[1] if len(fields) > 1 else code
    
    result = {
        "code": code,
        "name": name,
    }
    
    # 当前价格、昨收、开盘
    result["current_price"] = safe_float(fields, 3, 0)
    result["yesterday_close"] = safe_float(fields, 4, 0)
    result["open_price"] = safe_float(fields, 5, 0)
    
    # 成交量(手)、买卖盘
    result["volume"] = safe_int(fields, 6, 0)
    result["bid_volume"] = safe_int(fields, 7, 0)
    result["ask_volume"] = safe_int(fields, 8, 0)
    
    # 最高最低
    result["high"] = safe_float(fields, 33, result["current_price"])
    result["low"] = safe_float(fields, 34, result["current_price"])
    
    # 涨跌额和涨跌幅
    yclose = result["yesterday_close"]
    if yclose > 0:
        change = result["current_price"] - yclose
        change_pct = (change / yclose) * 100
    else:
        change = 0
        change_pct = 0
    result["change"] = round(change, 2)
    result["change_pct"] = round(change_pct, 2)
    
    # 成交额 - 腾讯API字段37是成交额(万元)
    amount_wan = safe_float(fields, 37, 0)  # 万元
    result["amount"] = amount_wan * 10000  # 转元
    
    # 总市值(亿)、流通市值(亿)
    result["market_cap"] = safe_float(fields, 45, 0)
    result["circulating_cap"] = safe_float(fields, 44, 0)
    
    # 市盈率
    result["pe_ratio"] = safe_float(fields, 39, 0)
    
    # 振幅
    if yclose > 0:
        result["amplitude"] = round(((result["high"] - result["low"]) / yclose) * 100, 2)
    else:
        result["amplitude"] = 0
    
    return result


def safe_float(fields, idx, default=0):
    """安全地获取float字段"""
    try:
        if len(fields) > idx and fields[idx]:
            return float(fields[idx])
    except:
        pass
    return default


def safe_int(fields, idx, default=0):
    """安全地获取int字段"""
    try:
        if len(fields) > idx and fields[idx]:
            return int(fields[idx])
    except:
        pass
    return default


def fetch_multiple(codes):
    """批量获取多个标的行情"""
    results = []
    for code in codes:
        data = fetch_stock_quote(code)
        results.append(data)
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 stock-quote.py <代码1> [代码2] ...")
        print("示例: python3 stock-quote.py 159840 516020 512480 002594 603986")
        print("       python3 stock-quote.py sh000001 sz399001 sz399006  # 大盘指数")
        sys.exit(1)
    
    codes = sys.argv[1:]
    results = fetch_multiple(codes)
    print(json.dumps(results, ensure_ascii=False, indent=2))
