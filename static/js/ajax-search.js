/**
 * AJAX搜索功能 JavaScript
 * 负责处理搜索表单的AJAX提交、图表更新和数据表格更新
 */

// 发送AJAX请求更新饼图
function updatePieChart(timeRange) {
    console.log('🔄 开始更新饼图，时间段:', timeRange);
    
    // 先检查容器是否存在
    const pieContainer = document.getElementById('pie-chart-container');
    if (!pieContainer) {
        console.error('❌ 找不到饼图容器！无法更新饼图');
        alert('错误：找不到饼图容器！');
        return;
    }
    
    // 构建API请求URL
    const apiUrl = '/api/pie-chart' + (timeRange ? `?time_range=${timeRange}` : '');
    console.log('🌐 请求URL:', apiUrl);
    
    // 显示加载状态
    const originalContent = pieContainer.innerHTML;
    pieContainer.innerHTML = '<div style="padding: 20px; text-align: center;">🔄 正在更新饼图...</div>';
    
    // 发送AJAX请求
    fetch(apiUrl)
        .then(response => {
            console.log('📡 收到响应，状态:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📦 收到数据:', data);
            if (data.success) {
                // 成功：使用Plotly API直接绘制图表
                const chartData = data.chart_data;
                console.log('📊 图表配置:', chartData);
                
                // 清空容器并重新绘制
                pieContainer.innerHTML = '';
                
                // 使用Plotly.newPlot直接绘制图表
                if (window.Plotly) {
                    Plotly.newPlot(pieContainer, chartData.data, chartData.layout, {responsive: true});
                    console.log('✅ 饼图更新成功:', data.message);
                } else {
                    // 如果Plotly没有加载，先加载Plotly库
                    console.log('📚 Plotly库未加载，正在加载...');
                    const script = document.createElement('script');
                    script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
                    script.onload = function() {
                        Plotly.newPlot(pieContainer, chartData.data, chartData.layout, {responsive: true});
                        console.log('✅ 饼图更新成功（已加载Plotly）:', data.message);
                    };
                    document.head.appendChild(script);
                }
                
            } else {
                // 失败：显示错误信息
                pieContainer.innerHTML = `<div style="padding: 20px; color: red;">❌ ${data.message}</div>`;
                console.error('❌ 饼图更新失败:', data.error);
            }
        })
        .catch(error => {
            // 网络错误：恢复原内容并显示错误
            pieContainer.innerHTML = originalContent;
            console.error('❌ 网络请求失败:', error);
            alert('网络请求失败: ' + error.message);
        });
}
//发送AJAX表单请求更新趋势图
function updateTrendChart(direction){
    console.log('🔄 开始更新趋势图，方向:', direction);

    // 先检查容器是否存在
    const trendContainer = document.getElementById('trend-chart');
    console.log('🔍 查找趋势图容器，结果:', trendContainer);
    console.log('🔍 当前页面所有元素ID:', Array.from(document.querySelectorAll('[id]')).map(el => el.id));
    
    if (!trendContainer) {
        console.error('❌ 找不到趋势图容器！无法更新趋势图');
        alert('错误：找不到趋势图容器！');
        return;
    }
    
    // 构建API请求URL（只传递方向参数）
    const apiUrl = '/api/trend-chart' + (direction ? `?direction=${direction}` : '');
    console.log('🌐 趋势图请求URL:', apiUrl);
    
    // 显示加载状态
    const originalContent = trendContainer.innerHTML;
    trendContainer.innerHTML = '<div style="padding: 20px; text-align: center;">📈 正在更新趋势图...</div>';
    
    // 发送AJAX请求
    fetch(apiUrl)
        .then(response => {
            console.log('📡 趋势图响应状态:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📦 趋势图数据:', data);
            if (data.success) {
                // 成功：使用Plotly API直接绘制图表
                const chartData = data.chart_data;
                console.log('📈 趋势图配置:', chartData);
                
                // 清空容器并重新绘制
                trendContainer.innerHTML = '';
                
                // 使用Plotly.newPlot直接绘制图表
                if (window.Plotly) {
                    Plotly.newPlot(trendContainer, chartData.data, chartData.layout, {responsive: true});
                    console.log('✅ 趋势图更新成功:', data.message);
                } else {
                    // 如果Plotly没有加载，先加载Plotly库
                    console.log('📚 Plotly库未加载，正在加载...');
                    const script = document.createElement('script');
                    script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
                    script.onload = function() {
                        Plotly.newPlot(trendContainer, chartData.data, chartData.layout, {responsive: true});
                        console.log('✅ 趋势图更新成功（已加载Plotly）:', data.message);
                    };
                    document.head.appendChild(script);
                }
                
            } else {
                // 失败：显示错误信息
                trendContainer.innerHTML = `<div style="padding: 20px; color: red;">❌ ${data.message}</div>`;
                console.error('❌ 趋势图更新失败:', data.error);
            }
        })
        .catch(error => {
            // 网络错误：恢复原内容并显示错误
            trendContainer.innerHTML = originalContent;
            console.error('❌ 趋势图网络请求失败:', error);
            alert('趋势图网络请求失败: ' + error.message);
        });
}

//发送Ajax表单请求更新工作日vs周末对比图
function updateWeekdayWeekendChart(direction) {
    console.log('🔄 开始更新工作日vs周末对比图');
    
    // 先检查容器是否存在
    const chartContainer = document.getElementById('weekday-weekend-chart');
    if (!chartContainer) {
        console.error('❌ 找不到工作日vs周末对比图容器！无法更新图表');
        alert('错误：找不到工作日vs周末对比图容器！');
        return;
    }
    
    // 构建API请求URL
    const apiUrl = '/api/weekday-weekend-chart' + (direction ? `?direction=${direction}` : '');
    console.log('🌐 工作日vs周末对比图请求URL:', apiUrl);
    
    // 显示加载状态
    const originalContent = chartContainer.innerHTML;
    chartContainer.innerHTML = '<div style="padding: 20px; text-align: center;">📊 正在更新工作日vs周末对比图...</div>';
    
    // 发送AJAX请求
    fetch(apiUrl)
        .then(response => {
            console.log('📡 收到响应，状态:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📦 收到数据:', data);
            if (data.success) {
                // 成功：使用Plotly API直接绘制图表
                const chartData = data.chart_data;
                console.log('📊 工作日vs周末对比图配置:', chartData);
                
                // 清空容器并重新绘制
                chartContainer.innerHTML = '';
                
                // 使用Plotly.newPlot直接绘制图表
                if (window.Plotly) {
                    Plotly.newPlot(chartContainer, chartData.data, chartData.layout, {responsive: true});
                    console.log('✅ 工作日vs周末对比图更新成功:', data.message);
                } else {
                    // 如果Plotly没有加载，先加载Plotly库
                    console.log('📚 Plotly库未加载，正在加载...');
                    const script = document.createElement('script');
                    script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
                    script.onload = function() {
                        Plotly.newPlot(chartContainer, chartData.data, chartData.layout, {responsive: true});
                        console.log('✅ 工作日vs周末对比图更新成功（已加载Plotly）:', data.message);
                    };
                    document.head.appendChild(script);
                }
            } else {
                // 失败：显示错误信息
                chartContainer.innerHTML = `<div style="padding: 20px; color: red;">❌ ${data.message}</div>`;
                console.error('❌ 工作日vs周末对比图更新失败:', data.error);
            }
        })
        .catch(error => {
            // 网络错误：恢复原内容并显示错误   
            chartContainer.innerHTML = originalContent;
            console.error('❌ 工作日vs周末对比图网络请求失败:', error);
            alert('工作日vs周末对比图网络请求失败: ' + error.message);
        });
}
// 设置搜索表单AJAX拦截
function setupSearchForm() {
    const searchForm = document.querySelector('.search-form');
    
    if (searchForm) {
        console.log('✅ 找到搜索表单，设置AJAX拦截...');
        
        searchForm.addEventListener('submit', function(event) {
            // 阻止表单的默认提交行为（防止页面跳转）
            event.preventDefault();
            
            console.log('🔍 搜索表单被提交，使用AJAX处理...');
            
            // 获取表单数据
            const formData = new FormData(searchForm);
            const timeRange = formData.get('time_range') || '';
            const direction = formData.get('direction') || '';
            
            console.log('搜索参数:', {
                time_range: timeRange,
                direction: direction
            });
            
            // 同时调用多个图表更新函数
            console.log('🎯 开始批量更新图表和数据表格...');
            updatePieChart(timeRange);
            updateTrendChart(direction);
            updateWeekdayWeekendChart(direction);
            
            // 更新数据表格（重置到第1页）
            if (window.loadPage) {
                console.log('� 更新数据表格，重置到第1页');
                window.loadPage(1);
            } else {
                console.warn('⚠️ loadPage函数未找到，跳过数据表格更新');
            }
            
            console.log('�🚀 所有更新请求已发送');
        });
        
        return true;
    } else {
        console.error('❌ 找不到搜索表单！');
        return false;
    }
}

// 页面加载完成后初始化AJAX系统
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AJAX搜索系统初始化中...');
    console.log('🔍 DOM状态:', document.readyState);
    console.log('🔍 页面中所有ID:', Array.from(document.querySelectorAll('[id]')).map(el => el.id));
    
    // 等待一小段时间确保所有内容都加载完成
    setTimeout(function() {
        console.log('⏰ 延迟初始化开始...');
        console.log('🔍 延迟后的所有ID:', Array.from(document.querySelectorAll('[id]')).map(el => el.id));
        
        // 设置搜索表单拦截
        setupSearchForm();
        
        // 自动加载初始图表（无搜索条件）
        console.log('🎯 自动加载初始图表...');
        updatePieChart('');
        updateTrendChart('');  // 空字符串表示不限制方向
        updateWeekdayWeekendChart('');  // 加载工作日vs周末图表
        console.log('✅ 初始图表加载请求已发送');
    }, 100); // 等待100毫秒
});
