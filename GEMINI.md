# STRICT RESEARCH & ARCHITECTURAL RULES
# PDDL Lifecycle Agent — Master's Thesis Project

> **CRITICAL INSTRUCTION FOR ALL AI ASSISTANTS**:
> Read and strictly enforce these rules before updating any code, configuration, or prompts in this repository.

---

## 1. PDDL Standards Policy: Pure Classical PDDL 2.1 (STRIPS + Typing) Only
* **Strict Formal Standard**: The system operates **exclusively** on pure classical PDDL 2.1 with `:strips` and `:typing`.
* **NO Ad-Hoc / Handcrafted Rules or Heuristics**: Never inject bespoke, handcrafted, or domain-specific rules (e.g. artificial fuel instructions, custom mechanics, or workarounds), hardcoded scoring multipliers (e.g., ad-hoc multipliers or artificial tie-breakers), or keyword filter hacks into `tools/sbfl_analyzer.py`, `config/pddl_standards.py`, prompts, or nodes. All mathematical formulas must remain purely grounded.
* **Empirical Integrity**: If an LLM generates invalid constructs or fails to repair a domain within the allowed iterations, **that failure is scientifically valid and expected**. Do NOT force success through prompt engineering tricks or heuristic fallbacks. Record the result honestly as unverified/failure.
* **Mandatory File Inspection Before Editing**: Always view and inspect existing code files before proposing or applying updates. Never assume file state or write speculative code without verifying the active implementation.

---

## 2. LLM Provider & Model Policy: Strict Single-Model OpenRouter
* **Sole Provider**: OpenRouter is the only supported provider. All keys and endpoints are configured via OpenRouter.
* **Strict Phase Assignment**:
  - Phase 1 (Elicitation): Must strictly invoke `LLM_PHASE_1` from `.env`.
  - Phase 3 (Triage & Repair): Must strictly invoke `LLM_PHASE_3` from `.env`.
  - Phase 4 (Maintenance / Regression): Must strictly invoke `LLM_PHASE_4` from `.env`.
* **NO Model Cascading or Fallback**: Under no circumstances should the system silently switch models, fall back to secondary providers, or mutate model selection on errors or rate limits. If a model call fails, report the error directly.

---

## 3. Continuous Evolution & UI Requirements
* **Prompt Freedom**: The continuous evolution text area must remain clean and empty by default (`value=""`), using helpful placeholder guidance rather than forcing a pre-filled default description.
* **Manual File Selection**: Users manually select/upload `domain.pddl` and `problem.pddl`. Never assume or force hardcoded domain files.
* **Display Cleanliness**: Do not display long absolute filesystem paths in the UI; show clean relative names (e.g., `Streamlit_output_file/<domain>/<file>.pddl`).
* **Tab 1 Structure**: Tab 1 (`📄 Compiled PDDL Code`) must display clean side-by-side PDDL (`domain.pddl` and `problem.pddl`) without redundant metric banners or extra subtabs.

---

## 4. Code & Streamlit Conventions
* **Deprecation Avoidance**: In Streamlit components, avoid deprecated parameters (e.g. follow current Streamlit layout and width conventions).
* **Deterministic Compilers**: All PDDL compilation from AST blueprints is 100% deterministic via Python compiler (`nodes/generation.py`), never direct unverified raw LLM string generation.
* **Symbolic Verification**: VAL and Fast Downward are the sole ground-truth classical oracles.

---

## 5. Execution Environment: Conda `agent_env` Only
* **Target Environment**: The sole active Python environment for this project is Conda `agent_env`.
* **Binary Path**: `C:\Users\Srushti\miniconda3\envs\agent_env\python.exe`
* **Command Rule**: Always execute all Python scripts, tests, dependencies, and Streamlit servers strictly within `agent_env` (never base or global system Python).

# please write it correctly...

never use latex format for math formulas during feedback or response you give.

While writing any report please use the ARMS template as it would help to validate, verify and improve the work.

# QUestion answer section

Always update the latest correct discussion output in the question answers markdown file: [QUESTION_ANSWERS.md](file:///e:/Rosh/Thesis/pddl_lifecycle_agent/QUESTION_ANSWERS.md).
If we are discussing and we get the correct output we should save it and also should provide the reference in the new file. We should not overite it unless its really necessary.
For numerical or equation like question always write the formula, why it is needed and concept behind it.


## Output Formatting Rules

- **No LaTeX Math:** Never output formulas, variables, conditions, or math logic using LaTeX delimiters (`$` or `$$`), `\neq`, `\times`, or TeX commands.
- **Readable Plain Text:** Always express mathematical statements in plain text, standard code blocks, or simple Unicode characters (e.g., write `m != k`, `m is not equal to k`, `x^2`, `sqrt(x)`).