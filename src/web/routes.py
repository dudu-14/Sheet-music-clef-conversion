"""
Web路由模块
定义API端点和路由处理
"""

from flask import Blueprint, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import time
from pathlib import Path

from ..core.converter import ClefConverter
from ..utils.logger import get_logger
from ..utils.file_utils import validate_image_file

logger = get_logger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')
web_bp = Blueprint('web', __name__)


# Web页面路由
@web_bp.route('/')
def index():
    """主页"""
    return render_template('index.html')


@web_bp.route('/help')
def help_page():
    """帮助页面"""
    return render_template('help.html')


@web_bp.route('/about')
def about_page():
    """关于页面"""
    return render_template('about.html')


# API路由
@api_bp.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })


@api_bp.route('/formats')
def get_supported_formats():
    """获取支持的格式"""
    return jsonify({
        'input_formats': ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'gif'],
        'output_formats': ['png', 'pdf', 'midi', 'svg']
    })


@api_bp.route('/validate', methods=['POST'])
def validate_file():
    """
    验证上传的文件
    """
    try:
        if 'file' not in request.files:
            return jsonify({'valid': False, 'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'valid': False, 'error': '文件名为空'}), 400
        
        # 检查文件扩展名
        allowed_extensions = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'gif'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'valid': False, 
                'error': '不支持的文件格式'
            }), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            return jsonify({
                'valid': False,
                'error': f'文件过大，最大支持{max_size // (1024*1024)}MB'
            }), 400
        
        if file_size == 0:
            return jsonify({
                'valid': False,
                'error': '文件为空'
            }), 400
        
        return jsonify({
            'valid': True,
            'filename': file.filename,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        logger.error(f"文件验证失败: {e}")
        return jsonify({
            'valid': False,
            'error': f'验证失败: {str(e)}'
        }), 500


@api_bp.route('/convert/quick', methods=['POST'])
def quick_convert():
    """
    快速转换API（同步处理）
    适用于小文件的快速转换
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 获取参数
        high_quality = request.form.get('high_quality', 'false').lower() == 'true'
        output_formats = request.form.get('formats', 'png').split(',')
        
        # 保存临时文件
        temp_dir = Path('/tmp') / 'clef_converter' / str(uuid.uuid4())
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        input_path = temp_dir / secure_filename(file.filename)
        file.save(str(input_path))
        
        # 验证图像
        if not validate_image_file(input_path):
            return jsonify({'error': '无效的图像文件'}), 400
        
        # 执行转换
        converter = ClefConverter(high_quality=high_quality)
        
        result = converter.convert_single(
            input_path,
            temp_dir / 'output',
            output_formats
        )
        
        if result['success']:
            # 返回结果信息
            response_data = {
                'success': True,
                'notes_count': result.get('notes_count', 0),
                'processing_time': result.get('processing_time', 0),
                'output_files': list(result['output_files'].keys()),
                'download_urls': {}
            }
            
            # 生成下载URL（这里简化处理，实际应该使用临时URL）
            for format_name, file_path in result['output_files'].items():
                response_data['download_urls'][format_name] = f'/api/download/temp/{Path(file_path).name}'
            
            return jsonify(response_data)
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '转换失败')
            }), 500
            
    except Exception as e:
        logger.error(f"快速转换失败: {e}")
        return jsonify({
            'success': False,
            'error': f'转换失败: {str(e)}'
        }), 500


@api_bp.route('/convert/batch', methods=['POST'])
def batch_convert():
    """
    批量转换API
    """
    try:
        # 检查文件
        if 'files' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': '没有有效文件'}), 400
        
        # 获取参数
        high_quality = request.form.get('high_quality', 'false').lower() == 'true'
        output_formats = request.form.get('formats', 'png').split(',')
        
        # 创建批量任务
        task_id = str(uuid.uuid4())
        temp_dir = Path('/tmp') / 'clef_converter' / task_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存所有文件
        input_files = []
        for file in files:
            if file.filename:
                file_path = temp_dir / secure_filename(file.filename)
                file.save(str(file_path))
                if validate_image_file(file_path):
                    input_files.append(file_path)
        
        if not input_files:
            return jsonify({'error': '没有有效的图像文件'}), 400
        
        # 执行批量转换
        converter = ClefConverter(high_quality=high_quality)
        
        # 这里应该使用异步任务队列，简化处理直接执行
        results = []
        for input_file in input_files:
            result = converter.convert_single(
                input_file,
                temp_dir / 'output',
                output_formats
            )
            results.append({
                'filename': input_file.name,
                'success': result['success'],
                'error': result.get('error'),
                'notes_count': result.get('notes_count', 0),
                'output_files': list(result.get('output_files', {}).keys())
            })
        
        # 统计结果
        successful_count = sum(1 for r in results if r['success'])
        failed_count = len(results) - successful_count
        total_notes = sum(r.get('notes_count', 0) for r in results if r['success'])
        
        return jsonify({
            'task_id': task_id,
            'total_files': len(input_files),
            'successful_count': successful_count,
            'failed_count': failed_count,
            'total_notes': total_notes,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"批量转换失败: {e}")
        return jsonify({
            'error': f'批量转换失败: {str(e)}'
        }), 500


@api_bp.route('/stats')
def get_stats():
    """
    获取系统统计信息
    """
    try:
        # 这里应该从数据库或缓存中获取真实统计数据
        # 简化处理返回模拟数据
        stats = {
            'total_conversions': 1234,
            'total_notes_converted': 56789,
            'average_processing_time': 2.5,
            'supported_formats': {
                'input': ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif', 'gif'],
                'output': ['png', 'pdf', 'midi', 'svg']
            },
            'system_info': {
                'version': '1.0.0',
                'uptime': time.time() - 1640995200,  # 假设启动时间
                'memory_usage': '256MB',
                'cpu_usage': '15%'
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'error': '获取统计信息失败'}), 500


@api_bp.errorhandler(400)
def bad_request(error):
    """400错误处理"""
    return jsonify({'error': '请求参数错误'}), 400


@api_bp.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({'error': '资源不存在'}), 404


@api_bp.errorhandler(413)
def payload_too_large(error):
    """413错误处理"""
    return jsonify({'error': '文件过大'}), 413


@api_bp.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"API内部错误: {error}")
    return jsonify({'error': '服务器内部错误'}), 500


def register_routes(app):
    """
    注册所有路由到Flask应用
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)
    
    logger.info("所有路由已注册")
