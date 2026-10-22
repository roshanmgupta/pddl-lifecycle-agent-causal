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
# Binary path resolution — configurable via .env (VAL_PATH, FAST_DOWNWARD_PATH)
# with automated fallback to repository tools/bin/ or system PATH.
# ---------------------------------------------------------------------------
import shutil
from dotenv import load_dotenv

load_dotenv()

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_oracle_binary(env_var_name: str, candidate_rel_paths: list, default_cmd: str) -> str:
    """
    Resolves binary path with priority:
    1. Environment variable (e.g. from .env file), resolved as absolute or relative to project root.
    2. Candidate relative paths inside project repository.
    3. System PATH lookup via shutil.which.
    4. Fallback to default candidate path.
    """
    env_path = os.getenv(env_var_name)
    if env_path:
        env_path = env_path.strip().strip('"').strip("'")
        if env_path:
            if not os.path.isabs(env_path):
                candidate_env = os.path.normpath(os.path.join(_PROJECT_ROOT, env_path))
            else:
                candidate_env = os.path.normpath(env_path)
            if os.path.exists(candidate_env):
                return candidate_env
            which_env = shutil.which(env_path)
            if which_env:
                return which_env
            return candidate_env

    for rel in candidate_rel_paths:
        full_p = os.path.normpath(os.path.join(_PROJECT_ROOT, rel))
        if os.path.exists(full_p):
            return full_p

    which_cmd = shutil.which(default_cmd)
    if which_cmd:
        return which_cmd

    if candidate_rel_paths:
        return os.path.normpath(os.path.join(_PROJECT_ROOT, candidate_rel_paths[0]))
    return default_cmd


def get_val_binary() -> str:
    """Returns resolved path to VAL (Validate) binary."""
    return _resolve_oracle_binary(
        env_var_name="VAL_PATH",
        candidate_rel_paths=[
            os.path.join("tools", "bin", "VAL", "build", "bin", "Validate.exe"),
            os.path.join("tools", "bin", "Validate.exe"),
            os.path.join("tools", "bin", "VAL", "build", "bin", "Validate"),
            os.path.join("tools", "bin", "Validate"),
        ],
        default_cmd="Validate",
    )


def get_fast_downward_binary() -> str:
    """Returns resolved path to Fast Downward script or executable."""
    env_name = "FAST_DOWNWARD_PATH" if os.getenv("FAST_DOWNWARD_PATH") else "FD_PATH"
    return _resolve_oracle_binary(
        env_var_name=env_name,
        candidate_rel_paths=[
            os.path.join("tools", "bin", "downward", "fast-downward.py"),
            os.path.join("tools", "bin", "fast-downward.py"),
        ],
        default_cmd="fast-downward",
    )


# Export resolved paths for module compatibility
VAL_BINARY = get_val_binary()
FD_BINARY = get_fast_downward_binary()


def run_val_validator(domain_path: str, problem_path: str = None) -> Tuple[bool, str]:
    """
    Executes VAL (Validate binary) against generated PDDL files.
    Returns (is_valid, console_output_log).
    """
    if not os.path.exists(domain_path):
        return False, f"File Error: Path '{domain_path}' does not exist."

    val_exe = get_val_binary()
    if not os.path.exists(val_exe) and not shutil.which(val_exe):
        return False, (
            f"VAL Error: Validate binary not found at '{val_exe}'. "
            "Please configure 'VAL_PATH' in your .env file (e.g., VAL_PATH=tools/bin/VAL/build/bin/Validate.exe) "
            "or ensure 'Validate' is available on your system PATH."
        )

    cmd = [val_exe, "-v", domain_path]
    if problem_path and os.path.exists(problem_path):
        cmd.append(problem_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout + "\n" + result.stderr

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
        return False, (
            f"VAL Error: Failed to execute VAL binary at '{val_exe}'. "
            "Verify 'VAL_PATH' in your .env file."
        )
    except subprocess.TimeoutExpired:
        return False, "Execution Error: VAL timed out after 15 seconds."


def run_fast_downward(domain_path: str, problem_path: str) -> Tuple[bool, str]:
    """
    Executes Fast Downward classical planner engine.
    Returns (plan_found, log_output).
    """
    if not os.path.exists(domain_path) or not os.path.exists(problem_path):
        return False, "File Error: Domain or Problem PDDL path is missing."

    fd_bin = get_fast_downward_binary()
    if not os.path.exists(fd_bin) and not shutil.which(fd_bin):
        return False, (
            f"Planner Error: Fast Downward not found at '{fd_bin}'. "
            "Please configure 'FAST_DOWNWARD_PATH' in your .env file (e.g., FAST_DOWNWARD_PATH=tools/bin/downward/fast-downward.py) "
            "or ensure 'fast-downward' is available on your system PATH."
        )

    if fd_bin.endswith(".py"):
        fd_cmd = [sys.executable, fd_bin]
    else:
        fd_cmd = [fd_bin]

    cmd = fd_cmd + [domain_path, problem_path, "--search", "lazy_greedy([ff()])"]

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
        return False, (
            f"Planner Error: Failed to execute Fast Downward at '{fd_bin}'. "
            "Verify 'FAST_DOWNWARD_PATH' in your .env file."
        )


def validate_plan_with_val(domain_path: str, problem_path: str, plan_path: str = "sas_plan") -> Tuple[bool, str]:
    """
    Executes VAL (Validate) against a domain, problem, and plan file to mathematically certify the plan.
    Returns (is_plan_valid, console_log).
    """
    if not os.path.exists(domain_path) or not os.path.exists(problem_path) or not os.path.exists(plan_path):
        return False, "File Error: Domain, Problem, or Plan path is missing."

    val_exe = get_val_binary()
    if not os.path.exists(val_exe) and not shutil.which(val_exe):
        return False, f"VAL Error: Validate binary not found at '{val_exe}'. Configure VAL_PATH in .env."

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


def validate_plan_semantic_soundness(
    ground_truth_domain_path: str, 
    problem_path: str, 
    plan_path: str,
    generated_domain_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validates a plan synthesized from a generated domain (D_gen) against the
    human gold-standard ground-truth domain (D_gt).
    Applies bijective operator and argument mapping from D_gen to D_gt so that VAL
    validates the true physical transitions in D_gt without string-name false negatives.
    """
    if generated_domain_path and os.path.exists(generated_domain_path) and os.path.exists(ground_truth_domain_path) and os.path.exists(plan_path):
        try:
            with open(ground_truth_domain_path, "r", encoding="utf-8", errors="ignore") as f:
                gt_dom = f.read()
            with open(generated_domain_path, "r", encoding="utf-8", errors="ignore") as f:
                gen_dom = f.read()
            with open(plan_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_lines = [l.strip() for l in f.readlines() if l.strip() and not l.strip().startswith(";")]

            from eval.action_reconstruction import translate_plan_to_ground_truth
            translated_steps = translate_plan_to_ground_truth(raw_lines, gt_dom, gen_dom)

            mapped_plan_path = plan_path + ".mapped.val"
            with open(mapped_plan_path, "w", encoding="utf-8") as pf:
                for idx, stp in enumerate(translated_steps, 1):
                    clean_stp = re.sub(r"^\d+:\s*", "", stp).strip()
                    pf.write(f"{idx}: {clean_stp}\n")

            is_valid, log = validate_plan_with_val(ground_truth_domain_path, problem_path, mapped_plan_path)
            if os.path.exists(mapped_plan_path):
                try:
                    os.remove(mapped_plan_path)
                except Exception:
                    pass
            return is_valid, log
        except Exception:
            pass

    return validate_plan_with_val(ground_truth_domain_path, problem_path, plan_path)



def validate_domain_coverage_admissibility(generated_domain_path: str, problem_path: str, ground_truth_plan_path: str) -> Tuple[bool, str]:
    """
    Validates whether the known human ground-truth plan (pi_gt) executes cleanly on
    the generated domain (D_gen).
    Verifies that the generated domain is not over-constrained or blocking valid classical trajectories.
    """
    return validate_plan_with_val(generated_domain_path, problem_path, ground_truth_plan_path)


def run_fast_downward_with_plan(
    domain_path: str, 
    problem_path: str, 
    ground_truth_domain_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes Fast Downward and returns comprehensive plan metrics + VAL validation certificate.
    
    If 'ground_truth_domain_path' is provided, performs non-circular Semantic Soundness Cross-Validation:
    validates the synthesized plan against D_gt using VAL, ensuring the plan obeys real-world invariants.
    """
    is_ok, raw_log = run_fast_downward(domain_path, problem_path)
    
    plan_steps = []
    plan_cost = 0
    search_time = 0.0
    val_valid = False
    val_log = ""
    semantic_soundness_valid = False
    semantic_soundness_log = ""
    
    from config.paths import get_temp_plan_path
    plan_file = get_temp_plan_path()
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
        # 1. Internal Consistency Check (Circularity baseline: D_gen satisfies itself)
        val_valid, val_log = validate_plan_with_val(domain_path, problem_path, plan_file)
        
        # 2. Non-Circular Semantic Soundness Check: D_gt evaluates pi_gen
        if ground_truth_domain_path and os.path.exists(ground_truth_domain_path):
            semantic_soundness_valid, semantic_soundness_log = validate_plan_semantic_soundness(
                ground_truth_domain_path, problem_path, plan_file, generated_domain_path=domain_path
            )

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
        "semantic_soundness_valid": semantic_soundness_valid,
        "semantic_soundness_log": semantic_soundness_log,
        "raw_fd_log": raw_log
    }