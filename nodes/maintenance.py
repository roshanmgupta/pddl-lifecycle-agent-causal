import os
import tempfile
from typing import Dict, Any, List
from schemas.pddl_blueprint import (
    DiagnosticReport,
    ErrorCategory,
    RepairOperationType,
    HistoricalProblemCase
)
from nodes.generation import compile_pddl_programmatically, compile_problem_pddl
from tools.symbolic_oracles import run_val_validator, run_fast_downward

def run_maintenance_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 4: Maintenance & Evolution Node.
    
    Verifies that an updated/repaired domain blueprint maintains backward compatibility
    with all historical problem instances stored in the regression suite.
    """
    import time
    start_t = time.time()
    domain_blueprint = state.get("pddl_domain_blueprint")
    domain_pddl = state.get("generated_domain_pddl")
    regression_suite = state.get("historical_regression_suite", [])

    if not regression_suite:
        print("[Maintenance Node]: No historical test cases in regression suite. Skipping backward compatibility check.")
        return state

    print(f"[Maintenance Node]: Running Phase 4 Backward Compatibility Suite on {len(regression_suite)} historical problem(s)...")

    # Ensure domain_blueprint is a dictionary if passed as a Pydantic model
    if hasattr(domain_blueprint, "model_dump"):
        domain_blueprint = domain_blueprint.model_dump()
    elif hasattr(domain_blueprint, "dict"):
        domain_blueprint = domain_blueprint.dict()

    # Ensure domain PDDL is compiled
    if not domain_pddl and domain_blueprint:
        domain_pddl = compile_pddl_programmatically(domain_blueprint)

    if not domain_pddl:
        print("[Maintenance Node Warning]: No compiled domain PDDL available for maintenance verification.")
        return state

    # Isolate Phase 4 error collectors to prevent inheriting stale errors
    verification_errors = []
    diagnostic_reports = []
    has_regression_failure = False

    with tempfile.TemporaryDirectory() as temp_dir:
        domain_file_path = os.path.join(temp_dir, "domain.pddl")
        with open(domain_file_path, "w", encoding="utf-8") as f:
            f.write(domain_pddl)

        for case_idx, case_data in enumerate(regression_suite):
            if isinstance(case_data, dict):
                case_id = case_data.get("case_id", f"historical_case_{case_idx+1}")
                prob_bp = dict(case_data.get("problem_blueprint", {}))
            elif isinstance(case_data, HistoricalProblemCase):
                case_id = case_data.case_id
                prob_bp = case_data.problem_blueprint.model_dump()
            else:
                continue

            # Ensure problem domain_name strictly matches active domain_blueprint domain_name
            if domain_blueprint and "domain_name" in domain_blueprint:
                prob_bp["domain_name"] = domain_blueprint["domain_name"]

            # Compile historical problem PDDL
            try:
                hist_prob_pddl = compile_problem_pddl(prob_bp, domain_blueprint_data=domain_blueprint)
            except Exception as e:
                err_msg = f"[REGRESSION_ERROR]: Failed to compile historical problem '{case_id}': {str(e)}"
                verification_errors.append(err_msg)
                has_regression_failure = True
                continue

            problem_file_path = os.path.join(temp_dir, f"problem_{case_id}.pddl")
            with open(problem_file_path, "w", encoding="utf-8") as f:
                f.write(hist_prob_pddl)

            # Step 1: Check Syntax with VAL
            val_ok, val_log = run_val_validator(domain_file_path, problem_file_path)
            if not val_ok:
                err_text = f"[REGRESSION_BREAKAGE]: Historical case '{case_id}' failed VAL syntax validation.\nLog: {val_log}"
                print(f"  [FAIL] {err_text}")
                import re
                missing_pred_m = re.search(r"Predicate\s+(\w+)\s+not found", val_log)
                hint = f"Historical test case '{case_id}' failed syntax validation with updated domain. Check for broken predicate definitions or arities."
                if missing_pred_m:
                    pname = missing_pred_m.group(1)
                    hint = f"Historical test case '{case_id}' failed because predicate '{pname}' is missing in the evolved domain. Declare '({pname} ...)' in domain 'predicates' with matching argument types to restore backward compatibility."

                verification_errors.append(err_text)
                diagnostic_reports.append(
                    DiagnosticReport(
                        error_category=ErrorCategory.HISTORICAL_REGRESSION,
                        repair_operation_type=RepairOperationType.REGRESSION_BACKWARD_COMPATIBILITY,
                        faulty_element=case_id,
                        suspiciousness_score=1.0,
                        raw_log=val_log,
                        suggested_repair_hint=hint
                    )
                )
                has_regression_failure = True
                continue

            # Step 2: Check Plan Reachability with Fast Downward
            from tools.symbolic_oracles import run_fast_downward_with_plan
            plan_res = run_fast_downward_with_plan(domain_file_path, problem_file_path)
            fd_ok = plan_res["is_solvable"]
            fd_log = plan_res.get("raw_fd_log", "")
            
            if not fd_ok:
                err_text = f"[REGRESSION_BREAKAGE]: Historical case '{case_id}' failed Fast Downward plan reachability.\nLog: {fd_log}"
                print(f"  [FAIL] {err_text}")
                verification_errors.append(err_text)
                diagnostic_reports.append(
                    DiagnosticReport(
                        error_category=ErrorCategory.HISTORICAL_REGRESSION,
                        repair_operation_type=RepairOperationType.REGRESSION_BACKWARD_COMPATIBILITY,
                        faulty_element=case_id,
                        suspiciousness_score=1.0,
                        raw_log=fd_log,
                        suggested_repair_hint=f"Historical test case '{case_id}' became unsolvable with updated domain. Ensure newly added action preconditions do not over-constrain historical state transitions."
                    )
                )
                has_regression_failure = True
            else:
                print(f"  [PASS] Historical case '{case_id}' passed backward compatibility check!")
                hist_plans = list(state.get("historical_plan_results", []))
                hist_plans.append({
                    "case_id": case_id,
                    "plan_result": plan_res
                })
                state["historical_plan_results"] = hist_plans

    if has_regression_failure:
        state["verification_errors"] = verification_errors
        state["diagnostic_reports"] = diagnostic_reports
    else:
        state["verification_errors"] = []
        state["diagnostic_reports"] = []
        print("[Maintenance Node]: All historical regression test cases passed successfully!")
        
    latencies = state.get("node_latencies", {})
    latencies["maintenance"] = round(latencies.get("maintenance", 0.0) + (time.time() - start_t), 3)
    state["node_latencies"] = latencies
    return state
