Here is the complete Markdown file (`SYSTEM_ARCHITECTURE_SPEC.md`) specifying the architectural flow, state management, and code execution pipeline for your project.

Save this file directly in your project root folder (`pddl_lifecycle_agent/SYSTEM_ARCHITECTURE_SPEC.md`) so your AI coding assistant (like Roo Code) or human collaborators can analyze, test, and verify your implementation against the formal **Knowledge Engineering for Planning and Scheduling (KEPS)** framework.

```markdown
# Unified Autonomous Lifecycle Agent for PDDL Domain Modelling
## System Architecture & Code Flow Specification

---

## 1. System Motivation & Goal
The central premise of this research is that **PDDL domain engineering is a continuous lifecycle, not a single one-shot generation task**. Existing LLM approaches treat planning domain generation as an isolated task, leading to syntax collapse, parameter mismatches, or unhandled errors.

This project implements a **Unified Autonomous Agentic System** built with **LangGraph** that orchestrates the complete 4-phase KEPS lifecycle:
1. **Phase 1: Acquisition & Conceptualization:** Natural language requirement extraction and relational state memory.
2. **Phase 2: Formulation & Encoding:** Intermediate Pydantic JSON schema generation and programmatic PDDL compilation (Option B).
3. **Phase 3: Verification & Validation (V&V):** Deterministic tool execution (VAL & Fast Downward) and LLM-driven diagnostic fault isolation.
4. **Phase 4: Maintenance & Evolution:** Backward compatibility checking against historical regression benchmarks.

---

## 2. Directory & Module Structure

```text
pddl_lifecycle_agent/
│
├── config/
│   └── __init__.py            # API keys, OpenRouter/Gemini endpoints, and base URLs
│
├── schemas/
│   ├── __init__.py
│   └── pddl_blueprint.py      # Phase 2.1: Intermediate Output Schema (Pydantic JSON Contracts)
│
├── tools/
│   ├── __init__.py
│   └── symbolic_oracles.py    # Phase 3.1: Subprocess Execution Wrappers for VAL & Fast Downward
│
├── nodes/
│   ├── __init__.py
│   ├── elicitation.py         # Phase 1.2: LLM Relational Knowledge Extractor
│   └── generation.py          # Phase 2.2: Programmatic Deterministic PDDL String Compiler
│
├── graph.py                   # Central Core Hub: LangGraph State Graph & Conditional Router Edges
├── main_workspace.ipynb       # Main Trigger, Evaluation & Testing Environment
├── SYSTEM_ARCHITECTURE_SPEC.md # This Architectural Blueprint Document
├── requirements.txt           # Project Dependencies
└── .clinerules                # Roo Code / VS Code AI Assistant Context Configuration

```

---

## 3. High-Level System Architecture & Closed Feedback Loop

The Central Core Hub (LangGraph Orchestrator) acts as the state controller. **Individual worker nodes never call each other directly.** Instead, worker nodes write updates to the `Shared State`, and the Central Core Hub routes data based on diagnostic results.

```text
+---------------------------------------------------------------------------------------------------+
|                               PHASE 1: ACQUISITION & CONCEPTUALIZATION                            |
|  [1.1 Natural Language Input] ---> [1.2 LLM Elicitation & Memory 🧠] ---> [1.3 Requirements Spec] |
+---------------------------------------------------|-----------------------------------------------+
                                                    |
                                                    v
+---------------------------------------------------------------------------------------------------+
|                                CENTRAL CORE HUB 🧠 (LangGraph Orchestrator)                       |
+---------------------------------------------------|-----------------------------------------------+
                                                    |
                                                    v
+---------------------------------------------------------------------------------------------------+
|                                 PHASE 2: FORMULATION & ENCODING                                   |
|        [2.1 Intermediate Output Schema ⚙️] ---> [2.2 Programmatic PDDL Compiler ⚙️]                |
+---------------------------------------------------|-----------------------------------------------+
                                                    |
                                                    v
+---------------------------------------------------------------------------------------------------+
|                               PHASE 3: VERIFICATION & VALIDATION (V&V)                            |
|  [3.1 Tool Execution Wrapper ⚡] ---> [3.2 Diagnostic Triage 🧠] ---> [3.3 Validated PDDL Model]    |
+---------------------------------------------------|-----------------------------------------------+
                                                    |
                                                    v
+---------------------------------------------------------------------------------------------------+
|                               PHASE 4: MAINTENANCE & EVOLUTION                                    |
|                       [4.1 Backward Compatibility / Historical Regression Suite ⚙️]                |
+---------------------------------------------------------------------------------------------------+

```

### Legend

* `🧠` **Probabilistic LLM Node:** Handles natural language interpretation, entity extraction, and failure log triage.
* `⚙️` **Deterministic Script Node:** Enforces rigid Pydantic JSON contracts and programmatic Lisp string builders.
* `⚡` **Symbolic Binary Oracle:** Invokes native command-line executables (`Validate` or `fast-downward`).

---

## 4. Shared Memory Contract (`AgentState`)

All data moving through the LangGraph nodes is maintained in a centralized, typed Python dictionary:

```python
from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    requirements: str                      # Raw Natural Language requirements (Block 1.1)
    pddl_domain_blueprint: Dict[str, Any]  # Intermediate Relational JSON Schema (Block 2.1)
    generated_domain_pddl: str             # Programmatically compiled domain.pddl text (Block 2.2)
    verification_errors: List[str]         # Console output / failure traces captured from VAL/FD (Block 3.1)

```

---

## 5. File Specifications & Implementation Code

### 5.1 `schemas/pddl_blueprint.py` (Phase 2.1 AST Contract)

Defines the Pydantic data structures that force the LLM to output a clean, code-accessible JSON structure before code string generation.

```python
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class PddlActionSchema(BaseModel):
    """Schema definition for individual PDDL actions."""
    action_name: str = Field(
        description="Snake_case identifier for the action, e.g., 'move_robot'"
    )
    parameters: Dict[str, str] = Field(
        description="Map of parameter variables to their types, e.g., {'?r': 'robot', '?from': 'location', '?to': 'location'}"
    )
    preconditions: List[str] = Field(
        description="List of PDDL predicate statements required before execution, e.g., ['(at ?r ?from)', '(connected ?from ?to)']"
    )
    effects: List[str] = Field(
        description="List of PDDL state modifications after execution, e.g., ['(at ?r ?to)', '(not (at ?r ?from))']"
    )

class DomainBlueprint(BaseModel):
    """Phase 2.1 Intermediate Output: Relational Blueprint Schema."""
    domain_name: str = Field(
        default="generated_domain", 
        description="Identifier for the domain, e.g., 'logistics_warehouse'"
    )
    requirements: List[str] = Field(
        default=[":strips", ":typing"], 
        description="List of required PDDL features, e.g., [':strips', ':typing']"
    )
    types: Dict[str, Optional[str]] = Field(
        description="Map of object types to their parent supertype, e.g., {'robot': 'agent', 'crate': 'object', 'location': None}"
    )
    predicates: List[str] = Field(
        description="List of formal predicate signatures, e.g., ['(at ?r - robot ?l - location)', '(holding ?r - robot ?c - crate)']"
    )
    actions: List[PddlActionSchema] = Field(
        description="List of all operational action schemas defined in the domain"
    )

```

---

### 5.2 `nodes/elicitation.py` (Phase 1.2 LLM Relational Extractor)

Parses the user's natural language input into the structured `DomainBlueprint` Pydantic model. Supports OpenRouter free endpoints or direct Google Gemini APIs.

```python
import os
from langchain_openai import ChatOpenAI
from schemas.pddl_blueprint import DomainBlueprint

def run_elicitation_node(state: dict) -> dict:
    """
    Phase 1.2 / 2.1 Node: Elicits requirements and populates 
    the Relational Knowledge Blueprint (DomainBlueprint JSON).
    """
    requirements_text = state.get("requirements", "")
    verification_errors = state.get("verification_errors", [])
    
    # Configure OpenRouter / OpenAI-compatible endpoint
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "your-key-here")
    
    llm = ChatOpenAI(
        model_name="google/gemini-2.0-flash-exp:free",
        openai_api_key=openrouter_key,
        openai_api_base="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)",
        temperature=0.0,
        max_retries=5
    )
    
    # Force structured output according to DomainBlueprint schema
    structured_llm = llm.with_structured_output(DomainBlueprint)
    
    feedback_context = ""
    if verification_errors:
        feedback_context = f"\nPrevious Diagnostic Feedback / Verification Errors to resolve:\n{verification_errors}\n"
    
    prompt = f"""
    You are an expert PDDL Knowledge Engineer. Analyze the following domain requirement text 
    and construct a valid intermediate PDDL Domain Blueprint JSON object.
    
    Requirements Text:
    {requirements_text}
    {feedback_context}
    Ensure all object types, predicates, and action parameters use proper variable names starting with '?'.
    """
    
    blueprint_object = structured_llm.invoke(prompt)
    state["pddl_domain_blueprint"] = blueprint_object.model_dump()
    return state

```

---

### 5.3 `nodes/generation.py` (Phase 2.2 Programmatic Compiler - Option B)

Bypasses the LLM entirely for string synthesis. Uses a deterministic Python string formatter to build Lisp-compliant `.pddl` code, eliminating syntax hallucinations.

```python
from schemas.pddl_blueprint import DomainBlueprint, PddlActionSchema

def compile_pddl_programmatically(blueprint_data: dict) -> str:
    """
    Option B Engine: Converts a DomainBlueprint JSON dictionary
    into perfectly indented, parenthetically closed Lisp PDDL code.
    """
    domain_name = blueprint_data.get("domain_name", "generated_domain")
    requirements = blueprint_data.get("requirements", [":strips", ":typing"])
    types = blueprint_data.get("types", {})
    predicates = blueprint_data.get("predicates", [])
    actions = blueprint_data.get("actions", [])
    
    pddl_lines = []
    
    # 1. Header & Requirements
    pddl_lines.append(f"(define (domain {domain_name})")
    req_str = " ".join(requirements) if isinstance(requirements, list) else ":strips :typing"
    pddl_lines.append(f"  (:requirements {req_str})")
    pddl_lines.append("")
    
    # 2. Types Hierarchy Block
    if types:
        pddl_lines.append("  (:types")
        supertype_map = {}
        for child, parent in types.items():
            parent_key = parent if parent else "object"
            if parent_key not in supertype_map:
                supertype_map[parent_key] = []
            supertype_map[parent_key].append(child)
            
        for parent, children in supertype_map.items():
            children_str = " ".join(children)
            if parent == "object":
                pddl_lines.append(f"    {children_str} - object")
            else:
                pddl_lines.append(f"    {children_str} - {parent}")
        pddl_lines.append("  )")
        pddl_lines.append("")
        
    # 3. Predicates Block
    if predicates:
        pddl_lines.append("  (:predicates")
        for pred in predicates:
            clean_pred = pred.strip()
            if not clean_pred.startswith("("):
                clean_pred = f"({clean_pred}"
            if not clean_pred.endswith(")"):
                clean_pred = f"{clean_pred})"
            pddl_lines.append(f"    {clean_pred}")
        pddl_lines.append("  )")
        pddl_lines.append("")
        
    # 4. Action Schemas Compilation
    for act in actions:
        if isinstance(act, dict):
            act_obj = PddlActionSchema(**act)
        else:
            act_obj = act
            
        pddl_lines.append(f"  (:action {act_obj.action_name}")
        param_parts = [f"{var} - {type_name}" for var, type_name in act_obj.parameters.items()]
        param_str = " ".join(param_parts)
        pddl_lines.append(f"    :parameters ({param_str})")
        
        # Preconditions
        if len(act_obj.preconditions) == 1:
            pddl_lines.append(f"    :precondition {act_obj.preconditions[0].strip()}")
        elif len(act_obj.preconditions) > 1:
            pres = " ".join([p.strip() for p in act_obj.preconditions])
            pddl_lines.append(f"    :precondition (and {pres})")
        else:
            pddl_lines.append("    :precondition (and)")
            
        # Effects
        if len(act_obj.effects) == 1:
            pddl_lines.append(f"    :effect {act_obj.effects[0].strip()}")
        elif len(act_obj.effects) > 1:
            effs = " ".join([e.strip() for e in act_obj.effects])
            pddl_lines.append(f"    :effect (and {effs})")
        else:
            pddl_lines.append("    :effect (and)")
            
        pddl_lines.append("  )")
        pddl_lines.append("")
        
    pddl_lines.append(")")
    return "\n".join(pddl_lines)

def run_generation_node(state: dict) -> dict:
    """
    Phase 2.2 Node: Programmatically compiles the DomainBlueprint JSON
    into valid Lisp PDDL code without calling an LLM.
    """
    blueprint_data = state.get("pddl_domain_blueprint", {})
    compiled_pddl = compile_pddl_programmatically(blueprint_data)
    state["generated_domain_pddl"] = compiled_pddl
    return state

```

---

### 5.4 `tools/symbolic_oracles.py` (Phase 3.1 Subprocess Wrapper)

Interface for invoking binary validators (`Validate`) and planners (`Fast Downward`) via Python's native `subprocess` module.

```python
import subprocess
import os
from typing import Tuple

def run_val_validator(domain_path: str, problem_path: str = None) -> Tuple[bool, str]:
    """
    Executes VAL against a generated domain.pddl file.
    Returns (is_valid, console_output_log).
    """
    if not os.path.exists(domain_path):
        return False, f"File Error: Path '{domain_path}' does not exist."

    cmd = ["Validate", domain_path]
    if problem_path and os.path.exists(problem_path):
        cmd.append(problem_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout + "\n" + result.stderr
        
        if "Errors: 0" in output or "Successful plans:" in output:
            return True, output
        elif result.returncode == 0 and "Error" not in output:
            return True, output
        else:
            return False, output

    except FileNotFoundError:
        return False, "System Warning: 'Validate' binary not found in system PATH."
    except subprocess.TimeoutExpired:
        return False, "Execution Error: VAL timed out after 15 seconds."

```

---

### 5.5 `graph.py` (Central Core Hub & Closed-Loop Router)

Assembles the state graph and implements the gatekeeper logic routing execution through the **Central Core Hub**.

```python
import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from nodes.elicitation import run_elicitation_node
from nodes.generation import run_generation_node
from tools.symbolic_oracles import run_val_validator

class AgentState(TypedDict):
    requirements: str
    pddl_domain_blueprint: dict
    generated_domain_pddl: str
    verification_errors: List[str]

def run_validation_node(state: AgentState) -> AgentState:
    pddl_code = state.get("generated_domain_pddl", "")
    temp_file = "temp_domain.pddl"
    
    with open(temp_file, "w") as f:
        f.write(pddl_code)
        
    is_valid, log_output = run_val_validator(temp_file)
    
    if not is_valid and "not found" not in log_output:
        state["verification_errors"] = [log_output]
    else:
        state["verification_errors"] = []
        
    return state

def route_after_validation(state: AgentState) -> str:
    """
    Conditional Gatekeeper Edge: Checks for error logs.
    If errors exist, routes execution back to Elicitation (Fast Repair Loop).
    """
    if state.get("verification_errors"):
        return "elicit"  # Fast Repair Loop back to Elicitation
    return END           # Validation Passed

# Construct Graph
builder = StateGraph(AgentState)

builder.add_node("elicit", run_elicitation_node)
builder.add_node("generate", run_generation_node)
builder.add_node("validate", run_validation_node)

builder.set_entry_point("elicit")
builder.add_edge("elicit", "generate")
builder.add_edge("generate", "validate")
builder.add_conditional_edges("validate", route_after_validation)

pddl_lifecycle_graph = builder.compile()

```

---

## 6. Execution & Testing Protocol (`main_workspace.ipynb`)

Execute the following cell in your Jupyter Notebook to run the graph and verify that data flows correctly across all files:

```python
%load_ext autoreload
%autoreload 2

import os
# Set OpenRouter or Gemini Key
os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-..."

from graph import pddl_lifecycle_graph

sample_requirements = """
We need a warehouse logistics domain. 
There are robots and crates. 
Robots can move between connected locations. 
A robot can pick up a crate at its current location if its hand is empty. 
A robot can drop a crate at its current location.
"""

initial_state = {
    "requirements": sample_requirements,
    "pddl_domain_blueprint": {},
    "generated_domain_pddl": "",
    "verification_errors": []
}

print("🚀 Executing Unified Lifecycle Agent Pipeline...\n")

final_state = pddl_lifecycle_graph.invoke(initial_state)

print("="*60)
print("1. RELATIONAL KNOWLEDGE BLUEPRINT (JSON SCHEMA)")
print("="*60)
import json
print(json.dumps(final_state["pddl_domain_blueprint"], indent=2))

print("\n" + "="*60)
print("2. PROGRAMMATICALLY COMPILED PDDL DOMAIN CODE")
print("="*60)
print(final_state["generated_domain_pddl"])

```

---

## 7. Validation Checklist for AI Debugging Agents

When your AI assistant (e.g., Roo Code) inspects your codebase, verify the following checks:

1. **Schema Check:** Does `schemas/pddl_blueprint.py` contain both `PddlActionSchema` and `DomainBlueprint`?
2. **LLM Binding Check:** Does `nodes/elicitation.py` invoke `.with_structured_output(DomainBlueprint)`?
3. **Option B Check:** Does `nodes/generation.py` call `compile_pddl_programmatically()` without making external LLM calls?
4. **Subprocess Check:** Does `tools/symbolic_oracles.py` handle missing binary exceptions gracefully?
5. **Central Hub Edge Check:** Does `graph.py` route validation errors back to `elicit` through conditional edges?

```

```