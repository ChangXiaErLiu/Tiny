"""DeepSeek LLM provider with streaming support."""
import httpx
import json
from typing import AsyncIterator, Dict, Any, Optional, List
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class LLMProvider:
    """Provider for DeepSeek LLM API with streaming."""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.timeout = settings.llm_timeout / 1000
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate a non-streaming response."""
        if not self.api_key:
            return self._get_mock_response(prompt)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "usage": data.get("usage", {}),
                        "model": data.get("model", "deepseek-chat")
                    }
                
                return self._get_mock_response(prompt)
                
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._get_mock_response(prompt)
    
    async def stream_generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[Dict[str, Any]]:
        """Generate a streaming response."""
        if not self.api_key:
            async for chunk in self._mock_stream_response(prompt):
                yield chunk
            return
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "stream": True
                    }
                ) as response:
                    
                    if response.status_code != 200:
                        logger.error(f"LLM stream error: {response.status_code}")
                        async for chunk in self._mock_stream_response(prompt):
                            yield chunk
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                yield {"type": "done", "content": ""}
                                return
                            
                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                
                                if content:
                                    yield {"type": "content", "content": content}
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"LLM stream error: {e}")
            async for chunk in self._mock_stream_response(prompt):
                yield chunk
    
    async def health_check(self) -> bool:
        """Check if LLM API is available."""
        if not self.api_key:
            return True
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": "hi"}],
                        "max_tokens": 10
                    }
                )
                return response.status_code == 200
        except:
            return False
    
    def _get_mock_response(self, prompt: str) -> Dict[str, Any]:
        """Get mock LLM response."""
        return {
            "content": f"【模拟响应】收到您的请求: {prompt[:50]}...\n\n这是一个模拟的AI响应。在配置真实的DeepSeek API密钥后，将返回真实的AI生成内容。",
            "usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150},
            "model": "mock-model"
        }
    
    async def _mock_stream_response(self, prompt: str) -> AsyncIterator[Dict[str, Any]]:
        """Generate mock streaming response."""
        mock_chunks = [
            "【模拟AI响应】\n\n",
            "根据您的请求，",
            "我已经分析了相关数据。\n\n",
            "以下是为您生成的回复内容：\n\n",
            "这是一个流式输出的演示。\n\n",
            "在实际配置API密钥后，",
            "这里会显示真实的",
            "DeepSeek AI生成内容。"
        ]
        
        for chunk in mock_chunks:
            yield {"type": "content", "content": chunk}
            await asyncio.sleep(0.1)
        
        yield {"type": "done", "content": ""}
    
    async def build_travel_prompt(
        self, 
        city: str, 
        days: int, 
        weather_data: Optional[Dict[str, Any]] = None,
        attractions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build a prompt for travel planning."""
        prompt = f"请为我去{city}旅游{days}天制定一份详细的旅游计划。\n\n"
        
        if weather_data:
            prompt += "【天气信息】\n"
            daily = weather_data.get("daily", [])
            for day in daily:
                prompt += f"- {day.get('date')}: {day.get('weather')}, "
                prompt += f"气温{day.get('tempMin')}-{day.get('tempMax')}℃\n"
            prompt += "\n"
        
        if attractions:
            prompt += "【推荐景点】\n"
            for spot in attractions[:5]:
                prompt += f"- {spot.get('name')}: {spot.get('description', '暂无描述')}\n"
            prompt += "\n"
        
        prompt += "请根据天气情况合理安排行程，给出每天的具体安排，包括：\n"
        prompt += "1. 上午、下午、晚上的活动\n"
        prompt += "2. 用餐建议\n"
        prompt += "3. 注意事项（如带伞、防晒等）\n\n"
        prompt += "请用简洁明了的格式回复。"
        
        return prompt


import asyncio
