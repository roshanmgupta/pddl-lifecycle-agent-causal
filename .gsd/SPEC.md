# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
Construct an autonomous agentic framework (UPDEAgent) and an evaluation benchmark (PDDLLifeCycleBench) that orchestrates the end-to-end PDDL domain engineering lifecycle—from natural language elicitation and intermediate schema formulation to symbolic validation (VAL/Fast Downward), diagnostic fault localization, automated repair, and backward-compatible domain evolution.

## Goals
1. **Lifecycle Model Formalization**: Define a formal lifecycle activity model for PDDL domain engineering detailing activities, typed inputs/outputs, and dependency structures.
2. **Autonomous Agent Development (UPDEAgent)**: Build a multi-node agentic system (using LangGraph, Pydantic, VAL, and Fast Downward) capable of stateful iteration, fault triage, layered feedback interpretation, and automated model repair/evolution.
3. **Benchmark Construction (PDDLLifeCycleBench)**: Assemble a multi-activity benchmark combining classical IPC domains (Blocksworld, Logistics, Rovers, Depots, Satellite), flawed domains, and natural language specifications across generation, repair, fault localization, and evolution tasks.
4. **Empirical & Qualitative Evaluation**: Quantitatively evaluate the agent against single-shot LLM baselines and ablated variants across plan validity rate, repair success, evolution correctness, and iteration efficiency; conduct qualitative error analysis on LLM reasoning over formal state-transition models.

## Non-Goals (Out of Scope)
- **Runtime Robotics Sensor Feedback**: Offline domain engineering is the target (not online sensor-driven execution feedback as in robotics frameworks like LASP).
- **HTN / Non-Classical Extensions as Core**: Primary focus is classical PDDL domain engineering (STRIPS, typed parameters, preconditions, effects).

## Users
- AI Planning researchers and Knowledge Engineers constructing, validating, and evolving PDDL domain models.

## Constraints
- **Licensing**: Open-source under the MIT License.
- **Tech Stack**: Python 3.10+, LangGraph, Pydantic v2, VAL (`Validate`), Fast Downward (`fast-downward`).
- **Feedback Oracles**: Pure symbolic validator/planner tool output without human steering in the loop.

## Success Criteria
- [ ] Complete formal specification of PDDL domain engineering lifecycle activities and typed contracts.
- [ ] Fully functional LangGraph closed-loop agent supporting elicitation, blueprinting, compilation, validation, fault localization, repair, and evolution.
- [ ] Comprehensive PDDLLifeCycleBench containing task suites for Elicitation, Generation, Fault Repair, and Domain Evolution.
- [ ] Empirical benchmark evaluation showing UPDEAgent significantly outperforming single-step LLM baselines on multi-step repair and evolution.
