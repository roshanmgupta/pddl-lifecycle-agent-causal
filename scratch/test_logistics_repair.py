import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmark.dataset import BENCHMARK_TASKS
from app import parse_pddl_domain_to_blueprint, parse_pddl_problem_to_blueprint
from nodes.elicitation import run_elicitation_node
from graph import pddl_lifecycle_graph

task = BENCHMARK_TASKS[3] # logistics_repair_type_mismatch_01
print("Selected Task:", task.task_id, "| Title:", task.title)

domain_bp = parse_pddl_domain_to_blueprint(task.initial_domain_pddl)
prob_bp = parse_pddl_problem_to_blueprint(task.initial_problem_pddl)

print("Parsed Domain Name:", domain_bp.get("domain_name"))
print("Actions:", [a["action_name"] for a in domain_bp.get("actions", [])])
print("Action parameters for load-truck:", domain_bp["actions"][0]["parameters"])

initial_state = {
    "requirements": task.natural_language_requirements,
    "pddl_domain_blueprint": domain_bp,
    "pddl_problem_blueprint": prob_bp,
    "generated_domain_pddl": task.initial_domain_pddl,
    "generated_problem_pddl": getattr(task, "initial_problem_pddl", ""),
    "verification_errors": [f"Initial fault trigger for {task.task_id}"],
    "diagnostic_reports": [],
    "formatted_diagnostic_feedback": "",
    "historical_regression_suite": [],
    "iteration_count": 0,
    "max_iterations": 5
}

print("\n--- Executing Graph Stream for Logistics Repair Task ---")
for output in pddl_lifecycle_graph.stream(initial_state, stream_mode="updates"):
    for node_name, node_output in output.items():
        print(f"Node Executed: {node_name}")
        if node_name == "elicit":
            bp = node_output.get("pddl_domain_blueprint", {})
            print("  Elicited Domain Name:", bp.get("domain_name"))
            print("  Elicited Actions:", [a["action_name"] for a in bp.get("actions", [])])
