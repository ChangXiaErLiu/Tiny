import httpx
import json

r = httpx.post(
    'http://127.0.0.1:8002/api/v1/chat/stream',
    json={'message': '南宁明天天气怎么样'},
    timeout=30
)
print(f"Status: {r.status_code}")
print(f"Response text: {r.text}")