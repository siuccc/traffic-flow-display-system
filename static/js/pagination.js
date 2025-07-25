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
    
    // 跳转到目标页
    window.location.href = '/?page=' + page;
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
