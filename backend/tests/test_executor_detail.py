import sys
import os
sys.path.insert(0, r'C:\Users\97247\Desktop\hobbit\backend')

import asyncio
import json
import tempfile
from pathlib import Path

async def test_executor():
    from app.core.skill.executor import ScriptExecutor
    from app.core.skill.base import SkillContext

    executor = ScriptExecutor(timeout=10000)

    script_content = '''
import json
import sys

data = json.loads(sys.stdin.read())
print(json.dumps({"data": {"city": data.get("city", "unknown"), "temp": "25"}, "success": True}))
'''

    context = SkillContext(parameters={"city": "南宁", "days": 3})

    print("Testing executor with simple script...")
    result = await executor.execute(script_content, context)
    print(f"Result success: {result.success}")
    print(f"Result error: {result.error}")
    print(f"Result data: {result.data}")
    print(f"Result execution_time_ms: {result.execution_time_ms}")
    print()

    print("Testing executor with weather_query script from registry...")
    from app.core.skill.registry import SkillRegistry
    registry = SkillRegistry()
    if not registry.list_all():
        from app.main import register_skills_from_filesystem
        register_skills_from_filesystem(registry)

    skill_doc = registry.get("weather_query")
    if skill_doc:
        print(f"Found weather_query skill, script length: {len(skill_doc.script_content)}")
        result2 = await executor.execute(
            skill_doc.script_content,
            context,
            reference_contents=skill_doc.reference_contents
        )
        print(f"Result2 success: {result2.success}")
        print(f"Result2 error: {result2.error}")
        print(f"Result2 data: {result2.data}")
        print(f"Result2 execution_time_ms: {result2.execution_time_ms}")
    else:
        print("weather_query skill not found in registry!")

asyncio.run(test_executor())