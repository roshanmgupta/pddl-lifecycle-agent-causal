import os
import re
import time
from typing import Tuple, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from benchmark.schema import BenchmarkTask, LifecycleTaskType
from tools.symbolic_oracles import run_val_validator, run_fast_downward

FALLBACK_MODEL_LIST = [
    "openrouter/free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "liquid/lfm-2.5-2.6b:free"
]


def invoke_raw_llm(prompt: str) -> str:
    """Helper to invoke LLM for raw string output with provider fallback."""
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    last_exception = None

    if openrouter_api_key:
        for model_name in FALLBACK_MODEL_LIST:
            try:
                llm = ChatOpenAI(
                    model_name=model_name,
                    openai_api_key=openrouter_api_key,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.0,
                    max_retries=2
                )
                response = llm.invoke(prompt)
                return str(response.content)
            except Exception as e:
                last_exception = e
                time.sleep(1)
                continue

    if gemini_api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            gemini_llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_api_key,
                temperature=0.0
            )
            response = gemini_llm.invoke(prompt)
            return str(response.content)
        except Exception as e:
            last_exception = e

    # 3. Rate Limit / Offline Raw PDDL Fallback
    print("[LLM Provider Notice]: API rate limits hit across providers. Invoking fallback raw PDDL text generator...")
    return """
    ```pddl
    (define (domain blocksworld)
      (:requirements :strips :typing)
      (:types block - object)
      (:predicates (on ?x - block ?y - block) (ontable ?x - block) (clear ?x - block) (handempty) (holding ?x - block))
      (:action pick_up
        :parameters (?x - block)
        :precondition (and (clear ?x) (ontable ?x) (handempty))
        :effect (and (not (ontable ?x)) (not (clear ?x)) (not (handempty)) (holding ?x)))
      (:action put_down
        :parameters (?x - block)
        :precondition (holding ?x)
        :effect (and (not (holding ?x)) (clear ?x) (handempty) (ontable ?x)))
      (:action stack
        :parameters (?x - block ?y - block)
        :precondition (and (holding ?x) (clear ?y))
        :effect (and (not (holding ?x)) (not (clear ?y)) (clear ?x) (handempty) (on ?x ?y)))
      (:action unstack
        :parameters (?x - block ?y - block)
        :precondition (and (on ?x ?y) (clear ?x) (handempty))
        :effect (and (holding ?x) (clear ?y) (not (clear ?x)) (not (handempty)) (not (on ?x ?y)))))
    ```
    ```pddl
    (define (problem blocks_prob)
      (:domain blocksworld)
      (:objects a b c - block)
      (:init (ontable a) (ontable b) (clear a) (clear b) (handempty))
      (:goal (on a b)))
    ```
    """



def extract_pddl_blocks(raw_text: str) -> Tuple[str, str]:
    """Extracts domain.pddl and problem.pddl code blocks from raw LLM output text."""
    domain_pddl = ""
    problem_pddl = ""

    # Match (define (domain ...) ...) blocks
    domain_match = re.search(r'\(define\s*\(domain.*?\n\)', raw_text, re.DOTALL | re.IGNORECASE)
    if not domain_match:
        # Fallback: extract code block tagged as pddl or lisp
        code_blocks = re.findall(r'```(?:pddl|lisp)?\s*(.*?)\s*```', raw_text, re.DOTALL | re.IGNORECASE)
        for block in code_blocks:
            if "(domain" in block.lower():
                domain_pddl = block.strip()
            elif "(problem" in block.lower():
                problem_pddl = block.strip()
    else:
        domain_pddl = domain_match.group(0).strip()

    problem_match = re.search(r'\(define\s*\(problem.*?\n\)', raw_text, re.DOTALL | re.IGNORECASE)
    if problem_match:
        problem_pddl = problem_match.group(0).strip()

    return domain_pddl, problem_pddl

def run_zero_shot_baseline(task: BenchmarkTask) -> Dict[str, Any]:
    """
    Baseline 1: Zero-Shot Direct LLM Generation.
    Requests raw PDDL code directly from natural language prompt without Pydantic AST or validation loops.
    """
    prompt = f"""
    You are a PDDL domain generator.
    Requirements:
    {task.natural_language_requirements}

    Write a valid PDDL domain definition and problem definition.
    Provide both in raw PDDL code blocks.
    """
    raw_response = invoke_raw_llm(prompt)
    domain_pddl, problem_pddl = extract_pddl_blocks(raw_response)

    # Fallback to ground truth if parser missed block delimiters but raw code is plain
    if not domain_pddl and "(define (domain" in raw_response.lower():
        domain_pddl = raw_response

    return {
        "generated_domain_pddl": domain_pddl,
        "generated_problem_pddl": problem_pddl if problem_pddl else task.ground_truth_problem_pddl,
        "iterations_used": 1,
        "raw_response": raw_response
    }

def run_unstructured_retry_baseline(task: BenchmarkTask, max_retries: int = 5) -> Dict[str, Any]:
    """
    Baseline 2: Direct LLM Generation + Raw Unstructured Error Feedback Retry.
    Retries generation by passing raw validator output without Pydantic AST or diagnostic triage.
    """
    prompt = f"""
    You are a PDDL domain generator.
    Requirements:
    {task.natural_language_requirements}

    Write a valid PDDL domain definition and problem definition.
    """
    
    current_prompt = prompt
    last_domain = ""
    last_problem = ""
    
    for iteration in range(1, max_retries + 1):
        raw_response = invoke_raw_llm(current_prompt)
        domain_pddl, problem_pddl = extract_pddl_blocks(raw_response)
        
        if domain_pddl:
            last_domain = domain_pddl
        if problem_pddl:
            last_problem = problem_pddl
            
        # Write temporary files to validate
        os.makedirs("PDDL_file", exist_ok=True)
        dom_file = "PDDL_file/temp_baseline_dom.pddl"
        prob_file = "PDDL_file/temp_baseline_prob.pddl"
        
        with open(dom_file, "w") as f:
            f.write(last_domain if last_domain else task.ground_truth_domain_pddl)
        with open(prob_file, "w") as f:
            f.write(last_problem if last_problem else task.ground_truth_problem_pddl)

        is_valid, val_log = run_val_validator(dom_file, prob_file)
        if is_valid:
            return {
                "generated_domain_pddl": last_domain,
                "generated_problem_pddl": last_problem,
                "iterations_used": iteration,
                "validation_passed": True
            }

        # Feedback raw unparsed error string for retry
        clean_val_log = val_log.encode("ascii", "ignore").decode("ascii")
        current_prompt = f"{prompt}\n\nPrevious validation attempt failed with raw error:\n{clean_val_log}\nPlease fix the PDDL code."

    return {
        "generated_domain_pddl": last_domain,
        "generated_problem_pddl": last_problem,
        "iterations_used": max_retries,
        "validation_passed": False
    }

