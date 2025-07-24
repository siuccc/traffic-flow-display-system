#!/usr/bin/env python3
"""
Flask交通流量数据展示系统
"""

# 导入Flask相关模块
from flask import Flask, render_template
from datetime import datetime, timezone, timedelta
import os
import sys

# 导入我们自己的数据库模块
from utils.database import TrafficDatabase

# 创建Flask应用实例
app = Flask(__name__)

# 初始化数据库连接
def get_database():
    """获取数据库实例"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'traffic.db')
    return TrafficDatabase(db_path)

# 定义路由和视图函数
@app.route('/')
def index():
    """首页 - 展示前20条交通数据"""
    try:
        # 创建数据库连接
        db = get_database()
        
        # 连接数据库
        if not db.connect():
            return "<h1>❌ 数据库连接失败</h1><p>无法连接到交通数据库</p>"
        
        # 获取前20条交通记录
        traffic_records = db.get_first_records('traffic', limit=20)
        
        # 处理时间格式转换
        for record in traffic_records:
            # 将Unix时间戳转换为北京时间
            timestamp = record['time']
            # 创建北京时区（UTC+8）
            beijing_tz = timezone(timedelta(hours=8))
            # 转换为北京时间
            beijing_time = datetime.fromtimestamp(timestamp, tz=beijing_tz)
            record['formatted_time'] = beijing_time.strftime('%Y-%m-%d %H:%M:%S (北京时间)')
            
            # 将方向代码转换为文字
            direction_map = {1: '北往南', 2: '南往北', 3: '东往西', 4: '西往东'}
            record['direction_text'] = direction_map.get(record['direction'], '未知方向')
        
        # 获取当前时间作为更新时间
        current_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
        
        # 断开数据库连接
        db.disconnect()
        
        # 使用模板渲染页面
        return render_template('index.html',
                             traffic_records=traffic_records,
                             record_count=len(traffic_records),
                             update_time=current_time)
        
    except Exception as e:
        return f"<h1>❌ 数据库连接错误</h1><p>错误信息: {str(e)}</p>"

if __name__ == '__main__':
    # 启动Flask应用
    print("🚀 启动交通流量数据展示系统...")
    print("📍 访问地址: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
