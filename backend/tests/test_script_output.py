import subprocess
import sys
import json

proc = subprocess.Popen(
    [sys.executable, '-m', 'app.skills.weather_query.script'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=r'C:\Users\97247\Desktop\hobbit\backend'
)

stdout, stderr = proc.communicate(input=json.dumps({"city": "南宁", "days": 3}).encode('utf-8'))
print(f"Return code: {proc.returncode}")
print(f"Stdout bytes length: {len(stdout)}")
print(f"Stderr bytes length: {len(stderr)}")
print(f"Stdout hex: {stdout[:100].hex()}")
print(f"Stderr: {stderr.decode('utf-8', errors='replace')}")
print(f"Stdout decoded: {stdout.decode('utf-8', errors='replace')}")