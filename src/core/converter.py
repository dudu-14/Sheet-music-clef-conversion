"""
主转换器模块
整合所有模块，实现完整的谱号转换流程
"""

import os
import time
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Callable
import traceback

from ..models.note import Note
from ..models.score_metadata import ScoreMetadata
from ..models.recognition_result import RecognitionResult
from ..models.measure import Measure

from .image_preprocessor import ImagePreprocessor
from .omr_engine import OMREngine
from .midi_converter import MIDIConverter
from .clef_converter import ClefConverter as ClefConverterModule
from .score_renderer import ScoreRenderer

from ..utils.logger import get_logger, LoggerMixin
from ..utils.file_utils import (
    validate_image_file,
    validate_output_format,
    ensure_directory,
    generate_output_path,
    find_image_files,
    cleanup_temp_files,
)
from ..utils.image_utils import load_image, get_image_info

logger = get_logger(__name__)


class ConversionProgress:
    """转换进度跟踪器"""

    def __init__(self):
        self.total_steps = 0
        self.current_step = 0
        self.current_operation = ""
        self.start_time = None
        self.callbacks: List[Callable] = []

    def set_total_steps(self, total: int):
        """设置总步数"""
        self.total_steps = total
        self.current_step = 0
        self.start_time = time.time()

    def next_step(self, operation: str):
        """进入下一步"""
        self.current_step += 1
        self.current_operation = operation
        self._notify_callbacks()

    def add_callback(self, callback: Callable):
        """添加进度回调函数"""
        self.callbacks.append(callback)

    def _notify_callbacks(self):
        """通知所有回调函数"""
        progress_data = {
            "step": self.current_step,
            "total": self.total_steps,
            "operation": self.current_operation,
            "percentage": (
                (self.current_step / self.total_steps * 100)
                if self.total_steps > 0
                else 0
            ),
            "elapsed_time": time.time() - self.start_time if self.start_time else 0,
        }

        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                logger.warning(f"进度回调函数执行失败: {e}")


class ClefConverter(LoggerMixin):
    """
    主转换器类
    整合所有模块，实现完整的谱号转换流程
    """

    def __init__(
        self,
        high_quality: bool = False,
        verbose: bool = False,
        temp_dir: Optional[str] = None,
    ):
        """
        初始化转换器

        Args:
            high_quality: 是否使用高质量模式
            verbose: 是否启用详细输出
            temp_dir: 临时目录路径
        """
        self.high_quality = high_quality
        self.verbose = verbose
        self.temp_dir = Path(temp_dir) if temp_dir else Path("temp")

        # 确保临时目录存在
        ensure_directory(self.temp_dir)

        # 初始化各个模块
        self.image_preprocessor = ImagePreprocessor()
        self.omr_engine = OMREngine()
        self.midi_converter = MIDIConverter()
        self.clef_converter_module = ClefConverterModule()
        self.score_renderer = ScoreRenderer()

        # 进度跟踪器
        self.progress = ConversionProgress()

        self.logger.info(f"转换器初始化完成 - 高质量模式: {high_quality}")

    def convert_single(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        formats: List[str] = ["png"],
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        转换单个文件

        Args:
            input_path: 输入图片路径
            output_path: 输出路径
            formats: 输出格式列表
            progress_callback: 进度回调函数

        Returns:
            转换结果字典
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            # 添加进度回调
            if progress_callback:
                self.progress.add_callback(progress_callback)

            # 设置总步数
            self.progress.set_total_steps(6)

            self.logger.info(f"开始转换: {input_path} -> {output_path}")

            # 步骤1: 验证输入文件
            self.progress.next_step("验证输入文件")
            if not validate_image_file(input_path):
                raise ValueError(f"无效的输入图片文件: {input_path}")

            # 步骤2: 图像预处理
            self.progress.next_step("图像预处理")
            image = load_image(input_path)
            if image is None:
                raise ValueError(f"无法加载图像: {input_path}")

            preprocessed_image = self.image_preprocessor.preprocess(
                image, high_quality=self.high_quality
            )

            # 步骤3: OMR识别
            self.progress.next_step("音乐识别")
            recognition_result = self.omr_engine.recognize_score(preprocessed_image)

            if not recognition_result.notes:
                raise ValueError("未识别到任何音符")

            # 步骤4: 谱号转换
            self.progress.next_step("谱号转换")
            if recognition_result.metadata.clef_type == "alto":
                converted_result = (
                    self.clef_converter_module.convert_recognition_result(
                        recognition_result, "treble"
                    )
                )
            else:
                self.logger.warning(
                    f"输入不是中音谱号: {recognition_result.metadata.clef_type}"
                )
                converted_result = recognition_result

            # 步骤5: 生成输出
            self.progress.next_step("生成输出文件")
            output_files = {}

            for format_str in formats:
                if not validate_output_format(format_str):
                    self.logger.warning(f"不支持的输出格式: {format_str}")
                    continue

                format_output_path = generate_output_path(
                    input_path,
                    output_path.parent,
                    suffix="converted",
                    extension=f".{format_str}",
                )

                if format_str in ["png", "pdf", "svg"]:
                    # 渲染乐谱图像
                    success = self.score_renderer.render_score_to_file(
                        converted_result, format_output_path, format_str
                    )
                elif format_str in ["midi", "mid"]:
                    # 生成MIDI文件
                    success = self.midi_converter.notes_to_midi(
                        converted_result.notes,
                        format_output_path,
                        metadata=converted_result.metadata,
                    )
                else:
                    success = False

                if success:
                    output_files[format_str] = str(format_output_path)
                    self.logger.info(f"生成输出文件: {format_output_path}")
                else:
                    self.logger.error(f"生成{format_str}文件失败")

            # 步骤6: 完成
            self.progress.next_step("转换完成")

            result = {
                "success": True,
                "input_file": str(input_path),
                "output_files": output_files,
                "recognition_result": recognition_result,
                "converted_result": converted_result,
                "processing_time": time.time() - self.progress.start_time,
                "notes_count": len(converted_result.notes),
            }

            self.logger.info(f"转换完成: {len(output_files)}个输出文件")
            return result

        except Exception as e:
            self.logger.error(f"转换失败: {e}")
            if self.verbose:
                self.logger.error(traceback.format_exc())

            return {
                "success": False,
                "error": str(e),
                "input_file": str(input_path),
                "output_files": {},
                "processing_time": (
                    time.time() - self.progress.start_time
                    if self.progress.start_time
                    else 0
                ),
            }

    def convert_batch(
        self,
        input_pattern: str,
        output_dir: Union[str, Path],
        formats: List[str] = ["png"],
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        批量转换文件

        Args:
            input_pattern: 输入文件模式（支持通配符）
            output_dir: 输出目录
            formats: 输出格式列表
            progress_callback: 进度回调函数

        Returns:
            批量转换结果字典
        """
        try:
            output_dir = Path(output_dir)
            ensure_directory(output_dir)

            # 查找匹配的图像文件
            if "*" in input_pattern or "?" in input_pattern:
                # 通配符模式
                pattern_path = Path(input_pattern)
                input_files = list(pattern_path.parent.glob(pattern_path.name))
                input_files = [f for f in input_files if validate_image_file(f)]
            else:
                # 目录模式
                input_dir = Path(input_pattern)
                if input_dir.is_dir():
                    input_files = list(find_image_files(input_dir))
                else:
                    input_files = [input_dir] if validate_image_file(input_dir) else []

            if not input_files:
                raise ValueError(f"未找到有效的图像文件: {input_pattern}")

            self.logger.info(f"开始批量转换: {len(input_files)}个文件")

            # 批量转换
            results = []
            successful_count = 0
            failed_count = 0

            for i, input_file in enumerate(input_files):
                self.logger.info(f"处理文件 {i+1}/{len(input_files)}: {input_file}")

                # 为每个文件创建单独的进度回调
                def file_progress_callback(progress_data):
                    # 计算总体进度
                    file_progress = progress_data["percentage"] / 100
                    total_progress = (i + file_progress) / len(input_files) * 100

                    overall_data = {
                        "file_index": i + 1,
                        "total_files": len(input_files),
                        "current_file": str(input_file),
                        "file_progress": progress_data["percentage"],
                        "total_progress": total_progress,
                        "operation": progress_data["operation"],
                    }

                    if progress_callback:
                        progress_callback(overall_data)

                # 转换单个文件
                result = self.convert_single(
                    input_file, output_dir, formats, file_progress_callback
                )

                results.append(result)

                if result["success"]:
                    successful_count += 1
                else:
                    failed_count += 1
                    self.logger.error(f"文件转换失败: {input_file}")

            # 汇总结果
            total_processing_time = sum(r.get("processing_time", 0) for r in results)
            total_notes = sum(r.get("notes_count", 0) for r in results if r["success"])

            batch_result = {
                "success": successful_count > 0,
                "total_files": len(input_files),
                "successful_count": successful_count,
                "failed_count": failed_count,
                "results": results,
                "total_processing_time": total_processing_time,
                "total_notes": total_notes,
                "output_directory": str(output_dir),
            }

            self.logger.info(
                f"批量转换完成: {successful_count}成功, {failed_count}失败, "
                f"总计{total_notes}个音符"
            )

            return batch_result

        except Exception as e:
            self.logger.error(f"批量转换失败: {e}")
            if self.verbose:
                self.logger.error(traceback.format_exc())

            return {
                "success": False,
                "error": str(e),
                "total_files": 0,
                "successful_count": 0,
                "failed_count": 0,
                "results": [],
                "total_processing_time": 0,
                "total_notes": 0,
            }

    def cleanup(self):
        """清理临时文件"""
        try:
            cleanup_temp_files(self.temp_dir)
            self.logger.info("临时文件清理完成")
        except Exception as e:
            self.logger.warning(f"清理临时文件失败: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()
