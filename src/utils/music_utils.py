"""
音乐理论工具模块
提供音符转换、调号处理、节拍计算等功能
"""

from typing import Dict, List, Tuple, Optional, Union
import math
from .logger import get_logger

logger = get_logger(__name__)


# 音符名称到MIDI音高的映射
NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9,
    'A#': 10, 'Bb': 10, 'B': 11
}

# MIDI音高到音符名称的映射
MIDI_TO_NOTE = {v: k for k, v in NOTE_TO_MIDI.items() if '#' not in k and 'b' not in k}

# 谱号类型和其对应的中央C位置
CLEF_POSITIONS = {
    'treble': 60,    # 高音谱号，中央C在下加一线
    'alto': 60,      # 中音谱号，中央C在中间线
    'bass': 60,      # 低音谱号，中央C在上加一线
    'tenor': 60,     # 次中音谱号
    'soprano': 60,   # 女高音谱号
    'mezzo': 60,     # 女中音谱号
    'baritone': 60   # 男中音谱号
}

# 调号信息
KEY_SIGNATURES = {
    'C': {'sharps': 0, 'flats': 0, 'accidentals': []},
    'G': {'sharps': 1, 'flats': 0, 'accidentals': ['F#']},
    'D': {'sharps': 2, 'flats': 0, 'accidentals': ['F#', 'C#']},
    'A': {'sharps': 3, 'flats': 0, 'accidentals': ['F#', 'C#', 'G#']},
    'E': {'sharps': 4, 'flats': 0, 'accidentals': ['F#', 'C#', 'G#', 'D#']},
    'B': {'sharps': 5, 'flats': 0, 'accidentals': ['F#', 'C#', 'G#', 'D#', 'A#']},
    'F#': {'sharps': 6, 'flats': 0, 'accidentals': ['F#', 'C#', 'G#', 'D#', 'A#', 'E#']},
    'C#': {'sharps': 7, 'flats': 0, 'accidentals': ['F#', 'C#', 'G#', 'D#', 'A#', 'E#', 'B#']},
    'F': {'sharps': 0, 'flats': 1, 'accidentals': ['Bb']},
    'Bb': {'sharps': 0, 'flats': 2, 'accidentals': ['Bb', 'Eb']},
    'Eb': {'sharps': 0, 'flats': 3, 'accidentals': ['Bb', 'Eb', 'Ab']},
    'Ab': {'sharps': 0, 'flats': 4, 'accidentals': ['Bb', 'Eb', 'Ab', 'Db']},
    'Db': {'sharps': 0, 'flats': 5, 'accidentals': ['Bb', 'Eb', 'Ab', 'Db', 'Gb']},
    'Gb': {'sharps': 0, 'flats': 6, 'accidentals': ['Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']},
    'Cb': {'sharps': 0, 'flats': 7, 'accidentals': ['Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb', 'Fb']}
}

# 拍号信息
TIME_SIGNATURES = {
    (4, 4): {'beats_per_measure': 4, 'beat_unit': 4, 'strong_beats': [0]},
    (3, 4): {'beats_per_measure': 3, 'beat_unit': 4, 'strong_beats': [0]},
    (2, 4): {'beats_per_measure': 2, 'beat_unit': 4, 'strong_beats': [0]},
    (6, 8): {'beats_per_measure': 6, 'beat_unit': 8, 'strong_beats': [0, 3]},
    (9, 8): {'beats_per_measure': 9, 'beat_unit': 8, 'strong_beats': [0, 3, 6]},
    (12, 8): {'beats_per_measure': 12, 'beat_unit': 8, 'strong_beats': [0, 3, 6, 9]},
    (2, 2): {'beats_per_measure': 2, 'beat_unit': 2, 'strong_beats': [0]},
    (3, 2): {'beats_per_measure': 3, 'beat_unit': 2, 'strong_beats': [0]}
}


def midi_to_note_name(midi_pitch: int, use_sharps: bool = True) -> str:
    """
    将MIDI音高转换为音符名称
    
    Args:
        midi_pitch: MIDI音高值 (0-127)
        use_sharps: 是否使用升号（否则使用降号）
        
    Returns:
        音符名称（如 "C4", "F#3"）
    """
    try:
        if not 0 <= midi_pitch <= 127:
            raise ValueError(f"MIDI音高值超出范围: {midi_pitch}")
        
        octave = (midi_pitch // 12) - 1
        note_index = midi_pitch % 12
        
        if note_index in MIDI_TO_NOTE:
            note_name = MIDI_TO_NOTE[note_index]
        else:
            # 处理升降号
            if use_sharps:
                if note_index == 1: note_name = 'C#'
                elif note_index == 3: note_name = 'D#'
                elif note_index == 6: note_name = 'F#'
                elif note_index == 8: note_name = 'G#'
                elif note_index == 10: note_name = 'A#'
            else:
                if note_index == 1: note_name = 'Db'
                elif note_index == 3: note_name = 'Eb'
                elif note_index == 6: note_name = 'Gb'
                elif note_index == 8: note_name = 'Ab'
                elif note_index == 10: note_name = 'Bb'
        
        return f"{note_name}{octave}"
        
    except Exception as e:
        logger.error(f"MIDI转音符名称失败: {e}")
        return "C4"


def note_name_to_midi(note_name: str) -> int:
    """
    将音符名称转换为MIDI音高
    
    Args:
        note_name: 音符名称（如 "C4", "F#3"）
        
    Returns:
        MIDI音高值
    """
    try:
        # 解析音符名称
        note_name = note_name.strip().upper()
        
        # 提取八度
        octave_str = ''
        note_part = ''
        for i, char in enumerate(note_name):
            if char.isdigit() or char == '-':
                octave_str = note_name[i:]
                note_part = note_name[:i]
                break
        
        if not octave_str:
            raise ValueError(f"无效的音符名称: {note_name}")
        
        octave = int(octave_str)
        
        # 获取音符的半音值
        if note_part not in NOTE_TO_MIDI:
            raise ValueError(f"未知的音符: {note_part}")
        
        semitone = NOTE_TO_MIDI[note_part]
        midi_pitch = (octave + 1) * 12 + semitone
        
        if not 0 <= midi_pitch <= 127:
            raise ValueError(f"MIDI音高值超出范围: {midi_pitch}")
        
        return midi_pitch
        
    except Exception as e:
        logger.error(f"音符名称转MIDI失败: {e}")
        return 60  # 默认返回中央C


def calculate_staff_position(midi_pitch: int, clef_type: str = 'treble') -> int:
    """
    计算音符在五线谱上的位置
    
    Args:
        midi_pitch: MIDI音高值
        clef_type: 谱号类型
        
    Returns:
        五线谱位置（0为中间线，正数向上，负数向下）
    """
    try:
        # 中央C在不同谱号中的位置
        clef_offsets = {
            'treble': -6,   # 高音谱号，中央C在下加一线
            'alto': 0,      # 中音谱号，中央C在中间线
            'bass': 6,      # 低音谱号，中央C在上加一线
            'tenor': 2,     # 次中音谱号
            'soprano': -8,  # 女高音谱号
            'mezzo': -4,    # 女中音谱号
            'baritone': 4   # 男中音谱号
        }
        
        if clef_type not in clef_offsets:
            logger.warning(f"未知的谱号类型: {clef_type}, 使用高音谱号")
            clef_type = 'treble'
        
        # 计算相对于中央C的半音数
        semitones_from_c4 = midi_pitch - 60
        
        # 转换为五线谱位置（每个位置代表一个音级）
        # 考虑音阶的不规律性（E-F和B-C之间只有半音）
        position = 0
        remaining_semitones = abs(semitones_from_c4)
        direction = 1 if semitones_from_c4 >= 0 else -1
        
        # 音阶模式：全全半全全全半
        scale_pattern = [2, 2, 1, 2, 2, 2, 1]  # C大调音阶的半音间隔
        
        while remaining_semitones > 0:
            step_size = scale_pattern[position % 7]
            if remaining_semitones >= step_size:
                remaining_semitones -= step_size
                position += direction
            else:
                break
        
        # 加上谱号偏移
        final_position = position + clef_offsets[clef_type]
        
        return final_position
        
    except Exception as e:
        logger.error(f"计算五线谱位置失败: {e}")
        return 0


def convert_clef_position(staff_position: int, from_clef: str, to_clef: str) -> int:
    """
    转换不同谱号之间的五线谱位置
    
    Args:
        staff_position: 原谱号中的位置
        from_clef: 源谱号类型
        to_clef: 目标谱号类型
        
    Returns:
        目标谱号中的位置
    """
    try:
        # 谱号偏移量（相对于中央C）
        clef_offsets = {
            'treble': -6, 'alto': 0, 'bass': 6, 'tenor': 2,
            'soprano': -8, 'mezzo': -4, 'baritone': 4
        }
        
        if from_clef not in clef_offsets or to_clef not in clef_offsets:
            logger.error(f"未知的谱号类型: {from_clef} 或 {to_clef}")
            return staff_position
        
        # 计算相对于中央C的位置
        relative_position = staff_position - clef_offsets[from_clef]
        
        # 转换到目标谱号
        new_position = relative_position + clef_offsets[to_clef]
        
        logger.debug(f"谱号位置转换: {staff_position}({from_clef}) -> {new_position}({to_clef})")
        return new_position
        
    except Exception as e:
        logger.error(f"谱号位置转换失败: {e}")
        return staff_position


def get_key_signature_accidentals(key: str) -> List[str]:
    """
    获取调号的升降号
    
    Args:
        key: 调号（如 "C", "G", "F"）
        
    Returns:
        升降号列表
    """
    try:
        if key in KEY_SIGNATURES:
            return KEY_SIGNATURES[key]['accidentals'].copy()
        else:
            logger.warning(f"未知的调号: {key}")
            return []
    except Exception as e:
        logger.error(f"获取调号升降号失败: {e}")
        return []


def calculate_beat_duration(tempo: int, beat_unit: int = 4) -> float:
    """
    计算节拍持续时间
    
    Args:
        tempo: 速度（BPM）
        beat_unit: 拍子单位（4表示四分音符）
        
    Returns:
        节拍持续时间（秒）
    """
    try:
        # 四分音符的持续时间
        quarter_note_duration = 60.0 / tempo
        
        # 根据拍子单位调整
        beat_duration = quarter_note_duration * (4.0 / beat_unit)
        
        return beat_duration
        
    except Exception as e:
        logger.error(f"计算节拍持续时间失败: {e}")
        return 0.5  # 默认值


def quantize_timing(timing: float, beat_duration: float, subdivision: int = 16) -> float:
    """
    量化音符时间
    
    Args:
        timing: 原始时间
        beat_duration: 节拍持续时间
        subdivision: 细分度（16表示十六分音符）
        
    Returns:
        量化后的时间
    """
    try:
        # 计算最小时间单位
        min_unit = beat_duration / subdivision
        
        # 量化到最近的时间点
        quantized = round(timing / min_unit) * min_unit
        
        return quantized
        
    except Exception as e:
        logger.error(f"时间量化失败: {e}")
        return timing


def validate_time_signature(numerator: int, denominator: int) -> bool:
    """
    验证拍号是否有效
    
    Args:
        numerator: 分子
        denominator: 分母
        
    Returns:
        是否为有效拍号
    """
    try:
        # 检查分母是否为2的幂
        if denominator <= 0 or (denominator & (denominator - 1)) != 0:
            return False
        
        # 检查分子是否为正数
        if numerator <= 0:
            return False
        
        # 检查是否为常见拍号
        return (numerator, denominator) in TIME_SIGNATURES or True  # 允许其他拍号
        
    except Exception as e:
        logger.error(f"验证拍号失败: {e}")
        return False


def get_enharmonic_equivalent(note_name: str, prefer_sharps: bool = True) -> str:
    """
    获取等音异名
    
    Args:
        note_name: 音符名称
        prefer_sharps: 是否偏好升号
        
    Returns:
        等音异名
    """
    try:
        # 等音异名映射
        enharmonic_map = {
            'C#': 'Db', 'Db': 'C#',
            'D#': 'Eb', 'Eb': 'D#',
            'F#': 'Gb', 'Gb': 'F#',
            'G#': 'Ab', 'Ab': 'G#',
            'A#': 'Bb', 'Bb': 'A#'
        }
        
        # 提取音符部分（不包括八度）
        note_part = ''.join(c for c in note_name if not c.isdigit() and c != '-')
        octave_part = note_name[len(note_part):]
        
        if note_part in enharmonic_map:
            equivalent = enharmonic_map[note_part] + octave_part
            return equivalent
        
        return note_name  # 没有等音异名
        
    except Exception as e:
        logger.error(f"获取等音异名失败: {e}")
        return note_name
