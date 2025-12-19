"""Parallel execution utilities."""
from typing import List, Callable, Any, Dict, Optional
import asyncio
from datetime import datetime


async def execute_parallel(
    tasks: List[Callable],
    *args,
    **kwargs
) -> List[Any]:
    """Execute multiple tasks in parallel."""
    coroutines = [task(*args, **kwargs) for task in tasks]
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    return results


async def execute_parallel_with_timeout(
    tasks: List[Dict[str, Any]],
    default_timeout: float = 30.0
) -> List[Dict[str, Any]]:
    """
    Execute multiple tasks in parallel with individual timeouts.
    
    Args:
        tasks: List of dicts with keys: 'name', 'coro', 'timeout'
        default_timeout: Default timeout if not specified
    
    Returns:
        List of results with keys: 'name', 'result', 'success', 'error', 'execution_time'
    """
    async def execute_with_timeout(task_info: Dict[str, Any]) -> Dict[str, Any]:
        name = task_info["name"]
        coro = task_info["coro"]
        timeout = task_info.get("timeout", default_timeout)
        
        start_time = datetime.utcnow()
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "name": name,
                "result": result,
                "success": True,
                "error": None,
                "execution_time": execution_time
            }
        except asyncio.TimeoutError:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "name": name,
                "result": None,
                "success": False,
                "error": f"Timeout after {timeout}s",
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            return {
                "name": name,
                "result": None,
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    results = await asyncio.gather(*[execute_with_timeout(task) for task in tasks])
    return results

