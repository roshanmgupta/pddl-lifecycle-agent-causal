import os
import shutil
import json
import re
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(r"e:\Rosh\Thesis\pddl_lifecycle_agent")
AUTOPLANBENCH_DATA = PROJECT_ROOT / "autoplanbench" / "data"
BENCHMARK_OUTPUT = PROJECT_ROOT / "PDDLLifeCycleBench"

# All 24 canonical domains strictly adhering to PDDL 2.1 STRIPS and typing
CANONICAL_24_DOMAINS = [
    "barman14-bfs",
    "blocksworld",
    "childsnack14",
    "depot",
    "driverlog02-bfs",
    "elevators08",
    "ferry",
    "floortile",
    "goldminer",
    "grid",
    "gripper",
    "hiking14",
    "logistics",
    "movie98",
    "mprime98",
    "mystery98",
    "parking11",
    "pegsol08",
    "pipesworld-notankage04-bfs",
    "rovers",
    "satellite",
    "scanalyzer08",
    "visitall",
    "zenotravel02"
]

def extract_balanced_expr(text, start_idx):
    """Finds the balanced parenthesis s-expression starting at or after start_idx."""
    depth = 0
    start = text.find('(', start_idx)
    if start == -1:
        return None, -1, -1
    for i in range(start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1], start, i+1
    return None, -1, -1

def extract_all_actions(domain_text):
    """Extracts all actions and their component boundaries from domain PDDL text."""
    actions = []
    idx = 0
    while True:
        pos = domain_text.lower().find('(:action', idx)
        if pos == -1:
            break
        act_expr, s, e = extract_balanced_expr(domain_text, pos)
        if not act_expr:
            break
        
        m_name = re.search(r'\(:action\s+([a-zA-Z0-9_\-]+)', act_expr, re.IGNORECASE)
        act_name = m_name.group(1) if m_name else 'unknown'
        
        # Parameters
        p_pos = act_expr.lower().find(':parameters')
        params_str, p_s, p_e = extract_balanced_expr(act_expr, p_pos) if p_pos != -1 else ('()', -1, -1)
        
        # Preconditions
        prec_pos = act_expr.lower().find(':precondition')
        prec_str, prec_s, prec_e = extract_balanced_expr(act_expr, prec_pos) if prec_pos != -1 else ('()', -1, -1)
        
        # Effects
        eff_pos = act_expr.lower().find(':effect')
        eff_str, eff_s, eff_e = extract_balanced_expr(act_expr, eff_pos) if eff_pos != -1 else ('()', -1, -1)
        
        actions.append({
            'name': act_name,
            'full_text': act_expr,
            'start': s,
            'end': e,
            'params': params_str,
            'precondition': prec_str,
            'effect': eff_str
        })
        idx = e
        
    return actions

def parse_objects(pddl_text):
    """Extracts objects and their types from problem PDDL."""
    obj_match = re.search(r'\(:objects\s+(.*?)\)\s*\(:init', pddl_text, re.DOTALL | re.IGNORECASE)
    if not obj_match:
        obj_match = re.search(r'\(:objects\s+(.*?)\)', pddl_text, re.DOTALL | re.IGNORECASE)
    if not obj_match:
        return {}
    
    raw = obj_match.group(1).strip()
    typed_objs = {}
    
    tokens = raw.split()
    current_objs = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == '-':
            if i + 1 < len(tokens):
                t_name = tokens[i+1]
                for o in current_objs:
                    typed_objs.setdefault(t_name, []).append(o)
                current_objs = []
                i += 2
                continue
        elif not token.startswith(';'):
            current_objs.append(token)
        i += 1
    
    if current_objs:
        for o in current_objs:
            typed_objs.setdefault("object", []).append(o)
            
    return typed_objs

def parse_atoms(block_text):
    """Extracts ground atoms from an init or goal block."""
    atoms = []
    for match in re.finditer(r'\(([a-zA-Z0-9_\-\?\=]+)(.*?)\)', block_text, re.DOTALL):
        pred = match.group(1).strip()
        if pred.lower() in ['and', 'not', 'or', 'forall', 'exists', 'imply']:
            continue
        args = match.group(2).split()
        atoms.append((pred, args))
    return atoms

def parse_problem_file(problem_path):
    """Parses problem.pddl into objects, init atoms, and goal atoms."""
    with open(problem_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    objs = parse_objects(content)
    
    # Init
    init_match = re.search(r'\(:init\s+(.*?)\)\s*\(:goal', content, re.DOTALL | re.IGNORECASE)
    init_text = init_match.group(1) if init_match else ""
    init_atoms = parse_atoms(init_text)
    
    # Goal
    goal_match = re.search(r'\(:goal\s+(.*?)\)\s*\)', content, re.DOTALL | re.IGNORECASE)
    goal_text = goal_match.group(1) if goal_match else ""
    goal_atoms = parse_atoms(goal_text)
    
    return objs, init_atoms, goal_atoms

def format_atom(pred, args, pred_mappings):
    """Formats an atom into natural language using AutoPlanBench mappings if available."""
    clean_args = [a.replace("?", "") for a in args]
    if pred in pred_mappings:
        template = pred_mappings[pred]
        try:
            return template.format(*clean_args)
        except Exception:
            pass
    if len(clean_args) == 0:
        return f"{pred} holds"
    elif len(clean_args) == 1:
        return f"{clean_args[0]} is {pred}"
    elif len(clean_args) == 2:
        return f"{clean_args[0]} is {pred} {clean_args[1]}"
    else:
        return f"{pred} between " + ", ".join(clean_args)

def generate_task_nl_description(domain_name, domain_encoding_text, prob_path, pred_mappings):
    """Generates the combined natural language description: Domain Rules + Instance Scenario."""
    objs, init_atoms, goal_atoms = parse_problem_file(prob_path)
    
    lines = []
    lines.append("================================================================================")
    lines.append(f"DOMAIN CAPABILITIES & ACTION RULES: {domain_name.upper()}")
    lines.append("================================================================================")
    lines.append(domain_encoding_text.strip())
    lines.append("")
    
    lines.append("================================================================================")
    lines.append(f"OPERATIONAL TASK SCENARIO & GOAL SPECIFICATION: {domain_name.upper()}")
    lines.append("================================================================================")
    lines.append("The following objects exist in this problem instance:")
    for t_name, obj_list in objs.items():
        if len(obj_list) == 1:
            lines.append(f"- {obj_list[0]} is of type {t_name}")
        else:
            lines.append(f"- {', '.join(obj_list[:-1])} and {obj_list[-1]} are of type {t_name}")
    lines.append("")
    
    lines.append("The initial state of the world is as follows:")
    if init_atoms:
        for p, args in init_atoms:
            desc = format_atom(p, args, pred_mappings)
            lines.append(f"- {desc}")
    else:
        lines.append("- (Empty initial state)")
    lines.append("")
    
    lines.append("My goal is to achieve the following state:")
    if goal_atoms:
        for p, args in goal_atoms:
            desc = format_atom(p, args, pred_mappings)
            lines.append(f"- {desc}")
    else:
        lines.append("- (No explicit goal specified)")
    lines.append("")
    lines.append("Please model and solve this classical PDDL 2.1 planning domain and task.")
    
    return "\n".join(lines)

def create_curated_flaws_for_domain(domain_name, clean_domain_text, clean_domain_dir, pred_mappings, encoding_text, prob_path):
    """
    Creates all 5 Category B curated flaw variants for the domain as defined in Section 2.3:
    (1) Type Signature / Arity Inversion
    (2) Precondition Misalignment
    (3) Action Effect Deletion
    (4) Initial / Goal Deadlocks
    (5) Backward-Compatibility Regressions
    """
    flaws_dir = clean_domain_dir / "flaws"
    flaws_dir.mkdir(parents=True, exist_ok=True)
    
    actions = extract_all_actions(clean_domain_text)
    if not actions:
        print(f"  Warning: No actions found in {domain_name}!")
        return
        
    act0 = actions[0]
    act_target_deadlock = actions[1] if len(actions) > 1 else actions[0]
    act_target_regression = actions[2] if len(actions) > 2 else actions[0]
    
    # -------------------------------------------------------------------------
    # 1. Type Signature / Arity Inversion Flaw
    # -------------------------------------------------------------------------
    flaw1_dir = flaws_dir / "flaw_01_type_signature_arity"
    flaw1_dir.mkdir(parents=True, exist_ok=True)
    
    act_name = act0['name']
    orig_params = act0['params']
    inner_params = orig_params[1:-1].strip()
    tokens = inner_params.split()
    if len(tokens) >= 3:
        mutated_inner = " ".join(tokens[:-2])  # truncate last typed argument
    else:
        mutated_inner = inner_params + " ?extra_unbound - object"
    mutated_params = f"({mutated_inner})"
    
    flawed_dom_1 = clean_domain_text.replace(orig_params, mutated_params, 1)
    (flaw1_dir / "domain_flawed.pddl").write_text(flawed_dom_1, encoding="utf-8")
    
    meta1 = {
        "flaw_category": "TYPE_SIGNATURE_ARITY_INVERSION",
        "target_action": act_name,
        "description": f"Mutated parameter signature in action '{act_name}' creating an arity mismatch or unbound parameter.",
        "ground_truth_fix": f"Restore original parameter signature: {orig_params}",
        "expected_oracle_signal": "Fast Downward parser aborts during translation with parameter arity error."
    }
    (flaw1_dir / "flaw_metadata.json").write_text(json.dumps(meta1, indent=2), encoding="utf-8")
    
    flawed_desc_1 = generate_task_nl_description(
        domain_name, 
        encoding_text + f"\n\n[NOTE: Flawed configuration where action '{act_name}' has broken parameter bindings.]",
        prob_path, 
        pred_mappings
    )
    (flaw1_dir / "complete_specification.txt").write_text(flawed_desc_1, encoding="utf-8")

    # -------------------------------------------------------------------------
    # 2. Precondition Misalignment Flaw
    # -------------------------------------------------------------------------
    flaw2_dir = flaws_dir / "flaw_02_precondition_misalignment"
    flaw2_dir.mkdir(parents=True, exist_ok=True)
    
    orig_prec = act0['precondition']
    if orig_prec.strip().startswith('(and'):
        mutated_prec = orig_prec.replace('(and', '(and (unreachable_precondition_clause)', 1)
    else:
        inner = orig_prec[1:-1].strip()
        mutated_prec = f"(and (unreachable_precondition_clause) {inner})"
        
    flawed_dom_2 = clean_domain_text.replace(orig_prec, mutated_prec, 1)
    if "(:predicates" in flawed_dom_2:
        flawed_dom_2 = flawed_dom_2.replace("(:predicates", "(:predicates\n    (unreachable_precondition_clause)", 1)
    (flaw2_dir / "domain_flawed.pddl").write_text(flawed_dom_2, encoding="utf-8")
    
    meta2 = {
        "flaw_category": "PRECONDITION_MISALIGNMENT",
        "target_action": act_name,
        "description": f"Injected unreachable precondition (unreachable_precondition_clause) in action '{act_name}'.",
        "ground_truth_fix": f"Remove (unreachable_precondition_clause) from action '{act_name}' preconditions.",
        "expected_oracle_signal": "Fast Downward SAS+ reachability search halts with goal unreachable from initial state."
    }
    (flaw2_dir / "flaw_metadata.json").write_text(json.dumps(meta2, indent=2), encoding="utf-8")
    
    flawed_desc_2 = generate_task_nl_description(
        domain_name, 
        encoding_text + f"\n\n[NOTE: Action '{act_name}' contains an invalid extraneous restriction.]",
        prob_path, 
        pred_mappings
    )
    (flaw2_dir / "complete_specification.txt").write_text(flawed_desc_2, encoding="utf-8")

    # -------------------------------------------------------------------------
    # 3. Action Effect Deletion Flaw (Replicating Gragera & Muise 2024)
    # -------------------------------------------------------------------------
    flaw3_dir = flaws_dir / "flaw_03_action_effect_deletion"
    flaw3_dir.mkdir(parents=True, exist_ok=True)
    
    # Find an action with multiple effect atoms
    target_act_eff = None
    target_atom = None
    for a in actions:
        eff_text = a['effect']
        atoms = re.findall(r'(\(not\s*\([^\)]+\)\)|\([a-zA-Z0-9_\-][^\(\)]*\))', eff_text, re.IGNORECASE)
        # Prefer positive add effects
        pos_atoms = [atom for atom in atoms if not atom.lower().startswith('(not')]
        if pos_atoms:
            target_act_eff = a
            target_atom = pos_atoms[0]
            break
        elif len(atoms) > 1:
            target_act_eff = a
            target_atom = atoms[0]
            break
            
    if not target_act_eff:
        target_act_eff = act0
        target_atom = act0['effect']
        
    flawed_eff = target_act_eff['effect'].replace(target_atom, "", 1)
    flawed_dom_3 = clean_domain_text.replace(target_act_eff['effect'], flawed_eff, 1)
    (flaw3_dir / "domain_flawed.pddl").write_text(flawed_dom_3, encoding="utf-8")
    
    meta3 = {
        "flaw_category": "ACTION_EFFECT_DELETION",
        "target_action": target_act_eff['name'],
        "deleted_effect": target_atom.strip(),
        "description": f"Deleted required causal add effect '{target_atom.strip()}' from action '{target_act_eff['name']}', breaking state transition reachability.",
        "ground_truth_fix": f"Re-insert effect '{target_atom.strip()}' into action '{target_act_eff['name']}'.",
        "expected_oracle_signal": "Fast Downward Causal Graph reveals missing variable transition; search fails or plan invalid in VAL."
    }
    (flaw3_dir / "flaw_metadata.json").write_text(json.dumps(meta3, indent=2), encoding="utf-8")
    
    flawed_desc_3 = generate_task_nl_description(
        domain_name, 
        encoding_text + f"\n\n[NOTE: Action '{target_act_eff['name']}' is missing one of its critical state transition effects.]",
        prob_path, 
        pred_mappings
    )
    (flaw3_dir / "complete_specification.txt").write_text(flawed_desc_3, encoding="utf-8")

    # -------------------------------------------------------------------------
    # 4. Initial / Goal Deadlocks Flaw
    # -------------------------------------------------------------------------
    flaw4_dir = flaws_dir / "flaw_04_initial_goal_deadlock"
    flaw4_dir.mkdir(parents=True, exist_ok=True)
    
    dl_act_name = act_target_deadlock['name']
    dl_orig_prec = act_target_deadlock['precondition']
    
    # Injects a mutually exclusive deadlock constraint
    if dl_orig_prec.strip().startswith('(and'):
        mutated_dl_prec = dl_orig_prec.replace('(and', '(and (state_deadlock_mutex_lock)', 1)
    else:
        inner = dl_orig_prec[1:-1].strip()
        mutated_dl_prec = f"(and (state_deadlock_mutex_lock) {inner})"
        
    flawed_dom_4 = clean_domain_text.replace(dl_orig_prec, mutated_dl_prec, 1)
    if "(:predicates" in flawed_dom_4:
        flawed_dom_4 = flawed_dom_4.replace("(:predicates", "(:predicates\n    (state_deadlock_mutex_lock)", 1)
        
    (flaw4_dir / "domain_flawed.pddl").write_text(flawed_dom_4, encoding="utf-8")
    
    # Also create companion problem_flawed.pddl containing contradictory deadlocked initial assertions
    orig_prob_text = prob_path.read_text(encoding="utf-8", errors="ignore")
    # In problem, inject conflicting initial state condition
    flawed_prob_text = orig_prob_text
    if "(:init" in flawed_prob_text:
        flawed_prob_text = flawed_prob_text.replace("(:init", "(:init\n    (state_deadlock_mutex_lock)", 1)
        # and in goal require a mutually exclusive deadlock condition
        if "(:goal" in flawed_prob_text:
            flawed_prob_text = flawed_prob_text.replace("(:goal", "(:goal (and (not (state_deadlock_mutex_lock))", 1)
            diff = flawed_prob_text.count('(') - flawed_prob_text.count(')')
            if diff > 0:
                flawed_prob_text = flawed_prob_text.rstrip() + (')' * diff) + "\n"
    (flaw4_dir / "problem_flawed.pddl").write_text(flawed_prob_text, encoding="utf-8")
    
    meta4 = {
        "flaw_category": "INITIAL_GOAL_DEADLOCK",
        "target_action": dl_act_name,
        "description": f"Mutually exclusive deadlock constraint injected into action '{dl_act_name}' rendering goal state unreachable from initial state.",
        "ground_truth_fix": f"Eliminate contradictory deadlock predicate '(state_deadlock_mutex_lock)' from action '{dl_act_name}' preconditions.",
        "expected_oracle_signal": "Fast Downward SAS+ translator or forward search halts; goal is provably unreachable from initial state."
    }
    (flaw4_dir / "flaw_metadata.json").write_text(json.dumps(meta4, indent=2), encoding="utf-8")
    
    flawed_desc_4 = generate_task_nl_description(
        domain_name, 
        encoding_text + f"\n\n[NOTE: Action '{dl_act_name}' contains a mutually exclusive state lock constraint rendering the initial state in a deadlock.]",
        prob_path, 
        pred_mappings
    )
    (flaw4_dir / "complete_specification.txt").write_text(flawed_desc_4, encoding="utf-8")

    # -------------------------------------------------------------------------
    # 5. Backward-Compatibility Regressions (State Reachability Regressions)
    # -------------------------------------------------------------------------
    flaw5_dir = flaws_dir / "flaw_05_state_reachability_regression"
    flaw5_dir.mkdir(parents=True, exist_ok=True)
    
    reg_act_name = act_target_regression['name']
    reg_orig_prec = act_target_regression['precondition']
    
    # Injects an over-constraining precondition satisfied only by specialized extensions but missing in all legacy problem instances
    if reg_orig_prec.strip().startswith('(and'):
        mutated_reg_prec = reg_orig_prec.replace('(and', '(and (specialized_mode_enabled)', 1)
    else:
        inner = reg_orig_prec[1:-1].strip()
        mutated_reg_prec = f"(and (specialized_mode_enabled) {inner})"
        
    flawed_dom_5 = clean_domain_text.replace(reg_orig_prec, mutated_reg_prec, 1)
    if "(:predicates" in flawed_dom_5:
        flawed_dom_5 = flawed_dom_5.replace("(:predicates", "(:predicates\n    (specialized_mode_enabled)", 1)
        
    (flaw5_dir / "domain_flawed.pddl").write_text(flawed_dom_5, encoding="utf-8")
    
    meta5 = {
        "flaw_category": "BACKWARD_COMPATIBILITY_REGRESSION",
        "target_action": reg_act_name,
        "injected_restriction": "(specialized_mode_enabled)",
        "description": f"Modified action '{reg_act_name}' to require an over-constrained precondition '(specialized_mode_enabled)' satisfying an ad-hoc feature but breaking all legacy regression instances.",
        "ground_truth_fix": f"Decouple specialized requirement from core legacy action '{reg_act_name}' to restore backward compatibility across historical problems.",
        "expected_oracle_signal": "Fast Downward planner fails on historical regression problems (instance-1 to instance-5); Phase 4 Regression Gatekeeper halts deployment."
    }
    (flaw5_dir / "flaw_metadata.json").write_text(json.dumps(meta5, indent=2), encoding="utf-8")
    
    flawed_desc_5 = generate_task_nl_description(
        domain_name, 
        encoding_text + f"\n\n[NOTE: Action '{reg_act_name}' has been modified with an over-constraining restriction that breaks legacy problem compatibility.]",
        prob_path, 
        pred_mappings
    )
    (flaw5_dir / "complete_specification.txt").write_text(flawed_desc_5, encoding="utf-8")

def create_category_c_evolutions_for_domain(domain_name, clean_domain_dir, encoding_text, dest_prob_dir):
    """
    Creates Category C Continuous Domain Evolution tasks (2 tasks per domain)
    as specified in Section 2.2:
    - Evolution 01: Capability / Equipment Extension
    - Evolution 02: Operational Prerequisite & Composite Action Pipeline
    """
    c_dir = clean_domain_dir / "evolution"
    c_dir.mkdir(parents=True, exist_ok=True)
    
    # Identify legacy problem instances (instances 1 through 3)
    all_instances = sorted(list(dest_prob_dir.glob("*.pddl")))
    legacy_instances = all_instances[:3] if len(all_instances) >= 3 else all_instances
    target_inst = all_instances[1] if len(all_instances) > 1 else all_instances[0]
    
    # -------------------------------------------------------------------------
    # Evolution 01: Incremental Capability Extension
    # -------------------------------------------------------------------------
    evo1_dir = c_dir / "evolution_01_feature_addition"
    evo1_dir.mkdir(parents=True, exist_ok=True)
    
    evo1_req = f"""================================================================================
CATEGORY C: CONTINUOUS DOMAIN EVOLUTION SPECIFICATION (TASK 1: CAPABILITY EXTENSION)
DOMAIN: {domain_name.upper()}
================================================================================
REQUIREMENT SUMMARY:
Extend the existing operational model of {domain_name} with an incremental feature request.
The domain must now support high-throughput express operations with specialized tooling prerequisites.

EVOLUTION RULES:
1. Synthesize an extended action schema or specialized capability flag supporting advanced operations.
2. CRITICAL PRESERVATION MANDATE: Backward compatibility across historical legacy problem instances
   (instance-1 to instance-3) must be 100% strictly preserved.
3. The Phase 4 Regression Gatekeeper will evaluate both the target problem and all historical test cases.
"""
    (evo1_dir / "feature_request_specification.txt").write_text(evo1_req, encoding="utf-8")
    
    # Save target problem and legacy regression problems
    shutil.copyfile(target_inst, evo1_dir / "target_problem.pddl")
    legacy_dir_1 = evo1_dir / "historical_regression_problems"
    legacy_dir_1.mkdir(parents=True, exist_ok=True)
    for inst in legacy_instances:
        shutil.copyfile(inst, legacy_dir_1 / inst.name)
        
    meta_evo1 = {
        "evolution_category": "INCREMENTAL_CAPABILITY_EXTENSION",
        "domain": domain_name,
        "historical_regression_instances": [inst.name for inst in legacy_instances],
        "target_problem": target_inst.name,
        "gatekeeper_requirement": "All historical problem instances must remain solvable without regression."
    }
    (evo1_dir / "evolution_metadata.json").write_text(json.dumps(meta_evo1, indent=2), encoding="utf-8")

    # -------------------------------------------------------------------------
    # Evolution 02: Composite Action Pipeline & Maintenance Constraint
    # -------------------------------------------------------------------------
    evo2_dir = c_dir / "evolution_02_composite_action"
    evo2_dir.mkdir(parents=True, exist_ok=True)
    
    target_inst_2 = all_instances[2] if len(all_instances) > 2 else all_instances[-1]
    evo2_req = f"""================================================================================
CATEGORY C: CONTINUOUS DOMAIN EVOLUTION SPECIFICATION (TASK 2: COMPOSITE ACTION PIPELINE)
DOMAIN: {domain_name.upper()}
================================================================================
REQUIREMENT SUMMARY:
Extend the existing operational model of {domain_name} to incorporate a multi-stage composite
action sequence and state maintenance invariant.

EVOLUTION RULES:
1. Formalize intermediate validation prerequisites before core state transitions can execute.
2. Ensure that existing action schemas retain default operational pathways for standard legacy problems.
3. The Phase 4 Regression Gatekeeper will halt deployment if legacy plan solvability degrades.
"""
    (evo2_dir / "feature_request_specification.txt").write_text(evo2_req, encoding="utf-8")
    
    shutil.copyfile(target_inst_2, evo2_dir / "target_problem.pddl")
    legacy_dir_2 = evo2_dir / "historical_regression_problems"
    legacy_dir_2.mkdir(parents=True, exist_ok=True)
    for inst in legacy_instances:
        shutil.copyfile(inst, legacy_dir_2 / inst.name)
        
    meta_evo2 = {
        "evolution_category": "COMPOSITE_ACTION_PIPELINE",
        "domain": domain_name,
        "historical_regression_instances": [inst.name for inst in legacy_instances],
        "target_problem": target_inst_2.name,
        "gatekeeper_requirement": "Zero regression on legacy problems; Phase 4 verification mandatory."
    }
    (evo2_dir / "evolution_metadata.json").write_text(json.dumps(meta_evo2, indent=2), encoding="utf-8")

def process_all_domains():
    print(f"Building PDDLLifeCycleBench at: {BENCHMARK_OUTPUT}")
    BENCHMARK_OUTPUT.mkdir(parents=True, exist_ok=True)
    
    summary = []
    
    for domain_name in CANONICAL_24_DOMAINS:
        src_dir = AUTOPLANBENCH_DATA / domain_name
        dest_dir = BENCHMARK_OUTPUT / domain_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nProcessing domain: {domain_name}...")
        
        # 1. Copy ground truth domain.pddl
        src_domain_file = src_dir / "domain.pddl"
        dest_domain_file = dest_dir / "domain.pddl"
        clean_domain_text = src_domain_file.read_text(encoding="utf-8", errors="ignore")
        dest_domain_file.write_text(clean_domain_text, encoding="utf-8")
        
        # 2. Copy orig_problems directory
        src_prob_dir = src_dir / "orig_problems"
        dest_prob_dir = dest_dir / "orig_problems"
        if dest_prob_dir.exists():
            shutil.rmtree(dest_prob_dir)
        shutil.copytree(src_prob_dir, dest_prob_dir)
        num_instances = len(list(dest_prob_dir.glob("*.pddl")))
        
        # 3. Read AutoPlanBench domain encoding
        src_encoding_file = src_dir / "domain_encoding.txt"
        encoding_text = src_encoding_file.read_text(encoding="utf-8", errors="ignore") if src_encoding_file.exists() else ""
        (dest_dir / "domain_encoding.txt").write_text(encoding_text, encoding="utf-8")
        
        # 4. Read predicate mappings from seed file if available
        src_seed_file = src_dir / "domain_description_seed1.json"
        pred_mappings = {}
        if src_seed_file.exists():
            try:
                with open(src_seed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pred_mappings = data.get("predicate_mappings", {})
            except Exception as e:
                print(f"  Warning: could not read seed file for {domain_name}: {e}")
                
        # 5. Generate unified complete_specification.txt (Category A Elicitation Task)
        first_prob = dest_prob_dir / "instance-1.pddl"
        if not first_prob.exists():
            probs = list(dest_prob_dir.glob("*.pddl"))
            first_prob = probs[0] if probs else None
            
        if first_prob:
            complete_nl = generate_task_nl_description(domain_name, encoding_text, first_prob, pred_mappings)
            (dest_dir / "complete_specification.txt").write_text(complete_nl, encoding="utf-8")
            
            # 6. Create Category B Curated Flaws (all 5 error classes from Section 2.3)
            create_curated_flaws_for_domain(
                domain_name, 
                clean_domain_text, 
                dest_dir, 
                pred_mappings, 
                encoding_text, 
                first_prob
            )
            
            # 7. Create Category C Continuous Domain Evolution tasks (2 tasks per domain)
            create_category_c_evolutions_for_domain(
                domain_name,
                dest_dir,
                encoding_text,
                dest_prob_dir
            )
            
        summary.append({
            "domain": domain_name,
            "instances": num_instances,
            "category_a_elicitation": 1,
            "flaws": 5,
            "evolution": 2
        })
        print(f"  -> Finished {domain_name}: {num_instances} problem instances, unified specification, 5 flaws, and 2 evolutions.")
        
    # Write benchmark manifest
    manifest_path = BENCHMARK_OUTPUT / "benchmark_manifest.json"
    manifest_path.write_text(json.dumps({
        "benchmark_name": "PDDLLifeCycleBench",
        "version": "2.0",
        "description": "Comprehensive benchmark suite across 24 canonical domains for classical PDDL 2.1 lifecycle evaluation.",
        "taxonomy": {
            "elicitation": "Initial Elicitation (24 tasks)",
            "flaws": "Synthetic Fault Repair across 5 error classes (120 tasks)",
            "evolution": "Continuous Domain Evolution with Phase 4 Regression Gatekeeper (48 tasks)"
        },
        "total_domains": len(summary),
        "total_tasks": len(summary) * 8, # 1 Elicitation + 5 Flaws + 2 Evolution = 8 tasks per domain = 192 tasks
        "domains": summary
    }, indent=2), encoding="utf-8")
    print(f"\nSuccessfully generated PDDLLifeCycleBench with all 24 domains at: {BENCHMARK_OUTPUT}")

if __name__ == "__main__":
    process_all_domains()
