#!/usr/bin/env python3
"""
tools/sbfl_analyzer.py
Spectrum-Based Fault Localization (SBFL) & Classical Causal Graph Diagnostic Engine.
Grounded in classical planning literature:
- Helmert (JAIR 2006): The Causal Graph for Fast Downward & SAS+ Planning.
- Torralba, Croitoru, Hoffmann (Saarland University 2018/2019): AI Planning Causal Graphs.
  * Invariant 1: Goal Relevance & Non-Goal Leaf Variable Pruning (Slide 18).
  * Invariant 2: Causal Cycle & Precondition Deadlock Detection (Slide 10/23).
  * Invariant 3: Domain Transition Graph (DTG) Invertibility & Irreversible Absorbing States (Slide 14).
  * Invariant 4: Mutex Contradictions & Effect-Effect Co-occurrences (Slide 9).
- Abreu et al. (2007) / Ochiai (1957): Mathematical Spectrum-Based Fault Localization.
Operates strictly on pure classical PDDL 2.1 (:strips, :typing) AST blueprints.
"""

import math
import re
from typing import Dict, List, Set, Any, Optional, Tuple
from tools.blueprint_parser import extract_predicate_names

def parse_atom_predicate_and_polarity(atom: str) -> Tuple[str, bool]:
    """
    Parses a PDDL atom into (predicate_name, is_positive).
    Example: '(not (clear ?x))' -> ('clear', False)
    Example: '(at ?r ?l)' -> ('at', True)
    """
    clean = atom.strip()
    is_positive = True
    if clean.startswith("(") and clean.endswith(")"):
        inner = clean[1:-1].strip()
    else:
        inner = clean

    if inner.lower().startswith("not"):
        is_positive = False
        inner = inner[3:].strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1].strip()

    tokens = inner.split()
    pred_name = tokens[0].lower() if tokens else ""
    return pred_name, is_positive

def compute_ochiai_score(e_f: int, e_p: int, n_f: int, n_p: int) -> float:
    """
    Computes the spectrum-based suspiciousness coefficient (Ochiai metric):
    sigma = e_f / sqrt((e_f + n_f) * (e_f + e_p))
    
    Returns float in range [0.0, 1.0].
    """
    if e_f <= 0:
        return 0.0
    denominator = math.sqrt(float((e_f + n_f) * (e_f + e_p)))
    if denominator == 0.0:
        return 0.0
    return round(float(e_f / denominator), 3)

def build_causal_graph_maps(domain_bp: Any, problem_bp: Any) -> Dict[str, Any]:
    """
    Builds the lifted bipartite Causal Graph maps from domain and problem blueprints:
    - producers: pred -> list of action_names that add pred
    - consumers: pred -> list of action_names that require pred as pos precondition
    - deleters: pred -> list of action_names that delete pred
    - action_adds: action_name -> set of added preds
    - action_dels: action_name -> set of deleted preds
    - action_preconds: action_name -> set of required positive preds
    - action_neg_preconds: action_name -> set of required negative preds
    - goal_preds: set of predicates specified in problem :goal
    - init_preds: set of predicates specified in problem :init
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    
    producers: Dict[str, Set[str]] = {}
    consumers: Dict[str, Set[str]] = {}
    deleters: Dict[str, Set[str]] = {}
    action_adds: Dict[str, Set[str]] = {}
    action_dels: Dict[str, Set[str]] = {}
    action_preconds: Dict[str, Set[str]] = {}
    action_neg_preconds: Dict[str, Set[str]] = {}

    for act in actions:
        name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        precs = getattr(act, "preconditions", []) if hasattr(act, "preconditions") else act.get("preconditions", [])

        action_adds[name] = set()
        action_dels[name] = set()
        action_preconds[name] = set()
        action_neg_preconds[name] = set()

        for eff in effs:
            pname, is_pos = parse_atom_predicate_and_polarity(eff)
            if not pname:
                continue
            if is_pos:
                action_adds[name].add(pname)
                producers.setdefault(pname, set()).add(name)
            else:
                action_dels[name].add(pname)
                deleters.setdefault(pname, set()).add(name)

        for prec in precs:
            pname, is_pos = parse_atom_predicate_and_polarity(prec)
            if not pname:
                continue
            if is_pos:
                action_preconds[name].add(pname)
                consumers.setdefault(pname, set()).add(name)
            else:
                action_neg_preconds[name].add(pname)

    # Problem Init and Goal predicates
    goal_atoms = []
    if hasattr(problem_bp, "goal_state") and getattr(problem_bp, "goal_state"):
        goal_atoms = getattr(problem_bp, "goal_state")
    elif hasattr(problem_bp, "goal") and getattr(problem_bp, "goal"):
        goal_atoms = getattr(problem_bp, "goal")
    elif isinstance(problem_bp, dict):
        goal_atoms = problem_bp.get("goal_state") or problem_bp.get("goal") or []

    init_atoms = []
    if hasattr(problem_bp, "initial_state") and getattr(problem_bp, "initial_state"):
        init_atoms = getattr(problem_bp, "initial_state")
    elif hasattr(problem_bp, "init") and getattr(problem_bp, "init"):
        init_atoms = getattr(problem_bp, "init")
    elif isinstance(problem_bp, dict):
        init_atoms = problem_bp.get("initial_state") or problem_bp.get("init") or []

    goal_preds = set()
    for g in goal_atoms:
        pname, _ = parse_atom_predicate_and_polarity(g)
        if pname:
            goal_preds.add(pname)

    init_preds = set()
    for i in init_atoms:
        pname, _ = parse_atom_predicate_and_polarity(i)
        if pname:
            init_preds.add(pname)

    return {
        "producers": producers,
        "consumers": consumers,
        "deleters": deleters,
        "action_adds": action_adds,
        "action_dels": action_dels,
        "action_preconds": action_preconds,
        "action_neg_preconds": action_neg_preconds,
        "goal_preds": goal_preds,
        "init_preds": init_preds,
        "action_names": [getattr(a, "action_name", "") if hasattr(a, "action_name") else a.get("action_name", "") for a in actions]
    }

def analyze_goal_relevance(
    cg_maps: Dict[str, Any]
) -> Tuple[Dict[str, int], Set[str]]:
    """
    Parameter 1: Goal Relevance & Non-Goal Leaf Variable Pruning (Torralba & Hoffmann Slide 18).
    Performs backward search from goal predicates along the causal graph to compute:
    - distance: shortest causal distance from action's effects to the goal (1 = direct goal producer, etc.)
    - non_goal_leaf_actions: actions that produce no predicates needed for any goal or intermediate enabler.
    """
    producers = cg_maps["producers"]
    action_preconds = cg_maps["action_preconds"]
    action_adds = cg_maps["action_adds"]
    goal_preds = cg_maps["goal_preds"]
    action_names = cg_maps["action_names"]

    action_distance: Dict[str, int] = {}
    visited_preds: Set[str] = set()
    current_preds: Set[str] = set(goal_preds)
    current_dist = 1

    while current_preds:
        next_preds: Set[str] = set()
        for pred in current_preds:
            visited_preds.add(pred)
            for act in producers.get(pred, set()):
                if act not in action_distance:
                    action_distance[act] = current_dist
                    for req_pred in action_preconds.get(act, set()):
                        if req_pred not in visited_preds:
                            next_preds.add(req_pred)
        current_preds = next_preds
        current_dist += 1

    # Non-goal leaf actions: actions with no causal path to any goal predicate
    non_goal_leaf_actions = set()
    for act in action_names:
        if act not in action_distance:
            non_goal_leaf_actions.add(act)

    return action_distance, non_goal_leaf_actions

def detect_causal_deadlocks_and_cycles(
    cg_maps: Dict[str, Any]
) -> List[List[str]]:
    """
    Parameter 2: Causal Cycle & Precondition Deadlock Detection (Torralba & Hoffmann Slide 10/23).
    Constructs the action enablement graph: directed edge (A -> B) if AddEffects(A) intersects Preconditions(B).
    Identifies circular action loops that lack an initial state bootstrap (causing search exhaustion or deadlocks).
    """
    action_adds = cg_maps["action_adds"]
    action_preconds = cg_maps["action_preconds"]
    init_preds = cg_maps["init_preds"]
    action_names = cg_maps["action_names"]

    # Check for direct self-deadlocks: action requires a precondition that it produces itself,
    # but no OTHER action in the domain produces it and it is not in :init
    detected_cycles: List[List[str]] = []
    for a in action_names:
        self_deps = action_adds[a].intersection(action_preconds[a])
        for p in self_deps:
            if p not in init_preds:
                other_producers = [o for o in action_names if o != a and p in action_adds[o]]
                if not other_producers:
                    detected_cycles.append([a, a])

    # Adjacency for multi-action cycles: act_a -> act_b where A produces a precondition for B
    adj: Dict[str, Set[str]] = {a: set() for a in action_names}
    for a in action_names:
        for b in action_names:
            if a != b:
                shared = action_adds[a].intersection(action_preconds[b])
                # Only consider an edge if at least one shared precondition is NOT already true in :init
                uninit_shared = {p for p in shared if p not in init_preds}
                if uninit_shared:
                    adj[a].add(b)

    # Detect multi-action cycles via DFS cycle finding
    visited: Set[str] = set()
    rec_stack: List[str] = []

    def dfs(curr: str):
        visited.add(curr)
        rec_stack.append(curr)
        for nxt in adj.get(curr, set()):
            if nxt not in visited:
                dfs(nxt)
            elif nxt in rec_stack:
                cycle_start_idx = rec_stack.index(nxt)
                cycle = rec_stack[cycle_start_idx:] + [nxt]
                norm_cycle = tuple(sorted(cycle[:-1]))
                if not any(tuple(sorted(c[:-1])) == norm_cycle for c in detected_cycles):
                    detected_cycles.append(cycle)
        rec_stack.pop()

    for act in action_names:
        if act not in visited:
            dfs(act)

    return detected_cycles

def detect_dtg_irreversibility(
    cg_maps: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Parameter 3: Domain Transition Graph (DTG) Invertibility & Irreversible Absorbing States (Slide 14).
    Flags any predicate that is deleted by an action but has NO producer in the entire domain.
    If such a predicate is needed for the goal or future actions, deleting it forms an irreversible absorbing state.
    """
    producers = cg_maps["producers"]
    deleters = cg_maps["deleters"]
    goal_preds = cg_maps["goal_preds"]
    consumers = cg_maps["consumers"]

    irreversible_issues = []
    for pred, del_actions in deleters.items():
        # Check if any action in the domain can reproduce this predicate once deleted
        adding_actions = producers.get(pred, set())
        if not adding_actions:
            is_goal = pred in goal_preds
            dependent_actions = consumers.get(pred, set())
            irreversible_issues.append({
                "predicate": pred,
                "deleted_by": sorted(list(del_actions)),
                "is_goal_predicate": is_goal,
                "required_by_actions": sorted(list(dependent_actions)),
                "severity": "CRITICAL" if (is_goal or dependent_actions) else "WARNING"
            })

    return irreversible_issues

def normalize_atom_expression(atom: str) -> Tuple[str, bool]:
    """
    Normalizes an atom into a canonical representation (without outer 'not')
    and returns (canonical_expr, is_positive).
    Example: '(not (clear ?x))' -> ('(clear ?x)', False)
    Example: '(clear ?x)' -> ('(clear ?x)', True)
    """
    clean = atom.strip()
    is_positive = True
    if clean.startswith("(") and clean.endswith(")"):
        inner = clean[1:-1].strip()
    else:
        inner = clean

    if inner.lower().startswith("not"):
        is_positive = False
        inner = inner[3:].strip()
        if inner.startswith("(") and inner.endswith(")"):
            inner = inner[1:-1].strip()

    tokens = inner.split()
    canonical = f"({' '.join(tokens)})" if tokens else ""
    return canonical, is_positive

def detect_internal_contradictions(
    domain_bp: Any
) -> List[Dict[str, Any]]:
    """
    Parameter 4: Mutex Contradiction & Effect-Effect Co-occurrences (Slide 9).
    Flags actions with internal STRIPS contradictions:
    - Adding and deleting the exact same atom simultaneously in :effect.
    - Requiring positive and negative of the exact same atom simultaneously in :precondition.
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    contradictions = []

    for act in actions:
        name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        precs = getattr(act, "preconditions", []) if hasattr(act, "preconditions") else act.get("preconditions", [])

        add_atoms = set()
        del_atoms = set()
        for eff in effs:
            canon, is_pos = normalize_atom_expression(eff)
            if canon:
                if is_pos:
                    add_atoms.add(canon)
                else:
                    del_atoms.add(canon)

        pos_precs = set()
        neg_precs = set()
        for prec in precs:
            canon, is_pos = normalize_atom_expression(prec)
            if canon:
                if is_pos:
                    pos_precs.add(canon)
                else:
                    neg_precs.add(canon)

        effect_clashes = add_atoms.intersection(del_atoms)
        precond_clashes = pos_precs.intersection(neg_precs)

        if effect_clashes:
            contradictions.append({
                "action_name": name,
                "type": "EFFECT_SELF_CONTRADICTION",
                "predicates": sorted(list(effect_clashes)),
                "description": f"Action '{name}' simultaneously adds and deletes atom(s): {', '.join(sorted(list(effect_clashes)))}."
            })
        if precond_clashes:
            contradictions.append({
                "action_name": name,
                "type": "PRECONDITION_SELF_CONTRADICTION",
                "predicates": sorted(list(precond_clashes)),
                "description": f"Action '{name}' simultaneously requires positive and negative precondition(s): {', '.join(sorted(list(precond_clashes)))}."
            })

    return contradictions

def run_causal_graph_sbfl_analysis(
    domain_bp: Any,
    problem_bp: Any,
    raw_errors: List[str],
    historical_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Unified Causal Graph & Spectrum-Based Fault Localization (SBFL) Engine.
    Executes all four classical planning causal graph invariants and computes
    grounded suspiciousness scores across all action schemas.
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    if not actions:
        return {
            "ranked_actions": [],
            "top_action": "General / Syntax",
            "top_score": 0.0,
            "goal_distances": {},
            "non_goal_leaf_actions": [],
            "causal_cycles": [],
            "irreversible_transitions": [],
            "internal_contradictions": [],
            "diagnostic_summary": "Empty domain actions."
        }

    # 1. Build Bipartite Causal Graph Maps
    cg_maps = build_causal_graph_maps(domain_bp, problem_bp)
    action_names = cg_maps["action_names"]

    # 2. Compute 4 Classical Invariants
    action_dist, non_goal_leaf_actions = analyze_goal_relevance(cg_maps)
    causal_cycles = detect_causal_deadlocks_and_cycles(cg_maps)
    irreversible_transitions = detect_dtg_irreversibility(cg_maps)
    internal_contradictions = detect_internal_contradictions(domain_bp)

    # 3. Filter Error Traces for Spectrum Implication
    filtered_error_lines = []
    for err in raw_errors:
        for line in err.splitlines():
            line_lower = line.lower()
            if "passes type checking" in line_lower or "action passes" in line_lower:
                continue
            filtered_error_lines.append(line_lower)
    filtered_error_str = " ".join(filtered_error_lines)

    # 4. Initialize Execution Spectrum
    spectrum: Dict[str, Dict[str, int]] = {
        name: {"e_f": 0, "e_p": 0, "n_f": 0, "n_p": 0} for name in action_names
    }

    # If historical test runs exist, incorporate empirical execution spectrum
    if historical_results:
        for hist in historical_results:
            passed = hist.get("passed", False)
            used_actions = set(hist.get("used_actions", []))
            if passed:
                for name in action_names:
                    if name in used_actions:
                        spectrum[name]["e_p"] += 1
                    else:
                        spectrum[name]["n_p"] += 1
            else:
                for name in action_names:
                    if name in used_actions:
                        spectrum[name]["e_f"] += 1
                    else:
                        spectrum[name]["n_f"] += 1

    # Implication from active failure:
    for name in action_names:
        implicated = False

        # Name explicitly mentioned in validator/planner trace
        pattern = rf"\b{re.escape(name.lower())}\b"
        if re.search(pattern, filtered_error_str):
            implicated = True

        # Precondition or effect predicate explicitly implicated
        for p in cg_maps["action_preconds"].get(name, set()).union(cg_maps["action_adds"].get(name, set())):
            p_pattern = rf"\b{re.escape(p.lower())}\b"
            if re.search(p_pattern, filtered_error_str):
                implicated = True

        # Implicated by structural defects
        if any(c["action_name"] == name for c in internal_contradictions):
            implicated = True
        if any(name in cycle for cycle in causal_cycles):
            implicated = True
        if any(name in it.get("deleted_by", []) and it.get("severity") == "CRITICAL" for it in irreversible_transitions):
            implicated = True

        if implicated:
            spectrum[name]["e_f"] += 1
        else:
            spectrum[name]["n_f"] += 1
            spectrum[name]["n_p"] += 1

    # 5. Compute Mathematically Grounded Suspiciousness with Causal Distance Modulator
    ranked = []
    details = {}
    for name in action_names:
        counts = spectrum[name]
        raw_ochiai = compute_ochiai_score(
            e_f=counts["e_f"],
            e_p=counts["e_p"],
            n_f=counts["n_f"],
            n_p=counts["n_p"]
        )

        # Modulate by causal distance to goal (closer to goal = higher priority on unsolvable search)
        d = action_dist.get(name, 999)
        causal_weight = 1.0 / (1.0 + 0.25 * (d - 1)) if d < 999 else 0.40

        # Structural defect adjustments
        has_contradiction = any(c["action_name"] == name for c in internal_contradictions)
        in_cycle = any(name in cycle for cycle in causal_cycles)
        in_irreversible = any(name in it.get("deleted_by", []) and it.get("severity") == "CRITICAL" for it in irreversible_transitions)

        if has_contradiction:
            final_score = 1.00
        elif raw_ochiai > 0.0:
            final_score = round(min(1.0, raw_ochiai * causal_weight), 2)
        else:
            final_score = 0.0

        details[name] = {
            "score": final_score,
            "raw_ochiai": raw_ochiai,
            "causal_distance": d if d < 999 else "unreachable",
            "is_goal_relevant": name not in non_goal_leaf_actions,
            "in_cycle": in_cycle,
            "in_irreversible_trap": in_irreversible,
            "counts": counts
        }
        ranked.append((name, final_score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    if ranked and ranked[0][1] > 0.0:
        top_action = ranked[0][0]
        top_score = ranked[0][1]
    else:
        top_action = "General / Syntax" if ("syntax" in filtered_error_str or "parse" in filtered_error_str) else "General / Unsolvable State Space"
        top_score = 0.0

    # 6. Generate Formatted Diagnostic Summary for LLM and UI
    summary_lines = ["--- Causal Graph Structural Analysis ---"]
    if internal_contradictions:
        summary_lines.append("[CRITICAL MUTEX CONTRADICTIONS]:")
        for ic in internal_contradictions:
            summary_lines.append(f"  * {ic['description']}")
    if causal_cycles:
        summary_lines.append("[CAUSAL PRECONDITION DEADLOCK CYCLES]:")
        for cyc in causal_cycles:
            summary_lines.append(f"  * Mutual dependency cycle detected: {' -> '.join(cyc)}")
    if irreversible_transitions:
        summary_lines.append("[DTG IRREVERSIBLE / ABSORBING TRANSITIONS]:")
        for it in irreversible_transitions:
            if it["severity"] == "CRITICAL":
                summary_lines.append(f"  * Predicate '{it['predicate']}' is deleted by {it['deleted_by']} but has NO producer action in domain!")
    if non_goal_leaf_actions:
        summary_lines.append(f"[NON-GOAL LEAF ACTIONS]: Actions disconnected from goal reachability: {', '.join(sorted(list(non_goal_leaf_actions)))}")

    summary_lines.append(f"[TOP FAULT CANDIDATE]: Action '{top_action}' (Suspiciousness: {top_score:.2f})")
    diagnostic_summary = "\n".join(summary_lines)

    return {
        "ranked_actions": ranked,
        "top_action": top_action,
        "top_score": top_score,
        "goal_distances": {k: (v if v < 999 else -1) for k, v in action_dist.items()},
        "non_goal_leaf_actions": sorted(list(non_goal_leaf_actions)),
        "causal_cycles": causal_cycles,
        "irreversible_transitions": irreversible_transitions,
        "internal_contradictions": internal_contradictions,
        "diagnostic_summary": diagnostic_summary,
        "details": details
    }

# Backward compatibility alias
def run_sbfl_fault_localization(
    domain_bp: Any,
    problem_bp: Any,
    raw_errors: List[str],
    historical_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    return run_causal_graph_sbfl_analysis(domain_bp, problem_bp, raw_errors, historical_results)
