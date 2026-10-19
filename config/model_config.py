import os
import time
import re
from typing import Type, TypeVar
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

T = TypeVar("T", bound=BaseModel)

# Dedicated LLM Models per KEPS Lifecycle Phase with dynamic .env resolution
def get_phase_model(phase: int = 1) -> str:
    """
    Dynamically reads the dedicated LLM model configured for each KEPS phase from .env.
    Enables empirical research and independent model selection per phase:
    - Phase 1 (Elicitation): Natural language extraction to relational AST schema
    - Phase 3 (Repair): Targeted repair guided by symbolic oracle triage diagnostics
    - Phase 4 (Maintenance): Historical regression and backward compatibility verification
    """
    load_dotenv(override=True)
    if phase == 1:
        val = os.getenv("LLM_PHASE_1", "deepseek/deepseek-chat")
    elif phase == 3:
        val = os.getenv("LLM_PHASE_3", "deepseek/deepseek-chat")
    elif phase == 4:
        val = os.getenv("LLM_PHASE_4", "deepseek/deepseek-chat")
    else:
        val = os.getenv(f"LLM_PHASE_{phase}", "deepseek/deepseek-chat")
    return str(val).strip().strip('"').strip("'")

LLM_MODEL_PHASE_1_ELICITATION = get_phase_model(1)
LLM_MODEL_PHASE_3_REPAIR = get_phase_model(3)
LLM_MODEL_PHASE_4_MAINTENANCE = get_phase_model(4)

import json

def extract_and_parse_json(schema: Type[T], raw_text: str) -> T:
    """Extracts JSON object substring from raw LLM output text and validates against Pydantic schema."""
    text = str(raw_text).strip() if raw_text is not None else ""
    
    if not text:
        raise ValueError(
            "The model returned an empty response. "
            "This usually happens when the model times out, exhausts output tokens during internal reasoning, "
            "or the upstream free-tier endpoint is temporarily congested."
        )
    
    # Strip markdown code fences
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()
    
    # Extract outermost JSON object { ... }
    json_match = re.search(r"(\{.*\})", text, re.DOTALL)
    json_str = json_match.group(1).strip() if json_match else text

    # Direct validation attempt
    try:
        return schema.model_validate_json(json_str)
    except Exception:
        pass

    # Helper function to normalize domain/problem keys
    def _normalize_and_validate(raw_data):
        if not isinstance(raw_data, dict):
            return None
        # Handle $defs or definitions wrappers
        if "$defs" in raw_data and "domain" not in raw_data:
            defs = raw_data["$defs"]
            dom = defs.get("DomainBlueprint") or defs.get("domain") or {}
            prob = defs.get("ProblemBlueprint") or defs.get("problem") or {}
            if dom:
                raw_data = {"domain": dom, "problem": prob}
        elif "definitions" in raw_data and "domain" not in raw_data:
            defs = raw_data["definitions"]
            dom = defs.get("DomainBlueprint") or defs.get("domain") or {}
            prob = defs.get("ProblemBlueprint") or defs.get("problem") or {}
            if dom:
                raw_data = {"domain": dom, "problem": prob}

        schema_fields = getattr(schema, "__fields__", {}) or getattr(schema, "model_fields", {})
        if "domain" in schema_fields and "problem" in schema_fields:
            if "domain" not in raw_data and ("domain_name" in raw_data or "actions" in raw_data):
                domain_name = raw_data.get("domain_name", "generated_domain")
                raw_data = {
                    "domain": raw_data,
                    "problem": {
                        "domain_name": domain_name,
                        "problem_name": f"{domain_name}_prob",
                        "objects": {},
                        "initial_state": [],
                        "goal_state": []
                    }
                }
            elif "domain" in raw_data and "problem" not in raw_data:
                domain_dict = raw_data.get("domain", {})
                domain_name = domain_dict.get("domain_name", "generated_domain") if isinstance(domain_dict, dict) else "generated_domain"
                raw_data["problem"] = {
                    "domain_name": domain_name,
                    "problem_name": f"{domain_name}_prob",
                    "objects": {},
                    "initial_state": [],
                    "goal_state": []
                }
        return schema.model_validate(raw_data)

    # 1. Fast Path: Standard Python json.loads
    try:
        data = json.loads(json_str)
        validated = _normalize_and_validate(data)
        if validated:
            return validated
    except Exception:
        pass

    # 2. Resilient Path: Professional json_repair
    # Automatically fixes unquoted keys, unclosed brackets, and trailing commas
    try:
        import json_repair
        data = json_repair.repair_json(json_str, return_objects=True)
        if isinstance(data, dict):
            validated = _normalize_and_validate(data)
            if validated:
                return validated
    except Exception:
        pass

    # 3. If both fail, raise clear diagnostic error
    snippet = text[:200] if len(text) > 200 else text
    raise ValueError(
        f"Failed to parse LLM output into schema {getattr(schema, '__name__', str(schema))}.\n"
        f"Received: {repr(snippet)}"
    )

def extract_telemetry_from_response(raw_resp) -> dict:
    """Extracts prompt_tokens, completion_tokens, total_tokens and estimates USD cost."""
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0

    if hasattr(raw_resp, "usage_metadata") and raw_resp.usage_metadata:
        um = raw_resp.usage_metadata
        prompt_tokens = um.get("input_tokens", 0) or um.get("prompt_tokens", 0) or 0
        completion_tokens = um.get("output_tokens", 0) or um.get("completion_tokens", 0) or 0
        total_tokens = um.get("total_tokens", 0) or (prompt_tokens + completion_tokens)
    elif hasattr(raw_resp, "response_metadata") and raw_resp.response_metadata:
        rm = raw_resp.response_metadata
        tu = rm.get("token_usage") or rm.get("usage") or {}
        if isinstance(tu, dict):
            prompt_tokens = tu.get("prompt_tokens", 0) or tu.get("input_tokens", 0) or 0
            completion_tokens = tu.get("completion_tokens", 0) or tu.get("output_tokens", 0) or 0
            total_tokens = tu.get("total_tokens", 0) or (prompt_tokens + completion_tokens)

    if total_tokens == 0:
        raw_text = str(raw_resp.content if hasattr(raw_resp, "content") else raw_resp)
        prompt_tokens = max(100, len(raw_text) // 4)
        completion_tokens = max(50, len(raw_text) // 4)
        total_tokens = prompt_tokens + completion_tokens

    cost = (prompt_tokens * 0.00000010) + (completion_tokens * 0.00000040)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(cost, 6)
    }

def invoke_structured_llm(schema: Type[T], prompt: str, target_model: str = None) -> T:
    """Invokes LLM with structured Pydantic schema validation."""
    result, _ = invoke_structured_llm_with_telemetry(schema, prompt, target_model=target_model)
    return result

def invoke_structured_llm_with_telemetry(schema: Type[T], prompt: str, target_model: str = None) -> tuple[T, dict]:
    """
    Invokes OpenRouter with structured Pydantic output AND returns usage telemetry dict (tokens & estimated cost).
    Strictly invokes only the requested model without switching or falling back to other models.
    """
    load_dotenv(override=True)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise RuntimeError("[ALERT] OPENROUTER_API_KEY is missing from your .env file!")

    model_name = target_model or get_phase_model(1)
    if model_name and model_name.endswith(":batch"):
        model_name = model_name[:-6]

    openrouter_max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "8192"))

    schema_json_hint = ""
    if hasattr(schema, "model_json_schema"):
        schema_json_hint = f"\n\nCRITICAL REQUIREMENT: Respond ONLY with a valid JSON object strictly matching this schema. Do not write markdown explanations or conversational text outside the JSON:\n{json.dumps(schema.model_json_schema())}"
    json_prompt = prompt + schema_json_hint

    try:
        print(f"[LLM Provider]: Invoking OpenRouter Model '{model_name}' (max_tokens={openrouter_max_tokens})...")
        llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.0,
            max_tokens=openrouter_max_tokens,
            timeout=120.0,
            max_retries=1
        )
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except Exception:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        raw_resp = llm.invoke(json_prompt)
        telemetry = extract_telemetry_from_response(raw_resp)
        raw_text = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)

        # If content is empty, check reasoning_content, response_metadata or refusal
        if not raw_text or not raw_text.strip():
            ak = getattr(raw_resp, "additional_kwargs", {}) or {}
            rm = getattr(raw_resp, "response_metadata", {}) or {}
            finish_reason = rm.get("finish_reason")
            if ak.get("reasoning_content"):
                raw_text = ak.get("reasoning_content")
            elif ak.get("refusal"):
                raise RuntimeError(f"OpenRouter model '{model_name}' refused the request: {ak.get('refusal')}")
            elif finish_reason == "length":
                raise RuntimeError(
                    f"OpenRouter model '{model_name}' exhausted max_tokens ({openrouter_max_tokens}) during internal reasoning. "
                    f"Please set OPENROUTER_MAX_TOKENS=16384 in your .env file or choose a non-reasoning chat model."
                )

        result = extract_and_parse_json(schema, raw_text)
        print(f"[LLM Provider]: Successfully obtained response from OpenRouter ('{model_name}').")
        return result, telemetry
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "rate limit" in err_msg.lower() or "rate_limit" in err_msg.lower() or "insufficient_quota" in err_msg.lower():
            raise RuntimeError(
                f"[ALERT] RATE / QUOTA LIMIT REACHED for model '{model_name}' on OpenRouter! Execution aborted.\n\n"
                f"Details: {err_msg}\n"
                f"[FIX]: Check your OpenRouter credits or rate limits, or switch provider in your .env file!"
            )
        else:
            raise RuntimeError(f"[ALERT] OpenRouter LLM API Error for Model '{model_name}': {err_msg}")

def invoke_raw_llm_with_telemetry(prompt: str, target_model: str = None) -> tuple[str, dict]:
    """
    Invokes OpenRouter for unstructured/raw string output (used by Zero-Shot and Unstructured-Retry baselines)
    and returns (raw_text, telemetry_dict).
    Strictly invokes only the requested model without switching or falling back to other models.
    """
    load_dotenv(override=True)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        raise RuntimeError("[ALERT] OPENROUTER_API_KEY is missing from your .env file!")

    model_name = target_model or get_phase_model(1)
    if model_name and model_name.endswith(":batch"):
        model_name = model_name[:-6]

    openrouter_max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "8192"))

    try:
        print(f"[LLM Provider]: Invoking OpenRouter (Raw) Model '{model_name}'...")
        llm = ChatOpenAI(
            model_name=model_name,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.0,
            max_tokens=openrouter_max_tokens,
            timeout=90.0,
        )
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except Exception:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        raw_resp = llm.invoke(prompt)
        telemetry = extract_telemetry_from_response(raw_resp)
        raw_text = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
        return raw_text, telemetry
    except Exception as e:
        raise RuntimeError(f"[ALERT] OpenRouter (Raw) LLM API Error for Model '{model_name}': {str(e)}")


