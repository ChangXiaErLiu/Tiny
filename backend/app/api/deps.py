"""Dependency injection for API routes."""
from typing import Optional
from ..core.skill.registry import SkillRegistry
from ..core.agent.skill_dispatcher import SkillDispatcher


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    return SkillRegistry()


def get_skill_dispatcher() -> SkillDispatcher:
    """Get the global skill dispatcher instance."""
    return SkillDispatcher()
