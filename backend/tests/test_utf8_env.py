import subprocess
import sys
import json
import os

# Set UTF-8 environment
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'

proc = subprocess.Popen(
    [sys.executable, '-c', '''
import json
import sys
data = json.loads(sys.stdin.read())
city = data.get("city", "unknown")
result = {"data": {"city": city, "temp": "25"}, "success": True}
print(json.dumps(result, ensure_ascii=False))
'''],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env
)

stdout, stderr = proc.communicate(input=json.dumps({"city": "南宁", "days": 3}).encode('utf-8'))
print(f"Return code: {proc.returncode}")
print(f"Stdout hex: {stdout[:200].hex()}")
print(f"Stdout decoded: {stdout.decode('utf-8')}")