/**
 * 文件上传功能
 */

(function() {
    'use strict';
    
    let selectedFile = null;
    let uploadArea = null;
    let fileInput = null;
    
    // 初始化上传功能
    function initUpload() {
        uploadArea = document.getElementById('uploadArea');
        fileInput = document.getElementById('fileInput');
        
        if (!uploadArea || !fileInput) {
            console.error('上传元素未找到');
            return;
        }
        
        // 绑定事件
        bindEvents();
    }
    
    // 绑定事件
    function bindEvents() {
        // 点击上传区域
        uploadArea.addEventListener('click', function(e) {
            if (e.target.tagName !== 'BUTTON') {
                fileInput.click();
            }
        });
        
        // 文件选择
        fileInput.addEventListener('change', handleFileSelect);
        
        // 拖拽事件
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
        
        // 阻止默认拖拽行为
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
    }
    
    // 阻止默认行为
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // 处理拖拽悬停
    function handleDragOver(e) {
        uploadArea.classList.add('dragover');
    }
    
    // 处理拖拽离开
    function handleDragLeave(e) {
        uploadArea.classList.remove('dragover');
    }
    
    // 处理文件拖拽放下
    function handleDrop(e) {
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }
    
    // 处理文件选择
    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }
    
    // 处理文件
    function handleFile(file) {
        // 验证文件类型
        if (!ClefConverter.Utils.validateFileType(file)) {
            ClefConverter.Utils.showToast('不支持的文件格式，请选择图片文件', 'error');
            return;
        }
        
        // 验证文件大小
        if (!ClefConverter.Utils.validateFileSize(file, 100)) {
            ClefConverter.Utils.showToast('文件过大，最大支持100MB', 'error');
            return;
        }
        
        // 保存文件引用
        selectedFile = file;
        
        // 显示文件信息
        showFileInfo(file);
        
        // 启用转换按钮
        enableConvertButton();
        
        // 触发文件选择事件
        ClefConverter.Events.emit('fileSelected', file);
        
        ClefConverter.Utils.showToast('文件选择成功', 'success');
    }
    
    // 显示文件信息
    function showFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = ClefConverter.Utils.formatFileSize(file.size);
            fileInfo.classList.remove('d-none');
            
            // 更新上传区域样式
            uploadArea.classList.add('has-file');
        }
    }
    
    // 启用转换按钮
    function enableConvertButton() {
        const convertBtn = document.getElementById('convertBtn');
        if (convertBtn) {
            convertBtn.disabled = false;
            convertBtn.classList.remove('btn-secondary');
            convertBtn.classList.add('btn-primary');
        }
    }
    
    // 禁用转换按钮
    function disableConvertButton() {
        const convertBtn = document.getElementById('convertBtn');
        if (convertBtn) {
            convertBtn.disabled = true;
            convertBtn.classList.remove('btn-primary');
            convertBtn.classList.add('btn-secondary');
        }
    }
    
    // 清除文件
    function clearFile() {
        selectedFile = null;
        fileInput.value = '';
        
        // 隐藏文件信息
        const fileInfo = document.getElementById('fileInfo');
        if (fileInfo) {
            fileInfo.classList.add('d-none');
        }
        
        // 恢复上传区域样式
        uploadArea.classList.remove('has-file');
        
        // 禁用转换按钮
        disableConvertButton();
        
        // 触发文件清除事件
        ClefConverter.Events.emit('fileCleared');
        
        ClefConverter.Utils.showToast('文件已清除', 'info');
    }
    
    // 获取选中的文件
    function getSelectedFile() {
        return selectedFile;
    }
    
    // 验证文件
    function validateFile() {
        if (!selectedFile) {
            ClefConverter.Utils.showToast('请先选择文件', 'warning');
            return false;
        }
        
        return true;
    }
    
    // 创建FormData
    function createFormData() {
        if (!selectedFile) {
            return null;
        }
        
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        // 添加处理选项
        const highQuality = document.getElementById('highQuality');
        if (highQuality && highQuality.checked) {
            formData.append('high_quality', 'true');
        }
        
        // 添加输出格式
        const formats = getSelectedFormats();
        formData.append('formats', formats.join(','));
        
        return formData;
    }
    
    // 获取选中的输出格式
    function getSelectedFormats() {
        const formats = [];
        
        const formatPng = document.getElementById('formatPng');
        if (formatPng && formatPng.checked) {
            formats.push('png');
        }
        
        const formatPdf = document.getElementById('formatPdf');
        if (formatPdf && formatPdf.checked) {
            formats.push('pdf');
        }
        
        const formatMidi = document.getElementById('formatMidi');
        if (formatMidi && formatMidi.checked) {
            formats.push('midi');
        }
        
        return formats.length > 0 ? formats : ['png'];
    }
    
    // 重置表单
    function resetForm() {
        clearFile();
        
        // 重置选项
        const highQuality = document.getElementById('highQuality');
        if (highQuality) {
            highQuality.checked = false;
        }
        
        const formatPng = document.getElementById('formatPng');
        if (formatPng) {
            formatPng.checked = true;
        }
        
        const formatPdf = document.getElementById('formatPdf');
        if (formatPdf) {
            formatPdf.checked = false;
        }
        
        const formatMidi = document.getElementById('formatMidi');
        if (formatMidi) {
            formatMidi.checked = false;
        }
        
        // 隐藏结果和错误区域
        const resultSection = document.getElementById('resultSection');
        if (resultSection) {
            resultSection.classList.add('d-none');
        }
        
        const errorSection = document.getElementById('errorSection');
        if (errorSection) {
            errorSection.classList.add('d-none');
        }
        
        const progressSection = document.getElementById('progressSection');
        if (progressSection) {
            progressSection.classList.add('d-none');
        }
    }
    
    // 导出到全局
    window.clearFile = clearFile;
    window.resetForm = resetForm;
    
    // 导出到ClefConverter命名空间
    ClefConverter.Upload = {
        getSelectedFile: getSelectedFile,
        validateFile: validateFile,
        createFormData: createFormData,
        getSelectedFormats: getSelectedFormats,
        clearFile: clearFile,
        resetForm: resetForm
    };
    
    // 页面加载完成后初始化
    ClefConverter.Events.on('pageLoaded', initUpload);
    
})();
