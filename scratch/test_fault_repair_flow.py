import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from nodes.generation import run_generation_node
from nodes.triage import run_triage_node
from nodes.repair import run_repair_node
from graph import run_full_validation_node, route_after_triage

def test_faulty_domain_repair():
    print("========================================================================")
    print("   TESTING SYNTHETIC FAULT REPAIR FLOW: BLOCKSWORLD MISSING PRECONDITION ")
    print("========================================================================\n")

    # 1. Define Faulty Domain Blueprint (Missing handempty in pick-up)
    faulty_domain_bp = {
        "domain_name": "blocksworld",
        "requirements": [":strips", ":typing"],
        "types": {"block": "object"},
        "predicates": [
            "(on ?x - block ?y - block)",
            "(ontable ?x - block)",
            "(clear ?x - block)",
            "(handempty)",
            "(holding ?x - block)"
        ],
        "actions": [
            {
                "action_name": "pick-up",
                "parameters": {"?x": "block"},
                "preconditions": ["(clear ?x)", "(ontable ?x)"],  # INTENTIONAL FAULT: Missing (handempty)!
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

    # 2. Define Problem Blueprint where picking up two blocks concurrently without checking handempty fails
    problem_bp = {
        "problem_name": "blocksworld_prob_01",
        "domain_name": "blocksworld",
        "objects": {"a": "block", "b": "block"},
        "initial_state": ["(ontable a)", "(ontable b)", "(clear a)", "(clear b)", "(handempty)"],
        "goal_state": ["(holding a)", "(holding b)"]
    }

    state = {
        "requirements": "Blocks domain where picking up requires arm to be empty.",
        "pddl_domain_blueprint": faulty_domain_bp,
        "pddl_problem_blueprint": problem_bp,
        "generated_domain_pddl": "",
        "generated_problem_pddl": "",
        "verification_errors": [],
        "diagnostic_reports": [],
        "formatted_diagnostic_feedback": "",
        "iteration_count": 0,
        "max_iterations": 5
    }

    # Step 1: Option B Compiler
    print("--- Step 1: Option B Compiler (Compiling Faulty Domain) ---")
    state = run_generation_node(state)
    print("Compiled Faulty PDDL Domain:\n", state["generated_domain_pddl"])

    # Step 2: Oracular Validation
    print("--- Step 2: Oracular Validation (VAL / Fast Downward) ---")
    state = run_full_validation_node(state)
    print("Verification Errors captured:", state["verification_errors"])

    # Step 3: Diagnostic Triage
    print("\n--- Step 3: Diagnostic Triage ---")
    state = run_triage_node(state)
    print("Formatted Triage Feedback:\n", state["formatted_diagnostic_feedback"])

    # Step 4: Targeted Repair Node
    print("\n--- Step 4: Targeted Model Repair Node ---")
    state = run_repair_node(state)

    # Step 5: Re-compilation & Re-validation
    print("\n--- Step 5: Re-compilation & Re-validation of Repaired Domain ---")
    state = run_generation_node(state)
    print("Repaired PDDL Domain Code:\n", state["generated_domain_pddl"])
    state = run_full_validation_node(state)
    print("Final Verification Errors:", state.get("verification_errors", []))

    print("\n========================================================================")
    print(" [SUCCESS] SYNTHETIC FAULT REPAIR FLOW VERIFIED SUCCESSFULLY!")
    print("========================================================================")

if __name__ == "__main__":
    test_faulty_domain_repair()
