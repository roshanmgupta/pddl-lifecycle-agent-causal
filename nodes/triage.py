import json
import re
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from schemas.pddl_blueprint import DiagnosticReport, ErrorCategory, RepairOperationType
from config.pddl_standards import STANDARD_CLASSICAL_PDDL_RULES, STANDARD_DIAGNOSTIC_RULES
from config.model_config import get_phase_model, invoke_structured_llm_with_telemetry
from tools.causal_triage_analyzer import run_causal_triage_analysis

class DiagnosticAnalysis(BaseModel):
    """Container for structured diagnostic reports produced by the Diagnostic LLM Agent."""
    reports: List[DiagnosticReport] = Field(
        default_factory=list,
        description="Ranked list of diagnostic reports localizing faults and suggesting repair operations"
    )

def check_system_oracle_binary_availability(raw_log: str, oracle_name: str) -> Optional[DiagnosticReport]:
    """
    Checks if an oracle error is caused by a missing system binary (VAL or Fast Downward)
    rather than a domain modeling defect.
    """
    log_lower = raw_log.lower()
    binary_missing = (
        "binary not found" in log_lower
        or "executable not found" in log_lower
        or "failed to execute val binary" in log_lower
        or "failed to execute fast downward" in log_lower
        or "cannot find the file specified" in log_lower
        or ("not found at" in log_lower and ("val" in log_lower or "downward" in log_lower))
    )
    if binary_missing:
        binary_label = "VAL Oracle Binary" if oracle_name == "VAL" else "Fast Downward Binary"
        hint = (
            "Ensure VAL executable path is properly configured via 'VAL_PATH' in your .env file or available on system PATH."
            if oracle_name == "VAL"
            else "Ensure Fast Downward path is properly configured via 'FAST_DOWNWARD_PATH' in your .env file or available on system PATH."
        )
        return DiagnosticReport(
            error_category=ErrorCategory.SYSTEM_ORACLE_ERROR,
            repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
            faulty_element=binary_label,
            raw_log=raw_log.strip()[:300],
            suggested_repair_hint=hint
        )
    return None

def parse_val_log(val_log: str) -> List[DiagnosticReport]:
    """Backward-compatible wrapper checking VAL binary availability."""
    rep = check_system_oracle_binary_availability(val_log, "VAL")
    return [rep] if rep else []

def parse_fast_downward_log(fd_log: str, causal_analysis: Optional[Dict[str, Any]] = None) -> List[DiagnosticReport]:
    """Backward-compatible wrapper checking Fast Downward binary availability."""
    rep = check_system_oracle_binary_availability(fd_log, "Fast Downward")
    return [rep] if rep else []

def format_diagnostic_feedback(reports: List[DiagnosticReport]) -> str:
    """
    Formats structured DiagnosticReports into a clear, literature-grounded feedback block
    (following Smirnov et al. 2024; Chen et al. 2024):
    [ERROR TYPE], [TARGET AST OPERATION], [LOCATION], and [SUGGESTION FOR REPAIR].
    """
    if not reports:
        return ""
        
    feedback_lines = ["### Diagnostic Failure Analysis Report (Symbolic Oracle Triage):"]
    for idx, report in enumerate(reports, 1):
        cat = report.error_category.value if hasattr(report.error_category, "value") else str(report.error_category)
        op = report.repair_operation_type.value if hasattr(report.repair_operation_type, "value") else str(report.repair_operation_type)
        feedback_lines.append(f"\nIssue #{idx}:")
        feedback_lines.append(f"  - [ERROR TYPE]: {cat}")
        feedback_lines.append(f"  - [TARGET AST OPERATION]: {op}")
        if report.faulty_element:
            feedback_lines.append(f"  - [LOCATION / COMPONENT]: {report.faulty_element}")
        feedback_lines.append(f"  - [DESCRIPTION / RAW TRACE]: {report.raw_log}")
        feedback_lines.append(f"  - [SUGGESTION FOR REPAIR]: {report.suggested_repair_hint}")
        
    return "\n".join(feedback_lines)

def is_subtype(child: str, parent: str, types_map: dict) -> bool:
    """Checks whether child inherits directly or indirectly from parent in the type hierarchy."""
    if not child or not parent or not types_map or not isinstance(types_map, dict):
        return False
    curr = str(child).strip()
    target = str(parent).strip().lower()
    if curr.lower() == target:
        return True
    seen = set()
    while curr and curr in types_map and curr not in seen:
        seen.add(curr)
        p = types_map[curr]
        if not p:
            break
        p_str = str(p).strip()
        if p_str.lower() == target:
            return True
        curr = p_str
    return False

def run_triage_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 3.1 Diagnostic Triage Node: Invokes the Diagnostic LLM Agent to reason about oracle failures,
    localize faulty actions/predicates, and generate structured DiagnosticReports.
    """
    start_t = time.time()
    raw_errors = state.get("verification_errors", [])
    
    if not raw_errors:
        state["diagnostic_reports"] = []
        state["formatted_diagnostic_feedback"] = ""
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    if state.get("skip_triage"):
        print("[Triage Node (ABLATION)]: Triage bypassed. Forwarding raw oracle errors directly to repair node.")
        state["diagnostic_reports"] = []
        state["formatted_diagnostic_feedback"] = "Raw Oracle Verification Errors (Unstructured Feedback):\n" + "\n".join(raw_errors)
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    # Pre-flight Check: Detect instant System Oracle / Executable binary errors
    system_reports: List[DiagnosticReport] = []
    for err in raw_errors:
        err_lower = err.lower()
        if "binary not found" in err_lower or "failed to execute" in err_lower or "system warning" in err_lower:
            if err.startswith("VAL Error:"):
                rep = check_system_oracle_binary_availability(err[len("VAL Error:"):].strip(), "VAL")
                if rep:
                    system_reports.append(rep)
            elif err.startswith("Planner Error:"):
                rep = check_system_oracle_binary_availability(err[len("Planner Error:"):].strip(), "Fast Downward")
                if rep:
                    system_reports.append(rep)

    if any(r.error_category == ErrorCategory.SYSTEM_ORACLE_ERROR for r in system_reports):
        print("[Triage Node]: Detected System Oracle executable binary issue. Bypassing LLM triage.")
        dumped_reports = [r.model_dump() for r in system_reports]
        state["diagnostic_reports"] = dumped_reports
        state["formatted_diagnostic_feedback"] = format_diagnostic_feedback(system_reports)
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    domain_bp = state.get("pddl_domain_blueprint", {})
    problem_bp = state.get("pddl_problem_blueprint", {})
    requirements_text = state.get("requirements", "")
    error_traces_str = "\n".join(raw_errors)

    # Classical Action-Predicate Causal Dependency Graph & Reachability Triage Analysis
    causal_analysis = run_causal_triage_analysis(
        domain_bp,
        problem_bp,
        raw_errors,
        state.get("historical_test_results", [])
    )
    state["causal_graph_analysis"] = causal_analysis
    causal_summary = causal_analysis.get("diagnostic_summary", "")

    val_syntax_or_type_error = any("VAL Error:" in err for err in raw_errors)
    focus_guidance = ""
    if val_syntax_or_type_error:
        val_type_diagnostics = []
        type_mismatch_entries = []
        unknown_type_entries = []
        current_val_action = None
        for err in raw_errors:
            for line in err.splitlines():
                if "...action passes type checking" in line or "Type-checking initial state" in line or "Type-checking goal state" in line or "Type problem in problem specification" in line:
                    current_val_action = None
                m_act = re.search(r"Type-checking\s+([a-zA-Z0-9_\-]+)", line)
                if m_act:
                    current_val_action = m_act.group(1)

                m_pred_nf = re.search(r"Predicate\s+([a-zA-Z0-9_\-]+)\s+not found", line)
                if m_pred_nf:
                    missing_pred = m_pred_nf.group(1)
                    dom_constants = domain_bp.get("constants", {}) if isinstance(domain_bp, dict) else {}
                    prob_objects = problem_bp.get("objects", {}) if isinstance(problem_bp, dict) else {}
                    if missing_pred in prob_objects or missing_pred in dom_constants:
                        obj_type = prob_objects.get(missing_pred) or dom_constants.get(missing_pred, "object")
                        val_type_diagnostics.append(
                            f"  * VAL Error: 'Predicate {missing_pred} not found' in initial/goal state.\n"
                            f"    CRITICAL ROOT CAUSE: Symbol '{missing_pred}' is declared as an OBJECT of type '{obj_type}', but was placed in the FIRST (PREDICATE) position of an atomic formula in problem ':init' or ':goal'!\n"
                            f"    In Classical PDDL 2.1 prefix notation, every fact must begin with a declared predicate symbol from 'domain.predicates' (e.g. '(rel arg1 arg2 ...)'). An object name can NEVER be in the predicate position.\n"
                            f"    MANDATORY REPAIR ACTION: Check problem 'initial_state' for facts starting with '({missing_pred} ...)'. "
                            f"    Determine the intended relational predicate described in the requirements (e.g. if describing that entity A is associated with entity B, declare a relational predicate like '(relation-name ?x - type1 ?y - type2)' in domain 'predicates', and rewrite the fact in problem 'initial_state' to prefix form '(relation-name {missing_pred} ...)'). "
                            f"    Do NOT declare '{missing_pred}' as a predicate!"
                        )
                    else:
                        val_type_diagnostics.append(
                            f"  * VAL Error: 'Predicate {missing_pred} not found' in problem initial/goal state.\n"
                            f"    CRITICAL ROOT CAUSE: Atomic formula in problem ':init' or ':goal' uses predicate '{missing_pred}', but '{missing_pred}' is NOT declared in domain 'predicates'.\n"
                            f"    MANDATORY REPAIR ACTION: In domain 'predicates', declare predicate '({missing_pred} ...)' with its appropriate typed parameter signature matching its arguments, or update the atom in problem 'initial_state' to use the correct declared predicate name."
                        )

                m_unk = re.search(r"Object with unknown type:\s*([a-zA-Z0-9_\-]+)", line)
                if m_unk:
                    unk_symbol = m_unk.group(1)
                    dom_constants = domain_bp.get("constants", {}) if isinstance(domain_bp, dict) else {}
                    prob_objects = problem_bp.get("objects", {}) if isinstance(problem_bp, dict) else {}
                    obj_types_set = set(prob_objects.values())

                    act_params = {}
                    for a in domain_bp.get("actions", []) if isinstance(domain_bp, dict) else []:
                        if a.get("action_name") == current_val_action or a.get("name") == current_val_action:
                            act_params = a.get("parameters", {})
                            break
                    param_types = set(act_params.values()) if isinstance(act_params, dict) else set()

                    if unk_symbol == "object":
                        hint = (
                            "VAL Error: 'Object with unknown type: object'. 'object' is the universal root type in Classical PDDL 2.1. "
                            "Ensure all types in domain 'types' inherit directly or indirectly from 'object'. Do NOT declare 'object' as a child of another type or declare 'object: object'."
                        )
                        target_elem = "types"
                    elif current_val_action:
                        # VAL is type-checking a domain action schema!
                        # In Classical PDDL 2.1, domain action schemas cannot reference problem :objects.
                        if unk_symbol in dom_constants:
                            hint = (
                                f"Constant '{unk_symbol}' in domain 'constants' is missing an explicit type declaration. "
                                f"In Classical PDDL (:typing), every constant must have a declared type. In domain 'constants', declare '{unk_symbol} - <type>' (e.g. '{unk_symbol} - object')."
                            )
                            target_elem = "constants"
                        elif unk_symbol in param_types:
                            if unk_symbol in obj_types_set:
                                hint = (
                                    f"Action '{current_val_action}' parameter requires type '{unk_symbol}', which exists in problem ':objects' but is missing from domain 'types'. "
                                    f"In domain 'types', declare '{unk_symbol}': 'object' (or its appropriate supertype)."
                                )
                                target_elem = "types"
                            else:
                                hint = (
                                    f"Action '{current_val_action}' declares a parameter with unknown type '{unk_symbol}', but problem :objects contains ZERO objects of type '{unk_symbol}'. "
                                    f"Do NOT declare '{unk_symbol}' in domain 'types' because it has no objects in problem :objects (this would make the action dead/ungroundable). "
                                    f"Remove parameter '?p - {unk_symbol}' from '{current_val_action}' and model the requirement as a state predicate over existing parameters."
                                )
                                target_elem = current_val_action or "types"
                        else:
                            # Symbol is referenced directly in the action schema (e.g. as a constant or literal entity)
                            hint = (
                                f"Symbol '{unk_symbol}' referenced in domain action '{current_val_action}' is treated as a constant/object but is not declared in domain 'constants'. "
                                f"In Classical PDDL 2.1, domain action schemas cannot access problem ':objects'. "
                                f"To resolve this, either: "
                                f"1) Declare '{unk_symbol} - <type>' in domain 'constants' (and remove '{unk_symbol}' from problem ':objects' to prevent duplicate object errors), "
                                f"2) Declare it as an action parameter in '{current_val_action}', or "
                                f"3) Model the condition as a state predicate (e.g. unary predicate) without referencing an undeclared constant."
                            )
                            target_elem = current_val_action
                    else:
                        # VAL is type-checking problem objects or initial/goal state
                        if unk_symbol in dom_constants:
                            hint = (
                                f"Constant '{unk_symbol}' in domain 'constants' is missing an explicit type declaration. "
                                f"In Classical PDDL (:typing), every constant must have a declared type. In domain 'constants', declare '{unk_symbol} - <type>' (e.g. '{unk_symbol} - object')."
                            )
                            target_elem = "constants"
                        elif unk_symbol in prob_objects:
                            hint = (
                                f"Object '{unk_symbol}' in problem ':objects' is missing an explicit type declaration. In problem ':objects', declare '{unk_symbol} - <type>'."
                            )
                            target_elem = "objects"
                        else:
                            hint = (
                                f"Symbol '{unk_symbol}' in problem definition has unknown type. "
                                f"Declare '{unk_symbol} - <type>' in problem ':objects' or domain 'constants'."
                            )
                            target_elem = "objects"

                    unknown_type_entries.append({
                        "action_name": current_val_action,
                        "unknown_symbol": unk_symbol,
                        "target_element": target_elem,
                        "hint": hint,
                        "raw_log": line.strip()
                    })
                    val_type_diagnostics.append(f"  * {hint}")

                m_arity = re.search(r"Type problem with proposition \(([a-zA-Z0-9_\-]+)[^)]*\)\s*-\s*too\s+(few|many)\s+parameters", line, re.IGNORECASE)
                if m_arity:
                    pred_name = m_arity.group(1)
                    problem_kind = m_arity.group(2).lower()
                    decl_str = ""
                    for p_decl in domain_bp.get("predicates", []):
                        clean_p = str(p_decl).strip('() ')
                        toks = clean_p.split()
                        if toks and toks[0] == pred_name:
                            decl_str = f"'{p_decl}'"
                            break
                    val_type_diagnostics.append(
                        f"  * Proposition in action '{current_val_action}' uses predicate '{pred_name}' with too {problem_kind} arguments compared to its declared signature {decl_str or f'for {pred_name}'}.\n"
                        f"    DIAGNOSIS & MANDATORY ACTION (PREDICATE OVERLOADING STRICTLY FORBIDDEN IN CLASSICAL PDDL):\n"
                        f"    In Classical PDDL 2.1, predicate symbols CANNOT be overloaded with different arities or multiple meanings. "
                        f"    If the natural language describes distinct relations (e.g. an entity's location vs a feature or sample at a location), "
                        f"    they MUST be declared as two separate, dedicated predicate symbols (e.g. binary '(at ?entity ?location)' AND unary '(at-target ?location)'). "
                        f"    Do NOT reuse or overload '{pred_name}' with conflicting arity! Declare a dedicated distinct predicate symbol in domain 'predicates' "
                        f"    with the required arity and update the action schemas, initial state, and goals to use this dedicated predicate."
                    )

                m = re.search(r"Type problem with proposition \(([a-zA-Z0-9_\-]+)\s+([^)]+)\)\s*-\s*parameter\s*(\d+)\s*is incorrectly typed", line)
                if m:
                    pred_name = m.group(1)
                    args = m.group(2).split()
                    param_idx = int(m.group(3)) - 1
                    faulty_arg = args[param_idx] if param_idx < len(args) else "unknown"
                    arg_type = None
                    obj_types = problem_bp.get("objects", {})
                    if faulty_arg in obj_types:
                        arg_type = obj_types[faulty_arg]
                    elif current_val_action:
                        for act in domain_bp.get("actions", []):
                            act_name = act.get("name") if isinstance(act, dict) else getattr(act, "name", None)
                            if act_name == current_val_action:
                                act_params = act.get("parameters", {}) if isinstance(act, dict) else getattr(act, "parameters", {})
                                if isinstance(act_params, dict):
                                    for p_name, p_type in act_params.items():
                                        if p_name.lstrip("?") == faulty_arg.lstrip("?"):
                                            arg_type = p_type
                                            break
                                break
                    if not arg_type:
                        arg_type = "object"
                    
                    expected_type = "object"
                    for p_decl in domain_bp.get("predicates", []):
                        clean_p = str(p_decl).strip('() ')
                        toks = clean_p.split()
                        if toks and toks[0] == pred_name:
                            matches = re.findall(r"\?\w+\s*-\s*([a-zA-Z0-9_\-]+)", clean_p)
                            if param_idx < len(matches):
                                expected_type = matches[param_idx]
                                break
                                
                    dom_types = domain_bp.get("types", {})
                    current_parent = dom_types.get(arg_type, "object") if isinstance(dom_types, dict) else "object"
                    
                    type_mismatch_entries.append({
                        "pred_name": pred_name,
                        "faulty_arg": faulty_arg,
                        "arg_type": arg_type,
                        "expected_type": expected_type,
                        "current_parent": current_parent,
                        "param_idx": param_idx,
                        "current_val_action": current_val_action,
                        "raw_log": line.strip()
                    })
                    
                    if is_subtype(expected_type, arg_type, dom_types) and expected_type.lower() != arg_type.lower():
                        val_type_diagnostics.append(
                            f"  * Proposition '({pred_name} {' '.join(args)})' (parameter {param_idx + 1}): Object/parameter '{faulty_arg}' has declared type '{arg_type}', but predicate '{pred_name}' parameter {param_idx + 1} was declared too narrowly expecting subtype '{expected_type}' (which already inherits from '{arg_type}').\n"
                            f"    DIAGNOSIS & MANDATORY ACTION:\n"
                            f"    1) In domain 'predicates', generalize parameter {param_idx + 1} of predicate '{pred_name}' to supertype '{arg_type}' (e.g. '({pred_name} ... ?x - {arg_type} ...)').\n"
                            f"    2) Alternatively, if '{faulty_arg}' in problem ':objects' is intended to be a specialized '{expected_type}', declare '{faulty_arg} - {expected_type}' in problem ':objects'.\n"
                            f"    Do NOT declare '{arg_type}' as a subtype of '{expected_type}' in domain 'types' (subtyping cannot be inverted)."
                        )
                    elif arg_type.lower() == expected_type.lower():
                        val_type_diagnostics.append(
                            f"  * Action '{current_val_action}' proposition '({pred_name} {' '.join(args)})' (parameter {param_idx + 1}): Parameter '{faulty_arg}' has type '{arg_type}' (inheriting from '{current_parent}').\n"
                            f"    VAL failed type-checking against expected type '{expected_type}' because intermediate supertype '{current_parent}' is not declared as inheriting from '{expected_type}' in domain 'types'.\n"
                            f"    DIAGNOSIS & MANDATORY ACTION: In domain 'types', ensure '{current_parent}': '{expected_type}' is declared. NEVER declare 'object': 'object'."
                        )
                    else:
                        val_type_diagnostics.append(
                            f"  * Proposition '({pred_name} {' '.join(args)})' (parameter {param_idx + 1}): Object/parameter '{faulty_arg}' has declared type '{arg_type}' (currently inheriting from '{current_parent}'), but predicate '{pred_name}' parameter {param_idx + 1} expects type '{expected_type}'.\n"
                            f"    DIAGNOSIS & MANDATORY ACTION: In domain 'types', check if '{arg_type}' should inherit from '{expected_type}' (e.g. declare '{arg_type}': '{expected_type}', or declare intermediate type '{current_parent}': '{expected_type}'). If '{arg_type}' is a subtype of '{expected_type}', update domain 'types' accordingly. Do NOT change the predicate declaration if it already expects the correct parent type!"
                        )

        type_diag_str = "\n".join(val_type_diagnostics) if val_type_diagnostics else ""
        if type_diag_str:
            type_diag_section = f"\nGROUNDED TYPE HIERARCHY MISMATCH TRACE:\n{type_diag_str}\n"
        else:
            type_diag_section = ""

        focus_guidance = f"""
CRITICAL TRIAGE FOCUS:
The primary error is a strict syntax or type-checking violation detected by VAL.
Focus strictly on localizing and resolving the syntax or type/arity mismatch in the indicated action/predicate schema or domain types hierarchy.
Do NOT report speculative state-reachability, cycle, or goal-distance issues when the domain has an active type or syntax defect.
{type_diag_section}
MANDATORY TYPE-CHECKING & SUBTYPING HIERARCHY RULES:
When VAL reports: "Type problem with proposition (p ...) - parameter N is incorrectly typed":
1. Check the type of the argument being passed in the action versus the declared parameter type of predicate 'p' in 'predicates'.
2. CASE 0 — MISSING SUBTYPE DECLARATION IN 'types':
   - If the object/argument's type is conceptually a subtype of the expected parameter type (e.g., child type 'subtype_entity' is a subtype of parent type 'supertype_entity'), the domain 'types' is missing the subtype inheritance!
   - The MANDATORY repair hint is: "In domain 'types', declare the child type as inheriting from the parent type (e.g., declare 'child_type': 'parent_type'). Set faulty_element to 'types' (NOT the predicate name!). Do NOT modify the predicate declaration if it already expects the correct parent type!"
3. CASE A — COMMON SUPERTYPE GENERALIZATION (Inheritance & Subtyping):
   - Check if the passed argument type and the declared predicate parameter type share a common supertype in domain 'types' (e.g., both 'ingredient' and 'cocktail' inherit from 'beverage'; both 'shot' and 'shaker' inherit from 'container').
   - If they share a supertype, the predicate was declared TOO NARROWLY!
   - The MANDATORY repair hint is: "Generalize parameter N of predicate 'p' in 'predicates' to the common supertype (e.g., declare '(contains ?c - container ?b - beverage)' instead of narrowing to shot or cocktail)."
   - CRITICAL ANTI-PATTERN: NEVER invent narrow ad-hoc predicates like '(contains-cocktail ?s - shot ?c - cocktail)' and then advise an action with an 'ingredient' parameter (like 'fill-shot') to use it! In PDDL, an argument's type MUST be an instance or subtype of the declared parameter type.
4. CASE B — DISJOINT PHYSICAL STATES (e.g., Hand Emptiness vs Container Emptiness):
   - If the types are completely disjoint (e.g., 'hand' and 'container' both inherit directly from 'object' with no common subtype):
   - Natural language requirements often use the same English word for two distinct physical states (e.g., "hand D is empty" and "shot A is empty").
   - Since PDDL predicates cannot be overloaded, declare distinct predicates for the disjoint entities: e.g., '(handempty ?h - hand)' or '(hand-empty ?h - hand)' for hands, and '(empty ?c - container)' for containers.
   - Similarly, if an action establishes a state for entity x (e.g., "power is on for instrument x") while deleting a resource on host y (e.g., "power is available for host y"), declare separate predicates '(power-on ?x - instrument)' and '(power-available ?y - host)'. NEVER advise substituting x with y to produce contradictory effects '(and (p y) (not (p y)))'.
5. CASE C — OVERLOADED RELATIONS (e.g., Location-to-Location Visibility vs Target-to-Location Visibility):
   - If a relation symbol like 'visible' is used between two locations (e.g. waypoint to waypoint) and also between a target/item and a location (e.g. objective from waypoint):
   - In PDDL, predicate signatures cannot be overloaded with different types.
   - Declare a distinct predicate symbol for the second relation (e.g. '(visible-from ?o - objective ?w - waypoint)' or '(target-visible ?o - objective ?w - waypoint)'), OR generalize the predicate parameter to their common supertype (e.g. '(visible ?o - object ?w - waypoint)').
6. ANTI-OSCILLATION & DOMAIN-WIDE CONSISTENCY:
   - NEVER alternate a predicate declaration back and forth between incompatible types across repair iterations.
   - Verify that the proposed predicate signature satisfies all actions across the domain simultaneously.
"""
    orphaned_goals = causal_analysis.get("orphaned_goals", [])
    if orphaned_goals and not val_syntax_or_type_error:
        focus_guidance += f"""
CRITICAL UNREACHABILITY / ORPHANED GOAL DETECTED:
The goal specification requires predicate(s): {', '.join(orphaned_goals)}, but NO action in the domain produces them in its positive effects!
MANDATORY ORPHANED GOAL REPAIR GUIDANCE:
1. Review the Natural Language Requirements for the action that establishes this relationship (e.g. the action that drops, places, stacks, loads, or delivers the object).
2. Add the missing positive effect (e.g. '({orphaned_goals[0]} ...)') to that action's effect schema!
3. NEVER advise removing the delete effect from actions that legitimately delete this predicate (such as lifting or removing an object)!
"""

    ungroundable_preconditions = causal_analysis.get("ungroundable_preconditions", [])
    if ungroundable_preconditions and not val_syntax_or_type_error:
        dead_list = "\n".join([f"- Action '{u['action_name']}': {u['reason']}" for u in ungroundable_preconditions])
        focus_guidance += f"""
CRITICAL DEAD / UNGROUNDABLE PRECONDITIONS DETECTED:
The planner found NO relaxed solution because action preconditions require static predicate facts or type signatures that do NOT exist in problem :init:
{dead_list}
MANDATORY REPAIR GUIDANCE:
1. Compare the action preconditions against the Natural Language Requirements:
   - Did the action check a spatial relation directly against an entity rather than its location (e.g. checking relation directly against an object/agent rather than the location where it is stationed)?
   - When an entity is stationed at a location, actions communicating or interacting with it must declare the station location parameter (e.g. '?loc - location'), bind the entity via '(at ?entity ?loc)', and assert spatial relations between the locations.
   - Did the action mistakenly repeat a variable reflexively (e.g. '(at ?l ?l)')? Use distinct variables for distinct entities and locations!
2. If an action permanently deletes an indispensable state resource (like an agent's availability or channel) without restoring it upon completion, ensure the action effect restores the resource so subsequent actions remain executable!
3. INVERTED ARGUMENT ORDER IN STATIC RELATIONS:
   If a static relation (e.g. '(rel ?x ?y)') has ZERO matching facts in :init because the argument types are reversed compared to declared initial facts:
   Swap the arguments in the action precondition to match the declared relation signature in problem :init.
4. MUTUALLY EXCLUSIVE PRECONDITIONS (SUPPORT/CONTAINER VS ITEM CLEARANCE):
   When an action precondition checks both a support relation (e.g. '(on ?item ?support)' or '(in ?item ?container)') and a clearance condition (e.g. '(clear ?support)'):
   The entity that must be clear (unobstructed) to be lifted/manipulated is the ITEM '?item', NOT the supporting surface underneath it!
   In the action precondition, bind '(clear ?item)' to the item parameter already present in the action.
   DO NOT invent duplicate parameters of the same type (such as '?s1' and '?s2')!
"""

    unproducible_goals = causal_analysis.get("unproducible_goals", [])
    if unproducible_goals and not val_syntax_or_type_error:
        unprod_list = "\n".join([f"- Action '{u['action_name']}': {u['reason']}" for u in unproducible_goals])
        focus_guidance += f"""
CRITICAL STATICALLY UNPRODUCIBLE GOAL ATOMS (FIRST-ORDER LOGIC INVARIANT):
The planner found NO plan because required ground goal atoms cannot be produced by any action due to static precondition parameter bounding:
{unprod_list}
MANDATORY FIRST-ORDER LOGIC REPAIR GUIDANCE:
1. When an action parameter is bound to a static precondition, its groundings are strictly fixed to the initial facts of that static relation in :init.
2. If the goal requires a different target entity/object, review whether the action parameter has been conflated with the static entity, OR if problem 'initial_state' is missing an initial fact.
3. Review the Natural Language Requirements:
   - CASE A — MISSING INITIAL STATE FACT: If the requirements specify that the target entity/location possesses this initial property or sample, augment problem 'initial_state' with the missing atom (e.g. '(at-sample target_entity)').
   - CASE B — PARAMETER CONFLATION: If the requirement describes distinct entities or locations (e.g., an acting agent location, a stationary support/station, and a target item/data), declare dedicated, distinct parameters for each independent role in the action schema and ensure the action effect asserts the target entity parameter.
"""

    unreleased_resources = causal_analysis.get("unreleased_resources", [])
    if unreleased_resources and not val_syntax_or_type_error:
        leak_list = "\n".join([f"- Action '{u['action_name']}': {u['description']}" for u in unreleased_resources])
        focus_guidance += f"""
CRITICAL UNRELEASED RESOURCE SINK / LEAK DETECTED (FIRST-ORDER OCCUPANCY BALANCE):
The causal graph analyzer identified actions that delete holding/occupancy relations without replenishing the corresponding operational readiness resource:
{leak_list}
MANDATORY RESOURCE LEAK REPAIR GUIDANCE:
1. When an action removes an entity from a container, agent, or support surface S, it deletes the holding relation (e.g. '(on ?x ?s)').
2. Check the Natural Language Requirements for the vacated entity S:
   Does the text state: 'Once I ... it is the case that ... S is clear / available / free'?
3. Add the missing positive effect (e.g. '({unreleased_resources[0].get("resource_predicate", "clear")} ?{unreleased_resources[0].get("resource_arg", "s")})') to the action effect schema in domain 'actions' so the resource/support is restored for subsequent actions!
"""

    directional_traps = causal_analysis.get("directional_traps", [])
    if directional_traps and not val_syntax_or_type_error:
        traps_list = "\n".join([f"- {dt['reason']}" for dt in directional_traps])
        focus_guidance += f"""
CRITICAL DIRECTIONAL ASYMMETRY / MISSING INVERSE TRANSITION ACTIONS (CLASSICAL STRIPS INVARIANT):
The planner found NO valid plan because movement/transition is only modeled in one direction along an asymmetric static relation:
{traps_list}
MANDATORY STRIPS ACTION REPAIR GUIDANCE:
1. In Classical STRIPS (:strips :typing), disjunction ('or') in preconditions is strictly unsupported.
2. When requirements specify that entities can move/transition under multiple conditions or in both directions (e.g. forward and backward, or 'B is above C' and 'C is above B'):
   EACH distinct condition MUST be declared as a SEPARATE, uniquely-named action schema (e.g. adding suffix '_reverse', '_up', or '_2').
3. Add the missing inverse action schema to domain 'actions' with its parameters, preconditions (asserting the reverse relation atom), and transition effects matching the requirements!
"""

    planner_unsolvability = any("Could not find a plan" in err or "Search stopped without finding a solution" in err for err in raw_errors)
    if planner_unsolvability and not val_syntax_or_type_error:
        focus_guidance += f"""
CRITICAL PLANNER REACHABILITY / GOAL UNSOLVABILITY:
Fast Downward executed SAS+ translation and heuristic search, but found NO valid plan to reach the goal state.
MANDATORY DIAGNOSTIC AUDIT SEQUENCE:
1. STRICTLY FORBIDDEN: NEVER ADVISE RELAXING OR DELETING EXPLICIT PRECONDITIONS!
   - Natural language restrictions state necessary physical requirements.
   - NEVER suggest relaxing or deleting explicit preconditions that are directly stipulated in the text. Removing physical constraints corrupts the domain contract and fails formal verification.
2. UNUSABLE OBJECTS & OVERLY NARROW ACTION PARAMETERS:
   - Check if any objects in problem ':objects' have types that cannot be accepted by any action parameter in the domain (e.g. an action parameter requires a leaf subtype instead of the common supertype).
   - If objects of a valid subtype cannot be used in any action, advise declaring the common supertype in domain 'types' (e.g. 'place') and generalizing action parameters to that common supertype (e.g. '?p - place' instead of '?p - depot').
3. RESOURCE RELEASE VS OCCUPANCY (FAITHFULNESS TO NATURAL LANGUAGE EFFECTS):
   - CRITICAL MUTEX AUDIT: An agent or device that is holding, lifting, carrying, or transporting an object is OCCUPIED, NOT AVAILABLE!
     If the requirements explicitly state: 'Once I lift/pick-up/unload... it is NOT the case anymore that agent A is available/free', NEVER advise asserting availability on that lifting/unloading action! The agent/device only becomes available again when it DROPS, PUTS DOWN, or LOADS the object.
   - VACATED SUPPORTS / SURFACES / RECEPTACLES CLEARING:
     When an action lifts, extracts, or unstacks an entity from a supporting surface or receptacle S:
     Did the action omit the positive state-clearing effect explicitly described in the requirements (e.g. 'C is clear' -> '(clear ?s)'; 'receptacle is empty')?
     If an action removes an entity from a support S without asserting that S is clear, underlying entities remain permanently blocked and un-manipulable, causing planner reachability failure (heuristic = infinity)!
   - CONTRADICTORY SIMULTANEOUS EFFECTS:
     If an action simultaneously asserts both '(pred ?x)' and '(not (pred ?x))':
     Consult the Natural Language Requirements! Check whether the text says 'it is the case that ...' (keep the positive atom) or 'it is NOT the case anymore that ...' (keep the negative atom). NEVER advise adding a positive effect that directly contradicts an explicit negative effect in the text.
   - AUDIT EVERY ACTION INDIVIDUALLY: Inspect the CURRENT domain blueprint carefully. Compare each action's positive effects against the 'Once I ... it is the case that ...' statements in the text. Find the specific action that is ACTUALLY missing a positive transition effect described in the requirements!
"""

    prompt = f"""You are an expert PDDL Diagnostic & Fault Localization Oracle.

Your task is to analyze the failure signals from symbolic oracles (VAL / Fast Downward / Regression Suite) against the current PDDL relational blueprints, localize the root-cause fault, and produce structured DiagnosticReports.

NATURAL LANGUAGE REQUIREMENTS:
{requirements_text}

CURRENT DOMAIN BLUEPRINT:
```json
{json.dumps(domain_bp, indent=2)}
```

CURRENT PROBLEM BLUEPRINT:
```json
{json.dumps(problem_bp, indent=2)}
```

RAW ORACLE VERIFICATION ERRORS:
{error_traces_str}

GROUNDED ACTION-PREDICATE CAUSAL DEPENDENCY & REACHABILITY ANALYSIS:
{causal_summary}

    {focus_guidance}
    {STANDARD_CLASSICAL_PDDL_RULES}
    {STANDARD_DIAGNOSTIC_RULES}

    For each identified issue, provide:
    - error_category: SYNTAX_PARSE, TYPE_SIGNATURE, GROUNDING_UNSOLVABILITY, or HISTORICAL_REGRESSION.
      CRITICAL CATEGORIZATION INVARIANT:
      SYSTEM_ORACLE_ERROR is strictly forbidden for domain/problem AST defects, action precondition/effect errors, or planner solvability failures. SYSTEM_ORACLE_ERROR is reserved exclusively for missing host binary executables.
      Contradictory effects (e.g. simultaneously adding and deleting an atom) or invalid precondition syntax MUST be categorized under SYNTAX_PARSE or GROUNDING_UNSOLVABILITY with repair_operation_type EFFECT_ALIGNMENT or PRECONDITION_INSERTION/RELAXATION.
    - repair_operation_type: PRECONDITION_RELAXATION, PRECONDITION_INSERTION, EFFECT_ALIGNMENT, TYPE_ARITY_ALIGNMENT, INITIAL_STATE_AUGMENTATION, or GENERAL_AST_REPAIR
    - faulty_element: Name of the specific action (e.g. 'pick-up', 'drop', 'drive'), predicate, or null if general
    - raw_log: Exact or summarized log snippet from the oracle
    - suggested_repair_hint: CRITICAL PRESCRIPTIVE REPAIR DIRECTIVE:
      Do NOT merely restate what happened or describe the symptom. Provide exact, actionable instructions:
      1) The exact AST target to modify (e.g. 'domain.actions.<action_name>', 'domain.predicates', 'problem.objects').
      2) The concrete operation (e.g. 'ADD action schema <name>', 'REPLACE precondition <pred> with <pred>', 'ADD positive effect <pred>').
      3) The exact PDDL literal or signature to write, and why it resolves the oracle failure.

    Return a valid JSON object strictly matching the DiagnosticAnalysis schema.
    """

    print("[Triage Node]: Invoking Diagnostic LLM Agent for structured fault localization...")
    diagnostic_reports: List[DiagnosticReport] = []

    try:
        analysis, usage = invoke_structured_llm_with_telemetry(
            DiagnosticAnalysis,
            prompt,
            target_model=get_phase_model(3)
        )
        diagnostic_reports = analysis.reports

        # Update Telemetry Metrics
        state["total_prompt_tokens"] = state.get("total_prompt_tokens", 0) + usage.get("prompt_tokens", 0)
        state["total_completion_tokens"] = state.get("total_completion_tokens", 0) + usage.get("completion_tokens", 0)
        state["total_tokens"] = state.get("total_tokens", 0) + usage.get("total_tokens", 0)
        state["estimated_cost_usd"] = round(state.get("estimated_cost_usd", 0.0) + usage.get("estimated_cost_usd", 0.0), 6)
        print(f"[Triage Node]: Diagnostic LLM Agent identified {len(diagnostic_reports)} diagnostic item(s).")

        # Grounded Type Hierarchy Alignment: If VAL reported a parameter type mismatch,
        # guide the repair based on formal subtyping relation:
        if val_syntax_or_type_error and 'type_mismatch_entries' in locals():
            for tm in type_mismatch_entries:
                p_idx = tm.get("param_idx", 0) + 1
                dom_types = domain_bp.get("types", {}) if isinstance(domain_bp, dict) else {}
                
                if is_subtype(tm["expected_type"], tm["arg_type"], dom_types) and tm["expected_type"].lower() != tm["arg_type"].lower():
                    target_elem = tm["pred_name"]
                    hint = (
                        f"Type mismatch on proposition '({tm['pred_name']} {tm['faulty_arg']} ...)': Object/parameter '{tm['faulty_arg']}' has declared type '{tm['arg_type']}', but predicate '{tm['pred_name']}' was declared too narrowly expecting subtype '{tm['expected_type']}' (which already inherits from '{tm['arg_type']}'). "
                        f"In domain 'predicates', generalize parameter {p_idx} of predicate '{tm['pred_name']}' to supertype '{tm['arg_type']}' (e.g. '({tm['pred_name']} ... ?x - {tm['arg_type']} ...)'). Alternatively, if problem requirements designate that '{tm['faulty_arg']}' is a specialized '{tm['expected_type']}', declare '{tm['faulty_arg']} - {tm['expected_type']}' in problem ':objects'. "
                        f"Do NOT invert domain 'types' by declaring '{tm['arg_type']}' as a subtype of '{tm['expected_type']}'."
                    )
                else:
                    target_elem = "types"
                    hint = (
                        f"In domain 'types', declare '{tm['arg_type']}': '{tm['expected_type']}' "
                        f"(currently inheriting from '{tm['current_parent']}'). Object '{tm['faulty_arg']}' has type '{tm['arg_type']}' "
                        f"and must inherit from '{tm['expected_type']}' to satisfy predicate '{tm['pred_name']}'. "
                        f"Do NOT change predicate '{tm['pred_name']}', as it already expects '{tm['expected_type']}'."
                    )
                
                matched = False
                for rep in diagnostic_reports:
                    if rep.error_category == ErrorCategory.TYPE_SIGNATURE and (rep.faulty_element in [tm["pred_name"], "types", tm["arg_type"], target_elem]):
                        rep.faulty_element = target_elem
                        rep.repair_operation_type = RepairOperationType.TYPE_ARITY_ALIGNMENT
                        rep.suggested_repair_hint = hint
                        matched = True
                        break
                if not matched:
                    diagnostic_reports.append(DiagnosticReport(
                        error_category=ErrorCategory.TYPE_SIGNATURE,
                        repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
                        faulty_element=target_elem,
                        raw_log=tm["raw_log"],
                        suggested_repair_hint=hint
                    ))

        if val_syntax_or_type_error and 'unknown_type_entries' in locals():
            for ute in unknown_type_entries:
                act = ute["action_name"] or "types"
                target_elem = ute["target_element"]
                hint = ute["hint"]
                sym = ute["unknown_symbol"]

                matched = False
                for rep in diagnostic_reports:
                    if rep.error_category == ErrorCategory.TYPE_SIGNATURE and (rep.faulty_element in [target_elem, act, "types", sym]):
                        rep.faulty_element = target_elem
                        rep.repair_operation_type = RepairOperationType.TYPE_ARITY_ALIGNMENT
                        rep.suggested_repair_hint = hint
                        matched = True
                        break
                if not matched:
                    diagnostic_reports.append(DiagnosticReport(
                        error_category=ErrorCategory.TYPE_SIGNATURE,
                        repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
                        faulty_element=target_elem,
                        raw_log=ute["raw_log"],
                        suggested_repair_hint=hint
                    ))

        # Grounded Action Reachability Alignment: If planner reported unsolvability and causal analysis
        # proved an action is dead due to empty parameter domain (0 objects of parameter type),
        # ensure diagnostic reports highlight this mathematical dead-end:
        ungroundable_list = causal_analysis.get("ungroundable_preconditions", [])
        for up in ungroundable_list:
            if "ZERO objects of type" in up.get("reason", ""):
                act = up.get("action_name", "")
                hint = up.get("reason", "")
                matched = False
                for rep in diagnostic_reports:
                    if rep.faulty_element in [act, "objects", up.get("predicate")]:
                        rep.faulty_element = act
                        rep.error_category = ErrorCategory.GROUNDING_UNSOLVABILITY
                        rep.repair_operation_type = RepairOperationType.TYPE_ARITY_ALIGNMENT
                        rep.suggested_repair_hint = hint
                        matched = True
                        break
                if not matched:
                    diagnostic_reports.append(DiagnosticReport(
                        error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
                        repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
                        faulty_element=act,
                        raw_log=up.get("reason", ""),
                        suggested_repair_hint=hint
                    ))

        # Grounded Directional Asymmetry Alignment: If planner reported unsolvability and causal analysis
        # proved a directional asymmetry trap (actions only permit one-way movement on an asymmetric relation,
        # but goals require reverse movement), ensure diagnostic reports highlight this structural deadlock:
        directional_traps = causal_analysis.get("directional_traps", [])
        for dt in directional_traps:
            f_acts = dt.get("forward_actions", [])
            act_target = f_acts[0] if f_acts else "domain.actions"
            hint = dt.get("reason", "")
            matched = False
            for rep in diagnostic_reports:
                if rep.faulty_element in f_acts or rep.faulty_element in ["actions", "domain.actions", dt.get("relation")]:
                    rep.faulty_element = act_target
                    rep.error_category = ErrorCategory.GROUNDING_UNSOLVABILITY
                    rep.repair_operation_type = RepairOperationType.GENERAL_AST_REPAIR
                    rep.suggested_repair_hint = hint
                    matched = True
                    break
            if not matched:
                diagnostic_reports.append(DiagnosticReport(
                    error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
                    repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
                    faulty_element=act_target,
                    raw_log=f"Directional Asymmetry Deadlock: static relation '{dt.get('relation')}' is directed and missing inverse action.",
                    suggested_repair_hint=hint
                ))
    except Exception as triage_err:
        print(f"[Triage Node ERROR]: Diagnostic LLM call failed: {triage_err}")
        # Strictly record the failure; NO deterministic heuristic fallbacks or ground-truth substitutions
        state["verification_errors"] = [f"Triage Diagnostic LLM Exception: {triage_err}"]
        state["diagnostic_reports"] = []
        state["formatted_diagnostic_feedback"] = f"Diagnostic LLM Failure: {triage_err}"
        elapsed = time.time() - start_t
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + elapsed, 3)
        state["node_latencies"] = latencies
        return state

    # Store structured reports and formatted feedback in state
    dumped_reports = [r.model_dump() for r in diagnostic_reports]
    state["diagnostic_reports"] = dumped_reports
    state["formatted_diagnostic_feedback"] = format_diagnostic_feedback(diagnostic_reports)

    # Accumulate historical reports for evaluation metrics
    hist_reports = state.get("historical_diagnostic_reports", [])
    for dr in dumped_reports:
        if dr not in hist_reports:
            hist_reports.append(dr)
    state["historical_diagnostic_reports"] = hist_reports

    elapsed = time.time() - start_t
    latencies = state.get("node_latencies", {})
    latencies["triage"] = round(latencies.get("triage", 0.0) + elapsed, 3)
    state["node_latencies"] = latencies

    return state
