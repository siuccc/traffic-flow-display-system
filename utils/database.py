#!/usr/bin/env python3
"""
数据库连接和操作模块
处理交通流量数据的读取和查询
"""

import sqlite3
import os
from typing import List, Dict, Optional

class TrafficDatabase:
    """交通数据库管理类"""
    
    def __init__(self, db_path: str = "data/traffic.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.connection = None
        
    def connect(self) -> bool:
        """
        连接到数据库
        
        Returns:
            bool: 连接是否成功
        """
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(self.db_path):
                print(f"❌ 数据库文件不存在: {self.db_path}")
                return False
            
            # 建立连接
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 让结果可以像字典一样访问
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def get_paginated_records(self, table_name: str, page: int = 1, per_page: int = 20) -> tuple:
        """
        获取指定表的分页记录
        
        Args:
            table_name: 表名
            page: 页码（从1开始）
            per_page: 每页记录数，默认20
            
        Returns:
            tuple: (记录列表, 总记录数, 总页数)
        """
        if not self.connection:
            print("❌ 请先连接数据库")
            return [], 0, 0
        
        try:
            cursor = self.connection.cursor()
            
            # 第1步：获取总记录数
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(count_query)
            total_records = cursor.fetchone()[0]
            
            # 第2步：计算总页数
            # 使用向上取整：(total_records + per_page - 1) // per_page
            total_pages = (total_records + per_page - 1) // per_page
            
            # 第3步：计算OFFSET（要跳过的记录数）
            # 第1页：跳过0条，第2页：跳过20条，第3页：跳过40条...
            offset = (page - 1) * per_page
            
            # 第4步：执行分页查询
            # 按数据库原始存储顺序显示，不进行排序
            # LIMIT per_page：只取指定数量的记录
            # OFFSET offset：跳过指定数量的记录
            data_query = f"""
                SELECT * FROM {table_name} 
                LIMIT {per_page} OFFSET {offset}
            """
            cursor.execute(data_query)
            
            # 第5步：将结果转换为字典列表
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
            
            return records, total_records, total_pages
            
        except sqlite3.Error as e:
            print(f"❌ 分页查询失败: {e}")
            return [], 0, 0
    
    def search_by_plate(self, plate_keyword: str, page: int = 1, per_page: int = 20) -> tuple:
        """
        根据车牌号关键字搜索记录（支持模糊搜索和分页）
        
        Args:
            plate_keyword: 车牌号关键字（支持部分匹配）
            page: 页码（从1开始）
            per_page: 每页记录数，默认20
            
        Returns:
            tuple: (记录列表, 总记录数, 总页数)
        """
        if not self.connection:
            print("❌ 请先连接数据库")
            return [], 0, 0
        
        # 处理空搜索关键字的情况
        if not plate_keyword or not plate_keyword.strip():
            print("⚠️ 搜索关键字为空，返回所有记录")
            return self.get_paginated_records('traffic', page, per_page)
        
        try:
            cursor = self.connection.cursor()
            
            # 清理搜索关键字：去除空格并转为大写（车牌通常是大写）
            clean_keyword = plate_keyword.strip().upper()
            
            # 第1步：获取匹配的总记录数
            # 使用LIKE进行模糊搜索，%关键字%表示包含关键字的所有记录
            count_query = """
                SELECT COUNT(*) FROM traffic 
                WHERE UPPER(plate) LIKE ?
            """
            cursor.execute(count_query, (f'%{clean_keyword}%',))
            total_records = cursor.fetchone()[0]
            
            # 第2步：计算总页数
            total_pages = (total_records + per_page - 1) // per_page
            
            # 如果没有找到匹配记录，直接返回
            if total_records == 0:
                return [], 0, 0
            
            # 第3步：计算OFFSET（要跳过的记录数）
            offset = (page - 1) * per_page
            
            # 第4步：执行分页搜索查询
            # 使用相同的LIKE条件进行实际数据查询
            search_query = """
                SELECT * FROM traffic 
                WHERE UPPER(plate) LIKE ?
                LIMIT ? OFFSET ?
            """
            cursor.execute(search_query, (f'%{clean_keyword}%', per_page, offset))
            
            # 第5步：将结果转换为字典列表
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
            
            print(f"🔍 搜索'{clean_keyword}'找到 {total_records} 条记录")
            return records, total_records, total_pages
            
        except sqlite3.Error as e:
            print(f"❌ 车牌搜索失败: {e}")
            return [], 0, 0
    
    def search_with_filters(self, time_range: str = '', direction_filter: str = '', page: int = 1, per_page: int = 20) -> tuple:
        """
        根据时间段和方向进行组合搜索（支持分页）
        
        Args:
            time_range: 时间段筛选（morning, noon, afternoon, evening, night，可为空）
            direction_filter: 方向筛选（1-4的字符串，可为空）
            page: 页码（从1开始）
            per_page: 每页记录数，默认20
            
        Returns:
            tuple: (记录列表, 总记录数, 总页数)
        """
        if not self.connection:
            print("❌ 请先连接数据库")
            return [], 0, 0
        
        try:
            cursor = self.connection.cursor()
            
            # 构建WHERE条件和参数列表
            where_conditions = []
            params = []
            
            # 处理时间段搜索条件
            if time_range and time_range.strip():
                time_condition = self._get_time_condition(time_range.strip())
                if time_condition:
                    where_conditions.append(time_condition)
            
            # 处理方向筛选条件
            if direction_filter and direction_filter.strip():
                where_conditions.append("direction = ?")
                params.append(int(direction_filter))
            
            # 构建完整的WHERE子句
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 第1步：获取匹配的总记录数
            count_query = f"SELECT COUNT(*) FROM traffic {where_clause}"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]
            
            # 第2步：计算总页数
            total_pages = (total_records + per_page - 1) // per_page
            
            # 如果没有找到匹配记录，直接返回
            if total_records == 0:
                return [], 0, 0
            
            # 第3步：计算OFFSET
            offset = (page - 1) * per_page
            
            # 第4步：执行分页查询
            search_query = f"""
                SELECT * FROM traffic 
                {where_clause}
                LIMIT ? OFFSET ?
            """
            # 添加分页参数
            params.extend([per_page, offset])
            cursor.execute(search_query, params)
            
            # 第5步：将结果转换为字典列表
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
            
            # 生成搜索描述
            search_desc = []
            if time_range and time_range.strip():
                time_map = {
                    'morning': '早高峰 (07:00-09:00)',
                    'noon': '中午时段 (11:00-13:00)', 
                    'afternoon': '下午时段 (14:00-17:00)',
                    'evening': '晚高峰 (17:00-19:00)',
                    'night': '夜间时段 (20:00-06:00)'
                }
                time_text = time_map.get(time_range, f"时间段{time_range}")
                search_desc.append(f"时间段'{time_text}'")
            if direction_filter and direction_filter.strip():
                direction_map = {'1': '北往南', '2': '南往北', '3': '东往西', '4': '西往东'}
                direction_text = direction_map.get(direction_filter, f"方向{direction_filter}")
                search_desc.append(f"方向'{direction_text}'")
            
            if search_desc:
                print(f"🔍 搜索{'+'.join(search_desc)}找到 {total_records} 条记录")
            
            return records, total_records, total_pages
            
        except sqlite3.Error as e:
            print(f"❌ 组合搜索失败: {e}")
            return [], 0, 0

    def _get_time_condition(self, time_range: str) -> str:
        """
        根据时间段返回SQL查询条件
        
        Args:
            time_range: 时间段标识
            
        Returns:
            str: SQL WHERE条件字符串
        """
        # 由于时间戳是Unix时间戳，我们需要用HOUR函数来提取小时
        # SQLite中可以使用strftime('%H', datetime(time, 'unixepoch'))来获取小时
        
        time_conditions = {
            'morning': "CAST(strftime('%H', datetime(time, 'unixepoch', 'localtime')) AS INTEGER) BETWEEN 7 AND 8",
            'noon': "CAST(strftime('%H', datetime(time, 'unixepoch', 'localtime')) AS INTEGER) BETWEEN 11 AND 12", 
            'afternoon': "CAST(strftime('%H', datetime(time, 'unixepoch', 'localtime')) AS INTEGER) BETWEEN 14 AND 16",
            'evening': "CAST(strftime('%H', datetime(time, 'unixepoch', 'localtime')) AS INTEGER) BETWEEN 17 AND 18",
            'night': "(CAST(strftime('%H', datetime(time, 'unixepoch', 'localtime')) AS INTEGER) >= 20 OR CAST(strftime('%H', datetime(time, 'unixepoch', 'localtime')) AS INTEGER) <= 5)"
        }
        
        return time_conditions.get(time_range, "")

# 简单的测试函数
def test_pagination():
    """测试分页功能的简单函数"""
    print("🧪 测试分页功能...")
    
    db = TrafficDatabase()
    if not db.connect():
        return False
    
    # 测试获取第1页数据
    records, total_records, total_pages = db.get_paginated_records('traffic', page=1, per_page=5)
    print(f"总记录数: {total_records}, 总页数: {total_pages}, 当前页记录: {len(records)}")
    
    db.disconnect()
    return True

if __name__ == "__main__":
    # 运行测试
    test_pagination()
