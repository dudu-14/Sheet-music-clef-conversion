/**
 * 通用JavaScript功能
 */

// 全局变量
window.ClefConverter = window.ClefConverter || {};

// 工具函数
ClefConverter.Utils = {
    /**
     * 显示提示消息
     */
    showToast: function(message, type = 'info') {
        const toast = document.getElementById('globalToast');
        const toastBody = toast.querySelector('.toast-body');
        const toastHeader = toast.querySelector('.toast-header');
        const icon = toastHeader.querySelector('i');
        
        // 设置消息内容
        toastBody.textContent = message;
        
        // 设置图标和样式
        icon.className = 'me-2';
        toast.className = 'toast';
        
        switch(type) {
            case 'success':
                icon.classList.add('fas', 'fa-check-circle', 'text-success');
                toast.classList.add('border-success');
                break;
            case 'error':
                icon.classList.add('fas', 'fa-exclamation-triangle', 'text-danger');
                toast.classList.add('border-danger');
                break;
            case 'warning':
                icon.classList.add('fas', 'fa-exclamation-circle', 'text-warning');
                toast.classList.add('border-warning');
                break;
            default:
                icon.classList.add('fas', 'fa-info-circle', 'text-primary');
                toast.classList.add('border-primary');
        }
        
        // 显示提示框
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    },
    
    /**
     * 显示加载遮罩
     */
    showLoading: function(message = '处理中，请稍候...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay.querySelector('p');
        text.textContent = message;
        overlay.classList.remove('d-none');
    },
    
    /**
     * 隐藏加载遮罩
     */
    hideLoading: function() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.add('d-none');
    },
    
    /**
     * 格式化文件大小
     */
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    /**
     * 格式化时间
     */
    formatTime: function(seconds) {
        if (seconds < 60) {
            return seconds.toFixed(1) + ' 秒';
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = Math.floor(seconds % 60);
            return minutes + ' 分 ' + remainingSeconds + ' 秒';
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return hours + ' 小时 ' + minutes + ' 分';
        }
    },
    
    /**
     * 验证文件类型
     */
    validateFileType: function(file) {
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff', 'image/gif'];
        return allowedTypes.includes(file.type);
    },
    
    /**
     * 验证文件大小
     */
    validateFileSize: function(file, maxSizeMB = 100) {
        const maxSizeBytes = maxSizeMB * 1024 * 1024;
        return file.size <= maxSizeBytes;
    },
    
    /**
     * 生成唯一ID
     */
    generateId: function() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * 防抖函数
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * 节流函数
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * 复制文本到剪贴板
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text).then(() => {
                this.showToast('已复制到剪贴板', 'success');
            }).catch(() => {
                this.showToast('复制失败', 'error');
            });
        } else {
            // 降级方案
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showToast('已复制到剪贴板', 'success');
            } catch (err) {
                this.showToast('复制失败', 'error');
            }
            document.body.removeChild(textArea);
        }
    }
};

// API请求封装
ClefConverter.API = {
    /**
     * 基础请求方法
     */
    request: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        };
        
        const finalOptions = Object.assign({}, defaultOptions, options);
        
        return fetch(url, finalOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('API请求失败:', error);
                throw error;
            });
    },
    
    /**
     * GET请求
     */
    get: function(url) {
        return this.request(url, { method: 'GET' });
    },
    
    /**
     * POST请求
     */
    post: function(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    /**
     * 上传文件
     */
    upload: function(url, formData) {
        return fetch(url, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },
    
    /**
     * 健康检查
     */
    healthCheck: function() {
        return this.get('/api/health');
    },
    
    /**
     * 获取支持的格式
     */
    getSupportedFormats: function() {
        return this.get('/api/formats');
    },
    
    /**
     * 获取系统统计
     */
    getStats: function() {
        return this.get('/api/stats');
    }
};

// 事件管理
ClefConverter.Events = {
    listeners: {},
    
    /**
     * 添加事件监听器
     */
    on: function(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    },
    
    /**
     * 移除事件监听器
     */
    off: function(event, callback) {
        if (!this.listeners[event]) return;
        
        const index = this.listeners[event].indexOf(callback);
        if (index > -1) {
            this.listeners[event].splice(index, 1);
        }
    },
    
    /**
     * 触发事件
     */
    emit: function(event, data) {
        if (!this.listeners[event]) return;
        
        this.listeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('事件处理器错误:', error);
            }
        });
    }
};

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化弹出框
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 添加页面加载动画
    document.body.classList.add('fade-in');
    
    // 检查API健康状态
    ClefConverter.API.healthCheck()
        .then(data => {
            console.log('API健康检查通过:', data);
        })
        .catch(error => {
            console.warn('API健康检查失败:', error);
            ClefConverter.Utils.showToast('服务连接异常，部分功能可能不可用', 'warning');
        });
    
    // 触发页面加载完成事件
    ClefConverter.Events.emit('pageLoaded');
});

// 错误处理
window.addEventListener('error', function(event) {
    console.error('页面错误:', event.error);
    ClefConverter.Utils.showToast('页面发生错误，请刷新重试', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('未处理的Promise拒绝:', event.reason);
    ClefConverter.Utils.showToast('操作失败，请重试', 'error');
});

// 导出到全局
window.ClefConverter = ClefConverter;
