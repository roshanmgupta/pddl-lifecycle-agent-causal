# ROADMAP.md

> **Current Phase**: Phase 1: Lifecycle Model & Blueprint Schemas
> **Milestone**: v1.0 — Master's Thesis Autonomous Lifecycle Agent & Benchmark

## Must-Haves (from SPEC)
- [ ] Formal PDDL domain engineering lifecycle specification
- [ ] Autonomous agentic closed-loop orchestrator (LangGraph)
- [ ] Layered diagnostic fault localization module
- [ ] Benchmark suite (PDDLLifeCycleBench) across 5 IPC domain families
- [ ] Empirical evaluation report against zero-shot and ablated baselines

## Phases

### Phase 1: Lifecycle Model & Blueprint Schemas
**Status**: ⬜ Not Started
**Objective**: Formalize the PDDL domain engineering lifecycle activities (elicitation, encoding, V&V, repair, evolution) and implement robust Pydantic blueprint contracts (`schemas/pddl_blueprint.py`).
**Requirements**: REQ-01, REQ-02

### Phase 2: Tool Wrappers & Diagnostic Triage Module
**Status**: ⬜ Not Started
**Objective**: Build deterministic symbolic oracle wrappers for VAL and Fast Downward (`tools/symbolic_oracles.py`) and implement a dedicated diagnostic triage node to categorize error signatures into actionable repair context.
**Requirements**: REQ-03, REQ-04

### Phase 3: LangGraph Autonomous Closed-Loop Orchestrator
**Status**: ⬜ Not Started
**Objective**: Integrate worker nodes (elicitation, AST generation, deterministic Lisp compiler, diagnostic repair, regression validator) into a unified stateful LangGraph router supporting repair loops and domain evolution.
**Requirements**: REQ-05

### Phase 4: PDDLLifeCycleBench Construction
**Status**: ⬜ Not Started
**Objective**: Build `PDDLLifeCycleBench` containing standardized test tasks for elicitation, model generation, synthetic fault repair (missing preconditions, wrong parameters, type errors), and domain evolution across IPC domains (Blocksworld, Logistics, Rovers, Depots, Satellite).
**Requirements**: REQ-06

### Phase 5: Empirical Evaluation, Baselines & Error Analysis
**Status**: ⬜ Not Started
**Objective**: Execute automated benchmark runs against zero-shot generation baselines and ablated agent variants (e.g. no diagnostic triage, fixed retries). Compute metrics and analyze LLM failure modes over state-transition models for the thesis paper.
**Requirements**: REQ-07, REQ-08
