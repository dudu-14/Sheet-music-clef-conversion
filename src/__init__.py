"""
谱号转换器 - 中音谱号到高音谱号转换工具

这个包提供了完整的光学音乐识别和谱号转换功能。
"""

__version__ = "1.0.0"
__author__ = "谱号转换器开发团队"
__email__ = "support@clef-converter.com"

from .core.converter import ClefConverter
from .core.omr_engine import OMREngine
from .core.midi_converter import MIDIConverter
from .core.score_renderer import ScoreRenderer

__all__ = [
    "ClefConverter",
    "OMREngine", 
    "MIDIConverter",
    "ScoreRenderer"
]
