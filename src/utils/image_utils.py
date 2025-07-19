"""
图像处理工具模块
提供图像格式转换、尺寸调整、质量优化等功能
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from pathlib import Path
from typing import Tuple, Optional, Union, List
import cv2
from .logger import get_logger

logger = get_logger(__name__)


def load_image(image_path: Union[str, Path]) -> Optional[Image.Image]:
    """
    加载图像文件
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        PIL Image对象，加载失败返回None
    """
    try:
        image = Image.open(image_path)
        logger.debug(f"成功加载图像: {image_path}, 尺寸: {image.size}, 模式: {image.mode}")
        return image
    except Exception as e:
        logger.error(f"加载图像失败: {image_path}, 错误: {e}")
        return None


def save_image(
    image: Image.Image,
    output_path: Union[str, Path],
    quality: int = 95,
    optimize: bool = True
) -> bool:
    """
    保存图像文件
    
    Args:
        image: PIL Image对象
        output_path: 输出路径
        quality: JPEG质量 (1-100)
        optimize: 是否优化
        
    Returns:
        是否保存成功
    """
    try:
        output_path = Path(output_path)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据文件扩展名设置保存参数
        save_kwargs = {}
        if output_path.suffix.lower() in ['.jpg', '.jpeg']:
            # JPEG格式需要RGB模式
            if image.mode in ['RGBA', 'LA', 'P']:
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            save_kwargs.update({'quality': quality, 'optimize': optimize})
        elif output_path.suffix.lower() == '.png':
            save_kwargs.update({'optimize': optimize})
        
        image.save(output_path, **save_kwargs)
        logger.info(f"图像保存成功: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"保存图像失败: {output_path}, 错误: {e}")
        return False


def resize_image(
    image: Image.Image,
    target_size: Tuple[int, int],
    maintain_aspect: bool = True,
    resample: int = Image.Resampling.LANCZOS
) -> Image.Image:
    """
    调整图像尺寸
    
    Args:
        image: PIL Image对象
        target_size: 目标尺寸 (width, height)
        maintain_aspect: 是否保持宽高比
        resample: 重采样方法
        
    Returns:
        调整后的图像
    """
    try:
        if maintain_aspect:
            # 计算保持宽高比的尺寸
            image.thumbnail(target_size, resample)
            logger.debug(f"图像尺寸调整: {image.size} -> {target_size} (保持宽高比)")
        else:
            # 直接调整到目标尺寸
            image = image.resize(target_size, resample)
            logger.debug(f"图像尺寸调整: {image.size} -> {target_size}")
        
        return image
        
    except Exception as e:
        logger.error(f"调整图像尺寸失败: {e}")
        return image


def enhance_image(
    image: Image.Image,
    brightness: float = 1.0,
    contrast: float = 1.0,
    sharpness: float = 1.0,
    color: float = 1.0
) -> Image.Image:
    """
    增强图像质量
    
    Args:
        image: PIL Image对象
        brightness: 亮度调整 (0.0-2.0, 1.0为原始)
        contrast: 对比度调整 (0.0-2.0, 1.0为原始)
        sharpness: 锐度调整 (0.0-2.0, 1.0为原始)
        color: 色彩饱和度调整 (0.0-2.0, 1.0为原始)
        
    Returns:
        增强后的图像
    """
    try:
        enhanced = image.copy()
        
        # 亮度调整
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(brightness)
        
        # 对比度调整
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(contrast)
        
        # 锐度调整
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(sharpness)
        
        # 色彩饱和度调整
        if color != 1.0 and enhanced.mode in ['RGB', 'RGBA']:
            enhancer = ImageEnhance.Color(enhanced)
            enhanced = enhancer.enhance(color)
        
        logger.debug(f"图像增强完成: 亮度={brightness}, 对比度={contrast}, 锐度={sharpness}, 色彩={color}")
        return enhanced
        
    except Exception as e:
        logger.error(f"图像增强失败: {e}")
        return image


def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """
    转换为灰度图像
    
    Args:
        image: PIL Image对象
        
    Returns:
        灰度图像
    """
    try:
        if image.mode != 'L':
            grayscale = image.convert('L')
            logger.debug("图像转换为灰度")
            return grayscale
        return image
    except Exception as e:
        logger.error(f"转换灰度图像失败: {e}")
        return image


def binarize_image(
    image: Image.Image,
    threshold: int = 128,
    method: str = 'simple'
) -> Image.Image:
    """
    二值化图像
    
    Args:
        image: PIL Image对象
        threshold: 阈值 (0-255)
        method: 二值化方法 ('simple', 'otsu', 'adaptive')
        
    Returns:
        二值化图像
    """
    try:
        # 先转换为灰度图像
        if image.mode != 'L':
            image = convert_to_grayscale(image)
        
        # 转换为numpy数组
        img_array = np.array(image)
        
        if method == 'simple':
            # 简单阈值二值化
            binary_array = (img_array > threshold).astype(np.uint8) * 255
        elif method == 'otsu':
            # Otsu自动阈值
            _, binary_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            # 自适应阈值
            binary_array = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
        else:
            logger.warning(f"未知的二值化方法: {method}, 使用简单阈值")
            binary_array = (img_array > threshold).astype(np.uint8) * 255
        
        # 转换回PIL图像
        binary_image = Image.fromarray(binary_array, mode='L')
        logger.debug(f"图像二值化完成: 方法={method}, 阈值={threshold}")
        return binary_image
        
    except Exception as e:
        logger.error(f"图像二值化失败: {e}")
        return image


def remove_noise(image: Image.Image, method: str = 'median') -> Image.Image:
    """
    去除图像噪声
    
    Args:
        image: PIL Image对象
        method: 去噪方法 ('median', 'gaussian', 'bilateral')
        
    Returns:
        去噪后的图像
    """
    try:
        if method == 'median':
            # 中值滤波
            filtered = image.filter(ImageFilter.MedianFilter(size=3))
        elif method == 'gaussian':
            # 高斯滤波
            filtered = image.filter(ImageFilter.GaussianBlur(radius=1))
        elif method == 'bilateral':
            # 双边滤波（需要OpenCV）
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                filtered_array = cv2.bilateralFilter(img_array, 9, 75, 75)
            else:
                filtered_array = cv2.bilateralFilter(img_array, 9, 75, 75)
            filtered = Image.fromarray(filtered_array)
        else:
            logger.warning(f"未知的去噪方法: {method}")
            return image
        
        logger.debug(f"图像去噪完成: 方法={method}")
        return filtered
        
    except Exception as e:
        logger.error(f"图像去噪失败: {e}")
        return image


def auto_crop(image: Image.Image, border_color: Tuple[int, ...] = (255, 255, 255)) -> Image.Image:
    """
    自动裁剪图像边缘
    
    Args:
        image: PIL Image对象
        border_color: 边缘颜色
        
    Returns:
        裁剪后的图像
    """
    try:
        # 使用PIL的自动裁剪功能
        cropped = ImageOps.crop(image, border=0)
        
        # 如果没有变化，尝试手动检测边缘
        if cropped.size == image.size:
            # 转换为numpy数组进行边缘检测
            img_array = np.array(image)
            
            # 查找非边缘颜色的区域
            if len(img_array.shape) == 3:
                # 彩色图像
                mask = np.any(img_array != border_color, axis=2)
            else:
                # 灰度图像
                mask = img_array != border_color[0]
            
            # 找到边界
            coords = np.argwhere(mask)
            if len(coords) > 0:
                y0, x0 = coords.min(axis=0)
                y1, x1 = coords.max(axis=0) + 1
                cropped = image.crop((x0, y0, x1, y1))
        
        logger.debug(f"自动裁剪完成: {image.size} -> {cropped.size}")
        return cropped
        
    except Exception as e:
        logger.error(f"自动裁剪失败: {e}")
        return image


def rotate_image(image: Image.Image, angle: float, expand: bool = True) -> Image.Image:
    """
    旋转图像
    
    Args:
        image: PIL Image对象
        angle: 旋转角度（度）
        expand: 是否扩展画布以容纳旋转后的图像
        
    Returns:
        旋转后的图像
    """
    try:
        rotated = image.rotate(angle, expand=expand, fillcolor='white')
        logger.debug(f"图像旋转完成: 角度={angle}度")
        return rotated
    except Exception as e:
        logger.error(f"图像旋转失败: {e}")
        return image


def get_image_info(image: Image.Image) -> dict:
    """
    获取图像信息
    
    Args:
        image: PIL Image对象
        
    Returns:
        图像信息字典
    """
    try:
        return {
            'size': image.size,
            'width': image.width,
            'height': image.height,
            'mode': image.mode,
            'format': image.format,
            'has_transparency': image.mode in ['RGBA', 'LA', 'P'] and 'transparency' in image.info
        }
    except Exception as e:
        logger.error(f"获取图像信息失败: {e}")
        return {}
