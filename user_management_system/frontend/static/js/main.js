document.addEventListener('DOMContentLoaded', function() {
    // 处理重置密码模态框
    if (document.getElementById('reset-password-modal')) {
        const modal = document.getElementById('reset-password-modal');
        const resetButtons = document.querySelectorAll('.btn-reset-password');
        const closeModal = document.querySelector('.close-modal');
        const resetForm = document.getElementById('reset-password-form');
        const userIdInput = document.getElementById('reset-user-id');
        
        // 点击重置密码按钮显示模态框
        resetButtons.forEach(button => {
            button.addEventListener('click', function() {
                const userId = this.getAttribute('data-user-id');
                userIdInput.value = userId;
                modal.style.display = 'block';
            });
        });
        
        // 点击关闭按钮隐藏模态框
        closeModal.addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        // 点击模态框外部隐藏模态框
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
        
        // 提交重置密码表单
        resetForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const userId = userIdInput.value;
            const newPassword = document.getElementById('new-password').value;
            
            // 构造表单数据
            const formData = new FormData();
            formData.append('new_password', newPassword);
            
            // 发送POST请求到后端
            fetch(`/reset_password/${userId}`, {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    // 刷新页面显示最新状态
                    window.location.reload();
                } else {
                    alert('密码重置失败');
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('密码重置失败');
            });
        });
    }
    
    // 检查登录状态（轮询）
    function checkLoginStatus() {
        fetch('/api/check_login')
            .then(response => response.json())
            .then(data => {
                // 如果用户未登录，跳转到登录页面
                if (!data.is_logged_in && window.location.pathname !== '/login') {
                    window.location.href = '/login';
                }
            })
            .catch(error => {
                console.error('检查登录状态失败:', error);
            });
    }
    
    // 每30秒检查一次登录状态
    setInterval(checkLoginStatus, 30000);
    
    // 初始化时检查一次登录状态
    checkLoginStatus();
    
    // 获取用户信息（可选功能，可用于显示用户信息）
    function getUserInfo() {
        fetch('/api/user_info')
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('获取用户信息失败');
                }
            })
            .then(data => {
                console.log('用户信息:', data);
                // 这里可以根据需要更新页面上的用户信息
            })
            .catch(error => {
                console.error('获取用户信息失败:', error);
            });
    }
    
    // 如果在仪表盘页面，获取用户信息
    if (window.location.pathname === '/') {
        getUserInfo();
    }
});