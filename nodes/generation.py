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
    # 4. Strip accidental inline typing in atomic formulas:
    # e.g., "(at ?b - waypoint ?c - store)" -> "(at ?b ?c)" or "(at waypoint0 - soil-sample waypoint0)" -> "(at waypoint0 waypoint0)"
    # In classical PDDL 2.1, atomic formulas in preconditions, effects, and initial/goal states cannot contain inline typing
    s = re.sub(r'(\?[a-zA-Z0-9_\-]+|[a-zA-Z0-9_\-]+)\s+-\s+[a-zA-Z0-9_\-]+', r'\1', s)
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

def get_ancestors(t: str, parent_map: dict) -> list:
    """Traverses type hierarchy upwards to find all ancestor types."""
    ancestors = []
    curr = str(t).strip()
    while curr and curr in parent_map and parent_map[curr]:
        p = str(parent_map[curr]).strip()
        if p.lower() == "object" or p in ancestors:
            ancestors.append("object")
            break
        ancestors.append(p)
        curr = p
    if "object" not in ancestors:
        ancestors.append("object")
    return ancestors

def find_common_supertype(t1: str, t2: str, parent_map: dict) -> str:
    """Returns the most specific common supertype for two types."""
    if not t1 or not t2:
        return "object"
    t1_s, t2_s = str(t1).strip(), str(t2).strip()
    if t1_s.lower() == t2_s.lower():
        return t1_s
    anc1 = [t1_s] + get_ancestors(t1_s, parent_map)
    anc2 = [t2_s] + get_ancestors(t2_s, parent_map)
    if t2_s in anc1:
        return t2_s
    if t1_s in anc2:
        return t1_s
    for a in anc1:
        if a in anc2:
            return a
    return "object"

def parse_pddl_typed_params(param_tokens: list) -> list:
    """Parses token stream into [(var_name, type_name), ...]."""
    params = []
    current_vars = []
    i = 0
    while i < len(param_tokens):
        token = param_tokens[i]
        if token == "-":
            ptype = param_tokens[i+1] if i+1 < len(param_tokens) else "object"
            for v in current_vars:
                var_name = v if v.startswith("?") else f"?{v}"
                params.append((var_name, ptype))
            current_vars = []
            i += 2
        else:
            current_vars.append(token)
            i += 1
    for v in current_vars:
        var_name = v if v.startswith("?") else f"?{v}"
        params.append((var_name, "object"))
    return params

def deduplicate_and_unify_predicates(predicates: list, parent_map: dict, has_typing: bool) -> list:
    """
    Deduplicates and unifies predicate declarations sharing the same predicate symbol.
    If multiple declarations exist for the same predicate name with matching arity,
    their parameter types are unified to the common supertype in parent_map.
    This strictly prevents duplicate predicate definitions which violate Classical PDDL.
    """
    pred_map = {}
    for pred in predicates:
        clean = str(pred).strip()
        if not clean.startswith("("):
            clean = f"({clean}"
        if not clean.endswith(")"):
            clean = f"{clean})"
        inner = clean[1:-1].strip()
        tokens = inner.split()
        if not tokens:
            continue
        pname = tokens[0]
        params = parse_pddl_typed_params(tokens[1:])
        
        if pname not in pred_map:
            pred_map[pname] = params
        else:
            existing_params = pred_map[pname]
            if len(existing_params) == len(params):
                unified_params = []
                for (v1, t1), (v2, t2) in zip(existing_params, params):
                    sup = find_common_supertype(t1, t2, parent_map) if has_typing else "object"
                    unified_params.append((v2 if v2 else v1, sup))
                pred_map[pname] = unified_params

    out = []
    for pname, params in pred_map.items():
        if not params:
            out.append(f"({pname})")
        elif has_typing:
            p_str = " ".join([f"{v if v.startswith('?') else '?' + v} - {t}" for v, t in params])
            out.append(f"({pname} {p_str})")
        else:
            p_str = " ".join([v if v.startswith('?') else '?' + v for v, t in params])
            out.append(f"({pname} {p_str})")
    return out

def sanitize_action_effects(raw_effects: list) -> list:
    r"""
    Enforces classical STRIPS invariant: add(a) \cap del(a) = \emptyset.
    Under standard STRIPS add-after-delete semantics, if an action asserts both
    literal P and (not P), the add effect takes precedence, and the conflicting
    delete effect (not P) is pruned. This prevents planner/validator translation failures.
    """
    flat = flatten_atoms_list(raw_effects)
    pos_atoms = set()
    for eff in flat:
        norm = normalize_pddl_expression(eff)
        inner = norm.strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1].strip()
        if not inner.lower().startswith("not"):
            clean_atom = re.sub(r'\s+', ' ', norm)
            pos_atoms.add(clean_atom)

    sanitized = []
    seen = set()
    for eff in flat:
        norm = normalize_pddl_expression(eff)
        inner = norm.strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1].strip()
        if inner.lower().startswith("not"):
            neg_content = inner[3:].strip()
            if not neg_content.startswith("("):
                neg_content = f"({neg_content})"
            norm_pos = re.sub(r'\s+', ' ', normalize_pddl_expression(neg_content))
            if norm_pos in pos_atoms:
                # Contradictory effect detected: positive add takes precedence under add-after-delete
                continue
        clean_norm = re.sub(r'\s+', ' ', norm)
        if clean_norm not in seen:
            seen.add(clean_norm)
            sanitized.append(clean_norm)
    return sanitized

def compile_pddl_programmatically(blueprint_data: dict) -> str:
    """
    Deterministic conversion of a DomainBlueprint JSON dictionary
    into perfectly indented, parenthetically closed Lisp PDDL code strings.
    """
    raw_dname = blueprint_data.get("domain_name", "generated_domain")
    domain_name = re.sub(r'\.pddl$', '', str(raw_dname), flags=re.IGNORECASE)
    domain_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', domain_name)
    if not domain_name:
        domain_name = "generated_domain"
    requirements = blueprint_data.get("requirements", [":strips", ":typing"])
    types = blueprint_data.get("types", {})
    predicates = blueprint_data.get("predicates", [])
    actions = blueprint_data.get("actions", [])
    
    pddl_lines = []
    
    # 1. Header & Requirements
    pddl_lines.append(f"(define (domain {domain_name})")
    req_str = " ".join(requirements) if isinstance(requirements, list) else ":strips :typing"
    has_typing = ":typing" in req_str
    pddl_lines.append(f"  (:requirements {req_str})")
    pddl_lines.append("")
    
    # 2. Types Hierarchy Block
    normalized_types = {}
    if isinstance(types, dict):
        for child, parent in types.items():
            if child and str(child).lower() != "object":
                normalized_types[str(child).strip()] = str(parent).strip() if parent and str(parent).lower() not in ["none", str(child).lower()] else None
    elif isinstance(types, list):
        for item in types:
            if "-" in str(item):
                parts = str(item).split("-")
                children = parts[0].strip().split()
                parent = parts[1].strip()
                for c in children:
                    if c and c.lower() != "object":
                        normalized_types[c] = parent if parent and parent.lower() not in ["none", c.lower()] else None
            else:
                for c in str(item).strip().split():
                    if c and c.lower() != "object":
                        normalized_types[c] = None

    # Auto-discover types from predicates and action parameters (only when :typing is active)
    if has_typing:
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

        # Auto-discover object constants appearing in action preconditions and effects
        # (Classical PDDL 2.1: any non-variable literal argument in action schemas is an object constant)
        raw_constants = getattr(blueprint_data, "constants", {}) if hasattr(blueprint_data, "constants") else blueprint_data.get("constants", {})
        if not isinstance(raw_constants, dict):
            raw_constants = {}

        for act in actions:
            if isinstance(act, dict):
                act_params = act.get("parameters", {})
                act_precs = act.get("preconditions", [])
                act_effs = act.get("effects", [])
            else:
                act_params = getattr(act, "parameters", {})
                act_precs = getattr(act, "preconditions", [])
                act_effs = getattr(act, "effects", [])
            VALID_IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\-]*$')
            PDDL_KEYWORDS = {"not", "and", "or", "imply", "exists", "forall", "object", "-", "="}
            norm_param_names = {k if k.startswith("?") else "?" + k for k in act_params.keys()}
            bare_param_names = {k.lstrip("?") for k in act_params.keys()}
            all_atoms = flatten_atoms_list(act_precs) + flatten_atoms_list(act_effs)
            for atom in all_atoms:
                norm_atom = normalize_pddl_expression(atom)
                clean = norm_atom.strip('() ')
                if clean.lower().startswith("not"):
                    clean = clean[3:].strip('() ')
                parts = clean.split()
                if len(parts) > 1:
                    for arg in parts[1:]:
                        if (
                            not arg.startswith("?")
                            and not arg.replace('.', '', 1).isdigit()
                            and VALID_IDENTIFIER.match(arg)
                            and arg.lower() not in PDDL_KEYWORDS
                            and arg not in normalized_types
                            and arg not in bare_param_names
                        ):
                            if arg not in raw_constants:
                                raw_constants[arg] = "object"

        if isinstance(blueprint_data, dict):
            blueprint_data["constants"] = raw_constants
        elif hasattr(blueprint_data, "constants"):
            setattr(blueprint_data, "constants", raw_constants)

        # Auto-discover types from constants
        if raw_constants and isinstance(raw_constants, dict):
            for cname, ctype in raw_constants.items():
                if ctype and str(ctype).lower() != "object":
                    discovered_types.add(str(ctype))

        for dt in discovered_types:
            if dt not in normalized_types and dt.lower() != "object":
                normalized_types[dt] = None

        # Universal PDDL 2.1 Typing AST Invariant:
        # Any type referenced as a supertype that is not itself declared as a child of another type
        # must be declared as a subtype of the universal root 'object'.
        all_referenced_parents = {p for p in list(normalized_types.values()) if p and str(p).lower() not in {"object", "none"}}
        for p in all_referenced_parents:
            if p not in normalized_types:
                normalized_types[p] = "object"

    # 2b. Constants Block Determination (Classical PDDL 2.1 Domain Constants)
    valid_constants = {}
    if raw_constants and isinstance(raw_constants, dict):
        VALID_IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\-]*$')
        PDDL_KEYWORDS = {"not", "and", "or", "imply", "exists", "forall", "object", "-", "="}
        for cname, ctype in raw_constants.items():
            cname_str = str(cname).strip()
            if (
                VALID_IDENTIFIER.match(cname_str)
                and cname_str.lower() not in PDDL_KEYWORDS
            ):
                valid_constants[cname_str] = ctype if ctype else "object"

    # In Classical PDDL 2.1 (:typing), every constant must have a valid declared type.
    # If a constant's declared type is not 'object', ensure its type is declared in normalized_types.
    for cname, ctype in valid_constants.items():
        if ctype and str(ctype).lower() != "object" and str(ctype) not in normalized_types:
            normalized_types[str(ctype)] = "object"

    # Only purge a constant symbol from types if it is NOT itself used as a type by any entity.
    used_type_names = {str(ctype) for ctype in valid_constants.values() if ctype} | {str(p) for p in normalized_types.values() if p}
    for cname in list(valid_constants.keys()):
        if cname not in used_type_names:
            normalized_types.pop(cname, None)

    # Filter out root 'object' from (:types ...)
    filtered_types = {c: p for c, p in normalized_types.items() if c and c.lower() != "object"}

    if filtered_types and has_typing:
        pddl_lines.append("  (:types")
        supertype_map = {}
        for child, parent in filtered_types.items():
            parent_key = parent if (parent and parent.lower() != "none" and parent.lower() != child.lower()) else "object"
            supertype_map.setdefault(parent_key, []).append(child)

        for parent, children in supertype_map.items():
            children_str = " ".join(sorted(set(children)))
            if parent == "object":
                pddl_lines.append(f"    {children_str} - object")
            else:
                pddl_lines.append(f"    {children_str} - {parent}")
        pddl_lines.append("  )")
        pddl_lines.append("")

    if valid_constants:
        pddl_lines.append("  (:constants")
        const_supertype_map = {}
        for cname, ctype in valid_constants.items():
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

        
    # 3. Predicates Block & Auto-Discovery
    # Build initial pred_map from declared predicates
    pred_map = {}
    for pred in predicates:
        clean = str(pred).strip()
        if not clean.startswith("("):
            clean = f"({clean}"
        if not clean.endswith(")"):
            clean = f"{clean})"
        inner = clean[1:-1].strip()
        tokens = inner.split()
        if not tokens:
            continue
        pname = tokens[0]
        params = parse_pddl_typed_params(tokens[1:])
        if pname not in pred_map:
            pred_map[pname] = params
        else:
            existing_params = pred_map[pname]
            if len(existing_params) == len(params):
                unified_params = []
                for (v1, t1), (v2, t2) in zip(existing_params, params):
                    sup = find_common_supertype(t1, t2, normalized_types) if has_typing else "object"
                    unified_params.append((v2 if v2 else v1, sup))
                pred_map[pname] = unified_params

    # Auto-discover predicates and unify parameter signatures across action schemas
    for act in actions:
        if isinstance(act, dict):
            act_params = act.get("parameters", {})
            act_precs = act.get("preconditions", [])
            act_effs = act.get("effects", [])
        else:
            act_params = getattr(act, "parameters", {})
            act_precs = getattr(act, "preconditions", [])
            act_effs = getattr(act, "effects", [])
        norm_params = {k if k.startswith("?") else "?" + k: v for k, v in act_params.items()}

        all_atoms = flatten_atoms_list(act_precs) + flatten_atoms_list(act_effs)
        for atom in all_atoms:
            clean = atom.strip('() ')
            if clean.lower().startswith("not"):
                clean = clean[3:].strip('() ')
            tokens = clean.split()
            if not tokens:
                continue
            pname = tokens[0]
            args = tokens[1:]

            inferred_types = []
            for arg in args:
                if arg in norm_params:
                    inferred_types.append(norm_params[arg])
                elif raw_constants and arg in raw_constants:
                    inferred_types.append(raw_constants[arg])
                else:
                    inferred_types.append("object")

            if pname not in pred_map:
                param_tuples = [
                    (f"?x{i+1}" if not arg.startswith("?") else arg, inferred_types[i])
                    for i, arg in enumerate(args)
                ]
                pred_map[pname] = param_tuples
            else:
                existing_params = pred_map[pname]
                if len(existing_params) == len(inferred_types):
                    unified_params = []
                    for (v1, t1), t2 in zip(existing_params, inferred_types):
                        sup = find_common_supertype(t1, t2, normalized_types) if has_typing else "object"
                        unified_params.append((v1, sup))
                    pred_map[pname] = unified_params

    if pred_map:
        pddl_lines.append("  (:predicates")
        for pname, params in pred_map.items():
            if not params:
                pddl_lines.append(f"    ({pname})")
            elif has_typing:
                p_str = " ".join([f"{v if v.startswith('?') else '?' + v} - {t}" for v, t in params])
                pddl_lines.append(f"    ({pname} {p_str})")
            else:
                p_str = " ".join([v if v.startswith('?') else '?' + v for v, t in params])
                pddl_lines.append(f"    ({pname} {p_str})")
        pddl_lines.append("  )")
        pddl_lines.append("")

    # 4. Action Schemas Compilation
    for act in actions:
        if isinstance(act, dict):
            act_obj = PddlActionSchema(**act)
        else:
            act_obj = act

        flat_preconds = flatten_atoms_list(act_obj.preconditions)
        flat_effects = sanitize_action_effects(act_obj.effects)

        # In Classical PDDL 2.1, free/unbound variables in action schemas violate AST well-formedness.
        # Ensure all variables in preconditions and effects are declared in parameters.
        all_atoms = flat_preconds + flat_effects
        used_vars = set(re.findall(r'\?[a-zA-Z0-9_\-]+', " ".join(all_atoms)))
        existing_params_norm = {k if k.startswith("?") else "?" + k: v for k, v in act_obj.parameters.items()}
        missing_vars = used_vars - set(existing_params_norm.keys())
        if missing_vars:
            for mv in sorted(missing_vars):
                inferred_type = "object"
                for atom in all_atoms:
                    clean = atom.strip('() ')
                    if clean.lower().startswith("not"):
                        clean = clean[3:].strip('() ')
                    parts = clean.split()
                    if parts and mv in parts[1:]:
                        idx = parts[1:].index(mv)
                        p_sym = parts[0]
                        if p_sym in pred_map:
                            sig_params = pred_map[p_sym]
                            if idx < len(sig_params):
                                inferred_type = sig_params[idx][1]
                                break
                existing_params_norm[mv] = inferred_type
            act_obj.parameters = existing_params_norm

        pddl_lines.append(f"  (:action {act_obj.action_name}")

        # Format Parameters: Ensure every variable starts with '?'
        if has_typing:
            param_parts = [
                f"{var if var.startswith('?') else '?' + var} - {type_name if type_name else 'object'}"
                for var, type_name in act_obj.parameters.items()
            ]
        else:
            param_parts = [
                f"{var if var.startswith('?') else '?' + var}"
                for var in act_obj.parameters.keys()
            ]
        param_str = " ".join(param_parts)
        pddl_lines.append(f"    :parameters ({param_str})")

        # Format Preconditions
        if len(flat_preconds) == 1:
            pre_str = normalize_pddl_expression(flat_preconds[0])
            pddl_lines.append(f"    :precondition {pre_str}")
        elif len(flat_preconds) > 1:
            pres = " ".join([normalize_pddl_expression(p) for p in flat_preconds])
            pddl_lines.append(f"    :precondition (and {pres})")
        else:
            pddl_lines.append("    :precondition (and)")

        # Format Effects
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
    raw_pname = problem_blueprint_data.get("problem_name", "generated_problem")
    problem_name = re.sub(r'\.pddl$', '', str(raw_pname), flags=re.IGNORECASE)
    problem_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', problem_name)
    if not problem_name:
        problem_name = "generated_problem"

    raw_dname = problem_blueprint_data.get("domain_name", "generated_domain")
    domain_name = re.sub(r'\.pddl$', '', str(raw_dname), flags=re.IGNORECASE)
    domain_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', domain_name)
    if not domain_name:
        domain_name = "generated_domain"

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

    # Determine whether typing is active
    has_typing = False
    if domain_blueprint_data and isinstance(domain_blueprint_data, dict):
        reqs = domain_blueprint_data.get("requirements", [])
        if isinstance(reqs, list) and ":typing" in reqs:
            has_typing = True
        elif isinstance(reqs, str) and ":typing" in reqs:
            has_typing = True
    else:
        has_typing = any(t and str(t).lower() != "object" for t in objects.values())

    # Auto-discover objects appearing in initial_state and goal_state that were omitted from objects dict
    all_prob_atoms = flatten_atoms_list(initial_state) + flatten_atoms_list(goal_state)
    for atom in all_prob_atoms:
        clean = atom.strip('() ')
        if clean.lower().startswith("not"):
            clean = clean[3:].strip('() ')
        parts = clean.split()
        VALID_IDENTIFIER = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\-]*$')
        PDDL_KEYWORDS = {"not", "and", "or", "imply", "exists", "forall", "object", "-", "="}
        if len(parts) > 1:
            for obj in parts[1:]:
                if (
                    not obj.startswith("?")
                    and not obj.replace('.', '', 1).isdigit()
                    and VALID_IDENTIFIER.match(obj)
                    and obj.lower() not in PDDL_KEYWORDS
                    and obj not in objects
                ):
                    if domain_blueprint_data and isinstance(domain_blueprint_data, dict):
                        domain_constants = domain_blueprint_data.get("constants", {})
                        if domain_constants and obj in domain_constants:
                            continue
                        domain_types = domain_blueprint_data.get("types", {})
                        if domain_types and obj in domain_types:
                            continue
                    objects[obj] = "object"

    # Classical PDDL 2.1 Typing AST Invariant:
    # Domain constants and problem objects share the object namespace and MUST be disjoint.
    # Any symbol declared as a domain constant cannot also be declared in problem (:objects ...).
    if domain_blueprint_data and isinstance(domain_blueprint_data, dict):
        dom_consts = domain_blueprint_data.get("constants", {})
        if dom_consts and isinstance(dom_consts, dict):
            for cname in dom_consts:
                objects.pop(str(cname).strip(), None)

    # 2. Objects
    if objects:
        pddl_lines.append("  (:objects")
        if has_typing:
            supertype_map = {}
            for name, obj_type in objects.items():
                t = str(obj_type) if obj_type else "object"
                supertype_map.setdefault(t, []).append(str(name))
            for t, names in supertype_map.items():
                names_str = " ".join(names)
                pddl_lines.append(f"    {names_str} - {t}")
        else:
            pddl_lines.append(f"    {' '.join(objects.keys())}")
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
