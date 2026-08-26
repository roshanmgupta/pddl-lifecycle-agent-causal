import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.pddl_blueprint import ErrorCategory, RepairOperationType
from nodes.maintenance import run_maintenance_node
from nodes.triage import run_triage_node

def test_phase_4_maintenance():
    print("==================================================")
    print("   TESTING PHASE 4: MAINTENANCE & EVOLUTION NODE ")
    print("==================================================\n")

    # Define historical problem blueprint (Blocksworld Problem 1)
    historical_problem_blueprint = {
        "problem_name": "blocksworld_prob_01",
        "domain_name": "blocksworld",
        "objects": {"b1": "block", "b2": "block"},
        "initial_state": ["(ontable b1)", "(clear b1)", "(handempty)"],
        "goal_state": ["(holding b1)"]
    }

    historical_suite = [
        {
            "case_id": "blocksworld_hist_01",
            "problem_blueprint": historical_problem_blueprint
        }
    ]

    # 1. TEST CASE 1: Backward-Compatible Domain Update
    print("--- 1. Testing Backward-Compatible Domain Update ---")
    valid_domain_blueprint = {
        "domain_name": "blocksworld",
        "requirements": [":strips", ":typing"],
        "types": {"block": "object"},
        "predicates": ["(ontable ?b - block)", "(clear ?b - block)", "(handempty)", "(holding ?b - block)"],
        "actions": [
            {
                "action_name": "pickup",
                "parameters": {"?b": "block"},
                "preconditions": ["(ontable ?b)", "(clear ?b)", "(handempty)"],
                "effects": ["(holding ?b)", "(not (ontable ?b))", "(not (clear ?b))", "(not (handempty))"]
            }
        ]
    }

    state_valid = {
        "pddl_domain_blueprint": valid_domain_blueprint,
        "historical_regression_suite": historical_suite,
        "verification_errors": [],
        "diagnostic_reports": []
    }

    res_valid = run_maintenance_node(state_valid)
    assert len(res_valid.get("verification_errors", [])) == 0, "Valid domain update should not trigger regression errors!"
    print("[SUCCESS]: Backward-compatible domain update passed Phase 4 Maintenance suite!\n")

    # 2. TEST CASE 2: Breaking Domain Update (Regression Introduced)
    print("--- 2. Testing Breaking Domain Update (Regression Introduced) ---")
    breaking_domain_blueprint = {
        "domain_name": "blocksworld",
        "requirements": [":strips", ":typing"],
        "types": {"block": "object"},
        "predicates": ["(ontable ?b - block)", "(clear ?b - block)", "(handempty)", "(holding ?b - block)"],
        "actions": [
            {
                "action_name": "pickup",
                "parameters": {"?b": "block"},
                "preconditions": ["(ontable ?b ?b)", "(clear ?b)", "(handempty)"], # Arity mismatch: 2 params instead of 1!
                "effects": ["(holding ?b)", "(not (ontable ?b))", "(not (clear ?b))", "(not (handempty))"]
            }
        ]
    }

    state_breaking = {
        "pddl_domain_blueprint": breaking_domain_blueprint,
        "historical_regression_suite": historical_suite,
        "verification_errors": [],
        "diagnostic_reports": []
    }

    res_breaking = run_maintenance_node(state_breaking)
    res_triage = run_triage_node(res_breaking)

    errors = res_triage.get("verification_errors", [])
    reports = res_triage.get("diagnostic_reports", [])
    feedback = res_triage.get("formatted_diagnostic_feedback", "")

    assert len(reports) > 0, "Breaking domain update MUST trigger a diagnostic report!"
    assert any("HISTORICAL_REGRESSION" in str(r) for r in reports), "Report MUST contain HISTORICAL_REGRESSION category!"

    print("Captured Diagnostic Reports for Maintenance Failure:")
    print(feedback)

    print("\n[SUCCESS]: Phase 4 Maintenance correctly detected backward-compatibility regression!")
    print("\n==================================================")
    print(" ALL PHASE 4 MAINTENANCE TESTS PASSED CLEANLY!")
    print("==================================================")

if __name__ == "__main__":
    test_phase_4_maintenance()
