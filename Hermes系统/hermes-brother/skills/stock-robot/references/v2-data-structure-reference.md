# 大盘复盘数据结构参考

> `brain/market_overview.py` 的 output JSON schema，供未来解析使用。

## build_market_overview() 返回结构

```python
{
    "timestamp": "2026-05-08 22:42",
    "indices": [
        {"name": "上证指数", "price": 4179.95, "change_pct": -0.00, "amount": 13317},
        {"name": "深证成指", "price": 15563.80, "change_pct": -0.50, ...},
    ],
    "breadth": [
        {"name": "上证指数", "advancers": 1200, "decliners": 800, "unchanged": 50, "total": 2050, "ratio": 1.50},
    ],
    "sh_trend": {
        "current": 4179.95, "change_pct": -0.00,
        "ma5": 4147.98, "ma10": 4100.0, "ma20": 4072.41,
        "above_ma5": True, "above_ma20": True,
        "ma5_trend": "up", "trend": "上涨",
    },
    "sectors": {
        "top_gainers": [{"name": "半导体", "code": "...", "change_pct": 3.45}, ...],
        "top_losers": [{"name": "房地产", ...}],
        "avg_sector_change": 0.00,
    },
    "market_status": "中性",  # 偏多/中性/偏空
    "advancers_total": 2400,
    "decliners_total": 1600,
    "adv_decl_ratio": 1.50,
}
```

## 决策评分卡 build_decision_card() 返回结构

```python
{
    "code": "159840", "name": "锂电池ETF",
    "status": "ok",
    "overall_score": 75,  # 0-100
    "grade": "A",   # A+/A/B+/B/C+/C/D
    "color": "#22aa44",
    "dimensions": {
        "technical": {"score": 85, "detail": {"macd": "金叉 ✅", "kdj": "中性", "ma": "多头排列 📈"}},
        "fundamental": {"score": 65, "detail": ...},
        "sentiment": {"score": 55, "detail": {"source": "看多"}},
        "trend_structure": {"score": 70, "detail": {"trend": "看多"}},
    },
    "action": {
        "signal": "看多",
        "entry_zone": {"reason": "MA20附近...", "low": 8.50, "high": 8.80},
        "exit_zone": {"reason": "近期高点...", "low": 9.50, "high": 9.80},
        "suggestion": "🚀 强烈推荐买入 — 多个维度共振",
    },
    "risk_alerts": [
        {"type": "warning", "message": "技术面偏弱..."},
    ],
    "risk_level": "中等风险 🟡",
    "checklist": [
        "✅ 技术面确认强势",
        "⬜ 等待技术面信号确认",
        ...
    ],
    "support_levels": ["MA20(8.52)", "近期低点(8.30)", "MA30(8.40)"],
    "resistance_levels": ["MA10(8.80)", "近期高点(9.20)"],
}
```

## 高级技术分析 advanced_technical_analysis() 返回结构

```python
{
    "chan_theory": {
        "fractal_count": 31,
        "top_fractals": 15, "bottom_fractals": 16,
        "bi_count": 11,
        "up_bi": 5, "down_bi": 6,
        "zone_count": 0,
        "zones": [{"zone_high": 9.20, "zone_low": 8.80, "midpoint": 9.00, ...}],
        "last_bi_type": "上升笔",
        "buy_sell_points": {
            "buy_points": [{"type": "第一类买点", "price_zone": "8.50附近", ...}],
            "sell_points": [...],
        },
    },
    "elliott_wave": {
        "wave_position": "第4浪调整",
        "peaks": 3, "troughs": 3,
        "last_peak": 9.20, "last_trough": 8.30,
        "rsi": 62.5,
        "rsi_divergence": "",
        "confidence": "中",
    },
    "ichimoku": {
        "tenkan": 8.90, "kijun": 8.70,
        "senkou_a": 8.80, "senkou_b": 8.50,
        "cloud_top": 8.80, "cloud_bottom": 8.50,
        "relative_position": "云层上方",
        "signals": ["☀️ 云层上方+转换>基准 → 强势多头"],
    },
    "summary": "缠论: 最近一笔为上升笔(幅度上涨9.1%) | 波浪: 第4浪调整 | 一目: ☀️ 云层上方+转换>基准 → 强势多头",
}
```
