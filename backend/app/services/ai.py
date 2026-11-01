"""
火山方舟AI服务封装
"""
import requests
import logging
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI服务类，封装火山方舟API调用"""
    
    def __init__(self):
        self.api_key = settings.VOLCENGINE_ARK_API_KEY
        self.base_url = settings.VOLCENGINE_ARK_BASE_URL
        self.model = settings.VOLCENGINE_ARK_MODEL
        self.timeout = settings.VOLCENGINE_ARK_TIMEOUT
        
        if not self.api_key:
            logger.warning("VOLCENGINE_ARK_API_KEY未配置，AI功能将不可用")
    
    def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        thinking_disabled: bool = True
    ) -> Optional[str]:
        """
        发送请求到火山方舟API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，控制随机性（0-1）
            max_tokens: 最大生成token数
            thinking_disabled: 是否关闭深度思考
        
        Returns:
            AI回复内容，失败返回None
        """
        if not self.api_key:
            logger.error("API Key未配置")
            return None
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # 关闭深度思考
        if thinking_disabled:
            payload["thinking"] = {"type": "disabled"}
        
        try:
            logger.info(f"发送AI请求: {len(messages)}条消息")
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"AI响应成功，长度: {len(content)}")
                return content
            else:
                logger.error(f"AI响应格式异常: {result}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("AI请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"AI请求失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"AI请求异常: {str(e)}")
            return None
    
    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        对话接口
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            conversation_history: 对话历史，格式为 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大生成token数
        
        Returns:
            AI回复内容
        """
        messages = []
        
        # 添加系统提示词
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return self._make_request(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def chat_with_context(
        self,
        user_message: str,
        context: Dict,
        system_prompt_template: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        带上下文的对话接口
        
        Args:
            user_message: 用户消息
            context: 上下文信息（如用户水平、学习模块等）
            system_prompt_template: 系统提示词模板，可以使用 {key} 格式引用context中的值
            temperature: 温度参数
            max_tokens: 最大生成token数
        
        Returns:
            AI回复内容
        """
        # 格式化系统提示词
        system_prompt = system_prompt_template.format(**context)
        
        return self.chat(
            user_message=user_message,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )


# 创建全局AI服务实例
ai_service = AIService()
