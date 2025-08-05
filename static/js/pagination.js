/**
 * 分页功能 JavaScript - AJAX版本
 * 提供无刷新页码跳转功能，保持搜索条件
 */

// 当前页码（全局变量）
let currentPage = 1;

// AJAX加载指定页码的数据
async function loadPage(page) {
    try {
        // 显示加载状态
        showLoadingState(page);
        
        // 获取当前搜索条件
        const timeRangeElement = document.getElementById('timeRangeSelect');
        const directionElement = document.getElementById('directionSelect');
        const timeRange = timeRangeElement?.value || '';
        const direction = directionElement?.value || '';
        
        console.log('🔍 搜索元素检查:', {
            timeRangeElement: timeRangeElement,
            directionElement: directionElement,
            timeRangeValue: timeRange,
            directionValue: direction
        });
        
        // 构建API请求URL
        const params = new URLSearchParams({
            page: page,
            time_range: timeRange,
            direction: direction
        });
        
        console.log(`🔢 AJAX翻页: 加载第${page}页，搜索条件: 时间="${timeRange}", 方向="${direction}"`);
        
        // 调用API
        const response = await fetch(`/api/traffic-data?${params}`);
        const data = await response.json();
        
        if (data.success) {
            // 更新表格内容
            updateTableContent(data.data);
            // 更新分页UI
            updatePaginationUI(data.pagination);
            // 更新搜索信息显示
            updateSearchInfo(data.search_info, data.pagination.total_records, timeRange, direction);
            // 更新当前页码
            currentPage = data.pagination.current_page;
            
            console.log(`✅ 翻页成功: 第${data.pagination.current_page}页，共${data.pagination.total_records}条记录`);
        } else {
            throw new Error(data.message || '数据加载失败');
        }
        
    } catch (error) {
        console.error('❌ 翻页失败:', error);
        showErrorMessage('翻页失败: ' + error.message);
    } finally {
        hideLoadingState();
    }
}

// 显示加载状态
function showLoadingState(targetPage) {
    const tableBody = document.querySelector('#traffic-table tbody');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px;">
                    <div style="color: #666;">⏳ 正在加载第${targetPage}页数据...</div>
                </td>
            </tr>
        `;
    }
    
    // 禁用分页按钮
    const paginationBtns = document.querySelectorAll('.page-btn, .page-num, .jump-btn');
    paginationBtns.forEach(btn => {
        btn.style.pointerEvents = 'none';
        btn.style.opacity = '0.5';
    });
}

// 隐藏加载状态
function hideLoadingState() {
    // 恢复分页按钮
    const paginationBtns = document.querySelectorAll('.page-btn, .page-num, .jump-btn');
    paginationBtns.forEach(btn => {
        btn.style.pointerEvents = 'auto';
        btn.style.opacity = '1';
    });
}

// 更新表格内容
function updateTableContent(trafficRecords) {
    const tableBody = document.querySelector('#traffic-table tbody');
    if (!tableBody) return;
    
    if (trafficRecords.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px;">
                    <div style="color: #999;">📭 没有找到符合条件的数据</div>
                </td>
            </tr>
        `;
        return;
    }
    
    // 生成表格行（字段对应：id, direction_text, formatted_time, plate）
    const rows = trafficRecords.map(record => `
        <tr>
            <td class="center">${record.id}</td>
            <td class="center direction-${record.direction}">${record.direction_text}</td>
            <td class="time">${record.formatted_time}</td>
            <td class="center plate">${record.plate}</td>
        </tr>
    `).join('');
    
    tableBody.innerHTML = rows;
}

// 更新分页UI
function updatePaginationUI(pagination) {
    // 更新页码显示信息
    const recordInfo = document.querySelector('.record-info');
    if (recordInfo) {
        recordInfo.textContent = `显示第 ${pagination.start_record}-${pagination.end_record} 条，共 ${pagination.total_records} 条记录`;
    }
    
    // 更新页码输入框
    const pageInput = document.getElementById('pageInput');
    if (pageInput) {
        pageInput.max = pagination.total_pages;
        pageInput.placeholder = pagination.current_page;
    }
    
    // 完全重新生成分页按钮区域
    regeneratePaginationButtons(pagination);
}

// 完全重新生成分页按钮区域
function regeneratePaginationButtons(pagination) {
    const paginationContainer = document.getElementById('pagination-container');
    if (!paginationContainer) {
        console.error('找不到分页容器');
        return;
    }
    
    // 生成页码按钮HTML
    let pageNumbersHtml = '';
    
    // 如果总页数大于1，才显示完整的页码
    if (pagination.total_pages > 1) {
        // 显示第一页
        if (pagination.current_page > 3) {
            pageNumbersHtml += '<button class="page-num" data-page="1">1</button>';
            if (pagination.current_page > 4) {
                pageNumbersHtml += '<span class="page-dots">...</span>';
            }
        }
        
        // 显示当前页前后的页码
        const startPage = Math.max(1, pagination.current_page - 2);
        const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            if (i === pagination.current_page) {
                pageNumbersHtml += `<span class="page-num current">${i}</span>`;
            } else {
                pageNumbersHtml += `<button class="page-num" data-page="${i}">${i}</button>`;
            }
        }
        
        // 显示最后一页
        if (pagination.current_page < pagination.total_pages - 2) {
            if (pagination.current_page < pagination.total_pages - 3) {
                pageNumbersHtml += '<span class="page-dots">...</span>';
            }
            pageNumbersHtml += `<button class="page-num" data-page="${pagination.total_pages}">${pagination.total_pages}</button>`;
        }
    } else {
        // 只有一页的情况
        pageNumbersHtml = '<span class="page-num current">1</span>';
    }
    
    // 重新生成整个分页区域
    paginationContainer.innerHTML = `
        <!-- 上一页按钮 -->
        <button class="page-btn prev-btn ${pagination.has_prev ? '' : 'disabled'}" ${pagination.has_prev ? `data-page="${pagination.prev_page}"` : ''}>
            ⬅️ 上一页
        </button>
        
        <!-- 页码显示 -->
        <div class="page-numbers">
            ${pageNumbersHtml}
        </div>
        
        <!-- 页码跳转输入框 -->
        <div class="page-jump">
            <span class="jump-label">跳转到</span>
            <input type="number" id="pageInput" class="page-input" min="1" max="${pagination.total_pages}" placeholder="${pagination.current_page}">
            <button onclick="jumpToPage()" class="jump-btn">GO</button>
        </div>
        
        <!-- 下一页按钮 -->
        <button class="page-btn next-btn ${pagination.has_next ? '' : 'disabled'}" ${pagination.has_next ? `data-page="${pagination.next_page}"` : ''}>
            下一页 ➡️
        </button>
    `;
}

// 更新分页按钮状态
function updatePaginationButtons(pagination) {
    // 更新上一页按钮
    const prevBtn = document.querySelector('.prev-btn');
    if (prevBtn) {
        if (pagination.has_prev) {
            prevBtn.classList.remove('disabled');
            prevBtn.setAttribute('data-page', pagination.prev_page);
        } else {
            prevBtn.classList.add('disabled');
            prevBtn.removeAttribute('data-page');
        }
    }
    
    // 更新下一页按钮
    const nextBtn = document.querySelector('.next-btn');
    if (nextBtn) {
        if (pagination.has_next) {
            nextBtn.classList.remove('disabled');
            nextBtn.setAttribute('data-page', pagination.next_page);
        } else {
            nextBtn.classList.add('disabled');
            nextBtn.removeAttribute('data-page');
        }
    }
    
    // 更新当前页码显示
    const currentPageSpan = document.querySelector('.page-num.current');
    if (currentPageSpan) {
        currentPageSpan.textContent = pagination.current_page;
    }
}

// 更新搜索信息显示
function updateSearchInfo(searchInfo, totalRecords, timeRange, direction) {
    // 更新下方的搜索信息
    const searchInfoElement = document.querySelector('.search-info');
    if (searchInfoElement) {
        searchInfoElement.textContent = searchInfo;
    }
    
    // 更新上方的搜索状态显示
    const searchStatusElement = document.getElementById('search-status-text');
    if (searchStatusElement) {
        // 判断是否有搜索条件
        const hasSearchConditions = timeRange || direction;
        
        if (hasSearchConditions) {
            searchStatusElement.innerHTML = `🎯 ${searchInfo} - 找到 <strong>${totalRecords.toLocaleString()}</strong> 条记录`;
        } else {
            searchStatusElement.innerHTML = `📋 ${searchInfo} - 共 <strong>${totalRecords.toLocaleString()}</strong> 条记录`;
        }
    }
}

// 显示错误信息
function showErrorMessage(message) {
    const tableBody = document.querySelector('#traffic-table tbody');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px;">
                    <div style="color: #d32f2f;">❌ ${message}</div>
                    <button onclick="loadPage(currentPage)" style="margin-top: 10px;">重试</button>
                </td>
            </tr>
        `;
    }
}

// 跳转到指定页码（修改为AJAX版本）
function jumpToPage() {
    const pageInput = document.getElementById('pageInput');
    const page = parseInt(pageInput.value);
    const totalPages = parseInt(pageInput.getAttribute('max'));
    
    // 验证输入
    if (isNaN(page) || page < 1 || page > totalPages) {
        alert(`请输入有效的页码 (1-${totalPages})`);
        pageInput.value = '';
        return;
    }
    
    // AJAX加载页面
    loadPage(page);
    pageInput.value = '';
}

// 设置分页事件监听器
function setupPaginationEvents() {
    // 监听所有分页按钮的点击事件
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        // 处理页码按钮点击
        if (target.classList.contains('page-num') && !target.classList.contains('current') && target.hasAttribute('data-page')) {
            event.preventDefault();
            const page = parseInt(target.getAttribute('data-page'));
            if (!isNaN(page)) {
                loadPage(page);
            }
        }
        
        // 处理上一页/下一页按钮
        if (target.classList.contains('page-btn') && !target.classList.contains('disabled') && target.hasAttribute('data-page')) {
            event.preventDefault();
            const page = parseInt(target.getAttribute('data-page'));
            if (!isNaN(page)) {
                loadPage(page);
            }
        }
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    const pageInput = document.getElementById('pageInput');
    
    if (pageInput) {
        // 支持回车键跳转
        pageInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                jumpToPage();
            }
        });
        
        // 自动选中输入框内容（方便快速输入）
        pageInput.addEventListener('focus', function() {
            this.select();
        });
    }
    
    // 设置分页事件监听器
    setupPaginationEvents();
    
    // 加载第一页数据
    console.log('🚀 初始化AJAX分页系统');
    loadPage(1);
});

// 导出函数供其他脚本使用
window.loadPage = loadPage;
window.jumpToPage = jumpToPage;
