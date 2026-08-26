import re
from typing import List, Tuple, Dict, Any, Optional
from schemas.pddl_blueprint import DiagnosticReport, ErrorCategory, RepairOperationType

def parse_val_log(val_log: str) -> List[DiagnosticReport]:
    """
    Parses output log from VAL (Validate binary) into structured DiagnosticReports.
    Categorizes errors into SYNTAX_PARSE, TYPE_SIGNATURE, or SYSTEM_ORACLE_ERROR.
    """
    reports = []
    
    if "not found" in val_log.lower() or "system warning" in val_log.lower():
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.SYSTEM_ORACLE_ERROR,
            repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
            faulty_element="VAL Oracle Binary",
            suspiciousness_score=0.0,
            raw_log=val_log.strip(),
            suggested_repair_hint="Ensure VAL executable 'Validate' is installed and available in system PATH."
        ))
        return reports

    lines = val_log.strip().split("\n")
    
    # Common VAL error patterns
    # 1. Type / Predicate signature errors
    type_err_patterns = [
        r"undefined predicate:?\s*\(?([\w-]+)",
        r"undefined type:?\s*([\w-]+)",
        r"type mismatch.*",
        r"arity mismatch.*",
        r"wrong number of arguments.*",
        r"type error.*"
    ]

    
    # 2. Syntax / Parse error patterns
    syntax_err_patterns = [
        r"syntax error.*",
        r"unexpected token.*",
        r"unclosed bracket.*",
        r"line (\d+):?\s*(.*)",
        r"error at or near.*",
        r"parse error.*"
    ]

    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("Successful plans:") or "Errors: 0" in line_clean:
            continue
            
        # Check for Type / Signature issues
        is_type_err = False
        for pat in type_err_patterns:
            match = re.search(pat, line_clean, re.IGNORECASE)
            if match:
                faulty = match.group(1) if match.groups() else None
                reports.append(DiagnosticReport(
                    error_category=ErrorCategory.TYPE_SIGNATURE,
                    repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
                    faulty_element=faulty,
                    suspiciousness_score=0.95,
                    raw_log=line_clean,
                    suggested_repair_hint=f"Check type declaration or predicate arity for '{faulty if faulty else 'implicated symbol'}'. Ensure parameter types and predicate declarations match."
                ))
                is_type_err = True
                break
        if is_type_err:
            continue

        # Check for Syntax / Parse issues
        is_syntax_err = False
        for pat in syntax_err_patterns:
            match = re.search(pat, line_clean, re.IGNORECASE)
            if match:
                reports.append(DiagnosticReport(
                    error_category=ErrorCategory.SYNTAX_PARSE,
                    repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
                    faulty_element=line_clean[:40],
                    suspiciousness_score=0.90,
                    raw_log=line_clean,
                    suggested_repair_hint="Fix PDDL syntax error. Ensure correct parenthesis nesting, valid keyword tags (:action, :parameters, :precondition, :effect), and proper PDDL headers."
                ))
                is_syntax_err = True
                break
        if is_syntax_err:
            continue

    # Fallback if log contains failure but no specific line matched
    if not reports and ("error" in val_log.lower() or "failed" in val_log.lower()):
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.SYNTAX_PARSE,
            repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
            faulty_element="Domain / Problem Specification",
            suspiciousness_score=0.70,
            raw_log=val_log.strip(),
            suggested_repair_hint="VAL validation failed. Verify PDDL domain and problem structure against PDDL standard specifications."
        ))

    return reports

def parse_fast_downward_log(fd_log: str) -> List[DiagnosticReport]:
    """
    Parses output log from Fast Downward planner into structured DiagnosticReports.
    Categorizes errors into GROUNDING_UNSOLVABILITY, TYPE_SIGNATURE, or SYSTEM_ORACLE_ERROR.
    """
    reports = []
    
    if "not found" in fd_log.lower() or "system warning" in fd_log.lower():
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.SYSTEM_ORACLE_ERROR,
            repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
            faulty_element="Fast Downward Binary",
            suspiciousness_score=0.0,
            raw_log=fd_log.strip(),
            suggested_repair_hint="Ensure Fast Downward executable 'fast-downward' is installed and available in system PATH."
        ))
        return reports

    log_lower = fd_log.lower()
    
    if "completely explored state space -- no solution" in log_lower or "no solution" in log_lower:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
            repair_operation_type=RepairOperationType.PRECONDITION_RELAXATION,
            faulty_element="State Transition Model / Goal Reachability",
            suspiciousness_score=0.88,
            raw_log="Fast Downward: Completely explored state space -- no solution!",
            suggested_repair_hint="The domain actions cannot achieve the goal state from the initial state. Relax over-constraining action preconditions or add missing state effects."
        ))
    elif "unbound variable" in log_lower or "grounding failed" in log_lower or "translate error" in log_lower:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.TYPE_SIGNATURE,
            repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
            faulty_element="Action Grounding / Variable Translation",
            suspiciousness_score=0.85,
            raw_log=fd_log.strip(),
            suggested_repair_hint="Fast Downward failed to ground action variables. Check that all variable parameters in preconditions and effects are declared in action parameters."
        ))
    elif "could not find a plan" in log_lower or "search stopped without finding a solution" in log_lower:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
            repair_operation_type=RepairOperationType.PRECONDITION_INSERTION,
            faulty_element="Planner Search",
            suspiciousness_score=0.80,
            raw_log=fd_log.strip(),
            suggested_repair_hint="Planner search exhausted or failed to find a valid action trajectory. Verify action causal chains from initial state to goal state."
        ))
    else:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
            faulty_element="Planning Execution",
            raw_log=fd_log.strip(),
            suggested_repair_hint="Fast Downward execution failed to produce a valid plan. Review domain action schemas and initial/goal problem definitions."
        ))

    return reports

def format_diagnostic_feedback(reports: List[DiagnosticReport]) -> str:
    """
    Formats a list of DiagnosticReports into a clean, structured feedback string
    suitable for LLM prompt context injection during repair iterations.
    """
    if not reports:
        return ""
        
    feedback_lines = ["### Diagnostic Failure Analysis Report:"]
    for idx, report in enumerate(reports, 1):
        feedback_lines.append(f"\nIssue #{idx}: [{report.error_category.value}]")
        feedback_lines.append(f"  - Target AST Operation: {report.repair_operation_type.value}")
        if report.faulty_element:
            feedback_lines.append(f"  - Implicated Component: {report.faulty_element} (Fault Rank Score: {report.suspiciousness_score})")
        feedback_lines.append(f"  - Oracle Raw Log Trace: {report.raw_log}")
        feedback_lines.append(f"  - Actionable Repair Hint: {report.suggested_repair_hint}")
        
    return "\n".join(feedback_lines)


def run_triage_node(state: dict) -> dict:
    """
    Phase 3.2 Triage Node: Receives raw verification errors from symbolic oracles,
    parses them into typed DiagnosticReports, and enriches the shared AgentState.
    """
    raw_errors = state.get("verification_errors", [])
    existing_reports = state.get("diagnostic_reports", [])
    
    diagnostic_reports: List[DiagnosticReport] = []
    
    # Re-hydrate existing DiagnosticReports if present (e.g. from Maintenance node)
    for report_item in existing_reports:
        if isinstance(report_item, DiagnosticReport):
            diagnostic_reports.append(report_item)
        elif isinstance(report_item, dict):
            try:
                diagnostic_reports.append(DiagnosticReport(**report_item))
            except Exception:
                pass

    for err in raw_errors:
        if err.startswith("VAL Error:"):
            val_log = err[len("VAL Error:"):].strip()
            parsed = parse_val_log(val_log)
            diagnostic_reports.extend(parsed)
        elif err.startswith("Planner Error:"):
            fd_log = err[len("Planner Error:"):].strip()
            parsed = parse_fast_downward_log(fd_log)
            diagnostic_reports.extend(parsed)
        elif err.startswith("[REGRESSION_BREAKAGE]"):
            diagnostic_reports.append(DiagnosticReport(
                error_category=ErrorCategory.HISTORICAL_REGRESSION,
                repair_operation_type=RepairOperationType.REGRESSION_BACKWARD_COMPATIBILITY,
                faulty_element="Backward Compatibility / Historical Regression Suite",
                suspiciousness_score=1.0,
                raw_log=err,
                suggested_repair_hint="The domain update broke planning capabilities on historical problem test cases. Ensure newly added action preconditions do not over-constrain existing state transitions."
            ))
        else:
            # Generic error wrapper
            diagnostic_reports.append(DiagnosticReport(
                error_category=ErrorCategory.SYNTAX_PARSE,
                faulty_element="General Validation",
                raw_log=err,
                suggested_repair_hint="Review PDDL blueprint syntax and structure."
            ))
            
    # Store structured reports and formatted string in shared state
    dumped_reports = [r.model_dump() for r in diagnostic_reports]
    state["diagnostic_reports"] = dumped_reports
    state["formatted_diagnostic_feedback"] = format_diagnostic_feedback(diagnostic_reports)

    hist_reports = state.get("historical_diagnostic_reports", [])
    for dr in dumped_reports:
        if dr not in hist_reports:
            hist_reports.append(dr)
    state["historical_diagnostic_reports"] = hist_reports
    
    print(f"[Triage Node]: Processed {len(diagnostic_reports)} diagnostic issues.")
    return state

