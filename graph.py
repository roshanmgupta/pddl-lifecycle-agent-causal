import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from nodes.elicitation import run_elicitation_node
from nodes.generation import run_generation_node
from nodes.triage import run_triage_node
from nodes.repair import run_repair_node
from nodes.maintenance import run_maintenance_node
from tools.symbolic_oracles import run_val_validator, run_fast_downward

# 1. Shared Memory AgentState Contract
class AgentState(TypedDict, total=False):
    requirements: str
    pddl_domain_blueprint: dict
    pddl_problem_blueprint: dict
    initial_pddl_domain_blueprint: dict
    generated_domain_pddl: str
    generated_problem_pddl: str
    initial_domain_pddl: str
    initial_problem_pddl: str
    is_evolution_task: bool
    is_synthetic_repair: bool
    skip_elicitation: bool
    skip_triage: bool
    system_type: str
    verification_errors: List[str]
    initial_verification_errors: List[str]
    diagnostic_reports: List[dict]
    historical_diagnostic_reports: List[dict]
    formatted_diagnostic_feedback: str
    historical_regression_suite: List[dict]
    iteration_count: int
    max_iterations: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    node_latencies: dict
    generated_plan_result: dict
    historical_plan_results: List[dict]
    causal_graph_analysis: dict

# 2. Validation Oracle Execution Node
def run_full_validation_node(state: AgentState) -> AgentState:
    import time
    start_t = time.time()
    pddl_code = state.get("generated_domain_pddl", "")
    if not pddl_code and state.get("initial_domain_pddl"):
        pddl_code = state.get("initial_domain_pddl", "")
        state["generated_domain_pddl"] = pddl_code

    problem_pddl_code = state.get("generated_problem_pddl")
    if not problem_pddl_code and state.get("initial_problem_pddl"):
        problem_pddl_code = state.get("initial_problem_pddl", "")
        state["generated_problem_pddl"] = problem_pddl_code
    
    # Ensure AST blueprints exist for triage & repair
    if not state.get("pddl_domain_blueprint") and pddl_code:
        from tools.blueprint_parser import parse_pddl_domain_to_blueprint
        state["pddl_domain_blueprint"] = parse_pddl_domain_to_blueprint(pddl_code)
    if not state.get("pddl_problem_blueprint") and problem_pddl_code:
        from tools.blueprint_parser import parse_pddl_problem_to_blueprint
        state["pddl_problem_blueprint"] = parse_pddl_problem_to_blueprint(problem_pddl_code)

    # Save temporary domain file to disk
    from config.paths import get_temp_domain_path, get_temp_problem_path
    temp_domain_file = get_temp_domain_path()
    with open(temp_domain_file, "w", encoding="utf-8") as f:
        f.write(pddl_code)
        
    temp_problem_file = None
    if problem_pddl_code:
        temp_problem_file = get_temp_problem_path()
        with open(temp_problem_file, "w", encoding="utf-8") as f:
            f.write(problem_pddl_code)

    # -- Oracle 1: VAL for Syntax/Semantic Check --
    is_valid_syntax, val_log = run_val_validator(temp_domain_file, temp_problem_file)
    
    if not is_valid_syntax:
        err_msg = "VAL Error: " + val_log
        state["verification_errors"] = [err_msg]
        if not state.get("initial_verification_errors"):
            state["initial_verification_errors"] = [err_msg]
        latencies = state.get("node_latencies", {})
        latencies["validate"] = round(latencies.get("validate", 0.0) + (time.time() - start_t), 3)
        state["node_latencies"] = latencies
        return state

    # -- Oracle 2: Fast Downward for Solvability Check & Plan Synthesis --
    if temp_problem_file:
        from tools.symbolic_oracles import run_fast_downward_with_plan
        plan_res = run_fast_downward_with_plan(temp_domain_file, temp_problem_file)
        state["generated_plan_result"] = plan_res
        
        if not plan_res["is_solvable"]:
            fd_log = plan_res.get("raw_fd_log", "")
            err_msg = "Planner Error: Could not find a plan. " + fd_log
            state["verification_errors"] = [err_msg]
            if not state.get("initial_verification_errors"):
                state["initial_verification_errors"] = [err_msg]
            latencies = state.get("node_latencies", {})
            latencies["validate"] = round(latencies.get("validate", 0.0) + (time.time() - start_t), 3)
            state["node_latencies"] = latencies
            return state

    # If both oracles pass, clear current active errors and diagnostic reports (historical reports remain preserved in historical_diagnostic_reports)
    state["verification_errors"] = []
    state["diagnostic_reports"] = []
    state["formatted_diagnostic_feedback"] = ""
    latencies = state.get("node_latencies", {})
    latencies["validate"] = round(latencies.get("validate", 0.0) + (time.time() - start_t), 3)
    state["node_latencies"] = latencies
    return state

MAX_ITERATIONS_DEFAULT = 5

# 3. Router Functions for Closed Loop Workflow
def route_after_validation(state: AgentState) -> str:
    """If primary validation fails, route directly to triage. If validation passes and regression suite is present, route to maintenance; else complete at END."""
    errors = state.get("verification_errors", [])
    if errors:
        return "triage"
    suite = state.get("historical_regression_suite", [])
    if suite:
        return "maintenance"
    print("[SUCCESS]: Model successfully verified by Oracles (VAL & Fast Downward)!")
    return END

def route_after_maintenance(state: AgentState) -> str:
    """If Phase 4 maintenance detected regression breakages, route to triage. Otherwise, complete successfully."""
    errors = state.get("verification_errors", [])
    if errors:
        return "triage"
    print("[SUCCESS]: Model successfully verified by Oracles & Phase 4 Maintenance Suite!")
    return END

def route_after_triage(state: AgentState) -> str:
    """Gatekeeper router after triage node."""
    errors = state.get("verification_errors", [])
    reports = state.get("diagnostic_reports", [])
    
    if not errors and not reports:
        print("[SUCCESS]: Model successfully verified by Oracles & Phase 4 Maintenance Suite!")
        return END           # Validation & Maintenance passed!

    # Guard: Halt only if the oracle binary itself is missing on the host OS (not an AST issue miscategorized by LLM)
    is_true_binary_failure = any(
        isinstance(r, dict)
        and (r.get("error_category") == "SYSTEM_ORACLE_ERROR" or str(r.get("error_category")).endswith("SYSTEM_ORACLE_ERROR"))
        and (
            r.get("faulty_element") in ["VAL Oracle Binary", "Fast Downward Binary"]
            or any(k in str(r.get("raw_log", "")).lower() for k in ["binary not found", "executable not found", "cannot find the file specified", "failed to execute val binary", "failed to execute fast downward"])
        )
        for r in reports
    )
    if is_true_binary_failure:
        print("[CRITICAL HALT]: System Oracle executable binary missing on host. Halting repair loop.")
        return END
        
    current_iteration = state.get("iteration_count", 0)
    max_iters = state.get("max_iterations", MAX_ITERATIONS_DEFAULT)
    
    if current_iteration >= max_iters:
        print(f"[WARNING]: Max repair iterations ({max_iters}) reached ({current_iteration}/{max_iters}). Terminating repair loop.")
        return END           # Max iteration guard triggered
        
    print(f"[ROUTER]: Routing to repair node (Next Repair Iteration: {current_iteration + 1}/{max_iters})")
    return "repair"          # Loop to repair node for targeted AST modification

def route_initial_entry(state: AgentState) -> str:
    """
    If a flawed domain or pre-existing domain PDDL is already provided
    (e.g. Category B Synthetic Fault Repair), bypass Phase 1 Elicitation & Generation entirely,
    routing directly to Phase 2 Validation -> Phase 3 Triage & Repair.
    """
    if (
        state.get("is_synthetic_repair")
        or state.get("skip_elicitation")
        or (
            state.get("generated_domain_pddl")
            and not state.get("is_evolution_task")
            and (state.get("verification_errors") or not state.get("requirements"))
        )
        or (state.get("generated_domain_pddl") and state.get("pddl_domain_blueprint") and not state.get("is_evolution_task"))
    ):
        print("[GRAPH ROUTER]: Pre-loaded domain detected for Repair. Bypassing Phase 1 Elicitation -> Starting at Validation.")
        return "validate"
    return "elicit"

# 4. Construct LangGraph Workflow
builder = StateGraph(AgentState)

builder.add_node("elicit", run_elicitation_node)
builder.add_node("generate", run_generation_node)
builder.add_node("validate", run_full_validation_node)
builder.add_node("maintenance", run_maintenance_node)
builder.add_node("triage", run_triage_node)
builder.add_node("repair", run_repair_node)

builder.set_conditional_entry_point(
    route_initial_entry,
    {
        "elicit": "elicit",
        "validate": "validate"
    }
)
builder.add_edge("elicit", "generate")
builder.add_edge("generate", "validate")
builder.add_conditional_edges("validate", route_after_validation)
builder.add_conditional_edges("maintenance", route_after_maintenance)
builder.add_conditional_edges("triage", route_after_triage)
builder.add_edge("repair", "generate")

pddl_lifecycle_graph = builder.compile()