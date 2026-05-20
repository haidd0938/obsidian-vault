#!/usr/bin/env python3
"""
顾比交易大脑 — 统一配置
"""
import os

# ====== 路径 ======
ROBOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.join(ROBOT_DIR, "scripts")
BRAIN_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROBOT_DIR, "data")
LOG_DIR = os.path.join(ROBOT_DIR, "logs")
COOKIE_JAR_PATH = os.path.join(DATA_DIR, "cookie_jar.json")
TRADE_LOG_PATH = os.path.join(DATA_DIR, "trade_log.json")
BRAIN_CONFIG_PATH = os.path.join(DATA_DIR, "brain_config.json")

# ====== YOLO 安全模式 ======
# YOLO_MODE=True: 系统只出建议，不执行任何交易
# YOLO_MODE=False: 系统可以自动执行交易（需要你先确认开启）
YOLO_MODE = True  # 默认安全模式

# ====== 信号权重配置 ======
WEIGHTS = {
    "technical": 0.40,   # 技术分析权重
    "fundamental": 0.25, # 基本面分析权重
    "sentiment": 0.20,   # 情绪/新闻权重
    "momentum": 0.15,    # 趋势动量权重
}

# ====== 持仓管理 ======
MAX_POSITIONS = 5        # 最大持仓数量
MAX_SINGLE_POSITION_PCT = 0.30  # 单只最大仓位比例

# ====== 监控列表 ======
# 这里复用 stock-robot 的监控池，但加上更多基本面维度
WATCHLIST = [
    # ETF
    {"code": "159840", "name": "锂电池ETF", "type": "ETF", "category": "新能源"},    # 老板关注的
    {"code": "516020", "name": "化工ETF", "type": "ETF", "category": "化工"},        # 老板关注的
    {"code": "512480", "name": "半导体ETF", "type": "ETF", "category": "半导体"},      # 老板关注的
    {"code": "588000", "name": "科创50ETF", "type": "ETF", "category": "科技"},
    {"code": "510300", "name": "沪深300ETF", "type": "ETF", "category": "大盘"},
    # 个股
    {"code": "002594", "name": "比亚迪", "type": "股票", "category": "新能源车"},
    {"code": "603986", "name": "兆易创新", "type": "股票", "category": "半导体"},
    {"code": "601668", "name": "中国建筑", "type": "股票", "category": "基建"},
    {"code": "601390", "name": "中国中铁", "type": "股票", "category": "基建"},
    {"code": "600585", "name": "海螺水泥", "type": "股票", "category": "建材"},
    # 额外
    {"code": "159865", "name": "基建ETF", "type": "ETF", "category": "基建"},
    {"code": "159930", "name": "能源ETF", "type": "ETF", "category": "能源"},
]

# ====== 基本面评分阈值 ======
PE_THRESHOLDS = {
    "低估": (0, 15),
    "合理": (15, 30),
    "高估": (30, float("inf")),
}

# ====== 情绪评分阈值 ======
SENTIMENT_THRESHOLDS = {
    "极度看多": 0.8,
    "看多": 0.3,
    "中性": -0.3,
    "看空": -0.8,
}
