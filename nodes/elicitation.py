import os
from pydantic import BaseModel
from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from config.model_config import invoke_structured_llm
from config.pddl_standards import STANDARD_CLASSICAL_PDDL_RULES

class UnifiedBlueprint(BaseModel):
    """A container for both the domain and problem relational blueprints."""
    domain: DomainBlueprint
    problem: ProblemBlueprint

def run_elicitation_node(state: dict) -> dict:
    """
    Phase 1.2 / 2.1 Node: Parses requirements into Relational Blueprint Schema.
    """
    requirements_text = state.get("requirements", "")
    formatted_feedback = state.get("formatted_diagnostic_feedback", "")
    verification_errors = state.get("verification_errors", [])
    existing_domain_bp = state.get("pddl_domain_blueprint")
    existing_problem_bp = state.get("pddl_problem_blueprint")
    
    # Preserve pre-loaded faulty blueprint for synthetic fault repair tasks
    if existing_domain_bp and verification_errors and not formatted_feedback:
        print("[Elicitation Node]: Pre-loaded faulty domain blueprint detected for synthetic repair task. Preserving blueprint for validation & repair loop.")
        return {
            "pddl_domain_blueprint": existing_domain_bp,
            "pddl_problem_blueprint": existing_problem_bp or {}
        }
        
    feedback_context = ""
    if formatted_feedback:
        feedback_context = f"\n{formatted_feedback}\nPlease resolve all listed diagnostic issues in your revised blueprint JSON.\n"
        print("Feedback Context for LLM (Triage Format):\n", feedback_context)
    elif verification_errors:
        feedback_context = f"\nPrevious Diagnostic Feedback / Verification Errors to resolve:\n{verification_errors}\n"
        print("Feedback Context for LLM:\n", feedback_context)
    elif existing_domain_bp and existing_domain_bp.get("actions"):
        import json
        feedback_context = f"\nBaseline / Reference Domain Blueprint to evolve or extend:\n```json\n{json.dumps(existing_domain_bp, indent=2)}\n```\nExtend the domain to satisfy the new requirements while preserving backward compatibility with the existing actions, types, and predicates.\n"
        if existing_problem_bp and existing_problem_bp.get("objects"):
            feedback_context += f"\nBaseline / Reference Problem Blueprint to evolve or adapt:\n```json\n{json.dumps(existing_problem_bp, indent=2)}\n```\nExtend or adapt the problem blueprint to incorporate the evolved capabilities, objects, initial state facts, and goal objectives as specified in the requirements.\n"
        print("[Elicitation Node]: Baseline domain and problem blueprints provided for domain evolution.")
        
    prompt = f"""
    You are an expert PDDL Knowledge Engineer. Your task is to analyze the following requirements text and construct a single, valid JSON object that strictly conforms to the provided schema.
    This JSON object must contain two top-level keys: "domain" and "problem".

    The domain part defines the general rules, types, predicates, and actions.
    The problem part defines the specific objects, initial state, and goal for a scenario.

    Here is an example of the required JSON structure:
    ```json
    {{
      "domain": {{
        "domain_name": "example_domain",
        "requirements": [":strips", ":typing"],
        "types": {{
          "entity_agent": "object",
          "target_element": "object"
        }},
        "constants": {{}},
        "predicates": ["(relational_state ?x - entity_agent ?y - target_element)"],
        "actions": [
          {{
            "action_name": "transition_action",
            "parameters": {{"?x": "entity_agent", "?src": "target_element", "?dst": "target_element"}},
            "preconditions": ["(relational_state ?x ?src)"],
            "effects": ["(not (relational_state ?x ?src))", "(relational_state ?x ?dst)"]
          }}
        ]
      }},
      "problem": {{
        "problem_name": "example_problem",
        "domain_name":  "example_domain",
        "objects": {{"e1": "entity_agent", "t1": "target_element", "t2": "target_element"}},
        "initial_state": ["(relational_state e1 t1)"],
        "goal_state": ["(relational_state e1 t2)"]
      }}
    }}
    ```

    Requirements Text:
    {requirements_text}
    {feedback_context}

    {STANDARD_CLASSICAL_PDDL_RULES}

    Produce ONLY the JSON object and nothing else.
    """
    
    import time
    from config.model_config import get_phase_model, invoke_structured_llm_with_telemetry
    start_t = time.time()
    unified_blueprint, usage = invoke_structured_llm_with_telemetry(UnifiedBlueprint, prompt, target_model=get_phase_model(1))
    elapsed = time.time() - start_t
    
    # Store Relational Blueprint inside Shared Memory State
    state["pddl_domain_blueprint"] = unified_blueprint.domain.model_dump()
    if existing_problem_bp and existing_problem_bp.get("objects") and not state.get("is_evolution_task"):
        print("[Elicitation Node]: Preserving pre-loaded target problem blueprint.")
        preserved_prob = dict(existing_problem_bp)
        preserved_prob["domain_name"] = unified_blueprint.domain.domain_name
        state["pddl_problem_blueprint"] = preserved_prob
    else:
        state["pddl_problem_blueprint"] = unified_blueprint.problem.model_dump()

    # Update Telemetry Metrics
    state["total_prompt_tokens"] = state.get("total_prompt_tokens", 0) + usage.get("prompt_tokens", 0)
    state["total_completion_tokens"] = state.get("total_completion_tokens", 0) + usage.get("completion_tokens", 0)
    state["total_tokens"] = state.get("total_tokens", 0) + usage.get("total_tokens", 0)
    state["estimated_cost_usd"] = round(state.get("estimated_cost_usd", 0.0) + usage.get("estimated_cost_usd", 0.0), 6)
    latencies = state.get("node_latencies", {})
    latencies["elicit"] = round(latencies.get("elicit", 0.0) + elapsed, 3)
    state["node_latencies"] = latencies
    return state