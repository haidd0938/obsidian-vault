#!/usr/bin/env python3
"""
顾比交易大脑 — 数据层
统一的数据获取引擎：行情 + K线 + 板块 + 大盘

从 stock-robot 直接复用腾讯免费API，新增基本面数据维度。
全部免费，无API Key。
"""
import sys
import os
import json
import urllib.request
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fetch_url(url, encoding='utf-8', timeout=15):
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode(encoding, errors='replace')
    except Exception as e:
        return None


def get_market_prefix(code):
    if code.startswith(('sh', 'sz', 'hk')):
        return code[:2], code[2:]
    if code.startswith('6') or code.startswith('9') or code.startswith('51') or \
       code.startswith('56') or code.startswith('58'):
        return 'sh', code
    if code.startswith('0') or code.startswith('30'):
        return 'sz', code
    if code.startswith('07'):
        return 'hk', code[2:] if code.startswith('07') else code
    return 'sz', code


def to_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default


def get_quote(codes):
    """获取实时行情"""
    if not codes:
        return []

    batch_size = 50
    all_results = []

    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        market_codes = []
        for c in batch:
            prefix, code = get_market_prefix(c)
            market_codes.append(f"{prefix}{code}")

        url = f"https://qt.gtimg.cn/q={'%s' % ','.join(market_codes)}"
        data = fetch_url(url, encoding='gbk')

        if not data:
            continue

        for line in data.split(';\n'):
            if '="' not in line:
                continue
            try:
                raw = line.split('="')[1].rstrip('";\n\r ')
                fields = raw.split('~')
                if len(fields) < 10:
                    continue

                quote = {
                    "code": batch[len(all_results)] if len(all_results) < len(batch) else "",
                    "name": fields[1] if len(fields) > 1 else "",
                    "current_price": to_float(fields[3]),
                    "prev_close": to_float(fields[4]),
                    "open": to_float(fields[5]),
                    "high": to_float(fields[33]) or to_float(fields[5]) if len(fields) > 33 else to_float(fields[5]),
                    "low": to_float(fields[34]) or to_float(fields[6]) if len(fields) > 34 else to_float(fields[6]),
                    "volume": to_float(fields[6]) / 10000 if len(fields) > 6 else 0,
                    "amount": to_float(fields[37]) if len(fields) > 37 else 0,
                    "change_pct": to_float(fields[32]) if len(fields) > 32 else 0,
                    "turnover_rate": to_float(fields[38]) if len(fields) > 38 else 0,
                    "amplitude": to_float(fields[43]) if len(fields) > 43 else 0,
                    "pe_ratio": to_float(fields[39]) if len(fields) > 39 else 0,
                    "market_cap": to_float(fields[45]) if len(fields) > 45 else 0,
                }
                # 修正代码
                if not quote["code"] or quote["code"] not in batch:
                    # 从返回数据中提取
                    full_code = fields[2] if len(fields) > 2 else ""
                    if full_code:
                        for c in batch:
                            if full_code.endswith(c):
                                quote["code"] = c
                                break
                all_results.append(quote)
            except:
                continue

    return all_results


def get_kline(code, days=120):
    """获取K线数据"""
    prefix, actual = get_market_prefix(code)

    # 日K: 腾讯
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={prefix}{actual},day,,,{days},qfq"
    data = fetch_url(url, encoding='utf-8')

    if not data:
        return {"code": code, "error": "获取K线失败"}

    try:
        parsed = json.loads(data)
        klines_data = parsed.get("data", {})
        stock_data = klines_data.get(f"{prefix}{actual}", {})

        # 尝试多个路径（qfqday优先于qt，因为qt可能是dict）
        days_data = (stock_data.get("qfqday") or stock_data.get("day") or
                     stock_data.get("qt") or
                     stock_data.get("data", {}).get(f"{prefix}{actual}", {}).get("day", []))

        if not days_data:
            for key in stock_data:
                if isinstance(stock_data[key], list) and len(stock_data[key]) > 0:
                    if len(stock_data[key][0]) >= 6:
                        days_data = stock_data[key]
                        break

        if not days_data or len(days_data) < 5:
            return {"code": code, "error": f"K线数据不足({len(days_data or [])})"}

        klines = []
        for k in days_data:
            if len(k) >= 6:
                klines.append({
                    "date": k[0],
                    "open": to_float(k[1]),
                    "close": to_float(k[2]),
                    "high": to_float(k[3]),
                    "low": to_float(k[4]),
                    "volume": to_float(k[5]),
                    "amount": to_float(k[6]) if len(k) > 6 else 0,
                })

        return {
            "code": code,
            "klines": klines,
        }
    except Exception as e:
        return {"code": code, "error": f"解析K线失败: {e}"}


def get_hot_sectors():
    """获取热门板块"""
    url = "https://push2.eastmoney.com/api/qt/clist/get?cb=&pn=1&pz=20&fs=m:90+t:3&fields=f12,f14,f3,f4,f104,f105"
    data = fetch_url(url, encoding='utf-8')
    if not data:
        return []

    try:
        data = data.strip()
        parsed = json.loads(data)
        items = parsed.get("data", {}).get("diff", [])
        sectors = []
        for item in items[:15]:
            sectors.append({
                "name": item.get("f14", ""),
                "code": item.get("f12", ""),
                "change_pct": to_float(item.get("f3", 0)),
                "turnover": to_float(item.get("f4", 0)),
            })
        return sectors
    except:
        return []


def get_market_indices():
    """获取主要股指"""
    codes = ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300", "sh000016"]
    quotes = get_quote(codes)

    name_map = {
        "000001": "上证指数", "399001": "深证成指", "399006": "创业板指",
        "000688": "科创50", "000300": "沪深300", "000016": "上证50"
    }

    indices = []
    for q in quotes:
        idx_code = q.get("code", "")
        for c, name in name_map.items():
            if c in idx_code or idx_code.endswith(c):
                indices.append({
                    "name": name,
                    "price": q.get("current_price", 0),
                    "change_pct": q.get("change_pct", 0),
                    "volume": q.get("volume", 0),
                    "amount": q.get("amount", 0),
                })
                break
    return indices


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        code = sys.argv[1]
        print(f"📡 获取数据: {code}")
        quote = get_quote([code])
        if quote:
            q = quote[0]
            if q.get("current_price", 0) > 0:
                print(f"📈 {q['name']}({q['code']})")
                print(f"现价: {q['current_price']:.2f} | 涨跌: {q['change_pct']:+.2f}%")
                print(f"高: {q['high']:.2f} | 低: {q['low']:.2f}")
                print(f"换手: {q['turnover_rate']:.2f}% | 振幅: {q['amplitude']:.2f}%")
                print(f"PE: {q['pe_ratio']:.2f} | 市值: {q['market_cap']:.2f}亿")
            else:
                print(f"❌ 获取行情失败: {q}")

        kline = get_kline(code, 120)
        if "error" not in kline:
            print(f"\n📊 K线: {len(kline.get('klines', []))}条")
        else:
            print(f"\n❌ {kline.get('error', 'K线获取失败')}")
    else:
        print("用法: python3 brain/data_layer.py <代码>")
