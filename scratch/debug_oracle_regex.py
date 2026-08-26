import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.symbolic_oracles import check_pddl_syntax_fallback
from nodes.generation import compile_pddl_programmatically

faulty_domain_bp = {
    "domain_name": "blocksworld",
    "requirements": [":strips", ":typing"],
    "types": {"block": "object"},
    "predicates": ["(on ?x - block ?y - block)", "(ontable ?x - block)", "(clear ?x - block)", "(handempty)", "(holding ?x - block)"],
    "actions": [
        {
            "action_name": "pick-up",
            "parameters": {"?x": "block"},
            "preconditions": ["(clear ?x)", "(ontable ?x)"], # Missing handempty!
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

compiled_pddl = compile_pddl_programmatically(faulty_domain_bp)
print("--- COMPILED DOMAIN PDDL ---")
print(compiled_pddl)

with open("scratch/temp_debug.pddl", "w") as f:
    f.write(compiled_pddl)

ok, log = check_pddl_syntax_fallback("scratch/temp_debug.pddl")
print("\n--- CHECK FALLBACK RESULT ---")
print("is_valid:", ok)
print("log:", log)
