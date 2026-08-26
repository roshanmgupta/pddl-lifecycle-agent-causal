import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmark.dataset import BENCHMARK_TASKS

def parse_pddl_domain_to_blueprint(pddl_str: str) -> dict:
    if not pddl_str or not pddl_str.strip():
        return {}
        
    domain_name = re.search(r"\(\s*domain\s+([a-zA-Z0-9_\-]+)", pddl_str, re.IGNORECASE)
    dname = domain_name.group(1) if domain_name else "unnamed_domain"
    
    types_match = re.search(r"\(:types\s+(.*?)\)", pddl_str, re.DOTALL | re.IGNORECASE)
    types_dict = {}
    if types_match:
        for line in types_match.group(1).split("\n"):
            line_clean = line.strip()
            if not line_clean or line_clean.startswith(";"):
                continue
            if "-" in line_clean:
                parts = line_clean.split("-")
                objs = parts[0].strip().split()
                parent = parts[1].strip()
                for o in objs:
                    types_dict[o] = parent
            else:
                objs = line_clean.split()
                for o in objs:
                    types_dict[o] = "object"

                    
    pred_match = re.search(r"\(:predicates\s+(.*?)\)\s*\(:", pddl_str, re.DOTALL | re.IGNORECASE)
    preds = []
    if pred_match:
        preds = ["(" + p.strip() + ")" for p in re.findall(r"\((.*?)\)", pred_match.group(1)) if p.strip()]

    actions = []
    for act_match in re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", pddl_str, re.DOTALL | re.IGNORECASE):
        act_name = act_match.group(1)
        act_body = act_match.group(2)
        
        # parameters
        params_match = re.search(r":parameters\s*\((.*?)\)", act_body, re.DOTALL | re.IGNORECASE)
        param_dict = {}
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
                
        # preconditions
        pre_match = re.search(r":precondition\s+(.*?)(?=:effect)", act_body, re.DOTALL | re.IGNORECASE)
        pre_list = []
        if pre_match:
            pre_str = pre_match.group(1).strip()
            pre_list = ["(" + p.strip() + ")" for p in re.findall(r"\(([^\(\)]+)\)", pre_str) if p.strip() and p.strip() != "and"]
            
        # effects
        eff_match = re.search(r":effect\s+(.*?)(?=\)\s*$)", act_body, re.DOTALL | re.IGNORECASE)
        eff_list = []
        if eff_match:
            eff_str = eff_match.group(1).strip()
            eff_list = ["(" + p.strip() + ")" for p in re.findall(r"\((?:not\s*\([^\(\)]+\)|[^\(\)]+)\)", eff_str) if p.strip() and p.strip() != "and"]
            
        actions.append({
            "action_name": act_name,
            "parameters": param_dict,
            "preconditions": pre_list,
            "effects": eff_list
        })
        
    return {
        "domain_name": dname,
        "requirements": [":strips", ":typing"],
        "types": types_dict,
        "predicates": preds,
        "actions": actions
    }

print("=== TESTING UNIVERSAL PDDL BLUEPRINT PARSER ON ALL TASKS ===")
for task in BENCHMARK_TASKS:
    pddl_code = task.initial_domain_pddl or task.ground_truth_domain_pddl
    bp = parse_pddl_domain_to_blueprint(pddl_code)
    print(f"\nTask: {task.task_id} ({task.domain_family})")
    print(f"  Parsed Domain Name: {bp.get('domain_name')}")
    print(f"  Actions ({len(bp.get('actions', []))}): {[a['action_name'] for a in bp.get('actions', [])]}")
