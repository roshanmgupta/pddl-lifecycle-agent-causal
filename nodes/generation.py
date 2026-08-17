from schemas.pddl_blueprint import DomainBlueprint, PddlActionSchema, ProblemBlueprint

def compile_pddl_programmatically(blueprint_data: dict) -> str:
    """
    Option B Engine: Deterministically converts a DomainBlueprint JSON dictionary
    into perfectly indented, parenthetically closed Lisp PDDL code strings.
    Bypasses LLM generation to eliminate syntax hallucinations.
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
    if types:
        pddl_lines.append("  (:types")
        # Group child types by supertype
        supertype_map = {}
        for child, parent in types.items():
            parent_key = parent if parent else "object"
            if parent_key not in supertype_map:
                supertype_map[parent_key] = []
            supertype_map[parent_key].append(child)
            
        for parent, children in supertype_map.items():
            children_str = " ".join(children)
            if parent == "object":
                pddl_lines.append(f"    {children_str} - object")
            else:
                pddl_lines.append(f"    {children_str} - {parent}")
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
        
        # Format Parameters: "?r - robot ?l - location"
        param_parts = [f"{var} - {type_name}" for var, type_name in act_obj.parameters.items()]
        param_str = " ".join(param_parts)
        pddl_lines.append(f"    :parameters ({param_str})")
        
        # Format Preconditions
        if len(act_obj.preconditions) == 1:
            pre_str = act_obj.preconditions[0].strip()
            pddl_lines.append(f"    :precondition {pre_str}")
        elif len(act_obj.preconditions) > 1:
            pres = " ".join([p.strip() for p in act_obj.preconditions])
            pddl_lines.append(f"    :precondition (and {pres})")
        else:
            pddl_lines.append("    :precondition (and)")
            
        # Format Effects
        if len(act_obj.effects) == 1:
            eff_str = act_obj.effects[0].strip()
            pddl_lines.append(f"    :effect {eff_str}")
        elif len(act_obj.effects) > 1:
            effs = " ".join([e.strip() for e in act_obj.effects])
            pddl_lines.append(f"    :effect (and {effs})")
        else:
            pddl_lines.append("    :effect (and)")
            
        pddl_lines.append("  )")
        pddl_lines.append("")
        
    pddl_lines.append(")")
    return "\n".join(pddl_lines)

def compile_problem_pddl(problem_blueprint_data: dict) -> str:
    """
    Deterministically converts a ProblemBlueprint JSON dictionary
    into a PDDL problem file string.
    """
    problem_name = problem_blueprint_data.get("problem_name", "generated_problem")
    domain_name = problem_blueprint_data.get("domain_name", "generated_domain")
    objects = problem_blueprint_data.get("objects", {})
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
    pddl_lines.extend([f"    {s.strip()}" for s in initial_state])
    pddl_lines.append("  )")
    pddl_lines.append("")

    # 4. Goal State
    goal_str = " ".join([g.strip() for g in goal_state])
    pddl_lines.append(f"  (:goal (and {goal_str}))")
    pddl_lines.append(")")

    return "\n".join(pddl_lines)

def run_generation_node(state: dict) -> dict:
    """
    Phase 2.2 Node: Programmatically compiles the DomainBlueprint JSON
    into valid Lisp PDDL code without calling an LLM.
    """
    blueprint_data = state.get("pddl_domain_blueprint", {})
    
    # Compile Domain
    compiled_pddl = compile_pddl_programmatically(blueprint_data)
    state["generated_domain_pddl"] = compiled_pddl

    # Compile Problem
    problem_blueprint_data = state.get("pddl_problem_blueprint")
    if problem_blueprint_data:
        compiled_problem_pddl = compile_problem_pddl(problem_blueprint_data)
        state["generated_problem_pddl"] = compiled_problem_pddl
    return state