import sys
sys.path.insert(0, r'C:\Users\97247\Desktop\hobbit\backend')

with open(r'C:\Users\97247\Desktop\hobbit\backend\app\skills\weather_query\script.py', 'rb') as f:
    content = f.read()

print("First 200 bytes hex:")
print(content[:200].hex())
print()

# Try to decode as different encodings
try:
    print("As UTF-8:", content[:200].decode('utf-8')[:100])
except Exception as e:
    print(f"UTF-8 failed: {e}")

try:
    print("As GBK:", content[:200].decode('gbk')[:100])
except Exception as e:
    print(f"GBK failed: {e}")