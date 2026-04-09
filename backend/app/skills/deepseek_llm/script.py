"""DeepSeek LLM Skill - Script

This script generates natural language responses using DeepSeek LLM.
Input: JSON with 'prompt', optional 'system_prompt', 'temperature', 'max_tokens'
Output: JSON with generated content
"""
import json
import sys
import httpx
import os
from typing import Dict, Any, Optional

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
TIMEOUT = 60.0


MOCK_RESPONSES = {
    "weather": "【模拟AI回复】根据查询到的天气数据，我已经为您整理好了天气预报信息。具体的天气情况和出行建议已在上面的技能结果中详细列出。",
    "travel": "【模拟AI回复】感谢您的旅游规划需求！我已经根据您提供的信息生成了详细的旅游计划。上方的行程安排包含了每日的活动建议、餐饮推荐和实用贴士，希望能为您的旅行提供帮助。祝您旅途愉快！",
    "default": "【模拟AI回复】您好！我已经收到了您的请求。虽然当前使用的是模拟数据，但框架已经完整搭建好了。在配置真实的 API 密钥后，我将为您提供更准确、更智能的服务。请问还有什么可以帮您的吗？"
}


def get_mock_response(prompt: str, system_prompt: str = "") -> Dict[str, Any]:
    """Return mock response when API key is not configured."""
    prompt_lower = prompt.lower()

    if "天气" in prompt:
        mock_content = MOCK_RESPONSES["weather"]
    elif "旅游" in prompt or "行程" in prompt or "计划" in prompt:
        mock_content = MOCK_RESPONSES["travel"]
    else:
        mock_content = MOCK_RESPONSES["default"]

    return {
        "content": mock_content,
        "usage": {
            "prompt_tokens": len(prompt) // 4,
            "completion_tokens": len(mock_content) // 4,
            "total_tokens": (len(prompt) + len(mock_content)) // 4
        },
        "model": "mock-model"
    }


async def call_deepseek_api(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """Call DeepSeek API to generate response."""
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
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

            return get_mock_response(prompt, system_prompt)

    except Exception as e:
        return get_mock_response(prompt, system_prompt)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        return

    prompt = input_data.get("prompt")
    system_prompt = input_data.get("system_prompt", "")
    temperature = input_data.get("temperature", 0.7)
    max_tokens = input_data.get("max_tokens", 2000)

    if not prompt:
        print(json.dumps({"error": "Prompt parameter is required"}))
        return

    import asyncio
    result = asyncio.run(call_deepseek_api(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    ))

    output = {
        "data": result,
        "success": True
    }

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
