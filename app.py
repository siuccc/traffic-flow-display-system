#!/usr/bin/env python3
"""
Flask交通流量数据展示系统
"""

# 导入Flask相关模块
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone, timedelta
import os
import sys

# 导入我们自己的数据库模块
from utils.database import get_database
# 导入图表生成器
from utils.chart_generator import create_pie_chart_data_for_ajax, create_trend_chart_data_for_ajax, create_weekday_weekend_trend_chart_for_ajax
# 导入常量
from utils.constants import get_time_text, get_direction_text, DIRECTION_MAP

# 创建Flask应用实例
app = Flask(__name__)

# 调试开关 - 控制是否显示详细日志
DEBUG_LOGS = True  # 设为True可以看到详细日志

@app.route('/')
def index():
    """首页 - 基础模板，数据通过AJAX加载"""
    return render_template('index.html',
                         # 空数据，全部通过AJAX加载
                         traffic_records=[],
                         record_count=0,
                         current_page=1,
                         total_pages=0,
                         total_records=0,
                         start_record=0,
                         end_record=0,
                         has_prev=False,
                         has_next=False,
                         prev_page=None,
                         next_page=None,
                         time_search='',
                         direction_search='',
                         search_info='正在加载数据...',
                         # AJAX图表占位符
                         pie_chart_html='<div class="loading">📊 加载中...</div>',
                         trend_chart_html='<div class="loading">📈 加载中...</div>',
                         weekday_weekend_chart_html='<div class="loading">📈 加载中...</div>')

@app.route('/chart')
def chart():
    """图表展示页面 - 重定向到API或返回图表配置"""
    try:
        # 第1步：获取URL参数
        time_range = request.args.get('time_range', '', type=str)
        
        if DEBUG_LOGS:
            print(f"📊 生成图表，时间段: '{time_range}'")
        
        # 第2步：使用AJAX数据生成功能
        chart_data = create_pie_chart_data_for_ajax(time_range=time_range if time_range else None)
        
        # 第3步：返回JSON数据（可以被其他应用使用）
        from flask import jsonify
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'message': f'图表数据生成成功，时间段: {time_range or "全部时间"}'
        })
        
    except Exception as e:
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '图表数据生成失败'
        }), 500
    
@app.route('/api/trend-chart')
def api_trend_chart():
    """API接口 - 返回24小时趋势图数据（专门为AJAX请求设计）"""
    try:
        # 获取搜索参数
        direction_filter = request.args.get('direction', '', type=str)

        if DEBUG_LOGS:
            print(f"🔥 API调用: 24小时趋势图请求，方向='{direction_filter}'")
        
        # 生成24小时趋势图数据（调用新的AJAX专用函数）
        chart_data = create_trend_chart_data_for_ajax(
            direction_filter=direction_filter if direction_filter and direction_filter.strip() else None
        )
        
        # 返回JSON响应（包含图表数据）
        from flask import jsonify
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'message': f'24小时趋势图更新成功，方向: {direction_filter or "全部方向"}'
        })
        
    except Exception as e:
        print(f"❌ 24小时趋势图API错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '24小时趋势图生成失败'
        }), 500

@app.route('/api/pie-chart')
def api_pie_chart():
    """API接口 - 返回饼图数据（专门为AJAX请求设计）"""
    try:
        # 获取搜索参数
        time_range = request.args.get('time_range', '', type=str)
        
        # 记录API调用
        print(f"🔥 API调用: 饼图请求，时间段='{time_range}'")
        
        # 生成饼图数据（调用chart_generator中的函数）
        chart_data = create_pie_chart_data_for_ajax(
            time_range=time_range if time_range and time_range.strip() else None
        )
        
        # 返回JSON响应（包含图表数据）
        from flask import jsonify
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'message': f'饼图更新成功，时间段: {time_range or "全部时间"}'
        })
        
    except Exception as e:
        print(f"❌ 饼图API错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '饼图生成失败'
        }), 500
    
@app.route('/api/weekday-weekend-chart')
def api_weekday_weekend_chart():
    """API接口 - 返回工作日vs周末对比图数据（专门为AJAX请求设计）"""
    try:
        #获取搜索参数
        direction_filter = request.args.get('direction', '', type=str)              #这个图只受方向选择的影响

        #记录api调用
        if DEBUG_LOGS:
            print(f"🔥 API调用: 工作日vs周末对比图请求，方向='{direction_filter}'")
        # 生成工作日vs周末对比图数据
        chart_data = create_weekday_weekend_trend_chart_for_ajax(
            direction_filter=direction_filter if direction_filter and direction_filter.strip() else None        #判断是否有数据输入
        )
        #返回json响应（包含图表数据）
        from flask import jsonify
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'message': f'工作日vs周末对比图更新成功，方向: {direction_filter or "全部方向"}'
        })
    except Exception as e:
        print(f"❌ 工作日vs周末对比图API错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '工作日vs周末对比图生成失败'
        }), 500
    
@app.route('/api/traffic-data')
def api_traffic_data():
    """API接口 - 返回交通流量数据 （供前端JavaScript使用）"""
    try:
        # 获取查询参数
        time_range = request.args.get('time_range', '', type=str)
        direction = request.args.get('direction', '', type=str)
        page = request.args.get('page', 1, type=int)
        
        # 记录API调用
        if DEBUG_LOGS:
            print(f"🔢 API调用: 交通数据请求，页码={page}")
            if time_range:
                print(f"🕒 搜索时间段: '{time_range}'")
            if direction:
                print(f"🧭 筛选方向: '{direction}'")
        
        # 参数验证
        if page < 1:
            page = 1
        
        # 创建数据库连接
        db = get_database()
        if not db.connect():
            return jsonify({
                'success': False,
                'error': '数据库连接失败',
                'message': '无法连接到交通数据库'
            }), 500
        
        # 查询数据
        per_page = 20
        traffic_records, total_records, total_pages = db.search_with_filters(
            time_range=time_range if time_range and time_range.strip() else None,
            direction_filter=direction if direction and direction.strip() else None,
            page=page,
            per_page=per_page
        )
        
        # 页码范围验证
        if page > total_pages and total_pages > 0:
            page = total_pages
            traffic_records, total_records, total_pages = db.search_with_filters(
                time_range=time_range if time_range and time_range.strip() else None,
                direction_filter=direction if direction and direction.strip() else None,
                page=page,
                per_page=per_page
            )
        
        # 生成搜索状态描述
        search_parts = []
        if time_range and time_range.strip():
            time_text = get_time_text(time_range)
            search_parts.append(f"时间段'{time_text}'")
        if direction and direction.strip():
            direction_text = get_direction_text(direction)
            search_parts.append(f"方向'{direction_text}'")
        
        search_info = f"搜索: {'+'.join(search_parts)}" if search_parts else "显示所有记录"
        
        # 处理时间格式转换
        for record in traffic_records:
            timestamp = record['time']
            beijing_tz = timezone(timedelta(hours=8))
            beijing_time = datetime.fromtimestamp(timestamp, tz=beijing_tz)
            record['formatted_time'] = beijing_time.strftime('%Y-%m-%d %H:%M:%S (北京时间)')
            record['direction_text'] = get_direction_text(record['direction'])
        
        # 计算分页信息
        start_record = (page - 1) * per_page + 1
        end_record = min(page * per_page, total_records)
        
        # 断开数据库连接
        db.disconnect()
        
        # 计算分页导航信息
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
        
        # 返回JSON响应
        return jsonify({
            'success': True,
            'data': traffic_records,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_records': total_records,
                'per_page': per_page,
                'start_record': start_record,
                'end_record': end_record,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_page': prev_page,
                'next_page': next_page
            },
            'search_info': search_info,
            'filters': {
                'time_range': time_range,
                'direction': direction
            }
        })
        
    except Exception as e:
        print(f"❌ 交通数据API错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取交通数据失败'
        }), 500


if __name__ == '__main__':
    # 启动Flask应用
    print(" 启动交通流量数据展示系统...")
    print(" 访问地址: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
