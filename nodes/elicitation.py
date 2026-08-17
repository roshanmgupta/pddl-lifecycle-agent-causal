import os
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint

class UnifiedBlueprint(BaseModel):
    """A container for both the domain and problem relational blueprints."""
    domain: DomainBlueprint
    problem: ProblemBlueprint

def run_elicitation_node(state: dict) -> dict:
    """
    Phase 1.2 / 2.1 Node: Parses requirements into Relational Blueprint Schema
    using OpenRouter Free Tier.
    """
    requirements_text = state.get("requirements", "")
    verification_errors = state.get("verification_errors", [])
    
    # Configure OpenRouter Free Model (e.g. Gemini 2.0 Flash Free)
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")
    
    llm = ChatOpenAI(
        model_name="google/gemma-4-26b-a4b-it:free",  # Free OpenRouter model
        openai_api_key=openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0,
        max_retries=5
    )
    
    # Enforce structured output parsing matching DomainBlueprint schema
    structured_llm = llm.with_structured_output(UnifiedBlueprint)
    
    feedback_context = ""
    if verification_errors:
        feedback_context = f"\nPrevious Diagnostic Feedback / Verification Errors to resolve:\n{verification_errors}\n"
        print("Feedback Context for LLM:", feedback_context)
        
    prompt = f"""
    You are an expert PDDL Knowledge Engineer. Analyze the following domain requirement text 
    and construct a valid, unified JSON object containing both the domain and problem blueprints.

    The domain part defines the general rules, types, predicates, and actions.
    The problem part defines the specific objects, initial state, and goal for a scenario.
    
    Requirements Text:
    {requirements_text}
    {feedback_context}
    Ensure all object types, predicates, and action parameters use proper variable names starting with '?'.
    The problem's domain_name must exactly match the domain's domain_name.
    """
    
    unified_blueprint = structured_llm.invoke(prompt)
    
    # Store Relational Blueprint inside Shared Memory State
    state["pddl_domain_blueprint"] = unified_blueprint.domain.model_dump()
    state["pddl_problem_blueprint"] = unified_blueprint.problem.model_dump()
    return state