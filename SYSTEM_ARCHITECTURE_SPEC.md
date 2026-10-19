# Unified Autonomous Lifecycle Agent for PDDL Domain Modelling
## System Architecture & Code Flow Specification (Updated with Causal Graph & SBFL)

---

## 1. System Motivation & Architectural Grounding

The fundamental premise of this thesis is that **PDDL domain engineering is a continuous lifecycle software engineering process, not a one-shot text completion task** (aligning with Prof. Dr. Ilche Georgievski's Knowledge Engineering for Planning and Scheduling framework). Existing LLM approaches treat planning domain generation as isolated text translation, resulting in syntax collapse, unbound parameter errors, and state-space deadlocks that ungrounded models cannot diagnose or repair.

This project implements a **Unified Closed-Loop Autonomous Agentic System** built with **LangGraph** orchestrating four lifecycle phases:
1. **Phase 1: Acquisition & Conceptualization**: Natural language requirement extraction and relational Pydantic AST schema elicitation.
2. **Phase 2: Formulation & Encoding**: Deterministic Python compilation from AST blueprints to 100% syntactically valid PDDL 2.1 (STRIPS + Typing) code.
3. **Phase 3: Verification, Causal Graph Invariant Analysis & SBFL Triage**:
   - **Symbolic Verification**: Ground-truth classical validators (VAL) and planners (Fast Downward).
   - **Deterministic Causal Graph Engine (`tools/sbfl_analyzer.py`)**: Computes 4 classical planning invariants (Goal Relevance, Causal Cycles, DTG Invertibility, and Mutex Contradictions) and mathematical Ochiai Spectrum-Based Fault Localization (SBFL).
   - **Diagnostic Reasoning LLM Agent (`nodes/triage.py`)**: Maps causal graph findings and validator traces into structured, actionable `DiagnosticReport` schemas.
   - **Surgical AST Repair (`nodes/repair.py`)**: Applies localized mutations strictly to relational AST blueprints.
4. **Phase 4: Maintenance & Evolution**: Backward compatibility verification against historical benchmark test suites (IPC and AutoPlanBench).

---

## 2. Directory & Module Structure

```text
pddl_lifecycle_agent/
│
├── config/
│   ├── model_config.py        # Strict single-model OpenRouter configuration & telemetry
│   └── pddl_standards.py      # Strict classical PDDL 2.1 rules and prompt contracts
│
├── schemas/
│   └── pddl_blueprint.py      # Pydantic AST blueprints (DomainBlueprint, ProblemBlueprint, DiagnosticReport)
│
├── tools/
│   ├── symbolic_oracles.py    # Subprocess execution wrappers for VAL (Validate) and Fast Downward
│   ├── sbfl_analyzer.py       # Deterministic Causal Graph & Ochiai SBFL Diagnostic Engine
│   ├── blueprint_parser.py    # Deterministic PDDL-to-Blueprint AST parser
│   └── benchmark_loader.py    # Automated dataset loader for IPC archives and AutoPlanBench
│
├── nodes/
│   ├── elicitation.py         # Phase 1: Relational Knowledge Extraction (LLM_PHASE_1)
│   ├── generation.py          # Phase 2: Deterministic Python PDDL Compiler (100% AST-driven)
│   ├── triage.py               # Phase 3.1: Dual-Layer Causal Graph & LLM Diagnostic Triage (LLM_PHASE_3)
│   ├── repair.py              # Phase 3.2: Surgical Relational Blueprint Repair (LLM_PHASE_3)
│   └── maintenance.py         # Phase 4: Backward Compatibility Regression Engine (LLM_PHASE_4)
│
├── eval/
│   ├── baselines.py           # Ablation (No Triage), Unstructured Retry, and Zero-Shot implementations
│   └── benchmark_runner.py    # Automated evaluation harness for 30 curated benchmark tasks
│
├── tests/
│   └── test_causal_graph_triage.py # Automated test suite for Causal Graph & DTG invariants
│
├── graph.py                   # Central LangGraph StateGraph & conditional router edges
└── app.py                     # Interactive Streamlit Web UI with multi-tab inspection
```

---

## 3. High-Level System Architecture & Closed Feedback Loop

```text
                                [ Natural Language Requirements ]
                                                │
                                                ▼
+───────────────────────────────────────────────────────────────────────────────────────────────────+
| PHASE 1: ACQUISITION & CONCEPTUALIZATION                                                          |
|   [1.1 Elicitation Node 🧠] ──► Extracts relational AST blueprints (DomainBlueprint, ProblemBlueprint)|
+───────────────────────────────────────────────┬───────────────────────────────────────────────────+
                                                │
                                                ▼
+───────────────────────────────────────────────────────────────────────────────────────────────────+
| PHASE 2: FORMULATION & ENCODING                                                                   |
|   [2.1 Deterministic Compiler ⚙️] ──► Generates 100% valid Lisp PDDL 2.1 (:strips, :typing) strings|
+───────────────────────────────────────────────┬───────────────────────────────────────────────────+
                                                │
                                                ▼
+───────────────────────────────────────────────────────────────────────────────────────────────────+
| PHASE 3: VERIFICATION, CAUSAL GRAPH ANALYSIS & SURGICAL REPAIR                                    |
|                                                                                                   |
|   [3.1 Symbolic Oracles ⚡]                                                                        |
|         ├─► VAL: Syntax, typing, arity, and plan validation                                       |
|         └─► Fast Downward: Grounding solvability and state-space reachability                     |
|                                                                                                   |
|         ▼ (On Oracle Failure / Search Exhaustion)                                                 |
|                                                                                                   |
|   [3.2 Classical Causal Graph & SBFL Engine ⚙️ (tools/sbfl_analyzer.py)]                           |
|         ├─► Invariant 1: Goal Relevance BFS & Non-Goal Leaf Action Pruning (Slide 18)             |
|         ├─► Invariant 2: Action Enablement Digraph Cycle & Deadlock Detection (Slide 10/23)       |
|         ├─► Invariant 3: Domain Transition Graph (DTG) Reversibility / Absorbing States (Slide 14)|
|         ├─► Invariant 4: STRIPS Mutex Contradiction & Effect Co-occurrence (Slide 9)              |
|         └─► Ochiai Formula: raw_ochiai = e_f / sqrt((e_f + n_f) * (e_f + e_p))                    |
|                                                                                                   |
|         ▼ (Mathematically Grounded Suspiciousness Matrix)                                         |
|                                                                                                   |
|   [3.3 Diagnostic Triage Node 🧠 (nodes/triage.py)]                                                |
|         └─► Synthesizes Causal Graph invariants & Oracle logs into structured DiagnosticReports    |
|                                                                                                   |
|         ▼ (Structured Failure Items)                                                              |
|                                                                                                   |
|   [3.4 Surgical Repair Node 🧠 (nodes/repair.py)]                                                 |
|         └─► Modifies AST blueprints in memory ──► Loops back to Phase 2 (Compiler)               |
+───────────────────────────────────────────────┬───────────────────────────────────────────────────+
                                                │ (When VAL & FD Pass Cleanly)
                                                ▼
+───────────────────────────────────────────────────────────────────────────────────────────────────+
| PHASE 4: MAINTENANCE & EVOLUTION                                                                  |
|   [4.1 Historical Regression Suite ⚙️] ──► Verifies backward compatibility across legacy problems |
|   [4.2 Gatekeeper Router] ──► Re-triages if regression broken, else outputs Verified PDDL Suite   |
+───────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 4. Shared Memory Contract (`AgentState`)

```python
class AgentState(TypedDict, total=False):
    # Requirements & Blueprints
    requirements: str
    pddl_domain_blueprint: dict
    pddl_problem_blueprint: dict
    initial_pddl_domain_blueprint: dict
    
    # Compiled PDDL Strings
    generated_domain_pddl: str
    generated_problem_pddl: str
    initial_domain_pddl: str
    initial_problem_pddl: str
    
    # Oracle & Diagnostic Signals
    verification_errors: List[str]
    initial_verification_errors: List[str]
    diagnostic_reports: List[dict]
    historical_diagnostic_reports: List[dict]
    formatted_diagnostic_feedback: str
    
    # Causal Graph & SBFL Telemetry
    causal_graph_analysis: dict
    
    # Lifecycle Control & Historical Regression
    historical_regression_suite: List[dict]
    iteration_count: int
    max_iterations: int
    skip_triage: bool
    system_type: str
    
    # Plan Synthesis & Telemetry
    generated_plan_result: dict
    historical_plan_results: List[dict]
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    node_latencies: dict
```

---

## 5. Detailed Component Specifications

### 5.1 Deterministic Compiler (`nodes/generation.py`)
Direct raw string generation by LLMs frequently yields unbalanced parentheses and invalid keyword tags. The compiler eliminates syntax errors deterministically:
* Accepts `DomainBlueprint` and `ProblemBlueprint` JSON objects.
* Assembles clean, standard classical PDDL 2.1 code using rigid formatting rules.
* Guarantees 100% syntactically valid PDDL strings on every pass.

### 5.2 Deterministic Causal Graph & SBFL Engine (`tools/sbfl_analyzer.py`)
Grounded in classical planning literature (*Helmert 2006; Torralba, Croitoru, & Hoffmann 2018; Abreu et al. 2007*):

1. **Goal Relevance & Non-Goal Leaf Pruning**:
   - Traverses backward from `:goal` predicates across action add-effects and preconditions.
   - Computes `causal_distance` for every action schema. Actions disconnected from the goal receive a suspiciousness score of 0.00, pruning search-space noise.
2. **Causal Cycle & Deadlock Detection**:
   - Builds directed enablement graph: directed edge (A -> B) if AddEffects(A) intersects Preconditions(B).
   - Identifies self-deadlocks and multi-action circular dependency loops lacking an initial state bootstrap.
3. **DTG Reversibility / Absorbing State Detection**:
   - Identifies any predicate deleted by an action schema that has no producer action anywhere in the domain.
   - Flags critical absorbing state locks that trap planners in unsolvable states.
4. **STRIPS Mutex Contradiction Detection**:
   - Identifies actions that simultaneously assert and negate the exact same atom.
5. **Ochiai SBFL Formulation**:
   - `raw_ochiai = e_f / sqrt((e_f + n_f) * (e_f + e_p))`
   - Suspiciousness is modulated by topological distance to goal:
     `final_score = min(1.0, raw_ochiai * (1.0 / (1.0 + 0.25 * (causal_distance - 1))))`
     (with structural deadlocks assigned a lower bound of 0.85 and mutex contradictions assigned 1.00).

### 5.3 Diagnostic Triage Node (`nodes/triage.py`)
Operates as a **post-execution debugging oracle**:
* Injects the Causal Graph summary into the prompt of `LLM_PHASE_3`.
* Constrains the LLM to output structured `DiagnosticReport` schemas:
  - `error_category`: SYNTAX_PARSE, TYPE_SIGNATURE, GROUNDING_UNSOLVABILITY, SYSTEM_ORACLE_ERROR, or HISTORICAL_REGRESSION.
  - `repair_operation_type`: PRECONDITION_RELAXATION, PRECONDITION_INSERTION, EFFECT_ALIGNMENT, TYPE_ARITY_ALIGNMENT, INITIAL_STATE_AUGMENTATION, or GENERAL_AST_REPAIR.
  - `faulty_element`: Identified action schema name.
  - `suspiciousness_score`: Mathematically grounded rank.
  - `suggested_repair_hint`: Actionable adjustment instructions.
* **Empirical Integrity**: Operates with 100% LLM reasoning grounded in the Causal Graph matrix. If an LLM call fails, the failure is recorded directly without heuristic fallbacks or synthetic substitutes.

### 5.4 Surgical Repair Node (`nodes/repair.py`)
* Never edits raw text strings.
* Ingests current `DomainBlueprint` JSON and the `DiagnosticReport` items.
* Performs targeted AST updates on identified action preconditions, effects, or signatures.
* Returns modified blueprint back to the Python Compiler.

### 5.5 Phase 4 Maintenance & Regression Suite (`nodes/maintenance.py`)
* Evaluates the repaired domain against historical problem instances (Method A: Autonomous Evolution vs Method B: Benchmark Multi-Instance).
* Prevents "overfitting" repairs that fix the active problem while breaking historical planning capabilities.