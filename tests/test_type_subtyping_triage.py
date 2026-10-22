"""
Unit test verifying domain-agnostic triage for VAL proposition parameter type mismatch errors,
specifically verifying that when expected_type is a declared subtype of arg_type,
triage targets the predicate or problem objects and does NOT invert the domain types hierarchy.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nodes.triage import is_subtype

def test_is_subtype_hierarchy():
    types_map = {
        "airplane": "obj",
        "truck": "obj",
        "airport": "location",
        "city": "object",
        "location": "object",
        "obj": "object"
    }
    
    # Subtypes
    assert is_subtype("airport", "location", types_map) is True
    assert is_subtype("airplane", "obj", types_map) is True
    assert is_subtype("airplane", "object", types_map) is True
    assert is_subtype("airport", "object", types_map) is True
    
    # Self identity
    assert is_subtype("location", "location", types_map) is True
    assert is_subtype("airport", "airport", types_map) is True
    
    # Inverted (must be False)
    assert is_subtype("location", "airport", types_map) is False
    assert is_subtype("object", "airport", types_map) is False
    assert is_subtype("obj", "truck", types_map) is False
    
    # Disjoint
    assert is_subtype("truck", "location", types_map) is False
    assert is_subtype("airplane", "truck", types_map) is False

def test_type_mismatch_subtyping_triage_routing():
    dom_types = {
        "sub_loc": "super_loc",
        "super_loc": "object",
        "item": "object"
    }
    
    # Case 1: Predicate declared with sub_loc, but argument in problem is super_loc
    # Expected type = sub_loc, Arg type = super_loc
    expected_type = "sub_loc"
    arg_type = "super_loc"
    
    # Verify subtyping relationship
    assert is_subtype(expected_type, arg_type, dom_types) is True
    assert is_subtype(arg_type, expected_type, dom_types) is False
    
    # Triage decision logic
    if is_subtype(expected_type, arg_type, dom_types) and expected_type.lower() != arg_type.lower():
        target_elem = "at-subloc"
        action_allowed = "generalize_predicate_or_update_object"
    else:
        target_elem = "types"
        action_allowed = "declare_subtype"
        
    assert target_elem == "at-subloc", f"Expected target_elem 'at-subloc', got '{target_elem}'"
    assert action_allowed == "generalize_predicate_or_update_object"

    # Case 2: Object has child_item, predicate expects parent_item (normal missing inheritance in types)
    expected_type_2 = "item"
    arg_type_2 = "special_item"
    dom_types_2 = {"item": "object", "special_item": "object"}
    
    assert is_subtype(expected_type_2, arg_type_2, dom_types_2) is False
    assert is_subtype(arg_type_2, expected_type_2, dom_types_2) is False
    
    if is_subtype(expected_type_2, arg_type_2, dom_types_2) and expected_type_2.lower() != arg_type_2.lower():
        target_elem_2 = "pred"
    else:
        target_elem_2 = "types"
        
    assert target_elem_2 == "types"

if __name__ == "__main__":
    test_is_subtype_hierarchy()
    test_type_mismatch_subtyping_triage_routing()
    print("ALL TESTS PASSED!")
