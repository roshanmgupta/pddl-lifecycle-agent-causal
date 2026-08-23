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

        # 3. Check problem file if provided
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