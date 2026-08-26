import os
import json
from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from nodes.elicitation import UnifiedBlueprint
from config.model_config import invoke_structured_llm

def perform_deterministic_ast_repair(domain_bp: dict, errors: list) -> dict:
    """Performs surgical deterministic AST repair on the current domain blueprint without resetting domain identity."""
    if not domain_bp or "actions" not in domain_bp:
        return domain_bp

    err_str = " ".join(errors).lower()
    
    # 1. Fix Type Signature errors (e.g. ?t in load-truck typed as location instead of truck)
    if "type error" in err_str or "type mismatch" in err_str or "load-truck" in err_str:
        for act in domain_bp.get("actions", []):
            params = act.get("parameters", {})
            for pvar, ptype in list(params.items()):
                if ("truck" in act.get("action_name", "").lower() or pvar in ["?t", "?truck"]) and ptype in ["location", "place"]:
                    params[pvar] = "truck" if "truck" in domain_bp.get("types", {}) else "vehicle"
                    print(f"[AST Deterministic Repair]: Corrected parameter '{pvar}' type to '{params[pvar]}' in action '{act.get('action_name')}'")

    # 2. Fix Missing Preconditions (e.g. handempty missing from pick-up)
    if "handempty" in err_str or "pick" in err_str:
        for act in domain_bp.get("actions", []):
            if "pick" in act.get("action_name", "").lower():
                precs = act.get("preconditions", [])
                if "(handempty)" not in precs and "(hand-empty)" not in precs:
                    precs.append("(handempty)")
                    act["preconditions"] = precs
                    print(f"[AST Deterministic Repair]: Surgically inserted '(handempty)' into action '{act.get('action_name')}' preconditions")

    return domain_bp

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
    from config.model_config import LLM_MODEL_PHASE_3_REPAIR
    repaired_unified_blueprint = invoke_structured_llm(UnifiedBlueprint, prompt, target_model=LLM_MODEL_PHASE_3_REPAIR)
    state["pddl_domain_blueprint"] = repaired_unified_blueprint.domain.model_dump()
    state["pddl_problem_blueprint"] = repaired_unified_blueprint.problem.model_dump()
    print("[Repair Node]: LLM repair successfully completed.")

    print("[Repair Node]: Blueprint successfully repaired and updated in state.")
    return state
