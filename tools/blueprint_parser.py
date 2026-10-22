#!/usr/bin/env python3
"""
tools/blueprint_parser.py
Universal deterministic PDDL domain and problem string-to-AST blueprint parsers.
Provides centralized AST blueprint conversion across the lifecycle agent,
reducing code duplication in app.py, benchmark loaders, and evaluation scripts.
"""

import re
from typing import Dict, List, Set, Any, Optional

def extract_predicate_names(atom_list: List[str]) -> Set[str]:
    """Extracts base predicate names from a list of PDDL atom strings."""
    preds = set()
    for atom in atom_list:
        clean = atom.strip().replace("(", "").replace(")", "").replace("not", "").strip()
        tokens = clean.split()
        if tokens:
            preds.add(tokens[0].lower())
    return preds

def clean_blueprint_expression(raw_s: str) -> Optional[str]:
    """Cleans an individual PDDL precondition or effect expression into a valid blueprint atom."""
    s = raw_s.strip()
    if not s or s.lower() == "and":
        return None
    while s.startswith("((") and s.endswith("))"):
        s = s[1:-1].strip()
    if not s.startswith("("):
        s = f"({s}"
    if not s.endswith(")"):
        s = f"{s})"
    return s

def parse_pddl_domain_to_blueprint(pddl_str: str) -> Dict[str, Any]:
    """
    Parses a raw PDDL domain string into a structured Domain Blueprint dictionary.
    Extracts domain name, types hierarchy, predicates, and actions with parameters,
    preconditions, and effects.
    """
    if not pddl_str or not pddl_str.strip():
        return {}

    domain_name = re.search(r"\(\s*domain\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    dname = domain_name.group(1) if domain_name else "unnamed_domain"

    req_match = re.search(r"\(:requirements\s+(.*?)\)", pddl_str, re.IGNORECASE)
    reqs: List[str] = []
    if req_match:
        for r in req_match.group(1).split():
            clean_r = r.strip()
            if clean_r:
                if not clean_r.startswith(":"):
                    clean_r = f":{clean_r}"
                reqs.append(clean_r)

    types_match = re.search(r"\(:types\s+(.*?)\)", pddl_str, re.DOTALL | re.IGNORECASE)
    types_dict: Dict[str, str] = {}
    if types_match:
        tokens = types_match.group(1).split()
        current_types = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == "-":
                parent = tokens[i+1] if i+1 < len(tokens) else "object"
                for t in current_types:
                    types_dict[t] = parent
                current_types = []
                i += 2
            else:
                current_types.append(tok)
                i += 1
        for t in current_types:
            types_dict[t] = "object"

    if not reqs:
        if types_dict or re.search(r"\?\w+\s*-\s*[a-zA-Z0-9_\-]+", pddl_str):
            reqs = [":strips", ":typing"]
        else:
            reqs = [":strips"]

    pred_match = re.search(r"\(:predicates\s+(.*?)\)\s*\(:", pddl_str, re.DOTALL | re.IGNORECASE)
    preds: List[str] = []
    if pred_match:
        preds = ["(" + p.strip() + ")" for p in re.findall(r"\((.*?)\)", pred_match.group(1)) if p.strip()]

    const_match = re.search(r"\(:constants\s+(.*?)\)\s*\(:", pddl_str, re.DOTALL | re.IGNORECASE)
    consts_dict: Dict[str, str] = {}
    if const_match:
        for line in const_match.group(1).split("\n"):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith(";"):
                continue
            if "-" in line_clean:
                parts = line_clean.split("-")
                objs = parts[0].strip().split()
                parent = parts[1].strip()
                for o in objs:
                    consts_dict[o] = parent
            else:
                objs = line_clean.split()
                for o in objs:
                    consts_dict[o] = "object"

    actions: List[Dict[str, Any]] = []
    for act_match in re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", pddl_str, re.DOTALL | re.IGNORECASE):
        act_name = act_match.group(1)
        act_body = act_match.group(2)

        params_match = re.search(r":parameters\s*\((.*?)\)", act_body, re.DOTALL | re.IGNORECASE)
        param_dict: Dict[str, str] = {}
        if params_match:
            raw_p = params_match.group(1).strip()
            tokens = raw_p.split()
            i = 0
            while i < len(tokens):
                if tokens[i].startswith("?"):
                    pvar = tokens[i]
                    ptype = "object"
                    if i + 2 < len(tokens) and tokens[i+1] == "-":
                        ptype = tokens[i+2]
                        i += 2
                    param_dict[pvar] = ptype
                i += 1

        pre_match = re.search(r":precondition\s+(.*?)(?=:effect)", act_body, re.DOTALL | re.IGNORECASE)
        pre_list: List[str] = []
        if pre_match:
            pre_str = pre_match.group(1).strip()
            raw_pre = re.findall(r"\((?:not\s*\([^\(\)]+\)|[^\(\)]+)\)", pre_str)
            pre_list = [clean_blueprint_expression(p) for p in raw_pre if clean_blueprint_expression(p)]

        eff_match = re.search(r":effect\s+(.*?)(?=\)\s*$)", act_body, re.DOTALL | re.IGNORECASE)
        eff_list: List[str] = []
        if eff_match:
            eff_str = eff_match.group(1).strip()
            raw_eff = re.findall(r"\((?:not\s*\([^\(\)]+\)|[^\(\)]+)\)", eff_str)
            eff_list = [clean_blueprint_expression(p) for p in raw_eff if clean_blueprint_expression(p)]

        actions.append({
            "action_name": act_name,
            "parameters": param_dict,
            "preconditions": pre_list,
            "effects": eff_list
        })

    return {
        "domain_name": dname,
        "requirements": reqs,
        "types": types_dict,
        "constants": consts_dict,
        "predicates": preds,
        "actions": actions
    }

def parse_pddl_problem_to_blueprint(pddl_str: str) -> Dict[str, Any]:
    """
    Parses a raw PDDL problem string into a structured Problem Blueprint dictionary.
    Uses balanced S-expression depth parsing for :init and :goal clauses.
    """
    if not pddl_str or not pddl_str.strip():
        return {}

    prob_name = re.search(r"\(\s*problem\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    pname = prob_name.group(1) if prob_name else "unnamed_problem"

    dom_name = re.search(r"\(\s*:domain\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    dname = dom_name.group(1) if dom_name else "unnamed_domain"

    obj_match = re.search(r"\(:objects\s+(.*?)\)", pddl_str, re.DOTALL | re.IGNORECASE)
    objs_dict: Dict[str, str] = {}
    if obj_match:
        tokens = obj_match.group(1).split()
        pending = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.startswith(";"):
                i += 1
                continue
            if tok == "-":
                if i + 1 < len(tokens):
                    target_type = tokens[i + 1]
                    for p in pending:
                        objs_dict[p] = target_type
                    pending = []
                    i += 2
                    continue
            else:
                pending.append(tok)
            i += 1
        for p in pending:
            objs_dict[p] = "object"

    # S-expression extraction for :init
    inits: List[str] = []
    init_match = re.search(r"\(:init\b", pddl_str, re.IGNORECASE)
    if init_match:
        start = init_match.start()
        depth = 0
        init_body = ""
        for i in range(start, len(pddl_str)):
            if pddl_str[i] == "(":
                depth += 1
            elif pddl_str[i] == ")":
                depth -= 1
                if depth == 0:
                    init_body = pddl_str[start:i+1]
                    break
        if not init_body:
            end_idx = goal_match.start() if goal_match else len(pddl_str)
            init_body = pddl_str[start:end_idx]
        inner_init = init_body[6:-1].strip() if init_body.startswith("(:init") and init_body.endswith(")") else init_body[6:].strip()
        pdepth = 0
        c_start = -1
        for idx, c in enumerate(inner_init):
            if c == "(":
                if pdepth == 0:
                    c_start = idx
                pdepth += 1
            elif c == ")":
                pdepth -= 1
                if pdepth == 0 and c_start != -1:
                    clause = inner_init[c_start:idx+1].strip()
                    if clause:
                        inits.append(clause)
                    c_start = -1

    # S-expression extraction for :goal
    goals: List[str] = []
    goal_match = re.search(r"\(:goal\b", pddl_str, re.IGNORECASE)
    if goal_match:
        start = goal_match.start()
        depth = 0
        goal_body = ""
        for i in range(start, len(pddl_str)):
            if pddl_str[i] == "(":
                depth += 1
            elif pddl_str[i] == ")":
                depth -= 1
                if depth == 0:
                    goal_body = pddl_str[start:i+1]
                    break
        if not goal_body:
            goal_body = pddl_str[start:]
        raw_goals = re.findall(r"\((?:not\s*\([^\(\)]+\)|[^\(\)]+)\)", goal_body)
        for g in raw_goals:
            clean_g = g.strip()
            if clean_g.lower() != "and":
                goals.append(clean_g)

    return {
        "problem_name": pname,
        "domain_name": dname,
        "objects": objs_dict,
        "initial_state": inits,
        "goal_state": goals
    }
