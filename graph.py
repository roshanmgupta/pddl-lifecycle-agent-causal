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
    verification_errors: List[str]
    initial_verification_errors: List[str]
    diagnostic_reports: List[dict]
    historical_diagnostic_reports: List[dict]
    formatted_diagnostic_feedback: str
    historical_regression_suite: List[dict]
    iteration_count: int
    max_iterations: int

# 2. Validation Oracle Execution Node
def run_full_validation_node(state: AgentState) -> AgentState:
    pddl_code = state.get("generated_domain_pddl", "")
    
    os.makedirs("PDDL_file", exist_ok=True)
    
    # Save temporary domain file to disk
    temp_domain_file = "PDDL_file/temp_domain_2.pddl"
    with open(temp_domain_file, "w", encoding="utf-8") as f:
        f.write(pddl_code)
        
    problem_pddl_code = state.get("generated_problem_pddl")
    temp_problem_file = None
    if problem_pddl_code:
        temp_problem_file = "PDDL_file/temp_problem_2.pddl"
        with open(temp_problem_file, "w", encoding="utf-8") as f:
            f.write(problem_pddl_code)

    # -- Oracle 1: VAL for Syntax/Semantic Check --
    is_valid_syntax, val_log = run_val_validator(temp_domain_file, temp_problem_file)
    
    if not is_valid_syntax:
        if "not found" not in val_log.lower(): # Ignore if binary tool is missing
            err_msg = "VAL Error: " + val_log
            state["verification_errors"] = [err_msg]
            if not state.get("initial_verification_errors"):
                state["initial_verification_errors"] = [err_msg]
        return state

    # -- Oracle 2: Fast Downward for Solvability Check --
    if temp_problem_file:
        plan_found, fd_log = run_fast_downward(temp_domain_file, temp_problem_file)
        if not plan_found:
            if "not found" not in fd_log.lower(): # Ignore if binary tool is missing
                err_msg = "Planner Error: Could not find a plan. " + fd_log
                state["verification_errors"] = [err_msg]
                if not state.get("initial_verification_errors"):
                    state["initial_verification_errors"] = [err_msg]
            return state

    # If both oracles pass, clear current active errors and diagnostic reports (historical reports remain preserved in historical_diagnostic_reports)
    state["verification_errors"] = []
    state["diagnostic_reports"] = []
    state["formatted_diagnostic_feedback"] = ""
    return state

MAX_ITERATIONS_DEFAULT = 5

# 3. Router Functions for Closed Loop Workflow
def route_after_validation(state: AgentState) -> str:
    """If primary validation fails, route directly to triage. If validation passes, route to Phase 4 maintenance."""
    errors = state.get("verification_errors", [])
    if errors:
        return "triage"
    return "maintenance"

def route_after_triage(state: AgentState) -> str:
    """Gatekeeper router after triage node."""
    errors = state.get("verification_errors", [])
    reports = state.get("diagnostic_reports", [])
    
    if not errors and not reports:
        print("[SUCCESS]: Model successfully verified by Oracles & Phase 4 Maintenance Suite!")
        return END           # Validation & Maintenance passed!
        
    current_iteration = state.get("iteration_count", 0) + 1
    state["iteration_count"] = current_iteration
    max_iters = state.get("max_iterations", MAX_ITERATIONS_DEFAULT)
    
    if current_iteration >= max_iters:
        print(f"[WARNING]: Max repair iterations ({max_iters}) reached. Terminating repair loop.")
        return END           # Max iteration guard triggered
        
    print(f"[ROUTER]: Routing to repair node (Iteration {current_iteration}/{max_iters})")
    return "repair"          # Loop to repair node for targeted AST modification

# 4. Construct LangGraph Workflow
builder = StateGraph(AgentState)

builder.add_node("elicit", run_elicitation_node)
builder.add_node("generate", run_generation_node)
builder.add_node("validate", run_full_validation_node)
builder.add_node("maintenance", run_maintenance_node)
builder.add_node("triage", run_triage_node)
builder.add_node("repair", run_repair_node)

builder.set_entry_point("elicit")
builder.add_edge("elicit", "generate")
builder.add_edge("generate", "validate")
builder.add_conditional_edges("validate", route_after_validation)
builder.add_edge("maintenance", "triage")
builder.add_conditional_edges("triage", route_after_triage)
builder.add_edge("repair", "generate")

pddl_lifecycle_graph = builder.compile()