#!/bin/bash
# 停止交通流量数据展示系统

echo "⏹️  正在停止交通流量数据展示系统..."

# 查找并杀死占用5001端口的进程
if lsof -ti:5001 > /dev/null; then
    echo "📡 发现端口5001被占用，正在释放..."
    lsof -ti:5001 | xargs kill
    echo "✅ 端口5001已释放"
else
    echo "✅ 端口5001未被占用"
fi

# 也可以杀死所有app.py相关进程
pkill -f "python.*app.py" 2>/dev/null || true

echo "🎯 系统已停止"
