import os
import json
from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from nodes.elicitation import UnifiedBlueprint
from config.model_config import invoke_structured_llm

def run_repair_node(state: dict) -> dict:
    """
    Phase 3.2 Repair Node: Performs targeted repair on existing domain and problem blueprints
    based on diagnostic reports from the triage node.
    """
    requirements_text = state.get("requirements", "")
    domain_blueprint = state.get("pddl_domain_blueprint", {})
    problem_blueprint = state.get("pddl_problem_blueprint", {})
    formatted_feedback = state.get("formatted_diagnostic_feedback", "")
    verification_errors = state.get("verification_errors", [])

    # Format feedback context
    feedback_context = formatted_feedback
    if not feedback_context and verification_errors:
        feedback_context = f"Verification Errors:\n" + "\n".join(verification_errors)

    prompt = f"""
    You are an expert PDDL Knowledge Engineer specializing in formal domain model repair.
    Your task is to repair the existing PDDL Domain and Problem blueprints to resolve the diagnostic errors reported by symbolic oracles.

    Original Requirements Text:
    {requirements_text}

    CURRENT DOMAIN BLUEPRINT:
    ```json
    {json.dumps(domain_blueprint, indent=2)}
    ```

    CURRENT PROBLEM BLUEPRINT:
    ```json
    {json.dumps(problem_blueprint, indent=2)}
    ```

    {feedback_context}

    REPAIR INSTRUCTIONS & GUIDELINES:
    1. TARGETED REPAIR: Do NOT re-extract everything from scratch or remove valid existing actions, predicates, or types unless required.
    2. FIX DIAGNOSED FAULTS: 
       - If there are [TYPE_SIGNATURE] or missing predicate errors: Add missing predicates to 'predicates' or fix parameter type annotations.
       - If there are [SYNTAX_PARSE] errors: Fix malformed expressions, unclosed parens, or parameter names.
       - If there are [GROUNDING_UNSOLVABILITY] errors: Check action preconditions (ensure they aren't overly restrictive), add missing effects, or add required initial state facts to the problem blueprint.
    3. Ensure all variable names in predicates and action parameters start with '?'.
    4. Ensure problem.domain_name matches domain.domain_name exactly.

    Produce ONLY the updated valid JSON object conforming to the UnifiedBlueprint schema.
    """

    print("[Repair Node]: Executing targeted blueprint repair based on diagnostic feedback...")
    repaired_unified_blueprint = invoke_structured_llm(UnifiedBlueprint, prompt)

    # Store updated blueprints back into shared state
    state["pddl_domain_blueprint"] = repaired_unified_blueprint.domain.model_dump()
    state["pddl_problem_blueprint"] = repaired_unified_blueprint.problem.model_dump()

    print("[Repair Node]: Blueprint successfully repaired and updated in state.")
    return state
