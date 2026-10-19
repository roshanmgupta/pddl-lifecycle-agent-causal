# Pending Cross-Domain Batch Metrics Tracking

> **Status Notice**: The metrics in this document represent cross-domain distribution-level parameters. 
> Per explicit experimental protocol, they are **NOT** calculated during isolated single-task executions in Streamlit.
> They will be populated once the complete 120-task benchmark suite has been executed across all domain families.

---

## 1. Parameters Excluded from Evaluation (Per User Instruction)
- **Statistical Significance Testing (McNemar's Test & Wilcoxon Signed-Rank Test)**: Excluded from active evaluation.
- **Co-Solved Set Makespan (Plan Length Intersection)**: Excluded from active run reporting.

---

## 2. Parameter 1: Repair Convergence Acceleration (RCA)

### Concept & Formula
- **Objective**: Quantifies the percentage reduction in feedback repair cycles achieved by our Causal Graph + SBFL diagnostic triage engine over naive unguided error backprompting (Baseline 2).
- **Evaluation Dataset**: Category B (Synthetic Fault Repair — 48 tasks across 24 domains).
- **Formula (Plain Text)**:
  ```
  RCA = ((Mean_Iterations_Baseline_2 - Mean_Iterations_Proposed_Agent) / Mean_Iterations_Baseline_2) * 100%
  ```

### Tracking Status: [PENDING BATCH BENCHMARK RUN]

```
Domain Family       Task ID                  Flaw Category               Baseline 2 (Unstructured)  Proposed Agent (Closed Loop)  Iteration Delta
                                                                         Iterations Used (1-10)     Iterations Used (1-10)        (Base2 - Proposed)
----------------------------------------------------------------------------------------------------------------------------------------------------
barman14-bfs        flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
barman14-bfs        flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
blocksworld         flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
blocksworld         flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
floortile           flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
floortile           flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
gripper             flaw_01_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
gripper             flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
depot               flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
depot               flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
driverlog02-bfs     flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
driverlog02-bfs     flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
elevators08         flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
elevators08         flaw_02_deadlock         Initial/Goal Deadlock       [Pending]                  [Pending]                     [Pending]
ferry               flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
ferry               flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
hiking14            flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
hiking14            flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
logistics           flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
logistics           flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
zenotravel02        flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
zenotravel02        flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
childsnack14        flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
childsnack14        flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
goldminer           flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
goldminer           flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
pipesworld          flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
pipesworld          flaw_02_deadlock         Initial/Goal Deadlock       [Pending]                  [Pending]                     [Pending]
rovers              flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
rovers              flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
satellite           flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
satellite           flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
scanalyzer08        flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
scanalyzer08        flaw_02_deadlock         Initial/Goal Deadlock       [Pending]                  [Pending]                     [Pending]
grid                flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
grid                flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
movie98             flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
movie98             flaw_02_effect_deletion  Action Effect Deletion      [Pending]                  [Pending]                     [Pending]
mprime98            flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
mprime98            flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
mystery98           flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
mystery98           flaw_02_deadlock         Initial/Goal Deadlock       [Pending]                  [Pending]                     [Pending]
parking11           flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
parking11           flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
pegsol08            flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
pegsol08            flaw_02_deadlock         Initial/Goal Deadlock       [Pending]                  [Pending]                     [Pending]
visitall            flaw_01_type_signature   Type / Arity Inversion      [Pending]                  [Pending]                     [Pending]
visitall            flaw_02_precondition     Precondition Misalignment   [Pending]                  [Pending]                     [Pending]
----------------------------------------------------------------------------------------------------------------------------------------------------
OVERALL AVERAGE     Avg_I (Mean Cycles)                                  [Mean Base2 Avg_I]         [Mean Proposed Avg_I]         --
NET RCA (%)         ((Mean Base2 - Mean Proposed) / Mean Base2) * 100%   --> NET RCA = [Pending %]
```

---

## 3. Parameter 2: Token Efficiency per Verified Domain (TEVD)

### Concept & Formula
- **Objective**: Evaluates the architectural compute economy (Göbel et al., 2026) by measuring the total inference tokens (prompt + completion) consumed per working, verified domain deliverable produced.
- **Evaluation Dataset**: All 120 tasks across the 4 systems.
- **Formula (Plain Text)**:
  ```
  TEVD = Total Cumulative Tokens Consumed / Total Count of Verified Domains (E2E == True)
  ```

### Tracking Status: [PENDING BATCH BENCHMARK RUN]

```
Architecture / System            Total Tasks Run  Verified Domains Count (E2E == True)  Total Prompt Tokens  Total Completion Tokens  Total Cumulative Tokens  TEVD (Tokens / Verified Domain)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Baseline 1: Zero-Shot Direct     120              [Pending Count]                       [Pending]            [Pending]                [Pending Sum]            [Pending TEVD]
Baseline 2: Unstructured Retry   120              [Pending Count]                       [Pending]            [Pending]                [Pending Sum]            [Pending TEVD]
ABLATION_NO_TRIAGE               120              [Pending Count]                       [Pending]            [Pending]                [Pending Sum]            [Pending TEVD]
CLOSED_LOOP_AST_AGENT (Proposed) 120              [Pending Count]                       [Pending]            [Pending]                [Pending Sum]            [Pending TEVD]
```

---

## 4. Execution Command to Finalize These Tables
Once you are ready to execute the batch testing over all domains, run:
```powershell
python -m eval.run_ipc_evaluation --all-domains --systems CLOSED_LOOP_AST_AGENT,UNSTRUCTURED_RETRY,ZERO_SHOT
```
This will generate `output/benchmark_run_summary.csv`, from which the iteration numbers and token sums will be filled directly into the two tables above.
