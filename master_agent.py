import json
from typing import Dict, Any, Optional, List, Union, Iterator
from llm_conversation import LLMConversation
from transcript_storage import TranscriptStorage


class MasterAgent:
    """
    百变大师模块，根据用户学习内容动态生成个性化AI学习导师
    """
    def __init__(self):
        """初始化百变大师"""
        self.llm = LLMConversation(temperature=0.8)  # 更高的temperature让对话更生动
        self.transcript_storage = TranscriptStorage()
        self.master_identity = None
        self.master_context = None
    
    def generate_master_identity(self, summary: str) -> Dict[str, Any]:
        """
        根据摘要生成大师身份提示词
        
        Args:
            summary: 视频摘要文本
            
        Returns:
            包含identity和title的字典
        """
        prompt = f"""根据以下视频摘要，为这个学习内容生成一个合适的"大师"身份。

要求：
1. 根据内容领域选择合适的大师身份（如历史学家、科学家、艺术家等）
2. 给大师一个响亮的称号或名号（如"博古通今"、"融会贯通"等）
3. 大师应该具备该领域的专业知识和教学能力
4. 大师的性格应该幽默风趣，善于引导思考
5. 重要要求：请使用简体中文输出，不要使用繁体中文

输出格式必须为 JSON：
{{
    "identity": "大师身份描述，如：资深历史学家",
    "title": "大师称号，如：博古通今",
    "full_name": "完整称呼，如：资深历史学家·博古通今"
}}

视频摘要：
{summary[:1000]}
"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的角色设计专家，擅长根据内容特点设计合适的教学角色。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.llm.send_message(messages, max_tokens=500)
            
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
            self.master_identity = result
            return result
        except Exception as e:
            print(f"Error generating master identity: {e}")
            # 返回默认身份
            return {
                "identity": "知识导师",
                "title": "博学多才",
                "full_name": "知识导师·博学多才"
            }
    
    def create_master_context(self, summary: str, quiz_results: Optional[Dict[str, Any]] = None) -> str:
        """
        构建大师对话上下文
        
        Args:
            summary: 视频摘要
            quiz_results: 答题结果（可选），包含得分、错题信息等
            
        Returns:
            系统提示词
        """
        identity_info = ""
        if self.master_identity:
            identity_info = f"你现在是{self.master_identity.get('full_name', '知识导师')}。"
        else:
            identity_info = "你是一位知识渊博的学习导师。"
        
        quiz_info = ""
        if quiz_results:
            score = quiz_results.get('score', 0)
            total = quiz_results.get('total', 0)
            wrong_questions = quiz_results.get('wrong_questions', [])
            
            quiz_info = f"""
【用户学习状态】：
用户刚刚完成了学习测试，得分：{score}/{total}分。

"""
            if wrong_questions:
                quiz_info += f"用户答错了以下题目：\n"
                for q in wrong_questions:
                    quiz_info += f"- 第{q.get('id', '?')}题：{q.get('question', '')}\n"
                quiz_info += "请针对这些错题给予针对性的指导。\n"
            else:
                quiz_info += "用户全部答对了，表现优秀！请给予鼓励并可以提出更深层次的问题引导思考。\n"
        else:
            quiz_info = """
【用户学习状态】：
用户还未进行学习测试。建议他先完成测试以获得更好的学习效果。
"""
        
        system_prompt = f"""{identity_info}

【背景信息】：
用户刚学完这个视频，摘要如下：
{summary[:500]}

{quiz_info}

请用大师的口吻，幽默风趣地解答用户的问题。如果用户没做题，可以推荐他去做题。回答要简洁有力，富有启发性。
"""
        
        self.master_context = system_prompt
        return system_prompt
    
    def chat_with_master(self, user_message: str, summary: str, quiz_results: Optional[Dict[str, Any]] = None, conversation_history: Optional[List[Dict[str, Any]]] = None, stream: bool = True) -> Union[str, Iterator[str]]:
        """
        与大师对话
        
        Args:
            user_message: 用户消息
            summary: 视频摘要
            quiz_results: 答题结果（可选）
            conversation_history: 对话历史（可选）
            stream: 是否使用流式响应（默认True，模拟真实对话）
            
        Returns:
            如果stream=False: 大师的完整回复
            如果stream=True: 流式响应迭代器
        """
        # 如果没有生成身份，先生成
        if not self.master_identity:
            self.generate_master_identity(summary)
        
        # 构建系统提示词
        system_prompt = self.create_master_context(summary, quiz_results)
        
        # 构建消息列表
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # 添加对话历史
        if conversation_history:
            for msg in conversation_history:
                messages.append(msg)
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            return self.llm.send_message(messages, max_tokens=1000, stream=stream)
        except Exception as e:
            print(f"Error in master chat: {e}")
            if stream:
                return iter(["抱歉，我现在有些困惑，请稍后再试。"])
            else:
                return "抱歉，我现在有些困惑，请稍后再试。"
    
    def get_master_info(self) -> Optional[Dict[str, Any]]:
        """
        获取大师信息
        
        Returns:
            大师身份信息
        """
        return self.master_identity
