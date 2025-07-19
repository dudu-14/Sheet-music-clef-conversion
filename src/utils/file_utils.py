"""
文件操作工具模块
提供文件验证、路径处理、批量文件操作等功能
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Union, Generator, Tuple
import mimetypes
import hashlib
from .logger import get_logger

logger = get_logger(__name__)


# 支持的图像格式
SUPPORTED_IMAGE_FORMATS = {
    '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif'
}

# 支持的输出格式
SUPPORTED_OUTPUT_FORMATS = {
    '.png', '.pdf', '.midi', '.mid', '.svg'
}


def validate_image_file(file_path: Union[str, Path]) -> bool:
    """
    验证图像文件是否有效
    
    Args:
        file_path: 图像文件路径
        
    Returns:
        是否为有效的图像文件
    """
    try:
        path = Path(file_path)
        
        # 检查文件是否存在
        if not path.exists():
            logger.error(f"文件不存在: {path}")
            return False
        
        # 检查是否为文件
        if not path.is_file():
            logger.error(f"不是文件: {path}")
            return False
        
        # 检查文件扩展名
        if path.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            logger.error(f"不支持的图像格式: {path.suffix}")
            return False
        
        # 检查文件大小
        file_size = path.stat().st_size
        if file_size == 0:
            logger.error(f"文件为空: {path}")
            return False
        
        # 检查MIME类型
        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type and not mime_type.startswith('image/'):
            logger.error(f"MIME类型不是图像: {mime_type}")
            return False
        
        logger.debug(f"图像文件验证通过: {path}")
        return True
        
    except Exception as e:
        logger.error(f"验证图像文件时出错: {e}")
        return False


def validate_output_format(format_str: str) -> bool:
    """
    验证输出格式是否支持
    
    Args:
        format_str: 输出格式字符串
        
    Returns:
        是否为支持的输出格式
    """
    if not format_str.startswith('.'):
        format_str = '.' + format_str
    
    return format_str.lower() in SUPPORTED_OUTPUT_FORMATS


def ensure_directory(dir_path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        目录路径对象
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"确保目录存在: {path}")
    return path


def get_safe_filename(filename: str) -> str:
    """
    获取安全的文件名，移除或替换不安全字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    # 移除或替换不安全字符
    unsafe_chars = '<>:"/\\|?*'
    safe_filename = filename
    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # 移除前后空格和点
    safe_filename = safe_filename.strip(' .')
    
    # 确保文件名不为空
    if not safe_filename:
        safe_filename = 'untitled'
    
    return safe_filename


def generate_output_path(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    suffix: str = '',
    extension: str = '.png'
) -> Path:
    """
    生成输出文件路径
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        suffix: 文件名后缀
        extension: 文件扩展名
        
    Returns:
        输出文件路径
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    
    # 确保输出目录存在
    ensure_directory(output_dir)
    
    # 生成输出文件名
    base_name = input_path.stem
    if suffix:
        output_filename = f"{base_name}_{suffix}{extension}"
    else:
        output_filename = f"{base_name}{extension}"
    
    # 生成安全的文件名
    safe_filename = get_safe_filename(output_filename)
    
    return output_dir / safe_filename


def find_image_files(
    directory: Union[str, Path],
    recursive: bool = True,
    pattern: Optional[str] = None
) -> Generator[Path, None, None]:
    """
    查找目录中的图像文件
    
    Args:
        directory: 搜索目录
        recursive: 是否递归搜索子目录
        pattern: 文件名模式（glob模式）
        
    Yields:
        图像文件路径
    """
    directory = Path(directory)
    
    if not directory.exists():
        logger.error(f"目录不存在: {directory}")
        return
    
    # 设置搜索模式
    if pattern:
        search_pattern = pattern
    else:
        search_pattern = '*'
    
    # 搜索文件
    if recursive:
        files = directory.rglob(search_pattern)
    else:
        files = directory.glob(search_pattern)
    
    # 过滤图像文件
    for file_path in files:
        if file_path.is_file() and validate_image_file(file_path):
            yield file_path


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5, sha1, sha256)
        
    Returns:
        文件哈希值
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def copy_file_with_backup(
    src: Union[str, Path],
    dst: Union[str, Path],
    backup_suffix: str = '.bak'
) -> bool:
    """
    复制文件，如果目标文件存在则创建备份
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        backup_suffix: 备份文件后缀
        
    Returns:
        是否复制成功
    """
    try:
        src = Path(src)
        dst = Path(dst)
        
        # 确保目标目录存在
        ensure_directory(dst.parent)
        
        # 如果目标文件存在，创建备份
        if dst.exists():
            backup_path = dst.with_suffix(dst.suffix + backup_suffix)
            shutil.copy2(dst, backup_path)
            logger.info(f"创建备份文件: {backup_path}")
        
        # 复制文件
        shutil.copy2(src, dst)
        logger.info(f"文件复制成功: {src} -> {dst}")
        return True
        
    except Exception as e:
        logger.error(f"复制文件失败: {e}")
        return False


def create_temp_file(suffix: str = '', prefix: str = 'clef_converter_') -> Tuple[int, str]:
    """
    创建临时文件
    
    Args:
        suffix: 文件后缀
        prefix: 文件前缀
        
    Returns:
        (文件描述符, 文件路径)
    """
    return tempfile.mkstemp(suffix=suffix, prefix=prefix)


def cleanup_temp_files(temp_dir: Optional[Union[str, Path]] = None) -> None:
    """
    清理临时文件
    
    Args:
        temp_dir: 临时目录，None表示使用系统默认临时目录
    """
    try:
        if temp_dir:
            temp_path = Path(temp_dir)
            if temp_path.exists():
                shutil.rmtree(temp_path)
                logger.info(f"清理临时目录: {temp_path}")
        else:
            # 清理系统临时目录中的相关文件
            temp_path = Path(tempfile.gettempdir())
            for file_path in temp_path.glob('clef_converter_*'):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                    logger.debug(f"清理临时文件: {file_path}")
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {file_path}, {e}")
                    
    except Exception as e:
        logger.error(f"清理临时文件时出错: {e}")


def get_file_info(file_path: Union[str, Path]) -> dict:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息字典
    """
    try:
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'path': str(path.absolute()),
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix,
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'is_file': path.is_file(),
            'is_dir': path.is_dir(),
            'exists': path.exists()
        }
    except Exception as e:
        logger.error(f"获取文件信息失败: {e}")
        return {}
