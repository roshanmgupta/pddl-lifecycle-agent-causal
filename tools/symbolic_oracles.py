"""
tools/symbolic_oracles.py
Phase 3.1 Tool Execution Wrapper: Strict Symbolic Oracles

Direct command-line subprocess interface to:
1. VAL (Validate.exe / Validate) - Formal syntax, type, and plan validator.
2. Fast Downward (fast-downward.py) - SAS+ translator and classical heuristic planner.
"""
import subprocess
import os
import sys
import re
from typing import Tuple, Dict, Any

# ---------------------------------------------------------------------------
# Binary path resolution — tools live inside tools/bin/ in the project repo.
# This works regardless of system PATH configuration.
# ---------------------------------------------------------------------------
import shutil

_TOOLS_BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools", "bin")

# Locate VAL (Windows .exe, system PATH)
_val_candidates = [
    os.path.join(_TOOLS_BIN, "VAL", "build", "bin", "Validate.exe"),
    shutil.which("Validate") or ""
]
VAL_BINARY = next((p for p in _val_candidates if p and os.path.exists(p)), os.path.join(_TOOLS_BIN, "VAL", "build", "bin", "Validate.exe"))

# Locate Fast Downward (bundled Python script or system fast-downward)
_fd_candidates = [
    os.path.join(_TOOLS_BIN, "downward", "fast-downward.py"),
    shutil.which("fast-downward") or ""
]
FD_BINARY = next((p for p in _fd_candidates if p and os.path.exists(p)), os.path.join(_TOOLS_BIN, "downward", "fast-downward.py"))


def run_val_validator(domain_path: str, problem_path: str = None) -> Tuple[bool, str]:
    """
    Executes VAL (Validate.exe binary) against generated PDDL files.
    Returns (is_valid, console_output_log).
    """
    if not os.path.exists(domain_path):
        return False, f"File Error: Path '{domain_path}' does not exist."

    # Use bundled VAL binary from tools/bin/ with verbose flag for granular diagnostics
    val_exe = VAL_BINARY if os.path.exists(VAL_BINARY) else "Validate"
    cmd = [val_exe, "-v", domain_path]
    if problem_path and os.path.exists(problem_path):
        cmd.append(problem_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout + "\n" + result.stderr # the output look like ex. ./validate domain.pddl problem.pddl and return errors if any 
        
        # Check for VAL failure signals
        has_error = (
            result.returncode != 0
            or "error in type-checking" in output.lower()
            or "type problem" in output.lower()
            or "syntax error" in output.lower()
            or "parse error" in output.lower()
            or "error:" in output.lower()
        )
        if not has_error and ("Errors: 0" in output or "Successful plans:" in output or result.returncode == 0):
            return True, output
        else:
            clean_out = output.strip()
            if not clean_out and result.returncode != 0:
                clean_out = f"VAL Parser Crash (exit code {result.returncode}): Syntax violation detected. Check for undeclared variables or inline type annotations in action expressions."
            return False, clean_out

    except FileNotFoundError:
        return False, f"VAL Error: Validate.exe not found at '{VAL_BINARY}'. Ensure tools/bin/VAL/ is present."
    except subprocess.TimeoutExpired:
        return False, "Execution Error: VAL timed out after 15 seconds."


def run_fast_downward(domain_path: str, problem_path: str) -> Tuple[bool, str]:
    """
    Executes Fast Downward classical planner engine.
    Returns (plan_found, log_output).
    """
    if not os.path.exists(domain_path) or not os.path.exists(problem_path):
        return False, "File Error: Domain or Problem PDDL path is missing."

    # Use bundled Fast Downward from tools/bin/
    fd_exe = [sys.executable, FD_BINARY] if os.path.exists(FD_BINARY) else ["fast-downward"]
    cmd = fd_exe + [domain_path, problem_path, "--search", "lazy_greedy([ff()])"]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            stdout, stderr = proc.communicate(timeout=30)
            output = (stdout or "") + "\n" + (stderr or "")
            if "Solution found!" in output:
                return True, output
            else:
                return False, output
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
            else:
                proc.kill()
            return False, "Execution Error: Fast Downward timed out after 30 seconds."
    except FileNotFoundError:
        return False, f"Planner Error: fast-downward.py not found at '{FD_BINARY}'. Ensure tools/bin/downward/ is present."


def validate_plan_with_val(domain_path: str, problem_path: str, plan_path: str = "sas_plan") -> Tuple[bool, str]:
    """
    Executes VAL (Validate.exe) against a domain, problem, and plan file to mathematically certify the plan.
    Returns (is_plan_valid, console_log).
    """
    if not os.path.exists(domain_path) or not os.path.exists(problem_path) or not os.path.exists(plan_path):
        return False, "File Error: Domain, Problem, or Plan path is missing."

    val_exe = VAL_BINARY if os.path.exists(VAL_BINARY) else "Validate"
    cmd = [val_exe, domain_path, problem_path, plan_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout + "\n" + result.stderr
        if "Plan valid" in output or "Successful plans:" in output:
            return True, output
        else:
            return False, output
    except Exception as e:
        return False, f"VAL Plan Validation Error: {e}"


def run_fast_downward_with_plan(domain_path: str, problem_path: str) -> Dict[str, Any]:
    """
    Executes Fast Downward and returns comprehensive plan metrics + VAL validation certificate.
    """
    is_ok, raw_log = run_fast_downward(domain_path, problem_path)
    
    plan_steps = []
    plan_cost = 0
    search_time = 0.0
    val_valid = False
    val_log = ""
    
    plan_file = "sas_plan"
    if not os.path.exists(plan_file):
        for candidate in ["sas_plan.1", "sas_plan.2", "sas_plan.3"]:
            if os.path.exists(candidate):
                plan_file = candidate
                break

    if os.path.exists(plan_file):
        try:
            with open(plan_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            for l in lines:
                if l.startswith(";"):
                    cost_m = re.search(r"cost\s*=\s*(\d+)", l)
                    if cost_m:
                        plan_cost = int(cost_m.group(1))
                else:
                    plan_steps.append(l)
        except Exception:
            pass

    time_m = re.search(r"Search time:\s*([0-9\.]+)s", raw_log)
    if time_m:
        try:
            search_time = float(time_m.group(1))
        except ValueError:
            pass

    if is_ok and os.path.exists(plan_file):
        val_valid, val_log = validate_plan_with_val(domain_path, problem_path, plan_file)

    # Clean up intermediate solver artifacts
    for artifact in ["output.sas", "sas_plan", "sas_plan.1", "sas_plan.2", "sas_plan.3"]:
        if os.path.exists(artifact):
            try:
                os.remove(artifact)
            except Exception:
                pass
            
    return {
        "is_solvable": is_ok,
        "plan_steps": plan_steps,
        "plan_length": len(plan_steps),
        "plan_cost": plan_cost if plan_cost > 0 else len(plan_steps),
        "search_time": search_time,
        "val_plan_valid": val_valid,
        "val_log": val_log,
        "raw_fd_log": raw_log
    }