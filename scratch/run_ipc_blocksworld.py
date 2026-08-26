import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from benchmark.dataset import BENCHMARK_TASKS
from graph import pddl_lifecycle_graph

def run_ipc_blocksworld_test():
    print("========================================================================")
    print("   AUTOMATED END-TO-END IPC BENCHMARK TEST: BLOCKSWORLD_ELICITATION_01  ")
    print("========================================================================\n")

    # Find blocksworld_elicitation_01 from official dataset
    task = next((t for t in BENCHMARK_TASKS if t.task_id == "blocksworld_elicitation_01"), None)
    if not task:
        print("❌ Error: Task 'blocksworld_elicitation_01' not found in benchmark/dataset.py")
        sys.exit(1)

    print(f"Task ID: {task.task_id}")
    print(f"Domain Family: {task.domain_family}")
    print(f"Task Title: {task.title}\n")
    print("--- NATURAL LANGUAGE IPC REQUIREMENTS ---")
    print(task.natural_language_requirements.strip())
    print("-" * 50 + "\n")

    # Define historical problem case for Phase 4 maintenance verification
    historical_problem_blueprint = {
        "problem_name": "blocksworld_prob_hist_01",
        "domain_name": "blocksworld",
        "objects": {"a": "block", "b": "block"},
        "initial_state": ["(ontable a)", "(ontable b)", "(clear a)", "(clear b)", "(handempty)"],
        "goal_state": ["(holding a)"]
    }

    initial_state = {
        "requirements": task.natural_language_requirements,
        "pddl_domain_blueprint": {},
        "pddl_problem_blueprint": {},
        "generated_domain_pddl": "",
        "generated_problem_pddl": "",
        "verification_errors": [],
        "diagnostic_reports": [],
        "formatted_diagnostic_feedback": "",
        "historical_regression_suite": [
            {
                "case_id": "blocksworld_hist_01",
                "problem_blueprint": historical_problem_blueprint
            }
        ],
        "iteration_count": 0,
        "max_iterations": 5
    }

    print("[RUNNER] Invoking Full Agentic Lifecycle Graph across all 5 Nodes...\n")
    final_state = pddl_lifecycle_graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print(" 1. EXTRACTED RELATIONAL DOMAIN BLUEPRINT (PHASE 1 AST)")
    print("=" * 70)
    print(json.dumps(final_state.get("pddl_domain_blueprint", {}), indent=2))

    print("\n" + "=" * 70)
    print(" 2. EXTRACTED RELATIONAL PROBLEM BLUEPRINT (PHASE 1 AST)")
    print("=" * 70)
    print(json.dumps(final_state.get("pddl_problem_blueprint", {}), indent=2))

    print("\n" + "=" * 70)
    print(" 3. OPTION B PROGRAMMATICALLY COMPILED DOMAIN PDDL (PHASE 2)")
    print("=" * 70)
    print(final_state.get("generated_domain_pddl", ""))

    print("\n" + "=" * 70)
    print(" 4. OPTION B PROGRAMMATICALLY COMPILED PROBLEM PDDL (PHASE 2)")
    print("=" * 70)
    print(final_state.get("generated_problem_pddl", ""))

    print("\n" + "=" * 70)
    print(" 5. PHASE 3 & PHASE 4 VERIFICATION RESULTS")
    print("=" * 70)
    errors = final_state.get("verification_errors", [])
    reports = final_state.get("diagnostic_reports", [])
    
    if not errors and not reports:
        print("[SUCCESS]: Blocksworld domain & problem passed all Oracles and Phase 4 Maintenance Checks!")
    else:
        print(f"[WARNING]: Validation found {len(errors)} issues:")
        for err in errors:
            print(f"  - {err}")

    print("\n========================================================================")
    print(" [SUCCESS] IPC BLOCKSWORLD END-TO-END WORKFLOW VERIFICATION COMPLETED!")
    print("========================================================================")

if __name__ == "__main__":
    run_ipc_blocksworld_test()
