"""Script executor for running skill scripts."""
import asyncio
import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .base import SkillContext, SkillResult
import time
import logging
import platform

logger = logging.getLogger(__name__)


def _get_event_loop():
    """Get appropriate event loop for subprocess support on Windows."""
    if platform.system() == 'Windows':
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception as e:
            logger.warning(f"Failed to set WindowsSelectorEventLoopPolicy: {e}")
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


class ScriptExecutionError(Exception):
    """Exception raised when script execution fails."""
    pass


class ScriptExecutor:
    """Executes declarative skill scripts."""
    
    def __init__(self, timeout: int = 10000, max_retry: int = 3):
        self.default_timeout = timeout
        self.max_retry = max_retry
    
    async def execute(
        self,
        script_content: str,
        context: SkillContext,
        reference_contents: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
        retry_count: Optional[int] = None
    ) -> SkillResult:
        """Execute a skill script with the given parameters."""
        start_time = time.time()
        timeout = timeout or self.default_timeout
        retry_count = retry_count or self.max_retry
        
        parameters = context.parameters.copy()
        parameters['_context'] = {
            'request_id': context.request_id,
            'metadata': context.metadata
        }
        
        if reference_contents:
            parameters['_references'] = reference_contents
        
        logger.info(f"Script execution started with parameters: {list(parameters.keys())}")
        logger.debug(f"Full parameters: {json.dumps(parameters, default=str)}")
        
        last_error = None
        
        for attempt in range(retry_count):
            try:
                logger.info(f"Executing script (attempt {attempt + 1}/{retry_count})")
                logger.debug(f"Script content length: {len(script_content)} characters")
                
                result = await self._run_script(
                    script_content,
                    parameters,
                    timeout / 1000.0
                )
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                if result['success']:
                    logger.info(f"Script execution successful in {execution_time_ms:.2f}ms")
                    logger.debug(f"Script result data keys: {list(result.get('data', {}).keys()) if isinstance(result.get('data'), dict) else 'non-dict'}")
                    return SkillResult(
                        success=True,
                        data=result.get('data'),
                        raw_output=result.get('raw_output', ''),
                        execution_time_ms=execution_time_ms
                    )
                else:
                    last_error = result.get('error', 'Unknown error')
                    logger.warning(f"Script execution failed: {last_error}")
                    logger.debug(f"Raw output on failure: {result.get('raw_output', '')}")
                    
            except asyncio.TimeoutError:
                last_error = f"Script execution timed out after {timeout}ms"
                logger.warning(f"Script timeout (attempt {attempt + 1}/{retry_count})")
                
            except Exception as e:
                import traceback
                last_error = str(e)
                logger.error(f"Script execution error: {type(e).__name__}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            
            if attempt < retry_count - 1:
                wait_time = min(2 ** attempt, 10)
                logger.info(f"Retrying after {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        return SkillResult(
            success=False,
            error=last_error or "Script execution failed after all retries",
            execution_time_ms=(time.time() - start_time) * 1000
        )
    
    async def _run_script(
        self,
        script_content: str,
        parameters: Dict[str, Any],
        timeout: float
    ) -> Dict[str, Any]:
        """Run the script with parameters via subprocess."""
        loop = _get_event_loop()
        
        input_data = json.dumps(parameters)

        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(script_content)
            script_path = f.name

        def _run_subprocess():
            try:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env
                )
                stdout, stderr = process.communicate(
                    input=input_data.encode('utf-8'),
                    timeout=timeout
                )
                return process.returncode, stdout, stderr
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                return -1, b'', b'Timeout'
            finally:
                Path(script_path).unlink(missing_ok=True)

        try:
            returncode, stdout, stderr = await loop.run_in_executor(
                None, _run_subprocess
            )

            if returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"Script stderr: {error_msg}")
                logger.error(f"Script stdout: {stdout.decode('utf-8') if stdout else ''}")
                return {
                    'success': False,
                    'error': error_msg,
                    'raw_output': stdout.decode('utf-8') if stdout else ''
                }

            output = stdout.decode('utf-8').strip()

            if not output:
                return {'success': True, 'data': None, 'raw_output': ''}

            try:
                result_data = json.loads(output)
                return {
                    'success': True,
                    'data': result_data.get('data', result_data),
                    'raw_output': output
                }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'data': output,
                    'raw_output': output
                }

        except asyncio.TimeoutError:
            raise
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            raise
    
    async def execute_with_interpretation(
        self,
        script_content: str,
        context: SkillContext,
        llm_interpretation: str,
        reference_contents: Optional[Dict[str, str]] = None
    ) -> SkillResult:
        """Execute a script where LLM has interpreted and prepared the logic."""
        start_time = time.time()
        
        parameters = context.parameters.copy()
        parameters['_interpretation'] = llm_interpretation
        parameters['_context'] = {
            'request_id': context.request_id,
            'metadata': context.metadata
        }
        
        if reference_contents:
            parameters['_references'] = reference_contents
        
        try:
            result = await self._run_script(
                script_content,
                parameters,
                self.default_timeout / 1000.0
            )
            
            return SkillResult(
                success=result['success'],
                data=result.get('data'),
                error=result.get('error'),
                raw_output=result.get('raw_output', ''),
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            return SkillResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
