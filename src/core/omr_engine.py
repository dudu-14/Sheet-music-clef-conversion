"""
OMR光学音乐识别引擎
"""

import numpy as np
import cv2
from typing import List, Optional, Tuple
import logging
import time
from pathlib import Path

from ..models.note import Note
from ..models.score_metadata import ScoreMetadata
from ..models.recognition_result import RecognitionResult
from ..models.measure import Measure
from .image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)


class OMREngine:
    """光学音乐识别引擎"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化OMR引擎
        
        Args:
            model_path: 模型文件路径，如果为None则使用默认模型
        """
        self.model_path = model_path
        self.preprocessor = ImagePreprocessor()
        self.is_initialized = False
        
        # 尝试导入oemer库
        try:
            import oemer
            self.oemer = oemer
            self.has_oemer = True
            logger.info("成功导入oemer库")
        except ImportError:
            self.oemer = None
            self.has_oemer = False
            logger.warning("未找到oemer库，将使用基础识别方法")
    
    def initialize(self) -> bool:
        """
        初始化OMR引擎
        
        Returns:
            bool: 是否初始化成功
        """
        try:
            if self.has_oemer:
                # 初始化oemer模型
                logger.info("正在初始化oemer模型...")
                # 这里可以添加模型加载代码
                self.is_initialized = True
                logger.info("OMR引擎初始化成功")
            else:
                # 使用基础方法
                self.is_initialized = True
                logger.info("使用基础识别方法初始化成功")
            
            return True
            
        except Exception as e:
            logger.error(f"OMR引擎初始化失败: {str(e)}")
            return False
    
    def detect_clef(self, image: np.ndarray) -> str:
        """
        检测谱号类型
        
        Args:
            image: 输入图像
            
        Returns:
            str: 谱号类型 ('treble', 'alto', 'bass')
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 简单的谱号检测逻辑
            # 这里使用基础的模板匹配方法
            height, width = gray.shape
            
            # 在图像左侧寻找谱号
            left_region = gray[:, :width//4]
            
            # 使用轮廓检测寻找可能的谱号
            _, binary = cv2.threshold(left_region, 127, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 分析轮廓特征来判断谱号类型
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # 过滤小轮廓
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w
                    
                    # 基于轮廓特征的简单判断
                    if aspect_ratio > 2.0:  # 高瘦的形状，可能是高音谱号
                        logger.info("检测到高音谱号")
                        return "treble"
                    elif 1.0 < aspect_ratio < 2.0:  # 中等比例，可能是中音谱号
                        logger.info("检测到中音谱号")
                        return "alto"
                    elif aspect_ratio < 1.0:  # 宽矮的形状，可能是低音谱号
                        logger.info("检测到低音谱号")
                        return "bass"
            
            # 默认返回中音谱号（根据需求）
            logger.info("未明确检测到谱号，默认为中音谱号")
            return "alto"
            
        except Exception as e:
            logger.error(f"谱号检测失败: {str(e)}")
            return "alto"
    
    def detect_staff_lines(self, image: np.ndarray) -> List[int]:
        """
        检测五线谱线条
        
        Args:
            image: 输入图像
            
        Returns:
            List[int]: 五线谱线条的y坐标
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 水平投影
            horizontal_projection = np.sum(gray < 128, axis=1)
            
            # 寻找峰值（五线谱线条）
            height = len(horizontal_projection)
            staff_lines = []
            
            # 简单的峰值检测
            threshold = np.max(horizontal_projection) * 0.3
            for i in range(1, height - 1):
                if (horizontal_projection[i] > threshold and 
                    horizontal_projection[i] > horizontal_projection[i-1] and 
                    horizontal_projection[i] > horizontal_projection[i+1]):
                    staff_lines.append(i)
            
            # 过滤相邻的线条
            filtered_lines = []
            for line in staff_lines:
                if not filtered_lines or line - filtered_lines[-1] > 10:
                    filtered_lines.append(line)
            
            logger.info(f"检测到 {len(filtered_lines)} 条五线谱线")
            return filtered_lines
            
        except Exception as e:
            logger.error(f"五线谱线检测失败: {str(e)}")
            return []
    
    def detect_notes_basic(self, image: np.ndarray, staff_lines: List[int]) -> List[Note]:
        """
        基础音符检测方法
        
        Args:
            image: 输入图像
            staff_lines: 五线谱线条位置
            
        Returns:
            List[Note]: 检测到的音符列表
        """
        notes = []
        
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 二值化
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
            
            # 寻找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 分析轮廓，寻找音符
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if 50 < area < 1000:  # 过滤大小不合适的轮廓
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算音符在五线谱上的位置
                    center_y = y + h // 2
                    staff_position = self._calculate_staff_position(center_y, staff_lines)
                    
                    # 根据位置计算音高（中音谱号）
                    pitch = self._staff_position_to_pitch(staff_position, "alto")
                    
                    # 估算时间位置（基于x坐标）
                    start_time = x / image.shape[1] * 4.0  # 假设4秒的乐曲
                    
                    # 创建音符对象
                    note = Note(
                        pitch=pitch,
                        start_time=start_time,
                        duration=0.5,  # 默认时长
                        staff_position=staff_position
                    )
                    
                    notes.append(note)
            
            logger.info(f"基础方法检测到 {len(notes)} 个音符")
            return notes
            
        except Exception as e:
            logger.error(f"基础音符检测失败: {str(e)}")
            return []
    
    def _calculate_staff_position(self, y: int, staff_lines: List[int]) -> int:
        """
        计算音符在五线谱上的位置
        
        Args:
            y: 音符的y坐标
            staff_lines: 五线谱线条位置
            
        Returns:
            int: 五线谱位置（0为中间线）
        """
        if not staff_lines or len(staff_lines) < 5:
            return 0
        
        # 找到最接近的五线谱线
        distances = [abs(y - line) for line in staff_lines]
        closest_line_idx = distances.index(min(distances))
        
        # 计算相对位置
        staff_position = closest_line_idx - 2  # 中间线为0
        
        # 如果不在线上，判断是在线间
        if distances[closest_line_idx] > 5:  # 不在线上
            if y < staff_lines[closest_line_idx]:
                staff_position += 0.5  # 线上方的间
            else:
                staff_position -= 0.5  # 线下方的间
        
        return int(staff_position * 2)  # 转换为整数位置
    
    def _staff_position_to_pitch(self, position: int, clef: str) -> int:
        """
        将五线谱位置转换为MIDI音高
        
        Args:
            position: 五线谱位置
            clef: 谱号类型
            
        Returns:
            int: MIDI音高值
        """
        # 中音谱号的C4在第三线（position=0）
        if clef == "alto":
            # C4 = 60, 中音谱号第三线是C4
            base_pitch = 60  # C4
            return max(21, min(108, base_pitch + position))
        elif clef == "treble":
            # 高音谱号的G4在第二线
            base_pitch = 67  # G4
            return max(21, min(108, base_pitch + position))
        elif clef == "bass":
            # 低音谱号的F3在第四线
            base_pitch = 53  # F3
            return max(21, min(108, base_pitch + position))
        else:
            return 60  # 默认C4
    
    def recognize_with_oemer(self, image_path: str) -> RecognitionResult:
        """
        使用oemer库进行识别
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            RecognitionResult: 识别结果
        """
        if not self.has_oemer:
            raise RuntimeError("oemer库未安装")
        
        try:
            start_time = time.time()
            
            # 使用oemer进行识别
            # 注意：这里需要根据实际的oemer API进行调整
            logger.info("使用oemer进行识别...")
            
            # 创建结果对象
            result = RecognitionResult()
            result.image_path = image_path
            result.processing_time = time.time() - start_time
            result.confidence = 0.8  # 假设置信度
            
            # 这里应该调用实际的oemer API
            # 由于oemer的具体API可能变化，这里提供一个框架
            
            result.add_warning("oemer识别功能需要进一步实现")
            
            return result
            
        except Exception as e:
            logger.error(f"oemer识别失败: {str(e)}")
            raise
    
    def recognize_basic(self, image_path: str) -> RecognitionResult:
        """
        使用基础方法进行识别
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            RecognitionResult: 识别结果
        """
        try:
            start_time = time.time()
            
            # 预处理图像
            image = self.preprocessor.preprocess(image_path)
            
            # 检测谱号
            clef_type = self.detect_clef(image)
            
            # 检测五线谱线条
            staff_lines = self.detect_staff_lines(image)
            
            # 检测音符
            notes = self.detect_notes_basic(image, staff_lines)
            
            # 创建元数据
            metadata = ScoreMetadata(clef_type=clef_type)
            
            # 创建结果对象
            result = RecognitionResult(
                notes=notes,
                metadata=metadata,
                confidence=0.6,  # 基础方法置信度较低
                processing_time=time.time() - start_time,
                image_path=image_path
            )
            
            # 验证结果
            result.validate()
            
            logger.info(f"基础识别完成，检测到 {len(notes)} 个音符")
            return result
            
        except Exception as e:
            logger.error(f"基础识别失败: {str(e)}")
            raise
    
    def recognize_score(self, image_path: str, use_oemer: bool = True) -> RecognitionResult:
        """
        识别乐谱
        
        Args:
            image_path: 图像文件路径
            use_oemer: 是否使用oemer库
            
        Returns:
            RecognitionResult: 识别结果
        """
        if not self.is_initialized:
            if not self.initialize():
                raise RuntimeError("OMR引擎未初始化")
        
        logger.info(f"开始识别乐谱: {image_path}")
        
        try:
            if use_oemer and self.has_oemer:
                return self.recognize_with_oemer(image_path)
            else:
                return self.recognize_basic(image_path)
                
        except Exception as e:
            logger.error(f"乐谱识别失败: {str(e)}")
            # 创建错误结果
            result = RecognitionResult(
                confidence=0.0,
                processing_time=0.0,
                image_path=image_path
            )
            result.add_error(f"识别失败: {str(e)}")
            return result
