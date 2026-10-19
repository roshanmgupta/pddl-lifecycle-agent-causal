import json
import re
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from schemas.pddl_blueprint import DiagnosticReport, ErrorCategory, RepairOperationType
from config.pddl_standards import STANDARD_CLASSICAL_PDDL_RULES, STANDARD_DIAGNOSTIC_RULES
from config.model_config import get_phase_model, invoke_structured_llm_with_telemetry
from tools.sbfl_analyzer import run_causal_graph_sbfl_analysis

class DiagnosticAnalysis(BaseModel):
    """Container for structured diagnostic reports produced by the Diagnostic LLM Agent."""
    reports: List[DiagnosticReport] = Field(
        default_factory=list,
        description="Ranked list of diagnostic reports localizing faults and suggesting repair operations"
    )

def check_system_oracle_binary_availability(raw_log: str, oracle_name: str) -> Optional[DiagnosticReport]:
    """
    Checks if an oracle error is caused by a missing system binary (Validate.exe or downward.exe)
    rather than a domain modeling defect.
    """
    log_lower = raw_log.lower()
    if "not found" in log_lower or "system warning" in log_lower:
        binary_label = "VAL Oracle Binary (Validate.exe)" if oracle_name == "VAL" else "Fast Downward Binary (downward.exe)"
        hint = (
            "Ensure VAL executable 'Validate.exe' is installed and available in tools/bin/VAL/."
            if oracle_name == "VAL"
            else "Ensure Fast Downward executable 'downward.exe' is available in tools/bin/downward/."
        )
        return DiagnosticReport(
            error_category=ErrorCategory.SYSTEM_ORACLE_ERROR,
            repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
            faulty_element=binary_label,
            suspiciousness_score=0.0,
            raw_log=raw_log.strip()[:300],
            suggested_repair_hint=hint
        )
    return None

def parse_val_log(val_log: str) -> List[DiagnosticReport]:
    """Backward-compatible wrapper checking VAL binary availability."""
    rep = check_system_oracle_binary_availability(val_log, "VAL")
    return [rep] if rep else []

    # [LEGACY CODE COMMENTED OUT TEMPORARILY - Will be removed once agent workflow is completely finalized]
    # lines = val_log.strip().split("\n")
    # type_err_patterns = [
    #     r"undefined predicate:?\s*\(?([\w-]+)",
    #     r"undefined type:?\s*([\w-]+)",
    #     r"type mismatch.*",
    #     r"arity mismatch.*",
    #     r"wrong number of arguments.*",
    #     r"type error.*",
    #     r"undefined object:?\s*([\w-]+)",
    #     r"unknown type:?\s*([\w-]+)"
    # ]
    # syntax_err_patterns = [
    #     r"syntax error.*",
    #     r"unexpected token.*",
    #     r"unclosed bracket.*",
    #     r"line (\d+):?\s*(.*)",
    #     r"error at or near.*",
    #     r"parse error.*",
    #     r"failed to read file.*",
    #     r"parser failed.*"
    # ]
    # for line in lines:
    #     line_clean = line.strip()
    #     if not line_clean or line_clean.startswith("Successful plans:") or "Errors: 0" in line_clean or "passes type checking" in line_clean:
    #         continue
    #     is_type_err = False
    #     for pat in type_err_patterns:
    #         match = re.search(pat, line_clean, re.IGNORECASE)
    #         if match:
    #             faulty = match.group(1) if match.groups() else None
    #             reports.append(DiagnosticReport(
    #                 error_category=ErrorCategory.TYPE_SIGNATURE,
    #                 repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
    #                 faulty_element=faulty or "Type / Predicate Signature",
    #                 suspiciousness_score=0.90,
    #                 raw_log=line_clean,
    #                 suggested_repair_hint=f"Check type declaration or predicate arity for '{faulty if faulty else 'implicated symbol'}'. Ensure parameter types and predicate declarations match."
    #             ))
    #             is_type_err = True
    #             break
    #     if is_type_err:
    #         continue
    #     is_syntax_err = False
    #     for pat in syntax_err_patterns:
    #         match = re.search(pat, line_clean, re.IGNORECASE)
    #         if match:
    #             reports.append(DiagnosticReport(
    #                 error_category=ErrorCategory.SYNTAX_PARSE,
    #                 repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
    #                 faulty_element=line_clean[:40],
    #                 suspiciousness_score=1.00,
    #                 raw_log=line_clean,
    #                 suggested_repair_hint="Fix PDDL syntax error. Ensure correct parenthesis nesting, valid keyword tags (:action, :parameters, :precondition, :effect), and proper PDDL headers."
    #             ))
    #             is_syntax_err = True
    #             break
    #     if is_syntax_err:
    #         continue
    # if not reports and ("error" in val_log.lower() or "failed" in val_log.lower()):
    #     reports.append(DiagnosticReport(
    #         error_category=ErrorCategory.SYNTAX_PARSE,
    #         repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
    #         faulty_element="Domain / Problem Specification",
    #         suspiciousness_score=0.80,
    #         raw_log=val_log.strip()[:300],
    #         suggested_repair_hint="VAL validation failed. Verify PDDL domain and problem structure against PDDL standard specifications."
    #     ))

    return reports

def parse_fast_downward_log(fd_log: str, causal_analysis: Optional[Dict[str, Any]] = None) -> List[DiagnosticReport]:
    """Backward-compatible wrapper checking Fast Downward binary availability."""
    rep = check_system_oracle_binary_availability(fd_log, "Fast Downward")
    return [rep] if rep else []

    # [LEGACY CODE COMMENTED OUT TEMPORARILY - Will be removed once agent workflow is completely finalized]
    # if causal_analysis:
    #     for ic in causal_analysis.get("internal_contradictions", []):
    #         reports.append(DiagnosticReport(
    #             error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
    #             repair_operation_type=RepairOperationType.EFFECT_ALIGNMENT,
    #             faulty_element=f"Action '{ic['action_name']}'",
    #             suspiciousness_score=1.0,
    #             raw_log=ic["description"],
    #             suggested_repair_hint=f"Resolve internal contradiction in action '{ic['action_name']}': an action cannot simultaneously assert and negate predicates: {', '.join(ic.get('predicates', []))}."
    #         ))
    #     for it in causal_analysis.get("irreversible_transitions", []):
    #         if it.get("severity") == "CRITICAL":
    #             del_str = ", ".join(it.get("deleted_by", []))
    #             reports.append(DiagnosticReport(
    #                 error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
    #                 repair_operation_type=RepairOperationType.EFFECT_ALIGNMENT,
    #                 faulty_element=f"Predicate '{it['predicate']}'",
    #                 suspiciousness_score=0.90,
    #                 raw_log=f"Predicate '{it['predicate']}' is deleted by [{del_str}] but has no producer action in domain.",
    #                 suggested_repair_hint=f"Ensure an enabling action provides an effect asserting '({it['predicate']} ...)' or adjust [{del_str}] to prevent absorbing state lockouts."
    #             ))
    #     for cyc in causal_analysis.get("causal_cycles", []):
    #         cyc_str = " -> ".join(cyc)
    #         reports.append(DiagnosticReport(
    #             error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
    #             repair_operation_type=RepairOperationType.PRECONDITION_RELAXATION,
    #             faulty_element=f"Cycle [{cyc_str}]",
    #             suspiciousness_score=0.88,
    #             raw_log=f"Circular action dependency cycle detected without initial state bootstrap: {cyc_str}",
    #             suggested_repair_hint=f"Break the circular dependency in cycle [{cyc_str}] or initialize required preconditions in problem :init."
    #         ))
    # log_lower = fd_log.lower()
    # top_candidate = causal_analysis.get("top_action") if causal_analysis else None
    # top_score = causal_analysis.get("top_score", 0.85) if causal_analysis else 0.85
    # fault_elem = f"Action '{top_candidate}'" if (top_candidate and not top_candidate.startswith("General")) else "State Transition Model / Goal Reachability"
    # if "completely explored state space -- no solution" in log_lower or "no solution" in log_lower:
    #     reports.append(DiagnosticReport(
    #         error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
    #         repair_operation_type=RepairOperationType.PRECONDITION_RELAXATION,
    #         faulty_element=fault_elem,
    #         suspiciousness_score=max(0.85, top_score),
    #         raw_log="Fast Downward: Completely explored state space -- no solution!",
    #         suggested_repair_hint="The domain actions cannot achieve the goal state from the initial state. Check if action preconditions are over-constraining state transitions, if required state effects are missing, or if required initial state facts are missing in problem :init."
    #     ))
    # elif "unbound variable" in log_lower or "grounding failed" in log_lower or "translate error" in log_lower or "undefined variable" in log_lower:
    #     match = re.search(r"undefined variable.*?got:?\s*(\?\w+)", fd_log, re.IGNORECASE)
    #     var_name = match.group(1) if match else "Unbound Variable"
    #     reports.append(DiagnosticReport(
    #         error_category=ErrorCategory.TYPE_SIGNATURE,
    #         repair_operation_type=RepairOperationType.TYPE_ARITY_ALIGNMENT,
    #         faulty_element=f"Variable {var_name}",
    #         suspiciousness_score=0.85,
    #         raw_log=fd_log.strip()[:300],
    #         suggested_repair_hint=f"Fast Downward failed during variable grounding. Ensure variable '{var_name}' is explicitly declared in the action's :parameters list."
    #     ))
    # elif "could not find a plan" in log_lower or "search stopped without finding a solution" in log_lower or "timed out" in log_lower:
    #     reports.append(DiagnosticReport(
    #         error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
    #         repair_operation_type=RepairOperationType.PRECONDITION_INSERTION,
    #         faulty_element=fault_elem,
    #         suspiciousness_score=max(0.80, top_score),
    #         raw_log=fd_log.strip()[:300],
    #         suggested_repair_hint="Planner search exhausted or timed out. Verify action causal chains from initial state to goal state and ensure required enabling actions are present."
    #     ))
    # elif not reports:
    #     reports.append(DiagnosticReport(
    #         error_category=ErrorCategory.GROUNDING_UNSOLVABILITY,
    #         repair_operation_type=RepairOperationType.GENERAL_AST_REPAIR,
    #         faulty_element=fault_elem,
    #         suspiciousness_score=0.75,
    #         raw_log=fd_log.strip()[:300],
    #         suggested_repair_hint="Fast Downward execution failed to produce a valid plan. Review domain action schemas and initial/goal problem definitions."
    #     ))

    return reports

def format_diagnostic_feedback(reports: List[DiagnosticReport]) -> str:
    """
    Formats structured DiagnosticReports into a clear, literature-grounded feedback block
    (following Smirnov et al. 2024; Chen et al. 2024):
    [ERROR TYPE], [TARGET AST OPERATION], [LOCATION], and [SUGGESTION FOR REPAIR].
    """
    if not reports:
        return ""
        
    feedback_lines = ["### Diagnostic Failure Analysis Report (Symbolic Oracle Triage):"]
    for idx, report in enumerate(reports, 1):
        cat = report.error_category.value if hasattr(report.error_category, "value") else str(report.error_category)
        op = report.repair_operation_type.value if hasattr(report.repair_operation_type, "value") else str(report.repair_operation_type)
        feedback_lines.append(f"\nIssue #{idx}:")
        feedback_lines.append(f"  - [ERROR TYPE]: {cat}")
        feedback_lines.append(f"  - [TARGET AST OPERATION]: {op}")
        if report.faulty_element:
            score_str = f"{report.suspiciousness_score:.2f}" if isinstance(report.suspiciousness_score, (int, float)) else str(report.suspiciousness_score)
            feedback_lines.append(f"  - [LOCATION / COMPONENT]: {report.faulty_element} (Fault Suspiciousness Score: {score_str})")
        feedback_lines.append(f"  - [DESCRIPTION / RAW TRACE]: {report.raw_log}")
        feedback_lines.append(f"  - [SUGGESTION FOR REPAIR]: {report.suggested_repair_hint}")
        
    return "\n".join(feedback_lines)

def run_triage_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 3.1 Diagnostic Triage Node: Invokes the Diagnostic LLM Agent to reason about oracle failures,
    localize faulty actions/predicates, and generate structured DiagnosticReports.
    """
    start_t = time.time()
    raw_errors = state.get("verification_errors", [])
    
    if not raw_errors:
        state["diagnostic_reports"] = []
        state["formatted_diagnostic_feedback"] = ""
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    if state.get("skip_triage"):
        print("[Triage Node (ABLATION)]: Triage bypassed. Forwarding raw oracle errors directly to repair node.")
        state["diagnostic_reports"] = []
        state["formatted_diagnostic_feedback"] = "Raw Oracle Verification Errors (Unstructured Feedback):\n" + "\n".join(raw_errors)
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    # Pre-flight Check: Detect instant System Oracle / Executable binary errors
    system_reports: List[DiagnosticReport] = []
    for err in raw_errors:
        err_lower = err.lower()
        if "not found" in err_lower or "system warning" in err_lower:
            if err.startswith("VAL Error:"):
                rep = check_system_oracle_binary_availability(err[len("VAL Error:"):].strip(), "VAL")
                if rep:
                    system_reports.append(rep)
            elif err.startswith("Planner Error:"):
                rep = check_system_oracle_binary_availability(err[len("Planner Error:"):].strip(), "Fast Downward")
                if rep:
                    system_reports.append(rep)

    if any(r.error_category == ErrorCategory.SYSTEM_ORACLE_ERROR for r in system_reports):
        print("[Triage Node]: Detected System Oracle executable binary issue. Bypassing LLM triage.")
        dumped_reports = [r.model_dump() for r in system_reports]
        state["diagnostic_reports"] = dumped_reports
        state["formatted_diagnostic_feedback"] = format_diagnostic_feedback(system_reports)
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    domain_bp = state.get("pddl_domain_blueprint", {})
    problem_bp = state.get("pddl_problem_blueprint", {})
    requirements_text = state.get("requirements", "")
    error_traces_str = "\n".join(raw_errors)

    # Classical Causal Graph & Spectrum-Based Fault Localization Analysis
    causal_analysis = run_causal_graph_sbfl_analysis(
        domain_bp,
        problem_bp,
        raw_errors,
        state.get("historical_test_results", [])
    )
    state["causal_graph_analysis"] = causal_analysis
    causal_summary = causal_analysis.get("diagnostic_summary", "")

    val_syntax_or_type_error = any("VAL Error:" in err for err in raw_errors)
    focus_guidance = ""
    if val_syntax_or_type_error:
        focus_guidance = """
CRITICAL TRIAGE FOCUS:
The primary error is a strict syntax or type-checking violation detected by VAL.
Focus strictly on localizing and resolving the syntax or type/arity mismatch in the indicated action/predicate schema.
Do NOT report speculative state-reachability, cycle, or goal-distance issues when the domain has an active type or syntax defect.
"""

    prompt = f"""You are an expert PDDL Diagnostic & Fault Localization Oracle.

Your task is to analyze the failure signals from symbolic oracles (VAL / Fast Downward / Regression Suite) against the current PDDL relational blueprints, localize the root-cause fault, and produce structured DiagnosticReports.

NATURAL LANGUAGE REQUIREMENTS:
{requirements_text}

CURRENT DOMAIN BLUEPRINT:
```json
{json.dumps(domain_bp, indent=2)}
```

CURRENT PROBLEM BLUEPRINT:
```json
{json.dumps(problem_bp, indent=2)}
```

RAW ORACLE VERIFICATION ERRORS:
{error_traces_str}

GROUNDED CAUSAL GRAPH & SPECTRUM-BASED FAULT LOCALIZATION ANALYSIS:
{causal_summary}

    {focus_guidance}
    {STANDARD_CLASSICAL_PDDL_RULES}
    {STANDARD_DIAGNOSTIC_RULES}

    For each identified issue, provide:
    - error_category: SYNTAX_PARSE, TYPE_SIGNATURE, GROUNDING_UNSOLVABILITY, SYSTEM_ORACLE_ERROR, or HISTORICAL_REGRESSION
    - repair_operation_type: PRECONDITION_RELAXATION, PRECONDITION_INSERTION, EFFECT_ALIGNMENT, TYPE_ARITY_ALIGNMENT, INITIAL_STATE_AUGMENTATION, or GENERAL_AST_REPAIR
    - faulty_element: Name of the specific action (e.g. 'pick-up', 'drop', 'drive'), predicate, or null if general
    - suspiciousness_score: Fault localization confidence ranking between 0.0 and 1.0 (e.g. 0.9 for primary suspect, 0.7 for secondary)
    - raw_log: Exact or summarized log snippet from the oracle
    - suggested_repair_hint: Detailed actionable guidance on what conditions or transitions to adjust

    Return a valid JSON object strictly matching the DiagnosticAnalysis schema.
    """

    print("[Triage Node]: Invoking Diagnostic LLM Agent for structured fault localization...")
    diagnostic_reports: List[DiagnosticReport] = []

    try:
        analysis, usage = invoke_structured_llm_with_telemetry(
            DiagnosticAnalysis,
            prompt,
            target_model=get_phase_model(3)
        )
        diagnostic_reports = analysis.reports

        # Ensure valid normalized suspiciousness scores
        action_scores = dict(causal_analysis.get("ranked_actions", []))
        for report in diagnostic_reports:
            if report.suspiciousness_score is None:
                report.suspiciousness_score = action_scores.get(report.faulty_element, 0.5)
            else:
                report.suspiciousness_score = round(max(0.0, min(1.0, float(report.suspiciousness_score))), 2)

        # Update Telemetry Metrics
        state["total_prompt_tokens"] = state.get("total_prompt_tokens", 0) + usage.get("prompt_tokens", 0)
        state["total_completion_tokens"] = state.get("total_completion_tokens", 0) + usage.get("completion_tokens", 0)
        state["total_tokens"] = state.get("total_tokens", 0) + usage.get("total_tokens", 0)
        state["estimated_cost_usd"] = round(state.get("estimated_cost_usd", 0.0) + usage.get("estimated_cost_usd", 0.0), 6)
        print(f"[Triage Node]: Diagnostic LLM Agent identified {len(diagnostic_reports)} diagnostic item(s).")
    except Exception as triage_err:
        print(f"[Triage Node ERROR]: Diagnostic LLM call failed: {triage_err}")
        # Strictly record the failure; NO deterministic heuristic fallbacks or ground-truth substitutions
        state["verification_errors"] = [f"Triage Diagnostic LLM Exception: {triage_err}"]
        state["diagnostic_reports"] = []
        state["formatted_diagnostic_feedback"] = f"Diagnostic LLM Failure: {triage_err}"
        elapsed = time.time() - start_t
        latencies = state.get("node_latencies", {})
        latencies["triage"] = round(latencies.get("triage", 0.0) + elapsed, 3)
        state["node_latencies"] = latencies
        return state

    # Store structured reports and formatted feedback in state
    dumped_reports = [r.model_dump() for r in diagnostic_reports]
    state["diagnostic_reports"] = dumped_reports
    state["formatted_diagnostic_feedback"] = format_diagnostic_feedback(diagnostic_reports)

    # Accumulate historical reports for evaluation metrics
    hist_reports = state.get("historical_diagnostic_reports", [])
    for dr in dumped_reports:
        if dr not in hist_reports:
            hist_reports.append(dr)
    state["historical_diagnostic_reports"] = hist_reports

    elapsed = time.time() - start_t
    latencies = state.get("node_latencies", {})
    latencies["triage"] = round(latencies.get("triage", 0.0) + elapsed, 3)
    state["node_latencies"] = latencies

    return state
