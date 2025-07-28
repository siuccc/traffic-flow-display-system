#!/usr/bin/env python3
"""
测试时间段搜索功能 - pytest版本
"""

import pytest
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils.database import TrafficDatabase


class TestTimeSearch:
    """时间段搜索功能测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def database(self):
        """创建数据库连接"""
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'traffic.db')
        db = TrafficDatabase(db_path)
        if db.connect():
            yield db
            db.disconnect()
        else:
            pytest.skip("数据库连接失败")
    
    def test_database_search_morning_time(self, database):
        """测试数据库层：搜索早高峰时间段"""
        records, total_records, total_pages = database.search_with_filters(
            time_range='morning', page=1, per_page=5
        )
        
        assert isinstance(records, list)
        assert isinstance(total_records, int)
        assert isinstance(total_pages, int)
        assert len(records) <= 5
        
        # 如果有记录，验证时间确实在早高峰范围内
        if records:
            import datetime
            for record in records:
                # 将Unix时间戳转换为时间对象验证小时
                dt = datetime.datetime.fromtimestamp(record['time'])
                hour = dt.hour
                assert 7 <= hour <= 8, f"记录时间{hour}不在早高峰范围内"
    
    def test_database_search_evening_time(self, database):
        """测试数据库层：搜索晚高峰时间段"""
        records, total_records, total_pages = database.search_with_filters(
            time_range='evening', page=1, per_page=10
        )
        
        assert isinstance(records, list)
        assert len(records) <= 10
        
        # 如果有记录，验证时间确实在晚高峰范围内
        if records:
            import datetime
            for record in records:
                dt = datetime.datetime.fromtimestamp(record['time'])
                hour = dt.hour
                assert 17 <= hour <= 18, f"记录时间{hour}不在晚高峰范围内"
    
    def test_database_search_night_time(self, database):
        """测试数据库层：搜索夜间时间段（跨日期）"""
        records, total_records, total_pages = database.search_with_filters(
            time_range='night', page=1, per_page=5
        )
        
        assert isinstance(records, list)
        assert isinstance(total_records, int)
        assert isinstance(total_pages, int)
        assert len(records) <= 5
        
        # 如果有记录，验证时间确实在夜间范围内（20:00-06:00）
        if records:
            import datetime
            for record in records:
                dt = datetime.datetime.fromtimestamp(record['time'])
                hour = dt.hour
                assert (hour >= 20 or hour <= 5), f"记录时间{hour}不在夜间范围内"
    
    def test_database_search_empty_time_query(self, database):
        """测试数据库层：空时间段查询"""
        records, total_records, total_pages = database.search_with_filters(
            time_range='', page=1, per_page=5
        )
        
        # 空查询应该返回所有记录（分页后的结果）
        assert isinstance(records, list)
        assert len(records) == 5  # per_page参数
        assert total_records > 0
    
    def test_web_home_page(self, client):
        """测试Web层：访问主页"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert '交通数据概览' in response.get_data(as_text=True)
        assert '时间段' in response.get_data(as_text=True)
        assert 'search-section' in response.get_data(as_text=True)
    
    def test_web_search_morning_time(self, client):
        """测试Web层：搜索早高峰时间段"""
        response = client.get('/?time_range=morning')
        
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert 'selected' in content  # 下拉框应该保持选中状态
        assert '早高峰' in content
    
    def test_web_search_with_pagination(self, client):
        """测试Web层：时间段搜索结合分页"""
        response = client.get('/?time_range=evening&page=2')
        
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert '晚高峰' in content
        # 检查分页链接是否保持搜索参数
        assert 'time_range=evening&page=' in content
    
    def test_web_search_combined_filters(self, client):
        """测试Web层：时间段和方向组合搜索"""
        response = client.get('/?time_range=morning&direction=1')
        
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert '早高峰' in content
        assert '北往南' in content
    
    def test_web_search_no_results(self, client):
        """测试Web层：搜索无结果的情况"""
        # 使用一个不太可能有数据的时间段进行测试
        response = client.get('/?time_range=noon')
        
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        # 检查页面正常渲染，即使没有结果
        assert '中午时段' in content
    
    def test_web_pagination_links_preserve_search(self, client):
        """测试Web层：分页链接保持搜索条件"""
        response = client.get('/?time_range=evening&direction=2')
        content = response.get_data(as_text=True)
        
        # 检查分页链接是否包含时间段和方向参数
        if 'page-num' in content:
            assert 'time_range=evening' in content
            assert 'direction=2' in content


if __name__ == "__main__":
    # 运行特定测试
    pytest.main([__file__, "-v"])
