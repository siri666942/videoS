import json
from typing import Dict, Any, Optional
from llm_conversation import LLMConversation
from transcript_storage import TranscriptStorage


class ContentGenerator:
    """
    内容生成模块，用于生成标题、概要、思维导图和习题
    """
    def __init__(self):
        """初始化内容生成器"""
        self.llm = LLMConversation()
        self.transcript_storage = TranscriptStorage()
    
    def generate_title_and_summary(self, transcript_text: str) -> Dict[str, Any]:
        """
        合并功能一+二：生成去标题党的真实标题和文字概要
        
        Args:
            transcript_text: 视频完整转录文本
            
        Returns:
            包含real_title和summary的字典
        """
        prompt = f"""你是一个知识视频分析专家。请阅读以下视频文本，完成两个任务：

1. 拟定一个去标题党的、能概括核心知识点的真实标题。
2. 生成一份结构清晰的文字概要（约300字）。

重要要求：请使用简体中文输出，不要使用繁体中文。

输出格式必须为 JSON，不要包含其他废话：

{{
    "real_title": "...",
    "summary": "..."
}}

视频文本：
{transcript_text[:8000]}  # 限制长度避免token过多
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的知识视频分析专家，擅长提炼核心内容和去除标题党。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.llm.send_message(messages, max_tokens=1000)
            
            # 解析JSON响应
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return {
                "real_title": result.get("real_title", ""),
                "summary": result.get("summary", "")
            }
        except Exception as e:
            print(f"Error generating title and summary: {e}")
            return {
                "real_title": "视频标题",
                "summary": "视频概要生成失败，请稍后重试。"
            }
    
    def generate_mindmap(self, transcript_text: str) -> str:
        """
        功能三：生成思维导图（Markdown格式）
        
        Args:
            transcript_text: 视频完整转录文本
            
        Returns:
            Markdown格式的思维导图文本
        """
        prompt = f"""请根据视频文本生成一个思维导图。

必须直接输出 Markdown 格式的列表，不要包含其他废话。
重要要求：请使用简体中文输出，不要使用繁体中文。

格式示例：
# 核心主题

## 分支1
- 知识点A
- 知识点B

## 分支2
- 知识点C
- 知识点D

视频文本：
{transcript_text[:8000]}  # 限制长度避免token过多
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的思维导图生成专家，擅长将复杂内容组织成清晰的层次结构。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.llm.send_message(messages, max_tokens=2000)
            
            # 清理响应，确保是纯Markdown
            response = response.strip()
            if response.startswith("```markdown"):
                response = response[11:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return response
        except Exception as e:
            print(f"Error generating mindmap: {e}")
            return "# 思维导图\n\n生成失败，请稍后重试。"
    
    def generate_quiz(self, transcript_text: str) -> Dict[str, Any]:
        """
        功能五：生成游戏化习题库（3-5道单选题）
        
        Args:
            transcript_text: 视频完整转录文本
            
        Returns:
            包含questions列表的字典
        """
        prompt = f"""请根据视频文本生成3-5道单选题，用于检验学习者的理解程度。

要求：
1. 每道题有4个选项
2. 包含正确答案和详细解析
3. 设定难度系数（easy/medium/hard）
4. 题目要有针对性，能真正检验对核心知识点的理解
5. 重要要求：请使用简体中文输出，不要使用繁体中文

输出格式必须为 JSON，不要包含其他废话：

{{
    "questions": [
        {{
            "id": 1,
            "question": "问题内容",
            "options": ["选项A", "选项B", "选项C", "选项D"],
            "correct_answer": 0,
            "explanation": "答案解析",
            "difficulty": "easy"
        }}
    ]
}}

视频文本：
{transcript_text[:8000]}  # 限制长度避免token过多
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的教育内容生成专家，擅长设计能检验真实理解程度的题目。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.llm.send_message(messages, max_tokens=2000)
            
            # 解析JSON响应
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return {
                "questions": []
            }
    
    def generate_all_content(self, video_filename: str) -> Dict[str, Any]:
        """
        并行生成所有内容（在实际实现中，这应该使用asyncio并行调用）
        
        Args:
            video_filename: 视频文件名
            
        Returns:
            包含所有生成内容的字典
        """
        # 获取转录文本
        transcript_text = self.transcript_storage.get_full_text(video_filename)
        
        if not transcript_text:
            return {
                "error": "转录文本不存在，请先上传并处理视频"
            }
        
        # 生成内容（在实际API中应该并行执行）
        title_summary = self.generate_title_and_summary(transcript_text)
        mindmap = self.generate_mindmap(transcript_text)
        quiz = self.generate_quiz(transcript_text)
        
        return {
            "title": title_summary.get("real_title", ""),
            "summary": title_summary.get("summary", ""),
            "mindmap": mindmap,
            "quiz": quiz
        }
