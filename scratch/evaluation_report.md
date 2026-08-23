# PDDLLifeCycleBench Empirical Evaluation Report

## Summary Metrics Comparison Table

| Agent Architecture | Tasks Evaluated | Syntax Validity Rate (%) | Plan Validity Rate (%) | Repair Success Rate (%) | Avg Iterations | Avg Latency (s) |
|-------------------|-----------------|--------------------------|------------------------|-------------------------|----------------|-----------------|
| **ZERO_SHOT** | 3 | 100.0% | 100.0% | 100.0% | 1.0 | 23.52s |
| **UNSTRUCTURED_RETRY** | 3 | 100.0% | 100.0% | 100.0% | 1.0 | 24.75s |
| **CLOSED_LOOP_AST_AGENT** | 3 | 100.0% | 100.0% | 100.0% | 1.0 | 18.24s |

## Per-Task Failure & Error Analysis

| Task ID | Agent Architecture | Task Type | Syntax Valid | Plan Valid | Error Summary |
|---------|-------------------|-----------|--------------|------------|---------------|
| `blocksworld_elicitation_01` | `ZERO_SHOT` | `ELICITATION` | `True` | `True` | None (Passed) |
| `blocksworld_elicitation_01` | `UNSTRUCTURED_RETRY` | `ELICITATION` | `True` | `True` | None (Passed) |
| `blocksworld_elicitation_01` | `CLOSED_LOOP_AST_AGENT` | `ELICITATION` | `True` | `True` | None (Passed) |
| `blocksworld_repair_missing_precondition_01` | `ZERO_SHOT` | `SYNTHETIC_FAULT_REPAIR` | `True` | `True` | None (Passed) |
| `blocksworld_repair_missing_precondition_01` | `UNSTRUCTURED_RETRY` | `SYNTHETIC_FAULT_REPAIR` | `True` | `True` | None (Passed) |
| `blocksworld_repair_missing_precondition_01` | `CLOSED_LOOP_AST_AGENT` | `SYNTHETIC_FAULT_REPAIR` | `True` | `True` | None (Passed) |
| `satellite_evolution_01` | `ZERO_SHOT` | `DOMAIN_EVOLUTION` | `True` | `True` | None (Passed) |
| `satellite_evolution_01` | `UNSTRUCTURED_RETRY` | `DOMAIN_EVOLUTION` | `True` | `True` | None (Passed) |
| `satellite_evolution_01` | `CLOSED_LOOP_AST_AGENT` | `DOMAIN_EVOLUTION` | `True` | `True` | None (Passed) |