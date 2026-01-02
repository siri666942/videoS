import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class TranscriptStorage:
    """
    转录文本存储模块，用于保存和读取视频转录文本
    """
    def __init__(self, storage_dir: str = "transcripts"):
        """
        初始化转录文本存储
        
        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_transcript_path(self, video_filename: str) -> Path:
        """
        获取转录文件的路径
        
        Args:
            video_filename: 视频文件名
            
        Returns:
            转录文件路径
        """
        # 移除文件扩展名，添加_transcript.json后缀
        base_name = Path(video_filename).stem
        return self.storage_dir / f"{base_name}_transcript.json"
    
    def save_transcript(self, video_filename: str, transcript_data: Dict[str, Any]) -> str:
        """
        保存转录结果到JSON文件
        
        Args:
            video_filename: 视频文件名
            transcript_data: 转录数据字典，包含text和segments等
            
        Returns:
            保存的文件路径
        """
        transcript_path = self._get_transcript_path(video_filename)
        
        # 保存完整转录数据
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
        
        return str(transcript_path)
    
    def load_transcript(self, video_filename: str) -> Optional[Dict[str, Any]]:
        """
        读取转录文本
        
        Args:
            video_filename: 视频文件名
            
        Returns:
            转录数据字典，如果文件不存在则返回None
        """
        transcript_path = self._get_transcript_path(video_filename)
        
        if not transcript_path.exists():
            return None
        
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading transcript: {e}")
            return None
    
    def get_full_text(self, video_filename: str) -> Optional[str]:
        """
        获取完整文本字符串
        
        Args:
            video_filename: 视频文件名
            
        Returns:
            完整文本字符串，如果文件不存在则返回None
        """
        transcript_data = self.load_transcript(video_filename)
        
        if transcript_data is None:
            return None
        
        # 从转录数据中提取完整文本
        full_text = transcript_data.get('text', '')
        return full_text.strip() if full_text else None
    
    def transcript_exists(self, video_filename: str) -> bool:
        """
        检查转录文件是否存在
        
        Args:
            video_filename: 视频文件名
            
        Returns:
            如果文件存在返回True，否则返回False
        """
        transcript_path = self._get_transcript_path(video_filename)
        return transcript_path.exists()

