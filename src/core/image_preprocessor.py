"""
图像预处理模块
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """图像预处理器"""
    
    def __init__(self, target_dpi: int = 300):
        """
        初始化图像预处理器
        
        Args:
            target_dpi: 目标DPI，用于图像缩放
        """
        self.target_dpi = target_dpi
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'}
    
    def validate_image(self, image_path: str) -> bool:
        """
        验证图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            bool: 是否为有效图像
        """
        try:
            # 检查文件扩展名
            import os
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in self.supported_formats:
                logger.error(f"不支持的图像格式: {ext}")
                return False
            
            # 尝试打开图像
            with Image.open(image_path) as img:
                # 检查图像尺寸
                width, height = img.size
                if width < 100 or height < 100:
                    logger.error(f"图像尺寸过小: {width}x{height}")
                    return False
                
                if width > 65536 or height > 65536:
                    logger.error(f"图像尺寸过大: {width}x{height}")
                    return False
                
                logger.info(f"图像验证通过: {width}x{height}, 模式: {img.mode}")
                return True
                
        except Exception as e:
            logger.error(f"图像验证失败: {str(e)}")
            return False
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        加载图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            np.ndarray: 图像数组
        """
        try:
            # 使用PIL加载图像
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 转换为numpy数组
                image_array = np.array(img)
                
                # 转换为OpenCV格式 (BGR)
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                
                logger.info(f"成功加载图像: {image_bgr.shape}")
                return image_bgr
                
        except Exception as e:
            logger.error(f"加载图像失败: {str(e)}")
            raise
    
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        图像增强
        
        Args:
            image: 输入图像
            
        Returns:
            np.ndarray: 增强后的图像
        """
        try:
            # 转换为PIL图像进行增强
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # 对比度增强
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.2)
            
            # 锐度增强
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.1)
            
            # 转换回OpenCV格式
            enhanced = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # 去噪
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            logger.info("图像增强完成")
            return enhanced
            
        except Exception as e:
            logger.error(f"图像增强失败: {str(e)}")
            return image
    
    def auto_rotate(self, image: np.ndarray) -> np.ndarray:
        """
        自动旋转图像
        
        Args:
            image: 输入图像
            
        Returns:
            np.ndarray: 旋转后的图像
        """
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 边缘检测
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # 霍夫直线检测
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # 计算主要直线的角度
                angles = []
                for rho, theta in lines[:10]:  # 只考虑前10条直线
                    angle = theta * 180 / np.pi
                    # 将角度标准化到-45到45度之间
                    if angle > 45:
                        angle -= 90
                    elif angle < -45:
                        angle += 90
                    angles.append(angle)
                
                # 计算平均角度
                if angles:
                    avg_angle = np.median(angles)
                    
                    # 如果角度偏差超过阈值，进行旋转
                    if abs(avg_angle) > 1.0:
                        height, width = image.shape[:2]
                        center = (width // 2, height // 2)
                        
                        # 创建旋转矩阵
                        rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                        
                        # 执行旋转
                        rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                               flags=cv2.INTER_CUBIC, 
                                               borderMode=cv2.BORDER_CONSTANT,
                                               borderValue=(255, 255, 255))
                        
                        logger.info(f"图像旋转: {avg_angle:.2f}度")
                        return rotated
            
            logger.info("无需旋转")
            return image
            
        except Exception as e:
            logger.error(f"自动旋转失败: {str(e)}")
            return image
    
    def binarize(self, image: np.ndarray) -> np.ndarray:
        """
        图像二值化
        
        Args:
            image: 输入图像
            
        Returns:
            np.ndarray: 二值化图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 自适应阈值二值化
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 形态学操作去除噪声
            kernel = np.ones((2, 2), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            logger.info("图像二值化完成")
            return binary
            
        except Exception as e:
            logger.error(f"图像二值化失败: {str(e)}")
            raise
    
    def crop_staff_area(self, image: np.ndarray) -> np.ndarray:
        """
        裁剪五线谱区域
        
        Args:
            image: 输入图像
            
        Returns:
            np.ndarray: 裁剪后的图像
        """
        try:
            # 转换为灰度图
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 水平投影，寻找五线谱区域
            horizontal_projection = np.sum(gray < 128, axis=1)
            
            # 找到投影值较大的区域（五线谱区域）
            threshold = np.max(horizontal_projection) * 0.1
            staff_rows = np.where(horizontal_projection > threshold)[0]
            
            if len(staff_rows) > 0:
                # 扩展边界
                top = max(0, staff_rows[0] - 20)
                bottom = min(gray.shape[0], staff_rows[-1] + 20)
                
                # 垂直投影，寻找左右边界
                vertical_projection = np.sum(gray[top:bottom] < 128, axis=0)
                staff_cols = np.where(vertical_projection > threshold)[0]
                
                if len(staff_cols) > 0:
                    left = max(0, staff_cols[0] - 20)
                    right = min(gray.shape[1], staff_cols[-1] + 20)
                    
                    # 裁剪图像
                    cropped = image[top:bottom, left:right]
                    
                    logger.info(f"裁剪五线谱区域: ({left},{top}) to ({right},{bottom})")
                    return cropped
            
            logger.info("未找到明显的五线谱区域，返回原图")
            return image
            
        except Exception as e:
            logger.error(f"裁剪五线谱区域失败: {str(e)}")
            return image
    
    def resize_image(self, image: np.ndarray, target_width: Optional[int] = None) -> np.ndarray:
        """
        调整图像尺寸
        
        Args:
            image: 输入图像
            target_width: 目标宽度，如果为None则根据DPI计算
            
        Returns:
            np.ndarray: 调整后的图像
        """
        try:
            height, width = image.shape[:2]
            
            if target_width is None:
                # 根据目标DPI计算目标宽度
                target_width = min(2048, width)  # 限制最大宽度
            
            if width != target_width:
                # 计算目标高度，保持宽高比
                target_height = int(height * target_width / width)
                
                # 调整尺寸
                resized = cv2.resize(image, (target_width, target_height), 
                                   interpolation=cv2.INTER_CUBIC)
                
                logger.info(f"图像尺寸调整: {width}x{height} -> {target_width}x{target_height}")
                return resized
            
            return image
            
        except Exception as e:
            logger.error(f"调整图像尺寸失败: {str(e)}")
            return image
    
    def preprocess(self, image_path: str, high_quality: bool = False) -> np.ndarray:
        """
        完整的图像预处理流程
        
        Args:
            image_path: 图像文件路径
            high_quality: 是否使用高质量模式
            
        Returns:
            np.ndarray: 预处理后的图像
        """
        logger.info(f"开始预处理图像: {image_path}")
        
        # 验证图像
        if not self.validate_image(image_path):
            raise ValueError(f"无效的图像文件: {image_path}")
        
        # 加载图像
        image = self.load_image(image_path)
        
        # 调整尺寸
        if high_quality:
            image = self.resize_image(image, target_width=2048)
        else:
            image = self.resize_image(image, target_width=1024)
        
        # 图像增强
        image = self.enhance_image(image)
        
        # 自动旋转
        image = self.auto_rotate(image)
        
        # 裁剪五线谱区域
        image = self.crop_staff_area(image)
        
        logger.info("图像预处理完成")
        return image
