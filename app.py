#!/usr/bin/env python3
"""
Flask交通流量数据展示系统
在这里开始编写您的Flask应用
"""

# 导入Flask模块
from flask import Flask

# 创建Flask应用实例
app = Flask(__name__)

# 定义路由和视图函数
@app.route('/')
def index():
    """首页"""
    return "<h1>欢迎来到交通流量数据展示系统！</h1><p>Flask应用正在运行中...</p>"

if __name__ == '__main__':
    # 启动Flask应用
    print("🚀 启动交通流量数据展示系统...")
    print("📍 访问地址: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
