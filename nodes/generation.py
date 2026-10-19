import re
from typing import Optional, Dict, Any, List
from schemas.pddl_blueprint import DomainBlueprint, PddlActionSchema, ProblemBlueprint


def normalize_pddl_expression(expr: str) -> str:
    """
    Normalizes whitespace in a PDDL expression to ensure valid syntax.
    
    Fixes common LLM output issues:
      - Missing space before '?' variables:  "(at?r" -> "(at ?r"
      - Missing space after type annotations: "robot?l" -> "robot ?l"
      - Collapsed 'not(' patterns:            "(not(" -> "(not ("
      - Multiple consecutive spaces collapsed to single space
    
    Examples:
      >>> normalize_pddl_expression("(at?r - robot?l - location)")
      '(at ?r - robot ?l - location)'
      >>> normalize_pddl_expression("(not(at?r?from))")
      '(not (at ?r ?from))'
    """
    s = expr.strip()
    # Strip redundant outer nested parentheses e.g. "((not ...))" -> "(not ...)"
    while s.startswith("((") and s.endswith("))"):
        inner = s[1:-1].strip()
        depth = 0
        balanced = True
        for idx, char in enumerate(inner):
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0 and idx < len(inner) - 1:
                    balanced = False
                    break
        if depth == 0 and balanced:
            s = inner
        else:
            break

    # 1. Ensure space before any '?' that is preceded by a word character
    #    Handles: "(at?r" -> "(at ?r" and "robot?l" -> "robot ?l"
    s = re.sub(r'(?<=\w)\?', ' ?', s)
    # 2. Ensure space after '(' when followed by a word char but not already spaced
    #    Handles: "(not(" -> "(not (" — insert space between closing keywords and '('
    s = re.sub(r'(?<=\w)\(', ' (', s)
    # 3. Collapse multiple spaces into single space
    s = re.sub(r' {2,}', ' ', s)
    return s

def flatten_atoms_list(items) -> list:
    """Recursively flattens nested lists or tuples of PDDL atom strings."""
    if not items:
        return []
    flat = []
    for item in items:
        if isinstance(item, (list, tuple)):
            flat.extend(flatten_atoms_list(item))
        elif isinstance(item, str):
            item_str = item.strip()
            if item_str:
                flat.append(item_str)
        elif item is not None:
            flat.append(str(item).strip())
    return flat

def compile_pddl_programmatically(blueprint_data: dict) -> str:
    """
    Deterministic conversion of a DomainBlueprint JSON dictionary
    into perfectly indented, parenthetically closed Lisp PDDL code strings.
    """
    domain_name = blueprint_data.get("domain_name", "generated_domain")
    requirements = blueprint_data.get("requirements", [":strips", ":typing"])
    types = blueprint_data.get("types", {})
    predicates = blueprint_data.get("predicates", [])
    actions = blueprint_data.get("actions", [])
    
    pddl_lines = []
    
    # 1. Header & Requirements
    pddl_lines.append(f"(define (domain {domain_name})")
    req_str = " ".join(requirements) if isinstance(requirements, list) else ":strips :typing"
    pddl_lines.append(f"  (:requirements {req_str})")
    pddl_lines.append("")
    
    # 2. Types Hierarchy Block
    normalized_types = {}
    if isinstance(types, dict):
        for child, parent in types.items():
            normalized_types[str(child).strip()] = str(parent).strip() if parent and str(parent).lower() != "none" else None
    elif isinstance(types, list):
        for item in types:
            if "-" in str(item):
                parts = str(item).split("-")
                children = parts[0].strip().split()
                parent = parts[1].strip()
                for c in children:
                    normalized_types[c] = parent if parent and parent.lower() != "none" else None
            else:
                for c in str(item).strip().split():
                    normalized_types[c] = None

    # Auto-discover types from predicates and action parameters
    discovered_types = set()
    for pred in predicates:
        matches = re.findall(r"\?\w+\s*-\s*([a-zA-Z0-9_\-]+)", str(pred))
        for t in matches:
            if t.lower() != "object":
                discovered_types.add(t)

    for act in actions:
        if isinstance(act, dict):
            params = act.get("parameters", {})
        else:
            params = getattr(act, "parameters", {})
        if isinstance(params, dict):
            for pvar, ptype in params.items():
                if ptype and str(ptype).lower() != "object":
                    discovered_types.add(str(ptype))

    # Auto-discover types from constants
    raw_constants = getattr(blueprint_data, "constants", {}) if hasattr(blueprint_data, "constants") else blueprint_data.get("constants", {})
    if raw_constants and isinstance(raw_constants, dict):
        for cname, ctype in raw_constants.items():
            if ctype and str(ctype).lower() != "object":
                discovered_types.add(str(ctype))

    for dt in discovered_types:
        if dt not in normalized_types:
            normalized_types[dt] = None

    if normalized_types or ":typing" in req_str:
        pddl_lines.append("  (:types")
        if normalized_types:
            supertype_map = {}
            for child, parent in normalized_types.items():
                parent_key = parent if parent else "object"
                if parent_key not in supertype_map:
                    supertype_map[parent_key] = []
                supertype_map[parent_key].append(child)

            for parent, children in supertype_map.items():
                children_str = " ".join(sorted(children))
                if parent == "object":
                    pddl_lines.append(f"    {children_str} - object")
                else:
                    pddl_lines.append(f"    {children_str} - {parent}")
        pddl_lines.append("  )")
        pddl_lines.append("")

    # 2b. Constants Block (Classical PDDL 2.1 Domain Constants)
    if raw_constants and isinstance(raw_constants, dict):
        pddl_lines.append("  (:constants")
        const_supertype_map = {}
        for cname, ctype in raw_constants.items():
            ckey = str(ctype) if ctype else "object"
            const_supertype_map.setdefault(ckey, []).append(str(cname))
        for ctype, clist in const_supertype_map.items():
            cstr = " ".join(sorted(clist))
            if ctype == "object":
                pddl_lines.append(f"    {cstr} - object")
            else:
                pddl_lines.append(f"    {cstr} - {ctype}")
        pddl_lines.append("  )")
        pddl_lines.append("")

        
    # 3. Predicates Block
    if predicates:
        pddl_lines.append("  (:predicates")
        for pred in predicates:
            clean_pred = pred.strip()
            if not clean_pred.startswith("("):
                clean_pred = f"({clean_pred}"
            if not clean_pred.endswith(")"):
                clean_pred = f"{clean_pred})"
            clean_pred = normalize_pddl_expression(clean_pred)
            pddl_lines.append(f"    {clean_pred}")
        pddl_lines.append("  )")
        pddl_lines.append("")
        
    # 4. Action Schemas Compilation
    for act in actions:
        if isinstance(act, dict):
            act_obj = PddlActionSchema(**act)
        else:
            act_obj = act
            
        pddl_lines.append(f"  (:action {act_obj.action_name}")
        
        # Format Parameters: Ensure every variable starts with '?' (e.g. "?r - robot ?l - location")
        param_parts = [
            f"{var if var.startswith('?') else '?' + var} - {type_name}"
            for var, type_name in act_obj.parameters.items()
        ]
        param_str = " ".join(param_parts)
        pddl_lines.append(f"    :parameters ({param_str})")
        
        # Format Preconditions
        flat_preconds = flatten_atoms_list(act_obj.preconditions)
        if len(flat_preconds) == 1:
            pre_str = normalize_pddl_expression(flat_preconds[0])
            pddl_lines.append(f"    :precondition {pre_str}")
        elif len(flat_preconds) > 1:
            pres = " ".join([normalize_pddl_expression(p) for p in flat_preconds])
            pddl_lines.append(f"    :precondition (and {pres})")
        else:
            pddl_lines.append("    :precondition (and)")
            
        # Format Effects
        flat_effects = flatten_atoms_list(act_obj.effects)
        if len(flat_effects) == 1:
            eff_str = normalize_pddl_expression(flat_effects[0])
            pddl_lines.append(f"    :effect {eff_str}")
        elif len(flat_effects) > 1:
            effs = " ".join([normalize_pddl_expression(e) for e in flat_effects])
            pddl_lines.append(f"    :effect (and {effs})")
        else:
            pddl_lines.append("    :effect (and)")
            
        pddl_lines.append("  )")
        pddl_lines.append("")
        
    pddl_lines.append(")")
    return "\n".join(pddl_lines)

def compile_problem_pddl(problem_blueprint_data: dict, domain_blueprint_data: Optional[dict] = None) -> str:
    """
    Deterministically converts a ProblemBlueprint JSON dictionary
    into a PDDL problem file string.
    Automatically filters out any objects declared as domain constants to avoid
    'duplicate objects' validator errors in classical PDDL 2.1.
    """
    problem_name = problem_blueprint_data.get("problem_name", "generated_problem")
    domain_name = problem_blueprint_data.get("domain_name", "generated_domain")
    raw_objects = problem_blueprint_data.get("objects", {})
    objects = dict(raw_objects) if isinstance(raw_objects, dict) else {}

    # In Classical PDDL 2.1, objects declared in domain (:constants ...) are in global scope.
    # Declaring the same identifier in problem (:objects ...) causes Fast Downward / VAL to reject
    # the problem with "Found the following duplicate objects". We filter them out deterministically.
    if domain_blueprint_data and isinstance(domain_blueprint_data, dict):
        domain_constants = domain_blueprint_data.get("constants", {})
        if domain_constants and isinstance(domain_constants, dict):
            for cname in domain_constants:
                if cname in objects:
                    del objects[cname]

    initial_state = problem_blueprint_data.get("initial_state", [])
    goal_state = problem_blueprint_data.get("goal_state", [])

    pddl_lines = []

    # 1. Header
    pddl_lines.append(f"(define (problem {problem_name})")
    pddl_lines.append(f"  (:domain {domain_name})")
    pddl_lines.append("")

    # 2. Objects
    if objects:
        pddl_lines.append("  (:objects")
        obj_lines = [f"    {name} - {obj_type}" for name, obj_type in objects.items()]
        pddl_lines.extend(obj_lines)
        pddl_lines.append("  )")
        pddl_lines.append("")

    # 3. Initial State
    pddl_lines.append("  (:init")
    pddl_lines.extend([f"    {normalize_pddl_expression(s)}" for s in initial_state])
    pddl_lines.append("  )")
    pddl_lines.append("")

    # 4. Goal State
    goal_str = " ".join([normalize_pddl_expression(g) for g in goal_state])
    pddl_lines.append(f"  (:goal (and {goal_str}))")
    pddl_lines.append(")")

    return "\n".join(pddl_lines)

def run_generation_node(state: dict) -> dict:
    """
    Phase 2.2 Node: Programmatically compiles the DomainBlueprint JSON
    into valid Lisp PDDL code without calling an LLM.
    """
    import time
    start_t = time.time()
    blueprint_data = state.get("pddl_domain_blueprint", {})
    if hasattr(blueprint_data, "model_dump"): 
        blueprint_data = blueprint_data.model_dump() #model_dump is a built-in method from Pydantic V2 used to convert a Pydantic model instance into a standard Python
    elif hasattr(blueprint_data, "dict"):
        blueprint_data = blueprint_data.dict()
    
    # Compile Domain
    compiled_pddl = compile_pddl_programmatically(blueprint_data)
    state["generated_domain_pddl"] = compiled_pddl
    if "initial_domain_pddl" not in state or not state["initial_domain_pddl"]:
        state["initial_domain_pddl"] = compiled_pddl
    if "initial_pddl_domain_blueprint" not in state or not state["initial_pddl_domain_blueprint"]:
        state["initial_pddl_domain_blueprint"] = blueprint_data

    # Compile Problem
    problem_blueprint_data = state.get("pddl_problem_blueprint")
    if problem_blueprint_data:
        if hasattr(problem_blueprint_data, "model_dump"):
            problem_blueprint_data = problem_blueprint_data.model_dump()
        elif hasattr(problem_blueprint_data, "dict"):
            problem_blueprint_data = problem_blueprint_data.dict()
            
        compiled_problem_pddl = compile_problem_pddl(problem_blueprint_data, domain_blueprint_data=blueprint_data)
        state["generated_problem_pddl"] = compiled_problem_pddl
        if "initial_problem_pddl" not in state or not state["initial_problem_pddl"]:
            state["initial_problem_pddl"] = compiled_problem_pddl

    latencies = state.get("node_latencies", {})
    latencies["generate"] = round(latencies.get("generate", 0.0) + (time.time() - start_t), 3)
    state["node_latencies"] = latencies
    return state
