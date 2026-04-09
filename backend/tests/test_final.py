import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream('POST', 'http://127.0.0.1:8001/api/v1/chat/stream', json={'message': '南宁明天天气怎么样'}) as r:
            print(f"Status: {r.status_code}")
            async for line in r.aiter_lines():
                if line.startswith('data: '):
                    data = line[6:]
                    if '"content"' in data and '抱歉' not in data:
                        print(f"Content part: {data}")
                    if '"done"' in data or 'done' in data:
                        print("Stream complete!")

asyncio.run(test())