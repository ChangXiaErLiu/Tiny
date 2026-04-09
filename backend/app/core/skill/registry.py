"""Skill loader - parses SKILL.md files and loads skill documents."""
import re
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, List, Any
from .base import SkillManifest, SkillDocument
import logging

logger = logging.getLogger(__name__)


class SkillLoader:
    """Loads and parses declarative skills from filesystem."""
    
    def __init__(self, skills_base_path: str):
        self.skills_base_path = Path(skills_base_path)
    
    def load_skill(self, skill_name: str) -> Optional[SkillDocument]:
        """Load a complete skill document by name."""
        skill_path = self.skills_base_path / skill_name
        
        if not skill_path.exists():
            logger.error(f"Skill path does not exist: {skill_path}")
            return None
        
        manifest = self._parse_skill_md(skill_path / "SKILL.md")
        if not manifest:
            logger.error(f"Failed to parse SKILL.md for skill: {skill_name}")
            return None
        
        manifest.name = skill_name
        manifest.script_path = str(skill_path / "script.py")
        
        script_content = self._load_script(skill_path / "script.py")
        reference_contents = self._load_references(skill_path / "reference")
        
        return SkillDocument(
            manifest=manifest,
            script_content=script_content,
            reference_contents=reference_contents
        )
    
    def load_all_skills(self) -> List[SkillDocument]:
        """Load all skills from the skills directory."""
        skills = []
        
        if not self.skills_base_path.exists():
            logger.warning(f"Skills base path does not exist: {self.skills_base_path}")
            return skills
        
        for skill_dir in self.skills_base_path.iterdir():
            if skill_dir.is_dir():
                skill_doc = self.load_skill(skill_dir.name)
                if skill_doc:
                    skills.append(skill_doc)
        
        return skills
    
    def _parse_skill_md(self, skill_md_path: Path) -> Optional[SkillManifest]:
        """Parse SKILL.md file into SkillManifest."""
        if not skill_md_path.exists():
            logger.error(f"SKILL.md not found: {skill_md_path}")
            return None
        
        content = skill_md_path.read_text(encoding='utf-8')
        
        manifest = SkillManifest(
            name="",
            version="1.0.0",
            description=""
        )
        
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            section_match = re.match(r'^##\s+(.+)$', line)
            if section_match:
                if current_section and section_content:
                    self._process_section(manifest, current_section, section_content)
                
                current_section = section_match.group(1).strip().lower()
                section_content = []
            else:
                if current_section:
                    section_content.append(line)
        
        if current_section and section_content:
            self._process_section(manifest, current_section, section_content)
        
        if not manifest.description:
            first_heading = content.split('\n')[0] if content else ""
            manifest.description = first_heading.replace('#', '').strip()
        
        return manifest
    
    def _process_section(self, manifest: SkillManifest, section: str, lines: List[str]):
        """Process a section of SKILL.md."""
        content = '\n'.join(lines).strip()
        
        if 'version' in section:
            version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', content)
            if version_match:
                manifest.version = version_match.group(1)
        
        elif 'use case' in section:
            manifest.use_cases = [
                line.strip().lstrip('-').strip()
                for line in lines
                if line.strip().startswith('-')
            ]
        
        elif 'usage guide' in section or 'how to use' in section:
            manifest.usage_guide = content
        
        elif 'precaution' in section or 'note' in section or 'attention' in section:
            manifest.precautions = [
                line.strip().lstrip('-').strip()
                for line in lines
                if line.strip().startswith('-')
            ]
        
        elif 'parameter' in section:
            manifest.parameters = self._parse_parameters(content)
        
        elif 'reference' in section:
            pass
    
    def _parse_parameters(self, content: str) -> Dict[str, Any]:
        """Parse parameters section into structured format."""
        params = {}
        
        param_patterns = [
            r'-?\s*(\w+)[\s:]+(.*?)(?=\n\s*-|\n\n|\Z)',
        ]
        
        lines = content.split('\n')
        current_param = None
        current_desc = []
        
        for line in lines:
            param_match = re.match(r'^\s*[-*]?\s*(\w+)\s*\((\w+)\)(?:\s*[:\-]?\s*(.*))?$', line)
            if param_match:
                if current_param:
                    params[current_param]['description'] = ' '.join(current_desc).strip()
                
                param_name = param_match.group(1)
                param_type = param_match.group(2)
                param_desc = param_match.group(3) or ""
                
                params[param_name] = {
                    'type': param_type,
                    'description': param_desc.strip(),
                    'required': 'required' in param_desc.lower() or '必填' in param_desc
                }
                current_param = param_name
                current_desc = [param_desc]
            elif line.strip() and current_param:
                if line.strip().startswith('-'):
                    params[current_param]['description'] = ' '.join(current_desc).strip()
                    current_param = None
                    current_desc = []
                else:
                    current_desc.append(line.strip())
        
        if current_param:
            params[current_param]['description'] = ' '.join(current_desc).strip()
        
        return params
    
    def _load_script(self, script_path: Path) -> str:
        """Load the script file content."""
        if not script_path.exists():
            logger.warning(f"Script file not found: {script_path}")
            return ""
        
        return script_path.read_text(encoding='utf-8')
    
    def _load_references(self, reference_path: Path) -> Dict[str, str]:
        """Load all reference files."""
        references = {}
        
        if not reference_path.exists():
            return references
        
        for ref_file in reference_path.iterdir():
            if ref_file.is_file():
                references[ref_file.name] = ref_file.read_text(encoding='utf-8')
        
        return references


class SkillRegistry:
    """Registry for managing loaded skills."""
    
    _instance: Optional['SkillRegistry'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._skills: Dict[str, SkillDocument] = {}
            cls._instance._loader: Optional[SkillLoader] = None
        return cls._instance
    
    def initialize(self, skills_base_path: str):
        """Initialize the registry with a skill loader."""
        self._loader = SkillLoader(skills_base_path)
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all skills from the base path."""
        if not self._loader:
            logger.error("SkillLoader not initialized")
            return
        
        skills = self._loader.load_all_skills()
        for skill in skills:
            self._skills[skill.manifest.name] = skill
            logger.info(f"Loaded skill: {skill.manifest.name} v{skill.manifest.version}")
    
    def get(self, name: str) -> Optional[SkillDocument]:
        """Get a skill document by name."""
        return self._skills.get(name)
    
    def list_all(self) -> List[SkillManifest]:
        """List all registered skill manifests."""
        return [skill.manifest for skill in self._skills.values()]
    
    def exists(self, name: str) -> bool:
        """Check if a skill is registered."""
        return name in self._skills
    
    def get_skill_prompt(self, name: str) -> Optional[str]:
        """Get the LLM prompt for a skill."""
        skill = self.get(name)
        if skill:
            return skill.get_prompt_for_llm()
        return None
