import sys
import os
sys.path.insert(0, r'C:\Users\97247\Desktop\hobbit\backend')

import asyncio
import json
from app.core.skill.registry import SkillRegistry
from app.core.agent.skill_dispatcher import SkillDispatcher
from app.main import register_skills_from_filesystem

async def test():
    registry = SkillRegistry()
    register_skills_from_filesystem(registry)

    print(f"Registry has {len(registry.list_all())} skills")
    for manifest in registry.list_all():
        print(f"  - {manifest.name}: {manifest.timeout}ms timeout, {manifest.retry} retries")

    dispatcher = SkillDispatcher(registry)

    print("\nDispatching weather_query skill...")
    result = await dispatcher.dispatch_single(
        "weather_query",
        {"city": "南宁", "days": 3}
    )

    print(f"\nResult:")
    print(f"  success: {result.success}")
    print(f"  error: {result.error}")
    print(f"  data: {result.data}")
    print(f"  execution_time_ms: {result.execution_time_ms}")

asyncio.run(test())