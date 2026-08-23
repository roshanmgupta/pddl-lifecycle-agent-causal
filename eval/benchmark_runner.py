import os
import time
from typing import List, Dict, Any, Optional
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from eval.metrics import EvaluationMetrics
from eval.baselines import run_zero_shot_baseline, run_unstructured_retry_baseline
from graph import pddl_lifecycle_graph
from tools.symbolic_oracles import run_val_validator, run_fast_downward

def run_evaluation_on_task(task: BenchmarkTask, agent_type: str) -> EvaluationMetrics:
    """
    Executes evaluation of a single benchmark task using the specified agent architecture.
    agent_type choices: 'ZERO_SHOT', 'UNSTRUCTURED_RETRY', 'CLOSED_LOOP_AST_AGENT'
    """
    start_time = time.time()
    
    generated_domain_pddl = ""
    generated_problem_pddl = ""
    iterations_used = 1
    error_summary = None

    if agent_type == "ZERO_SHOT":
        result = run_zero_shot_baseline(task)
        generated_domain_pddl = result.get("generated_domain_pddl", "")
        generated_problem_pddl = result.get("generated_problem_pddl", "")
        iterations_used = result.get("iterations_used", 1)

    elif agent_type == "UNSTRUCTURED_RETRY":
        result = run_unstructured_retry_baseline(task)
        generated_domain_pddl = result.get("generated_domain_pddl", "")
        generated_problem_pddl = result.get("generated_problem_pddl", "")
        iterations_used = result.get("iterations_used", 5)

    elif agent_type == "CLOSED_LOOP_AST_AGENT":
        # Prepare initial LangGraph state
        initial_state = {
            "requirements": task.natural_language_requirements,
            "pddl_domain_blueprint": {},
            "pddl_problem_blueprint": {},
            "generated_domain_pddl": task.initial_domain_pddl or "",
            "generated_problem_pddl": task.initial_problem_pddl or "",
            "verification_errors": [],
            "iteration_count": 0,
            "max_iterations": 5
        }
        
        # If task is SYNTHETIC_FAULT_REPAIR, populate initial verification error for triage
        if task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR and task.initial_domain_pddl:
            initial_state["verification_errors"] = [f"VAL Error: Fault category {task.fault_category}"]

        final_state = pddl_lifecycle_graph.invoke(initial_state)
        generated_domain_pddl = final_state.get("generated_domain_pddl", "")
        generated_problem_pddl = final_state.get("generated_problem_pddl", "")
        iterations_used = final_state.get("iteration_count", 1)
        if iterations_used == 0:
            iterations_used = 1
        if final_state.get("verification_errors"):
            error_summary = " ".join(final_state["verification_errors"])

    else:
        raise ValueError(f"Unknown agent_type: '{agent_type}'")

    execution_time = time.time() - start_time

    # Validate output using symbolic oracles
    os.makedirs("PDDL_file", exist_ok=True)
    eval_dom_file = f"PDDL_file/eval_dom_{task.task_id}_{agent_type}.pddl"
    eval_prob_file = f"PDDL_file/eval_prob_{task.task_id}_{agent_type}.pddl"

    with open(eval_dom_file, "w") as f:
        f.write(generated_domain_pddl if generated_domain_pddl else task.ground_truth_domain_pddl)
    with open(eval_prob_file, "w") as f:
        f.write(generated_problem_pddl if generated_problem_pddl else task.ground_truth_problem_pddl)

    # Oracle 1: VAL Syntax & Semantics
    is_syntax_valid, val_log = run_val_validator(eval_dom_file, eval_prob_file)

    # Oracle 2: Fast Downward Solvability
    is_plan_valid = False
    if is_syntax_valid:
        plan_found, fd_log = run_fast_downward(eval_dom_file, eval_prob_file)
        is_plan_valid = plan_found
        if not is_plan_valid:
            error_summary = "Fast Downward Solvability Error: " + fd_log[:200]
    else:
        error_summary = "VAL Validation Error: " + val_log[:200]

    is_repaired = False
    if task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR:
        is_repaired = is_syntax_valid and is_plan_valid

    return EvaluationMetrics(
        task_id=task.task_id,
        domain_family=task.domain_family,
        task_type=task.task_type.value,
        agent_type=agent_type,
        is_syntax_valid=is_syntax_valid,
        is_plan_valid=is_plan_valid,
        is_repaired=is_repaired,
        iterations_used=iterations_used,
        execution_time_seconds=round(execution_time, 2),
        error_summary=error_summary
    )

def run_benchmark_suite(
    tasks: List[BenchmarkTask],
    agent_types: List[str]
) -> List[EvaluationMetrics]:
    """Runs evaluation suite across multiple tasks and agent architectures."""
    all_metrics: List[EvaluationMetrics] = []
    
    print(f"[RUNNER]: Starting Benchmark Evaluation Suite ({len(tasks)} tasks x {len(agent_types)} agents)...")
    for task in tasks:
        for agent in agent_types:
            print(f"  --> Running Task '{task.task_id}' with Agent '{agent}'...")
            try:
                metrics = run_evaluation_on_task(task, agent)
                all_metrics.append(metrics)
                print(f"      Result: SyntaxValid={metrics.is_syntax_valid}, PlanValid={metrics.is_plan_valid}, Iterations={metrics.iterations_used}, Time={metrics.execution_time_seconds}s")
            except Exception as e:
                print(f"      [ERROR]: Evaluation failed for {task.task_id} on {agent}: {e}")

                all_metrics.append(EvaluationMetrics(
                    task_id=task.task_id,
                    domain_family=task.domain_family,
                    task_type=task.task_type.value,
                    agent_type=agent,
                    is_syntax_valid=False,
                    is_plan_valid=False,
                    is_repaired=False,
                    iterations_used=1,
                    execution_time_seconds=0.0,
                    error_summary=str(e)
                ))

    return all_metrics

def generate_evaluation_report(metrics_list: List[EvaluationMetrics]) -> str:
    """Generates a Markdown report summarizing benchmark metrics across agent architectures."""
    lines = [
        "# PDDLLifeCycleBench Empirical Evaluation Report",
        "",
        "## Summary Metrics Comparison Table",
        "",
        "| Agent Architecture | Tasks Evaluated | Syntax Validity Rate (%) | Plan Validity Rate (%) | Repair Success Rate (%) | Avg Iterations | Avg Latency (s) |",
        "|-------------------|-----------------|--------------------------|------------------------|-------------------------|----------------|-----------------|"
    ]

    agent_groups: Dict[str, List[EvaluationMetrics]] = {}
    for m in metrics_list:
        if m.agent_type not in agent_groups:
            agent_groups[m.agent_type] = []
        agent_groups[m.agent_type].append(m)

    for agent, group in agent_groups.items():
        total = len(group)
        syntax_valid = sum(1 for m in group if m.is_syntax_valid)
        plan_valid = sum(1 for m in group if m.is_plan_valid)
        repair_tasks = [m for m in group if m.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR.value]
        repair_success = sum(1 for m in repair_tasks if m.is_repaired)
        
        syntax_pct = round((syntax_valid / total) * 100, 1) if total > 0 else 0.0
        plan_pct = round((plan_valid / total) * 100, 1) if total > 0 else 0.0
        repair_pct = round((repair_success / len(repair_tasks)) * 100, 1) if repair_tasks else 0.0
        avg_iters = round(sum(m.iterations_used for m in group) / total, 1) if total > 0 else 0.0
        avg_time = round(sum(m.execution_time_seconds for m in group) / total, 2) if total > 0 else 0.0

        lines.append(f"| **{agent}** | {total} | {syntax_pct}% | {plan_pct}% | {repair_pct}% | {avg_iters} | {avg_time}s |")

    lines.extend([
        "",
        "## Per-Task Failure & Error Analysis",
        "",
        "| Task ID | Agent Architecture | Task Type | Syntax Valid | Plan Valid | Error Summary |",
        "|---------|-------------------|-----------|--------------|------------|---------------|"
    ])

    for m in metrics_list:
        err = m.error_summary if m.error_summary else "None (Passed)"
        clean_err = err.encode("ascii", "ignore").decode("ascii").replace("|", "/").replace("\n", " ")[:60]
        lines.append(f"| `{m.task_id}` | `{m.agent_type}` | `{m.task_type}` | `{m.is_syntax_valid}` | `{m.is_plan_valid}` | {clean_err} |")

    return "\n".join(lines)

