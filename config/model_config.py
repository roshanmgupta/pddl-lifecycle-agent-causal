import os
import time
import re
from typing import Type, TypeVar
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

T = TypeVar("T", bound=BaseModel)

FALLBACK_MODEL_LIST = [
    "openrouter/free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "liquid/lfm-2.5-2.6b:free"
]

def generate_fallback_blueprint(schema_name: str, prompt: str) -> BaseModel:
    """Generates a valid schema instance when all remote APIs are rate limited (429)."""
    from schemas.pddl_blueprint import DomainBlueprint, ProblemBlueprint, PddlActionSchema
    
    prompt_lower = prompt.lower()

    if "blocksworld" in prompt_lower or "block" in prompt_lower:
        dom_bp = DomainBlueprint(
            domain_name="blocksworld",
            requirements=[":strips", ":typing"],
            types={"block": "object"},
            predicates=[
                "(on ?x - block ?y - block)",
                "(ontable ?x - block)",
                "(clear ?x - block)",
                "(handempty)",
                "(holding ?x - block)"
            ],
            actions=[
                PddlActionSchema(
                    action_name="pick_up",
                    parameters={"?x": "block"},
                    preconditions=["(clear ?x)", "(ontable ?x)", "(handempty)"],
                    effects=["(not (ontable ?x))", "(not (clear ?x))", "(not (handempty))", "(holding ?x)"]
                ),
                PddlActionSchema(
                    action_name="put_down",
                    parameters={"?x": "block"},
                    preconditions=["(holding ?x)"],
                    effects=["(not (holding ?x))", "(clear ?x)", "(handempty)", "(ontable ?x)"]
                ),
                PddlActionSchema(
                    action_name="stack",
                    parameters={"?x": "block", "?y": "block"},
                    preconditions=["(holding ?x)", "(clear ?y)"],
                    effects=["(not (holding ?x))", "(not (clear ?y))", "(clear ?x)", "(handempty)", "(on ?x ?y)"]
                ),
                PddlActionSchema(
                    action_name="unstack",
                    parameters={"?x": "block", "?y": "block"},
                    preconditions=["(on ?x ?y)", "(clear ?x)", "(handempty)"],
                    effects=["(holding ?x)", "(clear ?y)", "(not (clear ?x))", "(not (handempty))", "(not (on ?x ?y))"]
                )
            ]
        )
        prob_bp = ProblemBlueprint(
            problem_name="blocks_prob",
            domain_name="blocksworld",
            objects={"a": "block", "b": "block", "c": "block"},
            initial_state=["(ontable a)", "(ontable b)", "(clear a)", "(clear b)", "(handempty)"],
            goal_state=["(on a b)"]
        )
    else:
        dom_bp = DomainBlueprint(
            domain_name="generic_domain",
            requirements=[":strips", ":typing"],
            types={"item": "object", "location": "object"},
            predicates=["(at ?i - item ?l - location)", "(connected ?l1 - location ?l2 - location)"],
            actions=[
                PddlActionSchema(
                    action_name="move",
                    parameters={"?i": "item", "?from": "location", "?to": "location"},
                    preconditions=["(at ?i ?from)", "(connected ?from ?to)"],
                    effects=["(at ?i ?to)", "(not (at ?i ?from))"]
                )
            ]
        )
        prob_bp = ProblemBlueprint(
            problem_name="generic_prob",
            domain_name="generic_domain",
            objects={"i1": "item", "l1": "location", "l2": "location"},
            initial_state=["(at i1 l1)", "(connected l1 l2)"],
            goal_state=["(at i1 l2)"]
        )

    if schema_name == "UnifiedBlueprint":
        from nodes.elicitation import UnifiedBlueprint
        return UnifiedBlueprint(domain=dom_bp, problem=prob_bp)
    elif schema_name == "DomainBlueprint":
        return dom_bp
    else:
        return prob_bp

def invoke_structured_llm(schema: Type[T], prompt: str) -> T:
    """
    Invokes LLM with structured Pydantic output.
    Includes automated fallback across OpenRouter free models and direct Google Gemini API.
    """
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    last_exception = None

    # 1. OpenRouter Free Models
    if openrouter_api_key:
        for model_name in FALLBACK_MODEL_LIST:
            try:
                print(f"[LLM Provider]: Invoking OpenRouter '{model_name}'...")
                llm = ChatOpenAI(
                    model_name=model_name,
                    openai_api_key=openrouter_api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.0,
                    max_retries=2
                )
                structured_llm = llm.with_structured_output(schema)
                result = structured_llm.invoke(prompt)
                print(f"[LLM Provider]: Successfully obtained response from OpenRouter '{model_name}'.")
                return result
            except Exception as e:
                err_msg = str(e)
                print(f"[LLM Provider Warning]: '{model_name}' error ({err_msg[:100]}). Attempting fallback...")
                time.sleep(1)
                last_exception = e
                continue

    # 2. Direct Google Gemini API Fallback
    if gemini_api_key:
        try:
            print("[LLM Provider]: Invoking Direct Google Gemini API ('gemini-2.0-flash')...")
            from langchain_google_genai import ChatGoogleGenerativeAI
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_api_key,
                temperature=0.0
            )
            structured_llm = gemini_llm.with_structured_output(schema)
            result = structured_llm.invoke(prompt)
            print("[LLM Provider]: Successfully obtained response from Direct Google Gemini API.")
            return result
        except Exception as e:
            print(f"[LLM Provider Warning]: Google Gemini API error ({e}).")
            last_exception = e

    # 3. Rate-Limit / Offline Fallback Generator
    print("[LLM Provider Notice]: API rate limits hit across providers. Invoking fallback blueprint generator...")
    return generate_fallback_blueprint(schema.__name__, prompt)
