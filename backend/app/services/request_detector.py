"""
请求类型检测器：识别用户请求的类型（作文批改、题目生成等）
"""
import re
from typing import Dict, Optional, Tuple


class RequestDetector:
    """请求类型检测器"""
    
    # 作文批改关键词
    ESSAY_KEYWORDS = [
        "批改", "修改", "改作文", "批改作文", "作文批改",
        "correct", "correction", "essay", "writing", "作文",
        "帮我改", "帮我批改", "帮我修改"
    ]
    
    # 题目生成关键词
    QUESTION_GENERATION_KEYWORDS = [
        "出题", "生成题目", "出", "道题", "题目",
        "generate", "question", "练习", "题目生成",
        "帮我出", "给我出", "生成"
    ]
    
    # 口语题关键词
    SPEAKING_KEYWORDS = [
        "口语", "speaking", "对话", "口语练习"
    ]
    
    # 阅读题关键词
    READING_KEYWORDS = [
        "阅读", "reading", "阅读理解"
    ]
    
    # 写作题关键词
    WRITING_KEYWORDS = [
        "写作", "writing", "作文题"
    ]
    
    # 听力题关键词
    LISTENING_KEYWORDS = [
        "听力", "listening", "听力练习"
    ]
    
    @classmethod
    def detect_request_type(cls, message: str) -> Tuple[str, Optional[Dict]]:
        """
        检测请求类型
        
        Returns:
            (request_type, params)
            request_type: "essay_correction", "question_generation", "general"
            params: 请求参数（如主题、数量等）
        """
        message_lower = message.lower().strip()
        
        # 检测作文批改
        if cls._contains_keywords(message_lower, cls.ESSAY_KEYWORDS):
            return "essay_correction", None
        
        # 检测题目生成
        if cls._contains_keywords(message_lower, cls.QUESTION_GENERATION_KEYWORDS):
            params = cls._extract_question_params(message)
            return "question_generation", params
        
        # 默认：一般对话
        return "general", None
    
    @classmethod
    def _contains_keywords(cls, text: str, keywords: list) -> bool:
        """检查文本是否包含关键词"""
        for keyword in keywords:
            if keyword in text:
                return True
        return False
    
    @classmethod
    def _extract_question_params(cls, message: str) -> Dict:
        """从消息中提取题目生成参数"""
        message_lower = message.lower()
        
        # 提取数量
        count = 5  # 默认5道题
        count_patterns = [
            r'(\d+)\s*道',
            r'(\d+)\s*个',
            r'(\d+)\s*题',
            r'(\d+)\s*questions?'
        ]
        for pattern in count_patterns:
            match = re.search(pattern, message_lower)
            if match:
                count = int(match.group(1))
                break
        
        # 提取主题
        topic = "通用"
        # 检查是否包含"关于"、"主题"等
        topic_patterns = [
            r'关于\s*([^的]+)',
            r'主题[是为：]\s*([^的]+)',
            r'关于\s*([^的]+?)(?:的|题目|题)',
        ]
        for pattern in topic_patterns:
            match = re.search(pattern, message)
            if match:
                topic = match.group(1).strip()
                break
        
        # 提取题目类型
        question_type = "选择题"
        if cls._contains_keywords(message_lower, cls.SPEAKING_KEYWORDS):
            question_type = "口语题"
        elif cls._contains_keywords(message_lower, cls.READING_KEYWORDS):
            question_type = "阅读题"
        elif cls._contains_keywords(message_lower, cls.WRITING_KEYWORDS):
            question_type = "写作题"
        elif cls._contains_keywords(message_lower, cls.LISTENING_KEYWORDS):
            question_type = "听力题"
        elif "选择" in message_lower or "choice" in message_lower:
            question_type = "选择题"
        elif "填空" in message_lower or "fill" in message_lower:
            question_type = "填空题"
        
        return {
            "count": count,
            "topic": topic,
            "question_type": question_type
        }
    
    @classmethod
    def extract_essay_content(cls, message: str) -> Optional[str]:
        """从消息中提取作文内容"""
        # 如果消息很长（超过200字符），可能是直接发送的作文
        if len(message) > 200:
            return message
        
        # 检查是否包含"作文内容："、"以下是我的作文"等标识
        patterns = [
            r'作文[内容：:]\s*(.+)',
            r'以下是我的作文[：:]\s*(.+)',
            r'我的作文[：:]\s*(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
