"""
Web界面模块 - 提供Web用户界面
"""

from .app import create_app
from .routes import main_bp

__all__ = [
    "create_app",
    "main_bp"
]
