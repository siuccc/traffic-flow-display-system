#!/usr/bin/env python3
"""
交通流量图表生成器
使用Plotly生成交互式图表，连接真实数据库数据

主要功能：
- 为AJAX请求生成饼图数据 (create_pie_chart_data_for_ajax)
- 为AJAX请求生成24小时趋势图数据 (create_trend_chart_data_for_ajax)  
- 为AJAX请求生成工作日vs周末对比图数据 (create_weekday_weekend_trend_chart_for_ajax)

所有函数返回JSON格式的Plotly图表配置，供前端JavaScript使用
"""

import plotly.graph_objects as go
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.database import get_database

# 在作为模块运行时使用相对导入，作为脚本运行时使用绝对导入
try:
    from .constants import TIME_RANGE_MAP, DIRECTION_STR_MAP, CHART_COLORS
except ImportError:
    from constants import TIME_RANGE_MAP, DIRECTION_STR_MAP, CHART_COLORS

def create_pie_chart_data_for_ajax(time_range=None):
    """
    专门为AJAX请求创建饼图数据（返回图表配置而不是HTML）
    
    Args:
        time_range: 时间段筛选 ('morning', 'noon', 'afternoon', 'evening', 'night')
    
    Returns:
        dict: Plotly图表配置数据
    """
    print(f"🎨 正在生成AJAX饼图数据，时间段: {time_range}")
    
    # 连接数据库获取真实数据
    db = get_database()
    
    if not db.connect():
        print("❌ 数据库连接失败")
        raise Exception("无法连接数据库")
    
    try:
        # 获取方向分布数据
        direction_data = db.get_direction_distribution(time_range=time_range)
        db.disconnect()
        
        if not direction_data:
            print("⚠️ 没有找到数据")
            raise Exception("暂无数据可显示")
        
        print(f"📊 获取到方向数据: {direction_data}")
        
        # 准备数据 - direction_data是{方向ID: 数量}的字典格式
        labels = []
        values = []
        
        for direction_id, count in direction_data.items():
            label = DIRECTION_STR_MAP.get(str(direction_id), f"方向{direction_id}")
            labels.append(label)
            values.append(count)
        
        colors = CHART_COLORS['directions'][:len(labels)]
        
        # 设置标题
        title_suffix = TIME_RANGE_MAP.get(time_range, '') if time_range else ''
        title = f"交通方向分布{' - ' + title_suffix if title_suffix else ''}"
        
        # 返回Plotly图表配置
        chart_config = {
            'data': [{
                'labels': labels,
                'values': values,
                'type': 'pie',
                'hole': 0.3,
                'marker': {
                    'colors': colors
                }
            }],
            'layout': {
                'title': {
                    'text': title,
                    'x': 0.5,
                    'font': {'size': 18, 'family': 'Arial, sans-serif'}
                },
                'font': {'size': 14},
                'showlegend': True,
                'legend': {
                    'orientation': 'h',
                    'yanchor': 'bottom',
                    'y': -0.2,
                    'xanchor': 'center',
                    'x': 0.5
                },
                'margin': {'t': 60, 'b': 100, 'l': 20, 'r': 20},
                'height': 400
            }
        }
        
        print(f"✅ AJAX饼图数据生成成功！数据总量：{sum(values)}")
        return chart_config
            
    except Exception as e:
        print(f"❌ 生成AJAX饼图数据时发生错误：{e}")
        db.disconnect()
        raise e

def create_trend_chart_data_for_ajax(direction_filter=None):
    """
    专门为AJAX请求创建24小时趋势图数据（返回图表配置而不是HTML）
    
    Args:
        direction_filter: 方向筛选 ('1', '2', '3', '4')，None表示所有方向
    
    Returns:
        dict: Plotly图表配置数据
    """
    print(f"📈 正在生成AJAX趋势图数据，方向: {direction_filter}")
    
    # 连接数据库获取趋势数据
    db = get_database()
    
    if not db.connect():
        print("❌ 数据库连接失败")
        raise Exception("无法连接数据库")
    
    try:
        # 获取24小时趋势数据
        hourly_data = db.get_hourly_traffic_trend(direction_filter=direction_filter)
        db.disconnect()
        
        if not hourly_data or sum(hourly_data.values()) == 0:
            print("⚠️ 没有找到趋势数据")
            raise Exception("暂无趋势数据可显示")
        
        print(f"📈 获取到趋势数据: {sum(hourly_data.values())} 总车流量")
        
        # 准备图表数据
        hours = list(range(24))  # 0-23小时
        counts = [hourly_data[hour] for hour in hours]
        time_labels = [f"{hour:02d}:00" for hour in hours]
        
        # 设置图表标题
        title = "24小时车流量趋势"
        if direction_filter:
            direction_name = DIRECTION_STR_MAP.get(str(direction_filter), f'方向{direction_filter}')
            title += f" - {direction_name}"
        
        # 返回Plotly图表配置
        chart_config = {
            'data': [{
                'x': time_labels,
                'y': counts,
                'mode': 'lines+markers',
                'name': '车流量',
                'type': 'scatter',
                'line': {
                    'color': CHART_COLORS['trend_line'],
                    'width': 3,
                    'shape': 'spline'
                },
                'marker': {
                    'size': 8,
                    'color': CHART_COLORS['trend_marker'],
                    'line': {'color': 'white', 'width': 2}
                },
                'hovertemplate': '<b>时间：%{x}</b><br>' +
                               '车流量：%{y}辆<br>' +
                               '<extra></extra>'
            }],
            'layout': {
                'title': {
                    'text': title,
                    'x': 0.5,
                    'font': {'size': 18, 'family': 'Arial, sans-serif'}
                },
                'xaxis': {
                    'title': '时间（小时）',
                    'tickangle': 45,
                    'showgrid': True,
                    'gridwidth': 1,
                    'gridcolor': 'rgba(128,128,128,0.2)',
                    'tickmode': 'array',
                    'tickvals': list(range(0, 24, 2)),
                    'ticktext': [f"{hour:02d}:00" for hour in range(0, 24, 2)]
                },
                'yaxis': {
                    'title': '车流量（辆）',
                    'showgrid': True,
                    'gridwidth': 1,
                    'gridcolor': 'rgba(128,128,128,0.2)'
                },
                'font': {'size': 12},
                'showlegend': False,
                'margin': {'t': 60, 'b': 80, 'l': 80, 'r': 40},
                'height': 400,
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'autosize': True
            }
        }
        
        print(f"✅ AJAX趋势图数据生成成功！数据总量：{sum(counts)}")
        return chart_config
            
    except Exception as e:
        print(f"❌ 生成AJAX趋势图数据时发生错误：{e}")
        db.disconnect()
        raise e
    
def create_weekday_weekend_trend_chart_for_ajax(direction_filter=None):
    """
    专门为AJAX请求创建工作日vs周末趋势对比图（返回图表配置而不是HTML）
    
    Args:
        direction_filter: 方向筛选 ('1', '2', '3', '4')，None表示所有方向
    
    Returns:
        dict: Plotly图表配置数据
    """
    print(f"📈 正在生成AJAX工作日vs周末对比图数据，方向: {direction_filter}")
    
    # 连接数据库获取真实数据
    db = get_database()
    
    if not db.connect():
        print("❌ 数据库连接失败")
        raise Exception("无法连接数据库")
    
    try:
        # 获取按工作日/周末区分的24小时平均趋势数据
        trend_data = db.get_hourly_traffic_trend_by_weekday(direction_filter=direction_filter)
        db.disconnect()
        
        weekday_data = trend_data['weekday']  # 工作日平均每小时
        weekend_data = trend_data['weekend']  # 周末平均每小时
        
        # 检查是否有数据
        weekday_total = sum(weekday_data.values())
        weekend_total = sum(weekend_data.values())
        
        if weekday_total == 0 and weekend_total == 0:
            print("⚠️ 没有找到工作日vs周末数据")
            raise Exception("暂无数据可显示")
        
        print(f"📊 获取到工作日数据总计: {weekday_total}, 周末数据总计: {weekend_total}")
        
        # 准备小时数据（0-23小时）
        hours = list(range(24))
        weekday_values = [weekday_data.get(hour, 0) for hour in hours]
        weekend_values = [weekend_data.get(hour, 0) for hour in hours]
        
        # 创建Plotly图表
        fig = go.Figure()
        
        # 添加工作日数据线
        fig.add_trace(go.Scatter(
            x=hours,
            y=weekday_values,
            mode='lines+markers',
            name='工作日平均',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6),
            hovertemplate='<b>工作日</b><br>时间: %{x}:00<br>平均车流量: %{y}<extra></extra>'
        ))
        
        # 添加周末数据线
        fig.add_trace(go.Scatter(
            x=hours,
            y=weekend_values,
            mode='lines+markers',
            name='周末平均',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=6),
            hovertemplate='<b>周末</b><br>时间: %{x}:00<br>平均车流量: %{y}<extra></extra>'
        ))
        
        # 设置图表布局
        direction_text = {
            '1': '北往南',
            '2': '南往北', 
            '3': '东往西',
            '4': '西往东'
        }.get(direction_filter, '全部方向')
        
        fig.update_layout(
            title=f'📊 工作日vs周末流量对比 ({direction_text})',
            xaxis_title='时间 (小时)',
            yaxis_title='平均车流量',
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=2,
                range=[-0.5, 23.5]
            ),
            yaxis=dict(
                title='平均车流量',
                showgrid=True
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=400,
            margin=dict(l=50, r=50, t=80, b=50),
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # 返回图表配置数据（需要转换为可JSON序列化的格式）
        chart_config = {
            'data': [trace.to_plotly_json() for trace in fig.data],
            'layout': fig.layout.to_plotly_json()
        }
        
        print(f"✅ AJAX工作日vs周末对比图数据生成成功")
        return chart_config
        
    except Exception as e:
        print(f"❌ 生成AJAX工作日vs周末对比图数据时发生错误：{e}")
        db.disconnect()
        raise e

if __name__ == '__main__':
    # 测试函数
    print("🧪 测试图表生成器...")
    
    # 测试饼图
    print("\n📊 测试方向分布饼图:")
    pie_chart_data = create_pie_chart_data_for_ajax()
    print("📊 饼图数据生成完成！")
    
    # 测试趋势图
    print("\n📈 测试24小时趋势图数据:")
    trend_chart_data = create_trend_chart_data_for_ajax()
    print("📈 趋势图数据生成完成！")
    
    # 测试工作日vs周末对比图
    print("\n📈 测试工作日vs周末趋势对比图:")
    weekday_weekend_chart_data = create_weekday_weekend_trend_chart_for_ajax()
    print("📈 工作日vs周末对比图数据生成完成！")
    
    print("\n🎉 所有图表测试完成！")