"""
谱号转换模块
"""

from typing import List, Dict, Tuple, Optional
import logging

from ..models.note import Note
from ..models.score_metadata import ScoreMetadata
from ..models.recognition_result import RecognitionResult

logger = logging.getLogger(__name__)


class ClefConverter:
    """谱号转换器"""
    
    # 中音谱号到高音谱号的位置偏移
    ALTO_TO_TREBLE_OFFSET = -6
    
    # 谱号位置映射表
    CLEF_POSITION_MAP = {
        'alto_to_treble': {
            # 中音谱号位置 -> 高音谱号位置
            -10: -16,  # 下加五线 -> 下加八线
            -9: -15,   # 下加五间 -> 下加八间
            -8: -14,   # 下加四线 -> 下加七线
            -7: -13,   # 下加四间 -> 下加七间
            -6: -12,   # 下加三线 -> 下加六线
            -5: -11,   # 下加三间 -> 下加六间
            -4: -10,   # 下加二线 -> 下加五线
            -3: -9,    # 下加二间 -> 下加五间
            -2: -8,    # 下加一线 -> 下加四线
            -1: -7,    # 下加一间 -> 下加四间
            0: -6,     # 第一线 -> 下加三线
            1: -5,     # 第一间 -> 下加三间
            2: -4,     # 第二线 -> 下加二线
            3: -3,     # 第二间 -> 下加二间
            4: -2,     # 第三线(C4) -> 下加一线
            5: -1,     # 第三间 -> 下加一间
            6: 0,      # 第四线 -> 第一线(E4)
            7: 1,      # 第四间 -> 第一间
            8: 2,      # 第五线 -> 第二线(G4)
            9: 3,      # 第五间 -> 第二间
            10: 4,     # 上加一线 -> 第三线
            11: 5,     # 上加一间 -> 第三间
            12: 6,     # 上加二线 -> 第四线
            13: 7,     # 上加二间 -> 第四间
            14: 8,     # 上加三线 -> 第五线
            15: 9,     # 上加三间 -> 第五间
            16: 10,    # 上加四线 -> 上加一线
        },
        'treble_to_alto': {
            # 高音谱号位置 -> 中音谱号位置 (反向映射)
            v: k for k, v in {
                -10: -16, -9: -15, -8: -14, -7: -13, -6: -12, -5: -11,
                -4: -10, -3: -9, -2: -8, -1: -7, 0: -6, 1: -5,
                2: -4, 3: -3, 4: -2, 5: -1, 6: 0, 7: 1,
                8: 2, 9: 3, 10: 4, 11: 5, 12: 6, 13: 7,
                14: 8, 15: 9, 16: 10
            }.items()
        }
    }
    
    # MIDI音高到谱号位置的映射
    MIDI_TO_STAFF_POSITION = {
        'alto': {
            # 中音谱号：C4(60)在第三线(位置4)
            48: -8,   # C3
            49: -7,   # C#3
            50: -6,   # D3
            51: -5,   # D#3
            52: -4,   # E3
            53: -3,   # F3
            54: -2,   # F#3
            55: -1,   # G3
            56: 0,    # G#3
            57: 1,    # A3
            58: 2,    # A#3
            59: 3,    # B3
            60: 4,    # C4 (中音谱号第三线)
            61: 5,    # C#4
            62: 6,    # D4
            63: 7,    # D#4
            64: 8,    # E4
            65: 9,    # F4
            66: 10,   # F#4
            67: 11,   # G4
            68: 12,   # G#4
            69: 13,   # A4
            70: 14,   # A#4
            71: 15,   # B4
            72: 16,   # C5
        },
        'treble': {
            # 高音谱号：G4(67)在第二线(位置2)
            48: -14,  # C3
            49: -13,  # C#3
            50: -12,  # D3
            51: -11,  # D#3
            52: -10,  # E3
            53: -9,   # F3
            54: -8,   # F#3
            55: -7,   # G3
            56: -6,   # G#3
            57: -5,   # A3
            58: -4,   # A#3
            59: -3,   # B3
            60: -2,   # C4
            61: -1,   # C#4
            62: 0,    # D4
            63: 1,    # D#4
            64: 2,    # E4 (高音谱号第一线)
            65: 3,    # F4
            66: 4,    # F#4
            67: 5,    # G4 (高音谱号第二线)
            68: 6,    # G#4
            69: 7,    # A4
            70: 8,    # A#4
            71: 9,    # B4
            72: 10,   # C5
        }
    }
    
    def __init__(self):
        """初始化谱号转换器"""
        pass
    
    def convert_alto_to_treble(self, notes: List[Note]) -> List[Note]:
        """
        将中音谱号音符转换为高音谱号
        
        Args:
            notes: 中音谱号音符列表
            
        Returns:
            List[Note]: 高音谱号音符列表
        """
        converted_notes = []
        
        try:
            for note in notes:
                # 创建新的音符对象
                converted_note = Note(
                    pitch=note.pitch,  # MIDI音高保持不变
                    start_time=note.start_time,
                    duration=note.duration,
                    velocity=note.velocity,
                    accidental=note.accidental,
                    tie=note.tie,
                    dot=note.dot
                )
                
                # 转换五线谱位置
                converted_note.staff_position = self._convert_staff_position(
                    note.staff_position, 'alto', 'treble'
                )
                
                converted_notes.append(converted_note)
            
            logger.info(f"成功转换 {len(notes)} 个音符从中音谱号到高音谱号")
            return converted_notes
            
        except Exception as e:
            logger.error(f"谱号转换失败: {str(e)}")
            raise
    
    def convert_treble_to_alto(self, notes: List[Note]) -> List[Note]:
        """
        将高音谱号音符转换为中音谱号
        
        Args:
            notes: 高音谱号音符列表
            
        Returns:
            List[Note]: 中音谱号音符列表
        """
        converted_notes = []
        
        try:
            for note in notes:
                # 创建新的音符对象
                converted_note = Note(
                    pitch=note.pitch,  # MIDI音高保持不变
                    start_time=note.start_time,
                    duration=note.duration,
                    velocity=note.velocity,
                    accidental=note.accidental,
                    tie=note.tie,
                    dot=note.dot
                )
                
                # 转换五线谱位置
                converted_note.staff_position = self._convert_staff_position(
                    note.staff_position, 'treble', 'alto'
                )
                
                converted_notes.append(converted_note)
            
            logger.info(f"成功转换 {len(notes)} 个音符从高音谱号到中音谱号")
            return converted_notes
            
        except Exception as e:
            logger.error(f"谱号转换失败: {str(e)}")
            raise
    
    def _convert_staff_position(self, position: int, from_clef: str, to_clef: str) -> int:
        """
        转换五线谱位置
        
        Args:
            position: 原始位置
            from_clef: 源谱号
            to_clef: 目标谱号
            
        Returns:
            int: 转换后的位置
        """
        conversion_key = f"{from_clef}_to_{to_clef}"
        
        if conversion_key in self.CLEF_POSITION_MAP:
            position_map = self.CLEF_POSITION_MAP[conversion_key]
            if position in position_map:
                return position_map[position]
            else:
                # 如果位置不在映射表中，使用偏移量计算
                if from_clef == 'alto' and to_clef == 'treble':
                    return position + self.ALTO_TO_TREBLE_OFFSET
                elif from_clef == 'treble' and to_clef == 'alto':
                    return position - self.ALTO_TO_TREBLE_OFFSET
        
        # 默认返回原位置
        logger.warning(f"无法转换位置 {position} 从 {from_clef} 到 {to_clef}")
        return position
    
    def calculate_staff_position_from_pitch(self, pitch: int, clef: str) -> int:
        """
        根据MIDI音高计算五线谱位置
        
        Args:
            pitch: MIDI音高值
            clef: 谱号类型
            
        Returns:
            int: 五线谱位置
        """
        if clef in self.MIDI_TO_STAFF_POSITION:
            position_map = self.MIDI_TO_STAFF_POSITION[clef]
            if pitch in position_map:
                return position_map[pitch]
            else:
                # 扩展映射范围
                if clef == 'alto':
                    # 中音谱号：C4(60)在位置4
                    base_pitch = 60
                    base_position = 4
                elif clef == 'treble':
                    # 高音谱号：E4(64)在位置2
                    base_pitch = 64
                    base_position = 2
                else:
                    return 0
                
                # 每个半音对应0.5个位置
                position_offset = (pitch - base_pitch) * 0.5
                return int(base_position + position_offset)
        
        return 0
    
    def handle_ledger_lines(self, position: int, clef: str) -> Tuple[int, int]:
        """
        处理加线
        
        Args:
            position: 五线谱位置
            clef: 谱号类型
            
        Returns:
            Tuple[int, int]: (调整后的位置, 加线数量)
        """
        ledger_lines = 0
        adjusted_position = position
        
        if clef == 'treble':
            # 高音谱号：第一线到第五线为位置2到10
            if position < 2:  # 下加线
                ledger_lines = (2 - position + 1) // 2
            elif position > 10:  # 上加线
                ledger_lines = (position - 10 + 1) // 2
        elif clef == 'alto':
            # 中音谱号：第一线到第五线为位置0到8
            if position < 0:  # 下加线
                ledger_lines = (0 - position + 1) // 2
            elif position > 8:  # 上加线
                ledger_lines = (position - 8 + 1) // 2
        
        return adjusted_position, ledger_lines
    
    def convert_recognition_result(self, result: RecognitionResult, 
                                 target_clef: str) -> RecognitionResult:
        """
        转换识别结果的谱号
        
        Args:
            result: 原始识别结果
            target_clef: 目标谱号类型
            
        Returns:
            RecognitionResult: 转换后的识别结果
        """
        try:
            if not result.metadata:
                raise ValueError("识别结果缺少元数据")
            
            source_clef = result.metadata.clef_type
            
            if source_clef == target_clef:
                logger.info(f"源谱号和目标谱号相同({source_clef})，无需转换")
                return result
            
            # 转换音符
            if source_clef == 'alto' and target_clef == 'treble':
                converted_notes = self.convert_alto_to_treble(result.notes)
            elif source_clef == 'treble' and target_clef == 'alto':
                converted_notes = self.convert_treble_to_alto(result.notes)
            else:
                raise ValueError(f"不支持的谱号转换: {source_clef} -> {target_clef}")
            
            # 创建新的元数据
            new_metadata = ScoreMetadata(
                time_signature=result.metadata.time_signature,
                key_signature=result.metadata.key_signature,
                tempo=result.metadata.tempo,
                clef_type=target_clef,
                title=result.metadata.title,
                composer=result.metadata.composer
            )
            
            # 创建新的识别结果
            converted_result = RecognitionResult(
                notes=converted_notes,
                metadata=new_metadata,
                measures=result.measures,  # 小节信息保持不变
                confidence=result.confidence,
                processing_time=result.processing_time,
                image_path=result.image_path,
                errors=result.errors.copy(),
                warnings=result.warnings.copy()
            )
            
            # 添加转换信息
            converted_result.add_warning(f"谱号已从{source_clef}转换为{target_clef}")
            
            logger.info(f"成功转换识别结果从{source_clef}到{target_clef}")
            return converted_result
            
        except Exception as e:
            logger.error(f"转换识别结果失败: {str(e)}")
            raise
    
    def validate_conversion(self, original: List[Note], converted: List[Note]) -> bool:
        """
        验证转换结果
        
        Args:
            original: 原始音符列表
            converted: 转换后音符列表
            
        Returns:
            bool: 转换是否正确
        """
        try:
            if len(original) != len(converted):
                logger.error(f"音符数量不匹配: {len(original)} vs {len(converted)}")
                return False
            
            for i, (orig, conv) in enumerate(zip(original, converted)):
                # 检查MIDI音高是否保持不变
                if orig.pitch != conv.pitch:
                    logger.error(f"音符{i}的MIDI音高发生变化: {orig.pitch} -> {conv.pitch}")
                    return False
                
                # 检查时间信息是否保持不变
                if abs(orig.start_time - conv.start_time) > 0.001:
                    logger.error(f"音符{i}的开始时间发生变化: {orig.start_time} -> {conv.start_time}")
                    return False
                
                if abs(orig.duration - conv.duration) > 0.001:
                    logger.error(f"音符{i}的持续时间发生变化: {orig.duration} -> {conv.duration}")
                    return False
            
            logger.info("转换验证通过")
            return True
            
        except Exception as e:
            logger.error(f"转换验证失败: {str(e)}")
            return False
    
    def get_conversion_info(self, from_clef: str, to_clef: str) -> Dict[str, any]:
        """
        获取转换信息
        
        Args:
            from_clef: 源谱号
            to_clef: 目标谱号
            
        Returns:
            Dict: 转换信息
        """
        return {
            'from_clef': from_clef,
            'to_clef': to_clef,
            'position_offset': self.ALTO_TO_TREBLE_OFFSET if from_clef == 'alto' and to_clef == 'treble' else -self.ALTO_TO_TREBLE_OFFSET,
            'supported': f"{from_clef}_to_{to_clef}" in self.CLEF_POSITION_MAP,
            'description': f"将{from_clef}谱号转换为{to_clef}谱号"
        }
