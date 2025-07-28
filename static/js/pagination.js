/**
 * 分页功能 JavaScript
 * 提供页码跳转功能
 */

// 跳转到指定页码
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
    
    // 获取当前URL的搜索参数
    const urlParams = new URLSearchParams(window.location.search);
    
    // 设置页码参数
    urlParams.set('page', page);
    
    // 构建新的URL并跳转
    const newUrl = window.location.pathname + '?' + urlParams.toString();
    window.location.href = newUrl;
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
});
