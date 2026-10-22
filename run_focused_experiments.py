"""
run_focused_experiments.py
Autonomous Empirical Benchmark Runner for the 10 Selected Benchmark Domains.

Runs the 4 experimental configurations:
1. ZERO_SHOT (Baseline 1): One-shot direct PDDL text generation.
2. UNSTRUCTURED_RETRY / ABLATION_NO_AST (Baseline 2 / Ablation 1): Closed loop + raw PDDL text + raw logs. Tests H1.
3. ABLATION_NO_TRIAGE (Ablation 2): Closed loop + AST Blueprint + unguided raw logs. Tests H2.
4. CLOSED_LOOP_AST_AGENT (Full Proposed UPDEAgent): Closed loop + AST Blueprint + Structured Triage.

Outputs:
- CSV: evaluation_results_10_domains.csv
- Markdown Report: evaluation_report.md
"""

import sys
import os
import csv
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.loader import load_selected_evaluation_tasks, SELECTED_BENCHMARK_DOMAINS
from eval.benchmark_runner import run_evaluation_on_task, generate_evaluation_report
from eval.metrics import EvaluationMetrics

def main():
    tasks = load_selected_evaluation_tasks()
    print(f"==========================================================================")
    print(f" FOCUSED EMPIRICAL BENCHMARK: 10 SELECTED BENCHMARK DOMAINS ({len(tasks)} TASKS)")
    print(f" Target Domains: {SELECTED_BENCHMARK_DOMAINS}")
    print(f"==========================================================================")

    # Agent configurations to evaluate
    agent_configs = [
        "ZERO_SHOT",
        "UNSTRUCTURED_RETRY",
        "ABLATION_NO_TRIAGE",
        "CLOSED_LOOP_AST_AGENT"
    ]

    all_metrics = []
    csv_file = "evaluation_results_10_domains.csv"
    report_file = "evaluation_report.md"

    fieldnames = [
        "task_id", "domain_family", "task_type", "agent_type",
        "e2e_success", "is_syntax_valid", "is_plan_valid", "plan_execution_valid",
        "semantic_soundness_valid", "logic_match_score", "is_repaired",
        "fault_localization_top1", "fault_localization_top3", "fault_localization_mrr",
        "evolution_capability_valid", "regression_pass_rate",
        "iterations_used", "execution_time_seconds", "total_tokens", "estimated_cost_usd",
        "plan_length", "plan_cost", "search_time", "error_summary"
    ]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, task in enumerate(tasks, 1):
            print(f"\n--------------------------------------------------------------------------")
            print(f" Task [{idx}/{len(tasks)}]: {task.task_id} ({task.task_type.value}) - Domain: {task.domain_family}")
            print(f"--------------------------------------------------------------------------")

            for agent in agent_configs:
                print(f"  [Evaluating Agent: {agent}]...", end="", flush=True)
                start_t = time.time()
                try:
                    m = run_evaluation_on_task(task, agent, max_iterations=5)
                    all_metrics.append(m)
                    elapsed = round(time.time() - start_t, 2)
                    print(f" Done in {elapsed}s | Success={m.e2e_success} | Syntax={m.is_syntax_valid} | Solvable={m.is_plan_valid} | Iters={m.iterations_used}")
                    
                    writer.writerow(m.dict())
                    f.flush()
                except Exception as e:
                    print(f" FAILED with exception: {e}")

    # Generate and save summary report
    report_md = generate_evaluation_report(all_metrics)
    with open(report_file, "w", encoding="utf-8") as rf:
        rf.write(report_md)

    print(f"\n==========================================================================")
    print(f" Benchmark Complete! Results saved to:")
    print(f" - CSV: {csv_file}")
    print(f" - Report: {report_file}")
    print(f"==========================================================================")

if __name__ == "__main__":
    main()
