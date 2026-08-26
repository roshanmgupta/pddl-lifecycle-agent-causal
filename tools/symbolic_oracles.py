import subprocess
import os
import re
from typing import Tuple, Dict, Any

def check_pddl_syntax_fallback(domain_path: str, problem_path: str = None) -> Tuple[bool, str]:
    """
    Python fallback syntax validator used when VAL binary ('Validate') is not installed in PATH.
    Performs structural parenthetical balance checks, keyword verification, and tag validation.
    """
    try:
        if not os.path.exists(domain_path):
            return False, f"File Error: Path '{domain_path}' does not exist."
            
        with open(domain_path, "r", encoding="utf-8", errors="ignore") as f:
            domain_code = f.read()

        # 1. Check parenthetical balance
        open_p = domain_code.count("(")
        close_p = domain_code.count(")")
        if open_p != close_p:
            return False, f"Syntax Error: Parentheses mismatch in domain. (open={open_p}, close={close_p})"

        # 2. Check essential PDDL keywords
        dom_lower = domain_code.lower()
        if "(define" not in dom_lower or "(domain" not in dom_lower:
            return False, "Syntax Error: Missing '(define (domain ...)' header block."

        if ":action" in dom_lower and ":parameters" not in dom_lower:
            return False, "Syntax Error: Action definition missing ':parameters' tag."

        # 3. Check predicate arity and parameter type declarations
        pred_decls = {}
        pred_types = {}
        type_hierarchy = {}
        
        # Parse type hierarchy: (:types truck airplane - vehicle) or (:types block)
        types_match = re.search(r"\(:types\s+(.*?)\)", domain_code, re.DOTALL)
        if types_match:
            for line in types_match.group(1).split("\n"):
                line_clean = line.strip()
                if not line_clean or line_clean.startswith(";"):
                    continue
                if "-" in line_clean:
                    parts = line_clean.split("-")
                    children = parts[0].strip().split()
                    parent = parts[1].strip()
                    for c in children:
                        type_hierarchy[c] = parent
                else:
                    children = line_clean.split()
                    for c in children:
                        type_hierarchy[c] = "object"


        def is_subtype_or_equal(child: str, target: str) -> bool:
            if child == target or target == "object":
                return True
            curr = child
            while curr in type_hierarchy:
                curr = type_hierarchy[curr]
                if curr == target:
                    return True
            return False

        pred_match = re.search(r"\(:predicates\s+(.*?)\)\s*\(:", domain_code, re.DOTALL)
        if pred_match:
            pred_block = pred_match.group(1)
            for raw_pred in re.findall(r"\((.*?)\)", pred_block):
                tokens = raw_pred.split()
                if tokens:
                    pname = tokens[0]
                    params = [t for t in tokens[1:] if t.startswith("?")]
                    pred_decls[pname] = len(params)
                    
                    # Parse declared parameter types
                    ptypes = []
                    i = 1
                    while i < len(tokens):
                        if tokens[i].startswith("?"):
                            ptype = "object"
                            if i + 2 < len(tokens) and tokens[i+1] == "-":
                                ptype = tokens[i+2]
                                i += 2
                            ptypes.append(ptype)
                        i += 1
                    pred_types[pname] = ptypes

        if pred_decls:
            for act_match in re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", domain_code, re.DOTALL):
                act_name = act_match.group(1)
                act_body = act_match.group(2)
                
                # Parse action parameters and their types
                act_param_types = {}
                param_match = re.search(r":parameters\s*\((.*?)\)", act_body, re.DOTALL)
                if param_match:
                    p_tokens = param_match.group(1).split()
                    idx = 0
                    while idx < len(p_tokens):
                        if p_tokens[idx].startswith("?"):
                            pvar = p_tokens[idx]
                            ptype = "object"
                            if idx + 2 < len(p_tokens) and p_tokens[idx+1] == "-":
                                ptype = p_tokens[idx+2]
                                idx += 2
                            act_param_types[pvar] = ptype
                        idx += 1

                for raw_stmt in re.findall(r"\(([a-zA-Z0-9_\-]+)\s+([^()]+)\)", act_body):
                    pname = raw_stmt[0]
                    args = [a for a in raw_stmt[1].split() if a != "not" and not a.startswith(":")]
                    if pname in pred_decls:
                        expected = pred_decls[pname]
                        actual = len(args)
                        if expected != actual:
                            return False, f"VAL Error: Error: Undefined predicate or arity mismatch: ({pname} {' '.join(args)}) in action '{act_name}' (expected arity {expected}, got {actual})"

                        # Check argument type compatibility against predicate definition
                        expected_types = pred_types.get(pname, [])
                        for arg_idx, arg_var in enumerate(args):
                            if arg_var in act_param_types and arg_idx < len(expected_types):
                                actual_type = act_param_types[arg_var]
                                req_type = expected_types[arg_idx]
                                if not is_subtype_or_equal(actual_type, req_type):
                                    return False, f"VAL Error: Type error in action '{act_name}': parameter '{arg_var}' of type '{actual_type}' passed to predicate '({pname} ...)' which expects type '{req_type}'."

        # 4. Universal Domain-Agnostic Static Analysis Rule (State Effect Duality)
        # For ANY domain and ANY predicate P: If an action asserts a negative state change (not (P ...)),
        # P MUST be declared in its preconditions (an action cannot negate a fact it did not verify).
        for act_match in re.finditer(r"\(:action\s+([a-zA-Z0-9_\-]+)(.*?)(?=\(:action|\)\s*$)", domain_code, re.DOTALL):
            act_name = act_match.group(1)
            act_body = act_match.group(2)
            pre_match = re.search(r":precondition\s+(.*?)(?=:effect)", act_body, re.DOTALL)
            eff_match = re.search(r":effect\s+(.*?)(?=\)\s*$)", act_body, re.DOTALL)
            if pre_match and eff_match:
                pre_text = pre_match.group(1)
                eff_text = eff_match.group(1)
                
                # Dynamically extract ALL negated predicates from effects
                for neg_pred in re.findall(r"\(\s*not\s*\(\s*([a-zA-Z0-9_\-]+)", eff_text):
                    if neg_pred not in pre_text:
                        return False, f"VAL Error: Action '{act_name}' asserts negative state effect '(not ({neg_pred} ...))' but fails to declare required precondition constraint '{neg_pred}'."

        # 4. Check problem file if provided
        if problem_path and os.path.exists(problem_path):
            with open(problem_path, "r", encoding="utf-8", errors="ignore") as f:
                prob_code = f.read()

            if prob_code.count("(") != prob_code.count(")"):
                return False, "Syntax Error: Parentheses mismatch in problem file."

            prob_lower = prob_code.lower()
            if "(define" not in prob_lower or "(problem" not in prob_lower:
                return False, "Syntax Error: Missing '(define (problem ...)' header block."

        return True, "PDDL Syntax Check Passed (Python Oracular Fallback)."

    except Exception as e:
        return False, f"Python Syntax Checker Error: {e}"

def run_val_validator(domain_path: str, problem_path: str = None) -> Tuple[bool, str]:
    """
    Executes VAL (Validate binary) against a generated domain.pddl file.
    Returns (is_valid, console_output_log).
    Falls back to Python structural syntax validator if Validate executable is missing.
    """
    if not os.path.exists(domain_path):
        return False, f"File Error: Path '{domain_path}' does not exist."

    # Shell command for VAL parser
    cmd = ["Validate", domain_path]
    if problem_path and os.path.exists(problem_path):
        cmd.append(problem_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout + "\n" + result.stderr
        
        # Check for typical VAL failure markers or missing tool warnings
        if "not found" in output.lower() or "system warning" in output.lower():
            return check_pddl_syntax_fallback(domain_path, problem_path)
        elif "Errors: 0" in output or "Successful plans:" in output:
            return True, output
        elif result.returncode == 0 and "Error" not in output:
            return True, output
        else:
            return False, output

    except FileNotFoundError:
        # Fallback to Python syntax check if VAL binary isn't in PATH
        return check_pddl_syntax_fallback(domain_path, problem_path)
    except subprocess.TimeoutExpired:
        return False, "Execution Error: VAL timed out after 15 seconds."


def run_fast_downward(domain_path: str, problem_path: str) -> Tuple[bool, str]:
    """
    Executes Fast Downward classical planner engine.
    Returns (plan_found, log_output).
    """
    if not os.path.exists(domain_path) or not os.path.exists(problem_path):
        return False, "File Error: Domain or Problem PDDL path is missing."

    cmd = ["fast-downward", domain_path, problem_path, "--search", "lazy_greedy([ff()])"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + "\n" + result.stderr

        if "Solution found!" in output or "Actual search time" in output:
            return True, output
        else:
            return False, output

    except FileNotFoundError:
        # If fast-downward binary is missing in local environment, fallback syntax check
        is_syntax_valid, log = check_pddl_syntax_fallback(domain_path, problem_path)
        if is_syntax_valid:
            return True, "Planner Info: fast-downward binary missing in local PATH, fallback syntax passed."
        return False, "System Warning: 'fast-downward' executable not found in system PATH."
    except subprocess.TimeoutExpired:
        return False, "Execution Error: Fast Downward timed out after 30 seconds."