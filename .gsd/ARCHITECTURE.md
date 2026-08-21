# ARCHITECTURE.md — System Architecture & Design

## Overview
UPDEAgent is an autonomous agentic framework designed to orchestrate the end-to-end PDDL Domain Engineering Lifecycle using a closed feedback loop between Large Language Models (LLMs) and symbolic automated planning oracles (VAL and Fast Downward).

## Core Architectural Blueprint

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

## System Components

### 1. LangGraph Core Orchestrator ([`graph.py`](file:///e:/Rosh/Thesis/pddl_lifecycle_agent/graph.py))
- Controls workflow routing, iteration counting, state persistence, and diagnostic feedback loops.
- Maintains `AgentState` containing requirements, domain/problem blueprints, compiled PDDL, verification logs, and repair history.

### 2. Intermediate Blueprint AST ([`schemas/pddl_blueprint.py`](file:///e:/Rosh/Thesis/pddl_lifecycle_agent/schemas/pddl_blueprint.py))
- Pydantic v2 schemas defining `DomainBlueprint` and `PddlActionSchema`.
- Decouples probabilistic semantic extraction from rigid Lisp formatting.

### 3. Worker Nodes ([`nodes/`](file:///e:/Rosh/Thesis/pddl_lifecycle_agent/nodes))
- `elicitation.py`: LLM node extracting relational domain mechanics into structured JSON blueprints.
- `generation.py`: Deterministic string builder compiling JSON AST into valid PDDL files.
- `diagnosis.py` (Planned): Diagnostic triage node transforming dry tool error logs into targeted repair instructions.

### 4. Symbolic Tool Oracles ([`tools/symbolic_oracles.py`](file:///e:/Rosh/Thesis/pddl_lifecycle_agent/tools/symbolic_oracles.py))
- `VAL` (`Validate` binary): Checks syntax and semantics of generated domain and problem files.
- `Fast Downward` (`fast-downward` script/binary): Checks plan reachability and solvability.
