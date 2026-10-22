# Agentic AI PDDL Lifecycle System - Core Architectural Principles

## 1. Domain-Agnostic Agent Mandate (Zero Hardcoding / Zero Overfitting)
- **General-Purpose Goal**: This system is designed as an autonomous, general-purpose agent for PDDL domain lifecycle engineering (Elicitation $\rightarrow$ Compilation $\rightarrow$ Validation $\rightarrow$ Triage $\rightarrow$ Repair $\rightarrow$ Evolution $\rightarrow$ Maintenance).
- **Universal Applicability**: Every component, rule, prompt, heuristic, and validator must be universally applicable to **ANY valid PDDL (STRIPS + Typing) domain**.
- **Strictly Prohibited**:
  - NEVER write rules, heuristics, or prompt patches tailored to a single specific domain (e.g., Blocksworld, Gripper, Barman, Satellite, Rovers, Depot, etc.).
  - NEVER hardcode domain-specific type names, action names, or predicate names (e.g., `shot`, `shaker`, `cocktail`, `spanner`, `rover`, `rock-sample`, `gripper`) as specialized case-handling logic in prompts or code.
  - NEVER alter the agent's logic just to force one specific test case or benchmark instance to pass if that logic does not universally hold for all PDDL domains.

## 2. Universal Formal PDDL Semantics Only
- All rules codified in `config/pddl_standards.py`, triage prompts, repair prompts, and compiler modules must strictly derive from:
  1. Classical PDDL 2.1 formal semantics (Fox & Long 2003; McDermott 1998; Haslum et al. 2019).
  2. First-Order Logic (FOL) well-formedness (variable scoping, quantifier semantics, relation invariance).
  3. Formal Planning AST invariants (acyclic type hierarchy under `object`, unique predicate symbols without signature overloading, well-typed grounding).
- **Abstract Illustrative Examples Only**: If an example is needed in prompt instructions to clarify an abstract rule, it must use domain-independent, generic archetypes (e.g., `item`, `container`, `location`, `vehicle`, `agent`) and clearly illustrate a general principle, not a domain-specific workaround.

## 3. Mandatory Audit Before Modifying `config/pddl_standards.py`
- **Mandatory Pre-Flight Check**: Whenever an issue arises on a specific benchmark domain, the developer/agent MUST first consult this file (`AGENTS.md`).
- **Generalizability Test**: Before adding or updating any rule in `config/pddl_standards.py`, answer:
  > *"Is this rule derived from formal PDDL syntax and semantics that apply identically to all possible PDDL domains, or is it a tailored patch for the currently failing domain?"*
  - If it is universal (e.g., "no duplicate predicate symbols in `(:predicates ...)`", "every parameter variable must start with `?`", "parameter types must match declared predicate signatures"), it is permitted.
  - If it relies on domain-specific semantics or assumptions, it is **strictly forbidden**.

## 4. Code Nomenclature, Semantic Accuracy, and Zero Legacy Aliases
- **No Stale Aliases**: Never retain or introduce backwards-compatibility alias names (such as `evaluate_bilevel_domain_equivalence = evaluate_action_reconstruction`) across the codebase. Always call and import the canonical, updated name directly.
- **Continuous Logic-to-Code Alignment**: When the algorithmic logic, metric, or architectural component is updated or refactored, you MUST immediately update all function names, variable names, and file names across all calling modules to accurately reflect the true underlying semantics and literature foundation.

* **Empirical Integrity**: If an LLM generates invalid constructs or fails to repair a domain within the allowed iterations, **that failure is scientifically valid and expected**. Do NOT force success through prompt engineering tricks or heuristic fallbacks. Record the result honestly as unverified/failure.
* **Mandatory File Inspection Before Editing**: Always view and inspect existing code files before proposing or applying updates. Never assume file state or contents.
## 5. Execution Environment: Conda `agent_env` Only
* **Target Environment**: The sole active Python environment for this project is Conda `agent_env`.
* **Binary Path**: `C:\Users\Srushti\miniconda3\envs\agent_env\python.exe`
* **Command Rule**: Always execute all Python scripts, tests, dependencies, and Streamlit servers strictly within `agent_env` (never base or global system Python).



* **Never use latex format for math formulas** during feedback or response or explanation.

* **While writing any report please use the ARMS template** as it would help to validate, verify and improve the work.

# Important
* **Whatever code we have plan and are planning we need make sure that our important goal is evaluate our generated domain, problem and plan with standard domain, problem and plan for semantic soundness, task completeness and logical consistency.** Lets verify our entire logic again if it align with above rules and principles. It is fine if not every domain gets evaluated against the standard domain and problem but at least we should not use any hard corded logic just to generated and validate the generated plan. 