import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.pddl_blueprint import ErrorCategory, DiagnosticReport
from nodes.triage import parse_val_log, parse_fast_downward_log, format_diagnostic_feedback, run_triage_node

def test_syntax_parse_triage():
    val_syntax_log = """
    Errors in domain file:
    Line 14: Unexpected token ')' near (:action move)
    Parse error: unclosed bracket at line 20
    """
    reports = parse_val_log(val_syntax_log)
    print("\n--- 1. Testing Syntax & Parse Error Triage ---")
    for r in reports:
        print(f"Category: {r.error_category}")
        print(f"Faulty Element: {r.faulty_element}")
        print(f"Repair Hint: {r.suggested_repair_hint}")
        assert r.error_category == ErrorCategory.SYNTAX_PARSE

def test_type_signature_triage():
    val_type_log = """
    Error: Undefined predicate: (at_location ?r ?l)
    Error: Type mismatch for parameter ?r - expected robot, got location
    Error: Arity mismatch in precondition
    """
    reports = parse_val_log(val_type_log)
    print("\n--- 2. Testing Type & Signature Error Triage ---")
    for r in reports:
        print(f"Category: {r.error_category}")
        print(f"Faulty Element: {r.faulty_element}")
        print(f"Repair Hint: {r.suggested_repair_hint}")
        assert r.error_category == ErrorCategory.TYPE_SIGNATURE

def test_grounding_unsolvability_triage():
    fd_unsolvable_log = """
    INFO     Building translation graph...
    INFO     Translating task...
    INFO     Completely explored state space -- no solution!
    Search stopped without finding a solution.
    """
    reports = parse_fast_downward_log(fd_unsolvable_log)
    print("\n--- 3. Testing Grounding & Unsolvability Error Triage ---")
    for r in reports:
        print(f"Category: {r.error_category}")
        print(f"Faulty Element: {r.faulty_element}")
        print(f"Repair Hint: {r.suggested_repair_hint}")
        assert r.error_category == ErrorCategory.GROUNDING_UNSOLVABILITY

def test_system_oracle_warning_triage():
    missing_tool_log = "System Warning: 'Validate' binary not found in system PATH."
    reports = parse_val_log(missing_tool_log)
    print("\n--- 4. Testing System Oracle Warning Triage ---")
    for r in reports:
        print(f"Category: {r.error_category}")
        print(f"Faulty Element: {r.faulty_element}")
        assert r.error_category == ErrorCategory.SYSTEM_ORACLE_ERROR

def test_full_triage_node_execution():
    state = {
        "verification_errors": [
            "VAL Error: Error: Undefined predicate: (in_room ?r)",
            "Planner Error: Could not find a plan. Fast Downward: Completely explored state space -- no solution!"
        ]
    }
    updated_state = run_triage_node(state)
    print("\n--- 5. Testing Full Triage Node Execution ---")
    print("Report Count:", len(updated_state["diagnostic_reports"]))
    print("Formatted Feedback:\n", updated_state["formatted_diagnostic_feedback"])
    assert len(updated_state["diagnostic_reports"]) == 2
    assert "### Diagnostic Failure Analysis Report:" in updated_state["formatted_diagnostic_feedback"]

if __name__ == "__main__":
    print("[START] Running Triage Unit Tests...")
    test_syntax_parse_triage()
    test_type_signature_triage()
    test_grounding_unsolvability_triage()
    test_system_oracle_warning_triage()
    test_full_triage_node_execution()
    print("\n[SUCCESS] ALL TRIAGE TESTS PASSED SUCCESSFULLY!")
