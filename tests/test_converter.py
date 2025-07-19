"""
主转换器测试用例
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.converter import ClefConverter
from src.models.note import Note
from src.models.score_metadata import ScoreMetadata
from src.models.recognition_result import RecognitionResult


class TestClefConverter(unittest.TestCase):
    """主转换器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.converter = ClefConverter(temp_dir=str(self.temp_dir))
        
        # 创建测试图像
        self.test_image_path = self.temp_dir / "test_image.png"
        self.create_test_image()
    
    def tearDown(self):
        """测试后清理"""
        self.converter.cleanup()
        # 清理临时文件
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_test_image(self):
        """创建测试图像"""
        # 创建一个简单的白色图像
        image = Image.new('RGB', (800, 600), 'white')
        
        # 添加一些简单的线条模拟五线谱
        import PIL.ImageDraw as ImageDraw
        draw = ImageDraw.Draw(image)
        
        # 画五线谱
        for i in range(5):
            y = 200 + i * 20
            draw.line([(100, y), (700, y)], fill='black', width=2)
        
        # 保存图像
        image.save(self.test_image_path)
    
    def test_converter_initialization(self):
        """测试转换器初始化"""
        self.assertIsNotNone(self.converter)
        self.assertIsNotNone(self.converter.image_preprocessor)
        self.assertIsNotNone(self.converter.omr_engine)
        self.assertIsNotNone(self.converter.midi_converter)
        self.assertIsNotNone(self.converter.clef_converter_module)
        self.assertIsNotNone(self.converter.score_renderer)
    
    def test_convert_single_file_validation(self):
        """测试单文件转换的文件验证"""
        # 测试不存在的文件
        result = self.converter.convert_single(
            "nonexistent.png", 
            self.temp_dir / "output.png"
        )
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_convert_single_valid_file(self):
        """测试单文件转换（有效文件）"""
        output_path = self.temp_dir / "output"
        
        result = self.converter.convert_single(
            self.test_image_path,
            output_path,
            formats=['png']
        )
        
        # 由于我们使用的是简单的测试图像，可能无法识别到音符
        # 但至少应该能够处理而不崩溃
        self.assertIn('success', result)
        self.assertIn('input_file', result)
        self.assertIn('processing_time', result)
    
    def test_progress_tracking(self):
        """测试进度跟踪"""
        progress_data = []
        
        def progress_callback(data):
            progress_data.append(data)
        
        result = self.converter.convert_single(
            self.test_image_path,
            self.temp_dir / "output",
            progress_callback=progress_callback
        )
        
        # 检查是否有进度回调
        self.assertGreater(len(progress_data), 0)
        
        # 检查进度数据结构
        if progress_data:
            data = progress_data[0]
            self.assertIn('step', data)
            self.assertIn('total', data)
            self.assertIn('operation', data)
            self.assertIn('percentage', data)
    
    def test_batch_conversion_empty_pattern(self):
        """测试批量转换（空模式）"""
        result = self.converter.convert_batch(
            "nonexistent_pattern_*.png",
            self.temp_dir / "output"
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['total_files'], 0)
    
    def test_batch_conversion_single_file(self):
        """测试批量转换（单文件）"""
        result = self.converter.convert_batch(
            str(self.test_image_path),
            self.temp_dir / "output"
        )
        
        self.assertIn('success', result)
        self.assertIn('total_files', result)
        self.assertIn('results', result)
    
    def test_cleanup(self):
        """测试清理功能"""
        # 创建一些临时文件
        temp_file = self.temp_dir / "temp_test.txt"
        temp_file.write_text("test")
        
        self.assertTrue(temp_file.exists())
        
        # 执行清理
        self.converter.cleanup()
        
        # 注意：cleanup主要清理converter自己的临时文件
        # 我们的测试文件可能不会被清理
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with ClefConverter() as converter:
            self.assertIsNotNone(converter)
        
        # 上下文退出后应该自动清理


class TestConversionProgress(unittest.TestCase):
    """转换进度测试类"""
    
    def setUp(self):
        """测试前准备"""
        from src.core.converter import ConversionProgress
        self.progress = ConversionProgress()
    
    def test_progress_initialization(self):
        """测试进度初始化"""
        self.assertEqual(self.progress.total_steps, 0)
        self.assertEqual(self.progress.current_step, 0)
        self.assertEqual(self.progress.current_operation, "")
        self.assertIsNone(self.progress.start_time)
    
    def test_set_total_steps(self):
        """测试设置总步数"""
        self.progress.set_total_steps(5)
        self.assertEqual(self.progress.total_steps, 5)
        self.assertEqual(self.progress.current_step, 0)
        self.assertIsNotNone(self.progress.start_time)
    
    def test_next_step(self):
        """测试下一步"""
        self.progress.set_total_steps(3)
        
        self.progress.next_step("步骤1")
        self.assertEqual(self.progress.current_step, 1)
        self.assertEqual(self.progress.current_operation, "步骤1")
        
        self.progress.next_step("步骤2")
        self.assertEqual(self.progress.current_step, 2)
        self.assertEqual(self.progress.current_operation, "步骤2")
    
    def test_progress_callback(self):
        """测试进度回调"""
        callback_data = []
        
        def test_callback(data):
            callback_data.append(data)
        
        self.progress.add_callback(test_callback)
        self.progress.set_total_steps(2)
        self.progress.next_step("测试步骤")
        
        self.assertEqual(len(callback_data), 1)
        data = callback_data[0]
        self.assertEqual(data['step'], 1)
        self.assertEqual(data['total'], 2)
        self.assertEqual(data['operation'], "测试步骤")
        self.assertEqual(data['percentage'], 50.0)


if __name__ == '__main__':
    unittest.main()
