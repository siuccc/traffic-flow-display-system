# 交通流量数据展示系统

## 项目描述
一个基于Flask的Web应用，用于展示和分析交通流量数据。系统支持按时间段、方向、车牌号等多维度搜索交通数据，提供直观的数据可视化和统计分析功能。

## 功能特性
- 🔍 **多维度搜索**：按时间段、方向、车牌号等条件精确搜索
- 📊 **数据可视化**：生成交互式图表展示流量趋势和统计信息
- 🌐 **响应式界面**：简洁美观的Web界面
- 📈 **实时统计**：车流量统计、高峰期分析、方向分布等
- 🚗 **智能匹配**：支持车牌号的模糊搜索和精确匹配
- 📄 **数据导出**：支持搜索结果导出功能

## 开发阶段规划

### 第一阶段 - 静态页面展示 🎯
- [x] 项目初始化和环境搭建
- [x] 创建Flask基础应用结构
- [ ] 设计HTML模板，展示前20条交通数据
- [ ] 实现基本的路由和视图函数
- [ ] 创建简洁的CSS样式

### 第二阶段 - 动态页面功能 🚀
- [ ] 实现数据分页查询功能
- [ ] 添加搜索表单和筛选功能
- [ ] 动态生成数据表格
- [ ] 实现AJAX异步数据加载
- [ ] 优化页面性能和用户体验

### 第三阶段 - 高级搜索算法 🔍
- [ ] 时间段搜索（如：某天7-8点的数据）
- [ ] 方向筛选（南北/东西方向车流）
- [ ] 复合条件搜索和逻辑组合
- [ ] 搜索结果排序和高级过滤
- [ ] 搜索历史记录功能

### 第四阶段 - 扩展功能 ✨
- [ ] 数据可视化图表（Plotly/Chart.js）
- [ ] 实时数据监控仪表盘
- [ ] 车流量预测和趋势分析
- [ ] 数据统计报表生成
- [ ] RESTful API接口
- [ ] 数据导入/导出功能

## 项目结构
```
交通流量数据展示系统/
├── app.py                  # Flask应用主入口
├── config.py               # 应用配置文件
├── requirements.txt        # 项目依赖包
├── utils/                  # 工具函数模块
│   ├── __init__.py         
│   ├── data_handler.py     # 数据处理和读取
│   ├── search_engine.py    # 搜索算法实现
│   └── chart_generator.py  # 图表生成工具
├── templates/              # Jinja2模板文件
│   ├── base.html           # 基础模板
│   ├── index.html          # 首页模板
│   ├── search.html         # 搜索页面
│   └── results.html        # 结果展示页面
├── static/                 # 静态资源文件
│   ├── css/                
│   │   └── style.css       # 样式文件
│   ├── js/                 
│   │   └── main.js         # JavaScript脚本
│   └── images/             # 图片资源
├── data/                   # 数据文件目录
│   └── traffic.db          # 交通流量数据库文件
├── tests/                  # 测试文件
│   ├── test_app.py         # 应用测试
│   └── test_utils.py       # 工具函数测试
├── README.md               # 项目说明
└── .gitignore              # Git忽略文件
```

## 安装和运行

### 环境要求
- Python 3.8+
- 已安装pip包管理工具

### 快速开始

1. **克隆项目**
```bash
git clone <your-repo-url>
cd "first python project"
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **准备数据文件**
```bash
# 交通数据库文件已准备就绪
# 数据库文件位置: data/traffic.db
```

4. **启动应用**
```bash
python app.py
```

5. **访问应用**
```
在浏览器中打开: http://localhost:5001
```

### 开发模式运行
```bash
# 启动开发服务器（调试模式）
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py

# 运行测试
python -m pytest tests/

# 查看测试覆盖率
pytest --cov=utils tests/
```

## 使用说明

### 基本功能演示
1. **浏览数据**：访问首页查看最新的20条交通记录
2. **搜索功能**：使用搜索表单按条件筛选数据
3. **数据可视化**：查看图表分析车流趋势
4. **导出数据**：将搜索结果导出为CSV文件

### 搜索示例
```
- 时间范围搜索：2024-01-01 08:00 至 2024-01-01 18:00
- 方向筛选：选择"北向"查看北向车流
- 车牌搜索：输入"粤A"查找所有粤A开头的车牌
- 复合搜索：结合时间+方向+车牌号进行精确查找
```

### API接口（第四阶段实现）
```bash
# 获取所有交通数据
GET /api/traffic

# 按条件搜索
GET /api/search?start_time=2024-01-01&end_time=2024-01-02&direction=north

# 获取统计数据
GET /api/stats?date=2024-01-01

# 导出数据
GET /api/export?format=csv&search_params=...
```

## 数据格式说明
系统支持的CSV数据格式：
```csv
timestamp,plate_number,direction,location,speed,vehicle_type
2024-01-01 08:00:00,粤A12345,北向,路口A,45.5,小型车
2024-01-01 08:01:00,粤B67890,南向,路口B,52.0,大型车
2024-01-01 08:02:00,京C11111,东向,路口C,38.2,小型车
```

### 字段说明
- `timestamp`: 记录时间 (YYYY-MM-DD HH:MM:SS)
- `plate_number`: 车牌号码
- `direction`: 行驶方向 (北向/南向/东向/西向)
- `location`: 记录位置
- `speed`: 车辆速度 (km/h)
- `vehicle_type`: 车辆类型 (小型车/大型车/摩托车等)

## 技术栈
- **后端框架**: Flask 2.3+ (轻量级、灵活的Web框架)
- **模板引擎**: Jinja2 (Flask内置模板引擎)
- **数据处理**: Pandas (数据分析和CSV处理)
- **数据可视化**: Plotly + Chart.js (交互式图表)
- **前端技术**: HTML5 + CSS3 + JavaScript + Bootstrap
- **数据存储**: CSV文件 (可扩展到SQLite/MySQL)
- **测试框架**: pytest + Flask-Testing

## 开发指南

### 添加新功能
1. 在 `app.py` 中添加新的路由和视图函数
2. 在 `utils/` 中创建相应的数据处理模块
3. 在 `templates/` 中设计HTML模板
4. 在 `static/` 中添加CSS/JS资源
5. 编写对应的测试用例

## 版本信息
- **当前版本**: v0.1.0
- **Python版本**: 3.8+
- **Flask版本**: 2.3+
- **创建日期**: 2025年7月23日
- **最后更新**: 2025年7月23日

## 更新日志
### v0.1.0 (2025-07-23)
- 🎉 项目初始化，确定技术栈
- 📋 完成项目规划和分阶段目标
- 📝 编写详细的项目文档
- 🏗️ 设计Flask应用架构

