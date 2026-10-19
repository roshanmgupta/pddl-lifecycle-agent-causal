import os
import sys
import time
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from glob import glob
from graph import pddl_lifecycle_graph
from tools.symbolic_oracles import run_val_validator, run_fast_downward

BENCHMARK_DIR = "pddl_benchmark_instances/repairer-benchmarks/valid-benchmarks-0.2"

def evaluate_domain_repair(domain_folder_name: str):
    domain_path = os.path.join(BENCHMARK_DIR, domain_folder_name)
    flawed_domain_file = os.path.join(domain_path, "domain-modified.pddl")
    ground_truth_domain_file = os.path.join(domain_path, "domain.pddl")

    if not os.path.exists(flawed_domain_file):
        print(f"[SKIP]: {domain_folder_name} has no domain-modified.pddl")
        return

    # Find first problem file in any benchmark task subdirectory
    subdirs = [d for d in glob(os.path.join(domain_path, "*")) if os.path.isdir(d) and not os.path.basename(d).startswith(".")]
    problem_file = None
    for sub in subdirs:
        p_files = [f for f in glob(os.path.join(sub, "*.pddl")) if not os.path.basename(f).startswith("domain")]
        if p_files:
            problem_file = p_files[0]
            break

    with open(flawed_domain_file, "r", encoding="utf-8") as f:
        flawed_domain_pddl = f.read()

    problem_pddl = ""
    if problem_file and os.path.exists(problem_file):
        with open(problem_file, "r", encoding="utf-8") as f:
            problem_pddl = f.read()

    print(f"\n=======================================================")
    print(f"   EVALUATING DOMAIN: {domain_folder_name}")
    print(f"=======================================================")
    print(f"  Flawed Domain Size: {len(flawed_domain_pddl)} chars")
    if problem_file:
        print(f"  Problem File: {os.path.basename(problem_file)}")

    # Execute 4-Phase Lifecycle Agent
    start_time = time.time()
    initial_state = {
        "requirements": f"Repair flawed domain for {domain_folder_name}",
        "pddl_domain_blueprint": {},
        "pddl_problem_blueprint": {},
        "generated_domain_pddl": flawed_domain_pddl,
        "generated_problem_pddl": problem_pddl,
        "verification_errors": ["VAL Error: Synthetic flaw injected in domain-modified.pddl"],
        "iteration_count": 0,
        "max_iterations": 10
    }

    final_state = pddl_lifecycle_graph.invoke(initial_state)
    elapsed_time = round(time.time() - start_time, 2)

    repaired_domain_pddl = final_state.get("generated_domain_pddl", "")
    iterations = final_state.get("iteration_count", 1)

    # Save output
    os.makedirs("PDDL_file/repaired_ipc_domains", exist_ok=True)
    out_dom_path = f"PDDL_file/repaired_ipc_domains/{domain_folder_name}_repaired.pddl"
    with open(out_dom_path, "w", encoding="utf-8") as f:
        f.write(repaired_domain_pddl)

    # Verify with Oracles
    is_syntax_valid, val_log = run_val_validator(out_dom_path, problem_file if problem_file else out_dom_path)
    is_plan_valid = False
    if is_syntax_valid and problem_file:
        is_plan_valid, fd_log = run_fast_downward(out_dom_path, problem_file)

    print(f"\n  --- REPAIRED PDDL DOMAIN CODE ({domain_folder_name}) ---")
    # print(repaired_domain_pddl)
    print("  ---------------------------------------------------\n")

    print(f"  [RESULT]: Repaired File -> {out_dom_path}")
    print(f"  [METRICS]: Syntax Valid = {is_syntax_valid} | Plan Solvable = {is_plan_valid} | Iterations = {iterations} | Time = {elapsed_time}s")

def main():
    if not os.path.exists(BENCHMARK_DIR):
        print(f"[ERROR]: Benchmark directory '{BENCHMARK_DIR}' not found!")
        sys.exit(1)

    domains = [d for d in os.listdir(BENCHMARK_DIR) if os.path.isdir(os.path.join(BENCHMARK_DIR, d))]
    print(f"[FOUND]: {len(domains)} IPC domains in {BENCHMARK_DIR}")
    for d in domains:
        try:
            evaluate_domain_repair(d)
        except Exception as e:
            print(f"  [ERROR evaluating {d}]: {e}")

if __name__ == "__main__":
    main()
