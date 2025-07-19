"""
MIDI转换模块
"""

import mido
import numpy as np
from typing import List, Optional, Dict, Any
import logging
import tempfile
import os

from ..models.note import Note
from ..models.score_metadata import ScoreMetadata
from ..models.recognition_result import RecognitionResult

logger = logging.getLogger(__name__)


class MIDIConverter:
    """MIDI转换器"""
    
    def __init__(self, ticks_per_beat: int = 480):
        """
        初始化MIDI转换器
        
        Args:
            ticks_per_beat: 每拍的tick数
        """
        self.ticks_per_beat = ticks_per_beat
    
    def notes_to_midi(self, notes: List[Note], metadata: ScoreMetadata) -> mido.MidiFile:
        """
        将音符列表转换为MIDI文件
        
        Args:
            notes: 音符列表
            metadata: 乐谱元数据
            
        Returns:
            mido.MidiFile: MIDI文件对象
        """
        try:
            # 创建MIDI文件
            mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
            track = mido.MidiTrack()
            mid.tracks.append(track)
            
            # 添加元数据
            self._add_metadata_to_track(track, metadata)
            
            # 转换音符为MIDI事件
            midi_events = self._notes_to_midi_events(notes, metadata)
            
            # 按时间排序事件
            midi_events.sort(key=lambda x: x['time'])
            
            # 添加事件到轨道
            current_time = 0
            for event in midi_events:
                delta_time = event['time'] - current_time
                delta_ticks = self._seconds_to_ticks(delta_time, metadata.tempo)
                
                if event['type'] == 'note_on':
                    msg = mido.Message('note_on', 
                                     channel=0, 
                                     note=event['note'], 
                                     velocity=event['velocity'], 
                                     time=delta_ticks)
                elif event['type'] == 'note_off':
                    msg = mido.Message('note_off', 
                                     channel=0, 
                                     note=event['note'], 
                                     velocity=0, 
                                     time=delta_ticks)
                
                track.append(msg)
                current_time = event['time']
            
            logger.info(f"成功转换 {len(notes)} 个音符为MIDI")
            return mid
            
        except Exception as e:
            logger.error(f"MIDI转换失败: {str(e)}")
            raise
    
    def _add_metadata_to_track(self, track: mido.MidiTrack, metadata: ScoreMetadata) -> None:
        """添加元数据到MIDI轨道"""
        try:
            # 设置速度
            tempo = mido.bpm2tempo(metadata.tempo)
            track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
            
            # 设置拍号
            numerator, denominator = metadata.time_signature
            track.append(mido.MetaMessage('time_signature', 
                                        numerator=numerator, 
                                        denominator=denominator, 
                                        clocks_per_click=24, 
                                        notated_32nd_notes_per_beat=8, 
                                        time=0))
            
            # 设置调号
            key_sharps_flats = metadata.get_key_signature_sharps_flats()
            track.append(mido.MetaMessage('key_signature', 
                                        key=key_sharps_flats, 
                                        time=0))
            
            # 添加标题和作曲家信息
            if metadata.title:
                track.append(mido.MetaMessage('track_name', name=metadata.title, time=0))
            
            if metadata.composer:
                track.append(mido.MetaMessage('text', text=f"Composer: {metadata.composer}", time=0))
            
        except Exception as e:
            logger.warning(f"添加MIDI元数据失败: {str(e)}")
    
    def _notes_to_midi_events(self, notes: List[Note], metadata: ScoreMetadata) -> List[Dict[str, Any]]:
        """将音符转换为MIDI事件列表"""
        events = []
        
        for note in notes:
            # Note On事件
            events.append({
                'time': note.start_time,
                'type': 'note_on',
                'note': note.pitch,
                'velocity': note.velocity
            })
            
            # Note Off事件
            events.append({
                'time': note.end_time,
                'type': 'note_off',
                'note': note.pitch,
                'velocity': 0
            })
        
        return events
    
    def _seconds_to_ticks(self, seconds: float, tempo: int) -> int:
        """将秒数转换为MIDI ticks"""
        beats = seconds * tempo / 60.0
        ticks = int(beats * self.ticks_per_beat)
        return max(0, ticks)
    
    def calculate_timing(self, notes: List[Note]) -> List[Note]:
        """
        计算和调整音符时间
        
        Args:
            notes: 输入音符列表
            
        Returns:
            List[Note]: 调整后的音符列表
        """
        if not notes:
            return notes
        
        # 按开始时间排序
        sorted_notes = sorted(notes, key=lambda n: n.start_time)
        
        # 调整重叠的音符
        adjusted_notes = []
        for i, note in enumerate(sorted_notes):
            adjusted_note = Note(
                pitch=note.pitch,
                start_time=note.start_time,
                duration=note.duration,
                velocity=note.velocity,
                staff_position=note.staff_position,
                accidental=note.accidental
            )
            
            # 检查与前一个音符的重叠
            if i > 0:
                prev_note = adjusted_notes[-1]
                if adjusted_note.start_time < prev_note.end_time:
                    # 调整开始时间避免重叠
                    adjusted_note.start_time = prev_note.end_time
            
            # 检查与后一个音符的重叠
            if i < len(sorted_notes) - 1:
                next_note = sorted_notes[i + 1]
                if adjusted_note.end_time > next_note.start_time:
                    # 调整持续时间避免重叠
                    max_duration = next_note.start_time - adjusted_note.start_time
                    if max_duration > 0:
                        adjusted_note.duration = min(adjusted_note.duration, max_duration)
                    else:
                        adjusted_note.duration = 0.1  # 最小持续时间
            
            adjusted_notes.append(adjusted_note)
        
        logger.info(f"调整了 {len(notes)} 个音符的时间")
        return adjusted_notes
    
    def quantize_timing(self, notes: List[Note], resolution: float = 0.125) -> List[Note]:
        """
        量化音符时间
        
        Args:
            notes: 输入音符列表
            resolution: 量化分辨率（秒）
            
        Returns:
            List[Note]: 量化后的音符列表
        """
        quantized_notes = []
        
        for note in notes:
            # 量化开始时间
            quantized_start = round(note.start_time / resolution) * resolution
            
            # 量化持续时间
            quantized_duration = max(resolution, round(note.duration / resolution) * resolution)
            
            quantized_note = Note(
                pitch=note.pitch,
                start_time=quantized_start,
                duration=quantized_duration,
                velocity=note.velocity,
                staff_position=note.staff_position,
                accidental=note.accidental
            )
            
            quantized_notes.append(quantized_note)
        
        logger.info(f"量化了 {len(notes)} 个音符的时间")
        return quantized_notes
    
    def midi_to_notes(self, midi_file: mido.MidiFile) -> tuple[List[Note], ScoreMetadata]:
        """
        将MIDI文件转换为音符列表
        
        Args:
            midi_file: MIDI文件对象
            
        Returns:
            tuple: (音符列表, 元数据)
        """
        notes = []
        metadata = ScoreMetadata()
        
        try:
            # 解析MIDI文件
            current_time = 0
            active_notes = {}  # 记录正在播放的音符
            
            for track in midi_file.tracks:
                current_time = 0
                
                for msg in track:
                    current_time += mido.tick2second(msg.time, midi_file.ticks_per_beat, 500000)
                    
                    if msg.type == 'note_on' and msg.velocity > 0:
                        # 音符开始
                        active_notes[msg.note] = {
                            'start_time': current_time,
                            'velocity': msg.velocity
                        }
                    
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        # 音符结束
                        if msg.note in active_notes:
                            note_info = active_notes.pop(msg.note)
                            duration = current_time - note_info['start_time']
                            
                            if duration > 0:
                                note = Note(
                                    pitch=msg.note,
                                    start_time=note_info['start_time'],
                                    duration=duration,
                                    velocity=note_info['velocity']
                                )
                                notes.append(note)
                    
                    elif msg.type == 'set_tempo':
                        # 更新速度
                        metadata.tempo = mido.tempo2bpm(msg.tempo)
                    
                    elif msg.type == 'time_signature':
                        # 更新拍号
                        metadata.time_signature = (msg.numerator, msg.denominator)
                    
                    elif msg.type == 'key_signature':
                        # 更新调号（简化处理）
                        if msg.key == 0:
                            metadata.key_signature = 'C'
                        elif msg.key > 0:
                            sharp_keys = ['G', 'D', 'A', 'E', 'B', 'F#', 'C#']
                            metadata.key_signature = sharp_keys[min(msg.key - 1, 6)]
                        else:
                            flat_keys = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
                            metadata.key_signature = flat_keys[min(-msg.key - 1, 6)]
            
            logger.info(f"从MIDI文件解析出 {len(notes)} 个音符")
            return notes, metadata
            
        except Exception as e:
            logger.error(f"MIDI解析失败: {str(e)}")
            raise
    
    def save_midi_file(self, midi_file: mido.MidiFile, output_path: str) -> bool:
        """
        保存MIDI文件
        
        Args:
            midi_file: MIDI文件对象
            output_path: 输出路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            midi_file.save(output_path)
            logger.info(f"MIDI文件已保存: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存MIDI文件失败: {str(e)}")
            return False
    
    def validate_midi(self, midi_file: mido.MidiFile) -> bool:
        """
        验证MIDI文件
        
        Args:
            midi_file: MIDI文件对象
            
        Returns:
            bool: 是否有效
        """
        try:
            # 检查基本结构
            if not midi_file.tracks:
                logger.error("MIDI文件没有轨道")
                return False
            
            # 检查是否有音符事件
            has_notes = False
            for track in midi_file.tracks:
                for msg in track:
                    if msg.type in ['note_on', 'note_off']:
                        has_notes = True
                        break
                if has_notes:
                    break
            
            if not has_notes:
                logger.warning("MIDI文件没有音符事件")
                return False
            
            logger.info("MIDI文件验证通过")
            return True
            
        except Exception as e:
            logger.error(f"MIDI文件验证失败: {str(e)}")
            return False
