"""
工具模块测试用例
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils import file_utils, image_utils, music_utils, logger


class TestFileUtils(unittest.TestCase):
    """文件工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # 创建测试图像文件
        self.test_image = self.temp_dir / "test.png"
        image = Image.new('RGB', (100, 100), 'white')
        image.save(self.test_image)
        
        # 创建测试文本文件
        self.test_text = self.temp_dir / "test.txt"
        self.test_text.write_text("test content")
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_validate_image_file_valid(self):
        """测试验证有效图像文件"""
        self.assertTrue(file_utils.validate_image_file(self.test_image))
    
    def test_validate_image_file_invalid(self):
        """测试验证无效图像文件"""
        self.assertFalse(file_utils.validate_image_file(self.test_text))
        self.assertFalse(file_utils.validate_image_file("nonexistent.png"))
    
    def test_validate_output_format(self):
        """测试验证输出格式"""
        self.assertTrue(file_utils.validate_output_format("png"))
        self.assertTrue(file_utils.validate_output_format(".pdf"))
        self.assertTrue(file_utils.validate_output_format("midi"))
        self.assertFalse(file_utils.validate_output_format("xyz"))
    
    def test_ensure_directory(self):
        """测试确保目录存在"""
        new_dir = self.temp_dir / "new_directory"
        self.assertFalse(new_dir.exists())
        
        result = file_utils.ensure_directory(new_dir)
        self.assertTrue(new_dir.exists())
        self.assertEqual(result, new_dir)
    
    def test_get_safe_filename(self):
        """测试获取安全文件名"""
        unsafe_name = "test<>:\"/\\|?*.txt"
        safe_name = file_utils.get_safe_filename(unsafe_name)
        self.assertNotIn('<', safe_name)
        self.assertNotIn('>', safe_name)
        self.assertNotIn(':', safe_name)
    
    def test_generate_output_path(self):
        """测试生成输出路径"""
        output_path = file_utils.generate_output_path(
            self.test_image,
            self.temp_dir / "output",
            suffix="converted",
            extension=".png"
        )
        
        self.assertTrue(output_path.parent.exists())
        self.assertTrue(output_path.name.endswith("_converted.png"))
    
    def test_find_image_files(self):
        """测试查找图像文件"""
        # 创建更多测试文件
        (self.temp_dir / "test2.jpg").write_bytes(b"fake jpg")
        (self.temp_dir / "test.txt").write_text("not image")
        
        # 由于我们的validate_image_file会检查真实的图像格式
        # 只有真正的图像文件会被找到
        image_files = list(file_utils.find_image_files(self.temp_dir))
        self.assertGreater(len(image_files), 0)
        
        # 检查找到的文件都是图像文件
        for file_path in image_files:
            self.assertTrue(file_utils.validate_image_file(file_path))
    
    def test_calculate_file_hash(self):
        """测试计算文件哈希"""
        hash_md5 = file_utils.calculate_file_hash(self.test_text, 'md5')
        hash_sha1 = file_utils.calculate_file_hash(self.test_text, 'sha1')
        
        self.assertIsInstance(hash_md5, str)
        self.assertIsInstance(hash_sha1, str)
        self.assertNotEqual(hash_md5, hash_sha1)
        self.assertEqual(len(hash_md5), 32)  # MD5 长度
        self.assertEqual(len(hash_sha1), 40)  # SHA1 长度
    
    def test_get_file_info(self):
        """测试获取文件信息"""
        info = file_utils.get_file_info(self.test_image)
        
        self.assertIn('path', info)
        self.assertIn('name', info)
        self.assertIn('size', info)
        self.assertIn('exists', info)
        self.assertTrue(info['exists'])
        self.assertTrue(info['is_file'])


class TestImageUtils(unittest.TestCase):
    """图像工具测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # 创建测试图像
        self.test_image_path = self.temp_dir / "test.png"
        self.test_image = Image.new('RGB', (200, 150), 'white')
        self.test_image.save(self.test_image_path)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_image(self):
        """测试加载图像"""
        image = image_utils.load_image(self.test_image_path)
        self.assertIsNotNone(image)
        self.assertEqual(image.size, (200, 150))
        
        # 测试加载不存在的文件
        none_image = image_utils.load_image("nonexistent.png")
        self.assertIsNone(none_image)
    
    def test_save_image(self):
        """测试保存图像"""
        output_path = self.temp_dir / "output.png"
        success = image_utils.save_image(self.test_image, output_path)
        
        self.assertTrue(success)
        self.assertTrue(output_path.exists())
    
    def test_resize_image(self):
        """测试调整图像尺寸"""
        # 保持宽高比
        resized = image_utils.resize_image(self.test_image, (100, 100), maintain_aspect=True)
        self.assertLessEqual(max(resized.size), 100)
        
        # 不保持宽高比
        resized = image_utils.resize_image(self.test_image, (100, 100), maintain_aspect=False)
        self.assertEqual(resized.size, (100, 100))
    
    def test_enhance_image(self):
        """测试图像增强"""
        enhanced = image_utils.enhance_image(
            self.test_image,
            brightness=1.2,
            contrast=1.1,
            sharpness=1.1
        )
        
        self.assertIsNotNone(enhanced)
        self.assertEqual(enhanced.size, self.test_image.size)
    
    def test_convert_to_grayscale(self):
        """测试转换为灰度"""
        grayscale = image_utils.convert_to_grayscale(self.test_image)
        self.assertEqual(grayscale.mode, 'L')
    
    def test_binarize_image(self):
        """测试图像二值化"""
        binary = image_utils.binarize_image(self.test_image, threshold=128, method='simple')
        self.assertEqual(binary.mode, 'L')
    
    def test_get_image_info(self):
        """测试获取图像信息"""
        info = image_utils.get_image_info(self.test_image)
        
        self.assertIn('size', info)
        self.assertIn('width', info)
        self.assertIn('height', info)
        self.assertIn('mode', info)
        self.assertEqual(info['width'], 200)
        self.assertEqual(info['height'], 150)


class TestMusicUtils(unittest.TestCase):
    """音乐工具测试类"""
    
    def test_midi_to_note_name(self):
        """测试MIDI转音符名称"""
        # 中央C
        self.assertEqual(music_utils.midi_to_note_name(60), "C4")
        
        # A4 (440Hz)
        self.assertEqual(music_utils.midi_to_note_name(69), "A4")
        
        # 测试升号
        self.assertEqual(music_utils.midi_to_note_name(61, use_sharps=True), "C#4")
        
        # 测试降号
        self.assertEqual(music_utils.midi_to_note_name(61, use_sharps=False), "Db4")
    
    def test_note_name_to_midi(self):
        """测试音符名称转MIDI"""
        self.assertEqual(music_utils.note_name_to_midi("C4"), 60)
        self.assertEqual(music_utils.note_name_to_midi("A4"), 69)
        self.assertEqual(music_utils.note_name_to_midi("C#4"), 61)
        self.assertEqual(music_utils.note_name_to_midi("Db4"), 61)
    
    def test_calculate_staff_position(self):
        """测试计算五线谱位置"""
        # 中央C在高音谱号的位置
        treble_pos = music_utils.calculate_staff_position(60, 'treble')
        self.assertIsInstance(treble_pos, int)
        
        # 中央C在中音谱号的位置
        alto_pos = music_utils.calculate_staff_position(60, 'alto')
        self.assertIsInstance(alto_pos, int)
        
        # 中音谱号和高音谱号的位置应该不同
        self.assertNotEqual(treble_pos, alto_pos)
    
    def test_convert_clef_position(self):
        """测试谱号位置转换"""
        # 中音谱号位置0转换为高音谱号
        converted_pos = music_utils.convert_clef_position(0, 'alto', 'treble')
        self.assertIsInstance(converted_pos, int)
        
        # 转换应该是可逆的
        back_converted = music_utils.convert_clef_position(converted_pos, 'treble', 'alto')
        self.assertEqual(back_converted, 0)
    
    def test_get_key_signature_accidentals(self):
        """测试获取调号升降号"""
        # C大调没有升降号
        c_major = music_utils.get_key_signature_accidentals('C')
        self.assertEqual(len(c_major), 0)
        
        # G大调有一个升号
        g_major = music_utils.get_key_signature_accidentals('G')
        self.assertEqual(len(g_major), 1)
        self.assertIn('F#', g_major)
        
        # F大调有一个降号
        f_major = music_utils.get_key_signature_accidentals('F')
        self.assertEqual(len(f_major), 1)
        self.assertIn('Bb', f_major)
    
    def test_calculate_beat_duration(self):
        """测试计算节拍持续时间"""
        # 120 BPM的四分音符
        duration = music_utils.calculate_beat_duration(120, 4)
        self.assertAlmostEqual(duration, 0.5, places=2)
        
        # 60 BPM的四分音符
        duration = music_utils.calculate_beat_duration(60, 4)
        self.assertAlmostEqual(duration, 1.0, places=2)
    
    def test_validate_time_signature(self):
        """测试验证拍号"""
        self.assertTrue(music_utils.validate_time_signature(4, 4))
        self.assertTrue(music_utils.validate_time_signature(3, 4))
        self.assertTrue(music_utils.validate_time_signature(6, 8))
        
        # 无效拍号
        self.assertFalse(music_utils.validate_time_signature(4, 3))  # 分母不是2的幂
        self.assertFalse(music_utils.validate_time_signature(0, 4))  # 分子为0
        self.assertFalse(music_utils.validate_time_signature(4, 0))  # 分母为0
    
    def test_get_enharmonic_equivalent(self):
        """测试获取等音异名"""
        self.assertEqual(music_utils.get_enharmonic_equivalent('C#4'), 'Db4')
        self.assertEqual(music_utils.get_enharmonic_equivalent('Db4'), 'C#4')
        self.assertEqual(music_utils.get_enharmonic_equivalent('F#3'), 'Gb3')
        
        # 没有等音异名的音符
        self.assertEqual(music_utils.get_enharmonic_equivalent('C4'), 'C4')


class TestLogger(unittest.TestCase):
    """日志工具测试类"""
    
    def test_setup_logger(self):
        """测试设置日志器"""
        test_logger = logger.setup_logger('test_logger', level='DEBUG')
        self.assertIsNotNone(test_logger)
        self.assertEqual(test_logger.level, logging.DEBUG)
    
    def test_get_logger(self):
        """测试获取日志器"""
        test_logger = logger.get_logger('test_module')
        self.assertIsNotNone(test_logger)
        self.assertEqual(test_logger.name, 'test_module')
    
    def test_logger_mixin(self):
        """测试日志器混入类"""
        class TestClass(logger.LoggerMixin):
            pass
        
        test_obj = TestClass()
        self.assertIsNotNone(test_obj.logger)
        self.assertTrue(test_obj.logger.name.endswith('TestClass'))


if __name__ == '__main__':
    unittest.main()
