"""
乐谱渲染模块
"""

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from typing import List, Optional, Tuple, Dict, Any
import logging
import tempfile
import os
import subprocess

from ..models.note import Note
from ..models.score_metadata import ScoreMetadata
from ..models.recognition_result import RecognitionResult

logger = logging.getLogger(__name__)


class ScoreRenderer:
    """乐谱渲染器"""

    def __init__(self, width: int = 800, height: int = 600, dpi: int = 300):
        """
        初始化乐谱渲染器

        Args:
            width: 图像宽度
            height: 图像高度
            dpi: 分辨率
        """
        self.width = width
        self.height = height
        self.dpi = dpi
        self.staff_line_spacing = 20  # 五线谱线间距
        self.staff_height = self.staff_line_spacing * 4  # 五线谱总高度

        # 尝试导入music21库
        try:
            import music21

            self.music21 = music21
            self.has_music21 = True
            logger.info("成功导入music21库")
        except ImportError:
            self.music21 = None
            self.has_music21 = False
            logger.warning("未找到music21库，将使用基础渲染方法")

        # 检查LilyPond是否可用
        self.has_lilypond = self._check_lilypond()

    def _check_lilypond(self) -> bool:
        """检查LilyPond是否安装"""
        try:
            result = subprocess.run(
                ["lilypond", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info("检测到LilyPond")
                return True
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

        logger.warning("未检测到LilyPond，将使用基础渲染方法")
        return False

    def render_score(
        self, notes: List[Note], metadata: ScoreMetadata, output_format: str = "png"
    ) -> Image.Image:
        """
        渲染乐谱

        Args:
            notes: 音符列表
            metadata: 乐谱元数据
            output_format: 输出格式

        Returns:
            Image.Image: 渲染后的图像
        """
        try:
            if self.has_music21 and self.has_lilypond:
                return self._render_with_music21(notes, metadata, output_format)
            else:
                return self._render_basic(notes, metadata)
        except Exception as e:
            logger.error(f"渲染乐谱失败: {e}")
            return None

    def render_score_to_file(
        self,
        recognition_result: RecognitionResult,
        output_path: str,
        output_format: str = "png",
    ) -> bool:
        """
        渲染乐谱并保存到文件

        Args:
            recognition_result: 识别结果
            output_path: 输出文件路径
            output_format: 输出格式

        Returns:
            bool: 是否成功
        """
        try:
            # 渲染乐谱图像
            image = self.render_score(
                recognition_result.notes, recognition_result.metadata, output_format
            )

            if image is None:
                logger.error("渲染乐谱失败")
                return False

            # 保存图像
            if output_format.lower() in ["png", "jpg", "jpeg"]:
                image.save(output_path, format=output_format.upper())
                logger.info(f"乐谱图像已保存: {output_path}")
                return True
            else:
                logger.error(f"不支持的图像格式: {output_format}")
                return False

        except Exception as e:
            logger.error(f"渲染乐谱到文件失败: {e}")
            return False

        except Exception as e:
            logger.error(f"乐谱渲染失败: {str(e)}")
            # 返回错误图像
            return self._create_error_image(str(e))

    def _render_with_music21(
        self, notes: List[Note], metadata: ScoreMetadata, output_format: str
    ) -> Image.Image:
        """使用music21和LilyPond渲染乐谱"""
        try:
            # 创建music21 Stream对象
            score = self.music21.stream.Score()
            part = self.music21.stream.Part()

            # 设置谱号
            if metadata.clef_type == "treble":
                clef = self.music21.clef.TrebleClef()
            elif metadata.clef_type == "alto":
                clef = self.music21.clef.AltoClef()
            elif metadata.clef_type == "bass":
                clef = self.music21.clef.BassClef()
            else:
                clef = self.music21.clef.TrebleClef()

            part.append(clef)

            # 设置拍号
            time_sig = self.music21.meter.TimeSignature(
                f"{metadata.time_signature[0]}/{metadata.time_signature[1]}"
            )
            part.append(time_sig)

            # 设置调号
            key_sig = self.music21.key.KeySignature(
                metadata.get_key_signature_sharps_flats()
            )
            part.append(key_sig)

            # 添加音符
            for note in sorted(notes, key=lambda n: n.start_time):
                # 转换MIDI音高为music21音符
                m21_note = self.music21.note.Note(midi=note.pitch)

                # 设置时值（简化处理）
                duration_quarters = note.duration * metadata.tempo / 60.0
                m21_note.duration = self.music21.duration.Duration(
                    quarterLength=duration_quarters
                )

                part.append(m21_note)

            score.append(part)

            # 使用LilyPond渲染
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, f"score.{output_format}")

                # 生成LilyPond文件
                ly_path = os.path.join(temp_dir, "score.ly")
                score.write("lilypond", fp=ly_path)

                # 调用LilyPond渲染
                cmd = ["lilypond", "--png", "--output", temp_dir, ly_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    # 查找生成的PNG文件
                    png_files = [f for f in os.listdir(temp_dir) if f.endswith(".png")]
                    if png_files:
                        png_path = os.path.join(temp_dir, png_files[0])
                        image = Image.open(png_path)
                        logger.info("使用music21+LilyPond成功渲染乐谱")
                        return image

                logger.warning("LilyPond渲染失败，使用基础方法")
                return self._render_basic(notes, metadata)

        except Exception as e:
            logger.error(f"music21渲染失败: {str(e)}")
            return self._render_basic(notes, metadata)

    def _render_basic(self, notes: List[Note], metadata: ScoreMetadata) -> Image.Image:
        """基础乐谱渲染方法"""
        try:
            # 创建白色背景图像
            image = Image.new("RGB", (self.width, self.height), "white")
            draw = ImageDraw.Draw(image)

            # 计算五线谱位置
            staff_y = self.height // 2 - self.staff_height // 2

            # 绘制五线谱
            self._draw_staff(draw, staff_y)

            # 绘制谱号
            self._draw_clef(draw, metadata.clef_type, staff_y)

            # 绘制拍号
            self._draw_time_signature(draw, metadata.time_signature, staff_y)

            # 绘制音符
            self._draw_notes(draw, notes, staff_y, metadata)

            logger.info("使用基础方法成功渲染乐谱")
            return image

        except Exception as e:
            logger.error(f"基础渲染失败: {str(e)}")
            return self._create_error_image(str(e))

    def _draw_staff(self, draw: ImageDraw.Draw, staff_y: int) -> None:
        """绘制五线谱"""
        line_color = "black"
        line_width = 2

        for i in range(5):
            y = staff_y + i * self.staff_line_spacing
            draw.line(
                [(50, y), (self.width - 50, y)], fill=line_color, width=line_width
            )

    def _draw_clef(self, draw: ImageDraw.Draw, clef_type: str, staff_y: int) -> None:
        """绘制谱号"""
        clef_x = 70
        clef_y = staff_y + self.staff_height // 2

        # 简化的谱号绘制
        if clef_type == "treble":
            # 高音谱号 (简化为G字符)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            draw.text((clef_x, clef_y - 20), "𝄞", fill="black", font=font)
        elif clef_type == "alto":
            # 中音谱号 (简化为C字符)
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            draw.text((clef_x, clef_y - 15), "𝄡", fill="black", font=font)
        elif clef_type == "bass":
            # 低音谱号 (简化为F字符)
            try:
                font = ImageFont.truetype("arial.ttf", 35)
            except:
                font = ImageFont.load_default()
            draw.text((clef_x, clef_y - 18), "𝄢", fill="black", font=font)

    def _draw_time_signature(
        self, draw: ImageDraw.Draw, time_sig: Tuple[int, int], staff_y: int
    ) -> None:
        """绘制拍号"""
        sig_x = 120

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # 分子
        draw.text(
            (sig_x, staff_y + self.staff_line_spacing),
            str(time_sig[0]),
            fill="black",
            font=font,
        )

        # 分母
        draw.text(
            (sig_x, staff_y + self.staff_line_spacing * 2),
            str(time_sig[1]),
            fill="black",
            font=font,
        )

    def _draw_notes(
        self,
        draw: ImageDraw.Draw,
        notes: List[Note],
        staff_y: int,
        metadata: ScoreMetadata,
    ) -> None:
        """绘制音符"""
        if not notes:
            return

        # 计算音符间距
        note_spacing = (self.width - 200) / max(len(notes), 1)
        start_x = 180

        for i, note in enumerate(sorted(notes, key=lambda n: n.start_time)):
            x = start_x + i * note_spacing

            # 计算音符在五线谱上的y位置
            y = self._calculate_note_y(note, staff_y, metadata.clef_type)

            # 绘制音符
            self._draw_single_note(draw, x, y, note, staff_y)

    def _calculate_note_y(self, note: Note, staff_y: int, clef_type: str) -> int:
        """计算音符的y坐标"""
        # 根据谱号类型和音高计算位置
        if clef_type == "treble":
            # 高音谱号：E4(64)在第一线
            base_pitch = 64
            base_y = staff_y + self.staff_height
        elif clef_type == "alto":
            # 中音谱号：C4(60)在第三线
            base_pitch = 60
            base_y = staff_y + self.staff_line_spacing * 2
        elif clef_type == "bass":
            # 低音谱号：G2(43)在第一线
            base_pitch = 43
            base_y = staff_y + self.staff_height
        else:
            base_pitch = 60
            base_y = staff_y + self.staff_line_spacing * 2

        # 每个半音对应的像素偏移
        semitone_offset = self.staff_line_spacing / 4

        # 计算y坐标
        pitch_diff = note.pitch - base_pitch
        y = base_y - pitch_diff * semitone_offset

        return int(y)

    def _draw_single_note(
        self, draw: ImageDraw.Draw, x: int, y: int, note: Note, staff_y: int
    ) -> None:
        """绘制单个音符"""
        note_radius = 6

        # 绘制符头
        draw.ellipse(
            [
                x - note_radius,
                y - note_radius // 2,
                x + note_radius,
                y + note_radius // 2,
            ],
            fill="black",
        )

        # 绘制符干
        stem_height = 30
        if y < staff_y + self.staff_height // 2:
            # 音符在五线谱上方，符干向下
            draw.line(
                [(x - note_radius, y), (x - note_radius, y + stem_height)],
                fill="black",
                width=2,
            )
        else:
            # 音符在五线谱下方，符干向上
            draw.line(
                [(x + note_radius, y), (x + note_radius, y - stem_height)],
                fill="black",
                width=2,
            )

        # 绘制加线（如果需要）
        self._draw_ledger_lines(draw, x, y, staff_y)

    def _draw_ledger_lines(
        self, draw: ImageDraw.Draw, x: int, y: int, staff_y: int
    ) -> None:
        """绘制加线"""
        line_length = 20

        # 检查是否需要下加线
        if y > staff_y + self.staff_height:
            lines_below = (
                int((y - (staff_y + self.staff_height)) / self.staff_line_spacing) + 1
            )
            for i in range(1, lines_below + 1):
                line_y = staff_y + self.staff_height + i * self.staff_line_spacing
                if abs(y - line_y) < self.staff_line_spacing // 2:
                    draw.line(
                        [
                            (x - line_length // 2, line_y),
                            (x + line_length // 2, line_y),
                        ],
                        fill="black",
                        width=2,
                    )

        # 检查是否需要上加线
        elif y < staff_y:
            lines_above = int((staff_y - y) / self.staff_line_spacing) + 1
            for i in range(1, lines_above + 1):
                line_y = staff_y - i * self.staff_line_spacing
                if abs(y - line_y) < self.staff_line_spacing // 2:
                    draw.line(
                        [
                            (x - line_length // 2, line_y),
                            (x + line_length // 2, line_y),
                        ],
                        fill="black",
                        width=2,
                    )

    def _create_error_image(self, error_message: str) -> Image.Image:
        """创建错误图像"""
        image = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # 绘制错误信息
        draw.text(
            (50, self.height // 2), f"渲染错误: {error_message}", fill="red", font=font
        )

        return image

    def export_image(
        self, image: Image.Image, output_path: str, format: str = "PNG"
    ) -> bool:
        """
        导出图像

        Args:
            image: 图像对象
            output_path: 输出路径
            format: 图像格式

        Returns:
            bool: 是否导出成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # 保存图像
            if format.upper() == "PDF":
                image.save(output_path, format="PDF", resolution=self.dpi)
            else:
                image.save(output_path, format=format.upper(), dpi=(self.dpi, self.dpi))

            logger.info(f"图像已导出: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出图像失败: {str(e)}")
            return False

    def render_to_file(
        self,
        notes: List[Note],
        metadata: ScoreMetadata,
        output_path: str,
        format: str = "PNG",
    ) -> bool:
        """
        渲染乐谱并保存到文件

        Args:
            notes: 音符列表
            metadata: 乐谱元数据
            output_path: 输出路径
            format: 输出格式

        Returns:
            bool: 是否成功
        """
        try:
            image = self.render_score(notes, metadata, format.lower())
            return self.export_image(image, output_path, format)

        except Exception as e:
            logger.error(f"渲染到文件失败: {str(e)}")
            return False
