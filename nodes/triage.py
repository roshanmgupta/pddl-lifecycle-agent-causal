import re
from typing import List, Tuple, Dict, Any, Optional
from schemas.pddl_blueprint import DiagnosticReport, ErrorCategory

def parse_val_log(val_log: str) -> List[DiagnosticReport]:
    """
    Parses output log from VAL (Validate binary) into structured DiagnosticReports.
    Categorizes errors into SYNTAX_PARSE, TYPE_SIGNATURE, or SYSTEM_ORACLE_ERROR.
    """
    reports = []
    
    if "not found" in val_log.lower() or "system warning" in val_log.lower():
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.SYSTEM_ORACLE_ERROR,
            faulty_element="VAL Oracle Binary",
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
                    faulty_element=faulty,
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
                    faulty_element=line_clean[:40],
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
            faulty_element="Domain / Problem Specification",
            raw_log=val_log.strip()[:300],
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
            faulty_element="Fast Downward Binary",
            raw_log=fd_log.strip(),
            suggested_repair_hint="Ensure Fast Downward executable 'fast-downward' is installed and available in system PATH."
        ))
        return reports

    log_lower = fd_log.lower()
    
    if "completely explored state space -- no solution" in log_lower or "no solution" in log_lower:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
            faulty_element="State Transition Model / Goal Reachability",
            raw_log="Fast Downward: Completely explored state space -- no solution!",
            suggested_repair_hint="The domain actions cannot achieve the goal state from the initial state. Check if preconditions are too restrictive, if state transition effects are missing, or if required initial state facts are missing in the problem."
        ))
    elif "unbound variable" in log_lower or "grounding failed" in log_lower or "translate error" in log_lower:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.TYPE_SIGNATURE,
            faulty_element="Grounding / Variable Binding",
            raw_log=fd_log.strip()[:300],
            suggested_repair_hint="Fast Downward translator failed during grounding. Check action parameter variable names (must begin with '?') and type declarations."
        ))
    elif "could not find a plan" in log_lower or "search stopped without finding a solution" in log_lower:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
            faulty_element="Planner Search",
            raw_log=fd_log.strip()[:300],
            suggested_repair_hint="Planner search exhausted or failed to find a valid action trajectory. Verify action causal chains from initial state to goal state."
        ))
    else:
        reports.append(DiagnosticReport(
            error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
            faulty_element="Planning Execution",
            raw_log=fd_log.strip()[:300],
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
        if report.faulty_element:
            feedback_lines.append(f"  - Implicated Component: {report.faulty_element}")
        feedback_lines.append(f"  - Oracle Raw Log Trace: {report.raw_log}")
        feedback_lines.append(f"  - Actionable Repair Hint: {report.suggested_repair_hint}")
        
    return "\n".join(feedback_lines)

def run_triage_node(state: dict) -> dict:
    """
    Phase 3.2 Triage Node: Receives raw verification errors from symbolic oracles,
    parses them into typed DiagnosticReports, and enriches the shared AgentState.
    """
    raw_errors = state.get("verification_errors", [])
    
    diagnostic_reports: List[DiagnosticReport] = []
    
    for err in raw_errors:
        if err.startswith("VAL Error:"):
            val_log = err[len("VAL Error:"):].strip()
            parsed = parse_val_log(val_log)
            diagnostic_reports.extend(parsed)
        elif err.startswith("Planner Error:"):
            fd_log = err[len("Planner Error:"):].strip()
            parsed = parse_fast_downward_log(fd_log)
            diagnostic_reports.extend(parsed)
        else:
            # Generic error wrapper
            diagnostic_reports.append(DiagnosticReport(
                error_category=ErrorCategory.SYNTAX_PARSE,
                faulty_element="General Validation",
                raw_log=err,
                suggested_repair_hint="Review PDDL blueprint syntax and structure."
            ))
            
    # Store structured reports and formatted string in shared state
    state["diagnostic_reports"] = [r.model_dump() for r in diagnostic_reports]
    state["formatted_diagnostic_feedback"] = format_diagnostic_feedback(diagnostic_reports)
    
    print(f"[Triage Node]: Processed {len(diagnostic_reports)} diagnostic issues.")
    return state

