"""
日志配置模块
提供统一的日志配置和管理功能
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    verbose: bool = False,
    log_file: Optional[str] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        name: 日志器名称，默认为根日志器
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        verbose: 是否启用详细输出
        log_file: 日志文件路径，None表示不写入文件
        max_file_size: 日志文件最大大小（字节）
        backup_count: 备份文件数量
        
    Returns:
        配置好的日志器
    """
    # 如果启用详细输出，设置为DEBUG级别
    if verbose:
        level = "DEBUG"
    
    # 获取日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用RotatingFileHandler支持日志轮转
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        日志器实例
    """
    return logging.getLogger(name)


def set_log_level(logger: logging.Logger, level: str) -> None:
    """
    设置日志器级别
    
    Args:
        logger: 日志器实例
        level: 日志级别
    """
    logger.setLevel(getattr(logging, level.upper()))
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, level.upper()))


class LoggerMixin:
    """
    日志器混入类，为其他类提供日志功能
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志器"""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# 默认日志配置
def configure_default_logging(verbose: bool = False) -> None:
    """
    配置默认的日志设置
    
    Args:
        verbose: 是否启用详细输出
    """
    # 创建logs目录
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 设置根日志器
    setup_logger(
        name=None,  # 根日志器
        level="DEBUG" if verbose else "INFO",
        verbose=verbose,
        log_file=str(logs_dir / "clef_converter.log")
    )
    
    # 设置第三方库的日志级别
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("music21").setLevel(logging.WARNING)


# 便捷函数
def debug(msg: str, *args, **kwargs) -> None:
    """记录DEBUG级别日志"""
    logging.debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """记录INFO级别日志"""
    logging.info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """记录WARNING级别日志"""
    logging.warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """记录ERROR级别日志"""
    logging.error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """记录CRITICAL级别日志"""
    logging.critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    """记录异常信息"""
    logging.exception(msg, *args, **kwargs)
