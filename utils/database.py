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
