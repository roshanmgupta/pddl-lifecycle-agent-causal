import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from benchmark.dataset import BENCHMARK_TASKS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
from config.paths import get_benchmark_dir
BENCHMARK_ROOT = get_benchmark_dir()

# ==============================================================================
# PDDLLifeCycleBench Dynamic Loader Helpers (Flaws & Evolution)
# ==============================================================================

def list_benchmark_domains() -> List[str]:
    """Returns sorted list of all 24 canonical domains available in PDDLLifeCycleBench."""
    if not BENCHMARK_ROOT.exists():
        return []
    domains = [
        d.name for d in BENCHMARK_ROOT.iterdir()
        if d.is_dir() and not d.name.startswith((".", "__"))
    ]
    return sorted(domains)

def list_domain_flaws(domain_name: str) -> List[str]:
    """Lists available curated flaw task folders for a domain."""
    flaws_dir = BENCHMARK_ROOT / domain_name / "flaws"
    if not flaws_dir.exists():
        return []
    flaws = [f.name for f in flaws_dir.iterdir() if f.is_dir()]
    return sorted(flaws)

def load_flaw_task(domain_name: str, flaw_name: str) -> Optional[BenchmarkTask]:
    """
    Loads a single Category B flaw task from PDDLLifeCycleBench/<domain>/flaws/<flaw_name>.
    Constructs an executable BenchmarkTask with ground-truth metadata and oracle expectations.
    """
    flaw_dir = BENCHMARK_ROOT / domain_name / "flaws" / flaw_name
    if not flaw_dir.exists():
        return None

    dom_flawed = (flaw_dir / "domain_flawed.pddl").read_text(encoding="utf-8")
    meta = json.loads((flaw_dir / "flaw_metadata.json").read_text(encoding="utf-8"))
    spec = (flaw_dir / "complete_specification.txt").read_text(encoding="utf-8")
    gt_dom = (BENCHMARK_ROOT / domain_name / "domain.pddl").read_text(encoding="utf-8")

    # Use problem_flawed.pddl if present (e.g. initial/goal deadlocks), otherwise instance-1
    prob_file = flaw_dir / "problem_flawed.pddl"
    if not prob_file.exists():
        prob_file = BENCHMARK_ROOT / domain_name / "orig_problems" / "instance-1.pddl"
    prob_pddl = prob_file.read_text(encoding="utf-8") if prob_file.exists() else ""

    fcat = meta.get("flaw_category", "UNKNOWN")
    return BenchmarkTask(
        task_id=f"{domain_name}_{flaw_name}",
        domain_family=domain_name,
        task_type=LifecycleTaskType.SYNTHETIC_FAULT_REPAIR,
        title=f"{domain_name.upper()} Flaw: {fcat}",
        natural_language_requirements=spec,
        initial_domain_pddl=dom_flawed,
        initial_problem_pddl=prob_pddl,
        fault_category=fcat,
        gold_fault_element=meta.get("target_action"),
        gold_fault_category=fcat,
        expected_repair_behavior=meta.get("ground_truth_fix"),
        ground_truth_domain_pddl=gt_dom,
        ground_truth_problem_pddl=prob_pddl
    )

def list_domain_evolutions(domain_name: str) -> List[str]:
    """Lists available Continuous Domain Evolution task folders for a domain."""
    evo_dir = BENCHMARK_ROOT / domain_name / "evolution"
    if not evo_dir.exists():
        return []
    evos = [e.name for e in evo_dir.iterdir() if e.is_dir()]
    return sorted(evos)

def load_evolution_task(domain_name: str, evo_name: str) -> Optional[BenchmarkTask]:
    """
    Loads a single Category C continuous domain evolution task from
    PDDLLifeCycleBench/<domain>/evolution/<evo_name>.
    """
    evo_dir = BENCHMARK_ROOT / domain_name / "evolution" / evo_name
    if not evo_dir.exists():
        return None

    meta = json.loads((evo_dir / "evolution_metadata.json").read_text(encoding="utf-8"))
    spec = (evo_dir / "feature_request_specification.txt").read_text(encoding="utf-8")
    gt_dom = (BENCHMARK_ROOT / domain_name / "domain.pddl").read_text(encoding="utf-8")
    target_prob = (evo_dir / "target_problem.pddl").read_text(encoding="utf-8")

    reg_probs = []
    reg_dir = evo_dir / "historical_regression_problems"
    if reg_dir.exists():
        for rf in sorted(reg_dir.glob("*.pddl")):
            reg_probs.append(rf.read_text(encoding="utf-8"))

    cat = meta.get("evolution_category", "DOMAIN_EVOLUTION")
    return BenchmarkTask(
        task_id=f"{domain_name}_{evo_name}",
        domain_family=domain_name,
        task_type=LifecycleTaskType.DOMAIN_EVOLUTION,
        title=f"{domain_name.upper()} Evolution: {cat}",
        natural_language_requirements=spec,
        initial_domain_pddl=gt_dom,
        initial_problem_pddl=target_prob,
        evolution_target_problem_pddl=target_prob,
        historical_regression_problems=reg_probs,
        expected_repair_behavior=meta.get("gatekeeper_requirement"),
        ground_truth_domain_pddl=gt_dom,
        ground_truth_problem_pddl=target_prob
    )

# ==============================================================================
# Selected Benchmark Domains Suite (Focused Evaluation Scope)
# ==============================================================================

SELECTED_BENCHMARK_DOMAINS = [
    "blocksworld",
    "gripper",
    "logistics",
    "ferry",
    "satellite",
    "rovers",
    "depot",
    "parking11",
    "zenotravel02",
    "floortile"
]

# Alias for backwards compatibility
CANONICAL_10_DOMAINS = SELECTED_BENCHMARK_DOMAINS

def load_elicitation_task(domain_name: str) -> Optional[BenchmarkTask]:
    """Loads a single Category A Elicitation task for a standard benchmark domain."""
    dom_dir = BENCHMARK_ROOT / domain_name
    if not dom_dir.exists():
        return None
    spec_file = dom_dir / "complete_specification.txt"
    dom_file = dom_dir / "domain.pddl"
    prob_files = sorted(list((dom_dir / "orig_problems").glob("instance-*.pddl")))
    if not spec_file.exists() or not dom_file.exists() or not prob_files:
        return None

    spec = spec_file.read_text(encoding="utf-8")
    gt_dom = dom_file.read_text(encoding="utf-8")
    gt_prob = prob_files[0].read_text(encoding="utf-8")

    return BenchmarkTask(
        task_id=f"{domain_name}_elicit",
        domain_family=domain_name,
        task_type=LifecycleTaskType.ELICITATION,
        title=f"{domain_name.upper()} Initial Elicitation",
        natural_language_requirements=spec,
        initial_domain_pddl=None,
        initial_problem_pddl=None,
        ground_truth_domain_pddl=gt_dom,
        ground_truth_problem_pddl=gt_prob
    )

def load_selected_evaluation_tasks() -> List[BenchmarkTask]:
    """
    Curates the focused evaluation suite for the 10 selected benchmark domains:
    - 10 Category A Elicitation Tasks (1 per domain)
    - 20 Category B Synthetic Fault Repair Tasks (2 per domain: arity & precondition flaws)
    - 2 Category C Continuous Evolution Tasks (Blocksworld & Logistics demonstration)
    Total: 32 tasks.
    """
    suite = []
    # 1. Category A: 10 Elicitation Tasks
    for d in SELECTED_BENCHMARK_DOMAINS:
        t_elicit = load_elicitation_task(d)
        if t_elicit:
            suite.append(t_elicit)

    # 2. Category B: 20 Synthetic Fault Repair Tasks (2 per domain)
    for d in SELECTED_BENCHMARK_DOMAINS:
        flaws = list_domain_flaws(d)
        for flaw_name in flaws[:2]:
            t_flaw = load_flaw_task(d, flaw_name)
            if t_flaw:
                suite.append(t_flaw)

    # 3. Category C: 2 Domain Evolution Demonstrations
    t_evo_bw = load_evolution_task("blocksworld", "evolution_01_feature_addition")
    if t_evo_bw:
        suite.append(t_evo_bw)
    t_evo_log = load_evolution_task("logistics", "evolution_01_feature_addition")
    if t_evo_log:
        suite.append(t_evo_log)

    return suite

# Alias for backwards compatibility
load_canonical_10_evaluation_tasks = load_selected_evaluation_tasks

def load_all_lifecycle_bench_tasks() -> List[BenchmarkTask]:
    """Dynamically compiles all flaws and evolutions from PDDLLifeCycleBench into BenchmarkTasks."""
    tasks = []
    for domain in list_benchmark_domains():
        for flaw in list_domain_flaws(domain):
            t = load_flaw_task(domain, flaw)
            if t:
                tasks.append(t)
        for evo in list_domain_evolutions(domain):
            t = load_evolution_task(domain, evo)
            if t:
                tasks.append(t)
    return tasks

# ==============================================================================
# Legacy Compatible Functions
# ==============================================================================

def load_benchmark_tasks(
    domain_family: Optional[str] = None,
    task_type: Optional[LifecycleTaskType] = None
) -> List[BenchmarkTask]:
    """
    Loads benchmark evaluation tasks from both legacy BENCHMARK_TASKS
    and PDDLLifeCycleBench. Supports filtering by domain_family or task_type.
    """
    tasks = list(BENCHMARK_TASKS)
    
    # Also include dynamically loaded lifecycle tasks
    dynamic_tasks = load_all_lifecycle_bench_tasks()
    existing_ids = set(t.task_id for t in tasks)
    for dt in dynamic_tasks:
        if dt.task_id not in existing_ids:
            tasks.append(dt)
            existing_ids.add(dt.task_id)

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
            
    # Check dynamic PDDLLifeCycleBench
    if "_" in task_id:
        parts = task_id.split("_", 1)
        domain = parts[0]
        subtask = parts[1]
        if subtask.startswith("flaw_"):
            return load_flaw_task(domain, subtask)
        elif subtask.startswith("evolution_"):
            return load_evolution_task(domain, subtask)
            
    return None

def list_benchmark_summary() -> Dict[str, Any]:
    """Returns summary metadata statistics for PDDLLifeCycleBench."""
    all_tasks = load_benchmark_tasks()
    summary = {
        "total_tasks": len(all_tasks),
        "domain_families": sorted(list(set(t.domain_family for t in all_tasks))),
        "task_types": sorted(list(set(t.task_type.value for t in all_tasks))),
        "task_counts_by_family": {},
        "task_counts_by_type": {}
    }

    for t in all_tasks:
        fam = t.domain_family
        summary["task_counts_by_family"][fam] = summary["task_counts_by_family"].get(fam, 0) + 1

        ttype = t.task_type.value
        summary["task_counts_by_type"][ttype] = summary["task_counts_by_type"].get(ttype, 0) + 1

    return summary
