import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from nodes.generation import compile_pddl_programmatically, compile_problem_pddl
from tools.symbolic_oracles import check_pddl_syntax_fallback

print("=== TESTING DOMAIN PDDL TYPE GENERATION & AUTO-DISCOVERY ===")

# Test Case 1: Dict types with None/object
bp1 = {
    "domain_name": "blocks_typed_test",
    "requirements": [":strips", ":typing"],
    "types": {"block": None},
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
            "preconditions": ["(clear ?x)", "(ontable ?x)", "(handempty)"],
            "effects": ["(not (ontable ?x))", "(not (clear ?x))", "(not (handempty))", "(holding ?x)"]
        }
    ]
}

pddl1 = compile_pddl_programmatically(bp1)
print("\n--- Compiled PDDL (Test Case 1: Dict types) ---")
print(pddl1)
assert "(:types" in pddl1
assert "block - object" in pddl1

# Test Case 2: List types
bp2 = {
    "domain_name": "logistics_test",
    "requirements": [":strips", ":typing"],
    "types": ["truck - vehicle", "airplane - vehicle", "vehicle - object", "location - object"],
    "predicates": [
        "(at ?v - vehicle ?l - location)"
    ],
    "actions": []
}

pddl2 = compile_pddl_programmatically(bp2)
print("\n--- Compiled PDDL (Test Case 2: List types) ---")
print(pddl2)
assert "(:types" in pddl2
assert "airplane truck - vehicle" in pddl2 or "truck airplane - vehicle" in pddl2

# Test Case 3: Empty types with Auto-Discovery from signatures
bp3 = {
    "domain_name": "autodiscover_types_test",
    "requirements": [":strips", ":typing"],
    "types": {},
    "predicates": [
        "(at ?r - robot ?l - location)"
    ],
    "actions": [
        {
            "action_name": "move",
            "parameters": {"?r": "robot", "?from": "location", "?to": "location"},
            "preconditions": ["(at ?r ?from)"],
            "effects": ["(not (at ?r ?from))", "(at ?r ?to)"]
        }
    ]
}

pddl3 = compile_pddl_programmatically(bp3)
print("\n--- Compiled PDDL (Test Case 3: Auto-Discovery) ---")
print(pddl3)
assert "(:types" in pddl3
assert "location robot - object" in pddl3 or ("location - object" in pddl3 and "robot - object" in pddl3)

print("\nALL DOMAIN PDDL TYPE GENERATION TESTS PASSED!")
