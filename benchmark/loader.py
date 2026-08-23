from typing import List, Optional, Dict, Any
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from benchmark.dataset import BENCHMARK_TASKS

def load_benchmark_tasks(
    domain_family: Optional[str] = None,
    task_type: Optional[LifecycleTaskType] = None
) -> List[BenchmarkTask]:
    """
    Loads benchmark evaluation tasks from PDDLLifeCycleBench.
    Supports filtering by domain_family (e.g. 'blocksworld') or task_type (e.g. ELICITATION).
    """
    tasks = BENCHMARK_TASKS
    if domain_family:
        tasks = [t for t in tasks if t.domain_family.lower() == domain_family.lower()]
    if task_type:
        tasks = [t for t in tasks if t.task_type == task_type]
    return tasks

def get_benchmark_task_by_id(task_id: str) -> Optional[BenchmarkTask]:
    """Finds a single benchmark task by its unique task_id."""
    for task in BENCHMARK_TASKS:
        if task.task_id == task_id:
            return task
    return None

def list_benchmark_summary() -> Dict[str, Any]:
    """Returns summary metadata statistics for PDDLLifeCycleBench."""
    summary = {
        "total_tasks": len(BENCHMARK_TASKS),
        "domain_families": list(set(t.domain_family for t in BENCHMARK_TASKS)),
        "task_types": list(set(t.task_type.value for t in BENCHMARK_TASKS)),
        "task_counts_by_family": {},
        "task_counts_by_type": {}
    }
    
    for t in BENCHMARK_TASKS:
        fam = t.domain_family
        summary["task_counts_by_family"][fam] = summary["task_counts_by_family"].get(fam, 0) + 1
        
        ttype = t.task_type.value
        summary["task_counts_by_type"][ttype] = summary["task_counts_by_type"].get(ttype, 0) + 1
        
    return summary
