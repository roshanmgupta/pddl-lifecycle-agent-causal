import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.model_config import invoke_structured_llm, LLM_MODEL_PHASE_1_ELICITATION, LLM_MODEL_PHASE_3_REPAIR
from nodes.elicitation import UnifiedBlueprint

print(f"Phase 1 Assigned Model: {LLM_MODEL_PHASE_1_ELICITATION}")
print(f"Phase 3 Assigned Model: {LLM_MODEL_PHASE_3_REPAIR}")

prompt = "We need a simple domain with robot r1 and location l1."

try:
    print("Testing single-model structured LLM invocation...")
    res = invoke_structured_llm(UnifiedBlueprint, prompt, target_model=LLM_MODEL_PHASE_1_ELICITATION)
    print("Invocation Succeeded! Domain Name:", res.domain.domain_name)
except Exception as e:
    print("Caught Exception cleanly as expected:", e)
