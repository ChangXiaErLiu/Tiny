import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream('POST', 'http://127.0.0.1:8001/api/v1/chat/stream', json={'message': '南宁明天天气怎么样'}) as r:
            print(f"Status: {r.status_code}")
            async for line in r.aiter_lines():
                print(line)

asyncio.run(test())