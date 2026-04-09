"""Skill dispatcher with declarative skill support."""
from typing import List, Dict, Any, Optional
from ..skill.registry import SkillRegistry
from ..skill.executor import ScriptExecutor
from ..skill.base import SkillContext, SkillResult, SkillDocument
from ..tracing import log_step
import logging
import time
import json

logger = logging.getLogger(__name__)


class SkillDispatcher:
    """Dispatches and coordinates declarative skill execution."""
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.executor = ScriptExecutor()
        self.execution_history: List[Dict[str, Any]] = []
    
    async def dispatch_single(
        self,
        skill_name: str,
        parameters: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> SkillResult:
        """Dispatch execution of a single declarative skill."""
        start_time = time.time()
        
        log_step(f"[{skill_name}] Loading skill manifest")
        skill_doc = self.registry.get(skill_name)
        if not skill_doc:
            logger.error(f"Skill not found: {skill_name}")
            return SkillResult(
                success=False,
                error=f"Skill '{skill_name}' not found",
                skill_name=skill_name
            )
        
        context = SkillContext(
            parameters=parameters,
            metadata={"session_id": session_id} if session_id else {}
        )
        
        log_step(f"[{skill_name}] Executing script", {
            'timeout': skill_doc.manifest.timeout,
            'retry': skill_doc.manifest.retry,
            'params': parameters
        })
        
        result = await self.executor.execute(
            script_content=skill_doc.script_content,
            context=context,
            reference_contents=skill_doc.reference_contents,
            timeout=skill_doc.manifest.timeout,
            retry_count=skill_doc.manifest.retry
        )
        
        result.skill_name = skill_name
        result.execution_time_ms = (time.time() - start_time) * 1000
        
        log_step(f"[{skill_name}] Execution completed", {
            'success': result.success,
            'execution_time_ms': result.execution_time_ms,
            'error': result.error,
            'raw_output': result.raw_output[:500] if result.raw_output else None
        })
        
        self.execution_history.append({
            "skill_name": skill_name,
            "status": "success" if result.success else "failed",
            "duration_ms": result.execution_time_ms,
            "timestamp": start_time
        })
        
        return result
    
    async def dispatch_multiple(
        self,
        skill_requests: List[Dict[str, Any]],
        session_id: Optional[str] = None,
        parallel: bool = True
    ) -> Dict[str, SkillResult]:
        """Dispatch multiple skills."""
        if parallel:
            import asyncio
            tasks = {
                req["skill"]: self.dispatch_single(
                    req["skill"],
                    req.get("parameters", {}),
                    session_id
                )
                for req in skill_requests
            }
            
            results = {}
            completed = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            for (skill_name, _), result in zip(tasks.items(), completed):
                if isinstance(result, Exception):
                    results[skill_name] = SkillResult(
                        success=False,
                        error=str(result),
                        skill_name=skill_name
                    )
                else:
                    results[skill_name] = result
            
            return results
        else:
            results = {}
            for req in skill_requests:
                result = await self.dispatch_single(
                    req["skill"],
                    req.get("parameters", {}),
                    session_id
                )
                results[req["skill"]] = result
            return results
    
    async def dispatch_with_dependencies(
        self,
        skill_chain: List[List[str]],
        base_params: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, SkillResult]:
        """Dispatch skills in stages where each stage can use previous results."""
        all_results: Dict[str, SkillResult] = {}
        accumulated_params = base_params.copy()
        
        for stage_idx, stage_skills in enumerate(skill_chain):
            logger.info(f"Executing stage {stage_idx + 1}/{len(skill_chain)}: {stage_skills}")
            
            stage_results = await self.dispatch_multiple(
                [{"skill": s, "parameters": accumulated_params} for s in stage_skills],
                session_id=session_id,
                parallel=True
            )
            
            for skill_name, result in stage_results.items():
                all_results[skill_name] = result
                
                if result.success and result.data:
                    accumulated_params[skill_name] = result.data
            
            failed_count = sum(
                1 for r in stage_results.values()
                if not r.success
            )
            
            if failed_count > 0:
                logger.warning(f"Stage {stage_idx + 1} had {failed_count} failures")
        
        return all_results
    
    def get_skill_prompt(self, skill_name: str) -> Optional[str]:
        """Get the full skill prompt (SKILL.md content) for LLM context."""
        return self.registry.get_skill_prompt(skill_name)
    
    def get_all_skill_prompts(self) -> Dict[str, str]:
        """Get prompts for all registered skills."""
        prompts = {}
        for manifest in self.registry.list_all():
            prompt = self.registry.get_skill_prompt(manifest.name)
            if prompt:
                prompts[manifest.name] = prompt
        return prompts
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution history."""
        return self.execution_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
