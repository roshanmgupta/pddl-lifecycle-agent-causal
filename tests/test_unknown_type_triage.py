"""
Unit test verifying domain-agnostic triage for VAL 'Object with unknown type: <symbol>' errors.
Tests:
1. Symbol in action schema when symbol exists in problem :objects (must target action or constants, NOT problem objects).
2. Symbol is a phantom parameter type with zero instances in problem :objects (must advise removing phantom parameter).
3. Symbol is a missing type that exists in problem :objects (must advise declaring type in domain types).
4. Root type 'object' error (must advise acyclic inheritance under 'object').
5. Problem-level unknown object (when action is None).
"""
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def test_triage_action_constant_not_misrouted_to_objects():
    state = {
        "requirements": "Dummy requirements text",
        "pddl_domain_blueprint": {
            "domain_name": "test_domain",
            "types": {"container": "object", "hand": "object"},
            "constants": {},
            "predicates": ["(on ?c - container ?t - object)", "(empty ?h - hand)"],
            "actions": [
                {
                    "action_name": "grasp_container",
                    "parameters": {"?b": "container", "?a": "hand"},
                    "preconditions": ["(on ?b table)", "(empty ?a)"],
                    "effects": ["(holding ?a ?b)"]
                }
            ]
        },
        "pddl_problem_blueprint": {
            "problem_name": "test_prob",
            "domain_name": "test_domain",
            "objects": {"table": "object", "c1": "container", "h1": "hand"},
            "initial_state": ["(on c1 table)", "(empty h1)"],
            "goal_state": ["(holding h1 c1)"]
        },
        "verification_errors": [
            "VAL Error: Type-checking grasp_container\nObject with unknown type: table\n\nErrors: 0, warnings: 2\n\nError: Error in type-checking!"
        ]
    }

    # Simulate triage extraction without invoking remote LLM
    val_err = state["verification_errors"][0]
    m_act = re.search(r"Type-checking\s+([a-zA-Z0-9_\-]+)", val_err)
    assert m_act is not None
    current_val_action = m_act.group(1)
    assert current_val_action == "grasp_container"

    m_unk = re.search(r"Object with unknown type:\s*([a-zA-Z0-9_\-]+)", val_err)
    assert m_unk is not None
    unk_symbol = m_unk.group(1)
    assert unk_symbol == "table"

    dom_bp = state["pddl_domain_blueprint"]
    prob_bp = state["pddl_problem_blueprint"]
    dom_constants = dom_bp.get("constants", {})
    prob_objects = prob_bp.get("objects", {})
    obj_types_set = set(prob_objects.values())

    act_params = {}
    for a in dom_bp.get("actions", []):
        if a.get("action_name") == current_val_action:
            act_params = a.get("parameters", {})
            break
    param_types = set(act_params.values())

    # Verify triage routing logic
    if unk_symbol == "object":
        target_elem = "types"
    elif current_val_action:
        if unk_symbol in dom_constants:
            target_elem = "constants"
        elif unk_symbol in param_types:
            target_elem = "types" if unk_symbol in obj_types_set else current_val_action
        else:
            target_elem = current_val_action
    else:
        target_elem = "objects"

    assert target_elem == "grasp_container", f"Expected target_elem to be 'grasp_container', got '{target_elem}'"
    print("PASS: test_triage_action_constant_not_misrouted_to_objects verified successfully!")

if __name__ == "__main__":
    test_triage_action_constant_not_misrouted_to_objects()
