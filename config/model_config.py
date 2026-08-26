import os
import time
import re
from typing import Type, TypeVar
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

T = TypeVar("T", bound=BaseModel)

# FALLBACK_MODEL_LIST = [
#     "openrouter/free",
#     "google/gemma-4-26b-a4b-it:free",
#     "google/gemma-4-31b-it:free",
#     "nvidia/nemotron-3-nano-30b-a3b:free",
#     "liquid/lfm-2.5-2.6b:free"
# ]

# Dedicated LLM Models per KEPS Lifecycle Phase
LLM_MODEL_PHASE_1_ELICITATION = os.getenv("LLM_PHASE_1", "openrouter/free")
LLM_MODEL_PHASE_3_REPAIR = os.getenv("LLM_PHASE_3", "openrouter/free")
LLM_MODEL_PHASE_4_MAINTENANCE = os.getenv("LLM_PHASE_4", "openrouter/free")

def extract_and_parse_json(schema: Type[T], raw_text: str) -> T:
    """Extracts JSON object substring from raw LLM output text and validates against Pydantic schema."""
    text = str(raw_text).strip()
    
    # Strip markdown code fences
    text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"```$", "", text, flags=re.MULTILINE).strip()
    
    # Extract outermost JSON object { ... }
    json_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            return schema.model_validate_json(json_str)
        except Exception:
            pass
            
    # Try direct validation
    return schema.model_validate_json(text)

def invoke_structured_llm(schema: Type[T], prompt: str, target_model: str = None) -> T:
    """
    Invokes the selected LLM provider (Groq, OpenRouter, or Gemini) with structured Pydantic output.
    Forces override=True to dynamically detect any changes made to .env without restarting.
    """
    load_dotenv(override=True)
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("Groq_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    # Determine effective provider strictly
    if provider == "groq":
        effective_provider = "groq"
    elif provider == "openrouter":
        effective_provider = "openrouter"
    elif provider == "gemini":
        effective_provider = "gemini"
    else:
        # Default auto-detection precedence if LLM_PROVIDER is omitted in .env
        if groq_api_key:
            effective_provider = "groq"
        elif openrouter_api_key:
            effective_provider = "openrouter"
        elif gemini_api_key:
            effective_provider = "gemini"
        else:
            raise RuntimeError("[ALERT] No LLM API Keys Found in .env file.")

    print(f"[LLM Config]: Active Provider selected -> '{effective_provider.upper()}'")

    # 1. Groq Execution
    if effective_provider == "groq":
        if not groq_api_key:
            raise RuntimeError("[ALERT] LLM_PROVIDER is set to 'groq' but no GROQ_API_KEY was found in your .env file!")
        
        # Production active models on Groq
        groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        last_err = None
        for g_model in groq_models:
            try:
                print(f"[LLM Provider]: Invoking Groq API ('{g_model}')...")
                llm = ChatOpenAI(
                    model_name=g_model,
                    openai_api_key=groq_api_key,
                    openai_api_base="https://api.groq.com/openai/v1",
                    temperature=0.0,
                    max_retries=1
                )
                try:
                    structured_llm = llm.with_structured_output(schema)
                    result = structured_llm.invoke(prompt)
                    print(f"[LLM Provider]: Successfully obtained response from Groq ('{g_model}').")
                    return result
                except Exception as parse_err:
                    err_str = str(parse_err)
                    if "json" in err_str.lower() or "validation" in err_str.lower() or "expected value" in err_str.lower():
                        print(f"[LLM Provider]: Groq structured parse warning ({err_str[:60]}...). Running JSON extraction fallback...")
                        raw_resp = llm.invoke(prompt)
                        raw_text = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                        result = extract_and_parse_json(schema, raw_text)
                        print(f"[LLM Provider]: Successfully extracted JSON from Groq response.")
                        return result
                    else:
                        raise parse_err
            except Exception as e:
                last_err = e
                err_msg = str(e)
                if "decommissioned" in err_msg.lower() or "not found" in err_msg.lower() or "404" in err_msg:
                    print(f"[LLM Provider Warning]: Groq model '{g_model}' unavailable ({err_msg[:60]}...). Trying next Groq model...")
                    continue
                if "rate_limit" in err_msg.lower() or "429" in err_msg or "token" in err_msg.lower():
                    raise RuntimeError(f"[ALERT] TOKEN LIMIT REACHED on Groq! Execution aborted.\nDetails: {err_msg}")
                print(f"[LLM Provider Warning]: Groq model '{g_model}' failed ({err_msg[:80]}). Trying next Groq model...")

        raise RuntimeError(f"[ALERT] Groq API Error: All Groq models failed ({last_err}). Please check your Groq API key in .env at https://console.groq.com/keys")

    # 2. OpenRouter Execution
    elif effective_provider == "openrouter":
        if not openrouter_api_key:
            raise RuntimeError("[ALERT] LLM_PROVIDER is set to 'openrouter' but no OPENROUTER_API_KEY was found in your .env file!")
        
        model_name = target_model or LLM_MODEL_PHASE_1_ELICITATION
        try:
            print(f"[LLM Provider]: Invoking OpenRouter Model '{model_name}'...")
            llm = ChatOpenAI(
                model_name=model_name,
                openai_api_key=openrouter_api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0.0,
                max_retries=1
            )
            try:
                structured_llm = llm.with_structured_output(schema)
                result = structured_llm.invoke(prompt)
                print(f"[LLM Provider]: Successfully obtained response from OpenRouter ('{model_name}').")
                return result
            except Exception as parse_err:
                err_str = str(parse_err)
                if "length limit" in err_str.lower() or "token" in err_str.lower():
                    raise RuntimeError(
                        f"[ALERT] TOKEN LIMIT REACHED for model '{model_name}' on OpenRouter! Execution aborted.\n\n"
                        f"👉 TO FIX: Change 'LLM_PROVIDER=groq' or 'LLM_PROVIDER=gemini' in your .env file!"
                    )
                elif "json" in err_str.lower() or "validation" in err_str.lower() or "expected value" in err_str.lower() or "user safety" in err_str.lower():
                    print(f"[LLM Provider]: Structured parsing encountered non-JSON preamble ({err_str[:60]}...). Running robust JSON extraction fallback...")
                    raw_resp = llm.invoke(prompt)
                    raw_text = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                    result = extract_and_parse_json(schema, raw_text)
                    print(f"[LLM Provider]: Successfully extracted and validated JSON from OpenRouter response.")
                    return result
                else:
                    raise parse_err
        except Exception as e:
            err_msg = str(e)
            if "length limit" in err_msg.lower() or "token" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                raise RuntimeError(
                    f"[ALERT] TOKEN LIMIT REACHED for model '{model_name}' on OpenRouter! Execution aborted.\n\n"
                    f"👉 TO FIX: Change 'LLM_PROVIDER=groq' or 'LLM_PROVIDER=gemini' in your .env file!"
                )
            else:
                raise RuntimeError(f"[ALERT] OpenRouter LLM API Error for Model '{model_name}': {err_msg}")

    # 3. Google Gemini API Execution
    elif effective_provider == "gemini":
        if not gemini_api_key:
            raise RuntimeError("[ALERT] LLM_PROVIDER is set to 'gemini' but no GEMINI_API_KEY (or GOOGLE_API_KEY) was found in your .env file!")

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            gemini_models = [
                os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-3.6-flash"
            ]
            last_err = None
            for g_model in gemini_models:
                try:
                    print(f"[LLM Provider]: Invoking Google Gemini API ('{g_model}')...")
                    gemini_llm = ChatGoogleGenerativeAI(
                        model=g_model,
                        google_api_key=gemini_api_key,
                        temperature=0.0,
                        timeout=30.0
                    )
                    
                    schema_json_hint = ""
                    if hasattr(schema, "model_json_schema"):
                        schema_json_hint = f"\n\nRespond ONLY with a valid JSON object matching this schema:\n{schema.model_json_schema()}"
                    
                    json_prompt = prompt + schema_json_hint
                    raw_resp = gemini_llm.invoke(json_prompt)
                    raw_content = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)
                    if isinstance(raw_content, list):
                        raw_text = "".join([b.get("text", "") if isinstance(b, dict) else str(b) for b in raw_content])
                    else:
                        raw_text = str(raw_content)

                    result = extract_and_parse_json(schema, raw_text)
                    print(f"[LLM Provider]: Successfully obtained and validated response from Google Gemini API ('{g_model}').")
                    return result
                except Exception as e:
                    last_err = e
                    err_msg = str(e)
                    if any(k in err_msg.lower() for k in ["not_found", "404", "no longer available", "resource_exhausted", "429", "quota"]):
                        print(f"[LLM Provider Warning]: Gemini model '{g_model}' rate-limited/unavailable ({err_msg[:60]}...). Automatic fallback to next available model...")
                        continue
                    raise RuntimeError(f"[ALERT] Google Gemini API Error for Model '{g_model}': {err_msg}")

            raise RuntimeError(f"[ALERT] Google Gemini API Error: All Gemini models failed ({last_err}). Please verify your GEMINI_API_KEY at https://aistudio.google.com/")
        except ImportError:
            raise RuntimeError("[ALERT] Package 'langchain-google-genai' is missing. Please run: pip install langchain-google-genai")
        except Exception as e:
            raise RuntimeError(f"[ALERT] Google Gemini API Error: {str(e)}")

    else:
        raise RuntimeError("[ALERT] No LLM API Keys Found. Please configure GROQ_API_KEY, OPENROUTER_API_KEY, or GEMINI_API_KEY in your .env file.")
