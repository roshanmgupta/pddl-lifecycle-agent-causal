import os
from pydantic import BaseModel
from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from config.model_config import invoke_structured_llm

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
    
    feedback_context = ""
    if formatted_feedback:
        feedback_context = f"\n{formatted_feedback}\nPlease resolve all listed diagnostic issues in your revised blueprint JSON.\n"
        print("Feedback Context for LLM (Triage Format):\n", feedback_context)
    elif verification_errors:
        feedback_context = f"\nPrevious Diagnostic Feedback / Verification Errors to resolve:\n{verification_errors}\n"
        print("Feedback Context for LLM:\n", feedback_context)
        
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
          "robot": "object",
          "location": "object"
        }},
        "predicates": ["(at ?r - robot ?l - location)"],
        "actions": [
          {{
            "action_name": "move",
            "parameters": {{"?r": "robot", "?from": "location", "?to": "location"}},
            "preconditions": ["(at ?r ?from)"],
            "effects": ["(not (at ?r ?from))", "(at ?r ?to)"]
          }}
        ]
      }},
      "problem": {{
        "problem_name": "example_problem",
        "domain_name": "example_domain",
        "objects": {{"r1": "robot", "loc_a": "location", "loc_b": "location"}},
        "initial_state": ["(at r1 loc_a)"],
        "goal_state": ["(at r1 loc_b)"]
      }}
    }}
    ```

    Requirements Text:
    {requirements_text}
    {feedback_context}

    Ensure all object types, predicates, and action parameters use proper variable names starting with '?'.
    The problem's domain_name must exactly match the domain's domain_name.
    Produce ONLY the JSON object and nothing else.
    """
    
    unified_blueprint = invoke_structured_llm(UnifiedBlueprint, prompt)
    
    # Store Relational Blueprint inside Shared Memory State
    state["pddl_domain_blueprint"] = unified_blueprint.domain.model_dump()
    state["pddl_problem_blueprint"] = unified_blueprint.problem.model_dump()
    return state