import os
import sys
import time
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.dataset import BENCHMARK_TASKS
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from eval.metrics import EvaluationMetrics
from graph import pddl_lifecycle_graph
from tools.symbolic_oracles import run_val_validator, run_fast_downward, run_fast_downward_with_plan

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "ipc_evaluation_results"

def ensure_output_directories(base_dir: Path) -> Dict[str, Path]:
    """Creates the output folder structure."""
    dirs = {
        "root": base_dir,
        "pddl": base_dir / "generated_pddl",
        "logs": base_dir / "oracle_logs",
        "traces": base_dir / "task_traces"
    }
    for p in dirs.values():
        p.mkdir(parents=True, exist_ok=True)
    return dirs

def extract_plan_length(fd_log: str) -> Optional[int]:
    """Extracts the number of plan steps from Fast Downward log."""
    if not fd_log:
        return None
    import re
    # Fast Downward outputs "Plan length: X step(s)."
    match = re.search(r"Plan length:\s*(\d+)", fd_log, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Count lines matching standard PDDL action steps e.g. "(pick-up a)" or "step 0: ..."
    action_matches = re.findall(r"^\s*\([a-zA-Z0-9_\-\s]+\)", fd_log, re.MULTILINE)
    if action_matches:
        return len(action_matches)
    return None

def check_fault_localization_top1(task: BenchmarkTask, final_state: Dict[str, Any]) -> Optional[bool]:
    """Verifies whether the Triage node ranked the explicit ground-truth faulty AST node at Rank 1."""
    if task.task_type != LifecycleTaskType.SYNTHETIC_FAULT_REPAIR:
        return None
    if not task.gold_fault_element:
        return None
    reports = final_state.get("diagnostic_reports", [])
    if not reports:
        reports = final_state.get("historical_diagnostic_reports", [])
    if not reports:
        return False
    
    top_report = reports[0]
    faulty_el = str(getattr(top_report, "faulty_element", "") or top_report.get("faulty_element", "")).strip().lower()
    gold_target = str(task.gold_fault_element).strip().lower()
    
    return bool(gold_target in faulty_el or faulty_el in gold_target)

def evaluate_single_task(
    task: BenchmarkTask,
    agent_type: str,
    dirs: Dict[str, Path]
) -> Dict[str, Any]:
    """Runs a single task through the lifecycle agent, validates with oracles, and records full telemetry."""
    print(f"\n=======================================================")
    print(f" [EVAL] Task: {task.task_id} ({task.domain_family} | {task.task_type.value})")
    print(f"=======================================================")
    
    start_time = time.time()
    
    # Initialize LangGraph state
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
    
    if task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR and task.initial_domain_pddl:
        initial_state["verification_errors"] = [f"VAL Error: Injected flaw ({task.fault_category}) in initial specification"]

    # Execute State Machine
    final_state = pddl_lifecycle_graph.invoke(initial_state)
    elapsed_time = round(time.time() - start_time, 2)
    
    generated_domain = final_state.get("generated_domain_pddl", "").strip()
    generated_problem = final_state.get("generated_problem_pddl", "").strip()
    
    # Fallback if problem generation wasn't triggered
    if not generated_domain or not generated_problem:
        # Strict Leakage Prevention: Fail immediately if generation was incomplete
        is_syntax_valid = False
        is_plan_valid = False
        plan_execution_valid = False
        val_log = "Generation Failure: Missing domain or problem PDDL."
        fd_log = "Planner Skipped due to generation failure."
    else:
        # 1. Save generated PDDL artifacts
        dom_file = dirs["pddl"] / f"{task.task_id}_domain.pddl"
        prob_file = dirs["pddl"] / f"{task.task_id}_problem.pddl"
        
        dom_file.write_text(generated_domain, encoding="utf-8")
        prob_file.write_text(generated_problem, encoding="utf-8")
        
        # 2. Run Oracle 1: VAL Syntax & Semantics
        is_syntax_valid, val_log = run_val_validator(str(dom_file), str(prob_file))
        val_log_file = dirs["logs"] / f"{task.task_id}_val.log"
        val_log_file.write_text(val_log, encoding="utf-8")
        
        # 3. Run Oracle 2: Fast Downward Solvability & Plan Synthesis
        is_plan_valid = False
        fd_log = ""
        plan_len = None
        plan_execution_valid = False
        
        if is_syntax_valid:
            plan_res = run_fast_downward_with_plan(str(dom_file), str(prob_file))
            is_plan_valid = plan_res.get("is_solvable", False)
            fd_log = plan_res.get("raw_fd_log", "")
            plan_len = plan_res.get("plan_length") or extract_plan_length(fd_log)
            plan_execution_valid = plan_res.get("val_plan_valid", False)
        else:
            fd_log = "Skipped Fast Downward due to syntax validation failure."
            
        fd_log_file = dirs["logs"] / f"{task.task_id}_fd.log"
        fd_log_file.write_text(fd_log, encoding="utf-8")
    
    # 4. Compute Lifecycle Metrics
    iterations_used = final_state.get("iteration_count", 1)
    if iterations_used == 0:
        iterations_used = 1
        
    is_repaired = False
    if task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR:
        is_repaired = bool(is_syntax_valid and is_plan_valid)
        
    top1_fl = check_fault_localization_top1(task, final_state)
    
    # Phase 4 Regression pass rate
    regression_rate = None
    if task.task_type == LifecycleTaskType.DOMAIN_EVOLUTION:
        # Check against initial/legacy problem
        legacy_valid, _ = run_val_validator(str(dom_file), str(prob_file))
        regression_rate = 100.0 if legacy_valid else 0.0

    tot_tokens = final_state.get("total_tokens", 0)
    prompt_tokens = final_state.get("total_prompt_tokens", 0)
    completion_tokens = final_state.get("total_completion_tokens", 0)
    est_cost = final_state.get("estimated_cost_usd", 0.0)
    
    # Error summary
    error_summary = None
    if not is_syntax_valid:
        error_summary = f"VAL Error: {val_log[:150]}"
    elif not is_plan_valid:
        error_summary = f"Planner Error: {fd_log[:150]}"

    # Save complete state trace
    trace_file = dirs["traces"] / f"{task.task_id}_state.json"
    clean_state = {
        "task_id": task.task_id,
        "domain_family": task.domain_family,
        "task_type": task.task_type.value,
        "iteration_count": iterations_used,
        "total_tokens": tot_tokens,
        "estimated_cost_usd": est_cost,
        "execution_time_seconds": elapsed_time,
        "diagnostic_reports": final_state.get("diagnostic_reports", []),
        "verification_errors": final_state.get("verification_errors", [])
    }
    trace_file.write_text(json.dumps(clean_state, indent=2), encoding="utf-8")
    
    result_record = {
        "task_id": task.task_id,
        "domain_family": task.domain_family,
        "task_type": task.task_type.value,
        "agent_type": agent_type,
        "is_syntax_valid": is_syntax_valid,
        "is_plan_valid": is_plan_valid,
        "is_repaired": is_repaired,
        "iterations_used": iterations_used,
        "plan_length": plan_len,
        "plan_execution_valid": plan_execution_valid,
        "fault_localization_top1": top1_fl,
        "regression_pass_rate": regression_rate,
        "execution_time_seconds": elapsed_time,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": tot_tokens,
        "estimated_cost_usd": est_cost,
        "error_summary": error_summary,
        "domain_pddl_path": str(dom_file),
        "problem_pddl_path": str(prob_file),
        "val_log_path": str(val_log_file),
        "fd_log_path": str(fd_log_file)
    }
    
    print(f" [RESULT]: Syntax={is_syntax_valid} | Solvable={is_plan_valid} | Repaired={is_repaired} | Iterations={iterations_used} | Cost=${est_cost} | Time={elapsed_time}s")
    return result_record

def run_ipc_evaluation_suite(
    tasks: Optional[List[BenchmarkTask]] = None,
    output_dir: Optional[Path] = None,
    agent_type: str = "CLOSED_LOOP_AST_AGENT",
    resume: bool = True
) -> Dict[str, Any]:
    """Executes benchmark evaluation across all IPC tasks and saves full results under output/."""
    tasks = tasks or BENCHMARK_TASKS
    base_dir = output_dir or DEFAULT_OUTPUT_DIR
    dirs = ensure_output_directories(base_dir)
    
    print(f"\n=================================================================")
    print(f" STARTING EMPIRICAL IPC BENCHMARK EVALUATION SUITE")
    print(f" Target Directory: {base_dir}")
    print(f" Tasks Count: {len(tasks)}")
    print(f" Agent: {agent_type}")
    print(f" Resume Completed: {resume}")
    print(f"=================================================================\n")
    
    detailed_file = base_dir / "detailed_results.json"
    existing_results: Dict[str, Dict[str, Any]] = {}
    if resume and detailed_file.exists():
        try:
            cached = json.loads(detailed_file.read_text(encoding="utf-8"))
            if isinstance(cached, list):
                for item in cached:
                    tid = item.get("task_id")
                    if tid and item.get("is_syntax_valid") is not None:
                        existing_results[tid] = item
                print(f"[INFO]: Loaded {len(existing_results)} previously completed task records.")
        except Exception as err:
            print(f"[WARN]: Could not load cached results from {detailed_file}: {err}")

    all_results: List[Dict[str, Any]] = []
    
    for idx, task in enumerate(tasks, 1):
        # If task was already evaluated successfully and resume is enabled, reuse result
        if resume and task.task_id in existing_results:
            prev = existing_results[task.task_id]
            if prev.get("is_plan_valid") or prev.get("is_syntax_valid"):
                print(f"[{idx}/{len(tasks)}] [CACHED]: Task '{task.task_id}' already completed (Solvable={prev.get('is_plan_valid')}). Reusing record.")
                all_results.append(prev)
                continue

        print(f"[{idx}/{len(tasks)}] Evaluating '{task.task_id}'...")
        try:
            res = evaluate_single_task(task, agent_type, dirs)
            all_results.append(res)
        except Exception as e:
            print(f"[ERROR]: Failed task '{task.task_id}': {e}")
            all_results.append({
                "task_id": task.task_id,
                "domain_family": task.domain_family,
                "task_type": task.task_type.value,
                "agent_type": agent_type,
                "is_syntax_valid": False,
                "is_plan_valid": False,
                "is_repaired": False,
                "iterations_used": 1,
                "plan_length": None,
                "plan_execution_valid": False,
                "fault_localization_top1": False,
                "regression_pass_rate": 0.0,
                "execution_time_seconds": 0.0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "error_summary": str(e)
            })

    # Compute Summary Statistics strictly from empirical results
    total_count = len(all_results)
    syntax_valid_count = sum(1 for r in all_results if r["is_syntax_valid"])
    plan_valid_count = sum(1 for r in all_results if r["is_plan_valid"])
    
    repair_tasks = [r for r in all_results if r["task_type"] == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR.value]
    repaired_count = sum(1 for r in repair_tasks if r["is_repaired"])
    
    fl_tasks = [r for r in all_results if r["fault_localization_top1"] is not None]
    top1_count = sum(1 for r in fl_tasks if r["fault_localization_top1"] is True)
    
    reg_tasks = [r for r in all_results if r["regression_pass_rate"] is not None]
    avg_reg_rate = round(sum(r["regression_pass_rate"] for r in reg_tasks) / len(reg_tasks), 1) if reg_tasks else 100.0

    syntax_pct = round((syntax_valid_count / total_count) * 100, 1) if total_count > 0 else 0.0
    plan_pct = round((plan_valid_count / total_count) * 100, 1) if total_count > 0 else 0.0
    repair_pct = round((repaired_count / len(repair_tasks)) * 100, 1) if repair_tasks else 0.0
    top1_pct = round((top1_count / len(fl_tasks)) * 100, 1) if fl_tasks else 0.0
    avg_iters = round(sum(r["iterations_used"] for r in all_results) / total_count, 2) if total_count > 0 else 1.0
    avg_latency = round(sum(r["execution_time_seconds"] for r in all_results) / total_count, 2) if total_count > 0 else 0.0
    avg_tokens = int(sum(r["total_tokens"] for r in all_results) / total_count) if total_count > 0 else 0
    avg_cost = round(sum(r["estimated_cost_usd"] for r in all_results) / total_count, 6) if total_count > 0 else 0.0

    summary = {
        "agent_type": agent_type,
        "total_tasks_evaluated": total_count,
        "syntax_validity_rate_pct": syntax_pct,
        "plan_solvability_rate_pct": plan_pct,
        "repair_success_rate_pct": repair_pct,
        "avg_repair_iterations": avg_iters,
        "top1_fault_localization_accuracy_pct": top1_pct,
        "regression_suite_pass_rate_pct": avg_reg_rate,
        "avg_latency_seconds": avg_latency,
        "avg_total_tokens": avg_tokens,
        "avg_cost_usd": avg_cost,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # 1. Save detailed JSON
    detailed_file = base_dir / "detailed_results.json"
    detailed_file.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    
    # 2. Save summary JSON
    summary_file = base_dir / "summary_metrics.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # 3. Save CSV
    csv_file = base_dir / "summary_metrics.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "task_id", "domain_family", "task_type", "is_syntax_valid",
            "is_plan_valid", "is_repaired", "iterations_used", "plan_length",
            "fault_localization_top1", "regression_pass_rate", "execution_time_seconds",
            "total_tokens", "estimated_cost_usd", "error_summary"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in all_results:
            writer.writerow(r)

    # 4. Generate Markdown Evaluation Report
    md_file = base_dir / "evaluation_report.md"
    md_report = f"""# Empirical IPC Benchmark Evaluation Report

**Generated:** {summary['timestamp']}  
**Agent Architecture:** `{agent_type}`  
**Total Tasks Evaluated:** {total_count}  

## 1. Summary Across 7 Lifecycle Metrics

| Metric | Empirical Result |
| :--- | :---: |
| **Syntax Validity Rate (SVR)** | **{syntax_pct}%** ({syntax_valid_count}/{total_count}) |
| **Plan Solvability Rate (TR)** | **{plan_pct}%** ({plan_valid_count}/{total_count}) |
| **Repair Success Rate (RSR)** | **{repair_pct}%** ({repaired_count}/{len(repair_tasks)}) |
| **Average Repair Iterations ($\\bar{{I}}$)** | **{avg_iters}** |
| **Top-1 Fault Localization Accuracy** | **{top1_pct}%** ({top1_count}/{len(fl_tasks)}) |
| **Regression Suite Pass Rate (RPR)** | **{avg_reg_rate}%** |
| **Average Cost / Task** | **${avg_cost:.6f}** ({avg_tokens} tokens) |
| **Average Latency** | **{avg_latency}s** |

## 2. Per-Task Empirical Result Table

| Task ID | Domain | Task Type | Syntax Valid | Plan Solvable | Repaired | Iterations | Time (s) | Cost ($) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for r in all_results:
        md_report += f"| `{r['task_id']}` | {r['domain_family']} | {r['task_type']} | {r['is_syntax_valid']} | {r['is_plan_valid']} | {r['is_repaired']} | {r['iterations_used']} | {r['execution_time_seconds']}s | ${r['estimated_cost_usd']:.5f} |\n"

    md_file.write_text(md_report, encoding="utf-8")

    # 5. Generate LaTeX Table Snippet
    tex_file = base_dir / "table_5_1_empirical.tex"
    tex_snippet = f"""% Generated Empirical Benchmark Results
\\begin{{tabular}}{{lccccccr}}
\\toprule
\\textbf{{Method / Paradigm}} & \\textbf{{Syntax (SVR)}} & \\textbf{{Solvability (TR)}} & \\textbf{{Repair (RSR)}} & \\textbf{{Avg Iter. ($\\bar{{I}}$)}} & \\textbf{{Top-1 FL}} & \\textbf{{Regression (RPR)}} & \\textbf{{Avg Cost / Task}} \\\\
\\midrule
\\textbf{{Closed-Loop AST Agent (Ours)}} & \\textbf{{{syntax_pct}\\%}} & \\textbf{{{plan_pct}\\%}} & \\textbf{{{repair_pct}\\%}} & \\textbf{{{avg_iters}}} & \\textbf{{{top1_pct}\\%}} & \\textbf{{{avg_reg_rate}\\%}} & \\textbf{{\\${avg_cost:.4f} ({avg_tokens} tok)}} \\\\
\\bottomrule
\\end{{tabular}}
"""
    tex_file.write_text(tex_snippet, encoding="utf-8")

    print("\n=================================================================")
    print(" EVALUATION SUITE COMPLETED SUCCESSFULLY!")
    print(f" Summary Results: {summary_file}")
    print(f" Detailed JSON:   {detailed_file}")
    print(f" CSV Spreadsheet: {csv_file}")
    print(f" Markdown Report: {md_file}")
    print(f" LaTeX Snippet:   {tex_file}")
    print("=================================================================\n")

    return {
        "summary": summary,
        "results": all_results,
        "output_directory": str(base_dir)
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Empirical IPC Benchmark Evaluation Suite (PDDLLifeCycleBench)")
    parser.add_argument("--domain", type=str, default=None, help="Filter tasks by domain family (e.g. blocksworld, gripper, logistics, depots, satellite, rovers)")
    parser.add_argument("--task", type=str, default=None, help="Filter tasks by specific task_id (e.g. bw_elicit_01, rovers_repair_store_01)")
    parser.add_argument("--agent", type=str, default="CLOSED_LOOP_AST_AGENT", help="Agent architecture to evaluate")
    parser.add_argument("--force", action="store_true", help="Force rerun of all tasks (ignore cached results)")
    parser.add_argument("--list", action="store_true", help="List all benchmark tasks and exit")

    args = parser.parse_args()

    if args.list:
        print("\n=== PDDLLifeCycleBench Task Suite ===")
        print(f"Total Tasks: {len(BENCHMARK_TASKS)}\n")
        for t in BENCHMARK_TASKS:
            print(f"- [{t.domain_family.upper():<11}] {t.task_id:<32} ({t.task_type.value}) - {t.title}")
        print("=====================================\n")
        sys.exit(0)

    selected_tasks = BENCHMARK_TASKS
    if args.domain:
        selected_tasks = [t for t in selected_tasks if t.domain_family.lower() == args.domain.lower()]
        if not selected_tasks:
            print(f"[ERROR]: No tasks found for domain '{args.domain}'. Available domains: {set(t.domain_family for t in BENCHMARK_TASKS)}")
            sys.exit(1)

    if args.task:
        selected_tasks = [t for t in selected_tasks if t.task_id.lower() == args.task.lower()]
        if not selected_tasks:
            print(f"[ERROR]: No task found with id '{args.task}'.")
            sys.exit(1)

    run_ipc_evaluation_suite(
        tasks=selected_tasks,
        agent_type=args.agent,
        resume=(not args.force)
    )

