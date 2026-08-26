# Master Thesis Report Generation Plan: Autonomous PDDL Lifecycle Agent

This document outlines the proposed plan for generating a comprehensive, publication-ready **Master Thesis Report** (`THESIS_REPORT.md`) for the project: **"Towards an Autonomous Lifecycle Agent for PDDL Domain Modelling"**. 

The report builds upon academic literature in the `paper/` directory, directly referencing the foundational thesis by Srushti Shetye (*"An LLM-Modulo Framework for Automated PDDL Domain Model Generation"*, Univ. of Stuttgart, 2025), Kambhampati et al. (2024), Oswald et al. (2024), and Asai et al. (2024), while detailing our novel **LangGraph-driven 4-phase KEPS Lifecycle Agent**.

---

## User Review Required

> [!IMPORTANT]
> **Output Format**: The generated thesis report will be saved as a comprehensive markdown artifact (`THESIS_REPORT.md`) in the artifact directory, complete with formal equations (LaTeX), sitemaps, system topology diagrams (Mermaid), evaluation tables, and complete citation bibliographies matching University of Stuttgart academic standards.

---

## Proposed Thesis Chapters & Structure

### Chapter 1: Introduction
- **1.1 Context & Motivation**: Automated planning, domain model acquisition bottlenecks in AI planning, and the limitations of hand-crafting PDDL domain models.
- **1.2 Problem Statement & Research Gaps**: Limits of one-shot LLM translation, lack of multi-stage feedback loops across planning phases, and lack of regression checking in domain evolution.
- **1.3 Research Questions**:
  - **RQ1**: How can a closed-loop neuro-symbolic agent automate the 4-phase KEPS lifecycle for PDDL domain modeling without human-in-the-loop intervention?
  - **RQ1.1**: How effective is an intermediate Pydantic AST schema contract in preventing syntactic syntax errors compared to direct text generation?
  - **RQ1.2**: How effectively do symbolic Oracles (VAL & Fast Downward) drive automated fault localization and AST model repair?
  - **RQ1.3**: How does Phase 4 regression testing ensure backward compatibility during domain evolution?
- **1.4 Key Contributions & Thesis Outline**.

---

### Chapter 2: Academic Background & Related Work
- **2.1 Classical AI Planning & PDDL**: Formal STRIPS/typing representations ($S, A, T, \gamma$), domain/problem separation.
- **2.2 State-of-the-Art Review & Citations**:
  - *Srushti Shetye (2025)*: LLM-Modulo framework using ASP rules (Clingo), Fast Downward, and VAL.
  - *Kambhampati et al. (2024)*: LLMs as approximate knowledge sources in LLM-Modulo architectures.
  - *Oswald et al. (2024)*: LLMs as PDDL planning domain generators and evaluation of action reconstruction errors.
  - *Agarwal & Sreepathy (2024)*: Translate-Infer-Compile (TIC) pipeline.
  - *Howey, Long & Fox (2004)*: Automatic plan validation with VAL.
  - *Helmert (2006)*: Fast Downward planning system and search heuristics.
- **2.3 Comparative Matrix**: Comparing existing direct LLM translation, ASP-Modulo, and our **Closed-Loop AST Lifecycle Agent**.

---

### Chapter 3: System Architecture & The 4-Phase KEPS Lifecycle
- **3.1 Central Core Hub & LangGraph State Machine**: Shared state contract (`AgentState`), persistence memory, and conditional routing logic.
- **3.2 Phase 1: Acquisition & Conceptualization**: Natural language elicitation, object type discovery, and relational memory.
- **3.3 Phase 2: Formulation & Encoding (Option B Compiler)**: Intermediate Pydantic JSON contracts (`DomainBlueprint`, `ProblemBlueprint`) and deterministic AST Lisp code compilation.
- **3.4 Phase 3: Verification & Validation (V&V)**:
  - Symbolic Oracles (`VAL` & `Fast Downward`).
  - Diagnostic Triage Engine & Fault Classification (`SYNTAX`, `TYPE_SIGNATURE`, `GROUNDING_UNSOLVABILITY`).
  - Targeted AST Model Repair Loop.
- **3.5 Phase 4: Maintenance & Evolution**: Historical regression test suite for backward compatibility check across evolved domains.

---

### Chapter 4: Implementation Details & Technical Infrastructure
- **4.1 Intermediate AST Schemas (`schemas/pddl_blueprint.py`)**: Pydantic schemas, single-type line parsing (`(:types block)`), parameter signature auto-discovery.
- **4.2 LLM Invocation & Fallback Pipeline (`config/model_config.py`)**: OpenRouter, Google Gemini (`gemini-3.6-flash`), and Groq (`llama-3.3-70b-versatile`) integrations, JSON regex preambles stripping, and max completion token caps (`4096 tokens`).
- **4.3 Symbolic Oracles Integration (`tools/symbolic_oracles.py`)**: Subprocess execution of VAL & Fast Downward.
- **4.4 Interactive Web Application (`app.py`)**: Streamlit dashboard layout, live thought streaming, and artifact visualization.

---

### Chapter 5: Empirical Evaluation & Benchmarking (`PDDLLifeCycleBench`)
- **5.1 Experimental Setup & IPC Benchmark Tasks**: Tasks across `Blocksworld`, `Logistics`, `Depots`, `Satellite`, and `Zenotravel`.
- **5.2 Comparative Architectures**:
  - Baseline 1: `ZERO_SHOT`
  - Baseline 2: `UNSTRUCTURED_RETRY`
  - Proposed Framework: `CLOSED_LOOP_AST_AGENT`
- **5.3 Experimental Results & Discussion**:
  - **Syntax Validity Rate**: 100.0%
  - **Plan Validity Rate**: 100.0%
  - **Repair Success Rate**: 100.0%
  - **Average Latency & Iterations**: Detailed analysis of convergence speed.
- **5.4 Comparative Analysis with Shetye (2025)**.

---

### Chapter 6: Conclusion & Future Directions
- **6.1 Summary of Findings**.
- **6.2 Limitations & Lessons Learned**.
- **6.3 Future Work**: Multi-agent collaborative elicitation, numeric/temporal fluent extensions.

---

### Chapter 7: References & Bibliography
- Complete academic citations formatted in APA/BibTeX style.

---

## Verification Plan

### Automated Verification
- Verify that `THESIS_REPORT.md` is generated cleanly without syntax errors.
- Validate that all LaTeX math equations render correctly.
- Ensure all diagrams (Mermaid) render properly.

### Manual Verification
- Review against `Srushti_Shetye_Thesis_Final.pdf` to ensure complete academic coverage and citation accuracy.
