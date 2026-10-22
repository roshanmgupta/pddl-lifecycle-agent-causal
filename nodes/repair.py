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
    iteration = state.get("iteration_count", 0) + 1
    state["iteration_count"] = iteration

    feedback_context = formatted_feedback
    if not feedback_context and verification_errors:
        feedback_context = f"Verification Errors:\n" + "\n".join(verification_errors)

    causal_context = ""
    causal_analysis = state.get("causal_graph_analysis", {})
    if causal_analysis:
        summary = causal_analysis.get("diagnostic_summary", "")
        if summary:
            causal_context = f"\nGROUNDED ACTION-PREDICATE CAUSAL DEPENDENCY & REACHABILITY ANALYSIS:\n{summary}\n"

    history_context = ""
    hist_reports = state.get("historical_diagnostic_reports", [])
    if iteration > 1 and hist_reports:
        recent_history = [
            f"- Previous Attempt Issue: [{r.get('error_category')}] in '{r.get('faulty_element')}': {r.get('suggested_repair_hint')}"
            for r in hist_reports[-3:] if isinstance(r, dict)
        ]
        if recent_history:
            history_context = "\nPREVIOUS FAILED REPAIR ATTEMPTS (DO NOT REVERT OR OSCILLATE):\n" + "\n".join(recent_history) + "\nNote: Do NOT repeat previously rejected modifications or alternate parameter types back and forth. Apply a globally consistent resolution across all actions.\n"

    prompt = f"""
    You are an expert PDDL Knowledge Engineer specializing in formal domain model repair.
    Your task is to repair the existing PDDL Domain and Problem blueprints to resolve the diagnostic errors reported by symbolic oracles.
    Treat the provided blueprints as a working draft to surgically edit, not as disposable context.
    Preserve all elements that are already correct and apply the smallest set of changes needed to satisfy oracle feedback.

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
    {causal_context}
    {history_context}

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
