import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from nodes.elicitation import run_elicitation_node
from nodes.generation import run_generation_node
from tools.symbolic_oracles import run_val_validator

# 1. Memory Stream Shared State
class AgentState(TypedDict, total=False):
    requirements: str
    pddl_domain_blueprint: dict
    pddl_problem_blueprint: dict
    generated_domain_pddl: str
    generated_problem_pddl: str
    verification_errors: List[str]

# 2. Validation Oracle Execution Node
def run_validation_node(state: AgentState) -> AgentState:
    pddl_code = state.get("generated_domain_pddl", "")
    
    # Save temporary domain file to disk
    temp_domain_file = "temp_domain.pddl"
    with open(temp_domain_file, "w") as f:
        f.write(pddl_code)
        
    problem_pddl_code = state.get("generated_problem_pddl")
    temp_problem_file = None
    if problem_pddl_code:
        temp_problem_file = "temp_problem.pddl"
        with open(temp_problem_file, "w") as f:
            f.write(problem_pddl_code)

    # Execute VAL syntax oracle
    is_valid, log_output = run_val_validator(temp_domain_file, temp_problem_file)
    
    if not is_valid and "not found" not in log_output:
        state["verification_errors"] = [log_output]
    else:
        state["verification_errors"] = []
        
    return state

# 3. Router Function for Closed Loop
def route_after_validation(state: AgentState) -> str:
    if state.get("verification_errors"):
        return "elicit"  # Loop back to elicitation node to fix relational schema
    return END           # Validation passed!

# 4. Construct LangGraph Workflow
builder = StateGraph(AgentState)

builder.add_node("elicit", run_elicitation_node)
builder.add_node("generate", run_generation_node)
builder.add_node("validate", run_validation_node)

builder.set_entry_point("elicit")
builder.add_edge("elicit", "generate")
builder.add_edge("generate", "validate")
builder.add_conditional_edges("validate", route_after_validation)

pddl_lifecycle_graph = builder.compile()