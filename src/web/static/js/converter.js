/**
 * 转换功能
 */

(function() {
    'use strict';
    
    let currentTaskId = null;
    let progressInterval = null;
    
    // 开始转换
    function startConversion() {
        // 验证文件
        if (!ClefConverter.Upload.validateFile()) {
            return;
        }
        
        // 显示进度区域
        showProgressSection();
        
        // 禁用转换按钮
        const convertBtn = document.getElementById('convertBtn');
        if (convertBtn) {
            convertBtn.disabled = true;
            convertBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>处理中...';
        }
        
        // 上传文件
        uploadFile()
            .then(response => {
                currentTaskId = response.task_id;
                ClefConverter.Utils.showToast('文件上传成功，开始转换...', 'success');
                
                // 开始转换
                return startConversionTask();
            })
            .then(() => {
                // 开始监控进度
                startProgressMonitoring();
            })
            .catch(error => {
                console.error('转换失败:', error);
                showError(error.message || '转换失败');
                resetConvertButton();
            });
    }
    
    // 上传文件
    function uploadFile() {
        const formData = ClefConverter.Upload.createFormData();
        if (!formData) {
            throw new Error('无法创建表单数据');
        }
        
        updateProgress(10, '上传文件...');
        
        return ClefConverter.API.upload('/upload', formData);
    }
    
    // 开始转换任务
    function startConversionTask() {
        if (!currentTaskId) {
            throw new Error('任务ID不存在');
        }
        
        const options = {
            high_quality: document.getElementById('highQuality')?.checked || false,
            formats: ClefConverter.Upload.getSelectedFormats()
        };
        
        updateProgress(20, '初始化转换...');
        
        return fetch(`/convert/${currentTaskId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    }
    
    // 开始进度监控
    function startProgressMonitoring() {
        if (!currentTaskId) {
            return;
        }
        
        progressInterval = setInterval(() => {
            checkTaskStatus();
        }, 1000); // 每秒检查一次
        
        // 设置超时
        setTimeout(() => {
            if (progressInterval) {
                clearInterval(progressInterval);
                showError('转换超时，请重试');
                resetConvertButton();
            }
        }, 300000); // 5分钟超时
    }
    
    // 检查任务状态
    function checkTaskStatus() {
        if (!currentTaskId) {
            return;
        }
        
        fetch(`/status/${currentTaskId}`)
            .then(response => response.json())
            .then(data => {
                updateProgress(data.progress, data.message);
                
                if (data.status === 'completed') {
                    // 转换完成
                    clearInterval(progressInterval);
                    progressInterval = null;
                    showResult(data);
                } else if (data.status === 'failed') {
                    // 转换失败
                    clearInterval(progressInterval);
                    progressInterval = null;
                    showError(data.error || '转换失败');
                    resetConvertButton();
                }
            })
            .catch(error => {
                console.error('状态检查失败:', error);
                clearInterval(progressInterval);
                progressInterval = null;
                showError('状态检查失败');
                resetConvertButton();
            });
    }
    
    // 显示进度区域
    function showProgressSection() {
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.classList.remove('d-none');
        }
        
        // 隐藏其他区域
        const resultSection = document.getElementById('resultSection');
        if (resultSection) {
            resultSection.classList.add('d-none');
        }
        
        const errorSection = document.getElementById('errorSection');
        if (errorSection) {
            errorSection.classList.add('d-none');
        }
    }
    
    // 更新进度
    function updateProgress(percentage, message) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const progressMessage = document.getElementById('progressMessage');
        
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
        }
        
        if (progressText) {
            progressText.textContent = Math.round(percentage) + '%';
        }
        
        if (progressMessage) {
            progressMessage.textContent = message || '处理中...';
        }
    }
    
    // 显示结果
    function showResult(data) {
        const resultSection = document.getElementById('resultSection');
        const notesCount = document.getElementById('notesCount');
        const processingTime = document.getElementById('processingTime');
        const downloadLinks = document.getElementById('downloadLinks');
        
        if (resultSection) {
            resultSection.classList.remove('d-none');
        }
        
        if (notesCount) {
            notesCount.textContent = data.notes_count || 0;
        }
        
        if (processingTime) {
            processingTime.textContent = ClefConverter.Utils.formatTime(data.processing_time || 0);
        }
        
        if (downloadLinks && data.output_files) {
            downloadLinks.innerHTML = '';
            data.output_files.forEach(format => {
                const link = createDownloadLink(format);
                downloadLinks.appendChild(link);
            });
        }
        
        // 隐藏进度区域
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.classList.add('d-none');
        }
        
        // 重置转换按钮
        resetConvertButton();
        
        ClefConverter.Utils.showToast('转换完成！', 'success');
    }
    
    // 创建下载链接
    function createDownloadLink(format) {
        const link = document.createElement('a');
        link.href = `/download/${currentTaskId}/${format}`;
        link.className = 'btn btn-outline-primary btn-sm me-2 mb-2';
        link.download = true;
        
        let icon = 'fas fa-download';
        let text = format.toUpperCase();
        
        switch(format) {
            case 'png':
                icon = 'fas fa-image';
                text = 'PNG 图片';
                break;
            case 'pdf':
                icon = 'fas fa-file-pdf';
                text = 'PDF 文档';
                break;
            case 'midi':
                icon = 'fas fa-music';
                text = 'MIDI 音频';
                break;
            case 'svg':
                icon = 'fas fa-vector-square';
                text = 'SVG 矢量';
                break;
        }
        
        link.innerHTML = `<i class="${icon} me-1"></i>${text}`;
        
        return link;
    }
    
    // 显示错误
    function showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorSection) {
            errorSection.classList.remove('d-none');
        }
        
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        
        // 隐藏进度区域
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.classList.add('d-none');
        }
        
        ClefConverter.Utils.showToast(message, 'error');
    }
    
    // 重置转换按钮
    function resetConvertButton() {
        const convertBtn = document.getElementById('convertBtn');
        if (convertBtn) {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '<i class="fas fa-magic me-2"></i>开始转换';
        }
    }
    
    // 清理任务
    function cleanupTask() {
        if (currentTaskId) {
            fetch(`/cleanup/${currentTaskId}`, {
                method: 'DELETE'
            }).catch(error => {
                console.warn('清理任务失败:', error);
            });
            
            currentTaskId = null;
        }
        
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }
    
    // 导出到全局
    window.startConversion = startConversion;
    
    // 导出到ClefConverter命名空间
    ClefConverter.Converter = {
        startConversion: startConversion,
        cleanupTask: cleanupTask
    };
    
    // 页面卸载时清理任务
    window.addEventListener('beforeunload', cleanupTask);
    
})();
