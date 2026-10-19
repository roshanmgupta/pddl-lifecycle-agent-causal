# Research Paper Deep Dive & Architectural Mapping
## Paper: "Generating Consistent PDDL Domains with Large Language Models"
**Authors**: Pavel Smirnov, Frank Joublin, Antonello Ceravola, and Michael Gienger  
**Affiliation**: Honda Research Institute Europe GmbH, Offenbach am Main, Germany  
**Publication**: *Proceedings of the 2024 IEEE International Conference on Robotics and Automation (ICRA 2024)*, pages 10582–10588.  
**DOI / Preprint**: [arXiv:2404.07751](https://arxiv.org/abs/2404.07751)

---

### 1. Executive Summary & Core Research Problem

Classical AI planning requires mathematically consistent domain models specified in the Planning Domain Definition Language (PDDL). While Large Language Models (LLMs) possess vast commonsense knowledge for decomposing human tasks, direct text-to-PDDL generation suffers from:
1. **Syntactic malformations**: Parenthesis mismatch, illegal colon prefixes, and formatting bugs inherent to autoregressive next-token generation.
2. **Internal consistency failures**: Discrepancies between predicate declarations and their instantiations in action signatures, parameter type violations, and undeclared variables.
3. **Reachability deadlocks**: Syntactically parseable domains whose actions cannot achieve the goal state due to missing causal preconditions or omitted initial state facts.

Smirnov et al. tackle this by introducing a **four-step generation and consistency-checking pipeline**. Their primary innovation is replacing direct PDDL text prompting with an intermediate **JSON markup** and executing a **rule-based error correction loop** before compiling to PDDL.

---

### 2. Detailed Technical Breakdown of Smirnov et al.'s Methodology

The paper structures domain modeling into four sequential phases:

```
[Natural Language Input]
       │
       ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: Textual Planning & Domain Narrative            │
│ LLM generates an informal narrative of actions/objects │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Intermediate Markup Generation (JSON)          │
│ Uses function signatures format rather than PDDL Lisp  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Step 3.1 & 3.2: Consistency Checking & Correction Loop │
│ - Rule-based checks over 15 error categories (Table I) │
│ - Feeds structured suggestions back to LLM (max 15 iter)│
└──────────────────────────┬─────────────────────────────┘
                           │ (Zero consistency errors)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Reachability Analysis via Fast Downward        │
│ - Translates JSON to PDDL                              │
│ - SAS+ translation & causal predicate dependency check │
│ - OPEN-LOOP: Outputs reachability report to human      │
└────────────────────────────────────────────────────────┘
```

#### A. Intermediate JSON Markup (Step 2)
- **Rationale**: LLMs encounter significantly more JSON and programming language function signatures in pre-training data than PDDL Lisp S-expressions.
- **Design**: Action schemas are drafted with typed parameters and explicit precondition/effect lists as JSON dictionaries. Single-letter variables (`?x`, `?y`) are discouraged in favor of semantically meaningful names (`?robot`, `?location`).

#### B. The 15 Error Types & Feedback Protocol (Step 3.1 & Table I)
Smirnov et al. empirically measured 15 categories of errors in LLM-generated JSON models across 5 domains (*Gripper, Pizza, Logistics, Household, Tyreworld*):
1. **Wrong type use (37.25%)**: Parameter types used in a predicate contradict its definition.
2. **Undeclared parameter use (26.27%)**: An action's precondition or effect references a variable not declared in the action's parameter list.
3. **Wrong parameter (14.62%)**: Using a type name where a parameter variable was expected, or referencing undefined objects.
4. **Missing parameters (6.66%)**: Action or predicate declared with empty or incomplete parameter signatures.
5. **Predicate mismatch (5.56%)**: Arguments do not match predicate arity or parameter types.
6. **Minor structural errors (<4% each)**: Wrong type casing, duplicate predicates, unusable `:init` predicates, duplicate actions, unreachable goal predicates.

#### C. The Feedback Format
Rather than piping unparsed terminal logs back to the LLM, Step 3.2 provides structured natural language feedback:
- `[ERROR TYPE]`: The formal classification from Table I.
- `[DESCRIPTION]`: Specific context detailing which action/predicate is invalid.
- `[SUGGESTION FOR LLM]`: Actionable instructions (e.g., *"Either add the parameter ?l to the action signature or remove it from the predicate"*).

#### D. Reachability Analysis via Planner (Step 4 & Figure 2)
Once the JSON passes all consistency checks, it is deterministically converted into PDDL. Fast Downward is executed:
- The translator checks whether actions are reachable.
- Causal analysis identifies predicates that are **never affected by any action**. If these predicates are absent from the initial state (`:init`), the action can never execute.
- **Crucial Architectural Limitation**: Smirnov et al. **did not automate the repair of reachability errors**. Step 4 was strictly evaluated as an open-loop report for human analysis. The paper explicitly leaves an automated LLM reachability repair loop for future work.

---

### 3. What We Took and Adapted from Smirnov et al.

Our PDDL Lifecycle Agent adopts three major insights from Smirnov et al. while formalizing and significantly extending them:

#### 1. The Intermediate Representation (AST Schemas)
- **Smirnov et al.**: Used an informal, ad-hoc Python JSON dictionary.
- **Our System**: Replaced ad-hoc JSON with a formal, strictly validated **Pydantic AST model** (`DomainBlueprint`, `ProblemBlueprint` in `schemas/pddl_blueprint.py`). Pydantic enforces typing, field validation, and variable naming deterministically before any code is generated.

#### 2. Structured Diagnostic Feedback Formatting
- **Smirnov et al.**: Demonstrated that structured triage (`[ERROR TYPE]`, `[LOCATION]`, `[SUGGESTION]`) reduces human correction time from hours to minutes.
- **Our System**: Directly implemented this exact feedback structure in `nodes/triage.py` (`format_diagnostic_feedback`):
  ```python
  feedback_lines.append(f"  - [ERROR TYPE]: {cat}")
  feedback_lines.append(f"  - [TARGET AST OPERATION]: {op}")
  feedback_lines.append(f"  - [LOCATION / COMPONENT]: {report.faulty_element} (Suspiciousness: {report.suspiciousness_score})")
  feedback_lines.append(f"  - [DESCRIPTION / RAW TRACE]: {report.raw_log}")
  feedback_lines.append(f"  - [SUGGESTION FOR REPAIR]: {report.suggested_repair_hint}")
  ```

#### 3. Error Classification Taxonomy
- Smirnov's top three error classes (*Wrong type use 37%*, *Undeclared parameter 26%*, *Wrong parameter 15%*) form our core AST triage categories:
  - `ErrorCategory.TYPE_SIGNATURE`
  - `ErrorCategory.SYNTAX_PARSE`
  - `ErrorCategory.GROUNDING_UNSOLVABILITY`

---

### 4. How Our PDDL Lifecycle Agent Extends Beyond Smirnov et al.

While Smirnov et al. provided a foundational proof-of-concept for JSON consistency checking, our master's thesis resolves its primary limitations:

| Architectural Dimension | Smirnov et al. (ICRA 2024) | Our PDDL Lifecycle Agent |
| :--- | :--- | :--- |
| **Reachability Feedback Loop** | **Open-Loop**: Reachability errors reported to human only; no automated repair loop. | **Closed-Loop**: Fast Downward and VAL errors feed directly into an automated LLM Diagnostic Triage & Repair cycle. |
| **Fault Localization** | Naive rule-based matching across Table I. | **Spectrum-Based Fault Localization**: Computes suspiciousness scores $\sigma(n) \in [0.0, 1.0]$ to rank root causes. |
| **Repair Granularity** | Global regeneration of the entire JSON model. | **Localized Delta Repair**: Isolates `faulty_element` to patch only the defective action sub-schema. |
| **Formal Standard** | Custom function syntax compiled to unvalidated PDDL. | **Strict Classical PDDL 2.1 (`:strips :typing`)** verified against ground-truth VAL and Fast Downward oracles. |
| **Lifecycle & Maintenance** | Single-shot generation only; no evolution or regression handling. | **Full KEPS SDLC**: Elicitation $\rightarrow$ Generation $\rightarrow$ Triage $\rightarrow$ Repair $\rightarrow$ Evolution with historical regression testing. |

---

### 5. Summary Text for Thesis Report (How to Cite Smirnov et al.)

> *"Smirnov et al. [ICRA 2024] demonstrated that decoupling natural language requirements from PDDL syntax through an intermediate JSON markup significantly mitigates syntax collapse. Furthermore, their empirical findings revealed that the vast majority of modeling defects stem from relational inconsistencies—specifically parameter type mismatches (37.3%) and undeclared action parameters (26.3%)—which can be resolved through structured diagnostic suggestions. However, their architecture remained fundamentally open-loop: while static consistency was checked automatically, planner reachability failures were not connected back into an iterative LLM repair loop. In this thesis, we build upon Smirnov et al.'s structured feedback paradigm by formalizing the intermediate representation into a strictly typed Pydantic AST schema, closing the reachability loop via automated symbolic oracle triage (VAL and Fast Downward), and extending the architecture to support continuous domain evolution with regression guarantees."*
