"""Skill management endpoints for declarative skills."""
from fastapi import APIRouter, HTTPException
from typing import List
from ...schemas.response import SkillListResponse, SkillInvokeResponse, SkillManifestResponse
from ...schemas.request import SkillInvokeRequest
from ...core.skill.registry import SkillRegistry
from ...core.agent.skill_dispatcher import SkillDispatcher
import time

router = APIRouter()


def get_registry() -> SkillRegistry:
    """Get skill registry instance."""
    return SkillRegistry()


def get_dispatcher() -> SkillDispatcher:
    """Get skill dispatcher instance."""
    return SkillDispatcher(get_registry())


@router.get("", response_model=SkillListResponse)
async def list_skills():
    """List all registered declarative skills."""
    registry = get_registry()
    manifests = registry.list_all()

    return SkillListResponse(
        code=200,
        message="success",
        skills=[
            SkillManifestResponse(
                name=m.name,
                version=m.version,
                description=m.description,
                parameters=m.parameters,
                timeout=m.timeout,
                retry=m.retry
            )
            for m in manifests
        ]
    )


@router.get("/{skill_name}")
async def get_skill(skill_name: str):
    """Get details of a specific skill including SKILL.md content."""
    registry = get_registry()
    skill_doc = registry.get(skill_name)

    if not skill_doc:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    manifest = skill_doc.manifest

    skill_prompt = registry.get_skill_prompt(skill_name)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "use_cases": manifest.use_cases,
            "usage_guide": manifest.usage_guide,
            "precautions": manifest.precautions,
            "parameters": manifest.parameters,
            "script_path": manifest.script_path,
            "reference_files": list(skill_doc.reference_contents.keys()),
            "timeout": manifest.timeout,
            "retry": manifest.retry,
            "skill_prompt": skill_prompt
        }
    }


@router.post("/{skill_name}/invoke", response_model=SkillInvokeResponse)
async def invoke_skill(skill_name: str, request: SkillInvokeRequest):
    """Manually invoke a declarative skill."""
    dispatcher = get_dispatcher()
    start_time = time.time()

    result = await dispatcher.dispatch_single(skill_name, request.parameters)

    return SkillInvokeResponse(
        code=200 if result.success else 400,
        message="success" if result.success else "error",
        skill=skill_name,
        status="success" if result.success else "failed",
        result=result.data,
        execution_time_ms=(time.time() - start_time) * 1000 + result.execution_time_ms
    )


@router.get("/{skill_name}/script")
async def get_skill_script(skill_name: str):
    """Get the script content of a skill."""
    registry = get_registry()
    skill_doc = registry.get(skill_name)

    if not skill_doc:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    return {
        "code": 200,
        "message": "success",
        "data": {
            "name": skill_name,
            "script_content": skill_doc.script_content,
            "reference_contents": skill_doc.reference_contents
        }
    }
