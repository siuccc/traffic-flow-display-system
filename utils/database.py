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
            print(f"✅ 成功连接到数据库: {self.db_path}")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔌 数据库连接已断开")
    
    def get_table_info(self) -> List[str]:
        """
        获取数据库中的表信息
        
        Returns:
            List[str]: 表名列表
        """
        if not self.connection:
            print("❌ 请先连接数据库")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📋 发现 {len(tables)} 个表: {tables}")
            return tables
            
        except sqlite3.Error as e:
            print(f"❌ 获取表信息失败: {e}")
            return []
    
    def get_first_records(self, table_name: str, limit: int = 20) -> List[Dict]:
        """
        获取指定表的前N条记录
        
        Args:
            table_name: 表名
            limit: 返回记录数量，默认20
            
        Returns:
            List[Dict]: 记录列表
        """
        if not self.connection:
            print("❌ 请先连接数据库")
            return []
        
        try:
            cursor = self.connection.cursor()
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            cursor.execute(query)
            
            # 将结果转换为字典列表
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]
            
            print(f"📊 从表 '{table_name}' 获取了 {len(records)} 条记录")
            return records
            
        except sqlite3.Error as e:
            print(f"❌ 查询数据失败: {e}")
            return []
    
    def get_column_info(self, table_name: str) -> List[Dict]:
        """
        获取表的列信息
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict]: 列信息列表
        """
        if not self.connection:
            print("❌ 请先连接数据库")
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            column_info = []
            for col in columns:
                column_info.append({
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default': col[4],
                    'primary_key': bool(col[5])
                })
            
            print(f"🏗️ 表 '{table_name}' 的列信息:")
            for col in column_info:
                print(f"   - {col['name']} ({col['type']})")
            
            return column_info
            
        except sqlite3.Error as e:
            print(f"❌ 获取列信息失败: {e}")
            return []

# 便利函数：快速测试数据库连接
def test_database_connection():
    """测试数据库连接的便利函数"""
    print("🧪 开始测试数据库连接...")
    
    # 创建数据库实例
    db = TrafficDatabase()
    
    # 连接数据库
    if not db.connect():
        return False
    
    # 获取表信息
    tables = db.get_table_info()
    
    if tables:
        # 测试第一个表
        first_table = tables[0]
        print(f"\n📋 正在分析表: {first_table}")
        
        # 获取列信息
        columns = db.get_column_info(first_table)
        
        # 获取前5条记录作为示例
        records = db.get_first_records(first_table, limit=5)
        
        if records:
            print(f"\n📊 前5条记录示例:")
            for i, record in enumerate(records, 1):
                print(f"   记录 {i}: {dict(record)}")
    
    # 断开连接
    db.disconnect()
    
    return True

if __name__ == "__main__":
    # 如果直接运行这个文件，执行测试
    test_database_connection()
