"""
Flask Web应用主文件
提供谱号转换的Web界面
"""

import os
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
import tempfile
import threading
import time

from ..core.converter import ClefConverter
from ..utils.logger import get_logger, configure_default_logging
from ..utils.file_utils import validate_image_file, cleanup_temp_files

logger = get_logger(__name__)


def create_app(config=None):
    """
    创建Flask应用
    
    Args:
        config: 配置字典
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 基本配置
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB
        'UPLOAD_FOLDER': tempfile.gettempdir(),
        'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'gif'},
        'OUTPUT_FORMATS': ['png', 'pdf', 'midi'],
        'PROCESSING_TIMEOUT': 300,  # 5分钟
    })
    
    # 应用自定义配置
    if config:
        app.config.update(config)
    
    # 配置日志
    configure_default_logging(verbose=app.debug)
    
    # 存储转换任务的字典
    conversion_tasks = {}
    
    def allowed_file(filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        """
        处理文件上传
        """
        try:
            # 检查是否有文件
            if 'file' not in request.files:
                return jsonify({'error': '没有选择文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '没有选择文件'}), 400
            
            # 检查文件类型
            if not allowed_file(file.filename):
                return jsonify({'error': '不支持的文件格式'}), 400
            
            # 保存文件
            filename = secure_filename(file.filename)
            task_id = str(uuid.uuid4())
            upload_dir = Path(app.config['UPLOAD_FOLDER']) / 'clef_converter' / task_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / filename
            file.save(str(file_path))
            
            # 验证图像文件
            if not validate_image_file(file_path):
                return jsonify({'error': '无效的图像文件'}), 400
            
            # 获取处理选项
            options = {
                'high_quality': request.form.get('high_quality', 'false').lower() == 'true',
                'output_formats': request.form.get('formats', 'png').split(',')
            }
            
            # 创建任务记录
            conversion_tasks[task_id] = {
                'status': 'uploaded',
                'progress': 0,
                'message': '文件上传成功',
                'input_file': str(file_path),
                'output_files': {},
                'error': None,
                'created_at': time.time()
            }
            
            logger.info(f"文件上传成功: {filename}, 任务ID: {task_id}")
            
            return jsonify({
                'task_id': task_id,
                'filename': filename,
                'message': '文件上传成功'
            })
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return jsonify({'error': f'上传失败: {str(e)}'}), 500
    
    @app.route('/convert/<task_id>', methods=['POST'])
    def start_conversion(task_id):
        """
        开始转换任务
        """
        try:
            if task_id not in conversion_tasks:
                return jsonify({'error': '任务不存在'}), 404
            
            task = conversion_tasks[task_id]
            if task['status'] != 'uploaded':
                return jsonify({'error': '任务状态无效'}), 400
            
            # 更新任务状态
            task['status'] = 'processing'
            task['progress'] = 0
            task['message'] = '开始处理...'
            
            # 在后台线程中执行转换
            def convert_in_background():
                try:
                    # 创建转换器
                    converter = ClefConverter(
                        high_quality=request.json.get('high_quality', False),
                        verbose=app.debug
                    )
                    
                    # 设置进度回调
                    def progress_callback(progress_data):
                        task['progress'] = progress_data['percentage']
                        task['message'] = progress_data['operation']
                    
                    # 执行转换
                    input_file = task['input_file']
                    output_dir = Path(input_file).parent / 'output'
                    formats = request.json.get('formats', ['png'])
                    
                    result = converter.convert_single(
                        input_file, output_dir, formats, progress_callback
                    )
                    
                    if result['success']:
                        task['status'] = 'completed'
                        task['progress'] = 100
                        task['message'] = '转换完成'
                        task['output_files'] = result['output_files']
                        task['notes_count'] = result.get('notes_count', 0)
                        task['processing_time'] = result.get('processing_time', 0)
                    else:
                        task['status'] = 'failed'
                        task['error'] = result.get('error', '转换失败')
                        task['message'] = f"转换失败: {task['error']}"
                    
                    # 清理转换器
                    converter.cleanup()
                    
                except Exception as e:
                    logger.error(f"转换任务失败: {e}")
                    task['status'] = 'failed'
                    task['error'] = str(e)
                    task['message'] = f"转换失败: {str(e)}"
            
            # 启动后台线程
            thread = threading.Thread(target=convert_in_background)
            thread.daemon = True
            thread.start()
            
            return jsonify({'message': '转换任务已启动'})
            
        except Exception as e:
            logger.error(f"启动转换任务失败: {e}")
            return jsonify({'error': f'启动失败: {str(e)}'}), 500
    
    @app.route('/status/<task_id>')
    def get_task_status(task_id):
        """
        获取任务状态
        """
        if task_id not in conversion_tasks:
            return jsonify({'error': '任务不存在'}), 404
        
        task = conversion_tasks[task_id]
        
        # 清理敏感信息
        safe_task = {
            'status': task['status'],
            'progress': task['progress'],
            'message': task['message'],
            'error': task.get('error'),
            'notes_count': task.get('notes_count'),
            'processing_time': task.get('processing_time'),
            'output_files': list(task.get('output_files', {}).keys())
        }
        
        return jsonify(safe_task)
    
    @app.route('/download/<task_id>/<format>')
    def download_file(task_id, format):
        """
        下载转换结果文件
        """
        try:
            if task_id not in conversion_tasks:
                return jsonify({'error': '任务不存在'}), 404
            
            task = conversion_tasks[task_id]
            if task['status'] != 'completed':
                return jsonify({'error': '任务未完成'}), 400
            
            output_files = task.get('output_files', {})
            if format not in output_files:
                return jsonify({'error': f'格式 {format} 不存在'}), 404
            
            file_path = output_files[format]
            if not os.path.exists(file_path):
                return jsonify({'error': '文件不存在'}), 404
            
            # 生成下载文件名
            original_name = Path(task['input_file']).stem
            download_name = f"{original_name}_converted.{format}"
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=download_name
            )
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            return jsonify({'error': f'下载失败: {str(e)}'}), 500
    
    @app.route('/cleanup/<task_id>', methods=['DELETE'])
    def cleanup_task(task_id):
        """
        清理任务文件
        """
        try:
            if task_id not in conversion_tasks:
                return jsonify({'error': '任务不存在'}), 404
            
            task = conversion_tasks[task_id]
            
            # 清理文件
            input_file = task.get('input_file')
            if input_file:
                task_dir = Path(input_file).parent
                if task_dir.exists():
                    cleanup_temp_files(task_dir)
            
            # 删除任务记录
            del conversion_tasks[task_id]
            
            return jsonify({'message': '任务清理完成'})
            
        except Exception as e:
            logger.error(f"任务清理失败: {e}")
            return jsonify({'error': f'清理失败: {str(e)}'}), 500
    
    @app.errorhandler(413)
    def too_large(e):
        """文件过大错误处理"""
        return jsonify({'error': '文件过大，最大支持100MB'}), 413
    
    @app.errorhandler(500)
    def internal_error(e):
        """内部错误处理"""
        logger.error(f"内部错误: {e}")
        return jsonify({'error': '服务器内部错误'}), 500
    
    # 定期清理过期任务
    def cleanup_expired_tasks():
        """清理过期任务"""
        current_time = time.time()
        expired_tasks = []
        
        for task_id, task in conversion_tasks.items():
            # 清理超过1小时的任务
            if current_time - task['created_at'] > 3600:
                expired_tasks.append(task_id)
        
        for task_id in expired_tasks:
            try:
                cleanup_task(task_id)
                logger.info(f"清理过期任务: {task_id}")
            except Exception as e:
                logger.warning(f"清理过期任务失败: {task_id}, {e}")
    
    # 启动定期清理任务
    def start_cleanup_scheduler():
        """启动清理调度器"""
        def scheduler():
            while True:
                time.sleep(3600)  # 每小时执行一次
                cleanup_expired_tasks()
        
        thread = threading.Thread(target=scheduler)
        thread.daemon = True
        thread.start()
    
    start_cleanup_scheduler()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
