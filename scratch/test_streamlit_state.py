import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmark.dataset import BENCHMARK_TASKS
from nodes.elicitation import run_elicitation_node
from graph import pddl_lifecycle_graph

selected_task = BENCHMARK_TASKS[1] # blocksworld_repair_missing_precondition_01

initial_domain_bp_input = {
    "domain_name": "blocksworld",
    "requirements": [":strips", ":typing"],
    "types": {"block": "object"},
    "predicates": ["(on ?x - block ?y - block)", "(ontable ?x - block)", "(clear ?x - block)", "(handempty)", "(holding ?x - block)"],
    "actions": [
        {
            "action_name": "pick-up",
            "parameters": {"?x": "block"},
            "preconditions": ["(clear ?x)", "(ontable ?x)"], # FAULT
            "effects": ["(not (ontable ?x))", "(not (clear ?x))", "(not (handempty))", "(holding ?x)"]
        },
        {
            "action_name": "put-down",
            "parameters": {"?x": "block"},
            "preconditions": ["(holding ?x)"],
            "effects": ["(not (holding ?x))", "(clear ?x)", "(handempty)", "(ontable ?x)"]
        }
    ]
}

initial_prob_bp_input = {
    "problem_name": "blocksworld_prob_01",
    "domain_name": "blocksworld",
    "objects": {"a": "block", "b": "block"},
    "initial_state": ["(ontable a)", "(ontable b)", "(clear a)", "(clear b)", "(handempty)"],
    "goal_state": ["(holding a)", "(holding b)"]
}

initial_errors_input = ["VAL Error: Action 'pick-up' asserts negative state effect '(not (handempty))' but fails to declare required precondition constraint 'handempty'."]

initial_state = {
    "requirements": selected_task.natural_language_requirements,
    "pddl_domain_blueprint": initial_domain_bp_input,
    "pddl_problem_blueprint": initial_prob_bp_input,
    "generated_domain_pddl": selected_task.initial_domain_pddl,
    "generated_problem_pddl": getattr(selected_task, "initial_problem_pddl", ""),
    "verification_errors": initial_errors_input,
    "diagnostic_reports": [],
    "formatted_diagnostic_feedback": "",
    "historical_regression_suite": [],
    "iteration_count": 0,
    "max_iterations": 5
}

print("--- Testing run_elicitation_node directly ---")
res_elicit = run_elicitation_node(initial_state)
print("Elicit Returned Domain BP Actions:", len(res_elicit["pddl_domain_blueprint"]["actions"]))

print("\n--- Testing pddl_lifecycle_graph.stream ---")
for output in pddl_lifecycle_graph.stream(initial_state, stream_mode="updates"):
    for node_name, node_output in output.items():
        print(f"Node Executed: {node_name}")
        if node_name == "elicit":
            bp = node_output.get("pddl_domain_blueprint", {})
            print("  Elicit BP Actions count:", len(bp.get("actions", [])))
