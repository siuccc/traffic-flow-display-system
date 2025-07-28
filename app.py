#!/usr/bin/env python3
"""
Flask交通流量数据展示系统
"""

# 导入Flask相关模块
from flask import Flask, render_template, request
from datetime import datetime, timezone, timedelta
import os
import sys

# 导入我们自己的数据库模块
from utils.database import TrafficDatabase

# 创建Flask应用实例
app = Flask(__name__)

# 调试开关 - 控制是否显示详细日志
DEBUG_LOGS = False  # 设为True可以看到详细日志

# 初始化数据库连接
def get_database():
    """获取数据库实例"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'traffic.db')
    return TrafficDatabase(db_path)

@app.route('/')
def index():
    """首页 - 展示交通数据（支持分页和时间段搜索）"""
    try:
        # 第1步：从URL参数获取page、时间段搜索和方向筛选
        page = request.args.get('page', 1, type=int)
        time_search = request.args.get('time_range', '', type=str)  # 时间段搜索关键字
        direction_search = request.args.get('direction', '', type=str)  # 方向筛选参数
        
        if DEBUG_LOGS:
            print(f"🔢 用户请求第 {page} 页")
            if time_search:
                print(f"� 搜索时间段: '{time_search}'")
            if direction_search:
                print(f"🧭 筛选方向: '{direction_search}'")
        
        # 第2步：参数验证
        # 确保页码不能小于1
        if page < 1:
            page = 1
        
        # 第3步：创建数据库连接
        db = get_database()
        
        # 连接数据库
        if not db.connect():
            return "<h1> 数据库连接失败</h1><p>无法连接到交通数据库</p>"
        
        # 第4步：根据搜索条件选择查询方法
        # 每页显示20条记录
        per_page = 20
        
        # 使用统一的组合搜索方法
        traffic_records, total_records, total_pages = db.search_with_filters(
            time_range=time_search,
            direction_filter=direction_search,
            page=page,
            per_page=per_page
        )
        
        # 生成搜索状态描述
        search_parts = []
        if time_search and time_search.strip():
            time_map = {
                'morning': '早高峰 (07:00-09:00)',
                'noon': '中午时段 (11:00-13:00)', 
                'afternoon': '下午时段 (14:00-17:00)',
                'evening': '晚高峰 (17:00-19:00)',
                'night': '夜间时段 (20:00-06:00)'
            }
            time_text = time_map.get(time_search, f"时间段{time_search}")
            search_parts.append(f"时间段'{time_text}'")
        if direction_search and direction_search.strip():
            direction_map = {'1': '北往南', '2': '南往北', '3': '东往西', '4': '西往东'}
            direction_text = direction_map.get(direction_search, f"方向{direction_search}")
            search_parts.append(f"方向'{direction_text}'")
        
        if search_parts:
            search_info = f"搜索: {'+'.join(search_parts)}"
        else:
            search_info = "显示所有记录"
        
        # 第5步：再次验证页码（防止超出范围）
        if page > total_pages and total_pages > 0:
            page = total_pages
            # 重新查询正确页码的数据，保持搜索条件
            traffic_records, total_records, total_pages = db.search_with_filters(
                time_range=time_search,
                direction_filter=direction_search,
                page=page,
                per_page=per_page
            )
        
        # 第6步：处理时间格式转换
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
        
        # 第7步：计算分页显示信息
        # 计算当前页显示的记录范围
        start_record = (page - 1) * per_page + 1
        end_record = min(page * per_page, total_records)
        
        # 获取当前时间作为更新时间
        current_time = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
        
        # 断开数据库连接
        db.disconnect()
        
        # 第8步：计算分页导航信息
        # 是否有上一页
        has_prev = page > 1
        # 是否有下一页
        has_next = page < total_pages
        # 上一页页码
        prev_page = page - 1 if has_prev else None
        # 下一页页码
        next_page = page + 1 if has_next else None
        
        # 第9步：使用模板渲染页面，传递分页和搜索信息
        return render_template('index.html',
                             traffic_records=traffic_records,
                             record_count=len(traffic_records),
                             # 分页相关信息
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records,
                             start_record=start_record,
                             end_record=end_record,
                             has_prev=has_prev,
                             has_next=has_next,
                             prev_page=prev_page,
                             next_page=next_page,
                             # 搜索相关信息
                             time_search=time_search,          # 当前时间段搜索
                             direction_search=direction_search, # 当前方向筛选
                             search_info=search_info)          # 搜索状态描述
        
    except Exception as e:
        return f"<h1> 数据库连接错误</h1><p>错误信息: {str(e)}</p>"

if __name__ == '__main__':
    # 启动Flask应用
    print(" 启动交通流量数据展示系统...")
    print(" 访问地址: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
