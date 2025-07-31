#!/usr/bin/env python3
"""
常量定义模块
统一管理系统中使用的各种常量和映射关系
"""

# 时间段映射 - 将时间段代码映射为中文描述
TIME_RANGE_MAP = {
    'morning': '早高峰 (07:00-09:00)',
    'noon': '中午时段 (11:00-13:00)', 
    'afternoon': '下午时段 (14:00-17:00)',
    'evening': '晚高峰 (17:00-19:00)',
    'night': '夜间时段 (20:00-06:00)'
}

# 方向映射 - 将方向代码映射为中文描述
DIRECTION_MAP = {
    1: '北往南', 
    2: '南往北', 
    3: '东往西', 
    4: '西往东'
}

# 方向映射 (字符串版本) - 用于URL参数处理
DIRECTION_STR_MAP = {
    '1': '北往南', 
    '2': '南往北', 
    '3': '东往西', 
    '4': '西往东'
}

# 图表颜色配置
CHART_COLORS = {
    'directions': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],  # 方向饼图颜色
    'trend_line': '#2E86AB',     # 趋势线颜色
    'trend_marker': '#F24236',   # 趋势点颜色
    'weekday_line': '#2E86AB',   # 工作日趋势线颜色
    'weekend_line': '#FF6B6B',   # 周末趋势线颜色
    'weekday_marker': '#1976D2', # 工作日趋势点颜色
    'weekend_marker': '#F44336'  # 周末趋势点颜色
}

# 工具函数
def get_time_text(time_range: str) -> str:
    """
    获取时间段的中文描述
    
    Args:
        time_range: 时间段代码
        
    Returns:
        str: 时间段中文描述
    """
    return TIME_RANGE_MAP.get(time_range, f"时间段{time_range}")

def get_direction_text(direction) -> str:
    """
    获取方向的中文描述
    
    Args:
        direction: 方向代码 (可以是int或str)
        
    Returns:
        str: 方向中文描述
    """
    if isinstance(direction, str):
        return DIRECTION_STR_MAP.get(direction, f"方向{direction}")
    else:
        return DIRECTION_MAP.get(direction, f"方向{direction}")
