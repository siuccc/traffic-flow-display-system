#!/usr/bin/env python3
"""
交通流量图表生成器
使用Plotly生成交互式图表，连接真实数据库数据
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

def create_direction_pie_chart(time_range=None, direction_filter=None):
    """
    创建方向分布饼图，基于真实数据库数据
    
    Args:
        time_range: 时间段筛选 ('morning', 'noon', 'afternoon', 'evening', 'night')
        direction_filter: 方向筛选 ('1', '2', '3', '4')
    
    Returns:
        str: Plotly图表的HTML代码
    """
    print(f"🎨 正在生成方向分布图表...")
    
    # 连接数据库获取真实数据
    db = get_database()
    
    if not db.connect():
        print("❌ 数据库连接失败")
        return "<div class='alert alert-danger'>📊 无法连接数据库生成图表</div>"
    
    try:
        # 获取方向分布数据
        direction_data = db.get_direction_distribution(time_range=time_range)
        db.disconnect()
        
        if not direction_data:
            print("⚠️ 没有找到数据")
            return "<div class='alert alert-warning'>📊 暂无数据可显示</div>"
        
        # 创建饼图
        labels = ['北往南', '南往北', '东往西', '西往东']
        values = [
            direction_data.get(1, 0),  # 北往南
            direction_data.get(2, 0),  # 南往北  
            direction_data.get(3, 0),  # 东往西
            direction_data.get(4, 0)   # 西往东
        ]
        colors = CHART_COLORS['directions']
        
        # 过滤掉值为0的数据
        filtered_data = [(label, value, color) for label, value, color in zip(labels, values, colors) if value > 0]
        
        if not filtered_data:
            return "<div class='alert alert-warning'>📊 所选条件下暂无数据</div>"
        
        labels, values, colors = zip(*filtered_data)
        
        fig = go.Figure(data=go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.3  # 创建甜甜圈样式
        ))
        
        # 设置标题
        title = "交通方向分布"
        if time_range:
            title += f" - {TIME_RANGE_MAP.get(time_range, time_range)}"
        
        # 更新图表布局
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=18, family="Arial, sans-serif")
            ),
            font=dict(size=14),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=60, b=100, l=20, r=20),
            height=400
        )
        
        # 转换为HTML
        html_str = fig.to_html(include_plotlyjs='cdn', div_id="direction-chart")
        print(f"✅ 图表生成成功！数据总量：{sum(values)}")
        return html_str
    
    except Exception as e:
        print(f"❌ 生成图表时发生错误：{e}")
        db.disconnect()
        return "<div class='alert alert-danger'>📊 图表生成失败，请稍后重试</div>"

def create_hourly_trend_chart(direction_filter: str = None) -> str:
    """
    生成24小时车流量趋势折线图
    
    Args:
        direction_filter: 方向筛选 ('1', '2', '3', '4')，None表示所有方向
        
    Returns:
        str: Plotly图表的HTML代码
    """
    print(f"📈 正在生成24小时趋势图表...")
    
    # 连接数据库获取趋势数据
    db = get_database()
    
    if not db.connect():
        print("❌ 数据库连接失败")
        return "<div class='alert alert-danger'>📈 无法连接数据库生成趋势图表</div>"
    
    try:
        # 获取24小时趋势数据
        hourly_data = db.get_hourly_traffic_trend(direction_filter=direction_filter)
        db.disconnect()
        
        if not hourly_data or sum(hourly_data.values()) == 0:
            print("⚠️ 没有找到趋势数据")
            return "<div class='alert alert-warning'>📈 暂无趋势数据可显示</div>"
        
        # 准备图表数据
        hours = list(range(24))  # 0-23小时
        counts = [hourly_data[hour] for hour in hours]
        
        # 创建时间标签（更友好的显示）
        time_labels = [f"{hour:02d}:00" for hour in hours]
        
        # 创建折线图
        fig = go.Figure()
        
        # 添加折线
        fig.add_trace(go.Scatter(
            x=time_labels,
            y=counts,
            mode='lines+markers',
            name='车流量',
            line=dict(
                color=CHART_COLORS['trend_line'],
                width=3,
                shape='spline'  # 平滑曲线
            ),
            marker=dict(
                size=8,
                color=CHART_COLORS['trend_marker'],
                line=dict(color='white', width=2)
            ),
            hovertemplate='<b>时间：%{x}</b><br>' +
                         '车流量：%{y}辆<br>' +
                         '<extra></extra>'
        ))
        
        # 设置图表标题
        title = "24小时车流量趋势"
        if direction_filter:
            direction_name = DIRECTION_STR_MAP.get(direction_filter, f'方向{direction_filter}')
            title += f" - {direction_name}"
        
        # 更新图表布局
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=18, family="Arial, sans-serif")
            ),
            xaxis=dict(
                title="时间（小时）",
                tickangle=45,
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                tickmode='array',
                tickvals=list(range(0, 24, 2)),  # 每隔2小时显示一个刻度
                ticktext=[f"{hour:02d}:00" for hour in range(0, 24, 2)]
            ),
            yaxis=dict(
                title="车流量（辆）",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            font=dict(size=12),
            showlegend=False,
            margin=dict(t=60, b=80, l=80, r=40),
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            autosize=True  # 自动适应容器大小
        )
        
        # 转换为HTML
        html_str = fig.to_html(include_plotlyjs='cdn', div_id="trend-chart")
        total_traffic = sum(counts)
        print(f"✅ 趋势图表生成成功！总车流量：{total_traffic}")
        return html_str
    
    except Exception as e:
        print(f"❌ 生成趋势图表时发生错误：{e}")
        db.disconnect()
        return "<div class='alert alert-danger'>📈 趋势图表生成失败，请稍后重试</div>"

def create_weekday_weekend_trend_chart(direction_filter: str = None) -> str:
    """
    生成工作日vs周末的24小时平均车流量趋势对比图
    
    Args:
        direction_filter: 方向筛选 ('1', '2', '3', '4')，None表示所有方向
        
    Returns:
        str: Plotly图表的HTML代码
    """
    print(f"📈 正在生成工作日vs周末平均趋势对比图...")
    
    # 连接数据库获取趋势数据
    db = get_database()
    
    if not db.connect():
        print("❌ 数据库连接失败")
        return "<div class='alert alert-danger'>📈 无法连接数据库生成对比图表</div>"
    
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
            print("⚠️ 没有找到趋势数据")
            return "<div class='alert alert-warning'>📈 暂无趋势数据可显示</div>"
        
        # 准备图表数据
        hours = list(range(24))  # 0-23小时
        weekday_counts = [weekday_data[hour] for hour in hours]
        weekend_counts = [weekend_data[hour] for hour in hours]
        
        # 创建时间标签（更友好的显示）
        time_labels = [f"{hour:02d}:00" for hour in hours]
        
        # 创建折线图
        fig = go.Figure()
        
        # 添加工作日折线
        fig.add_trace(go.Scatter(
            x=time_labels,
            y=weekday_counts,
            mode='lines+markers',
            name='工作日平均 (周一至周五)',
            line=dict(
                color=CHART_COLORS['weekday_line'],
                width=3,
                shape='spline'  # 平滑曲线
            ),
            marker=dict(
                size=6,
                color=CHART_COLORS['weekday_marker'],
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>工作日平均 - %{x}</b><br>' +
                         '平均车流量：%{y:.0f}辆/小时<br>' +
                         '<extra></extra>'
        ))
        
        # 添加周末折线
        fig.add_trace(go.Scatter(
            x=time_labels,
            y=weekend_counts,
            mode='lines+markers',
            name='周末平均 (周六至周日)',
            line=dict(
                color=CHART_COLORS['weekend_line'],
                width=3,
                shape='spline'  # 平滑曲线
            ),
            marker=dict(
                size=6,
                color=CHART_COLORS['weekend_marker'],
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>周末平均 - %{x}</b><br>' +
                         '平均车流量：%{y:.0f}辆/小时<br>' +
                         '<extra></extra>'
        ))
        
        # 设置图表标题
        title = "工作日vs周末平均车流量对比"
        if direction_filter:
            direction_name = DIRECTION_STR_MAP.get(direction_filter, f'方向{direction_filter}')
            title += f" - {direction_name}"
        
        # 更新图表布局
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=18, family="Arial, sans-serif")
            ),
            xaxis=dict(
                title="时间（小时）",
                tickangle=45,
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)',
                tickmode='array',
                tickvals=list(range(0, 24, 2)),  # 每隔2小时显示一个刻度
                ticktext=[f"{hour:02d}:00" for hour in range(0, 24, 2)]
            ),
            yaxis=dict(
                title="平均车流量（辆/小时）",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            font=dict(size=12),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=60, b=100, l=80, r=40),
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            autosize=True  # 自动适应容器大小
        )
        
        # 转换为HTML
        html_str = fig.to_html(include_plotlyjs='cdn', div_id="weekday-weekend-trend-chart")
        print(f"✅ 工作日vs周末平均对比图生成成功！")
        print(f"   工作日平均每小时总和：{weekday_total:.0f}")
        print(f"   周末平均每小时总和：{weekend_total:.0f}")
        return html_str
    
    except Exception as e:
        print(f"❌ 生成工作日vs周末对比图时发生错误：{e}")
        db.disconnect()
        return "<div class='alert alert-danger'>📈 工作日vs周末对比图生成失败，请稍后重试</div>"

if __name__ == '__main__':
    # 测试函数
    print("🧪 测试图表生成器...")
    
    # 测试饼图
    print("\n📊 测试方向分布饼图:")
    pie_chart = create_direction_pie_chart()
    print("📊 饼图生成完成！")
    
    # 测试折线图
    print("\n📈 测试24小时趋势折线图:")
    trend_chart = create_hourly_trend_chart()
    print("📈 趋势图生成完成！")
    
    # 测试工作日vs周末对比图
    print("\n📈 测试工作日vs周末趋势对比图:")
    weekday_weekend_chart = create_weekday_weekend_trend_chart()
    print("📈 工作日vs周末对比图生成完成！")
    
    print("\n🎉 所有图表测试完成！")