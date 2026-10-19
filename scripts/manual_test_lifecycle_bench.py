"""
Manual Interactive Test Runner for PDDLLifeCycleBench Flaws & Evolution.

Allows manual testing of any curated flaw or evolution task without running batch experiments.
Executes the closed-loop agent (Phase 2, Phase 3, Phase 4) and displays diagnostic reports,
repaired code, and symbolic oracle verifications.
"""

import sys
import argparse
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from benchmark.loader import (
    list_benchmark_domains,
    list_domain_flaws,
    list_domain_evolutions,
    load_flaw_task,
    load_evolution_task
)
from graph import pddl_lifecycle_graph
from tools.symbolic_oracles import run_val_validator, run_fast_downward

def run_manual_flaw_test(domain_name: str, flaw_name: str, max_iterations: int = 5):
    print("=" * 80)
    print(f"MANUAL TEST: Flaw Repair on {domain_name} -> {flaw_name}")
    print("=" * 80)

    task = load_flaw_task(domain_name, flaw_name)
    if not task:
        print(f"[ERROR]: Flaw '{flaw_name}' not found for domain '{domain_name}'.")
        return

    print(f"  Domain Family:    {task.domain_family}")
    print(f"  Fault Category:   {task.fault_category}")
    print(f"  Target Action:    {task.gold_fault_element}")
    print(f"  Expected Fix:     {task.expected_repair_behavior}")
    print(f"  Initial Domain:   {len(task.initial_domain_pddl)} chars")
    print(f"  Initial Problem:  {len(task.initial_problem_pddl)} chars")
    print("-" * 80)

    initial_state = {
        "requirements": task.natural_language_requirements,
        "pddl_domain_blueprint": {},
        "pddl_problem_blueprint": {},
        "generated_domain_pddl": task.initial_domain_pddl,
        "generated_problem_pddl": task.initial_problem_pddl,
        "verification_errors": [f"Initial Oracle Signal: Fault category {task.fault_category} detected."],
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "skip_triage": False
    }

    start_time = time.time()
    print("\n[INFO]: Invoking Closed-Loop Lifecycle Agent (Phase 2 -> Phase 3 -> Repair)...")
    final_state = pddl_lifecycle_graph.invoke(initial_state)
    elapsed = round(time.time() - start_time, 2)

    repaired_dom = final_state.get("generated_domain_pddl", "")
    repaired_prob = final_state.get("generated_problem_pddl", "")
    iterations = final_state.get("iteration_count", 1)
    diag_reports = final_state.get("diagnostic_reports", []) or final_state.get("historical_diagnostic_reports", [])

    print("\n" + "=" * 80)
    print("DIAGNOSTIC TRIAGE SUMMARY (Fault Localization)")
    print("=" * 80)
    if diag_reports:
        for idx, r in enumerate(diag_reports, 1):
            faulty = getattr(r, "faulty_element", "") if hasattr(r, "faulty_element") else str(r.get("faulty_element", ""))
            expl = getattr(r, "explanation", "") if hasattr(r, "explanation") else str(r.get("explanation", ""))
            print(f"  [Suspect #{idx}]: {faulty}")
            if expl:
                print(f"     Explanation: {expl[:120]}...")
    else:
        print("  (No diagnostic issues reported or errors resolved)")

    # Save outputs for inspection
    out_dir = PROJECT_ROOT / "Streamlit_output_file" / "manual_tests" / f"{domain_name}_{flaw_name}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dom_path = out_dir / "domain_repaired.pddl"
    out_prob_path = out_dir / "problem.pddl"
    out_dom_path.write_text(repaired_dom, encoding="utf-8")
    out_prob_path.write_text(repaired_prob, encoding="utf-8")

    # Oracle verification
    val_valid, val_log = run_val_validator(str(out_dom_path), str(out_prob_path))
    fd_valid = False
    if val_valid:
        fd_valid, fd_log = run_fast_downward(str(out_dom_path), str(out_prob_path))

    print("\n" + "=" * 80)
    print("ORACLE VERIFICATION RESULTS")
    print("=" * 80)
    print(f"  Iterations Used:        {iterations} / {max_iterations}")
    print(f"  Execution Time:         {elapsed}s")
    print(f"  Syntax / VAL Valid:     {val_valid}")
    print(f"  Fast Downward Solvable: {fd_valid}")
    print(f"  Repaired Domain Saved:  {out_dom_path}")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Manual test runner for PDDLLifeCycleBench flaws and evolutions.")
    parser.add_argument("--domain", type=str, default=None, help="Domain name (e.g. barman14-bfs, blocksworld, depot)")
    parser.add_argument("--flaw", type=str, default=None, help="Flaw name (e.g. flaw_01_type_signature_arity, flaw_03_action_effect_deletion)")
    parser.add_argument("--evolution", type=str, default=None, help="Evolution task name (e.g. evolution_01_feature_addition)")
    parser.add_argument("--list", action="store_true", help="List all available domains, flaws, and evolutions.")
    args = parser.parse_args()

    domains = list_benchmark_domains()

    if args.list or not args.domain:
        print("=" * 80)
        print(f"PDDLLifeCycleBench: {len(domains)} Canonical Domains Available")
        print("=" * 80)
        for d in domains:
            flaws = list_domain_flaws(d)
            evos = list_domain_evolutions(d)
            print(f"• {d:28} | Flaws: {len(flaws)} | Evolution: {len(evos)}")
        print("\nUsage example:")
        print("  python scripts/manual_test_lifecycle_bench.py --domain barman14-bfs --flaw flaw_03_action_effect_deletion")
        return

    if args.domain not in domains:
        print(f"[ERROR]: Unknown domain '{args.domain}'. Choose from:\n{domains}")
        return

    flaws = list_domain_flaws(args.domain)
    evos = list_domain_evolutions(args.domain)

    if args.flaw:
        run_manual_flaw_test(args.domain, args.flaw)
    elif args.evolution:
        print(f"Evolution task manual testing selected: {args.domain} -> {args.evolution}")
        task = load_evolution_task(args.domain, args.evolution)
        if task:
            print(f"  Task ID: {task.task_id}")
            print(f"  Requirements:\n{task.natural_language_requirements}")
            print(f"  Historical regression problem count: {len(task.historical_regression_problems)}")
    else:
        print(f"Available Flaws for '{args.domain}':")
        for f in flaws:
            print(f"  --flaw {f}")
        print(f"\nAvailable Evolution tasks for '{args.domain}':")
        for e in evos:
            print(f"  --evolution {e}")

if __name__ == "__main__":
    main()
