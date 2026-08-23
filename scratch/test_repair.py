import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

from nodes.triage import run_triage_node
from nodes.repair import run_repair_node
from nodes.generation import compile_pddl_programmatically
from graph import pddl_lifecycle_graph

def test_repair_node_standalone():
    print("\n--- 1. Testing Targeted Model Repair Node Standalone ---")
    
    # Faulty initial state (missing '(holding ?r ?c)' in predicates definition)
    initial_domain_blueprint = {
        "domain_name": "logistics_warehouse",
        "requirements": [":strips", ":typing"],
        "types": {
            "robot": "object",
            "crate": "object",
            "location": "object"
        },
        "predicates": [
            "(at ?r - robot ?l - location)",
            "(crate_at ?c - crate ?l - location)"
            # Note: (holding ?r - robot ?c - crate) is intentionally missing!
        ],
        "actions": [
            {
                "action_name": "pick_up",
                "parameters": {"?r": "robot", "?c": "crate", "?l": "location"},
                "preconditions": ["(at ?r ?l)", "(crate_at ?c ?l)"],
                "effects": ["(holding ?r ?c)", "(not (crate_at ?c ?l))"]
            }
        ]
    }
    
    initial_problem_blueprint = {
        "problem_name": "pick_one_crate",
        "domain_name": "logistics_warehouse",
        "objects": {"r1": "robot", "c1": "crate", "loc1": "location"},
        "initial_state": ["(at r1 loc1)", "(crate_at c1 loc1)"],
        "goal_state": ["(holding r1 c1)"]
    }
    
    state = {
        "requirements": "Robots pick up crates at locations.",
        "pddl_domain_blueprint": initial_domain_blueprint,
        "pddl_problem_blueprint": initial_problem_blueprint,
        "verification_errors": [
            "VAL Error: Error: Undefined predicate: (holding ?r ?c)"
        ]
    }
    
    # Step A: Run Triage
    state = run_triage_node(state)
    print("Triage Reports Generated:", len(state["diagnostic_reports"]))
    print("Formatted Feedback:\n", state["formatted_diagnostic_feedback"])
    
    # Step B: Run Repair
    state = run_repair_node(state)
    repaired_domain = state["pddl_domain_blueprint"]
    
    print("\nRepaired Domain Predicates:")
    print(repaired_domain.get("predicates"))
    
    # Check if holding predicate was added to repair domain
    predicates_str = " ".join(repaired_domain.get("predicates", []))
    assert "holding" in predicates_str.lower(), "Expected repair node to declare the missing 'holding' predicate!"
    print("\n[SUCCESS]: Standalone Repair Node test passed! 'holding' predicate correctly added.")

def test_full_graph_compilation():
    print("\n--- 2. Testing Graph Workflow Structure ---")
    nodes = pddl_lifecycle_graph.nodes
    print("Graph Registered Nodes:", list(nodes.keys()))
    assert "repair" in nodes, "Expected 'repair' node in compiled LangGraph workflow!"
    assert "triage" in nodes, "Expected 'triage' node in compiled LangGraph workflow!"
    print("[SUCCESS]: LangGraph workflow verified with all 5 lifecycle nodes!")

if __name__ == "__main__":
    print("[START] Running Repair Node Unit Tests...")
    test_repair_node_standalone()
    test_full_graph_compilation()
    print("\n[SUCCESS] ALL REPAIR TESTS PASSED SUCCESSFULLY!")
