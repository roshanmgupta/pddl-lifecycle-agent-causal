r"""
tools/causal_triage_analyzer.py
Action-Predicate Causal Dependency Graph & Diagnostic Reachability Triage Engine.
Grounded strictly in classical automated planning literature:
- Action-Predicate Causal Dependency Graph G_dep = (V, E) where V = A union P:
  * Producer relations: (a -> p) where p in eff+(a)
  * Consumer relations: (p -> a) where p in prec(a)
  * Deleter relations: (a -/-> p) where p in eff-(a)
- Invariant 1: Orphaned Goal Detection G_orphan = G \ (bigcup eff+(a) union I) & Shortest Goal Distance.
- Invariant 2: Causal Precondition Deadlock Cycle Detection on Action Enablement Graph (Torralba & Hoffmann).
- Invariant 3: Domain Transition Graph (DTG) Invertibility & Irreversible Absorbing States.
- Invariant 4: Mutex Contradictions & Add/Delete Clashes in AST Schemas.
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
        "goal_atoms": goal_atoms,
        "init_atoms": init_atoms,
        "action_names": [getattr(a, "action_name", "") if hasattr(a, "action_name") else a.get("action_name", "") for a in actions]
    }

def analyze_goal_relevance(
    cg_maps: Dict[str, Any]
) -> Tuple[Dict[str, int], Set[str], List[str]]:
    r"""
    Parameter 1: Goal Relevance, Orphaned Goals & Non-Goal Leaf Action Pruning.
    Performs backward search from goal predicates along the causal graph to compute:
    - distance: shortest causal distance from action's effects to the goal (1 = direct goal producer, etc.)
    - non_goal_leaf_actions: actions that produce no predicates needed for any goal or intermediate enabler.
    - orphaned_goals: goal predicates with NO producer action in domain and not in problem :init:
      Formally: G_orphan = G \ (bigcup_{a in A} eff+(a) union I)
    """
    producers = cg_maps["producers"]
    action_preconds = cg_maps["action_preconds"]
    action_adds = cg_maps["action_adds"]
    goal_preds = cg_maps["goal_preds"]
    init_preds = cg_maps.get("init_preds", set())
    action_names = cg_maps["action_names"]

    init_facts_set = set()
    for i in cg_maps.get("init_atoms", []):
        c = str(i).strip('() ')
        toks = c.split()
        if toks:
            init_facts_set.add((toks[0], tuple(toks[1:])))

    orphaned_goals_set = set()
    for g in cg_maps.get("goal_atoms", []):
        c = str(g).strip('() ')
        toks = c.split()
        if toks:
            g_pred = toks[0]
            g_args = tuple(toks[1:])
            # If no action produces g_pred, and this exact goal fact is not in :init:
            if not producers.get(g_pred) and (g_pred, g_args) not in init_facts_set:
                orphaned_goals_set.add(g_pred)

    orphaned_goals = sorted(list(orphaned_goals_set))

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

    return action_distance, non_goal_leaf_actions, orphaned_goals

def detect_causal_deadlocks_and_cycles(
    cg_maps: Dict[str, Any]
) -> List[List[str]]:
    """
    Parameter 2: Causal Cycle & Precondition Deadlock Detection.
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
                    cycle_nodes = set(cycle[:-1])
                    # A cycle is only a deadlock if NO action in the cycle can be enabled from outside the cycle
                    has_external_entry = False
                    for c_act in cycle_nodes:
                        precs = action_preconds.get(c_act, set())
                        uninit_precs = {p for p in precs if p not in init_preds}
                        if uninit_precs and all(any(p in action_adds[ext] for ext in action_names if ext not in cycle_nodes) for p in uninit_precs):
                            has_external_entry = True
                            break
                        elif not uninit_precs:
                            has_external_entry = True
                            break
                    if not has_external_entry:
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
    Parameter 3: Domain Transition Graph (DTG) Invertibility & Irreversible Absorbing States.
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
            all_dependent_actions = consumers.get(pred, set())
            other_dependent_actions = all_dependent_actions - del_actions
            # A predicate deletion is an irreversible transition if it deletes a goal predicate,
            # or if actions in the domain depend on it as a precondition
            if is_goal or all_dependent_actions:
                irreversible_issues.append({
                    "predicate": pred,
                    "deleted_by": sorted(list(del_actions)),
                    "is_goal_predicate": is_goal,
                    "required_by_actions": sorted(list(all_dependent_actions)),
                    "other_dependent_actions": sorted(list(other_dependent_actions)),
                    "severity": "CRITICAL" if (is_goal or other_dependent_actions) else "WARNING"
                })

    return irreversible_issues

def detect_unreleased_resource_sinks(domain_bp: Any) -> List[Dict[str, Any]]:
    """
    Classical Planning Invariant: Reversible Resource / Occupancy Balance.
    Identifies actions that delete an occupancy/holding relation H(arg1, ...) without asserting
    the corresponding operational resource/readiness predicate R(arg1) that was consumed when H was established.
    Example: If action A1 consumes R(x) to assert H(x, y), any action A2 that deletes H(x, y) must
    replenish R(x) to prevent permanent resource absorption.
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    
    claimed = {}
    for act in actions:
        act_name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        
        del_atoms = []
        add_atoms = []
        for eff in effs:
            pname, is_pos = parse_atom_predicate_and_polarity(eff)
            clean = eff.strip('() ')
            if clean.lower().startswith("not"):
                clean = clean[3:].strip('() ')
            toks = clean.split()
            if len(toks) > 1:
                args = [t.lstrip("?") for t in toks[1:]]
                if not is_pos:
                    del_atoms.append((toks[0].lower(), args))
                else:
                    add_atoms.append((toks[0].lower(), args))
                    
        for del_p, del_args in del_atoms:
            # Operational resource readiness predicates are unary (e.g. available, clear, empty, handempty, free)
            if len(del_args) == 1:
                for add_p, add_args in add_atoms:
                    if del_p != add_p and del_args[0] in add_args:
                        claimed.setdefault(add_p, []).append({
                            "claiming_action": act_name,
                            "resource_predicate": del_p,
                            "add_arg_idx": add_args.index(del_args[0]),
                        })
                    
    unreleased = []
    for act in actions:
        act_name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        
        eff_adds = set()
        add_atoms = []
        eff_dels = []
        for eff in effs:
            pname, is_pos = parse_atom_predicate_and_polarity(eff)
            clean = eff.strip('() ')
            if clean.lower().startswith("not"):
                clean = clean[3:].strip('() ')
            toks = clean.split()
            if len(toks) > 1:
                if is_pos:
                    eff_adds.add(toks[0].lower())
                    add_atoms.append((toks[0].lower(), [t.lstrip("?") for t in toks[1:]]))
                else:
                    eff_dels.append((toks[0].lower(), [t.lstrip("?") for t in toks[1:]]))
                    
        for del_p, del_args in eff_dels:
            if del_p in claimed:
                for claim_info in claimed[del_p]:
                    claim_act = claim_info["claiming_action"]
                    res_pred = claim_info["resource_predicate"]
                    add_idx = claim_info.get("add_arg_idx", 0)
                    if claim_act != act_name and res_pred not in eff_adds:
                        res_arg = del_args[add_idx] if len(del_args) > add_idx else (del_args[0] if del_args else "x")
                        # Check if res_arg is transferred to another holding/state relation in positive effects (custody handover)
                        arg_transferred = any(res_arg in a_args for a_pred, a_args in add_atoms)
                        if not arg_transferred:
                            unreleased.append({
                                "action_name": act_name,
                                "intermediate_predicate": del_p,
                                "claiming_action": claim_act,
                                "resource_predicate": res_pred,
                                "resource_arg": res_arg,
                                "description": f"Action '{act_name}' deletes '{del_p}' (which claims operational resource '{res_pred}' in action '{claim_act}'), but fails to restore '({res_pred} ?{res_arg})' in its positive effects."
                            })
                        
    return unreleased

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
    Parameter 4: Mutex Contradiction & Effect-Effect Co-occurrences.
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

def detect_ungroundable_preconditions(
    domain_bp: Any,
    problem_bp: Any
) -> List[Dict[str, Any]]:
    """
    Parameter 5: Dead / Ungroundable Precondition Invariant.
    Derived from Classical Automated Planning Theory (Helmert 2006; Haslum et al. 2019):
    Identifies action preconditions that can never be instantiated in any reachable state:
    1. Static predicate with ZERO facts in problem :init.
    2. Static predicate whose argument types have ZERO compatible facts in problem :init.
    3. Reflexive precondition (P ?x ?x) requiring identical arguments when neither :init
       nor any action produces identical arguments.
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    raw_constants = getattr(domain_bp, "constants", {}) if hasattr(domain_bp, "constants") else domain_bp.get("constants", {})
    init_atoms = getattr(problem_bp, "initial_state", []) if hasattr(problem_bp, "initial_state") else problem_bp.get("initial_state", [])
    objects = getattr(problem_bp, "objects", {}) if hasattr(problem_bp, "objects") else problem_bp.get("objects", {})

    produced_preds = set()
    produced_reflexive = set()
    for act in actions:
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        for eff in effs:
            clean = str(eff).strip('() ')
            if not clean.lower().startswith("not"):
                tokens = clean.split()
                if tokens:
                    pname = tokens[0]
                    produced_preds.add(pname)
                    if len(tokens) == 3 and tokens[1] == tokens[2]:
                        produced_reflexive.add(pname)

    init_facts = {}
    init_types_by_pred = {}
    for a in init_atoms:
        clean = str(a).strip('() ')
        tokens = clean.split()
        if not tokens:
            continue
        pname = tokens[0]
        args = tuple(tokens[1:])
        init_facts.setdefault(pname, []).append(args)
        arg_types = tuple(objects.get(obj, raw_constants.get(obj, "object")) for obj in args)
        init_types_by_pred.setdefault(pname, set()).add(arg_types)

    dom_types_map = domain_bp.get("types", {}) if isinstance(domain_bp, dict) else getattr(domain_bp, "types", {})
    if not isinstance(dom_types_map, dict):
        dom_types_map = {}

    def _is_subtype(c, p):
        if not c or not p or p.lower() == "object" or c.lower() == p.lower():
            return True
        curr = c
        seen_t = set()
        while curr and curr in dom_types_map and curr not in seen_t:
            seen_t.add(curr)
            parent_t = dom_types_map[curr]
            if parent_t and parent_t.lower() == p.lower():
                return True
            curr = parent_t
        return False

    all_known_objs = {**raw_constants, **objects}

    ungroundable = []
    for act in actions:
        act_name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
        params = getattr(act, "parameters", {}) if hasattr(act, "parameters") else act.get("parameters", {})
        norm_params = {k if k.startswith("?") else "?" + k: v for k, v in params.items()}
        precs = getattr(act, "preconditions", []) if hasattr(act, "preconditions") else act.get("preconditions", [])

        # Classical Planning Invariant: Parameter Domain Non-Emptiness.
        # Every parameter ?p - T in an action schema requires at least one object in problem :objects
        # or domain :constants whose type inherits from or equals T. If 0 matching objects exist,
        # the action has 0 groundings and can NEVER execute.
        if objects:
            for p_name, p_type in norm_params.items():
                if not p_type:
                    continue
                matching_objs = [
                    obj for obj, obj_t in all_known_objs.items()
                    if _is_subtype(obj_t, p_type)
                ]
                if not matching_objs:
                    ungroundable.append({
                        "action_name": act_name,
                        "predicate": p_type,
                        "expression": f"{p_name} - {p_type}",
                        "reason": (
                            f"Action '{act_name}' parameter '{p_name}' requires type '{p_type}', but problem :objects and domain :constants contain ZERO objects of type '{p_type}' (or its subtypes)! "
                            f"This action can NEVER be grounded (0 groundings), making any plan relying on it unreachable. "
                            f"To resolve: In problem ':objects', declare the relevant objects as type '{p_type}' according to the requirements (e.g. declare them as '{p_type}' instead of a broad supertype), "
                            f"or if '{act_name}' should operate on the broader supertype, generalize parameter '{p_name}' in domain 'actions'."
                        )
                    })

        for prec in precs:
            clean = str(prec).strip('() ')
            if clean.lower().startswith("not"):
                continue
            tokens = clean.split()
            if not tokens:
                continue
            pname = tokens[0]
            args = tokens[1:]

            # Check Reflexive precondition (P ?x ?x)
            if len(args) == 2 and args[0] == args[1]:
                has_init_reflexive = any(f[0] == f[1] for f in init_facts.get(pname, []) if len(f) == 2)
                if not has_init_reflexive and pname not in produced_reflexive:
                    ungroundable.append({
                        "action_name": act_name,
                        "predicate": pname,
                        "expression": clean,
                        "reason": f"Precondition '({clean})' requires identical arguments '{args[0]}', but no fact in :init and no action effect satisfies '({pname} X X)'."
                    })
                    continue

            # Check Static Predicates (not produced by any action)
            if pname not in produced_preds:
                if pname not in init_facts:
                    ungroundable.append({
                        "action_name": act_name,
                        "predicate": pname,
                        "expression": clean,
                        "reason": f"Static precondition '({clean})' has ZERO facts in problem :init (predicate '{pname}' is never added by any action and is completely missing from :init)."
                    })
                    continue

                req_types = [norm_params.get(a if a.startswith("?") else "?" + a, "object") for a in args]

                has_type_match = False
                for fact_types in init_types_by_pred.get(pname, set()):
                    if len(fact_types) == len(req_types):
                        match = True
                        for ft, rt in zip(fact_types, req_types):
                            if rt != "object" and ft != "object" and rt != ft:
                                if not _is_subtype(ft, rt):
                                    match = False
                                    break
                        if match:
                            has_type_match = True
                            break
                if not has_type_match:
                    avail_str = ", ".join([str(list(ft)) for ft in init_types_by_pred.get(pname, set())])
                    ungroundable.append({
                        "action_name": act_name,
                        "predicate": pname,
                        "expression": clean,
                        "reason": f"Static precondition '({clean})' requires argument types {req_types}, but :init contains ZERO matching facts! Available type signatures in :init for '{pname}' are: {avail_str}."
                    })

        # Check Pairwise Mutex Preconditions on shared parameters
        pos_precs = []
        for prec in act.get("preconditions", []):
            c = str(prec).strip('() ')
            if not c.lower().startswith("not"):
                toks = c.split()
                if toks:
                    pos_precs.append((toks[0], toks[1:], c))

        for i in range(len(pos_precs)):
            p1_name, p1_args, p1_str = pos_precs[i]
            for j in range(i + 1, len(pos_precs)):
                p2_name, p2_args, p2_str = pos_precs[j]
                shared_vars = set(p1_args).intersection(set(p2_args))
                for v in shared_vars:
                    k1 = p1_args.index(v)
                    k2 = p2_args.index(v)
                    cand1 = {f[k1] for f in init_facts.get(p1_name, []) if len(f) > k1}
                    cand2 = {f[k2] for f in init_facts.get(p2_name, []) if len(f) > k2}
                    # In Classical PDDL, objects in :init are closed and invariant throughout execution
                    # ONLY for purely static predicates (predicates never produced by any action).
                    # If either predicate is dynamic (produced by an action), its reachable arguments
                    # change during execution and are not bounded by :init facts alone!
                    if (p1_name not in produced_preds and p2_name not in produced_preds) and cand1 and cand2 and cand1.isdisjoint(cand2):
                        ungroundable.append({
                            "action_name": act_name,
                            "predicate": f"{p1_name}+{p2_name}",
                            "expression": f"({p1_str}) and ({p2_str})",
                            "reason": (
                                f"Variable conflation on parameter '{v}': Static preconditions '({p1_str})' and '({p2_str})' "
                                f"share parameter '{v}', but their valid groundings in problem :init are completely disjoint "
                                f"({sorted(list(cand1))} vs {sorted(list(cand2))}). Since both predicates are static (never produced by any action), "
                                f"no plan can ever satisfy both preconditions simultaneously. "
                                f"In action '{act_name}', verify parameter bindings against the requirements to ensure parameter '{v}' "
                                f"is not conflating two distinct physical entities or roles."
                            )
                        })

        # Check Causal Producer-Delete Clashes:
        # If action requires both P1 and P2, and the sole/primary producer of P1 explicitly deletes P2,
        # and no action restores P2 while preserving P1, the action is fundamentally blocked!
        precs_clean = [str(p).strip('() ') for p in act.get("preconditions", []) if not str(p).strip('() ').lower().startswith("not")]
        for p in precs_clean:
            p_toks = p.split()
            if not p_toks:
                continue
            pname, pargs = p_toks[0], p_toks[1:]
            for prod in actions:
                p_act_name = prod.get("action_name")
                if p_act_name == act_name:
                    continue
                prod_adds = [str(e).strip('() ').split() for e in prod.get("effects", []) if not str(e).strip('() ').lower().startswith("not")]
                prod_dels = [str(e).strip('() ')[3:].strip('() ').split() for e in prod.get("effects", []) if str(e).strip('() ').lower().startswith("not")]
                for add in prod_adds:
                    if add and add[0] == pname:
                        add_args = add[1:]
                        var_map = {add_args[k]: pargs[k] for k in range(min(len(add_args), len(pargs)))}
                        for del_atom in prod_dels:
                            if not del_atom:
                                continue
                            del_pred = del_atom[0]
                            del_args = del_atom[1:]
                            # In classical STRIPS / First-Order Logic semantics, a deleted literal in a producer action
                            # can only cause a causal clash with a consumer's precondition if all its parameters are
                            # bound by the establishing relation (var_map). Unbound producer variables are locally scoped.
                            if any(a not in var_map for a in del_args):
                                continue
                            del_args_mapped = [var_map[a] for a in del_args]
                            for other_p in precs_clean:
                                other_toks = other_p.split()
                                if other_toks[0] == del_pred and other_toks[1:] == del_args_mapped:
                                    ungroundable.append({
                                        "action_name": act_name,
                                        "predicate": f"{del_pred}<-del_by({p_act_name})",
                                        "expression": f"({other_p}) vs ({p})",
                                        "reason": (
                                            f"Causal clash in preconditions: Precondition '({other_p})' is explicitly DELETED by producer '{p_act_name}' when establishing '({p})'. "
                                            f"Review the requirements: either producer '{p_act_name}' inverted an effect (e.g. deleting a freed surface/receptacle or resource instead of asserting it as clear/available), "
                                            f"or action '{act_name}' was checking the wrong object in '({other_p})'."
                                        )
                                    })

    return ungroundable


def detect_statically_unproducible_goals(
    domain_bp: Any,
    problem_bp: Any
) -> List[Dict[str, Any]]:
    """
    Classical Planning Invariant: Static Goal Reachability (Helmert 2006; Haslum et al. 2019).
    Derived strictly from First-Order Logic semantics:
    A ground goal atom g = (p o_1 ... o_k) is statically unproducible if:
    1. g is not present in problem :init.
    2. Every action schema 'act' adding predicate 'p' requires static preconditions
       that constrain its parameters to a set of objects strictly disjoint from (o_1, ..., o_k).
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    dom_types_map = getattr(domain_bp, "types", {}) if hasattr(domain_bp, "types") else domain_bp.get("types", {})
    if not isinstance(dom_types_map, dict):
        dom_types_map = {}
    constants = getattr(domain_bp, "constants", {}) if hasattr(domain_bp, "constants") else domain_bp.get("constants", {})
    if not isinstance(constants, dict):
        constants = {}
    objects = getattr(problem_bp, "objects", {}) if hasattr(problem_bp, "objects") else problem_bp.get("objects", {})
    if not isinstance(objects, dict):
        objects = {}

    all_objs = {}
    all_objs.update(constants)
    all_objs.update(objects)

    init_atoms = getattr(problem_bp, "initial_state", []) if hasattr(problem_bp, "initial_state") else problem_bp.get("initial_state", [])
    if not init_atoms and (hasattr(problem_bp, "init") or (isinstance(problem_bp, dict) and "init" in problem_bp)):
        init_atoms = getattr(problem_bp, "init", []) if hasattr(problem_bp, "init") else problem_bp.get("init", [])

    goal_atoms = getattr(problem_bp, "goal_state", []) if hasattr(problem_bp, "goal_state") else problem_bp.get("goal_state", [])
    if not goal_atoms and (hasattr(problem_bp, "goal") or (isinstance(problem_bp, dict) and "goal" in problem_bp)):
        goal_atoms = getattr(problem_bp, "goal", []) if hasattr(problem_bp, "goal") else problem_bp.get("goal", [])

    init_facts: Dict[str, List[List[str]]] = {}
    for a in init_atoms:
        c = str(a).strip('() ')
        toks = c.split()
        if toks:
            init_facts.setdefault(toks[0], []).append(toks[1:])

    goals: List[Tuple[str, List[str], str]] = []
    for g in goal_atoms:
        c = str(g).strip('() ')
        toks = c.split()
        if toks:
            goals.append((toks[0], toks[1:], c))

    def _is_subtype(sub: str, super_t: str) -> bool:
        if not sub or not super_t or super_t == "object" or sub == super_t:
            return True
        curr = sub
        seen = set()
        while curr and curr in dom_types_map and curr not in seen:
            seen.add(curr)
            parent = dom_types_map[curr]
            if parent == super_t:
                return True
            curr = parent
        return False

    # Map what each action adds and deletes
    action_adds: Dict[str, List[Tuple[str, List[str], Any]]] = {}
    action_dels: Dict[str, List[Tuple[str, List[str], Any]]] = {}
    for act in actions:
        act_name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        for eff in effs:
            ec = str(eff).strip('() ')
            if not ec.lower().startswith("not"):
                etoks = ec.split()
                if etoks:
                    action_adds.setdefault(etoks[0], []).append((act_name, etoks[1:], act))
            else:
                inner = ec[3:].strip('() ')
                etoks = inner.split()
                if etoks:
                    action_dels.setdefault(etoks[0], []).append((act_name, etoks[1:], act))

    unproducible: List[Dict[str, Any]] = []

    for pred, args, g_str in goals:
        if pred in init_facts and args in init_facts[pred]:
            continue

        prods = action_adds.get(pred, [])
        if not prods:
            continue

        producible_by_any = False
        blocked_diagnostics: List[Dict[str, Any]] = []

        for act_name, eff_args, act in prods:
            raw_params = getattr(act, "parameters", {}) if hasattr(act, "parameters") else act.get("parameters", {})
            params = {}
            if isinstance(raw_params, dict):
                params = {k if k.startswith("?") else "?" + k: v for k, v in raw_params.items()}

            var_map = {eff_args[i]: args[i] for i in range(min(len(eff_args), len(args)))}
            act_can_produce = True

            precs = getattr(act, "preconditions", []) if hasattr(act, "preconditions") else act.get("preconditions", [])
            for v, target_obj in var_map.items():
                target_type = all_objs.get(target_obj)
                norm_v = v if v.startswith("?") else "?" + v
                param_type = params.get(norm_v, "object")
                if target_type and param_type != "object" and not _is_subtype(target_type, param_type):
                    act_can_produce = False
                    blocked_diagnostics.append({
                        "action_name": act_name,
                        "predicate": pred,
                        "target_object": target_obj,
                        "reason": f"Action '{act_name}' parameter '{v}' requires type '{param_type}', but goal object '{target_obj}' has declared type '{target_type}'."
                    })
                    break

                for prec in precs:
                    pc = str(prec).strip('() ')
                    if not pc.lower().startswith("not"):
                        ptoks = pc.split()
                        if not ptoks:
                            continue
                        pname, pargs = ptoks[0], ptoks[1:]
                        if v in pargs:
                            v_idx = pargs.index(v)
                            p_producers = action_adds.get(pname, [])
                            p_deleters = action_dels.get(pname, [])
                            other_indices = [j for j in range(len(pargs)) if j != v_idx]

                            # Predicates with ZERO producers have their extensions upper-bounded strictly by :init
                            if len(p_producers) == 0:
                                cand_facts = init_facts.get(pname, [])
                                valid_cands = set()
                                for f in cand_facts:
                                    if len(f) > v_idx:
                                        match = True
                                        for j in other_indices:
                                            if len(f) > j:
                                                other_obj = f[j]
                                                other_var = pargs[j]
                                                norm_other = other_var if other_var.startswith("?") else "?" + other_var
                                                other_type = params.get(norm_other, "object")
                                                obj_t = all_objs.get(other_obj, "object")
                                                if not _is_subtype(obj_t, other_type):
                                                    match = False
                                                    break
                                        if match:
                                            valid_cands.add(f[v_idx])

                                if valid_cands and target_obj not in valid_cands:
                                    act_can_produce = False
                                    other_desc = ', '.join([f"{pargs[j]} - {params.get(pargs[j] if pargs[j].startswith('?') else '?' + pargs[j], 'object')}" for j in other_indices])
                                    if len(p_deleters) == 0:
                                        # Purely static topology relation
                                        reason_text = (
                                            f"Goal atom '({g_str})' cannot be produced: In action '{act_name}', effect parameter '{v}' in '({pred} {' '.join(eff_args)})' "
                                            f"is bound to static precondition '({pc})' where {other_desc}. "
                                            f"Facts in :init for '({pc})' restrict '{v}' strictly to {sorted(list(valid_cands))}, which does not include required goal object '{target_obj}'! "
                                            f"This proves parameter '{v}' was conflated with a static entity. Disentangle parameter '{v}' by declaring a dedicated parameter "
                                            f"for the target entity in '{act_name}' and referencing it in the effect."
                                        )
                                    else:
                                        # Consumable initial property/sample missing from :init
                                        reason_text = (
                                            f"Goal atom '({g_str})' cannot be produced: Action '{act_name}' requires precondition '({pc})', "
                                            f"but predicate '{pname}' has NO producing action in the domain and problem ':init' only contains facts for {sorted(list(valid_cands))}, "
                                            f"omitting required goal entity '{target_obj}'! "
                                            f"Check the Natural Language Requirements: If the requirements specify that '{target_obj}' has this initial property/sample, "
                                            f"augment problem 'initial_state' with '({pname} {target_obj})'."
                                        )
                                    blocked_diagnostics.append({
                                        "action_name": act_name,
                                        "predicate": pred,
                                        "target_object": target_obj,
                                        "expression": f"({pred} {' '.join(eff_args)})",
                                        "reason": reason_text
                                    })
                                    break

            if act_can_produce:
                producible_by_any = True
                break

        if not producible_by_any and blocked_diagnostics:
            for bd in blocked_diagnostics:
                unproducible.append(bd)

    return unproducible


def detect_directional_asymmetry_traps(
    domain_bp: Any,
    problem_bp: Any
) -> List[Dict[str, Any]]:
    """
    Classical Planning Invariant: Directional Asymmetry & Inverse Action Schema Completeness.
    Derived from Classical STRIPS (:strips :typing) semantics:
    In Classical STRIPS, disjunctions ('or') in action preconditions are forbidden.
    When an action transitions a dynamic state variable (e.g. '(at ?e ?from)' -> '(at ?e ?to)')
    constrained by a static topological relation R(?from, ?to):
    If R is asymmetric in problem :init (i.e. R(u, v) in :init does not imply R(v, u) in :init),
    and no action exists in the domain allowing transition under R(?to, ?from) (the reverse direction):
    Then if problem :goal requires an entity currently at L_start to reach L_dest where
    R(L_dest, L_start) holds (the reverse direction), the goal is provably unreachable!
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    init_atoms = getattr(problem_bp, "initial_state", []) if hasattr(problem_bp, "initial_state") else problem_bp.get("initial_state", [])
    if not init_atoms and (hasattr(problem_bp, "init") or (isinstance(problem_bp, dict) and "init" in problem_bp)):
        init_atoms = getattr(problem_bp, "init", []) if hasattr(problem_bp, "init") else problem_bp.get("init", [])

    goal_atoms = getattr(problem_bp, "goal_state", []) if hasattr(problem_bp, "goal_state") else problem_bp.get("goal_state", [])
    if not goal_atoms and (hasattr(problem_bp, "goal") or (isinstance(problem_bp, dict) and "goal" in problem_bp)):
        goal_atoms = getattr(problem_bp, "goal", []) if hasattr(problem_bp, "goal") else problem_bp.get("goal", [])

    produced_preds = set()
    for act in actions:
        effs = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
        for eff in effs:
            canon, is_pos = normalize_atom_expression(eff)
            if canon:
                toks = canon.strip('() ').split()
                if toks:
                    produced_preds.add(toks[0])

    init_facts = {}
    for a in init_atoms:
        canon, is_pos = normalize_atom_expression(a)
        if canon and is_pos:
            toks = canon.strip('() ').split()
            if toks:
                init_facts.setdefault(toks[0], []).append(toks[1:])

    asymmetric_static = {}
    for pred, facts in init_facts.items():
        if pred not in produced_preds and all(len(f) == 2 for f in facts) and facts:
            f_set = {tuple(f) for f in facts}
            if any((b, a) not in f_set for (a, b) in f_set):
                asymmetric_static[pred] = f_set

    traps = []
    for r_name, r_facts in asymmetric_static.items():
        forward_acts = []
        reverse_acts = []

        for act in actions:
            act_name = getattr(act, "action_name", "") if hasattr(act, "action_name") else act.get("action_name", "")
            precs = [normalize_atom_expression(p)[0] for p in (getattr(act, "preconditions", []) if hasattr(act, "preconditions") else act.get("preconditions", []))]
            effs_raw = getattr(act, "effects", []) if hasattr(act, "effects") else act.get("effects", [])
            eff_adds = [normalize_atom_expression(e)[0] for e in effs_raw if normalize_atom_expression(e)[1]]
            eff_dels = [normalize_atom_expression(e)[0] for e in effs_raw if not normalize_atom_expression(e)[1]]

            for prec in precs:
                ptoks = prec.strip('() ').split()
                if len(ptoks) == 3 and ptoks[0] == r_name:
                    r_arg1, r_arg2 = ptoks[1], ptoks[2]
                    for d in eff_dels:
                        dtoks = d.strip('() ').split()
                        if r_arg1 in dtoks:
                            idx = dtoks.index(r_arg1)
                            for a in eff_adds:
                                atoks = a.strip('() ').split()
                                if atoks and atoks[0] == dtoks[0] and len(atoks) == len(dtoks) and atoks[idx] == r_arg2:
                                    forward_acts.append((act_name, dtoks[0], r_arg1, r_arg2))
                        elif r_arg2 in dtoks:
                            idx = dtoks.index(r_arg2)
                            for a in eff_adds:
                                atoks = a.strip('() ').split()
                                if atoks and atoks[0] == dtoks[0] and len(atoks) == len(dtoks) and atoks[idx] == r_arg1:
                                    reverse_acts.append((act_name, dtoks[0], r_arg2, r_arg1))

        if forward_acts and not reverse_acts:
            for g in goal_atoms:
                g_canon, _ = normalize_atom_expression(g)
                gtoks = g_canon.strip('() ').split()
                if gtoks and len(gtoks) >= 2:
                    g_pred = gtoks[0]
                    g_obj = gtoks[1]
                    g_dest = gtoks[-1]
                    for f in init_facts.get(g_pred, []):
                        if len(f) >= 2 and f[0] == g_obj:
                            g_start = f[-1]
                            if (g_dest, g_start) in r_facts and (g_start, g_dest) not in r_facts:
                                traps.append({
                                    "relation": r_name,
                                    "forward_actions": [fa[0] for fa in forward_acts],
                                    "target_entity": g_obj,
                                    "start_loc": g_start,
                                    "dest_loc": g_dest,
                                    "state_pred": g_pred,
                                    "reason": (
                                        f"Directional Asymmetry / Missing Inverse Transition Action: Action(s) {[fa[0] for fa in forward_acts]} "
                                        f"transition '{g_pred}' under static relation '({r_name} ?from ?to)'. In problem :init, '{r_name}' is directed/asymmetric, "
                                        f"and the domain contains NO action allowing transition in the inverse direction ('({r_name} ?to ?from)'). "
                                        f"However, goal requires entity '{g_obj}' to transition from '{g_start}' to '{g_dest}' where '({r_name} {g_dest} {g_start})' holds! "
                                        f"In Classical STRIPS (:strips :typing), disjunctions ('or') in preconditions are unsupported, so bidirectional transitions "
                                        f"require separate, uniquely-named action schemas for each valid direction described in the requirements. "
                                        f"Add the missing action schema (e.g. '{forward_acts[0][0]}_up' or '{forward_acts[0][0]}_2') with precondition '({r_name} ?to ?from)'."
                                    )
                                })
    return traps


def detect_unusable_problem_objects(
    domain_bp: Any,
    problem_bp: Any
) -> List[Dict[str, Any]]:
    """
    Classical Typed Planning Invariant: Object Type Action Inaccessibility.
    Identifies objects or object types declared in problem :objects (or referenced in :init / :goal)
    that cannot be accepted by ANY action parameter in the domain due to overly narrow typing
    or missing supertype declarations in domain :types.
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    dom_types_map = getattr(domain_bp, "types", {}) if hasattr(domain_bp, "types") else domain_bp.get("types", {})
    if not isinstance(dom_types_map, dict):
        dom_types_map = {}
    objects = getattr(problem_bp, "objects", {}) if hasattr(problem_bp, "objects") else problem_bp.get("objects", {})
    if not isinstance(objects, dict):
        objects = {}

    if not objects or not actions:
        return []

    def get_ancestors(t: str) -> Set[str]:
        anc = set()
        curr = t
        seen = set()
        while curr and curr in dom_types_map and curr not in seen:
            seen.add(curr)
            parent = dom_types_map[curr]
            if parent:
                anc.add(parent.lower())
                curr = parent
            else:
                break
        anc.add("object")
        return anc

    all_param_types = set()
    for act in actions:
        params = getattr(act, "parameters", {}) if hasattr(act, "parameters") else act.get("parameters", {})
        if isinstance(params, dict):
            for p, pt in params.items():
                if pt:
                    all_param_types.add(pt.lower())

    unusable = []
    unusable_types_reported = set()
    for obj, obj_t in objects.items():
        if not obj_t:
            continue
        obj_t_lower = obj_t.lower()
        if obj_t_lower in unusable_types_reported:
            continue
        ancestors = get_ancestors(obj_t_lower)
        can_use = ("object" in all_param_types or 
                   obj_t_lower in all_param_types or 
                   any(pt in ancestors for pt in all_param_types))

        if not can_use:
            unusable_types_reported.add(obj_t_lower)
            unusable.append({
                "object": obj,
                "type": obj_t,
                "reason": (
                    f"Overly narrow action typing or missing supertype hierarchy: Object '{obj}' has type '{obj_t}', "
                    f"but ZERO actions in the domain accept type '{obj_t}' or any of its ancestors! "
                    f"All action parameters in the domain are restricted to {sorted(list(all_param_types))}. "
                    f"Check domain 'types' and action parameter signatures: declare the common supertype specified in the requirements "
                    f"(which both '{obj_t}' and related types inherit from), and generalize action parameters to accept this common supertype."
                )
            })

    return unusable


def detect_problem_atom_well_formedness(
    domain_bp: Any,
    problem_bp: Any
) -> List[Dict[str, Any]]:
    """
    Classical Relational Planning AST Invariant: Atomic Formula Well-Formedness.
    Verifies that every atomic formula in problem :init and :goal begins with
    a valid declared predicate symbol, and flags instances where an object/constant
    was erroneously placed in the predicate position or an undeclared predicate was used.
    """
    dom_preds = set()
    raw_preds = getattr(domain_bp, "predicates", []) if hasattr(domain_bp, "predicates") else domain_bp.get("predicates", [])
    for p in raw_preds:
        c = str(p).strip('() ')
        toks = c.split()
        if toks:
            dom_preds.add(toks[0].lower())

    dom_constants = getattr(domain_bp, "constants", {}) if hasattr(domain_bp, "constants") else domain_bp.get("constants", {})
    if not isinstance(dom_constants, dict):
        dom_constants = {}
    prob_objects = getattr(problem_bp, "objects", {}) if hasattr(problem_bp, "objects") else problem_bp.get("objects", {})
    if not isinstance(prob_objects, dict):
        prob_objects = {}

    all_objs = {**dom_constants, **prob_objects}

    init_atoms = getattr(problem_bp, "initial_state", []) if hasattr(problem_bp, "initial_state") else problem_bp.get("initial_state", [])
    goal_atoms = getattr(problem_bp, "goal_state", []) if hasattr(problem_bp, "goal_state") else problem_bp.get("goal_state", [])

    malformed = []
    seen_symbols = set()

    for scope, atoms in [("initial_state", init_atoms), ("goal_state", goal_atoms)]:
        for atom in atoms:
            c = str(atom).strip('() ')
            if c.lower().startswith("not"):
                c = c[3:].strip('() ')
            toks = c.split()
            if not toks:
                continue
            head = toks[0]
            head_lower = head.lower()
            if head_lower in dom_preds or head_lower in {"=", "distinct"}:
                continue

            if head_lower in seen_symbols:
                continue
            seen_symbols.add(head_lower)

            if head in all_objs or head_lower in {k.lower() for k in all_objs}:
                obj_t = all_objs.get(head) or all_objs.get(head_lower, "object")
                malformed.append({
                    "symbol": head,
                    "kind": "OBJECT_IN_PREDICATE_POSITION",
                    "atom": str(atom),
                    "scope": scope,
                    "reason": (
                        f"Object in predicate position: Atom '({c})' in problem {scope} begins with '{head}', "
                        f"which is declared as an OBJECT of type '{obj_t}', not a predicate! "
                        f"In Classical PDDL 2.1 prefix notation, every fact must begin with a declared predicate symbol. "
                        f"Declare the intended relational predicate in domain 'predicates' (e.g. '(rel-name ?x - type1 ?y - type2)') "
                        f"and rewrite the fact in problem {scope} as '(rel-name {head} ...)'."
                    )
                })
            else:
                malformed.append({
                    "symbol": head,
                    "kind": "UNDECLARED_PREDICATE",
                    "atom": str(atom),
                    "scope": scope,
                    "reason": (
                        f"Undeclared predicate in problem {scope}: Atom '({c})' uses predicate symbol '{head}', "
                        f"which is NOT declared in domain 'predicates'. "
                        f"Declare '({head} ...)' in domain 'predicates' with its typed parameter signature, "
                        f"or update the atom in problem {scope} to use the correct declared predicate name."
                    )
                })

    return malformed


def run_causal_triage_analysis(
    domain_bp: Any,
    problem_bp: Any,
    raw_errors: List[str],
    historical_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Unified Action-Predicate Causal Dependency Graph & Triage Diagnostic Engine.
    Executes all classical planning causal invariants, detects orphaned goals,
    and isolates structural fault candidates across all action schemas.
    """
    actions = getattr(domain_bp, "actions", []) if hasattr(domain_bp, "actions") else domain_bp.get("actions", [])
    if not actions:
        return {
            "candidate_actions": [],
            "top_action": "General / Syntax",
            "top_reason": "Empty domain actions.",
            "goal_distances": {},
            "orphaned_goals": [],
            "non_goal_leaf_actions": [],
            "causal_cycles": [],
            "irreversible_transitions": [],
            "internal_contradictions": [],
            "ungroundable_preconditions": [],
            "diagnostic_summary": "Empty domain actions."
        }

    # 1. Build Bipartite Causal Graph Maps
    cg_maps = build_causal_graph_maps(domain_bp, problem_bp)
    action_names = cg_maps["action_names"]

    # 2. Compute Classical Invariants & Goal Reachability
    action_dist, non_goal_leaf_actions, orphaned_goals = analyze_goal_relevance(cg_maps)
    causal_cycles = detect_causal_deadlocks_and_cycles(cg_maps)
    irreversible_transitions = detect_dtg_irreversibility(cg_maps)
    internal_contradictions = detect_internal_contradictions(domain_bp)
    ungroundable_preconditions = detect_ungroundable_preconditions(domain_bp, problem_bp)
    unproducible_goals = detect_statically_unproducible_goals(domain_bp, problem_bp)
    unreleased_resources = detect_unreleased_resource_sinks(domain_bp)
    unusable_objects = detect_unusable_problem_objects(domain_bp, problem_bp)
    malformed_atoms = detect_problem_atom_well_formedness(domain_bp, problem_bp)
    directional_traps = detect_directional_asymmetry_traps(domain_bp, problem_bp)

    # 3. Filter Error Traces from Symbolic Oracles
    filtered_error_lines = []
    for err in raw_errors:
        for line in err.splitlines():
            line_lower = line.lower()
            if "passes type checking" in line_lower or "action passes" in line_lower:
                continue
            filtered_error_lines.append(line_lower)
    filtered_error_str = " ".join(filtered_error_lines)

    # 4. Topological Fault Candidate Isolation
    # Prioritizes candidate actions strictly based on mathematical invariant proofs:
    # Priority -1: Unusable problem objects (objects in problem :objects that cannot be accepted by any action)
    # Priority 0: Dead ungroundable static preconditions / Statically unproducible goal atoms / Directional asymmetry traps
    # Priority 1: Mutex contradictions (simultaneous add and delete effects) or unreleased resource leaks
    # Priority 2: Directly implicated by validator / compiler error trace
    # Priority 3: Precondition deadlock cycles (mutual dependency loops on the enablement graph)
    # Priority 4: Irreversible absorbing transitions (deleting predicates with zero restoring producers)
    # Priority 999: Innocent actions with no invariant violations (NEVER speculatively blamed)
    candidate_actions = []
    for name in action_names:
        dead_precs = [u for u in ungroundable_preconditions if u["action_name"] == name]
        unprod_goals = [u for u in unproducible_goals if u["action_name"] == name]
        has_directional_trap = any(name in dt.get("forward_actions", []) for dt in directional_traps)
        has_contradiction = any(c["action_name"] == name for c in internal_contradictions)
        has_leak = [u for u in unreleased_resources if u["action_name"] == name]

        # Check direct implication from oracle error trace
        is_in_oracle_log = False
        name_clean = name.lower().replace("_", "-")
        for line in filtered_error_lines:
            if name.lower() in line or name_clean in line:
                is_in_oracle_log = True
                break
        if not is_in_oracle_log:
            for p in cg_maps["action_preconds"].get(name, set()).union(cg_maps["action_adds"].get(name, set())):
                p_pattern = rf"\b{re.escape(p.lower())}\b"
                if re.search(p_pattern, filtered_error_str):
                    is_in_oracle_log = True
                    break

        in_cycle = any(name in cycle for cycle in causal_cycles)
        in_irreversible = any(name in it.get("deleted_by", []) and it.get("severity") == "CRITICAL" for it in irreversible_transitions)

        if dead_precs:
            priority = 0
            reason = f"Dead ungroundable precondition: {dead_precs[0]['reason']}"
        elif unprod_goals:
            priority = 0
            reason = f"Statically unproducible goal: {unprod_goals[0]['reason']}"
        elif has_directional_trap:
            priority = 0
            matching_dt = next(dt for dt in directional_traps if name in dt.get("forward_actions", []))
            reason = f"Directional asymmetry (missing inverse transition action): {matching_dt['reason']}"
        elif has_contradiction:
            priority = 1
            reason = "Mutex contradiction (simultaneous add and delete clash in action schema)"
        elif has_leak:
            priority = 1
            reason = f"Unreleased resource leak: {has_leak[0]['description']}"
        elif is_in_oracle_log:
            priority = 2
            reason = "Directly implicated by validator / compiler error trace"
        elif in_cycle:
            priority = 3
            reason = "Precondition deadlock cycle on action enablement graph"
        elif in_irreversible:
            priority = 4
            reason = "Irreversible absorbing state: deletes predicate with zero restoring producers"
        else:
            priority = 999
            reason = "No structural invariant violation detected"

        candidate_actions.append((name, priority, reason))

    candidate_actions.sort(key=lambda x: x[1])

    if malformed_atoms:
        top_action = "Problem Initial/Goal State & Predicates"
        top_reason = malformed_atoms[0]["reason"]
    elif unusable_objects:
        top_action = "Domain Types & Action Parameters"
        top_reason = unusable_objects[0]["reason"]
    elif candidate_actions and candidate_actions[0][1] <= 4:
        top_action = candidate_actions[0][0]
        top_reason = candidate_actions[0][2]
    elif directional_traps:
        top_action = directional_traps[0]["forward_actions"][0] if directional_traps[0].get("forward_actions") else "Domain Actions"
        top_reason = directional_traps[0]["reason"]
    elif orphaned_goals:
        top_action = "Domain Action Effects (Missing Goal Producer)"
        top_reason = f"Goal predicate(s) {orphaned_goals} have NO producing action in the domain and are not in problem :init! Review the requirements to add the missing positive effect to the establishing action."
    else:
        top_action = "General / Semantic Reachability"
        top_reason = "No structural invariant violations detected; root cause is semantic parameterization or state reachability."

    # 5. Generate Formatted Diagnostic Summary for LLM and UI
    summary_lines = ["--- Action-Predicate Causal Dependency Structural Analysis ---"]
    if malformed_atoms:
        summary_lines.append("[MALFORMED PROBLEM ATOMIC FORMULAS / UNDECLARED PREDICATES]:")
        for ma in malformed_atoms:
            summary_lines.append(f"  * {ma['reason']}")
    if unusable_objects:
        summary_lines.append("[UNUSABLE PROBLEM OBJECTS / OVERLY NARROW TYPING]:")
        for uo in unusable_objects:
            summary_lines.append(f"  * {uo['reason']}")
    if ungroundable_preconditions:
        summary_lines.append("[DEAD UNGROUNDABLE PRECONDITIONS (ACTION CAN NEVER EXECUTE)]:")
        for up in ungroundable_preconditions:
            summary_lines.append(f"  * Action '{up['action_name']}': {up['reason']}")
    if unproducible_goals:
        summary_lines.append("[STATICALLY UNPRODUCIBLE GOAL ATOMS (FIRST-ORDER LOGIC BOUNDING)]:")
        for ug in unproducible_goals:
            summary_lines.append(f"  * Action '{ug['action_name']}': {ug['reason']}")
    if directional_traps:
        summary_lines.append("[DIRECTIONAL ASYMMETRY / MISSING INVERSE TRANSITION ACTIONS]:")
        for dt in directional_traps:
            summary_lines.append(f"  * {dt['reason']}")
    if orphaned_goals:
        summary_lines.append("[ORPHANED UNPRODUCED GOALS]:")
        for og in orphaned_goals:
            summary_lines.append(f"  * Goal predicate '{og}' has NO producing action in the domain and is not in problem :init!")
    if internal_contradictions:
        summary_lines.append("[CRITICAL MUTEX CONTRADICTIONS]:")
        for ic in internal_contradictions:
            summary_lines.append(f"  * {ic['description']}")
    if unreleased_resources:
        summary_lines.append("[CRITICAL UNRELEASED RESOURCE SINK / LEAK]:")
        for ur in unreleased_resources:
            summary_lines.append(f"  * {ur['description']}")
    if causal_cycles:
        summary_lines.append("[CAUSAL PRECONDITION DEADLOCK CYCLES]:")
        for cyc in causal_cycles:
            summary_lines.append(f"  * Mutual dependency cycle detected: {' -> '.join(cyc)}")
    if irreversible_transitions:
        summary_lines.append("[DTG IRREVERSIBLE / ABSORBING TRANSITIONS]:")
        for it in irreversible_transitions:
            if it["severity"] == "CRITICAL":
                if it.get("is_goal_predicate"):
                    summary_lines.append(
                        f"  * Predicate '{it['predicate']}' is a GOAL predicate deleted by {it['deleted_by']}, but has NO action in the domain producing it! "
                        f"Review the Natural Language Requirements: The domain is missing a positive effect '({it['predicate']} ...)' on the action that establishes this relationship "
                        f"(such as dropping, placing, stacking, or delivering). Add '({it['predicate']} ...)' to that action's positive effects! "
                        f"NEVER remove the delete effect from {it['deleted_by']}."
                    )
                else:
                    summary_lines.append(f"  * Predicate '{it['predicate']}' is deleted by {it['deleted_by']} without any producing action, permanently disabling actions {it.get('required_by_actions', [])}! If '{it['predicate']}' is an operational resource or agent availability state that remains true after the action, REMOVE the delete effect '(not ({it['predicate']} ...))' from {it['deleted_by']} rather than simultaneously adding and deleting it in the same action.")
    if non_goal_leaf_actions:
        summary_lines.append(f"[NON-GOAL LEAF ACTIONS]: Actions disconnected from goal reachability: {', '.join(sorted(list(non_goal_leaf_actions)))}")

    summary_lines.append(f"[TOP FAULT CANDIDATE]: Action '{top_action}' ({top_reason})")
    diagnostic_summary = "\n".join(summary_lines)

    return {
        "candidate_actions": candidate_actions,
        "top_action": top_action,
        "top_reason": top_reason,
        "goal_distances": {k: (v if v < 999 else -1) for k, v in action_dist.items()},
        "orphaned_goals": orphaned_goals,
        "non_goal_leaf_actions": sorted(list(non_goal_leaf_actions)),
        "causal_cycles": causal_cycles,
        "irreversible_transitions": irreversible_transitions,
        "internal_contradictions": internal_contradictions,
        "ungroundable_preconditions": ungroundable_preconditions,
        "unproducible_goals": unproducible_goals,
        "unreleased_resources": unreleased_resources,
        "unusable_objects": unusable_objects,
        "directional_traps": directional_traps,
        "diagnostic_summary": diagnostic_summary
    }
