import sys
import os
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmark.dataset import BENCHMARK_TASKS

def parse_pddl_domain_to_blueprint(pddl_str: str) -> dict:
    domain_name = re.search(r"\(\s*domain\s+([a-zA-Z0-9_\-]+)", pddl_str)
    dname = domain_name.group(1) if domain_name else "unnamed_domain"
    
    types_match = re.search(r"\(:types\s+(.*?)\)", pddl_str, re.DOTALL)
    types_dict = {}
    if types_match:
        for line in types_match.group(1).split("\n"):
            if "-" in line:
                parts = line.split("-")
                objs = parts[0].strip().split()
                parent = parts[1].strip()
                for o in objs:
                    types_dict[o] = parent
                    
    pred_match = re.search(r"\(:predicates\s+(.*?)\)\s*\(:", pddl_str, re.DOTALL)
    preds = []
    if pred_match:
        preds = ["(" + p.strip() + ")" for p in re.findall(r"\((.*?)\)", pred_match.group(1)) if p.strip()]

    actions = []
    for act_match in re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", pddl_str, re.DOTALL):
        act_name = act_match.group(1)
        act_body = act_match.group(2)
        
        # params
        params_match = re.search(r":parameters\s*\((.*?)\)", act_body)
        param_dict = {}
        if params_match:
            raw_p = params_match.group(1)
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
        pre_match = re.search(r":precondition\s+(.*?)(?=:effect)", act_body, re.DOTALL)
        pre_list = []
        if pre_match:
            pre_str = pre_match.group(1).strip()
            pre_list = ["(" + p.strip() + ")" for p in re.findall(r"\(([^\(\)]+)\)", pre_str)]
            
        # effects
        eff_match = re.search(r":effect\s+(.*?)(?=\)\s*$)", act_body, re.DOTALL)
        eff_list = []
        if eff_match:
            eff_str = eff_match.group(1).strip()
            eff_list = ["(" + p.strip() + ")" for p in re.findall(r"\((?:not\s*\([^\(\)]+\)|[^\(\)]+)\)", eff_str)]
            
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

task = BENCHMARK_TASKS[1] # blocksworld_repair_missing_precondition_01
bp = parse_pddl_domain_to_blueprint(task.initial_domain_pddl)
print("Parsed Blueprint Domain Name:", bp["domain_name"])
print("Actions count:", len(bp["actions"]))
for a in bp["actions"]:
    print("Action:", a["action_name"])
    print("  Preconditions:", a["preconditions"])
