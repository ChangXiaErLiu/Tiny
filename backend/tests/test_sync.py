import httpx
import json

r = httpx.post(
    'http://127.0.0.1:8001/api/v1/chat/stream',
    json={'message': '南宁明天天气怎么样'},
    timeout=30
)
print(f"Status: {r.status_code}")
print(f"Content type: {r.headers.get('content-type')}")
print(f"Response text (first 1000 chars): {r.text[:1000]}")