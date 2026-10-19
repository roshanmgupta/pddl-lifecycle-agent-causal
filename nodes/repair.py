import os
import json
import time
from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint
from nodes.elicitation import UnifiedBlueprint
from config.pddl_standards import STANDARD_CLASSICAL_PDDL_RULES, STANDARD_REPAIR_RULES
from config.model_config import get_phase_model, invoke_structured_llm_with_telemetry

def run_repair_node(state: dict) -> dict:
    """
    Phase 3.2 Repair Node: Performs targeted repair on existing domain and problem blueprints
    based on diagnostic reports from the triage node.
    100% LLM-driven reasoning; strictly NO deterministic heuristic fallbacks or ground-truth substitutions.
    """
    requirements_text = state.get("requirements", "")
    domain_blueprint = state.get("pddl_domain_blueprint", {})
    problem_blueprint = state.get("pddl_problem_blueprint", {})
    formatted_feedback = state.get("formatted_diagnostic_feedback", "")
    verification_errors = state.get("verification_errors", [])
    state["iteration_count"] = state.get("iteration_count", 0) + 1

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

    {STANDARD_CLASSICAL_PDDL_RULES}
    {STANDARD_REPAIR_RULES}

    Produce ONLY the updated valid JSON object conforming to the UnifiedBlueprint schema.
    """

    print("[Repair Node]: Executing 100% LLM-driven blueprint repair based on diagnostic feedback...")
    start_t = time.time()
    
    try:
        repaired_unified_blueprint, usage = invoke_structured_llm_with_telemetry(
            UnifiedBlueprint, 
            prompt, 
            target_model=get_phase_model(3)
        )
        state["pddl_domain_blueprint"] = repaired_unified_blueprint.domain.model_dump()
        state["pddl_problem_blueprint"] = repaired_unified_blueprint.problem.model_dump()

        # Update Telemetry Metrics
        state["total_prompt_tokens"] = state.get("total_prompt_tokens", 0) + usage.get("prompt_tokens", 0)
        state["total_completion_tokens"] = state.get("total_completion_tokens", 0) + usage.get("completion_tokens", 0)
        state["total_tokens"] = state.get("total_tokens", 0) + usage.get("total_tokens", 0)
        state["estimated_cost_usd"] = round(state.get("estimated_cost_usd", 0.0) + usage.get("estimated_cost_usd", 0.0), 6)
        print("[Repair Node]: LLM repair successfully completed.")
    except Exception as llm_err:
        print(f"[Repair Node ERROR]: LLM structured repair invocation failed: {llm_err}")
        # Strictly record the failure; NO deterministic fallbacks or ground-truth injection
        state["verification_errors"] = [f"Repair LLM Exception: {llm_err}"]

    elapsed = time.time() - start_t
    latencies = state.get("node_latencies", {})
    latencies["repair"] = round(latencies.get("repair", 0.0) + elapsed, 3)
    state["node_latencies"] = latencies

    print("[Repair Node]: Blueprint updated in state.")
    return state
