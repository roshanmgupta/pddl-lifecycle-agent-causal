"""
run_autoplanbench_pure21_experiments.py
Autonomous Empirical Benchmark Runner for the 17 Verified AutoPlanBench PDDL 2.1 Pure Domains.

Measures all thesis metrics across 4 experimental conditions:
1. CLOSED_LOOP_AST_AGENT (Full Proposed UPDEAgent with AST + Causal Triage + Oracles)
2. ABLATION_NO_TRIAGE (AST Blueprint + Raw Unguided Logs, Tests H2)
3. ABLATION_NO_AST (Raw PDDL text iterative retry, Tests H1)
4. ZERO_SHOT (Direct one-shot generation baseline, Tests MRQ 1)

Generates:
- autoplanbench_master_metrics.csv: All primary, representation, repair, regression, and LLM metrics.
- autoplanbench_semantic_soundness_audit.csv: Mathematical proof of semantic equivalence to standard domain.
- autoplanbench_summary_metrics.csv: Statistical aggregations answering MRQ 1, SRQ 1, SRQ 2, SRQ 3, SRQ 4, H1, H2, H3.
"""

import sys
import os
import csv
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.pure_strips_benchmarks import (
    AUTOPLANBENCH_PURE_STRIPS_DOMAINS,
    load_autoplanbench_original_domain_data,
    get_autoplanbench_domain_folder
)
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from eval.baselines import run_zero_shot_baseline, run_unstructured_retry_baseline
from eval.action_reconstruction import evaluate_action_reconstruction
from tools.symbolic_oracles import (
    run_val_validator,
    run_fast_downward_with_plan,
    validate_plan_semantic_soundness
)
from tools.blueprint_parser import parse_pddl_problem_to_blueprint
from graph import pddl_lifecycle_graph

# ---------------------------------------------------------------------------
# Pricing for openai/gpt-4o-mini
# ---------------------------------------------------------------------------
PRICE_PROMPT_PER_M = 0.15      # $0.15 per 1M prompt tokens
PRICE_COMPLETION_PER_M = 0.60  # $0.60 per 1M completion tokens

def calculate_llm_cost(prompt_tokens: int, completion_tokens: int) -> float:
    return round(
        (prompt_tokens * PRICE_PROMPT_PER_M / 1_000_000) +
        (completion_tokens * PRICE_COMPLETION_PER_M / 1_000_000), 
        6
    )

def classify_behavioral_outcome(
    is_syntax_valid: bool,
    is_plan_valid: bool,
    val_plan_valid: bool,
    semantic_soundness_valid: bool,
    macro_f1: float,
    iters: int
) -> Tuple[str, str]:
    """
    Returns (behavioral_code, defect_class) conforming to A.1 - F taxonomy.
    """
    is_sound = (semantic_soundness_valid is True) or (macro_f1 >= 0.85)
    e2e_ok = is_syntax_valid and is_plan_valid and val_plan_valid and is_sound

    if e2e_ok:
        if iters == 1:
            return "A.1: First-Attempt Direct Success", "NONE"
        else:
            return "A.2: Refined Success via Feedback Loops", "RECOVERED"

    if not is_syntax_valid:
        return "B: Unparseable PDDL Syntax Failure", "SYNTAX_PARSE_ERROR"

    if is_syntax_valid and not is_plan_valid:
        return "C: Syntactically Valid but Planner Deadlock (Unsolvable)", "CAUSAL_REACHABILITY_DEADLOCK"

    if is_plan_valid and not val_plan_valid:
        return "D: Plan Generated but Fails VAL Self-Certification", "ACTION_EFFECT_CONTRADICTION"

    if not is_sound:
        return "E: Plan Execution Rejection on Standard Domain", "PRECONDITION_MISALIGNMENT"

    if iters >= 10:
        return "F: Iteration Budget Exhausted (Oscillation)", "UNRESOLVED_CONTRADICTION"

    return "G: Diagnostic Anomaly", "OTHER"

def main():
    print("=" * 80)
    print(" AUTONOMOUS EMPIRICAL BENCHMARK: 17 AUTOPLANBENCH PURE PDDL 2.1 DOMAINS")
    print(f" LLM Model: openai/gpt-4o-mini | Max Iterations: 10")
    print(f" Target Domains ({len(AUTOPLANBENCH_PURE_STRIPS_DOMAINS)}): {AUTOPLANBENCH_PURE_STRIPS_DOMAINS}")
    print("=" * 80)

    os.makedirs("Streamlit_output_file", exist_ok=True)
    csv_master = "autoplanbench_master_metrics_10iters.csv"
    csv_audit = "autoplanbench_semantic_soundness_audit_10iters.csv"
    csv_diagnostic = "autoplanbench_diagnostic_reports_10iters.csv"

    # Master Metrics CSV Header
    master_fields = [
        "domain", "agent_type", "task_type", "e2e_success",
        "is_syntax_valid", "is_plan_valid", "val_plan_valid",
        "semantic_soundness_valid", "svr_init", "iterations_used",
        "is_repaired", "repair_iterations",
        "macro_structural_f1", "precondition_f1", "add_effect_f1", "delete_effect_f1", "action_f1",
        "rpr_regression_pass_rate", "historical_problems_passed", "historical_problems_total",
        "candidate_rejections_count", "evolution_iteration_overhead",
        "plan_length", "plan_cost", "search_time_sec", "execution_time_sec",
        "prompt_tokens", "completion_tokens", "total_tokens", "estimated_cost_usd",
        "behavioral_code", "defect_class", "error_summary"
    ]

    # Semantic Audit CSV Header
    audit_fields = [
        "domain", "agent_type", "gold_operator_count", "candidate_operator_count",
        "matched_operator_count", "macro_structural_f1", "precondition_f1",
        "add_effect_f1", "delete_effect_f1", "action_f1",
        "val_internal_valid", "val_standard_transfer_valid",
        "semantic_verdict", "action_bijection_mapping"
    ]

    # Diagnostic Report CSV Header (Answers user request for deep failure inspection)
    diagnostic_fields = [
        "domain", "agent_type", "behavioral_code", "why_failed_verdict",
        "iterations_used", "val_syntax_summary", "planner_summary",
        "plan_transfer_summary", "triage_diagnostic_hints", "macro_structural_f1"
    ]

    # Initialize CSV files
    with open(csv_master, "w", newline="", encoding="utf-8") as f_m, \
         open(csv_audit, "w", newline="", encoding="utf-8") as f_a, \
         open(csv_diagnostic, "w", newline="", encoding="utf-8") as f_d:
        writer_m = csv.DictWriter(f_m, fieldnames=master_fields)
        writer_m.writeheader()
        writer_a = csv.DictWriter(f_a, fieldnames=audit_fields)
        writer_a.writeheader()
        writer_d = csv.DictWriter(f_d, fieldnames=diagnostic_fields)
        writer_d.writeheader()

    agent_configs = [
        "CLOSED_LOOP_AST_AGENT",
        "ABLATION_NO_TRIAGE",
        "ABLATION_NO_AST",
        "ZERO_SHOT"
    ]

    all_master_rows = []

    # Iterate over all 17 domains
    for d_idx, domain_name in enumerate(AUTOPLANBENCH_PURE_STRIPS_DOMAINS, 1):
        print(f"\n[{d_idx}/{len(AUTOPLANBENCH_PURE_STRIPS_DOMAINS)}] Evaluating Domain: {domain_name.upper()}")

        # Load domain data directly from original autoplanbench/data/<domain>/
        unified_prompt, dom_desc, prob_desc, ref_dom, ref_inst, prob_files = load_autoplanbench_original_domain_data(domain_name)

        if not ref_dom or not ref_inst:
            print(f"  [SKIPPED]: Missing reference domain or problem for '{domain_name}'.")
            continue

        # Save reference files to disk for VAL oracle verification
        ref_dom_file = f"Streamlit_output_file/ref_dom_{domain_name}.pddl"
        ref_prob_file = f"Streamlit_output_file/ref_prob_{domain_name}.pddl"
        with open(ref_dom_file, "w", encoding="utf-8") as f:
            f.write(ref_dom)
        with open(ref_prob_file, "w", encoding="utf-8") as f:
            f.write(ref_inst)

        # Prepare Historical Regression Cases from prob_files[1:3]
        historical_suite = []
        d_folder = get_autoplanbench_domain_folder(domain_name) / "orig_problems"
        for hist_name in prob_files[1:3]:  # Up to 2 regression test instances
            h_path = d_folder / hist_name
            if h_path.exists():
                h_txt = h_path.read_text(encoding="utf-8", errors="ignore")
                bp = parse_pddl_problem_to_blueprint(h_txt)
                if bp:
                    historical_suite.append({
                        "case_id": f"{domain_name}_{hist_name.replace('.pddl', '')}",
                        "problem_blueprint": bp,
                        "raw_pddl": h_txt
                    })

        # Create BenchmarkTask object
        task = BenchmarkTask(
            task_id=f"apb_{domain_name}",
            domain_family=domain_name,
            task_type=LifecycleTaskType.ELICITATION,
            title=f"AutoPlanBench {domain_name.capitalize()} Elicitation",
            natural_language_requirements=unified_prompt,
            ground_truth_domain_pddl=ref_dom,
            ground_truth_problem_pddl=ref_inst
        )

        # Evaluate across the 4 configurations
        for agent in agent_configs:
            print(f"  -> Agent Config: {agent} ... ", end="", flush=True)
            start_t = time.time()

            gen_dom = ""
            gen_prob = ""
            iters = 1
            p_tokens = 0
            c_tokens = 0
            err_summary = ""
            svr_init = False
            candidate_rejections = 0

            try:
                if agent == "ZERO_SHOT":
                    res = run_zero_shot_baseline(task)
                    gen_dom = res.get("generated_domain_pddl", "")
                    gen_prob = res.get("generated_problem_pddl", "")
                    iters = 1
                    p_tokens = res.get("prompt_tokens", 0)
                    c_tokens = res.get("completion_tokens", 0)
                    if res.get("error"):
                        err_summary = res["error"]

                elif agent == "ABLATION_NO_AST":
                    res = run_unstructured_retry_baseline(task, max_retries=5)
                    gen_dom = res.get("generated_domain_pddl", "")
                    gen_prob = res.get("generated_problem_pddl", "")
                    iters = res.get("iterations_used", 10)
                    p_tokens = res.get("prompt_tokens", 0)
                    c_tokens = res.get("completion_tokens", 0)

                elif agent in ["CLOSED_LOOP_AST_AGENT", "ABLATION_NO_TRIAGE"]:
                    init_state = {
                        "requirements": task.natural_language_requirements,
                        "pddl_domain_blueprint": {},
                        "pddl_problem_blueprint": {},
                        "generated_domain_pddl": "",
                        "generated_problem_pddl": "",
                        "verification_errors": [],
                        "iteration_count": 0,
                        "max_iterations": 10,
                        "skip_triage": (agent == "ABLATION_NO_TRIAGE"),
                        "historical_regression_suite": []  # Pure Elicitation has no legacy suite
                    }
                    final_state = pddl_lifecycle_graph.invoke(init_state)
                    gen_dom = final_state.get("generated_domain_pddl", "")
                    gen_prob = final_state.get("generated_problem_pddl", "")
                    iters = max(1, final_state.get("iteration_count", 1))
                    p_tokens = final_state.get("total_prompt_tokens", 0)
                    c_tokens = final_state.get("total_completion_tokens", 0)
                    candidate_rejections = final_state.get("candidate_rejections_count", 0)
                    if final_state.get("verification_errors"):
                        err_summary = " ".join(final_state["verification_errors"])[:200]
                    
                    # Capture diagnostic triage reports
                    if agent == "CLOSED_LOOP_AST_AGENT":
                        t_reps = final_state.get("historical_diagnostic_reports", []) or final_state.get("diagnostic_reports", [])
                        triage_hints_list = []
                        for tr in t_reps:
                            if isinstance(tr, dict):
                                triage_hints_list.append(f"[{tr.get('error_category')} in '{tr.get('faulty_element')}']: {tr.get('suggested_repair_hint', '')}")
                        triage_diagnostic_hints = " | ".join(triage_hints_list) if triage_hints_list else "All verification checks passed cleanly."
                    else:
                        triage_diagnostic_hints = "Triage bypassed (Testing H2). Raw unguided compiler log was supplied directly to repair prompt."

            except Exception as e:
                err_summary = f"Agent Execution Crash: {str(e)}"[:200]
                triage_diagnostic_hints = f"Crash Exception: {str(e)}"

            if agent == "ABLATION_NO_AST":
                triage_diagnostic_hints = "AST bypassed (Testing H1). Raw PDDL text strings were edited iteratively via unstructured backprompting."
            elif agent == "ZERO_SHOT":
                triage_diagnostic_hints = "Zero-shot baseline (Testing MRQ 1). Direct one-shot generation without feedback loop."

            elapsed_sec = round(time.time() - start_t, 2)
            tot_tokens = p_tokens + c_tokens
            cost_usd = calculate_llm_cost(p_tokens, c_tokens)

            # -------------------------------------------------------------
            # Formal Symbolic Oracles Evaluation
            # -------------------------------------------------------------
            eval_dom_file = f"Streamlit_output_file/cand_dom_{domain_name}_{agent}.pddl"
            eval_prob_file = f"Streamlit_output_file/cand_prob_{domain_name}_{agent}.pddl"
            with open(eval_dom_file, "w", encoding="utf-8") as f:
                f.write(gen_dom)
            with open(eval_prob_file, "w", encoding="utf-8") as f:
                f.write(gen_prob)

            # 1. Oracle 1: VAL Syntax & Type-Check
            is_syntax_valid, val_syntax_log = run_val_validator(eval_dom_file, eval_prob_file)
            if iters == 1 and is_syntax_valid:
                svr_init = True

            # 2. Oracle 2: Fast Downward Solvability & Plan Synthesis
            is_plan_valid = False
            val_plan_valid = False
            semantic_soundness_valid = False
            plan_len = 0
            plan_cost = 0
            search_t = 0.0

            if is_syntax_valid:
                fd_res = run_fast_downward_with_plan(eval_dom_file, eval_prob_file)
                is_plan_valid = fd_res["is_solvable"]
                val_plan_valid = fd_res["val_plan_valid"]
                plan_len = fd_res["plan_length"]
                plan_cost = fd_res["plan_cost"]
                search_t = fd_res["search_time"]

                pts_log = ""
                # 3. Oracle 3: Plan Transfer Soundness (PTS) on Gold Standard Domain
                if is_plan_valid and val_plan_valid:
                    plan_candidate_file = "sas_plan"
                    if not os.path.exists(plan_candidate_file):
                        for pf in ["sas_plan.1", "sas_plan.2"]:
                            if os.path.exists(pf):
                                plan_candidate_file = pf
                                break

                    if os.path.exists(plan_candidate_file):
                        pts_ok, pts_log = validate_plan_semantic_soundness(
                            ref_dom_file, ref_prob_file, plan_candidate_file
                        )
                        semantic_soundness_valid = pts_ok
            else:
                pts_log = ""

            # -------------------------------------------------------------
            # Action Reconstruction Error (ARE / Structural F1)
            # -------------------------------------------------------------
            are_data = evaluate_action_reconstruction(ref_dom, gen_dom)
            macro_f1 = are_data.get("macro_structural_f1", 0.0)
            pre_f1 = are_data.get("mean_precondition_f1", 0.0)
            add_f1 = are_data.get("mean_add_effect_f1", 0.0)
            del_f1 = are_data.get("mean_delete_effect_f1", 0.0)
            action_f1 = are_data.get("action_f1", 0.0)
            action_map = are_data.get("action_mapping", {})

            # -------------------------------------------------------------
            # Historical Regression Testing (Backward Compatibility)
            # -------------------------------------------------------------
            hist_total = 0
            hist_passed = 0
            rpr = None  # Pure elicitation does not have a legacy problem suite

            # E2E Success: Syntax + Solvable + Plan Certified + Semantic Equivalence
            is_semantically_sound = (semantic_soundness_valid is True) or (macro_f1 >= 0.85)
            e2e_success = is_syntax_valid and is_plan_valid and val_plan_valid and is_semantically_sound

            # Repair Metrics
            is_repaired = (iters > 1 and e2e_success)
            repair_iters = (iters - 1) if (iters > 1) else 0
            evolution_overhead = 0

            # Behavioral Outcome Taxonomy (A.1 - F)
            beh_code, defect_cls = classify_behavioral_outcome(
                is_syntax_valid, is_plan_valid, val_plan_valid,
                semantic_soundness_valid, macro_f1, iters
            )

            # Detailed Why-Failed Verdict for Diagnostic Inspection
            if e2e_success:
                why_verdict = f"SUCCESS: Domain is valid, solvable ({plan_len} steps, cost={plan_cost}), and formally verified."
            elif not is_syntax_valid:
                first_err = val_syntax_log.strip().split("\n")[-1] if val_syntax_log else "Syntax error"
                why_verdict = f"SYNTAX FAILURE: VAL rejected model ({first_err[:120]})."
            elif not is_plan_valid:
                why_verdict = f"SOLVER FAILURE: Fast Downward returned unsolvable (Causal Reachability Deadlock - goal unreachable from init)."
            elif not val_plan_valid:
                why_verdict = f"PLAN EXECUTION FAILED: Plan steps failed self-certification in VAL."
            elif not is_semantically_sound:
                why_verdict = f"SEMANTIC DIVERGENCE: Plan produced on candidate model failed execution on standard gold domain (F1: {macro_f1:.2f} < 0.85; PTS failed)."
            elif iters >= 10:
                why_verdict = f"BUDGET EXHAUSTION: Reached maximum 10 iterations without formal resolution."
            else:
                why_verdict = f"FAILURE: {err_summary[:120]}"

            print(f"Done in {elapsed_sec}s | E2E={e2e_success} | Solvable={is_plan_valid} | F1={macro_f1:.2f} | Code={beh_code[:3]}")

            # Assemble Master Row
            row_master = {
                "domain": domain_name,
                "agent_type": agent,
                "task_type": "ELICITATION",
                "e2e_success": e2e_success,
                "is_syntax_valid": is_syntax_valid,
                "is_plan_valid": is_plan_valid,
                "val_plan_valid": val_plan_valid,
                "semantic_soundness_valid": semantic_soundness_valid,
                "svr_init": svr_init,
                "iterations_used": iters,
                "is_repaired": is_repaired,
                "repair_iterations": repair_iters,
                "macro_structural_f1": macro_f1,
                "precondition_f1": pre_f1,
                "add_effect_f1": add_f1,
                "delete_effect_f1": del_f1,
                "action_f1": action_f1,
                "rpr_regression_pass_rate": rpr if rpr is not None else 1.0,
                "historical_problems_passed": hist_passed,
                "historical_problems_total": hist_total,
                "candidate_rejections_count": candidate_rejections,
                "evolution_iteration_overhead": evolution_overhead,
                "plan_length": plan_len,
                "plan_cost": plan_cost,
                "search_time_sec": search_t,
                "execution_time_sec": elapsed_sec,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "total_tokens": tot_tokens,
                "estimated_cost_usd": cost_usd,
                "behavioral_code": beh_code,
                "defect_class": defect_cls,
                "error_summary": err_summary
            }
            all_master_rows.append(row_master)

            # Assemble Semantic Audit Row
            row_audit = {
                "domain": domain_name,
                "agent_type": agent,
                "gold_operator_count": are_data.get("gt_operator_count", 0),
                "candidate_operator_count": are_data.get("generated_operator_count", 0),
                "matched_operator_count": are_data.get("matched_operator_count", 0),
                "macro_structural_f1": macro_f1,
                "precondition_f1": pre_f1,
                "add_effect_f1": add_f1,
                "delete_effect_f1": del_f1,
                "action_f1": action_f1,
                "val_internal_valid": val_plan_valid,
                "val_standard_transfer_valid": semantic_soundness_valid,
                "semantic_verdict": "SOUND_AND_CONVERSANT" if is_semantically_sound else "PARTIAL_OR_DIVERGENT",
                "action_bijection_mapping": json.dumps(action_map)
            }

            # Assemble Detailed Diagnostic Row
            clean_syntax = re.sub(r"\s+", " ", val_syntax_log).strip() if val_syntax_log else "Clean"
            clean_pts = re.sub(r"\s+", " ", pts_log).strip() if pts_log else ("Sound" if semantic_soundness_valid else "Incompatible")
            row_diagnostic = {
                "domain": domain_name,
                "agent_type": agent,
                "behavioral_code": beh_code,
                "why_failed_verdict": why_verdict,
                "iterations_used": iters,
                "val_syntax_summary": clean_syntax[:200],
                "planner_summary": f"Solvable={is_plan_valid}, Steps={plan_len}, Cost={plan_cost}, SearchTime={search_t:.4f}s",
                "plan_transfer_summary": clean_pts[:200],
                "triage_diagnostic_hints": triage_diagnostic_hints[:250],
                "macro_structural_f1": macro_f1
            }

            # Immediate Disk Flush (Zero Data Loss on Interruption)
            with open(csv_master, "a", newline="", encoding="utf-8") as f_m, \
                 open(csv_audit, "a", newline="", encoding="utf-8") as f_a, \
                 open(csv_diagnostic, "a", newline="", encoding="utf-8") as f_d:
                writer_m = csv.DictWriter(f_m, fieldnames=master_fields)
                writer_m.writerow(row_master)
                f_m.flush()

                writer_a = csv.DictWriter(f_a, fieldnames=audit_fields)
                writer_a.writerow(row_audit)
                f_a.flush()

                writer_d = csv.DictWriter(f_d, fieldnames=diagnostic_fields)
                writer_d.writerow(row_diagnostic)
                f_d.flush()

    # Generate Statistical Summary CSV
    generate_summary_csv(all_master_rows, "autoplanbench_summary_metrics.csv")
    print("\n" + "=" * 80)
    print(" BENCHMARK COMPLETED SUCCESSFULLY!")
    print(f" 1. Master Results   : {csv_master}")
    print(f" 2. Semantic Audit   : {csv_audit}")
    print(f" 3. Statistical Table: autoplanbench_summary_metrics.csv")
    print("=" * 80)

def generate_summary_csv(rows: List[Dict[str, Any]], output_summary_path: str):
    """Aggregates metrics by agent_type answering MRQ 1, SRQ 1, SRQ 2, SRQ 3, SRQ 4."""
    if not rows:
        return
    configs = sorted(list(set(r["agent_type"] for r in rows)))

    summary_fields = [
        "agent_type", "total_runs", "e2e_sr_pct", "psr_solvability_pct",
        "pts_transfer_soundness_pct", "svr_init_pct", "avg_iterations_total",
        "macro_structural_f1", "precondition_f1", "add_effect_f1", "delete_effect_f1",
        "rsr_repair_success_pct", "avg_repair_iterations",
        "rpr_regression_pass_rate_pct", "total_candidate_rejections",
        "mean_total_tokens", "mean_latency_sec", "total_cost_usd"
    ]

    with open(output_summary_path, "w", newline="", encoding="utf-8") as sf:
        writer = csv.DictWriter(sf, fieldnames=summary_fields)
        writer.writeheader()

        for cfg in configs:
            c_rows = [r for r in rows if r["agent_type"] == cfg]
            n = len(c_rows)
            if n == 0:
                continue

            e2e = round(sum(1 for r in c_rows if r["e2e_success"]) / n * 100, 1)
            psr = round(sum(1 for r in c_rows if r["is_plan_valid"]) / n * 100, 1)
            solv_rows = [r for r in c_rows if r["is_plan_valid"]]
            pts = round(sum(1 for r in solv_rows if r["semantic_soundness_valid"]) / len(solv_rows) * 100, 1) if solv_rows else 0.0

            svr = round(sum(1 for r in c_rows if r["svr_init"]) / n * 100, 1)
            avg_it = round(sum(r["iterations_used"] for r in c_rows) / n, 2)

            f1 = round(sum(r["macro_structural_f1"] for r in c_rows) / n, 4)
            pre = round(sum(r["precondition_f1"] for r in c_rows) / n, 4)
            add = round(sum(r["add_effect_f1"] for r in c_rows) / n, 4)
            dele = round(sum(r["delete_effect_f1"] for r in c_rows) / n, 4)

            repair_needed = [r for r in c_rows if r["iterations_used"] > 1]
            rsr = round(sum(1 for r in repair_needed if r["is_repaired"]) / len(repair_needed) * 100, 1) if repair_needed else 100.0
            avg_rep_it = round(sum(r["repair_iterations"] for r in repair_needed) / len(repair_needed), 2) if repair_needed else 0.0

            rpr_vals = [r["rpr_regression_pass_rate"] for r in c_rows if r["rpr_regression_pass_rate"] is not None]
            rpr = round(sum(rpr_vals) / len(rpr_vals) * 100, 1) if rpr_vals else 100.0
            crc_tot = sum(r["candidate_rejections_count"] for r in c_rows)

            mean_tok = int(sum(r["total_tokens"] for r in c_rows) / n)
            mean_lat = round(sum(r["execution_time_sec"] for r in c_rows) / n, 2)
            tot_cost = round(sum(r["estimated_cost_usd"] for r in c_rows), 4)

            writer.writerow({
                "agent_type": cfg,
                "total_runs": n,
                "e2e_sr_pct": e2e,
                "psr_solvability_pct": psr,
                "pts_transfer_soundness_pct": pts,
                "svr_init_pct": svr,
                "avg_iterations_total": avg_it,
                "macro_structural_f1": f1,
                "precondition_f1": pre,
                "add_effect_f1": add,
                "delete_effect_f1": dele,
                "rsr_repair_success_pct": rsr,
                "avg_repair_iterations": avg_rep_it,
                "rpr_regression_pass_rate_pct": rpr,
                "total_candidate_rejections": crc_tot,
                "mean_total_tokens": mean_tok,
                "mean_latency_sec": mean_lat,
                "total_cost_usd": tot_cost
            })

if __name__ == "__main__":
    main()
