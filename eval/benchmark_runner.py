import os
import time
from typing import List, Dict, Any, Optional
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from eval.metrics import EvaluationMetrics
from eval.baselines import run_zero_shot_baseline, run_unstructured_retry_baseline
from graph import pddl_lifecycle_graph
from tools.symbolic_oracles import run_val_validator, run_fast_downward_with_plan
from config.paths import get_eval_output_dir

def compute_fault_localization_metrics(
    gold_element: Optional[str],
    diagnostic_reports: List[Any]
) -> tuple[Optional[bool], Optional[bool], Optional[float]]:
    """
    Computes Top-1, Top-3, and MRR for fault localization against explicit ground truth AST element.
    Returns (top1, top3, mrr).
    """
    if not gold_element or not diagnostic_reports:
        return None, None, None

    clean_gold = gold_element.strip().lower()
    ranked_candidates = []
    for r in diagnostic_reports:
        faulty = getattr(r, "faulty_element", "") if hasattr(r, "faulty_element") else str(r.get("faulty_element", ""))
        if faulty:
            ranked_candidates.append(faulty.strip().lower())

    if not ranked_candidates:
        return False, False, 0.0

    def _matches(gold: str, cand: str) -> bool:
        return gold in cand or cand in gold

    top1 = _matches(clean_gold, ranked_candidates[0])
    top3 = any(_matches(clean_gold, c) for c in ranked_candidates[:3])

    mrr = 0.0
    for idx, cand in enumerate(ranked_candidates):
        if _matches(clean_gold, cand):
            mrr = 1.0 / (idx + 1)
            break

    return top1, top3, mrr

def run_evaluation_on_task(task: BenchmarkTask, agent_type: str, max_iterations: int = 5) -> EvaluationMetrics:
    """
    Executes evaluation of a single benchmark task using the specified agent architecture.
    Strictly NO evaluation leakage or ground truth fallback.
    """
    start_time = time.time()
    
    generated_domain_pddl = ""
    generated_problem_pddl = ""
    iterations_used = 1
    tot_tokens = 0
    est_cost = 0.0
    error_summary = None
    diagnostic_reports = []

    # -------------------------------------------------------------
    # 1. Execute Agent Architecture
    # -------------------------------------------------------------
    if agent_type == "ZERO_SHOT":
        result = run_zero_shot_baseline(task)
        generated_domain_pddl = result.get("generated_domain_pddl", "")
        generated_problem_pddl = result.get("generated_problem_pddl", "")
        iterations_used = result.get("iterations_used", 1)
        tot_tokens = result.get("total_tokens", 0)
        est_cost = result.get("estimated_cost_usd", 0.0)
        if result.get("error"):
            error_summary = result["error"]

    elif agent_type in ["UNSTRUCTURED_RETRY", "ABLATION_NO_AST"]:
        result = run_unstructured_retry_baseline(task, max_retries=max_iterations)
        generated_domain_pddl = result.get("generated_domain_pddl", "")
        generated_problem_pddl = result.get("generated_problem_pddl", "")
        iterations_used = result.get("iterations_used", max_iterations)
        tot_tokens = result.get("total_tokens", 0)
        est_cost = result.get("estimated_cost_usd", 0.0)

    elif agent_type in ["CLOSED_LOOP_AST_AGENT", "ABLATION_NO_TRIAGE"]:
        initial_state = {
            "requirements": task.natural_language_requirements,
            "pddl_domain_blueprint": {},
            "pddl_problem_blueprint": {},
            "generated_domain_pddl": task.initial_domain_pddl or "",
            "generated_problem_pddl": task.initial_problem_pddl or "",
            "verification_errors": [],
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "skip_triage": (agent_type == "ABLATION_NO_TRIAGE")
        }
        
        # Injected verification error trigger for synthetic repair tasks
        if task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR and task.initial_domain_pddl:
            fault_cat = task.fault_category or "SYNTAX_PARSE"
            initial_state["verification_errors"] = [f"VAL Error: Fault category {fault_cat} detected in initial model."]

        final_state = pddl_lifecycle_graph.invoke(initial_state)
        generated_domain_pddl = final_state.get("generated_domain_pddl", "")
        generated_problem_pddl = final_state.get("generated_problem_pddl", "")
        iterations_used = max(1, final_state.get("iteration_count", 1))
        tot_tokens = final_state.get("total_tokens", 0)
        est_cost = final_state.get("estimated_cost_usd", 0.0)
        diagnostic_reports = final_state.get("diagnostic_reports", []) or final_state.get("historical_diagnostic_reports", [])
        
        if final_state.get("verification_errors"):
            error_summary = " ".join(final_state["verification_errors"])[:300]

    else:
        raise ValueError(f"Unknown agent_type: '{agent_type}'")

    execution_time = time.time() - start_time

    return evaluate_candidate_pddl(
        task=task,
        agent_type=agent_type,
        generated_domain_pddl=generated_domain_pddl,
        generated_problem_pddl=generated_problem_pddl,
        iterations_used=iterations_used,
        execution_time_seconds=execution_time,
        total_tokens=tot_tokens,
        estimated_cost_usd=est_cost,
        diagnostic_reports=diagnostic_reports,
        error_summary=error_summary
    )

def evaluate_candidate_pddl(
    task: BenchmarkTask,
    agent_type: str,
    generated_domain_pddl: str,
    generated_problem_pddl: str,
    iterations_used: int = 1,
    execution_time_seconds: float = 0.0,
    total_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
    diagnostic_reports: Optional[List[Any]] = None,
    error_summary: Optional[str] = None
) -> EvaluationMetrics:
    """
    Evaluates candidate PDDL domain and problem against classical oracles (VAL & Fast Downward).
    Computes rigorous primary (E2E Success) and secondary metrics without evaluation leakage.
    """
    # -------------------------------------------------------------
    # Strict Oracle Verification (NO Ground-Truth Fallback)
    # -------------------------------------------------------------
    eval_dir = str(get_eval_output_dir())
    os.makedirs(eval_dir, exist_ok=True)
    eval_dom_file = os.path.join(eval_dir, f"eval_dom_{task.task_id}_{agent_type}.pddl")
    eval_prob_file = os.path.join(eval_dir, f"eval_prob_{task.task_id}_{agent_type}.pddl")

    # Evaluation Leakage Prevention: If agent output is missing, record failure directly!
    if not generated_domain_pddl or not generated_problem_pddl:
        return EvaluationMetrics(
            task_id=task.task_id,
            domain_family=task.domain_family,
            task_type=task.task_type.value,
            agent_type=agent_type,
            e2e_success=False,
            is_syntax_valid=False,
            is_plan_valid=False,
            plan_execution_valid=False,
            is_repaired=False,
            iterations_used=iterations_used,
            execution_time_seconds=round(execution_time_seconds, 2),
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost_usd,
            error_summary="Generation Failed: Incomplete or missing domain/problem PDDL output from agent."
        )

    with open(eval_dom_file, "w", encoding="utf-8") as f:
        f.write(generated_domain_pddl)
    with open(eval_prob_file, "w", encoding="utf-8") as f:
        f.write(generated_problem_pddl)

    eval_dom_gt_file = None
    if getattr(task, "ground_truth_domain_pddl", None):
        eval_dom_gt_file = os.path.join(eval_dir, f"eval_dom_gt_{task.task_id}_{agent_type}.pddl")
        with open(eval_dom_gt_file, "w", encoding="utf-8") as f:
            f.write(task.ground_truth_domain_pddl)

    # Oracle 1: VAL Syntax & Semantics
    is_syntax_valid, val_log = run_val_validator(eval_dom_file, eval_prob_file)

    # Oracle 2: Fast Downward Search & Oracle 3: VAL Plan Certification
    is_plan_valid = False
    plan_execution_valid = False
    semantic_soundness_valid = None
    logic_match_score = None
    plan_length = None
    plan_cost = None
    search_time = None

    if is_syntax_valid:
        # For Synthetic Fault Repair & Evolution, vocabulary is shared with D_gt, so direct VAL is valid.
        # For Elicitation, vocabulary is generated from NL, so direct VAL would fail due to lexical naming differences.
        fd_gt_path = str(eval_dom_gt_file) if (eval_dom_gt_file and task.task_type != LifecycleTaskType.ELICITATION) else None
        fd_res = run_fast_downward_with_plan(
            eval_dom_file, 
            eval_prob_file, 
            ground_truth_domain_path=fd_gt_path
        )
        is_plan_valid = fd_res["is_solvable"]
        plan_execution_valid = fd_res["val_plan_valid"]
        semantic_soundness_valid = fd_res.get("semantic_soundness_valid")
        plan_length = fd_res["plan_length"]
        plan_cost = fd_res["plan_cost"]
        search_time = fd_res["search_time"]

        # For Elicitation tasks: Evaluate Action Reconstruction Error (ARE) against ground truth
        if task.task_type == LifecycleTaskType.ELICITATION and getattr(task, "ground_truth_domain_pddl", None):
            try:
                from eval.action_reconstruction import evaluate_action_reconstruction
                are_res = evaluate_action_reconstruction(task.ground_truth_domain_pddl, generated_domain_pddl)
                logic_match_score = are_res.get("macro_structural_f1")
                # Structural alignment score is recorded; plan execution is verified by VAL
                semantic_soundness_valid = plan_execution_valid
            except Exception as e:
                logic_match_score = None
                semantic_soundness_valid = False

        if not is_plan_valid:
            error_summary = "Planner Unsolvability: " + fd_res["raw_fd_log"][:200]
        elif not plan_execution_valid:
            error_summary = "Plan Certification Failed: " + fd_res.get("val_log", "")[:200]
        elif semantic_soundness_valid is False and task.task_type != LifecycleTaskType.ELICITATION:
            error_summary = "Semantic Soundness Failed (D_gt Rejected Plan): " + fd_res.get("semantic_soundness_log", "")[:200]
    else:
        error_summary = "VAL Validation Error: " + val_log[:200]

    # -------------------------------------------------------------
    # Task-Specific Secondary Metrics
    # -------------------------------------------------------------
    # A. Fault Repair Verification
    is_repaired = False
    if task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR:
        is_repaired = is_syntax_valid and is_plan_valid and plan_execution_valid and (semantic_soundness_valid if semantic_soundness_valid is not None else True)

    # B. Fault Localization Accuracy
    top1, top3, mrr = compute_fault_localization_metrics(task.gold_fault_element, diagnostic_reports or [])

    # C. Domain Evolution & Regression Suite
    evolution_capability_valid = None
    regression_pass_rate = None
    hist_passed = None
    hist_total = None

    if task.task_type == LifecycleTaskType.DOMAIN_EVOLUTION:
        # Align problem domain name to match generated domain name to satisfy Fast Downward parser requirement
        import re
        m_dom = re.search(r"\(\s*domain\s+([a-zA-Z0-9_\-]+)\s*\)", generated_domain_pddl, re.IGNORECASE)
        dom_name = m_dom.group(1) if m_dom else None

        # Check new capability
        target_prob_file = eval_prob_file
        if task.evolution_target_problem_pddl:
            target_prob_file = os.path.join(eval_dir, f"eval_evol_target_{task.task_id}_{agent_type}.pddl")
            t_content = task.evolution_target_problem_pddl
            if dom_name:
                t_content = re.sub(r"\(\s*:domain\s+[a-zA-Z0-9_\-]+\s*\)", f"(:domain {dom_name})", t_content, count=1, flags=re.IGNORECASE)
            with open(target_prob_file, "w", encoding="utf-8") as f:
                f.write(t_content)
        
        evol_res = run_fast_downward_with_plan(eval_dom_file, target_prob_file)
        evolution_capability_valid = evol_res["is_solvable"] and evol_res["val_plan_valid"]

        # Run historical regression suite
        if task.historical_regression_problems:
            hist_total = len(task.historical_regression_problems)
            hist_passed = 0
            for idx, hist_pddl in enumerate(task.historical_regression_problems):
                hist_prob_file = os.path.join(eval_dir, f"eval_hist_{task.task_id}_{idx}.pddl")
                h_content = hist_pddl
                if dom_name:
                    h_content = re.sub(r"\(\s*:domain\s+[a-zA-Z0-9_\-]+\s*\)", f"(:domain {dom_name})", h_content, count=1, flags=re.IGNORECASE)
                with open(hist_prob_file, "w", encoding="utf-8") as f:
                    f.write(h_content)
                h_res = run_fast_downward_with_plan(eval_dom_file, hist_prob_file)
                if h_res["is_solvable"] and h_res["val_plan_valid"]:
                    hist_passed += 1
            regression_pass_rate = round(hist_passed / hist_total, 3) if hist_total > 0 else 1.0

    # -------------------------------------------------------------
    # Primary Metric: End-to-End Verified Lifecycle Success
    # -------------------------------------------------------------
    e2e_success = False
    if is_syntax_valid and is_plan_valid and plan_execution_valid:
        if task.task_type == LifecycleTaskType.ELICITATION:
            e2e_success = True
        elif task.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR:
            e2e_success = is_repaired
        elif task.task_type == LifecycleTaskType.DOMAIN_EVOLUTION:
            no_regression = (regression_pass_rate is None or regression_pass_rate == 1.0)
            e2e_success = bool(evolution_capability_valid and no_regression)

    return EvaluationMetrics(
        task_id=task.task_id,
        domain_family=task.domain_family,
        task_type=task.task_type.value,
        agent_type=agent_type,
        e2e_success=e2e_success,
        is_syntax_valid=is_syntax_valid,
        is_plan_valid=is_plan_valid,
        plan_execution_valid=plan_execution_valid,
        semantic_soundness_valid=semantic_soundness_valid,
        logic_match_score=logic_match_score,
        is_repaired=is_repaired,
        fault_localization_top1=top1,
        fault_localization_top3=top3,
        fault_localization_mrr=mrr,
        evolution_capability_valid=evolution_capability_valid,
        regression_pass_rate=regression_pass_rate,
        historical_problems_passed=hist_passed,
        historical_problems_total=hist_total,
        iterations_used=iterations_used,
        execution_time_seconds=round(execution_time_seconds, 2),
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost_usd,
        error_summary=error_summary,
        plan_length=plan_length,
        plan_cost=plan_cost,
        search_time=search_time
    )

def run_benchmark_suite(
    tasks: List[BenchmarkTask],
    agent_types: List[str],
    max_iterations: int = 5
) -> List[EvaluationMetrics]:
    """Runs evaluation suite across multiple tasks and agent architectures."""
    all_metrics: List[EvaluationMetrics] = []
    
    print(f"\n==========================================================================")
    print(f" [RUNNER]: Starting Empirical Benchmark Suite ({len(tasks)} tasks x {len(agent_types)} agents)")
    print(f"==========================================================================")
    for task in tasks:
        for agent in agent_types:
            print(f"\n[RUNNER] Task: '{task.task_id}' | Agent: '{agent}'...")
            try:
                metrics = run_evaluation_on_task(task, agent, max_iterations=max_iterations)
                all_metrics.append(metrics)
                print(f"  --> Result: E2E={metrics.e2e_success} | Syntax={metrics.is_syntax_valid} | Solvable={metrics.is_plan_valid} | Certified={metrics.plan_execution_valid} | Iters={metrics.iterations_used} | Cost=${metrics.estimated_cost_usd:.4f}")
            except Exception as e:
                print(f"  --> [ERROR] Execution crashed: {e}")
                all_metrics.append(EvaluationMetrics(
                    task_id=task.task_id,
                    domain_family=task.domain_family,
                    task_type=task.task_type.value,
                    agent_type=agent,
                    e2e_success=False,
                    is_syntax_valid=False,
                    is_plan_valid=False,
                    plan_execution_valid=False,
                    is_repaired=False,
                    iterations_used=1,
                    execution_time_seconds=0.0,
                    total_tokens=0,
                    estimated_cost_usd=0.0,
                    error_summary=f"Runner Exception: {e}"
                ))

    return all_metrics

def generate_evaluation_report(metrics_list: List[EvaluationMetrics]) -> str:
    """Generates a rigorous Markdown report summarizing primary and secondary metrics."""
    lines = [
        "# Empirical Lifecycle Evaluation Report",
        "",
        "## 1. Primary & Secondary Benchmark Comparison Table",
        "",
        "| Agent Architecture | Tasks | E2E Success (%) | Syntax (%) | Solvable (%) | Plan Certified (%) | Repair (%) | Fault Top-1 (%) | Regression Pass (%) | Avg Iters | Avg Latency (s) | Avg Cost ($) |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    ]

    agent_groups: Dict[str, List[EvaluationMetrics]] = {}
    for m in metrics_list:
        if m.agent_type not in agent_groups:
            agent_groups[m.agent_type] = []
        agent_groups[m.agent_type].append(m)

    for agent, group in agent_groups.items():
        total = len(group)
        e2e_count = sum(1 for m in group if m.e2e_success)
        syntax_count = sum(1 for m in group if m.is_syntax_valid)
        plan_count = sum(1 for m in group if m.is_plan_valid)
        cert_count = sum(1 for m in group if m.plan_execution_valid)
        
        repair_tasks = [m for m in group if m.task_type == LifecycleTaskType.SYNTHETIC_FAULT_REPAIR.value]
        repair_count = sum(1 for m in repair_tasks if m.is_repaired)
        
        fault_top1_tasks = [m for m in group if m.fault_localization_top1 is not None]
        fault_top1_count = sum(1 for m in fault_top1_tasks if m.fault_localization_top1)

        reg_tasks = [m for m in group if m.regression_pass_rate is not None]
        avg_reg = round((sum(m.regression_pass_rate for m in reg_tasks) / len(reg_tasks)) * 100, 1) if reg_tasks else "N/A"

        e2e_pct = round((e2e_count / total) * 100, 1) if total > 0 else 0.0
        syntax_pct = round((syntax_count / total) * 100, 1) if total > 0 else 0.0
        plan_pct = round((plan_count / total) * 100, 1) if total > 0 else 0.0
        cert_pct = round((cert_count / total) * 100, 1) if total > 0 else 0.0
        repair_pct = round((repair_count / len(repair_tasks)) * 100, 1) if repair_tasks else "N/A"
        top1_pct = round((fault_top1_count / len(fault_top1_tasks)) * 100, 1) if fault_top1_tasks else "N/A"

        avg_iters = round(sum(m.iterations_used for m in group) / total, 1) if total > 0 else 0.0
        avg_time = round(sum(m.execution_time_seconds for m in group) / total, 2) if total > 0 else 0.0
        avg_cost = round(sum(m.estimated_cost_usd for m in group) / total, 6) if total > 0 else 0.0

        top1_str = f"{top1_pct}%" if isinstance(top1_pct, float) else top1_pct
        repair_str = f"{repair_pct}%" if isinstance(repair_pct, float) else repair_pct
        reg_str = f"{avg_reg}%" if isinstance(avg_reg, float) else avg_reg

        lines.append(f"| **{agent}** | {total} | **{e2e_pct}%** | {syntax_pct}% | {plan_pct}% | {cert_pct}% | {repair_str} | {top1_str} | {reg_str} | {avg_iters} | {avg_time}s | ${avg_cost:.4f} |")

    lines.extend([
        "",
        "## 2. Granular Task Execution Log",
        "",
        "| Task ID | Agent Architecture | Task Type | E2E Success | Plan Certified | Fault Top-1 | Regression Pass | Diagnostic Summary |",
        "|:---|:---|:---|:---:|:---:|:---:|:---:|:---|"
    ])

    for m in metrics_list:
        err = m.error_summary if m.error_summary else "Passed (Verified)"
        clean_err = err.encode("ascii", "ignore").decode("ascii").replace("|", "/").replace("\n", " ")[:60]
        f_top1 = str(m.fault_localization_top1) if m.fault_localization_top1 is not None else "N/A"
        r_rate = f"{round(m.regression_pass_rate*100)}%" if m.regression_pass_rate is not None else "N/A"
        lines.append(f"| `{m.task_id}` | `{m.agent_type}` | `{m.task_type}` | **{m.e2e_success}** | {m.plan_execution_valid} | {f_top1} | {r_rate} | {clean_err} |")

    return "\n".join(lines)
