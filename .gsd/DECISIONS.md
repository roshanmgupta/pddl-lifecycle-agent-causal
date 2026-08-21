# DECISIONS.md — Architectural Decision Log

## ADR-001: LangGraph for Agentic Lifecycle Orchestration
- **Date**: 2026-08-22
- **Status**: Accepted
- **Context**: Autonomous PDDL domain engineering requires state retention across multi-step repair and evolution loops, with explicit tool invocation (VAL, Fast Downward).
- **Decision**: Use `LangGraph` as the stateful orchestrator with centralized `AgentState` memory and conditional edge routing based on diagnostic tool feedback.
- **Consequences**: Standardized state management, modular worker node development, clear feedback loops.

## ADR-002: Intermediate Pydantic Blueprint JSON (AST)
- **Date**: 2026-08-22
- **Status**: Accepted
- **Context**: Direct LLM generation of PDDL string syntax frequently leads to missing parenthesization and syntax errors.
- **Decision**: Impose a two-stage encoding pipeline: (1) LLM generates structured Pydantic JSON AST (`DomainBlueprint`), and (2) deterministic Python script compiles JSON into valid PDDL Lisp strings.
- **Consequences**: Eliminates trivial syntax errors and guarantees strict schema validation prior to PDDL compilation.
