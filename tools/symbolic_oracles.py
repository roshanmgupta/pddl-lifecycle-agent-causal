# %%writefile tools/symbolic_oracles.py
import subprocess
import os
from typing import Tuple, Dict, Any

def run_val_validator(domain_path: str, problem_path: str = None) -> Tuple[bool, str]:
    """
    Executes VAL (Validate binary) against a generated domain.pddl file.
    Returns (is_valid, console_output_log).
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
        
        # Check for typical VAL failure markers
        if "Errors: 0" in output or "Successful plans:" in output:
            return True, output
        elif result.returncode == 0 and "Error" not in output:
            return True, output
        else:
            return False, output

    except FileNotFoundError:
        # Fallback handling if VAL binary isn't globally in $PATH during early testing
        return False, "System Warning: 'Validate' binary not found in system PATH."
    except subprocess.TimeoutExpired:
        return False, "Execution Error: VAL timed out after 15 seconds."

def run_fast_downward(domain_path: str, problem_path: str) -> Tuple[bool, str]:
    """
    Executes Fast Downward classical planner engine.
    Returns (plan_found, log_output).
    """
    if not os.path.exists(domain_path) or not os.path.exists(problem_path):
        return False, "File Error: Domain or Problem PDDL path is missing."

    # Fast Downward search invocation using LAMA-first alias or default heuristic
    cmd = ["fast-downward", domain_path, problem_path, "--search", "lazy_greedy([ff()])"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + "\n" + result.stderr

        if "Solution found!" in output or "Actual search time" in output:
            return True, output
        else:
            return False, output

    except FileNotFoundError:
        return False, "System Warning: 'fast-downward' executable not found in system PATH."
    except subprocess.TimeoutExpired:
        return False, "Execution Error: Fast Downward timed out after 30 seconds."