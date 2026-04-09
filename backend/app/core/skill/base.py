"""Declarative Skill base classes and protocols."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import json
import re


@dataclass
class SkillManifest:
    """Skill metadata definition from SKILL.md"""
    name: str
    version: str
    description: str
    use_cases: List[str] = field(default_factory=list)
    usage_guide: str = ""
    precautions: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    reference_files: Dict[str, str] = field(default_factory=dict)
    script_path: str = ""
    timeout: int = 10000
    retry: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "use_cases": self.use_cases,
            "usage_guide": self.usage_guide,
            "precautions": self.precautions,
            "parameters": self.parameters,
            "reference_files": self.reference_files,
            "script_path": self.script_path,
            "timeout": self.timeout,
            "retry": self.retry
        }


@dataclass 
class SkillContext:
    """Context passed to skill during execution."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_param(self, key: str, default: Any = None) -> Any:
        return self.parameters.get(key, default)
    
    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)


@dataclass
class SkillResult:
    """Result returned by skill execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    skill_name: str = ""
    raw_output: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "skill_name": self.skill_name,
            "raw_output": self.raw_output
        }


class SkillDocument:
    """Represents a complete declarative skill with SKILL.md, script, and references."""
    
    def __init__(self, manifest: SkillManifest, script_content: str, reference_contents: Dict[str, str]):
        self.manifest = manifest
        self.script_content = script_content
        self.reference_contents = reference_contents
    
    def get_prompt_for_llm(self) -> str:
        """Generate a comprehensive prompt that describes this skill to an LLM."""
        prompt_parts = [
            f"# Skill: {self.manifest.name}",
            f"## Version: {self.manifest.version}",
            f"## Description",
            self.manifest.description,
            "",
            "## Use Cases",
        ]
        
        for use_case in self.manifest.use_cases:
            prompt_parts.append(f"- {use_case}")
        
        prompt_parts.extend([
            "",
            "## Usage Guide",
            self.manifest.usage_guide,
            "",
            "## Parameters",
        ])
        
        for param_name, param_info in self.manifest.parameters.items():
            required = "Required" if param_info.get("required") else "Optional"
            prompt_parts.append(f"- {param_name} ({required}): {param_info.get('description', '')}")
        
        if self.manifest.precautions:
            prompt_parts.extend(["", "## Precautions"])
            for precaution in self.manifest.precautions:
                prompt_parts.append(f"- {precaution}")
        
        if self.reference_contents:
            prompt_parts.extend(["", "## Reference Materials"])
            for ref_name, ref_content in self.reference_contents.items():
                prompt_parts.append(f"\n### {ref_name}\n{ref_content}")
        
        prompt_parts.extend([
            "",
            "## Execution Script",
            "```python",
            self.script_content,
            "```"
        ])
        
        return "\n".join(prompt_parts)
